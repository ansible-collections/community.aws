#!/usr/bin/python
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = '''
---
module: aws_asg_complete_lifecycle_action
short_description: Completes the lifecycle action of an instance
description:
  - Used to complete the lifecycle action for the specified instance with the specified result
version_added: "1.0.0"
requirements: [ boto3 ]
author:
    - Saleh Abbas (@salehabbas) <saleh.abbas@thetradedesk.com>
options:
  asg_name:
    description:
      - The name of the Auto Scaling group which the instance belongs to.
    type: str
    required: true
  lifecycle_hook_name:
    description:
      - The name of the lifecycle hook to complete.
    type: str
    required: true
  lifecycle_action_result:
    description:
      - The action for the lifecycle hook to take. It can be either CONTINUE or ABANDON.
    type: str
    required: true
  instance_id:
    description:
      - The ID of the instance.
    type: str
    required: true
extends_documentation_fragment:
    - amazon.aws.aws
    - amazon.aws.ec2
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
    import botocore
except ImportError:
    pass  # caught by AnsibleAWSModule

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import get_aws_connection_info, boto3_conn, HAS_BOTO3

def main():
    argument_spec = dict(
        asg_name=dict(required=True, type='str'),
        lifecycle_hook_name=dict(required=True, type='str'),
        lifecycle_action_result=dict(required=True, type='str'),
        instance_id=dict(required=True, type='str')
    )

    module = AnsibleAWSModule(argument_spec=argument_spec)
    if not HAS_BOTO3:
        module.fail_json(msg='boto3 required for this module')

    asg_name = module.params.get('asg_name')
    lifecycle_hook_name = module.params.get('lifecycle_hook_name')
    lifecycle_action_result = module.params.get('lifecycle_action_result')
    instance_id = module.params.get('instance_id')

    try:
        region, ec2_url, aws_connect_kwargs = get_aws_connection_info(module, boto3=True)
        autoscaling = boto3_conn(module, conn_type='client', resource='autoscaling', region=region, endpoint=ec2_url, **aws_connect_kwargs)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Failed to completes the lifecycle action")

    results = autoscaling.complete_lifecycle_action(
        LifecycleHookName=lifecycle_hook_name,
        AutoScalingGroupName=asg_name,
        LifecycleActionResult=lifecycle_action_result,
        InstanceId=instance_id
    )

    module.exit_json(results=results)


if __name__ == '__main__':
    main()
