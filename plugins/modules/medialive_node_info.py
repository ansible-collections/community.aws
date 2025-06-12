#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
module: medialive_node
short_description: Gather AWS MediaLive Anywhere node info
version_added: 10.1.0
description:
  - Get details about a AWS MediaLive Anywhere node.
  - This module requires boto3 >= 1.35.17.
author:
  - "Sergey Papyan"
options:
  id:
    description:
      - The ID of the Node.
      - Exactly one of I(id) or I(name) must be provided.
    required: false
    type: str
    aliases: ["node_id"]
  name:
    description:
      - The name of the Node.
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
  
extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
# Find a MediaLive Anywhere node by ID
- community.aws.medialive_node_info:
    id: '1234567'
    cluster_id: '7654321'
  register: found_node

# Find a MediaLive Anywhere node by name
- community.aws.medialive_node_info:
    name: 'ExampleNode'
    cluster_id: '7654321'
  register: found_node
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

from typing import Dict

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict
from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.botocore import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.exceptions import AnsibleAWSError


class MedialiveAnsibleAWSError(AnsibleAWSError):
    pass

class MediaLiveNodeGetter:
    '''Look up AWS MediaLive Anywhere nodes'''

    def __init__(self, module: AnsibleAWSModule):
        '''
        Initialize the MediaLiveNodeGetter

        Args:
            module: AnsibleAWSModule instance
        '''
        self.module = module
        self.client = self.module.client('medialive')
        self._node = {}

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

        except (ClientError, BotoCoreError) as e:
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
        cluster_id=dict(type='str', required=True)
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[('id', 'node_id', 'name', 'node_name')],
    )

    # Extract module parameters
    node_id = get_arg('id', module.params, argument_spec)
    node_name = get_arg('name', module.params, argument_spec)
    cluster_id = get_arg('cluster_id', module.params, argument_spec)

    # Initialize the getter
    getter = MediaLiveNodeGetter(module)

    # Find the node by ID or name
    # Update getter.node with the details
    if node_id:
        getter.get_node_by_id(cluster_id, node_id) # type: ignore
    elif node_name:
        getter.get_node_by_name(cluster_id, node_name) # type: ignore

    module.exit_json(changed=False, node=getter.node)

if __name__ == '__main__':
    main()
