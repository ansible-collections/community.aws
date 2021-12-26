#!/usr/bin/python
# Copyright (c) 2018 Ansible Project
# Copyright (c) 2021 Alina Buzachis (@alinabuzachis)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
---
module: aws_amp_rule
short_description: Amazon Managed Service for Prometheus.
version_added: "3.0.0"
description:
    - Create, delete and modify a rule group namespace.
author:
    - Alina Buzachis (@alinabuzachis)
options:
    state:
        description: Create (C(present)) or delete (C(absent)) cluster.
        choices: ['present', 'absent']
        type: str
        default: 'present'
    client_token:
        description:
            - Optional, unique, case-sensitive, user-provided identifier to ensure the idempotency of the request.
            - This field is autopopulated if not provided.
        type: str
    data:
        description:
            - The alert manager definition data.
        type: str
    name:
        description:
            - The rule groups namespace name.
        type: str
    tags:
        description:
            - Optional, user-provided tags for this workspace.
        type: dict
    workspace_id:
        description:
            - The ID of the workspace.
        type: str  
"""

EXAMPLES = r"""

"""

RETURN = r"""

"""

import time
from base64 import b64decode

try:
    import botocore
except ImportError:
    pass  # handled by AnsibleAWSModule

from ansible.module_utils._text import to_bytes

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AWSRetry


def describe_rule_groups_namespace():
    params = {}
    params["name"] = module.params.get("name")
    params["workspace_id"] = module.params.get("workspace_id")

    try:
        results = client.describe_rule_groups_namespace(aws_retry=True, **params)
    except is_boto3_error_code('ResourceNotFoundException'):
        return {}
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Could not describe rule groups namespace")

    return results


def create_rule_groups_namespace():
    params = {}
    result = {}
    existing = None

    if module.params.get("client_token"):
        params["clientToken"] = module.params.get("client_token")
    
    params["name"] = module.params.get("name")
    params["workspace_id"] = module.params.get("workspace_id")

    # TODO: Handle tags update
    params["tags"] = module.params.get("tags")

    existing = list_alert_manager_definition()

    if existing:
        # We probably would like to update a workspace.
        existing_data = b64decode(existing["data"])

        if exsiting_data == module.params.get("data"):
            module.exit_json(changed=False, **result)
        
        params["data"] = module.params.get("data")

        try:
            result = client.put_rule_groups_namespace(aws_retry=True, **params)
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Could not update rule groups namespace")
    else:
        # There is no alert manager definition in the workspace. We need to create it.
        params["data"] = module.params.get("data")

        try:
            result = client.create_rule_groups_namespace(aws_retry=True, **params)
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Could not create rule groups namespace")


def delete_rule_groups_namespace():
    params = {}
    result = {}

    if module.params.get("client_token"):
        params["clientToken"] = module.params.get("client_token")
    
    params["name"] = module.params.get("name")
    params["workspaceId"] = module.params.get("workspace_id")

    try:
        result = client.delete_rule_groups_namespace(aws_retry=True, **params)
    except is_boto3_error_code('ResourceNotFoundException'):
        module.exit_json(changed=True, **result)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Could not delete rule groups namespace")

def main():
    global module
    global client

    arg_spec = dict(
        state=dict(choices=['present', 'absent'], default='present'),
        alias=dict(type='str'),
        client_token=dict(type='str'),
        tags=dict(type='dict'),
        workspace_id=dict(type='str'),
    )
    
    module = AnsibleAWSModule(
        argument_spec=arg_spec,
        required_if=[
            ('state', 'absent', ('workspace_id')),
        ],
        supports_check_mode=True
    )

    retry_decorator = AWSRetry.jittered_backoff(retries=10)

    try:
        client = module.client('amp', retry_decorator=retry_decorator)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg='Failed to connect to AWS.')
    
    if module.params.get("state") == "present":
        create_rule_groups_namespace()
    else:
        delete_rule_groups_namespace()


if __name__ == "__main__":
    main()
