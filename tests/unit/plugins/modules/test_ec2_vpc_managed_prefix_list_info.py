# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest.mock import MagicMock, patch

import pytest

from ansible_collections.amazon.aws.plugins.module_utils.botocore import HAS_BOTO3

if not HAS_BOTO3:
    pytestmark = pytest.mark.skip(
        "test_ec2_vpc_managed_prefix_list_info.py requires the `boto3` and `botocore` modules"
    )

from ansible_collections.community.aws.plugins.modules.ec2_vpc_managed_prefix_list_info import (
    format_prefix_list,
    get_prefix_list_entries,
    list_prefix_lists,
)
from ansible_collections.community.aws.tests.unit.plugins.modules.utils import (
    AnsibleExitJson,
    ModuleTestCase,
    set_module_args,
)

EXAMPLE_PREFIX_LIST = {
    "PrefixListId": "pl-0a1b2c3d4e5f6789a",
    "AddressFamily": "IPv4",
    "State": "create-complete",
    "StateMessage": "",
    "PrefixListArn": "arn:aws:ec2:us-east-1:123456789012:prefix-list/pl-0a1b2c3d4e5f6789a",
    "PrefixListName": "test-prefix-list",
    "MaxEntries": 10,
    "Version": 1,
    "Tags": [{"Key": "Name", "Value": "test-prefix-list"}],
}

EXAMPLE_ENTRIES = [
    {"Cidr": "10.0.0.0/24", "Description": "My subnet"},
    {"Cidr": "10.1.0.0/24", "Description": "Other subnet"},
]


def make_module(params):
    module = MagicMock()
    module.params = params
    return module


def make_paginator_result(items):
    """Create a mock paginator that returns items when build_full_result() is called."""
    paginator = MagicMock()
    paginator.paginate.return_value.build_full_result.return_value = items
    return paginator


# ============================================================
# Tests for format_prefix_list
# ============================================================


class TestFormatPrefixList:
    def test_converts_camel_to_snake(self):
        result = format_prefix_list(EXAMPLE_PREFIX_LIST)

        assert result["prefix_list_id"] == "pl-0a1b2c3d4e5f6789a"
        assert result["prefix_list_arn"] == EXAMPLE_PREFIX_LIST["PrefixListArn"]
        assert result["prefix_list_name"] == "test-prefix-list"
        assert result["address_family"] == "IPv4"
        assert result["max_entries"] == 10
        assert result["state"] == "create-complete"
        assert result["version"] == 1

    def test_converts_tags_from_list_to_dict(self):
        result = format_prefix_list(EXAMPLE_PREFIX_LIST)

        assert result["tags"] == {"Name": "test-prefix-list"}

    def test_empty_tags(self):
        pl = {**EXAMPLE_PREFIX_LIST, "Tags": []}
        result = format_prefix_list(pl)

        assert result["tags"] == {}

    def test_missing_tags_key(self):
        pl = {k: v for k, v in EXAMPLE_PREFIX_LIST.items() if k != "Tags"}
        result = format_prefix_list(pl)

        assert result["tags"] == {}


# ============================================================
# Tests for get_prefix_list_entries
# ============================================================


class TestGetPrefixListEntries:
    def test_returns_entries_as_snake_case(self):
        client = MagicMock()
        client.get_paginator.return_value = make_paginator_result({"Entries": EXAMPLE_ENTRIES})
        module = make_module({})

        result = get_prefix_list_entries(client, module, "pl-0a1b2c3d4e5f6789a")

        assert len(result) == 2
        assert result[0] == {"cidr": "10.0.0.0/24", "description": "My subnet"}
        assert result[1] == {"cidr": "10.1.0.0/24", "description": "Other subnet"}

    def test_empty_entries(self):
        client = MagicMock()
        client.get_paginator.return_value = make_paginator_result({"Entries": []})
        module = make_module({})

        result = get_prefix_list_entries(client, module, "pl-0a1b2c3d4e5f6789a")

        assert result == []

    def test_uses_correct_paginator(self):
        client = MagicMock()
        client.get_paginator.return_value = make_paginator_result({"Entries": []})
        module = make_module({})

        get_prefix_list_entries(client, module, "pl-0a1b2c3d4e5f6789a")

        client.get_paginator.assert_called_once_with("get_managed_prefix_list_entries")
        client.get_paginator.return_value.paginate.assert_called_once_with(
            PrefixListId="pl-0a1b2c3d4e5f6789a"
        )

    def test_empty_description_normalized(self):
        entries = [{"Cidr": "10.0.0.0/24", "Description": None}]
        client = MagicMock()
        client.get_paginator.return_value = make_paginator_result({"Entries": entries})
        module = make_module({})

        result = get_prefix_list_entries(client, module, "pl-0a1b2c3d4e5f6789a")

        assert result[0]["description"] == ""


