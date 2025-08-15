#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
module: medialive_input
short_description: Manage AWS MediaLive Anywhere inputs
version_added: 10.1.0
description:
  - A module for creating, updating and deleting AWS MediaLive inputs.
  - Requires boto3 >= 1.37.34
author:
  - Sergey Papyan (@r363x)
options:
  name:
    description:
      - Name of the input
      - Mutually exclusive with O(id)
    type: str
  id:
    description:
      - ID of the input
      - Mutually exclusive with O(name)
    type: str
  destinations:
    description:
      - A list of destination settings for PUSH type inputs
      - Required if O(type=UDP_PUSH)
      - Required if O(type=RTP_PUSH)
      - Required if O(type=RTMP_PUSH)
    type: list
    elements: dict
    suboptions:
      stream_name:
        description:
          - A unique name for the location the RTMP stream is being pushed to
        required: true
        type: str
      network:
        description:
          - The ID of the attached network
          - Required if O(input_network_location=ON_PREMISES)
        type: str
      network_routes:
        description:
          - The route of the input on the customer local network
          - Required if O(input_network_location=ON_PREMISES)
        type: list
        elements: dict
        suboptions:
          cidr:
            description:
              - The CIDR of the route
            required: true
            type: str
          gateway:
            description:
              - An optional gateway for the route
            type: str
      static_ip_address:
        description:
          - IP address of the input on the customer local network
          - Optional if O(input_network_location=ON_PREMISES)
        type: str
  input_devices:
    description:
      - Settings for the input devices
      - Required if O(type=INPUT_DEVICE)
    type: list
    elements: dict
    suboptions:
      id:
        description:
          - The unique ID for the device
        type: str
        required: true
  input_security_groups:
    description:
      - A list of security groups referenced by IDs to attach to the input
    type: list
    elements: str
  media_connect_flows:
    description:
      - A list of the MediaConnect Flows that you want to use in this input
      - You can specify as few as one Flow and presently, as many as two
      - |
        The only requirement is when you have more than one is that
        each Flow is in a separate Availability Zone as this ensures
        your EML input is redundant to AZ issues.
      - Required if O(type=MEDIACONNECT)
    type: list
    elements: dict
    suboptions:
      flow_arn:
        description:
          - The ARN of the MediaConnect Flow that you want to use as a source
        type: str
        required: true
  role_arn:
    description:
      - The Amazon Resource Name (ARN) of the role this input assumes during and after creation
      - Required if O(vpc)
    type: str
  sources:
    description:
      - The source URLs for PULL type inputs
      - Two sources must be provided
      - If identical, the input_class of the resulting Input will be SINGLE_PIPELINE
      - If not idential, the input_class of the resulting Input will be STANDARD
      - Required if O(type=RTMP_PULL)
      - Required if O(type=URL_PULL)
      - Required if O(type=MP4_FILE)
      - Required if O(type=TS_FILE)
    type: list
    elements: dict
    suboptions:
      password_param:
        description:
          - The key used to extract the password from SSM Parameter store
        type: str
      url:
        description:
          - This represents the customer’s source URL where stream is pulled from
        required: true
        type: str
      username:
        description:
          - The username for the input source
        type: str
  type:
    description:
      - The type of input to create
      - Required if O(state=present)
    type: str
    choices:
      - UDP_PUSH
      - RTP_PUSH
      - RTMP_PUSH
      - RTMP_PULL
      - URL_PULL
      - MP4_FILE
      - MEDIACONNECT
      - INPUT_DEVICE
      - AWS_CDI
      - TS_FILE
      - SRT_CALLER
      - MULTICAST
      - SMPTE_2110_RECEIVER_GROUP
      - SDI
  vpc:
    description:
      - Settings for a private VPC Input
      - When this property is specified, the input destination addresses will be created in a VPC rather than with public Internet addresses
      - Mutually exclusive with O(input_security_groups)
    type: dict
    suboptions:
      security_group_ids:
        description:
          - A list of up to 5 EC2 VPC security group IDs to attach to the Input VPC network interfaces
          - If none are specified then the VPC default security group will be used
        type: list
        elements: str
      subnet_ids:
        description:
          - A list of 2 VPC subnet IDs from the same VPC
          - Subnet IDs must be mapped to two unique availability zones (AZ)
        type: list
        required: true
        elements: str
  srt_settings:
    description:
      - The settings associated with an SRT input
    type: dict
    suboptions:
      srt_caller_sources:
        description:
          - A list of connection configurations for sources that use SRT as the connection protocol
          - In terms of establishing the connection, MediaLive is always the caller and the upstream system is always the listener
          - In terms of transmission of the source content, MediaLive is always the receiver and the upstream system is always the sender
        type: list
        elements: dict
        suboptions:
          decryption:
            description:
              - Decryption configuration
              - Required only if the content is encrypted
            type: dict
            suboptions:
              algorithm:
                description:
                  - The algorithm used to encrypt content
                type: str
              passphrase_secret_arn:
                description:
                  - The ARN for the secret in Secrets Manager
                  - The secret holds the passphrase that MediaLive will use to decrypt the source content
                  - The secret must be created in advance
                type: str
          minimum_latency:
            description:
              - The preferred latency (in milliseconds) for implementing packet loss and recovery
              - Packet recovery is a key feature of SRT
              - Obtain this value from the operator at the upstream system
            type: int
          srt_listener_address:
            description:
              - The IP address at the upstream system (the listener) that MediaLive (the caller) will connect to
            type: str
          srt_listener_port:
            description:
              - The port at the upstream system (the listener) that MediaLive (the caller) will connect to
            type: str
          stream_id:
            description:
              - |
                This value is required if the upstream system uses this identifier because without it,
                the SRT handshake between MediaLive (the caller) and the upstream system (the listener) might fail
            type: str
  input_network_location:
    description:
      - The location of this input
      - AWS for an input existing in the AWS Cloud
      - ON_PREMISES for an input in a customer network
      - Required if O(type=RTP)
      - Required if O(type=RTMP_PUSH)
      - Must be AWS if O(type=URL_PULL)
      - Must be ON_PREMISES if O(type=SDI)
    type: str
    choices: ['AWS', 'ON_PREMISES']
  multicast_settings:
    description:
      - Multicast Input settings
      - Required if O(type=MULTICAST)
    type: dict
    suboptions:
      sources:
        description:
          - List of pairs of multicast urls and source ip addresses that make up a multicast source
        type: list
        elements: dict
        suboptions:
          source_ip:
            description:
              - This represents the ip address of the device sending the multicast stream
            type: str
          url:
            description:
              - This represents the ip address of the device sending the multicast stream
            type: str
            required: true
  smpte_2110_receiver_group_settings:
    description:
      - Settings to identify the stream sources
      - Required if O(type=SMPTE_2110_RECEIVER_GROUP)
    type: dict
    suboptions:
      smpte_2110_receiver_groups:
        description:
          - List of receiver groups
          - A receiver group is a collection of video, audio, and ancillary streams that you want to group together and attach to one input
        type: list
        elements: dict
        suboptions:
          sdp_settings:
            description:
              - The single dict of settings that identify the video, audio, and ancillary streams for this receiver group
            type: dict
            suboptions:
              ancillary_sdps:
                description:
                  - A list of input SDP locations
                  - Each item in the list specifies the SDP file and index for one ancillary SMPTE 2110 stream
                  - Each stream encapsulates one captions stream (out of any number you can include) or the single SCTE 35 stream that you can include
                type: list
                elements: dict
                suboptions:
                  media_index:
                    description:
                      - The index of the media stream in the SDP file for one SMPTE 2110 stream
                    type: int
                  sdp_url:
                    description:
                      - The URL of the SDP file for one SMPTE 2110 stream
                    type: str
              audio_sdps:
                description:
                  - A list of input SDP locations
                  - Each item in the list specifies the SDP file and index for one audio SMPTE 2110 stream in a receiver group
                type: list
                elements: dict
                suboptions:
                  media_index:
                    description:
                      - The index of the media stream in the SDP file for one SMPTE 2110 stream
                    type: int
                  sdp_url:
                    description:
                      - The URL of the SDP file for one SMPTE 2110 stream
                    type: str
              video_sdp:
                description:
                  - A dict that specifies the SDP file and index for the single video SMPTE 2110 stream for this 2110 input
                type: dict
                suboptions:
                  media_index:
                    description:
                      - The index of the media stream in the SDP file for one SMPTE 2110 stream
                    type: int
                  sdp_url:
                    description:
                      - The URL of the SDP file for one SMPTE 2110 stream
                    type: str
  sdi_sources:
    description:
      - SDI Sources for this Input
      - Must contain a single item - the ID of the SDI source
      - Required if O(type=SDI)
    type: list
    elements: str
  state:
    description:
      - Create/update or remove the input
    choices: ['present', 'absent']
    default: 'present'
    type: str
  wait:
    description:
      - Whether to wait for the input to reach the desired state
      - When I(state=present), wait for the input to reach the DETACHED state
      - When I(state=absent), wait for the input to reach the DELETED state
    type: bool
    default: true
  wait_timeout:
    description:
      - The maximum time in seconds to wait for the input to reach the desired state
      - Defaults to 60 seconds
    type: int
    default: 60

extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
  - amazon.aws.tags
"""

EXAMPLES = r"""
"""

RETURN = r"""
"""

from typing import Dict, List, Literal

try:
    from botocore.exceptions import WaiterError, ClientError, BotoCoreError
except ImportError:
    pass # caught by AnsibleAWSModule

from ansible.module_utils.common.dict_transformations import snake_dict_to_camel_dict, camel_dict_to_snake_dict, recursive_diff
from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.botocore import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.tagging import compare_aws_tags
from ansible_collections.community.aws.plugins.module_utils.medialive import MedialiveAnsibleAWSError


class MediaLiveInputManager:
    """Manage AWS MediaLive Anywhere inputs"""

    def __init__(self, module: AnsibleAWSModule):
        """
        Initialize the MediaLiveInputManager

        Args:
            module: AnsibleAWSModule instance
        """
        self.module = module
        self.client = self.module.client('medialive')
        self._input = {}
        self.changed = False

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
            del input['response_metadata']
        if input.get('id'):
            input['input_id'] = input.get('id')
            del input['id']
        if tags:
            input['tags'] = tags
        self._input = input

    def validate_sdi_source(self, sources: List[str], check_use=False):
        """
        Validates the following:
            * the list of sdi_sources provided by the user contains only a single item
            * the SDI Source exists
            * if check_use=True then makes sure the state of the SDI Source is not IN_USE
        """
        # Though still undocumented, if you pass more than one SDI Input Source ID
        # to the CreateInput API you get the following BadRequest error
        # "The SDI sources for an SDI input must specify exactly one SDI source"
        if len(sources) != 1:
            raise MedialiveAnsibleAWSError(message='The sdi_sources list must contain a single element')

        # Make sure the SDI source exists and is in IDLE state
        try:
            response = self.client.describe_sdi_source(SdiSourceId=sources[0]) # type: ignore
            if check_use and response['SdiSource']['State'] == 'IN_USE':
                raise MedialiveAnsibleAWSError(message='The provided sdi_source is already in use')

        except is_boto3_error_code('ResourceNotFoundException'):
            raise MedialiveAnsibleAWSError(message='The provided sdi_source does not exist')

    def get_input_by_name(self, name: str):
        """
        Find a input by name

        Args:
            name: The name of the input to find
        """

        try:
            paginator = self.client.get_paginator('list_inputs')  # type: ignore
            for page in paginator.paginate():
                for input in page.get('Inputs', []):
                    if input.get('Name') == name:
                        self.get_input_by_id(input.get('Id'))
                        return
        except (ClientError, BotoCoreError) as e: # type: ignore
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
        except (ClientError, BotoCoreError) as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message='Unable to get Medialive Input',
                exception=e
            )

    def wait_for(self,
        want: Literal['input_attached','input_deleted','input_detached'],
        input_id: str,
        wait_timeout: int = 60):
        """
        Wait for an Input to reach the wanted state

        Args:
            want: the waiter to invoke
            input_id: the ID of the Input
            wait_timeout: the maximum amount of time to wait in seconds (default: 60)
        """

        try:
            waiter = self.client.get_waiter(want) # type: ignore
            config = {
                'Delay': min(5, wait_timeout),
                'MaxAttempts': wait_timeout // 5
            }
            waiter.wait(
                InputId=input_id,
                WaiterConfig=config
            )
        except WaiterError as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message=f'Timeout waiting for Input {input_id}',
                exception=e
            )

    def do_create_input(self, params):
        """
        Create a new MediaLive input
        
        Args:
            params: Parameters for input creation
        """
        allowed_params = [
            'destinations',
            'input_devices',
            'input_security_groups',
            'media_connect_flows',
            'name',
            'role_arn',
            'sources',
            'type',
            'vpc',
            'srt_settings',
            'input_network_location',
            'multicast_settings',
            'smpte_2110_receiver_group_settings',
            'sdi_sources',
            'tags'
        ]

        create_params = { k: v for k, v in params.items() if k in allowed_params and v }

        # Do some extra validation
        sdi_sources = create_params.get('sdi_sources')
        if sdi_sources:
            self.validate_sdi_source(sdi_sources)

        tags = create_params.get('tags') # To preserve case in tag keys
        create_params = snake_dict_to_camel_dict(create_params, capitalize_first=True)

        if tags and create_params:
            create_params['Tags'] = tags

        try:
            self.input = self.client.create_input(**create_params)['Input']  # type: ignore
            self.changed = True
        except (ClientError, BotoCoreError) as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message='Unable to create Medialive Input',
                exception=e
            )

    def do_update_input(self, params):
        """
        Update a new MediaLive input
        
        Args:
            params: Parameters for input update
        """
        if not params.get('input_id'):
            raise MedialiveAnsibleAWSError(message='The input_id parameter is required during input update.')

        tags = params.get('tags')
        purge_tags = params.get('purge_tags')
        del params['tags']
        del params['purge_tags']

        allowed_params = [
            'destinations',
            'input_devices',
            'input_id',
            'input_security_groups',
            'media_connect_flows',
            'name',
            'role_arn',
            'sources',
            'srt_settings',
            'multicast_settings',
            'smpte_2110_receiver_group_settings',
            'sdi_sources'
        ]

        update_params = { k: v for k, v in params.items() if k in allowed_params and v }

        current_params = {}
        for k, v in self.input.items():
            if k in allowed_params and k in update_params:
                current_params[k] = v

        try:
            if recursive_diff(current_params, update_params):
                update_params = snake_dict_to_camel_dict(update_params, capitalize_first=True)
                self.input = self.client.update_input(**update_params)['Input']  # type: ignore
                self.changed = True
            if tags and self._update_tags(tags, purge_tags):
                self.input = self.get_input_by_id(self.input['input_id']) # type: ignore
                self.changed = True

        except (ClientError, BotoCoreError) as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message='Unable to update Medialive Input',
                exception=e
            )

    def delete_input(self, input_id: str):
        """
        Delete a MediaLive input
        
        Args:
            input_id: ID of the input to delete
        """
        try:
            self.client.delete_input(InputId=input_id)  # type: ignore
            self.input = {}
            self.changed = True
        except is_boto3_error_code('ResourceNotFoundException'):
            self.input = {}
        except (ClientError, BotoCoreError) as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message='Unable to delete Medialive Input',
                exception=e
            )

    def _update_tags(self, tags: dict, purge: bool) -> bool:
        """
        Takes care of updating Input tags

        Args:
            tags: a dict of tags supplied by the user
            purge: whether or not to delete existing tags that aren't in the tags dict
        Returns:
            True if tags were updated, otherwise False
        """

        # Short-circuit
        if self.module.check_mode:
            return False

        to_add, to_delete = compare_aws_tags(self.input['tags'], tags, purge)

        if not any((to_add, to_delete)):
            return False

        try:
            if to_add:
                self.client.create_tags(ResourceArn=self.input['arn'], Tags=to_add) # type: ignore
            if to_delete:
                self.client.delete_tags(ResourceArn=self.input['arn'], TagKeys=to_delete) # type: ignore
        except (ClientError, BotoCoreError) as e: # type: ignore
            raise MedialiveAnsibleAWSError(
                message='Unable to update MediaLive Input resource Tags',
                exception=e
            )

        return True


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
        state=dict(type='str', default='present', choices=['present', 'absent']),
        request_id=dict(type='str'),
        destinations=dict(
            type='list',
            elements='dict',
            options=dict(
                stream_name=dict(type='str', required=True),
                network=dict(type='str'),
                network_routes=dict(
                    type='list',
                    elements='dict',
                    options=dict(
                        cidr=dict(type='str', required=True),
                        gateway=dict(type='str')
                    )
                ),
                static_ip_address=dict(type='str') # TODO: validate in code that input_network_location is ON_PREMISES

            ),
            required_if=[('input_network_location', 'ON_PREMISES', ['network', 'network_routes'])]
        ),
        input_devices=dict(
            type='list',
            elements='dict',
            options=dict(
                id=dict(type='str', required=True)
            )
        ),
        input_security_groups=dict(type='list', elements='str'),
        media_connect_flows=dict(
            type='list',
            elements='dict',
            options=dict(
                flow_arn=dict(type='str', required=True)
            )
        ),
        role_arn=dict(type='str'),
        sources=dict(
            type='list',
            elements='dict',
            options=dict(
                password_param=dict(type='str'),
                url=dict(type='str', required=True),
                username=dict(type='str')
            )
        ),
        type=dict(
            type='str',
            choices=[
                'UDP_PUSH',
                'RTP_PUSH',
                'RTMP_PUSH',
                'RTMP_PULL',
                'URL_PULL',
                'MP4_FILE',
                'MEDIACONNECT',
                'INPUT_DEVICE',
                'AWS_CDI',
                'TS_FILE',
                'SRT_CALLER',
                'MULTICAST',
                'SMPTE_2110_RECEIVER_GROUP',
                'SDI',
            ]
        ),
        vpc=dict(
            type='dict',
            options=dict(
                security_group_ids=dict(type='list', elements='str'),
                subnet_ids=dict(type='list', elements='str', required=True)
            )
        ),
        srt_settings=dict(
            type='dict',
            options=dict(
                srt_caller_sources=dict(
                    type='list',
                    elements='dict',
                    options=dict(
                        decryption=dict(
                            type='dict',
                            options=dict(
                                algorithm=dict(type='str'),
                                passphrase_secret_arn=dict(type='str')
                            )
                        ),
                        minimum_latency=dict(type='int'),
                        srt_listener_address=dict(type='str'),
                        srt_listener_port=dict(type='str'),
                        stream_id=dict(type='str')
                    )
                )
            )
        ),
        input_network_location=dict(
            type='str',
            choices=['AWS', 'ON_PREMISES'] # TODO: validate in code: Must be AWS if O(type=URL_PULL), ON_PREMISES if O(type=SDI)
        ),
        multicast_settings=dict(
            type='dict',
            options=dict(
                sources=dict(
                    type='list',
                    elements='dict',
                    options=dict(
                        type='dict',
                        options=dict(
                            source_ip=dict(type='str'),
                            url=dict(type='str', required=True)
                        )
                    )
                )
            )
        ),
        smpte_2110_receiver_group_settings=dict(
            type='dict',
            options=dict(
                smpte_2110_receiver_groups=dict(
                    type='list',
                    elements='dict',
                    options=dict(
                        sdp_settings=dict(
                            type='dict',
                            options=dict(
                                ancillary_sdps=dict(
                                    type='list',
                                    elements='dict',
                                    options=dict(
                                        meta_index=dict(type='int'),
                                        sdp_url=dict(type='str')
                                    )
                                ),
                                audio_sdps=dict(
                                    type='list',
                                    elements='dict',
                                    options=dict(
                                        meta_index=dict(type='int'),
                                        sdp_url=dict(type='str')
                                    )
                                ),
                                video_sdp=dict(
                                    type='list',
                                    elements='dict',
                                    options=dict(
                                        meta_index=dict(type='int'),
                                        sdp_url=dict(type='str')
                                    )
                                )
                            )
                        )
                    )
                )
            )
        ),
        sdi_sources=dict(
            type='list',
            elements='str'
        ),
        tags=dict(type='dict'),
        purge_tags=dict(type="bool", default=True),
        wait=dict(type='bool', default=True),
        wait_timeout=dict(type='int', default=60),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[
            ('id', 'input_id', 'name', 'input_name'),
            ('vpc', 'input_security_groups')
        ],
        required_one_of=[('id', 'input_id', 'name', 'input_name')],
        required_if=[
            ('state', 'present', ['type']),
            ('type', 'UDP_PUSH', ['destinations']),
            ('type', 'RTP_PUSH', ['destinations']),
            ('type', 'RTMP_PUSH', ['destinations', 'input_network_location']),
            ('type', 'INPUT_DEVICE', ['input_devices']),
            ('type', 'MEDIACONNECT', ['media_connect_flows']),
            ('type', 'RTMP_PULL', ['sources']),
            ('type', 'URL_PULL', ['sources', 'input_network_location']),
            ('type', 'MP4_FILE', ['sources']),
            ('type', 'TS_FILE', ['sources']),
            ('type', 'RTP', ['input_network_location']),
            ('type', 'SDI', ['input_network_location', 'sdi_sources']),
            ('type', 'MULTICAST', ['multicast_settings']),
            ('type', 'SMPTE_2110_RECEIVER_GROUP', ['smpte_2110_receiver_group_settings']),
        ],
        required_by={
            'vpc': ('role_arn')
        }
    )

    # Extract module arguments
    input_id = get_arg('id', module.params, argument_spec)
    input_name = get_arg('name', module.params, argument_spec)
    state = get_arg('state', module.params, argument_spec)
    destinations = get_arg('destinations', module.params, argument_spec)
    input_devices = get_arg('input_devices', module.params, argument_spec)
    input_security_groups = get_arg('input_security_groups', module.params, argument_spec)
    media_connect_flows = get_arg('media_connect_flows', module.params, argument_spec)
    role_arn = get_arg('role_arn', module.params, argument_spec)
    sources = get_arg('sources', module.params, argument_spec)
    input_type = get_arg('type', module.params, argument_spec)
    vpc = get_arg('vpc', module.params, argument_spec)
    srt_settings = get_arg('srt_settings', module.params, argument_spec)
    input_network_location = get_arg('input_network_location', module.params, argument_spec)
    multicast_settings = get_arg('multicast_settings', module.params, argument_spec)
    smpte_2110_receiver_group_settings = get_arg('smpte_2110_receiver_group_settings', module.params, argument_spec)
    sdi_sources = get_arg('sdi_sources', module.params, argument_spec)
    tags = get_arg('tags', module.params, argument_spec)
    purge_tags = get_arg('purge_tags', module.params, argument_spec)
    wait = get_arg('wait', module.params, argument_spec)
    wait_timeout = get_arg('wait_timeout', module.params, argument_spec)

    # Initialize the manager
    manager = MediaLiveInputManager(module)

    # Find the input by ID or name
    if input_id:
        manager.get_input_by_id(input_id)
    elif input_name:
        manager.get_input_by_name(input_name)
        input_id = manager.input.get('input_id')

    # Do nothing in check mode
    if module.check_mode:
        module.exit_json(changed=True)

    # Handle present state
    if state == 'present':

        # Case update
        if manager.input:

            update_params = {
                'destinations': destinations,
                'input_devices': input_devices,
                'input_id': input_id,
                'input_security_groups': input_security_groups,
                'media_connect_flows': media_connect_flows,
                'name': input_name,
                'role_arn': role_arn,
                'sources': sources,
                'srt_settings': srt_settings,
                'multicast_settings': multicast_settings,
                'smpte_2110_receiver_group_settings': smpte_2110_receiver_group_settings,
                'sdi_sources': sdi_sources,
                'tags': tags,
                'purge_tags': purge_tags
            }

            manager.do_update_input(update_params)

        # Case create
        else:
            create_params = {
                'destinations': destinations,
                'input_devices': input_devices,
                'input_security_groups': input_security_groups,
                'media_connect_flows': media_connect_flows,
                'name': input_name,
                'role_arn': role_arn,
                'sources': sources,
                'type': input_type,
                'vpc': vpc,
                'srt_settings': srt_settings,
                'input_network_location': input_network_location,
                'multicast_settings': multicast_settings,
                'smpte_2110_receiver_group_settings': smpte_2110_receiver_group_settings,
                'sdi_sources': sdi_sources,
                'tags': tags
            }
            
            manager.do_create_input(create_params)
            input_id = manager.input.get('input_id')

            # Wait for the input to be created
            if wait and input_id:
                manager.wait_for('input_detached', input_id, wait_timeout) # type: ignore
                manager.get_input_by_id(input_id)
            
    # Handle absent state
    elif state == 'absent':
        if manager.input:
            # Network exists, delete it
            input_id = manager.input.get('input_id')
            manager.delete_input(input_id) # type: ignore

            # Wait for the input to be deleted
            if wait and input_id:
                manager.wait_for('input_deleted', input_id, wait_timeout) # type: ignore

    module.exit_json(changed=manager.changed, input=manager.input)

if __name__ == '__main__':
    main()
