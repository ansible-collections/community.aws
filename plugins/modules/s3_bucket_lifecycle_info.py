#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: s3_bucket_lifecycle_info
version_added: 11.1.0
short_description: Retrieve lifecycle configuration for S3 buckets
description:
  - Retrieve lifecycle configuration for S3 buckets.
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

- name: Retrieve lifecycle configuration for a bucket
  community.aws.s3_bucket_lifecycle_info:
    name: my-bucket
  register: result

- name: Display lifecycle rules
  ansible.builtin.debug:
    var: result.lifecycle_rules
"""

RETURN = r"""
lifecycle_rules:
  description: List of lifecycle rules for the bucket
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: Unique identifier for the rule
      returned: when configured
      type: str
      sample: "Delete old logs"
    status:
      description: Whether the rule is currently being applied
      returned: always
      type: str
      sample: "Enabled"
    prefix:
      description: Object key prefix identifying objects to which the rule applies
      returned: when configured
      type: str
      sample: "logs/"
    filter:
      description: Filter identifying objects to which the rule applies
      returned: when configured
      type: dict
    expiration:
      description: Expiration configuration
      returned: when configured
      type: dict
      contains:
        days:
          description: Number of days after which to expire objects
          returned: when configured
          type: int
          sample: 30
        date:
          description: Date when objects will expire
          returned: when configured
          type: str
        expired_object_delete_marker:
          description: Remove delete markers with no noncurrent versions
          returned: when configured
          type: bool
    transitions:
      description: Transition configurations
      returned: when configured
      type: list
      elements: dict
      contains:
        days:
          description: Number of days after which to transition objects
          returned: when configured
          type: int
          sample: 30
        date:
          description: Date when objects will transition
          returned: when configured
          type: str
        storage_class:
          description: Storage class to transition to
          returned: always
          type: str
          sample: "GLACIER"
    noncurrent_version_expiration:
      description: Noncurrent version expiration configuration
      returned: when configured
      type: dict
    noncurrent_version_transitions:
      description: Noncurrent version transition configurations
      returned: when configured
      type: list
      elements: dict
    abort_incomplete_multipart_upload:
      description: Abort incomplete multipart upload configuration
      returned: when configured
      type: dict
"""

from ansible_collections.amazon.aws.plugins.module_utils.s3 import AnsibleS3Error

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule
from ansible_collections.community.aws.plugins.module_utils.s3 import get_bucket_lifecycle_configuration
from ansible_collections.community.aws.plugins.module_utils.s3 import normalize_lifecycle_rules


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
        lifecycle_config = get_bucket_lifecycle_configuration(client, bucket_name)

        # Convert to snake_case
        result = normalize_lifecycle_rules(lifecycle_config)

        module.exit_json(changed=False, lifecycle_rules=result)

    except AnsibleS3Error as e:
        module.fail_json_aws_error(e)


if __name__ == "__main__":
    main()
