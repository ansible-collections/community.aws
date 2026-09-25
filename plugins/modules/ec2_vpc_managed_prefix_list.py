#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: ec2_vpc_managed_prefix_list
version_added: 11.1.0
short_description: Manage AWS EC2 Managed Prefix Lists
description:
  - Create, update, and delete AWS EC2 Managed Prefix Lists.
  - Supports idempotent operations and check mode.
notes:
  - The I(address_family) of a prefix list cannot be changed after creation.
author:
  - Andrii Savchenko (@Ptico)
options:
  state:
    description:
      - Whether the prefix list should be present or absent.
    choices: ['present', 'absent']
    default: present
    type: str
  name:
    description:
      - The name of the prefix list.
      - Required when I(state=present) and I(prefix_list_id) is not provided.
      - One of I(name) or I(prefix_list_id) is required.
    type: str
  prefix_list_id:
    description:
      - The ID of the prefix list.
      - One of I(name) or I(prefix_list_id) is required.
    type: str
  entries:
    description:
      - A list of CIDR entries for the prefix list.
      - If not specified, entries will not be modified.
    type: list
    elements: dict
    suboptions:
      cidr:
        description:
          - The CIDR block.
        type: str
        required: true
      description:
        description:
          - A description for the CIDR block.
        type: str
        default: ""
  max_entries:
    description:
      - The maximum number of entries for the prefix list.
      - Required when I(state=present).
    type: int
  address_family:
    description:
      - The IP address family (IPv4 or IPv6).
      - Cannot be changed after the prefix list is created.
    choices: ['IPv4', 'IPv6']
    default: IPv4
    type: str
  purge_entries:
    description:
      - If C(true), entries not present in I(entries) will be removed.
      - Has no effect when I(entries) is not specified.
    type: bool
    default: true
extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.tags
  - amazon.aws.boto3
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details, see the AWS Guide for details.

- name: Create a prefix list
  community.aws.ec2_vpc_managed_prefix_list:
    state: present
    name: my-prefix-list
    address_family: IPv4
    max_entries: 10
    entries:
      - cidr: 10.0.0.0/24
        description: My subnet
  register: prefix_list

- name: Create a prefix list with tags
  community.aws.ec2_vpc_managed_prefix_list:
    state: present
    name: my-prefix-list
    address_family: IPv4
    max_entries: 10
    tags:
      Environment: production
      Owner: networking-team
  register: prefix_list

- name: Update entries in a prefix list
  community.aws.ec2_vpc_managed_prefix_list:
    state: present
    name: my-prefix-list
    max_entries: 10
    entries:
      - cidr: 10.0.0.0/24
        description: My subnet
      - cidr: 10.1.0.0/24
        description: My other subnet

- name: Add entries without removing existing ones
  community.aws.ec2_vpc_managed_prefix_list:
    state: present
    prefix_list_id: pl-0a1b2c3d4e5f6789a
    max_entries: 10
    entries:
      - cidr: 10.2.0.0/24
        description: New subnet
    purge_entries: false

- name: Delete a prefix list by ID
  community.aws.ec2_vpc_managed_prefix_list:
    state: absent
    prefix_list_id: pl-0a1b2c3d4e5f6789a

- name: Delete a prefix list by name
  community.aws.ec2_vpc_managed_prefix_list:
    state: absent
    name: my-prefix-list
"""

RETURN = r"""
changed:
  description: Whether any changes were made.
  type: bool
  returned: always
prefix_list_id:
  description: The ID of the prefix list.
  type: str
  returned: I(state=present)
  sample: "pl-0a1b2c3d4e5f6789a"
prefix_list:
  description: The prefix list resource details.
  type: dict
  returned: I(state=present)
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
      sample: {"Environment": "production"}
    entries:
      description: The current entries in the prefix list.
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

