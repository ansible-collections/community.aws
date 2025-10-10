# -*- coding: utf-8 -*-

# Copyright: (c) 2025, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest.mock import MagicMock

import pytest
from botocore.exceptions import ClientError

from ansible.errors import AnsibleError

from ansible_collections.community.aws.plugins.lookup.dynamodb_query import LookupModule


@pytest.fixture(name="lookup_plugin")
def fixture_lookup_plugin():
    """Create a lookup plugin instance with mocked dependencies."""
    lookup = LookupModule()
    lookup.params = {}

    lookup.get_option = MagicMock()

    def _get_option(x):
        return lookup.params.get(x)

    lookup.get_option.side_effect = _get_option
    lookup.client = MagicMock()

    return lookup


def _create_dynamodb_item(attributes):
    """Helper to create DynamoDB formatted items."""
    item = {}
    for key, value in attributes.items():
        if isinstance(value, str):
            item[key] = {"S": value}
        elif isinstance(value, (int, float)):
            item[key] = {"N": str(value)}
        elif isinstance(value, bool):
            item[key] = {"BOOL": value}
        elif value is None:
            item[key] = {"NULL": True}
    return item


def _create_client_error(code, message):
    """Helper to create boto3 ClientError."""
    return ClientError(
        {
            "Error": {"Code": code, "Message": message},
            "ResponseMetadata": {"RequestId": "test-request-id"},
        },
        "Query",
    )


class TestLookupModuleBasicQuery:
    """Test basic query operations."""

    def test_query_with_partition_key_only(self, lookup_plugin, mocker):
        """Test simple query with only partition key."""
        aws_lookup_base_run = mocker.patch(
            "ansible_collections.community.aws.plugins.lookup.dynamodb_query.AWSLookupBase.run"
        )
        aws_lookup_base_run.return_value = True

        # Mock DynamoDB response
        mock_client = MagicMock()
        mock_client.query.return_value = {
            "Items": [
                _create_dynamodb_item({"id": "123", "name": "Test User"}),
                _create_dynamodb_item({"id": "124", "name": "Another User"}),
            ],
            "Count": 2,
        }
        mock_client.meta.region_name = "us-east-1"

        lookup_plugin.client = MagicMock(return_value=mock_client)
        lookup_plugin.params = {
            "table_name": "Users",
            "partition_key": "id",
            "partition_value": "123",
            "operation": "query",
            "scan_index_forward": True,
            "consistent_read": False,
            "return_consumed_capacity": "NONE",
        }

        result = lookup_plugin.run(terms=[], variables={})

        assert len(result) == 2
        assert result[0]["id"] == "123"
        assert result[0]["name"] == "Test User"
        assert result[1]["id"] == "124"

    def test_query_with_sort_key_eq(self, lookup_plugin, mocker):
        """Test query with partition key and sort key using EQ operator."""
        aws_lookup_base_run = mocker.patch(
            "ansible_collections.community.aws.plugins.lookup.dynamodb_query.AWSLookupBase.run"
        )
        aws_lookup_base_run.return_value = True

        mock_client = MagicMock()
        mock_client.query.return_value = {
            "Items": [
                _create_dynamodb_item({"platform": "dev", "env": "test", "status": "active"}),
            ],
            "Count": 1,
        }
        mock_client.meta.region_name = "us-east-1"

        lookup_plugin.client = MagicMock(return_value=mock_client)
        lookup_plugin.params = {
            "table_name": "Stacks",
            "partition_key": "platform",
            "partition_value": "dev",
            "sort_key": "env",
            "sort_value": "test",
            "sort_operator": "EQ",
            "operation": "query",
            "scan_index_forward": True,
            "consistent_read": False,
            "return_consumed_capacity": "NONE",
        }

        result = lookup_plugin.run(terms=[], variables={})

        assert len(result) == 1
        assert result[0]["platform"] == "dev"
        assert result[0]["env"] == "test"

        # Verify the query was called with correct KeyConditionExpression
        call_args = mock_client.query.call_args
        assert "#pk = :pkval AND #sk = :skval" in call_args[1]["KeyConditionExpression"]

    def test_query_with_sort_key_ge(self, lookup_plugin, mocker):
        """Test query with GE (greater or equal) operator."""
        aws_lookup_base_run = mocker.patch(
            "ansible_collections.community.aws.plugins.lookup.dynamodb_query.AWSLookupBase.run"
        )
        aws_lookup_base_run.return_value = True

        mock_client = MagicMock()
        mock_client.query.return_value = {
            "Items": [
                _create_dynamodb_item({"id": "1", "timestamp": "2024-01-01"}),
                _create_dynamodb_item({"id": "1", "timestamp": "2024-01-02"}),
            ],
            "Count": 2,
        }
        mock_client.meta.region_name = "us-east-1"

        lookup_plugin.client = MagicMock(return_value=mock_client)
        lookup_plugin.params = {
            "table_name": "Events",
            "partition_key": "id",
            "partition_value": "1",
            "sort_key": "timestamp",
            "sort_value": "2024-01-01",
            "sort_operator": "GE",
            "operation": "query",
            "scan_index_forward": True,
            "consistent_read": False,
            "return_consumed_capacity": "NONE",
        }

        result = lookup_plugin.run(terms=[], variables={})

        assert len(result) == 2

        # Verify >= operator was used
        call_args = mock_client.query.call_args
        assert "#sk >= :skval" in call_args[1]["KeyConditionExpression"]

    def test_query_with_begins_with(self, lookup_plugin, mocker):
        """Test query with BEGINS_WITH operator."""
        aws_lookup_base_run = mocker.patch(
            "ansible_collections.community.aws.plugins.lookup.dynamodb_query.AWSLookupBase.run"
        )
        aws_lookup_base_run.return_value = True

        mock_client = MagicMock()
        mock_client.query.return_value = {
            "Items": [
                _create_dynamodb_item({"id": "1", "name": "prefix_item1"}),
                _create_dynamodb_item({"id": "1", "name": "prefix_item2"}),
            ],
            "Count": 2,
        }
        mock_client.meta.region_name = "us-east-1"

        lookup_plugin.client = MagicMock(return_value=mock_client)
        lookup_plugin.params = {
            "table_name": "Items",
            "partition_key": "id",
            "partition_value": "1",
            "sort_key": "name",
            "sort_value": "prefix",
            "sort_operator": "BEGINS_WITH",
            "operation": "query",
            "scan_index_forward": True,
            "consistent_read": False,
            "return_consumed_capacity": "NONE",
        }

        result = lookup_plugin.run(terms=[], variables={})

        assert len(result) == 2

        # Verify begins_with function was used
        call_args = mock_client.query.call_args
        assert "begins_with(#sk, :skval)" in call_args[1]["KeyConditionExpression"]


