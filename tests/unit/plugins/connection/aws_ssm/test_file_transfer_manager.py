# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from unittest.mock import MagicMock

import pytest

from ansible.errors import AnsibleError

from ansible_collections.community.aws.plugins.plugin_utils.ssm.filetransfermanager import CommandResult
from ansible_collections.community.aws.plugins.plugin_utils.ssm.filetransfermanager import FileTransferManager


class TestFileTransferManager:
    @pytest.fixture
    def mock_connection(self):
        """Creates a mock connection object."""
        mock_conn = MagicMock()
        mock_conn._s3_client = MagicMock()
        mock_conn._generate_commands.return_value = ([{"command": "test-cmd", "method": "put"}], {})
        return mock_conn

    @pytest.fixture
    def file_transfer_manager(self, mock_connection):
        """Creates an instance of FileTransferManager with a mock connection."""
        return FileTransferManager(mock_connection)

    def test_escape_path(self):
        assert FileTransferManager._escape_path("path\\with\\backslashes") == "path/with/backslashes"

    @pytest.mark.parametrize(
        "ssm_action, handler_method, expected_output, in_path, out_path",
        [
            ("get", "_handle_get", "Success", "local_in.txt", "remote_out.txt"),
            ("put", "_handle_put", "Uploaded", "local_in2.txt", "remote_out2.txt"),
            ("get", "_handle_get", "Success", "input_3.txt", "output_3.txt"),
            ("put", "_handle_put", "Uploaded", "input_4.txt", "output_4.txt"),
        ],
    )
    def test_file_transport_command(
        self,
        file_transfer_manager,
        mock_connection,
        ssm_action: str,
        handler_method: str,
        expected_output: str,
        in_path: str,
        out_path: str,
    ):
        mock_connection._s3_client.delete_object = MagicMock()
        handler_mock = MagicMock(return_value=CommandResult(returncode=0, stdout=expected_output, stderr=""))
        setattr(file_transfer_manager, handler_method, handler_mock)

        result = file_transfer_manager._file_transport_command(in_path, out_path, ssm_action)

        handler_mock.assert_called_once()
        mock_connection._s3_client.delete_object.assert_called_once()
        assert result["returncode"] == 0
        assert result["stdout"] == expected_output
        assert result["stderr"] == ""

    @pytest.mark.parametrize(
        "command_input, expected_returncode, expected_stdout",
        [
            ("echo test", 0, "Command executed"),
            ("failing command", 1, "Error message"),
        ],
    )
    def test_exec_transport_commands(
        self, file_transfer_manager, mock_connection, command_input: str, expected_returncode: int, expected_stdout: str
    ):
        # Mocking exec_command for the given command input
        mock_connection.exec_command.return_value = CommandResult(
            returncode=expected_returncode,
            stdout=expected_stdout,
            stderr="" if expected_returncode == 0 else "Error message",
        )

        commands = [{"command": command_input}]

        if expected_returncode == 0:
            result = file_transfer_manager._exec_transport_commands("input.txt", "output.txt", commands)
            assert result["returncode"] == expected_returncode
            assert result["stdout"] == expected_stdout
        else:
            with pytest.raises(AnsibleError, match=r"failed to transfer file to input.txt output.txt:\s*Error message"):
                file_transfer_manager._exec_transport_commands("input.txt", "output.txt", commands)
