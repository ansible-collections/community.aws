#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: s3_bucket_metrics_configuration
version_added: 1.3.0
short_description: Manage s3 bucket metrics configuration in AWS
description:
  - Manage s3 bucket metrics configuration in AWS which allows to get the CloudWatch request metrics for the objects in a bucket
  - Since release 11.1.0 the preferred name is C(community.aws.s3_bucket_metrics_configuration), C(community.aws.s3_metrics_configuration) remains as an alias.
author:
  - Dmytro Vorotyntsev (@vorotech)
notes:
  - This modules manages single metrics configuration, the s3 bucket might have up to 1,000 metrics configurations
  - To request metrics for the entire bucket, create a metrics configuration without a filter
  - Metrics configurations are necessary only to enable request metric, bucket-level daily storage metrics are always turned on
options:
  bucket_name:
    description:
      - "Name of the s3 bucket"
    required: true
    type: str
  id:
    description:
      - "The ID used to identify the metrics configuration"
    required: true
    type: str
  filter_prefix:
    description:
      - "A prefix used when evaluating a metrics filter"
    required: false
    type: str
  filter_tags:
    description:
      - "A dictionary of one or more tags used when evaluating a metrics filter"
    required: false
    aliases: ['filter_tag']
    type: dict
    default: {}
  state:
    description:
      - "Create or delete metrics configuration"
    default: present
    choices: ['present', 'absent']
    type: str
extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

RETURN = r""" # """

EXAMPLES = r"""
# Note: These examples do not set authentication details, see the AWS Guide for details.

- name: Create a metrics configuration that enables metrics for an entire bucket
  community.aws.s3_metrics_configuration:
    bucket_name: my-bucket
    id: EntireBucket
    state: present

- name: Put a metrics configuration that enables metrics for objects starting with a prefix
  community.aws.s3_metrics_configuration:
    bucket_name: my-bucket
    id: Assets
    filter_prefix: assets
    state: present

- name: Put a metrics configuration that enables metrics for objects with specific tag
  community.aws.s3_metrics_configuration:
    bucket_name: my-bucket
    id: Assets
    filter_tag:
      kind: asset
    state: present

- name: Put a metrics configuration that enables metrics for objects that start with a particular prefix and have specific tags applied
  community.aws.s3_metrics_configuration:
    bucket_name: my-bucket
    id: ImportantBlueDocuments
    filter_prefix: documents
    filter_tags:
      priority: high
      class: blue
    state: present

- name: Delete metrics configuration
  community.aws.s3_metrics_configuration:
    bucket_name: my-bucket
    id: EntireBucket
    state: absent
"""

from ansible_collections.amazon.aws.plugins.module_utils.s3 import AnsibleS3Error

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule
from ansible_collections.community.aws.plugins.module_utils.s3 import create_metrics_configuration
from ansible_collections.community.aws.plugins.module_utils.s3 import delete_bucket_metrics_configuration
from ansible_collections.community.aws.plugins.module_utils.s3 import get_bucket_metrics_configuration
from ansible_collections.community.aws.plugins.module_utils.s3 import put_bucket_metrics_configuration


def create_or_update_metrics_configuration(module, client):
    """Create or update bucket metrics configuration."""
    bucket_name = module.params.get("bucket_name")
    mc_id = module.params.get("id")
    filter_prefix = module.params.get("filter_prefix")
    filter_tags = module.params.get("filter_tags")

    metrics_configuration = get_bucket_metrics_configuration(client, bucket_name, mc_id)
    new_configuration = create_metrics_configuration(mc_id, filter_prefix, filter_tags)

    # Check if already in desired state
    if metrics_configuration and metrics_configuration == new_configuration:
        return False

    if module.check_mode:
        return True

    put_bucket_metrics_configuration(client, bucket_name, mc_id, new_configuration)
    return True


def delete_metrics_configuration(module, client):
    """Delete bucket metrics configuration."""
    bucket_name = module.params.get("bucket_name")
    mc_id = module.params.get("id")

    metrics_configuration = get_bucket_metrics_configuration(client, bucket_name, mc_id)

    # Check if already absent
    if not metrics_configuration:
        return False

    if module.check_mode:
        return True

    result = delete_bucket_metrics_configuration(client, bucket_name, mc_id)
    # If result is False, configuration didn't exist (race condition - already deleted)
    return result is not False


def main():
    argument_spec = dict(
        bucket_name=dict(type="str", required=True),
        id=dict(type="str", required=True),
        filter_prefix=dict(type="str", required=False),
        filter_tags=dict(default={}, type="dict", required=False, aliases=["filter_tag"]),
        state=dict(default="present", type="str", choices=["present", "absent"]),
    )
    module = AnsibleAWSModule(argument_spec=argument_spec, supports_check_mode=True)

    try:
        client = module.client("s3")
        state = module.params.get("state")

        if state == "present":
            changed = create_or_update_metrics_configuration(module, client)
        else:  # absent
            changed = delete_metrics_configuration(module, client)

        module.exit_json(changed=changed)
    except AnsibleS3Error as e:
        module.fail_json_aws_error(e)


if __name__ == "__main__":
    main()
