"""The action plugin file to create AWS HSM Device."""
from __future__ import absolute_import, division, print_function

from typing import Any

__metaclass__ = type

from ansible.plugins.action import ActionBase
from ansible_collections.community.aws.plugins.module_utils.create_hsm import CreateHsm


class ActionModule(ActionBase):
    """Action module."""

    # Keep internal params away from user interactions
    _VALID_ARGS = frozenset(
        (
            "aws_access_key",
            "aws_secret_key",
            "region",
            "availability_zone",
            "cluster_id",
            "ip_address",
            "eni_id",
            "hsm_id",
            "eni_ip",
            "state",
            "count",
        )
    )

    def run(self, tmp=None, task_vars=None):
        """Run logic."""
        self._supports_check_mode = True
        self._supports_async = False
        self._result = super(ActionModule, self).run(tmp, task_vars)

        self.args = self._task.args
        self.state = self.args["state"]

        resource = CreateHsm(self.args, task_vars)
        if self.state == "present":
            self._result.update(resource.present())
        else:
            self._result.update(resource.absent())

        return self._result
