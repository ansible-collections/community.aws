"""Test file for create_cluster.py method"""

from __future__ import absolute_import, division, print_function

import pytest
from ansible.errors import AnsibleActionFail

__metaclass__ = type
import sys

sys.path.append("./plugins/module_utils")
from create_cluster import CreateHsmCluster, CreateHsmClusterValidator
from constants import *


@pytest.mark.parametrize("module_args, play_vars", [({}, {})], ids=["No arguments"])
def test_backup_retention_days_no_input(module_args, play_vars):
    """Testing CreateHsmClusterValidator.backup_retention_days method
    No inputs are provided, hence no exception is raised
    """
    CreateHsmClusterValidator(module_args, play_vars).backup_retention_days()


@pytest.mark.parametrize(
    "module_args, play_vars",
    [
        ({"backup_retention_days": 90, "state": "present"}, {}),
        ({"backup_retention_days": "90", "state": "present"}, {}),
    ],
    ids=[
        "Valid argument value int",
        "Valid argument value str",
    ],
)
def test_backup_retention_days_valid_input(module_args, play_vars):
    """Testing CreateHsmClusterValidator.backup_retention_days method
    A value of 90 is provided as an input, but no exception is raised
    """
    CreateHsmClusterValidator(module_args, play_vars).backup_retention_days()


@pytest.mark.parametrize(
    "module_args, play_vars, match",
    [
        (
            {"backup_retention_days": "400", "state": "present"},
            {},
            "^Wrong\\s+value.*7\\s+and\\s+379",
        ),
        (
            {"backup_retention_days": 1, "state": "present"},
            {},
            "^Wrong\\s+value.*7\\s+and\\s+379",
        ),
        (
            {"backup_retention_days": "abc", "state": "present"},
            {},
            "^Wrong\\s+type.*\\s+Provided:\\s+str",
        ),
        (
            {"backup_retention_days": [90], "state": "present"},
            {},
            "^Wrong\\s+type.*\\s+Provided:\\s+list",
        ),
    ],
    ids=[
        "Disallowed argument value > 379",
        "Disallowed argument value < 7",
        "Disallowed argument value type: string",
        "Disallowed argument value type: list",
    ],
)
def test_backup_retention_days_exception(module_args, play_vars, match):
    """Testing CreateHsmClusterValidator.backup_retention_days method
    Disallowed values are provided as an input, and AnsibleActionFail exception is raised
    """
    with pytest.raises(AnsibleActionFail, match=rf"{match}"):
        CreateHsmClusterValidator(module_args, play_vars).backup_retention_days()


#################################################################################################


@pytest.mark.parametrize("module_args, play_vars", [({}, {})], ids=["No arguments"])
def test_source_backup_id_no_input(module_args, play_vars):
    """Testing CreateHsmClusterValidator.source_backup_id method
    No inputs are provided, hence no exception is raised
    """
    CreateHsmClusterValidator(module_args, play_vars).source_backup_id()


@pytest.mark.parametrize(
    "module_args, play_vars",
    [({"source_backup_id": "backup-id", "state": "present"}, {})],
    ids=["Valid argument value"],
)
def test_source_backup_id_input_valid(module_args, play_vars):
    """Testing CreateHsmClusterValidator.source_backup_id method
    Valid input is provided, no exception is raised.
    """
    CreateHsmClusterValidator(module_args, play_vars).source_backup_id()


@pytest.mark.parametrize(
    "module_args, play_vars, match",
    [
        (
            {"source_backup_id": 400, "state": "present"},
            {},
            "^Wrong\\s+type.*\\s+Provided:\\s+int",
        ),
        (
            {"source_backup_id": ["backup-id"], "state": "present"},
            {},
            "^Wrong\\s+type.*\\s+Provided:\\s+list",
        ),
        (
            {"source_backup_id": True, "state": "present"},
            {},
            "^Wrong\\s+type.*\\s+Provided:\\s+bool",
        ),
    ],
    ids=[
        "Disallowed argument value 400",
        "Disallowed argument value type: list",
        "Disallowed argument value type: bool",
    ],
)
def test_source_backup_id_exception(module_args, play_vars, match):
    """Testing CreateHsmClusterValidator.source_backup_id method
    Disallowed values are provided as an input, and AnsibleActionFail exception is raised
    """
    with pytest.raises(AnsibleActionFail, match=rf"{match}"):
        CreateHsmClusterValidator(module_args, play_vars).source_backup_id()


