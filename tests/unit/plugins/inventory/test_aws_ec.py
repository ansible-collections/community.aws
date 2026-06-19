# -*- coding: utf-8 -*-

# Copyright 2024 Your friendly neighbourhood Rafael (@Rafjt/@Raf211)
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

import copy
import random
import string
from unittest.mock import MagicMock
from unittest.mock import call
from unittest.mock import patch

import pytest

try:
    import botocore
except ImportError:
    # Handled by HAS_BOTO3
    pass

from ansible.errors import AnsibleError

from ansible_collections.amazon.aws.plugins.inventory.aws_ec import InventoryModule
from ansible_collections.amazon.aws.plugins.inventory.aws_ec import _add_tags_for_ec_clusters
from ansible_collections.amazon.aws.plugins.inventory.aws_ec import _describe_replication_groups
from ansible_collections.amazon.aws.plugins.inventory.aws_ec import _describe_cache_clusters
from ansible_collections.amazon.aws.plugins.inventory.aws_ec import _find_ec_clusters_with_valid_statuses
from ansible_collections.amazon.aws.plugins.inventory.aws_ec import ansible_dict_to_boto3_filter_list
from ansible_collections.amazon.aws.plugins.module_utils.botocore import HAS_BOTO3

if not HAS_BOTO3:
    pytestmark = pytest.mark.skip("test_aws_ec.py requires the python modules 'boto3' and 'botocore'") 


def make_clienterror_exception(code="AccessDenied"):
    return botocore.exceptions.ClientError(
        {
            "Error": {"Code": code, "Message": "User is not authorized to perform: xxx on resource: user yyyy"},
            "ResponseMetadata": {"RequestId": "01234567-89ab-cdef-0123-456789abcdef"},
        },
        "getXXX",
    )


@pytest.fixture()
def inventory():
    inventory = InventoryModule()
    inventory.inventory = MagicMock()
    inventory._populate_host_vars = MagicMock()

    inventory.all_clients = MagicMock()
    inventory.get_option = MagicMock()

    inventory._set_composite_vars = MagicMock()
    inventory._add_host_to_composed_groups = MagicMock()
    inventory._add_host_to_keyed_groups = MagicMock()
    inventory._read_config_data = MagicMock()
    inventory._set_credentials = MagicMock()

    inventory.get_cache_key = MagicMock()

    inventory._cache = {}
    return inventory


@pytest.fixture()
def connection():
    conn = MagicMock()
    return conn

@pytest.mark.parametrize(
    "suffix,result",
    [
        ("aws_ec.yml", True),
        ("aws_ec.yaml", True),
        ("aws_EC.yml", False),
        ("AWS_ec.yaml", False),
    ],
)

def test_inventory_verify_file_suffix(inventory, suffix, result, tmp_path):
    test_dir = tmp_path / "test_aws_ec"
    test_dir.mkdir()
    inventory_file = "inventory" + suffix
    inventory_file = test_dir / inventory_file
    inventory_file.write_text("my inventory")
    assert result == inventory.verify_file(str(inventory_file))


def test_inventory_verify_file_with_missing_file(inventory):
    inventory_file = "this_file_does_not_exist_aws_ec.yml"
    assert not inventory.verify_file(inventory_file)


def generate_random_string(with_digits=True, with_punctuation=True, length=16):
    data = string.ascii_letters
    if with_digits:
        data += string.digits
    if with_punctuation:
        data += string.punctuation
    return "".join([random.choice(data) for i in range(length)])


