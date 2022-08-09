"""pytest fixtures"""
import json
import os
import sys

import pytest

sys.path.append("plugins/module_utils")
from aws_hsm import AwsHsm, Validator
from constants import *
from create_cluster import CreateHsmCluster
from create_hsm import CreateHsm
from describe_cluster import DescribeHsmCluster
from describe_hsm import DescribeHsm
from initialize_cluster import HsmClusterInit


@pytest.fixture()
def absoulte_path():
    """pytest fixture which returns absolute path to the tests folder"""
    return os.path.dirname(os.path.abspath(__file__))


@pytest.fixture(
    params=[
        [
            {
                "aws_access_key": "TESTAWSACCESSKEY",
                "aws_secret_key": "testawssecretkey",
                "region": "us-east-2",
                "state": "absent",
            },
            {},
        ]
    ],
)
def validator_no_vars(request):
    """pytest fixture to instantiate Validator without vars"""
    return Validator(request.param[0], request.param[1])


@pytest.fixture(
    params=[
        [
            {"state": "absent"},
            {
                "aws_access_key": "TESTAWSACCESSKEY",
                "aws_secret_key": "testawssecretkey",
                "aws_region": "us-east-2",
            },
        ]
    ]
)
def validator_no_args(request):
    """pytest fixture to instantiate Validator with vars and required args"""
    return Validator(request.param[0], request.param[1])


@pytest.fixture(params=[[{}, {}]])
def validator_no_args_vars(request):
    """pytest fixture to instantiate Validator without vars and args"""
    return Validator(request.param[0], request.param[1])


@pytest.fixture()
def mock_boto3(mocker, absoulte_path):
    """pytest fixture to instantiate boto3"""

    def mock_describe_clusters(Filters):
        return_data = {
            "Clusters": [],
            "ResponseMetadata": {
                "RequestId": "test-test-test-test-testtest",
                "HTTPStatusCode": 200,
                "HTTPHeaders": {
                    "x-amzn-requestid": "test-test-test-test-testtest",
                    "content-type": "application/x-amz-json-1.1",
                    "content-length": "468",
                    "date": "Sat, 23 Jul 2022 23: 57:29 GMT",
                },
                "RetryAttempts": 0,
            },
        }
        raw_data = json.load(open(f"{absoulte_path}/mocks/hsm_cluster_default.json"))
        if Filters == {}:
            return raw_data
        else:
            if "states" in Filters:
                for state in Filters["states"]:
                    for cluster in raw_data["Clusters"]:
                        if cluster["State"] == state:
                            return_data["Clusters"].append(cluster)
            elif "clusterIds" in Filters:
                for cluster_id in Filters["clusterIds"]:
                    for cluster in raw_data["Clusters"]:
                        if cluster["ClusterId"] == cluster_id:
                            return_data["Clusters"].append(cluster)
        return return_data

    def mock_create_hsm(ClusterId, AvailabilityZone, IpAddress=None):
        return_data = {
            "Hsm": {
                "AvailabilityZone": AvailabilityZone,
                "ClusterId": ClusterId,
                "EniId": "eni-test",
                "HsmId": "hsm-test",
                "State": "ACTIVE",
                "StateMessage": "HSM created.",
                "SubnetId": "subnet-test",
            }
        }
        if IpAddress:
            return_data["Hsm"]["EniIp"] = IpAddress
        else:
            return_data["Hsm"]["EniIp"] = "127.0.0.1"
        return return_data

    def mock_delete_hsm(ClusterId, HsmId=None, EniIp=None, EniId=None):
        hsm_cluster = json.load(
            open(absoulte_path + "/mocks/hsm_cluster_with_hsm.json")
        )
        hsms = hsm_cluster["Clusters"][0]["Hsms"]
        return_body = {}
        for hsm in hsms:
            if not HsmId and not EniIp and not EniId:
                return return_body
            if HsmId and hsm["HsmId"] == HsmId:
                return_body["Hsm"] = HsmId
                return return_body
            if EniIp and hsm["EniIp"] == EniIp:
                return_body["Hsm"] = hsm["HsmId"]
                return return_body
            if EniId and hsm["EniId"] == EniId:
                return_body["Hsm"] = hsm["HsmId"]
                return return_body
        raise Exception(
            "CloudHSMV2.Client.exceptions.CloudHsmResourceNotFoundException"
        )

    boto3_cls = mocker.patch(f"{AWS_HSM}.boto3.client")
    boto3_obj = boto3_cls.return_value

    boto3_obj.describe_clusters.side_effect = mock_describe_clusters
    boto3_obj.create_cluster.return_value = json.load(
        open(absoulte_path + "/mocks/hsm_cluster_create.json")
    )

    boto3_obj.delete_cluster.side_effect = json.load(
        open(absoulte_path + "/mocks/hsm_cluster_create.json")
    )

    boto3_obj.create_hsm.side_effect = mock_create_hsm
    boto3_obj.delete_hsm.side_effect = mock_delete_hsm

    boto3_obj.initialize_cluster.side_effect = [
        {
            "State": "INITIALIZE_IN_PROGRESS",
            "StateMessage": "Test initialization",
            "ResponseMetadata": {
                "RequestId": "test-test-test-test-testtest",
                "HTTPStatusCode": 200,
                "HTTPHeaders": {
                    "x-amzn-requestid": "test-test-test-test-testtest",
                    "content-type": "application/x-amz-json-1.1",
                    "content-length": "468",
                    "date": "Sat, 23 Jul 2022 23: 57: 29 GMT",
                },
                "RetryAttempts": 0,
            },
        }
    ]