class TestLookupModuleProjection:
    """Test projection expression functionality."""

    def test_projection_expression_as_string(self, lookup_plugin, mocker):
        """Test projection expression as comma-separated string."""
        aws_lookup_base_run = mocker.patch(
            "ansible_collections.community.aws.plugins.lookup.dynamodb_query.AWSLookupBase.run"
        )
        aws_lookup_base_run.return_value = True

        mock_client = MagicMock()
        mock_client.query.return_value = {
            "Items": [
                _create_dynamodb_item({"id": "1", "name": "Test"}),
            ],
            "Count": 1,
        }
        mock_client.meta.region_name = "us-east-1"

        lookup_plugin.client = MagicMock(return_value=mock_client)
        lookup_plugin.params = {
            "table_name": "Users",
            "partition_key": "id",
            "partition_value": "1",
            "projection_expression": "id,name,email",
            "operation": "query",
            "scan_index_forward": True,
            "consistent_read": False,
            "return_consumed_capacity": "NONE",
        }

        result = lookup_plugin.run(terms=[], variables={})

        assert len(result) == 1

        # Verify projection expression was passed
        call_args = mock_client.query.call_args
        assert call_args[1]["ProjectionExpression"] == "id,name,email"

    def test_projection_expression_as_list(self, lookup_plugin, mocker):
        """Test projection expression as list (should be converted to string)."""
        aws_lookup_base_run = mocker.patch(
            "ansible_collections.community.aws.plugins.lookup.dynamodb_query.AWSLookupBase.run"
        )
        aws_lookup_base_run.return_value = True

        mock_client = MagicMock()
        mock_client.query.return_value = {
            "Items": [
                _create_dynamodb_item({"id": "1", "name": "Test"}),
            ],
            "Count": 1,
        }
        mock_client.meta.region_name = "us-east-1"

        lookup_plugin.client = MagicMock(return_value=mock_client)
        lookup_plugin.params = {
            "table_name": "Users",
            "partition_key": "id",
            "partition_value": "1",
            "projection_expression": ["id", "name", "email"],
            "operation": "query",
            "scan_index_forward": True,
            "consistent_read": False,
            "return_consumed_capacity": "NONE",
        }

        result = lookup_plugin.run(terms=[], variables={})

        assert len(result) == 1

        # Verify list was converted to comma-separated string
        call_args = mock_client.query.call_args
        assert call_args[1]["ProjectionExpression"] == "id,name,email"


