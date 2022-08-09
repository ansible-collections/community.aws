"""Test file for aws_hsm.py method"""

from __future__ import absolute_import, division, print_function

import configparser
import json
import os
import sys
from os.path import expanduser
from typing import Any

import pytest
from ansible.errors import AnsibleActionFail
from botocore.exceptions import ClientError

sys.path.append("plugins/module_utils")
from aws_hsm import AwsHsm, Validator

__metaclass__ = type

ABSOLUTE_PATH = os.path.dirname(os.path.abspath(__file__))
AWS_HSM = "aws_hsm"


def json_load(path: str) -> dict[str, Any]:
    """Load file containing JSON data and return dict

    Args:
        path (str): Path to the file containing JSON data

    Returns:
        dict: Data loaded from the JSON file
    """
    with open(path, encoding="utf-8") as _file:
        return json.load(_file)


@pytest.mark.parametrize(
    "arg, value, regex", [("cluster_id", "cluster-test123", "cluster-.*")]
)
def test_regex_check(arg, value, regex):
    """Testing _regex_check method
    Valid data is provided, no exception is raised.
    """
    Validator({}, {})._regex_check(arg, value, regex)


@pytest.mark.parametrize(
    "arg, value, regex", [("cluster_id", "subnet-test123", "cluster-.*")]
)
def test_regex_check_exception(arg, value, regex):
    """Testing _regex_check method
    Valid data is provided, no exception is raised.
    """
    with pytest.raises(
        AnsibleActionFail,
        match=r"The\s+value\s+of\s+the\s+'cluster_id'.*Provided:\s+subnet-test123",
    ):
        Validator({}, {})._regex_check(arg, value, regex)


#################################################################################################


@pytest.mark.parametrize(
    "module_vars, play_vars",
    [
        (
            {
                "aws_access_key": "TESTAWSACCESSKEY",
                "aws_secret_key": "testawssecretkey",
                "region": "us-east-2",
                "state": "absent",
            },
            {},
        ),
        (
            {"state": "absent"},
            {
                "aws_access_key": "TESTAWSACCESSKEY",
                "aws_secret_key": "testawssecretkey",
                "region": "us-east-2",
            },
        ),
        ({}, {}),
    ],
    ids=["args_no_vars", "min_args_vars", "no_args_no_vars"],
)
def test_validator_init(module_vars, play_vars):
    """Testing Validator.__init__

    Args:
        module_vars (_type_): pytest parameter
        play_vars (_type_): pytest parameter
    """
    validator = Validator(module_vars, play_vars)

    assert validator.play_vars == play_vars
    assert validator.module_args == module_vars


#################################################################################################


def test_auth_no_vars(validator_no_vars, mocker):
    """Testing auth method without vars"""
    mock_config_read = mocker.patch(
        f"{AWS_HSM}.configparser.ConfigParser.read", return_value=[]
    )
    validator_no_vars.auth()
    assert (
        os.getenv("AWS_ACCESS_KEY_ID")
        == validator_no_vars.module_args["aws_access_key"]
    )
    assert (
        os.getenv("AWS_SECRET_ACCESS_KEY")
        == validator_no_vars.module_args["aws_secret_key"]
    )
    mock_config_read.assert_called_once_with(f"{expanduser('~')}/.aws/credentials")


def test_auth_no_args(validator_no_args, mocker):
    """Testing auth method without args"""
    mock_config_read = mocker.patch(
        f"{AWS_HSM}.configparser.ConfigParser.read", return_value=[]
    )
    validator_no_args.auth()
    assert (
        os.getenv("AWS_ACCESS_KEY_ID") == validator_no_args.play_vars["aws_access_key"]
    )
    assert (
        os.getenv("AWS_SECRET_ACCESS_KEY")
        == validator_no_args.play_vars["aws_secret_key"]
    )
    mock_config_read.assert_called_once_with(f"{expanduser('~')}/.aws/credentials")


def test_auth_no_args_vars_exception_1(validator_no_args_vars, mocker):
    """Testing auth method without args and vars.
    AnsibleActionFail should be raised because the AWS_ACCESS_KEY_ID env var is empty.
    """
    mock_config_read = mocker.patch(
        f"{AWS_HSM}.configparser.ConfigParser.read", return_value=[]
    )
    mock_os_getenv = mocker.patch(f"{AWS_HSM}.os.getenv", return_value="")
    with pytest.raises(AnsibleActionFail, match=r"^.*aws_access_key.*$"):
        validator_no_args_vars.auth()
    mock_config_read.assert_called_once_with(f"{expanduser('~')}/.aws/credentials")
    mock_os_getenv.assert_called_once_with("AWS_ACCESS_KEY_ID")