@pytest.mark.parametrize(
    "replication_groups, cache_clusters, statuses, expected",
    [
        (
            [
                {"replication_group": "rg1", "Status": "Available"},
                {"replication_group": "rg2", "Status": "Creating"},
            ],
            [
                {"host": "host1", "CacheClusterStatus": "Available", "Status": "active"},
                {"host": "host2", "CacheClusterStatus": "Creating", "Status": "active"},
                {"host": "host3", "CacheClusterStatus": "Stopped", "Status": "active"},
                {"host": "host4", "CacheClusterStatus": "Configuring", "Status": "active"},
            ],
            ["Available"],
            [
                {"replication_group": "rg1", "Status": "Available"},
                {"host": "host1", "CacheClusterStatus": "Available", "Status": "active"},
            ],
        ),
        (
            [
                {"replication_group": "rg1", "Status": "Available"},
                {"replication_group": "rg2", "Status": "Creating"},
            ],
            [
                {"host": "host1", "CacheClusterStatus": "Available", "Status": "active"},
                {"host": "host2", "CacheClusterStatus": "Creating", "Status": "active"},
                {"host": "host3", "CacheClusterStatus": "Stopped", "Status": "active"},
                {"host": "host4", "CacheClusterStatus": "Configuring", "Status": "active"},
            ],
            ["all"],
            [
                {"replication_group": "rg1", "Status": "Available"},
                {"replication_group": "rg2", "Status": "Creating"},
                {"host": "host1", "CacheClusterStatus": "Available", "Status": "active"},
                {"host": "host2", "CacheClusterStatus": "Creating", "Status": "active"},
                {"host": "host3", "CacheClusterStatus": "Stopped", "Status": "active"},
                {"host": "host4", "CacheClusterStatus": "Configuring", "Status": "active"},
            ],
        ),
        (
            [
                {"replication_group": "rg1", "Status": "Available"},
                {"replication_group": "rg2", "Status": "Creating"},
            ],
            [
                {"host": "host1", "CacheClusterStatus": "Available", "Status": "active"},
                {"host": "host2", "CacheClusterStatus": "Creating", "Status": "Available"},
                {"host": "host3", "CacheClusterStatus": "Stopped", "Status": "active"},
                {"host": "host4", "CacheClusterStatus": "Configuring", "Status": "active"},
            ],
            ["Available"],
            [
                {"replication_group": "rg1", "Status": "Available"},
                {"host": "host1", "CacheClusterStatus": "Available", "Status": "active"},
                {"host": "host2", "CacheClusterStatus": "Creating", "Status": "Available"},
            ],
        ),
    ],
)
def test_find_ec_clusters_with_valid_statuses(replication_groups, cache_clusters, statuses, expected):
    expected == _find_ec_clusters_with_valid_statuses(replication_groups, cache_clusters, statuses)



import pytest
from unittest.mock import MagicMock

@pytest.mark.parametrize("length", range(0, 10, 2))
def test_inventory_populate(inventory, length):
    cluster_group_name = "cluster_group"
    replication_group_name = "replication_group"
    
    replication_groups = [f"replication_group_{int(i)}" for i in range(length)]
    cache_clusters = [f"cache_cluster_{int(i)}" for i in range(length)]

    inventory._add_hosts = MagicMock()
    inventory.inventory.add_group = MagicMock()
    inventory.inventory.add_child = MagicMock()
    
    inventory._populate(replication_groups=replication_groups, cache_clusters=cache_clusters)

    if len(replication_groups) == 0 and len(cache_clusters) == 0:
        inventory._add_hosts.assert_not_called()
        inventory.inventory.add_child.assert_not_called()
    else:
        if replication_groups:
            inventory._add_hosts.assert_any_call(hosts=replication_groups, group=replication_group_name)
            inventory.inventory.add_child.assert_any_call("all", replication_group_name)
        if cache_clusters:
            inventory._add_hosts.assert_any_call(hosts=cache_clusters, group=cluster_group_name)
            inventory.inventory.add_child.assert_any_call("all", cluster_group_name)


def test_inventory_populate_from_source(inventory):
    source_data = {
        "_meta": {
            "hostvars": {
                "host_1_0": {"var10": "value10"},
                "host_2": {"var2": "value2"},
                "host_3": {"var3": ["value30", "value31", "value32"]},
            }
        },
        "all": {"hosts": ["host_1_0", "host_1_1", "host_2", "host_3"]},
        "aws_host_1": {"hosts": ["host_1_0", "host_1_1"]},
        "aws_host_2": {"hosts": ["host_2"]},
        "aws_host_3": {"hosts": ["host_3"]},
    }

    inventory._populate_from_source(source_data)
    inventory.inventory.add_group.assert_has_calls(
        [
            call("aws_host_1"),
            call("aws_host_2"),
            call("aws_host_3"),
        ],
        any_order=True,
    )
    inventory.inventory.add_child.assert_has_calls(
        [
            call("all", "aws_host_1"),
            call("all", "aws_host_2"),
            call("all", "aws_host_3"),
        ],
        any_order=True,
    )

    inventory._populate_host_vars.assert_has_calls(
        [
            call(["host_1_0"], {"var10": "value10"}, "aws_host_1"),
            call(["host_1_1"], {}, "aws_host_1"),
            call(["host_2"], {"var2": "value2"}, "aws_host_2"),
            call(["host_3"], {"var3": ["value30", "value31", "value32"]}, "aws_host_3"),
        ],
        any_order=True,
    )


