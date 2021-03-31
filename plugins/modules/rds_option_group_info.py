#!/usr/bin/python
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: rds_option_group_info
version_added: 1.5.0
short_description: Gather information about ...
description:
    - Gather information about ....
requirements: [ boto3 ]
author: "Alina Buzachis (@alinabuzachis)"
options:
  filters:
    description:
      - A dict of filters to apply. Each dict item consists of a filter key and a filter value.
        See U(https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds.html#RDS.Client.describe_option_groups) for possible filters.
    type: dict
....

extends_documentation_fragment:
- amazon.aws.aws
- amazon.aws.ec2

'''

EXAMPLES = r'''
# Note: These examples do not set authentication details, see the AWS Guide for details.

- name: List all the option groups
  community.aws.rds_option_group_info:
    region: ap-southeast-2
    profile: production
    option_group_name: test-mysql-option-group
  register: option_group

'''

RETURN = r'''

'''

try:
    import botocore
except ImportError:
    pass  # Handled by AnsibleAWSModule

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.core import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AWSRetry
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import boto3_tag_list_to_ansible_dict
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import ansible_dict_to_boto3_filter_list
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import camel_dict_to_snake_dict


def list_option_groups(client, module):
    params = dict()
    params['OptionGroupName'] = module.params.get('option_group_name')
    params['Filters'] = ansible_dict_to_boto3_filter_list(module.params.get('filters'))

    try:
        result = client.describe_option_groups(aws_retry=True, **params)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e)

    return result


def main():
    argument_spec = dict(
        option_group_name=dict(default='', type='str'),
        filters=dict(type='dict', default=dict()),
    )

    module = AnsibleAWSModule(argument_spec=argument_spec, supports_check_mode=True)

    # Validate Requirements
    try:
        connection = module.client('rds', retry_decorator=AWSRetry.jittered_backoff())
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg='Failed to connect to AWS')

    results = list_option_groups(connection, module)

    module.exit_json(**camel_dict_to_snake_dict(results))


if __name__ == '__main__':
    main()
