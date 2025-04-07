# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import os
import random
import re
import select
import string
from typing import Any
from typing import Callable
from typing import Iterator
from typing import List
from typing import Tuple

from ansible.module_utils._text import to_bytes
from ansible.module_utils._text import to_text
from ansible.plugins.shell.powershell import _common_args

from .common import SSMDisplay
from .common import StdoutPoller
from .turbo_client import turbo_exec_command


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


class CommandManager(SSMDisplay):
    def __init__(self, shell: Any, session: Any, stdout_r: Any, ssm_timeout: int, verbosity_display: Callable) -> None:
        super(CommandManager, self).__init__(verbosity_display=verbosity_display)
        self._shell = shell
        stdout = os.fdopen(stdout_r, "rb", 0)
        poller = select.poll()
        poller.register(stdout, select.POLLIN)
        self._poller = StdoutPoller(session=session, stdout=stdout, poller=poller, timeout=ssm_timeout)
        self.is_windows = bool(getattr(self._shell, "SHELL_FAMILY", "") == "powershell")

    @property
    def poller(self) -> Any:
        return self._poller

    @property
    def has_timeout(self) -> bool:
        return self._poller._has_timeout

    def _wrap_command(self, cmd: str, mark_start: str, mark_end: str) -> str:
        """Wrap command so stdout and status can be extracted"""
        if self.is_windows:
            if not cmd.startswith(" ".join(_common_args) + " -EncodedCommand"):
                cmd = self._shell._encode_script(cmd, preserve_rc=True)
            cmd = cmd + "; echo " + mark_start + "\necho " + mark_end + "\n"
        else:
            cmd = (
                f"printf '%s\\n' '{mark_start}';\n"
                f"echo | {cmd};\n"
                f"printf '\\n%s\\n%s\\n' \"$?\" '{mark_end}';\n"
            )  # fmt: skip

        self.verbosity_display(4, f"_wrap_command: \n'{to_text(cmd)}'")
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

    def exec_communicate(self, mark_start: str, mark_begin: str, mark_end: str) -> Tuple[int, str, str]:
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
            self.verbosity_display(4, f"EXEC stdout line: \n{line}")

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
                    self.verbosity_display(4, f"POST_PROCESS: \n{to_text(stdout)}")
                    returncode, stdout = self._post_process(stdout, mark_begin)
                    self.verbosity_display(4, f"POST_PROCESSED: \n{to_text(stdout)}")
                    break
                stdout = stdout + line

        # see https://github.com/pylint-dev/pylint/issues/8909)
        return (returncode, stdout, self._poller.flush_stderr())  # pylint: disable=unreachable

    def exec_command(self, cmd: str, instance_id: str, region_name: str) -> Tuple[int, str, str]:
        self.verbosity_display(3, f"EXEC: {to_text(cmd)}")

        turbo_result = turbo_exec_command(command=cmd, instance_id=instance_id, region_name=region_name, verbosity_display=self.verbosity_display)
        self.verbosity_display(4, f"TURBO COMMAND RESULT: {turbo_result}")

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

        return self.exec_communicate(mark_start, mark_begin, mark_end)