from ansible_collections.amazon.aws.plugins.module_utils.ec2 import ensure_ec2_tags
from ansible_collections.amazon.aws.plugins.module_utils.retries import AWSRetry
from ansible_collections.amazon.aws.plugins.module_utils.tagging import boto3_tag_list_to_ansible_dict
from ansible_collections.amazon.aws.plugins.module_utils.tagging import boto3_tag_specifications

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule


def get_prefix_list(client, module):
    """Look up an existing prefix list by ID or name."""
    prefix_list_id = module.params.get("prefix_list_id")
    prefix_list_name = module.params.get("name")

    params = dict(aws_retry=True)

    if prefix_list_id:
        params["PrefixListIds"] = [prefix_list_id]
    elif prefix_list_name:
        params["Filters"] = [{"Name": "prefix-list-name", "Values": [prefix_list_name]}]

    try:
        response = client.describe_managed_prefix_lists(**params)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Failed to describe managed prefix lists")

    if response["PrefixLists"]:
        return response["PrefixLists"][0]
    return None


def get_prefix_list_entries(client, module, prefix_list_id):
    """Retrieve the current entries for a prefix list."""
    try:
        return client.get_managed_prefix_list_entries(
            aws_retry=True,
            PrefixListId=prefix_list_id,
        )["Entries"]
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg=f"Failed to get entries for prefix list {prefix_list_id}")


def create_prefix_list(client, module):
    """Create a new managed prefix list."""
    params = dict(
        PrefixListName=module.params.get("name"),
        MaxEntries=module.params.get("max_entries"),
        AddressFamily=module.params.get("address_family"),
    )

    if module.params.get("entries"):
        params["Entries"] = [
            {"Cidr": e["cidr"], "Description": e.get("description") or ""}
            for e in module.params.get("entries")
        ]

    if module.params.get("tags") is not None:
        params["TagSpecifications"] = boto3_tag_specifications(
            module.params.get("tags"), types="prefix-list"
        )

    try:
        pl = client.create_managed_prefix_list(**params)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Failed to create prefix list")

    return pl["PrefixList"]


def update_prefix_list(prefix_list, client, module):
    """Update an existing prefix list's name, max_entries, and/or entries."""
    prefix_list_id = prefix_list.get("PrefixListId")
    changed = False

    params = dict(
        PrefixListId=prefix_list_id,
        CurrentVersion=prefix_list.get("Version"),
    )

    if module.params.get("name") and module.params.get("name") != prefix_list.get("PrefixListName"):
        params["PrefixListName"] = module.params.get("name")
        changed = True

    if (
        module.params.get("max_entries") is not None
        and module.params.get("max_entries") != prefix_list.get("MaxEntries")
    ):
        params["MaxEntries"] = module.params.get("max_entries")
        changed = True

    # Address family cannot be changed after creation
    if (
        module.params.get("address_family")
        and module.params.get("address_family") != prefix_list.get("AddressFamily")
    ):
        module.fail_json(
            msg=(
                f"Cannot change address_family of an existing prefix list {prefix_list_id}. "
                f"Current: {prefix_list.get('AddressFamily')}, "
                f"Requested: {module.params.get('address_family')}"
            )
        )

    # Compute entry changes only when entries are specified
    if module.params.get("entries") is not None:
        new_entries = module.params.get("entries")
        existing_entries = get_prefix_list_entries(client, module, prefix_list_id)
        purge_entries = module.params.get("purge_entries")

        add_entries = []
        remove_entries = []

        new_dict = {item["cidr"]: item.get("description") or "" for item in new_entries}
        existing_dict = {item["Cidr"]: item.get("Description") or "" for item in existing_entries}

        for cidr, desc in new_dict.items():
            if cidr not in existing_dict:
                add_entries.append({"Cidr": cidr, "Description": desc})
            elif desc != existing_dict[cidr]:
                add_entries.append({"Cidr": cidr, "Description": desc})
                remove_entries.append({"Cidr": cidr})

        for cidr in existing_dict:
            if cidr not in new_dict and purge_entries:
                remove_entries.append({"Cidr": cidr})

        if add_entries:
            params["AddEntries"] = add_entries
            changed = True
        if remove_entries:
            params["RemoveEntries"] = remove_entries
            changed = True

    if not changed:
        return prefix_list, False

    if module.check_mode:
        return prefix_list, True

    try:
        prefix_list = client.modify_managed_prefix_list(**params)["PrefixList"]
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg=f"Failed to modify prefix list {prefix_list_id}")

    return prefix_list, True