# ============================================================
# Tests for list_prefix_lists
# ============================================================


class TestListPrefixLists:
    def test_lists_all_when_no_filters(self):
        client = MagicMock()
        client.get_paginator.side_effect = [
            make_paginator_result({"PrefixLists": [EXAMPLE_PREFIX_LIST]}),
            make_paginator_result({"Entries": []}),
        ]
        module = make_module({
            "prefix_list_ids": [],
            "filters": {},
            "include_entries": True,
        })

        result = list_prefix_lists(client, module)

        assert len(result) == 1
        assert result[0]["prefix_list_id"] == "pl-0a1b2c3d4e5f6789a"

    def test_filters_by_id(self):
        client = MagicMock()
        client.get_paginator.side_effect = [
            make_paginator_result({"PrefixLists": [EXAMPLE_PREFIX_LIST]}),
            make_paginator_result({"Entries": []}),
        ]
        module = make_module({
            "prefix_list_ids": ["pl-0a1b2c3d4e5f6789a"],
            "filters": {},
            "include_entries": True,
        })

        list_prefix_lists(client, module)

        describe_paginator = client.get_paginator.return_value
        describe_paginator.paginate.assert_called_once_with(
            PrefixListIds=["pl-0a1b2c3d4e5f6789a"]
        )

    def test_filters_by_dict(self):
        client = MagicMock()
        client.get_paginator.side_effect = [
            make_paginator_result({"PrefixLists": [EXAMPLE_PREFIX_LIST]}),
            make_paginator_result({"Entries": []}),
        ]
        module = make_module({
            "prefix_list_ids": [],
            "filters": {"prefix-list-name": "test-prefix-list"},
            "include_entries": True,
        })

        list_prefix_lists(client, module)

        describe_paginator = client.get_paginator.return_value
        call_kwargs = describe_paginator.paginate.call_args[1]
        assert "Filters" in call_kwargs
        assert any(f["Name"] == "prefix-list-name" for f in call_kwargs["Filters"])

    def test_includes_entries_when_requested(self):
        entries_paginator = make_paginator_result({"Entries": EXAMPLE_ENTRIES})
        describe_paginator = make_paginator_result({"PrefixLists": [EXAMPLE_PREFIX_LIST]})
        client = MagicMock()
        client.get_paginator.side_effect = [describe_paginator, entries_paginator]
        module = make_module({
            "prefix_list_ids": [],
            "filters": {},
            "include_entries": True,
        })

        result = list_prefix_lists(client, module)

        assert "entries" in result[0]
        assert len(result[0]["entries"]) == 2

    def test_excludes_entries_when_not_requested(self):
        client = MagicMock()
        client.get_paginator.return_value = make_paginator_result(
            {"PrefixLists": [EXAMPLE_PREFIX_LIST]}
        )
        module = make_module({
            "prefix_list_ids": [],
            "filters": {},
            "include_entries": False,
        })

        result = list_prefix_lists(client, module)

        assert "entries" not in result[0]
        # Only one paginator call (describe only, no entries fetch)
        assert client.get_paginator.call_count == 1

    def test_empty_result(self):
        client = MagicMock()
        client.get_paginator.return_value = make_paginator_result({"PrefixLists": []})
        module = make_module({
            "prefix_list_ids": [],
            "filters": {},
            "include_entries": True,
        })

        result = list_prefix_lists(client, module)

        assert result == []

    def test_multiple_prefix_lists(self):
        second_pl = {**EXAMPLE_PREFIX_LIST, "PrefixListId": "pl-other", "PrefixListName": "other"}
        entries_paginator_1 = make_paginator_result({"Entries": []})
        entries_paginator_2 = make_paginator_result({"Entries": []})
        describe_paginator = make_paginator_result(
            {"PrefixLists": [EXAMPLE_PREFIX_LIST, second_pl]}
        )
        client = MagicMock()
        client.get_paginator.side_effect = [
            describe_paginator,
            entries_paginator_1,
            entries_paginator_2,
        ]
        module = make_module({
            "prefix_list_ids": [],
            "filters": {},
            "include_entries": True,
        })

        result = list_prefix_lists(client, module)

        assert len(result) == 2
        assert result[0]["prefix_list_id"] == "pl-0a1b2c3d4e5f6789a"
        assert result[1]["prefix_list_id"] == "pl-other"


