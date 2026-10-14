#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: cognito_managed_login_branding
version_added: 11.1.0
short_description: Manage AWS Cognito Managed Login Branding styles
description:
  - Creates, updates, or deletes AWS Cognito Managed Login Branding styles.
  - Managed login branding allows customization of the Cognito hosted UI appearance.
  - Supports custom assets (logos, backgrounds, icons) and style settings.
notes:
  - The total request size for assets and settings combined cannot exceed 2 megabytes.
  - When using I(use_cognito_provided_values=true), omit I(settings) and I(assets).
  - You can find the branding style either by I(managed_login_branding_id) or by I(client_id).
  - For details see U(https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_CreateManagedLoginBranding.html).
author:
  - "Jonathan Springer (@jonpspri)"
options:
    state:
        description:
          - The desired state of the managed login branding style.
        required: true
        choices: ["present", "absent"]
        type: str
    user_pool_id:
        description:
          - The ID of the user pool where the branding style exists or should be created.
        required: true
        type: str
    client_id:
        description:
          - The app client that the branding style is assigned to.
          - Required when I(state=present) and creating a new branding style.
          - Can be used to find an existing branding style instead of I(managed_login_branding_id).
        required: false
        type: str
    managed_login_branding_id:
        description:
          - The ID of an existing managed login branding style.
          - If not provided, the module will attempt to find the branding by I(client_id).
        required: false
        type: str
    use_cognito_provided_values:
        description:
          - When true, applies the default branding style options managed by Amazon Cognito.
          - When set to true, omit I(settings) and I(assets) parameters.
          - Useful for initializing branding with defaults that can be modified later.
        required: false
        type: bool
    settings:
        description:
          - A JSON object with the style settings to apply.
          - Contains branding configuration like colors, fonts, and component styles.
          - Cannot be used when I(use_cognito_provided_values=true).
        required: false
        type: dict
    assets:
        description:
          - List of image assets for backgrounds, logos, and icons.
          - Each asset specifies the image data, category, and color mode.
          - Maximum 40 assets allowed.
          - Cannot be used when I(use_cognito_provided_values=true).
        required: false
        type: list
        elements: dict
        suboptions:
            category:
                description:
                  - The category of the asset.
                type: str
                required: true
                choices:
                  - FAVICON_ICO
                  - FAVICON_SVG
                  - EMAIL_GRAPHIC
                  - SMS_GRAPHIC
                  - AUTH_APP_GRAPHIC
                  - PASSWORD_GRAPHIC
                  - PASSKEY_GRAPHIC
                  - PAGE_HEADER_LOGO
                  - PAGE_HEADER_BACKGROUND
                  - PAGE_FOOTER_LOGO
                  - PAGE_FOOTER_BACKGROUND
                  - PAGE_BACKGROUND
                  - FORM_BACKGROUND
                  - FORM_LOGO
                  - IDP_BUTTON_ICON
            color_mode:
                description:
                  - The color mode for this asset.
                type: str
                required: true
                choices:
                  - LIGHT
                  - DARK
                  - DYNAMIC
            bytes:
                description:
                  - Base64-encoded image data.
                  - Use this or I(resource_id), not both.
                type: str
            resource_id:
                description:
                  - The ID of a previously uploaded resource.
                  - Use this or I(bytes), not both.
                type: str
            extension:
                description:
                  - The file extension of the asset.
                type: str
                choices:
                  - ICO
                  - JPEG
                  - PNG
                  - SVG
                  - WEBP
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
# Create a branding style with Cognito defaults
- cognito_managed_login_branding:
    state: present
    user_pool_id: us-east-1_ABC123
    client_id: "1234567890abcdef"
    use_cognito_provided_values: true

# Create a branding style with custom settings
- cognito_managed_login_branding:
    state: present
    user_pool_id: us-east-1_ABC123
    client_id: "1234567890abcdef"
    settings:
      components:
        pageHeader:
          logoUrl: "https://example.com/logo.png"
        primaryButton:
          defaults:
            backgroundColor: "#007bff"

# Create a branding style with custom logo asset
- cognito_managed_login_branding:
    state: present
    user_pool_id: us-east-1_ABC123
    client_id: "1234567890abcdef"
    assets:
      - category: PAGE_HEADER_LOGO
        color_mode: LIGHT
        bytes: "{{ lookup('file', 'logo.png') | b64encode }}"
        extension: PNG

# Update an existing branding style by ID
- cognito_managed_login_branding:
    state: present
    user_pool_id: us-east-1_ABC123
    managed_login_branding_id: "12345678-1234-4123-8123-123456789012"
    settings:
      components:
        primaryButton:
          defaults:
            backgroundColor: "#28a745"

