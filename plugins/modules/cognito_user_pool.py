#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: cognito_user_pool
version_added: 11.1.0
short_description: Manage AWS Cognito User Pools
description:
  - Creates, updates, or deletes AWS Cognito User Pools.
  - For details of the parameters and returns see U(https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp.html).
notes:
  - Some parameters (I(alias_attributes), I(username_attributes), I(username_configuration), I(schema)) can only
    be set during pool creation and cannot be modified after the pool is created.
  - The UpdateUserPool API resets any omitted mutable fields to their defaults. This module
    always reads the current pool configuration before updating and preserves all fields that
    are not explicitly specified, so partial updates are safe.
author:
  - "Jonathan Springer (@jonpspri)"
options:
    state:
        description:
          - The desired state of the user pool.
        required: true
        choices: ["present", "absent"]
        type: str
    name:
        description:
          - The name of the user pool.
          - Required when I(state=present) and the pool does not exist.
          - Used for lookup if I(user_pool_id) is not provided.
        required: false
        type: str
    user_pool_id:
        description:
          - The ID of an existing user pool to update or delete.
          - Takes precedence over name-based lookup.
        required: false
        type: str
    user_pool_tier:
        description:
          - The tier for the user pool.
        required: false
        type: str
        choices: ["LITE", "ESSENTIALS", "PLUS"]
    deletion_protection:
        description:
          - Whether deletion protection is enabled.
          - When C(ACTIVE), the pool cannot be deleted until protection is set to C(INACTIVE).
        required: false
        type: str
        choices: ["ACTIVE", "INACTIVE"]
    mfa_configuration:
        description:
          - The MFA configuration for the user pool.
        required: false
        type: str
        choices: ["OFF", "ON", "OPTIONAL"]
    auto_verified_attributes:
        description:
          - Attributes to be auto-verified.
        required: false
        type: list
        elements: str
        choices: ["email", "phone_number"]
    alias_attributes:
        description:
          - Attributes that can be used as aliases for signing in.
          - Create-only parameter; cannot be changed after pool creation.
          - Mutually exclusive with I(username_attributes).
        required: false
        type: list
        elements: str
        choices: ["phone_number", "email", "preferred_username"]
    username_attributes:
        description:
          - Attributes to use as the username for signing in.
          - Create-only parameter; cannot be changed after pool creation.
          - Mutually exclusive with I(alias_attributes).
        required: false
        type: list
        elements: str
        choices: ["phone_number", "email"]
    username_configuration:
        description:
          - Configuration for username case sensitivity.
          - Create-only parameter; cannot be changed after pool creation.
        required: false
        type: dict
        suboptions:
            case_sensitive:
                description: Whether usernames are case sensitive.
                type: bool
                required: true
    schema:
        description:
          - Custom attribute schema definitions.
          - Create-only parameter; cannot be changed after pool creation.
        required: false
        type: list
        elements: dict
    policies:
        description:
          - Password and sign-in policies.
        required: false
        type: dict
        suboptions:
            password_policy:
                description: Password policy settings.
                type: dict
                suboptions:
                    minimum_length:
                        description: Minimum password length.
                        type: int
                    require_uppercase:
                        description: Require at least one uppercase letter.
                        type: bool
                    require_lowercase:
                        description: Require at least one lowercase letter.
                        type: bool
                    require_numbers:
                        description: Require at least one number.
                        type: bool
                    require_symbols:
                        description: Require at least one symbol.
                        type: bool
                    temporary_password_validity_days:
                        description: Days before a temporary password expires.
                        type: int
            sign_in_policy:
                description: Sign-in policy settings.
                type: dict
                suboptions:
                    allowed_first_auth_factors:
                        description: Allowed first authentication factors.
                        type: list
                        elements: str
    lambda_config:
        description:
          - Lambda trigger configuration.
          - Keys should be in snake_case and will be converted to CamelCase.
        required: false
        type: dict
    email_configuration:
        description:
          - Email configuration for the user pool.
        required: false
        type: dict
        suboptions:
            source_arn:
                description: ARN of the SES verified email identity.
                type: str
            reply_to_email_address:
                description: Reply-to email address.
                type: str
            email_sending_account:
                description: Account used for sending email (COGNITO_DEFAULT or DEVELOPER).
                type: str
                choices: ["COGNITO_DEFAULT", "DEVELOPER"]
            from_address:
                description: >-
                    The "From" address for emails. Maps to the C(From) key in the API
                    (not C(FromAddress)).
                type: str
            configuration_set:
                description: SES configuration set name.
                type: str
    sms_configuration:
        description:
          - SMS configuration for the user pool.
        required: false
        type: dict
        suboptions:
            sns_caller_arn:
                description: ARN of the IAM role for SMS.
                type: str
                required: true
            external_id:
                description: External ID for assuming the SMS role.
                type: str
            sns_region:
                description: AWS region for SNS.
                type: str
    admin_create_user_config:
        description:
          - Configuration for admin-created users.
        required: false
        type: dict
        suboptions:
            allow_admin_create_user_only:
                description: Only allow admin to create users.
                type: bool
            invite_message_template:
                description: Invitation message template.
                type: dict
                suboptions:
                    sms_message:
                        description: SMS message template.
                        type: str
                    email_message:
                        description: Email message template.
                        type: str
                    email_subject:
                        description: Email subject template.
                        type: str
    account_recovery_setting:
        description:
          - Account recovery settings.
        required: false
        type: dict
        suboptions:
            recovery_mechanisms:
                description: List of recovery mechanisms.
                type: list
                elements: dict
                suboptions:
                    priority:
                        description: Priority of this recovery mechanism.
                        type: int
                        required: true
                    name:
                        description: Recovery mechanism name.
                        type: str
                        required: true
                        choices: ["verified_email", "verified_phone_number", "admin_only"]
    device_configuration:
        description:
          - Device tracking configuration.
        required: false
        type: dict
        suboptions:
            challenge_required_on_new_device:
                description: Whether a challenge is required on new devices.
                type: bool
            device_only_remembered_on_user_prompt:
                description: Whether devices are only remembered when user opts in.
                type: bool
    verification_message_template:
        description:
          - Verification message template configuration.
        required: false
        type: dict
    user_attribute_update_settings:
        description:
          - Settings for requiring verification before updating attributes.
        required: false
        type: dict
        suboptions:
            attributes_require_verification_before_update:
                description: Attributes that require verification before update.
                type: list
                elements: str
    user_pool_add_ons:
        description:
          - User pool add-ons configuration (advanced security).
        required: false
        type: dict
        suboptions:
            advanced_security_mode:
                description: Advanced security mode.
                type: str
                required: true
                choices: ["OFF", "AUDIT", "ENFORCED"]
    tags:
        description:
          - Tags to apply to the user pool.
        required: false
        type: dict
        aliases: ['resource_tags']
    purge_tags:
        description:
          - Whether to remove tags not specified in I(tags).
        required: false
        type: bool
        default: true
extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
# Create a simple user pool
- community.aws.cognito_user_pool:
    state: present
    name: my-user-pool

# Create a user pool with ESSENTIALS tier and MFA
- community.aws.cognito_user_pool:
    state: present
    name: my-secure-pool
    user_pool_tier: ESSENTIALS
    mfa_configuration: OPTIONAL
    auto_verified_attributes:
      - email
    policies:
      password_policy:
        minimum_length: 12
        require_uppercase: true
        require_lowercase: true
        require_numbers: true
        require_symbols: true
    tags:
      Environment: production

# Update an existing user pool by ID
- community.aws.cognito_user_pool:
    state: present
    user_pool_id: us-east-1_ABC123
    deletion_protection: ACTIVE

# Delete a user pool by name
- community.aws.cognito_user_pool:
    state: absent
    name: my-user-pool

# Delete a user pool by ID
- community.aws.cognito_user_pool:
    state: absent
    user_pool_id: us-east-1_ABC123
"""

RETURN = r"""
user_pool:
    description: Details of the user pool.
    returned: when state is present
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
            description: The ARN of the user pool.
            returned: always
            type: str
        status:
            description: The status of the user pool.
            returned: always
            type: str
        creation_date:
            description: The date the user pool was created.
            returned: always
            type: str
        last_modified_date:
            description: The date the user pool was last modified.
            returned: always
            type: str
        mfa_configuration:
            description: The MFA configuration.
            returned: always
            type: str
        user_pool_tier:
            description: The tier of the user pool.
            returned: when available
            type: str
        deletion_protection:
            description: Whether deletion protection is enabled.
            returned: when available
            type: str
        policies:
            description: Password and sign-in policies.
            returned: always
            type: dict
        user_pool_tags:
            description: Tags on the user pool.
            returned: when configured
            type: dict
