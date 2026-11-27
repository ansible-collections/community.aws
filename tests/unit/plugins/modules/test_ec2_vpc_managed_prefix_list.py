# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest.mock import MagicMock, call, patch

import pytest

from ansible_collections.amazon.aws.plugins.module_utils.botocore import HAS_BOTO3

if not HAS_BOTO3:
    pytestmark = pytest.mark.skip(
        "test_ec2_vpc_managed_prefix_list.py requires the `boto3` and `botocore` modules"
    )

from ansible_collections.community.aws.plugins.modules.ec2_vpc_managed_prefix_list import (
    create_prefix_list,
    delete_prefix_list,
    format_prefix_list,
    get_prefix_list,
    get_prefix_list_entries,
    update_prefix_list,
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
    "Tags": [],
}

EXAMPLE_ENTRIES = [
    {"Cidr": "10.0.0.0/24", "Description": "My subnet"},
    {"Cidr": "10.1.0.0/24", "Description": "My other subnet"},
]


def make_module(params, check_mode=False):
    """Helper to create a mock module with given params."""
    module = MagicMock()
    module.params = params
    module.check_mode = check_mode
    return module


def make_client(describe_results=None, entries_results=None):
    """Helper to create a mock boto3 EC2 client."""
    client = MagicMock()
    if describe_results is not None:
        client.describe_managed_prefix_lists.return_value = {"PrefixLists": describe_results}
    if entries_results is not None:
        client.get_managed_prefix_list_entries.return_value = {"Entries": entries_results}
    return client


# ============================================================
# Tests for get_prefix_list
# ============================================================


class TestGetPrefixList:
    def test_lookup_by_name(self):
        client = make_client(describe_results=[EXAMPLE_PREFIX_LIST])
        module = make_module({"prefix_list_id": None, "name": "test-prefix-list"})

        result = get_prefix_list(client, module)

        assert result["PrefixListId"] == "pl-0a1b2c3d4e5f6789a"
        client.describe_managed_prefix_lists.assert_called_once_with(
            aws_retry=True,
            Filters=[{"Name": "prefix-list-name", "Values": ["test-prefix-list"]}],
        )

    def test_lookup_by_id(self):
        client = make_client(describe_results=[EXAMPLE_PREFIX_LIST])
        module = make_module({"prefix_list_id": "pl-0a1b2c3d4e5f6789a", "name": None})

        result = get_prefix_list(client, module)

        assert result["PrefixListId"] == "pl-0a1b2c3d4e5f6789a"
        client.describe_managed_prefix_lists.assert_called_once_with(
            aws_retry=True,
            PrefixListIds=["pl-0a1b2c3d4e5f6789a"],
        )

    def test_returns_none_when_not_found(self):
        client = make_client(describe_results=[])
        module = make_module({"prefix_list_id": None, "name": "nonexistent"})

        result = get_prefix_list(client, module)

        assert result is None


# ============================================================
# Tests for format_prefix_list
# ============================================================


class TestFormatPrefixList:
    def test_converts_to_snake_case(self):
        result = format_prefix_list(EXAMPLE_PREFIX_LIST, EXAMPLE_ENTRIES)

        assert result["prefix_list_id"] == "pl-0a1b2c3d4e5f6789a"
        assert result["prefix_list_name"] == "test-prefix-list"
        assert result["address_family"] == "IPv4"
        assert result["max_entries"] == 10
        assert result["version"] == 1

    def test_converts_tags(self):
        pl_with_tags = {**EXAMPLE_PREFIX_LIST, "Tags": [{"Key": "Env", "Value": "prod"}]}
        result = format_prefix_list(pl_with_tags, [])

        assert result["tags"] == {"Env": "prod"}

    def test_converts_entries(self):
        result = format_prefix_list(EXAMPLE_PREFIX_LIST, EXAMPLE_ENTRIES)

        assert len(result["entries"]) == 2
        assert result["entries"][0] == {"cidr": "10.0.0.0/24", "description": "My subnet"}
        assert result["entries"][1] == {"cidr": "10.1.0.0/24", "description": "My other subnet"}

    def test_empty_entries(self):
        result = format_prefix_list(EXAMPLE_PREFIX_LIST, [])

        assert result["entries"] == []

    def test_empty_tags(self):
        result = format_prefix_list(EXAMPLE_PREFIX_LIST, [])

        assert result["tags"] == {}


# ============================================================
# Tests for update_prefix_list
# ============================================================


