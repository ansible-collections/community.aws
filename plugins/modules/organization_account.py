#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible_collections.community.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.community.aws.plugins.module_utils.retries import AWSRetry
import time

try:
    from botocore.exceptions import ClientError
except ImportError:
    pass


DOCUMENTATION = r'''
---
module: organization_account
version_added: 7.0.0
short_description: Creates or moves AWS accounts within an Organization
description:
  - Module to create AWS accounts in an Organization and move existing accounts to Organizational Units (OUs).
  - This module supports creating new AWS accounts with optional custom IAM role names and tags.
  - It also supports moving existing accounts between Organizational Units.
options:
    action:
        description: Action to be performed create or move an account.
        required: true
        type: str
        choices: ['create_account', 'move_account']
    email:
        description:
          - Email for the account to be created. Required for create_account.
        required: false
        type: str
    name:
        description:
          - Name of the account to be created. Required for create_account.
        required: false
        type: str
    admin_role_name:
        description:
          - Name of the IAM role to be created by default in the new account (e.g., 'OrganizationAccountAccessRole').
        required: false
        type: str
    tags:
        description:
          - A list of tags (key/value) to apply to the new account.
        required: false
        type: list
        elements: dict
    id:
        description:
          - ID of the account to be moved. Required for move_account.
        required: false
        type: str
    ou_id:
        description:
          - ID of the destination OU. Required for move_account.
        required: false
        type: str
    aws_access_key:
        description:
          - AWS access key ID. If not set then the value of the AWS_ACCESS_KEY_ID, AWS_ACCESS_KEY, or EC2_ACCESS_KEY environment variable is used.
        required: false
        type: str
        aliases: ['ec2_access_key', 'access_key']
    aws_secret_key:
        description:
          - AWS secret access key. If not set then the value of the AWS_SECRET_ACCESS_KEY, AWS_SECRET_KEY, or EC2_SECRET_KEY environment variable is used.
        required: false
        type: str
        aliases: ['ec2_secret_key', 'secret_key']
    aws_security_token:
        description:
          - AWS STS security token. If not set then the value of the AWS_SECURITY_TOKEN or EC2_SECURITY_TOKEN environment variable is used.
        required: false
        type: str
        aliases: ['access_token']
    region:
        description:
          - The AWS region to use. If not specified then the value of the AWS_REGION or EC2_REGION environment variable, if any, is used.
        required: false
        type: str
        aliases: ['aws_region', 'ec2_region']
    profile:
        description:
          - Uses a boto profile. Only works with boto >= 2.24.0.
        required: false
        type: str
    validate_certs:
        description:
          - When set to "no", SSL certificates will not be validated for boto versions >= 2.6.0.
        required: false
        type: bool
        default: true
author:
    - Lauro Gomes (@laurobmb)
'''

EXAMPLES = r'''
# Note: These examples do not set authentication details, see the AWS Guide for details.

- name: Create new AWS account (simple)
  laurobmb.aws.organization_account:
    action: create_account
    email: "admin@company.com"
    name: "DemoProject"
  register: create_account_result

- name: Create new AWS account with custom Role and Tags
  laurobmb.aws.organization_account:
    action: create_account
    email: "admin@company.com"
    name: "DemoProjectWithTags"
    admin_role_name: "CustomOrganizationRole"
    tags:
      - Key: Environment
        Value: Production
      - Key: BilledTo
        Value: "Dept-123"
  register: create_account_custom_result

- name: Move the newly created account to the destination OU
  laurobmb.aws.organization_account:
    action: move_account
    id: "{{ create_account_result.status.AccountId }}"
    ou_id: "ou-jojo-zeg98nd3"
  when: create_account_result.changed
'''

RETURN = r'''
msg:
    description: Summary message of the action performed
    type: str
    returned: always
    sample: "Account 123456789012 created successfully for the project DemoProject."
changed:
    description: Indicates if a change was made to the environment
    type: bool
    returned: always
status:
    description: Detailed status of the account creation (only for create_account)
    type: dict
    returned: when action is create_account
    contains:
        AccountId:
            description: The ID of the created account
            type: str
            sample: "123456789012"
        State:
            description: The state of the account creation
            type: str
            sample: "SUCCEEDED"
response:
    description: Response from the AWS API (only for move_account)
    type: dict
    returned: when action is move_account
'''