class TestLookupModuleScan:
    """Test scan operation."""

    def test_scan_operation(self, lookup_plugin, mocker):
        """Test scan operation."""
        aws_lookup_base_run = mocker.patch(
            "ansible_collections.community.aws.plugins.lookup.dynamodb_query.AWSLookupBase.run"
        )
        aws_lookup_base_run.return_value = True

        mock_client = MagicMock()
        mock_client.scan.return_value = {
            "Items": [
                _create_dynamodb_item({"id": "1", "name": "Item1"}),
                _create_dynamodb_item({"id": "2", "name": "Item2"}),
            ],
            "Count": 2,
        }
        mock_client.meta.region_name = "us-east-1"

        lookup_plugin.client = MagicMock(return_value=mock_client)
        lookup_plugin.params = {
            "table_name": "Items",
            "operation": "scan",
            "limit": 10,
            "consistent_read": False,
            "return_consumed_capacity": "NONE",
        }

        result = lookup_plugin.run(terms=[], variables={})

        assert len(result) == 2
        assert result[0]["id"] == "1"
        assert result[1]["id"] == "2"

        # Verify scan was called
        mock_client.scan.assert_called_once()


class TestLookupModulePagination:
    """Test pagination handling."""

    def test_query_with_pagination(self, lookup_plugin, mocker):
        """Test that pagination is handled correctly."""
        aws_lookup_base_run = mocker.patch(
            "ansible_collections.community.aws.plugins.lookup.dynamodb_query.AWSLookupBase.run"
        )
        aws_lookup_base_run.return_value = True

        mock_client = MagicMock()

        # First page
        first_response = {
            "Items": [
                _create_dynamodb_item({"id": "1", "name": "Item1"}),
            ],
            "Count": 1,
            "LastEvaluatedKey": {"id": {"S": "1"}},
        }

        # Second page
        second_response = {
            "Items": [
                _create_dynamodb_item({"id": "2", "name": "Item2"}),
            ],
            "Count": 1,
        }

        mock_client.query.side_effect = [first_response, second_response]
        mock_client.meta.region_name = "us-east-1"

        lookup_plugin.client = MagicMock(return_value=mock_client)
        lookup_plugin.params = {
            "table_name": "Items",
            "partition_key": "category",
            "partition_value": "books",
            "operation": "query",
            "scan_index_forward": True,
            "consistent_read": False,
            "return_consumed_capacity": "NONE",
        }

        result = lookup_plugin.run(terms=[], variables={})

        # Should have items from both pages
        assert len(result) == 2
        assert result[0]["id"] == "1"
        assert result[1]["id"] == "2"

        # Verify query was called twice
        assert mock_client.query.call_count == 2


class TestLookupModuleErrors:
    """Test error handling."""

    def test_table_not_found(self, lookup_plugin, mocker):
        """Test ResourceNotFoundException handling."""
        aws_lookup_base_run = mocker.patch(
            "ansible_collections.community.aws.plugins.lookup.dynamodb_query.AWSLookupBase.run"
        )
        aws_lookup_base_run.return_value = True

        mock_client = MagicMock()
        mock_client.query.side_effect = _create_client_error(
            "ResourceNotFoundException", "Requested resource not found"
        )
        mock_client.meta.region_name = "us-east-1"

        lookup_plugin.client = MagicMock(return_value=mock_client)
        lookup_plugin.params = {
            "table_name": "NonExistentTable",
            "partition_key": "id",
            "partition_value": "1",
            "operation": "query",
            "scan_index_forward": True,
            "consistent_read": False,
            "return_consumed_capacity": "NONE",
        }

        with pytest.raises(AnsibleError) as exc_info:
            lookup_plugin.run(terms=[], variables={})

        assert "not found" in str(exc_info.value).lower()

    def test_validation_exception(self, lookup_plugin, mocker):
        """Test ValidationException handling."""
        aws_lookup_base_run = mocker.patch(
            "ansible_collections.community.aws.plugins.lookup.dynamodb_query.AWSLookupBase.run"
        )
        aws_lookup_base_run.return_value = True

        mock_client = MagicMock()
        mock_client.query.side_effect = _create_client_error(
            "ValidationException", "Invalid key condition expression"
        )
        mock_client.meta.region_name = "us-east-1"

        lookup_plugin.client = MagicMock(return_value=mock_client)
        lookup_plugin.params = {
            "table_name": "Users",
            "partition_key": "id",
            "partition_value": "1",
            "operation": "query",
            "scan_index_forward": True,
            "consistent_read": False,
            "return_consumed_capacity": "NONE",
        }

        with pytest.raises(AnsibleError) as exc_info:
            lookup_plugin.run(terms=[], variables={})

        assert "Invalid DynamoDB query parameters" in str(exc_info.value)

    def test_missing_table_name(self, lookup_plugin, mocker):
        """Test error when table_name is not provided."""
        aws_lookup_base_run = mocker.patch(
            "ansible_collections.community.aws.plugins.lookup.dynamodb_query.AWSLookupBase.run"
        )
        aws_lookup_base_run.return_value = True

        lookup_plugin.params = {
            "partition_key": "id",
            "partition_value": "1",
            "operation": "query",
        }

        with pytest.raises(AnsibleError) as exc_info:
            lookup_plugin.run(terms=[], variables={})

        assert "table_name is required" in str(exc_info.value)

    def test_missing_partition_key_for_query(self, lookup_plugin, mocker):
        """Test error when partition_key is missing for query operation."""
        aws_lookup_base_run = mocker.patch(
            "ansible_collections.community.aws.plugins.lookup.dynamodb_query.AWSLookupBase.run"
        )
        aws_lookup_base_run.return_value = True

        lookup_plugin.params = {
            "table_name": "Users",
            "operation": "query",
            "partition_value": "1",
        }

        with pytest.raises(AnsibleError) as exc_info:
            lookup_plugin.run(terms=[], variables={})

        assert "partition_key and partition_value are required" in str(exc_info.value)


