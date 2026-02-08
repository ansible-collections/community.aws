# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""Unit tests for cognito_user_pool_client — duplicate name detection."""

import pytest
from unittest.mock import MagicMock, patch

import botocore.exceptions

from ansible_collections.community.aws.plugins.modules.cognito_user_pool_client import (
    CognitoUserPoolClientManager,
)


@pytest.fixture
def manager():
    """Create a CognitoUserPoolClientManager with a mocked module and client."""
    module = MagicMock()
    module.client.return_value = MagicMock()

    mgr = CognitoUserPoolClientManager.__new__(CognitoUserPoolClientManager)
    mgr.module = module
    mgr.client = module.client.return_value
    return mgr


class TestFindClientByName:
    """find_client_by_name should fail when multiple clients share the same name."""

    def test_single_match_returns_client_id(self, manager):
        manager.client.get_paginator.return_value.paginate.return_value = [
            {
                "UserPoolClients": [
                    {"ClientName": "my-app", "ClientId": "id-111"},
                    {"ClientName": "other-app", "ClientId": "id-222"},
                ]
            }
        ]

        result = manager.find_client_by_name("eu-west-1_POOL", "my-app")
        assert result == "id-111"

    def test_no_match_returns_none(self, manager):
        manager.client.get_paginator.return_value.paginate.return_value = [
            {
                "UserPoolClients": [
                    {"ClientName": "other-app", "ClientId": "id-222"},
                ]
            }
        ]

        result = manager.find_client_by_name("eu-west-1_POOL", "my-app")
        assert result is None

    def test_duplicate_names_fails(self, manager):
        manager.client.get_paginator.return_value.paginate.return_value = [
            {
                "UserPoolClients": [
                    {"ClientName": "my-app", "ClientId": "id-111"},
                    {"ClientName": "my-app", "ClientId": "id-222"},
                    {"ClientName": "other-app", "ClientId": "id-333"},
                ]
            }
        ]

        manager.find_client_by_name("eu-west-1_POOL", "my-app")

        manager.module.fail_json.assert_called_once()
        args = manager.module.fail_json.call_args
        assert "Multiple app clients" in args[1]["msg"]
        assert "id-111" in args[1]["msg"]
        assert "id-222" in args[1]["msg"]

    def test_duplicate_names_across_pages_fails(self, manager):
        manager.client.get_paginator.return_value.paginate.return_value = [
            {
                "UserPoolClients": [
                    {"ClientName": "my-app", "ClientId": "id-111"},
                ]
            },
            {
                "UserPoolClients": [
                    {"ClientName": "my-app", "ClientId": "id-222"},
                ]
            },
        ]

        manager.find_client_by_name("eu-west-1_POOL", "my-app")

        manager.module.fail_json.assert_called_once()
        args = manager.module.fail_json.call_args
        assert "Multiple app clients" in args[1]["msg"]
