#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: medialive_sdi_source_info
version_added: 10.1.0
short_description: Gather AWS MediaLive Anywhere SDI source info
description:
  - Get details about a AWS MediaLive Anywhere SDI source.
  - This module requires boto3 >= 1.37.34.
author:
  - "Brenton Buxell (@bbuxell)"
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

extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
  - amazon.aws.tags
"""

EXAMPLES = r"""
- name: Create a MediaLive Anywhere SDI source by name
  community.aws.medialive_sdi_source_info:
    name: 'ExampleSdiSource'
  register: found_source
  
- name: Create a MediaLive Anywhere SDI source by ID
  community.aws.medialive_sdi_source_info:
    id: '1234567'
  register: found_source
"""

RETURN = r"""
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
      description: The state of the SDI source
      type: str
      returned: success
      example: "IN_USE"
    type:
      description: The type of the SDI source
      type: str
      returned: success
      example: "SINGLE"
"""

from typing import Dict

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict
from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.botocore import is_boto3_error_code
from ansible_collections.community.aws.plugins.module_utils.medialive import MedialiveAnsibleAWSError


class MediaLiveSdiSourceGetter:
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

def main():
    """Main entry point for the module"""
    argument_spec = dict(
        id=dict(type='str', required=False, aliases=['sdi_source_id']),
        name=dict(type='str', required=False, aliases=['sdi_source_name'])
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    # Do nothing in check mode
    if module.check_mode:
        module.exit_json(changed=True)

    # Extract module parameters
    sdi_source_id = module.params.get('id')
    sdi_source_name = module.params.get('name')

    # Initialize the getter
    getter = MediaLiveSdiSourceGetter(module)

    # Find the SDI source by ID or name
    # Update manager.sdi_source with the details
    if sdi_source_id:
        getter.get_sdi_source_by_id(sdi_source_id)
    elif sdi_source_name:
        getter.get_sdi_source_by_name(sdi_source_name)

    module.exit_json(changed=False, sdi_source=getter.sdi_source)

if __name__ == '__main__':
    main()