#################################################################################################


@pytest.mark.parametrize(
    "module_args, play_vars", [({"state": "absent"}, {})], ids=["Absent state"]
)
def test_subnet_ids_no_input(module_args, play_vars):
    """Testing CreateHsmClusterValidator.subnet_ids method
    No inputs are provided, hence no exception is raised
    """
    CreateHsmClusterValidator(module_args, play_vars).subnet_ids()


@pytest.mark.parametrize(
    "module_args, play_vars",
    [
        ({"subnet_ids": "subnet-abc1234564", "state": "present"}, {}),
        ({"subnet_ids": ["subnet-abc1234564"], "state": "present"}, {}),
    ],
    ids=["Valid argument value type str", "Valid argument value type list"],
)
def test_subnet_ids_input_valid(module_args, play_vars):
    """Testing CreateHsmClusterValidator.subnet_ids method
    Valid input is provided, no exception is raised.
    """
    CreateHsmClusterValidator(module_args, play_vars).subnet_ids()


@pytest.mark.parametrize(
    "module_args, play_vars, match",
    [
        (
            {"subnet_ids": 400, "state": "present"},
            {},
            "^Wrong\\s+type.*\\s+Provided:\\s+int",
        ),
        (
            {"subnet_ids": {"subnetid-test": "subnetid-test"}, "state": "present"},
            {},
            "^Wrong\\s+type.*\\s+Provided:\\s+dict",
        ),
        (
            {"subnet_ids": True, "state": "present"},
            {},
            "^Wrong\\s+type.*\\s+Provided:\\s+bool",
        ),
        (
            {"state": "present"},
            {},
            "^'subnet_ids'\\s+is\\s+a\\s+mandatory\\s+argument.",
        ),
    ],
    ids=[
        "Disallowed argument value 400",
        "Disallowed argument value type: dict",
        "Disallowed argument value type: bool",
        "Missing argument",
    ],
)
def test_subnet_ids_exception(module_args, play_vars, match):
    """Testing CreateHsmClusterValidator.subnet_ids method
    Disallowed values are provided as an input, and AnsibleActionFail exception is raised
    """
    with pytest.raises(AnsibleActionFail, match=rf"{match}"):
        CreateHsmClusterValidator(module_args, play_vars).subnet_ids()


#################################################################################################


@pytest.mark.parametrize("module_args, play_vars", [({}, {})], ids=["No arguments"])
def test_tags_no_input(module_args, play_vars):
    """Testing CreateHsmClusterValidator.tags method
    No inputs are provided, hence no exception is raised
    """
    CreateHsmClusterValidator(module_args, play_vars).tags()


@pytest.mark.parametrize(
    "module_args, play_vars",
    [
        ({"tags": {"region": "us-west-2"}, "state": "present"}, {}),
    ],
    ids=["Valid argument value type dict"],
)
def test_tags_input_valid(module_args, play_vars):
    """Testing CreateHsmClusterValidator.tags method
    Valid input is provided, no exception is raised.
    """
    CreateHsmClusterValidator(module_args, play_vars).tags()


@pytest.mark.parametrize(
    "module_args, play_vars, match",
    [
        (
            {"tags": 400, "state": "present"},
            {},
            "^Wrong\\s+type.*\\s+Provided:\\s+int",
        ),
        (
            {"tags": "trust", "state": "present"},
            {},
            "^Wrong\\s+type.*\\s+Provided:\\s+str",
        ),
        (
            {"tags": True, "state": "present"},
            {},
            "^Wrong\\s+type.*\\s+Provided:\\s+bool",
        ),
        (
            {"tags": ["key", "value"], "state": "present"},
            {},
            "^Wrong\\s+type.*\\s+Provided:\\s+list",
        ),
    ],
    ids=[
        "Disallowed argument value 400",
        "Disallowed argument value type: str",
        "Disallowed argument value type: bool",
        "Disallowed argument value type: list",
    ],
)
def test_tags_exception(module_args, play_vars, match):
    """Testing CreateHsmClusterValidator.tags method
    Disallowed values are provided as an input, and AnsibleActionFail exception is raised
    """
    with pytest.raises(AnsibleActionFail, match=rf"{match}"):
        CreateHsmClusterValidator(module_args, play_vars).tags()


