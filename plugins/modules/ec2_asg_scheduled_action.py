#!/usr/bin/python

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

# Based off of https://github.com/mmochan/ansible-aws-ec2-asg-scheduled-actions/blob/master/library/ec2_asg_scheduled_action.py
# (c) 2016, Mike Mochan <@mmochan>

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
module: ec2_asg_scheduled_actions
short_description: Create, modify and delete AutoScaling Scheduled Actions.
description:
  - Read the AWS documentation for Scheduled Actions
    U(http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-as-scheduledaction.html
options:
  autoscaling_group_name:
    description:
      - The name of the autoscaling group to add a scheduled action to.
    required: true
  scheduled_action_name:
    description:
      - The name of the scheduled action.
    type: str
    required: true
  start_time:
    description:
      - Start time for the action.
    type: str
  end_time:
    description:
      - End time for the action.
    type: str
  time_zone:
    description:
      - Time zone to run against.
    type: str
  recurrence:
    description:
      - Cron style schedule.
    type: str
    required: true
  min_size:
    description:
      - ASG min capacity.
    type: int
  max_size:
    description:
      - ASG max capacity.
    type: int
  desired_capacity:
    description:
      - ASG desired capacity.
    type: int
  state:
    description:
      - Create / update or delete scheduled action.
    required: false
    default: present
    choices: ['present', 'absent']
author: Mark Woolley(@marknet15)
extends_documentation_fragment:
- amazon.aws.aws
- amazon.aws.ec2
'''

EXAMPLES = r'''
# Create a scheduled action for a autoscaling group.
- name: Create a minimal scheduled action for autoscaling group
  community.aws.ec2_asg_scheduled_action:
    autoscaling_group_name: test_asg
    scheduled_action_name: test_scheduled_action
    start_time: 2021 October 25 08:00 UTC
    recurrence: 40 22 * * 1-5
    desired_capacity: 10
    state: present
  register: scheduled_action

- name: Create a scheduled action for autoscaling group
  community.aws.ec2_asg_scheduled_action:
    autoscaling_group_name: test_asg
    scheduled_action_name: test_scheduled_action
    start_time: 2021 October 25 08:00 UTC
    end_time: 2021 October 25 08:00 UTC
    time_zone: Europe/London
    recurrence: 40 22 * * 1-5
    min_size: 10
    max_size: 15
    desired_capacity: 10
    state: present
  register: scheduled_action

- name: Delete scheduled action
  community.aws.ec2_asg_scheduled_action:
    autoscaling_group_name: test_asg
    scheduled_action_name: test_scheduled_action
    state: absent
'''
RETURN = r'''
task:
  description: The result of the present, and absent actions.
  returned: success
  type: dictionary
'''

try:
    import botocore
except ImportError:
    pass  # caught by AnsibleAWSModule

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AWSRetry


def format_request():
    params = dict(
        AutoScalingGroupName=module.params.get('autoscaling_group_name'),
        ScheduledActionName=module.params.get('scheduled_action_name'),
        Recurrence=module.params.get('recurrence')
    )

    # Some of these params are optional
    if module.params.get('desired_capacity') is not None:
        params['DesiredCapacity'] = module.params.get('desired_capacity')

    if module.params.get('min_size') is not None:
        params['MinSize'] = module.params.get('min_size')

    if module.params.get('max_size') is not None:
        params['MaxSize'] = module.params.get('max_size')

    if module.params.get('time_zone') is not None:
        params['TimeZone'] = module.params.get('time_zone')

    if module.params.get('start_time') is not None:
        params['StartTime'] = module.params.get('start_time')

    if module.params.get('end_time') is not None:
        params['EndTime'] = module.params.get('end_time')

    return params


def delete_scheduled_action(current_actions):
    changed = False

    if current_actions == []:
        return changed

    if module.check_mode:
        return True

    params = dict(
        AutoScalingGroupName=module.params.get('autoscaling_group_name'),
        ScheduledActionName=module.params.get('scheduled_action_name')
    )

    try:
        client.delete_scheduled_action(aws_retry=True, **params)
    except botocore.exceptions.ClientError as e:
        module.fail_json(msg=str(e))

    return changed


def get_scheduled_actions():
    try:
        actions = client.describe_scheduled_actions(aws_retry=True,
            AutoScalingGroupName=module.params.get('autoscaling_group_name'),
            ScheduledActionNames=[module.params.get('scheduled_action_name')]
        )
    except botocore.exceptions.ClientError as e:
        module.fail_json_aws(e)

    current_actions = actions.get("ScheduledUpdateGroupActions")

    return current_actions


def put_scheduled_update_group_action(current_actions):
    changed = False
    params = format_request()

    if len(current_actions) < 1:
        changed = True
    elif current_actions != params:
        changed = True

    if module.check_mode:
        return changed

    try:
        client.put_scheduled_update_group_action(aws_retry=True, **params)
    except botocore.exceptions.ClientError as e:
        module.fail_json_aws(e)

    return changed


def main():
    global module
    global client

    argument_spec = dict(
        autoscaling_group_name=dict(required=True, type='str'),
        scheduled_action_name=dict(required=True, type='str'),
        start_time=dict(default=None, type='str'),
        end_time=dict(default=None, type='str'),
        time_zone=dict(default=None, type='str'),
        recurrence=dict(required=True, type='str'),
        min_size=dict(default=None, type='int'),
        max_size=dict(default=None, type='int'),
        desired_capacity=dict(default=None, type='int'),
        state=dict(default='present', choices=['present', 'absent'])
    )

    module = AnsibleAWSModule(argument_spec=argument_spec, supports_check_mode=True)
    client = module.client('autoscaling', retry_decorator=AWSRetry.jittered_backoff())
    current_actions = get_scheduled_actions()
    state = module.params.get('state')
    results = dict()

    if state == 'present':
        changed = put_scheduled_update_group_action(current_actions)
        updated_action = get_scheduled_actions()[0]
        results = dict(
            scheduled_action_name=updated_action.get('ScheduledActionName'),
            start_time=updated_action.get('StartTime'),
            end_time=updated_action.get('EndTime'),
            time_zone=updated_action.get('TimeZone'),
            recurrence=updated_action.get('Recurrence'),
            min_size=updated_action.get('MinSize'),
            max_size=updated_action.get('MaxSize'),
            desired_capacity=updated_action.get('DesiredCapacity')
        )
    else:
        changed = delete_scheduled_action(current_actions)

    results['changed'] = changed
    module.exit_json(**results)


if __name__ == '__main__':
    main()