class TestLookupModuleDataTypes:
    """Test DynamoDB data type serialization and deserialization."""

    def test_deserialize_various_types(self, lookup_plugin, mocker):
        """Test deserialization of various DynamoDB types."""
        aws_lookup_base_run = mocker.patch(
            "ansible_collections.community.aws.plugins.lookup.dynamodb_query.AWSLookupBase.run"
        )
        aws_lookup_base_run.return_value = True

        mock_client = MagicMock()
        mock_client.query.return_value = {
            "Items": [
                {
                    "string_attr": {"S": "test"},
                    "number_attr": {"N": "42"},
                    "float_attr": {"N": "3.14"},
                    "bool_attr": {"BOOL": True},
                    "null_attr": {"NULL": True},
                    "list_attr": {"L": [{"S": "item1"}, {"N": "2"}]},
                    "map_attr": {"M": {"key1": {"S": "value1"}}},
                }
            ],
            "Count": 1,
        }
        mock_client.meta.region_name = "us-east-1"

        lookup_plugin.client = MagicMock(return_value=mock_client)
        lookup_plugin.params = {
            "table_name": "TestTable",
            "partition_key": "id",
            "partition_value": "1",
            "operation": "query",
            "scan_index_forward": True,
            "consistent_read": False,
            "return_consumed_capacity": "NONE",
        }

        result = lookup_plugin.run(terms=[], variables={})

        assert len(result) == 1
        item = result[0]

        # Verify type conversions
        assert item["string_attr"] == "test"
        assert item["number_attr"] == 42
        assert item["float_attr"] == 3.14
        assert item["bool_attr"] is True
        assert item["null_attr"] is None
        assert item["list_attr"] == ["item1", 2]
        assert item["map_attr"] == {"key1": "value1"}


class TestLookupModuleIndex:
    """Test secondary index queries."""

    def test_query_with_gsi(self, lookup_plugin, mocker):
        """Test query using Global Secondary Index."""
        aws_lookup_base_run = mocker.patch(
            "ansible_collections.community.aws.plugins.lookup.dynamodb_query.AWSLookupBase.run"
        )
        aws_lookup_base_run.return_value = True

        mock_client = MagicMock()
        mock_client.query.return_value = {
            "Items": [
                _create_dynamodb_item({"email": "[email protected]", "name": "John"}),
            ],
            "Count": 1,
        }
        mock_client.meta.region_name = "us-east-1"

        lookup_plugin.client = MagicMock(return_value=mock_client)
        lookup_plugin.params = {
            "table_name": "Users",
            "index_name": "email-index",
            "partition_key": "email",
            "partition_value": "[email protected]",
            "operation": "query",
            "scan_index_forward": True,
            "consistent_read": False,
            "return_consumed_capacity": "NONE",
        }

        result = lookup_plugin.run(terms=[], variables={})

        assert len(result) == 1
        assert result[0]["email"] == "[email protected]"

        # Verify IndexName was passed
        call_args = mock_client.query.call_args
        assert call_args[1]["IndexName"] == "email-index"


