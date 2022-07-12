#!/usr/bin/python
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: ec2_vpc_cagw
version_added: 1.0.0
short_description: Manage an AWS VPC Carrier gateway
description:
    - Manage an AWS VPC Carrier gateway
author: "Marco Braga (@mtulio)"
options:
  vpc_id:
    description:
      - The VPC ID for the VPC in which to manage the Carrier Gateway.
    required: true
    type: str
  state:
    description:
      - Create or terminate the CAGW
    default: present
    choices: [ 'present', 'absent' ]
    type: str
notes:
- Support for I(purge_tags) was added in release 1.3.0.
extends_documentation_fragment:
- amazon.aws.aws
- amazon.aws.ec2
- amazon.aws.tags
'''

EXAMPLES = '''
# Note: These examples do not set authentication details, see the AWS Guide for details.

# Ensure that the VPC has an Carrier Gateway.
# The Carrier Gateway ID is can be accessed via {{cagw.carrier_gateway_id}} for use in setting up NATs etc.
- name: Create Carrier gateway
  community.aws.ec2_vpc_cagw:
    vpc_id: vpc-abcdefgh
    state: present
  register: cagw

- name: Create Carrier gateway with tags
  community.aws.ec2_vpc_cagw:
    vpc_id: vpc-abcdefgh
    state: present
    tags:
        Tag1: tag1
        Tag2: tag2
  register: cagw

- name: Delete Carrier gateway
  community.aws.ec2_vpc_cagw:
    state: absent
    vpc_id: vpc-abcdefgh
  register: vpc_cagw_delete
'''

RETURN = '''
changed:
  description: If any changes have been made to the Carrier Gateway.
  type: bool
  returned: always
  sample:
    changed: false
carrier_gateway_id:
  description: The unique identifier for the Carrier Gateway.
  type: str
  returned: I(state=present)
  sample:
    carrier_gateway_id: "cagw-XXXXXXXX"
tags:
  description: The tags associated the Carrier Gateway.
  type: dict
  returned: I(state=present)
  sample:
    tags:
      "Ansible": "Test"
vpc_id:
  description: The VPC ID associated with the Carrier Gateway.
  type: str
  returned: I(state=present)
  sample:
    vpc_id: "vpc-XXXXXXXX"
'''

try:
    import botocore
except ImportError:
    pass  # caught by AnsibleAWSModule

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AWSRetry
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import camel_dict_to_snake_dict
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import ensure_ec2_tags
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import ansible_dict_to_boto3_filter_list
from ansible_collections.amazon.aws.plugins.module_utils.tagging import boto3_tag_list_to_ansible_dict

@AWSRetry.jittered_backoff(retries=10, delay=10)
def describe_cagws_with_backoff(connection, **params):
    paginator = connection.get_paginator('describe_carrier_gateways')
    return paginator.paginate(**params).build_full_result()['CarrierGateways']


class AnsibleEc2Cagw():

    def __init__(self, module, results):
        self._module = module
        self._results = results
        self._connection = self._module.client(
            'ec2', retry_decorator=AWSRetry.jittered_backoff()
        )
        self._check_mode = self._module.check_mode

    def process(self):
        vpc_id = self._module.params.get('vpc_id')
        state = self._module.params.get('state', 'present')
        tags = self._module.params.get('tags')
        purge_tags = self._module.params.get('purge_tags')

        if state == 'present':
            self.ensure_cagw_present(vpc_id, tags, purge_tags)
        elif state == 'absent':
            self.ensure_cagw_absent(vpc_id)

    def get_matching_cagw(self, vpc_id, carrier_gateway_id=None):
        '''
        Returns the carrier gateway found.
            Parameters:
                vpc_id (str): VPC ID
                carrier_gateway_id (str): Carrier Gateway ID, if specified
            Returns:
                cagw (dict): dict of cagw found, None if none found
        '''
        filters = ansible_dict_to_boto3_filter_list({'vpc-id': vpc_id})
        try:
            if not carrier_gateway_id:
                cagws = describe_cagws_with_backoff(self._connection, Filters=filters)
            else:
                cagws = describe_cagws_with_backoff(self._connection, CarrierGatewayIds=[carrier_gateway_id])
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            self._module.fail_json_aws(e)

        cagw = None
        if len(cagws) > 1:
            self._module.fail_json(
                msg='EC2 returned more than one Carrier Gateway for VPC {0}, aborting'
                    .format(vpc_id))
        elif cagws:
            cagw = camel_dict_to_snake_dict(cagws[0])

        return cagw

    @staticmethod
    def get_cagw_info(cagw, vpc_id):
        return {
            'carrier_gateway_id': cagw['carrier_gateway_id'],
            'tags': boto3_tag_list_to_ansible_dict(cagw['tags']),
            'vpc_id': vpc_id
        }

    def ensure_cagw_absent(self, vpc_id):
        cagw = self.get_matching_cagw(vpc_id)
        if cagw is None:
            return self._results

        if self._check_mode:
            self._results['changed'] = True
            return self._results

        try:
            self._results['changed'] = True
            self._connection.delete_carrier_gateway(
                aws_retry=True,
                CarrierGatewayId=cagw['carrier_gateway_id']
            )
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            self._module.fail_json_aws(e, msg="Unable to delete Carrier Gateway")

        return self._results

    def ensure_cagw_present(self, vpc_id, tags, purge_tags):
        cagw = self.get_matching_cagw(vpc_id)

        if cagw is None:
            if self._check_mode:
                self._results['changed'] = True
                self._results['carrier_gateway_id'] = None
                return self._results

            try:
                response = self._connection.create_carrier_gateway(VpcId=vpc_id, aws_retry=True)
                cagw = camel_dict_to_snake_dict(response['CarrierGateway'])
                self._results['changed'] = True
            except botocore.exceptions.WaiterError as e:
                self._module.fail_json_aws(e, msg="No Carrier Gateway exists.")
            except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
                self._module.fail_json_aws(e, msg='Unable to create Carrier Gateway')

        # Modify tags
        self._results['changed'] |= ensure_ec2_tags(
            self._connection, self._module, cagw['carrier_gateway_id'],
            resource_type='carrier-gateway', tags=tags, purge_tags=purge_tags,
            retry_codes='InvalidCarrierGatewayID.NotFound'
        )

        # Update cagw
        cagw = self.get_matching_cagw(vpc_id, carrier_gateway_id=cagw['carrier_gateway_id'])
        cagw_info = self.get_cagw_info(cagw, vpc_id)
        self._results.update(cagw_info)

        return self._results


def main():
    argument_spec = dict(
        carrier_gateway_id=dict(required=False),
        vpc_id=dict(required=False),
        state=dict(default='present', choices=['present', 'absent']),
        tags=dict(required=False, type='dict', aliases=['resource_tags']),
        purge_tags=dict(default=True, type='bool'),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    results = dict(
        changed=False
    )
    cagw_manager = AnsibleEc2Cagw(module=module, results=results)
    cagw_manager.process()

    module.exit_json(**results)


if __name__ == '__main__':
    main()
