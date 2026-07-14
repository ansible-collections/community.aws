#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: s3_cors
version_added: 1.0.0
short_description: Manage CORS for S3 buckets in AWS
description:
  - Manage CORS for S3 buckets in AWS.
  - Prior to release 5.0.0 this module was called C(community.aws.aws_s3_cors).
    The usage did not change.
author:
  - "Oyvind Saltvik (@fivethreeo)"
options:
  name:
    description:
      - Name of the S3 bucket.
    required: true
    type: str
  rules:
    description:
      - CORS rules to apply to the S3 bucket.
    type: list
    elements: dict
    suboptions:
      allowed_origins:
        description:
          - One or more origins you want customers to be able to access the bucket from.
        type: list
        elements: str
        required: true
      allowed_methods:
        description:
          - HTTP methods that are allowed from the origin specified in I(allowed_origins).
        type: list
        elements: str
        required: true
        choices: ['GET', 'PUT', 'HEAD', 'POST', 'DELETE']
      allowed_headers:
        description:
          - Headers that are specified in the C(Access-Control-Request-Headers) header.
        type: list
        elements: str
      expose_headers:
        description:
          - One or more headers in the response that you want customers to be able to access from their applications.
        type: list
        elements: str
      max_age_seconds:
        description:
          - Time in seconds that the browser should cache the preflight response for the specified resource.
        type: int
  state:
    description:
      - Create or remove cors on the S3 bucket.
    required: true
    choices: [ 'present', 'absent' ]
    type: str
extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details, see the AWS Guide for details.

# Create a simple cors for s3 bucket
- community.aws.s3_cors:
    name: mys3bucket
    state: present
    rules:
      - allowed_origins:
          - http://www.example.com/
        allowed_methods:
          - GET
          - POST
        allowed_headers:
          - Authorization
        expose_headers:
          - x-amz-server-side-encryption
          - x-amz-request-id
        max_age_seconds: 30000

# Remove cors for s3 bucket
- community.aws.s3_cors:
    name: mys3bucket
    state: absent

# Create CORS rules with multiple origins and methods
- community.aws.s3_cors:
    name: mys3bucket
    state: present
    rules:
      - allowed_origins:
          - http://www.example.com
          - http://www.example.org
        allowed_methods:
          - GET
          - PUT
          - POST
        allowed_headers:
          - '*'
        max_age_seconds: 3600
      - allowed_origins:
          - '*'
        allowed_methods:
          - GET
"""

RETURN = r"""
changed:
  description: check to see if a change was made to the rules
  returned: always
  type: bool
  sample: true
name:
  description: Name of the S3 bucket.
  returned: when I(state=present)
  type: str
  sample: 'bucket-name'
rules:
  description: CORS rules applied to the bucket.
  returned: when I(state=present)
  type: list
  sample: [
     {
        "allowed_headers": [
          "Authorization"
        ],
        "allowed_methods": [
          "GET"
        ],
        "allowed_origins": [
          "*"
        ],
        "max_age_seconds": 30000
      }
    ]
"""

try:
    from botocore.exceptions import BotoCoreError
    from botocore.exceptions import ClientError
except ImportError:
    pass  # Handled by AnsibleAWSModule

from ansible.module_utils.common.dict_transformations import snake_dict_to_camel_dict

from ansible_collections.amazon.aws.plugins.module_utils.botocore import is_boto3_error_code

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule


def normalize_cors_rules(rules: list[dict] | None) -> list[dict]:
    """Normalize CORS rules for deterministic comparison.

    Sorts list values within each rule (e.g., AllowedOrigins, AllowedMethods) and
    sorts the rules themselves by a stable tuple-based key so that two equivalent
    rule sets always compare equal regardless of ordering.

    Args:
        rules: A list of CORS rule dicts as returned by boto3 or passed by the user.
               May be None or empty.

    Returns:
        A new list of normalized rule dicts, sorted deterministically.
    """
    if not rules:
        return []

    normalized = []
    for rule in rules:
        norm_rule = {}
        for key, value in rule.items():
            if isinstance(value, list):
                norm_rule[key] = sorted(value)
            else:
                norm_rule[key] = value
        normalized.append(norm_rule)

    def sort_key(rule):
        """Create a hashable, sortable key from a rule dict."""
        return tuple(sorted((k, tuple(v) if isinstance(v, list) else v) for k, v in rule.items()))

    return sorted(normalized, key=sort_key)


def create_or_update_bucket_cors(connection, module):
    """Create or update CORS configuration on an S3 bucket."""
    name = module.params.get("name")
    rules = module.params.get("rules", [])
    changed = False

    try:
        current_camel_rules = connection.get_bucket_cors(Bucket=name)["CORSRules"]
    except is_boto3_error_code("NoSuchCORSConfiguration"):
        current_camel_rules = []
    except (BotoCoreError, ClientError) as e:  # pylint: disable=duplicate-except
        module.fail_json_aws(e, msg=f"Unable to get CORS configuration for bucket {name}")

    new_camel_rules = snake_dict_to_camel_dict(rules, capitalize_first=True)

    # Compare normalized rules
    if normalize_cors_rules(new_camel_rules) != normalize_cors_rules(current_camel_rules):
        changed = True

    if changed and not module.check_mode:
        try:
            connection.put_bucket_cors(Bucket=name, CORSConfiguration={"CORSRules": new_camel_rules})
        except (BotoCoreError, ClientError) as e:
            module.fail_json_aws(e, msg=f"Unable to update CORS for bucket {name}")

    module.exit_json(changed=changed, name=name, rules=rules)


def destroy_bucket_cors(connection, module):
    """Remove CORS configuration from an S3 bucket."""
    name = module.params.get("name")
    changed = False

    # Check if CORS configuration exists
    try:
        connection.get_bucket_cors(Bucket=name)
        # CORS exists, so we need to delete it
        changed = True
    except is_boto3_error_code("NoSuchCORSConfiguration"):
        # Bucket has no CORS configuration, nothing to delete
        changed = False
    except (BotoCoreError, ClientError) as e:  # pylint: disable=duplicate-except
        # Some other error occurred
        module.fail_json_aws(e, msg=f"Unable to get CORS configuration for bucket {name}")

    # Only delete if CORS exists and not in check mode
    if changed and not module.check_mode:
        try:
            connection.delete_bucket_cors(Bucket=name)
        except (BotoCoreError, ClientError) as e:
            module.fail_json_aws(e, msg=f"Unable to delete CORS for bucket {name}")

    module.exit_json(changed=changed)


def main():
    """Entry point for the s3_cors Ansible module."""
    argument_spec = dict(
        name=dict(required=True, type="str"),
        rules=dict(type="list", elements="dict"),
        state=dict(type="str", choices=["present", "absent"], required=True),
    )

    module = AnsibleAWSModule(argument_spec=argument_spec, supports_check_mode=True)

    client = module.client("s3")

    state = module.params.get("state")

    if state == "present":
        create_or_update_bucket_cors(client, module)
    elif state == "absent":
        destroy_bucket_cors(client, module)


if __name__ == "__main__":
    main()
