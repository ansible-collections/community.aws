# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json
import os
import pty
import select
import subprocess
import time
from functools import wraps
from typing import Any
from typing import Callable
from typing import Dict
from typing import NoReturn
from typing import Optional
from typing import TypedDict
from typing import Union

from ansible.errors import AnsibleConnectionFailure
from ansible.errors import AnsibleError
from ansible.module_utils._text import to_text


def ssm_retry(func: Any) -> Any:
    """
    Decorator to retry in the case of a connection failure
    Will retry if:
    * an exception is caught
    Will not retry if
    * remaining_tries is <2
    * retries limit reached
    """

    @wraps(func)
    def wrapped(self, *args: Any, **kwargs: Any) -> Any:
        for attr in ("reconnection_retries", "verbosity_display"):
            if not hasattr(self, attr):
                raise AnsibleError(f"Cannot decorate this function with 'ssm_retry', missing attribute '{attr}'")
        remaining_tries = int(getattr(self, "reconnection_retries")) + 1
        cmd_summary = f"{args[0]}..."
        for attempt in range(remaining_tries):
            try:
                return_tuple = func(self, *args, **kwargs)
                self.verbosity_display(4, f"ssm_retry: (success) {to_text(return_tuple)}")
                break

            except (AnsibleConnectionFailure, Exception) as e:
                if attempt == remaining_tries - 1:
                    raise
                pause = 2**attempt - 1
                pause = min(pause, 30)

                if isinstance(e, AnsibleConnectionFailure):
                    msg = f"ssm_retry: attempt: {attempt}, cmd ({cmd_summary}), pausing for {pause} seconds"
                else:
                    msg = (
                        f"ssm_retry: attempt: {attempt}, caught exception({e})"
                        f"from cmd ({cmd_summary}),pausing for {pause} seconds"
                    )

                self.verbosity_display(2, msg)

                time.sleep(pause)

                # Do not attempt to reuse the existing session on retries
                # This will cause the SSM session to be completely restarted,
                # as well as reinitializing the boto3 clients
                if hasattr(self, "close"):
                    getattr(self, "close")()

                continue

        return return_tuple

    return wrapped


class CommandResult(TypedDict):
    """
    A dictionary that contains the executed command results.
    """

    returncode: int
    stdout_combined: str
    stderr_combined: str


class SSMDisplay:
    def __init__(self, verbosity_display: Callable[[int, str], None]):
        self.verbosity_display = verbosity_display


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


class SSMSessionManager(SSMDisplay):
    def __init__(
        self,
        client: Any,
        instance_id: str,
        executable: str,
        region: Optional[str],
        profile: Optional[str],
        ssm_timeout: int,
        verbosity_display: Callable,
        document_name: Optional[str] = None,
        document_parameters: Optional[Dict] = None,
    ):
        super(SSMSessionManager, self).__init__(verbosity_display=verbosity_display)

        self._client = client
        params = {"Target": instance_id}
        if document_name:
            params["DocumentName"] = document_name
        if document_parameters:
            params["Parameters"] = document_parameters

        try:
            response = self._client.start_session(**params)
            self._session_id = response["SessionId"]
            self.verbosity_display(4, f"Start session - SessionId: {self._session_id}")

            cmd = [
                executable,
                json.dumps(response),
                region,
                "StartSession",
                profile,
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
