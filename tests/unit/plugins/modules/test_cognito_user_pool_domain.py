# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for cognito_user_pool_domain — pool-ID mismatch validation."""

import pytest
from unittest.mock import MagicMock, patch

from ansible_collections.community.aws.plugins.modules.cognito_user_pool_domain import main


@pytest.fixture
def mock_module():
    """Create a mock AnsibleAWSModule."""
    with patch(
        "ansible_collections.community.aws.plugins.modules.cognito_user_pool_domain.AnsibleAWSModule"
    ) as MockModule:
        module = MockModule.return_value
        module.check_mode = False
        module.client.return_value = MagicMock()
        yield module


class TestDomainPoolIdMismatch:
    """When a domain exists but belongs to a different pool, the module should fail."""

    def test_present_with_wrong_pool_id_fails(self, mock_module):
        mock_module.params = {
            "state": "present",
            "domain": "my-domain",
            "user_pool_id": "eu-west-1_AAAA",
            "managed_login_version": None,
            "custom_domain_config": None,
        }

        # Simulate DescribeUserPoolDomain returning a domain owned by a different pool
        cognito_client = mock_module.client.return_value
        cognito_client.describe_user_pool_domain.return_value = {
            "DomainDescription": {
                "Domain": "my-domain",
                "UserPoolId": "eu-west-1_BBBB",
                "Status": "ACTIVE",
            }
        }

        main()

        mock_module.fail_json.assert_called_once()
        args = mock_module.fail_json.call_args
        assert "eu-west-1_BBBB" in args[1]["msg"]
        assert "eu-west-1_AAAA" in args[1]["msg"]

    def test_absent_with_wrong_pool_id_fails(self, mock_module):
        mock_module.params = {
            "state": "absent",
            "domain": "my-domain",
            "user_pool_id": "eu-west-1_AAAA",
            "managed_login_version": None,
            "custom_domain_config": None,
        }

        cognito_client = mock_module.client.return_value
        cognito_client.describe_user_pool_domain.return_value = {
            "DomainDescription": {
                "Domain": "my-domain",
                "UserPoolId": "eu-west-1_BBBB",
                "Status": "ACTIVE",
            }
        }

        main()

        mock_module.fail_json.assert_called_once()
        args = mock_module.fail_json.call_args
        assert "different pool" in args[1]["msg"]

    def test_present_with_correct_pool_id_does_not_fail(self, mock_module):
        mock_module.params = {
            "state": "present",
            "domain": "my-domain",
            "user_pool_id": "eu-west-1_AAAA",
            "managed_login_version": None,
            "custom_domain_config": None,
        }

        cognito_client = mock_module.client.return_value
        cognito_client.describe_user_pool_domain.return_value = {
            "DomainDescription": {
                "Domain": "my-domain",
                "UserPoolId": "eu-west-1_AAAA",
                "Status": "ACTIVE",
            }
        }

        main()

        mock_module.fail_json.assert_not_called()
