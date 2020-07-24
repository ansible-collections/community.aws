#!/usr/bin/python
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
module: ec2_scaling_policy
short_description: Create or delete AWS scaling policies for Autoscaling groups
version_added: 1.0.0
description:
  - Can create or delete scaling policies for autoscaling groups.
  - Referenced autoscaling groups must already exist.
author: "Zacharie Eakin (@Zeekin)"
requirements: [ "boto3", "botocore" ]
options:
  state:
    description:
      - Register or deregister the policy.
    default: present
    choices: ['present', 'absent']
    type: str
  name:
    description:
      - Unique name for the scaling policy.
    required: true
    type: str
  asg_name:
    description:
      - Name of the associated autoscaling group.
    required: true
    type: str
  adjustment_type:
    description:
      - The type of change in capacity of the autoscaling group.
    choices: ['ChangeInCapacity','ExactCapacity','PercentChangeInCapacity']
    type: str
  scaling_adjustment:
    description:
      - The amount by which the autoscaling group is adjusted by the policy.
    type: int
  min_adjustment_step:
    description:
      - Minimum amount of adjustment when policy is triggered. Only used with adjustment_type of PercentChangeInCapacity.
    type: int
  cooldown:
    description:
      - The minimum period of time (in seconds) between which autoscaling actions can take place.
    type: int
extends_documentation_fragment:
- amazon.aws.aws
- amazon.aws.ec2

'''

EXAMPLES = '''
# Scale out by 4
- community.aws.ec2_scaling_policy:
    state: present
    region: US-XXX
    name: "scaleout-policy"
    asg_name: "slave-pool"
    adjustment_type: "ChangeInCapacity"
    scaling_adjustment: 4
    cooldown: 300

# Scale in by 4
- community.aws.ec2_scaling_policy:
    state: present
    region: US-XXX
    name: "scalein-policy"
    asg_name: "slave-pool"
    adjustment_type: "ChangeInCapacity"
    scaling_adjustment: -4
    cooldown: 300
'''

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import snake_dict_to_camel_dict

try:
    from botocore.exceptions import ClientError
except ImportError:
    pass  # protected by AnsibleAWSModule


def create_scaling_policy(connection, module):
    sp_name = module.params.get('name')
    adjustment_type = module.params.get('adjustment_type')
    asg_name = module.params.get('asg_name')
    scaling_adjustment = module.params.get('scaling_adjustment')
    min_adjustment_step = module.params.get('min_adjustment_step')
    cooldown = module.params.get('cooldown')

    scaling_policies = connection.describe_policies(AutoScalingGroupName=asg_name, PolicyNames=[sp_name])

    if not scaling_policies['ScalingPolicies']:
        if adjustment_type != 'PercentChangeInCapacity':
            try:
                connection.put_scaling_policy(
                    PolicyName=sp_name,
                    AdjustmentType=adjustment_type,
                    AutoScalingGroupName=asg_name,
                    ScalingAdjustment=scaling_adjustment,
                    Cooldown=cooldown)
                policy = connection.describe_policies(AutoScalingGroupName=asg_name,
                                                      PolicyNames=[sp_name])['ScalingPolicies'][0]
                module.exit_json(changed=True, name=policy['PolicyName'], arn=policy['PolicyARN'],
                                 as_name=policy['AutoScalingGroupName'], scaling_adjustment=policy['ScalingAdjustment'],
                                 cooldown=policy['Cooldown'], adjustment_type=policy['AdjustmentType'])
            except ClientError as e:
                module.fail_json_aws(e, "Failed to create scaling policy.")

        else:
            try:
                connection.put_scaling_policy(
                    PolicyName=sp_name,
                    AdjustmentType=adjustment_type,
                    AutoScalingGroupName=asg_name,
                    ScalingAdjustment=scaling_adjustment,
                    MinAdjustmentStep=min_adjustment_step,
                    Cooldown=cooldown)
                policy = connection.describe_policies(AutoScalingGroupName=asg_name,
                                                      PolicyNames=[sp_name])['ScalingPolicies'][0]
                module.exit_json(changed=True, name=policy['PolicyName'], arn=policy['PolicyARN'],
                                 as_name=policy['AutoScalingGroupName'], scaling_adjustment=policy['ScalingAdjustment'],
                                 cooldown=policy['Cooldown'], adjustment_type=policy['AdjustmentType'],
                                 min_adjustment_step=policy['MinAdjustmentStep'])
            except ClientError as e:
                module.fail_json_aws(e, "Failed to create scaling policy.")

    else:
        policy = scaling_policies['ScalingPolicies'][0]
        changed = False

        # min_adjustment_step attribute is only relevant if the adjustment_type
        # is set to percentage change in capacity, so it is a special case
        if policy.get('AdjustmentType') == 'PercentChangeInCapacity':
            if policy.get('MinAdjustmentStep') != min_adjustment_step:
                changed = True

            # set the min adjustment step in case the user decided to change their
            # adjustment type to percentage
            policy['MinAdjustmentStep'] = min_adjustment_step

        # check the remaining attributes
        for attr in ('AdjustmentType', 'ScalingAdjustment', 'Cooldown'):
            camel_options = snake_dict_to_camel_dict(module.params, capitalize_first=True)
            if policy.get(attr) != camel_options.get(attr):
                changed = True
                policy[attr] = camel_options.get(attr)

        try:
            if changed:
                connection.put_scaling_policy(policy)
                policy = connection.describe_policies(AutoScalingGroupName=asg_name,
                                                      PolicyNames=[sp_name])['ScalingPolicies'][0]
            module.exit_json(changed=changed, name=policy['PolicyName'], arn=policy['PolicyARN'],
                             as_name=policy['AutoScalingGroupName'], scaling_adjustment=policy['ScalingAdjustment'],
                             cooldown=policy['Cooldown'], adjustment_type=policy['AdjustmentType'],
                             min_adjustment_step=policy['MinAdjustmentStep'])
        except ClientError as e:
            module.fail_json_aws(e, "Failed to modify scaling policy.")


def delete_scaling_policy(connection, module):
    sp_name = module.params.get('name')
    asg_name = module.params.get('asg_name')

    scaling_policies = connection.describe_policies(AutoScalingGroupName=asg_name, PolicyNames=[sp_name])

    if scaling_policies['ScalingPolicies']:
        try:
            connection.delete_policy(PolicyName=sp_name, AutoScalingGroupName=asg_name)
            module.exit_json(changed=True)
        except ClientError as e:
            module.fail_json_aws(e, "Failed to destroy scaling policy.")
    else:
        module.exit_json(changed=False)


def main():
    argument_spec = dict(
        name=dict(required=True, type='str'),
        adjustment_type=dict(type='str', choices=['ChangeInCapacity', 'ExactCapacity', 'PercentChangeInCapacity']),
        asg_name=dict(required=True, type='str'),
        scaling_adjustment=dict(type='int'),
        min_adjustment_step=dict(type='int'),
        cooldown=dict(type='int'),
        state=dict(default='present', choices=['present', 'absent']),
    )

    module = AnsibleAWSModule(argument_spec=argument_spec)

    state = module.params.get('state')

    connection = module.client('autoscaling')

    if state == 'present':
        create_scaling_policy(connection, module)
    elif state == 'absent':
        delete_scaling_policy(connection, module)


if __name__ == '__main__':
    main()
