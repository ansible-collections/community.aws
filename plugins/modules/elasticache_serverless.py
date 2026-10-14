#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: elasticache_serverless
version_added: "12.0.0"
short_description: Manage ElastiCache Serverless caches.
description:
  - Create, update, and delete Amazon ElastiCache Serverless caches.
  - ElastiCache Serverless scales cache capacity automatically; no node type or node count is required.
  - Supports C(redis) and C(valkey) engines. Memcached is not available in serverless mode.
author:
  - Ansible Project
options:
  state:
    description:
      - The desired state of the serverless cache.
    required: true
    choices: ["present", "absent"]
    type: str
  name:
    description:
      - The name of the serverless cache.
      - Must be 50 characters or fewer.
    required: true
    type: str
  engine:
    description:
      - The engine type for the serverless cache.
    type: str
    choices: ["redis", "valkey"]
  description:
    description:
      - A user-defined description for the serverless cache.
    type: str
  major_engine_version:
    description:
      - The major engine version to use.
      - If omitted, AWS chooses the latest supported version.
    type: str
  cache_usage_limits:
    description:
      - Maximum capacity limits for the serverless cache.
      - Omitting this parameter leaves existing limits unchanged on update.
    type: dict
    suboptions:
      data_storage:
        description:
          - Data storage limit.
        type: dict
        suboptions:
          maximum:
            description: Upper storage limit in I(unit).
            type: int
          minimum:
            description: Lower storage limit in I(unit).
            type: int
          unit:
            description: Unit for data storage.
            type: str
            default: GB
      ecpu_per_second:
        description:
          - ElastiCache Processing Unit (ECPU) limit per second.
        type: dict
        suboptions:
          maximum:
            description: Upper ECPU/s limit.
            type: int
          minimum:
            description: Lower ECPU/s limit.
            type: int
  kms_key_id:
    description:
      - ARN of the KMS key used for encryption at rest.
      - Cannot be changed after creation.
    type: str
  security_group_ids:
    description:
      - List of VPC security group IDs to associate with the serverless cache.
    type: list
    elements: str
  subnet_ids:
    description:
      - List of VPC subnet IDs for the serverless cache.
      - Cannot be changed after creation.
    type: list
    elements: str
  snapshot_arns_to_restore:
    description:
      - List of snapshot ARNs to restore from when creating the cache.
      - Ignored on updates.
    type: list
    elements: str
  snapshot_retention_limit:
    description:
      - Number of days ElastiCache retains automatic snapshots.
      - Set to C(0) to disable automatic snapshots.
    type: int
  daily_snapshot_time:
    description:
      - Daily UTC time window (HH:MM) during which ElastiCache begins taking a snapshot.
    type: str
  tags:
    description:
      - Dictionary of tags to apply to the serverless cache.
      - If not set, tags are not modified.
    type: dict
  purge_tags:
    description:
      - If I(purge_tags=true) and I(tags) is set, existing tags not in I(tags) are removed.
    type: bool
    default: true
  wait:
    description:
      - Whether to wait for the cache to reach its target state before returning.
    type: bool
    default: true
  wait_timeout:
    description:
      - Maximum seconds to wait for the target state.
    type: int
    default: 600
extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
- name: Create a Redis serverless cache
  community.aws.elasticache_serverless:
    name: my-cache
    state: present
    engine: redis
    description: Production Redis cache
    subnet_ids:
      - subnet-aabbccdd
      - subnet-11223344
    security_group_ids:
      - sg-aabbccdd
    cache_usage_limits:
      data_storage:
        maximum: 100
        unit: GB
      ecpu_per_second:
        maximum: 5000
    tags:
      Environment: production

- name: Update cache limits and tags
  community.aws.elasticache_serverless:
    name: my-cache
    state: present
    cache_usage_limits:
      ecpu_per_second:
        maximum: 10000
    tags:
      Environment: production
      Team: platform

- name: Create a Valkey serverless cache
  community.aws.elasticache_serverless:
    name: my-valkey-cache
    state: present
    engine: valkey
    description: Production Valkey cache
    subnet_ids:
      - subnet-aabbccdd
      - subnet-11223344
    security_group_ids:
      - sg-aabbccdd
    tags:
      Environment: production

- name: Delete a serverless cache
  community.aws.elasticache_serverless:
    name: my-cache
    state: absent
"""

RETURN = r"""
serverless_cache:
  description: Details of the serverless cache.
  returned: when state is present
  type: dict
  contains:
    serverless_cache_name:
      description: Name of the serverless cache.
      type: str
      returned: always
    description:
      description: User-defined description.
      type: str
      returned: when set
    status:
      description: Current status of the cache (e.g. C(available), C(creating)).
      type: str
      returned: always
    engine:
      description: Cache engine type.
      type: str
      returned: always
    full_engine_version:
      description: Full engine version string.
      type: str
      returned: always
    arn:
      description: ARN of the serverless cache.
      type: str
      returned: always
    endpoint:
      description: Primary endpoint for connecting to the cache.
      type: dict
      returned: when available
    reader_endpoint:
      description: Reader endpoint (Redis and Valkey).
      type: dict
      returned: when available
    security_group_ids:
      description: VPC security group IDs associated with the cache.
      type: list
      elements: str
      returned: always
    subnet_ids:
      description: VPC subnet IDs.
      type: list
      elements: str
      returned: always
    cache_usage_limits:
      description: Current capacity limits.
      type: dict
      returned: when set
    snapshot_retention_limit:
      description: Number of days automatic snapshots are retained.
      type: int
      returned: when set
    daily_snapshot_time:
      description: Daily snapshot time window.
      type: str
      returned: when set