class TestUpdatePrefixList:
    def test_no_changes_returns_false(self):
        client = make_client(entries_results=[])
        module = make_module({
            "name": "test-prefix-list",
            "max_entries": 10,
            "address_family": "IPv4",
            "entries": [],
            "purge_entries": True,
        })

        result_pl, changed = update_prefix_list(EXAMPLE_PREFIX_LIST, client, module)

        assert changed is False
        client.modify_managed_prefix_list.assert_not_called()

    def test_name_change_triggers_update(self):
        updated = {**EXAMPLE_PREFIX_LIST, "PrefixListName": "new-name"}
        client = make_client(entries_results=[])
        client.modify_managed_prefix_list.return_value = {"PrefixList": updated}
        module = make_module({
            "name": "new-name",
            "max_entries": 10,
            "address_family": "IPv4",
            "entries": None,
            "purge_entries": True,
        })

        result_pl, changed = update_prefix_list(EXAMPLE_PREFIX_LIST, client, module)

        assert changed is True
        client.modify_managed_prefix_list.assert_called_once()
        call_kwargs = client.modify_managed_prefix_list.call_args[1]
        assert call_kwargs["PrefixListName"] == "new-name"

    def test_max_entries_change_triggers_update(self):
        updated = {**EXAMPLE_PREFIX_LIST, "MaxEntries": 20}
        client = make_client(entries_results=[])
        client.modify_managed_prefix_list.return_value = {"PrefixList": updated}
        module = make_module({
            "name": "test-prefix-list",
            "max_entries": 20,
            "address_family": "IPv4",
            "entries": None,
            "purge_entries": True,
        })

        result_pl, changed = update_prefix_list(EXAMPLE_PREFIX_LIST, client, module)

        assert changed is True
        call_kwargs = client.modify_managed_prefix_list.call_args[1]
        assert call_kwargs["MaxEntries"] == 20

    def test_address_family_change_fails(self):
        client = make_client(entries_results=[])
        module = make_module({
            "name": "test-prefix-list",
            "max_entries": 10,
            "address_family": "IPv6",
            "entries": None,
            "purge_entries": True,
        })

        update_prefix_list(EXAMPLE_PREFIX_LIST, client, module)

        module.fail_json.assert_called_once()
        assert "address_family" in module.fail_json.call_args[1]["msg"]

    def test_new_entry_added(self):
        updated = {**EXAMPLE_PREFIX_LIST, "Version": 2}
        client = make_client(entries_results=[])
        client.modify_managed_prefix_list.return_value = {"PrefixList": updated}
        module = make_module({
            "name": "test-prefix-list",
            "max_entries": 10,
            "address_family": "IPv4",
            "entries": [{"cidr": "10.0.0.0/24", "description": "New"}],
            "purge_entries": True,
        })

        result_pl, changed = update_prefix_list(EXAMPLE_PREFIX_LIST, client, module)

        assert changed is True
        call_kwargs = client.modify_managed_prefix_list.call_args[1]
        assert {"Cidr": "10.0.0.0/24", "Description": "New"} in call_kwargs["AddEntries"]

    def test_existing_entry_removed_with_purge(self):
        updated = {**EXAMPLE_PREFIX_LIST, "Version": 2}
        client = make_client(entries_results=[{"Cidr": "10.0.0.0/24", "Description": "Old"}])
        client.modify_managed_prefix_list.return_value = {"PrefixList": updated}
        module = make_module({
            "name": "test-prefix-list",
            "max_entries": 10,
            "address_family": "IPv4",
            "entries": [],
            "purge_entries": True,
        })

        result_pl, changed = update_prefix_list(EXAMPLE_PREFIX_LIST, client, module)

        assert changed is True
        call_kwargs = client.modify_managed_prefix_list.call_args[1]
        assert {"Cidr": "10.0.0.0/24"} in call_kwargs["RemoveEntries"]

    def test_existing_entry_kept_without_purge(self):
        client = make_client(entries_results=[{"Cidr": "10.0.0.0/24", "Description": "Keep me"}])
        module = make_module({
            "name": "test-prefix-list",
            "max_entries": 10,
            "address_family": "IPv4",
            "entries": [],
            "purge_entries": False,
        })

        result_pl, changed = update_prefix_list(EXAMPLE_PREFIX_LIST, client, module)

        assert changed is False
        client.modify_managed_prefix_list.assert_not_called()

    def test_entry_description_update(self):
        updated = {**EXAMPLE_PREFIX_LIST, "Version": 2}
        client = make_client(entries_results=[{"Cidr": "10.0.0.0/24", "Description": "Old desc"}])
        client.modify_managed_prefix_list.return_value = {"PrefixList": updated}
        module = make_module({
            "name": "test-prefix-list",
            "max_entries": 10,
            "address_family": "IPv4",
            "entries": [{"cidr": "10.0.0.0/24", "description": "New desc"}],
            "purge_entries": True,
        })

        result_pl, changed = update_prefix_list(EXAMPLE_PREFIX_LIST, client, module)

        assert changed is True
        call_kwargs = client.modify_managed_prefix_list.call_args[1]
        assert {"Cidr": "10.0.0.0/24", "Description": "New desc"} in call_kwargs["AddEntries"]
        assert {"Cidr": "10.0.0.0/24"} in call_kwargs["RemoveEntries"]

    def test_check_mode_returns_changed_without_api_call(self):
        client = make_client(entries_results=[])
        module = make_module(
            {
                "name": "new-name",
                "max_entries": 10,
                "address_family": "IPv4",
                "entries": None,
                "purge_entries": True,
            },
            check_mode=True,
        )

        result_pl, changed = update_prefix_list(EXAMPLE_PREFIX_LIST, client, module)

        assert changed is True
        client.modify_managed_prefix_list.assert_not_called()
        # Returns original (unmodified) prefix list
        assert result_pl["PrefixListName"] == "test-prefix-list"