def test_auth_no_args_vars_exception_2(validator_no_args_vars, mocker):
    """Testing auth method without args and vars.
    AnsibleActionFail should be raised because the AWS_SECRET_ACCESS_KEY env var is empty.
    """

    def env_var_side_effect(value: str):
        if value == "AWS_ACCESS_KEY_ID":
            return "TESTAWSACCESSKEY"
        elif value == "AWS_SECRET_ACCESS_KEY":
            return ""

    mock_config_read = mocker.patch(
        f"{AWS_HSM}.configparser.ConfigParser.read", return_value=[]
    )
    mock_os_getenv = mocker.patch("os.getenv", side_effect=env_var_side_effect)
    with pytest.raises(AnsibleActionFail, match=r"^.*aws_secret_key.*$"):
        validator_no_args_vars.auth()
    mock_config_read.assert_called_once_with(f"{expanduser('~')}/.aws/credentials")
    mock_os_getenv.assert_called_with("AWS_SECRET_ACCESS_KEY")
    assert mock_os_getenv.call_count == 2


def test_auth_no_args_vars_read_creds_file(
    validator_no_args_vars, absoulte_path, mocker
):
    """Testing auth method without args and vars.
    The code should read the config from ~/.aws/credentials
    Mocker will present mocked data. No exceptions should be raised.
    """
    config = configparser.ConfigParser()

    mock_config_read = mocker.patch(
        f"{AWS_HSM}.configparser.ConfigParser.read",
        return_value=config.read(f"{absoulte_path}/mocks/creds.ini"),
    )

    mock_config_sections = mocker.patch(
        f"{AWS_HSM}.configparser.ConfigParser.sections",
        return_value=config.sections(),
    )
    mock_config_options = mocker.patch(
        f"{AWS_HSM}.configparser.ConfigParser.options",
        return_value=config.options(section="default"),
    )
    validator_no_args_vars.auth()
    mock_config_read.assert_called_once_with(f"{expanduser('~')}/.aws/credentials")
    mock_config_sections.assert_called_once()
    assert mock_config_options.call_count == 2


def test_auth_no_args_vars_read_creds_file_exception_1(
    validator_no_args_vars, absoulte_path, mocker
):
    """Testing auth method without args and vars.
    The code should read the config from ~/.aws/credentials
    Mocker will present mocked data.
    AnsibleActionFail should be raised because the aws_access_key_id is missing.
    """
    config = configparser.ConfigParser()

    mock_config_read = mocker.patch(
        f"{AWS_HSM}.configparser.ConfigParser.read",
        return_value=config.read(f"{absoulte_path}/mocks/creds.ini"),
    )

    mock_config_sections = mocker.patch(
        f"{AWS_HSM}.configparser.ConfigParser.sections",
        return_value=config.sections(),
    )
    mock_config_options = mocker.patch(
        f"{AWS_HSM}.configparser.ConfigParser.options", return_value=[]
    )
    with pytest.raises(
        AnsibleActionFail, match=r"^AWS\s+Access\s+Key.*aws_access_key_id.*$"
    ):
        validator_no_args_vars.auth()

    mock_config_read.assert_called_once_with(f"{expanduser('~')}/.aws/credentials")
    mock_config_sections.assert_called_once()
    mock_config_options.assert_called_once_with(section="default")


def test_auth_no_args_vars_read_creds_file_exception_2(
    validator_no_args_vars, absoulte_path, mocker
):
    """Testing auth method without args and vars.
    The code should read the config from ~/.aws/credentials
    Mocker will present mocked data.
    AnsibleActionFail should be raised because the aws_secret_access_key is missing.
    """
    config = configparser.ConfigParser()

    mock_config_read = mocker.patch(
        f"{AWS_HSM}.configparser.ConfigParser.read",
        return_value=config.read(f"{absoulte_path}/mocks/creds.ini"),
    )

    mock_config_sections = mocker.patch(
        f"{AWS_HSM}.configparser.ConfigParser.sections",
        return_value=config.sections(),
    )
    mock_config_options = mocker.patch(
        f"{AWS_HSM}.configparser.ConfigParser.options",
        side_effect=[["aws_access_key_id"], []],
    )
    with pytest.raises(
        AnsibleActionFail,
        match=r"^AWS\s+Secret\s+Access\s+Key.*aws_secret_access_key.*$",
    ):
        validator_no_args_vars.auth()

    mock_config_read.assert_called_once_with(f"{expanduser('~')}/.aws/credentials")
    mock_config_sections.assert_called()
    assert mock_config_sections.call_count == 1
    mock_config_options.assert_called_with(section="default")
    assert mock_config_options.call_count == 2


