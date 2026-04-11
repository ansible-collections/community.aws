#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
module: medialive_network
short_description: Gather MediaLive Anywhere network info
version_added: 10.1.0
description:
  - Get details about a AWS MediaLive Anywhere network.
  - This module requires boto3 >= 1.35.17.
author:
  - Sergey Papyan (@r363x)
options:
  id:
    description:
      - The ID of the network.
      - At least this or name must be provided
    required: false
    type: str
    aliases: ['network_id']
  name:
    description:
      - The name of the network.
      - At least this or id must be provided
    required: false
    type: str
    aliases: ['network_name']

extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
# Find a MediaLive Anywhere network by ID
- community.aws.medialive_network_info:
    id: '1234567'
  register: found_network

# Find a MediaLive Anywhere network by name
- community.aws.medialive_network_info:
    name: 'ExampleNetwork'
  register: found_network
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
      example: "arn:aws:medialive:us-east-1:123456789012:network:1234567"
    associated_cluster_ids:
      description: The IDs of clusters associated with the network.
      type: list
      elements: str
      returned: success
      example: ["cluster-1234abcd"]
    id:
      description: The ID of the network.
      type: str
      returned: success
      example: "1234567"
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

from typing import Dict

try:
    from botocore.exceptions import ClientError, BotoCoreError
except ImportError:
    pass # caught by AnsibleAWSModule

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict
from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.botocore import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.exceptions import AnsibleAWSError


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

    def find_network_by_name(self, name: str):
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
                raise AnsibleAWSError(message='Found more than one Networks under the same name')
            elif len(found) == 1:
                self.get_network_by_id(found[0])
        except (ClientError, BotoCoreError) as e: # type: ignore
            raise AnsibleAWSError(
                message='Unable to get Medialive Network',
                exception=e
            )

    def get_network_by_id(self, id: str):
        """
        Get a network by ID

        Args:
            id: The ID of the network to retrieve
        """
        try:
            self.network = self.client.describe_network(NetworkId=id)  # type: ignore
        except is_boto3_error_code('ResourceNotFoundException'):
            self.network = {}
        except (ClientError, BotoCoreError) as e: # type: ignore
            raise AnsibleAWSError(
                message='Unable to get Medialive Network',
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
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[('id', 'network_id', 'name', 'network_name')]
    )

    # Extract module parameters
    network_id = get_arg('id', module.params, argument_spec)
    network_name = get_arg('name', module.params, argument_spec)

    # Initialize the manager
    manager = MediaLiveNetworkManager(module)

    # Find the network by ID or name
    if network_id:
        manager.get_network_by_id(network_id)
    elif network_name:
        manager.find_network_by_name(network_name)

    module.exit_json(changed=False, network=manager.network)

if __name__ == '__main__':
    main()
