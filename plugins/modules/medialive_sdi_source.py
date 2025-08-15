#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: medialive_sdi_source
version_added: 10.1.0
short_description: Manage AWS MediaLive Anywhere SDI sources
description:
  - A module for creating, updating and deleting AWS MediaLive Anywhere SDI sources.
  - This module requires boto3 >= 1.37.34.
author:
  - "Brenton Buxell (@buxell)"
options:
  id:
    description:
      - The ID of the SDI source.
    required: false
    type: str
    aliases: ['sdi_source_id']
  name:
    description:
      - The name of the SDI source.
    required: false
    type: str
    aliases: ['sdi_source_name']
  state:
    description:
      - Create/update or remove the SDI source.
    required: false
    choices: ['present', 'absent']
    default: 'present'
    type: str
  mode:
    description:
      - Applies only if the type is 'QUAD'
      - Specify the mode for handling the quad-link signal, 'QUADRANT' or 'INTERLEAVE'
    type: str
    required: false
    choices: ['QUADRANT', 'INTERLEAVE']
  type:
    description:
      - Specify the type of the SDI source
      - SINGLE, the source is a single-link source
      - QUAD, the source is one part of a quad-link source
      - Defaults to 'SINGLE' when creating a new SDI source
    default: 'SINGLE'
    type: str
    required: false
    choices: ['SINGLE', 'QUAD']

extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
- name: Create a MediaLive Anywhere SDI source
  community.aws.medialive_sdi_source:
    name: 'ExampleSdiSource'
    state: present
    type: 'QUAD'
    mode: 'INTERLEAVE'

- name: Delete a MediaLive Anywhere SDI source
  community.aws.medialive_sdi_source:
    name: 'ExampleSdiSource'
    state: absent
"""

RETURN = r"""
changed:
  description: if a MediaLive SDI Source has been created, updated or deleted
  returned: always
  type: bool
  sample:
    changed: true
sdi_source:
  description: The details of the SDI source
  returned: success
  type: dict
  contains:
    arn:
      description: The ARN of the SDI source.
      type: str
      returned: success
      example: "arn:aws:medialive:us-east-1:123456789012:sdiSource/123456"
    id:
      description: The ID of the SDI source
      type: str
      returned: success
      example: "123456"
    inputs:
      description: The list of inputs that are currently using this SDI source
      type: list
      elements: str
      returned: success
      example: ["Input1", "Input2"]
    mode:
      description: Applies only if the type is QUAD. The mode for handling the quad-link signal QUADRANT or INTERLEAVE
      type: str
      returned: success
      example: "QUADRANT"
    name:
      description: The name of the SDI source
      type: str
      returned: success
      example: "ExampleSdiSource"
    state:
      description: The state of the SDI source. Either 'IDLE', 'IN_USE' or 'DELETED'
      type: str
      returned: success
      example: "IN_USE"
    type:
      description: The type of the SDI source
      type: str
      returned: success
      example: "SINGLE"
