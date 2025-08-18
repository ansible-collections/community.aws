#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
module: medialive_channel_placement_group
short_description: Manage AWS MediaLive Channel Placement Groups
version_added: 10.1.0
description:
  - A module for creating, updating and deleting AWS MediaLive Channel Placement Groups.
  - This module requires boto3 >= 1.35.17.
author:
  - "David Teach"
options:
  id:
    description:
      - The ID of the channel placement group.
      - Required when updating or deleting an existing placement group.
    required: false
    type: str
    aliases: ['channel_placement_group_id']
  cluster_id:
    description:
      - The ID of the cluster.
      - Required for all operations.
    required: true
    type: str
  nodes:
    description:
      - A list of node IDs to associate with the channel placement group.
      - Required when creating a new placement group.
    type: list
    elements: str
    required: false
  state:
    description:
      - Create/update or remove the channel placement group.
    required: false
    choices: ['present', 'absent']
    default: 'present'
    type: str
  wait:
    description:
      - Whether to wait for the channel placement group to reach the desired state.
      - When I(state=present), wait for the placement group to reach the ACTIVE state.
      - When I(state=absent), wait for the placement group to be deleted.
    type: bool
    required: false
    default: true
  wait_timeout:
    description:
      - The maximum time in seconds to wait for the channel placement group to reach the desired state.
      - Defaults to 60 seconds.
    type: int
    required: false
    default: 60

extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
# Create a MediaLive Channel Placement Group
- community.aws.medialive_channel_placement_group:
    cluster_id: '123456'
    nodes:
      - '34598743'
    state: present

# Update a MediaLive Channel Placement Group
- community.aws.medialive_channel_placement_group:
    id: '234523'
    cluster_id: '123456'
    name: 'UpdatedPlacementGroup'
    nodes:
      - '34598743'
    state: present

# Delete a MediaLive Channel Placement Group
- community.aws.medialive_channel_placement_group:
    id: '234523'
    cluster_id: '123456'
    state: absent
"""

RETURN = r"""
placement_group:
  description: The details of the channel placement group
  returned: success
  type: dict
  contains:
    arn:
      description: The ARN of the channel placement group
      type: str
      returned: success
      example: "arn:aws:medialive:us-east-1:123456789012:channelplacementgroup/cpg-12345"
    channel_placement_group_id:
      description: The ID of the channel placement group
      type: str
      returned: success
      example: "234523"
    cluster_id:
      description: The ID of the cluster
      type: str
      returned: success
      example: "123456"
    created:
      description: When the channel placement group was created
      type: str
      returned: success
      example: "2025-03-31T23:08:55Z"
    state:
      description: The state of the channel placement group
      type: str
      returned: success
      example: "ACTIVE"
