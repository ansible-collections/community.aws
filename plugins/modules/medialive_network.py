#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
module: medialive_network
short_description: Manage AWS MediaLive Anywhere networks
version_added: 10.1.0
description:
  - A module for creating, updating and deleting AWS MediaLive Anywhere networks.
  - This module requires boto3 >= 1.35.17.
author:
  - Sergey Papyan (@r363x)
options:
  id:
    description:
      - The ID of the network.
      - Exactly one of I(id) or I(name) must be provided.
    required: false
    type: str
    aliases: ['network_id']
  name:
    description:
      - The name of the network.
      - Exactly one of I(id) or I(name) must be provided.
    required: false
    type: str
    aliases: ['network_name']
  state:
    description:
      - Create/update or remove the network.
    required: false
    choices: ['present', 'absent']
    default: 'present'
    type: str
  ip_pools:
    description:
      - A list of IP pools to associate with the network.
      - Required when creating a new network.
    type: list
    elements: dict
    required: false
    suboptions:
      cidr:
        description:
          - The CIDR block for the IP pool.
        type: str
        required: true
  routes:
    description:
      - A list of routes to associate with the network.
    type: list
    elements: dict
    required: false
    suboptions:
      cidr:
        description:
          - The CIDR block for the route.
        type: str
        required: true
      gateway:
        description:
          - The gateway for the route.
        type: str
        required: true

extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
# Create a MediaLive Anywhere network
- community.aws.medialive_network:
    name: 'ExampleNetwork'
    state: present
    ip_pools:
      - cidr: '10.0.0.0/24'
    routes:
      - cidr: '0.0.0.0/0'
        gateway: '10.0.0.1'

# Delete a MediaLive Anywhere network
- community.aws.medialive_network:
    name: 'ExampleNetwork'
    state: absent
"""

RETURN = r"""
network:
  description: The details of the network
  returned: success
  type: dict
  contains:
    arn:
      description: The ARN of the network.
      type: str
      returned: success
      example: "arn:aws:medialive:us-east-1:123456789012:network/1234abcd-12ab-34cd-56ef-1234567890ab"
    associated_cluster_ids:
      description: The IDs of clusters associated with the network.
      type: list
      elements: str
      returned: success
      example: ["cluster-1234abcd"]
    network_id:
      description: The ID of the network.
      type: str
      returned: success
      example: "1234abcd-12ab-34cd-56ef-1234567890ab"
    ip_pools:
      description: The IP pools associated with the network.
      type: list
      elements: dict
      returned: success
      contains:
        cidr:
          description: The CIDR block for the IP pool.
          type: str
          returned: success
          example: "10.0.0.0/24"
    name:
      description: The name of the network.
      type: str
      returned: success
      example: "ExampleNetwork"
    routes:
      description: The routes associated with the network.
      type: list
      elements: dict
      returned: success
      contains:
        cidr:
          description: The CIDR block for the route.
          type: str
          returned: success
          example: "0.0.0.0/0"
        gateway:
          description: The gateway for the route.
          type: str
          returned: success
          example: "10.0.0.1"
    state:
      description: The state of the network.
      type: str
      returned: success
      example: "ACTIVE"
