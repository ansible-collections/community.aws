#!/usr/bin/python
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: ec2_vpc_nat_gateway
version_added: 1.0.0
short_description: Manage AWS VPC NAT Gateways.
description:
  - Ensure the state of AWS VPC NAT Gateways based on their id, allocation and subnet ids.
requirements: [boto3, botocore]
options:
  state:
    description:
      - Ensure NAT Gateway is present or absent.
    default: "present"
    choices: ["present", "absent"]
    type: str
  nat_gateway_id:
    description:
      - The id AWS dynamically allocates to the NAT Gateway on creation.
        This is required when the absent option is present.
    type: str
  subnet_id:
    description:
      - The id of the subnet to create the NAT Gateway in. This is required
        with the present option.
    type: str
  allocation_id:
    description:
      - The id of the elastic IP allocation. If this is not passed and the
        eip_address is not passed. An EIP is generated for this NAT Gateway.
    type: str
  eip_address:
    description:
      - The elastic IP address of the EIP you want attached to this NAT Gateway.
        If this is not passed and the allocation_id is not passed,
        an EIP is generated for this NAT Gateway.
    type: str
  if_exist_do_not_create:
    description:
      - if a NAT Gateway exists already in the subnet_id, then do not create a new one.
    required: false
    default: false
    type: bool
  tags:
    description:
      - A dict of tags to apply to the NAT gateway.
      - To remove all tags set I(tags={}) and I(purge_tags=true).
    aliases: [ 'resource_tags' ]
    type: dict
    version_added: 1.4.0
  purge_tags:
    description:
      - Remove tags not listed in I(tags).
    type: bool
    default: true
    version_added: 1.4.0
  release_eip:
    description:
      - Deallocate the EIP from the VPC.
      - Option is only valid with the absent state.
      - You should use this with the wait option. Since you can not release an address while a delete operation is happening.
    default: false
    type: bool
  wait:
    description:
      - Wait for operation to complete before returning.
    default: false
    type: bool
  wait_timeout:
    description:
      - How many seconds to wait for an operation to complete before timing out.
    default: 320
    type: int
  client_token:
    description:
      - Optional unique token to be used during create to ensure idempotency.
        When specifying this option, ensure you specify the eip_address parameter
        as well otherwise any subsequent runs will fail.
    type: str
author:
  - Allen Sanabria (@linuxdynasty)
  - Jon Hadfield (@jonhadfield)
  - Karen Cheng (@Etherdaemon)
extends_documentation_fragment:
- amazon.aws.aws
- amazon.aws.ec2

'''

EXAMPLES = '''
# Note: These examples do not set authentication details, see the AWS Guide for details.

- name: Create new nat gateway with client token.
  community.aws.ec2_vpc_nat_gateway:
    state: present
    subnet_id: subnet-12345678
    eip_address: 52.1.1.1
    region: ap-southeast-2
    client_token: abcd-12345678
  register: new_nat_gateway

- name: Create new nat gateway using an allocation-id.
  community.aws.ec2_vpc_nat_gateway:
    state: present
    subnet_id: subnet-12345678
    allocation_id: eipalloc-12345678
    region: ap-southeast-2
  register: new_nat_gateway

- name: Create new nat gateway, using an EIP address  and wait for available status.
  community.aws.ec2_vpc_nat_gateway:
    state: present
    subnet_id: subnet-12345678
    eip_address: 52.1.1.1
    wait: true
    region: ap-southeast-2
  register: new_nat_gateway

- name: Create new nat gateway and allocate new EIP.
  community.aws.ec2_vpc_nat_gateway:
    state: present
    subnet_id: subnet-12345678
    wait: true
    region: ap-southeast-2
  register: new_nat_gateway

- name: Create new nat gateway and allocate new EIP if a nat gateway does not yet exist in the subnet.
  community.aws.ec2_vpc_nat_gateway:
    state: present
    subnet_id: subnet-12345678
    wait: true
    region: ap-southeast-2
    if_exist_do_not_create: true
  register: new_nat_gateway

- name: Delete nat gateway using discovered nat gateways from facts module.
  community.aws.ec2_vpc_nat_gateway:
    state: absent
    region: ap-southeast-2
    wait: true
    nat_gateway_id: "{{ item.NatGatewayId }}"
    release_eip: true
  register: delete_nat_gateway_result
  loop: "{{ gateways_to_remove.result }}"

