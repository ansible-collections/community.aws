# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import argparse
import asyncio
import json
import os
import pickle
import pty
import random
import re
import select
import signal
import string
import subprocess
import sys
import time
import traceback
import uuid
from datetime import datetime
from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import NoReturn
from typing import Optional
from typing import Tuple
from typing import Union

try:
    import boto3
except ImportError:
    pass

from ansible.errors import AnsibleConnectionFailure
from ansible.module_utils._text import to_bytes
from ansible.module_utils._text import to_text
from ansible.plugins.shell.powershell import _common_args


@staticmethod
def generate_mark() -> str:
    """Generates a random string of characters to delimit SSM CLI commands"""
    mark = "".join([random.choice(string.ascii_letters) for i in range(26)])
    return mark


def chunks(lst: List, n: int) -> Iterator[List[Any]]:
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]  # fmt: skip


def filter_ansi(line: str, is_windows: bool) -> str:
    """Remove any ANSI terminal control codes.

    :param line: The input line.
    :param is_windows: Whether the output is coming from a Windows host.
    :returns: The result line.
    """
    line = to_text(line)

    if is_windows:
        osc_filter = re.compile(r"\x1b\][^\x07]*\x07")
        line = osc_filter.sub("", line)
        ansi_filter = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]")
        line = ansi_filter.sub("", line)

        # Replace or strip sequence (at terminal width)
        line = line.replace("\r\r\n", "\n")
        if len(line) == 201:
            line = line[:-1]

    return line


def encode_script(shell: Any, cmd: str) -> str:
    result = cmd
    if getattr(shell, "SHELL_FAMILY", "") == "powershell" and not cmd.startswith(
        " ".join(_common_args) + " -EncodedCommand"
    ):
        result = shell._encode_script(cmd, preserve_rc=True)
    return result


class CacheDisplay:
    trace_file = None
    file_handler = None

    @staticmethod
    def display(message):
        if CacheDisplay.trace_file:
            if CacheDisplay.file_handler is None:
                CacheDisplay.file_handler = open(CacheDisplay.trace_file, "w")
            CacheDisplay.file_handler.write(message + "\n")
            CacheDisplay.file_handler.flush()


class StdoutPoller:
    def __init__(self, session: Any, stdout: Any, poller: Any, timeout: int) -> None:
        self._stdout = stdout
        self._poller = poller
        self._session = session
        self._timeout = timeout
        self._has_timeout = False

    def readline(self):
        return self._stdout.readline()

    def has_data(self, timeout: int = 1000) -> bool:
        return bool(self._poller.poll(timeout))

    def read_stdout(self, length: int = 1024) -> str:
        return self._stdout.read(length).decode("utf-8")

    def stdin_write(self, value: Union[str | bytes]) -> None:
        self._session.stdin.write(value)

    def poll(self) -> NoReturn:
        start = round(time.time())
        yield self.has_data()
        while self._session.poll() is None:
            remaining = start + self._timeout - round(time.time())
            if remaining < 0:
                self._has_timeout = True
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


class SSMSessionManager:
    def __init__(
        self,
        client: Any,
        instance_id: str,
        executable: str,
        region: Optional[str],
        profile: Optional[str],
        ssm_timeout: int,
        document_name: Optional[str] = None,
        document_parameters: Optional[Dict] = None,
    ):
        self._client = client
        params = {"Target": instance_id}
        if document_name:
            params["DocumentName"] = document_name
        if document_parameters:
            params["Parameters"] = document_parameters

        try:
            response = self._client.start_session(**params)
            self._session_id = response["SessionId"]
            CacheDisplay.display(f"Start session - SessionId: {self._session_id}")

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
            CacheDisplay.display(f"Terminating AWS Session: {self._session_id}")
            self._client.terminate_session(SessionId=self._session_id)
        if self._session:
            CacheDisplay.display("Terminating subprocess.Popen session")
            self._session.terminate()


