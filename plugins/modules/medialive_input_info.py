#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
module: medialive_input_info
short_description: Gather MediaLive Anywhere input info
version_added: 10.1.0
description:
  - A module for gathering information about AWS MediaLive inputs
  - Requires boto3 >= 1.37.34
author:
  - Sergey Papyan (@r363x)
options:
  name:
    description:
      - Name of the input
      - At least this or id must be provided
    type: str
  id:
    description:
      - ID of the input
      - At least this or name must be provided
    type: str

extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
# Find a MediaLive Anywhere Input by ID
- community.aws.medialive_input_info:
    id: '1234567'
  register: found_input

# Find a MediaLive Anywhere Input by name
- community.aws.medialive_input_info:
    name: 'ExampleInput'
  register: found_input
"""

RETURN = r"""
"""

from typing import Dict, List

try:
    from botocore.exceptions import WaiterError, ClientError, BotoCoreError
except ImportError:
    pass # caught by AnsibleAWSModule

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict
from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.botocore import is_boto3_error_code
from ansible_collections.community.aws.plugins.module_utils.medialive import MedialiveAnsibleAWSError


class MediaLiveInputGetter:
    """Gather info about AWS MediaLive Anywhere Inputs"""

    def __init__(self, module: AnsibleAWSModule):
        """
        Initialize the MediaLiveInputGetter

        Args:
            module: AnsibleAWSModule instance
        """
        self.module = module
        self.client = self.module.client('medialive')
        self._input = {}

    @property
    def input(self):
        """Simple getter for input"""
        return self._input

    @input.setter
    def input(self, input: Dict):
        """Setter for input that takes care of normalizing raw API responses"""
        tags = input.get('Tags') # To preserve case in tag keys
        input = camel_dict_to_snake_dict(input)
        if 'response_metadata' in input.keys():
            del input['response_metadata'] # Unneeded
        if input.get('id'):
            input['input_id'] = input.get('id')
            del input['id']
        if tags:
            input['tags'] = tags
        self._input = input

    def find_input_by_name(self, name: str):
        """
        Find an Input by name

        Args:
            name: The name of the input to find
        """

        try:
            paginator = self.client.get_paginator('list_inputs')  # type: ignore
            found = []
            for page in paginator.paginate():
                for input in page.get('Inputs', []):
                    if input.get('Name') == name:
                        found.append(input.get('Id'))
            if len(found) > 1:
                raise MedialiveAnsibleAWSError(message='Found more than one Inputs under the same name')
            elif len(found) == 1:
                self.get_input_by_id(found[0])
        except (ClientError, BotoCoreError) as e:
            raise MedialiveAnsibleAWSError(
                message='Unable to get Medialive Input',
                exception=e
            )

    def get_input_by_id(self, input_id: str):
        """
        Get an input by ID

        Args:
            input_id: The ID of the input to retrieve
        """
        try:
            self.input = self.client.describe_input(InputId=input_id)  # type: ignore
        except is_boto3_error_code('ResourceNotFoundException'):
            self.input = {}
        except (ClientError, BotoCoreError) as e:
            raise MedialiveAnsibleAWSError(
                message='Unable to get Medialive Input',
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
        id=dict(type='str', aliases=['input_id']),
        name=dict(type='str', aliases=['input_name']),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[('id', 'input_id', 'name', 'input_name')]
    )

    # Extract module arguments
    input_id = get_arg('id', module.params, argument_spec)
    input_name = get_arg('name', module.params, argument_spec)

    # Initialize the manager
    manager = MediaLiveInputGetter(module)

    # Find the input by ID or name
    if input_id:
        manager.get_input_by_id(input_id)
    elif input_name:
        manager.find_input_by_name(input_name)
        input_id = manager.input.get('input_id')

    module.exit_json(changed=False, input=manager.input)

if __name__ == '__main__':
    main()
