#!/usr/bin/python
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}


DOCUMENTATION = '''
---
module: aws_asg_complete_lifecycle_action
short_description: Completes the lifecycle action of an instance
description:
  - Used to complete the lifecycle action for the specified instance with the specified result
version_added: "2.2"
requirements: [ boto3 ]
author:
    - Saleh Abbas (@salehabbas) <saleh.abbas@thetradedesk.com>
options:
  asg_name:
    description:
      - The name of the Auto Scaling group which the instance belongs to.
    required: true
  lifecycle_hook_name:
    description:
      - The name of the lifecycle hook to complete.
    required: true
  lifecycle_action_result:
    description:
      - The action for the lifecycle hook to take. It can be either CONTINUE or ABANDON.
    required: true
  instance_id:
    description:
      - The ID of the instance.
    required: true

extends_documentation_fragment:
    - aws
    - ec2
'''

EXAMPLES = '''
# Note: These examples do not set authentication details, see the AWS Guide for details.

# Complete the lifecycle action
- aws_asg_complete_lifecycle_action:
    asg_name: my-auto-scaling-group
    lifecycle_hook_name: my-lifecycle-hook
    lifecycle_action_result: CONTINUE
    instance_id: i-123knm1l2312
'''

RETURN = '''
---
status:
    description: How things went
    returned: success
    type: str
    sample: ["OK"]
'''

import re

try:
    from botocore.exceptions import ClientError
except ImportError:
    pass  # caught by imported HAS_BOTO3

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.ec2 import (get_aws_connection_info, boto3_conn, ec2_argument_spec,
                                      camel_dict_to_snake_dict, HAS_BOTO3)

def main():

    argument_spec = ec2_argument_spec()
    argument_spec.update(
        dict(
            asg_name=dict(type='str'),
            lifecycle_hook_name=dict(type='str'),
            lifecycle_action_result=dict(type='str'),
            instance_id=dict(type='str')
        )
    )
    module = AnsibleModule(argument_spec=argument_spec)
    if not HAS_BOTO3:
        module.fail_json(msg='boto3 required for this module')

    asg_name = module.params.get('asg_name')
    lifecycle_hook_name = module.params.get('lifecycle_hook_name')
    lifecycle_action_result = module.params.get('lifecycle_action_result')
    instance_id = module.params.get('instance_id')

    try:
        region, ec2_url, aws_connect_kwargs = get_aws_connection_info(module, boto3=True)
        autoscaling = boto3_conn(module, conn_type='client', resource='autoscaling', region=region, endpoint=ec2_url, **aws_connect_kwargs)
    except ClientError as e:
        module.fail_json(msg=e.message, **camel_dict_to_snake_dict(e.response))

    results = autoscaling.complete_lifecycle_action(
        LifecycleHookName=lifecycle_hook_name,
        AutoScalingGroupName=asg_name,
        LifecycleActionResult=lifecycle_action_result,
        InstanceId=instance_id
    )

    module.exit_json(results=results)


if __name__ == '__main__':
    main()
