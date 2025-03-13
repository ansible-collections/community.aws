# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json
import os
import pty
import random
import re
import select
import socket
import string
import subprocess
import time
from typing import Any
from typing import Dict
from typing import List
from typing import NoReturn
from typing import Optional
from typing import Union

from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils._text import to_text
from ansible.utils.display import Display

display = Display()


class ConnectionPluginDisplay:
    def __init__(self, host: Optional[str]) -> None:
        self._host_args = {}
        if host:
            self._host_args = {"host": host}

    def _display(self, f: callable, message: str) -> None:
        f(to_text(message), **self._host_args)

    def v(self, message):
        self._display(display.v, message)

    def vv(self, message):
        self._display(display.vv, message)

    def vvv(self, message):
        self._display(display.vvv, message)

    def vvvv(self, message):
        self._display(display.vvvv, message)


class StdoutPoller:
    def __init__(self, session: Any, stdout: Any, poller: Any, timeout: int) -> None:
        self._stdout = stdout
        self._poller = poller
        self._session = session
        self._timeout = timeout

    def readline(self):
        return self._stdout.readline()

    def has_data(self) -> bool:
        return bool(self._poller.poll(self._timeout))

    def read_stdout(self, length: int = 1024) -> str:
        return self._stdout.read(length).decode("utf-8")

    def stdin_write(self, value: str) -> None:
        self._session.stdin.write(value)

    def poll(self) -> NoReturn:
        start = round(time.time())
        yield self.has_data()
        while self._session.poll() is None:
            remaining = start + self._timeout - round(time.time())
            if remaining < 0:
                raise AnsibleConnectionFailure("StdoutPoller timeout...")
            yield self.has_data()

    def match_expr(self, expr: Union[str, callable]) -> str:
        time_start = time.time()
        content = ""
        while (int(time.time()) - time_start) < self._timeout:
            if self.poll():
                content += self.read_stdout()
                if callable(expr):
                    if expr(content):
                        return content
                elif expr in content:
                    return content
        raise TimeoutError(f"Unable to match expr '{expr}' from content")

    def flush_stderr(self) -> str:
        """read and return stderr with minimal blocking"""

        poll_stderr = select.poll()
        poll_stderr.register(self._session.stderr, select.POLLIN)
        stderr = ""
        while self._session.poll() is None:
            if not poll_stderr.poll(1):
                break
            line = self._session.stderr.readline()
            stderr = stderr + line
        return stderr


class AnsibleAwsSSMSession:
    def __init__(
        self,
        display: ConnectionPluginDisplay,
        ssm_client: Any,
        instance_id: str,
        executable: str,
        ssm_timeout: int,
        region_name: Optional[str],
        profile_name: str,
        document_name: Optional[str] = None,
        parameters: Optional[Dict[str, List[str]]] = None,
    ) -> None:
        self._client = ssm_client
        self._session = None
        self._session_id = None
        self._local_port = None
        self._display = display

        params = {"Target": instance_id}
        if document_name:
            params["DocumentName"] = document_name
        if parameters:
            params["Parameters"] = parameters

        try:
            response = self._client.start_session(**params)
            self._session_id = response["SessionId"]
            self._display.vvvv(f"Start session - SessionId: {self._session_id}")

            cmd = [
                executable,
                json.dumps(response),
                region_name,
                "StartSession",
                profile_name,
                json.dumps({"Target": instance_id}),
                self._client.meta.endpoint_url,
            ]

            stdout_r, stdout_w = pty.openpty()
            self._session = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=stdout_w,
                stderr=subprocess.PIPE,
                close_fds=True,
                bufsize=0,
            )

            os.close(stdout_w)
            stdout = os.fdopen(stdout_r, "rb", 0)
            self._poller = StdoutPoller(
                session=self._session,
                stdout=stdout,
                poller=select.poll().register(stdout, select.POLLIN),
                timeout=ssm_timeout,
            )
        except Exception as e:
            raise AnsibleConnectionFailure(f"failed to start session: {e}")

    def __del__(self):
        if self._session_id:
            self._display.vvvv(f"Terminating AWS Session: {self._session_id}")
            self._client.terminate_session(SessionId=self._session_id)
        if self._session:
            self._display.vvvv("Terminating subprocess.Popen session")
            self._session.terminate()


