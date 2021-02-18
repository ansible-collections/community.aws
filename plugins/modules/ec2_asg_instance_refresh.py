#!/usr/bin/python
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: ec2_asg_instance_refresh
version_added: 1.0.0
short_description: Start or cancel an  ec2 Auto Scaling Group Instance Refresh in AWS
description:
  - Start or cancel an ec2 Auto Scaling Group Instance Refresh in AWS
  - Can be used with ec2_asg_instance_refreshes_info to track the subsequent progress
requirements: [ boto3 ]
author: "Dan Khersonsky (@danquixote)"
options:
  state:
    description:
      - Desired state
    type: str
    required: true
    choices: [ 'started', 'canceled' ]
  name:
    description:
      - The name of the auto scaling group you are searching for.
    type: str
    required: true
  strategy:
    description:
      - The strategy to use for the instance refresh. The only valid value is Rolling.
    type: str
    default: 'Rolling'
  preferences:
    description:
      - preferences
    required: false
    suboptions:
      min_healthy_percentage:
        description:
          - The amount of capacity in the Auto Scaling group that must remain healthy during an instance refresh to allow the operation to continue,
          - as a percentage of the desired capacity of the Auto Scaling group (rounded up to the nearest integer).
          - The default is 90.
        type: int
      instance_warmup:
        description:
          - instance_warmup
        type: int
    type: dict
extends_documentation_fragment:
- amazon.aws.aws
- amazon.aws.ec2

'''

EXAMPLES = '''
# Note: These examples do not set authentication details, see the AWS Guide for details.

- name: Start a refresh
  community.aws.ec2_asg_instance_refresh:
    name: some-asg
    state: started

- name: Cancel a refresh
  community.aws.ec2_asg_instance_refresh:
    name: some-asg
    state: canceled

- name: Start a refresh and pass preferences
  community.aws.ec2_asg_instance_refresh:
    name: some-asg
    state: started
    preferences:
      min_healthy_percentage: 91
      instance_warmup: 60

'''

RETURN = '''
---
instance_refresh_id:
    description: instance refresh id
    returned: success
    type: str
    sample: "08b91cf7-8fa6-48af-b6a6-d227f40f1b9b"
'''

try:
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:
    pass  # caught by AnsibleAWSModule

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import camel_dict_to_snake_dict
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AWSRetry


def start_or_cancel_instance_refresh(conn, module):
    """
    Args:
        conn (boto3.AutoScaling.Client): Valid Boto3 ASG client.
        name (str): Mandatory name of the ASG you are looking for.
        state (str): Start or Cancel a refresh

    Returns:
        Dict
        {
            'instance_refresh_id': 'string'
        }
    """

    asg_state = module.params.get('state')
    asg_name = module.params.get('name')
    preferences = module.params.get('preferences')

    args = {}
    args['AutoScalingGroupName'] = asg_name
    if asg_state == 'started':
        args['Strategy'] = 'Rolling'
    if preferences:
        if asg_state == 'canceled':
            module.fail_json(msg='can not pass preferences dict when canceling a refresh')
        args['Preferences'] = {}
        if preferences.get('min_healthy_percentage'):
            args['Preferences']['MinHealthyPercentage'] = preferences['min_healthy_percentage']
        if preferences.get('instance_warmup'):
            args['Preferences']['InstanceWarmup'] = preferences['instance_warmup']
    cmd_invocations = {
        'canceled': conn.cancel_instance_refresh,
        'started': conn.start_instance_refresh,
    }
    try:
        result = cmd_invocations[asg_state](aws_retry=True, **args)
        result = dict(
            instance_refresh_id=result['InstanceRefreshId']
        )
        return module.exit_json(**result)
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(
            e,
            msg='Failed to {0} InstanceRefresh'.format(
                asg_state.replace('ed', '')
            )
        )


def main():

    argument_spec = dict(
        state=dict(
            type='str',
            required=True,
            choices=['started', 'canceled'],
        ),
        name=dict(required=True),
        strategy=dict(
            type='str',
            default='Rolling',
            required=False
        ),
        preferences=dict(
            type='dict',
            required=False,
            options=dict(
                min_healthy_percentage=dict(type='int'),
                instance_warmup=dict(type='int'),
            )
        ),
    )

    module = AnsibleAWSModule(argument_spec=argument_spec)
    autoscaling = module.client(
        'autoscaling',
        retry_decorator=AWSRetry.jittered_backoff(
            retries=10,
            catch_extra_error_codes=['InstanceRefreshInProgress']
        )
    )
    results = start_or_cancel_instance_refresh(
        autoscaling,
        module,
    )
    return results


if __name__ == '__main__':
    main()
