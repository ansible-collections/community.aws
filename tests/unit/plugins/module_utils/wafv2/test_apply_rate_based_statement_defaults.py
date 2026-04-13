# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

__metaclass__ = type

from ansible_collections.community.aws.plugins.module_utils.wafv2 import apply_rate_based_statement_defaults


class TestApplyRateBasedStatementDefaults:
    """Test the apply_rate_based_statement_defaults function."""

    def test_adds_default_evaluation_window_sec_when_missing(self):
        """Test that evaluation_window_sec is added with default value 300 when not present."""
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

        result = apply_rate_based_statement_defaults(rules)

        assert result[0]["Statement"]["RateBasedStatement"]["EvaluationWindowSec"] == 300
        assert result[0]["Statement"]["RateBasedStatement"]["Limit"] == 5000
        assert result[0]["Statement"]["RateBasedStatement"]["AggregateKeyType"] == "IP"

    def test_preserves_existing_evaluation_window_sec(self):
        """Test that existing evaluation_window_sec values are not overwritten."""
        rules = [
            {
                "Name": "rate-limit-rule",
                "Priority": 1,
                "Statement": {
                    "RateBasedStatement": {
                        "Limit": 5000,
                        "AggregateKeyType": "IP",
                        "EvaluationWindowSec": 600,
                    }
                },
            }
        ]

        result = apply_rate_based_statement_defaults(rules)

        assert result[0]["Statement"]["RateBasedStatement"]["EvaluationWindowSec"] == 600

    def test_handles_multiple_rules(self):
        """Test that function handles multiple rules correctly."""
        rules = [
            {
                "Name": "rule-without-eval-window",
                "Priority": 1,
                "Statement": {
                    "RateBasedStatement": {
                        "Limit": 5000,
                        "AggregateKeyType": "IP",
                    }
                },
            },
            {
                "Name": "rule-with-eval-window",
                "Priority": 2,
                "Statement": {
                    "RateBasedStatement": {
                        "Limit": 1000,
                        "AggregateKeyType": "FORWARDED_IP",
                        "EvaluationWindowSec": 120,
                    }
                },
            },
        ]

        result = apply_rate_based_statement_defaults(rules)

        assert result[0]["Statement"]["RateBasedStatement"]["EvaluationWindowSec"] == 300
        assert result[1]["Statement"]["RateBasedStatement"]["EvaluationWindowSec"] == 120

    def test_ignores_non_rate_based_statements(self):
        """Test that non-rate-based statements are not modified."""
        rules = [
            {
                "Name": "byte-match-rule",
                "Priority": 1,
                "Statement": {
                    "ByteMatchStatement": {
                        "SearchString": "test",
                        "FieldToMatch": {"UriPath": {}},
                        "TextTransformations": [{"Type": "NONE", "Priority": 0}],
                        "PositionalConstraint": "CONTAINS",
                    }
                },
            }
        ]

        result = apply_rate_based_statement_defaults(rules)

        # Should not add EvaluationWindowSec to non-rate-based statements
        assert "RateBasedStatement" not in result[0]["Statement"]
        assert "ByteMatchStatement" in result[0]["Statement"]

    def test_handles_empty_rules_list(self):
        """Test that function handles empty rules list."""
        rules = []

        result = apply_rate_based_statement_defaults(rules)

        assert result == []

    def test_handles_rule_without_statement(self):
        """Test that function handles rules without Statement field."""
        rules = [
            {
                "Name": "incomplete-rule",
                "Priority": 1,
            }
        ]

        result = apply_rate_based_statement_defaults(rules)

        # Should not crash, just return the rule as-is
        assert len(result) == 1
        assert result[0]["Name"] == "incomplete-rule"

    def test_does_not_modify_original_rules(self):
        """Test that the function returns the same list object (modifies in place)."""
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

        result = apply_rate_based_statement_defaults(rules)

        # The function modifies in place and returns the same list
        assert result is rules
        assert result[0]["Statement"]["RateBasedStatement"]["EvaluationWindowSec"] == 300
