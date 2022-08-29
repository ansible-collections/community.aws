#!/usr/bin/python
# Copyright: (c) 2022, TachTech <info@tachtech.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

from email.policy import default

__metaclass__ = type

DOCUMENTATION = """
---
module: cloudhsm_hsm
short_description: Create HSM Device in AWS.
author:
    - Armen Martirosyan (@armartirosyan)
requirements:
    - boto3
description:
    - Create HSM Device(s) in AWS's HSM Cluster.
options:
    availability_zone:
        description:
            - Availability Zone where the HSM will be created
        type: str
        required: false
    cluster_id:
        description:
            - The HSM cluster's identifier.
        type: str
        required: false
    ip_address:
        description:
            - IP Address of the HSM device.
        type: list
        required: false
    state:
        description:
            - The state of the HSM Device. If present, the device will be created, if absent, the device will be removed.
        type: str
        required: true
        choices:
            - present
            - absent
    name:
        description:
            - The name of the cluster
        type: str
        required: false
    count:
        description:
            - Number of HSM devices that need to be created.
            - The value cannot be greater than 3.
        type: int
        required: false
        default: 1
    eni_id:
        description:
            - Elastic network interface (ENI) identifier of the HSM
        type: list
        required: false
    eni_ip:
        description:
            - Elastic network interface (ENI) IP address of the HSM
        type: list
        required: false
    hsm_id:
        description:
            - The identifier of the HSM
        type: list
        required: false
"""


EXAMPLES = """
# Note: These examples do not set authentication details, see the AWS Guide for details

- name: "Create an HSM Device"
  community.aws.cloudhsm_hsm:
    availability_zone: us-west-2b
    cluster_id: cluster_a3231231
    count: 1
    state: present


- name: "Create an HSM Device with IP"
  community.aws.cloudhsm_hsm:
    availability_zone: us-west-2b
    cluster_id: cluster_a3231231
    ip_address: 192.168.0.1
    count: 1
    state: present

- name: "Create Two HSM Devices with IP"
  community.aws.cloudhsm_hsm:
    availability_zone: us-west-2b
    cluster_id: cluster_a3231231
    ip_address:
      - 192.168.0.1  # IP address of the first HSM Device
      - 192.168.0.2  # IP address of the second HSM Device
    count: 2
    state: present

- name: "Add Second HSM Devices to the Existing One"
  community.aws.cloudhsm_hsm:
    availability_zone: us-west-2b
    cluster_id: cluster_a3231231
    count: 2
    state: present

- name: "Remove all HSM Devices"
  community.aws.cloudhsm_hsm:
    cluster_id: cluster_a3231231
    state: absent

- name: "Remove HSM Device Using HSM ID"
  community.aws.cloudhsm_hsm:
    cluster_id: cluster_a3231231
    hsm_id: hsm_asdasd123123
    state: absent

- name: "Remove HSM Device Using ENI ID"
  community.aws.cloudhsm_hsm:
    cluster_id: cluster_a3231231
    eni_id: eni_123asd123
    state: absent

- name: "Remove HSM Device Using ENI IP"
  community.aws.cloudhsm_hsm:
    cluster_id: cluster_a3231231
    eni_ip: 192.168.0.1
    state: absent
"""

RETURN = """
changed:
  description: Boolean that is true if the command changed the state.
  returned: always
  type: bool
  sample: True
data:
  description: HSM information returned by the AWS.
  returned: always
  type: list
  sample:
    - availability_zone: us-east-2b
      cluster_id: cluster-test4
      eni_id: eni-test
      eni_ip: 127.0.0.1
      hsm_id: hsm-test
      state: ACTIVE
      state_message: HSM created
      subnet_id: subnet-test
"""


from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict
from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.community.aws.plugins.module_utils.cloudhsm import (
    CloudHsmCluster,
)


