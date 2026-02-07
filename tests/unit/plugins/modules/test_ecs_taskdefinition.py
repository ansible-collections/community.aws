# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

__metaclass__ = type

import pytest

from ansible_collections.community.aws.plugins.modules.ecs_taskdefinition import _right_has_values_of_left


class TestRightHasValuesOfLeft:
    def test_exact_match(self):
        left = {"name": "web", "image": "nginx"}
        right = {"name": "web", "image": "nginx"}
        assert _right_has_values_of_left(left, right) is True

    def test_left_subset_of_right_extra_truthy_rejected(self):
        # Right has extra truthy keys not in left — the function rejects these
        left = {"name": "web"}
        right = {"name": "web", "image": "nginx", "cpu": 256}
        assert _right_has_values_of_left(left, right) is False

    def test_left_subset_of_right_extra_falsy_accepted(self):
        # Right has extra keys that are falsy — accepted
        left = {"name": "web"}
        right = {"name": "web", "links": [], "cpu": 0}
        assert _right_has_values_of_left(left, right) is True

    def test_scalar_value_mismatch(self):
        left = {"name": "web", "image": "nginx"}
        right = {"name": "web", "image": "httpd"}
        assert _right_has_values_of_left(left, right) is False

    def test_left_has_key_right_doesnt(self):
        left = {"name": "web", "image": "nginx"}
        right = {"name": "web"}
        assert _right_has_values_of_left(left, right) is False

    def test_empty_left_with_truthy_right(self):
        # Empty left, but right has truthy values — rejected by the second loop
        assert _right_has_values_of_left({}, {"name": "web"}) is False

    def test_empty_left_empty_right(self):
        assert _right_has_values_of_left({}, {}) is True

    def test_falsy_value_in_left_missing_in_right(self):
        # When left has a falsy value (0, "", [], None) and right doesn't have the key,
        # the function treats them as equivalent
        left = {"name": "web", "cpu": 0}
        right = {"name": "web"}
        assert _right_has_values_of_left(left, right) is True

    def test_list_match_same_order(self):
        left = {"ports": [{"containerPort": 80}, {"containerPort": 443}]}
        right = {"ports": [{"containerPort": 80}, {"containerPort": 443}]}
        assert _right_has_values_of_left(left, right) is True

    def test_list_match_different_order(self):
        left = {"ports": [{"containerPort": 443}, {"containerPort": 80}]}
        right = {"ports": [{"containerPort": 80}, {"containerPort": 443}]}
        assert _right_has_values_of_left(left, right) is True

    def test_list_length_mismatch(self):
        left = {"ports": [{"containerPort": 80}]}
        right = {"ports": [{"containerPort": 80}, {"containerPort": 443}]}
        assert _right_has_values_of_left(left, right) is False

    def test_list_element_mismatch(self):
        # Regression test: list elements that don't match must return False
        left = {"ports": [{"a": 1}]}
        right = {"ports": [{"a": 2}]}
        assert _right_has_values_of_left(left, right) is False

    def test_port_mapping_without_protocol_matches_default(self):
        # Left omits 'protocol', right has 'protocol: tcp' (the default) — should match
        left = {"portMappings": [{"containerPort": 80}]}
        right = {"portMappings": [{"containerPort": 80, "protocol": "tcp"}]}
        assert _right_has_values_of_left(left, right) is True

    def test_port_mapping_mismatch_despite_protocol_default(self):
        # hostPort differs — should NOT match even after protocol default fill-in
        left = {"portMappings": [{"containerPort": 80, "hostPort": 8080}]}
        right = {"portMappings": [{"containerPort": 80, "hostPort": 80, "protocol": "tcp"}]}
        assert _right_has_values_of_left(left, right) is False

    def test_essential_key_default_true(self):
        # Right has 'essential: True' that left doesn't — should be accepted as a default
        left = {"name": "web"}
        right = {"name": "web", "essential": True}
        assert _right_has_values_of_left(left, right) is True

    def test_right_has_extra_truthy_non_essential_key(self):
        # Right has a truthy key not in left (and it's not 'essential') — should fail
        left = {"name": "web"}
        right = {"name": "web", "memory": 512}
        assert _right_has_values_of_left(left, right) is False