# ============================================================
# Tests for create_prefix_list
# ============================================================


class TestCreatePrefixList:
    def test_basic_creation(self):
        client = MagicMock()
        client.create_managed_prefix_list.return_value = {"PrefixList": EXAMPLE_PREFIX_LIST}
        module = make_module({
            "name": "test-prefix-list",
            "max_entries": 10,
            "address_family": "IPv4",
            "entries": None,
            "tags": None,
        })

        result = create_prefix_list(client, module)

        assert result["PrefixListId"] == "pl-0a1b2c3d4e5f6789a"
        client.create_managed_prefix_list.assert_called_once()
        call_kwargs = client.create_managed_prefix_list.call_args[1]
        assert call_kwargs["PrefixListName"] == "test-prefix-list"
        assert call_kwargs["MaxEntries"] == 10
        assert call_kwargs["AddressFamily"] == "IPv4"
        assert "Entries" not in call_kwargs
        assert "TagSpecifications" not in call_kwargs

    def test_creation_with_entries(self):
        client = MagicMock()
        client.create_managed_prefix_list.return_value = {"PrefixList": EXAMPLE_PREFIX_LIST}
        module = make_module({
            "name": "test-prefix-list",
            "max_entries": 10,
            "address_family": "IPv4",
            "entries": [{"cidr": "10.0.0.0/24", "description": "My subnet"}],
            "tags": None,
        })

        create_prefix_list(client, module)

        call_kwargs = client.create_managed_prefix_list.call_args[1]
        assert call_kwargs["Entries"] == [{"Cidr": "10.0.0.0/24", "Description": "My subnet"}]

    def test_creation_with_tags(self):
        client = MagicMock()
        client.create_managed_prefix_list.return_value = {"PrefixList": EXAMPLE_PREFIX_LIST}
        module = make_module({
            "name": "test-prefix-list",
            "max_entries": 10,
            "address_family": "IPv4",
            "entries": None,
            "tags": {"Env": "prod"},
        })

        create_prefix_list(client, module)

        call_kwargs = client.create_managed_prefix_list.call_args[1]
        assert "TagSpecifications" in call_kwargs


# ============================================================
# Tests for delete_prefix_list
# ============================================================


class TestDeletePrefixList:
    def test_delete_calls_api(self):
        client = MagicMock()
        module = make_module({})

        delete_prefix_list(EXAMPLE_PREFIX_LIST, client, module)

        client.delete_managed_prefix_list.assert_called_once_with(
            aws_retry=True,
            PrefixListId="pl-0a1b2c3d4e5f6789a",
        )

    def test_check_mode_skips_api_call(self):
        client = MagicMock()
        module = make_module({}, check_mode=True)

        delete_prefix_list(EXAMPLE_PREFIX_LIST, client, module)

        client.delete_managed_prefix_list.assert_not_called()


# ============================================================
# Tests for main() via module-level mocking
# ============================================================


