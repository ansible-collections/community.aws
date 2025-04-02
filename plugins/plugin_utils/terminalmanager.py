# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import random
import re
import string
from typing import Any
from typing import Callable

from ansible.module_utils._text import to_bytes
from ansible.module_utils._text import to_text
from ansible.plugins.shell.powershell import _common_args


class TerminalManager:
    MARK_LENGTH = 26

    def __init__(self, session: Any, stdout: Any, poller: Callable, verbosity_display: Callable) -> None:
        self._session = session
        self._stdout = stdout
        self._poller = poller
        self.verbosity_display = verbosity_display

    def prepare_terminal(self, is_windows: bool) -> None:
        """perform any one-time terminal settings"""
        # No Windows setup for now
        if is_windows:
            return

        # Ensure SSM Session has started
        self.ensure_ssm_session_has_started()

        # Disable echo command
        self.disable_echo_command()  # pylint: disable=unreachable

        # Disable prompt command
        self.disable_prompt_command()  # pylint: disable=unreachable

        self.verbosity_display(4, "PRE Terminal configured")  # pylint: disable=unreachable

    def wrap_command(self, cmd: str, mark_start: str, mark_end: str, is_windows: bool, shell: Any) -> str:
        """Wrap command so stdout and status can be extracted"""
        if is_windows:
            if not cmd.startswith(" ".join(_common_args) + " -EncodedCommand"):
                cmd = shell._encode_script(cmd, preserve_rc=True)
            cmd = cmd + "; echo " + mark_start + "\necho " + mark_end + "\n"
        else:
            cmd = (
                f"printf '%s\\n' '{mark_start}';\n"
                f"echo | {cmd};\n"
                f"printf '\\n%s\\n%s\\n' \"$?\" '{mark_end}';\n"
            )  # fmt: skip

        self.verbosity_display(4, f"wrap_command: \n'{to_text(cmd)}'")
        return cmd

    def disable_echo_command(self) -> None:
        """Disable echo command from the host"""
        disable_echo_cmd = to_bytes("stty -echo\n", errors="surrogate_or_strict")

        # Send command
        self.verbosity_display(4, f"DISABLE ECHO Disabling Prompt: \n{disable_echo_cmd}")
        self._session.stdin.write(disable_echo_cmd)

        stdout = ""
        for poll_result in self._poller("DISABLE ECHO", disable_echo_cmd):
            if poll_result:
                stdout += to_text(self._stdout.read(1024))
                self.verbosity_display(4, f"DISABLE ECHO stdout line: \n{to_bytes(stdout)}")
                match = str(stdout).find("stty -echo")
                if match != -1:
                    break

    def disable_prompt_command(self) -> None:
        """Disable prompt command from the host"""
        end_mark = "".join([random.choice(string.ascii_letters) for i in range(self.MARK_LENGTH)])
        disable_prompt_cmd = to_bytes(
            "PS1='' ; bind 'set enable-bracketed-paste off'; printf '\\n%s\\n' '" + end_mark + "'\n",
            errors="surrogate_or_strict",
        )
        disable_prompt_reply = re.compile(r"\r\r\n" + re.escape(end_mark) + r"\r\r\n", re.MULTILINE)

        # Send command
        self.verbosity_display(4, f"DISABLE PROMPT Disabling Prompt: \n{disable_prompt_cmd}")
        self._session.stdin.write(disable_prompt_cmd)

        stdout = ""
        for poll_result in self._poller("DISABLE PROMPT", disable_prompt_cmd):
            if poll_result:
                stdout += to_text(self._stdout.read(1024))
                self.verbosity_display(4, f"DISABLE PROMPT stdout line: \n{to_bytes(stdout)}")
                if disable_prompt_reply.search(stdout):
                    break

    def ensure_ssm_session_has_started(self) -> None:
        """Ensure the SSM session has started on the host. We poll stdout
        until we match the following string 'Starting session with SessionId'
        """
        stdout = ""
        for poll_result in self._poller("START SSM SESSION", "start_session"):
            if poll_result:
                stdout += to_text(self._stdout.read(1024))
                self.verbosity_display(4, f"START SSM SESSION stdout line: \n{to_bytes(stdout)}")
                match = str(stdout).find("Starting session with SessionId")
                if match != -1:
                    self.verbosity_display(4, "START SSM SESSION startup output received")
                    break