class PortForwardingFileTransferManager:
    DEFAULT_HOST_PORT = 80

    def __init__(
        self,
        host: Optional[str],
        ssm_client: Any,
        instance_id: str,
        executable: str,
        ssm_timeout: int,
        region_name: Optional[str],
        profile_name: str,
        host_port: Optional[int],
        local_port: Optional[int],
    ) -> None:
        self._client = ssm_client
        self._session = None
        self._instance_id = instance_id
        self._session_id = None
        self._poller = None
        self._local_port = local_port
        self._host_port = host_port or self.DEFAULT_HOST_PORT
        self._display = ConnectionPluginDisplay(host=host)

        # Create Port forwarding Session
        parameters = {}
        if local_port:
            parameters["localPortNumber"] = [str(local_port)]
        if host_port:
            parameters["portNumber"] = [str(host_port)]
        self._portforwarding_session = AnsibleAwsSSMSession(
            ssm_client=ssm_client,
            instance_id=instance_id,
            executable=executable,
            ssm_timeout=ssm_timeout,
            region_name=region_name,
            profile_name=profile_name,
            document_name="AWS-StartPortForwardingSession",
            parameters=parameters,
            display=self._display,
        )

        match_expr = re.compile(r"Port ([0-9]+) opened for sessionId")
        content = self._portforwarding_session._poller.match_expr(expr=match_expr.search)
        match = match_expr.search(content)
        self._local_port = int(match.group(1))
        self._display.vvvv(f"SSM PORT FORWARDING - Local port '{self._local_port}'")

        # Start shell session
        self._shell_session = AnsibleAwsSSMSession(
            ssm_client=ssm_client,
            instance_id=instance_id,
            executable=executable,
            ssm_timeout=ssm_timeout,
            region_name=region_name,
            profile_name=profile_name,
            display=self._display,
        )

    def _socket_connect(self, session: Any, port: int, host: str = "localhost", max_attempts=10) -> None:
        """Connect to socket"""
        for attempt in range(max_attempts):
            try:
                session.connect((host, port))
                break
            except OSError:
                if attempt == max_attempts - 1:
                    self._display.vvvv(f"SOCKET _CONNECT: Failed to intiate socket connection on '{host}:{port}'")
                    raise
                time.sleep(0.05)

    def _socket_read(self, port: int, out_path: Optional[str] = None) -> None:
        self._display.vvvv(f"Read content from socket on port '{port}'...")
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as session:
            session.settimeout(1)
            self._socket_connect(session=session, port=port)
            try:
                with open(out_path, "wb") as fhandler:
                    while 1:
                        data = session.recv(1024)
                        if not data:
                            break
                        fhandler.write(data)
                        time.sleep(0.05)
            except TimeoutError:
                pass
        self._display.vvvv("Socket connection closed.")

    def _socket_write(self, port: int, in_path: str) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as session:
            self._socket_connect(session=session, port=port)
            with open(in_path, "rb") as f:
                session.sendall(f.read())

    def put_file(self, in_path: str, out_path: str) -> None:
        # Start listener on Remote host
        mark_end = "".join([random.choice(string.ascii_lowercase + string.digits) for i in range(12)])
        put_cmd = f"sudo nc -l -v -p {str(self._host_port)} > {out_path}; printf '{mark_end}'"
        put_cmd = (put_cmd + "\n").encode()
        self._display.vvvv(f"Write command '{put_cmd}'")
        self._shell_session._poller.flush_stderr()
        self._shell_session._poller.stdin_write(put_cmd)
        # Ensure server is listening
        self._shell_session._poller.match_expr(expr="Listening")
        self._display.vvvv("Server is listening...")

        # Write data into socket
        self._socket_write(port=self._local_port, in_path=in_path)

        # Ensure nc command has ended on remote host
        self._shell_session._poller.match_expr(expr=mark_end)

        self._display.vvvv(f"End of polling, stderr = {self._shell_session._poller.flush_stderr()}")

    def fetch_file(self, in_path: str, out_path: str) -> None:
        self._shell_session._poller.flush_stderr()
        mark_end = "".join([random.choice(string.ascii_lowercase + string.digits) for i in range(12)])
        fetch_cmd = f"sudo nc -v -l {self._host_port} < {in_path}; printf '{mark_end}'"
        fetch_cmd = (fetch_cmd + "\n").encode()
        self._display.vvvv(f"Write command '{fetch_cmd}'")
        self._shell_session._poller.stdin_write(fetch_cmd)

        # Ensure server is listening
        self._shell_session._poller.match_expr(expr="Listening")
        self._display.vvvv("Server is listening...")
        # Read data from socket
        self._socket_read(port=self._local_port, out_path=out_path)
        # Ensure nc command has ended on remote host
        self._shell_session._poller.match_expr(expr=mark_end)

        self._display.vvvv(f"End of polling, stderr = {self._shell_session._poller.flush_stderr()}")
