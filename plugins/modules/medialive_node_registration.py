#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
module: medialive_node_registration
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
      - The ID of the Node to create registration script for.
    required: true
    type: str
    aliases: ["node_id"]
  cluster_id:
    description:
      - The ID of the cluster where the node lives.
    required: true
    type: str
    aliases: ["cluster"]
  role:
    description:
      - The initial role of the Node in the Cluster.
      - ACTIVE means the Node is available for encoding.
      - BACKUP means the Node is a redundant Node and might get used if an ACTIVE Node fails.
    required: true
    type: str
    choices: ["ACTIVE", "BACKUP"]

extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
# Request a MediaLive Anywhere node registration script
- community.aws.medialive_node_registration:
    cluster_id: '1234567'
    node_id: '7654321'
    role: 'ACTIVE'
  register: response
"""

RETURN = r"""
node_registration_script:
  description: A script that can be run on a Bring Your Own Device Elemental Anywhere system to create a node in a cluster.
  returned: success
  type: str
"""

import uuid
from typing import Dict

try:
    from botocore.exceptions import ClientError, BotoCoreError
except ImportError:
    pass # caught by AnsibleAWSModule

from ansible.module_utils.common.dict_transformations import snake_dict_to_camel_dict, camel_dict_to_snake_dict
from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.community.aws.plugins.module_utils.medialive import MedialiveAnsibleAWSError


class MediaLiveNodeRegistrationScriptManager:
    '''Requests AWS MediaLive Anywhere node registration script'''

    def __init__(self, module: AnsibleAWSModule):
        '''
        Initialize the MediaLiveNodeRegistrationScriptManager

        Args:
            module: AnsibleAWSModule instance
        '''
        self.module = module
        self.client = self.module.client('medialive')
        self._script = {}
        self.changed = False

    @property
    def script(self):
        return self._script

    @script.setter
    def script(self, script: Dict):
        script = camel_dict_to_snake_dict(script)
        if script.get('response_metadata'):
            del script['response_metadata']
        self._script = script

    # TODO: this needs to be updated once the API and the docs are fixed
    def do_create_registration_script(self, params):
        """
        Create a new MediaLive node registration script
        
        Args:
            params: Parameters for node registration script creation
        """
        # NOTE: The API docs don't match the reality as of today
        allowed_params = ['cluster_id', 'id', 'name', 'node_interface_mappings', 'request_id', 'role']
        required_params = ['cluster_id', 'id', 'role']

        for param in required_params:
            if not params.get(param):
                raise MedialiveAnsibleAWSError(
                    message=f'The {", ".join(required_params)} parameters are required when creating a new node registration script'
                )

        create_params = { k: v for k, v in params.items() if k in allowed_params and v }
        create_params = snake_dict_to_camel_dict(create_params, capitalize_first=True)

        try:
            self.script = self.client.create_node_registration_script(**create_params)  # type: ignore
            self.changed = True
        except (ClientError, BotoCoreError) as e:
            raise MedialiveAnsibleAWSError(
                message='Unable to create Medialive node registration script',
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
        id=dict(type='str', required=True, aliases=['node_id']),
        cluster_id=dict(type='str', required=True),
        role=dict(type='str', required=True, choices=["ACTIVE", "BACKUP"])
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    # Extract module parameters
    node_id = get_arg('id', module.params, argument_spec)
    cluster_id = get_arg('cluster_id', module.params, argument_spec)
    role = get_arg('role', module.params, argument_spec)

    # Initialize the manager
    manager = MediaLiveNodeRegistrationScriptManager(module)

    # Do nothing in check mode
    if module.check_mode:
        module.exit_json(changed=True)

    # Create the script
    create_params = {
        'cluster_id': cluster_id,
        'id': node_id,
        'role': role,
        'request_id': str(uuid.uuid4())
    }

    manager.do_create_registration_script(create_params)

    module.exit_json(changed=manager.changed, node=manager.script)

if __name__ == '__main__':
    main()
