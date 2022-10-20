#!/usr/bin/python

# Copyright: (c) 2022, TachTech <info@tachtech.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: cloudhsm_cluster_info
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
    elements: str
    required: false
  state:
    description:
      - Filter based on the state of the HSM cluster.
    type: list
    required: false
    choices:
      - CREATE_IN_PROGRESS
      - UNINITIALIZED
      - INITIALIZE_IN_PROGRESS
      - INITIALIZED
      - ACTIVE
      - UPDATE_IN_PROGRESS
      - DELETE_IN_PROGRESS
      - DELETED
      - DEGRADED
    elements: str
  name:
    description:
      - Filter based on the name of the HSM cluster.
    type: str
    required: false
extends_documentation_fragment:
- amazon.aws.aws
- amazon.aws.ec2
"""


EXAMPLES = """
# Note: These examples do not set authentication details, see the AWS Guide for details

- name: "Get All HSM Clusters in Defined AWS Region"
  community.aws.cloudhsm_cluster_info:

- name: "Get All HSM Clusters in INITIALIZED state"
  community.aws.cloudhsm_cluster_info:
    state: INITIALIZED

- name: "Get All HSM Clusters in INITIALIZED and ACTIVE state"
  community.aws.cloudhsm_cluster_info:
    state:
      - INITIALIZED
      - ACTIVE

- name: "Get HSM Cluster Based on the Cluster ID"
  community.aws.cloudhsm_cluster_info:
    cluster_id: cluster_a3231231

- name: "Get HSM Cluster Based on the Multiple Cluster IDs"
  community.aws.cloudhsm_cluster_info:
    cluster_id:
      - cluster_a3231231
      - cluster_a3231232

- name: "Get HSM Cluster Based on the Cluster name"
  community.aws.cloudhsm_cluster_info:
    name: WestHSMCluster
"""

RETURN = r"""
changed:
  description: This module does not make any changes. The value is always False
  returned: always
  type: bool
  sample: False
data:
  description: HSM Cluster information returned by the AWS
  returned: always
  type: list
  sample:
    - backup_policy: DEFAULT
      backup_retention_policy:
      type: DAYS
      value: '90'
      certificates: {}
      cluster_id: cluster-sample
      create_timestamp: '2022-07-24T19:35:10.889000-07:00'
      hsm_type: hsm1.medium
      hsms: []
      security_group: sg-sample
      state: UNINITIALIZED
      subnet_mapping:
      us-east-2b: subnet-sample
      tag_list:
      - key: sec
        value: none
      - key: name
        value: '456'
      - key: zone
        value: west
        vpc_id: vpc-sample
"""


from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict
from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.community.aws.plugins.module_utils.cloudhsm import (
    CLUSTER_STATES,
    CloudHsmCluster,
)


def main():
    """Main function for the module."""

    argument_spec = dict(
        state=dict(required=False, type="list", choices=CLUSTER_STATES, elements="str"),
        cluster_id=dict(required=False, type="list", elements="str"),
        name=dict(required=False, type="str"),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=False,
    )

    cluster_mgr = CloudHsmCluster(module)
    existing = cluster_mgr.describe_cluster()

    results = dict(changed=False, data=[])
    if existing:
        for cluster in existing:
            results["data"].append(camel_dict_to_snake_dict(cluster))
    cluster_mgr.module.exit_json(**results)


if __name__ == "__main__":
    main()
