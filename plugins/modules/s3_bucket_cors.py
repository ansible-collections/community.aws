#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: s3_bucket_cors
version_added: 1.0.0
short_description: Manage CORS for S3 buckets in AWS
description:
  - Manage CORS for S3 buckets in AWS.
  - Prior to release 5.0.0 this module was called C(community.aws.aws_s3_cors).
  - Since release 11.1.0 the preferred name is C(community.aws.s3_bucket_cors), C(community.aws.s3_cors) remains as an alias.
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
      - Cors rules to put on the S3 bucket.
    type: list
    elements: dict
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
"""

RETURN = r"""
changed:
  description: check to see if a change was made to the rules
  returned: always
  type: bool
  sample: true
name:
  description: name of bucket
  returned: always
  type: str
  sample: 'bucket-name'
rules:
  description: list of current rules
  returned: always
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

from ansible.module_utils.common.dict_transformations import snake_dict_to_camel_dict

from ansible_collections.amazon.aws.plugins.module_utils.policy import compare_policies
from ansible_collections.amazon.aws.plugins.module_utils.s3 import AnsibleS3Error

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule
from ansible_collections.community.aws.plugins.module_utils.s3 import delete_bucket_cors
from ansible_collections.community.aws.plugins.module_utils.s3 import get_bucket_cors
from ansible_collections.community.aws.plugins.module_utils.s3 import put_bucket_cors


def create_or_update_bucket_cors(module, client):
    """Create or update bucket CORS configuration."""
    name = module.params.get("name")
    rules = module.params.get("rules", [])

    current_camel_rules = get_bucket_cors(client, name)
    new_camel_rules = snake_dict_to_camel_dict(rules, capitalize_first=True)

    # compare_policies() takes two dicts and makes them hashable for comparison
    if not compare_policies(new_camel_rules, current_camel_rules):
        return False

    if module.check_mode:
        return True

    put_bucket_cors(client, name, new_camel_rules)
    return True


def delete_bucket_cors_configuration(module, client):
    """Delete bucket CORS configuration."""
    name = module.params.get("name")

    current_camel_rules = get_bucket_cors(client, name)

    # Check if already absent
    if not current_camel_rules:
        return False

    if module.check_mode:
        return True

    result = delete_bucket_cors(client, name)
    # If result is False, configuration didn't exist (race condition - already deleted)
    return result is not False


def main():
    argument_spec = dict(
        name=dict(required=True, type="str"),
        rules=dict(type="list", elements="dict"),
        state=dict(type="str", choices=["present", "absent"], required=True),
    )

    module = AnsibleAWSModule(argument_spec=argument_spec, supports_check_mode=True)

    try:
        client = module.client("s3")
        state = module.params.get("state")

        if state == "present":
            changed = create_or_update_bucket_cors(module, client)
        else:  # absent
            changed = delete_bucket_cors_configuration(module, client)

        module.exit_json(changed=changed, name=module.params["name"], rules=module.params.get("rules", []))
    except AnsibleS3Error as e:
        module.fail_json_aws_error(e)


if __name__ == "__main__":
    main()
