# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest

from ansible_collections.community.aws.plugins.modules.route53_wait import detect_task_results

_SINGLE_RESULT_SUCCESS = {
    "changed": True,
    "diff": {},
    "failed": False,
    "wait_id": None,
}

_SINGLE_RESULT_FAILED = {
    "changed": False,
    "failed": True,
    "msg": "value of type must be one of: A, AAAA, CAA, CNAME, MX, NS, PTR, SOA, SPF, SRV, TXT, got: bar",
}

_MULTI_RESULT_SUCCESS = {
    "ansible_loop_var": "item",
    "changed": True,
    "diff": {},
    "failed": False,
    "invocation": {
        "module_args": {
            "access_key": "asdf",
            "alias": None,
            "alias_evaluate_target_health": False,
            "alias_hosted_zone_id": None,
            "aws_access_key": "asdf",
            "aws_ca_bundle": None,
            "aws_config": None,
            "aws_secret_key": "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER",
            "debug_botocore_endpoint_logs": False,
            "endpoint_url": None,
            "failover": None,
            "geo_location": None,
            "health_check": None,
            "hosted_zone_id": None,
            "identifier": None,
            "overwrite": True,
            "private_zone": False,
            "profile": None,
            "record": "foo.example.org",
            "region": None,
            "retry_interval": 500,
            "secret_key": "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER",
            "session_token": None,
            "state": "present",
            "ttl": 300,
            "type": "TXT",
            "validate_certs": True,
            "value": ["foo"],
            "vpc_id": None,
            "wait": False,
            "wait_timeout": 300,
            "weight": None,
            "zone": "example.org",
        },
    },
    "item": {"record": "foo.example.org", "value": "foo"},
    "wait_id": None,
}

_MULTI_RESULT_FAILED = {
    "ansible_loop_var": "item",
    "changed": False,
    "failed": True,
    "invocation": {
        "module_args": {
            "access_key": "asdf",
            "alias": None,
            "alias_evaluate_target_health": False,
            "alias_hosted_zone_id": None,
            "aws_access_key": "asdf",
            "aws_ca_bundle": None,
            "aws_config": None,
            "aws_secret_key": "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER",
            "debug_botocore_endpoint_logs": False,
            "endpoint_url": None,
            "failover": None,
            "geo_location": None,
            "health_check": None,
            "hosted_zone_id": None,
            "identifier": None,
            "overwrite": True,
            "private_zone": False,
            "profile": None,
            "record": "foo.example.org",
            "region": None,
            "retry_interval": 500,
            "secret_key": "VALUE_SPECIFIED_IN_NO_LOG_PARAMETER",
            "session_token": None,
            "state": "present",
            "ttl": 300,
            "type": "bar",
            "validate_certs": True,
            "value": ["foo"],
            "vpc_id": None,
            "wait": False,
            "wait_timeout": 300,
            "weight": None,
            "zone": "example.org",
        },
    },
    "item": {"record": "foo.example.org", "value": "foo"},
    "msg": "value of type must be one of: A, AAAA, CAA, CNAME, MX, NS, PTR, SOA, SPF, SRV, TXT, got: bar",
}


DETECT_TASK_RESULTS_DATA = [
    [
        _SINGLE_RESULT_SUCCESS,
        [
            (
                "",
                _SINGLE_RESULT_SUCCESS,
            ),
        ],
    ],
    [
        {
            "changed": True,
            "msg": "All items completed",
            "results": [
                _MULTI_RESULT_SUCCESS,
            ],
            "skipped": False,
        },
        [
            (
                " for result #1",
                _MULTI_RESULT_SUCCESS,
            ),
        ],
    ],
    [
        _SINGLE_RESULT_FAILED,
        [
            (
                "",
                _SINGLE_RESULT_FAILED,
            ),
        ],
    ],
    [
        {
            "changed": False,
            "failed": True,
            "msg": "One or more items failed",
            "results": [
                _MULTI_RESULT_FAILED,
            ],
            "skipped": False,
        },
        [
            (
                " for result #1",
                _MULTI_RESULT_FAILED,
            ),
        ],
    ],
]


@pytest.mark.parametrize(
    "input, expected",
    DETECT_TASK_RESULTS_DATA,
)
def test_detect_task_results(input, expected):
    assert list(detect_task_results(input)) == expected


DETECT_TASK_RESULTS_FAIL_DATA = [
    [
        {},
        "missing changed key",
        [],
    ],
    [
        {"changed": True},
        "missing failed key",
        [],
    ],
    [
        {"results": None},
        "missing changed key",
        [],
    ],
    [
        {"results": None, "changed": True, "msg": "foo"},
        "missing skipped key",
        [],
    ],
    [
        {"results": None, "changed": True, "msg": "foo", "skipped": False},
        "results is present, but not a list",
        [],
    ],
    [
        {"results": [None], "changed": True, "msg": "foo", "skipped": False},
        "result 1 is not a dictionary",
        [],
    ],
    [
        {"results": [{}], "changed": True, "msg": "foo", "skipped": False},
        "missing changed key for result 1",
        [],
    ],
    [
        {
            "results": [{"changed": True, "failed": False, "ansible_loop_var": "item", "invocation": {}}, {}],
            "changed": True,
            "msg": "foo",
            "skipped": False,
        },
        "missing changed key for result 2",
        [(" for result #1", {"changed": True, "failed": False, "ansible_loop_var": "item", "invocation": {}})],
    ],
]


@pytest.mark.parametrize(
    "input, expected_exc, expected_result",
    DETECT_TASK_RESULTS_FAIL_DATA,
)
def test_detect_task_fail_results(input, expected_exc, expected_result):
    result = []
    with pytest.raises(ValueError) as exc:
        for res in detect_task_results(input):
            result.append(res)

    print(exc.value.args[0])
    assert expected_exc == exc.value.args[0]
    print(result)
    assert expected_result == result
