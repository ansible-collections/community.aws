#!/usr/bin/python
# aws_transfer_transfer.py
# Ansible AWS Transfer Plugin
# Copyright (C) 2021  Fayez ALSEDLAH; Trading Central

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = '''
---
module: transfer
short_description: Manage SFTP Severs in AWS.
description:
    - Manage SFTP Servers in AWS Using AWS Transfer Service.
version_added: "2.4"
requirements: [ boto3 ]
author: "Fayez ALSEDLAH(@falsedlah); Trading Central"
options:
  name:
    description:
      - Fully Qualified Domain name of the SFTP Server to create
    required: true
    type: str
  state:
    description:
      - Create or remove the SFTP Server
      - Present will also execute an update if necessary.
    required: false
    default: present
    choices: [ 'present', 'absent', 'add_user', 'remove_user' ]
    type: str
  tags:
    description:
      - tags dict to apply to the server
    type: dict
  purge_tags:
    description:
      - whether to remove tags that aren't present in the C(tags) parameter
    type: bool
    default: True
  endpoint_type:
    description:
      - The type of endpoint to be used.
    type: str
    choices: ['PUBLIC', 'VPC_ENDPOINT']
    default: 'PUBLIC'
  identity_provider_type:
    description:
      - The identity provider type.
    type: str
    choices: ['SERVICE_MANAGED', 'API_GATEWAY']
    default: 'SERVICE_MANAGED'
  user_home_directory_type:
    description:
      - The Type of directory that the user is mapped to.
    type: str
    choices: ['PATH', 'LOGICAL']
  user_home_directory:
    description:
      - The location of the directory for the user home directory.
    type: str
    default: '/'
  user_home_directory_mappings:
    description:
      - Mappings for the user home directory on S3 to the local filesystem on the SFTP server.
    type: dict
  user_name:
    description:
      - The user name to create an account on the SFTP Server for.
    type: str
  user_policy:
    description:
      - A JSON-Formatted policy to limit the user, if needed.
    type: str
  user_role:
    description:
      - The ARN that points to the role that the user should assume.  This role should have access to the S3 Bucket.
    type: str
  user_ssh_public_key_body:
    description:
      - The body of the public key that will be used (if pre-generated) to access the SFTP Server.
    type: str
  user_tags:
    description:
      - Tags that should be associated with the user when created.
    type: list
  host_key:
    description:
      - The SSH-keygen generated key for this particular host.
      - It is not recommended to manage your own SSH keys for sftp hosts, but it is provided as a convenience for migration.
    type: str
  identity_provider_role:
    description:
      - The role parameter provides the type of role used to authenticate the user account.
      - Length Constraints -  Minimum length of 20. Maximum length of 2048.
      - 'Pattern:: arn::.*role/.*'
    type: str
  identity_provider_url:
    description:
    - The Url parameter provides contains the location of the service endpoint used to authenticate users.
    - Length Constraints - Maximum length of 255.
    type: str
  logging_role:
    description:
      - A value that allows the service to write your SFTP users' activity to your Amazon CloudWatch logs for monitoring and auditing purposes.
      - Length Constraints - Minimum length of 20. Maximum length of 2048.
      - 'Pattern:: arn::.*role/.*'
    type: str
  transfer_endpoint_url:
    description:
      - The URL for the transfer endpoint.
    type: str
  vpc_id:
    description:
      - the VPC to place the created SFTP server into.
    type: str
extends_documentation_fragment:
    - aws
    - ec2
notes:
    - If C(requestPayment), C(policy), C(tagging) or C(versioning)
      operations/API aren't implemented by the endpoint, module doesn't fail
      if related parameters I(requester_pays), I(policy), I(tags) or
      I(versioning) are C(None).
'''

EXAMPLES = '''
# Note: These examples do not set authentication details, see the AWS Guide for details.

'''


from ansible.module_utils._text import to_text
from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import ec2_argument_spec, AWSRetry, boto3_tag_list_to_ansible_dict, \
    ansible_dict_to_boto3_tag_list, get_aws_connection_info
