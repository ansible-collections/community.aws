"""The action plugin file to create AWS HSM Cluster."""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.plugins.action import ActionBase
from ansible_collections.community.aws.plugins.module_utils.create_cluster import (
    CreateHsmCluster,
)


class ActionModule(ActionBase):
    """Action module."""

    # Keep internal params away from user interactions
    _VALID_ARGS = frozenset(
        (
            "aws_access_key",
            "aws_secret_key",
            "region",
            "backup_retention_days",
            "source_backup_id",
            "subnet_ids",
            "tags",
            "name",
            "state",
        )
    )

    def run(self, tmp=None, task_vars=None):
        """Run logic."""
        self._supports_check_mode = True
        self._supports_async = False
        self._result = super(ActionModule, self).run(tmp, task_vars)

        args = self._task.args
        state = args["state"]

        resource = CreateHsmCluster(args, task_vars)
        if state == "present":
            self._result.update(resource.present())
        else:
            self._result.update(resource.absent())

        return self._result