class CommandManager:
    def __init__(self, is_windows: bool, session: Any, stdout_r: Any, ssm_timeout: int) -> None:
        stdout = os.fdopen(stdout_r, "rb", 0)
        poller = select.poll()
        poller.register(stdout, select.POLLIN)
        self._poller = StdoutPoller(session=session, stdout=stdout, poller=poller, timeout=ssm_timeout)
        self.is_windows = is_windows

    @property
    def poller(self) -> Any:
        return self._poller

    @property
    def has_timeout(self) -> bool:
        return self._poller._has_timeout

    def _wrap_command(self, cmd: str, mark_start: str, mark_end: str) -> str:
        """Wrap command so stdout and status can be extracted"""
        if self.is_windows:
            cmd = f"{cmd}; echo {mark_start}\necho {mark_end}\n"
        else:
            cmd = (
                f"printf '%s\\n' '{mark_start}';\n"
                f"echo | {cmd};\n"
                f"printf '\\n%s\\n%s\\n' \"$?\" '{mark_end}';\n"
            )  # fmt: skip

        CacheDisplay.display(f"_wrap_command: \n'{to_text(cmd)}'")
        return cmd

    def _post_process(self, stdout: str, mark_begin: str) -> Tuple[str, str]:
        """extract command status and strip unwanted lines"""

        if not self.is_windows:
            # Get command return code
            returncode = int(stdout.splitlines()[-2])

            # Throw away final lines
            for _x in range(0, 3):
                stdout = stdout[:stdout.rfind('\n')]  # fmt: skip

            return (returncode, stdout)

        # Windows is a little more complex
        # Value of $LASTEXITCODE will be the line after the mark
        trailer = stdout[stdout.rfind(mark_begin):]  # fmt: skip
        last_exit_code = trailer.splitlines()[1]
        if last_exit_code.isdigit:
            returncode = int(last_exit_code)
        else:
            returncode = -1
        # output to keep will be before the mark
        stdout = stdout[:stdout.rfind(mark_begin)]  # fmt: skip

        # If the return code contains #CLIXML (like a progress bar) remove it
        clixml_filter = re.compile(r"#<\sCLIXML\s<Objs.*</Objs>")
        stdout = clixml_filter.sub("", stdout)

        # If it looks like JSON remove any newlines
        if stdout.startswith("{"):
            stdout = stdout.replace("\n", "")

        return (returncode, stdout)

    def _exec_communicate(self, mark_start: str, mark_begin: str, mark_end: str) -> Tuple[int, str, str]:
        """Interact with session.
        Read stdout between the markers until 'mark_end' is reached.

        :param cmd: The command being executed.
        :param mark_start: The marker which starts the output.
        :param mark_begin: The begin marker.
        :param mark_end: The end marker.
        :returns: A tuple with the return code, the stdout and the stderr content.
        """
        # Read stdout between the markers
        stdout = ""
        win_line = ""
        begin = False
        returncode = None
        for poll_result in self._poller.poll():
            if not poll_result:
                continue

            line = filter_ansi(self._poller.readline(), self.is_windows)
            CacheDisplay.display(f"EXEC stdout line: \n{line}")

            if not begin and self.is_windows:
                win_line = win_line + line
                line = win_line

            if mark_start in line:
                begin = True
                if not line.startswith(mark_start):
                    stdout = ""
                continue
            if begin:
                if mark_end in line:
                    CacheDisplay.display(f"POST_PROCESS: \n{to_text(stdout)}")
                    returncode, stdout = self._post_process(stdout, mark_begin)
                    CacheDisplay.display(f"POST_PROCESSED: \n{to_text(stdout)}")
                    break
                stdout = stdout + line

        # see https://github.com/pylint-dev/pylint/issues/8909)
        return (returncode, stdout, self._poller.flush_stderr())  # pylint: disable=unreachable

    def exec_command(self, cmd: str) -> Tuple[int, str, str]:
        CacheDisplay.display(f"EXEC: {to_text(cmd)}")

        mark_begin = generate_mark()
        if self.is_windows:
            mark_start = mark_begin + " $LASTEXITCODE"
        else:
            mark_start = mark_begin
        mark_end = generate_mark()

        # Wrap command in markers accordingly for the shell used
        cmd = self._wrap_command(cmd, mark_start, mark_end)

        self._poller.flush_stderr()
        for chunk in chunks(cmd, 1024):
            self._poller.stdin_write(to_bytes(chunk, errors="surrogate_or_strict"))

        return self._exec_communicate(mark_start, mark_begin, mark_end)


