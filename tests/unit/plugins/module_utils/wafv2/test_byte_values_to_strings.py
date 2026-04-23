# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

__metaclass__ = type

from ansible_collections.community.aws.plugins.module_utils.wafv2 import byte_values_to_strings_before_compare
from ansible_collections.community.aws.plugins.module_utils.wafv2 import nested_byte_values_to_strings


class TestByteValuesToStringsBeforeCompare:
    """Test the byte_values_to_strings_before_compare function."""

    def test_converts_byte_match_statement_search_string(self):
        """Test that ByteMatchStatement SearchString is converted from bytes to string."""
        rules = [
            {
                "Name": "byte-match-rule",
                "Priority": 1,
                "Statement": {
                    "ByteMatchStatement": {
                        "SearchString": b"badbot",
                        "FieldToMatch": {"UriPath": {}},
                        "TextTransformations": [{"Type": "NONE", "Priority": 0}],
                        "PositionalConstraint": "CONTAINS",
                    }
                },
            }
        ]

        result = byte_values_to_strings_before_compare(rules)

        assert result[0]["Statement"]["ByteMatchStatement"]["SearchString"] == "badbot"
        assert isinstance(result[0]["Statement"]["ByteMatchStatement"]["SearchString"], str)

    def test_handles_multiple_rules_with_byte_match(self):
        """Test that function handles multiple rules with ByteMatchStatement."""
        rules = [
            {
                "Name": "rule-1",
                "Priority": 1,
                "Statement": {
                    "ByteMatchStatement": {
                        "SearchString": b"bot1",
                        "FieldToMatch": {"UriPath": {}},
                        "TextTransformations": [{"Type": "NONE", "Priority": 0}],
                        "PositionalConstraint": "CONTAINS",
                    }
                },
            },
            {
                "Name": "rule-2",
                "Priority": 2,
                "Statement": {
                    "ByteMatchStatement": {
                        "SearchString": b"bot2",
                        "FieldToMatch": {"UriPath": {}},
                        "TextTransformations": [{"Type": "NONE", "Priority": 0}],
                        "PositionalConstraint": "CONTAINS",
                    }
                },
            },
        ]

        result = byte_values_to_strings_before_compare(rules)

        assert result[0]["Statement"]["ByteMatchStatement"]["SearchString"] == "bot1"
        assert result[1]["Statement"]["ByteMatchStatement"]["SearchString"] == "bot2"

    def test_handles_non_byte_match_statements(self):
        """Test that non-ByteMatchStatement rules are not modified."""
        rules = [
            {
                "Name": "rate-limit-rule",
                "Priority": 1,
                "Statement": {
                    "RateBasedStatement": {
                        "Limit": 5000,
                        "AggregateKeyType": "IP",
                    }
                },
            }
        ]

        result = byte_values_to_strings_before_compare(rules)

        # Should not modify non-ByteMatchStatement rules
        assert "RateBasedStatement" in result[0]["Statement"]
        assert result[0]["Statement"]["RateBasedStatement"]["Limit"] == 5000

    def test_handles_or_statement_with_byte_match(self):
        """Test that OrStatement with nested ByteMatchStatement is handled."""
        rules = [
            {
                "Name": "or-statement-rule",
                "Priority": 1,
                "Statement": {
                    "OrStatement": {
                        "Statements": [
                            {
                                "ByteMatchStatement": {
                                    "SearchString": b"bot1",
                                    "FieldToMatch": {"UriPath": {}},
                                    "TextTransformations": [{"Type": "NONE", "Priority": 0}],
                                    "PositionalConstraint": "CONTAINS",
                                }
                            },
                            {
                                "ByteMatchStatement": {
                                    "SearchString": b"bot2",
                                    "FieldToMatch": {"UriPath": {}},
                                    "TextTransformations": [{"Type": "NONE", "Priority": 0}],
                                    "PositionalConstraint": "CONTAINS",
                                }
                            },
                        ]
                    }
                },
            }
        ]

        result = byte_values_to_strings_before_compare(rules)

        assert result[0]["Statement"]["OrStatement"]["Statements"][0]["ByteMatchStatement"]["SearchString"] == "bot1"
        assert result[0]["Statement"]["OrStatement"]["Statements"][1]["ByteMatchStatement"]["SearchString"] == "bot2"

    def test_handles_and_statement_with_byte_match(self):
        """Test that AndStatement with nested ByteMatchStatement is handled."""
        rules = [
            {
                "Name": "and-statement-rule",
                "Priority": 1,
                "Statement": {
                    "AndStatement": {
                        "Statements": [
                            {
                                "ByteMatchStatement": {
                                    "SearchString": b"test",
                                    "FieldToMatch": {"UriPath": {}},
                                    "TextTransformations": [{"Type": "NONE", "Priority": 0}],
                                    "PositionalConstraint": "CONTAINS",
                                }
                            }
                        ]
                    }
                },
            }
        ]

        result = byte_values_to_strings_before_compare(rules)

        assert result[0]["Statement"]["AndStatement"]["Statements"][0]["ByteMatchStatement"]["SearchString"] == "test"

    def test_handles_not_statement_with_byte_match(self):
        """Test that NotStatement with nested ByteMatchStatement is handled."""
        rules = [
            {
                "Name": "not-statement-rule",
                "Priority": 1,
                "Statement": {
                    "NotStatement": {
                        "Statements": [
                            {
                                "ByteMatchStatement": {
                                    "SearchString": b"goodbot",
                                    "FieldToMatch": {"UriPath": {}},
                                    "TextTransformations": [{"Type": "NONE", "Priority": 0}],
                                    "PositionalConstraint": "CONTAINS",
                                }
                            }
                        ]
                    }
                },
            }
        ]

        result = byte_values_to_strings_before_compare(rules)

        assert (
            result[0]["Statement"]["NotStatement"]["Statements"][0]["ByteMatchStatement"]["SearchString"] == "goodbot"
        )

    def test_handles_empty_rules_list(self):
        """Test that function handles empty rules list."""
        rules = []

        result = byte_values_to_strings_before_compare(rules)

        assert result == []

    def test_handles_utf8_characters(self):
        """Test that UTF-8 characters are properly decoded."""
        rules = [
            {
                "Name": "utf8-rule",
                "Priority": 1,
                "Statement": {
                    "ByteMatchStatement": {
                        "SearchString": "tëst".encode("utf-8"),
                        "FieldToMatch": {"UriPath": {}},
                        "TextTransformations": [{"Type": "NONE", "Priority": 0}],
                        "PositionalConstraint": "CONTAINS",
                    }
                },
            }
        ]

        result = byte_values_to_strings_before_compare(rules)

        assert result[0]["Statement"]["ByteMatchStatement"]["SearchString"] == "tëst"

    def test_modifies_in_place(self):
        """Test that the function modifies the list in place."""
        rules = [
            {
                "Name": "byte-match-rule",
                "Priority": 1,
                "Statement": {
                    "ByteMatchStatement": {
                        "SearchString": b"test",
                        "FieldToMatch": {"UriPath": {}},
                        "TextTransformations": [{"Type": "NONE", "Priority": 0}],
                        "PositionalConstraint": "CONTAINS",
                    }
                },
            }
        ]

        result = byte_values_to_strings_before_compare(rules)

        # The function modifies in place and returns the same list
        assert result is rules
        assert result[0]["Statement"]["ByteMatchStatement"]["SearchString"] == "test"