def test_auth_no_args_vars_exception(validator_no_args_vars, absoulte_path, mocker):
    """Testing auth method without args and vars.
    AnsibleActionFail should be raised because the no credentials were found anywhere.
    """
    config = configparser.ConfigParser()
    config.read(f"{absoulte_path}/mocks/creds.ini")

    mock_config_read = mocker.patch(
        f"{AWS_HSM}.configparser.ConfigParser.read",
        return_value=["us-east-2"],
    )
    with pytest.raises(
        AnsibleActionFail,
        match=r"^Something\s+went\s+wrong.*$",
    ):
        validator_no_args_vars.auth()
    assert mock_config_read.call_count == 1


#################################################################################################


def test_region_no_vars(validator_no_vars, mocker):
    """Testing region method without vars"""
    mock_config_sections = mocker.patch(
        f"{AWS_HSM}.configparser.ConfigParser.sections", return_value=[]
    )
    validator_no_vars.region()
    assert os.getenv("AWS_DEFAULT_REGION") == validator_no_vars.module_args["region"]
    mock_config_sections.assert_called_once()


def test_region_no_args(validator_no_args, mocker):
    """Testing region method without args"""
    mock_config_sections = mocker.patch(
        f"{AWS_HSM}.configparser.ConfigParser.sections", return_value=[]
    )
    validator_no_args.region()
    assert os.getenv("AWS_DEFAULT_REGION") == validator_no_args.play_vars["aws_region"]
    mock_config_sections.assert_called_once()


def test_region_no_args_vars_exception_1(validator_no_args_vars, mocker):
    """Testing region method without args and vars.
    AnsibleActionFail should be raised because the AWS_DEFAULT_REGION env var is empty.
    """
    mock_config_sections = mocker.patch(
        f"{AWS_HSM}.configparser.ConfigParser.sections", return_value=[]
    )
    mock_os_getenv = mocker.patch("os.getenv", return_value="")
    with pytest.raises(AnsibleActionFail, match=r"^.*aws_region.*$"):
        validator_no_args_vars.region()

    mock_config_sections.assert_called_once()
    mock_os_getenv.assert_called_once()


def test_region_no_args_vars_read_creds_file(
    validator_no_args_vars, absoulte_path, mocker
):
    """Testing region method without args and vars.
    The code should read the config from ~/.aws/config
    Mocker will present mocked data. No exceptions should be raised.
    """
    config = configparser.ConfigParser()
    config.read(f"{absoulte_path}/mocks/config.ini")

    mocker.patch(
        f"{AWS_HSM}.configparser.ConfigParser.read",
        return_value=[f"{absoulte_path}/mocks/config.ini"],
    )

    mock_config_sections = mocker.patch(
        f"{AWS_HSM}.configparser.ConfigParser.sections",
        return_value=config.sections(),
    )
    mock_config_get = mocker.patch(
        f"{AWS_HSM}.configparser.ConfigParser.get",
        return_value=config["default"].get("region"),
    )
    validator_no_args_vars.region()
    assert mock_config_sections.call_count == 2
    assert mock_config_get.call_count == 1


def test_region_no_args_vars_read_creds_file_exception(
    validator_no_args_vars, absoulte_path, mocker
):
    """Testing region method without args and vars.
    The code should read the config from ~/.aws/config
    Mocker will present mocked data.
    AnsibleActionFail should be raised because the aws_region is missing.
    """
    config = configparser.ConfigParser()
    config.read(f"{absoulte_path}/mocks/config.ini")

    mock_config_sections = mocker.patch(
        f"{AWS_HSM}.configparser.ConfigParser.sections",
        return_value=config.sections(),
    )
    mock_config_get = mocker.patch(
        f"{AWS_HSM}.configparser.ConfigParser.get", return_value=None
    )
    with pytest.raises(
        AnsibleActionFail, match=r"^AWS\s+Default\s+Region.*aws_region.*$"
    ):
        validator_no_args_vars.region()

    assert mock_config_sections.call_count == 2
    assert mock_config_get.call_count == 1


