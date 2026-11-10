# -*- coding: utf-8 -*-
# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

__metaclass__ = type

from unittest.mock import patch

from ansible_collections.community.aws.plugins.modules import secretsmanager_secret


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
