# -*- coding: utf-8 -*-

# (c) 2025, Timur Gadiev (@tgadiev) <tgadiev@gmail.com>
# Copyright: (c) 2025, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
name: dynamodb_query
author:
  - Timur Gadiev (@tgadiev)
version_added: 11.0.0
short_description: Query AWS DynamoDB table
description:
  - This lookup plugin allows you to query AWS DynamoDB tables and retrieve items.
  - The plugin supports both Query and Scan operations.
  - Results are returned as a list of items.
options:
  table_name:
    description:
      - The name of the DynamoDB table to query.
    required: true
    type: str
  partition_key:
    description:
      - The partition key attribute name.
      - Required when using Query operation.
    type: str
  partition_value:
    description:
      - The value of the partition key to query.
      - Required when using Query operation.
    type: str
  sort_key:
    description:
      - The sort key attribute name.
      - Optional, used with Query operation.
    type: str
  sort_value:
    description:
      - The value of the sort key.
      - Optional, used with Query operation when sort_key is specified.
    type: str
  sort_operator:
    description:
      - The comparison operator for the sort key.
      - Only used when sort_key and sort_value are specified.
    type: str
    default: 'EQ'
    choices: ['EQ', 'LE', 'LT', 'GE', 'GT', 'BEGINS_WITH', 'BETWEEN']
  index_name:
    description:
      - The name of a secondary index to query.
      - If not specified, the query is performed on the table.
    type: str
  filter_expression:
    description:
      - A filter expression to apply after the query.
      - Uses DynamoDB filter expression syntax.
    type: str
  expression_attribute_names:
    description:
      - A dictionary mapping placeholder names to actual attribute names.
      - Used to reference reserved keywords or attributes with special characters.
      - Example C({'#status'{{':'}} 'status', '#name'{{':'}} 'name'})
    type: dict
  expression_attribute_values:
    description:
      - A dictionary mapping placeholder values to actual values.
      - Used with filter_expression to provide parameter values.
      - Example C({':active'{{':'}} 'active', ':min_count'{{':'}} 5})
    type: dict
  projection_expression:
    description:
      - Attributes to retrieve from the table.
      - Can be a comma-separated string (e.g., 'attr1,attr2,attr3') or a list of attribute names.
      - If not specified, all attributes are returned.
    type: raw
  limit:
    description:
      - The maximum number of items to return.
      - If not specified, DynamoDB default limit applies.
    type: int
  scan_index_forward:
    description:
      - Specifies the order for index traversal.
      - If true (default), the traversal is performed in ascending order.
      - If false, the traversal is performed in descending order.
    type: bool
    default: true
  consistent_read:
    description:
      - If true, a strongly consistent read is used.
      - If false (default), an eventually consistent read is used.
    type: bool
    default: false
  operation:
    description:
      - The DynamoDB operation to perform.
      - Use 'query' for partition key-based queries (more efficient).
      - Use 'scan' to retrieve all items (less efficient, use with caution).
    type: str
    default: 'query'
    choices: ['query', 'scan']
  return_consumed_capacity:
    description:
      - Determines the level of detail about provisioned throughput consumption.
    type: str
    choices: ['INDEXES', 'TOTAL', 'NONE']
    default: 'NONE'
  _page_size:
    description:
      - Internal parameter for testing pagination.
      - Sets the DynamoDB Limit parameter to force pagination with small datasets.
      - This is NOT documented and should only be used for testing.
    type: int
extends_documentation_fragment:
  - amazon.aws.common.plugins
  - amazon.aws.region.plugins
  - amazon.aws.boto3
"""

EXAMPLES = r"""
---
# Query items by partition key
- name: Get user by ID
  ansible.builtin.debug:
    msg: >-
      {{ lookup('community.aws.dynamodb_query', table_name='Users', partition_key='user_id', partition_value='12345') }}

