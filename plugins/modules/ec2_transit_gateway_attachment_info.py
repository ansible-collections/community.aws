#!/usr/bin/python
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = r'''
module: ec2_transit_gateway_attachment_info
short_description: Gather information about ec2 transit gateway attachments in AWS
version_added: 2.1.0
description:
    - Gather information about ec2 transit gateway attachmentss in AWS
author: "Chris Forkner (@gen2fish)"
options:
  transit_gateway_attachment_ids:
    description:
      - A list of transit gateway attachment IDs to gather information for.
    aliases: [attachment_id]
    type: list
    elements: str
  filters:
    description:
      - A dict of filters to apply. Each dict item consists of a filter key and a filter value.
        See U(https://docs.aws.amazon.com/AWSEC2/latest/APIReference/API_DescribeTransitGatewayAttachments.html) for filters.
    type: dict
extends_documentation_fragment:
- amazon.aws.aws
- amazon.aws.ec2
'''

EXAMPLES = r'''
- name: Gather info about all transit gateway attachments
  community.aws.ec2_transit_gateway_attachment_info:

- name: Gather info about a particular transit gateway attachments using filter transit gateway attachment ID
  community.aws.ec2_transit_gateway_attachment_info:
    filters:
      transit-gateway-id: tgw-02c42332e6b7da829

- name: Gather info about a particular transit gateway attachments using multiple option filters
  community.aws.ec2_transit_gateway_attachment_info:
    filters:
      association.state: associated
      state: available

- name: Gather info about multiple transit gateway attachments using module param
  community.aws.ec2_transit_gateway_attachment_info:
    transit_gateway_attachment_ids:
      - tgw-attach-0d26048d68ce9d462
      - tgw-attach-0726a587e6d7ccf9b
'''

RETURN = r'''
transit_gateway_attachments:
    description: >
        Transit gateway attachments that match the provided filters. Each element consistes of a dict with all the information
        related to that transit gateway attachment.
    returned: on success
    type: complex
    contains:
        association:
            description: The association status of the transit gateway attachment.
            returned: always
            type: complex
            contains:
                state:
                    description: The state of the association.
                    returned: always
                    type: str
                    sample: "associated"
                transit_gateway_route_table_id:
                    description: The ID of the route table for the transit gateway
                    returned: always
                    type: str
                    sample: "tgw-rtb-02e2bdf14e27c0263"
        creation_time:
            description: The creation time.
            returned: always
            type: str
            sample: "2019-02-05T16:19:58+00:00"
        resource_id:
            description: The ID of the AWS resource that the transit gateway attachment is attached to.
            returned: always
            type: str
            sample: "vpc-0791793c6332069d4"
        resource_owner_id:
            description: The AWS account number ID which owns the resource that the transit gateway attachment is attached to.
            returned: always
            type: str
            sample: "1234567654323"
        resource_type:
            description: The resource type that the transit gateway attachment is attached to.
            returned: always
            type: str
            sample: "vpc"
        state:
            description: The state of the transit gateway.
            returned: always
            type: str
            sample: "available"
        tags:
            description: A dict of tags associated with the transit gateway.
            returned: always
            type: dict
            sample: '{
              "Name": "A sample TGW"
              }'
        transit_gateway_attachment_id:
            description: The ID of the transit gateway attachment.
            returned: always
            type: str
            sampe: "tgw-attach-0d26048d68ce9d462"
        transit_gateway_id:
            description: The ID of the transit gateway attached to.
            returned: always
            type: str
            sample: "tgw-02c42332e6b7da829"
        transit_gateway_owner_id:
            description: The AWS account number ID which owns the transit gateway.
            returned: always
            type: str
            sample: "1234567654323"
'''

try:
    import botocore
except ImportError:
    pass  # handled by imported AnsibleAWSModule

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.core import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AWSRetry
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import ansible_dict_to_boto3_filter_list
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import boto3_tag_list_to_ansible_dict


