# -*- coding: utf-8 -*-

# Copyright: (c) 2025, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest

from ansible_collections.community.aws.plugins.module_utils.dict_transformations import rename_dict_keys


@pytest.mark.parametrize(
    "input_value, expected_result",
    [
        ({"items": 0}, {"elements": 0}),
        ({"elements": 0}, {"elements": 0}),
        ([{"items": 0}], [{"elements": 0}]),
        (
            {"origins": {"items": ["path1", "path2"], "config": True}},
            {"origins": {"elements": ["path1", "path2"], "config": True}},
        ),
    ],
)
def test_rename_dict_keys(input_value, expected_result):
    assert rename_dict_keys(input_value, "items", "elements") == expected_result
