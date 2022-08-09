"""Test file for create_hsm.py method"""

from __future__ import absolute_import, division, print_function

import pytest
from ansible.errors import AnsibleActionFail

__metaclass__ = type

import json
import sys

sys.path.append("./plugins/module_utils")

from constants import *
from create_hsm import CreateHsm, CreateHsmValidator


@pytest.mark.parametrize("module_args, play_vars", [({}, {})], ids=["Valid IP"])
def test_ip_check_valid_input(module_args, play_vars):
    """Testing CreateHsmValidator._ip_check method
    Valid IP is provided, no exception is raised
    """
    CreateHsmValidator(module_args, play_vars)._ip_check("192.168.0.1")


@pytest.mark.parametrize("module_args, play_vars", [({}, {})], ids=["Invalid IP"])
def test_ip_check_exception(module_args, play_vars):
    """Testing CreateHsmValidator._ip_check method
    Invalid IP is provided and exception is raised
    """
    with pytest.raises(
        AnsibleActionFail,
        match=r"'1192.168.0.1'\s+does\s+not\s+appear\s+to\s+be\s+an\s+IPv4\s+or\s+IPv6\s+address",
    ):
        CreateHsmValidator(module_args, play_vars)._ip_check("1192.168.0.1")


#################################################################################################


@pytest.mark.parametrize(
    "module_args, play_vars",
    [
        ({"availability_zone": "us-west-2b", "state": "present"}, {}),
        ({"availability_zone": "us-west-2b", "state": "absent"}, {}),
        ({"state": "absent"}, {}),
    ],
    ids=["Valid AZ State present", "Valid AZ State absent", "No AZ State absent"],
)
def test_availability_zone(module_args, play_vars):
    """Testing CreateHsmValidator.availability_zone method
    Valid AZ is provided, no exception is raised
    """
    CreateHsmValidator(module_args, play_vars).availability_zone()


@pytest.mark.parametrize(
    "module_args, play_vars, match",
    [
        (
            {"availability_zone": 1, "state": "present"},
            {},
            "^Wrong\\s+type\\s+was.*Provided:\\s+int",
        ),
        (
            {"availability_zone": ["us-west-2b"], "state": "present"},
            {},
            "^Wrong\\s+type\\s+was.*Provided:\\s+list",
        ),
        (
            {"state": "present"},
            {},
            "'availability_zone'\\s+is\\s+a\\s+mandatory\\s+argument.",
        ),
        (
            {"availability_zone": "u-west-2b", "state": "present"},
            {},
            "^Invalid\\s+value\\s+was\\s+provided\\s+to.*Provided:\\s+'u-west-2b'",
        ),
    ],
    ids=[
        "Invalid AZ type int",
        "Invalid AZ type list",
        "Missing AZ state present",
        "Invalid AZ value",
    ],
)
def test_availability_zone_exception(module_args, play_vars, match):
    """Testing CreateHsmValidator.availability_zone method
    Invalid AZ is provided, exception is raised
    """
    with pytest.raises(AnsibleActionFail, match=rf"{match}"):
        CreateHsmValidator(module_args, play_vars).availability_zone()


#################################################################################################


@pytest.mark.parametrize(
    "module_args, play_vars",
    [
        ({"count": "1"}, {}),
        ({"count": 1}, {}),
        ({}, {}),
    ],
    ids=["Valid count type str", "Valid count type int", "No count"],
)
def test_count(module_args, play_vars):
    """Testing CreateHsmValidator.count method
    Valid count is provided, no exception is raised
    """
    CreateHsmValidator(module_args, play_vars).count()


@pytest.mark.parametrize(
    "module_args, play_vars, match",
    [
        (
            {"count": ["1"]},
            {},
            "^Wrong\\s+type\\s+was.*Provided:\\s+list",
        ),
        ({"count": {1}}, {}, "^Wrong\\s+type\\s+was.*Provided:\\s+set"),
        ({"count": 4}, {}, "'count'\\s+value\\s+cannot\\s+be.*Provided:\\s+4"),
        ({"count": -1}, {}, "'count'\\s+value\\s+cannot\\s+be.*Provided:\\s+-1"),
    ],
    ids=[
        "Invalid count type list",
        "Invalid count type set",
        "Invalid count value 4",
        "Invalid count value -1",
    ],
)
def test_count_exception(module_args, play_vars, match):
    """Testing CreateHsmValidator.count method
    Invalid count is provided, exception is raised
    """
    with pytest.raises(AnsibleActionFail, match=rf"{match}"):
        CreateHsmValidator(module_args, play_vars).count()


