#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: cognito_managed_login_branding_info
version_added: 11.1.0
short_description: Retrieve information about AWS Cognito Managed Login Branding styles
description:
  - Retrieves detailed information about an AWS Cognito Managed Login Branding style.
  - Can look up by I(managed_login_branding_id) or by I(client_id).
  - Optionally returns merged resources (Cognito defaults combined with customizations).
notes:
  - This is an info module and does not modify any resources.
  - For details see U(https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_DescribeManagedLoginBranding.html).
author:
  - "Jonathan Springer (@jonpspri)"
options:
    user_pool_id:
        description:
          - The ID of the user pool.
        required: true
        type: str
    managed_login_branding_id:
        description:
          - The ID of the managed login branding style to describe.
          - Mutually exclusive with I(client_id).
        required: false
        type: str
    client_id:
        description:
          - The app client ID to look up the branding style for.
          - Mutually exclusive with I(managed_login_branding_id).
        required: false
        type: str
    return_merged_resources:
        description:
          - When true, the response includes branding values unchanged from Cognito defaults.
          - When false, only returns customized branding values.
        required: false
        type: bool
        default: false
extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
# Get branding info by client ID
- community.aws.cognito_managed_login_branding_info:
    user_pool_id: us-east-1_ABC123
    client_id: "1234567890abcdef"
  register: branding_info

# Get branding info by branding ID with merged resources
- community.aws.cognito_managed_login_branding_info:
    user_pool_id: us-east-1_ABC123
    managed_login_branding_id: "12345678-1234-4123-8123-123456789012"
    return_merged_resources: true
  register: branding_info

# Display the branding settings
- ansible.builtin.debug:
    msg: "Branding ID: {{ branding_info.branding.managed_login_branding_id }}"
"""

RETURN = r"""
branding:
    description: Details of the managed login branding style.
    returned: success
    type: complex
    contains:
        managed_login_branding_id:
            description: The ID of the managed login branding style.
            returned: always
            type: str
            sample: "12345678-1234-4123-8123-123456789012"
        user_pool_id:
            description: The ID of the user pool.
            returned: always
            type: str
        client_id:
            description: The app client ID associated with this branding.
            returned: always
            type: str
        use_cognito_provided_values:
            description: Whether Cognito-provided default values are used.
            returned: always
            type: bool
        settings:
            description: The branding style settings.
            returned: when available
            type: dict
        assets:
            description: The branding assets.
            returned: when available
            type: list
            elements: dict
        creation_date:
            description: The date when the branding style was created.
            returned: always
            type: str
        last_modified_date:
            description: The date when the branding style was last modified.
            returned: always
            type: str
"""

try:
    import botocore
except ImportError:
    pass  # caught by AnsibleAWSModule

import base64

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule


def jsonize(branding_data):
    """Convert datetime and binary fields for JSON serialization"""
    if branding_data is None:
        return None
    result = dict(branding_data)
    if "CreationDate" in result:
        result["CreationDate"] = str(result["CreationDate"])
    if "LastModifiedDate" in result:
        result["LastModifiedDate"] = str(result["LastModifiedDate"])
    if "Assets" in result:
        sanitized_assets = []
        for asset in result["Assets"]:
            asset = dict(asset)
            if "Bytes" in asset and isinstance(asset["Bytes"], bytes):
                asset["Bytes"] = base64.b64encode(asset["Bytes"]).decode("ascii")
            sanitized_assets.append(asset)
        result["Assets"] = sanitized_assets
    return result


def main():
    argument_spec = dict(
        user_pool_id=dict(required=True, type="str"),
        managed_login_branding_id=dict(required=False, type="str"),
        client_id=dict(required=False, type="str"),
        return_merged_resources=dict(required=False, type="bool", default=False),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[["managed_login_branding_id", "client_id"]],
        mutually_exclusive=[["managed_login_branding_id", "client_id"]],
    )

    user_pool_id = module.params["user_pool_id"]
    branding_id = module.params.get("managed_login_branding_id")
    client_id = module.params.get("client_id")
    return_merged = module.params.get("return_merged_resources", False)

    try:
        client = module.client("cognito-idp")
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Failed to connect to AWS")

    try:
        branding = None
        if branding_id:
            response = client.describe_managed_login_branding(
                UserPoolId=user_pool_id,
                ManagedLoginBrandingId=branding_id,
                ReturnMergedResources=return_merged,
            )
            branding = response.get("ManagedLoginBranding")
        else:
            response = client.describe_managed_login_branding_by_client(
                UserPoolId=user_pool_id,
                ClientId=client_id,
                ReturnMergedResources=return_merged,
            )
            branding = response.get("ManagedLoginBranding")

        if branding is None:
            lookup = branding_id or client_id
            module.fail_json(msg=f"Managed login branding not found for '{lookup}' in pool '{user_pool_id}'")

        result = camel_dict_to_snake_dict(jsonize(branding))
        module.exit_json(changed=False, branding=result)

    except client.exceptions.ResourceNotFoundException:
        lookup = branding_id or client_id
        module.fail_json(msg=f"Managed login branding not found for '{lookup}' in pool '{user_pool_id}'")
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Failed to describe managed login branding")


if __name__ == "__main__":
    main()
