#!/usr/bin/python
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from os import remove
__metaclass__ = type


DOCUMENTATION = '''

'''

EXAMPLES = '''
- name: Create a new transit gateway using defaults
  community.aws.ec2_transit_gateway:
    state: present
    region: us-east-1
    description: personal-testing
  register: created_tgw

- name: Create a new transit gateway with options
  community.aws.ec2_transit_gateway:
    asn: 64514
    auto_associate: no
    auto_propagate: no
    dns_support: True
    description: "nonprod transit gateway"
    purge_tags: False
    state: present
    region: us-east-1
    tags:
      Name: nonprod transit gateway
      status: testing

- name: Remove a transit gateway by description
  community.aws.ec2_transit_gateway:
    state: absent
    region: us-east-1
    description: personal-testing

- name: Remove a transit gateway by id
  community.aws.ec2_transit_gateway:
    state: absent
    region: ap-southeast-2
    transit_gateway_id: tgw-3a9aa123
  register: deleted_tgw
'''

RETURN = '''

'''

try:
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:
    pass  # handled by imported AnsibleAWSModule

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from time import sleep, time
from ansible.module_utils._text import to_text
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import (
    ansible_dict_to_boto3_tag_list,
    ansible_dict_to_boto3_filter_list,
    AWSRetry,
    boto3_tag_list_to_ansible_dict,
    camel_dict_to_snake_dict,
    compare_aws_tags
)

class AnsibleEc2TgwAttachment(object):
    def __init__(self, module, results):
        self._module = module
        self._results = results
        self._connection = self._module.client('ec2')
        self._check_mode = self._module.check_mode


    def process(self):
        description = self._module.params.get('description')
        state = self._module.params.get('state', 'present')
        attach_id = self._module.params.get('attachment_id')
        if self._module.params.get('vpc_id'):
            self._attachment_type = "vpc"
        elif self._module.params.get('peer_transit_gateway'):
            self._attachment_type = "peer"

        if state == "present":
            if self._attachment_type == "vpc":
                vpc_result = self.vpc_ensure_attachment()
                self._results['transit_gateway_attachment'] = vpc_result

                return self._results

    @staticmethod
    def enable_option_flag(flag):
        disabled = "disable"
        enabled = "enable"
        if flag:
            return enabled
        return disabled

    @staticmethod
    def compare_tags(current_tags, desired_tags):
        tags_to_add = {}
        tags_to_remove = {}

        for k,v in desired_tags.items():
            if k not in current_tags.keys():
                tags_to_add[k] = v
                continue
            elif current_tags[k] != v:
                tags_to_add[k] = v
                continue

        for k,v in current_tags.items():
            if k not in desired_tags.keys():
                tags_to_remove[k] = v


        return tags_to_add, tags_to_remove

    def vpc_check_existing(self, vpc_id, tgw_id):
        filter_dict = {
            "vpc-id": vpc_id,
            "transit-gateway-id": tgw_id
        }
        filters = ansible_dict_to_boto3_filter_list(filter_dict)
        vpc_response = self._connection.describe_transit_gateway_vpc_attachments(Filters=filters)
        

        return vpc_response.get('TransitGatewayVpcAttachments', [])

    def tgw_update_tags(self, attachment_id, current_tags, desired_tags):
        return

    @staticmethod
    def vpc_compare_subnets(current_subnets, desired_subnets):
        add_subnets = set(desired_subnets).difference(current_subnets)
        remove_subnets = set(current_subnets).difference(desired_subnets)

        return add_subnets, remove_subnets

    @AWSRetry.exponential_backoff()
    def vpc_compare_and_update(self, tgw_attachment):
        changed = False
        
        tgw_options = {
                "ApplianceModeSupport": self.enable_option_flag(self._module.params.get('vpc_dns_support')),
                "DnsSupport": self.enable_option_flag(self._module.params.get('vpc_ipv6_support')),
                "Ipv6Support": self.enable_option_flag(self._module.params.get('vpc_appliance_mode_support'))
        }

        subnets_to_add, subnets_to_remove = self.vpc_compare_subnets(
            tgw_attachment['SubnetIds'],
            self._module.params.get('subnet_ids')
        )

        tags_to_add, tags_to_remove = self.compare_tags(
                boto3_tag_list_to_ansible_dict(tgw_attachment.get('Tags', None)),
                self._module.params.get('tags')
            )

        if tgw_options != tgw_attachment['Options']:
            changed = True
        elif len(tags_to_add) > 0 or len(tags_to_remove) > 0:
            changed = True
        elif len(subnets_to_add) > 0 or len(subnets_to_remove) > 0:
            changed = True

        

        # if len(tags_to_add) > 0:
            

        # if len(tags_to_remove) > 0:



        if changed:
            try:
                if not self._check_mode:
                    # response =self._connection.modify_transit_gateway_vpc_attachment(**update_params)
                    return
                self._results['changed'] = True
            except (BotoCoreError, ClientError) as e:
                self._module.fail_json_aws(e, msg="Trying to update transit gateway attachment configuration")

        

        else:
            return current_tags, desired_tags


    def vpc_ensure_attachment(self):
        tgw_id = self._module.params.get('transit_gateway_id')
        vpc_id = self._module.params.get('vpc_id')

        existing = self.vpc_check_existing(vpc_id, tgw_id)

        if len(existing) == 0:
            return
        elif len(existing) == 1:
            return self.vpc_compare_and_update(existing[0])
        else:
            return "BORK!"


def setup_module_object():
    """
    merge argument spec and create Ansible module object
    :return: Ansible module object
    """

    argument_spec = dict(
        transit_gateway_id=dict(type='str', required=True),

        vpc_id=dict(type='str'),
        subnet_ids=dict(type='list', default=[]),
        vpc_dns_support=dict(type='bool', default='yes'),
        vpc_ipv6_support=dict(type='bool', default='no'),
        vpc_appliance_mode_support=dict(type='bool', default='no'),

        peer_transit_gateway_id=dict(type='str'),
        peer_account_id=dict(type='str'),
        peer_region=dict(type='str'),

        attachment_id=dict(type='str'),
        state=dict(default='present', choices=['present', 'absent', 'accept', 'reject']),
        
        wait=dict(type='bool', default='yes'),
        wait_timeout=dict(type='int', default=300),
        tags=dict(type='dict', default={})
    )

    mutually_exclusive = [
      ['vpc_id','peer_transit_gateway']
    ]

    required_one_of = [
      ['vpc_id','peer_transit_gateway']
    ]

    required_together = [
      ['vpc_id','subnet_ids'],
      ['peer_transit_gateway_id','peer_region']
    ]

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        required_one_of=required_one_of,
        mutually_exclusive=mutually_exclusive,
        required_together=required_together,
        supports_check_mode=True,
    )

    return module


def main():

    module = setup_module_object()

    results = dict(
        changed=False
    )

    tgw_manager = AnsibleEc2TgwAttachment(module=module, results=results)
    tgw_manager.process()

    module.exit_json(**results)


if __name__ == '__main__':
    main()