def test_region_no_args_vars_exception_2(validator_no_args_vars, absoulte_path, mocker):
    """Testing region method without args and vars.
    AnsibleActionFail should be raised because the no region information was found anywhere.
    """
    config = configparser.ConfigParser()
    config.read(f"{absoulte_path}/mocks/config.ini")

    mock_config_sections = mocker.patch(
        f"{AWS_HSM}.configparser.ConfigParser.sections",
        return_value=["us-east-2"],
    )
    with pytest.raises(
        AnsibleActionFail,
        match=r"^Something\s+went\s+wrong.*$",
    ):
        validator_no_args_vars.region()
    assert mock_config_sections.call_count == 2


#################################################################################################


def test_state_no_vars(validator_no_vars):
    """Testing state method"""
    validator_no_vars.state()


def test_state_no_vars_exception_1(validator_no_vars):
    """Testing state method
    AnsibleActionFail should be raised because the state was not provided as an argument.
    """
    validator_no_vars.module_args.pop("state")
    with pytest.raises(
        AnsibleActionFail, match=r"^\'state\'\s+is\s+a\s+mandatory\s+argument"
    ):
        validator_no_vars.state()


def test_state_no_vars_exception_2(validator_no_vars):
    """Testing state method
    AnsibleActionFail should be raised because wrong value was provided to the state argument.
    """
    validator_no_vars.module_args["state"] = "test"
    with pytest.raises(
        AnsibleActionFail, match=r".*Must\s+be\s+either\s+\'present\'\s+or\s+\'absent\'"
    ):
        validator_no_vars.state()


#################################################################################################


@pytest.mark.parametrize(
    "cluster_id, mandatory",
    [
        (None, False),
        ("cluster-test", False),
        ("cluster-test", True),
        (["cluster-test"], False),
    ],
)
def test_cluster_id(cluster_id, mandatory, validator_no_vars):
    """Testing cluster_id method
    Valid data is provided, no exception is raised"""
    validator_no_vars.module_args["cluster_id"] = cluster_id
    validator_no_vars.cluster_id(mandatory)


@pytest.mark.parametrize(
    "cluster_id, mandatory, match",
    [
        (None, True, "'cluster_id'\\s+is\\s+a\\s+mandatory\\s+argument."),
        (["cluster-test"], True, "Wrong\\s+type\\s+was\\s+provided.*Provided:\\s+list"),
        (1, True, "Wrong\\s+type\\s+was\\s+provided.*Provided:\\s+int"),
        (1, False, "Wrong\\s+type\\s+was\\s+provided.*Provided:\\s+int"),
    ],
)
def test_cluster_id_exception(cluster_id, mandatory, match, validator_no_vars):
    """Testing cluster_id method
    invalid data is provided exception is raised"""
    validator_no_vars.module_args["cluster_id"] = cluster_id
    with pytest.raises(AnsibleActionFail, match=rf"{match}"):
        validator_no_vars.cluster_id(mandatory)


#################################################################################################
def test_name_no_input(validator_no_vars):
    """Testing name method
    No inputs are provided, hence no exception is raised
    """
    validator_no_vars.name()


@pytest.mark.parametrize(
    "module_args, mandatory",
    [
        ({"name": "test-name"}, False),
        ({"name": "test-name"}, True),
    ],
    ids=[
        "Valid argument value test-name mandatory: False",
        "Valid argument value test-name mandatory: True",
    ],
)
def test_name_valid_input(module_args, mandatory, validator_no_vars):
    """Testing DescribeHsmClusterValidator.name method
    A valid input is provided, but no exception is raised
    """
    validator_no_vars.module_args.update(module_args)
    validator_no_vars.name(mandatory)


@pytest.mark.parametrize(
    "module_args, mandatory, match",
    [
        (
            {"name": 90},
            True,
            "^Wrong\\s+type.*\\s+Provided:\\s+int",
        ),
        (
            {"name": True},
            True,
            "^Wrong\\s+type.*\\s+Provided:\\s+bool",
        ),
        (
            {},
            True,
            "^'name'\\s+is\\s+a\\s+mandatory\\s+argument.",
        ),
    ],
    ids=[
        "Disallowed argument value 90",
        "Disallowed argument value True",
        "Missing mandatory value",
    ],
)
def test_name_exception(module_args, mandatory, match, validator_no_vars):
    """Testing DescribeHsmClusterValidator.name method
    Disallowed values are provided as an input, and AnsibleActionFail exception is raised
    """
    validator_no_vars.module_args = {}
    validator_no_vars.module_args.update(module_args)

    with pytest.raises(AnsibleActionFail, match=rf"{match}"):
        validator_no_vars.name(mandatory)


#################################################################################################


