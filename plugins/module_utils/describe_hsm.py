# -*- coding: utf-8 -*-
# Copyright: (c) 2022, TachTech  LLC <info@tachtech.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""AWS HSM Getting Module Plugin Utilities."""


from __future__ import absolute_import, division, print_function

from typing import Any

from ansible.errors import AnsibleActionFail

__metaclass__ = type


from ansible_collections.aws.hsm.plugins.module_utils.aws_hsm import AwsHsm, Validator
from ansible_collections.aws.hsm.plugins.module_utils.constants import *


class DescribeHsmValidator(Validator):  # type: ignore
    """DescribeHsmValidator validation class"""

    def state(self):
        """Validate if necessary state information is provided."""
        state: Any = self.module_args.get("state")  # type: ignore
        if state:
            if not isinstance(state, (str, list)):
                raise AnsibleActionFail(
                    f"Wrong type was provided for the 'state' argument. Must be either a string or a list. Provided: {type(state).__name__}"
                )
            if isinstance(state, str) and state not in STATES:
                raise AnsibleActionFail(
                    f"Wrong value was set to the 'state' argument. Must be {', '.join(STATES)}. Provided: {state}"
                )
            elif isinstance(state, list):
                for _state in state:  # type: ignore
                    if _state not in STATES:
                        raise AnsibleActionFail(
                            f"Wrong value was set to the 'state' argument. Must be {', '.join(STATES)}. Provided: {state}"
                        )

    def validate(self):
        """Validate all."""
        self.auth()  # type: ignore
        self.region()  # type: ignore
        self.cluster_id()
        self.state()
        self.name()


class DescribeHsm(AwsHsm):  # type: ignore
    """Class to get the HSM device information"""

    def __init__(self, module_args: dict[str, Any], play_vars) -> None:
        super().__init__()
        self.play_vars = play_vars
        self.module_args = module_args
        DescribeHsmValidator(self.module_args, self.play_vars).validate()

    def get(self) -> list[dict[str, Any]]:
        """Gets the HSM device information.

        Returns:
            list[dict]: List of HSM clusters, if any.
        """
        return self._get_hsm(filters=self.module_args, extend_search=True)
