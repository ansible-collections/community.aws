#!/usr/bin/python
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: iam_managed_policy_attachment
short_description: Attach/detach managed policies from users, groups and roles
description:
    - Allows attaching and detaching managed policies for IAM users, groups and roles
version_added: "2.10"
options:
  iam_type:
    description:
      - Type of IAM resource
    required: True
    choices: [ "user", "group", "role"]
  iam_name:
    description:
      - Name of IAM resource you wish to target for policy actions. In other words, the user name, group name or role name.
    required: True
  policy_arn:
    description:
      - The ARN of the managed policy.
    required: True
  state:
    description:
      - Should this managed policy be present or absent on the IAM entity
    default: present
    choices: [ "present", "absent" ]
author: "Radoslaw Bobrowicz"
extends_documentation_fragment:
  - aws
  - ec2
requirements:
    - boto3
    - botocore
'''

EXAMPLES = '''
# Attach a policy to a role
- iam_managed_policy_attachment:
    iam_name: MyRole
    iam_type: role
    policy_arn: arn:aws:iam::123456789012:policy/AnsibleTestEC2Policy
    state: present

# Detach a policy from a user
- iam_managed_policy_attachment:
    iam_name: MyUser
    iam_type: user
    policy_arn: arn:aws:iam::123456789012:policy/AdministratorAccess
    state: absent
'''

RETURN = '''
iam_name:
    description: The IAM name of the user, group or role being operated on
    returned: always
    type: str
iam_type:
    description: The IAM type of the resource being managed (user, group or role)
    returned: always
    type: str
policies:
    description: List of attached managed policies
    returned: always
    type: complex
    contains:
        policy_arn:
            description: Amazon Resource Name for the policy
            returned: always
            type: str
            sample: arn:aws:iam::123456789012:policy/AnsibleTestEC2Policy
        policy_name:
            description: Name of managed policy
            returned: always
            type: str
            sample: AnsibleTestEC2Policy
