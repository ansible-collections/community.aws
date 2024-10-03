# (c) 2017 Red Hat Inc.
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from unittest.mock import MagicMock
from unittest.mock import Mock

import pytest

from ansible_collections.community.aws.plugins.modules import ec2_vpc_vpn


@pytest.fixture
def ansible_module():
    module = MagicMock()
    module.check_mode = False
    module.params = {"delay": 5, "wait_timeout": 30}
    module.fail_json.side_effect = SystemExit(1)
    module.fail_json_aws.side_effect = SystemExit(1)

    return module


@pytest.mark.parametrize(
    "vpn_connections, expected_result, expected_exception",
    [
        # Case 1: Single VPN connection available
        (
            {"VpnConnections": [{"VpnConnectionId": "vpn-123", "State": "available"}]},
            {"VpnConnectionId": "vpn-123", "State": "available"},
            None,
        ),
        # Case 2: Multiple valid VPN connections available (expecting an exception)
        (
            {
                "VpnConnections": [
                    {"VpnConnectionId": "vpn-123", "State": "available"},
                    {"VpnConnectionId": "vpn-456", "State": "available"},
                ]
            },
            None,
            "More than one matching VPN connection was found. To modify or delete a VPN please specify vpn_connection_id or add filters.",
        ),
        # Case 3: No VPN connections available
        ({"VpnConnections": []}, None, None),
        # Case 4: Multiple connections with one deleted (expecting the viable connection)
        (
            {
                "VpnConnections": [
                    {"VpnConnectionId": "vpn-123", "State": "deleted"},
                    {"VpnConnectionId": "vpn-456", "State": "available"},
                ]
            },
            {"VpnConnectionId": "vpn-456", "State": "available"},
            None,
        ),
    ],
)
def test_find_connection_response(ansible_module, vpn_connections, expected_result, expected_exception):
    if expected_exception:
        with pytest.raises(SystemExit) as e:  # Assuming fail_json raises SystemExit
            ec2_vpc_vpn.find_connection_response(ansible_module, vpn_connections)
        assert e.value.code == 1  # Ensure exit code is as expected
        # Check that the message is the same as expected
        assert str(ansible_module.fail_json.call_args[1]["msg"]) == expected_exception
    else:
        result = ec2_vpc_vpn.find_connection_response(ansible_module, vpn_connections)
        assert result == expected_result


@pytest.mark.parametrize(
    "vpn_connection_id, filters, describe_response, expected_result, expected_exception",
    [
        # Case 1: Single VPN connection found
        (
            "vpn-123",
            None,
            {"VpnConnections": [{"VpnConnectionId": "vpn-123", "State": "available"}]},
            {"VpnConnectionId": "vpn-123", "State": "available"},
            None,
        ),
        # Case 2: Multiple VPN connections found (expecting an exception)
        (
            "vpn-123",
            None,
            {
                "VpnConnections": [
                    {"VpnConnectionId": "vpn-123", "State": "available"},
                    {"VpnConnectionId": "vpn-456", "State": "available"},
                ]
            },
            None,
            "More than one matching VPN connection was found. To modify or delete a VPN please specify vpn_connection_id or add filters.",
        ),
        # Case 3: No VPN connections found
        ("vpn-123", None, {"VpnConnections": []}, None, None),
    ],
)
def test_find_vpn_connection(
    ansible_module, vpn_connection_id, filters, describe_response, expected_result, expected_exception
):
    client = Mock()
    ansible_module.params = {"vpn_connection_id": vpn_connection_id, "filters": filters}

    # Mock the describe_vpn_connections function
    client.describe_vpn_connections.return_value = describe_response if describe_response else {}

    if expected_exception:
        if "More than one matching VPN connection" in expected_exception:
            with pytest.raises(SystemExit) as e:
                ec2_vpc_vpn.find_vpn_connection(client, ansible_module)
            # Check that the exception message matches the expected exception
            assert str(ansible_module.fail_json.call_args[1]["msg"]) == expected_exception
    else:
        result = ec2_vpc_vpn.find_vpn_connection(client, ansible_module)
        assert result == expected_result


@pytest.mark.parametrize(
    "provided_filters, expected_result, expected_exception",
    [
        ({"cgw": "cgw-123"}, [{"Name": "customer-gateway-id", "Values": ["cgw-123"]}], None),
        ({"invalid_filter": "value"}, None, "invalid_filter is not a valid filter."),
        (
            {"tags": {"key1": "value1", "key2": "value2"}},
            [{"Name": "tag:key1", "Values": ["value1"]}, {"Name": "tag:key2", "Values": ["value2"]}],
            None,
        ),
        ({"static-routes-only": True}, [{"Name": "option.static-routes-only", "Values": ["true"]}], None),
    ],
)
def test_create_filter(ansible_module, provided_filters, expected_result, expected_exception):
    if expected_exception:
        with pytest.raises(SystemExit) as e:
            ec2_vpc_vpn.create_filter(ansible_module, provided_filters)
        # Check that the exception message matches the expected exception
        assert str(ansible_module.fail_json.call_args[1]["msg"]) == expected_exception
    else:
        result = ec2_vpc_vpn.create_filter(ansible_module, provided_filters)
        assert result == expected_result


