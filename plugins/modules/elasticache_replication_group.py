#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: elasticache_replication_group
version_added: "12.1.0"
short_description: Manage ElastiCache replication groups
description:
  - Creates, modifies, and deletes ElastiCache replication groups.
  - Supports Redis and Valkey engines.
  - A replication group consists of a primary node and one or more read replicas.
author:
  - Ansible Project
options:
  state:
    description:
      - C(present) to create or update a replication group.
      - C(absent) to delete a replication group.
    choices: ['present', 'absent']
    required: true
    type: str
  replication_group_id:
    description:
      - The identifier for the replication group.
      - Must be 1–40 characters and contain only letters, digits, or hyphens.
      - Must begin with a letter.
    required: true
    type: str
  description:
    description:
      - A user-supplied description for the replication group.
      - Required when I(state=present) and the group does not yet exist.
    type: str
  engine:
    description:
      - The cache engine to use for the replication group.
      - C(redis) and C(valkey) are supported.
    choices: ['redis', 'valkey']
    default: redis
    type: str
  engine_version:
    description:
      - The version number of the cache engine.
    type: str
  node_type:
    description:
      - The compute and memory capacity of the nodes.
    type: str
  num_cache_clusters:
    description:
      - The number of clusters this replication group initially has.
      - This is the total number of nodes (primary + replicas) when not in cluster mode.
      - Mutually exclusive with I(num_node_groups) and I(replicas_per_node_group).
    type: int
  num_node_groups:
    description:
      - The number of node groups (shards) for this replication group.
      - Must be used together with I(replicas_per_node_group) to enable cluster mode.
      - Mutually exclusive with I(num_cache_clusters).
    type: int
  replicas_per_node_group:
    description:
      - The number of replica nodes in each node group.
      - Required when I(num_node_groups) is set.
      - Mutually exclusive with I(num_cache_clusters).
    type: int
  automatic_failover_enabled:
    description:
      - Enable automatic failover for this replication group.
      - When enabled, the number of nodes in the replication group must be at least 2.
    type: bool
  multi_az_enabled:
    description:
      - Enable Multi-AZ support for this replication group.
    type: bool
  cache_subnet_group_name:
    description:
      - The name of the cache subnet group to be used for this replication group.
    type: str
  security_group_ids:
    description:
      - One or more VPC security group IDs to associate with this replication group.
    type: list
    elements: str
  cache_parameter_group_name:
    description:
      - The name of the parameter group to associate with this replication group.
    type: str
  at_rest_encryption_enabled:
    description:
      - Enable encryption of data stored on disk.
      - Can only be set when creating the replication group.
    type: bool
  transit_encryption_enabled:
    description:
      - Enable encryption of data in transit.
      - Can only be set when creating the replication group.
    type: bool
  auth_token:
    description:
      - The password used to access a password protected server.
      - Must be specified along with I(transit_encryption_enabled=true).
    type: str
  snapshot_retention_limit:
    description:
      - The number of days for which ElastiCache retains automatic snapshots.
      - Set to C(0) to disable snapshots.
    type: int
  snapshot_window:
    description:
      - The daily time range (in UTC) during which ElastiCache begins taking a daily snapshot.
      - 'Example: C(05:00-09:00).'
    type: str
  preferred_maintenance_window:
    description:
      - Specifies the weekly time range during which system maintenance can occur.
      - 'Format: C(ddd:hh24:mi-ddd:hh24:mi), e.g. C(sun:05:00-sun:09:00).'
    type: str
  port:
    description:
      - The port number on which each member of the replication group accepts connections.
    type: int
  apply_immediately:
    description:
      - If C(true), apply modifications immediately instead of at the next maintenance window.
    type: bool
    default: true
  wait:
    description:
      - Wait for the replication group to reach the desired state before returning.
    type: bool
    default: true
  wait_timeout:
    description:
      - How many seconds to wait for the replication group to become available or be deleted.
    type: int
    default: 900
extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
  - amazon.aws.tags
"""

EXAMPLES = r"""
- name: Create a single-node Valkey replication group
  community.aws.elasticache_replication_group:
    replication_group_id: my-valkey-rg
    description: My Valkey replication group
    engine: valkey
    engine_version: "7.2"
    node_type: cache.t3.micro
    num_cache_clusters: 1
    state: present

- name: Create a Redis replication group with 1 primary and 2 replicas
  community.aws.elasticache_replication_group:
    replication_group_id: my-redis-rg
    description: My Redis replication group
    engine: redis
    node_type: cache.t3.medium
    num_cache_clusters: 3
    automatic_failover_enabled: true
    multi_az_enabled: true
    cache_subnet_group_name: my-subnet-group
    security_group_ids:
      - sg-12345678
    state: present