def delete_prefix_list(prefix_list, client, module):
    """Delete an existing managed prefix list."""
    prefix_list_id = prefix_list["PrefixListId"]

    if module.check_mode:
        return

    try:
        client.delete_managed_prefix_list(
            aws_retry=True,
            PrefixListId=prefix_list_id,
        )
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg=f"Failed to delete prefix list {prefix_list_id}")


def format_prefix_list(prefix_list, entries):
    """Convert a boto3 prefix list response to Ansible snake_case format."""
    result = camel_dict_to_snake_dict(prefix_list, ignore_list=["Tags"])
    result["tags"] = boto3_tag_list_to_ansible_dict(prefix_list.get("Tags", []))
    result["entries"] = [
        {"cidr": e["Cidr"], "description": e.get("Description") or ""}
        for e in entries
    ]
    return result


def main():
    argument_spec = dict(
        name=dict(type="str"),
        prefix_list_id=dict(type="str"),
        entries=dict(
            type="list",
            elements="dict",
            options=dict(
                cidr=dict(type="str", required=True),
                description=dict(type="str", default=""),
            ),
        ),
        max_entries=dict(type="int"),
        state=dict(type="str", choices=["present", "absent"], default="present"),
        address_family=dict(type="str", choices=["IPv4", "IPv6"], default="IPv4"),
        tags=dict(type="dict", aliases=["resource_tags"]),
        purge_tags=dict(type="bool", default=True),
        purge_entries=dict(type="bool", default=True),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        required_if=[("state", "present", ["max_entries"])],
        required_one_of=[["name", "prefix_list_id"]],
        supports_check_mode=True,
    )

    client = module.client("ec2", retry_decorator=AWSRetry.jittered_backoff())

    prefix_list = get_prefix_list(client, module)
    state = module.params.get("state")
    changed = False

    if state == "present":
        if prefix_list:
            prefix_list, changed = update_prefix_list(prefix_list, client, module)

            tags_changed = ensure_ec2_tags(
                client,
                module,
                prefix_list["PrefixListId"],
                resource_type="prefix-list",
                tags=module.params.get("tags"),
                purge_tags=module.params.get("purge_tags"),
                retry_codes="InvalidPrefixListID.NotFound",
            )
            changed = changed or tags_changed

            # Re-fetch to reflect any changes (tags, entries, etc.)
            prefix_list = get_prefix_list(client, module)
            entries = get_prefix_list_entries(client, module, prefix_list["PrefixListId"])
            pl_info = format_prefix_list(prefix_list, entries)

            module.exit_json(
                changed=changed,
                prefix_list_id=prefix_list["PrefixListId"],
                prefix_list=pl_info,
            )
        else:
            if module.check_mode:
                module.exit_json(changed=True)

            prefix_list = create_prefix_list(client, module)
            # Re-fetch to get the full current state
            prefix_list = get_prefix_list(client, module)
            entries = get_prefix_list_entries(client, module, prefix_list["PrefixListId"])
            pl_info = format_prefix_list(prefix_list, entries)

            module.exit_json(
                changed=True,
                prefix_list_id=prefix_list["PrefixListId"],
                prefix_list=pl_info,
            )

    elif state == "absent":
        if prefix_list:
            delete_prefix_list(prefix_list, client, module)
            changed = True

        module.exit_json(changed=changed)


if __name__ == "__main__":
    main()
