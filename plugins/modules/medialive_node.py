#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
DOCUMENTATION = r"""
module: medialive_node
short_description: Manage AWS MediaLive Anywhere nodes
version_added: 10.1.0
description:
  - A module for creating, updating and deleting AWS MediaLive Anywhere nodes.
  - This module requires boto3 >= 1.37.34.
author:
  - Sergey Papyan (@r363x)
options:
  id:
    description:
      - The ID of the Node to manage.
      - Exactly one of I(id) or I(name) must be provided.
    required: false
    type: str
    aliases: ["node_id"]
  name:
    description:
      - The user-specified name of the Node to be created.
      - Name should include at least one number or letter. The allowed special characters are - space, at-sign, hyphen, underscore, period, comma, apostrophe and semicolon.
      - Exactly one of I(id) or I(name) must be provided.
    required: false
    type: str
    aliases: ["node_name"]
  cluster_id:
    description:
      - The ID of the cluster.
    required: true
    type: str
    aliases: ["cluster"]
  node_interface_mappings:
    description:
      - A list of logical interface to physical interface mappings
    required: false
    type: list
    elements: dict
    suboptions:
      logical_interface_name:
        description:
          - one of the logicalInterfaceNames in the Cluster that this node belongs to
        type: str
        required: true
      physical_interface_name:
        description:
          - the physical interface name that corresponds to the logical interface name
        type: str
        required: true
      network_interface_mode:
        description:
          - The style of the network – NAT or BRIDGE.
        type: str
        choices: ["NAT", "BRIDGE"]
        required: true
  role:
    description:
      - The initial role of the Node in the Cluster.
      - ACTIVE means the Node is available for encoding.
      - BACKUP means the Node is a redundant Node and might get used if an ACTIVE Node fails.
    required: false
    type: str
    choices: ["ACTIVE", "BACKUP"]
  sdi_source_mappings:
    description:
      - The mappings of a SDI capture card port to a logical SDI data stream
      - Can only be applied to an existing node, not on node creation.
    required: false
    type: list
    elements: dict
    suboptions:
      card_number:
        description: 
          - A number that uniquely identifies the SDI card on the node hardware. 
          - For information about how physical cards are identified on your node hardware, see the documentation for your node hardware. 
          - The numbering always starts at 1.
        type: int
        required: true
      channel_number:
        description: 
          - A number that uniquely identifies a port on the card. 
          - This must be an SDI port (not a timecode port, for example). 
          - For information about how ports are identified on physical cards, see the documentation for your node hardware.
        type: int
        required: true
      sdi_source:
        description: 
          - The ID of a SDI source streaming on the given SDI capture card port.
        required: true
        type: str
  
extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
# Create a MediaLive Anywhere node
- community.aws.medialive_node:
    name: 'ExampleNode'
    cluster_id: '1234567'
    node_interface_mappings:
      - logical_interface_name: input-if-1
        physical_interface_name: eth1
        network_interface_mode: NAT
    role: 'ACTIVE'
    state: present
    
# Update an existing MediaLive Anywhere node with SDI mappings
- community.aws.medialive_node:
    name: 'ExampleNode'
    cluster_id: '1234567'
    sdi_source_mappings:
      - card_number: 123
        channel_number: 123
        sdi_source: 'string'
    state: present

# Delete a MediaLive Anywhere node
- community.aws.medialive_node:
    id: '1234567'
    cluster_id: '7654321'
    state: absent
"""