# Delete a branding style
- cognito_managed_login_branding:
    state: absent
    user_pool_id: us-east-1_ABC123
    client_id: "1234567890abcdef"

# Delete a branding style by ID
- cognito_managed_login_branding:
    state: absent
    user_pool_id: us-east-1_ABC123
    managed_login_branding_id: "12345678-1234-4123-8123-123456789012"
"""

RETURN = r"""
branding:
    description: Details of the managed login branding style.
    returned: when state is present
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
            sample: "us-east-1_ABC123"
        client_id:
            description: The app client ID associated with this branding.
            returned: always
            type: str
            sample: "1234567890abcdef"
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
import binascii

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule


class CognitoManagedLoginBrandingManager:
    """Handles Cognito Managed Login Branding operations"""

    def __init__(self, module):
        self.module = module
        self.client = module.client("cognito-idp")

    def describe_branding_by_client(self, user_pool_id, client_id, return_merged=False):
        """Get branding style by app client ID"""
        try:
            response = self.client.describe_managed_login_branding_by_client(
                UserPoolId=user_pool_id,
                ClientId=client_id,
                ReturnMergedResources=return_merged
            )
            return response.get("ManagedLoginBranding")
        except self.client.exceptions.ResourceNotFoundException:
            return None
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            # Handle case where no branding exists for this client
            if hasattr(e, 'response') and e.response.get('Error', {}).get('Code') == 'ResourceNotFoundException':
                return None
            self.module.fail_json_aws(e, msg=f"Failed to describe branding for client {client_id}")

    def describe_branding(self, user_pool_id, branding_id, return_merged=False):
        """Get branding style by branding ID"""
        try:
            response = self.client.describe_managed_login_branding(
                UserPoolId=user_pool_id,
                ManagedLoginBrandingId=branding_id,
                ReturnMergedResources=return_merged
            )
            return response.get("ManagedLoginBranding")
        except self.client.exceptions.ResourceNotFoundException:
            return None
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            if hasattr(e, 'response') and e.response.get('Error', {}).get('Code') == 'ResourceNotFoundException':
                return None
            self.module.fail_json_aws(e, msg=f"Failed to describe branding {branding_id}")

    def create_branding(self, params):
        """Create a new managed login branding style"""
        try:
            response = self.client.create_managed_login_branding(**params)
            return response.get("ManagedLoginBranding")
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            self.module.fail_json_aws(e, msg="Failed to create managed login branding")

    def update_branding(self, params):
        """Update an existing managed login branding style"""
        try:
            response = self.client.update_managed_login_branding(**params)
            return response.get("ManagedLoginBranding")
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            self.module.fail_json_aws(e, msg="Failed to update managed login branding")

    def delete_branding(self, user_pool_id, branding_id):
        """Delete a managed login branding style"""
        try:
            self.client.delete_managed_login_branding(
                UserPoolId=user_pool_id,
                ManagedLoginBrandingId=branding_id
            )
            return True
        except self.client.exceptions.ResourceNotFoundException:
            return False
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            if hasattr(e, 'response') and e.response.get('Error', {}).get('Code') == 'ResourceNotFoundException':
                return False
            self.module.fail_json_aws(e, msg=f"Failed to delete managed login branding {branding_id}")

    def jsonize(self, branding_data):
        """Convert datetime and binary fields for JSON serialization"""
        if branding_data is None:
            return None
        result = dict(branding_data)
        if "CreationDate" in result:
            result["CreationDate"] = str(result["CreationDate"])
        if "LastModifiedDate" in result:
            result["LastModifiedDate"] = str(result["LastModifiedDate"])
        # Base64-encode any binary asset data so Ansible can serialize it
        if "Assets" in result:
            sanitized_assets = []
            for asset in result["Assets"]:
                asset = dict(asset)
                if "Bytes" in asset and isinstance(asset["Bytes"], bytes):
                    asset["Bytes"] = base64.b64encode(asset["Bytes"]).decode("ascii")
                sanitized_assets.append(asset)
            result["Assets"] = sanitized_assets
        return result


def build_assets(module, assets_param):
    """Build assets list for API call"""
    if assets_param is None:
        return None

    if not assets_param:
        return []

    assets = []
    for idx, asset in enumerate(assets_param):
        if asset.get("bytes") and asset.get("resource_id"):
            module.fail_json(msg=f"assets[{idx}]: 'bytes' and 'resource_id' are mutually exclusive")
        asset_entry = {
            "Category": asset["category"],
            "ColorMode": asset["color_mode"],
        }
        if asset.get("bytes"):
            try:
                asset_entry["Bytes"] = base64.b64decode(asset["bytes"])
            except (binascii.Error, ValueError) as e:
                module.fail_json(msg=f"Invalid base64 in assets[{idx}].bytes: {e}")
        if asset.get("resource_id"):
            asset_entry["ResourceId"] = asset["resource_id"]
        if asset.get("extension"):
            asset_entry["Extension"] = asset["extension"]
        assets.append(asset_entry)

    return assets


