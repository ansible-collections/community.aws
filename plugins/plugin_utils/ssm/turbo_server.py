# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import argparse
import asyncio
import json
import os
import pickle
import signal
import sys
import traceback
import uuid
from datetime import datetime


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


def trace_value(msg):
    with open("/Users/aubinho/work/aws/connection_ssm/turbo/trace.txt", "a+") as f:
        f.write(f"{msg}\n")


class SSMTurboMode:
    def __init__(self, socket_path, ttl):
        self.socket_path = socket_path
        self.ttl = ttl
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

        def _terminate(result):
            writer.write(json.dumps(result).encode())
            writer.close()

        result = {
            "returncode": 1,
            "stdout": "some content received from server",
            "stderr": "some flush error",
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

        # trace_value(f"Socket path: {self.socket_path}")

        # if os.path.exists(self.socket_path):
        #     trace_value("Socket path exist going to remove it")
        #     os.remove(self.socket_path)
        # trace_value("loop.run_until_complete...")
        # self.loop.run_until_complete(asyncio.start_unix_server(self.handle, path=self.socket_path))
        # trace_value("chmod socket...")
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
    parser.add_argument("--socket-path")
    parser.add_argument("--ttl", default=15, type=int)
    parser.add_argument("--fork", action="store_true")

    args = parser.parse_args()
    if args.fork:
        trace_value("forking process")
        fork_process()

    server = SSMTurboMode(socket_path=args.socket_path, ttl=args.ttl)
    server.start()