def fork_process():
    """
    This function performs the double fork process to detach from the
    parent process and execute.
    """
    pid = os.fork()

    if pid == 0:
        fd = os.open(os.devnull, os.O_RDWR)

        # clone stdin/out/err
        for num in range(3):
            if fd != num:
                os.dup2(fd, num)

        if fd not in range(3):
            os.close(fd)

        pid = os.fork()
        if pid > 0:
            os._exit(0)

        # get new process session and detach
        sid = os.setsid()
        if sid == -1:
            raise Exception("Unable to detach session while daemonizing")

        # avoid possible problems with cwd being removed
        os.chdir("/")

        pid = os.fork()
        if pid > 0:
            sys.exit(0)  # pylint: disable=ansible-bad-function
    else:
        sys.exit(0)  # pylint: disable=ansible-bad-function
    return pid


class CommandHandler:
    def __init__(self, args: Any) -> None:
        for attr in (
            "instance_id",
            "ssm_timeout",
            "reconnection_retries",
            "access_key_id",
            "secret_access_key",
            "session_token",
            "profile",
            "region",
            "ssm_document",
            "executable",
            "socket_path",
            "is_windows",
        ):
            setattr(self, attr, getattr(args, attr))

        self.client = None
        self.session_id = None
        self.session = None
        self.file_handler = open(f"{self.socket_path}.trace", "a")
        self.command_mgr = None

    def __del__(self) -> None:
        if self.session_id and self.client:
            if self.command_mgr.has_timeout:
                self.session.terminate()
            else:
                cmd = b"\nexit\n"
                self.session.communicate(cmd)
            self.client.terminate_session(SessionId=self.session_id)
        if self.file_handler:
            self.file_handler.close()

    def _init_client(self) -> Any:
        if not self.client:
            session_args = {
                "aws_access_key_id": getattr(self, "access_key_id"),
                "aws_secret_access_key": getattr(self, "secret_access_key"),
                "aws_session_token": getattr(self, "session_token"),
                "region_name": getattr(self, "region"),
            }

            if (profile := getattr(self, "profile")) is not None:
                session_args["profile_name"] = profile
            session = boto3.session.Session(**session_args)
            self.client = session.client("ssm")

    def _init_session(self) -> None:
        self._init_client()
        if not self.session:
            ssm_session_args = {"Target": self.instance_id, "Parameters": {}}
            if (document_name := getattr(self, "ssm_document")) is not None:
                ssm_session_args["DocumentName"] = document_name
            response = self.client.start_session(**ssm_session_args)
            self._session_id = response["SessionId"]
            CacheDisplay.display(f"SSM CONNECTION ID: {self._session_id}")

            region_name = getattr(self, "region")
            profile_name = getattr(self, "profile") or ""
            cmd = [
                self.executable,
                json.dumps(response),
                region_name,
                "StartSession",
                profile_name,
                json.dumps({"Target": self.instance_id}),
                self.client.meta.endpoint_url,
            ]

            CacheDisplay.display(f"SSM COMMAND: {(cmd)}")

            stdout_r, stdout_w = pty.openpty()
            self.session = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=stdout_w,
                stderr=subprocess.PIPE,
                close_fds=True,
                bufsize=0,
            )

            os.close(stdout_w)
            self.command_mgr = CommandManager(
                is_windows=self.is_windows,
                session=self.session,
                stdout_r=stdout_r,
                ssm_timeout=self.ssm_timeout,
            )

            # For non-windows Hosts: Ensure the session has started, and disable command echo and prompt.
            if not self.is_windows:
                self.command_mgr.poller.match_expr(expr="Starting session with SessionId")

                # Disable echo command from the host
                disable_echo_cmd = to_bytes("stty -echo\n", errors="surrogate_or_strict")
                CacheDisplay.display(f"DISABLE ECHO Disabling Prompt: \n{disable_echo_cmd}")
                self.command_mgr.poller.stdin_write(disable_echo_cmd)
                self.command_mgr.poller.match_expr(expr="stty -echo")

                # Disable prompt command from the host
                end_mark = "".join([random.choice(string.ascii_letters) for i in range(26)])
                disable_prompt_cmd = to_bytes(
                    "PS1='' ; bind 'set enable-bracketed-paste off'; printf '\\n%s\\n' '" + end_mark + "'\n",
                    errors="surrogate_or_strict",
                )
                disable_prompt_reply = re.compile(r"\r\r\n" + re.escape(end_mark) + r"\r\r\n", re.MULTILINE)
                CacheDisplay.display(f"DISABLE PROMPT Disabling Prompt: \n{disable_prompt_cmd}")
                self.command_mgr.poller.stdin_write(disable_prompt_cmd)
                self.command_mgr.poller.match_expr(expr=disable_prompt_reply.search)

    def exec_command(self, command: str) -> Tuple[int, str, str]:
        self._init_session()
        return self.command_mgr.exec_command(command)


