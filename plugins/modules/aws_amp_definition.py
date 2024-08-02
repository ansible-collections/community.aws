#!/usr/bin/python
# Copyright (c) 2018 Ansible Project
# Copyright (c) 2021 Alina Buzachis (@alinabuzachis)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r"""
---
module: aws_amp_definition
short_description: Amazon Managed Service for Prometheus.
version_added: "3.0.0"
description:
    - Create, delete and modify an alert manager definition.
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
    workspace_id:
        description:
            - The ID of the workspace in which to create the alert manager definition.
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


def describe_alert_manager_definition():
    try:
        results = client.describe_alert_manager_definition(aws_retry=True, workspaceId=module.params.get("workspace_id"))
    except is_boto3_error_code('ResourceNotFoundException'):
        return {}
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Could not describe alert manager definition")

    return results


def create_alert_manager_definition():
    params = {}
    result = {}
    existing = None

    if module.params.get("client_token"):
        params["clientToken"] = module.params.get("client_token")
    
    params["workspaceId"] = module.params.get("workspace_id")

    existing = describe_alert_manager_definition()

    if existing:
        # We probably would like to update an alert manager definition.
        existing_data = b64decode(existing["data"])

        if exsiting_data == module.params.get("data"):
            module.exit_json(changed=False, **result)
        
        params["data"] = to_bytes(module.params.get("data"))

        try:
            result = client.put_alert_manager_definition(aws_retry=True, **params)
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Could not update alert manager definition data")
    else:
        # There is no alert manager definition in the workspace. We need to create it.
        params["data"] = to_bytes(module.params.get("data"))

        try:
            result = client.create_alert_manager_definition(aws_retry=True, **params)
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Could not create an alert manager definition")


def delete_alert_manager_definition():
    params = {}
    result = {}

    if module.params.get("client_token"):
        params["clientToken"] = module.params.get("client_token")
    
    params["workspaceId"] = module.params.get("workspace_id")

    try:
        result = client.delete_alert_manager_definition(aws_retry=True, **params)
    except is_boto3_error_code('ResourceNotFoundException'):
        module.exit_json(changed=True, **result)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Could not delete the alert manager definition")

def main():
    global module
    global client

    arg_spec = dict(
        state=dict(choices=['present', 'absent'], default='present'),
        client_token=dict(type='str'),
        data=dict(type='str'),
        workspace_id=dict(type='str', required=True),
    )
    
    module = AnsibleAWSModule(
        argument_spec=arg_spec,
        required_if=[
            ('state', 'present', ('data')),
        ],
        supports_check_mode=True
    )

    retry_decorator = AWSRetry.jittered_backoff(retries=10)

    try:
        client = module.client('amp', retry_decorator=retry_decorator)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg='Failed to connect to AWS.')
    
    if module.params.get("state") == "present":
        create_alert_manager_definition()
    else:
        delete_alert_manager_definition()


if __name__ == "__main__":
    main()
