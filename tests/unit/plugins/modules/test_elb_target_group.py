# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from ansible_collections.community.aws.plugins.modules import elb_target_group

mod_name = "ansible_collections.community.aws.plugins.modules.elb_target_group"

TG_ARN = "arn:aws:elasticloadbalancing:us-east-1:123456789012:targetgroup/my-tg/0123456789abcdef"


@pytest.fixture(name="module")
def fixture_module():
    module = MagicMock()
    module.params = {
        "name": "my-tg",
        "target_type": "ip",
        "protocol": "http",
        "protocol_version": None,
        "ip_address_type": None,
        "port": 80,
        "vpc_id": "vpc-0123456",
        "tags": None,
        "purge_tags": True,
        "health_check_path": None,
        "health_check_protocol": None,
        "health_check_port": None,
        "health_check_interval": None,
        "health_check_timeout": None,
        "healthy_threshold_count": None,
        "unhealthy_threshold_count": None,
        "successful_response_codes": None,
        "modify_targets": False,
        "targets": None,
        "wait": False,
    }
    module.fail_json.side_effect = SystemExit(1)
    module.fail_json_aws.side_effect = SystemExit(1)
    module.exit_json.side_effect = SystemExit(0)
    return module


def _existing_target_group(ip_address_type):
    return {
        "TargetGroupArn": TG_ARN,
        "TargetGroupName": "my-tg",
        "TargetType": "ip",
        "Protocol": "HTTP",
        "Port": 80,
        "VpcId": "vpc-0123456",
        "IpAddressType": ip_address_type,
    }


@pytest.mark.parametrize("ip_address_type", ["ipv4", "ipv6"])
@patch(mod_name + ".get_target_group_tags", return_value=[])
@patch(mod_name + ".get_tg_attributes", return_value={})
@patch(mod_name + ".create_or_update_attributes", return_value=False)
@patch(mod_name + ".get_target_group")
def test_create_passes_ip_address_type(
    m_get_target_group, _m_attributes, _m_get_tg_attributes, _m_tags, module, ip_address_type
):
    connection = MagicMock()
    module.params["ip_address_type"] = ip_address_type
    m_get_target_group.side_effect = [
        None,
        _existing_target_group(ip_address_type),
        _existing_target_group(ip_address_type),
    ]

    with pytest.raises(SystemExit):
        elb_target_group.create_or_update_target_group(connection, module)

    connection.create_target_group.assert_called_once()
    assert connection.create_target_group.call_args.kwargs["IpAddressType"] == ip_address_type
    assert module.exit_json.call_args.kwargs["changed"] is True
    assert module.exit_json.call_args.kwargs["ip_address_type"] == ip_address_type


@patch(mod_name + ".get_target_group_tags", return_value=[])
@patch(mod_name + ".get_tg_attributes", return_value={})
@patch(mod_name + ".create_or_update_attributes", return_value=False)
@patch(mod_name + ".get_target_group")
def test_create_without_ip_address_type(m_get_target_group, _m_attributes, _m_get_tg_attributes, _m_tags, module):
    connection = MagicMock()
    m_get_target_group.side_effect = [None, _existing_target_group("ipv4"), _existing_target_group("ipv4")]

    with pytest.raises(SystemExit):
        elb_target_group.create_or_update_target_group(connection, module)

    assert "IpAddressType" not in connection.create_target_group.call_args.kwargs


@pytest.mark.parametrize("ip_address_type", [None, "ipv6"])
@patch(mod_name + ".get_target_group_tags", return_value=[])
@patch(mod_name + ".get_tg_attributes", return_value={})
@patch(mod_name + ".create_or_update_attributes", return_value=False)
@patch(mod_name + ".get_target_group")
def test_existing_with_same_ip_address_type(
    m_get_target_group, _m_attributes, _m_get_tg_attributes, _m_tags, module, ip_address_type
):
    connection = MagicMock()
    module.params["ip_address_type"] = ip_address_type
    m_get_target_group.return_value = _existing_target_group("ipv6")

    with pytest.raises(SystemExit):
        elb_target_group.create_or_update_target_group(connection, module)

    module.fail_json.assert_not_called()
    connection.create_target_group.assert_not_called()
    assert module.exit_json.call_args.kwargs["changed"] is False


@patch(mod_name + ".get_target_group")
def test_existing_with_different_ip_address_type(m_get_target_group, module):
    connection = MagicMock()
    module.params["ip_address_type"] = "ipv6"
    m_get_target_group.return_value = _existing_target_group("ipv4")

    with pytest.raises(SystemExit):
        elb_target_group.create_or_update_target_group(connection, module)

    module.fail_json.assert_called_once_with(msg="Cannot modify IpAddressType parameter(s) for a target group")
    connection.create_target_group.assert_not_called()