@pytest.fixture()
def mock_AwsHsm(mock_boto3):
    """pytest fixture to instantiate AwsHsm class"""
    return AwsHsm()


@pytest.fixture()
def mock_configparser_sections(mocker):
    """pytest fixture to patch ConfigParser.sections method"""
    mocker.patch(
        f"{AWS_HSM}.configparser.ConfigParser.sections",
        return_value=[],
    )


@pytest.fixture(
    params=[
        [
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
        ]
    ],
)
def mock_CreateHsmCluster(request, mock_configparser_sections, mock_boto3):
    """pytest fixture to instantiate CreateHsmCluster class"""
    return CreateHsmCluster(request.param[0], request.param[1])


@pytest.fixture(
    params=[
        [
            {
                "aws_access_key": "TESTAWSACCESSKEY",
                "aws_secret_key": "testawssecretkey",
                "region": "us-east-2",
            },
            {},
        ]
    ],
)
def mock_DescribeHsmCluster(request, mock_configparser_sections, mock_boto3):
    """pytest fixture to instantiate DescribeHsmCluster class"""
    return DescribeHsmCluster(request.param[0], request.param[1])


@pytest.fixture(
    params=[
        [
            {
                "aws_access_key": "TESTAWSACCESSKEY",
                "aws_secret_key": "testawssecretkey",
                "region": "us-east-2",
            },
            {},
        ]
    ],
)
def mock_DescribeHsm(request, mock_configparser_sections, mock_boto3):
    """pytest fixture to instantiate DescribeHsm class"""
    return DescribeHsm(request.param[0], request.param[1])


@pytest.fixture(
    params=[
        [
            {
                "availability_zone": "us-west-2b",
                "cluster_id": "cluster-test",
                "state": "present",
                "aws_access_key": "TESTAWSACCESSKEY",
                "aws_secret_key": "testawssecretkey",
                "region": "us-east-2",
            },
            {},
        ]
    ]
)
def mock_CreateHsm(request, mock_configparser_sections, mock_boto3):
    """pytest fixture to instantiate CreateHsm class"""
    return CreateHsm(request.param[0], request.param[1])


@pytest.fixture(
    params=[
        [
            {
                "cluster_id": "cluster-test",
                "signed_cert": "./tests/unit/module_utils/mocks/hsm_signed.crt",
                "trust_anchor": "./tests/unit/module_utils/mocks/customerCA.crt",
                "aws_access_key": "TESTAWSACCESSKEY",
                "aws_secret_key": "testawssecretkey",
                "region": "us-east-2",
            },
            {},
        ]
    ]
)
def mock_HsmClusterInit(request, mock_configparser_sections, mock_boto3):
    """pytest fixture to instantiate HsmClusterInit class"""
    return HsmClusterInit(request.param[0], request.param[1])