@pytest.mark.parametrize(
    "params, expected_result, expected_exception",
    [
        # Case 1: Successful creation of a VPN connection
        (
            {"customer_gateway_id": "cgw-123", "vpn_gateway_id": "vgw-123", "static_only": True},
            {"VpnConnectionId": "vpn-123"},
            None,
        ),
        # Case 3: Missing required parameters (simulating failure)
        (
            {"customer_gateway_id": None, "vpn_gateway_id": "vgw-123", "static_only": True},
            None,
            "No matching connection was found. To create a new connection you must provide customer_gateway_id and one of either transit_gateway_id or vpn_gateway_id.",
        ),
        # Case 4: Both customer gateway and VPN gateway are None
        (
            {"customer_gateway_id": None, "vpn_gateway_id": None, "static_only": False},
            None,
            "No matching connection was found. To create a new connection you must provide customer_gateway_id and one of either transit_gateway_id or vpn_gateway_id.",
        ),
        # Case 5: Optional parameters passed (e.g., static routes)
        (
            {"customer_gateway_id": "cgw-123", "vpn_gateway_id": "vgw-123", "static_only": True},
            {"VpnConnectionId": "vpn-456"},
            None,
        ),
    ],
)
def test_create_connection(ansible_module, params, expected_result, expected_exception):
    client = Mock()
    ansible_module.params = params

    if expected_exception:
        client.create_vpn_connection.side_effect = Exception("AWS Error")
        with pytest.raises(SystemExit) as e:  # Assuming fail_json raises SystemExit
            ec2_vpc_vpn.create_connection(
                client,
                ansible_module,
                params["customer_gateway_id"],
                params["static_only"],
                params["vpn_gateway_id"],
                None,
                None,
                None,
                None,
                None,
            )
        # Check that the exception message matches the expected exception
        assert str(ansible_module.fail_json.call_args[1]["msg"]) == expected_exception
    else:
        client.create_vpn_connection.return_value = {"VpnConnection": expected_result}
        result = ec2_vpc_vpn.create_connection(
            client,
            ansible_module,
            params["customer_gateway_id"],
            params["static_only"],
            params["vpn_gateway_id"],
            None,
            None,
            None,
            None,
            None,
        )
        assert result == expected_result


@pytest.mark.parametrize(
    "vpn_connection_id, routes, purge_routes, current_routes, expected_result",
    [
        # Case 1: No changes in routes
        (
            "vpn-123",
            ["10.0.0.0/16"],
            False,
            [{"DestinationCidrBlock": "10.0.0.0/16"}],
            {"routes_to_add": [], "routes_to_remove": []},
        ),
        # Case 3: Old routes empty, new routes not empty
        ("vpn-123", ["10.0.1.0/16"], False, [], {"routes_to_add": ["10.0.1.0/16"], "routes_to_remove": []}),
        # Case 4: New routes empty, old routes not empty
        (
            "vpn-123",
            [],
            False,
            [{"DestinationCidrBlock": "10.0.0.0/16"}],
            {"routes_to_add": [], "routes_to_remove": []},
        ),
        # Case 5: Purge routes - removing non-existent routes
        (
            "vpn-123",
            ["10.0.1.0/16"],
            True,
            [{"DestinationCidrBlock": "10.0.0.0/16"}],
            {"routes_to_add": ["10.0.1.0/16"], "routes_to_remove": ["10.0.0.0/16"]},
        ),
        # Case 6: Both old and new routes are empty
        ("vpn-123", [], False, [], {"routes_to_add": [], "routes_to_remove": []}),
        # Case 7: Purge routes with existing routes
        (
            "vpn-123",
            [],
            True,
            [{"DestinationCidrBlock": "10.0.0.0/16"}],
            {"routes_to_add": [], "routes_to_remove": ["10.0.0.0/16"]},
        ),
    ],
)
def test_check_for_routes_update(
    ansible_module, vpn_connection_id, routes, purge_routes, current_routes, expected_result
):
    ansible_module.params = {
        "routes": routes,
        "purge_routes": purge_routes,
    }

    # Mock the find_vpn_connection function
    client = MagicMock()
    ec2_vpc_vpn.find_vpn_connection = Mock(return_value={"Routes": current_routes})

    # Call the function and check results
    result = ec2_vpc_vpn.check_for_routes_update(client, ansible_module, vpn_connection_id)
    assert result == expected_result