RETURN = r"""
node:
  description: The details of the node
  returned: success
  type: dict
  contains:
    arn:
      description: The ARN of the node.
      type: str
      returned: success
      example: "arn:aws:medialive:us-east-1:123456789012:node:1234567/7654321"
    channel_placement_groups:
      description: An array of IDs. Each ID is one channel_placement_group that is associated with this Node. Empty if the Node is not yet associated with any groups.
      type: list
      elements: str
      returned: success
      example: ["1234567", "7654321"]
    cluster_id:
      description: The ID of the cluster that the node belongs to.
      type: str
      returned: success
      example: "1234567"
    connection_state:
      description: The connection state of the node. Can be CONNECTED or DISCONNECTED.
      type: str
      returned: success
      example: "CONNECTED"
    node_id:
      description: The unique ID of the node. Unique in the cluster. The ID is the resource-id portion of the ARN.
      type: str
      returned: success
      example: "1234567"
    instance_arn:
      description: The ARN of the EC2/SSM Managed instance hosting the Node.
      type: str
      returned: success
      example: "arn:aws:ssm:us-east-1:123456789012:managed-instance/mi-abcdefgh12345678"
    name:
      description: The name of the node.
      type: str
      returned: success
      example: "ExampleNode"
    node_interface_mappings:
      description: A mapping that’s used to pair a logical network interface name on a node with the physical interface name exposed in the operating system.
      type: list
      elements: dict
      returned: success
      contains:
        logical_interface_name:
          description: A uniform logical interface name to address in a MediaLive channel configuration.
          type: str
          returned: success
          example: "input-if-1"
        physical_interface_name:
          description: The name of the physical interface on the hardware that will be running AWS MediaLive anywhere.
          type: str
          returned: success
          example: "eth1"
        network_interface_mode:
          description: The style of the network – NAT or BRIDGE.
          type: str
          returned: success
          example: "NAT"
    role:
      description: The role of the node in the cluster. Can be ACTIVE or BACKUP.
      type: str
      returned: success
      example: "ACTIVE"
    sdi_source_mappings:
      description: 
        - An array of SDI source mappings. 
        - Each mapping connects one logical SdiSource to the physical SDI card and port that the physical SDI source uses.
      type: list
      elements: dict
      returned: success
      contains:
        card_number:
          description: 
            - A number that uniquely identifies the SDI card on the node hardware. 
            - For information about how physical cards are identified on your node hardware, see the documentation for your node hardware. 
            - The numbering always starts at 1.
          type: int
          returned: success
        channel_number:
          description: 
            - A number that uniquely identifies a port on the card. 
            - This must be an SDI port (not a timecode port, for example). 
            - For information about how ports are identified on physical cards, see the documentation for your node hardware.
          type: int
          returned: success
        sdi_source:
          description: 
            - The ID of a SDI source streaming on the given SDI capture card port.
          returned: success
          type: str
    state:
      description: >
        The current state of the node.
        Possible values:
          - CREATED
          - REGISTERING
          - READY_TO_ACTIVATE
          - REGISTRATION_FAILED
          - ACTIVATION_FAILED
          - ACTIVE
          - READY
          - IN_USE
          - DEREGISTERING
          - DRAINING
          - DEREGISTRATION_FAILED
          - DEREGISTERED
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
from ansible_collections.community.aws.plugins.module_utils.medialive import MedialiveAnsibleAWSError


class MediaLiveNodeManager:
    '''Manage AWS MediaLive Anywhere node'''

    def __init__(self, module: AnsibleAWSModule):
        '''
        Initialize the MediaLiveNodeManager

        Args:
            module: AnsibleAWSModule instance
        '''
        self.module = module
        self.client = self.module.client('medialive')
        self._node = {}
        self.changed = False

    @property
    def node(self):
        return self._node

    @node.setter
    def node(self, node: Dict):
        node = camel_dict_to_snake_dict(node)
        if node.get('response_metadata'):
            del node['response_metadata']
        if node.get('id'):
            node['node_id'] = node.get('id')
            del node['id']
        self._node = node

    def do_create_node(self, params):
        """
        Create a new MediaLive node
        
        Args:
            params: Parameters for node creation
        """
        allowed_params = ['cluster_id', 'name', 'node_interface_mappings', 'role', 'request_id']
        required_params = ['cluster_id', 'name', 'node_interface_mappings', 'role']

        for param in required_params:
            if not params.get(param):
                raise MedialiveAnsibleAWSError(
                    message=f'The {", ".join(required_params)} parameters are required when creating a new node'
                )

        create_params = { k: v for k, v in params.items() if k in allowed_params and v }
        create_params = snake_dict_to_camel_dict(create_params, capitalize_first=True)

        try:
            self.node = self.client.create_node(**create_params)  # type: ignore
            self.changed = True
        except (ClientError, BotoCoreError) as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message='Unable to create Medialive node',
                exception=e
            )

    def do_update_node(self, params: dict):
        """
        Update a new MediaLive node
        
        Args:
            params: Parameters for node update
        """

        allowed_params = ['cluster_id', 'node_id', 'name', 'role']

        current_params = { k: v for k, v in self.node.items() if k in allowed_params }
        update_params = { k: v for k, v in params.items() if k in allowed_params and v }

        update_params['cluster_id'] = self.node.get('cluster_id')
        update_params['node_id'] = self.node.get('node_id')
        if params.get('sdi_source_mappings'):
            update_params['sdi_source_mappings'] = params.get('sdi_source_mappings')

        # Short circuit
        if not recursive_diff(current_params, update_params):
            return

        update_params = snake_dict_to_camel_dict(update_params, capitalize_first=True)

        try:
            response = self.client.update_node(**update_params)  # type: ignore
            self.node = camel_dict_to_snake_dict(response)
            self.changed = True
        except (ClientError, BotoCoreError) as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message='Unable to update Medialive node',
                exception=e
            )

    def delete_node(self):
        """
        Delete a MediaLive node
        """
        try:
            self.client.delete_node(ClusterId=self.node.get('cluster_id'), NodeId=self.node.get('node_id'))  # type: ignore
            self.changed = True
        except is_boto3_error_code('ResourceNotFoundException'):
            self.node = {}
        except (ClientError, BotoCoreError) as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message='Unable to delete Medialive node',
                exception=e
            )

    def get_node_by_name(self, cluster_id: str, name: str):
        """
        Find a node by name

        Args:
            cluster_id: The id of the cluster to which the node belongs
            name: The name of the node to find
        """
        try:
            paginator = self.client.get_paginator('list_nodes') # type: ignore
            found = []
            for page in paginator.paginate(ClusterId=cluster_id):
                for node in page.get('Nodes', []):
                    if node.get('Name') == name:
                        found.append(node.get('Id'))
            if len(found) > 1:
                raise MedialiveAnsibleAWSError(message='Found more than one Nodes under the same name')
            elif len(found) == 1:
                self.get_node_by_id(cluster_id, found[0])

        except (ClientError, BotoCoreError) as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message='Unable to get Medialive Node',
                exception=e
            )

    def get_node_by_id(self, cluster_id: str, node_id: str):
        """
        Get a node by ID

        Args:
            cluster_id: The id of the cluster to which the node belongs
            node_id: The ID of the node to retrieve
        """
        try:
            self.node = self.client.describe_node(ClusterId=cluster_id, NodeId=node_id) # type: ignore
            return True
        except is_boto3_error_code('ResourceNotFoundException'):
            self.node = {}

def get_arg(arg:str, params:dict, spec:dict):
    if arg in spec.keys():
        aliases = spec[arg].get('aliases', [])
        for k, v in params.items():
            if k in [arg, *aliases] and v:
                return v

def main():
    """Main entry point for the module"""
    argument_spec = dict(
        id=dict(type='str', required=False, aliases=['node_id']),
        name=dict(type='str', required=False, aliases=['node_name']),
        cluster_id=dict(type='str', required=True),
        node_interface_mappings=dict(
            type='list',
            elements='dict',
            required=False,
            options=dict(
                logical_interface_name=dict(type='str', required=True),
                physical_interface_name=dict(type='str', required=True),
                network_interface_mode=dict(type='str', required=True, choices=['NAT', 'BRIDGE']),
            )
        ),
        role=dict(type='str', required=False, choices=["ACTIVE", "BACKUP"]),
        sdi_source_mappings=dict(
            type='list',
            elements='dict',
            required=False,
            options=dict(
                card_number=dict(type='int', required=True),
                channel_number=dict(type='int', required=True),
                sdi_source=dict(type='str', required=True),
            )
        ),
        state=dict(type='str', default='present', choices=['present', 'absent'])
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[('id', 'node_id', 'name', 'node_name')]
    )

    # Extract module parameters
    node_id = get_arg('id', module.params, argument_spec)
    node_name = get_arg('name', module.params, argument_spec)
    cluster_id = get_arg('cluster_id', module.params, argument_spec)
    node_interface_mappings = get_arg('node_interface_mappings', module.params, argument_spec)
    role = get_arg('role', module.params, argument_spec)
    sdi_source_mappings = get_arg('sdi_source_mappings', module.params, argument_spec)
    state = get_arg('state', module.params, argument_spec)

    # Initialize the manager
    manager = MediaLiveNodeManager(module)

    # Find the node by ID or name
    # Update manager.node with the details
    if node_id:
        manager.get_node_by_id(cluster_id, node_id) # type: ignore
    elif node_name:
        manager.get_node_by_name(cluster_id, node_name) # type: ignore

    # Do nothing in check mode
    if module.check_mode:
        module.exit_json(changed=True)

    # Handle present state
    if state == 'present':

        # Case update
        if manager.node:
            update_params = {
                'name': node_name,
                'role': role,
                'sdi_source_mappings': sdi_source_mappings
            }

            manager.do_update_node(update_params)

        # Case create
        else:
            create_params = {
                'cluster_id': cluster_id,
                'name': node_name,
                'node_interface_mappings': node_interface_mappings,
                'role': role,
                'request_id': str(uuid.uuid4())
            }

            manager.do_create_node(create_params)

    # Handle absent state
    elif state == 'absent':
        if manager.node:
            # Node exists, delete it
            manager.delete_node()

    module.exit_json(changed=manager.changed, node=manager.node)

if __name__ == '__main__':
    main()
