# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest

from ansible_collections.community.aws.plugins.modules.s3_lifecycle import filters_are_equal


@pytest.mark.parametrize(
    "filter1,filter2,result",
    [
        [None, None, True],
        [{}, {}, True],
        # Simple filters equal
        [{"Prefix": ""}, {"Prefix": ""}, True],
        [{"Prefix": "prefix/"}, {"Prefix": "prefix/"}, True],
        [{"ObjectSizeGreaterThan": 100}, {"ObjectSizeGreaterThan": 100}, True],
        [{"ObjectSizeLessThan": 100}, {"ObjectSizeLessThan": 100}, True],
        # One filter is empty
        [{"Prefix": ""}, {}, False],
        [{"ObjectSizeGreaterThan": 100}, {}, False],
        [{"ObjectSizeLessThan": 100}, {}, False],
        # One filter is None
        [{"Prefix": ""}, None, False],
        [{"ObjectSizeGreaterThan": 100}, None, False],
        [{"ObjectSizeLessThan": 100}, None, False],
        # Filters differ in a single key
        [{"Prefix": "prefix/"}, {"Prefix": "prefix2/"}, False],
        [{"ObjectSizeGreaterThan": 100}, {"ObjectSizeGreaterThan": 200}, False],
        [{"ObjectSizeLessThan": 100}, {"ObjectSizeLessThan": 200}, False],
        # While in theory, these would be equal.  We currently don't treat them as such and
        # a single key in the "And" dict is technically not valid.
        [{"Prefix": "prefix/"}, {"And": {"Prefix": "prefix/"}}, False],
        [{"ObjectSizeGreaterThan": 100}, {"And": {"ObjectSizeGreaterThan": 100}}, False],
        [{"ObjectSizeLessThan": 100}, {"And": {"ObjectSizeLessThan": 100}}, False],
    ],
)
def test_filters_are_equal_simple(filter1, filter2, result):
    assert filters_are_equal(filter1, filter2) is result
    assert filters_are_equal(filter2, filter1) is result  # pylint: disable=arguments-out-of-order


# Could be merged with the ones above, but naming will give a better idea of what's wrong
@pytest.mark.parametrize(
    "filter1,filter2,result",
    [
        # Equal
        [
            {"And": {"Prefix": "nested/", "ObjectSizeGreaterThan": 150, "ObjectSizeLessThan": 180}},
            {"And": {"Prefix": "nested/", "ObjectSizeGreaterThan": 150, "ObjectSizeLessThan": 180}},
            True,
        ],
        # Special case of "Prefix" missing == Prefix of ""
        [
            {"And": {"Prefix": "", "ObjectSizeGreaterThan": 150, "ObjectSizeLessThan": 180}},
            {"And": {"ObjectSizeGreaterThan": 150, "ObjectSizeLessThan": 180}},
            True,
        ],
        # Equal but with 2 of 3 "And" keys
        [
            {"And": {"ObjectSizeGreaterThan": 150, "ObjectSizeLessThan": 180}},
            {"And": {"ObjectSizeGreaterThan": 150, "ObjectSizeLessThan": 180}},
            True,
        ],
        [
            {"And": {"Prefix": "nested/", "ObjectSizeLessThan": 180}},
            {"And": {"Prefix": "nested/", "ObjectSizeLessThan": 180}},
            True,
        ],
        [
            {"And": {"Prefix": "nested/", "ObjectSizeGreaterThan": 150}},
            {"And": {"Prefix": "nested/", "ObjectSizeGreaterThan": 150}},
            True,
        ],
        # One key missing
        [
            {"And": {"Prefix": "nested/", "ObjectSizeGreaterThan": 150, "ObjectSizeLessThan": 180}},
            {"And": {"ObjectSizeGreaterThan": 150, "ObjectSizeLessThan": 180}},
            False,
        ],
        [
            {"And": {"Prefix": "nested/", "ObjectSizeGreaterThan": 150, "ObjectSizeLessThan": 180}},
            {"And": {"Prefix": "nested/", "ObjectSizeLessThan": 180}},
            False,
        ],
        [
            {"And": {"Prefix": "nested/", "ObjectSizeGreaterThan": 150, "ObjectSizeLessThan": 180}},
            {"And": {"Prefix": "nested/", "ObjectSizeGreaterThan": 150}},
            False,
        ],
        # One key different
        [
            {"And": {"Prefix": "nested/", "ObjectSizeGreaterThan": 150, "ObjectSizeLessThan": 180}},
            {"And": {"Prefix": "another/", "ObjectSizeGreaterThan": 150, "ObjectSizeLessThan": 180}},
            False,
        ],
        [
            {"And": {"Prefix": "nested/", "ObjectSizeGreaterThan": 150, "ObjectSizeLessThan": 180}},
            {"And": {"Prefix": "nested/", "ObjectSizeGreaterThan": 42, "ObjectSizeLessThan": 180}},
            False,
        ],
        [
            {"And": {"Prefix": "nested/", "ObjectSizeGreaterThan": 150, "ObjectSizeLessThan": 180}},
            {"And": {"Prefix": "nested/", "ObjectSizeGreaterThan": 150, "ObjectSizeLessThan": 90}},
            False,
        ],
        # Mixed with a non-and
        [
            {"Prefix": "test/"},
            {"And": {"Prefix": "nested/", "ObjectSizeGreaterThan": 150, "ObjectSizeLessThan": 90}},
            False,
        ],
    ],
)
def test_filters_are_equal_and(filter1, filter2, result):
    assert filters_are_equal(filter1, filter2) is result
    assert filters_are_equal(filter2, filter1) is result  # pylint: disable=arguments-out-of-order
