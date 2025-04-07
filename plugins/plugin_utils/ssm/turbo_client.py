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
from typing import Callable
from typing import Dict

from ansible.errors import AnsibleRuntimeError

from .common import SSMDisplay


def create_socket_path(instance_id: str, region_name: str) -> str:
    return os.path.join(
        os.environ["HOME"], ".ansible", "_".join(["connection_aws_ssm_turbo", instance_id, region_name])
    )


class SSMTurboSocket(SSMDisplay):
    def __init__(self, instance_id, region_name, ttl, verbosity_display):
        super(SSMTurboSocket, self).__init__(verbosity_display)
        self._socket_path = create_socket_path(instance_id, region_name)
        self.verbosity_display(4, f">>> SSM TURBO SOCKET PATH = {self._socket_path}")
        self._ttl = ttl
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

    def start_server(self):
        env = os.environ
        parameters = ["--fork", "--socket-path", self._socket_path, "--ttl", str(self._ttl)]

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
        self.verbosity_display(4, f">>> SSM TURBO SOCKET COMMAND = '{command + parameters}'")
        p = subprocess.Popen(
            command + parameters,
            env=env,
            close_fds=True,
        )
        result = p.communicate()
        self.verbosity_display(4, f">>> SSM TURBO SOCKET COMMAND Pid = '{p.pid}' (result = {result})")
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
def connect(instance_id, region_name, ttl, verbosity_display):
    turbo_socket = SSMTurboSocket(
        instance_id=instance_id, region_name=region_name, ttl=ttl, verbosity_display=verbosity_display
    )
    try:
        turbo_socket.bind()
        yield turbo_socket
    finally:
        turbo_socket.close()


def turbo_exec_command(command: str, instance_id: str, region_name: str, verbosity_display: Callable, ttl=10) -> Dict:
    with connect(instance_id, region_name, ttl=ttl, verbosity_display=verbosity_display) as turbo_socket:
        return turbo_socket.communicate(command=command)
