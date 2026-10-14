#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: cognito_user_pool_info
version_added: 11.1.0
short_description: Retrieve information about an AWS Cognito User Pool
description:
  - Retrieves detailed information about an AWS Cognito User Pool using the DescribeUserPool API.
  - Returns user pool configuration including domain, ARN, policies, and other settings.
  - Useful for obtaining the user pool domain for ALB authenticate-cognito configuration.
notes:
  - This is an info module and does not modify any resources.
  - For details see U(https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_DescribeUserPool.html).
author:
  - "Jonathan Springer (@jonpspri)"
options:
    user_pool_id:
        description:
          - The ID of the user pool to describe.
        required: true
        type: str
extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
# Get information about a user pool
- cognito_user_pool_info:
    user_pool_id: us-east-1_ABC123
  register: user_pool_info

# Use the domain for ALB authenticate-cognito configuration
- name: Get user pool info for ALB configuration
  cognito_user_pool_info:
    user_pool_id: "{{ cognito_user_pool_id }}"
  register: cognito_pool_r

- name: Display the user pool domain
  ansible.builtin.debug:
    msg: "User pool domain: {{ cognito_pool_r.user_pool.domain }}"
"""

RETURN = r"""
user_pool:
    description: Details of the user pool.
    returned: success
    type: complex
    contains:
        id:
            description: The ID of the user pool.
            returned: always
            type: str
            sample: "us-east-1_ABC123"
        name:
            description: The name of the user pool.
            returned: always
            type: str
            sample: "my-user-pool"
        arn:
            description: The Amazon Resource Name (ARN) of the user pool.
            returned: always
            type: str
            sample: "arn:aws:cognito-idp:us-east-1:123456789012:userpool/us-east-1_ABC123"
        domain:
            description: The Cognito domain prefix for the user pool.
            returned: when configured
            type: str
            sample: "my-app-domain"
        custom_domain:
            description: The custom domain configured for the user pool.
            returned: when configured
            type: str
            sample: "auth.example.com"
        status:
            description: The status of the user pool.
            returned: always
            type: str
            sample: "Enabled"
        creation_date:
            description: The date the user pool was created.
            returned: always
            type: str
        last_modified_date:
            description: The date the user pool was last modified.
            returned: always
            type: str
        estimated_number_of_users:
            description: The estimated number of users in the pool.
            returned: always
            type: int
        mfa_configuration:
            description: The MFA configuration for the user pool.
            returned: always
            type: str
            sample: "OFF"
        user_pool_tier:
            description: The tier of the user pool.
            returned: when available
            type: str
        deletion_protection:
            description: Whether deletion protection is enabled.
            returned: when available
            type: str
        policies:
            description: The password and sign-in policies for the user pool.
            returned: always
            type: dict
        lambda_config:
            description: The Lambda triggers configured for the user pool.
            returned: always
            type: dict
        schema_attributes:
            description: The schema attributes for the user pool.
            returned: always
            type: list
            elements: dict
        auto_verified_attributes:
            description: Attributes that are automatically verified.
            returned: when configured
            type: list
            elements: str
        alias_attributes:
            description: Attributes that can be used as aliases.
            returned: when configured
            type: list
            elements: str
        username_attributes:
            description: Attributes used for username.
            returned: when configured
            type: list
            elements: str
        email_configuration:
            description: Email configuration for the user pool.
            returned: when configured
            type: dict
        sms_configuration:
            description: SMS configuration for the user pool.
            returned: when configured
            type: dict
        user_pool_tags:
            description: Tags associated with the user pool.
            returned: when configured
            type: dict
        admin_create_user_config:
            description: Admin create user configuration.
            returned: always
            type: dict
        account_recovery_setting:
            description: Account recovery settings.
            returned: when configured
            type: dict
"""

try:
    import botocore
except ImportError:
    pass  # caught by AnsibleAWSModule

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule


def describe_user_pool(client, user_pool_id):
    """Retrieve user pool information"""
    response = client.describe_user_pool(UserPoolId=user_pool_id)
    return response.get("UserPool")


def jsonize(user_pool_data):
    """Convert datetime fields to strings for JSON serialization"""
    if user_pool_data is None:
        return None
    result = dict(user_pool_data)
    if "CreationDate" in result:
        result["CreationDate"] = str(result["CreationDate"])
    if "LastModifiedDate" in result:
        result["LastModifiedDate"] = str(result["LastModifiedDate"])
    return result


def main():
    argument_spec = dict(
        user_pool_id=dict(required=True, type="str"),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    user_pool_id = module.params["user_pool_id"]

    try:
        client = module.client("cognito-idp")
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Failed to connect to AWS")

    try:
        user_pool = describe_user_pool(client, user_pool_id)

        if user_pool is None:
            module.fail_json(msg=f"User pool {user_pool_id} not found")

        result = camel_dict_to_snake_dict(jsonize(user_pool), ignore_list=["UserPoolTags"])
        module.exit_json(changed=False, user_pool=result)

    except client.exceptions.ResourceNotFoundException:
        module.fail_json(msg=f"User pool {user_pool_id} not found")
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg=f"Failed to describe user pool {user_pool_id}")


if __name__ == "__main__":
    main()
