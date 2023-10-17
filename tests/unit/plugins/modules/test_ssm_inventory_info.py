# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest
from botocore.exceptions import BotoCoreError

from ansible_collections.community.aws.plugins.modules.ssm_inventory_info import SsmInventoryInfoFailure
from ansible_collections.community.aws.plugins.modules.ssm_inventory_info import execute_module
from ansible_collections.community.aws.plugins.modules.ssm_inventory_info import get_ssm_inventory


def test_get_ssm_inventory():
    connection = MagicMock()
    inventory_response = MagicMock()
    connection.get_inventory.return_value = inventory_response
    filters = MagicMock()

    assert get_ssm_inventory(connection, filters) == inventory_response
    connection.get_inventory.assert_called_once_with(Filters=filters)


def test_get_ssm_inventory_failure():
    connection = MagicMock()
    connection.get_inventory.side_effect = BotoCoreError(error="failed", operation="get_ssm_inventory")
    filters = MagicMock()

    with pytest.raises(SsmInventoryInfoFailure):
        get_ssm_inventory(connection, filters)


@patch("ansible_collections.community.aws.plugins.modules.ssm_inventory_info.get_ssm_inventory")
def test_execute_module(m_get_ssm_inventory):
    instance_id = "i-0202020202020202"
    aws_inventory = {
        "AgentType": "amazon-ssm-agent",
        "AgentVersion": "3.2.582.0",
        "ComputerName": "ip-172-31-44-166.ec2.internal",
        "InstanceId": "i-039eb9b1f55934ab6",
        "InstanceStatus": "Active",
        "IpAddress": "172.31.44.166",
        "PlatformName": "Fedora Linux",
        "PlatformType": "Linux",
        "PlatformVersion": "37",
        "ResourceType": "EC2Instance",
    }

    ansible_inventory = {
        "agent_type": "amazon-ssm-agent",
        "agent_version": "3.2.582.0",
        "computer_name": "ip-172-31-44-166.ec2.internal",
        "instance_id": "i-039eb9b1f55934ab6",
        "instance_status": "Active",
        "ip_address": "172.31.44.166",
        "platform_name": "Fedora Linux",
        "platform_type": "Linux",
        "platform_version": "37",
        "resource_type": "EC2Instance",
    }

    m_get_ssm_inventory.return_value = {
        "Entities": [{"Id": instance_id, "Data": {"AWS:InstanceInformation": {"Content": [aws_inventory]}}}],
        "Status": 200,
    }

    connection = MagicMock()
    module = MagicMock()
    module.params = dict(instance_id=instance_id)
    module.exit_json.side_effect = SystemExit(1)
    module.fail_json_aws.side_effect = SystemError(2)

    with pytest.raises(SystemExit):
        execute_module(module, connection)

    module.exit_json.assert_called_once_with(changed=False, ssm_inventory=ansible_inventory)


@patch("ansible_collections.community.aws.plugins.modules.ssm_inventory_info.get_ssm_inventory")
def test_execute_module_no_data(m_get_ssm_inventory):
    instance_id = "i-0202020202020202"

    m_get_ssm_inventory.return_value = {
        "Entities": [{"Id": instance_id, "Data": {}}],
    }

    connection = MagicMock()
    module = MagicMock()
    module.params = dict(instance_id=instance_id)
    module.exit_json.side_effect = SystemExit(1)
    module.fail_json_aws.side_effect = SystemError(2)

    with pytest.raises(SystemExit):
        execute_module(module, connection)

    module.exit_json.assert_called_once_with(changed=False, ssm_inventory={})


@patch("ansible_collections.community.aws.plugins.modules.ssm_inventory_info.get_ssm_inventory")
def test_execute_module_failure(m_get_ssm_inventory):
    instance_id = "i-0202020202020202"

    m_get_ssm_inventory.side_effect = SsmInventoryInfoFailure(
        exc=BotoCoreError(error="failed", operation="get_ssm_inventory"), msg="get_ssm_inventory() failed."
    )

    connection = MagicMock()
    module = MagicMock()
    module.params = dict(instance_id=instance_id)
    module.exit_json.side_effect = SystemExit(1)
    module.fail_json_aws.side_effect = SystemError(2)

    with pytest.raises(SystemError):
        execute_module(module, connection)