class SSMCaching:
    def __init__(self, args: Any):
        self.socket_path = args.socket_path
        self.ttl = args.ttl
        self.command_handler = CommandHandler(args)
        self.jobs_ongoing = {}

    async def ghost_killer(self):
        while True:
            await asyncio.sleep(self.ttl)
            running_jobs = {
                job_id: start_date
                for job_id, start_date in self.jobs_ongoing.items()
                if (datetime.now() - start_date).total_seconds() < 3600
            }
            if running_jobs:
                continue
            self.stop()

    async def handle(self, reader, writer):
        result = None
        self._watcher.cancel()
        self._watcher = self.loop.create_task(self.ghost_killer())
        job_id = str(uuid.uuid4())
        self.jobs_ongoing[job_id] = datetime.now()
        raw_data = await reader.read()

        if not raw_data:
            return

        command = pickle.loads(raw_data)
        returncode, stdout, stderr = self.command_handler.exec_command(command=command)

        def _terminate(result):
            writer.write(json.dumps(result).encode())
            writer.close()

        result = {
            "returncode": returncode,
            "stdout": stdout,
            "stderr": stderr,
            "command": command,
        }
        _terminate(result)
        del self.jobs_ongoing[job_id]

    def handle_exception(self, loop, context):
        e = context.get("exception")
        traceback.print_exception(type(e), e, e.__traceback__)
        self.stop()

    def start(self):
        # Support for python2.x versions has been dropped from collection
        if sys.version_info.minor >= 11:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
            self.loop.add_signal_handler(signal.SIGTERM, self.stop)
            self.loop.set_exception_handler(self.handle_exception)
            self._watcher = self.loop.create_task(self.ghost_killer())

            self.loop.run_until_complete(asyncio.start_unix_server(self.handle, path=self.socket_path))
            self.loop.run_forever()
        else:
            self.loop = asyncio.get_event_loop()
            self.loop.add_signal_handler(signal.SIGTERM, self.stop)
            self.loop.set_exception_handler(self.handle_exception)
            self._watcher = self.loop.create_task(self.ghost_killer())

            if sys.version_info.minor >= 10:
                # py3.10 drops the loop argument of create_task.
                self.loop.create_task(asyncio.start_unix_server(self.handle, path=self.socket_path))
            else:
                self.loop.create_task(asyncio.start_unix_server(self.handle, path=self.socket_path, loop=self.loop))
        self.loop.run_forever()

    def stop(self):
        os.unlink(self.socket_path)
        self.loop.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start a background daemon.")
    parser.add_argument("--socket-path", required=True)
    parser.add_argument("--ttl", default=60, type=int)
    parser.add_argument("--fork", action="store_true")
    parser.add_argument("--instance-id", required=True)
    parser.add_argument("--ssm-timeout", type=int, required=True)
    parser.add_argument("--reconnection-retries", type=int, required=True)
    parser.add_argument("--access-key-id", required=False)
    parser.add_argument("--secret-access-key", required=False)
    parser.add_argument("--session-token", required=False)
    parser.add_argument("--profile", required=False)
    parser.add_argument("--region", required=False)
    parser.add_argument("--ssm-document", required=False)
    parser.add_argument("--executable", required=True)
    parser.add_argument("--is-windows", type=bool, default=False)
    parser.add_argument("--trace", action="store_true")

    args = parser.parse_args()
    if args.fork:
        fork_process()

    if args.trace:
        CacheDisplay.trace_file = args.socket_path + ".trace"
    server = SSMCaching(args=args)
    server.start()
