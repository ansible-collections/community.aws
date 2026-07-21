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
        [
            [{"AllowedMethods": ["POST", "GET"], "AllowedOrigins": ["http://b.example.com", "http://a.example.com"]}],
            [{"AllowedMethods": ["GET", "POST"], "AllowedOrigins": ["http://a.example.com", "http://b.example.com"]}],
        ],
    ],
)
def test_normalize_cors_rules_sorts_list_values(rules, expected):
    assert normalize_cors_rules(rules) == expected


def test_normalize_cors_rules_preserves_non_list_values():
    rules = [{"AllowedMethods": ["GET"], "AllowedOrigins": ["*"], "MaxAgeSeconds": 30000}]
    result = normalize_cors_rules(rules)
    assert result[0]["MaxAgeSeconds"] == 30000
    assert isinstance(result[0]["MaxAgeSeconds"], int)


@pytest.mark.parametrize(
    "rules_a,rules_b",
    [
        # Same rules in different list positions should normalize identically
        [
            [
                {"AllowedMethods": ["GET"], "AllowedOrigins": ["http://b.example.com"]},
                {"AllowedMethods": ["POST"], "AllowedOrigins": ["http://a.example.com"]},
            ],
            [
                {"AllowedMethods": ["POST"], "AllowedOrigins": ["http://a.example.com"]},
                {"AllowedMethods": ["GET"], "AllowedOrigins": ["http://b.example.com"]},
            ],
        ],
        # Different rule positions combined with unsorted list values
        [
            [
                {"AllowedOrigins": ["*"], "AllowedMethods": ["GET"], "MaxAgeSeconds": 100},
                {"AllowedMethods": ["POST", "PUT"], "AllowedOrigins": ["http://a.example.com"]},
            ],
            [
                {"AllowedOrigins": ["http://a.example.com"], "AllowedMethods": ["PUT", "POST"]},
                {"AllowedMethods": ["GET"], "AllowedOrigins": ["*"], "MaxAgeSeconds": 100},
            ],
        ],
    ],
)
def test_normalize_cors_rules_deterministic_order(rules_a, rules_b):
    assert normalize_cors_rules(rules_a) == normalize_cors_rules(rules_b)
