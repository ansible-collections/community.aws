# -*- coding: utf-8 -*-

# Copyright: (c) 2025, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from ansible.errors import AnsibleError

from ansible_collections.community.aws.plugins.lookup.dynamodb_query import LookupModule


@pytest.fixture(name="lookup_plugin")
def fixture_lookup_plugin():
    """Create a lookup plugin instance with lightweight option handling."""
    lookup = LookupModule()
    lookup.params = {}

    def _get_option(option):
        return lookup.params.get(option)

    lookup.get_option = MagicMock(side_effect=_get_option)

    return lookup


@pytest.fixture(name="aws_lookup_base_run")
def fixture_aws_lookup_base_run(mocker):
    """Avoid invoking parent setup logic in unit tests."""
    return mocker.patch(
        "ansible_collections.community.aws.plugins.lookup.dynamodb_query.AWSLookupBase.run",
        return_value=True,
    )


def _set_default_params(lookup_plugin, **overrides):
    params = {
        "operation": "query",
        "scan_index_forward": True,
        "consistent_read": False,
        "return_consumed_capacity": "NONE",
    }
    params.update(overrides)
    lookup_plugin.params = params


class TestLookupModuleRun:
    """Smoke tests for run() dispatch and local normalization."""

    def test_run_query_deserializes_execute_query_results(self, lookup_plugin, aws_lookup_base_run, mocker):
        mock_client = MagicMock()
        mock_client.meta = SimpleNamespace(region_name="us-east-1")
        lookup_plugin.client = MagicMock(return_value=mock_client)

        execute_query = mocker.patch.object(
            lookup_plugin,
            "_execute_query",
            return_value=[
                {
                    "id": {"S": "123"},
                    "name": {"S": "Test User"},
                    "active": {"BOOL": True},
                }
            ],
        )

        _set_default_params(
            lookup_plugin,
            table_name="Users",
            partition_key="id",
            partition_value="123",
        )

        result = lookup_plugin.run(terms=[], variables={})

        assert result == [{"id": "123", "name": "Test User", "active": True}]
        execute_query.assert_called_once()

    def test_run_scan_deserializes_execute_scan_results(self, lookup_plugin, aws_lookup_base_run, mocker):
        mock_client = MagicMock()
        mock_client.meta = SimpleNamespace(region_name="us-east-1")
        lookup_plugin.client = MagicMock(return_value=mock_client)

        execute_scan = mocker.patch.object(
            lookup_plugin,
            "_execute_scan",
            return_value=[
                {
                    "id": {"S": "item-1"},
                    "priority": {"N": "7"},
                }
            ],
        )

        _set_default_params(
            lookup_plugin,
            operation="scan",
            table_name="Items",
        )

        result = lookup_plugin.run(terms=[], variables={})

        assert result == [{"id": "item-1", "priority": 7}]
        execute_scan.assert_called_once()

    def test_projection_expression_list_is_normalized_before_execute_query(
        self, lookup_plugin, aws_lookup_base_run, mocker
    ):
        mock_client = MagicMock()
        mock_client.meta = SimpleNamespace(region_name="us-east-1")
        lookup_plugin.client = MagicMock(return_value=mock_client)

        execute_query = mocker.patch.object(lookup_plugin, "_execute_query", return_value=[])

        _set_default_params(
            lookup_plugin,
            table_name="Users",
            partition_key="id",
            partition_value="123",
            projection_expression=["id", "name", "email"],
        )

        lookup_plugin.run(terms=[], variables={})

        assert execute_query.call_args.args[11] == "id,name,email"


class TestLookupModuleValidation:
    """Tests for validation that happens before AWS calls."""

    def test_missing_table_name(self, lookup_plugin, aws_lookup_base_run):
        _set_default_params(
            lookup_plugin,
            partition_key="id",
            partition_value="123",
        )

        with pytest.raises(AnsibleError, match="table_name is required"):
            lookup_plugin.run(terms=[], variables={})

    def test_missing_partition_key_for_query(self, lookup_plugin, aws_lookup_base_run):
        _set_default_params(
            lookup_plugin,
            table_name="Users",
            partition_value="123",
        )

        with pytest.raises(AnsibleError, match="partition_key and partition_value are required"):
            lookup_plugin.run(terms=[], variables={})

    def test_between_requires_two_values(self, lookup_plugin):
        with pytest.raises(AnsibleError, match="two values"):
            lookup_plugin._execute_query(
                client=object(),
                table_name="Events",
                partition_key="id",
                partition_value="123",
                sort_key="timestamp",
                sort_value="2024-01-01",
                sort_operator="BETWEEN",
                index_name=None,
                filter_expression=None,
                expression_attribute_names=None,
                expression_attribute_values=None,
                projection_expression=None,
                limit=None,
                scan_index_forward=True,
                consistent_read=False,
                return_consumed_capacity="NONE",
            )


class TestLookupModuleSerialization:
    """Direct tests for value serialization."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("test", {"S": "test"}),
            (42, {"N": "42"}),
            (3.14, {"N": "3.14"}),
            (True, {"BOOL": True}),
            (None, {"NULL": True}),
            (b"hash", {"B": b"hash"}),
            (["item1", 2], {"L": [{"S": "item1"}, {"N": "2"}]}),
            (
                {"name": "demo", "enabled": False},
                {"M": {"name": {"S": "demo"}, "enabled": {"BOOL": False}}},
            ),
        ],
    )
    def test_serialize_value(self, lookup_plugin, value, expected):
        assert lookup_plugin._serialize_value(value) == expected


class TestLookupModuleDeserialization:
    """Direct tests for value and item deserialization."""

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ({"S": "test"}, "test"),
            ({"N": "42"}, 42),
            ({"N": "3.14"}, 3.14),
            ({"BOOL": True}, True),
            ({"NULL": True}, None),
            ({"B": b"hash"}, b"hash"),
            ({"SS": ["production", "critical"]}, ["production", "critical"]),
            ({"NS": ["80", "443", "3.14"]}, [80, 443, 3.14]),
            ({"BS": [b"hash1", b"hash2"]}, [b"hash1", b"hash2"]),
            ({"L": [{"S": "item1"}, {"N": "2"}]}, ["item1", 2]),
            ({"M": {"key": {"S": "value"}}}, {"key": "value"}),
        ],
    )
    def test_deserialize_value(self, lookup_plugin, value, expected):
        assert lookup_plugin._deserialize_value(value) == expected

    def test_deserialize_item_nested_structure(self, lookup_plugin):
        item = {
            "id": {"S": "123"},
            "profile": {
                "M": {
                    "enabled": {"BOOL": True},
                    "tags": {"SS": ["production", "critical"]},
                    "settings": {
                        "M": {
                            "threshold": {"N": "7"},
                            "theme": {"S": "dark"},
                        }
                    },
                }
            },
            "events": {
                "L": [
                    {
                        "M": {
                            "type": {"S": "deploy"},
                            "ok": {"BOOL": False},
                        }
                    }
                ]
            },
        }

        assert lookup_plugin._deserialize_item(item) == {
            "id": "123",
            "profile": {
                "enabled": True,
                "tags": ["production", "critical"],
                "settings": {
                    "threshold": 7,
                    "theme": "dark",
                },
            },
            "events": [
                {
                    "type": "deploy",
                    "ok": False,
                }
            ],
        }
