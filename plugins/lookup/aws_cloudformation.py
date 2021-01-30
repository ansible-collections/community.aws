# Copyright: (c) 2021, Ethem Cem Özkan <ethemcem.ozkan@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
lookup: aws_cloudformation
author:
  - Ethem Cem Özkan <ethemcem.ozkan@gmail.com>
requirements:
  - boto3
  - botocore>=1.10.0

short_description: Look up Cloudformation stack outputs
description:
  - Look up AWS Cloudformation outputs provided the caller
    has the appropriate permissions to read the output and stack is created.
  - Lookup is based on the stack name and output key
options:
  _terms:
    description: Name of the stack to lookup in AWS Cloudformation.
    required: True
  output_key:
    description: Key of the output that is in provided stack.
    default: None
    type: String
'''

EXAMPLES = r"""
 - name: lookup cloudformation output in the current region
   debug: msg="{{ lookup('community.aws.aws_cloudformation', 'stack_name', output_key='output_key' ) }}"

"""

RETURN = r"""
_raw:
  description:
    Returns the value of the output that is in Cloudformation stack.
"""

from ansible.errors import AnsibleError

try:
    import boto3
    import botocore
except ImportError:
    raise AnsibleError("The lookup aws_cloudformation requires boto3 and botocore.")

from ansible.plugins.lookup import LookupBase
from ansible.module_utils._text import to_native
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import HAS_BOTO3


def _boto3_conn(region, credentials):
    boto_profile = credentials.pop('aws_profile', None)

    try:
        connection = boto3.session.Session(profile_name=boto_profile).client('cloudformation', region, **credentials)
    except (botocore.exceptions.ProfileNotFound, botocore.exceptions.PartialCredentialsError) as e:
        if boto_profile:
            try:
                connection = boto3.session.Session(profile_name=boto_profile).client('cloudformation', region)
            except (botocore.exceptions.ProfileNotFound, botocore.exceptions.PartialCredentialsError) as e:
                raise AnsibleError("Insufficient credentials found.")
        else:
            raise AnsibleError("Insufficient credentials found.")
    return connection


def stack_output(stack, output_key):

    if 'Outputs' in stack and len(stack['Outputs']) > 0:
        outputs = stack['Outputs']
        stack_output = next(iter(filter(lambda output: output['OutputKey'] == output_key, outputs)), None)
        if stack_output is not None and 'OutputValue' in stack_output:
            return stack_output['OutputValue']
        else:
            raise AnsibleError("Provided Cloudformation stack doesn't contain output with key: {0}.".format(output_key))
    else:
        raise AnsibleError("Provided Cloudformation stack doesn't contain any outputs.")


class LookupModule(LookupBase):
    def run(self, terms, boto_profile=None, aws_profile=None,
            output_key=None, aws_access_key=None, aws_security_token=None, aws_secret_key=None, region=None):
        '''
                   :arg terms: a stack name to search outputs in.
                       e.g. ['parameter_name', 'parameter_name_too' ]
                   :kwarg aws_secret_key: identity of the AWS key to use
                   :kwarg aws_access_key: AWS secret key (matching identity)
                   :kwarg aws_security_token: AWS session key if using STS
                   :kwarg output_key: Output key from the provided stack
                   :kwarg region: AWS region in which to do the lookup
                   :returns: Output value from the Cloudformation stack.
               '''
        if not HAS_BOTO3:
            raise AnsibleError('botocore and boto3 are required for aws_cloudformation lookup.')

        if len(terms) < 1:
            raise AnsibleError("Provide Cloudformation stack name. Example: "
                               "lookup('community.aws.aws_cloudformation', 'stack_name', output_key='output_key' )")

        credentials = {}
        if aws_profile:
            credentials['aws_profile'] = aws_profile
        else:
            credentials['aws_profile'] = boto_profile
        credentials['aws_secret_access_key'] = aws_secret_key
        credentials['aws_access_key_id'] = aws_access_key
        credentials['aws_session_token'] = aws_security_token

        # fallback to IAM role credentials
        if not credentials['aws_profile'] and not (
                credentials['aws_access_key_id'] and credentials['aws_secret_access_key']):
            session = botocore.session.get_session()
            if session.get_credentials() is not None:
                credentials['aws_access_key_id'] = session.get_credentials().access_key
                credentials['aws_secret_access_key'] = session.get_credentials().secret_key
                credentials['aws_session_token'] = session.get_credentials().token

        client = _boto3_conn(region, credentials)
        stack = {}
        stack_name = terms[0]
        try:
            response = client.describe_stacks(
                StackName=stack_name
            )

            if 'Stacks' in response:
                stack = response['Stacks'][0]

        except (botocore.exceptions.ClientError,
                botocore.exceptions.BotoCoreError) as e:
            if 'Stack with id {} does not exist'.format(stack_name) in str(e):
                raise AnsibleError("Given stack doesn't exist: {0}".format(stack_name))
            else:
                raise AnsibleError("Failed to retrieve cloudformation stack: %s" % to_native(e))

        output_value = stack_output(stack=stack,
                                    output_key=output_key)
        return output_value
