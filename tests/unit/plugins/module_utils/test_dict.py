# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible_collections.community.aws.plugins.module_utils.dict import is_dict_subset


# ---------------------------------------------------------------------------
# Basic dict subset checks
# ---------------------------------------------------------------------------


class TestBasicSubset:
    def test_empty_expected_is_subset_of_any_dict(self):
        assert is_dict_subset({}, {"a": 1, "b": 2}) is True

    def test_empty_both(self):
        assert is_dict_subset({}, {}) is True

    def test_identical_dicts(self):
        d = {"a": 1, "b": "hello"}
        assert is_dict_subset(d, d) is True

    def test_expected_is_strict_subset(self):
        assert is_dict_subset({"a": 1}, {"a": 1, "b": 2}) is True

    def test_extra_key_in_expected_fails(self):
        assert is_dict_subset({"a": 1, "c": 3}, {"a": 1, "b": 2}) is False

    def test_value_mismatch(self):
        assert is_dict_subset({"a": 2}, {"a": 1, "b": 2}) is False

    def test_expected_key_missing_from_existing(self):
        assert is_dict_subset({"x": 1}, {"a": 1}) is False


# ---------------------------------------------------------------------------
# Nested dict subset checks
# ---------------------------------------------------------------------------


class TestNestedDicts:
    def test_nested_subset(self):
        expected = {"a": {"x": 1}}
        existing = {"a": {"x": 1, "y": 2}, "b": 3}
        assert is_dict_subset(expected, existing) is True

    def test_nested_value_mismatch(self):
        expected = {"a": {"x": 99}}
        existing = {"a": {"x": 1, "y": 2}}
        assert is_dict_subset(expected, existing) is False

    def test_nested_missing_key(self):
        expected = {"a": {"z": 1}}
        existing = {"a": {"x": 1, "y": 2}}
        assert is_dict_subset(expected, existing) is False

    def test_deeply_nested(self):
        expected = {"a": {"b": {"c": {"d": 1}}}}
        existing = {"a": {"b": {"c": {"d": 1, "e": 2}, "f": 3}}}
        assert is_dict_subset(expected, existing) is True

    def test_deeply_nested_mismatch(self):
        expected = {"a": {"b": {"c": {"d": 1}}}}
        existing = {"a": {"b": {"c": {"d": 2, "e": 2}, "f": 3}}}
        assert is_dict_subset(expected, existing) is False


# ---------------------------------------------------------------------------
# List comparison (no sort key)
# ---------------------------------------------------------------------------


class TestListComparison:
    def test_identical_lists(self):
        expected = {"items": [1, 2, 3]}
        existing = {"items": [1, 2, 3]}
        assert is_dict_subset(expected, existing) is True

    def test_list_length_mismatch(self):
        expected = {"items": [1, 2]}
        existing = {"items": [1, 2, 3]}
        assert is_dict_subset(expected, existing) is False

    def test_list_order_matters_without_sort_key(self):
        expected = {"items": [{"name": "a"}, {"name": "b"}]}
        existing = {"items": [{"name": "b"}, {"name": "a"}]}
        assert is_dict_subset(expected, existing) is False

    def test_list_of_dicts_with_extra_keys(self):
        expected = {"items": [{"name": "a"}]}
        existing = {"items": [{"name": "a", "extra": "value"}]}
        assert is_dict_subset(expected, existing) is True

    def test_empty_lists(self):
        assert is_dict_subset({"items": []}, {"items": []}) is True


# ---------------------------------------------------------------------------
# List sort key
# ---------------------------------------------------------------------------


