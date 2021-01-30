# (c) 2021 Ethem Cem Özkan
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)

__metaclass__ = type

import pytest
import pytest_mock
import datetime
from copy import copy

from ansible.errors import AnsibleError
from ansible.plugins.loader import lookup_loader

from ansible_collections.community.aws.plugins.lookup import aws_cloudformation

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    pytestmark = pytest.mark.skip("This test requires the boto3 and botocore Python libraries")


@pytest.fixture
def dummy_credentials():
    dummy_credentials = {}
    dummy_credentials['boto_profile'] = None
    dummy_credentials['aws_secret_key'] = "notasecret"
    dummy_credentials['aws_access_key'] = "notakey"
    dummy_credentials['aws_security_token'] = None
    dummy_credentials['region'] = 'eu-west-1'
    return dummy_credentials


simple_stack_with_outputs_response = {
    'Stacks':
        [
            {
                'StackId': 'arn:aws:cloudformation:eu-west-1:111111111111:stack'
                           '/stack_with_outputs/11111111-aaaa-xxxx-1111-222222222222',
                'StackName': 'stack_with_outputs',
                'Parameters': [
                    {'ParameterKey': 'TestParameter', 'ParameterValue': 'True'},
                ],
                'RollbackConfiguration': {},
                'StackStatus': 'UPDATE_COMPLETE',
                'DisableRollback': True,
                'NotificationARNs': [],
                'Capabilities': ['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM'],
                'EnableTerminationProtection': True,
                'Outputs':
                    [
                        {
                            'OutputKey': 'test_output',
                            'OutputValue': 'test_output_value',
                            'Description': 'Test output',
                            'ExportName': 'test_output'
                        }
                    ],
                'DriftInformation': {'StackDriftStatus': 'NOT_CHECKED'}
            }
        ],
    'ResponseMetadata':
        {
            'RequestId': '1111xxxd-2222-4444-aaaa-42555555',
            'HTTPStatusCode': 200,
            'HTTPHeaders':
                {
                    'x-amzn-requestid': 'xxxxxx-aaaa-xxxx-xxxx-xxxxxxx',
                    'content-type': 'text/xml',
                    'vary': 'accept-encoding',
                    'date': 'Sat, 31 Jan 2021 08:03:39 GMT'
                },
            'RetryAttempts': 0
        }
}

simple_stack_without_outputs_response = {
    'Stacks':
        [
            {
                'StackId': 'arn:aws:cloudformation:eu-west-1:111111111111:stack'
                           '/stack_without_outputs/11111111-aaaa-xxxx-1111-222222222222',
                'StackName': 'stack_without_outputs',
                'Parameters':
                    [
                        {'ParameterKey': 'TestParameter', 'ParameterValue': 'True'},
                    ],
                'RollbackConfiguration': {},
                'StackStatus': 'UPDATE_COMPLETE',
                'DisableRollback': True,
                'NotificationARNs': [],
                'Capabilities': ['CAPABILITY_IAM', 'CAPABILITY_NAMED_IAM'], 'EnableTerminationProtection': True,
                'DriftInformation': {'StackDriftStatus': 'NOT_CHECKED'}}
        ],
    'ResponseMetadata':
        {
            'RequestId': '11111-2222-4555-abbb-488888888',
            'HTTPStatusCode': 200,
            'HTTPHeaders':
                {
                    'x-amzn-requestid': 'xxxxxx-aaaa-xxxx-xxxx-xxxxxxx',
                    'content-type': 'text/xml',
                    'vary': 'accept-encoding',
                    'date': 'Sat, 31 Jan 2021 08:03:39 GMT'
                },
            'RetryAttempts': 0
        }
}


def test_lookup_stack_without_output(mocker, dummy_credentials):
    lookup = lookup_loader.get('community.aws.aws_cloudformation')
    boto3_double = mocker.MagicMock()
    boto3_double.Session.return_value.client.return_value.describe_stacks.return_value = copy(
        simple_stack_without_outputs_response)

    mocker.patch.object(boto3, 'session', boto3_double)
    with pytest.raises(AnsibleError, match="Provided Cloudformation stack doesn't contain any outputs."):
        retval = lookup.run(["stack_without_outputs"], output_key='test', **dummy_credentials)


def test_lookup_stack_with_output(mocker, dummy_credentials):
    lookup = lookup_loader.get('community.aws.aws_cloudformation')
    boto3_double = mocker.MagicMock()
    boto3_double.Session.return_value.client.return_value.describe_stacks.return_value = copy(
        simple_stack_with_outputs_response)
    mocker.patch.object(boto3, 'session', boto3_double)
    retval = lookup.run(["stack_without_outputs"], output_key='test_output', **dummy_credentials)
    assert (retval == 'test_output_value')


def test_lookup_stack_with_not_existing_output(mocker, dummy_credentials):
    lookup = lookup_loader.get('community.aws.aws_cloudformation')
    boto3_double = mocker.MagicMock()
    boto3_double.Session.return_value.client.return_value.describe_stacks.return_value = copy(
        simple_stack_with_outputs_response)
    mocker.patch.object(boto3, 'session', boto3_double)
    with pytest.raises(AnsibleError,
                       match="Provided Cloudformation stack doesn't contain output with key: test_not_existing_output."):
        retval = lookup.run(["stack_with_outputs"], output_key='test_not_existing_output', **dummy_credentials)


def test_lookup_not_existing_stack_output(mocker, dummy_credentials):
    lookup = lookup_loader.get('community.aws.aws_cloudformation')
    boto3_double = mocker.MagicMock()
    error_response_denied = {'Error': {'Code': 'ValidationError',
                                       'Message': 'Stack with id not_existing_stack does not exist'}}
    operation_name = 'DescribeStacks'
    boto3_double.Session.return_value.client.return_value.describe_stacks.side_effect = \
        ClientError(error_response_denied, operation_name)

    mocker.patch.object(boto3, 'session', boto3_double)
    with pytest.raises(AnsibleError, match="Given stack doesn't exist: not_existing_stack"):
        retval = lookup.run(["not_existing_stack"], output_key='test', **dummy_credentials)