# ============================================================
# Tests for main()
# ============================================================


class TestMain(ModuleTestCase):
    def setUp(self):
        super().setUp()
        self.mock_ec2 = MagicMock()
        self.client_patcher = patch(
            "ansible_collections.community.aws.plugins.modules"
            ".ec2_vpc_managed_prefix_list_info.AnsibleAWSModule.client",
            return_value=self.mock_ec2,
        )
        self.client_patcher.start()
        self.addCleanup(self.client_patcher.stop)

        entries_paginator = make_paginator_result({"Entries": []})
        describe_paginator = make_paginator_result({"PrefixLists": [EXAMPLE_PREFIX_LIST]})
        self.mock_ec2.get_paginator.side_effect = [describe_paginator, entries_paginator]

    def test_returns_prefix_lists(self):
        set_module_args({})

        with self.assertRaises(AnsibleExitJson) as cm:
            import ansible_collections.community.aws.plugins.modules.ec2_vpc_managed_prefix_list_info as m
            m.main()

        result = cm.exception.args[0]
        assert "prefix_lists" in result
        assert len(result["prefix_lists"]) == 1
        pl = result["prefix_lists"][0]
        assert pl["prefix_list_id"] == "pl-0a1b2c3d4e5f6789a"
        assert pl["prefix_list_name"] == "test-prefix-list"
        assert pl["tags"] == {"Name": "test-prefix-list"}
        assert pl["entries"] == []

    def test_filter_by_id(self):
        set_module_args({"prefix_list_ids": ["pl-0a1b2c3d4e5f6789a"]})

        with self.assertRaises(AnsibleExitJson) as cm:
            import ansible_collections.community.aws.plugins.modules.ec2_vpc_managed_prefix_list_info as m
            m.main()

        result = cm.exception.args[0]
        assert len(result["prefix_lists"]) == 1

    def test_no_entries_when_include_entries_false(self):
        self.mock_ec2.get_paginator.side_effect = None
        self.mock_ec2.get_paginator.return_value = make_paginator_result(
            {"PrefixLists": [EXAMPLE_PREFIX_LIST]}
        )
        set_module_args({"include_entries": False})

        with self.assertRaises(AnsibleExitJson) as cm:
            import ansible_collections.community.aws.plugins.modules.ec2_vpc_managed_prefix_list_info as m
            m.main()

        result = cm.exception.args[0]
        pl = result["prefix_lists"][0]
        assert "entries" not in pl

    def test_empty_result(self):
        self.mock_ec2.get_paginator.side_effect = None
        self.mock_ec2.get_paginator.return_value = make_paginator_result({"PrefixLists": []})
        set_module_args({})

        with self.assertRaises(AnsibleExitJson) as cm:
            import ansible_collections.community.aws.plugins.modules.ec2_vpc_managed_prefix_list_info as m
            m.main()

        result = cm.exception.args[0]
        assert result["prefix_lists"] == []