class TestLookupModuleSortOperators:
    """Test all sort key operators."""

    def test_query_with_sort_key_lt(self, lookup_plugin, mocker):
        """Test query with LT (less than) operator."""
        aws_lookup_base_run = mocker.patch(
            "ansible_collections.community.aws.plugins.lookup.dynamodb_query.AWSLookupBase.run"
        )
        aws_lookup_base_run.return_value = True

        mock_client = MagicMock()
        mock_client.query.return_value = {
            "Items": [
                _create_dynamodb_item({"id": "1", "timestamp": "2024-01-01"}),
            ],
            "Count": 1,
        }
        mock_client.meta.region_name = "us-east-1"

        lookup_plugin.client = MagicMock(return_value=mock_client)
        lookup_plugin.params = {
            "table_name": "Events",
            "partition_key": "id",
            "partition_value": "1",
            "sort_key": "timestamp",
            "sort_value": "2024-01-05",
            "sort_operator": "LT",
            "operation": "query",
            "scan_index_forward": True,
            "consistent_read": False,
            "return_consumed_capacity": "NONE",
        }

        result = lookup_plugin.run(terms=[], variables={})

        assert len(result) == 1

        # Verify < operator was used
        call_args = mock_client.query.call_args
        assert "#sk < :skval" in call_args[1]["KeyConditionExpression"]

    def test_query_with_sort_key_le(self, lookup_plugin, mocker):
        """Test query with LE (less than or equal) operator."""
        aws_lookup_base_run = mocker.patch(
            "ansible_collections.community.aws.plugins.lookup.dynamodb_query.AWSLookupBase.run"
        )
        aws_lookup_base_run.return_value = True

        mock_client = MagicMock()
        mock_client.query.return_value = {
            "Items": [
                _create_dynamodb_item({"id": "1", "timestamp": "2024-01-01"}),
                _create_dynamodb_item({"id": "1", "timestamp": "2024-01-05"}),
            ],
            "Count": 2,
        }
        mock_client.meta.region_name = "us-east-1"

        lookup_plugin.client = MagicMock(return_value=mock_client)
        lookup_plugin.params = {
            "table_name": "Events",
            "partition_key": "id",
            "partition_value": "1",
            "sort_key": "timestamp",
            "sort_value": "2024-01-05",
            "sort_operator": "LE",
            "operation": "query",
            "scan_index_forward": True,
            "consistent_read": False,
            "return_consumed_capacity": "NONE",
        }

        result = lookup_plugin.run(terms=[], variables={})

        assert len(result) == 2

        # Verify <= operator was used
        call_args = mock_client.query.call_args
        assert "#sk <= :skval" in call_args[1]["KeyConditionExpression"]

    def test_query_with_sort_key_gt(self, lookup_plugin, mocker):
        """Test query with GT (greater than) operator."""
        aws_lookup_base_run = mocker.patch(
            "ansible_collections.community.aws.plugins.lookup.dynamodb_query.AWSLookupBase.run"
        )
        aws_lookup_base_run.return_value = True

        mock_client = MagicMock()
        mock_client.query.return_value = {
            "Items": [
                _create_dynamodb_item({"id": "1", "timestamp": "2024-01-10"}),
            ],
            "Count": 1,
        }
        mock_client.meta.region_name = "us-east-1"

        lookup_plugin.client = MagicMock(return_value=mock_client)
        lookup_plugin.params = {
            "table_name": "Events",
            "partition_key": "id",
            "partition_value": "1",
            "sort_key": "timestamp",
            "sort_value": "2024-01-05",
            "sort_operator": "GT",
            "operation": "query",
            "scan_index_forward": True,
            "consistent_read": False,
            "return_consumed_capacity": "NONE",
        }

        result = lookup_plugin.run(terms=[], variables={})

        assert len(result) == 1

        # Verify > operator was used
        call_args = mock_client.query.call_args
        assert "#sk > :skval" in call_args[1]["KeyConditionExpression"]

    def test_query_with_between_operator(self, lookup_plugin, mocker):
        """Test query with BETWEEN operator."""
        aws_lookup_base_run = mocker.patch(
            "ansible_collections.community.aws.plugins.lookup.dynamodb_query.AWSLookupBase.run"
        )
        aws_lookup_base_run.return_value = True

        mock_client = MagicMock()
        mock_client.query.return_value = {
            "Items": [
                _create_dynamodb_item({"id": "1", "timestamp": "2024-01-02"}),
                _create_dynamodb_item({"id": "1", "timestamp": "2024-01-03"}),
                _create_dynamodb_item({"id": "1", "timestamp": "2024-01-04"}),
            ],
            "Count": 3,
        }
        mock_client.meta.region_name = "us-east-1"

        lookup_plugin.client = MagicMock(return_value=mock_client)
        lookup_plugin.params = {
            "table_name": "Events",
            "partition_key": "id",
            "partition_value": "1",
            "sort_key": "timestamp",
            "sort_value": "2024-01-01,2024-01-05",  # Two values separated by comma
            "sort_operator": "BETWEEN",
            "operation": "query",
            "scan_index_forward": True,
            "consistent_read": False,
            "return_consumed_capacity": "NONE",
        }

        result = lookup_plugin.run(terms=[], variables={})

        assert len(result) == 3

        # Verify BETWEEN syntax was used
        call_args = mock_client.query.call_args
        assert "#sk BETWEEN :skval1 AND :skval2" in call_args[1]["KeyConditionExpression"]

    def test_query_with_between_invalid_format(self, lookup_plugin, mocker):
        """Test that BETWEEN with single value raises error."""
        aws_lookup_base_run = mocker.patch(
            "ansible_collections.community.aws.plugins.lookup.dynamodb_query.AWSLookupBase.run"
        )
        aws_lookup_base_run.return_value = True

        lookup_plugin.params = {
            "table_name": "Events",
            "partition_key": "id",
            "partition_value": "1",
            "sort_key": "timestamp",
            "sort_value": "2024-01-01",  # Missing second value
            "sort_operator": "BETWEEN",
            "operation": "query",
            "scan_index_forward": True,
            "consistent_read": False,
            "return_consumed_capacity": "NONE",
        }

        with pytest.raises(AnsibleError) as exc_info:
            lookup_plugin.run(terms=[], variables={})

        assert "two values" in str(exc_info.value).lower()


