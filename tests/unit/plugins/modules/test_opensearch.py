# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

__metaclass__ = type

import functools

from ansible_collections.community.aws.plugins.module_utils.opensearch import compare_domain_versions
from ansible_collections.community.aws.plugins.module_utils.opensearch import parse_version


def test_parse_version():
    test_versions = [
        ["Elasticsearch_5.5", {"engine_type": "Elasticsearch", "major": 5, "minor": 5}],
        ["Elasticsearch_7.1", {"engine_type": "Elasticsearch", "major": 7, "minor": 1}],
        ["Elasticsearch_7.10", {"engine_type": "Elasticsearch", "major": 7, "minor": 10}],
        ["OpenSearch_1.0", {"engine_type": "OpenSearch", "major": 1, "minor": 0}],
        ["OpenSearch_1.1", {"engine_type": "OpenSearch", "major": 1, "minor": 1}],
        ["OpenSearch_a.b", None],
        ["OpenSearch_1.b", None],
        ["OpenSearch_1-1", None],
        ["OpenSearch_1.1.2", None],
        ["OpenSearch_foo_1.1", None],
        ["OpenSearch_1", None],
        ["OpenSearch-1.0", None],
        ["Foo_1.0", None],
    ]
    for expected in test_versions:
        ret = parse_version(expected[0])
        if ret != expected[1]:
            raise AssertionError(f"parse_version({expected[0]} returned {ret}, expected {expected[1]}")


def test_version_compare():
    test_versions = [
        ["Elasticsearch_5.5", "Elasticsearch_5.5", 0],
        ["Elasticsearch_5.5", "Elasticsearch_7.1", -1],
        ["Elasticsearch_7.1", "Elasticsearch_7.1", 0],
        ["Elasticsearch_7.1", "Elasticsearch_7.2", -1],
        ["Elasticsearch_7.1", "Elasticsearch_7.10", -1],
        ["Elasticsearch_7.2", "Elasticsearch_7.10", -1],
        ["Elasticsearch_7.10", "Elasticsearch_7.2", 1],
        ["Elasticsearch_7.2", "Elasticsearch_5.5", 1],
        ["Elasticsearch_7.2", "OpenSearch_1.0", -1],
        ["Elasticsearch_7.2", "OpenSearch_1.1", -1],
        ["OpenSearch_1.1", "OpenSearch_1.1", 0],
        ["OpenSearch_1.0", "OpenSearch_1.1", -1],
        ["OpenSearch_1.1", "OpenSearch_1.0", 1],
        ["foo_1.1", "OpenSearch_1.0", -1],
        ["Elasticsearch_5.5", "foo_1.0", 1],
    ]
    for v in test_versions:
        ret = compare_domain_versions(v[0], v[1])
        if ret != v[2]:
            raise AssertionError(f"compare({v[0]}, {v[1]} returned {ret}, expected {v[2]}")


def test_sort_versions():
    input_versions = [
        "Elasticsearch_5.6",
        "Elasticsearch_5.5",
        "Elasticsearch_7.10",
        "Elasticsearch_7.2",
        "foo_10.5",
        "OpenSearch_1.1",
        "OpenSearch_1.0",
        "Elasticsearch_7.3",
    ]
    expected_versions = [
        "foo_10.5",
        "Elasticsearch_5.5",
        "Elasticsearch_5.6",
        "Elasticsearch_7.2",
        "Elasticsearch_7.3",
        "Elasticsearch_7.10",
        "OpenSearch_1.0",
        "OpenSearch_1.1",
    ]
    input_versions = sorted(input_versions, key=functools.cmp_to_key(compare_domain_versions))
    if input_versions != expected_versions:
        raise AssertionError(f"Expected {expected_versions}, got {input_versions}")
