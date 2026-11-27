#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: cognito_user_pool_domain_info
version_added: 11.1.0
short_description: Retrieve information about an AWS Cognito User Pool domain
description:
  - Retrieves detailed information about an AWS Cognito User Pool domain using the DescribeUserPoolDomain API.
  - Returns domain configuration including status, CloudFront distribution, and managed login version.
notes:
  - This is an info module and does not modify any resources.
  - For details see U(https://docs.aws.amazon.com/cognito-user-identity-pools/latest/APIReference/API_DescribeUserPoolDomain.html).
author:
  - "Jonathan Springer (@jonpspri)"
options:
    domain:
        description:
          - The domain name to describe (prefix or FQDN).
        required: true
        type: str
extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
# Get information about a user pool domain
- community.aws.cognito_user_pool_domain_info:
    domain: my-app
  register: domain_info

# Display the domain status
- ansible.builtin.debug:
    msg: "Domain status: {{ domain_info.user_pool_domain.status }}"
"""

RETURN = r"""
user_pool_domain:
    description: Details of the user pool domain.
    returned: success
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

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule


def main():
    argument_spec = dict(
        domain=dict(required=True, type="str"),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    domain = module.params["domain"]

    try:
        client = module.client("cognito-idp")
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Failed to connect to AWS")

    try:
        response = client.describe_user_pool_domain(Domain=domain)
        domain_desc = response.get("DomainDescription", {})

        if not domain_desc.get("UserPoolId"):
            module.fail_json(msg=f"User pool domain '{domain}' not found")

        result = camel_dict_to_snake_dict(domain_desc)
        module.exit_json(changed=False, user_pool_domain=result)

    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg=f"Failed to describe user pool domain '{domain}'")


if __name__ == "__main__":
    main()
