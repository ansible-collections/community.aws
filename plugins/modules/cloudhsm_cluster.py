#!/usr/bin/python
# Copyright: (c) 2022, TachTech <info@tachtech.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: cloudhsm_cluster
short_description: Create or delete the CloudHSM Cluster in AWS
author:
    - Armen Martirosyan (@armartirosyan)
requirements:
    - boto3
description:
    - Create or delete the CloudHSM Cluster in AWS
options:
    backup_retention_days:
        description:
            - Backup retention days for the cluster
            - Must be a value between 7 and 379
        type: int
        required: false
        default: 90
    source_backup_id:
        description:
            - Cluster backup ID to restore the cluster from
        type: str
        required: false
    subnet_ids:
        description:
            - The IDs of subnets where the cluster is being created
        type: str
        required: false
    tags:
        description:
            - Tags to apply to the HSM cluster
        type: dict
        required: false
    name:
        description:
            - The name of the cluster
            - The name will be added as a tag for state keeping
        type: str
        required: true
    state:
        description:
            - The state of the CloudHSM  Cluster
            - present state will create an CloudHSM Cluster, if one does not exists
            - absent state will remove the CloudHSM Cluster, if one exists
            - initialize state will initialize the exiting CloudHSM Cluster
        type: str
        required: true
        choices:
            - present
            - absent
            - initialize
extends_documentation_fragment:
  - amazon.aws.aws
  - amazon.aws.cloudhsm

"""

EXAMPLES = """
# Note: These examples do not set authentication details, see the AWS Guide for details

- name: Create an HSM Cluster
  community.aws.cloudhsm_cluster:
    backup_retention_days: 7
    subnet_ids:
        - subnet-5855b205
    state: present
    name: "West2a_Cluster"

- name: Create an HSM Cluster With Tags
  community.aws.cloudhsm_cluster:
    subnet_ids:
        - subnet-5855b205
    state: present
    name: "West2a_Cluster"
    tags:
        zone: west
        sec: none

- name: "Remove HSM Cluster"
  community.aws.cloudhsm_cluster:
    state: absent
    name: "West2a_Cluster"
"""

RETURN = """
changed:
  description: Boolean that is true if the command changed the state.
  returned: always
  type: bool
  sample: True
data:
  description: HSM cluster information returned by the AWS.
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
    CloudHsmCluster,
)


def main():
    """Main function for the module."""

    argument_spec = dict(
        state=dict(required=True, choices=["present", "absent"]),
        name=dict(required=True, type="str"),
        subnet_ids=dict(required=False, type="list"),
        backup_retention_days=dict(required=False, type="str", default="90"),
        source_backup_id=dict(required=False, type="str"),
        tags=dict(required=False, type="dict"),
    )
    required_if = [("state", "present", ("name", "subnet_ids"))]

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=required_if,
    )
    cluster_mgr = CloudHsmCluster(module)
    existing = cluster_mgr.describe_cluster()
    results = dict(changed=False, data=[])
    if module.params["state"] == "present":
        if existing:
            for cluster in existing:
                results["data"].append(camel_dict_to_snake_dict(cluster))
        else:
            if not module.check_mode:
                # doesn't exist. create it
                results["data"].append(
                    camel_dict_to_snake_dict(cluster_mgr.create_cluster())
                )
                results["changed"] = True
            else:
                if existing:
                    module.exit_json(**results)
                results["changed"] = True
                results["data"] = [
                    camel_dict_to_snake_dict(
                        {
                            "BackupPolicy": "DEFAULT",
                            "BackupRetentionPolicy": {
                                "Type": "DAYS",
                                "Value": module.params["backup_retention_days"],
                            },
                            "Certificates": {},
                            "ClusterId": "cluster-checkmode-on",
                            "CreateTimestamp": "2022-08-24T14:41:17.712000-07:00",
                            "HsmType": "hsm1.medium",
                            "Hsms": [],
                            "State": "CREATE_IN_PROGRESS",
                            "SubnetMapping": {
                                "us-east-2b": module.params["backup_retention_days"]
                            },
                            "VpcId": "vpc-checkmode-on",
                        }
                    )
                ]

    # delete the cluster
    elif module.params["state"] == "absent":
        if not existing:
            pass
        else:
            if not module.check_mode:
                cluster_mgr.delete_cluster(existing[0]["ClusterId"])
                results["changed"] = True
            else:
                if existing:
                    results["changed"] = True

    cluster_mgr.module.exit_json(**results)


if __name__ == "__main__":
    main()