class TestLookupModuleFilterExpressions:
    """Test filter expression functionality."""

    def test_query_with_filter_expression(self, lookup_plugin, mocker):
        """Test query with filter expression."""
        aws_lookup_base_run = mocker.patch(
            "ansible_collections.community.aws.plugins.lookup.dynamodb_query.AWSLookupBase.run"
        )
        aws_lookup_base_run.return_value = True

        mock_client = MagicMock()
        mock_client.query.return_value = {
            "Items": [
                _create_dynamodb_item({"id": "1", "status": "active", "name": "Item1"}),
            ],
            "Count": 1,
        }
        mock_client.meta.region_name = "us-east-1"

        lookup_plugin.client = MagicMock(return_value=mock_client)
        lookup_plugin.params = {
            "table_name": "Items",
            "partition_key": "id",
            "partition_value": "1",
            "filter_expression": "attribute_exists(#status)",
            "expression_attribute_names": {"#status": "status"},
            "operation": "query",
            "scan_index_forward": True,
            "consistent_read": False,
            "return_consumed_capacity": "NONE",
        }

        result = lookup_plugin.run(terms=[], variables={})

        assert len(result) == 1

        # Verify filter expression was passed
        call_args = mock_client.query.call_args
        assert call_args[1]["FilterExpression"] == "attribute_exists(#status)"
        assert "#status" in call_args[1]["ExpressionAttributeNames"]
        assert call_args[1]["ExpressionAttributeNames"]["#status"] == "status"

    def test_query_with_expression_attribute_values(self, lookup_plugin, mocker):
        """Test query with expression attribute values."""
        aws_lookup_base_run = mocker.patch(
            "ansible_collections.community.aws.plugins.lookup.dynamodb_query.AWSLookupBase.run"
        )
        aws_lookup_base_run.return_value = True

        mock_client = MagicMock()
        mock_client.query.return_value = {
            "Items": [
                _create_dynamodb_item({"id": "1", "status": "active", "count": 5}),
            ],
            "Count": 1,
        }
        mock_client.meta.region_name = "us-east-1"

        lookup_plugin.client = MagicMock(return_value=mock_client)
        lookup_plugin.params = {
            "table_name": "Items",
            "partition_key": "id",
            "partition_value": "1",
            "filter_expression": "#s = :status AND #c > :min_count",
            "expression_attribute_names": {"#s": "status", "#c": "count"},
            "expression_attribute_values": {":status": "active", ":min_count": 3},
            "operation": "query",
            "scan_index_forward": True,
            "consistent_read": False,
            "return_consumed_capacity": "NONE",
        }

        result = lookup_plugin.run(terms=[], variables={})

        assert len(result) == 1

        # Verify expression attribute values were serialized and passed
        call_args = mock_client.query.call_args
        assert ":status" in call_args[1]["ExpressionAttributeValues"]
        assert ":min_count" in call_args[1]["ExpressionAttributeValues"]
        # Values should be serialized to DynamoDB format
        assert call_args[1]["ExpressionAttributeValues"][":status"] == {"S": "active"}
        assert call_args[1]["ExpressionAttributeValues"][":min_count"] == {"N": "3"}

    def test_scan_with_filter_expression(self, lookup_plugin, mocker):
        """Test scan with filter expression."""
        aws_lookup_base_run = mocker.patch(
            "ansible_collections.community.aws.plugins.lookup.dynamodb_query.AWSLookupBase.run"
        )
        aws_lookup_base_run.return_value = True

        mock_client = MagicMock()
        mock_client.scan.return_value = {
            "Items": [
                _create_dynamodb_item({"id": "1", "status": "active"}),
                _create_dynamodb_item({"id": "2", "status": "active"}),
            ],
            "Count": 2,
        }
        mock_client.meta.region_name = "us-east-1"

        lookup_plugin.client = MagicMock(return_value=mock_client)
        lookup_plugin.params = {
            "table_name": "Items",
            "operation": "scan",
            "filter_expression": "#s = :status",
            "expression_attribute_names": {"#s": "status"},
            "expression_attribute_values": {":status": "active"},
            "consistent_read": False,
            "return_consumed_capacity": "NONE",
        }

        result = lookup_plugin.run(terms=[], variables={})

        assert len(result) == 2

        # Verify filter was applied to scan
        call_args = mock_client.scan.call_args
        assert call_args[1]["FilterExpression"] == "#s = :status"


