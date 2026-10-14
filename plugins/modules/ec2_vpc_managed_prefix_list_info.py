#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: ec2_vpc_managed_prefix_list_info
version_added: 11.1.0
short_description: Retrieve information about AWS EC2 Managed Prefix Lists
description:
  - Retrieve information about one or more AWS EC2 Managed Prefix Lists.
  - Optionally retrieves the CIDR entries for each prefix list.
author:
  - Andrii Savchenko (@Ptico)
options:
  prefix_list_ids:
    description:
      - Get details of specific Managed Prefix Lists by ID.
      - Mutually exclusive with I(filters).
    type: list
    elements: str
    default: []
  filters:
    description:
      - A dict of filters to apply. Each dict item consists of a filter key and a filter value.
      - See U(https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeManagedPrefixLists.html) for possible filters.
      - Mutually exclusive with I(prefix_list_ids).
    type: dict
    default: {}
  include_entries:
    description:
      - If C(true), the CIDR entries of each prefix list are fetched and included in the output.
      - Set to C(false) to avoid the extra API call per prefix list when entries are not needed.
    type: bool
    default: true
extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details, see the AWS Guide for details.

- name: Gather information about all managed prefix lists
  community.aws.ec2_vpc_managed_prefix_list_info:
  register: result

- name: Gather information about a specific prefix list by ID
  community.aws.ec2_vpc_managed_prefix_list_info:
    prefix_list_ids:
      - pl-0a1b2c3d4e5f6789a
  register: result

- name: Gather information about multiple prefix lists by ID
  community.aws.ec2_vpc_managed_prefix_list_info:
    prefix_list_ids:
      - pl-0a1b2c3d4e5f6789a
      - pl-0b2c3d4e5f6789ab1
  register: result

- name: Gather information filtered by name
  community.aws.ec2_vpc_managed_prefix_list_info:
    filters:
      prefix-list-name: my-prefix-list
  register: result

- name: Gather information filtered by tag
  community.aws.ec2_vpc_managed_prefix_list_info:
    filters:
      "tag:Environment": production
  register: result

- name: Gather prefix list metadata only, without fetching CIDR entries
  community.aws.ec2_vpc_managed_prefix_list_info:
    include_entries: false
  register: result
"""

RETURN = r"""
prefix_lists:
  description: List of matching managed prefix lists.
  returned: always
  type: list
  elements: dict
  contains:
    prefix_list_id:
      description: The ID of the prefix list.
      type: str
      sample: "pl-0a1b2c3d4e5f6789a"
    prefix_list_arn:
      description: The ARN of the prefix list.
      type: str
      sample: "arn:aws:ec2:us-east-1:123456789012:prefix-list/pl-0a1b2c3d4e5f6789a"
    prefix_list_name:
      description: The name of the prefix list.
      type: str
      sample: "my-prefix-list"
    address_family:
      description: The IP address family.
      type: str
      sample: "IPv4"
    max_entries:
      description: The maximum number of entries allowed.
      type: int
      sample: 10
    state:
      description: The current state of the prefix list.
      type: str
      sample: "create-complete"
    version:
      description: The version of the prefix list.
      type: int
      sample: 1
    tags:
      description: Tags applied to the prefix list.
      type: dict
      sample: {"Name": "my-prefix-list", "Environment": "production"}
    entries:
      description: The CIDR entries in the prefix list. Only present when I(include_entries=true).
      type: list
      elements: dict
      contains:
        cidr:
          description: The CIDR block.
          type: str
          sample: "10.0.0.0/24"
        description:
          description: Description of the CIDR block.
          type: str
          sample: "My subnet"
"""

try:
    import botocore
except ImportError:
    pass  # caught by AnsibleAWSModule

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.amazon.aws.plugins.module_utils.botocore import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.retries import AWSRetry
from ansible_collections.amazon.aws.plugins.module_utils.tagging import boto3_tag_list_to_ansible_dict
from ansible_collections.amazon.aws.plugins.module_utils.transformation import ansible_dict_to_boto3_filter_list

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule


def get_prefix_list_entries(client, module, prefix_list_id):
    """Retrieve all CIDR entries for a prefix list using pagination."""
    try:
        paginator = client.get_paginator("get_managed_prefix_list_entries")
        entries = paginator.paginate(PrefixListId=prefix_list_id).build_full_result()["Entries"]
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg=f"Failed to get entries for prefix list {prefix_list_id}")
    return [
        {"cidr": e["Cidr"], "description": e.get("Description") or ""}
        for e in entries
    ]


def format_prefix_list(prefix_list):
    """Convert a boto3 prefix list to Ansible snake_case format."""
    result = camel_dict_to_snake_dict(prefix_list, ignore_list=["Tags"])
    result["tags"] = boto3_tag_list_to_ansible_dict(prefix_list.get("Tags", []))
    return result


def list_prefix_lists(client, module):
    params = {}

    if module.params.get("prefix_list_ids"):
        params["PrefixListIds"] = module.params.get("prefix_list_ids")

    if module.params.get("filters"):
        params["Filters"] = ansible_dict_to_boto3_filter_list(module.params.get("filters"))

    try:
        paginator = client.get_paginator("describe_managed_prefix_lists")
        raw_prefix_lists = paginator.paginate(**params).build_full_result()["PrefixLists"]
    except is_boto3_error_code("InvalidPrefixListID.NotFound"):
        module.fail_json(msg="One or more prefix list IDs were not found")
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Failed to describe managed prefix lists")

    include_entries = module.params.get("include_entries")
    result = []

    for pl in raw_prefix_lists:
        pl_info = format_prefix_list(pl)
        if include_entries:
            pl_info["entries"] = get_prefix_list_entries(client, module, pl["PrefixListId"])
        result.append(pl_info)

    return result


def main():
    argument_spec = dict(
        prefix_list_ids=dict(type="list", elements="str", default=[]),
        filters=dict(type="dict", default={}),
        include_entries=dict(type="bool", default=True),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        mutually_exclusive=[["prefix_list_ids", "filters"]],
        supports_check_mode=True,
    )

    try:
        client = module.client("ec2", retry_decorator=AWSRetry.jittered_backoff())
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Failed to connect to AWS")

    prefix_lists = list_prefix_lists(client, module)

    module.exit_json(prefix_lists=prefix_lists)


if __name__ == "__main__":
    main()
