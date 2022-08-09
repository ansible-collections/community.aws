"""The action plugin file to get AWS HSM information."""
from __future__ import absolute_import, division, print_function

from typing import Any

__metaclass__ = type

from ansible.plugins.action import ActionBase
from ansible_collections.aws.hsm.plugins.module_utils.describe_hsm import DescribeHsm


class ActionModule(ActionBase):
    """Action module."""

    # Keep internal params away from user interactions
    _VALID_ARGS = frozenset(
        (
            "aws_access_key",
            "aws_secret_key",
            "region",
            "cluster_id",
            "ip_address",
            "eni_id",
            "hsm_id",
            "eni_ip",
            "state",
        )
    )

    def run(self, tmp=None, task_vars=None) -> dict[str, Any]:
        """Run logic."""
        self._supports_check_mode = True
        self._supports_async = False
        self._result: dict[str, Any] = super(ActionModule, self).run(tmp, task_vars)  # type: ignore

        args = self._task.args  # type: ignore

        resource = DescribeHsm(args, task_vars)
        self._result["data"] = resource.get()  # type: ignore
        return self._result
