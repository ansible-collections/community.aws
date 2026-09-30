#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: cognito_user_pool_domain
version_added: 11.1.0
short_description: Manage AWS Cognito User Pool domains
description:
  - Creates, updates, or deletes AWS Cognito User Pool domains.
  - Supports both prefix domains (e.g. C(my-app)) and custom domains with ACM certificates.
  - For details see U(https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cognito-idp.html).
notes:
  - The I(managed_login_version) parameter requires botocore >= 1.35.68.
author:
  - "Jonathan Springer (@jonpspri)"
options:
    state:
        description:
          - The desired state of the user pool domain.
        required: true
        choices: ["present", "absent"]
        type: str
    domain:
        description:
          - The domain prefix (e.g. C(my-app)) or fully qualified domain name for custom domains.
        required: true
        type: str
    user_pool_id:
        description:
          - The ID of the user pool to associate the domain with.
        required: true
        type: str
    managed_login_version:
        description:
          - The version of managed login to use.
          - C(1) for the classic hosted UI, C(2) for the newer managed login pages.
          - Requires botocore >= 1.35.68.
        required: false
        type: int
        choices: [1, 2]
    custom_domain_config:
        description:
          - Configuration for a custom domain.
          - Required when using a fully qualified domain name instead of a prefix.
        required: false
        type: dict
        suboptions:
            certificate_arn:
                description:
                  - The ARN of the ACM certificate for the custom domain.
                type: str
                required: true
extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
# Create a simple domain prefix
- community.aws.cognito_user_pool_domain:
    state: present
    domain: my-app
    user_pool_id: us-east-1_ABC123

# Create a domain with managed login v2
- community.aws.cognito_user_pool_domain:
    state: present
    domain: my-app
    user_pool_id: us-east-1_ABC123
    managed_login_version: 2

# Create a custom domain with ACM certificate
- community.aws.cognito_user_pool_domain:
    state: present
    domain: auth.example.com
    user_pool_id: us-east-1_ABC123
    custom_domain_config:
      certificate_arn: arn:aws:acm:us-east-1:123456789012:certificate/abc-123

# Delete a domain
- community.aws.cognito_user_pool_domain:
    state: absent
    domain: my-app
    user_pool_id: us-east-1_ABC123
"""

RETURN = r"""
user_pool_domain:
    description: Details of the user pool domain.
    returned: when state is present
    type: complex
    contains:
        user_pool_id:
            description: The user pool ID.
            returned: always
            type: str
        aws_account_id:
            description: The AWS account ID for the domain.
            returned: always
            type: str
        domain:
            description: The domain string.
            returned: always
            type: str
        s3_bucket:
            description: The S3 bucket for the static assets.
            returned: when available
            type: str
        cloud_front_distribution:
            description: The CloudFront distribution ARN.
            returned: when available
            type: str
        version:
            description: The app version.
            returned: when available
            type: str
        status:
            description: The domain status.
            returned: always
            type: str
        managed_login_version:
            description: The managed login version.
            returned: when available
            type: int
        custom_domain_config:
            description: Custom domain configuration.
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


class CognitoUserPoolDomainManager:
    """Handles Cognito User Pool Domain operations"""

    def __init__(self, module):
        self.module = module
        self.client = module.client("cognito-idp")

    def describe_domain(self, domain):
        """Get details of a user pool domain. Returns None if not found."""
        try:
            response = self.client.describe_user_pool_domain(Domain=domain)
            domain_desc = response.get("DomainDescription", {})
            # AWS returns an empty DomainDescription (no UserPoolId) when domain doesn't exist
            if not domain_desc.get("UserPoolId"):
                return None
            return domain_desc
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            self.module.fail_json_aws(e, msg=f"Failed to describe user pool domain '{domain}'")

    def create_domain(self, params):
        """Create a user pool domain"""
        try:
            self.client.create_user_pool_domain(**params)
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            self.module.fail_json_aws(e, msg="Failed to create user pool domain")

    def update_domain(self, params):
        """Update a user pool domain"""
        try:
            self.client.update_user_pool_domain(**params)
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            self.module.fail_json_aws(e, msg="Failed to update user pool domain")

    def delete_domain(self, domain, user_pool_id):
        """Delete a user pool domain"""
        try:
            self.client.delete_user_pool_domain(Domain=domain, UserPoolId=user_pool_id)
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            self.module.fail_json_aws(e, msg=f"Failed to delete user pool domain '{domain}'")


