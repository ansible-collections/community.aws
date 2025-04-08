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
import signal
import string
import subprocess
import sys
import traceback
import uuid
from datetime import datetime
from functools import wraps
from typing import Any
from typing import Tuple

try:
    import boto3
except ImportError:
    pass

from ansible.module_utils._text import to_bytes

from .command import CommandManager


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


def _ensure_connect(func: Any, name: str) -> Any:
    @wraps(func)
    def wrapped(self, *args: Any, **kwargs: Any) -> Any:
        if getattr(self, name) is name:
            getattr(self, f"_init_{name}")()
        return func(self, *args, **kwargs)

    return wrapped


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
        self.trace_level = 0
        if trace_level := getattr(args, "trace_level"):
            self.trace_level = trace_level

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

    def _display(self, level: int, message: str) -> None:
        if level >= self.trace_level:
            message = f"[{''.join(['V' for i in range(level)])}] {message}\n"
            self.file_handler(message)
            self.file_handler.flush()

    @_ensure_connect(name="client")
    def _init_session(self) -> None:
        if not self.session:
            ssm_session_args = {"Target": self.instance_id, "Parameters": {}}
            if (document_name := getattr(self, "ssm_document")) is not None:
                ssm_session_args["DocumentName"] = document_name
            response = self._client.start_session(**ssm_session_args)
            self._session_id = response["SessionId"]
            self.verbosity_display(4, f"SSM CONNECTION ID: {self._session_id}")

            region_name = getattr(self, "region")
            profile_name = getattr(self, "profile") or ""
            cmd = [
                self.executable,
                json.dumps(response),
                region_name,
                "StartSession",
                profile_name,
                json.dumps({"Target": self.instance_id}),
                self._client.meta.endpoint_url,
            ]

            self._display(4, f"SSM COMMAND: {(cmd)}")

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
                shell=self._shell,
                session=self.session,
                stdout_r=stdout_r,
                ssm_timeout=self.ssm_timeout,
                verbosity_display=self._display,
            )

            # For non-windows Hosts: Ensure the session has started, and disable command echo and prompt.
            if not self.is_windows:
                self.command_mgr.poller.match_expr(expr="Starting session with SessionId")

                # Disable echo command from the host
                disable_echo_cmd = to_bytes("stty -echo\n", errors="surrogate_or_strict")
                self._display(4, f"DISABLE ECHO Disabling Prompt: \n{disable_echo_cmd}")
                self.command_mgr.poller.stdin_write(disable_echo_cmd)
                self.command_mgr.poller.match_expr(expr="stty -echo")

                # Disable prompt command from the host
                end_mark = "".join([random.choice(string.ascii_letters) for i in range(self.MARK_LENGTH)])
                disable_prompt_cmd = to_bytes(
                    "PS1='' ; bind 'set enable-bracketed-paste off'; printf '\\n%s\\n' '" + end_mark + "'\n",
                    errors="surrogate_or_strict",
                )
                disable_prompt_reply = re.compile(r"\r\r\n" + re.escape(end_mark) + r"\r\r\n", re.MULTILINE)
                self._display(4, f"DISABLE PROMPT Disabling Prompt: \n{disable_prompt_cmd}")
                self.command_mgr.poller.stdin_write(disable_prompt_cmd)
                self.command_mgr.poller.match_expr(expr=disable_prompt_reply.search)

    @_ensure_connect(name="session")
    def exec_command(self, command: str) -> Tuple[int, str, str]:
        return self.command_mgr.exec_command(command)


class SSMTurboMode:
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
        # for python versions >= Python3.11
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.loop.add_signal_handler(signal.SIGTERM, self.stop)
        self.loop.set_exception_handler(self.handle_exception)
        self._watcher = self.loop.create_task(self.ghost_killer())

        self.loop.run_until_complete(asyncio.start_unix_server(self.handle, path=self.socket_path))
        self.loop.run_forever()

        # print(f"sys hex version: {sys.hexversion}")
        # self.loop = asyncio.get_event_loop()
        # self.loop.add_signal_handler(signal.SIGTERM, self.stop)
        # self.loop.set_exception_handler(self.handle_exception)
        # self._watcher = self.loop.create_task(self.ghost_killer())

        # if os.path.exists(self.socket_path):
        #     os.remove(self.socket_path)
        # self.loop.run_until_complete(asyncio.start_unix_server(self.handle, path=self.socket_path))
        # os.chmod(self.socket_path, 0o666)
        # self.loop.run_forever()

        # if sys.hexversion >= 0x30A00B1:
        #     # py3.10 drops the loop argument of create_task.
        #     self.loop.create_task(
        #         asyncio.start_unix_server(self.handle, path=self.socket_path)
        #     )
        # else:
        #     self.loop.create_task(
        #         asyncio.start_unix_server(
        #             self.handle, path=self.socket_path, loop=self.loop
        #         )
        #     )
        # self.loop.run_forever()

    def stop(self):
        os.unlink(self.socket_path)
        self.loop.stop()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start a background daemon.")
    parser.add_argument("--socket-path", required=True)
    parser.add_argument("--ttl", default=15, type=int)
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

    args = parser.parse_args()
    if args.fork:
        fork_process()

    server = SSMTurboMode(args=args)
    server.start()