class TestLookupModuleSetTypes:
    """Test DynamoDB Set type deserialization."""

    def test_deserialize_string_set(self, lookup_plugin, mocker):
        """Test deserialization of String Set (SS)."""
        aws_lookup_base_run = mocker.patch(
            "ansible_collections.community.aws.plugins.lookup.dynamodb_query.AWSLookupBase.run"
        )
        aws_lookup_base_run.return_value = True

        mock_client = MagicMock()
        mock_client.query.return_value = {
            "Items": [
                {
                    "id": {"S": "1"},
                    "tags": {"SS": ["production", "critical", "web"]},
                }
            ],
            "Count": 1,
        }
        mock_client.meta.region_name = "us-east-1"

        lookup_plugin.client = MagicMock(return_value=mock_client)
        lookup_plugin.params = {
            "table_name": "Items",
            "partition_key": "id",
            "partition_value": "1",
            "operation": "query",
            "scan_index_forward": True,
            "consistent_read": False,
            "return_consumed_capacity": "NONE",
        }

        result = lookup_plugin.run(terms=[], variables={})

        assert len(result) == 1
        assert result[0]["tags"] == ["production", "critical", "web"]

    def test_deserialize_number_set(self, lookup_plugin, mocker):
        """Test deserialization of Number Set (NS)."""
        aws_lookup_base_run = mocker.patch(
            "ansible_collections.community.aws.plugins.lookup.dynamodb_query.AWSLookupBase.run"
        )
        aws_lookup_base_run.return_value = True

        mock_client = MagicMock()
        mock_client.query.return_value = {
            "Items": [
                {
                    "id": {"S": "1"},
                    "ports": {"NS": ["80", "443", "8080"]},
                    "scores": {"NS": ["3.14", "2.71", "1.41"]},
                }
            ],
            "Count": 1,
        }
        mock_client.meta.region_name = "us-east-1"

        lookup_plugin.client = MagicMock(return_value=mock_client)
        lookup_plugin.params = {
            "table_name": "Items",
            "partition_key": "id",
            "partition_value": "1",
            "operation": "query",
            "scan_index_forward": True,
            "consistent_read": False,
            "return_consumed_capacity": "NONE",
        }

        result = lookup_plugin.run(terms=[], variables={})

        assert len(result) == 1
        # Integers should be converted to int
        assert result[0]["ports"] == [80, 443, 8080]
        # Floats should be converted to float
        assert result[0]["scores"] == [3.14, 2.71, 1.41]

    def test_deserialize_binary_set(self, lookup_plugin, mocker):
        """Test deserialization of Binary Set (BS)."""
        aws_lookup_base_run = mocker.patch(
            "ansible_collections.community.aws.plugins.lookup.dynamodb_query.AWSLookupBase.run"
        )
        aws_lookup_base_run.return_value = True

        mock_client = MagicMock()
        mock_client.query.return_value = {
            "Items": [
                {
                    "id": {"S": "1"},
                    "hashes": {"BS": [b"hash1", b"hash2", b"hash3"]},
                }
            ],
            "Count": 1,
        }
        mock_client.meta.region_name = "us-east-1"

        lookup_plugin.client = MagicMock(return_value=mock_client)
        lookup_plugin.params = {
            "table_name": "Items",
            "partition_key": "id",
            "partition_value": "1",
            "operation": "query",
            "scan_index_forward": True,
            "consistent_read": False,
            "return_consumed_capacity": "NONE",
        }

        result = lookup_plugin.run(terms=[], variables={})

        assert len(result) == 1
        assert result[0]["hashes"] == [b"hash1", b"hash2", b"hash3"]


