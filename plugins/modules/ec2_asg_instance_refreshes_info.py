#!/usr/bin/python
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function


__metaclass__ = type


DOCUMENTATION = '''
---
module: ec2_asg_instance_refreshes_info
version_added: 3.2.0
short_description: Gather information about ec2 Auto Scaling Group (ASG) Instance Refreshes in AWS
description:
  - Describes one or more instance refreshes.
  - You can determine the status of a request by looking at the I(status) parameter.
requirements: [ boto3 ]
author: "Dan Khersonsky (@danquixote)"
options:
  name:
    description:
      - The name of the Auto Scaling group.
    type: str
    required: true
  ids:
    description:
      - One or more instance refresh IDs.
    type: list
    elements: str
    default: []
  next_token:
    description:
      - The token for the next set of items to return. (You received this token from a previous call.)
    type: str
  max_records:
    description:
      - The maximum number of items to return with this call. The default value is 50 and the maximum value is 100.
    type: int
    required: false
extends_documentation_fragment:
- amazon.aws.aws
- amazon.aws.ec2

'''

EXAMPLES = '''
# Note: These examples do not set authentication details, see the AWS Guide for details.

- name: Find an refresh by ASG name
  community.aws.ec2_asg_instance_refreshes_info:
    name: somename-asg

- name: Find an refresh by ASG name and one or more refresh-IDs
  community.aws.ec2_asg_instance_refreshes_info:
    name: somename-asg
    ids: ['some-id-123']
  register: asgs

- name: Find an refresh by ASG name and set max_records
  community.aws.ec2_asg_instance_refreshes_info:
    name: somename-asg
    max_records: 4
  register: asgs

- name: Find an refresh by ASG name and NextToken, if received from a previous call
  community.aws.ec2_asg_instance_refreshes_info:
    name: somename-asg
    next_token: 'some-token-123'
  register: asgs
'''

RETURN = '''
---
instance_refresh_id:
    description: instance refresh id
    returned: success
    type: str
    sample: "08b91cf7-8fa6-48af-b6a6-d227f40f1b9b"
auto_scaling_group_name:
    description: Name of autoscaling group
    returned: success
    type: str
    sample: "public-webapp-production-1"
status:
    description:
      -  The current state of the group when DeleteAutoScalingGroup is in progress.
      -  The following are the possible statuses
      -    Pending --  The request was created, but the operation has not started.
      -    InProgress --  The operation is in progress.
      -    Successful --  The operation completed successfully.
      -    Failed --  The operation failed to complete. You can troubleshoot using the status reason and the scaling activities.
      -    Cancelling --
      -        An ongoing operation is being cancelled.
      -        Cancellation does not roll back any replacements that have already been completed,
      -        but it prevents new replacements from being started.
      -    Cancelled --  The operation is cancelled.
    returned: success
    type: str
    sample: "Pending"
start_time:
    description: The date and time this ASG was created, in ISO 8601 format.
    returned: success
    type: str
    sample: "2015-11-25T00:05:36.309Z"
end_time:
    description: The date and time this ASG was created, in ISO 8601 format.
    returned: success
    type: str
    sample: "2015-11-25T00:05:36.309Z"
percentage_complete:
    description: the % of completeness
    returned: success
    type: int
    sample: 100
instances_to_update:
    description: num. of instance to update
    returned: success
    type: int
    sample: 5
'''

try:
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:
    pass  # caught by AnsibleAWSModule

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import camel_dict_to_snake_dict
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AWSRetry


def find_asg_instance_refreshes(conn, module):
    """
    Args:
        conn (boto3.AutoScaling.Client): Valid Boto3 ASG client.
        name (str): Mandatory name of the ASG you are looking for.
        ids (dict): Optional list of ASG Instace Refresh IDs
        max_records (int): Optional number of max records to return
        next_token (str): Optional NextToken from previous call

    Basic Usage:
        >>> name = 'some-asg'
        >>> conn = boto3.client('autoscaling', region_name='us-west-2')
        >>> results = find_asg_instance_refreshes(name, conn)

    Returns:
        Dict
        {
            'instance_refreshes': [
                    {
                        'instance_refresh_id': '6507a3e5-4950-4503-8978-e9f2636efc09',
                        'auto_scaling_group_name': 'ansible-test-hermes-63642726-asg',
                        'status': 'Cancelled',
                        'status_reason': 'Cancelled due to user request.',
                        'start_time': '2021-02-04T03:39:40+00:00',
                        'end_time': '2021-02-04T03:41:18+00:00',
                        'percentage_complete': 0,
                        'instances_to_update': 1
                    }
            ],
            'next_token': 'string'
        }
        """

    asg_name = module.params.get('name')
    asg_ids = module.params.get('ids')
    asg_next_token = module.params.get('next_token')
    asg_max_records = module.params.get('max_records')

    args = {}
    args['AutoScalingGroupName'] = asg_name
    if asg_ids:
        args['InstanceRefreshIds'] = asg_ids
    if asg_next_token:
        args['NextToken'] = asg_next_token
    if asg_max_records:
        args['MaxRecords'] = asg_max_records

    try:
        asgs = conn.describe_instance_refreshes(aws_retry=True, **args)
        asgs = camel_dict_to_snake_dict(asgs)
        result = dict(
            instance_refreshes=asgs['instance_refreshes'],
            next_token=asgs.get('next_token', ''),
        )
        return module.exit_json(**result)
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg='Failed to describe InstanceRefreshes')


def main():

    argument_spec = dict(
        name=dict(required=True, type='str'),
        ids=dict(required=False, default=[], elements='str', type='list'),
        next_token=dict(required=False, default=None, type='str', no_log=True),
        max_records=dict(required=False, type='int'),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    autoscaling = module.client(
        'autoscaling',
        retry_decorator=AWSRetry.jittered_backoff(retries=10)
    )
    results = find_asg_instance_refreshes(
        autoscaling,
        module,
    )

    return results


if __name__ == '__main__':
    main()