"""

import uuid
from typing import Dict, Literal

try:
    from botocore.exceptions import ClientError, BotoCoreError
except ImportError:
    pass # caught by AnsibleAWSModule

from ansible.module_utils.common.dict_transformations import snake_dict_to_camel_dict, camel_dict_to_snake_dict, recursive_diff
from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.botocore import is_boto3_error_code
from ansible_collections.community.aws.plugins.module_utils.medialive import MedialiveAnsibleAWSError

class MediaLiveNetworkManager:
    '''Manage AWS MediaLive Anywhere networks'''

    def __init__(self, module: AnsibleAWSModule):
        '''
        Initialize the MediaLiveNetworkManager

        Args:
            module: AnsibleAWSModule instance
        '''
        self.module = module
        self.client = self.module.client('medialive')
        self._network = {}
        self.changed = False

    @property
    def network(self):
        return self._network

    @network.setter
    def network(self, network: Dict):
        network = camel_dict_to_snake_dict(network)
        if network.get('response_metadata'):
            del network['response_metadata']
        if network.get('id'):
            network['network_id'] = network.get('id')
            del network['id']
        self._network = network


    def do_create_network(self, params):
        """
        Create a new MediaLive network
        
        Args:
            params: Parameters for network creation
        """
        allowed_params = ['ip_pools', 'name', 'routes', 'request_id']
        required_params = ['ip_pools', 'routes']

        for param in required_params:
            if not params.get(param):
                raise MedialiveAnsibleAWSError(message=f'The {param} parameter is required when creating a new Network')

        create_params = { k: v for k, v in params.items() if k in allowed_params and v }
        create_params = snake_dict_to_camel_dict(create_params, capitalize_first=True)

        try:
            self.network = self.client.create_network(**create_params)  # type: ignore
            self.changed = True
        except (ClientError, BotoCoreError) as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message='Unable to create Medialive Network',
                exception=e
            )


    def do_update_network(self, params):
        """
        Update a new MediaLive network
        
        Args:
            params: Parameters for network update
        """
        if not params.get('network_id'):
            raise MedialiveAnsibleAWSError(message='The network_id parameter is required during network update.')

        allowed_params = ['ip_pools', 'name', 'routes', 'network_id']


        current_params = { k: v for k, v in self.network.items() if k in allowed_params }
        update_params = { k: v for k, v in params.items() if k in allowed_params and v }

        # Short circuit
        if not recursive_diff(current_params, update_params):
            return

        update_params = snake_dict_to_camel_dict(update_params, capitalize_first=True)

        try:
            self.network = self.client.update_network(**update_params)  # type: ignore
            self.changed = True
        except (ClientError, BotoCoreError) as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message='Unable to update Medialive Network',
                exception=e
            )

    def get_network_by_name(self, name: str):
        """
        Find a network by name

        Args:
            name: The name of the network to find
        """

        try:
            paginator = self.client.get_paginator('list_networks')  # type: ignore
            found = []
            for page in paginator.paginate():
                for network in page.get('Networks', []):
                    if network.get('Name') == name:
                        found.append(network.get('Id'))
            if len(found) > 1:
                raise MedialiveAnsibleAWSError(message='Found more than one Networks under the same name')
            elif len(found) == 1:
                self.get_network_by_id(found[0])

        except (ClientError, BotoCoreError) as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message='Unable to get Medialive Network',
                exception=e
            )

    def get_network_by_id(self, network_id: str):
        """
        Get a network by ID

        Args:
            network_id: The ID of the network to retrieve
        """
        try:
            self.network = self.client.describe_network(NetworkId=network_id)  # type: ignore
        except is_boto3_error_code('ResourceNotFoundException'):
            self.network = {}
        except (ClientError, BotoCoreError) as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message='Unable to get Medialive Network',
                exception=e
            )

    def delete_network(self, network_id: str):
        """
        Delete a MediaLive network
        
        Args:
            network_id: ID of the network to delete
        """
        try:
            self.client.delete_network(NetworkId=network_id)  # type: ignore
            self.network = {}
            self.changed = True
        except is_boto3_error_code('ResourceNotFoundException'):
            self.network = {}
        except (ClientError, BotoCoreError) as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message='Unable to delete Medialive Network',
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
        id=dict(type='str', required=False, aliases=['network_id']),
        name=dict(type='str', required=False, aliases=['network_name']),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        ip_pools=dict(
            type='list',
            elements='dict',
            required=False,
            options=dict(cidr=dict(type='str', required=True),
        )),
        routes=dict(
            type='list',
            elements='dict',
            required=False,
            options=dict(
                cidr=dict(type='str', required=True),
                gateway=dict(type='str', required=True),
            )
        )
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[('id', 'network_id', 'name', 'network_name')]
    )

    # Extract module parameters
    network_id = get_arg('id', module.params, argument_spec)
    network_name = get_arg('name', module.params, argument_spec)
    state = get_arg('state', module.params, argument_spec)
    ip_pools = get_arg('ip_pools', module.params, argument_spec)
    routes = get_arg('routes', module.params, argument_spec)

    # Initialize the manager
    manager = MediaLiveNetworkManager(module)

    # Find the network by ID or name
    if network_id:
        manager.get_network_by_id(network_id)
    elif network_name:
        manager.get_network_by_name(network_name)
        network_id = manager.network.get('network_id')

    # Do nothing in check mode
    if module.check_mode:
        module.exit_json(changed=True)

    # Handle present state
    if state == 'present':

        # Case update
        if manager.network:

            update_params = {
                'name': network_name,
                'ip_pools': ip_pools,
                'routes': routes,
                'network_id': network_id
            }

            manager.do_update_network(update_params)

        # Case create
        else:
            create_params = {
                'name': network_name,
                'ip_pools': ip_pools,
                'routes': routes,
                'request_id': str(uuid.uuid4())
            }
            
            manager.do_create_network(create_params)
            network_id = manager.network.get('network_id')
            
    # Handle absent state
    elif state == 'absent':
        if manager.network:
            # Network exists, delete it
            network_id = manager.network.get('network_id')
            manager.delete_network(network_id) # type: ignore
            
    module.exit_json(changed=manager.changed, network=manager.network)


if __name__ == '__main__':
    main()