- name: Create a Valkey cluster-mode replication group
  community.aws.elasticache_replication_group:
    replication_group_id: my-valkey-cluster
    description: Valkey cluster mode
    engine: valkey
    node_type: cache.r6g.large
    num_node_groups: 3
    replicas_per_node_group: 1
    automatic_failover_enabled: true
    at_rest_encryption_enabled: true
    transit_encryption_enabled: true
    state: present

- name: Delete a replication group
  community.aws.elasticache_replication_group:
    replication_group_id: my-valkey-rg
    state: absent
"""

RETURN = r"""
replication_group:
  description: Details of the replication group.
  returned: when I(state=present)
  type: dict
  contains:
    replication_group_id:
      description: The identifier for the replication group.
      returned: always
      type: str
      sample: my-valkey-rg
    description:
      description: The user supplied description of the replication group.
      returned: always
      type: str
    status:
      description: The current state of the replication group.
      returned: always
      type: str
      sample: available
    member_clusters:
      description: The names of all the cache clusters that are part of this replication group.
      returned: always
      type: list
      elements: str
    node_groups:
      description: A list of node groups in this replication group.
      returned: always
      type: list
      elements: dict
    snapshotting_cluster_id:
      description: The cluster ID that is used as the daily snapshot source.
      returned: always
      type: str
    automatic_failover:
      description: Indicates the status of automatic failover.
      returned: always
      type: str
      sample: enabled
    multi_az:
      description: Whether Multi-AZ is enabled.
      returned: always
      type: str
      sample: enabled
    cache_node_type:
      description: The node type used by this replication group.
      returned: always
      type: str
      sample: cache.t3.micro
    auth_token_enabled:
      description: Whether an auth token (password) is required.
      returned: always
      type: bool
    transit_encryption_enabled:
      description: Whether in-transit encryption is enabled.
      returned: always
      type: bool
    at_rest_encryption_enabled:
      description: Whether at-rest encryption is enabled.
      returned: always
      type: bool
    arn:
      description: The ARN of the replication group.
      returned: always
      type: str