"""

import uuid
from typing import Dict

try:
    from botocore.exceptions import ClientError, BotoCoreError
except ImportError:
    pass # caught by AnsibleAWSModule

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict, snake_dict_to_camel_dict, recursive_diff
from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.botocore import is_boto3_error_code
from ansible_collections.community.aws.plugins.module_utils.medialive import MedialiveAnsibleAWSError


class MediaLiveSdiSourceManager:
    """Manage AWS MediaLive Anywhere SDI sources"""

    def __init__(self, module: AnsibleAWSModule):
        """
        Initialize the MediaLiveSdiSourceManager

        Args:
            module: AnsibleAWSModule instance
        """
        self.module = module
        self.client = module.client('medialive')
        self._sdi_source = {}
        self.changed = False

    @property
    def sdi_source(self):
        return self._sdi_source

    @sdi_source.setter
    def sdi_source(self, sdi_source: Dict):
        sdi_source = camel_dict_to_snake_dict(sdi_source)
        if sdi_source.get('response_metadata'):
            del sdi_source['response_metadata']

        # Handle nested sdi_source
        if sdi_source.get('sdi_source'):
            sdi_source = sdi_source.get('sdi_source') # type: ignore

        if sdi_source.get('id'):
            sdi_source['sdi_source_id'] = sdi_source.get('id')
            del sdi_source['id']
        self._sdi_source = sdi_source

    def do_create_sdi_source(self, params):
        """
        Create a new MediaLive SDI source
        
        Args:
            params: Parameters for SDI source creation
        """
        allowed_params = ['name', 'type', 'mode']
        required_params = ['name', 'type']

        for param in required_params:
            if not params.get(param):
                raise MedialiveAnsibleAWSError(message=f'The {param} parameter is required when creating a new SDI source')

        create_params = { k: v for k, v in params.items() if k in allowed_params and v }
        create_params = snake_dict_to_camel_dict(create_params, capitalize_first=True)

        try:
            response = self.client.create_sdi_source(**create_params)  # type: ignore
            self.sdi_source = response
            self.changed = True
        except (ClientError, BotoCoreError) as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message='Unable to create Medialive SDI Source',
                exception=e
            )

    def do_update_sdi_source(self, params):
        """
        Update a new MediaLive SDI source
        
        Args:
            params: Parameters for SDI source update
        """
        if not params.get('sdi_source_id'):
            raise MedialiveAnsibleAWSError(message='The sdi_source_id parameter is required during SDI source update.')

        allowed_params = ['sdi_source_id', 'name', 'mode', 'type']

        # Make sure current_params is always a subset of update_params, so we don't update unnecessarily
        current_params = {
            k: v for k, v in self.sdi_source.items()
            if k in allowed_params and k in params and params[k]
        }
        update_params = { k: v for k, v in params.items() if k in allowed_params and v }

        # Short circuit
        if not recursive_diff(current_params, update_params):
            return

        update_params = snake_dict_to_camel_dict(update_params, capitalize_first=True)

        try:
            response = self.client.update_sdi_source(**update_params)  # type: ignore
            self.sdi_source = response
            self.changed = True
        except (ClientError, BotoCoreError) as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message='Unable to update Medialive SDI Source',
                exception=e
            )

    def get_sdi_source_by_name(self, name: str):
        """
        Find an SDI source by name

        Args:
            name: The name of the SDI source to find
        """
        try:
            paginator = self.client.get_paginator('list_sdi_sources')  # type: ignore
            found = []
            for page in paginator.paginate():
                for sdi_source in page.get('SdiSources', []):
                    if sdi_source.get('Name') == name:
                        found.append(sdi_source.get('Id'))
            if len(found) > 1:
                raise MedialiveAnsibleAWSError(
                    message='Found more than one Medialive SDI Sources under the same name'
                )
            elif len(found) == 1:
                self.get_sdi_source_by_id(found[0])

        except (ClientError, BotoCoreError) as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message='Unable to get Medialive SDI Source',
                exception=e
            )

    def get_sdi_source_by_id(self, sdi_source_id: str):
        """
        Get an SDI source by ID

        Args:
            sdi_source_id: The ID of the SDI source to retrieve
        """
        try:
            self.sdi_source = self.client.describe_sdi_source(SdiSourceId=sdi_source_id) # type: ignore
            return True
        except is_boto3_error_code('ResourceNotFoundException'):
            self.sdi_source = {}

    def delete_sdi_source_by_id(self, sdi_source_id: str):
        """
        Delete a MediaLive SDI source
        
        Args:
            sdi_source_id: ID of the SDI source to delete
        """
        try:
            self.sdi_source = self.client.delete_sdi_source(SdiSourceId=sdi_source_id)  # type: ignore
            self.changed = True
        except is_boto3_error_code('ResourceNotFoundException'):
            self.sdi_source = {}
        except (ClientError, BotoCoreError) as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message='Unable to delete Medialive SDI source',
                exception=e
            )


def main():
    """Main entry point for the module"""
    argument_spec = dict(
        id=dict(type='str', required=False, aliases=['sdi_source_id']),
        name=dict(type='str', required=False, aliases=['sdi_source_name']),
        state=dict(type='str', default='present', choices=['present', 'absent']),
        type=dict(type='str', required=False, choices=['SINGLE', 'QUAD']),
        mode=dict(type='str', required=False, choices=['QUADRANT', 'INTERLEAVE'])
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    # Extract module parameters
    sdi_source_id = module.params.get('id')
    sdi_source_name = module.params.get('name')
    state = module.params.get('state')
    source_type = module.params.get('type')
    mode = module.params.get('mode')

    # Initialize the manager
    manager = MediaLiveSdiSourceManager(module)

    # Find the SDI source by ID or name
    # Update manager.sdi_source with the details
    if sdi_source_id:
        manager.get_sdi_source_by_id(sdi_source_id)
    elif sdi_source_name:
        manager.get_sdi_source_by_name(sdi_source_name)
        sdi_source_id = manager.sdi_source.get('sdi_source_id')

    # Do nothing in check mode
    if module.check_mode:
        module.exit_json(changed=True)

    # Handle present state
    if state == 'present':

        # Case update
        if manager.sdi_source:
            update_params = {
                'name': sdi_source_name,
                'sdi_source_id': sdi_source_id,
                'mode': mode,
                'type': source_type
            }
            manager.do_update_sdi_source(update_params)

        # Case create
        else:
            if not source_type:
                source_type = 'SINGLE'
            create_params = {
                'mode': mode,
                'name': sdi_source_name,
                'request_id': str(uuid.uuid4()),
                'type': source_type
            }

            manager.do_create_sdi_source(create_params)

    # Handle absent state
    elif state == 'absent':
        if manager.sdi_source and manager.sdi_source.get('state') != 'DELETED':
            # SDI source exists, delete it
            sdi_source_id = manager.sdi_source.get('sdi_source_id')
            manager.delete_sdi_source_by_id(sdi_source_id) # type: ignore

    module.exit_json(changed=manager.changed, sdi_source=manager.sdi_source)

if __name__ == '__main__':
    main()