"""

try:
    import botocore
except ImportError:
    pass  # caught by AnsibleAWSModule

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict
from ansible.module_utils.common.dict_transformations import snake_dict_to_camel_dict

from ansible_collections.amazon.aws.plugins.module_utils.transformation import scrub_none_parameters
from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule


# Parameters that can only be set during creation
CREATE_ONLY_PARAMS = ["alias_attributes", "username_attributes", "username_configuration", "schema"]


class CognitoUserPoolManager:
    """Handles Cognito User Pool operations"""

    def __init__(self, module):
        self.module = module
        self.client = module.client("cognito-idp")

    def find_pool_by_name(self, pool_name):
        """Find user pool(s) by name. Returns the pool ID or fails if multiple matches."""
        try:
            matches = []
            paginator = self.client.get_paginator("list_user_pools")
            for page in paginator.paginate(MaxResults=60):
                for pool in page.get("UserPools", []):
                    if pool.get("Name") == pool_name:
                        matches.append(pool.get("Id"))

            if len(matches) > 1:
                self.module.fail_json(
                    msg=f"Multiple user pools found with name '{pool_name}': {matches}. "
                    "Use user_pool_id to specify which pool to manage."
                )
            return matches[0] if matches else None
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            self.module.fail_json_aws(e, msg="Failed to list user pools")

    def describe_pool(self, user_pool_id):
        """Get details of a user pool"""
        try:
            response = self.client.describe_user_pool(UserPoolId=user_pool_id)
            return response.get("UserPool")
        except self.client.exceptions.ResourceNotFoundException:
            return None
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            self.module.fail_json_aws(e, msg=f"Failed to describe user pool {user_pool_id}")

    def create_pool(self, params):
        """Create a new user pool"""
        try:
            response = self.client.create_user_pool(**params)
            return response.get("UserPool")
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            self.module.fail_json_aws(e, msg="Failed to create user pool")

    def update_pool(self, params):
        """Update an existing user pool"""
        try:
            self.client.update_user_pool(**params)
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            self.module.fail_json_aws(e, msg="Failed to update user pool")

    def delete_pool(self, user_pool_id):
        """Delete a user pool"""
        try:
            self.client.delete_user_pool(UserPoolId=user_pool_id)
            return True
        except self.client.exceptions.ResourceNotFoundException:
            return False
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            self.module.fail_json_aws(e, msg=f"Failed to delete user pool {user_pool_id}")

    @staticmethod
    def jsonize(pool_data):
        """Convert datetime fields to strings for JSON serialization"""
        if pool_data is None:
            return None
        result = dict(pool_data)
        if "CreationDate" in result:
            result["CreationDate"] = str(result["CreationDate"])
        if "LastModifiedDate" in result:
            result["LastModifiedDate"] = str(result["LastModifiedDate"])
        return result


def _build_email_config(email_params):
    """Build EmailConfiguration from module params, mapping from_address to From."""
    config = {}
    key_map = {
        "source_arn": "SourceArn",
        "reply_to_email_address": "ReplyToEmailAddress",
        "email_sending_account": "EmailSendingAccount",
        "from_address": "From",
        "configuration_set": "ConfigurationSet",
    }
    for param_key, api_key in key_map.items():
        if email_params.get(param_key) is not None:
            config[api_key] = email_params[param_key]
    return config


def _deep_merge(base, override):
    """Recursively merge override into base, returning a new dict.

    Non-dict values in override replace base values. Dict values are
    merged recursively so that sibling keys in base are preserved.
    """
    result = dict(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def _build_nested_param(module_value):
    """Convert a snake_case dict parameter to CamelCase for the API.

    Ansible's argument processing sets unspecified suboptions to None.
    These must be stripped before sending to the API, as botocore rejects
    unknown None values and parameters not yet in its service model.
    """
    return snake_dict_to_camel_dict(scrub_none_parameters(module_value), capitalize_first=True)


def build_create_params(module):
    """Build parameters for the CreateUserPool API call."""
    params = {"PoolName": module.params["name"]}

    # Simple string/list params
    simple_params = {
        "user_pool_tier": "UserPoolTier",
        "deletion_protection": "DeletionProtection",
        "mfa_configuration": "MfaConfiguration",
        "auto_verified_attributes": "AutoVerifiedAttributes",
    }
    for mod_key, api_key in simple_params.items():
        if module.params.get(mod_key) is not None:
            params[api_key] = module.params[mod_key]

    # Create-only params
    if module.params.get("alias_attributes") is not None:
        params["AliasAttributes"] = module.params["alias_attributes"]
    if module.params.get("username_attributes") is not None:
        params["UsernameAttributes"] = module.params["username_attributes"]
    if module.params.get("username_configuration") is not None:
        params["UsernameConfiguration"] = _build_nested_param(module.params["username_configuration"])
    if module.params.get("schema") is not None:
        params["Schema"] = [_build_nested_param(s) for s in module.params["schema"]]

    # Nested dict params
    nested_params = {
        "policies": "Policies",
        "lambda_config": "LambdaConfig",
        "sms_configuration": "SmsConfiguration",
        "admin_create_user_config": "AdminCreateUserConfig",
        "account_recovery_setting": "AccountRecoverySetting",
        "device_configuration": "DeviceConfiguration",
        "verification_message_template": "VerificationMessageTemplate",
        "user_attribute_update_settings": "UserAttributeUpdateSettings",
        "user_pool_add_ons": "UserPoolAddOns",
    }
    for mod_key, api_key in nested_params.items():
        if module.params.get(mod_key) is not None:
            params[api_key] = _build_nested_param(module.params[mod_key])

    # Email configuration needs special handling for from_address -> From
    if module.params.get("email_configuration") is not None:
        params["EmailConfiguration"] = _build_email_config(module.params["email_configuration"])

    # Tags
    if module.params.get("tags") is not None:
        params["UserPoolTags"] = module.params["tags"]

    return params


def build_update_params(module, existing_pool):
    """Build parameters for the UpdateUserPool API call.

    The UpdateUserPool API resets omitted fields to defaults, so we must
    start from the existing pool configuration and overlay user params.
    """
    user_pool_id = existing_pool["Id"]
    params = {"UserPoolId": user_pool_id}

    # Fields to preserve from the existing pool if not specified by user.
    # We copy them from existing, then overlay user-specified values.
    preserve_fields = [
        "DeletionProtection",
        "MfaConfiguration",
        "AutoVerifiedAttributes",
        "Policies",
        "LambdaConfig",
        "EmailConfiguration",
        "SmsConfiguration",
        "AdminCreateUserConfig",
        "AccountRecoverySetting",
        "DeviceConfiguration",
        "VerificationMessageTemplate",
        "UserAttributeUpdateSettings",
        "UserPoolAddOns",
        "UserPoolTier",
        "SmsAuthenticationMessage",
        "SmsVerificationMessage",
        "EmailVerificationMessage",
        "EmailVerificationSubject",
    ]
    for field in preserve_fields:
        if field in existing_pool:
            params[field] = existing_pool[field]

    # Overlay user-specified simple params
    simple_params = {
        "user_pool_tier": "UserPoolTier",
        "deletion_protection": "DeletionProtection",
        "mfa_configuration": "MfaConfiguration",
        "auto_verified_attributes": "AutoVerifiedAttributes",
    }
    for mod_key, api_key in simple_params.items():
        if module.params.get(mod_key) is not None:
            params[api_key] = module.params[mod_key]

    # Overlay user-specified nested params, merging into preserved values
    # so that partial updates (e.g. setting one field inside policies.password_policy)
    # don't reset sibling keys to service defaults.
    nested_params = {
        "policies": "Policies",
        "lambda_config": "LambdaConfig",
        "sms_configuration": "SmsConfiguration",
        "admin_create_user_config": "AdminCreateUserConfig",
        "account_recovery_setting": "AccountRecoverySetting",
        "device_configuration": "DeviceConfiguration",
        "verification_message_template": "VerificationMessageTemplate",
        "user_attribute_update_settings": "UserAttributeUpdateSettings",
        "user_pool_add_ons": "UserPoolAddOns",
    }
    for mod_key, api_key in nested_params.items():
        if module.params.get(mod_key) is not None:
            user_value = _build_nested_param(module.params[mod_key])
            existing_value = params.get(api_key, {})
            params[api_key] = _deep_merge(existing_value, user_value)

    # Email configuration special handling — also merge into preserved value
    if module.params.get("email_configuration") is not None:
        user_value = _build_email_config(module.params["email_configuration"])
        existing_value = params.get("EmailConfiguration", {})
        params["EmailConfiguration"] = _deep_merge(existing_value, user_value)

    return params


def needs_update(existing_pool, update_params):
    """Check if the existing pool configuration differs from desired state."""
    for key, desired_value in update_params.items():
        if key == "UserPoolId":
            continue
        existing_value = existing_pool.get(key)

        if isinstance(desired_value, list) and isinstance(existing_value, list):
            if set(str(v) for v in desired_value) != set(str(v) for v in existing_value):
                return True
        elif isinstance(desired_value, dict) and isinstance(existing_value, dict):
            if desired_value != existing_value:
                return True
        elif desired_value != existing_value:
            return True

    return False


def check_create_only_params(module, existing_pool):
    """Warn if create-only params are specified on an existing pool and differ."""
    create_only_checks = {
        "alias_attributes": ("AliasAttributes", None),
        "username_attributes": ("UsernameAttributes", None),
        "username_configuration": ("UsernameConfiguration", _build_nested_param),
        "schema": ("SchemaAttributes", None),
    }
    for mod_key, (api_key, transform) in create_only_checks.items():
        if module.params.get(mod_key) is not None:
            desired = module.params[mod_key]
            if transform:
                desired = transform(desired)
            existing = existing_pool.get(api_key)
            if existing is not None and desired != existing:
                module.warn(
                    f"Parameter '{mod_key}' can only be set during pool creation and "
                    f"cannot be modified. Current value will be preserved."
                )


def handle_tags(module, manager, existing_pool):
    """Handle tag updates. Returns True if tags were changed."""
    desired_tags = module.params.get("tags")
    if desired_tags is None:
        return False

    pool_arn = existing_pool["Arn"]
    existing_tags = existing_pool.get("UserPoolTags", {})
    purge_tags = module.params.get("purge_tags", True)

    tags_to_add = {}
    tags_to_remove = []

    # Find tags to add or update
    for key, value in desired_tags.items():
        if key not in existing_tags or existing_tags[key] != value:
            tags_to_add[key] = value

    # Find tags to remove (only if purging)
    if purge_tags:
        for key in existing_tags:
            if key not in desired_tags:
                tags_to_remove.append(key)

    if not tags_to_add and not tags_to_remove:
        return False

    if not module.check_mode:
        try:
            if tags_to_remove:
                manager.client.untag_resource(ResourceArn=pool_arn, TagKeys=tags_to_remove)
            if tags_to_add:
                manager.client.tag_resource(ResourceArn=pool_arn, Tags=tags_to_add)
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Failed to update user pool tags")

    return True


def main():
    argument_spec = dict(
        state=dict(required=True, choices=["present", "absent"]),
        name=dict(required=False, type="str"),
        user_pool_id=dict(required=False, type="str"),
        user_pool_tier=dict(required=False, type="str", choices=["LITE", "ESSENTIALS", "PLUS"]),
        deletion_protection=dict(required=False, type="str", choices=["ACTIVE", "INACTIVE"]),
        mfa_configuration=dict(required=False, type="str", choices=["OFF", "ON", "OPTIONAL"]),
        auto_verified_attributes=dict(required=False, type="list", elements="str"),
        alias_attributes=dict(required=False, type="list", elements="str"),
        username_attributes=dict(required=False, type="list", elements="str"),
        username_configuration=dict(
            required=False,
            type="dict",
            options=dict(
                case_sensitive=dict(type="bool", required=True),
            ),
        ),
        schema=dict(required=False, type="list", elements="dict"),
        policies=dict(
            required=False,
            type="dict",
            options=dict(
                password_policy=dict(
                    type="dict",
                    options=dict(
                        minimum_length=dict(type="int"),
                        require_uppercase=dict(type="bool"),
                        require_lowercase=dict(type="bool"),
                        require_numbers=dict(type="bool"),
                        require_symbols=dict(type="bool"),
                        temporary_password_validity_days=dict(type="int"),
                    ),
                ),
                sign_in_policy=dict(
                    type="dict",
                    options=dict(
                        allowed_first_auth_factors=dict(type="list", elements="str"),
                    ),
                ),
            ),
        ),
        lambda_config=dict(required=False, type="dict"),
        email_configuration=dict(
            required=False,
            type="dict",
            options=dict(
                source_arn=dict(type="str"),
                reply_to_email_address=dict(type="str"),
                email_sending_account=dict(type="str", choices=["COGNITO_DEFAULT", "DEVELOPER"]),
                from_address=dict(type="str"),
                configuration_set=dict(type="str"),
            ),
        ),
        sms_configuration=dict(
            required=False,
            type="dict",
            options=dict(
                sns_caller_arn=dict(type="str", required=True),
                external_id=dict(type="str"),
                sns_region=dict(type="str"),
            ),
        ),
        admin_create_user_config=dict(
            required=False,
            type="dict",
            options=dict(
                allow_admin_create_user_only=dict(type="bool"),
                invite_message_template=dict(
                    type="dict",
                    options=dict(
                        sms_message=dict(type="str"),
                        email_message=dict(type="str"),
                        email_subject=dict(type="str"),
                    ),
                ),
            ),
        ),
        account_recovery_setting=dict(
            required=False,
            type="dict",
            options=dict(
                recovery_mechanisms=dict(
                    type="list",
                    elements="dict",
                    options=dict(
                        priority=dict(type="int", required=True),
                        name=dict(type="str", required=True),
                    ),
                ),
            ),
        ),
        device_configuration=dict(
            required=False,
            type="dict",
            options=dict(
                challenge_required_on_new_device=dict(type="bool"),
                device_only_remembered_on_user_prompt=dict(type="bool"),
            ),
        ),
        verification_message_template=dict(required=False, type="dict"),
        user_attribute_update_settings=dict(
            required=False,
            type="dict",
            options=dict(
                attributes_require_verification_before_update=dict(type="list", elements="str"),
            ),
        ),
        user_pool_add_ons=dict(
            required=False,
            type="dict",
            options=dict(
                advanced_security_mode=dict(type="str", required=True, choices=["OFF", "AUDIT", "ENFORCED"]),
            ),
        ),
        tags=dict(required=False, type="dict", aliases=["resource_tags"]),
        purge_tags=dict(required=False, type="bool", default=True),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[["name", "user_pool_id"]],
        mutually_exclusive=[["alias_attributes", "username_attributes"]],
    )

    state = module.params["state"]
    user_pool_id = module.params.get("user_pool_id")
    pool_name = module.params.get("name")

    manager = CognitoUserPoolManager(module)

    # Resolve pool ID by name if needed
    if not user_pool_id and pool_name:
        user_pool_id = manager.find_pool_by_name(pool_name)

    # Get existing pool if we have an ID
    existing_pool = None
    if user_pool_id:
        existing_pool = manager.describe_pool(user_pool_id)

    results = dict(changed=False)

    if state == "present":
        # If user explicitly provided user_pool_id but pool doesn't exist, fail
        # rather than silently creating a new pool with a different ID.
        if not existing_pool and module.params.get("user_pool_id"):
            module.fail_json(msg=f"User pool '{user_pool_id}' not found. Cannot create a pool when user_pool_id is specified.")

        if existing_pool:
            # Update existing pool
            check_create_only_params(module, existing_pool)

            update_params = build_update_params(module, existing_pool)
            changed = needs_update(existing_pool, update_params)

            if changed and not module.check_mode:
                manager.update_pool(update_params)

            # Handle tags (uses separate API calls)
            tags_changed = handle_tags(module, manager, existing_pool)
            changed = changed or tags_changed

            results["changed"] = changed

            # Re-read pool for accurate return data
            if changed and not module.check_mode:
                existing_pool = manager.describe_pool(user_pool_id)

            results["user_pool"] = camel_dict_to_snake_dict(manager.jsonize(existing_pool), ignore_list=["UserPoolTags"])
        else:
            # Create new pool
            if not pool_name:
                module.fail_json(msg="name is required when creating a new user pool")

            params = build_create_params(module)

            if not module.check_mode:
                new_pool = manager.create_pool(params)
                # Re-read to get the full pool data
                existing_pool = manager.describe_pool(new_pool["Id"])
                results["user_pool"] = camel_dict_to_snake_dict(manager.jsonize(existing_pool), ignore_list=["UserPoolTags"])
            else:
                results["user_pool"] = {"name": pool_name}

            results["changed"] = True

    elif state == "absent":
        if existing_pool:
            # Check deletion protection
            if existing_pool.get("DeletionProtection") == "ACTIVE":
                module.fail_json(
                    msg=f"User pool '{user_pool_id}' has deletion protection enabled. "
                    "Set deletion_protection to INACTIVE before deleting."
                )

            if not module.check_mode:
                manager.delete_pool(user_pool_id)
            results["changed"] = True

    module.exit_json(**results)


if __name__ == "__main__":
    main()