#################################################################################################


@pytest.mark.parametrize(
    "module_args, play_vars",
    [
        ({"ip_address": "192.168.0.1", "state": "present"}, {}),
        ({"ip_address": "192.168.0.1", "count": 1, "state": "present"}, {}),
        ({"ip_address": ["192.168.0.1"], "count": 1, "state": "present"}, {}),
        ({"state": "present"}, {}),
        ({"ip_address": "192.168.0.1", "state": "absent"}, {}),
    ],
    ids=[
        "Valid IP Address no count state present",
        "Valid IP Address count 1 state present",
        "Valid IP Address type list count 1 state present",
        "No IP Address, count state present",
        "Valid IP Address no count state absent",
    ],
)
def test_ip_address(module_args, play_vars):
    """Testing CreateHsmValidator.ip_address method
    Valid ip_address is provided, no exception is raised
    """
    CreateHsmValidator(module_args, play_vars).ip_address()


@pytest.mark.parametrize(
    "module_args, play_vars, match",
    [
        (
            {"ip_address": {"192.168.0.1"}, "count": 1, "state": "present"},
            {},
            "^Wrong\\s+type\\s+was.*Provided:\\s+set",
        ),
        (
            {"ip_address": "192.168.0.1", "count": 2, "state": "present"},
            {},
            "^Since\\s+only\\s+one\\s+'ip_address'.*Provided:\\s+2",
        ),
        (
            {"ip_address": ["192.168.0.1"], "count": 2, "state": "present"},
            {},
            "Number\\s+of\\s+provided\\s+IPs.*",
        ),
        (
            {
                "ip_address": ["192.168.0.1", "192.168.0.2"],
                "count": 1,
                "state": "present",
            },
            {},
            "Number\\s+of\\s+provided\\s+IPs.*",
        ),
    ],
    ids=[
        "Invalid IP address type set",
        "Valid IP wrong count",
        "Valid IP type list wrong count 1",
        "Valid IP type list wrong count 2",
    ],
)
def test_ip_address_exception(module_args, play_vars, match):
    """Testing CreateHsmValidator.ip_address method
    Invalid ip_address is provided, exception is raised
    """
    with pytest.raises(AnsibleActionFail, match=rf"{match}"):
        CreateHsmValidator(module_args, play_vars).ip_address()


#################################################################################################


@pytest.mark.parametrize(
    "module_args, play_vars",
    [
        ({"eni_id": "eni-test", "state": "present"}, {}),
        ({"eni_id": "eni-test", "count": 1, "state": "absent"}, {}),
        ({"eni_id": "eni-test", "count": 2, "state": "absent"}, {}),
        ({"eni_id": ["eni-test", "eni-test1"], "state": "absent"}, {}),
    ],
    ids=[
        "Valid ENI ID no count state present",
        "Valid ENI ID count 1 state absent",
        "Valid ENI ID count 2 state absent",
        "Valid ENI ID type list state absent",
    ],
)
def test_eni_id(module_args, play_vars):
    """Testing CreateHsmValidator.eni_id method
    Valid eni_id is provided, no exception is raised
    """
    CreateHsmValidator(module_args, play_vars).eni_id()


@pytest.mark.parametrize(
    "module_args, play_vars, match",
    [
        (
            {"eni_id": {"eni-test"}, "state": "absent"},
            {},
            "Wrong\\s+type\\s+was\\s+provided.*Provided:\\s+set",
        ),
        (
            {"eni_id": 1, "state": "absent"},
            {},
            "Wrong\\s+type\\s+was\\s+provided.*Provided:\\s+int",
        ),
        (
            {"eni_id": "enitest", "state": "absent"},
            {},
            "The\\s+value\\s+of\\s+the\\s+'eni_id'.*Provided:\\s+enitest",
        ),
        (
            {"eni_id": "test", "state": "absent"},
            {},
            "The\\s+value\\s+of\\s+the\\s+'eni_id'.*Provided:\\s+test",
        ),
    ],
    ids=[
        "Invalid ENI ID type set",
        "Invalid ENI ID type int",
        "Invalid ENI ID name enitest",
        "Invalid ENI ID name test",
    ],
)
def test_eni_id_exception(module_args, play_vars, match):
    """Testing CreateHsmValidator.eni_id method
    Invalid eni_id is provided, exception is raised
    """
    with pytest.raises(AnsibleActionFail, match=rf"{match}"):
        CreateHsmValidator(module_args, play_vars).eni_id()


