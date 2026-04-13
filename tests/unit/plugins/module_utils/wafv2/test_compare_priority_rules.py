# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

__metaclass__ = type

from ansible_collections.community.aws.plugins.module_utils.wafv2 import compare_priority_rules


class TestComparePriorityRulesWithRateBasedDefaults:
    """Test that compare_priority_rules correctly applies rate_based_statement defaults."""

    def test_idempotency_with_default_evaluation_window_sec(self):
        """Test that rules are considered equal when evaluation_window_sec matches AWS default."""
        # User's rule (no evaluation_window_sec specified)
        requested_rules = [
            {
                "Name": "rate-limit-rule",
                "Priority": 1,
                "Statement": {
                    "RateBasedStatement": {
                        "Limit": 5000,
                        "AggregateKeyType": "IP",
                    }
                },
                "VisibilityConfig": {
                    "SampledRequestsEnabled": True,
                    "CloudWatchMetricsEnabled": True,
                    "MetricName": "rate-limit",
                },
            }
        ]

        # AWS returns with default evaluation_window_sec
        existing_rules = [
            {
                "Name": "rate-limit-rule",
                "Priority": 1,
                "Statement": {
                    "RateBasedStatement": {
                        "Limit": 5000,
                        "AggregateKeyType": "IP",
                        "EvaluationWindowSec": 300,
                    }
                },
                "VisibilityConfig": {
                    "SampledRequestsEnabled": True,
                    "CloudWatchMetricsEnabled": True,
                    "MetricName": "rate-limit",
                },
            }
        ]

        diff, merged_rules = compare_priority_rules(existing_rules, requested_rules, purge_rules=True, state="present")

        # Should not detect a difference because the default is applied
        assert diff is False
        assert len(merged_rules) == 1

    def test_detects_difference_with_non_default_evaluation_window_sec(self):
        """Test that changes are detected when evaluation_window_sec differs from default."""
        # User's rule with custom evaluation_window_sec
        requested_rules = [
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
                "VisibilityConfig": {
                    "SampledRequestsEnabled": True,
                    "CloudWatchMetricsEnabled": True,
                    "MetricName": "rate-limit",
                },
            }
        ]

        # AWS returns with default evaluation_window_sec
        existing_rules = [
            {
                "Name": "rate-limit-rule",
                "Priority": 1,
                "Statement": {
                    "RateBasedStatement": {
                        "Limit": 5000,
                        "AggregateKeyType": "IP",
                        "EvaluationWindowSec": 300,
                    }
                },
                "VisibilityConfig": {
                    "SampledRequestsEnabled": True,
                    "CloudWatchMetricsEnabled": True,
                    "MetricName": "rate-limit",
                },
            }
        ]

        diff, merged_rules = compare_priority_rules(existing_rules, requested_rules, purge_rules=True, state="present")

        # Should detect a difference because 600 != 300
        assert diff is True

    def test_idempotency_with_multiple_rate_based_rules(self):
        """Test idempotency with multiple rate-based rules."""
        requested_rules = [
            {
                "Name": "rule-1",
                "Priority": 1,
                "Statement": {
                    "RateBasedStatement": {
                        "Limit": 5000,
                        "AggregateKeyType": "IP",
                    }
                },
                "VisibilityConfig": {
                    "SampledRequestsEnabled": True,
                    "CloudWatchMetricsEnabled": True,
                    "MetricName": "rule-1",
                },
            },
            {
                "Name": "rule-2",
                "Priority": 2,
                "Statement": {
                    "RateBasedStatement": {
                        "Limit": 1000,
                        "AggregateKeyType": "FORWARDED_IP",
                        "EvaluationWindowSec": 120,
                    }
                },
                "VisibilityConfig": {
                    "SampledRequestsEnabled": True,
                    "CloudWatchMetricsEnabled": True,
                    "MetricName": "rule-2",
                },
            },
        ]

        existing_rules = [
            {
                "Name": "rule-1",
                "Priority": 1,
                "Statement": {
                    "RateBasedStatement": {
                        "Limit": 5000,
                        "AggregateKeyType": "IP",
                        "EvaluationWindowSec": 300,
                    }
                },
                "VisibilityConfig": {
                    "SampledRequestsEnabled": True,
                    "CloudWatchMetricsEnabled": True,
                    "MetricName": "rule-1",
                },
            },
            {
                "Name": "rule-2",
                "Priority": 2,
                "Statement": {
                    "RateBasedStatement": {
                        "Limit": 1000,
                        "AggregateKeyType": "FORWARDED_IP",
                        "EvaluationWindowSec": 120,
                    }
                },
                "VisibilityConfig": {
                    "SampledRequestsEnabled": True,
                    "CloudWatchMetricsEnabled": True,
                    "MetricName": "rule-2",
                },
            },
        ]

        diff, merged_rules = compare_priority_rules(existing_rules, requested_rules, purge_rules=True, state="present")

        assert diff is False
        assert len(merged_rules) == 2

    def test_idempotency_with_mixed_rule_types(self):
        """Test that non-rate-based rules are unaffected by the defaults when mixed with rate-based rules."""
        requested_rules = [
            {
                "Name": "managed-rule",
                "Priority": 1,
                "OverrideAction": {"None": {}},
                "Statement": {
                    "ManagedRuleGroupStatement": {
                        "VendorName": "AWS",
                        "Name": "AWSManagedRulesCommonRuleSet",
                    }
                },
                "VisibilityConfig": {
                    "SampledRequestsEnabled": True,
                    "CloudWatchMetricsEnabled": True,
                    "MetricName": "managed-rule",
                },
            },
            {
                "Name": "rate-limit-rule",
                "Priority": 2,
                "Statement": {
                    "RateBasedStatement": {
                        "Limit": 5000,
                        "AggregateKeyType": "IP",
                    }
                },
                "VisibilityConfig": {
                    "SampledRequestsEnabled": True,
                    "CloudWatchMetricsEnabled": True,
                    "MetricName": "rate-limit",
                },
            },
        ]

        existing_rules = [
            {
                "Name": "managed-rule",
                "Priority": 1,
                "OverrideAction": {"None": {}},
                "Statement": {
                    "ManagedRuleGroupStatement": {
                        "VendorName": "AWS",
                        "Name": "AWSManagedRulesCommonRuleSet",
                    }
                },
                "VisibilityConfig": {
                    "SampledRequestsEnabled": True,
                    "CloudWatchMetricsEnabled": True,
                    "MetricName": "managed-rule",
                },
            },
            {
                "Name": "rate-limit-rule",
                "Priority": 2,
                "Statement": {
                    "RateBasedStatement": {
                        "Limit": 5000,
                        "AggregateKeyType": "IP",
                        "EvaluationWindowSec": 300,
                    }
                },
                "VisibilityConfig": {
                    "SampledRequestsEnabled": True,
                    "CloudWatchMetricsEnabled": True,
                    "MetricName": "rate-limit",
                },
            },
        ]

        diff, merged_rules = compare_priority_rules(existing_rules, requested_rules, purge_rules=True, state="present")

        assert diff is False
        assert len(merged_rules) == 2
