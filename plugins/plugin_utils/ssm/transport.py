# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import re
import socket
import string
import time
from typing import Any
from typing import Callable
from typing import Optional

from .common import SSMDisplay
from .common import SSMSessionManager


class PortForwardingFileTransportManager(SSMDisplay):
    DEFAULT_HOST_PORT = 80

    def __init__(
        self, host_port_number: Optional[int], local_port_number: Optional[str], verbosity_display: Callable
    ) -> None:
        super(PortForwardingFileTransportManager, self).__init__(verbosity_display=verbosity_display)

        self.host_port_number = host_port_number or self.DEFAULT_HOST_PORT
        self.local_port_number = local_port_number
        self._portforwarding_session = None
        self._shell_session = None

    def start_session(
        self,
        client: Any,
        instance_id: str,
        executable: str,
        region: Optional[str],
        profile: Optional[str],
        ssm_timeout: int,
    ) -> None:
        # Create Port forwarding Session
        parameters = {}
        if self.local_port_number:
            parameters["localPortNumber"] = [str(self.local_port_number)]
        if self.host_port_number:
            parameters["portNumber"] = [str(self.host_port_number)]

        self._portforwarding_session = SSMSessionManager(
            client=client,
            document_name="AWS-StartPortForwardingSession",
            document_parameters=parameters,
            instance_id=instance_id,
            executable=executable,
            region=region,
            profile=profile,
            ssm_timeout=ssm_timeout,
            verbosity_display=self.verbosity_display,
        )

        match_expr = re.compile(r"Port ([0-9]+) opened for sessionId")
        content = self._portforwarding_session._poller.match_expr(expr=match_expr.search)
        match = match_expr.search(content)
        self.local_port_number = int(match.group(1))
        self.verbosity_display(4, f"SSM PORT FORWARDING - Local port '{self.local_port_number}'")

        # Start shell session
        self._shell_session = SSMSessionManager(
            client=client,
            instance_id=instance_id,
            executable=executable,
            region=region,
            profile=profile,
            ssm_timeout=ssm_timeout,
            verbosity_display=self.verbosity_display,
        )

    def _socket_connect(self, session: Any, port: int, host: str = "localhost", max_attempts=10) -> None:
        """Connect to socket"""
        for attempt in range(max_attempts):
            try:
                session.connect((host, port))
                break
            except OSError:
                if attempt == max_attempts - 1:
                    self.verbosity_display(
                        4, f"SOCKET _CONNECT: Failed to intiate socket connection on '{host}:{port}'"
                    )
                    raise
                time.sleep(0.05)

    def _socket_read(self, port: int, out_path: Optional[str] = None) -> None:
        self.verbosity_display(4, f"Read content from socket on port '{port}'...")
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
        self.verbosity_display(4, "Socket connection closed.")

    def _socket_write(self, port: int, in_path: str) -> None:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as session:
            self._socket_connect(session=session, port=port)
            with open(in_path, "rb") as f:
                session.sendall(f.read())

    def put_file(self, in_path: str, out_path: str) -> None:
        # Start listener on Remote host
        mark_end = "".join([random.choice(string.ascii_lowercase + string.digits) for i in range(12)])
        put_cmd = f"sudo nc -l -v -p {str(self.host_port_number)} > {out_path}; printf '{mark_end}'"
        put_cmd = (put_cmd + "\n").encode()
        self.verbosity_display(4, f"Write command '{put_cmd}'")
        self._shell_session._poller.flush_stderr()
        self._shell_session._poller.stdin_write(put_cmd)
        # Ensure server is listening
        self._shell_session._poller.match_expr(expr="Listening")
        self.verbosity_display(4, "Server is listening...")

        # Write data into socket
        self._socket_write(port=self.local_port_number, in_path=in_path)

        # Ensure nc command has ended on remote host
        self._shell_session._poller.match_expr(expr=mark_end)

        self.verbosity_display(4, f"End of polling, stderr = {self._shell_session._poller.flush_stderr()}")

    def fetch_file(self, in_path: str, out_path: str) -> None:
        self._shell_session._poller.flush_stderr()
        mark_end = "".join([random.choice(string.ascii_lowercase + string.digits) for i in range(12)])
        fetch_cmd = f"sudo nc -v -l {self.host_port_number} < {in_path}; printf '{mark_end}'"
        fetch_cmd = (fetch_cmd + "\n").encode()
        self.verbosity_display(4, f"Write command '{fetch_cmd}'")
        self._shell_session._poller.stdin_write(fetch_cmd)

        # Ensure server is listening
        self._shell_session._poller.match_expr(expr="Listening")
        self.verbosity_display(4, "Server is listening...")
        # Read data from socket
        self._socket_read(port=self.local_port_number, out_path=out_path)
        # Ensure nc command has ended on remote host
        self._shell_session._poller.match_expr(expr=mark_end)

        self.verbosity_display(4, f"End of polling, stderr = {self._shell_session._poller.flush_stderr()}")