#################################################################################################


@pytest.mark.parametrize(
    "module_args, play_vars",
    [
        ({"eni_ip": "192.168.0.1", "state": "present"}, {}),
        ({"eni_ip": "192.168.0.1", "count": 1, "state": "absent"}, {}),
        ({"eni_ip": "192.168.0.1", "count": 2, "state": "absent"}, {}),
        ({"eni_ip": ["192.168.0.1", "192.168.0.2"], "state": "absent"}, {}),
        ({"state": "absent"}, {}),
    ],
    ids=[
        "Valid ENI IP no count state present",
        "Valid ENI IP count 1 state absent",
        "Valid ENI IP count 2 state absent",
        "Valid ENI IP type list state absent",
        "No ENI IP no count state absent",
    ],
)
def test_eni_ip(module_args, play_vars):
    """Testing CreateHsmValidator.eni_ip method
    Valid eni_id is provided, no exception is raised
    """
    CreateHsmValidator(module_args, play_vars).eni_ip()


@pytest.mark.parametrize(
    "module_args, play_vars, match",
    [
        (
            {"eni_ip": {"192.168.0.1"}, "state": "absent"},
            {},
            "Wrong\\s+type\\s+was\\s+provided.*Provided:\\s+set",
        ),
        (
            {"eni_ip": 192.168, "state": "absent"},
            {},
            "Wrong\\s+type\\s+was\\s+provided.*Provided:\\s+float",
        ),
        (
            {"eni_ip": "192.168.0.0.1", "state": "absent"},
            {},
            "'192.168.0.0.1'\\s+does\\s+not\\s+appear\\s+to\\s+be\\s+an\\s+IPv4\\s+or\\s+IPv6\\s+address",
        ),
    ],
    ids=[
        "Invalid ENI IP type set",
        "Invalid ENI IP type float",
        "Invalid ENI IP 192.168.0.0.1",
    ],
)
def test_eni_ip_exception(module_args, play_vars, match):
    """Testing CreateHsmValidator.eni_ip method
    Invalid eni_ip is provided, exception is raised
    """
    with pytest.raises(AnsibleActionFail, match=rf"{match}"):
        CreateHsmValidator(module_args, play_vars).eni_ip()


#################################################################################################


@pytest.mark.parametrize(
    "module_args, play_vars",
    [
        ({"hsm_id": "hsm-1t2e3s4t5", "state": "present"}, {}),
        ({"hsm_id": "hsm-1t2e3s4t5", "count": 1, "state": "absent"}, {}),
        ({"hsm_id": "hsm-1t2e3s4t5", "count": 2, "state": "absent"}, {}),
        ({"hsm_id": ["hsm-1t2e3s4t5", "hsm-6t7e8s9t10"], "state": "absent"}, {}),
        ({"state": "absent"}, {}),
    ],
    ids=[
        "Valid HSM ID no count state present",
        "Valid HSM ID count 1 state absent",
        "Valid HSM ID count 2 state absent",
        "Valid HSM ID type list state absent",
        "No HSM ID no count state absent",
    ],
)
def test_hsm_id(module_args, play_vars):
    """Testing CreateHsmValidator.hsm_id method
    Valid hsm_id is provided, no exception is raised
    """
    CreateHsmValidator(module_args, play_vars).hsm_id()


@pytest.mark.parametrize(
    "module_args, play_vars, match",
    [
        (
            {"hsm_id": {"hsm-1t2e3s4t5"}, "state": "absent"},
            {},
            "Wrong\\s+type\\s+was\\s+provided.*Provided:\\s+set",
        ),
        (
            {"hsm_id": 192, "state": "absent"},
            {},
            "Wrong\\s+type\\s+was\\s+provided.*Provided:\\s+int",
        ),
        (
            {"hsm_id": "hsmtest", "state": "absent"},
            {},
            "The\\s+value\\s+of\\s+the\\s+'hsm_id'.*Provided:\\s+hsmtest",
        ),
        (
            {"hsm_id": ["hsm-test", "hsmtest"], "state": "absent"},
            {},
            "The\\s+value\\s+of\\s+the\\s+'hsm_id'.*Provided:\\s+hsmtest",
        ),
    ],
    ids=[
        "Invalid HSM ID type set",
        "Invalid HSM ID type float",
        "Invalid HSM ID value hsmtest",
        "Invalid HSM ID type list value hsmtest",
    ],
)
def test_hsm_id_exception(module_args, play_vars, match):
    """Testing CreateHsmValidator.eni_ip method
    Invalid eni_ip is provided, exception is raised
    """
    with pytest.raises(AnsibleActionFail, match=rf"{match}"):
        CreateHsmValidator(module_args, play_vars).hsm_id()