@AWSRetry.jittered_backoff()
def get_current_parent_id(client, id):
    """Get the current Parent ID (Root or OU) of an account."""
    parents = client.list_parents(ChildId=id)
    return parents['Parents'][0]['Id']


@AWSRetry.jittered_backoff()
def move_account(client, id, ou_id):
    """Move an account to a new OU."""
    try:
        source_parent_id = get_current_parent_id(client, id)

        if source_parent_id == ou_id:
            return dict(
                changed=False,
                msg=f"Account {id} is already in the destination OU {ou_id}."
            )

        response = client.move_account(
            AccountId=id,
            SourceParentId=source_parent_id,
            DestinationParentId=ou_id
        )
        return dict(
            changed=True,
            msg=f"Account {id} moved from {source_parent_id} to {ou_id}.",
            response=response
        )
    except ClientError as e:
        return dict(
            failed=True,
            msg=f"Error moving account: {e.response['Error']['Message']}"
        )


@AWSRetry.jittered_backoff()
def create_account(client, email, name, admin_role_name=None, tags=None):
    """
    Create a new account in AWS Organization with optional RoleName and Tags,
    and wait for its completion.
    """
    try:
        params = {
            'Email': email,
            'AccountName': name,
            'IamUserAccessToBilling': 'ALLOW'
        }
        if admin_role_name:
            params['RoleName'] = admin_role_name
        if tags:
            params['Tags'] = tags

        response = client.create_account(**params)
        request_id = response['CreateAccountStatus']['Id']

        while True:
            status_response = client.describe_create_account_status(
                CreateAccountRequestId=request_id
            )
            status = status_response['CreateAccountStatus']
            state = status['State']

            if state == 'SUCCEEDED':
                return dict(
                    changed=True,
                    msg=f"Account {status['AccountId']} created successfully for the project {name}.",
                    status=status
                )

            if state == 'FAILED':
                return dict(
                    failed=True,
                    msg=f"Account creation failed. Reason: {status.get('FailureReason', 'Not specified')}"
                )

            time.sleep(15)

    except ClientError as e:
        return dict(
            failed=True,
            msg=f"AWS API error when creating account: {e.response['Error']['Message']}"
        )


def run_module():
    module_args = dict(
        action=dict(type='str', required=True, choices=['create_account', 'move_account']),
        email=dict(type='str', required=False),
        name=dict(type='str', required=False),
        admin_role_name=dict(type='str', required=False),
        tags=dict(type='list', elements='dict', required=False),
        id=dict(type='str', required=False),
        ou_id=dict(type='str', required=False),
        aws_access_key=dict(type='str', required=False, aliases=['ec2_access_key', 'access_key']),
        aws_secret_key=dict(type='str', required=False, aliases=['ec2_secret_key', 'secret_key'], no_log=True),
        aws_security_token=dict(type='str', required=False, aliases=['access_token'], no_log=True),
        region=dict(type='str', required=False, aliases=['aws_region', 'ec2_region']),
        profile=dict(type='str', required=False),
        validate_certs=dict(type='bool', required=False, default=True),
    )

    module = AnsibleAWSModule(
        argument_spec=module_args,
        supports_check_mode=False,
        required_if=[
            ('action', 'create_account', ['email', 'name']),
            ('action', 'move_account', ['id', 'ou_id']),
        ]
    )

    action = module.params['action']
    result = {}

    try:
        client = module.client('organizations')
    except Exception as e:
        module.fail_json(msg=f"Failed to initialize boto3 client: {str(e)}")

    if action == 'create_account':
        result = create_account(
            client=client,
            email=module.params['email'],
            name=module.params['name'],
            admin_role_name=module.params['admin_role_name'],
            tags=module.params['tags']
        )

    elif action == 'move_account':
        result = move_account(client, module.params['id'], module.params['ou_id'])

    if result.get("failed"):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