try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError, EndpointConnectionError, WaiterError
except ImportError:
    pass  # handled by AnsibleAWSModule

SERVER_NAME_KEY = 'aws:transfer:customHostname'


def create_or_update_sftp(client, module):
    name = module.params.get("name")
    purge_tags = module.params.get("purge_tags")
    tags = {}
    if module.params.get("tags") is not None:
        tags = module.params.get("tags")
    endpoint_type = module.params.get("endpoint_type")
    vpc_id = module.params.get("vpc_id")
    host_key = module.params.get("host_key")
    identity_provider_type = module.params.get("identity_provider_type")
    identity_provider_role = module.params.get("identity_provider_role")
    identity_provider_url = module.params.get("identity_provider_url")
    logging_role = module.params.get("logging_role")
    changed = False
    result = {}
    sftp_server = None
    needs_creation = False

    # TODO: Eventually, this needs to support all of the endpoint details, including vpc endpoint ids.
    endpoint_details = None
    if endpoint_type != 'PUBLIC' and vpc_id is not None:
        endpoint_details = {
            # "AddressAllocationIds": [],
            # "SubnetIds": [],
            # "VpcEndpointId": "",
            "VpcId": vpc_id
        }

    identity_provider_details = None
    if identity_provider_url is not None and identity_provider_role is not None:
        identity_provider_details = {
            "InvocationRole": identity_provider_role,
            "Url": identity_provider_url
        }

    name_tag = {'Key': SERVER_NAME_KEY, 'Value': name}
    assigned_tags = [name_tag]

    try:
        sftp_server = find_sftp_server(client, name)
        needs_creation = sftp_server is None
    except EndpointConnectionError as e:
        module.fail_json_aws(e, msg="Invalid endpoint provided: %s" % to_text(e))
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg="Failed to check Transfer presence")
    if needs_creation:
        result = create_sftp_server(client, endpoint_details, endpoint_type, host_key,
                                    identity_provider_details, identity_provider_type, logging_role, name_tag)
        sftp_server_id = result['ServerId']
        changed = True
    else:
        sftp_server_id = sftp_server['Server']['ServerId']
        if not purge_tags:
            assigned_tags = sftp_server['Tags']
    # Update SFTP Server Details
    # Update Tags
    for key, value in tags.items():
        item = [ tag for tag in assigned_tags if x['Key'] == key ][0]
        if item:
            item['Value'] = value
        else:
            item = {'Key': key, 'Value': value}
            assigned_tags.append(item)
    update_args = build_server_kwargs(endpoint_details, endpoint_type, host_key, identity_provider_details,
                                      identity_provider_type, logging_role, name, sftp_server_id, is_update=True)

    result = client.update_server(**update_args)
    changed = True

    module.exit_json(changed=changed, name=name, **result)


def find_sftp_server(client, server_name):
    # Finding a server by name is a little more complicated than I originally expected.  Rather than wasting resources
    # it's much easier to just go find it and then check if the return value of this method is None.
    # Load all of the server IDs in the account
    all_server_ids = [ server['ServerId'] for server  in client.list_servers()['Servers']]
    all_servers = [client.describe_server(ServerId=server_id) for server_id in all_server_ids]
    host = [server for server in all_servers for tags in server['Server']['Tags'] if tags['Value']==server_name]
    if host:
       return host[0]
    return None