class TestLookupModuleAdvancedParameters:
    """Test advanced query parameters."""

    def test_query_with_limit(self, lookup_plugin, mocker):
        """Test query with limit parameter."""
        aws_lookup_base_run = mocker.patch(
            "ansible_collections.community.aws.plugins.lookup.dynamodb_query.AWSLookupBase.run"
        )
        aws_lookup_base_run.return_value = True

        mock_client = MagicMock()
        # Simulate DynamoDB returning exactly 'limit' items
        mock_client.query.return_value = {
            "Items": [
                _create_dynamodb_item({"id": "1", "name": "Item1"}),
                _create_dynamodb_item({"id": "2", "name": "Item2"}),
                _create_dynamodb_item({"id": "3", "name": "Item3"}),
            ],
            "Count": 3,
        }
        mock_client.meta.region_name = "us-east-1"

        lookup_plugin.client = MagicMock(return_value=mock_client)
        lookup_plugin.params = {
            "table_name": "Items",
            "partition_key": "category",
            "partition_value": "books",
            "limit": 3,
            "operation": "query",
            "scan_index_forward": True,
            "consistent_read": False,
            "return_consumed_capacity": "NONE",
        }

        result = lookup_plugin.run(terms=[], variables={})

        assert len(result) == 3

        # Verify Limit parameter was passed to DynamoDB
        call_args = mock_client.query.call_args
        assert call_args[1]["Limit"] == 3

    def test_query_with_descending_order(self, lookup_plugin, mocker):
        """Test query with scan_index_forward=false (descending order)."""
        aws_lookup_base_run = mocker.patch(
            "ansible_collections.community.aws.plugins.lookup.dynamodb_query.AWSLookupBase.run"
        )
        aws_lookup_base_run.return_value = True

        mock_client = MagicMock()
        # Simulate items returned in descending order
        mock_client.query.return_value = {
            "Items": [
                _create_dynamodb_item({"id": "1", "timestamp": "2024-01-05"}),
                _create_dynamodb_item({"id": "1", "timestamp": "2024-01-03"}),
                _create_dynamodb_item({"id": "1", "timestamp": "2024-01-01"}),
            ],
            "Count": 3,
        }
        mock_client.meta.region_name = "us-east-1"

        lookup_plugin.client = MagicMock(return_value=mock_client)
        lookup_plugin.params = {
            "table_name": "Events",
            "partition_key": "id",
            "partition_value": "1",
            "sort_key": "timestamp",
            "scan_index_forward": False,  # Descending order
            "operation": "query",
            "consistent_read": False,
            "return_consumed_capacity": "NONE",
        }

        result = lookup_plugin.run(terms=[], variables={})

        assert len(result) == 3
        # Verify items are in descending order
        assert result[0]["timestamp"] == "2024-01-05"
        assert result[1]["timestamp"] == "2024-01-03"
        assert result[2]["timestamp"] == "2024-01-01"

        # Verify ScanIndexForward=False was passed to DynamoDB
        call_args = mock_client.query.call_args
        assert call_args[1]["ScanIndexForward"] is False

    def test_pagination_with_limit(self, lookup_plugin, mocker):
        """Test that pagination stops when limit is reached."""
        aws_lookup_base_run = mocker.patch(
            "ansible_collections.community.aws.plugins.lookup.dynamodb_query.AWSLookupBase.run"
        )
        aws_lookup_base_run.return_value = True

        mock_client = MagicMock()

        # First page: 3 items + LastEvaluatedKey
        first_response = {
            "Items": [
                _create_dynamodb_item({"id": "1", "name": "Item1"}),
                _create_dynamodb_item({"id": "2", "name": "Item2"}),
                _create_dynamodb_item({"id": "3", "name": "Item3"}),
            ],
            "Count": 3,
            "LastEvaluatedKey": {"id": {"S": "3"}},
        }

        # Second page: 2 items (should stop here because limit=5)
        second_response = {
            "Items": [
                _create_dynamodb_item({"id": "4", "name": "Item4"}),
                _create_dynamodb_item({"id": "5", "name": "Item5"}),
            ],
            "Count": 2,
            "LastEvaluatedKey": {"id": {"S": "5"}},  # More data available but we stop
        }

        mock_client.query.side_effect = [first_response, second_response]
        mock_client.meta.region_name = "us-east-1"

        lookup_plugin.client = MagicMock(return_value=mock_client)
        lookup_plugin.params = {
            "table_name": "Items",
            "partition_key": "category",
            "partition_value": "books",
            "limit": 5,  # Stop at 5 items
            "operation": "query",
            "scan_index_forward": True,
            "consistent_read": False,
            "return_consumed_capacity": "NONE",
        }

        result = lookup_plugin.run(terms=[], variables={})

        # Should stop at exactly 5 items despite more data being available
        assert len(result) == 5
        assert result[0]["id"] == "1"
        assert result[4]["id"] == "5"

        # Verify query was called twice (pagination)
        assert mock_client.query.call_count == 2
