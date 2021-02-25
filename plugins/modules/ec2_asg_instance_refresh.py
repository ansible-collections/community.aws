#!/usr/bin/python
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: ec2_asg_instance_refresh
version_added: 1.0.0
short_description: Start or cancel an ec2 Auto Scaling Group (ASG) Instance Refresh in AWS
description:
  - Start or cancel an ec2 Auto Scaling Group Instance Refresh in AWS
  - Can be used with ec2_asg_instance_refreshes_info to track the subsequent progress
requirements: [ boto3 ]
author: "Dan Khersonsky (@danquixote)"
options:
  state:
    description:
      - Desired state of the ASG
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
      - A rolling update is an update that is applied to all instances in an Auto Scaling group until all instances have been updated.
      - A rolling update can fail due to failed health checks or if instances are on standby or are protected from scale in.
      - If the rolling update process fails, any instances that were already replaced are not rolled back to their previous configuration.
    type: str
    default: 'Rolling'
  preferences:
    description:
      - Set of preferences associated with the instance refresh request.
      - If not provided, the default values are used. For MinHealthyPercentage, the default value is 90.
      - For InstanceWarmup, the default is to use the value specified for the health check grace period for the Auto Scaling group.
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
          - The number of seconds until a newly launched instance is configured and ready to use.
          - During this time, Amazon EC2 Auto Scaling does not immediately move on to the next replacement.
          - The default is to use the value for the health check grace period defined for the group.
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
from ansible_collections.amazon.aws.plugins.module_utils.core import scrub_none_parameters
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import camel_dict_to_snake_dict
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AWSRetry
from ansible.module_utils.common.dict_transformations import snake_dict_to_camel_dict


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
        _prefs = scrub_none_parameters(preferences)
        args['Preferences'] = snake_dict_to_camel_dict(_prefs, capitalize_first=True)
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