class TestListSortKey:
    def test_sort_key_reorders_before_comparison(self):
        expected = {"items": [{"id": "b", "val": 2}, {"id": "a", "val": 1}]}
        existing = {"items": [{"id": "a", "val": 1}, {"id": "b", "val": 2}]}
        assert is_dict_subset(expected, existing, list_sort_key="id") is True

    def test_sort_key_still_detects_value_mismatch(self):
        expected = {"items": [{"id": "b", "val": 99}, {"id": "a", "val": 1}]}
        existing = {"items": [{"id": "a", "val": 1}, {"id": "b", "val": 2}]}
        assert is_dict_subset(expected, existing, list_sort_key="id") is False

    def test_sort_key_with_extra_keys_in_existing(self):
        expected = {"items": [{"id": "b", "val": 2}, {"id": "a", "val": 1}]}
        existing = {"items": [{"id": "a", "val": 1, "extra": "x"}, {"id": "b", "val": 2, "extra": "y"}]}
        assert is_dict_subset(expected, existing, list_sort_key="id") is True

    def test_sort_key_missing_from_some_elements_falls_back_to_positional(self):
        """When not all elements have the sort key, positional comparison is used."""
        expected = {"items": [{"id": "a"}, {"other": "b"}]}
        existing = {"items": [{"id": "a"}, {"other": "b"}]}
        assert is_dict_subset(expected, existing, list_sort_key="id") is True

    def test_sort_key_missing_causes_order_sensitive_failure(self):
        """Without the sort key in all elements, order matters and a swap fails."""
        expected = {"items": [{"other": "b"}, {"id": "a"}]}
        existing = {"items": [{"id": "a"}, {"other": "b"}]}
        assert is_dict_subset(expected, existing, list_sort_key="id") is False

    def test_sort_key_not_in_existing_elements_falls_back_to_positional(self):
        """Sort key in expected but missing from existing — positional comparison."""
        expected = {"items": [{"id": "a"}, {"id": "b"}]}
        existing = {"items": [{"name": "a"}, {"name": "b"}]}
        assert is_dict_subset(expected, existing, list_sort_key="id") is False


# ---------------------------------------------------------------------------
# Scalar / type-mismatch edge cases
# ---------------------------------------------------------------------------


class TestScalarAndTypeMismatch:
    def test_scalar_equality(self):
        assert is_dict_subset(42, 42) is True

    def test_scalar_inequality(self):
        assert is_dict_subset(42, 43) is False

    def test_string_equality(self):
        assert is_dict_subset("hello", "hello") is True

    def test_none_values(self):
        assert is_dict_subset({"a": None}, {"a": None, "b": 1}) is True

    def test_bool_vs_int(self):
        # In Python bool is a subclass of int; True == 1. Verify we don't
        # break on this edge case.
        assert is_dict_subset({"a": True}, {"a": True}) is True

    def test_dict_expected_vs_non_dict_existing(self):
        assert is_dict_subset({"a": 1}, "not a dict") is False

    def test_list_expected_vs_non_list_existing(self):
        assert is_dict_subset({"a": [1]}, {"a": "not a list"}) is False


# ---------------------------------------------------------------------------
# Real-world: ECS Service Connect scenario
# ---------------------------------------------------------------------------


class TestServiceConnectScenario:
    """Simulates the ECS Service Connect comparison use case."""

    def _user_config(self):
        return {
            "enabled": True,
            "namespace": "my-namespace",
            "services": [
                {
                    "portName": "http",
                    "clientAliases": [{"port": 80}],
                },
            ],
        }

    def _aws_response(self):
        return {
            "enabled": True,
            "namespace": "my-namespace",
            "services": [
                {
                    "portName": "http",
                    "discoveryName": "http.my-namespace",
                    "clientAliases": [{"port": 80, "dnsName": "http.my-namespace"}],
                },
            ],
        }

    def test_user_config_is_subset_of_aws_response(self):
        assert is_dict_subset(self._user_config(), self._aws_response(), list_sort_key="portName") is True

    def test_changed_port_detected(self):
        user = self._user_config()
        user["services"][0]["clientAliases"][0]["port"] = 8080
        assert is_dict_subset(user, self._aws_response(), list_sort_key="portName") is False

    def test_changed_namespace_detected(self):
        user = self._user_config()
        user["namespace"] = "other-namespace"
        assert is_dict_subset(user, self._aws_response(), list_sort_key="portName") is False

    def test_disabled_detected(self):
        user = self._user_config()
        user["enabled"] = False
        assert is_dict_subset(user, self._aws_response(), list_sort_key="portName") is False

    def test_multiple_services_different_order(self):
        user = {
            "enabled": True,
            "namespace": "ns",
            "services": [
                {"portName": "grpc", "clientAliases": [{"port": 9090}]},
                {"portName": "http", "clientAliases": [{"port": 80}]},
            ],
        }
        aws = {
            "enabled": True,
            "namespace": "ns",
            "services": [
                {"portName": "http", "discoveryName": "http.ns", "clientAliases": [{"port": 80}]},
                {"portName": "grpc", "discoveryName": "grpc.ns", "clientAliases": [{"port": 9090}]},
            ],
        }
        assert is_dict_subset(user, aws, list_sort_key="portName") is True

    def test_added_service_detected(self):
        user = self._user_config()
        user["services"].append({"portName": "grpc", "clientAliases": [{"port": 9090}]})
        assert is_dict_subset(user, self._aws_response(), list_sort_key="portName") is False