- name: Delete nat gateway and wait for deleted status.
  community.aws.ec2_vpc_nat_gateway:
    state: absent
    nat_gateway_id: nat-12345678
    wait: true
    wait_timeout: 500
    region: ap-southeast-2

- name: Delete nat gateway and release EIP.
  community.aws.ec2_vpc_nat_gateway:
    state: absent
    nat_gateway_id: nat-12345678
    release_eip: true
    wait: yes
    wait_timeout: 300
    region: ap-southeast-2

- name: Create new nat gateway using an allocation-id and tags.
  community.aws.ec2_vpc_nat_gateway:
    state: present
    subnet_id: subnet-12345678
    allocation_id: eipalloc-12345678
    region: ap-southeast-2
    tags:
      Tag1: tag1
      Tag2: tag2
  register: new_nat_gateway
'''

RETURN = '''
create_time:
  description: The ISO 8601 date time format in UTC.
  returned: In all cases.
  type: str
  sample: "2016-03-05T05:19:20.282000+00:00'"
nat_gateway_id:
  description: id of the VPC NAT Gateway
  returned: In all cases.
  type: str
  sample: "nat-0d1e3a878585988f8"
subnet_id:
  description: id of the Subnet
  returned: In all cases.
  type: str
  sample: "subnet-12345"
state:
  description: The current state of the NAT Gateway.
  returned: In all cases.
  type: str
  sample: "available"
tags:
  description: The tags associated the VPC NAT Gateway.
  type: dict
  returned: When tags are present.
  sample:
    tags:
      "Ansible": "Test"
vpc_id:
  description: id of the VPC.
  returned: In all cases.
  type: str
  sample: "vpc-12345"
nat_gateway_addresses:
  description: List of dictionaries containing the public_ip, network_interface_id, private_ip, and allocation_id.
  returned: In all cases.
  type: str
  sample: [
      {
          'public_ip': '52.52.52.52',
          'network_interface_id': 'eni-12345',
          'private_ip': '10.0.0.100',
          'allocation_id': 'eipalloc-12345'
      }
  ]
