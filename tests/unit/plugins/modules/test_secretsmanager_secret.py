# -*- coding: utf-8 -*-
# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

__metaclass__ = type

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.community.aws.plugins.modules import secretsmanager_secret


class AnsibleFailJson(Exception):
    """Raised by the mocked module.fail_json to halt execution like the real one does"""


def make_module(params):
    module = MagicMock()
    module.params = params
    module.fail_json.side_effect = AnsibleFailJson
    return module


PROMOTE_PARAMS = {
    "replication_action": "promote_replica",
    "name": "test-example",
    "target_region": "us-west-2",
    "wait_timeout": 60,
}
REMOVE_PARAMS = {
    "replication_action": "remove_regions",
    "name": "test-example",
    "remove_replica_regions": ["us-west-2"],
    "wait_timeout": 60,
}


class TestHelperFunctions:
    """Test pure helper functions without external dependencies"""

    def test_is_replica_in_region_found(self):
        """Replica exists in specified region"""
        current_secret = {
            "ReplicationStatus": [
                {"Region": "us-east-2", "Status": "InSync"},
                {"Region": "us-west-2", "Status": "InSync"},
            ]
        }
        assert secretsmanager_secret.is_replica_in_region(current_secret, "us-east-2") is True

    def test_is_replica_in_region_not_found(self):
        """Replica does not exist in specified region"""
        current_secret = {"ReplicationStatus": [{"Region": "us-east-2", "Status": "InSync"}]}
        assert secretsmanager_secret.is_replica_in_region(current_secret, "eu-west-1") is False

    def test_is_replica_in_region_empty_list(self):
        """No replicas exist"""
        current_secret = {"ReplicationStatus": []}
        assert secretsmanager_secret.is_replica_in_region(current_secret, "us-east-2") is False

    def test_is_replica_in_region_missing_key(self):
        """ReplicationStatus key is missing"""
        current_secret = {}
        assert secretsmanager_secret.is_replica_in_region(current_secret, "us-east-2") is False

    def test_get_region_from_arn_valid(self):
        """Extract region from valid ARN"""
        arn = "arn:aws:secretsmanager:us-west-2:123456789012:secret:my-secret-EXAMPLE"
        assert secretsmanager_secret.get_region_from_arn(arn) == "us-west-2"

    def test_get_region_from_arn_invalid(self):
        """Handle invalid ARN"""
        assert secretsmanager_secret.get_region_from_arn("invalid-arn") is None
        assert secretsmanager_secret.get_region_from_arn(None) is None
        assert secretsmanager_secret.get_region_from_arn("") is None

    def test_is_primary_secret_no_primary_region_field(self):
        """Secret is a primary (no PrimaryRegion field - older format)"""
        current_secret = {
            "ARN": "arn:aws:secretsmanager:us-east-1:000000000000:secret:test-example-EXAMPLE",
            "Name": "test-example",
        }
        assert secretsmanager_secret.is_primary_secret(current_secret) is True

    def test_is_primary_secret_with_matching_primary_region(self):
        """Secret is a primary with PrimaryRegion field matching its own region"""
        current_secret = {
            "ARN": "arn:aws:secretsmanager:us-west-2:000000000000:secret:test-example-EXAMPLE",
            "Name": "test-example",
            "PrimaryRegion": "us-west-2",
            "ReplicationStatus": [{"Region": "eu-west-3", "Status": "InSync"}],
        }
        assert secretsmanager_secret.is_primary_secret(current_secret) is True

    def test_is_primary_secret_false_replica(self):
        """Secret is a replica (PrimaryRegion differs from secret's region)"""
        current_secret = {
            "ARN": "arn:aws:secretsmanager:eu-west-3:000000000000:secret:test-example-EXAMPLE",
            "Name": "test-example",
            "PrimaryRegion": "us-west-2",
        }
        assert secretsmanager_secret.is_primary_secret(current_secret) is False

    @patch("ansible_collections.community.aws.plugins.modules.secretsmanager_secret.boto3_tag_list_to_ansible_dict")
    def test_prepare_result_dict_with_tags(self, mock_tag_converter):
        """prepare_result_dict processes tags and removes metadata"""
        mock_tag_converter.return_value = {"env": "test", "team": "example"}

        secret_dict = {
            "arn": "arn:aws:secretsmanager:us-east-1:000000000000:secret:test-example-EXAMPLE",
            "name": "test-example",
            "tags": [{"Key": "env", "Value": "test"}, {"Key": "team", "Value": "example"}],
            "response_metadata": {"RequestId": "00000000-0000-0000-0000-000000000000", "HTTPStatusCode": 200},
        }

        result = secretsmanager_secret.prepare_result_dict(secret_dict)

        assert result["tags_dict"] == {"env": "test", "team": "example"}
        assert "response_metadata" not in result
        assert result["arn"] == secret_dict["arn"]
        assert result["name"] == secret_dict["name"]
        mock_tag_converter.assert_called_once_with(
            [{"Key": "env", "Value": "test"}, {"Key": "team", "Value": "example"}]
        )

    def test_prepare_result_dict_without_tags(self):
        """prepare_result_dict handles secrets without tags"""
        secret_dict = {
            "arn": "arn:aws:secretsmanager:us-east-1:000000000000:secret:test-example-EXAMPLE",
            "name": "test-example",
            "response_metadata": {"RequestId": "00000000-0000-0000-0000-000000000000"},
        }

        result = secretsmanager_secret.prepare_result_dict(secret_dict)

        assert "tags_dict" not in result
        assert "response_metadata" not in result
        assert result["arn"] == secret_dict["arn"]
        assert result["name"] == secret_dict["name"]


