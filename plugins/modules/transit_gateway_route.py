#!/usr/bin/python

# Copyright: (c) 2024, Paul Czarkowski <pczarkow@redhat.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: transit_gateway_route

short_description: Creates a transit gateway route

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: |
  Creates a transit gateway route to a specified transit gateway route table.

options:
    destination_cidr_block:
        description: The CIDR range used for destination matches. Routing decisions are based on the most specific match.
        required: true
        type: str
    region:
        description: The AWS region to use.
        required: true
        type: str
    transit_gateway_route_table_id:
        description: The ID of the transit gateway route table.
        required: true
        type: str
    transit_gateway_attachment_id:
        description: The ID of the transit gateway attachment.
        required: true
        type: str
    blackhole:
        description: Indicates whether to drop traffic that matches this route (blackhole). Defaults to false.
        required: false
        type: bool
    tags:
        description: AWS tags
        required: false
        type: list
    state:
        description: present or absent
        required: true
# Specify this value according to your collection
# in format of namespace.collection.doc_fragment_name
extends_documentation_fragment:
  - amazon.aws.common.modules

author:
    - Paul Czarkowski (@paulczar)
'''

EXAMPLES = r'''
# Create a transit gateway route
- name: Create a transit gateway route
    my_namespace.my_collection.transit_gateway_route:
        destination_cidr_block: 0.0.0.0/0
        region: us-east-1
        transit_gateway_route_table_id: tgw-rtb-1234567890
        transit_gateway_attachment_id: tgw-attach-1234567890
        blackhole: false
        state: present
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
routes:
    - destination_cidr_block: 0.0.0.0/0
      region: us-east-1
      transit_gateway_route_table_id: tgw-rtb-1234567890
      transit_gateway_attachment_id: tgw-attach-1234567890
'''

try:
    from botocore.exceptions import BotoCoreError
    from botocore.exceptions import ClientError
except ImportError:
    pass  # Handled by AnsibleAWSModule
from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.amazon.aws.plugins.module_utils.retries import AWSRetry
from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule
from re import sub

def snake_case(s):
  return '_'.join(
    sub('([A-Z][a-z]+)', r' \1',
    sub('([A-Z]+)', r' \1',
    s.replace('-', ' '))).split()).lower()

def process_response(response_in):
    if not response_in:
        return response_in
    return camel_dict_to_snake_dict(response_in)

def get_tgw_rt(connection,tgw_rt_id, tgw_att_id):
    filters = [dict(
        Name = 'attachment.transit-gateway-attachment-id',
        Values = [tgw_att_id]
    )]
    try:
        response = connection.search_transit_gateway_routes(
            TransitGatewayRouteTableId=tgw_rt_id, Filters=filters, MaxResults=5)
    except (BotoCoreError, ClientError) as e:
        return None, e
    tgw = response['Routes']
    return tgw, None

def run_module():
    module_args = dict(
        destination_cidr_block=dict(type='str', required=True),
        region=dict(type='str', required=True),
        transit_gateway_route_table_id=dict(type='str', required=True),
        transit_gateway_attachment_id=dict(type='str', required=True),
        blackhole=dict(type='bool', default=False, required=False),
        # Todo: support dry run
        state=dict(type='str', default='present', choices=['present','absent']),
    )

    module = AnsibleAWSModule(
        argument_spec=module_args,
        supports_check_mode=True
    )

    changed = False

    if module.check_mode:
        module.exit_json(changed=changed, routes=[])

    connection = module.client("ec2",
                    retry_decorator=AWSRetry.jittered_backoff(),
                    region=module.params['region'])

    # check to see if it exists
    response, err = get_tgw_rt(
        connection,
        module.params['transit_gateway_route_table_id'],
        module.params['transit_gateway_attachment_id'])
    if err:
        module.fail_json_aws(err, msg="Failed to check for existing transit gateway route")

    # if it is to be deleted
    if module.params['state'] == "absent":
        if not response:
            module.exit_json(changed=changed, routes=[])
        try:
            _ = connection.delete_transit_gateway_route(
                DestinationCidrBlock=module.params['destination_cidr_block'],
                TransitGatewayRouteTableId=module.params['transit_gateway_route_table_id'],
                # todo DryRun=module.params['string'],
            )
        except (BotoCoreError, ClientError) as e:
            module.fail_json_aws(e, msg="Failed to delete transit gateway route")
        changed = True
        module.exit_json(changed=changed, routes=[])

    if response:
        module.exit_json(changed=changed, routes=process_response(response))

    # create it
    try:
        response = connection.create_transit_gateway_route(
            DestinationCidrBlock=module.params['destination_cidr_block'],
            TransitGatewayRouteTableId=module.params['transit_gateway_route_table_id'],
            TransitGatewayAttachmentId=module.params['transit_gateway_attachment_id'],
            Blackhole=module.params['blackhole'],
            # todo DryRun=module.params['string'],
        )
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg="Unknown error")

    routes = [process_response(response)]
    changed = True
    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json(changed=changed, routes=routes)


def main():
    run_module()


if __name__ == '__main__':
    main()