@pytest.mark.parametrize("strict", [True, False])
def test_add_tags_for_ec_clusters_with_no_hosts(connection, strict):
    hosts = []

    _add_tags_for_ec_clusters(connection, hosts, strict)
    connection.list_tags_for_resource.assert_not_called()


def test_add_tags_for_ec_hosts_with_hosts(connection):
    hosts = [
        {'ReplicationGroupId': 'exemple-001', 'ARN': 'ARN_test'},
    ]

    ec_hosts_tags = {
        "ARN_test": {"TagList": ["tag1=ARN_test", "phase=units"]},
    }
    connection.list_tags_for_resource.side_effect = lambda **kwargs: ec_hosts_tags.get(kwargs.get("ResourceName"))

    _add_tags_for_ec_clusters(connection, hosts, strict=False)

    assert hosts == [
        {'ReplicationGroupId': 'exemple-001', 'ARN': 'ARN_test', 'Tags': ["tag1=ARN_test", "phase=units"]},
    ]

def test_add_tags_for_ec_clusters_with_failure_not_strict(connection):
    hosts = [{"ReplicationGroupId": "cachearn1",'ARN': 'ARN_test'}]

    connection.list_tags_for_resource.side_effect = make_clienterror_exception()

    _add_tags_for_ec_clusters(connection, hosts, strict=False)

    assert hosts == [
        {"ReplicationGroupId": "cachearn1",'ARN': 'ARN_test', "Tags": []},
    ]


def test_add_tags_for_ec_clusters_with_failure_strict(connection):
    hosts = [{"ReplicationGroupId": "cachearn1",'ARN': 'ARN_test',}]

    connection.list_tags_for_resource.side_effect = make_clienterror_exception()

    with pytest.raises(botocore.exceptions.ClientError):
        _add_tags_for_ec_clusters(connection, hosts, strict=True)


ADD_TAGS_FOR_EC_HOSTS = "ansible_collections.amazon.aws.plugins.inventory.aws_ec._add_tags_for_ec_clusters"


@patch(ADD_TAGS_FOR_EC_HOSTS)
def test_describe_replication_groups(add_tags_for_ec_clusters, connection):
    replication_group = {
        "ReplicationGroupId": "my_sample_cache",
        "CacheClusterStatus": "Stopped",
        "ReplicationGroupId": "replication_id_01",
        "CacheClusterArn": "arn:xxx:xxxx",
        "DeletionProtection": True,
    }

    mock_paginator = MagicMock()
    mock_paginator.paginate().build_full_result.return_value = {"ReplicationGroups": [replication_group]}
    connection.get_paginator.return_value = mock_paginator

    filters = generate_random_string(with_punctuation=False)
    strict = False

    result = _describe_replication_groups(connection=connection, strict=strict)

    assert result == [replication_group]

    add_tags_for_ec_clusters.assert_called_with(connection, result, strict)

@pytest.mark.parametrize("strict", [True, False])
@patch(ADD_TAGS_FOR_EC_HOSTS)
def test_describe_replication_groups_with_access_denied(add_tags_for_ec_clusters, connection, strict):
    paginator = MagicMock()
    paginator.paginate.side_effect = make_clienterror_exception()

    connection.get_paginator.return_value = paginator

    filters = generate_random_string(with_punctuation=False)

    if strict:
        with pytest.raises(AnsibleError):
            _describe_replication_groups(connection=connection, strict=strict)
    else:
        result = _describe_replication_groups(connection=connection, strict=strict)
        assert result == []

    add_tags_for_ec_clusters.assert_not_called()