"""

from time import sleep

try:
    import botocore
except ImportError:
    pass  # Handled by AnsibleAWSModule

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.amazon.aws.plugins.module_utils.botocore import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.retries import AWSRetry
from ansible_collections.amazon.aws.plugins.module_utils.tagging import (
    ansible_dict_to_boto3_tag_list,
    boto3_tag_list_to_ansible_dict,
    compare_aws_tags,
)

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule

TERMINAL_STATUSES = {"available", "create-failed"}
WAIT_STATUSES = {"creating", "modifying", "snapshotting"}


def get_replication_group(client, replication_group_id):
    try:
        response = client.describe_replication_groups(
            aws_retry=True,
            ReplicationGroupId=replication_group_id,
        )
        return response["ReplicationGroups"][0]
    except is_boto3_error_code("ReplicationGroupNotFoundFault"):
        return None
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Failed to describe replication group")


def wait_for_status(replication_group_id, awaited_status, timeout):
    elapsed = 0
    while elapsed < timeout:
        rg = get_replication_group(client, replication_group_id)
        if awaited_status == "gone":
            if rg is None:
                return
        else:
            if rg and rg["Status"] == awaited_status:
                return
            if rg and rg["Status"] == "create-failed":
                module.fail_json(msg=f"Replication group '{replication_group_id}' entered create-failed status.")
        sleep(15)
        elapsed += 15
    module.fail_json(
        msg=f"Timed out waiting for replication group '{replication_group_id}' to reach status '{awaited_status}'."
    )


def get_replication_group_tags(replication_group_arn):
    try:
        tags = client.list_tags_for_resource(aws_retry=True, ResourceName=replication_group_arn)["TagList"]
        return boto3_tag_list_to_ansible_dict(tags)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Failed to list tags for replication group")


def set_replication_group_tags(replication_group_arn, existing_tags, desired_tags, purge_tags):
    tags_to_add, tags_to_remove = compare_aws_tags(existing_tags, desired_tags, purge_tags)
    if not tags_to_add and not tags_to_remove:
        return False

    if module.check_mode:
        return True

    if tags_to_remove:
        try:
            client.remove_tags_from_resource(
                aws_retry=True,
                ResourceName=replication_group_arn,
                TagKeys=tags_to_remove,
            )
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Failed to remove tags from replication group")

    if tags_to_add:
        try:
            client.add_tags_to_resource(
                aws_retry=True,
                ResourceName=replication_group_arn,
                Tags=ansible_dict_to_boto3_tag_list(tags_to_add),
            )
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Failed to add tags to replication group")

    return True


def create_replication_group(params):
    replication_group_id = params["replication_group_id"]
    description = params["description"]
    if not description:
        module.fail_json(msg="'description' is required when creating a replication group")

    create_params = dict(
        ReplicationGroupId=replication_group_id,
        ReplicationGroupDescription=description,
        Engine=params["engine"],
    )

    optional_str_params = {
        "engine_version": "EngineVersion",
        "node_type": "CacheNodeType",
        "cache_subnet_group_name": "CacheSubnetGroupName",
        "cache_parameter_group_name": "CacheParameterGroupName",
        "snapshot_window": "SnapshotWindow",
        "preferred_maintenance_window": "PreferredMaintenanceWindow",
        "auth_token": "AuthToken",
    }
    for ansible_key, boto_key in optional_str_params.items():
        if params[ansible_key] is not None:
            create_params[boto_key] = params[ansible_key]

    optional_int_params = {
        "port": "Port",
        "snapshot_retention_limit": "SnapshotRetentionLimit",
    }
    for ansible_key, boto_key in optional_int_params.items():
        if params[ansible_key] is not None:
            create_params[boto_key] = params[ansible_key]

    optional_bool_params = {
        "automatic_failover_enabled": "AutomaticFailoverEnabled",
        "multi_az_enabled": "MultiAZEnabled",
        "at_rest_encryption_enabled": "AtRestEncryptionEnabled",
        "transit_encryption_enabled": "TransitEncryptionEnabled",
    }
    for ansible_key, boto_key in optional_bool_params.items():
        if params[ansible_key] is not None:
            create_params[boto_key] = params[ansible_key]

    if params["security_group_ids"]:
        create_params["SecurityGroupIds"] = params["security_group_ids"]

    if params["num_node_groups"] is not None:
        create_params["NumNodeGroups"] = params["num_node_groups"]
        if params["replicas_per_node_group"] is not None:
            create_params["ReplicasPerNodeGroup"] = params["replicas_per_node_group"]
    elif params["num_cache_clusters"] is not None:
        create_params["NumCacheClusters"] = params["num_cache_clusters"]

    if params["tags"]:
        create_params["Tags"] = ansible_dict_to_boto3_tag_list(params["tags"])

    if module.check_mode:
        return True

    try:
        client.create_replication_group(aws_retry=True, **create_params)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Failed to create replication group")

    if params["wait"]:
        wait_for_status(replication_group_id, "available", params["wait_timeout"])

    return True


def modify_replication_group(existing_rg, params):
    replication_group_id = params["replication_group_id"]
    modify_params = dict(
        ReplicationGroupId=replication_group_id,
        ApplyImmediately=params["apply_immediately"],
    )

    changed = False

    if params["description"] and existing_rg.get("Description") != params["description"]:
        modify_params["ReplicationGroupDescription"] = params["description"]
        changed = True

    if params["node_type"] and existing_rg.get("CacheNodeType") != params["node_type"]:
        modify_params["CacheNodeType"] = params["node_type"]
        changed = True

    if params["engine_version"] is not None:
        # EngineVersion is stored on member clusters; always pass through if provided
        modify_params["EngineVersion"] = params["engine_version"]
        changed = True

    if params["cache_parameter_group_name"] is not None:
        modify_params["CacheParameterGroupName"] = params["cache_parameter_group_name"]
        changed = True

    if params["security_group_ids"] is not None:
        existing_sgs = {sg["SecurityGroupId"] for sg in existing_rg.get("SecurityGroups", [])}
        if set(params["security_group_ids"]) != existing_sgs:
            modify_params["SecurityGroupIds"] = params["security_group_ids"]
            changed = True

    if params["automatic_failover_enabled"] is not None:
        current_af = existing_rg.get("AutomaticFailover", "disabled").lower() == "enabled"
        if params["automatic_failover_enabled"] != current_af:
            modify_params["AutomaticFailoverEnabled"] = params["automatic_failover_enabled"]
            changed = True

    if params["multi_az_enabled"] is not None:
        current_maz = existing_rg.get("MultiAZ", "disabled").lower() == "enabled"
        if params["multi_az_enabled"] != current_maz:
            modify_params["MultiAZEnabled"] = params["multi_az_enabled"]
            changed = True

    if params["snapshot_retention_limit"] is not None:
        if existing_rg.get("SnapshotRetentionLimit") != params["snapshot_retention_limit"]:
            modify_params["SnapshotRetentionLimit"] = params["snapshot_retention_limit"]
            changed = True

    if params["snapshot_window"] is not None:
        if existing_rg.get("SnapshotWindow") != params["snapshot_window"]:
            modify_params["SnapshotWindow"] = params["snapshot_window"]
            changed = True

    if params["preferred_maintenance_window"] is not None:
        if existing_rg.get("PreferredMaintenanceWindow") != params["preferred_maintenance_window"]:
            modify_params["PreferredMaintenanceWindow"] = params["preferred_maintenance_window"]
            changed = True

    if params["num_cache_clusters"] is not None:
        current_count = len(existing_rg.get("MemberClusters", []))
        if params["num_cache_clusters"] != current_count:
            modify_params["NumCacheClusters"] = params["num_cache_clusters"]
            changed = True

    if not changed:
        return False

    if module.check_mode:
        return True

    try:
        client.modify_replication_group(aws_retry=True, **modify_params)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Failed to modify replication group")

    if params["wait"]:
        wait_for_status(replication_group_id, "available", params["wait_timeout"])

    return True


def delete_replication_group(replication_group_id, wait, wait_timeout):
    if module.check_mode:
        return True

    try:
        client.delete_replication_group(
            aws_retry=True,
            ReplicationGroupId=replication_group_id,
        )
    except is_boto3_error_code("ReplicationGroupNotFoundFault"):
        return False
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Failed to delete replication group")

    if wait:
        wait_for_status(replication_group_id, "gone", wait_timeout)

    return True


def main():
    argument_spec = dict(
        state=dict(required=True, choices=["present", "absent"]),
        replication_group_id=dict(required=True, type="str"),
        description=dict(type="str"),
        engine=dict(default="redis", choices=["redis", "valkey"], type="str"),
        engine_version=dict(type="str"),
        node_type=dict(type="str"),
        num_cache_clusters=dict(type="int"),
        num_node_groups=dict(type="int"),
        replicas_per_node_group=dict(type="int"),
        automatic_failover_enabled=dict(type="bool"),
        multi_az_enabled=dict(type="bool"),
        cache_subnet_group_name=dict(type="str"),
        security_group_ids=dict(type="list", elements="str"),
        cache_parameter_group_name=dict(type="str"),
        at_rest_encryption_enabled=dict(type="bool"),
        transit_encryption_enabled=dict(type="bool"),
        auth_token=dict(type="str", no_log=True),
        snapshot_retention_limit=dict(type="int"),
        snapshot_window=dict(type="str"),
        preferred_maintenance_window=dict(type="str"),
        port=dict(type="int"),
        tags=dict(type="dict", aliases=["resource_tags"]),
        purge_tags=dict(type="bool", default=True),
        apply_immediately=dict(type="bool", default=True),
        wait=dict(type="bool", default=True),
        wait_timeout=dict(type="int", default=900),
    )

    global module
    global client

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[
            ["num_cache_clusters", "num_node_groups"],
            ["num_cache_clusters", "replicas_per_node_group"],
        ],
        required_together=[
            ["num_node_groups", "replicas_per_node_group"],
        ],
    )

    client = module.client("elasticache", retry_decorator=AWSRetry.jittered_backoff())

    state = module.params["state"]
    replication_group_id = module.params["replication_group_id"]
    params = module.params

    existing_rg = get_replication_group(client, replication_group_id)
    changed = False

    if state == "present":
        if existing_rg is None:
            changed = create_replication_group(params)
        else:
            if existing_rg["Status"] in WAIT_STATUSES and params["wait"]:
                wait_for_status(replication_group_id, "available", params["wait_timeout"])
                existing_rg = get_replication_group(client, replication_group_id)
            changed = modify_replication_group(existing_rg, params)

            if params["tags"] is not None:
                current_tags = get_replication_group_tags(existing_rg["ARN"])
                tags_changed = set_replication_group_tags(
                    existing_rg["ARN"], current_tags, params["tags"], params["purge_tags"]
                )
                changed = changed or tags_changed

        rg = get_replication_group(client, replication_group_id)
        if rg:
            result = camel_dict_to_snake_dict(rg)
        else:
            result = {}
        module.exit_json(changed=changed, replication_group=result)

    else:  # state == "absent"
        if existing_rg is None:
            module.exit_json(changed=False, replication_group={})

        if existing_rg["Status"] in WAIT_STATUSES and params["wait"]:
            wait_for_status(replication_group_id, "available", params["wait_timeout"])

        changed = delete_replication_group(replication_group_id, params["wait"], params["wait_timeout"])
        module.exit_json(changed=changed, replication_group={})


if __name__ == "__main__":
    main()
