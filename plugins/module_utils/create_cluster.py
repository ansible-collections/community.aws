# -*- coding: utf-8 -*-
# Copyright: (c) 2022, TachTech  LLC <info@tachtech.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""AWS HSM Cluster Module Plugin Utilities."""


from __future__ import absolute_import, division, print_function

import re
from typing import Any

from ansible.errors import AnsibleActionFail

__metaclass__ = type


from ansible_collections.aws.hsm.plugins.module_utils.aws_hsm import AwsHsm, Validator


class CreateHsmClusterValidator(Validator):
    """CreateHsmClusterValidator module args validation."""

    def backup_retention_days(self):
        """Validates if necessary backup_retention_days info is provided."""
        backup_retention_days = self.module_args.get("backup_retention_days", False)
        if backup_retention_days and self.module_args["state"] != "absent":
            if isinstance(backup_retention_days, (str, int)):
                try:
                    backup_retention_days = int(backup_retention_days)
                    if backup_retention_days < 7 or backup_retention_days > 379:
                        raise TypeError
                except TypeError as type_error:
                    raise AnsibleActionFail(
                        f"Wrong value was provided to the 'backup_retention_days' argument. Must be a number between 7 and 379. Provided: {backup_retention_days}"
                    ) from type_error
                except ValueError as value_error:
                    raise AnsibleActionFail(
                        f"Wrong type was provided for the 'backup_retention_days' argument. Must be a string. Provided: {type(backup_retention_days).__name__}"
                    ) from value_error

            else:
                raise AnsibleActionFail(
                    f"Wrong type was provided for the 'backup_retention_days' argument. Must be a string. Provided: {type(backup_retention_days).__name__}"
                )

    def source_backup_id(self):
        """Validates if necessary source_backup_id info is provided."""
        source_backup_id = self.module_args.get("source_backup_id", False)
        if source_backup_id and self.module_args["state"] != "absent":
            if not isinstance(source_backup_id, str):
                raise AnsibleActionFail(
                    f"Wrong type was provided for the 'source_backup_id' argument. Must be a string. Provided: {type(source_backup_id).__name__}"
                )

    def subnet_ids(self):
        """Validates if necessary subnet_ids info is provided."""
        if self.module_args["state"] == "absent":
            return
        try:
            subnet_ids = self.module_args["subnet_ids"]
            if not isinstance(subnet_ids, (str, list)):
                raise TypeError
            if isinstance(subnet_ids, str):
                self._regex_check("subnet_ids", subnet_ids, "^subnet-[0-9a-f].*")
            else:
                self._regex_check("subnet_ids", subnet_ids[0], "^subnet-[0-9a-f].*")
        except TypeError as type_error:
            raise AnsibleActionFail(
                f"Wrong type was provided for the 'subnet_ids' argument. Must be a either a list or a string. Provided: {type(subnet_ids).__name__}"
            ) from type_error
        except KeyError as key_error:
            raise AnsibleActionFail(
                "'subnet_ids' is a mandatory argument."
            ) from key_error

    def tags(self):
        """Validates if necessary tags info is provided."""
        tags = self.module_args.get("tags")
        if tags and self.module_args["state"] != "absent":
            if not isinstance(tags, dict):
                raise AnsibleActionFail(
                    f"Wrong type was provided for the 'tags' argument. Must be a dictionary. Provided: {type(tags).__name__}"
                )

    def validate(self):
        """Validate all."""
        self.main_validation()
        self.backup_retention_days()
        self.source_backup_id()
        self.subnet_ids()
        self.tags()
        self.name(mandatory=True)


class CreateHsmCluster(AwsHsm):
    """Class to create HSM Cluster"""

    def __init__(self, module_args: dict[str, Any], play_vars: dict[str, Any]) -> None:
        super().__init__()
        self.play_vars = play_vars
        self.module_args = module_args
        CreateHsmClusterValidator(self.module_args, self.play_vars).validate()
        self.cluster = self._get_cluster(self.module_args)

    def present(self) -> dict[str, Any]:
        """Creates HSM Cluster.

        Returns:
            dict[str, Any]: Cluster information
        """
        if not self.cluster:
            cluster_body = {
                "BackupRetentionPolicy": {
                    "Type": "DAYS",
                    "Value": str(self.module_args.get("backup_retention_days", "90")),
                },
                "HsmType": "hsm1.medium",
                "TagList": [
                    {"Key": "name", "Value": self.module_args["name"]},
                ],
            }
            if isinstance(self.module_args["subnet_ids"], str):
                cluster_body.update({"SubnetIds": [self.module_args["subnet_ids"]]})
            elif isinstance(self.module_args["subnet_ids"], list):
                cluster_body.update({"SubnetIds": self.module_args["subnet_ids"]})
            if self.module_args.get("tags"):
                for key, value in self.module_args.get("tags").items():
                    cluster_body["TagList"].append({"Key": key, "Value": value})
            return {
                "data": self.client.create_cluster(**cluster_body)["Cluster"],
                "changed": True,
            }
        return {"changed": False, "data": self.cluster}

    def absent(self):
        """Removes HSM Cluster from the AWS.

        Returns:
            dict: Changed true if the HSM cluster deleted else false.
        """
        if self.cluster:
            self.client.delete_cluster(ClusterId=self.cluster[0]["ClusterId"])
            return {"changed": True}
        return {"changed": False}
