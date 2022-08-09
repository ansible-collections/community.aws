"""The action plugin file to initialize the AWS HSM Cluster."""
from __future__ import absolute_import, division, print_function

__metaclass__ = type

from ansible.plugins.action import ActionBase
from ansible_collections.community.aws.plugins.module_utils.initialize_cluster import (
    HsmClusterInit,
)


class ActionModule(ActionBase):
    """Action module."""

    # Keep internal params away from user interactions
    _VALID_ARGS = frozenset(
        (
            "aws_access_key",
            "aws_secret_key",
            "region",
            "cluster_id",
            "signed_cert",
            "trust_anchor",
        )
    )

    def run(self, tmp=None, task_vars=None):
        """Run logic."""
        self._supports_check_mode = False
        self._supports_async = False
        self._result = super(ActionModule, self).run(tmp, task_vars)

        module_args = self._task.args

        resource = HsmClusterInit(module_args, task_vars)
        self._result.update(resource.init())

        return self._result