class AnsibleEc2TgwAttachmentInfo(object):

    def __init__(self, module, results):
        self._module = module
        self._results = results
        self._connection = self._module.client('ec2')
        self._check_mode = self._module.check_mode

    @AWSRetry.exponential_backoff()
    def describe_transit_gateway_attachments(self):
        """
        Describe transit gateway attachments.

        module  : AnsibleAWSModule object
        connection  : boto3 client connection object
        """
        # collect parameters
        filters = ansible_dict_to_boto3_filter_list(self._module.params['filters'])
        transit_gateway_attachment_ids = self._module.params['transit_gateway_attachment_ids']

        # init empty list for return vars
        transit_gateway_info = []

        # Get the basic transit gateway info
        try:
            response = self._connection.describe_transit_gateway_attachments(TransitGatewayAttachmentIds=transit_gateway_attachment_ids, Filters=filters)

        except is_boto3_error_code('InvalidTransitGatewayAttachmentID.NotFound'):
            self._results['transit_gateway_attachments'] = []
            return

        vpc_tgw_attachments = []
        peer_tgw_attachments = []

        for tgw_attachment in response['TransitGatewayAttachments']:
            if tgw_attachment['ResourceType'] == 'vpc':
                vpc_tgw_attachments.append(tgw_attachment['TransitGatewayAttachmentId'])
            elif tgw_attachment['ResourceType'] == 'peering':
                peer_tgw_attachments.append(tgw_attachment['TransitGatewayAttachmentId'])
            else:
                transit_gateway_info.append(camel_dict_to_snake_dict(transit_gateway, ignore_list=['Tags']))
                # convert tag list to ansible dict
                transit_gateway_info[-1]['tags'] = boto3_tag_list_to_ansible_dict(transit_gateway.get('Tags', []))


        vpc_response = self._connection.describe_transit_gateway_vpc_attachments(
            TransitGatewayAttachmentIds=vpc_tgw_attachments)
        peer_response = self._connection.describe_transit_gateway_peering_attachments(
            TransitGatewayAttachmentIds=peer_tgw_attachments)

        for tgw_attachment in response['TransitGatewayAttachments']:
            for vpc_attachment in vpc_response['TransitGatewayVpcAttachments']:
                if tgw_attachment['TransitGatewayAttachmentId'] == vpc_attachment['TransitGatewayAttachmentId']:
                    transit_gateway_info.append(camel_dict_to_snake_dict({**vpc_attachment, **tgw_attachment}, ignore_list=['Tags']))
                    # convert tag list to ansible dict
                    transit_gateway_info[-1]['tags'] = boto3_tag_list_to_ansible_dict(vpc_attachment.get('Tags', []))

            for peer_attachment in peer_response['TransitGatewayPeeringAttachments']:
                if tgw_attachment['TransitGatewayAttachmentId'] == peer_attachment['TransitGatewayAttachmentId']:
                    transit_gateway_info.append(camel_dict_to_snake_dict({**peer_attachment, **tgw_attachment}, ignore_list=['Tags']))
                    # convert tag list to ansible dict
                    transit_gateway_info[-1]['tags'] = boto3_tag_list_to_ansible_dict(tgw_attachment.get('Tags', []))

        self._results['transit_gateway_attachments'] = transit_gateway_info
        return


def setup_module_object():
    """
    merge argument spec and create Ansible module object
    :return: Ansible module object
    """

    argument_spec = dict(
        transit_gateway_attachment_ids=dict(type='list', default=[], elements='str', aliases=['attachment_id']),
        filters=dict(type='dict', default={})
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    return module


def main():

    module = setup_module_object()

    results = dict(
        changed=False
    )

    tgwf_manager = AnsibleEc2TgwAttachmentInfo(module=module, results=results)
    try:
        tgwf_manager.describe_transit_gateway_attachments()
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e)

    module.exit_json(**results)


if __name__ == '__main__':
    main()
