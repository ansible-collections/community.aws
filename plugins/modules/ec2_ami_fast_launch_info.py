#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: ec2_ami_fast_launch_info
version_added: 12.0.0
short_description: Gather information about EC2 Fast Launch enabled AMIs
description:
  - Gather information about AMIs that have EC2 Fast Launch enabled.
  - See U(https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/win-ami-config-fast-launch.html)
    for details on EC2 Fast Launch.
author:
  - "Ewald Bervoets (@ewaldbervoets)"
options:
  image_ids:
    description:
      - Restrict results to the specified AMI IDs.
    required: false
    type: list
    elements: str
  filters:
    description:
      - A dict of filters to apply. Each dict item consists of a filter key and a filter value.
        See U(https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeFastLaunchImages.html)
        for possible filters.
    required: false
    default: {}
    type: dict
extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details, see the AWS Guide for details.

- name: Gather information about all Fast Launch enabled AMIs
  community.aws.ec2_ami_fast_launch_info:
    region: us-east-1
  register: fast_launch_info

- name: Gather information about a specific Fast Launch enabled AMI
  community.aws.ec2_ami_fast_launch_info:
    region: us-east-1
    image_ids:
      - ami-0123456789abcdef0

- name: Filter by Fast Launch state
  community.aws.ec2_ami_fast_launch_info:
    region: us-east-1
    filters:
      state: enabled
"""

RETURN = r"""
changed:
    description: Always false; this is a read-only module.
    type: bool
    returned: always
    sample: false
fast_launch_images:
    description: List of Fast Launch enabled AMIs.
    returned: always
    type: complex
    contains:
        image_id:
            description: The ID of the AMI.
            type: str
            sample: ami-0123456789abcdef0
        resource_type:
            description: The pre-provisioned resource type used by Fast Launch.
            type: str
            sample: snapshot
        snapshot_configuration:
            description: Snapshot configuration used to pre-provision the AMI.
            type: dict
            contains:
                target_resource_count:
                    description: Target number of pre-provisioned snapshots to keep on hand.
                    type: int
                    sample: 5
        launch_template:
            description: Launch template used when provisioning pre-provisioned snapshots.
            type: dict
            contains:
                launch_template_id:
                    description: ID of the launch template.
                    type: str
                launch_template_name:
                    description: Name of the launch template.
                    type: str
                version:
                    description: Version of the launch template.
                    type: str
        max_parallel_launches:
            description: Maximum number of parallel instances launched for pre-provisioning.
            type: int
            sample: 6
        owner_id:
            description: AWS account ID that owns the AMI.
            type: str
            sample: "123456789012"
        state:
            description: Current Fast Launch state for the AMI.
            type: str
            sample: enabled
        state_transition_reason:
            description: Reason for the most recent state transition.
            type: str
        state_transition_time:
            description: ISO 8601 timestamp of the most recent state transition.
            type: str
"""

try:
    import botocore
except ImportError:
    pass  # Handled by AnsibleAWSModule

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.amazon.aws.plugins.module_utils.retries import AWSRetry
from ansible_collections.amazon.aws.plugins.module_utils.transformation import ansible_dict_to_boto3_filter_list

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule


def list_fast_launch_images(connection, module):
    params = {}
    filters = module.params.get("filters")
    if filters:
        params["Filters"] = ansible_dict_to_boto3_filter_list(filters)
    image_ids = module.params.get("image_ids")
    if image_ids:
        params["ImageIds"] = image_ids

    try:
        paginator = connection.get_paginator("describe_fast_launch_images")
        images = []
        for page in paginator.paginate(**params):
            images.extend(page.get("FastLaunchImages", []))
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Unable to describe Fast Launch images")

    return [camel_dict_to_snake_dict(image) for image in images]


def main():
    argument_spec = dict(
        image_ids=dict(type="list", elements="str"),
        filters=dict(type="dict", default={}),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    try:
        connection = module.client("ec2", retry_decorator=AWSRetry.jittered_backoff())
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Failed to connect to AWS")

    results = list_fast_launch_images(connection, module)
    module.exit_json(changed=False, fast_launch_images=results)


if __name__ == "__main__":
    main()
