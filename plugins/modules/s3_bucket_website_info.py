#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: s3_bucket_website_info
version_added: 11.1.0
short_description: Retrieve website configuration for S3 buckets
description:
  - Retrieve website configuration for S3 buckets.
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

- name: Retrieve website configuration for a bucket
  community.aws.s3_bucket_website_info:
    name: my-bucket
  register: result

- name: Display website configuration
  ansible.builtin.debug:
    var: result.website_configuration
"""

RETURN = r"""
website_configuration:
  description: Website configuration for the bucket (empty dict if not configured)
  returned: always
  type: dict
  contains:
    error_document:
      description: Error document configuration
      returned: when configured
      type: dict
      contains:
        key:
          description: Object key name to use when a 4XX class error occurs
          returned: always
          type: str
          sample: "error.html"
    index_document:
      description: Index document configuration
      returned: when configured
      type: dict
      contains:
        suffix:
          description: Suffix that is appended to a request for a directory
          returned: always
          type: str
          sample: "index.html"
    redirect_all_requests_to:
      description: Redirect all requests to another host
      returned: when configured
      type: dict
      contains:
        host_name:
          description: Name of the host where requests will be redirected
          returned: always
          type: str
          sample: "example.com"
        protocol:
          description: Protocol to use when redirecting requests
          returned: when configured
          type: str
          sample: "https"
    routing_rules:
      description: Routing rules
      returned: when configured
      type: list
      elements: dict
      contains:
        condition:
          description: Condition that must be met for the redirect to apply
          returned: when configured
          type: dict
          contains:
            http_error_code_returned_equals:
              description: HTTP error code when the redirect is applied
              returned: when configured
              type: str
              sample: "404"
            key_prefix_equals:
              description: Object key name prefix when the redirect is applied
              returned: when configured
              type: str
              sample: "docs/"
        redirect:
          description: Redirect information
          returned: always
          type: dict
          contains:
            host_name:
              description: Name of the host where requests will be redirected
              returned: when configured
              type: str
              sample: "example.com"
            http_redirect_code:
              description: HTTP redirect code to use on the response
              returned: when configured
              type: str
              sample: "301"
            protocol:
              description: Protocol to use when redirecting requests
              returned: when configured
              type: str
              sample: "https"
            replace_key_prefix_with:
              description: Object key prefix to use in the redirect request
              returned: when configured
              type: str
              sample: "documents/"
            replace_key_with:
              description: Specific object key to use in the redirect request
              returned: when configured
              type: str
              sample: "error.html"
"""

from ansible_collections.amazon.aws.plugins.module_utils.s3 import AnsibleS3Error

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule
from ansible_collections.community.aws.plugins.module_utils.s3 import get_bucket_website
from ansible_collections.community.aws.plugins.module_utils.s3 import normalize_website_configuration


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
        website_config = get_bucket_website(client, bucket_name)

        # Convert to snake_case
        result = normalize_website_configuration(website_config)

        module.exit_json(changed=False, website_configuration=result)

    except AnsibleS3Error as e:
        module.fail_json_aws_error(e)


if __name__ == "__main__":
    main()
