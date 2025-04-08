# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json
import os
import pickle
import socket
import subprocess
import sys
import time
from contextlib import contextmanager
from typing import Any
from typing import Dict

from ansible.errors import AnsibleRuntimeError

from .common import SSMDisplay


def create_socket_path(instance_id: str, region_name: str) -> str:
    return os.path.join(
        os.environ["HOME"], ".ansible", "_".join(["connection_aws_ssm_turbo", instance_id, region_name])
    )


class SSMTurboSocket(SSMDisplay):
    def __init__(self, conn_plugin: Any):
        super(SSMTurboSocket, self).__init__(conn_plugin.verbosity_display)
        self._region = conn_plugin.get_option("region") or "us-east-1"
        self._socket_path = create_socket_path(conn_plugin.instance_id, self._region)
        self.verbosity_display(4, f">>> SSM TURBO SOCKET PATH = {self._socket_path}")
        self.conn_plugin = conn_plugin
        self._socket = None

    def bind(self):
        running = False
        self._socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        for attempt in range(100, -1, -1):
            try:
                self._socket.connect(self._socket_path)
                return True
            except (ConnectionRefusedError, FileNotFoundError):
                if not running:
                    running = self.start_server()
                if attempt == 0:
                    raise
            time.sleep(0.01)

    def _mask_command(self, command: str) -> str:
        if self.conn_plugin.get_option("access_key_id"):
            command = command.replace(self.conn_plugin.get_option("access_key_id"), "*****")
        if self.conn_plugin.get_option("secret_access_key"):
            command = command.replace(self.conn_plugin.get_option("secret_access_key"), "*****")
        if self.conn_plugin.get_option("session_token"):
            command = command.replace(self.conn_plugin.get_option("session_token"), "*****")
        return command

    def start_server(self):
        env = os.environ
        parameters = [
            "--fork",
            "--socket-path",
            self._socket_path,
            "--region",
            self._region,
            "--executable",
            self.conn_plugin.get_executable(),
        ]

        pairing_options = {
            "--instance-id": "instance_id",
            "--ssm-timeout": "ssm_timeout",
            "--reconnection-retries": "reconnection_retries",
            "--access-key-id": "access_key_id",
            "--secret-access-key": "secret_access_key",
            "--session-token": "session_token",
            "--profile": "profile",
            "--ssm-document": "ssm_document",
            "--is-windows": "is_windows",
        }
        for opt, attr in pairing_options.items():
            if hasattr(self.conn_plugin, attr):
                if opt_value := getattr(self.conn_plugin, attr):
                    parameters.extend([opt, str(opt_value)])
            elif opt_value := self.conn_plugin.get_option(attr):
                parameters.extend([opt, str(opt_value)])

        command = [sys.executable]
        ansiblez_path = sys.path[0]
        env.update({"PYTHONPATH": ansiblez_path})
        command += [
            "-m",
            "ansible_collections.community.aws.plugins.plugin_utils.ssm.turbo_server",
        ]
        # parent_dir = os.path.dirname(__file__)
        # server_path = os.path.join(parent_dir, "server.py")
        # command += [server_path]
        displayed_command = self._mask_command(" ".join(command + parameters))
        self.verbosity_display(4, f">>> SSM TURBO SOCKET COMMAND = '{displayed_command}'")
        p = subprocess.Popen(
            command + parameters,
            env=env,
            close_fds=True,
        )
        p.communicate()
        self.verbosity_display(4, f">>> SSM TURBO SOCKET COMMAND Pid = '{p.pid}'")
        return p.pid

    def communicate(self, command, wait_sleep=0.01):
        encoded_data = pickle.dumps(command)
        self._socket.sendall(encoded_data)
        self._socket.shutdown(socket.SHUT_WR)
        raw_answer = b""
        while True:
            b = self._socket.recv((1024 * 1024))
            if not b:
                break
            raw_answer += b
            time.sleep(wait_sleep)
        try:
            result = json.loads(raw_answer.decode())
            return result
        except json.decoder.JSONDecodeError:
            raise AnsibleRuntimeError(f"Cannot decode exec_command answer: {raw_answer}")

    def close(self):
        if self._socket:
            self._socket.close()


@contextmanager
def connect(conn_plugin: Any):
    turbo_socket = SSMTurboSocket(conn_plugin)
    try:
        turbo_socket.bind()
        yield turbo_socket
    finally:
        turbo_socket.close()


def turbo_exec_command(conn_plugin: Any, encoded_cmd: str) -> Dict:
    with connect(conn_plugin) as turbo_socket:
        result = turbo_socket.communicate(command=encoded_cmd)
        return result.get("returncode"), result.get("stdout"), result.get("stderr")