"""

import time

try:
    import botocore
except ImportError:
    pass

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.amazon.aws.plugins.module_utils.tagging import ansible_dict_to_boto3_tag_list
from ansible_collections.amazon.aws.plugins.module_utils.tagging import boto3_tag_list_to_ansible_dict
from ansible_collections.amazon.aws.plugins.module_utils.tagging import compare_aws_tags

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule

_WAIT_SLEEP = 10


def get_serverless_cache(client, name):
    try:
        caches = client.describe_serverless_caches(ServerlessCacheName=name).get("ServerlessCaches", [])
        return caches[0] if caches else None
    except client.exceptions.ServerlessCacheNotFoundFault:
        return None


def wait_for_status(client, module, name, target_status, timeout):
    elapsed = 0
    while elapsed < timeout:
        try:
            cache = get_serverless_cache(client, name)
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Failed while polling serverless cache status")
        if cache is None:
            if target_status == "deleted":
                return None
            module.fail_json(msg=f"Serverless cache '{name}' disappeared unexpectedly.")
        status = cache.get("Status")
        if status == target_status:
            return cache
        if status == "create-failed":
            module.fail_json(msg=f"Serverless cache '{name}' entered create-failed state.")
        time.sleep(_WAIT_SLEEP)
        elapsed += _WAIT_SLEEP
    module.fail_json(msg=f"Timed out after {timeout}s waiting for serverless cache '{name}' to reach '{target_status}'.")


def build_cache_usage_limits(raw):
    if not raw:
        return None
    result = {}
    ds = raw.get("data_storage")
    if ds:
        entry = {"Unit": ds.get("unit", "GB")}
        if ds.get("maximum") is not None:
            entry["Maximum"] = ds["maximum"]
        if ds.get("minimum") is not None:
            entry["Minimum"] = ds["minimum"]
        result["DataStorage"] = entry
    ecpu = raw.get("ecpu_per_second")
    if ecpu:
        entry = {}
        if ecpu.get("maximum") is not None:
            entry["Maximum"] = ecpu["maximum"]
        if ecpu.get("minimum") is not None:
            entry["Minimum"] = ecpu["minimum"]
        if entry:
            result["ECPUPerSecond"] = entry
    return result or None


def usage_limits_changed(existing, desired_raw):
    desired = build_cache_usage_limits(desired_raw)
    if not desired:
        return False, None
    existing = existing or {}
    changed = False
    for section, existing_key in [("DataStorage", "DataStorage"), ("ECPUPerSecond", "ECPUPerSecond")]:
        if section not in desired:
            continue
        ex = existing.get(existing_key, {})
        for k, v in desired[section].items():
            if ex.get(k) != v:
                changed = True
                break
        if changed:
            break
    return changed, desired if changed else None


def get_tags(client, module, arn):
    try:
        return boto3_tag_list_to_ansible_dict(
            client.list_tags_for_resource(ResourceName=arn).get("TagList", [])
        )
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Failed to fetch tags for serverless cache")


def ensure_tags(client, module, arn, current_tags, desired_tags, purge_tags):
    add_tags, remove_tags = compare_aws_tags(current_tags, desired_tags, purge_tags=purge_tags)
    if not (add_tags or remove_tags):
        return False
    if not module.check_mode:
        try:
            if remove_tags:
                client.remove_tags_from_resource(ResourceName=arn, TagKeys=remove_tags)
            if add_tags:
                client.add_tags_to_resource(ResourceName=arn, Tags=ansible_dict_to_boto3_tag_list(add_tags))
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Failed to update tags on serverless cache")
    return True


def format_result(cache):
    result = camel_dict_to_snake_dict(cache)
    # Flatten security group objects to a plain id list
    sg_ids = result.get("security_group_ids", [])
    if sg_ids and isinstance(sg_ids[0], dict):
        result["security_group_ids"] = [sg.get("security_group_id") for sg in sg_ids]
    return result


def main():
    argument_spec = dict(
        state=dict(required=True, choices=["present", "absent"]),
        name=dict(required=True),
        engine=dict(choices=["redis", "valkey"]),
        description=dict(),
        major_engine_version=dict(),
        cache_usage_limits=dict(
            type="dict",
            options=dict(
                data_storage=dict(
                    type="dict",
                    options=dict(
                        maximum=dict(type="int"),
                        minimum=dict(type="int"),
                        unit=dict(default="GB"),
                    ),
                ),
                ecpu_per_second=dict(
                    type="dict",
                    options=dict(
                        maximum=dict(type="int"),
                        minimum=dict(type="int"),
                    ),
                ),
            ),
        ),
        kms_key_id=dict(),
        security_group_ids=dict(type="list", elements="str"),
        subnet_ids=dict(type="list", elements="str"),
        snapshot_arns_to_restore=dict(type="list", elements="str"),
        snapshot_retention_limit=dict(type="int"),
        daily_snapshot_time=dict(),
        tags=dict(type="dict"),
        purge_tags=dict(type="bool", default=True),
        wait=dict(type="bool", default=True),
        wait_timeout=dict(type="int", default=600),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    client = module.client("elasticache")
    state = module.params["state"]
    name = module.params["name"]
    wait = module.params["wait"]

    if len(name) > 50:
        module.fail_json(msg="Serverless cache name cannot be longer than 50 characters.")
    wait_timeout = module.params["wait_timeout"]

    try:
        existing = get_serverless_cache(client, name)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Failed to describe serverless cache")

    results = dict(changed=False)

    if state == "present":
        if existing is None:
            params = {"ServerlessCacheName": name}
            if module.params.get("engine"):
                params["Engine"] = module.params["engine"]
            if module.params.get("description"):
                params["Description"] = module.params["description"]
            if module.params.get("major_engine_version"):
                params["MajorEngineVersion"] = module.params["major_engine_version"]
            limits = build_cache_usage_limits(module.params.get("cache_usage_limits"))
            if limits:
                params["CacheUsageLimits"] = limits
            if module.params.get("kms_key_id"):
                params["KmsKeyId"] = module.params["kms_key_id"]
            if module.params.get("security_group_ids"):
                params["SecurityGroupIds"] = module.params["security_group_ids"]
            if module.params.get("subnet_ids"):
                params["SubnetIds"] = module.params["subnet_ids"]
            if module.params.get("snapshot_arns_to_restore"):
                params["SnapshotArnsToRestore"] = module.params["snapshot_arns_to_restore"]
            if module.params.get("snapshot_retention_limit") is not None:
                params["SnapshotRetentionLimit"] = module.params["snapshot_retention_limit"]
            if module.params.get("daily_snapshot_time"):
                params["DailySnapshotTime"] = module.params["daily_snapshot_time"]
            desired_tags = module.params.get("tags")
            if desired_tags:
                params["Tags"] = ansible_dict_to_boto3_tag_list(desired_tags)

            if not module.check_mode:
                try:
                    cache = client.create_serverless_cache(**params)["ServerlessCache"]
                except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
                    module.fail_json_aws(e, msg="Failed to create serverless cache")
                if wait:
                    cache = wait_for_status(client, module, name, "available", wait_timeout)
                results["serverless_cache"] = format_result(cache)
            results["changed"] = True

        else:
            cache = existing
            modify_params = {}

            if module.params.get("description") is not None:
                if module.params["description"] != existing.get("Description", ""):
                    modify_params["Description"] = module.params["description"]

            limits_changed, new_limits = usage_limits_changed(
                existing.get("CacheUsageLimits"), module.params.get("cache_usage_limits")
            )
            if limits_changed:
                modify_params["CacheUsageLimits"] = new_limits

            if module.params.get("security_group_ids") is not None:
                existing_sg_ids = sorted(
                    sg["SecurityGroupId"] for sg in existing.get("SecurityGroupIds", [])
                    if isinstance(sg, dict)
                )
                if sorted(module.params["security_group_ids"]) != existing_sg_ids:
                    modify_params["SecurityGroupIds"] = module.params["security_group_ids"]

            if module.params.get("snapshot_retention_limit") is not None:
                if module.params["snapshot_retention_limit"] != existing.get("SnapshotRetentionLimit"):
                    modify_params["SnapshotRetentionLimit"] = module.params["snapshot_retention_limit"]

            if module.params.get("daily_snapshot_time"):
                if module.params["daily_snapshot_time"] != existing.get("DailySnapshotTime"):
                    modify_params["DailySnapshotTime"] = module.params["daily_snapshot_time"]

            if modify_params:
                if not module.check_mode:
                    try:
                        cache = client.modify_serverless_cache(
                            ServerlessCacheName=name, **modify_params
                        )["ServerlessCache"]
                    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
                        module.fail_json_aws(e, msg="Failed to modify serverless cache")
                    if wait:
                        cache = wait_for_status(client, module, name, "available", wait_timeout)
                results["changed"] = True

            desired_tags = module.params.get("tags")
            if desired_tags is not None:
                current_tags = get_tags(client, module, existing["ARN"])
                if ensure_tags(client, module, existing["ARN"], current_tags, desired_tags, module.params["purge_tags"]):
                    results["changed"] = True

            results["serverless_cache"] = format_result(cache)

    elif state == "absent":
        if existing:
            if not module.check_mode:
                try:
                    client.delete_serverless_cache(ServerlessCacheName=name)
                except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
                    module.fail_json_aws(e, msg="Failed to delete serverless cache")
                if wait:
                    wait_for_status(client, module, name, "deleted", wait_timeout)
            results["changed"] = True

    module.exit_json(**results)


if __name__ == "__main__":
    main()