'''

import datetime
import random
import time

try:
    import botocore
except ImportError:
    pass  # Handled by AnsibleAWSModule



from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AWSRetry
from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.core import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import camel_dict_to_snake_dict
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import ansible_dict_to_boto3_filter_list
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import ansible_dict_to_boto3_tag_list
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import boto3_tag_list_to_ansible_dict
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import compare_aws_tags
from ansible.module_utils.six import string_types


def get_nat_gateways(client, module, subnet_id=None, nat_gateway_id=None,
                     states=None):
    """Retrieve a list of NAT Gateways
    Args:
        client (botocore.client.EC2): Boto3 client

    Kwargs:
        subnet_id (str): The subnet_id the NAT resides in.
        nat_gateway_id (str): The Amazon NAT gateway id.
        states (list): States available (pending, failed, available, deleting, and deleted)
            default=None

    Basic Usage:
        >>> client = boto3.client('ec2')
        >>> subnet_id = 'subnet-12345678'
        >>> get_nat_gateways(client, subnet_id)
        [
            true,
            "",
            {
                "nat_gateway_id": "nat-123456789",
                "subnet_id": "subnet-123456789",
                "nat_gateway_addresses": [
                    {
                        "public_ip": "55.55.55.55",
                        "network_interface_id": "eni-1234567",
                        "private_ip": "10.0.0.102",
                        "allocation_id": "eipalloc-1234567"
                    }
                ],
                "state": "deleted",
                "create_time": "2016-03-05T00:33:21.209000+00:00",
                "delete_time": "2016-03-05T00:36:37.329000+00:00",
                "vpc_id": "vpc-12345678"
            }

    Returns:
        Tuple (bool, str, list)
    """
    params = dict()
    existing_gateways = list()

    if not states:
        states = ['available', 'pending']
    if nat_gateway_id:
        params['NatGatewayIds'] = [nat_gateway_id]
    else:
        params['Filter'] = [
            {
                'Name': 'subnet-id',
                'Values': [subnet_id]
            },
            {
                'Name': 'state',
                'Values': states
            }
        ]

    try:
        gateways = client.describe_nat_gateways(aws_retry=True, **params)['NatGateways']
        if gateways:
            for gw in gateways:
                existing_gateways.append(camel_dict_to_snake_dict(gw))

    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e)
    
    return existing_gateways
   

def wait_for_status(client, module, wait_timeout, nat_gateway_id, status):
    """Wait for the NAT Gateway to reach a status
    Args:
        client (botocore.client.EC2): Boto3 client
        wait_timeout (int): Number of seconds to wait, until this timeout is reached.
        nat_gateway_id (str): The Amazon nat id.
        status (str): The status to wait for.
            examples. status=available, status=deleted

    Basic Usage:
        >>> client = boto3.client('ec2')
        >>> subnet_id = 'subnet-12345678'
        >>> allocation_id = 'eipalloc-12345678'
        >>> wait_for_status(client, subnet_id, allocation_id)
        [
            true,
            "",
            {
                "nat_gateway_id": "nat-123456789",
                "subnet_id": "subnet-1234567",
                "nat_gateway_addresses": [
                    {
                        "public_ip": "55.55.55.55",
                        "network_interface_id": "eni-1234567",
                        "private_ip": "10.0.0.102",
                        "allocation_id": "eipalloc-12345678"
                    }
                ],
                "state": "deleted",
                "create_time": "2016-03-05T00:33:21.209000+00:00",
                "delete_time": "2016-03-05T00:36:37.329000+00:00",
                "vpc_id": "vpc-12345677"
            }
        ]

    Returns:
        Tuple (bool, str, dict)
    """
    polling_increment_secs = 5
    wait_timeout = time.time() + wait_timeout
    status_achieved = False
    nat_gateway = dict()
    states = ['pending', 'failed', 'available', 'deleting', 'deleted']
    msg = ''

    ### How do we manage the status of the NAT Gateway?
    while wait_timeout > time.time():
        try:
            nat_gateways = (
                get_nat_gateways(
                    client, module, nat_gateway_id=nat_gateway_id,
                    states=states
                )
            )
            ### I don't need gws_retrieved because if nat_gateways exists I am sure
            ### one has been found
            if nat_gateway: 
                nat_gateway = nat_gateways[0]

                if nat_gateway.get('state') == status:
                    status_achieved = True
                    break

                elif nat_gateway.get('state') == 'failed':
                    msg = nat_gateway.get('failure_message')
                    break

                elif nat_gateway.get('state') == 'pending':
                    if 'failure_message' in nat_gateway:
                        msg = nat_gateway.get('failure_message')
                        status_achieved = False
                        break

            else:
                time.sleep(polling_increment_secs)

        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e)

    if not status_achieved:
        msg = "Wait time out reached, while waiting for results"
    
    return status_achieved, msg, nat_gateway



def gateway_in_subnet_exists(client, module, subnet_id, allocation_id=None):
    """Retrieve all NAT Gateways for a subnet.
    Args:
        client (botocore.client.EC2): Boto3 client
        subnet_id (str): The subnet_id the nat resides in.

    Kwargs:
        allocation_id (str): The EIP Amazon identifier.
            default = None
        

    Basic Usage:
        >>> client = boto3.client('ec2')
        >>> subnet_id = 'subnet-1234567'
        >>> allocation_id = 'eipalloc-1234567'
        >>> gateway_in_subnet_exists(client, subnet_id, allocation_id)
        (
            [
                {
                    "nat_gateway_id": "nat-123456789",
                    "subnet_id": "subnet-123456789",
                    "nat_gateway_addresses": [
                        {
                            "public_ip": "55.55.55.55",
                            "network_interface_id": "eni-1234567",
                            "private_ip": "10.0.0.102",
                            "allocation_id": "eipalloc-1234567"
                        }
                    ],
                    "state": "deleted",
                    "create_time": "2016-03-05T00:33:21.209000+00:00",
                    "delete_time": "2016-03-05T00:36:37.329000+00:00",
                    "vpc_id": "vpc-1234567"
                }
            ],
            False
        )

    Returns:
        Tuple (list, bool)
    """
    allocation_id_exists = False
    gateways = []
    states = ['available', 'pending']

    gws_retrieved = (
        get_nat_gateways(
            client, module, subnet_id, states=states
        )
    )

    if not gws_retrieved: 
        return gateways, allocation_id_exists
    
    for gw in gws_retrieved:
        for address in gw['nat_gateway_addresses']:
            if allocation_id:
                if address.get('allocation_id') == allocation_id:
                    allocation_id_exists = True
                    gateways.append(gw)
            else:
                gateways.append(gw)
    
    return gateways, allocation_id_exists


def get_eip_allocation_id_by_address(client, module, eip_address):
    """Release an EIP from your EIP Pool
    Args:
        client (botocore.client.EC2): Boto3 client
        eip_address (str): The Elastic IP Address of the EIP.

    Kwargs:
        check_mode (bool): if set to true, do not run anything and
            falsify the results.

    Basic Usage:
        >>> client = boto3.client('ec2')
        >>> eip_address = '52.87.29.36'
        >>> get_eip_allocation_id_by_address(client, eip_address)
        'eipalloc-36014da3'

    Returns:
        Tuple (str, str)
    """
    params = {
        'PublicIps': [eip_address],
    }
    allocation_id = None
    msg = ''

    try:
        allocations = client.describe_addresses(aws_retry=True, **params)['Addresses']
        if len(allocations) == 1:
            allocation = allocations[0]
        else:
            allocation = None

        if allocation:
            if allocation.get('Domain') != 'vpc':
                msg = (
                    "EIP {0} is a non-VPC EIP, please allocate a VPC scoped EIP"
                    .format(eip_address)
                )
            else:
                allocation_id = allocation.get('AllocationId')
        else:
            msg = (
                "EIP {0} does not exist".format(eip_address)
            )

    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e)
    

    return allocation_id, msg


def allocate_eip_address(client, module):
    """Release an EIP from your EIP Pool
    Args:
        client (botocore.client.EC2): Boto3 client

    Kwargs:
        check_mode (bool): if set to true, do not run anything and
            falsify the results.

    Basic Usage:
        >>> client = boto3.client('ec2')
        >>> allocate_eip_address(client)
        True

    Returns:
        Tuple (bool, str)
    """
    changed = False
    new_eip = None
    msg = ''
    
    params = {
        'Domain': 'vpc',
    }

    if module.check_mode:
        changed = True
        new_eip = None
        return changed, msg, new_eip

    try:
        new_eip = client.allocate_address(aws_retry=True, **params)['AllocationId']
        changed = True
        msg = 'eipalloc id {0} created'.format(new_eip)

    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e)

    return changed, msg, new_eip


def release_address(client, module, allocation_id):
    """Release an EIP from your EIP Pool
    Args:
        client (botocore.client.EC2): Boto3 client
        allocation_id (str): The eip Amazon identifier.

    Kwargs:
        check_mode (bool): if set to true, do not run anything and
            falsify the results.

    Basic Usage:
        >>> client = boto3.client('ec2')
        >>> allocation_id = "eipalloc-123456"
        >>> release_address(client, allocation_id)
        True

    Returns:
        Boolean, string
    """
    msg = ''

    if module.check_mode:
        return True, ''

    ip_released = False
    try:
        client.describe_addresses(aws_retry=True, AllocationIds=[allocation_id])
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        # IP address likely already released
        # Happens with gateway in 'deleted' state that
        # still lists associations
        return True, str(e)
    try:
        client.release_address(aws_retry=True, AllocationId=allocation_id)
        ip_released = True
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e)

    return ip_released, msg


def create(client, module, subnet_id, allocation_id, tags, purge_tags, client_token=None,
           wait=False, wait_timeout=0, if_exist_do_not_create=False):
    """Create an Amazon NAT Gateway.
    Args:
        client (botocore.client.EC2): Boto3 client
        subnet_id (str): The subnet_id the nat resides in.
        allocation_id (str): The eip Amazon identifier.

    Kwargs:
        if_exist_do_not_create (bool): if a nat gateway already exists in this
            subnet, than do not create another one.
            default = False
        wait (bool): Wait for the nat to be in the deleted state before returning.
            default = False
        wait_timeout (int): Number of seconds to wait, until this timeout is reached.
            default = 0
        client_token (str):
            default = None

    Basic Usage:
        >>> client = boto3.client('ec2')
        >>> subnet_id = 'subnet-1234567'
        >>> allocation_id = 'eipalloc-1234567'
        >>> create(client, subnet_id, allocation_id, if_exist_do_not_create=True, wait=True, wait_timeout=500)
        [
            true,
            "",
            {
                "nat_gateway_id": "nat-123456789",
                "subnet_id": "subnet-1234567",
                "nat_gateway_addresses": [
                    {
                        "public_ip": "55.55.55.55",
                        "network_interface_id": "eni-1234567",
                        "private_ip": "10.0.0.102",
                        "allocation_id": "eipalloc-1234567"
                    }
                ],
                "state": "deleted",
                "create_time": "2016-03-05T00:33:21.209000+00:00",
                "delete_time": "2016-03-05T00:36:37.329000+00:00",
                "vpc_id": "vpc-1234567"
            }
        ]

    Returns:
        Tuple (bool, str, list)
    """
    params = {
        'SubnetId': subnet_id,
        'AllocationId': allocation_id
    }
    request_time = datetime.datetime.utcnow()
    changed = False
    token_provided = False
    result = {}

    if client_token:
        token_provided = True
        params['ClientToken'] = client_token

    if module.check_mode:
        changed = True
        return changed, result

    try:
        result = camel_dict_to_snake_dict(client.create_nat_gateway(**params)["NatGateway"])
        create_time = result['create_time'].replace(tzinfo=None)
        changed = True

        if token_provided and (request_time > create_time):
            changed = False
        elif wait:
            result = (
                wait_for_status(
                    client, module, wait_timeout, result['nat_gateway_id'], 'available'
                )
            )
            
        result['tags'], tags_update_exists = ensure_tags(
            client, module, nat_gw_id=result['nat_gateway_id'], tags=tags,
            purge_tags=purge_tags
        )
    except is_boto3_error_code('IdempotentParameterMismatch'):
        changed = False 
        result = None
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e: # pylint: disable=duplicate-except
        module.fail_json_aws(e)
        
    return changed, result


def pre_create(client, module, subnet_id, tags, purge_tags, allocation_id=None, eip_address=None,
               if_exist_do_not_create=False, wait=False, wait_timeout=0,
               client_token=None):
    """Create an Amazon NAT Gateway.
    Args:
        client (botocore.client.EC2): Boto3 client
        module (AnsibleAWSModule)
        subnet_id (str): The subnet_id the NAT resides in.
        tags (dict): A dict of tags to apply to the NAT gateway.
        purge_tags (bool): Remove tags not listed in tags.

    Kwargs:
        allocation_id (str): The EIP Amazon identifier.
            default = None
        eip_address (str): The Elastic IP Address of the EIP.
            default = None
        if_exist_do_not_create (bool): if a NAT gateway already exists in this
            subnet, than do not create another one.
            default = False
        wait (bool): Wait for the NAT to be in the deleted state before returning.
            default = False
        wait_timeout (int): Number of seconds to wait, until this timeout is reached.
            default = 0
        client_token (str):
            default = None

    Basic Usage:
        >>> client = boto3.client('ec2')
        >>> subnet_id = 'subnet-w4t12897'
        >>> allocation_id = 'eipalloc-36014da3'
        >>> pre_create(client, subnet_id, allocation_id, if_exist_do_not_create=True, wait=True, wait_timeout=500)
        [
            true,
            "",
            {
                "nat_gateway_id": "nat-03835afb6e31df79b",
                "subnet_id": "subnet-w4t12897",
                "nat_gateway_addresses": [
                    {
                        "public_ip": "52.87.29.36",
                        "network_interface_id": "eni-5579742d",
                        "private_ip": "10.0.0.102",
                        "allocation_id": "eipalloc-36014da3"
                    }
                ],
                "state": "deleted",
                "create_time": "2016-03-05T00:33:21.209000+00:00",
                "delete_time": "2016-03-05T00:36:37.329000+00:00",
                "vpc_id": "vpc-w68571b5"
            }
        ]

    Returns:
        Tuple (bool, bool, str, list)
    """
    changed = False
    results = list()
    msg = ''

    if not allocation_id and not eip_address:
        existing_gateways, allocation_id_exists = (gateway_in_subnet_exists(client, subnet_id))
        
        if len(existing_gateways) > 0 and if_exist_do_not_create:
            results = existing_gateways[0]
            results['tags'], tags_update_exists = ensure_tags(client, module, results['nat_gateway_id'], tags, purge_tags)

            if tags_update_exists:
                changed = True
                return changed, msg, results

            changed = False
            module.exit_json(
                msg='NAT Gateway {0} already exists in subnet_id {1}'
                .format(
                    existing_gateways[0]['nat_gateway_id'], subnet_id
                )
            )
            return changed, msg, results
        else:
            changed, msg, allocation_id = (
                allocate_eip_address(client, module)
            )
            if not changed :
                return changed, msg, dict()

    elif eip_address or allocation_id:
        if eip_address and not allocation_id:
            allocation_id, msg = (
                get_eip_allocation_id_by_address(
                    client, module, eip_address
                )
            )
            if not allocation_id:
                changed = False
                return changed, msg, dict()

        existing_gateways, allocation_id_exists = (
            gateway_in_subnet_exists(
                client, subnet_id, allocation_id
            )
        )

        if len(existing_gateways) > 0 and (allocation_id_exists or if_exist_do_not_create):
            results = existing_gateways[0]
            results['tags'], tags_update_exists = ensure_tags(client, module, results['nat_gateway_id'], tags, purge_tags)
            if tags_update_exists:
                changed = True
                return changed, msg, results

            changed = False
            msg = (
                'NAT Gateway {0} already exists in subnet_id {1}'
                .format(
                    existing_gateways[0]['nat_gateway_id'], subnet_id
                )
            )
            return changed, msg, results
    
    changed, results = create(
        client, module, subnet_id, allocation_id, tags, purge_tags, client_token,
        wait, wait_timeout, if_exist_do_not_create
    )

    return changed, msg, results


def remove(client, module, nat_gateway_id, wait=False, wait_timeout=0,
           release_eip=False):
    """Delete an Amazon NAT Gateway.
    Args:
        client (botocore.client.EC2): Boto3 client
        nat_gateway_id (str): The Amazon nat id.

    Kwargs:
        wait (bool): Wait for the nat to be in the deleted state before returning.
        wait_timeout (int): Number of seconds to wait, until this timeout is reached.
        release_eip (bool): Once the nat has been deleted, you can deallocate the eip from the vpc.

    Basic Usage:
        >>> client = boto3.client('ec2')
        >>> nat_gw_id = 'nat-03835afb6e31df79b'
        >>> remove(client, nat_gw_id, wait=True, wait_timeout=500, release_eip=True)
        [
            true,
            "",
            {
                "nat_gateway_id": "nat-03835afb6e31df79b",
                "subnet_id": "subnet-w4t12897",
                "nat_gateway_addresses": [
                    {
                        "public_ip": "52.87.29.36",
                        "network_interface_id": "eni-5579742d",
                        "private_ip": "10.0.0.102",
                        "allocation_id": "eipalloc-36014da3"
                    }
                ],
                "state": "deleted",
                "create_time": "2016-03-05T00:33:21.209000+00:00",
                "delete_time": "2016-03-05T00:36:37.329000+00:00",
                "vpc_id": "vpc-w68571b5"
            }
        ]

    Returns:
        Tuple (bool, str, list)
    """
    params = {
        'NatGatewayId': nat_gateway_id
    }
    changed = False
    results = {}
    states = ['pending', 'available']
    msg = ''

    if module.check_mode:
        changed = True
        return changed, msg, results

    try:
        gw = (
            get_nat_gateways(
                client, module, nat_gateway_id=nat_gateway_id,
                states=states
            )
        )
        if exist and len(gw) == 1:
            results = gw[0]
            client.delete_nat_gateway(aws_retry=True, **params)

            allocation_id = (
                results['nat_gateway_addresses'][0]['allocation_id']
            )
            changed = True
            msg = (
                'NAT gateway {0} is in deleting state. Delete was successful'
                .format(nat_gateway_id)
            )

            if wait:
                status_achieved, msg, results = (
                    wait_for_status(
                        client, module, wait_timeout, nat_gateway_id, 'deleted'
                    )
                )
                if status_achieved:
                    msg = (
                        'NAT gateway {0} was deleted successfully'
                        .format(nat_gateway_id)
                    )

    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e)

    if release_eip:
        eip_released, msg = (
            release_address(client, module, allocation_id))
        if not eip_released:
            module.fail_json(
                msg="Failed to release EIP {0}: {1}"
                .format(allocation_id, msg)
            )
            
    return changed, msg, results


def ensure_tags(client, module, nat_gw_id, tags, purge_tags):
    final_tags = []
    changed = False

    if module.check_mode and nat_gw_id is None:
        # We can't describe tags without an option id, we might get here when creating a new option set in check_mode
        return final_tags, changed

    filters = ansible_dict_to_boto3_filter_list({'resource-id': nat_gw_id, 'resource-type': 'natgateway'})
    cur_tags = None

    try:
        cur_tags = client.describe_tags(aws_retry=True, Filters=filters)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, "Couldn't describe tags")

    if tags is None:
        return boto3_tag_list_to_ansible_dict(cur_tags['Tags']), changed

    to_update, to_delete = compare_aws_tags(boto3_tag_list_to_ansible_dict(cur_tags.get('Tags')), tags, purge_tags)
    final_tags = boto3_tag_list_to_ansible_dict(cur_tags.get('Tags'))

    if to_update:
        try:
            if module.check_mode:
                # update tags
                final_tags.update(to_update)
            else:
                client.create_tags(
                    aws_retry=True,
                    Resources=[nat_gw_id],
                    Tags=ansible_dict_to_boto3_tag_list(to_update)
                )

            changed = True
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, "Couldn't create tags {0}".format(to_update))

    if to_delete:
        try:
            if module.check_mode:
                # update tags
                for key in to_delete:
                    del final_tags[key]
            else:
                tags_list = []
                for key in to_delete:
                    tags_list.append({'Key': key})

                client.delete_tags(aws_retry=True, Resources=[nat_gw_id], Tags=tags_list)

            changed = True
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, "Couldn't delete tags {0}".format(to_delete))

    if not module.check_mode and (to_update or to_delete):
        try:
            response = client.describe_tags(aws_retry=True, Filters=filters)
            final_tags = boto3_tag_list_to_ansible_dict(response.get('Tags'))
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, "Couldn't describe tags")

    return final_tags, changed


def main():
    argument_spec = dict(
        subnet_id=dict(type='str'),
        eip_address=dict(type='str'),
        allocation_id=dict(type='str'),
        if_exist_do_not_create=dict(type='bool', default=False),
        state=dict(default='present', choices=['present', 'absent']),
        wait=dict(type='bool', default=False),
        wait_timeout=dict(type='int', default=320, required=False),
        release_eip=dict(type='bool', default=False),
        nat_gateway_id=dict(type='str'),
        client_token=dict(type='str'),
        tags=dict(required=False, type='dict', aliases=['resource_tags']),
        purge_tags=dict(default=True, type='bool'),
    )
    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[
            ['allocation_id', 'eip_address']
        ],
        required_if=[['state', 'absent', ['nat_gateway_id']],
                     ['state', 'present', ['subnet_id']]],
    )

    state = module.params.get('state').lower()
    subnet_id = module.params.get('subnet_id')
    allocation_id = module.params.get('allocation_id')
    eip_address = module.params.get('eip_address')
    nat_gateway_id = module.params.get('nat_gateway_id')
    wait = module.params.get('wait')
    wait_timeout = module.params.get('wait_timeout')
    release_eip = module.params.get('release_eip')
    client_token = module.params.get('client_token')
    if_exist_do_not_create = module.params.get('if_exist_do_not_create')
    tags = module.params.get('tags')
    purge_tags = module.params.get('purge_tags')

    try:
        client = module.client('ec2', retry_decorator=AWSRetry.jittered_backoff())
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg='Failed to connect to AWS.')

    changed = False 
    msg = ''

    if state == 'present':
        changed, msg, results = (
            pre_create(
                client, module, subnet_id, tags, purge_tags, allocation_id, eip_address,
                if_exist_do_not_create, wait, wait_timeout,
                client_token
            )
        )
    else:
        changed, msg, results = (
            remove(
                client, nat_gateway_id, wait, wait_timeout, release_eip
            )
        )

    module.exit_json(msg=msg, changed=changed, **results)


if __name__ == '__main__':
    main()

