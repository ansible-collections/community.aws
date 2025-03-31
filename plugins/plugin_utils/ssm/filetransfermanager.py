# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import List

from ansible.errors import AnsibleError
from ansible.module_utils._text import to_bytes

from ansible_collections.community.aws.plugins.plugin_utils.ssm.common import CommandResult


class FileTransferManager:
    """Manages file transfers using S3 as an intermediary."""

    def __init__(self, connection):
        """
        Initializes the FileTransferManager with a given connection.

        :param connection: The connection object used for S3 and remote execution.
        """
        self.connection = connection

    @staticmethod
    def _escape_path(path: str) -> str:
        """
        Converts a file path to a safe format by replacing backslashes with forward slashes.

        :param path: The file path to escape.
        :return: The escaped file path.
        """
        return path.replace("\\", "/")

    def _file_transport_command(self, in_path: str, out_path: str, ssm_action: str) -> CommandResult:
        """
        Transfers files to or from a remote host using S3.

        :param in_path: The local path of the file to be transferred.
        :param out_path: The remote path where the file should be placed.
        :param ssm_action: The action to perform, either 'get' (download) or 'put' (upload).
        :return: A CommandResult dictionary containing execution results.
        """
        bucket = self.connection.get_option("bucket_name")
        s3_path = self._escape_path(f"{self.connection.instance_id}/{out_path}")
        client = self.connection._s3_client
        commands, put_args = self.connection._generate_commands(bucket, s3_path, in_path, out_path)

        try:
            if ssm_action == "get":
                return self._handle_get(in_path, out_path, commands, bucket, s3_path, client)
            return self._handle_put(in_path, out_path, commands, bucket, s3_path, client, put_args)
        finally:
            client.delete_object(Bucket=bucket, Key=s3_path)

    def _handle_get(
        self, in_path: str, out_path: str, commands: List[dict], bucket: str, s3_path: str, client
    ) -> CommandResult:
        """
        Handles downloading a file from the remote host via S3.

        :param in_path: The local destination path for the file.
        :param out_path: The remote source path of the file.
        :param commands: The transport commands to execute.
        :param bucket: The S3 bucket name.
        :param s3_path: The S3 path where the file is stored.
        :param client: The S3 client used for downloading.
        :return: The command execution result.
        """
        put_commands = [cmd for cmd in commands if cmd.get("method") == "put"]

        result = self._exec_transport_commands(in_path, out_path, put_commands)
        with open(to_bytes(out_path, errors="surrogate_or_strict"), "wb") as data:
            client.download_fileobj(bucket, s3_path, data)

        return result

    def _handle_put(
        self, in_path: str, out_path: str, commands: List[dict], bucket: str, s3_path: str, client, put_args
    ) -> CommandResult:
        """
        Handles uploading a file to the remote host via S3.

        :param in_path: The local source path of the file.
        :param out_path: The remote destination path for the file.
        :param commands: The transport commands to execute.
        :param bucket: The S3 bucket name.
        :param s3_path: The S3 path where the file will be stored.
        :param client: The S3 client used for uploading.
        :param put_args: Additional arguments for S3 upload.
        :return: The command execution result.
        """
        get_commands = [cmd for cmd in commands if cmd.get("method") == "get"]

        result = self._exec_transport_commands(in_path, out_path, get_commands)
        with open(to_bytes(in_path, errors="surrogate_or_strict"), "rb") as data:
            client.upload_fileobj(data, bucket, s3_path, ExtraArgs=put_args)

        return result

    def _exec_transport_commands(self, in_path: str, out_path: str, commands: List[dict]) -> CommandResult:
        """
        Executes the provided transport commands.

        :param in_path: The input path.
        :param out_path: The output path.
        :param commands: A list of command dictionaries containing the command string and metadata.
        :return: A CommandResult dictionary containing execution results.
        """
        stdout_combined, stderr_combined = "", ""
        for command in commands:
            result = self.connection.exec_command(command["command"], in_data=None, sudoable=False)

            # Check the return code
            if result["returncode"] != 0:
                raise AnsibleError(
                    f"failed to transfer file to {in_path} {out_path}:\n{result['stdout']}\n{result['stderr']}"
                )

            stdout_combined += result["stdout"]
            stderr_combined += result["stderr"]

        return {"returncode": result["returncode"], "stdout": stdout_combined, "stderr": stderr_combined}
