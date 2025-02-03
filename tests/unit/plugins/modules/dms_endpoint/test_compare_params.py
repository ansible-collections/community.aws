# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from unittest.mock import patch

import pytest

from ansible_collections.community.aws.plugins.modules.dms_endpoint import compare_params


@pytest.mark.parametrize(
    "described_params,created_params,expected_result",
    [
        [dict(), dict(), False],
        # Tags and Password should be ignored
        [dict(Tags={"Somekey": "SomeValue"}), dict(Tags={"Somekey": "SomeValue"}), False],
        [dict(Tags={"Somekey": "SomeValue"}), dict(Tags={"Somekey": "Another"}), False],
        [dict(Tags={"Somekey": "Another"}), dict(), False],
        [dict(), dict(Tags={"Somekey": "Another"}), False],
        [dict(Password="Example"), dict(Password="Example"), False],
        [dict(Password="Example"), dict(Password="AnotherExample"), False],
        [dict(Password="AnotherExample"), dict(), False],
        [dict(), dict(Password="AnotherExample"), False],
        # Everything else should be compared
        [dict(EngineDisplayName="ADisplayName"), dict(EngineDisplayName="ADisplayName"), False],
        [dict(EngineDisplayName="ADisplayName"), dict(EngineDisplayName="Not that display name"), True],
        # Ignore extra values in output from describe_endpoint(), the API changes over time, we only
        # care about the things we manage, if they're missing from the described output it's a change
        [dict(NewKey="my value"), dict(), False],
        [dict(), dict(NewKey="my value"), True],
        # Cope with case-insensitivity for some of the keyword values
        [dict(SslMode="none"), dict(SslMode="none"), False],
        [dict(SslMode="None"), dict(SslMode="none"), False],
        [dict(SslMode="NONE"), dict(SslMode="none"), False],
        [dict(SslMode="none"), dict(SslMode="verify-ca"), True],
        [dict(SslMode="None"), dict(SslMode="verify-ca"), True],
        # Bools, and Ints are also valid
        [dict(Port=123), dict(Port=123), False],
        [dict(Port=123), dict(Port=321), True],
        [dict(NoHexPrefix=True), dict(NoHexPrefix=True), False],
        [dict(NoHexPrefix=False), dict(NoHexPrefix=False), False],
        [dict(NoHexPrefix=False), dict(NoHexPrefix=True), True],
        # Slightly more complex example
        [
            dict(Tags={"a": "b"}, Password="Example", EngineDisplayName="ADisplayName", SslMode="none", NewKey="123"),
            dict(Tags={"a": "b"}, Password="Example", EngineDisplayName="ADisplayName", SslMode="none"),
            False,
        ],
        [
            dict(EngineDisplayName="ADisplayName", SslMode="None"),
            dict(Tags={"a": "b"}, Password="Example", EngineDisplayName="ADisplayName", SslMode="none"),
            False,
        ],
        [
            dict(EngineDisplayName="ADisplayName", SslMode="none"),
            dict(Tags={"a": "b"}, Password="Example", EngineDisplayName="ADisplayName", SslMode="verify-ca"),
            True,
        ],
        [
            dict(EngineDisplayName="ADisplayName", SslMode="none"),
            dict(Tags={"a": "b"}, Password="Example", EngineDisplayName="Not that Name", SslMode="none"),
            True,
        ],
    ],
)
@patch("ansible_collections.community.aws.plugins.modules.dms_endpoint.create_module_params")
def test_compare_params(mock_create_module_params, described_params, created_params, expected_result):
    mock_create_module_params.return_value = dict(created_params)
    assert compare_params(described_params) is expected_result