@patch(ADD_TAGS_FOR_EC_HOSTS)
def test_describe_replication_groups_with_client_error(add_tags_for_ec_clusters, connection):
    paginator = MagicMock()
    paginator.paginate.side_effect = make_clienterror_exception(code="Unknown")

    connection.get_paginator.return_value = paginator

    filters = generate_random_string(with_punctuation=False)

    with pytest.raises(AnsibleError):
        _describe_replication_groups(connection=connection, strict=False)

    add_tags_for_ec_clusters.assert_not_called()

import pytest
import random
from unittest.mock import MagicMock, patch
from ansible_collections.amazon.aws.plugins.inventory.aws_ec import (
    _describe_replication_groups,
    _find_ec_clusters_with_valid_statuses,
    AWSInventoryBase,
)

DESCRIBE_REPLICATION_GROUPS = "ansible_collections.amazon.aws.plugins.inventory.aws_ec._describe_replication_groups"
FIND_EC_CLUSTERS_WITH_VALID_STATUSES = (
    "ansible_collections.amazon.aws.plugins.inventory.aws_ec._find_ec_clusters_with_valid_statuses"
)

BASE_INVENTORY_PARSE = "ansible_collections.amazon.aws.plugins.inventory.aws_ec.AWSInventoryBase.parse"


@pytest.mark.parametrize("include_clusters", [True, False])
@pytest.mark.parametrize("filter_replication_group_id", [True, False])
@pytest.mark.parametrize("user_cache_directive", [True, False])
@pytest.mark.parametrize("cache", [True, False])
@pytest.mark.parametrize("cache_hit", [True, False])
@patch(BASE_INVENTORY_PARSE)
def test_inventory_parse_ec(
    m_parse, inventory, include_clusters, filter_replication_group_id, user_cache_directive, cache, cache_hit
):

    inventory_data = MagicMock()
    loader = MagicMock()
    path = generate_random_string(with_punctuation=False, with_digits=False)

    
    options = {
        "regions": [f"us-east-{d}" for d in range(1, 3)],
        "strict_permissions": random.choice((True, False)),
        "statuses": ["available", "creating"],
    }
    inventory.get_option.side_effect = lambda opt: options.get(opt)

   
    cache_key = path + generate_random_string()
    inventory.get_cache_key.return_value = cache_key
    cached_data = generate_random_string()
    if cache_hit:
        inventory._cache[cache_key] = cached_data

    inventory._populate = MagicMock()
    inventory._populate_from_source = MagicMock()
    inventory._get_all_replication_groups = MagicMock()
    inventory._get_all_cache_clusters = MagicMock()
    inventory._format_inventory = MagicMock()
    inventory.get_cached_result = MagicMock(return_value=(cache_hit, cached_data if cache_hit else None))
    inventory.update_cached_result = MagicMock()

    mock_replication_groups = [{"host": f"host_{random.randint(1, 1000)}"} for _ in range(4)]
    inventory._get_all_replication_groups.return_value = mock_replication_groups
    formatted_inventory_rg = f"formatted_inventory_{mock_replication_groups}"
    inventory._format_inventory.return_value = formatted_inventory_rg

    mock_cache_clusters = [{"host": f"host_{random.randint(1, 1000)}"} for _ in range(4)]
    inventory._get_all_cache_clusters.return_value = mock_cache_clusters
    formatted_inventory_cc = f"formatted_inventory_{mock_cache_clusters}"
    inventory._format_inventory.return_value = formatted_inventory_cc
    
    inventory.parse(inventory_data, loader, path, cache)
    m_parse.assert_called_with(inventory_data, loader, path, cache=cache)

    if cache_hit:
        inventory._get_all_replication_groups.assert_not_called()
        inventory._get_all_cache_clusters.assert_not_called()
        inventory._populate.assert_not_called()
        inventory._format_inventory.assert_not_called()
        inventory._populate_from_source.assert_called_with(cached_data)
    else:
        inventory._get_all_replication_groups.assert_called_with(
            regions=options["regions"],
            strict=options["strict_permissions"],
            statuses=options["statuses"],
        )
        inventory._get_all_cache_clusters.assert_called_with(
            regions=options["regions"],
            strict=options["strict_permissions"],
            statuses=options["statuses"],
        )