# Query with sort key condition
- name: Get user orders within date range
  ansible.builtin.debug:
    msg: >-
      {{ lookup('community.aws.dynamodb_query',
                    table_name='Orders',
                    partition_key='user_id',
                    partition_value='12345',
                    sort_key='order_date',
                    sort_value='2024-01-01',
                    sort_operator='GE')
      }}

# Query using a secondary index
- name: Get items by email using GSI
  ansible.builtin.debug:
    msg: >-
      {{ lookup('community.aws.dynamodb_query',
                    table_name='Users',
                    index_name='email-index',
                    partition_key='email',
                    partition_value='[email protected]')
      }}

# Query with projection expression (retrieve specific attributes only)
# Using comma-separated string
- name: Get specific user attributes (string)
  ansible.builtin.debug:
    msg: >-
      {{ lookup('community.aws.dynamodb_query',
                    table_name='Users',
                    partition_key='user_id',
                    partition_value='12345',
                    projection_expression='user_id,name,email')
      }}

# Using list of attributes
- name: Get specific user attributes (list)
  ansible.builtin.debug:
    msg: >-
      {{ lookup('community.aws.dynamodb_query',
                    table_name='Users',
                    partition_key='user_id',
                    partition_value='12345',
                    projection_expression=['user_id', 'name', 'email'])
      }}

# Query with filter expression
- name: Get active users
  ansible.builtin.debug:
    msg: >-
      {{ lookup('community.aws.dynamodb_query',
                    table_name='Users',
                    partition_key='user_id',
                    partition_value='12345',
                    filter_expression='#status = :active',
                    expression_attribute_names={'#status': 'status'},
                    expression_attribute_values={':active': 'active'})
      }}

# Scan operation (use with caution on large tables)
- name: Scan all items in table
  ansible.builtin.debug:
    msg: >-
      {{ lookup('community.aws.dynamodb_query',
                    table_name='SmallTable',
                    operation='scan',
                    limit=100)
      }}

# Query with limit and descending order
- name: Get last 10 orders
  ansible.builtin.debug:
    msg: >-
      {{ lookup('community.aws.dynamodb_query',
                    table_name='Orders',
                    partition_key='user_id',
                    partition_value='12345',
                    limit=10,
                    scan_index_forward=false)
      }}

# Store results in a variable
- name: Query and store results
  ansible.builtin.set_fact:
    user_data: >-
      {{ lookup('community.aws.dynamodb_query',
                          table_name='Users',
                          partition_key='user_id',
                          partition_value='12345')
      }}
"""

RETURN = r"""
_list:
  description:
    - A list of items returned from the DynamoDB query or scan operation.
    - Each item is a dictionary with attribute names as keys.
  type: list
  elements: dict