def _build_custom_domain_config(params):
    """Build CustomDomainConfig from module params."""
    return snake_dict_to_camel_dict(scrub_none_parameters(params), capitalize_first=True)


def _needs_update(existing, module):
    """Check if the domain needs updating based on module params."""
    managed_login_version = module.params.get("managed_login_version")
    custom_domain_config = module.params.get("custom_domain_config")

    if managed_login_version is not None:
        if existing.get("ManagedLoginVersion") != managed_login_version:
            return True

    if custom_domain_config is not None:
        existing_cert = (existing.get("CustomDomainConfig") or {}).get("CertificateArn")
        desired_cert = custom_domain_config.get("certificate_arn")
        if existing_cert != desired_cert:
            return True

    return False


def main():
    argument_spec = dict(
        state=dict(required=True, choices=["present", "absent"]),
        domain=dict(required=True, type="str"),
        user_pool_id=dict(required=True, type="str"),
        managed_login_version=dict(required=False, type="int", choices=[1, 2]),
        custom_domain_config=dict(
            required=False,
            type="dict",
            options=dict(
                certificate_arn=dict(type="str", required=True),
            ),
        ),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    state = module.params["state"]
    domain = module.params["domain"]
    user_pool_id = module.params["user_pool_id"]

    manager = CognitoUserPoolDomainManager(module)

    existing = manager.describe_domain(domain)

    # Validate that an existing domain belongs to the requested user pool
    if existing and existing.get("UserPoolId") != user_pool_id:
        module.fail_json(
            msg=f"Domain '{domain}' exists but belongs to user pool '{existing['UserPoolId']}', "
            f"not '{user_pool_id}'. Cannot operate on a domain owned by a different pool."
        )

    results = dict(changed=False)

    if state == "present":
        if existing:
            # Domain exists — check if update is needed
            if _needs_update(existing, module):
                if not module.check_mode:
                    update_params = dict(Domain=domain, UserPoolId=user_pool_id)
                    if module.params.get("managed_login_version") is not None:
                        update_params["ManagedLoginVersion"] = module.params["managed_login_version"]
                    if module.params.get("custom_domain_config") is not None:
                        update_params["CustomDomainConfig"] = _build_custom_domain_config(
                            module.params["custom_domain_config"]
                        )
                    manager.update_domain(update_params)
                results["changed"] = True
        else:
            # Create new domain
            if not module.check_mode:
                create_params = dict(Domain=domain, UserPoolId=user_pool_id)
                if module.params.get("managed_login_version") is not None:
                    create_params["ManagedLoginVersion"] = module.params["managed_login_version"]
                if module.params.get("custom_domain_config") is not None:
                    create_params["CustomDomainConfig"] = _build_custom_domain_config(
                        module.params["custom_domain_config"]
                    )
                manager.create_domain(create_params)
            results["changed"] = True

        # Re-read for return data
        if not module.check_mode:
            domain_data = manager.describe_domain(domain)
            if domain_data:
                results["user_pool_domain"] = camel_dict_to_snake_dict(domain_data)
            else:
                results["user_pool_domain"] = {}
        else:
            results["user_pool_domain"] = {"domain": domain, "user_pool_id": user_pool_id}

    elif state == "absent":
        if existing:
            if not module.check_mode:
                manager.delete_domain(domain, user_pool_id)
            results["changed"] = True

    module.exit_json(**results)


if __name__ == "__main__":
    main()