#################################################################################################


@pytest.mark.parametrize(
    "module_args, play_vars",
    [
        (
            {
                "backup_retention_days": 90,
                "source_backup_id": "backup-id",
                "subnet_ids": "subnet-abc123456",
                "name": "test-cluster",
                "tags": {"region": "us-west-2"},
                "state": "present",
                "aws_access_key": "TESTAWSACCESSKEY",
                "aws_secret_key": "testawssecretkey",
                "region": "us-east-2",
            },
            {},
        )
    ],
    ids=["Full validate"],
)
def test_validate(module_args, play_vars, mock_configparser_sections):
    """Testing CreateHsmClusterValidator.validate method"""
    CreateHsmClusterValidator(module_args, play_vars).validate()


#################################################################################################


@pytest.mark.parametrize(
    "module_args, play_vars",
    [
        (
            {
                "backup_retention_days": 90,
                "source_backup_id": "backup-id",
                "subnet_ids": "subnet-abc123456",
                "name": "test-hsm",
                "tags": {"region": "us-west-2"},
                "state": "present",
                "aws_access_key": "TESTAWSACCESSKEY",
                "aws_secret_key": "testawssecretkey",
                "region": "us-east-2",
            },
            {},
        )
    ],
    ids=["CreateHsmCluster Init"],
)
def test_CreateHsmCluster_init(
    module_args, play_vars, mock_boto3, mock_configparser_sections
):
    """Testing CreateHsmCluster.__init__ method"""
    hsm_cluster = CreateHsmCluster(module_args, play_vars)
    assert hsm_cluster.module_args == module_args
    assert hsm_cluster.play_vars == play_vars
    assert hsm_cluster.cluster == []


@pytest.mark.parametrize(
    "subnet_ids",
    [("subnet-abc123456"), (["subnet-abc123456"])],
    ids=["Subnet IDs str,", "Subnet IDs list"],
)
def test_CreateHsmCluster_present_changed_true(subnet_ids, mock_CreateHsmCluster):
    """Testing CreateHsmCluster.present method"""
    hsm_cluster = mock_CreateHsmCluster
    hsm_cluster.module_args["subnet_ids"] = subnet_ids
    created = hsm_cluster.present()
    assert created["changed"]
    assert created["data"] == {
        "BackupPolicy": "DEFAULT",
        "BackupRetentionPolicy": {"Type": "DAYS", "Value": "90"},
        "ClusterId": "cluster-cmp4w4mhi4j",
        "CreateTimestamp": "2022-07-27T22:17:41.436000-07:00",
        "Hsms": [],
        "HsmType": "hsm1.medium",
        "State": "CREATE_IN_PROGRESS",
        "SubnetMapping": {"us-east-2b": "subnet-0dcef7af922f2d5bc"},
        "VpcId": "vpc-0f08baa19b887bd01",
        "Certificates": {},
    }


def test_CreateHsmCluster_present_changed_false(mock_CreateHsmCluster):
    """Testing CreateHsmCluster.present method"""
    hsm_cluster = mock_CreateHsmCluster
    hsm_cluster.cluster = "test"
    created = hsm_cluster.present()
    assert not created["changed"]


def test_CreateHsmCluster_absent_changed_true(mock_CreateHsmCluster):
    """Testing CreateHsmCluster.absent method"""
    hsm_cluster = mock_CreateHsmCluster
    hsm_cluster.cluster = [{"ClusterId": "test-cluster"}]
    created = hsm_cluster.absent()
    assert created["changed"]


def test_CreateHsmCluster_absent_changed_false(mock_CreateHsmCluster):
    """Testing CreateHsmCluster.absent method"""
    hsm_cluster = mock_CreateHsmCluster
    created = hsm_cluster.absent()
    assert not created["changed"]
