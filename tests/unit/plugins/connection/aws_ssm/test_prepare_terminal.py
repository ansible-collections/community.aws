# -*- coding: utf-8 -*-

# This file is part of Ansible
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# While it may seem appropriate to import our custom fixtures here, the pytest_ansible pytest plugin
# isn't as agressive as the ansible_test._util.target.pytest.plugins.ansible_pytest_collections plugin
# when it comes to rewriting the import paths and as such we can't import fixtures via their
# absolute import path or across collections.


from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from ansible_collections.amazon.aws.plugins.module_utils.botocore import HAS_BOTO3

from ansible_collections.community.aws.plugins.connection.aws_ssm import TerminalManager

if not HAS_BOTO3:
    pytestmark = pytest.mark.skip("test_poll.py requires the python modules 'boto3' and 'botocore'")


def poll_mock(x, y):
    while poll_mock.results:
        yield poll_mock.results.pop(0)
    raise TimeoutError("-- poll_stdout_mock() --- Process has timeout...")


@pytest.mark.parametrize(
    "stdout_lines,timeout_failure",
    [
        (["Starting ", "session ", "with SessionId"], False),
        (["Starting session", " with SessionId"], False),
        (["Init - Starting", " session", " with SessionId"], False),
        (["Starting", " session", " with SessionId "], False),
        (["Starting ", "session"], True),
        (["Starting ", "session  with Session"], True),
        (["session ", "with SessionId"], True),
    ],
)
@patch("ansible_collections.community.aws.plugins.connection.aws_ssm.to_bytes")
@patch("ansible_collections.community.aws.plugins.connection.aws_ssm.to_text")
def test_ensure_ssm_session_has_started(m_to_text, m_to_bytes, connection_aws_ssm, stdout_lines, timeout_failure):
    m_to_text.side_effect = str
    m_to_bytes.side_effect = str
    connection_aws_ssm.get_option = MagicMock(return_value=10)

    mock_session = MagicMock()
    mock_session.poll.return_value = None
    connection_aws_ssm._session = mock_session

    connection_aws_ssm._stdout = MagicMock()
    connection_aws_ssm._stdout.read.side_effect = stdout_lines

    poll_mock.results = [True for i in range(len(stdout_lines))]
    connection_aws_ssm.poll = MagicMock()
    connection_aws_ssm.poll.side_effect = poll_mock

    if not hasattr(connection_aws_ssm, "terminal_manager"):
        connection_aws_ssm.terminal_manager = TerminalManager(
            session=connection_aws_ssm._session,
            stdout=connection_aws_ssm._stdout,
            poller=connection_aws_ssm.poll,
            verbosity_display=connection_aws_ssm.verbosity_display,
        )

    poll_mock.results = [True for i in range(len(stdout_lines))]
    connection_aws_ssm.poll = MagicMock()
    connection_aws_ssm.poll.side_effect = poll_mock

    if timeout_failure:
        with pytest.raises(TimeoutError):
            connection_aws_ssm.terminal_manager.ensure_ssm_session_has_started()
    else:
        connection_aws_ssm.terminal_manager.ensure_ssm_session_has_started()


@pytest.mark.parametrize(
    "stdout_lines,timeout_failure",
    [
        (["stty -echo"], False),
        (["stty ", "-echo"], False),
        (["stty"], True),
        (["stty ", "-ech"], True),
    ],
)
@patch("ansible_collections.community.aws.plugins.plugin_utils.terminalmanager.to_bytes")
@patch("ansible_collections.community.aws.plugins.plugin_utils.terminalmanager.to_text")
def test_disable_echo_command(m_to_text, m_to_bytes, connection_aws_ssm, stdout_lines, timeout_failure):
    m_to_text.side_effect = str
    m_to_bytes.side_effect = lambda x, **kw: str(x)
    connection_aws_ssm._stdout.read = MagicMock()

    connection_aws_ssm._stdout.read.side_effect = stdout_lines

    poll_mock.results = [True for i in range(len(stdout_lines))]
    connection_aws_ssm.poll = MagicMock()
    connection_aws_ssm.poll.side_effect = poll_mock

    if not hasattr(connection_aws_ssm, "terminal_manager"):
        connection_aws_ssm.terminal_manager = TerminalManager(
            session=connection_aws_ssm._session,
            stdout=connection_aws_ssm._stdout,
            poller=connection_aws_ssm.poll,
            verbosity_display=connection_aws_ssm.verbosity_display,
        )

    if timeout_failure:
        with pytest.raises(TimeoutError):
            connection_aws_ssm.terminal_manager.disable_echo_command()
    else:
        connection_aws_ssm.terminal_manager.disable_echo_command()

    connection_aws_ssm._session.stdin.write.assert_called_once_with("stty -echo\n")


@pytest.mark.parametrize("timeout_failure", [True, False])
@patch("ansible_collections.community.aws.plugins.plugin_utils.terminalmanager.random")
@patch("ansible_collections.community.aws.plugins.plugin_utils.terminalmanager.to_bytes")
@patch("ansible_collections.community.aws.plugins.plugin_utils.terminalmanager.to_text")
def test_disable_prompt_command(m_to_text, m_to_bytes, m_random, connection_aws_ssm, timeout_failure):
    m_to_text.side_effect = str
    m_to_bytes.side_effect = lambda x, **kw: str(x)
    connection_aws_ssm._stdout.read = MagicMock()

    connection_aws_ssm.poll = MagicMock()
    connection_aws_ssm.poll.side_effect = poll_mock

    if not hasattr(connection_aws_ssm, "terminal_manager"):
        connection_aws_ssm.terminal_manager = TerminalManager(
            session=connection_aws_ssm._session,
            stdout=connection_aws_ssm._stdout,
            poller=connection_aws_ssm.poll,
            verbosity_display=connection_aws_ssm.verbosity_display,
        )

    m_random.choice = MagicMock()
    m_random.choice.side_effect = lambda x: "a"

    end_mark = "".join(["a" for i in range(connection_aws_ssm.MARK_LENGTH)])

    connection_aws_ssm._stdout.read.return_value = (
        f"\r\r\n{end_mark}\r\r\n" if not timeout_failure else "unmatching value"
    )
    poll_mock.results = [True]

    prompt_cmd = f"PS1='' ; bind 'set enable-bracketed-paste off'; printf '\\n%s\\n' '{end_mark}'\n"

    if timeout_failure:
        with pytest.raises(TimeoutError):
            connection_aws_ssm.terminal_manager.disable_prompt_command()
    else:
        connection_aws_ssm.terminal_manager.disable_prompt_command()

    connection_aws_ssm._session.stdin.write.assert_called_once_with(prompt_cmd)