"""

try:
    import botocore
except ImportError:
    pass  # Handled by AnsibleAWSPlugin

import os

from ansible.errors import AnsibleError
from ansible.module_utils._text import to_native
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display

from ansible_collections.amazon.aws.plugins.module_utils.botocore import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.retries import AWSRetry

try:
    from ansible_collections.amazon.aws.plugins.plugin_utils.lookup import AWSLookupBase

    HAS_AWS_LOOKUP_BASE = True
except ImportError:
    HAS_AWS_LOOKUP_BASE = False
    # Fallback to standard LookupBase
    AWSLookupBase = LookupBase

display = Display()


class LookupModule(AWSLookupBase):
    def run(self, terms, variables=None, **kwargs):
        """
        Execute the DynamoDB query or scan operation.

        Args:
            terms: Not used for this lookup plugin (options are passed via kwargs)
            variables: Ansible variables
            **kwargs: Plugin options

        Returns:
            list: List of items from DynamoDB
        """
        # Workaround: If AWS_PROFILE is set but profile is not in kwargs, use AWS_PROFILE
        # This ensures AWS_PROFILE environment variable works correctly
        if "profile" not in kwargs and "aws_profile" not in kwargs:
            aws_profile_env = os.environ.get("AWS_PROFILE")
            if aws_profile_env:
                kwargs["profile"] = aws_profile_env
                display.vvv(f"Using AWS_PROFILE from environment: {aws_profile_env}")

        # Call parent class run() which handles AWS SDK requirements and sets options
        if HAS_AWS_LOOKUP_BASE:
            super().run(terms, variables, **kwargs)
        else:
            # Fallback if AWSLookupBase is not available
            self.set_options(var_options=variables, direct=kwargs)

        # Get plugin options
        table_name = self.get_option("table_name")
        operation = self.get_option("operation")
        partition_key = self.get_option("partition_key")
        partition_value = self.get_option("partition_value")
        sort_key = self.get_option("sort_key")
        sort_value = self.get_option("sort_value")
        sort_operator = self.get_option("sort_operator")
        index_name = self.get_option("index_name")
        filter_expression = self.get_option("filter_expression")
        expression_attribute_names = self.get_option("expression_attribute_names")
        expression_attribute_values = self.get_option("expression_attribute_values")
        projection_expression = self.get_option("projection_expression")
        limit = self.get_option("limit")
        scan_index_forward = self.get_option("scan_index_forward")
        consistent_read = self.get_option("consistent_read")
        return_consumed_capacity = self.get_option("return_consumed_capacity")
        page_size = self.get_option("_page_size")  # Internal testing parameter

        # Convert projection_expression from list to comma-separated string if needed
        if projection_expression and isinstance(projection_expression, list):
            projection_expression = ",".join(projection_expression)
            display.vvv(f"Converted projection_expression list to string: {projection_expression}")

        if not table_name:
            raise AnsibleError("table_name is required for dynamodb_query lookup")

        # Validate query operation parameters
        if operation == "query":
            if not partition_key or not partition_value:
                raise AnsibleError("partition_key and partition_value are required when operation is 'query'")

        # Create DynamoDB client
        retry_decorator = AWSRetry.jittered_backoff(
            catch_extra_error_codes=["ProvisionedThroughputExceededException", "RequestLimitExceeded"]
        )

        if not HAS_AWS_LOOKUP_BASE:
            raise AnsibleError(
                "The dynamodb_query lookup plugin requires amazon.aws collection version 8.2.0 or later "
                "(for AWSLookupBase support). Please upgrade the amazon.aws collection."
            )

        client = self.client("dynamodb", retry_decorator=retry_decorator)

        # Debug output
        display.vvv(f"DynamoDB client created for region: {client.meta.region_name}")
        display.vvv(f"Querying table: {table_name}, operation: {operation}")

        try:
            if operation == "query":
                items = self._execute_query(
                    client,
                    table_name,
                    partition_key,
                    partition_value,
                    sort_key,
                    sort_value,
                    sort_operator,
                    index_name,
                    filter_expression,
                    expression_attribute_names,
                    expression_attribute_values,
                    projection_expression,
                    limit,
                    scan_index_forward,
                    consistent_read,
                    return_consumed_capacity,
                    page_size,
                )
            else:  # scan
                items = self._execute_scan(
                    client,
                    table_name,
                    filter_expression,
                    expression_attribute_names,
                    expression_attribute_values,
                    projection_expression,
                    limit,
                    consistent_read,
                    return_consumed_capacity,
                    page_size,
                )

            # Convert DynamoDB format to Python native types
            result = [self._deserialize_item(item) for item in items]

            display.vvv(f"DynamoDB {operation} returned {len(result)} items from table {table_name}")

            return result

        except is_boto3_error_code("ResourceNotFoundException") as e:
            error_msg = f"DynamoDB table '{table_name}' not found in region {client.meta.region_name}"
            display.vvv(f"Full error: {to_native(e)}")
            raise AnsibleError(error_msg)
        except is_boto3_error_code("ValidationException") as e:
            raise AnsibleError(f"Invalid DynamoDB query parameters: {to_native(e)}")
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            display.vvv(f"AWS Error details: {to_native(e)}")
            raise AnsibleError(f"Failed to query DynamoDB: {to_native(e)}")

    def _execute_query(
        self,
        client,
        table_name,
        partition_key,
        partition_value,
        sort_key,
        sort_value,
        sort_operator,
        index_name,
        filter_expression,
        expression_attribute_names,
        expression_attribute_values,
        projection_expression,
        limit,
        scan_index_forward,
        consistent_read,
        return_consumed_capacity,
        page_size=None,
    ):
        """Execute a DynamoDB Query operation."""
        params = {
            "TableName": table_name,
            "ScanIndexForward": scan_index_forward,
            "ConsistentRead": consistent_read,
            "ReturnConsumedCapacity": return_consumed_capacity,
        }

        # Build key condition expression
        key_condition_parts = []
        key_attr_names = {}
        key_attr_values = {}

        # Partition key condition
        key_attr_names["#pk"] = partition_key
        key_attr_values[":pkval"] = self._serialize_value(partition_value)
        key_condition_parts.append("#pk = :pkval")

        # Sort key condition
        if sort_key and sort_value:
            key_attr_names["#sk"] = sort_key

            if sort_operator == "BETWEEN":
                # BETWEEN requires two values separated by comma
                values = sort_value.split(",")
                if len(values) != 2:
                    raise AnsibleError("BETWEEN operator requires two values separated by comma")
                key_attr_values[":skval1"] = self._serialize_value(values[0].strip())
                key_attr_values[":skval2"] = self._serialize_value(values[1].strip())
                key_condition_parts.append("#sk BETWEEN :skval1 AND :skval2")
            elif sort_operator == "BEGINS_WITH":
                key_attr_values[":skval"] = self._serialize_value(sort_value)
                key_condition_parts.append("begins_with(#sk, :skval)")
            else:
                # EQ, LE, LT, GE, GT - convert to DynamoDB syntax
                operator_map = {
                    "EQ": "=",
                    "LE": "<=",
                    "LT": "<",
                    "GE": ">=",
                    "GT": ">",
                }
                dynamodb_operator = operator_map.get(sort_operator, sort_operator)
                key_attr_values[":skval"] = self._serialize_value(sort_value)
                key_condition_parts.append(f"#sk {dynamodb_operator} :skval")

        params["KeyConditionExpression"] = " AND ".join(key_condition_parts)

        # Merge key condition names/values with user-provided filter expression names/values
        all_attr_names = key_attr_names.copy()
        if expression_attribute_names:
            all_attr_names.update(expression_attribute_names)

        all_attr_values = key_attr_values.copy()
        if expression_attribute_values:
            # Serialize user-provided values to DynamoDB format
            for key, value in expression_attribute_values.items():
                all_attr_values[key] = self._serialize_value(value)

        params["ExpressionAttributeNames"] = all_attr_names
        params["ExpressionAttributeValues"] = all_attr_values

        if index_name:
            params["IndexName"] = index_name

        if filter_expression:
            params["FilterExpression"] = filter_expression

        if projection_expression:
            params["ProjectionExpression"] = projection_expression

        # Set initial page size for DynamoDB Limit parameter
        # If _page_size is set (for testing), use it to force pagination
        # Otherwise, use user's limit if specified
        if page_size:
            params["Limit"] = page_size
            display.vvv(f"Using _page_size={page_size} to force pagination for testing")
        elif limit:
            params["Limit"] = limit

        display.vvv(f"DynamoDB query params: {params}")

        # Execute query with pagination
        items = []
        while True:
            response = client.query(aws_retry=True, **params)
            items.extend(response.get("Items", []))

            # Check if there are more results
            if "LastEvaluatedKey" not in response or (limit and len(items) >= limit):
                break

            params["ExclusiveStartKey"] = response["LastEvaluatedKey"]

            # Adjust limit for next page
            if page_size:
                # When using page_size for testing, keep it constant
                # but respect user's limit if specified
                if limit:
                    remaining = limit - len(items)
                    params["Limit"] = min(page_size, remaining)
                else:
                    params["Limit"] = page_size
            elif limit:
                params["Limit"] = limit - len(items)

        return items

    def _execute_scan(
        self,
        client,
        table_name,
        filter_expression,
        expression_attribute_names,
        expression_attribute_values,
        projection_expression,
        limit,
        consistent_read,
        return_consumed_capacity,
        page_size=None,
    ):
        """Execute a DynamoDB Scan operation."""
        params = {
            "TableName": table_name,
            "ConsistentRead": consistent_read,
            "ReturnConsumedCapacity": return_consumed_capacity,
        }

        if expression_attribute_names:
            params["ExpressionAttributeNames"] = expression_attribute_names

        if expression_attribute_values:
            # Serialize values to DynamoDB format
            serialized_values = {}
            for key, value in expression_attribute_values.items():
                serialized_values[key] = self._serialize_value(value)
            params["ExpressionAttributeValues"] = serialized_values

        if filter_expression:
            params["FilterExpression"] = filter_expression

        if projection_expression:
            params["ProjectionExpression"] = projection_expression

        # Set initial page size for DynamoDB Limit parameter
        if page_size:
            params["Limit"] = page_size
            display.vvv(f"Using _page_size={page_size} to force pagination for testing")
        elif limit:
            params["Limit"] = limit

        # Execute scan with pagination
        items = []
        while True:
            response = client.scan(aws_retry=True, **params)
            items.extend(response.get("Items", []))

            # Check if there are more results
            if "LastEvaluatedKey" not in response or (limit and len(items) >= limit):
                break

            params["ExclusiveStartKey"] = response["LastEvaluatedKey"]

            # Adjust limit for next page
            if page_size:
                if limit:
                    remaining = limit - len(items)
                    params["Limit"] = min(page_size, remaining)
                else:
                    params["Limit"] = page_size
            elif limit:
                params["Limit"] = limit - len(items)

        return items

    def _serialize_value(self, value):
        """
        Serialize a Python value to DynamoDB format.

        Args:
            value: Python value to serialize

        Returns:
            dict: DynamoDB formatted value
        """
        if isinstance(value, bool):
            return {"BOOL": value}
        elif isinstance(value, (int, float)):
            return {"N": str(value)}
        elif isinstance(value, str):
            return {"S": value}
        elif isinstance(value, bytes):
            return {"B": value}
        elif isinstance(value, list):
            return {"L": [self._serialize_value(v) for v in value]}
        elif isinstance(value, dict):
            return {"M": {k: self._serialize_value(v) for k, v in value.items()}}
        elif value is None:
            return {"NULL": True}
        else:
            # Default to string
            return {"S": str(value)}

    def _deserialize_item(self, item):
        """
        Deserialize a DynamoDB item to Python native types.

        Args:
            item: DynamoDB item in wire format

        Returns:
            dict: Python dictionary with native types
        """
        result = {}
        for key, value in item.items():
            result[key] = self._deserialize_value(value)
        return result

    def _deserialize_value(self, value):
        """
        Deserialize a DynamoDB value to Python native type.

        Args:
            value: DynamoDB formatted value

        Returns:
            Python native value
        """
        if "S" in value:
            return value["S"]
        elif "N" in value:
            # Try to convert to int, fall back to float
            try:
                return int(value["N"])
            except ValueError:
                return float(value["N"])
        elif "BOOL" in value:
            return value["BOOL"]
        elif "NULL" in value:
            return None
        elif "B" in value:
            return value["B"]
        elif "SS" in value:
            return value["SS"]
        elif "NS" in value:
            return [int(n) if "." not in n else float(n) for n in value["NS"]]
        elif "BS" in value:
            return value["BS"]
        elif "L" in value:
            return [self._deserialize_value(v) for v in value["L"]]
        elif "M" in value:
            return {k: self._deserialize_value(v) for k, v in value["M"].items()}
        else:
            return value
