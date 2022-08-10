"""Test file for describe_cluster.py method"""

from __future__ import absolute_import, division, print_function

import pytest
from ansible.errors import AnsibleActionFail

__metaclass__ = type

import json
import sys

sys.path.append("./plugins/module_utils")

from describe_hsm import DescribeHsm, DescribeHsmValidator


@pytest.mark.parametrize("module_args, play_vars", [({}, {})], ids=["No arguments"])
def test_state_no_input(module_args, play_vars):
    """Testing DescribeHsmValidator.state method
    No inputs are provided, hence no exception is raised
    """
    DescribeHsmValidator(module_args, play_vars).state()


@pytest.mark.parametrize(
    "module_args, play_vars",
    [({"state": "CREATE_IN_PROGRESS"}, {}), ({"state": "UNINITIALIZED"}, {})],
    ids=[
        "Valid argument value CREATE_IN_PROGRESS",
        "Valid argument value UNINITIALIZED",
    ],
)
def test_state_valid_input(module_args, play_vars):
    """Testing DescribeHsmValidator.state method
    A valid input is provided, but no exception is raised
    """
    DescribeHsmValidator(module_args, play_vars).state()


@pytest.mark.parametrize(
    "module_args, play_vars, match",
    [
        (
            {"state": 90},
            {},
            "^Wrong\\s+type.*\\s+Provided:\\s+int",
        ),
        (
            {"state": True},
            {},
            "^Wrong\\s+type.*\\s+Provided:\\s+bool",
        ),
        (
            {"state": "initialized"},
            {},
            "^Wrong\\s+value.*\\s+Provided:\\s+initialized",
        ),
        (
            {"state": ["initialized"]},
            {},
            "^Wrong\\s+value.*\\s+Provided:\\s+\\['initialized'\\]",
        ),
    ],
    ids=[
        "Disallowed argument value 90",
        "Disallowed argument value True",
        "Disallowed argument value initialized type: string",
        "Disallowed argument value initialized type: list",
    ],
)
def test_state_exception(module_args, play_vars, match):
    """Testing DescribeHsmValidator.state method
    Disallowed values are provided as an input, and AnsibleActionFail exception is raised
    """
    with pytest.raises(AnsibleActionFail, match=rf"{match}"):
        DescribeHsmValidator(module_args, play_vars).state()


#################################################################################################


@pytest.mark.parametrize(
    "module_args, play_vars",
    [
        (
            {
                "state": "UNINITIALIZED",
                "aws_access_key": "TESTAWSACCESSKEY",
                "aws_secret_key": "testawssecretkey",
                "region": "us-east-2",
            },
            {},
        )
    ],
    ids=["Full validate"],
)
def test_validate(module_args, play_vars, mocker, mock_configparser_sections):
    """Testing DescribeHsmValidator.validate method"""
    DescribeHsmValidator(module_args, play_vars).validate()


#################################################################################################


@pytest.mark.parametrize(
    "module_args, play_vars",
    [
        (
            {
                "state": "UNINITIALIZED",
                "aws_access_key": "TESTAWSACCESSKEY",
                "aws_secret_key": "testawssecretkey",
                "region": "us-east-2",
            },
            {},
        )
    ],
    ids=["DescribeHsm init"],
)
def test_DescribeHsm_init(
    module_args, play_vars, mock_boto3, mock_configparser_sections
):
    """Testing mock_DescribeHsm.__init__ method"""
    hsm = DescribeHsm(module_args, play_vars)
    assert hsm.module_args == module_args
    assert hsm.play_vars == play_vars


def test_DescribeHsm_get(absoulte_path, mock_DescribeHsm):
    """Testing mock_DescribeHsm.__init__ method"""

    hsm = mock_DescribeHsm
    hsm.module_args["cluster_id"] = "cluster-test4"
    assert hsm.get() == json.load(open(f"{absoulte_path}/mocks/hsms.json"))
