#!/usr/bin/python

# Copyright: (c) 2022, TachTech <info@tachtech.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: cloudhsm_hsm_info
short_description: Get HSM information from AWS.
author:
  - Armen Martirosyan (@armartirosyan)
requirements:
  - boto3
description:
  - Get HSM information from AWS.
options:
  cluster_id:
    description:
      - The HSM cluster's identifier.
    type: list
    required: false
    elements: str
  state:
    description:
      - Filter based on the state of the HSM cluster.
    type: list
    required: false
    choices:
      - CREATE_IN_PROGRESS
      - ACTIVE
      - DEGRADED
      - DELETE_IN_PROGRESS
      - DELETED
    elements: str
  name:
    description:
      - Filter based on the name of the HSM cluster.
    type: str
    required: false
  eni_id:
      description:
          - Elastic network interface (ENI) identifier of the HSM
      type: list
      required: false
      elements: str
  eni_ip:
      description:
          - Elastic network interface (ENI) IP address of the HSM
      type: list
      required: false
      elements: str
  hsm_id:
      description:
          - The identifier of the HSM
      type: list
      elements: str
      required: false
extends_documentation_fragment:
- amazon.aws.aws
- amazon.aws.ec2
"""


EXAMPLES = """
# Note: These examples do not set authentication details, see the AWS Guide for details

- name: "Get All HSMs Across all HSM Clusters"
  community.aws.cloudhsm_hsm_info:

- name: "Get All HSMs in ACTIVE state"
  community.aws.cloudhsm_hsm_info:
    state: ACTIVE

- name: "Get All HSMs in DEGRADED and ACTIVE state"
  community.aws.cloudhsm_hsm_info:
    state:
      - DEGRADED
      - ACTIVE

- name: "Get all HSMs For a Particular Cluster ID"
  community.aws.cloudhsm_hsm_info:
    cluster_id: cluster_a3231231

- name: "Get HSM with Particular IP Address"
  community.aws.cloudhsm_hsm_info:
    eni_ip: 127.0.0.1

- name: "Get HSM with Particular ID"
  community.aws.cloudhsm_hsm_info:
    hsm_id: hsm-abcdef1234

- name: "Get HSM with Particular ENI ID"
  community.aws.cloudhsm_hsm_info:
    eni_id: eni-abcdef1234
"""

RETURN = """
changed:
  description: This module does not make any changes. The value is always False
  returned: always
  type: bool
  sample: False
data:
  description: HSM information returned by the AWS.
  returned: always
  type: list
  sample:
    - availability_zone: us-east-2b
      cluster_id: cluster-test4
      eni_id: eni-test1
      eni_ip: 127.0.0.2
      hsm_id: hsm-test1
      state: ACTIVE
      state_Message: HSM created.
      subnet_id: subnet-test
"""

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict
from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.community.aws.plugins.module_utils.cloudhsm import (
    HSM_STATES,
    CloudHsmCluster,
)


def main():
    """Main function for the module."""

    argument_spec = dict(
        state=dict(required=False, type="list", choices=HSM_STATES, elements="str"),
        cluster_id=dict(required=False, type="list", elements="str"),
        name=dict(required=False, type="str"),
        eni_id=dict(required=False, type="list", elements="str"),
        hsm_id=dict(required=False, type="list", elements="str"),
        eni_ip=dict(required=False, type="list", elements="str"),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    cluster_mgr = CloudHsmCluster(module)
    existing_hsms = cluster_mgr.describe_hsm(extend_search=True)

    results = dict(changed=False, data=[])
    if existing_hsms:
        for cluster in existing_hsms:
            results["data"].append(camel_dict_to_snake_dict(cluster))
    cluster_mgr.module.exit_json(**results)


if __name__ == "__main__":
    main()
