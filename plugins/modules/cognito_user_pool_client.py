#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: cognito_user_pool_client
version_added: 11.1.0
short_description: Manage AWS Cognito User Pool Clients
description:
  - Creates, updates, or deletes AWS Cognito User Pool Clients (App Clients).
  - Provides reasonable defaults for use with Application Load Balancer (ALB) authentication.
  - For ALB integration, the client needs code grant flow, a client secret, and appropriate OAuth scopes.
notes:
  - For ALB integration, callback URLs must be lowercase and use the format https://DNS/oauth2/idpresponse.
  - The default OAuth scopes (openid) return an ID token suitable for ALB authentication.
  - For details of the parameters and returns see U(https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp.html).
author:
  - "Jonathan Springer (@jonpspri)"
options:
    state:
        description:
          - The desired state of the user pool client.
        required: true
        choices: ["present", "absent"]
        type: str
    name:
        description:
          - A friendly name for the app client.
          - Required when I(state=present) and the client does not exist.
        required: false
        type: str
        aliases: ['client_name']
    client_id:
        description:
          - The ID of an existing user pool client to update or delete.
          - Required when I(state=absent) and I(name) is not provided.
          - If not provided when I(state=present), the module will search for a client by name.
        required: false
        type: str
    user_pool_id:
        description:
          - The ID of the user pool where the client exists or should be created.
        required: true
        type: str
    generate_secret:
        description:
          - Generate a client secret for the app client.
          - Required for ALB integration and server-side applications.
          - Can only be set during client creation, not update.
        required: false
        type: bool
        default: true
    callback_urls:
        description:
          - List of allowed callback URLs for OAuth 2.0 authentication.
          - For ALB integration, use format https://DNS/oauth2/idpresponse (lowercase).
          - Omit to preserve existing values on update.
        required: false
        type: list
        elements: str
    logout_urls:
        description:
          - List of allowed logout URLs.
          - Omit to preserve existing values on update.
        required: false
        type: list
        elements: str
    default_redirect_uri:
        description:
          - The default redirect URI.
          - Must be in the callback_urls list.
        required: false
        type: str
    allowed_oauth_flows:
        description:
          - OAuth grant types that the client can use.
          - For ALB integration, use 'code' (authorization code grant).
          - Omit to preserve existing values on update.
        required: false
        type: list
        elements: str
        choices: ["code", "implicit", "client_credentials"]
    allowed_oauth_flows_user_pool_client:
        description:
          - Set to true to enable OAuth 2.0 features in the client.
          - Omit to preserve existing value on update.
        required: false
        type: bool
    allowed_oauth_scopes:
        description:
          - OAuth scopes that the client can request.
          - For ALB integration, 'openid' is required to get an ID token.
          - Common scopes are openid, email, phone, profile, aws.cognito.signin.user.admin.
          - Omit to preserve existing values on update.
        required: false
        type: list
        elements: str
    supported_identity_providers:
        description:
          - List of identity providers supported by this client.
          - Use 'COGNITO' for Cognito user pool, or names of configured IdPs.
          - Omit to preserve existing values on update.
        required: false
        type: list
        elements: str
    explicit_auth_flows:
        description:
          - Authentication flows that the client supports.
        required: false
        type: list
        elements: str
        choices:
          - ALLOW_USER_AUTH
          - ALLOW_ADMIN_USER_PASSWORD_AUTH
          - ALLOW_CUSTOM_AUTH
          - ALLOW_USER_PASSWORD_AUTH
          - ALLOW_USER_SRP_AUTH
          - ALLOW_REFRESH_TOKEN_AUTH
    access_token_validity:
        description:
          - Time limit for access token validity.
          - Units specified by I(token_validity_units).
        required: false
        type: int
    id_token_validity:
        description:
          - Time limit for ID token validity.
          - Units specified by I(token_validity_units).
        required: false
        type: int
    refresh_token_validity:
        description:
          - Time limit for refresh token validity.
          - Units specified by I(token_validity_units).
        required: false
        type: int
    token_validity_units:
        description:
          - Units for token validity values.
        required: false
        type: dict
        suboptions:
            access_token:
                description: Units for access token (seconds, minutes, hours, days).
                type: str
                choices: ["seconds", "minutes", "hours", "days"]
            id_token:
                description: Units for ID token (seconds, minutes, hours, days).
                type: str
                choices: ["seconds", "minutes", "hours", "days"]
            refresh_token:
                description: Units for refresh token (seconds, minutes, hours, days).
                type: str
                choices: ["seconds", "minutes", "hours", "days"]
    read_attributes:
        description:
          - List of user attributes that the client can read.
        required: false
        type: list
        elements: str
    write_attributes:
        description:
          - List of user attributes that the client can write.
        required: false
        type: list
        elements: str
    enable_token_revocation:
        description:
          - Enable token revocation for the client.
        required: false
        type: bool
    prevent_user_existence_errors:
        description:
          - Error response preference for user existence errors.
          - When 'ENABLED', masks whether a user exists during authentication.
        required: false
        type: str
        choices: ["LEGACY", "ENABLED"]
    auth_session_validity:
        description:
          - Duration in minutes for session tokens during authentication challenges.
        required: false
        type: int
    enable_propagate_additional_user_context_data:
        description:
          - Activates the propagation of additional user context data.
          - Requires a client secret.
        required: false
        type: bool
extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
# Create a user pool client for ALB authentication
- cognito_user_pool_client:
    state: present
    name: my-alb-client
    user_pool_id: us-east-1_ABC123
    generate_secret: true
    callback_urls:
      - https://myapp.example.com/oauth2/idpresponse
    allowed_oauth_flows:
      - code
    allowed_oauth_scopes:
      - openid
      - email
      - profile
    supported_identity_providers:
      - COGNITO

# Create a client with custom token validity
- cognito_user_pool_client:
    state: present
    name: my-app-client
    user_pool_id: us-east-1_ABC123
    generate_secret: true
    callback_urls:
      - https://myapp.example.com/callback
    access_token_validity: 1
    id_token_validity: 1
    refresh_token_validity: 30
    token_validity_units:
      access_token: hours
      id_token: hours
      refresh_token: days

# Update an existing client by client_id
- cognito_user_pool_client:
    state: present
    client_id: "1234567890abcdef"
    user_pool_id: us-east-1_ABC123
    callback_urls:
      - https://myapp.example.com/oauth2/idpresponse
      - https://myapp-staging.example.com/oauth2/idpresponse

# Delete a user pool client
- cognito_user_pool_client:
    state: absent
    client_id: "1234567890abcdef"
    user_pool_id: us-east-1_ABC123

# Delete a user pool client by name
- cognito_user_pool_client:
    state: absent
    name: my-alb-client
    user_pool_id: us-east-1_ABC123