def build_create_params(module):
    """Build parameters for create API call"""
    params = {
        "UserPoolId": module.params["user_pool_id"],
        "ClientId": module.params["client_id"],
    }

    if module.params.get("use_cognito_provided_values"):
        params["UseCognitoProvidedValues"] = True
    else:
        if module.params.get("settings") is not None:
            params["Settings"] = module.params["settings"]
        assets = build_assets(module, module.params.get("assets"))
        if assets is not None:
            params["Assets"] = assets

    return params


def build_update_params(module, branding_id):
    """Build parameters for update API call"""
    params = {
        "UserPoolId": module.params["user_pool_id"],
        "ManagedLoginBrandingId": branding_id,
    }

    if module.params.get("use_cognito_provided_values"):
        params["UseCognitoProvidedValues"] = True
    else:
        if module.params.get("settings") is not None:
            params["Settings"] = module.params["settings"]
        assets = build_assets(module, module.params.get("assets"))
        if assets is not None:
            params["Assets"] = assets

    return params


def _assets_need_update(desired_assets_param, existing_assets):
    """Compare desired assets against existing assets.

    Returns True if an update is needed.  When any desired asset supplies raw
    ``bytes`` we cannot compare against the ``ResourceId`` returned by describe,
    so we conservatively assume an update is required.
    """
    if desired_assets_param is None:
        return False

    for asset in desired_assets_param:
        if asset.get("bytes"):
            return True

    desired_set = set()
    for asset in desired_assets_param:
        desired_set.add((
            asset.get("category"),
            asset.get("color_mode"),
            asset.get("resource_id", ""),
            asset.get("extension", ""),
        ))

    existing_set = set()
    for asset in (existing_assets or []):
        existing_set.add((
            asset.get("Category"),
            asset.get("ColorMode"),
            asset.get("ResourceId", ""),
            asset.get("Extension", ""),
        ))

    return desired_set != existing_set


def needs_update(existing, module):
    """Check if the existing branding needs to be updated"""
    # If use_cognito_provided_values was explicitly set, check if it changed
    desired_use_cognito = module.params.get("use_cognito_provided_values")
    if desired_use_cognito is not None:
        existing_use_cognito = existing.get("UseCognitoProvidedValues", False)
        if existing_use_cognito != desired_use_cognito:
            return True

    # If using cognito provided values, skip settings/assets check.
    # However, if the user supplied settings or assets, that implicitly means
    # they want custom branding — even if the existing resource uses cognito defaults.
    has_custom_content = bool(module.params.get("settings")) or bool(module.params.get("assets"))
    using_cognito = desired_use_cognito is True or (
        desired_use_cognito is None and existing.get("UseCognitoProvidedValues", False) and not has_custom_content
    )
    if not using_cognito:
        if module.params.get("settings") is not None:
            existing_settings = existing.get("Settings", {})
            if existing_settings != module.params["settings"]:
                return True

        if _assets_need_update(module.params.get("assets"), existing.get("Assets")):
            return True

    return False