class TestMain(ModuleTestCase):
    def setUp(self):
        super().setUp()
        # Patch module.client to return our mock EC2 client
        self.mock_ec2 = MagicMock()
        self.client_patcher = patch(
            "ansible_collections.community.aws.plugins.modules"
            ".ec2_vpc_managed_prefix_list.AnsibleAWSModule.client",
            return_value=self.mock_ec2,
        )
        self.client_patcher.start()
        self.addCleanup(self.client_patcher.stop)

        # Default mock responses
        self.mock_ec2.describe_managed_prefix_lists.return_value = {
            "PrefixLists": [EXAMPLE_PREFIX_LIST]
        }
        self.mock_ec2.get_managed_prefix_list_entries.return_value = {"Entries": []}
        self.mock_ec2.describe_tags.return_value = {"Tags": []}

    def test_create_prefix_list(self):
        set_module_args({
            "state": "present",
            "name": "test-prefix-list",
            "address_family": "IPv4",
            "max_entries": 10,
        })
        self.mock_ec2.describe_managed_prefix_lists.side_effect = [
            {"PrefixLists": []},
            {"PrefixLists": [EXAMPLE_PREFIX_LIST]},
        ]
        self.mock_ec2.create_managed_prefix_list.return_value = {"PrefixList": EXAMPLE_PREFIX_LIST}

        with self.assertRaises(AnsibleExitJson) as cm:
            import ansible_collections.community.aws.plugins.modules.ec2_vpc_managed_prefix_list as m
            m.main()

        result = cm.exception.args[0]
        assert result["changed"] is True
        assert result["prefix_list_id"] == "pl-0a1b2c3d4e5f6789a"
        assert "prefix_list" in result

    def test_create_check_mode(self):
        set_module_args({
            "state": "present",
            "name": "test-prefix-list",
            "address_family": "IPv4",
            "max_entries": 10,
            "_ansible_check_mode": True,
        })
        self.mock_ec2.describe_managed_prefix_lists.return_value = {"PrefixLists": []}

        with self.assertRaises(AnsibleExitJson) as cm:
            import ansible_collections.community.aws.plugins.modules.ec2_vpc_managed_prefix_list as m
            m.main()

        result = cm.exception.args[0]
        assert result["changed"] is True
        self.mock_ec2.create_managed_prefix_list.assert_not_called()

    def test_idempotent_no_change(self):
        set_module_args({
            "state": "present",
            "name": "test-prefix-list",
            "address_family": "IPv4",
            "max_entries": 10,
        })
        self.mock_ec2.describe_managed_prefix_lists.return_value = {
            "PrefixLists": [EXAMPLE_PREFIX_LIST]
        }
        self.mock_ec2.get_managed_prefix_list_entries.return_value = {"Entries": []}

        with self.assertRaises(AnsibleExitJson) as cm:
            import ansible_collections.community.aws.plugins.modules.ec2_vpc_managed_prefix_list as m
            m.main()

        result = cm.exception.args[0]
        assert result["changed"] is False
        self.mock_ec2.modify_managed_prefix_list.assert_not_called()
        self.mock_ec2.create_managed_prefix_list.assert_not_called()

    def test_delete_existing(self):
        set_module_args({
            "state": "absent",
            "prefix_list_id": "pl-0a1b2c3d4e5f6789a",
        })

        with self.assertRaises(AnsibleExitJson) as cm:
            import ansible_collections.community.aws.plugins.modules.ec2_vpc_managed_prefix_list as m
            m.main()

        result = cm.exception.args[0]
        assert result["changed"] is True
        self.mock_ec2.delete_managed_prefix_list.assert_called_once_with(
            aws_retry=True,
            PrefixListId="pl-0a1b2c3d4e5f6789a",
        )

    def test_delete_nonexistent(self):
        set_module_args({
            "state": "absent",
            "prefix_list_id": "pl-nonexistent",
        })
        self.mock_ec2.describe_managed_prefix_lists.return_value = {"PrefixLists": []}

        with self.assertRaises(AnsibleExitJson) as cm:
            import ansible_collections.community.aws.plugins.modules.ec2_vpc_managed_prefix_list as m
            m.main()

        result = cm.exception.args[0]
        assert result["changed"] is False
        self.mock_ec2.delete_managed_prefix_list.assert_not_called()

    def test_delete_check_mode(self):
        set_module_args({
            "state": "absent",
            "prefix_list_id": "pl-0a1b2c3d4e5f6789a",
            "_ansible_check_mode": True,
        })

        with self.assertRaises(AnsibleExitJson) as cm:
            import ansible_collections.community.aws.plugins.modules.ec2_vpc_managed_prefix_list as m
            m.main()

        result = cm.exception.args[0]
        assert result["changed"] is True
        self.mock_ec2.delete_managed_prefix_list.assert_not_called()

    def test_prefix_list_info_returned(self):
        set_module_args({
            "state": "present",
            "name": "test-prefix-list",
            "address_family": "IPv4",
            "max_entries": 10,
        })
        self.mock_ec2.get_managed_prefix_list_entries.return_value = {
            "Entries": [{"Cidr": "10.0.0.0/24", "Description": "My subnet"}]
        }

        with self.assertRaises(AnsibleExitJson) as cm:
            import ansible_collections.community.aws.plugins.modules.ec2_vpc_managed_prefix_list as m
            m.main()

        result = cm.exception.args[0]
        pl = result["prefix_list"]
        assert pl["prefix_list_id"] == "pl-0a1b2c3d4e5f6789a"
        assert pl["address_family"] == "IPv4"
        assert pl["max_entries"] == 10
        assert pl["entries"] == [{"cidr": "10.0.0.0/24", "description": "My subnet"}]
