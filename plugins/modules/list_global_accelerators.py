#!/usr/bin/python
#
# This is a free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This Ansible library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this library.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = '''
---
module: list_global_accelerators
short_description: Gather information about AWS Global Accelerators
description:
    - Gather information about Global Accelerators in AWS
    - Currently this module can not get information about a specific load balancer
author:
  - "Tyler Lubeck (@TylerLubeck)"
extends_documentation_fragment:
- amazon.aws.aws
- amazon.aws.ec2

requirements:
  - botocore
  - boto3
'''

EXAMPLES = '''
# Note: These examples do not set authentication details, see the AWS Guide for details.

# Gather information about all Accelerators
- list_global_accelerators:
  register: accelerator_info

- debug:
    msg: "{{ item.dns_name }}"
  loop: "{{ accelerator_info.accelerators }}"
'''

RETURN = '''
accelerators:
  description: a list of global accelerators
  returned: always
  type: list
  sample:
    accelerators:
      - attributes:
          accelerator_attributes:
            flow_logs_enabled: false
        created_time: 2020-04-24T04:54:02-00:00
        dns_name: abc123.awsglobalaccelerator.com
        enabled: true
        ip_address_type: IPV4
        ip_sets:
          - ip_addresses:
              - 1.1.1.1
              - 2.2.2.2
            ip_family: IPv4
        last_modified_time: 2020-04-24T04:54:02-00:00
        name: myaccelerator
        status: DEPLOYED
        tags: {}
'''

from ansible_collections.amazon.aws.plugins.module_utils.aws.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import (
    AWSRetry,
    camel_dict_to_snake_dict,
    boto3_tag_list_to_ansible_dict
)

try:
    import botocore
except ImportError:
    pass  # caught by AnsibleAWSModule


@AWSRetry.backoff(tries=5, delay=5, backoff=2.0)
def list_accelerators(connection):
    paginator = connection.get_paginator('list_accelerators')
    accelerators = paginator.paginate().build_full_result().get('Accelerators')
    results = []

    for accelerator in accelerators:
        description = camel_dict_to_snake_dict(accelerator)
        arn = accelerator['AcceleratorArn']
        description['tags'] = get_tags(connection, arn)
        description['attributes'] = get_accelerator_attributes(connection, arn)

        results.append(description)

    return results


def get_accelerator_attributes(connection, accelerator_arn):
    attributes = connection.describe_accelerator_attributes(AcceleratorArn=accelerator_arn)
    return camel_dict_to_snake_dict(attributes)

def get_tags(connection, accelerator_arn):
    tags = connection.list_tags_for_resource(ResourceArn=accelerator_arn)
    if not tags:
        return {}
    return boto3_tag_list_to_ansible_dict(tags['Tags'])


def main():
    argument_spec = {}
    module = AnsibleAWSModule(argument_spec=argument_spec,
                              supports_check_mode=True)

    connection = module.client('globalaccelerator')

    try:
        accelerators = list_accelerators(connection)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Failed to get load balancer information.")

    module.exit_json(accelerators=accelerators)


if __name__ == '__main__':
    main()