"""

import uuid
from typing import Dict, Literal

try:
    from botocore.exceptions import WaiterError, ClientError, BotoCoreError
except ImportError:
    pass # caught by AnsibleAWSModule

from ansible.module_utils.common.dict_transformations import snake_dict_to_camel_dict, camel_dict_to_snake_dict, recursive_diff
from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.botocore import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.exceptions import AnsibleAWSError
from ansible_collections.community.aws.plugins.module_utils.medialive import MedialiveAnsibleAWSError


class MediaLiveChannelPlacementGroupManager:
    '''Manage AWS MediaLive Channel Placement Groups'''

    def __init__(self, module: AnsibleAWSModule):
        '''
        Initialize the MediaLiveChannelPlacementGroupManager

        Args:
            module: AnsibleAWSModule instance
        '''
        self.module = module
        self.client = self.module.client('medialive')
        self._channel_placement_group = {}
        self.changed = False

    @property
    def channel_placement_group(self):
        return self._channel_placement_group

    @channel_placement_group.setter
    def channel_placement_group(self, channel_placement_group: Dict):
        if channel_placement_group.get('response_metadata'):
            del channel_placement_group['response_metadata']
        if channel_placement_group.get('id'):
            channel_placement_group['channel_placement_group_id'] = channel_placement_group.get('id')
            del channel_placement_group['id']
        self._channel_placement_group = channel_placement_group

    def do_create_channel_placement_group(self, params):
        """
        Create a new MediaLive channel placement group

        Args:
            params: Parameters for channel placement group creation
        """
        allowed_params = ['cluster_id', 'nodes', 'name', 'request_id']

        create_params = {k: v for k, v in params.items() if k in allowed_params and v}
        create_params = snake_dict_to_camel_dict(create_params, capitalize_first=True)

        try:
            response = self.client.create_channel_placement_group(**create_params)  # type: ignore
            self.channel_placement_group = camel_dict_to_snake_dict(response)
            self.changed = True
        except (ClientError, BotoCoreError) as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message='Unable to create MediaLive Channel Placement Group',
                exception=e
            )

    def do_update_channel_placement_group(self, params):
        """
        Update a MediaLive channel placement group

        Args:
            params: Parameters for channel placement group update
        """
        if not params.get('channel_placement_group_id'):
            raise MedialiveAnsibleAWSError(
                message='The channel_placement_group_id parameter is required during placement group update.')

        allowed_params = ['cluster_id', 'channel_placement_group_id', 'nodes', 'name']

        current_params = {k: v for k, v in self.channel_placement_group.items() if k in allowed_params}
        updated_params = {k: v for k, v in params.items() if k in allowed_params and v}

        # Check if params need updating
        if not recursive_diff(current_params, updated_params):
            return

        # Update nodes if provided
        if params.get('nodes'):
            try:
                # Check if nodes need updating
                current_nodes = self.channel_placement_group.get('nodes', [])
                if set(current_nodes) != set(params.get('nodes')):
                    update_params = {
                        'ChannelPlacementGroupId': params.get('channel_placement_group_id'),
                        'ClusterId': params.get('cluster_id'),
                        'Nodes': params.get('nodes')
                    }

                    # Add name if provided
                    if params.get('name'):
                        update_params['Name'] = params.get('name')

                    self.client.update_channel_placement_group(**update_params) # type: ignore
                    self.changed = True

                    # Refresh placement group data
                    self.get_channel_placement_group_by_id(
                        params.get('channel_placement_group_id'),
                        params.get('cluster_id')
                    )
            except (ClientError, BotoCoreError) as e: # type: ignore
                raise MedialiveAnsibleAWSError(
                    message='Unable to update nodes for MediaLive Channel Placement Group',
                    exception=e
                )
        # Update name if provided (and nodes not provided)
        elif params.get('name') and self.channel_placement_group.get('name') != params.get('name'):
            try:
                update_params = {
                    'ChannelPlacementGroupId': params.get('channel_placement_group_id'),
                    'ClusterId': params.get('cluster_id'),
                    'Name': params.get('name')
                }

                self.client.update_channel_placement_group(**update_params) # type: ignore
                self.changed = True

                # Refresh placement group data
                self.get_channel_placement_group_by_id(
                    params.get('channel_placement_group_id'),
                    params.get('cluster_id')
                )
            except (ClientError, BotoCoreError) as e: # type: ignore
                raise MedialiveAnsibleAWSError(
                    message='Unable to update name for MediaLive Channel Placement Group',
                    exception=e
                )

    def get_channel_placement_group_by_id(self, placement_group_id: str, cluster_id: str):
        """
        Get a channel placement group by ID

        Args:
            placement_group_id: The ID of the channel placement group to retrieve
            cluster_id: The ID of the cluster
        """
        try:
            response = self.client.describe_channel_placement_group( # type: ignore
                ChannelPlacementGroupId=placement_group_id,
                ClusterId=cluster_id
            )
            self.channel_placement_group = camel_dict_to_snake_dict(response)
        except is_boto3_error_code('ResourceNotFoundException'):
            self.channel_placement_group = {}
        except (ClientError, BotoCoreError) as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message='Unable to get MediaLive Channel Placement Group',
                exception=e
            )

    def get_channel_placement_group_by_name(self, name: str, cluster_id: str):
        """
        Get a channel placement group by name

        Args:
            name: The name of the channel placement group to retrieve
            cluster_id: The ID of the cluster
        """
        try:
            response = self.client.list_channel_placement_groups(ClusterId=cluster_id) # type: ignore
            if response['ChannelPlacementGroups']:
                found = []
                for cpg in response['ChannelPlacementGroups']:
                    if cpg['Name'] == name:
                        found.append(camel_dict_to_snake_dict(cpg))
                if len(found) > 1:
                    raise MedialiveAnsibleAWSError(message='Found more than one Channel Placement Groups under the same name')
                elif len(found) == 1:
                    self.channel_placement_group = camel_dict_to_snake_dict(found[0])
        except (ClientError, BotoCoreError) as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message='Unable to get MediaLive Channel Placement Group',
                exception=e
            )

    def delete_channel_placement_group(self, placement_group_id: str, cluster_id: str):
        """
        Delete a MediaLive channel placement group

        Args:
            placement_group_id: ID of the channel placement group to delete
            cluster_id: ID of the cluster
        """
        try:
            self.client.delete_channel_placement_group( # type: ignore
                ChannelPlacementGroupId=placement_group_id,
                ClusterId=cluster_id
            )
            self.changed = True
        except is_boto3_error_code('ResourceNotFoundException'):
            self.channel_placement_group = {}
        except (ClientError, BotoCoreError) as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message='Unable to delete MediaLive Channel Placement Group',
                exception=e
            )

    def wait_for(
        self,
        want: Literal['channel_placement_group_unassigned', 'channel_placement_group_deleted'],
        placement_group_id: str,
        cluster_id: str,
        wait_timeout = 60) -> None:
        """
        Wait for a channel placement group to reach the desired state

        Args:
            want: The desired state to wait for
            placement_group_id: The ID of the channel placement group
            cluster_id: The ID of the cluster
            wait_timeout: Maximum time to wait in seconds
        """
        try:
            waiter = self.client.get_waiter(want) # type: ignore
            config = {
                'Delay': min(5, wait_timeout),
                'MaxAttempts': wait_timeout // 5
            }
            waiter.wait(
                ChannelPlacementGroupId=placement_group_id,
                ClusterId=cluster_id,
                WaiterConfig=config
            )
        except WaiterError as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message=f'Timeout waiting for channel placement group {placement_group_id} to be {want.lower()}',
                exception=e
            )

def get_arg(arg:str, params:dict, spec:dict):
    if arg in spec.keys():
        aliases = spec[arg].get('aliases', [])
        for k, v in params.items():
            if k in [arg, *aliases] and v:
                return v

def main():
    """Main entry point for the module"""
    argument_spec = dict(
        id=dict(type='str', required=False, aliases=['channel_placement_group_id']),
        cluster_id=dict(type='str', required=True),
        nodes=dict(type='list', elements='str', required=False),
        name=dict(type='str', required=False),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        wait=dict(type='bool', default=True),
        wait_timeout=dict(type='int', default=60),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[('id', 'channel_placement_group_id', 'name')],
        required_if=[
            ('state', 'absent', ['id', 'channel_placement_group_id'], True),
        ],
    )

    # Extract module parameters
    placement_group_id = get_arg('id', module.params, argument_spec)
    cluster_id = get_arg('cluster_id', module.params, argument_spec)
    state = get_arg('state', module.params, argument_spec)
    nodes = get_arg('nodes', module.params, argument_spec)
    name = get_arg('name', module.params, argument_spec)
    wait = get_arg('wait', module.params, argument_spec)
    wait_timeout = get_arg('wait_timeout', module.params, argument_spec)

    # Initialize the manager
    manager = MediaLiveChannelPlacementGroupManager(module)

    # Find the placement group by ID if provided
    if placement_group_id:
        manager.get_channel_placement_group_by_id(placement_group_id, cluster_id) # type: ignore
    elif name:
        manager.get_channel_placement_group_by_name(name, cluster_id) # type: ignore

    # Do nothing in check mode
    if module.check_mode:
        module.exit_json(changed=True)

    # Handle present state
    if state == 'present':
        # Case update
        if manager.channel_placement_group:
            if not placement_group_id:
                placement_group_id = manager.channel_placement_group.get('channel_placement_group_id')
            update_params = {
                'channel_placement_group_id': placement_group_id,
                'cluster_id': cluster_id,
                'nodes': nodes,
                'name': name
            }

            manager.do_update_channel_placement_group(update_params)

            manager.get_channel_placement_group_by_id(placement_group_id, cluster_id) # type: ignore

        # Case create
        else:
            create_params = {
                'cluster_id': cluster_id,
                'nodes': nodes,
                'name': name,
                'request_id': str(uuid.uuid4())
            }

            manager.do_create_channel_placement_group(create_params)
            placement_group_id = manager.channel_placement_group.get('channel_placement_group_id')

            # Wait for the placement group to be created
            if wait and placement_group_id:
                manager.wait_for('channel_placement_group_unassigned', placement_group_id, cluster_id, wait_timeout) # type: ignore
                manager.get_channel_placement_group_by_id(placement_group_id, cluster_id) # type: ignore

    # Handle absent state
    elif state == 'absent':
        if manager.channel_placement_group.get('state') != 'DELETED':
            # Placement group exists, delete it
            manager.delete_channel_placement_group(placement_group_id, cluster_id) # type: ignore

            # Wait for the placement group to be deleted if requested
            if wait and placement_group_id:
                manager.wait_for('channel_placement_group_deleted', placement_group_id, cluster_id, wait_timeout) # type: ignore

    module.exit_json(changed=manager.changed, channel_placement_group=manager.channel_placement_group)


if __name__ == '__main__':
    main()
