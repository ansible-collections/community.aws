#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: cognito_user_pool_client_info
version_added: 11.1.0
short_description: Retrieve information about AWS Cognito User Pool Clients
description:
  - Retrieves detailed information about one or all AWS Cognito User Pool Clients.
  - When I(client_id) or I(name) is provided, returns full details for that specific client.
  - When neither is provided, returns a list of all clients in the user pool.
notes:
  - This is an info module and does not modify any resources.
  - When listing all clients (no I(client_id) or I(name)), the returned list contains
    summary information only (client ID, name, user pool ID). Use I(client_id) to get
    full details for a specific client.
  - For details see U(https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_DescribeUserPoolClient.html).
author:
  - "Jonathan Springer (@jonpspri)"
options:
    user_pool_id:
        description:
          - The ID of the user pool.
        required: true
        type: str
    client_id:
        description:
          - The ID of a specific user pool client to describe.
          - Mutually exclusive with I(name).
        required: false
        type: str
    name:
        description:
          - The name of a specific user pool client to describe.
          - If multiple clients share the same name, the module will fail.
          - Mutually exclusive with I(client_id).
        required: false
        type: str
        aliases: ['client_name']
extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
# Get details of a specific client by ID
- community.aws.cognito_user_pool_client_info:
    user_pool_id: us-east-1_ABC123
    client_id: "1234567890abcdef"
  register: client_info

# Get details of a specific client by name
- community.aws.cognito_user_pool_client_info:
    user_pool_id: us-east-1_ABC123
    name: my-app-client
  register: client_info

# List all clients in a user pool
- community.aws.cognito_user_pool_client_info:
    user_pool_id: us-east-1_ABC123
  register: all_clients

- ansible.builtin.debug:
    msg: "Found {{ all_clients.clients | length }} clients"
"""

RETURN = r"""
client:
    description: Full details of the user pool client.
    returned: when I(client_id) or I(name) is provided
    type: complex
    contains:
        client_id:
            description: The ID of the user pool client.
            returned: always
            type: str
            sample: "1234567890abcdef"
        client_name:
            description: The name of the user pool client.
            returned: always
            type: str
            sample: "my-app-client"
        user_pool_id:
            description: The ID of the user pool.
            returned: always
            type: str
            sample: "us-east-1_ABC123"
        client_secret:
            description: The client secret.
            returned: when configured
            type: str
        callback_urls:
            description: List of callback URLs.
            returned: when configured
            type: list
            elements: str
        logout_urls:
            description: List of logout URLs.
            returned: when configured
            type: list
            elements: str
        allowed_oauth_flows:
            description: Allowed OAuth flows.
            returned: when configured
            type: list
            elements: str
        allowed_oauth_scopes:
            description: Allowed OAuth scopes.
            returned: when configured
            type: list
            elements: str
        supported_identity_providers:
            description: Supported identity providers.
            returned: when configured
            type: list
            elements: str
        creation_date:
            description: The date when the client was created.
            returned: always
            type: str
        last_modified_date:
            description: The date when the client was last modified.
            returned: always
            type: str
clients:
    description: List of user pool clients (summary information).
    returned: when neither I(client_id) nor I(name) is provided
    type: list
    elements: dict
    contains:
        client_id:
            description: The ID of the user pool client.
            returned: always
            type: str
        client_name:
            description: The name of the user pool client.
            returned: always
            type: str
        user_pool_id:
            description: The ID of the user pool.
            returned: always
            type: str
"""

try:
    import botocore
except ImportError:
    pass  # caught by AnsibleAWSModule

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule


def jsonize(client_data):
    """Convert datetime fields to strings for JSON serialization"""
    if client_data is None:
        return None
    result = dict(client_data)
    if "CreationDate" in result:
        result["CreationDate"] = str(result["CreationDate"])
    if "LastModifiedDate" in result:
        result["LastModifiedDate"] = str(result["LastModifiedDate"])
    return result


def main():
    argument_spec = dict(
        user_pool_id=dict(required=True, type="str"),
        client_id=dict(required=False, type="str"),
        name=dict(required=False, type="str", aliases=["client_name"]),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[["client_id", "name"]],
    )

    user_pool_id = module.params["user_pool_id"]
    client_id = module.params.get("client_id")
    client_name = module.params.get("name")

    try:
        client = module.client("cognito-idp")
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Failed to connect to AWS")

    try:
        # Find by name if needed
        if client_name and not client_id:
            matches = []
            paginator = client.get_paginator("list_user_pool_clients")
            for page in paginator.paginate(UserPoolId=user_pool_id, MaxResults=60):
                for c in page.get("UserPoolClients", []):
                    if c.get("ClientName") == client_name:
                        matches.append(c.get("ClientId"))
            if len(matches) == 0:
                module.fail_json(msg=f"User pool client with name '{client_name}' not found in pool '{user_pool_id}'")
            if len(matches) > 1:
                module.fail_json(
                    msg=f"Multiple user pool clients found with name '{client_name}': {matches}. "
                    "Use client_id to specify which client."
                )
            client_id = matches[0]

        if client_id:
            # Describe a specific client
            response = client.describe_user_pool_client(
                UserPoolId=user_pool_id,
                ClientId=client_id,
            )
            client_data = response.get("UserPoolClient")
            if client_data is None:
                module.fail_json(msg=f"User pool client '{client_id}' not found in pool '{user_pool_id}'")
            result = camel_dict_to_snake_dict(jsonize(client_data))
            module.exit_json(changed=False, client=result)
        else:
            # List all clients
            clients = []
            paginator = client.get_paginator("list_user_pool_clients")
            for page in paginator.paginate(UserPoolId=user_pool_id, MaxResults=60):
                for c in page.get("UserPoolClients", []):
                    clients.append(camel_dict_to_snake_dict(jsonize(c)))
            module.exit_json(changed=False, clients=clients)

    except client.exceptions.ResourceNotFoundException:
        if client_id:
            module.fail_json(msg=f"User pool client '{client_id}' not found in pool '{user_pool_id}'")
        else:
            module.fail_json(msg=f"User pool '{user_pool_id}' not found")
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Failed to describe user pool client")


if __name__ == "__main__":
    main()