def test_main_validation(validator_no_args, mocker, mock_configparser_sections):
    """Testing main_validation method"""
    validator_no_args.main_validation()


#################################################################################################


@pytest.mark.parametrize(
    "filters, output",
    [
        (
            {"state": "DELETED"},
            [],
        ),
        (
            {},
            json_load(f"{ABSOLUTE_PATH}/mocks/hsm_cluster_no_filters_return.json"),
        ),
        (
            {"state": ["UNINITIALIZED"]},
            json_load(
                f"{ABSOLUTE_PATH}/mocks/hsm_cluster_state_uninitialized_return.json"
            ),
        ),
        (
            {"state": "UNINITIALIZED"},
            json_load(
                f"{ABSOLUTE_PATH}/mocks/hsm_cluster_state_uninitialized_return.json"
            ),
        ),
        (
            {"state": ["UNINITIALIZED", "ACTIVE"]},
            json_load(
                f"{ABSOLUTE_PATH}/mocks/hsm_cluster_states_uninitialized_active_return.json"
            ),
        ),
        ({"cluster_id": "cluster-test5"}, []),
        (
            {"cluster_id": "cluster-test"},
            json_load(f"{ABSOLUTE_PATH}/mocks/hsm_cluster_cluster_id_str_return.json"),
        ),
        (
            {"cluster_id": ["cluster-test"]},
            json_load(f"{ABSOLUTE_PATH}/mocks/hsm_cluster_cluster_id_str_return.json"),
        ),
        (
            {"cluster_id": ["cluster-test", "cluster-test1"]},
            json_load(f"{ABSOLUTE_PATH}/mocks/hsm_cluster_cluster_id_list_return.json"),
        ),
        (
            {"name": "test"},
            [],
        ),
        (
            {"name": "123"},
            json_load(f"{ABSOLUTE_PATH}/mocks/hsm_cluster_name_123_return.json"),
        ),
        ("raise", "ClientError"),
    ],
)
def test_get_cluster(filters, output, mock_AwsHsm):
    """Testing _get_cluster"""
    if filters == "raise":
        mock_AwsHsm.client.describe_clusters.side_effect = ClientError(
            error_response={}, operation_name="Testing ConnectionError raise"
        )
        with pytest.raises(
            AnsibleActionFail, match=r"^Something\s+went\s+wrong\s+while.*"
        ):
            mock_AwsHsm._get_cluster({})
    else:
        assert mock_AwsHsm._get_cluster(filters) == output


@pytest.mark.parametrize(
    "filters, extend_search, output",
    [
        (
            {"cluster_id": "cluster-test4"},
            False,
            json_load(f"{ABSOLUTE_PATH}/mocks/hsms.json"),
        ),
        ({"cluster_id": "cluster-test3"}, False, []),
        ({"cluster_id": "cluster-test3"}, True, []),
        (
            {"cluster_id": "cluster-test4"},
            True,
            json_load(f"{ABSOLUTE_PATH}/mocks/hsms.json"),
        ),
        (
            {"cluster_id": "cluster-test4", "eni_id": "eni-test"},
            True,
            [
                {
                    "AvailabilityZone": "us-east-2b",
                    "ClusterId": "cluster-test4",
                    "EniId": "eni-test",
                    "EniIp": "127.0.0.1",
                    "HsmId": "hsm-test",
                    "State": "ACTIVE",
                    "StateMessage": "HSM created.",
                    "SubnetId": "subnet-test",
                },
            ],
        ),
        (
            {"cluster_id": "cluster-test4", "eni_id": ["eni-test", "eni-test1"]},
            True,
            json_load(f"{ABSOLUTE_PATH}/mocks/hsms.json"),
        ),
        (
            {
                "cluster_id": "cluster-test4",
                "eni_id": "eni-test",
                "hsm_id": ["hsm-test1"],
            },
            True,
            json_load(f"{ABSOLUTE_PATH}/mocks/hsms.json"),
        ),
        (
            {"cluster_id": "cluster-test5"},
            True,
            [],
        ),
    ],
)
def test_get_hsm(filters, extend_search, output, mock_AwsHsm):
    """Testing _get_hsm"""
    assert mock_AwsHsm._get_hsm(filters, extend_search) == output


@pytest.mark.parametrize(
    "filters",
    [({"cluster_id": "cluster-123"})],
)
def test_get_hsm_exception(filters, mock_AwsHsm):
    """Testing _get_hsm"""
    with pytest.raises(AnsibleActionFail, match=r"^None\s+existing\s+HSM\s+Cluster.*"):
        mock_AwsHsm._get_hsm(filters)