'''

import json
import traceback

try:
    import botocore
except ImportError:
    pass  # caught by imported HAS_BOTO3

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.ec2 import (boto3_conn, HAS_BOTO3, ec2_argument_spec,
                                      get_aws_connection_info, camel_dict_to_snake_dict)

def is_policy_present(policies, policy_arn):
    policy_present = False
    for p in policies:
        if p['PolicyArn'] == policy_arn:
            policy_present = True
            break
    return policy_present

def get_attached_role_policies(module, iam, role_name):
    try:
        response = iam.list_attached_role_policies(RoleName=role_name)
        policies = response['AttachedPolicies']
        while response['IsTruncated']:
            response = iam.list_attached_role_policies(RoleName=role_name,
                                                       Marker=response['Marker'])
            policies.extend(response['AttachedPolicies'])
    except botocore.exceptions.ClientError as e:
        module.fail_json(msg="Couldn't get attached role policies: %s" % str(e),
                         exception=traceback.format_exc(),
                         **camel_dict_to_snake_dict(e.response))
    return policies

def get_attached_user_policies(module, iam, user_name):
    try:
        response = iam.list_attached_user_policies(UserName=user_name)
        policies = response['AttachedPolicies']
        while response['IsTruncated']:
            response = iam.list_attached_user_policies(UserName=user_name,
                                                       Marker=response['Marker'])
            policies.extend(response['AttachedPolicies'])
    except botocore.exceptions.ClientError as e:
        module.fail_json(msg="Couldn't get attached user policies: %s" % str(e),
                         exception=traceback.format_exc(),
                         **camel_dict_to_snake_dict(e.response))
    return policies

def get_attached_group_policies(module, iam, group_name):
    try:
        response = iam.list_attached_group_policies(GroupName=group_name)
        policies = response['AttachedPolicies']
        while response['IsTruncated']:
            response = iam.list_attached_group_policies(GroupName=group_name,
                                                        Marker=response['Marker'])
            policies.extend(response['AttachedPolicies'])
    except botocore.exceptions.ClientError as e:
        module.fail_json(msg="Couldn't get attached group policies: %s" % str(e),
                         exception=traceback.format_exc(),
                         **camel_dict_to_snake_dict(e.response))
    return policies

def role_action(module, iam, role_name, policy_arn, state):
    changed = False
    policies = get_attached_role_policies(module, iam, role_name)
    policy_present = is_policy_present(policies, policy_arn)

    if state == 'present':
        if policy_present:
            changed = False
        else:
            try:
                iam.attach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
                changed = True
            except botocore.exceptions.ClientError as e:
                module.fail_json(msg="Couldn't attach role policy: %s" % str(e),
                                exception=traceback.format_exc(),
                                **camel_dict_to_snake_dict(e.response))
    else:
        if policy_present:
            try:
                iam.detach_role_policy(RoleName=role_name, PolicyArn=policy_arn)
                changed = True
            except botocore.exceptions.ClientError as e:
                module.fail_json(msg="Couldn't detach role policy: %s" % str(e),
                                exception=traceback.format_exc(),
                                **camel_dict_to_snake_dict(e.response))
        else:
            changed = False

    if changed:
        policies = get_attached_role_policies(module, iam, role_name)

    return changed, policies

def user_action(module, iam, user_name, policy_arn, state):
    changed = False
    policies = get_attached_user_policies(module, iam, user_name)
    policy_present = is_policy_present(policies, policy_arn)

    if state == 'present':
        if policy_present:
            changed = False
        else:
            try:
                iam.attach_user_policy(UserName=user_name, PolicyArn=policy_arn)
                changed = True
            except botocore.exceptions.ClientError as e:
                module.fail_json(msg="Couldn't attach user policy: %s" % str(e),
                                exception=traceback.format_exc(),
                                **camel_dict_to_snake_dict(e.response))
    else:
        if policy_present:
            try:
                iam.detach_user_policy(UserName=user_name, PolicyArn=policy_arn)
                changed = True
            except botocore.exceptions.ClientError as e:
                module.fail_json(msg="Couldn't detach user policy: %s" % str(e),
                                exception=traceback.format_exc(),
                                **camel_dict_to_snake_dict(e.response))
        else:
            changed = False

    if changed:
        policies = get_attached_user_policies(module, iam, user_name)

    return changed, policies

def group_action(module, iam, group_name, policy_arn, state):
    changed = False
    policies = get_attached_group_policies(module, iam, group_name)
    policy_present = is_policy_present(policies, policy_arn)

    if state == 'present':
        if policy_present:
            changed = False
        else:
            try:
                iam.attach_group_policy(GroupName=group_name, PolicyArn=policy_arn)
                changed = True
            except botocore.exceptions.ClientError as e:
                module.fail_json(msg="Couldn't attach group policy: %s" % str(e),
                                exception=traceback.format_exc(),
                                **camel_dict_to_snake_dict(e.response))
    else:
        if policy_present:
            try:
                iam.detach_group_policy(GroupName=group_name, PolicyArn=policy_arn)
                changed = True
            except botocore.exceptions.ClientError as e:
                module.fail_json(msg="Couldn't detach group policy: %s" % str(e),
                                exception=traceback.format_exc(),
                                **camel_dict_to_snake_dict(e.response))
        else:
            changed = False

    if changed:
        policies = get_attached_group_policies(module, iam, group_name)

    return changed, policies

def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(dict(
        iam_name=dict(default=None, required=True),
        iam_type=dict(
            default=None, required=True, choices=['user', 'group', 'role']),
        policy_arn=dict(default=None, required=True),
        state=dict(
            default=None, required=True, choices=['present', 'absent']),
    ))

    module = AnsibleModule(
        argument_spec=argument_spec,
    )

    if not HAS_BOTO3:
        module.fail_json(msg='boto3 is required for this module')

    iam_name = module.params.get('iam_name')
    iam_type = module.params.get('iam_type').lower()
    policy_arn = module.params.get('policy_arn')
    state = module.params.get('state')

    try:
        region, ec2_url, aws_connect_kwargs = get_aws_connection_info(module, boto3=True)
        iam = boto3_conn(module, conn_type='client', resource='iam',
                         region=region, endpoint=ec2_url, **aws_connect_kwargs)
    except (botocore.exceptions.NoCredentialsError, botocore.exceptions.ProfileNotFound) as e:
        module.fail_json(
            msg="Can't authorize connection. Check your credentials and profile.",
            exceptions=traceback.format_exc(),
            **camel_dict_to_snake_dict(e.response))

    changed = False
    current_policies = None

    if iam_type == 'user':
        changed, current_policies = user_action(module, iam, iam_name, policy_arn, state)
    elif iam_type == 'group':
        changed, current_policies = group_action(module, iam, iam_name, policy_arn, state)
    elif iam_type == 'role':
        changed, current_policies = role_action(module, iam, iam_name, policy_arn, state)

    current_policies = [ camel_dict_to_snake_dict(p) for p in current_policies ]

    module.exit_json(changed=changed, iam_name=iam_name, iam_type=iam_type,
                     policies=current_policies)

# end main

if __name__ == '__main__':
    main()