#################################################################################################


@pytest.mark.parametrize(
    "module_args, play_vars",
    [
        (
            {
                "availability_zone": "us-east-2b",
                "count": "1",
                "cluster_id": "cluster-test123",
                "ip_address": "192.168.0.1",
                "eni_id": "eni-test123",
                "eni_ip": "192.168.0.1",
                "hsm_id": "hsm-test123",
                "state": "absent",
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
    """Testing CreateHsmValidator.validate method"""
    CreateHsmValidator(module_args, play_vars).validate()


#################################################################################################


@pytest.mark.parametrize(
    "module_args, play_vars",
    [
        (
            {
                "availability_zone": "us-east-2b",
                "count": "1",
                "cluster_id": "cluster-test123",
                "ip_address": "192.168.0.1",
                "eni_id": "eni-test123",
                "eni_ip": "192.168.0.1",
                "hsm_id": "hsm-test123",
                "state": "absent",
                "aws_access_key": "TESTAWSACCESSKEY",
                "aws_secret_key": "testawssecretkey",
                "region": "us-east-2",
            },
            {},
        )
    ],
    ids=["CreateHsm Init"],
)
def test_CreateHsm_init(module_args, play_vars, mock_configparser_sections):
    """Testing CreateHsm.__init__ method"""
    hsm = CreateHsm(module_args, play_vars)
    assert hsm.module_args == module_args
    assert hsm.play_vars == play_vars


@pytest.mark.parametrize(
    "count, ip_address, expected",
    [
        (
            1,
            "192.168.0.1",
            [
                {
                    "AvailabilityZone": "us-west-2b",
                    "ClusterId": "cluster-test",
                    "EniId": "eni-test",
                    "EniIp": "192.168.0.1",
                    "HsmId": "hsm-test",
                    "State": "ACTIVE",
                    "StateMessage": "HSM created.",
                    "SubnetId": "subnet-test",
                }
            ],
        ),
        (
            1,
            ["127.0.0.1"],
            [
                {
                    "AvailabilityZone": "us-west-2b",
                    "ClusterId": "cluster-test",
                    "EniId": "eni-test",
                    "EniIp": "127.0.0.1",
                    "HsmId": "hsm-test",
                    "State": "ACTIVE",
                    "StateMessage": "HSM created.",
                    "SubnetId": "subnet-test",
                }
            ],
        ),
        (
            2,
            ["192.168.0.1", "192.168.0.2"],
            [
                {
                    "AvailabilityZone": "us-west-2b",
                    "ClusterId": "cluster-test",
                    "EniId": "eni-test",
                    "EniIp": "192.168.0.1",
                    "HsmId": "hsm-test",
                    "State": "ACTIVE",
                    "StateMessage": "HSM created.",
                    "SubnetId": "subnet-test",
                },
                {
                    "AvailabilityZone": "us-west-2b",
                    "ClusterId": "cluster-test",
                    "EniId": "eni-test",
                    "EniIp": "192.168.0.2",
                    "HsmId": "hsm-test",
                    "State": "ACTIVE",
                    "StateMessage": "HSM created.",
                    "SubnetId": "subnet-test",
                },
            ],
        ),
        (
            2,
            None,
            [
                {
                    "AvailabilityZone": "us-west-2b",
                    "ClusterId": "cluster-test",
                    "EniId": "eni-test",
                    "EniIp": "127.0.0.1",
                    "HsmId": "hsm-test",
                    "State": "ACTIVE",
                    "StateMessage": "HSM created.",
                    "SubnetId": "subnet-test",
                },
                {
                    "AvailabilityZone": "us-west-2b",
                    "ClusterId": "cluster-test",
                    "EniId": "eni-test",
                    "EniIp": "127.0.0.1",
                    "HsmId": "hsm-test",
                    "State": "ACTIVE",
                    "StateMessage": "HSM created.",
                    "SubnetId": "subnet-test",
                },
            ],
        ),
    ],
    ids=[
        "Count 1 IP Addr 192.168.0.1",
        "Count 1 IP Addr 127.0.0.1",
        "Count 2 IP Addr 192.168.0.1 and 192.168.0.2",
        "Count 2 no IP Addr",
    ],
)
def test_CreateHsm_present(count, ip_address, expected, mock_CreateHsm):
    """Testing CreateHsm.present method
    HSM is created and no exception is raised
    """

    hsm = mock_CreateHsm
    hsm.module_args["count"] = count
    hsm.module_args["ip_address"] = ip_address
    create_hsm = hsm.present()

    assert create_hsm["changed"]
    assert create_hsm["data"] == expected


@pytest.mark.parametrize(
    "count, ip_address",
    [
        (1, ["192.168.0.1"]),
        (2, ["192.168.0.1", "192.168.0.2"]),
    ],
    ids=["Count 1 IP Addr 1", "Count 2 IP Addr 2"],
)
def test_CreateHsm_present_not_changed(
    count, ip_address, absoulte_path, mock_CreateHsm
):
    """Testing CreateHsm.present method
    HSM is not created and no exception is raised
    """
    hsm = mock_CreateHsm
    hsm.module_args["cluster_id"] = "cluster-test4"
    hsm.module_args["count"] = count
    hsm.module_args["ip_address"] = ip_address
    create_hsm = hsm.present()
    assert not create_hsm["changed"]


# TODO: Something is wrong with pytest.
# def test_CreateHsm_present_exception(mock_CreateHsm):
#     """Testing CreateHsm.present method
#     Exception is raised while creating the HSM
#     """
#     hsm = mock_CreateHsm
#     hsm.client.create_hsm.side_effect = Exception("Raising exception for testing purposes.")
#     while pytest.raises(Exception):
#         while pytest.raises(AnsibleActionFail):
#             hsm.present()


def test_CreateHsm_absent_no_hsms(mock_CreateHsm):
    """Testing CreateHsm.absent method
    HSM Cluster does not contain any HMS, no exception is raised.
    """
    hsm = mock_CreateHsm
    hsm.module_args["cluster_id"] = "cluster-test"
    hsm.module_args["state"] = "absent"
    delete_hsm = hsm.absent()
    assert not delete_hsm["changed"]
    assert delete_hsm["msg"] == "HSM Cluster cluster-test does not contain any HSMs."


@pytest.mark.parametrize(
    "hsm_id, eni_ip, eni_id",
    [
        (None, None, None),
        ("hsm-test", None, None),
        (["hsm-test"], None, None),
        (["hsm-test", "hsm-test1"], None, None),
        (None, "127.0.0.1", None),
        (None, ["127.0.0.2"], None),
        (None, ["127.0.0.1", "127.0.0.2"], None),
        (None, None, "eni-test1"),
        (None, None, ["eni-test"]),
        (None, None, ["eni-test", "eni-test1"]),
    ],
)
def test_CreateHsm_absent(hsm_id, eni_ip, eni_id, absoulte_path, mock_CreateHsm):
    """Testing CreateHsm.absent method
    HSM is removed and no exception is raised
    """
    hsm = mock_CreateHsm
    hsm.module_args["cluster_id"] = "cluster-test4"
    hsm.module_args["state"] = "absent"
    hsm.module_args["hsm_id"] = hsm_id
    hsm.module_args["eni_ip"] = eni_ip
    hsm.module_args["eni_id"] = eni_id

    delete_hsm = hsm.absent()

    assert delete_hsm["changed"]
    assert "msg" not in delete_hsm
    # hsm.client.delete_hsm.assert_called_once()


@pytest.mark.parametrize(
    "hsm_id, eni_ip, eni_id",
    [
        ("hsm-test2", None, None),
        (None, "127.0.0.3", None),
        (None, None, "eni-test3"),
    ],
)
def test_CreateHsm_absent_exception(
    hsm_id, eni_ip, eni_id, absoulte_path, mock_CreateHsm
):
    """Testing CreateHsm.absent method
    HSM Cluster does not contain any HMS, no exception is raised.
    """
    hsm = mock_CreateHsm
    hsm.module_args["state"] = "absent"
    hsm.module_args["hsm_id"] = hsm_id
    hsm.module_args["eni_ip"] = eni_ip
    hsm.module_args["eni_id"] = eni_id
    with pytest.raises(
        AnsibleActionFail,
        match=r"^Something\s+went\s+wrong.*CloudHSMV2.Client.exceptions.CloudHsmResourceNotFoundException",
    ):
        delete_hsm = hsm.absent()