def main():
    argument_spec = dict(
        state=dict(required=True, choices=["present", "absent"]),
        user_pool_id=dict(required=True, type="str"),
        client_id=dict(required=False, type="str"),
        managed_login_branding_id=dict(required=False, type="str"),
        use_cognito_provided_values=dict(required=False, type="bool", default=None),
        settings=dict(required=False, type="dict"),
        assets=dict(
            required=False,
            type="list",
            elements="dict",
            options=dict(
                category=dict(
                    type="str",
                    required=True,
                    choices=[
                        "FAVICON_ICO",
                        "FAVICON_SVG",
                        "EMAIL_GRAPHIC",
                        "SMS_GRAPHIC",
                        "AUTH_APP_GRAPHIC",
                        "PASSWORD_GRAPHIC",
                        "PASSKEY_GRAPHIC",
                        "PAGE_HEADER_LOGO",
                        "PAGE_HEADER_BACKGROUND",
                        "PAGE_FOOTER_LOGO",
                        "PAGE_FOOTER_BACKGROUND",
                        "PAGE_BACKGROUND",
                        "FORM_BACKGROUND",
                        "FORM_LOGO",
                        "IDP_BUTTON_ICON",
                    ],
                ),
                color_mode=dict(type="str", required=True, choices=["LIGHT", "DARK", "DYNAMIC"]),
                bytes=dict(type="str", no_log=True),
                resource_id=dict(type="str"),
                extension=dict(type="str", choices=["ICO", "JPEG", "PNG", "SVG", "WEBP"]),
            ),
        ),
        return_merged_resources=dict(required=False, type="bool", default=False),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[["client_id", "managed_login_branding_id"]],
    )

    state = module.params["state"]
    user_pool_id = module.params["user_pool_id"]
    client_id = module.params.get("client_id")
    branding_id = module.params.get("managed_login_branding_id")
    return_merged = module.params.get("return_merged_resources", False)

    # Manual mutual-exclusivity: use_cognito_provided_values=true cannot be
    # combined with settings or assets.  We handle this manually (instead of
    # via the mutually_exclusive parameter) because use_cognito_provided_values=false
    # combined with settings IS a valid combination (it means "switch to custom").
    desired_use_cognito = module.params.get("use_cognito_provided_values")
    has_settings = bool(module.params.get("settings"))
    has_assets = bool(module.params.get("assets"))

    if state == "present":
        if desired_use_cognito is True and (has_settings or has_assets):
            module.fail_json(
                msg="use_cognito_provided_values=true is mutually exclusive with settings and assets."
            )

    manager = CognitoManagedLoginBrandingManager(module)

    # Always use unmerged settings for the idempotency comparison so that
    # Cognito-injected defaults don't cause false positives.
    existing_branding = None
    if branding_id:
        existing_branding = manager.describe_branding(user_pool_id, branding_id, return_merged=False)
    elif client_id:
        existing_branding = manager.describe_branding_by_client(user_pool_id, client_id, return_merged=False)
        if existing_branding:
            branding_id = existing_branding.get("ManagedLoginBrandingId")

    # Fail fast when an explicit ID was provided but nothing was found
    if branding_id and not existing_branding:
        if state == "present":
            module.fail_json(
                msg=f"Managed login branding style '{branding_id}' not found in user pool '{user_pool_id}'"
            )

    results = dict(changed=False)

    if state == "present":
        if existing_branding:
            # Update existing branding
            if needs_update(existing_branding, module):
                # Catch the impossible transition: switching away from Cognito
                # defaults without providing replacement content.
                if desired_use_cognito is False and not has_settings and not has_assets:
                    module.fail_json(
                        msg="use_cognito_provided_values=false requires settings and/or assets to be provided. "
                        "To switch from Cognito defaults to custom branding, supply the desired settings or assets."
                    )
                if not module.check_mode:
                    params = build_update_params(module, branding_id)
                    updated_branding = manager.update_branding(params)
                    # Re-fetch with merged resources if requested, since
                    # update_managed_login_branding doesn't support ReturnMergedResources
                    if return_merged:
                        updated_branding = manager.describe_branding(user_pool_id, branding_id, return_merged=True)
                    results["branding"] = camel_dict_to_snake_dict(manager.jsonize(updated_branding))
                else:
                    results["branding"] = camel_dict_to_snake_dict(manager.jsonize(existing_branding))
                results["changed"] = True
            else:
                # No update needed — re-fetch with merged resources if requested
                if return_merged:
                    display = manager.describe_branding(user_pool_id, branding_id, return_merged=True)
                else:
                    display = existing_branding
                results["branding"] = camel_dict_to_snake_dict(manager.jsonize(display))
        else:
            # Create new branding
            if not client_id:
                module.fail_json(msg="client_id is required when creating a new managed login branding style")

            if not desired_use_cognito and not has_settings and not has_assets:
                module.fail_json(
                    msg="Cannot create managed login branding without content. "
                    "Set use_cognito_provided_values=true for Cognito defaults, "
                    "or provide settings and/or assets for custom branding."
                )

            if not module.check_mode:
                params = build_create_params(module)
                new_branding = manager.create_branding(params)
                # Re-fetch with merged resources if requested, since
                # create_managed_login_branding doesn't support ReturnMergedResources
                if return_merged:
                    new_branding_id = new_branding.get("ManagedLoginBrandingId")
                    new_branding = manager.describe_branding(user_pool_id, new_branding_id, return_merged=True)
                results["branding"] = camel_dict_to_snake_dict(manager.jsonize(new_branding))
            else:
                results["branding"] = {
                    "user_pool_id": user_pool_id,
                    "client_id": client_id,
                }
            results["changed"] = True

    elif state == "absent":
        if existing_branding:
            if not branding_id:
                branding_id = existing_branding.get("ManagedLoginBrandingId")

            if not module.check_mode:
                manager.delete_branding(user_pool_id, branding_id)
            results["changed"] = True
        # If branding doesn't exist, nothing to do

    module.exit_json(**results)


if __name__ == "__main__":
    main()
