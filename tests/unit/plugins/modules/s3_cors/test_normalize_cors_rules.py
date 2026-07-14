# -*- coding: utf-8 -*-

# Copyright: (c) 2026, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest

from ansible_collections.community.aws.plugins.modules.s3_cors import normalize_cors_rules


@pytest.mark.parametrize(
    "rules,expected",
    [
        [None, []],
        [[], []],
    ],
)
def test_normalize_cors_rules_empty(rules, expected):
    assert normalize_cors_rules(rules) == expected


@pytest.mark.parametrize(
    "rules,expected",
    [
        # List values within a rule should be sorted
        [
            [{"AllowedMethods": ["POST", "GET"], "AllowedOrigins": ["http://b.com", "http://a.com"]}],
            [{"AllowedMethods": ["GET", "POST"], "AllowedOrigins": ["http://a.com", "http://b.com"]}],
        ],
        # Non-list values (like MaxAgeSeconds) should pass through unchanged
        [
            [{"AllowedMethods": ["GET"], "AllowedOrigins": ["*"], "MaxAgeSeconds": 3600}],
            [{"AllowedMethods": ["GET"], "AllowedOrigins": ["*"], "MaxAgeSeconds": 3600}],
        ],
        # ExposeHeaders should also be sorted
        [
            [{"AllowedMethods": ["GET"], "AllowedOrigins": ["*"], "ExposeHeaders": ["x-amz-request-id", "x-amz-id-2"]}],
            [{"AllowedMethods": ["GET"], "AllowedOrigins": ["*"], "ExposeHeaders": ["x-amz-id-2", "x-amz-request-id"]}],
        ],
    ],
)
def test_normalize_cors_rules_single_rule(rules, expected):
    assert normalize_cors_rules(rules) == expected


@pytest.mark.parametrize(
    "rules_a,rules_b",
    [
        # Same rules in different order should normalize identically
        [
            [
                {"AllowedMethods": ["GET"], "AllowedOrigins": ["http://b.com"]},
                {"AllowedMethods": ["POST"], "AllowedOrigins": ["http://a.com"]},
            ],
            [
                {"AllowedMethods": ["POST"], "AllowedOrigins": ["http://a.com"]},
                {"AllowedMethods": ["GET"], "AllowedOrigins": ["http://b.com"]},
            ],
        ],
    ],
)
def test_normalize_cors_rules_deterministic_sort(rules_a, rules_b):
    assert normalize_cors_rules(rules_a) == normalize_cors_rules(rules_b)


@pytest.mark.parametrize(
    "rules_a,rules_b",
    [
        # Dict key ordering should not matter
        [
            [{"AllowedOrigins": ["*"], "AllowedMethods": ["GET"]}],
            [{"AllowedMethods": ["GET"], "AllowedOrigins": ["*"]}],
        ],
        # Multiple rules with different key orderings and list orderings
        [
            [
                {"AllowedOrigins": ["*"], "AllowedMethods": ["GET"], "MaxAgeSeconds": 100},
                {"AllowedMethods": ["POST", "PUT"], "AllowedOrigins": ["http://example.com"]},
            ],
            [
                {"AllowedOrigins": ["http://example.com"], "AllowedMethods": ["PUT", "POST"]},
                {"MaxAgeSeconds": 100, "AllowedMethods": ["GET"], "AllowedOrigins": ["*"]},
            ],
        ],
    ],
)
def test_normalize_cors_rules_key_order_independent(rules_a, rules_b):
    assert normalize_cors_rules(rules_a) == normalize_cors_rules(rules_b)


def test_normalize_cors_rules_max_age_seconds_int():
    rules = [{"AllowedMethods": ["GET"], "AllowedOrigins": ["*"], "MaxAgeSeconds": 30000}]
    result = normalize_cors_rules(rules)
    assert result[0]["MaxAgeSeconds"] == 30000
    assert isinstance(result[0]["MaxAgeSeconds"], int)
