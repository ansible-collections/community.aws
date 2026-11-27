#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: s3_bucket_cors_info
version_added: 11.1.0
short_description: Retrieve CORS configuration for S3 buckets
description:
  - Retrieve CORS configuration for S3 buckets.
author:
  - Mark Chappell (@tremble)
options:
  name:
    description:
      - Name of the S3 bucket.
    required: true
    type: str
    aliases: ['bucket_name']
extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details, see the AWS Guide for details.

- name: Retrieve CORS configuration for a bucket
  community.aws.s3_bucket_cors_info:
    name: my-bucket
  register: result

- name: Display CORS rules
  ansible.builtin.debug:
    var: result.cors_rules
"""

RETURN = r"""
cors_rules:
  description: List of CORS rules for the bucket
  returned: always
  type: list
  elements: dict
  contains:
    allowed_headers:
      description: Headers that are specified in the Access-Control-Request-Headers header
      returned: when configured
      type: list
      elements: str
      sample: ["Authorization"]
    allowed_methods:
      description: HTTP methods that the origin is allowed to execute
      returned: always
      type: list
      elements: str
      sample: ["GET", "PUT"]
    allowed_origins:
      description: Origins that are allowed to access the bucket
      returned: always
      type: list
      elements: str
      sample: ["https://example.com"]
    expose_headers:
      description: Headers in the response that customers are able to access from their applications
      returned: when configured
      type: list
      elements: str
      sample: ["ETag"]
    max_age_seconds:
      description: Time in seconds that browser can cache the response for a preflight request
      returned: when configured
      type: int
      sample: 3000
"""

from ansible_collections.amazon.aws.plugins.module_utils.s3 import AnsibleS3Error

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule
from ansible_collections.community.aws.plugins.module_utils.s3 import get_bucket_cors
from ansible_collections.community.aws.plugins.module_utils.s3 import normalize_cors_rules


def main():
    argument_spec = dict(
        name=dict(required=True, type="str", aliases=["bucket_name"]),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    bucket_name = module.params.get("name")

    try:
        client = module.client("s3")
        cors_rules = get_bucket_cors(client, bucket_name)

        # Convert to snake_case
        result = normalize_cors_rules(cors_rules)

        module.exit_json(changed=False, cors_rules=result)

    except AnsibleS3Error as e:
        module.fail_json_aws_error(e)


if __name__ == "__main__":
    main()