def main():
    """Main function for the module."""

    argument_spec = dict(
        state=dict(required=True, choices=["present", "absent"], type="str"),
        availability_zone=dict(required=False, type="str"),
        cluster_id=dict(required=False, type="str"),
        name=dict(required=False, type="str"),
        count=dict(required=False, type="int", default=1),
        ip_address=dict(required=False, type="list"),
        eni_id=dict(required=False, type="list", default=[]),
        eni_ip=dict(required=False, type="list", default=[]),
        hsm_id=dict(required=False, type="list", default=[]),
    )
    required_if = [
        ("state", "present", ("name", "cluster_id"), True),
        ("state", "present", ("availability_zone",)),
        ("state", "absent", ("cluster_id", "name"), True),
    ]

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=required_if,
    )
    cluster_mgr = CloudHsmCluster(module)
    ip_addr = cluster_mgr.module.params.get("ip_address", [])
    count = cluster_mgr.module.params["count"]
    if count < 1 or count > 3:
        cluster_mgr.module.fail_json(
            msg=f"'count' value cannot be less than 1 and more than 3. Provided: {count}"
        )
    if ip_addr and len(ip_addr) != count:
        cluster_mgr.module.fail_json(
            msg="Number of provided IP Addresses must be equal to the 'count' value."
        )

    existing_hsms = cluster_mgr.describe_hsm()
    existing_cluster = cluster_mgr.describe_cluster()
    results = dict(changed=False, data=[])
    if module.params["state"] == "present":
        if len(existing_hsms) == count or len(existing_hsms) > count:
            for hsm in existing_hsms:
                results["data"].append(camel_dict_to_snake_dict(hsm))
        else:
            if not module.check_mode:
                # doesn't exist. create it
                hsm_body = {
                    "ClusterId": existing_cluster[0]["ClusterId"],
                    "AvailabilityZone": cluster_mgr.module.params["availability_zone"],
                }
                if count == 1:
                    if ip_addr:
                        hsm_body.update({"IpAddress": ip_addr[0]})
                    results["data"].append(
                        camel_dict_to_snake_dict(cluster_mgr.create_hsm(hsm_body))
                    )
                else:
                    if ip_addr:
                        for ip_addr in ip_addr[count - (count - len(existing_hsms)) :]:
                            hsm_body.update({"IpAddress": ip_addr})
                            results["data"].append(
                                camel_dict_to_snake_dict(
                                    cluster_mgr.create_hsm(hsm_body)
                                )
                            )
                        results["changed"] = True
                    else:
                        for _ in range(0, count - len(existing_hsms)):
                            results["data"].append(
                                camel_dict_to_snake_dict(
                                    cluster_mgr.create_hsm(hsm_body)
                                )
                            )
                        results["changed"] = True
            else:
                hsm_data = {
                    "AvailabilityZone": cluster_mgr.module.params["availability_zone"],
                    "ClusterId": existing_cluster[0]["ClusterId"],
                    "SubnetId": "subnet-check-mode-on",
                    "State": "ACTIVE",
                    "StateMessage": "HSM created.",
                }
                for i in range(0, count - len(existing_hsms)):
                    hsm_data.update(
                        {
                            "EniIp": f"127.0.0.{i}",
                            "HsmId": f"hsm-check-mode-on-{i}",
                            "EniId": f"eni-check-mode-on-{i}",
                        }
                    )
                    results["data"].append(camel_dict_to_snake_dict(hsm_data))
                results["changed"] = True

    # delete the cluster
    elif module.params["state"] == "absent":
        count = cluster_mgr.module.params["count"]
        eni_id = cluster_mgr.module.params.get("eni_id")
        eni_ip = cluster_mgr.module.params.get("eni_ip")
        hsm_id = cluster_mgr.module.params.get("hsm_id")
        hsm_body = {
            "ClusterId": existing_cluster[0]["ClusterId"],
        }
        if not cluster_mgr.module.check_mode:
            if not eni_id and not eni_ip and not hsm_id:
                # If no information is provided, delete all HSMs
                hsm_ids_to_remove = [
                    hsm["HsmId"]
                    for index, hsm in enumerate(existing_hsms)
                    if index <= count and existing_cluster[0]["Hsms"]
                ]
                if not hsm_ids_to_remove:
                    results[
                        "msg"
                    ] = f"CloudHSM Cluster ID '{existing_cluster[0]['ClusterId']}' does not contain any HSMs."
                else:
                    for hsm_id in hsm_ids_to_remove:
                        hsm_body.update({"HsmId": hsm_id})
                        cluster_mgr.delete_hsm(hsm_body)
                    results["changed"] = True
            elif hsm_id:
                for hsm in hsm_id:
                    hsm_body.update({"HsmId": hsm})
                    cluster_mgr.delete_hsm(hsm_body)
                results["changed"] = True
            elif eni_ip:
                for eni in eni_ip:
                    hsm_body.update({"EniIp": eni})
                    cluster_mgr.delete_hsm(hsm_body)
                results["changed"] = True
            elif eni_id:
                for eni in eni_id:
                    hsm_body.update({"EniId": eni})
                    cluster_mgr.delete_hsm(hsm_body)
                results["changed"] = True
        else:
            results["changed"] = True

    cluster_mgr.module.exit_json(**results)


if __name__ == "__main__":
    main()
