#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: eks_pod_identity_association_info
version_added: 10.1.0
short_description: Retrieve EKS pod identity association details
description:
  - Get details about a pod identity association.
author:
  - Ali AlKhalidi (@doteast)
options:
  cluster_name:
    description: Name of EKS Cluster.
    required: true
    type: str
  association_id:
    description:
      - Get details for pod identity assosciation with specified Id.
    type: str
  namespace:
    description:
      - Get details for pod identity assosciations with specified namespace.
      - Ignore when association Id is provided.
      - Must be coupled with service_account.
    type: str
  service_account:
    description:
      - Get details for pod identity assosciation with specified service account.
      - Ignore when association Id is provided.
      - Must be coupled with namespace.
    type: str

extends_documentation_fragment:
  - amazon.aws.boto3
  - amazon.aws.common.modules
"""


EXAMPLES = r"""
- name: get current pod identity association settings by id
  community.aws.eks_pod_identity_association_info:
    cluster_name: myeks
    association_id: "aws-pod-identity-association-id"
  register: association_info
- name: get current pod identity association settings by service account and namespace
  community.aws.eks_pod_identity_association_info:
    cluster_name: myeks
    namespace: test-ns
    service_account: test-sa
  register: association_info
"""

RETURN = r"""
broker:
    description: API response of describe_pod_identity_association() converted to snake yaml.
    type: dict
    returned: success
"""

try:
    import botocore
except ImportError:
    # handled by AnsibleAWSModule
    pass

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.amazon.aws.plugins.module_utils.modules import AnsibleAWSModule


def get_association_id(client, module):
    cluster_name = module.params["cluster_name"]
    namespace = module.params["namespace"]
    service_account = module.params["service_account"]
    association_id = None
    try:
        response = client.list_pod_identity_associations(clusterName=cluster_name, namespace=namespace, serviceAccount=service_account)
    except botocore.exceptions.EndpointConnectionError:  # pylint: disable=duplicate-except
        module.fail_json(msg=f"Region {client.meta.region_name} is not supported by EKS")
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't list pod identity associations.")

    if len(response["associations"]) > 1:
        module.warn("found multiple associations matcing fields")
    if len(response["associations"]) >= 1:
        association_id = response["associations"][0]["associationId"]
    return association_id



def get_association_info(client, module, association_id, cluster_name):
    try:
        return client.describe_pod_identity_association(
            clusterName=cluster_name,
            associationId=association_id
            )
    except botocore.exceptions.EndpointConnectionError:  # pylint: disable=duplicate-except
        module.fail_json(msg=f"Region {client.meta.region_name} is not supported by EKS")
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't get pod identity association details.")


def main():
    argument_spec = dict(
        cluster_name=dict(type="str", required=True),
        association_id=dict(type="str"),
        namespace=dict(type="str"),
        service_account=dict(type="str")
    )
    required_one_of = (
        (
            "association_id",
            "namespace",
        ),
    )
    required_together = (
        (
            "namespace",
            "service_account",
        ),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        required_one_of=required_one_of,
        required_together=required_together,
        supports_check_mode=True,
    )
    cluster_name = module.params["cluster_name"]
    association_id = module.params["association_id"]

    client = module.client("eks")

    try:
        if not association_id:
            association_id = get_association_id(client, module)
        if not association_id:
            if module.check_mode:
                module.exit_json(
                    association={"association_id": "fakeId", "clusert_name": cluster_name if cluster_name else "fakeName"}
                )
        result = get_association_info(client, module, association_id, cluster_name)
    except botocore.exceptions.ClientError as e:
        module.fail_json_aws(e)
    #
    module.exit_json(association=camel_dict_to_snake_dict(result["association"], ignore_list=["Tags"]))


if __name__ == "__main__":
    main()
