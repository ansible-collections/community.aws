"""Test file for describe_cluster.py method"""

from __future__ import absolute_import, division, print_function

import pytest
from ansible.errors import AnsibleActionFail

__metaclass__ = type

import sys

sys.path.append("./plugins/module_utils")

from constants import *
from describe_cluster import DescribeHsmCluster, DescribeHsmClusterValidator


@pytest.mark.parametrize("module_args, play_vars", [({}, {})], ids=["No arguments"])
def test_state_no_input(module_args, play_vars):
    """Testing DescribeHsmClusterValidator.state method
    No inputs are provided, hence no exception is raised
    """
    DescribeHsmClusterValidator(module_args, play_vars).state()


@pytest.mark.parametrize(
    "module_args, play_vars",
    [({"state": "CREATE_IN_PROGRESS"}, {}), ({"state": "UNINITIALIZED"}, {})],
    ids=[
        "Valid argument value CREATE_IN_PROGRESS",
        "Valid argument value UNINITIALIZED",
    ],
)
def test_state_valid_input(module_args, play_vars):
    """Testing DescribeHsmClusterValidator.state method
    A valid input is provided, but no exception is raised
    """
    DescribeHsmClusterValidator(module_args, play_vars).state()


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
    """Testing DescribeHsmClusterValidator.state method
    Disallowed values are provided as an input, and AnsibleActionFail exception is raised
    """
    with pytest.raises(AnsibleActionFail, match=rf"{match}"):
        DescribeHsmClusterValidator(module_args, play_vars).state()


#################################################################################################


@pytest.mark.parametrize(
    "module_args, play_vars",
    [
        (
            {
                "name": "test-cluster",
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
    """Testing DescribeHsmClusterValidator.validate method"""
    DescribeHsmClusterValidator(module_args, play_vars).validate()


#################################################################################################


@pytest.mark.parametrize(
    "module_args, play_vars",
    [
        (
            {
                "name": "test-cluster",
                "state": "UNINITIALIZED",
                "aws_access_key": "TESTAWSACCESSKEY",
                "aws_secret_key": "testawssecretkey",
                "region": "us-east-2",
            },
            {},
        )
    ],
    ids=["DescribeHsmCluster init"],
)
def test_DescribeHsmCluster_init(
    module_args, play_vars, mock_boto3, mock_configparser_sections
):
    """Testing DescribeHsmCluster.__init__ method"""
    hsm_cluster = DescribeHsmCluster(module_args, play_vars)
    assert hsm_cluster.module_args == module_args
    assert hsm_cluster.play_vars == play_vars


#################################################################################################


@pytest.mark.parametrize(
    "key, value, result",
    [
        ("name", "test-cluster", []),
        (
            "name",
            "123",
            [
                {
                    "BackupPolicy": "DEFAULT",
                    "BackupRetentionPolicy": {"Type": "DAYS", "Value": "90"},
                    "ClusterId": "cluster-test",
                    "CreateTimestamp": "2022-07-23T02:08:23.631000-07:00",
                    "Hsms": [],
                    "HsmType": "hsm1.medium",
                    "SecurityGroup": "sg-test",
                    "State": "UNINITIALIZED",
                    "SubnetMapping": {"us-east-2b": "subnet-test"},
                    "VpcId": "vpc-test",
                    "Certificates": {},
                    "TagList": [
                        {"Key": "sec", "Value": "none"},
                        {"Key": "name", "Value": "123"},
                        {"Key": "zone", "Value": "west"},
                    ],
                }
            ],
        ),
        ("state", "DELETE_IN_PROGRESS", []),
        (
            "state",
            "ACTIVE",
            [
                {
                    "BackupPolicy": "DEFAULT",
                    "BackupRetentionPolicy": {"Type": "DAYS", "Value": "90"},
                    "ClusterId": "cluster-test2",
                    "CreateTimestamp": "2022-07-23T02:08:23.631000-07:00",
                    "Hsms": [],
                    "HsmType": "hsm1.medium",
                    "SecurityGroup": "sg-test",
                    "State": "ACTIVE",
                    "SubnetMapping": {"us-east-2b": "subnet-test"},
                    "VpcId": "vpc-test",
                    "Certificates": {},
                    "TagList": [
                        {"Key": "sec", "Value": "none"},
                        {"Key": "name", "Value": "456"},
                        {"Key": "zone", "Value": "west"},
                    ],
                }
            ],
        ),
    ],
)
def test_DescribeHsmCluster_get(key, value, result, mock_DescribeHsmCluster):
    """Testing DescribeHsmCluster.get method"""
    hsm_cluster = mock_DescribeHsmCluster
    hsm_cluster.module_args = {}
    hsm_cluster.module_args[key] = value
    hsm_cluster = hsm_cluster.get()
    assert hsm_cluster == result
