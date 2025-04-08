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
from typing import Any
from typing import Dict

from ansible.errors import AnsibleFileNotFound
from ansible.errors import AnsibleRuntimeError
from ansible.plugins.shell.powershell import _common_args


def _create_socket_path(instance_id: str, region_name: str) -> str:
    return os.path.join(
        os.environ["HOME"], ".ansible", "_".join(["connection_aws_ssm_caching", instance_id, region_name])
    )


class SSMCachingSocket:
    def __init__(self, conn_plugin: Any):
        self.verbosity_display = conn_plugin.verbosity_display
        self._verbosity_level = 1
        self._region = conn_plugin.get_option("region") or "us-east-1"
        self._socket_path = _create_socket_path(conn_plugin.instance_id, self._region)
        self.verbosity_display(self._verbosity_level, f">>> SSM Caching Socket path = {self._socket_path}")
        self.conn_plugin = conn_plugin
        self._socket = None
        self._bind()

    def _bind(self):
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
            "--ttl": "caching_ttl",
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
        parent_dir = os.path.dirname(__file__)
        server_path = os.path.join(parent_dir, "cache_server.py")
        if not os.path.exists(server_path):
            raise AnsibleFileNotFound(f"The socket does not exist at expected path = '{server_path}'")
        command += [server_path]
        displayed_command = self._mask_command(" ".join(command + parameters))
        self.verbosity_display(self._verbosity_level, f">>> SSM Caching socket command = '{displayed_command}'")
        p = subprocess.Popen(
            command + parameters,
            env=env,
            close_fds=True,
        )
        p.communicate()
        self.verbosity_display(self._verbosity_level, f">>> SSM Caching socket process pid = '{p.pid}'")
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

    def __enter__(self) -> Any:
        return self

    def __exit__(self, type, value, traceback):
        if self._socket:
            self._socket.close()


def exec_command_using_caching(conn_plugin: Any, cmd: str) -> Dict:
    with SSMCachingSocket(conn_plugin) as cache:
        # Encode Windows command
        if conn_plugin.is_windows:
            if not cmd.startswith(" ".join(_common_args) + " -EncodedCommand"):
                cmd = conn_plugin._shell._encode_script(cmd, preserve_rc=True)
        result = cache.communicate(command=cmd)
        return result.get("returncode"), result.get("stdout"), result.get("stderr")
