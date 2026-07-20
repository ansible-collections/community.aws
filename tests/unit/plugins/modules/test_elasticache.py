# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from ansible_collections.community.aws.plugins.modules import elasticache


def make_replication_group_manager(wait=False):
    module = MagicMock()
    module.client.return_value = MagicMock()
    with patch.object(elasticache.ReplicationGroupManager, "_refresh_data"):
        return elasticache.ReplicationGroupManager(
            module=module,
            name="test-rg",
            engine="redis",
            cache_engine_version="",
            node_type="cache.t3.micro",
            num_cache_clusters=1,
            cache_port=None,
            cache_parameter_group="",
            cache_subnet_group="",
            cache_security_groups=[],
            security_group_ids=[],
            replication_group_description="test",
            automatic_failover=None,
            multi_az_enabled=None,
            transit_encryption_enabled=None,
            replicas_per_node_group=None,
            num_node_groups=None,
            cluster_mode=None,
            retain_primary_cluster=None,
            wait=wait,
        )


def test_replication_group_exists_in_snapshotting_status():
    manager = make_replication_group_manager()
    manager.status = "snapshotting"

    assert manager.exists() is True


def test_replication_group_exists_in_create_failed_status():
    manager = make_replication_group_manager()
    manager.status = "create-failed"

    assert manager.exists() is True


def test_replication_group_sync_fails_in_create_failed_status():
    manager = make_replication_group_manager()
    manager.status = "create-failed"
    manager.module.fail_json.side_effect = RuntimeError("fail_json called")

    with pytest.raises(RuntimeError):
        manager.sync()

    manager.module.fail_json.assert_called_once_with(
        msg="'test-rg' is in create-failed status. Cannot sync. Delete and recreate the replication group."
    )


def test_replication_group_create_waits_when_snapshotting():
    manager = make_replication_group_manager(wait=True)
    manager.status = "snapshotting"
    manager._wait_for_status = MagicMock()

    manager.create()

    manager._wait_for_status.assert_called_once_with("available")
