# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible_collections.community.aws.plugins.modules.cognito_user_pool import _deep_merge


class TestDeepMerge:
    """Tests for _deep_merge used to preserve sibling keys during partial nested updates."""

    def test_override_replaces_simple_values(self):
        base = {"A": 1, "B": 2}
        override = {"A": 10}
        result = _deep_merge(base, override)
        assert result == {"A": 10, "B": 2}

    def test_override_adds_new_keys(self):
        base = {"A": 1}
        override = {"B": 2}
        result = _deep_merge(base, override)
        assert result == {"A": 1, "B": 2}

    def test_nested_dicts_are_merged(self):
        base = {"Policies": {"PasswordPolicy": {"MinimumLength": 8, "RequireUppercase": True}}}
        override = {"Policies": {"PasswordPolicy": {"MinimumLength": 14}}}
        result = _deep_merge(base, override)
        assert result == {"Policies": {"PasswordPolicy": {"MinimumLength": 14, "RequireUppercase": True}}}

    def test_nested_merge_preserves_sibling_sub_dicts(self):
        base = {
            "Policies": {
                "PasswordPolicy": {"MinimumLength": 8},
                "SignInPolicy": {"AllowedFirstAuthFactors": ["PASSWORD"]},
            }
        }
        override = {"Policies": {"PasswordPolicy": {"MinimumLength": 14}}}
        result = _deep_merge(base, override)
        assert result["Policies"]["PasswordPolicy"]["MinimumLength"] == 14
        assert result["Policies"]["SignInPolicy"] == {"AllowedFirstAuthFactors": ["PASSWORD"]}

    def test_override_replaces_non_dict_with_dict(self):
        base = {"A": "string_value"}
        override = {"A": {"nested": True}}
        result = _deep_merge(base, override)
        assert result == {"A": {"nested": True}}

    def test_override_replaces_dict_with_non_dict(self):
        base = {"A": {"nested": True}}
        override = {"A": "string_value"}
        result = _deep_merge(base, override)
        assert result == {"A": "string_value"}

    def test_empty_base(self):
        result = _deep_merge({}, {"A": 1})
        assert result == {"A": 1}

    def test_empty_override(self):
        result = _deep_merge({"A": 1}, {})
        assert result == {"A": 1}

    def test_does_not_mutate_base(self):
        base = {"A": {"B": 1}}
        override = {"A": {"B": 2}}
        _deep_merge(base, override)
        assert base == {"A": {"B": 1}}

    def test_three_level_merge(self):
        base = {"L1": {"L2": {"L3": "old", "Sibling": "keep"}}}
        override = {"L1": {"L2": {"L3": "new"}}}
        result = _deep_merge(base, override)
        assert result == {"L1": {"L2": {"L3": "new", "Sibling": "keep"}}}

    def test_list_values_replaced_not_merged(self):
        """Lists are not deep-merged — override replaces the entire list."""
        base = {"A": [1, 2, 3]}
        override = {"A": [4, 5]}
        result = _deep_merge(base, override)
        assert result == {"A": [4, 5]}