@AWSRetry.exponential_backoff(max_delay=120)
def create_sftp_server(client, endpoint_details, endpoint_type, host_key,
                       identity_provider_details, identity_provider_type, logging_role, name):
    """
    Does the work of actually creating the SFTP Server.
    :arg client: boto3.session.Session the boto3 client that is used to create the connection
    :arg endpoint_details: object The details that are provided to the endpoint - right now vpc_id is the only supported
    information.
    :arg endpoint_type: str The type of endpoint that the created SFTP Server connects to.  AWS Supports PUBLIC, VPC and
    VPC_ENDPOINT
    :arg host_key: str This is the generated ssh key for the host, the result of ssh-keygen.  Do not use this unless you
    are transitioning from another SFTP Server and need to maintain backward compatibility.
    :arg identity_provider_details: object The information for the provided entity type.
    See https://docs.aws.amazon.com/transfer/latest/userguide/API_IdentityProviderDetails.html for more details.
    :arg identity_provider_type: str Currently supports SERVICE_MANAGED or API_GATEWAY - if using API_GATEWAY,
    identity_provider_details becomes required.  SERVICE_MANAGED is the default, and allows AWS to manage the SFTP
    server.
    :arg logging_role: str A value that allows the service to write your SFTP users' activity to your Amazon CloudWatch
    logs for monitoring and auditing purposes.
    :arg name: dict The name of the SFTP server that also becomes the FQDN of it, in tag format.
    :rtype: dict A Single Entry Dictionary that contains the Server ID.
    """
    kwargDict = build_server_kwargs(endpoint_details, endpoint_type, host_key, identity_provider_details,
                                    identity_provider_type, logging_role, name)

    response = client.create_server(**kwargDict)
    # According to the documentation response should be an object containing a single string like this:
    # {
    #    ServerId: 'string(19)'
    # }
    return response


def build_server_kwargs(endpoint_details, endpoint_type, host_key, identity_provider_details, identity_provider_type,
                        logging_role, name, server_id=None, is_update=False):
    kwarg_dict = {}
    if not is_update:
        kwarg_dict['Tags'] = [name]
    if endpoint_details is not None:
        kwarg_dict['EndpointDetails'] = endpoint_details
    if endpoint_type is not None:
        kwarg_dict['EndpointType'] = endpoint_type
    if host_key is not None:
        kwarg_dict['HostKey'] = host_key
    if identity_provider_details is not None:
        kwarg_dict['IdentityProviderDetails'] = identity_provider_details
    if identity_provider_type is not None and not is_update:
        kwarg_dict['IdentityProviderType'] = identity_provider_type
    if logging_role is not None:
        kwarg_dict['LoggingRole'] = logging_role
    if server_id is not None:
        kwarg_dict['ServerId'] = server_id
    return kwarg_dict


def add_sftp_users(client, module):
    changed = False
    user_name = module.params.get('user_name')
    user_home_directory = module.params.get('user_home_directory')
    user_home_directory_type = module.params.get('user_home_directory_type')
    user_home_directory_mappings = module.params.get('user_home_directory_mappings')
    user_policy = module.params.get('user_policy')
    user_role = module.params.get('user_role')
    user_ssh_public_key_body = module.params.get('user_ssh_public_key_body')
    user_tags = module.params.get('user_tags')
    name = module.params.get('name')

    result = add_user(client, user_name, user_home_directory, user_home_directory_type, user_home_directory_mappings,
                      user_policy, user_role, user_ssh_public_key_body, user_tags, name)
    changed = True
    module.exit_json(changed=changed, **result)


@AWSRetry.exponential_backoff(max_delay=120)
def add_user(client, user_name, user_home_directory, user_home_directory_type,
             user_home_directory_mappings, user_policy, user_role, user_ssh_public_key_body, user_tags, name):
    result = {}
    sftp_server = find_sftp_server(client, name)
    exists = False
    if sftp_server is not None:
        sftp_server_id = sftp_server['Server']['ServerId']
        users = client.list_users(
            ServerId=sftp_server_id
        )

        if users is not None:
            exists = [ user for user in users['Users'] if user['UserName'] == user_name ]

        add_user_kwargs = dict(
            Role=user_role,
            ServerId=sftp_server_id,
            UserName=user_name
        )

        if user_home_directory is not None:
            add_user_kwargs['HomeDirectory'] = user_home_directory
        if user_home_directory_type is not None:
            add_user_kwargs['HomeDirectoryType'] = user_home_directory_type
        if user_home_directory_mappings is not None:
            add_user_kwargs['HomeDirectoryMappings'] = user_home_directory_mappings
        if user_policy is not None:
            add_user_kwargs['Policy'] = user_policy
        if user_ssh_public_key_body is not None:
            add_user_kwargs['SshPublicKeyBody'] = user_ssh_public_key_body
        if user_tags is not None:
            add_user_kwargs['Tags'] = user_tags

        if not exists:
            result = client.create_user(**add_user_kwargs)
        else:
            result = client.update_user(**add_user_kwargs)

    return result


