# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from ansible_collections.community.aws.plugins.modules import elasticache


@pytest.fixture
def manager():
    with patch.object(elasticache.ElastiCacheManager, "_get_elasticache_connection"), patch.object(
        elasticache.ElastiCacheManager, "_refresh_data"
    ):
        return elasticache.ElastiCacheManager(
            module=MagicMock(),
            name="test",
            engine="redis",
            cache_engine_version="",
            node_type="cache.t3.micro",
            num_nodes=1,
            cache_port=None,
            cache_parameter_group=None,
            cache_subnet_group=None,
            cache_security_groups=[],
            security_group_ids=[],
            zone=None,
            wait=False,
            hard_modify=False,
        )


@pytest.mark.parametrize(
    ("requested", "current", "expected"),
    [
        ("6.x", "6.0.5", False),
        ("6.x", "6.2.6", False),
        ("6.x", "7.0.7", True),
        ("7.0", "7.0", False),
        ("7.0", "7.1", True),
        ("", "7.1", False),
    ],
)
def test_requires_modification_engine_version(manager, requested, current, expected):
    manager.cache_engine_version = requested
    manager.data = {"NumCacheNodes": 1, "EngineVersion": current, "CacheSecurityGroups": []}

    assert manager._requires_modification() is expected


def test_requires_modification_num_nodes(manager):
    manager.data = {"NumCacheNodes": 2, "EngineVersion": "7.1", "CacheSecurityGroups": []}

    assert manager._requires_modification() is True