class TestNestedByteValuesToStrings:
    """Test the nested_byte_values_to_strings function."""

    def test_converts_or_statement_byte_match(self):
        """Test that OrStatement ByteMatchStatement is converted."""
        rule = {
            "Name": "or-rule",
            "Priority": 1,
            "Statement": {
                "OrStatement": {
                    "Statements": [
                        {
                            "ByteMatchStatement": {
                                "SearchString": b"bot",
                                "FieldToMatch": {"UriPath": {}},
                                "TextTransformations": [{"Type": "NONE", "Priority": 0}],
                                "PositionalConstraint": "CONTAINS",
                            }
                        }
                    ]
                }
            },
        }

        result = nested_byte_values_to_strings(rule, "OrStatement")

        assert result["Statement"]["OrStatement"]["Statements"][0]["ByteMatchStatement"]["SearchString"] == "bot"

    def test_converts_and_statement_byte_match(self):
        """Test that AndStatement ByteMatchStatement is converted."""
        rule = {
            "Name": "and-rule",
            "Priority": 1,
            "Statement": {
                "AndStatement": {
                    "Statements": [
                        {
                            "ByteMatchStatement": {
                                "SearchString": b"test",
                                "FieldToMatch": {"UriPath": {}},
                                "TextTransformations": [{"Type": "NONE", "Priority": 0}],
                                "PositionalConstraint": "CONTAINS",
                            }
                        }
                    ]
                }
            },
        }

        result = nested_byte_values_to_strings(rule, "AndStatement")

        assert result["Statement"]["AndStatement"]["Statements"][0]["ByteMatchStatement"]["SearchString"] == "test"

    def test_converts_not_statement_byte_match(self):
        """Test that NotStatement ByteMatchStatement is converted."""
        rule = {
            "Name": "not-rule",
            "Priority": 1,
            "Statement": {
                "NotStatement": {
                    "Statements": [
                        {
                            "ByteMatchStatement": {
                                "SearchString": b"bad",
                                "FieldToMatch": {"UriPath": {}},
                                "TextTransformations": [{"Type": "NONE", "Priority": 0}],
                                "PositionalConstraint": "CONTAINS",
                            }
                        }
                    ]
                }
            },
        }

        result = nested_byte_values_to_strings(rule, "NotStatement")

        assert result["Statement"]["NotStatement"]["Statements"][0]["ByteMatchStatement"]["SearchString"] == "bad"

    def test_handles_rule_without_specified_statement(self):
        """Test that function handles rules without the specified statement type."""
        rule = {
            "Name": "simple-rule",
            "Priority": 1,
            "Statement": {
                "RateBasedStatement": {
                    "Limit": 5000,
                    "AggregateKeyType": "IP",
                }
            },
        }

        result = nested_byte_values_to_strings(rule, "OrStatement")

        # Should not modify the rule if it doesn't have the specified statement
        assert "RateBasedStatement" in result["Statement"]
        assert "OrStatement" not in result["Statement"]