class TestHandleReplicationAction:
    """Test handle_replication_action with a mocked secrets_mgr"""

    @pytest.mark.parametrize(
        ("params", "current_secret", "updated_secret", "mocked_method", "mocked_args"),
        [
            pytest.param(
                PROMOTE_PARAMS,
                {"Name": "test-example", "ReplicationStatus": [{"Region": "us-west-2", "Status": "InSync"}]},
                {"Name": "test-example", "ReplicationStatus": []},
                "promote_replica",
                ("test-example", "us-west-2"),
                id="promote_replica",
            ),
            pytest.param(
                REMOVE_PARAMS,
                {
                    "Name": "test-example",
                    "ReplicationStatus": [
                        {"Region": "us-west-2", "Status": "InSync"},
                        {"Region": "eu-west-1", "Status": "InSync"},
                    ],
                },
                {"Name": "test-example", "ReplicationStatus": [{"Region": "eu-west-1", "Status": "InSync"}]},
                "remove_replication",
                ("test-example", ["us-west-2"]),
                id="remove_regions",
            ),
        ],
    )
    def test_action_not_idempotent(self, params, current_secret, updated_secret, mocked_method, mocked_args):
        """A replica change is needed: the AWS call is made and the updated secret is returned"""
        module = make_module(params)
        secrets_mgr = MagicMock()
        secrets_mgr.get_secret.return_value = updated_secret

        result = secretsmanager_secret.handle_replication_action(module, secrets_mgr, current_secret)

        getattr(secrets_mgr, mocked_method).assert_called_once_with(*mocked_args)
        assert result["changed"] is True
        assert result["result"] == camel_dict_to_snake_dict(updated_secret)
        module.fail_json.assert_not_called()

    @pytest.mark.parametrize(
        ("params", "current_secret", "mocked_method", "expected_msg"),
        [
            pytest.param(
                PROMOTE_PARAMS,
                {"Name": "test-example", "ReplicationStatus": []},
                "promote_replica",
                "No replica exists",
                id="promote_replica",
            ),
            pytest.param(
                REMOVE_PARAMS,
                {"Name": "test-example", "ReplicationStatus": [{"Region": "eu-west-1", "Status": "InSync"}]},
                "remove_replication",
                "No replicas exist",
                id="remove_regions",
            ),
        ],
    )
    def test_action_idempotent(self, params, current_secret, mocked_method, expected_msg):
        """No matching replica change is needed: the AWS call is skipped"""
        module = make_module(params)
        secrets_mgr = MagicMock()

        result = secretsmanager_secret.handle_replication_action(module, secrets_mgr, current_secret)

        getattr(secrets_mgr, mocked_method).assert_not_called()
        assert result["changed"] is False
        assert expected_msg in result["msg"]

    @patch("ansible_collections.community.aws.plugins.modules.secretsmanager_secret.time.time", side_effect=[0, 100])
    def test_action_timeout(self, mock_time):
        """Replication never propagates: module.fail_json is called with a timeout message.

        The deadline is faked to have already passed by the first check, so the test
        doesn't actually sleep. The wait/timeout mechanism in wait_for_secret_condition()
        is shared by both replication_action branches, so exercising it once here is
        sufficient; the per-branch idempotency checks are covered separately above.
        """
        current_secret = {"Name": "test-example", "ReplicationStatus": [{"Region": "us-west-2", "Status": "InSync"}]}
        module = make_module(PROMOTE_PARAMS)
        secrets_mgr = MagicMock()
        secrets_mgr.get_secret.return_value = current_secret  # state never changes

        with pytest.raises(AnsibleFailJson):
            secretsmanager_secret.handle_replication_action(module, secrets_mgr, current_secret)

        module.fail_json.assert_called_once()
        assert "Timeout" in module.fail_json.call_args.kwargs["msg"]
