#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: eks_pod_identity_association
version_added: 10.0.0
short_description: Manage an EKS pod identity association
description:
  - Manage an AWS EKS pod identity association. See
    U(https://docs.aws.amazon.com/eks/latest/userguide/pod-id-association.html)
    U(https://docs.aws.amazon.com/eks/latest/userguide/pod-id-assign-target-role.html) for details.
author:
  - "Ali Al-Khalidi (@doteast)"
options:
  cluster_name:
    description: Name of EKS Cluster.
    required: true
    type: str
  role_arn:
    description: ARN of IAM role to associate with the service account.
    type: str    
    required: true
  target_role_arn:
    description: ARN of IAM target role to associate with the service account.
    type: str    
    required: false
  namespace:
    description:
      - EKS Kubernetes namespace inside the cluster to create the association in.
      - Can be used only during creation.
    type: str
    required: true
  service_account:
    description:
      - EKS Kubernetes service account inside the cluster to associate the IAM credentials with.
      - Can be used only during creation.
    type: str
    required: true
  tags:
    description:
        - A dictionary of resource tags.
        - Can be used only during creation.
    type: dict
    aliases: ['resource_tags']
  disable_session_tags:
    description:
      - Whether or not to alter existing targets in the group to match what is passed with the module
    required: false
    default: false
    type: bool
  state:
    description:
      - Create or destroy the association.
    required: false
    default: present
    choices: [ 'present', 'absent' ]
    type: str
extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.tags
  - amazon.aws.boto3
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details, see the AWS Guide for details.

- name: Create pod identity association
  community.aws.eks_pod_identity_association:
    cluster_name: myeks
    role_arn: arn:aws:iam:us-east-1:1231231123:role/abcd
    namespace: test-ns
    service_account: test-sa
    state: present
"""

RETURN = r"""
cluster_name:
  description: The name of the cluster that the association is in.
  returned: when state is present
  type: str
  sample: test_cluster
role_arn:
  description: ARN of the IAM role to associate with the service account.
  returned: when state is present
  type: str
  sample: arn:aws:iam:us-east-1:1231231123:role/abcd
target_role_arn:
  description: ARN of the target IAM role to associate with the service account.
  returned: when state is present
  type: str
  sample: arn:aws:iam:us-east-1:1231231123:role/abcd
namespace:
    description: The name of the Kubernetes namespace inside the cluster to create the association in.
    returned: when state present
    type: str
    sample: test-ns
service_account:
    description: The name of the Kubernetes service account inside the cluster to associate the IAM credentials with.
    returned: when state present
    type: str
    sample: test-sa
association_arn:
    description: ARN of the association.
    returned: when state present
    type: str
    sample: arn:aws:els:us-east-1:1231231123:association/abcd
association_id:
    description: The ID of the association.
    returned: when state present
    type: str
    sample: TBD
tags:
    description: Metadata that assists with categorization and organization.
    returned: when state present
    type: dict
    sample:
      foo: bar
disable_session_tags:
    description: The state of the automatic sessions tags.
    returned: when state present
    type: bool
    sample: True
external_id:
    description: The unique identifier for this EKS Pod Identity association for a target IAM role.
    returned: when state present
    type: str
    sample: TBD
created_at:
  description: Association creation date and time.
  returned: when state is present
  type: str
  sample: '2022-01-18T20:00:00.111000+00:00'
modified_at:
  description: Association modified date and time.
  returned: when state is present
  type: str
  sample: '2022-01-18T20:00:00.111000+00:00'
owner_arn:
    description: If defined, the EKS Pod Identity association is owned by an Amazon EKS add-on.
    returned: when state present
    type: str
    sample: TBD
"""

try:
    import botocore
except ImportError:
    pass  # caught by AnsibleAWSModule
from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule

PARAMS_MAP = {
    "cluster_name": "clusterName",
    "role_arn": "roleArn",
    "target_role_arn": "targetRoleArn",
    "namespace": "namespace",
    "service_account": "serviceAccount",
    "disable_session_tags": "disableSessionTags",
    "tags": "Tags",
}

DEFAULTS = {
    "disable_session_tags": False,
}

CREATE_ONLY_PARAMS = [
    "namespace",
    "service_account",
    "tags",
]

def _set_kwarg(kwargs, key, value):
    mapped_key = PARAMS_MAP[key]
    key_list = [mapped_key]
    data = kwargs
    data[key_list[0]] = value


def _fill_kwargs(module, apply_defaults=True, ignore_create_params=False):
    kwargs = {}
    if apply_defaults:
        for p_name, p_value in DEFAULTS.items():
            _set_kwarg(kwargs, p_name, p_value)
    for p_name in module.params:
        if ignore_create_params and p_name in CREATE_ONLY_PARAMS:
            # ignore CREATE_ONLY_PARAMS on update
            continue
        if p_name in PARAMS_MAP and module.params[p_name] is not None:
            _set_kwarg(kwargs, p_name, module.params[p_name])
        else:
            # ignore
            pass
    return kwargs

def _needs_change(current, desired):
    needs_change = False
    for key in desired:
        current_value = current[key]
        desired_value = desired[key]
        if current_value != desired_value:
            needs_change = True
            break
    #
    return needs_change

def get_association_id(client, module):
    cluster_name = module.params["cluster_name"]
    namespace = module.params["namespace"]
    service_account = module.params["service_account"]
    association_id = None
    try:
        response = client.list_pod_identity_associations(clusterName=cluster_name, namespace=namespace, serviceAccount=service_account)
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
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't get pod identity association details.")


def update_assocition(client, module, association_id):
    kwargs = _fill_kwargs(module, apply_defaults=False, ignore_create_params=True)
    cluster_name = module.params["cluster_name"]
    kwargs["associationId"] = association_id
    # get current state for comparison:
    api_result = get_association_info(client, module, association_id, cluster_name)
    association_arn = api_result["associationArn"]
    result = {
        "association_id": association_id, "association_arn": association_arn
    }
    changed = False
    if _needs_change(api_result, kwargs):
        changed = True
        if not module.check_mode:
            api_result = client.update_pod_identity_association(**kwargs)
            result = camel_dict_to_snake_dict(api_result["association"], ignore_list=["Tags"])
        #

    return {"association": result, "changed": changed}

def delete_association(client, module, association_id, cluster_name):

    try:
        response = client.delete_pod_identity_association(
            clusterName=cluster_name,
            associationId=association_id
        )
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't delete pod identity association.")

    return response

def create_assocition(client, module):
    kwargs = _fill_kwargs(module)

    changed = True
    result = client.create_pod_identity_association(**kwargs)

    return {"association": camel_dict_to_snake_dict(result, ignore_list=["Tags"]), "changed": changed}


def ensure_present(client, module):
    if module.check_mode:
        return {
            "association": {
                "association_arn": "fakeArn",
                "association_id": "fakeId"
                },
            "changed": True
        }

    association_id = get_association_id(client, module)
    if association_id:
        return update_assocition(client, module, association_id)

    return create_assocition(client, module)


def ensure_absent(client, module):
    cluster_name = module.params["cluster_name"]
    result = {"cluster_name": cluster_name, "association_id": None}
    if module.check_mode:
        return {"association": camel_dict_to_snake_dict(result, ignore_list=["Tags"]), "changed": True}
    association_id = get_association_id(client, module)
    result["association_id"] = association_id

    if not association_id:
        # silently ignore delete of unknown association
        return {"association": result, "changed": False}

    try:
        api_result = get_association_info(client, module, association_id, cluster_name)
        delete_association(client, module, association_id, cluster_name)
    except botocore.exceptions.ClientError as e:
        module.fail_json_aws(e)

    return {"association": result, "changed": True}

def main():
    argument_spec = dict(
        cluster_name=dict(type="str", required=True),
        role_arn=dict(type="str", required=True),
        target_role_arn=dict(type="str"),
        namespace=dict(type="str",required=True),
        service_account=dict(type="str", required=True),
        disable_session_tags=dict(type="bool", default=False),
        tags=dict(type="dict"),
        state=dict(choices=["absent", "present"], default="present"),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    try:
        client = module.client("eks")
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        module.fail_json_aws(e, msg="Couldn't connect to AWS.")

    if module.params.get("state") == "present":
        try:
            result = ensure_present(client, module)
        except botocore.exceptions.ClientError as e:
            module.fail_json_aws(e)
    else:
        try:
            result = ensure_absent(client, module)
        except botocore.exceptions.ClientError as e:
            module.fail_json_aws(e)

    module.exit_json(**result)            


if __name__ == "__main__":
    main()
