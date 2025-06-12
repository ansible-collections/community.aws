#!/usr/bin/python
# Copyright: (c) 2025, Your Name <your.email@example.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: medialive_channel_placement_group_info
short_description: Get information about an AWS MediaLive Channel Placement Group
version_added: 10.1.0
description:
  - Get information about an AWS MediaLive Channel Placement Group.
  - This module allows retrieving detailed information about a specific channel placement group.
author:
  - "David Teach"
options:
  channel_placement_group_id:
    description:
      - The ID of the Channel Placement Group.
    required: true
    type: str
  cluster_id:
    description:
      - The ID of the cluster.
    required: true
    type: str
  aws_access_key:
    description:
      - AWS access key ID.
    type: str
  aws_secret_key:
    description:
      - AWS secret access key.
    type: str
  region:
    description:
      - The AWS region to use.
    required: true
    type: str
    
extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
'''

EXAMPLES = r'''
# Get information about a specific channel placement group
- name: Get channel placement group info
  aws_medialive_channel_placement_group_info:
    channel_placement_group_id: "cpg-12345"
    cluster_id: "cluster-67890"
    region: "us-west-2"
'''

RETURN = r'''
placement_group:
    description: The channel placement group information
    type: dict
    returned: always
    contains:
        arn:
            description: The ARN of the channel placement group
            type: str
            returned: always
        channel_placement_group_id:
            description: The ID of the channel placement group
            type: str
            returned: always
        cluster_id:
            description: The ID of the cluster
            type: str
            returned: always
        created:
            description: When the channel placement group was created
            type: str
            returned: always
        state:
            description: The state of the channel placement group
            type: str
            returned: always
'''

try:
    import botocore
except ImportError:
    pass  # Handled by AnsibleAWSModule

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict
from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AWSRetry


def get_channel_placement_group(client, module):
    """
    Get the channel placement group information
    """
    cpgs = []
    try:
        if not module.params['channel_placement_group_id']:
            response = client.list_channel_placement_groups(
                ClusterId=module.params['cluster_id']
            )
            if response['ChannelPlacementGroups']:
                cpgs = response['ChannelPlacementGroups']
        else:
            response = client.describe_channel_placement_group(
                ChannelPlacementGroupId=module.params['channel_placement_group_id'],
                ClusterId=module.params['cluster_id']
            )
            if response.get('Arn', None):
                cpgs.append(response)
        if len(cpgs) == 0:
            return cpgs
        results = [camel_dict_to_snake_dict(cpg) for cpg in cpgs]
        return results
    except client.exceptions.NotFoundException:
        return cpgs
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Failed to get channel placement group information")


def main():
    argument_spec = dict(
        cluster_id=dict(required=True, type='str'),
        channel_placement_group_id=dict(required=False, type='str'),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    try:
        client = module.client('medialive', retry_decorator=AWSRetry.exponential_backoff())
        cpgs = get_channel_placement_group(client, module)
        module.exit_json(changed=False, channel_placement_groups=cpgs)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg='Failed to connect to AWS')


if __name__ == '__main__':
    main()