"""

RETURN = r"""
client:
    description: Details of the user pool client.
    returned: when state is present
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
            sample: "my-alb-client"
        user_pool_id:
            description: The ID of the user pool.
            returned: always
            type: str
            sample: "us-east-1_ABC123"
        client_secret:
            description: The client secret (only returned on creation if generate_secret is true).
            returned: when available
            type: str
        callback_urls:
            description: List of callback URLs.
            returned: always
            type: list
            elements: str
        logout_urls:
            description: List of logout URLs.
            returned: always
            type: list
            elements: str
        allowed_oauth_flows:
            description: Allowed OAuth flows.
            returned: always
            type: list
            elements: str
        allowed_oauth_scopes:
            description: Allowed OAuth scopes.
            returned: always
            type: list
            elements: str
        supported_identity_providers:
            description: Supported identity providers.
            returned: always
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
"""

try:
    import botocore
except ImportError:
    pass  # caught by AnsibleAWSModule

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule


class CognitoUserPoolClientManager:
    """Handles Cognito User Pool Client operations"""

    def __init__(self, module):
        self.module = module
        self.client = module.client("cognito-idp")

    def find_client_by_name(self, user_pool_id, client_name):
        """Find a user pool client by name. Fails if multiple clients share the same name."""
        try:
            matches = []
            paginator = self.client.get_paginator("list_user_pool_clients")
            for page in paginator.paginate(UserPoolId=user_pool_id, MaxResults=60):
                for client in page.get("UserPoolClients", []):
                    if client.get("ClientName") == client_name:
                        matches.append(client.get("ClientId"))
            if len(matches) > 1:
                self.module.fail_json(
                    msg=f"Multiple app clients found with name '{client_name}' in pool '{user_pool_id}': "
                    f"{', '.join(matches)}. Use client_id to target a specific client."
                )
            return matches[0] if matches else None
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            self.module.fail_json_aws(e, msg=f"Failed to list user pool clients for pool {user_pool_id}")

    def describe_client(self, user_pool_id, client_id):
        """Get details of a user pool client"""
        try:
            response = self.client.describe_user_pool_client(
                UserPoolId=user_pool_id,
                ClientId=client_id
            )
            return response.get("UserPoolClient")
        except self.client.exceptions.ResourceNotFoundException:
            return None
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            self.module.fail_json_aws(e, msg=f"Failed to describe user pool client {client_id}")

    def create_client(self, params):
        """Create a new user pool client"""
        try:
            response = self.client.create_user_pool_client(**params)
            return response.get("UserPoolClient")
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            self.module.fail_json_aws(e, msg="Failed to create user pool client")

    def update_client(self, params):
        """Update an existing user pool client"""
        try:
            response = self.client.update_user_pool_client(**params)
            return response.get("UserPoolClient")
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            self.module.fail_json_aws(e, msg="Failed to update user pool client")

    def delete_client(self, user_pool_id, client_id):
        """Delete a user pool client"""
        try:
            self.client.delete_user_pool_client(
                UserPoolId=user_pool_id,
                ClientId=client_id
            )
            return True
        except self.client.exceptions.ResourceNotFoundException:
            return False
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            self.module.fail_json_aws(e, msg=f"Failed to delete user pool client {client_id}")

    def jsonize(self, client_data):
        """Convert datetime fields to strings for JSON serialization"""
        if client_data is None:
            return None
        result = dict(client_data)
        if "CreationDate" in result:
            result["CreationDate"] = str(result["CreationDate"])
        if "LastModifiedDate" in result:
            result["LastModifiedDate"] = str(result["LastModifiedDate"])
        return result


def build_client_params(module, for_update=False, existing_client=None):
    """Build parameters for create or update API call"""
    params = {
        "UserPoolId": module.params["user_pool_id"],
    }

    if for_update:
        params["ClientId"] = module.params["client_id"]

    # For updates, preserve existing client configuration as baseline.
    # The Cognito UpdateUserPoolClient API resets omitted fields to defaults,
    # so we must include all existing values to prevent destructive partial updates.
    if for_update and existing_client:
        preserve_fields = [
            "ClientName",
            "CallbackURLs",
            "LogoutURLs",
            "DefaultRedirectURI",
            "AllowedOAuthFlows",
            "AllowedOAuthFlowsUserPoolClient",
            "AllowedOAuthScopes",
            "SupportedIdentityProviders",
            "ExplicitAuthFlows",
            "AccessTokenValidity",
            "IdTokenValidity",
            "RefreshTokenValidity",
            "TokenValidityUnits",
            "ReadAttributes",
            "WriteAttributes",
            "EnableTokenRevocation",
            "PreventUserExistenceErrors",
            "AuthSessionValidity",
            "EnablePropagateAdditionalUserContextData",
            "AnalyticsConfiguration",
            "RefreshTokenRotation",
        ]
        for field in preserve_fields:
            if field in existing_client:
                params[field] = existing_client[field]

    # Client name - required for create, optional for update
    if module.params.get("name"):
        params["ClientName"] = module.params["name"]

    # Generate secret - only for create
    if not for_update and module.params.get("generate_secret") is not None:
        params["GenerateSecret"] = module.params["generate_secret"]

    # Callback and logout URLs
    if module.params.get("callback_urls") is not None:
        params["CallbackURLs"] = module.params["callback_urls"]
    if module.params.get("logout_urls") is not None:
        params["LogoutURLs"] = module.params["logout_urls"]
    if module.params.get("default_redirect_uri") is not None:
        params["DefaultRedirectURI"] = module.params["default_redirect_uri"]

    # OAuth settings
    if module.params.get("allowed_oauth_flows") is not None:
        params["AllowedOAuthFlows"] = module.params["allowed_oauth_flows"]
    if module.params.get("allowed_oauth_flows_user_pool_client") is not None:
        params["AllowedOAuthFlowsUserPoolClient"] = module.params["allowed_oauth_flows_user_pool_client"]
    if module.params.get("allowed_oauth_scopes") is not None:
        params["AllowedOAuthScopes"] = module.params["allowed_oauth_scopes"]
    if module.params.get("supported_identity_providers") is not None:
        params["SupportedIdentityProviders"] = module.params["supported_identity_providers"]

    # Auth flows
    if module.params.get("explicit_auth_flows") is not None:
        params["ExplicitAuthFlows"] = module.params["explicit_auth_flows"]

    # Token validity
    if module.params.get("access_token_validity") is not None:
        params["AccessTokenValidity"] = module.params["access_token_validity"]
    if module.params.get("id_token_validity") is not None:
        params["IdTokenValidity"] = module.params["id_token_validity"]
    if module.params.get("refresh_token_validity") is not None:
        params["RefreshTokenValidity"] = module.params["refresh_token_validity"]

    if module.params.get("token_validity_units"):
        token_units = dict(params.get("TokenValidityUnits", {}))
        units = module.params["token_validity_units"]
        if units.get("access_token"):
            token_units["AccessToken"] = units["access_token"]
        if units.get("id_token"):
            token_units["IdToken"] = units["id_token"]
        if units.get("refresh_token"):
            token_units["RefreshToken"] = units["refresh_token"]
        if token_units:
            params["TokenValidityUnits"] = token_units

    # Attributes
    if module.params.get("read_attributes") is not None:
        params["ReadAttributes"] = module.params["read_attributes"]
    if module.params.get("write_attributes") is not None:
        params["WriteAttributes"] = module.params["write_attributes"]

    # Other settings
    if module.params.get("enable_token_revocation") is not None:
        params["EnableTokenRevocation"] = module.params["enable_token_revocation"]
    if module.params.get("prevent_user_existence_errors") is not None:
        params["PreventUserExistenceErrors"] = module.params["prevent_user_existence_errors"]
    if module.params.get("auth_session_validity") is not None:
        params["AuthSessionValidity"] = module.params["auth_session_validity"]
    if module.params.get("enable_propagate_additional_user_context_data") is not None:
        params["EnablePropagateAdditionalUserContextData"] = module.params["enable_propagate_additional_user_context_data"]

    return params


def needs_update(existing, desired_params):
    """Check if the existing client needs to be updated"""
    # Compare relevant fields
    check_fields = [
        ("ClientName", "ClientName"),
        ("CallbackURLs", "CallbackURLs"),
        ("LogoutURLs", "LogoutURLs"),
        ("DefaultRedirectURI", "DefaultRedirectURI"),
        ("AllowedOAuthFlows", "AllowedOAuthFlows"),
        ("AllowedOAuthFlowsUserPoolClient", "AllowedOAuthFlowsUserPoolClient"),
        ("AllowedOAuthScopes", "AllowedOAuthScopes"),
        ("SupportedIdentityProviders", "SupportedIdentityProviders"),
        ("ExplicitAuthFlows", "ExplicitAuthFlows"),
        ("AccessTokenValidity", "AccessTokenValidity"),
        ("IdTokenValidity", "IdTokenValidity"),
        ("RefreshTokenValidity", "RefreshTokenValidity"),
        ("TokenValidityUnits", "TokenValidityUnits"),
        ("ReadAttributes", "ReadAttributes"),
        ("WriteAttributes", "WriteAttributes"),
        ("EnableTokenRevocation", "EnableTokenRevocation"),
        ("PreventUserExistenceErrors", "PreventUserExistenceErrors"),
        ("AuthSessionValidity", "AuthSessionValidity"),
        ("EnablePropagateAdditionalUserContextData", "EnablePropagateAdditionalUserContextData"),
    ]

    for existing_key, desired_key in check_fields:
        if desired_key in desired_params:
            existing_value = existing.get(existing_key)
            desired_value = desired_params[desired_key]

            # Normalize list comparison (order shouldn't matter for some fields)
            if isinstance(existing_value, list) and isinstance(desired_value, list):
                if set(existing_value) != set(desired_value):
                    return True
            elif existing_value != desired_value:
                return True

    return False


def main():
    argument_spec = dict(
        state=dict(required=True, choices=["present", "absent"]),
        name=dict(required=False, type="str", aliases=["client_name"]),
        client_id=dict(required=False, type="str"),
        user_pool_id=dict(required=True, type="str"),
        generate_secret=dict(required=False, type="bool", default=True),
        callback_urls=dict(required=False, type="list", elements="str"),
        logout_urls=dict(required=False, type="list", elements="str"),
        default_redirect_uri=dict(required=False, type="str"),
        allowed_oauth_flows=dict(
            required=False,
            type="list",
            elements="str",
            choices=["code", "implicit", "client_credentials"],
        ),
        allowed_oauth_flows_user_pool_client=dict(required=False, type="bool"),
        allowed_oauth_scopes=dict(required=False, type="list", elements="str"),
        supported_identity_providers=dict(required=False, type="list", elements="str"),
        explicit_auth_flows=dict(
            required=False,
            type="list",
            elements="str",
            choices=[
                "ALLOW_USER_AUTH",
                "ALLOW_ADMIN_USER_PASSWORD_AUTH",
                "ALLOW_CUSTOM_AUTH",
                "ALLOW_USER_PASSWORD_AUTH",
                "ALLOW_USER_SRP_AUTH",
                "ALLOW_REFRESH_TOKEN_AUTH",
            ],
        ),
        access_token_validity=dict(required=False, type="int", no_log=False),
        id_token_validity=dict(required=False, type="int", no_log=False),
        refresh_token_validity=dict(required=False, type="int", no_log=False),
        token_validity_units=dict(
            required=False,
            type="dict",
            no_log=False,
            options=dict(
                access_token=dict(type="str", choices=["seconds", "minutes", "hours", "days"]),
                id_token=dict(type="str", choices=["seconds", "minutes", "hours", "days"]),
                refresh_token=dict(type="str", choices=["seconds", "minutes", "hours", "days"]),
            ),
        ),
        read_attributes=dict(required=False, type="list", elements="str"),
        write_attributes=dict(required=False, type="list", elements="str"),
        enable_token_revocation=dict(required=False, type="bool"),
        prevent_user_existence_errors=dict(required=False, type="str", choices=["LEGACY", "ENABLED"]),
        auth_session_validity=dict(required=False, type="int"),
        enable_propagate_additional_user_context_data=dict(required=False, type="bool"),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[["name", "client_id"]],
    )

    state = module.params["state"]
    user_pool_id = module.params["user_pool_id"]
    client_id = module.params.get("client_id")
    client_name = module.params.get("name")

    manager = CognitoUserPoolClientManager(module)

    # If client_id not provided, try to find by name
    if not client_id and client_name:
        client_id = manager.find_client_by_name(user_pool_id, client_name)
        if client_id:
            module.params["client_id"] = client_id

    # Get existing client if we have an ID
    existing_client = None
    if client_id:
        existing_client = manager.describe_client(user_pool_id, client_id)

    # Fail fast when an explicit client_id was provided but nothing was found
    if module.params.get("client_id") and not existing_client:
        if state == "present":
            module.fail_json(
                msg=f"User pool client '{module.params['client_id']}' not found in user pool '{user_pool_id}'"
            )

    results = dict(changed=False)

    if state == "present":
        if existing_client:
            # Update existing client
            params = build_client_params(module, for_update=True, existing_client=existing_client)

            if needs_update(existing_client, params):
                if not module.check_mode:
                    updated_client = manager.update_client(params)
                    results["client"] = camel_dict_to_snake_dict(manager.jsonize(updated_client))
                else:
                    results["client"] = camel_dict_to_snake_dict(manager.jsonize(existing_client))
                results["changed"] = True
            else:
                results["client"] = camel_dict_to_snake_dict(manager.jsonize(existing_client))
        else:
            # Create new client
            if not client_name:
                module.fail_json(msg="name is required when creating a new user pool client")

            params = build_client_params(module, for_update=False)

            if not module.check_mode:
                new_client = manager.create_client(params)
                results["client"] = camel_dict_to_snake_dict(manager.jsonize(new_client))
            else:
                results["client"] = {"client_name": client_name, "user_pool_id": user_pool_id}
            results["changed"] = True

    elif state == "absent":
        if existing_client:
            if not module.check_mode:
                manager.delete_client(user_pool_id, client_id)
            results["changed"] = True
        # If client doesn't exist, nothing to do

    module.exit_json(**results)


if __name__ == "__main__":
    main()
