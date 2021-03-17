# (c) 2021 Red Hat Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import pytest

from ansible_collections.community.aws.plugins.modules.ec2_asg_tag import (
    compare_asg_tags,
    tag_list_to_dict,
    to_boto3_tag_list,
)


def as_tags(tags):
    return tag_list_to_dict(to_boto3_tag_list(tags, 'asg-test'))


def test_compare_asg_tags__add_tag():
    current_tags = as_tags([
        {'env': 'production', 'propagate_at_launch': True},
    ])
    new_tags = as_tags([
        {'role': 'web', 'propagate_at_launch': True},
    ])

    add, remove = compare_asg_tags(current_tags, new_tags, purge_tags=True)
    assert len(add) == 1
    assert 'role' in add
    assert len(remove) == 1
    assert 'env' in remove

    add, remove = compare_asg_tags(current_tags, new_tags, purge_tags=False)
    assert len(add) == 1
    assert 'role' in add
    assert len(remove) == 0


def test_compare_asg_tags__existing_tag():
    current_tags = as_tags([
        {'env': 'production', 'propagate_at_launch': True},
        {'role': 'web', 'propagate_at_launch': True},
    ])
    new_tags = as_tags([
        {'role': 'web', 'propagate_at_launch': True},
    ])

    add, remove = compare_asg_tags(current_tags, new_tags, purge_tags=True)
    assert len(add) == 0
    assert len(remove) == 1
    assert 'env' in remove

    add, remove = compare_asg_tags(current_tags, new_tags, purge_tags=False)
    assert len(add) == 0
    assert len(remove) == 0


def test_compare_asg_tags__remove_tag():
    current_tags = as_tags([
        {'env': 'production', 'propagate_at_launch': True},
        {'role': 'web', 'propagate_at_launch': True},
    ])
    new_tags = as_tags([])

    add, remove = compare_asg_tags(current_tags, new_tags, purge_tags=True)
    assert len(add) == 0
    assert len(remove) == 2
    assert 'role' in remove

    add, remove = compare_asg_tags(current_tags, new_tags, purge_tags=False)
    assert len(add) == 0
    assert len(remove) == 0


def test_compare_asg_tags__empty_value():
    current_tags = as_tags([
        {'env': 'production', 'propagate_at_launch': True},
        {'role': 'web', 'propagate_at_launch': True},
    ])
    new_tags = as_tags([
        {'role': None},
    ])

    add, remove = compare_asg_tags(current_tags, new_tags, purge_tags=True)
    assert len(add) == 1
    assert 'role' in add
    assert len(remove) == 1
    assert 'env' in remove

    add, remove = compare_asg_tags(current_tags, new_tags, purge_tags=False)
    assert len(add) == 1
    assert 'role' in add
    assert len(remove) == 0


def test_compare_asg_tags__update_propagate():
    current_tags = as_tags([
        {'env': 'production', 'propagate_at_launch': True},
        {'role': 'web', 'propagate_at_launch': False},
    ])
    new_tags = as_tags([
        {'role': 'web', 'propagate_at_launch': True},
    ])

    add, remove = compare_asg_tags(current_tags, new_tags, purge_tags=True)
    assert len(add) == 1
    assert 'role' in add
    assert len(remove) == 1
    assert 'env' in remove

    add, remove = compare_asg_tags(current_tags, new_tags, purge_tags=False)
    assert len(add) == 1
    assert 'role' in add
    assert len(remove) == 0