@AWSRetry.exponential_backoff(max_delay=120)
def destroy_sftp_server(client, module):
    name = module.params.get('name')
    response = dict()
    sftp_server = find_sftp_server(client, name)
    changed = False
    if sftp_server is not None:
        sftp_server_id = sftp_server['Server']['ServerId']
        response = client.delete_server(ServerId=sftp_server_id)
        changed = True
    module.exit_json(changed=changed, name=name, **response)


@AWSRetry.exponential_backoff(max_delay=120)
def destroy_sftp_users(client, module):
    changed = False
    response = dict()
    name = module.params.get('name')
    user_name = module.params.get('user_name')
    sftp_server_id = get_sftp_server_id(client, name)
    response = client.delete_user(ServerId=sftp_server_id, UserName=user_name)
    changed = True

    module.exit_json(changed=changed, name=name, **response)


def get_sftp_server_id(client, name):
    sftp_server = find_sftp_server(client, name)
    sftp_server_id = sftp_server['Server']['ServerId']
    return sftp_server_id


def main():
    argument_spec = ec2_argument_spec()
    argument_spec.update(
        dict(
            name=dict(required=True),
            state=dict(default='present', choices=['present', 'absent', 'add_user', 'remove_user']),
            tags=dict(type='dict'),
            purge_tags=dict(type='bool', default=True),
            # Default to public because AWS does.  This is probably not the best option.
            endpoint_type=dict(default="PUBLIC", choices=['PUBLIC', 'VPC_ENDPOINT']),
            vpc_id=dict(required=False),
            host_key=dict(),
            identity_provider_type=dict(default='SERVICE_MANAGED', choices=['SERVICE_MANAGED', 'API_GATEWAY']),
            identity_provider_role=dict(),
            identity_provider_url=dict(),
            transfer_endpoint_url=dict(),
            logging_role=dict(),
            user_name=dict(type='str'),
            user_home_directory=dict(type='str', default='/'),
            user_home_directory_type=dict(type='str', choices=['PATH', 'LOGICAL']),
            user_home_directory_mappings=dict(type='dict'),
            user_policy=dict(type='str'),
            user_role=dict(type='str'),
            user_ssh_public_key_body=dict(type='str'),
            user_tags=dict(type='list'),
        )
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
    )
    test_mo = module
    region, ec2_url, aws_connect_kwargs = get_aws_connection_info(module, boto3=True)

    if region in ('us-east-1', '', None):
        # default to US Standard region
        location = 'us-east-1'
    else:
        # Boto uses symbolic names for locations but region strings will
        # actually work fine for everything except us-east-1 (US Standard)
        location = region

    # Get AWS connection information.
    endpoint_url = module.params.get('transfer_endpoint_url')
    aws_access_token = aws_connect_kwargs.get('aws_access_key_id')
    aws_secret_key = aws_connect_kwargs.get('aws_secret_access_key')
    aws_session_token = aws_connect_kwargs.get('security_token')

    state = module.params.get("state")

    transfer_client = module.client('transfer')

    if state == 'present':
        create_or_update_sftp(transfer_client, module)
    elif state == 'absent':
        destroy_sftp_server(transfer_client, module)
    elif state == 'add_user':
        add_sftp_users(transfer_client, module)
    elif state == 'remove_user':
        destroy_sftp_users(transfer_client, module)


if __name__ == '__main__':
    main()