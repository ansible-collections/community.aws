#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r'''
---
module: rds_subnet_group
version_added: 1.0.0
short_description: manage RDS database subnet groups
description:
     - Creates, modifies, and deletes RDS database subnet groups.
options:
  state:
    description:
      - Specifies whether the subnet should be present or absent.
    required: true
    choices: [ 'present' , 'absent' ]
    type: str
  name:
    description:
      - Database subnet group identifier.
    required: true
    type: str
  description:
    description:
      - Database subnet group description.
      - Required when I(state=present).
    type: str
  subnets:
    description:
      - List of subnet IDs that make up the database subnet group.
      - Required when I(state=present).
    type: list
    elements: str
  tags:
    description:
      - A hash/dictionary of tags to add to the new RDS subnet group or to add/remove from an existing one.
    type: dict
    version_added: 1.5.0
  purge_tags:
    description:
       - Whether or not to remove tags assigned to the RDS subnet group if not specified in the playbook.
       - To remove all tags set I(tags) to an empty dictionary in conjunction with this.
    default: false
    type: bool
    version_added: 1.5.0
author:
    - "Scott Anderson (@tastychutney)"
    - "Alina Buzachis (@alinabuzachis)"
extends_documentation_fragment:
- amazon.aws.aws
- amazon.aws.ec2

'''

EXAMPLES = r'''
- name: Add or change a subnet group
  community.aws.rds_subnet_group:
    state: present
    name: norwegian-blue
    description: My Fancy Ex Parrot Subnet Group
    subnets:
      - subnet-aaaaaaaa
      - subnet-bbbbbbbb

- name: Add or change a subnet group and associate tags
  community.aws.rds_subnet_group:
    state: present
    name: norwegian-blue
    description: My Fancy Ex Parrot Subnet Group
    subnets:
      - subnet-aaaaaaaa
      - subnet-bbbbbbbb
    tags:
      tag1: Tag1
      tag2: Tag2

- name: Remove a subnet group
  community.aws.rds_subnet_group:
    state: absent
    name: norwegian-blue
'''

RETURN = r'''
changed:
    description: True if listing the RDS subnet group succeeds.
    type: bool
    returned: always
    sample: "false"
subnet_group:
    description: Dictionary of DB subnet group values
    returned: I(state=present)
    type: complex
    contains:
        name:
            description: The name of the DB subnet group (maintained for backward compatibility)
            returned: I(state=present)
            type: str
            sample: "ansible-test-mbp-13950442"
        db_subnet_group_name:
            description: The name of the DB subnet group
            returned: I(state=present)
            type: str
            sample: "ansible-test-mbp-13950442"
        description:
            description: The description of the DB subnet group (maintained for backward compatibility)
            returned: I(state=present)
            type: str
            sample: "Simple description."
        db_subnet_group_description:
            description: The description of the DB subnet group
            returned: I(state=present)
            type: str
            sample: "Simple description."
        vpc_id:
            description: The VpcId of the DB subnet group
            returned: I(state=present)
            type: str
            sample: "vpc-0acb0ba033ff2119c"
        subnet_ids:
            description: Contains a list of Subnet IDs
            returned: I(state=present)
            type: list
            sample:
                "subnet-08c94870f4480797e"
        subnets:
            description: Contains a list of Subnet elements (@see https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds.html#RDS.Client.describe_db_subnet_groups) # noqa
            returned: I(state=present)
            type: list
            contains:
                subnet_availability_zone:
                    description: Contains Availability Zone information.
                    returned: I(state=present)
                    type: dict
                    sample:
                        name: "eu-north-1b"
                subnet_identifier:
                    description: The identifier of the subnet.
                    returned: I(state=present)
                    type: str
                    sample: "subnet-08c94870f4480797e"
                subnet_outpost:
                    description: This value specifies the Outpost.
                    returned: I(state=present)
                    type: dict
                    sample: {}
                subnet_status:
                    description: The status of the subnet.
                    returned: I(state=present)
                    type: str
                    sample: "Active"
        status:
            description: The status of the DB subnet group (maintained for backward compatibility)
            returned: I(state=present)
            type: str
            sample: "Complete"
        subnet_group_status:
            description: The status of the DB subnet group
            returned: I(state=present)
            type: str
            sample: "Complete"
        db_subnet_group_arn:
            description: The ARN of the DB subnet group
            returned: I(state=present)
            type: str
            sample: "arn:aws:rds:eu-north-1:721066863947:subgrp:ansible-test-13950442"
        tags:
            description: The tags associated with the subnet group
            returned: I(state=present)
            type: dict
            sample:
                tag1: Tag1
                tag2: Tag2
'''

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict
from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule, is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import ansible_dict_to_boto3_tag_list
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import boto3_tag_list_to_ansible_dict
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AWSRetry
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import compare_aws_tags


try:
    import botocore
except ImportError:
    pass  # Handled by AnsibleAWSModule


def create_result(changed, subnet_group=None):
    if subnet_group is None:
        return dict(
            changed=changed
        )
    result_subnet_group = dict(subnet_group)
    result_subnet_group['name'] = result_subnet_group.get(
        'db_subnet_group_name')
    result_subnet_group['description'] = result_subnet_group.get(
        'db_subnet_group_description')
    result_subnet_group['status'] = result_subnet_group.get(
        'subnet_group_status')
    result_subnet_group['subnet_ids'] = create_subnet_list(
        subnet_group.get('subnets'))
    return dict(
        changed=changed,
        subnet_group=result_subnet_group
    )


def get_subnet_group(client, module):
    params = dict()
    params['DBSubnetGroupName'] = module.params.get('name').lower()

    try:
        _result = client.describe_db_subnet_groups(aws_retry=True, **params)
    except is_boto3_error_code('DBSubnetGroupNotFoundFault'):
        return None
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:  # pylint: disable=duplicate-except
        module.fail_json_aws(e, msg="Couldn't describe subnet groups.")

    if _result:
        result = camel_dict_to_snake_dict(_result['DBSubnetGroups'][0])
        try:
            tags = client.list_tags_for_resource(aws_retry=True, ResourceName=result['db_subnet_group_arn'])['TagList']
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Couldn't obtain subnet group tags.")

        result['tags'] = boto3_tag_list_to_ansible_dict(tags)

    return result


def create_subnet_list(subnets):
    '''
    Construct a list of subnet ids from a list of subnets dicts returned by boto3.
    Parameters:
        subnets (list): A list of subnets definitions.
        @see https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds.html#RDS.Client.describe_db_subnet_groups
    Returns:
        (list): List of subnet ids (str)
    '''
    subnets_ids = []
    for subnet in subnets:
        subnets_ids.append(subnet.get('subnet_identifier'))
    return subnets_ids


def update_tags(client, module, subnet_group):
    changed = False
    try:
        existing_tags = client.list_tags_for_resource(aws_retry=True, ResourceName=subnet_group['db_subnet_group_arn'])['TagList']
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't obtain subnet group tags.")

    to_update, to_delete = compare_aws_tags(boto3_tag_list_to_ansible_dict(existing_tags),
                                            module.params['tags'], module.params['purge_tags'])

    if to_update:
        try:
            if module.check_mode:
                return True
            client.add_tags_to_resource(aws_retry=True, ResourceName=subnet_group['db_subnet_group_arn'],
                                        Tags=ansible_dict_to_boto3_tag_list(to_update))
            changed = True
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Couldn't add tags to subnet group.")
    if to_delete:
        try:
            if module.check_mode:
                return True
            client.remove_tags_from_resource(aws_retry=True, ResourceName=subnet_group['db_subnet_group_arn'],
                                            TagKeys=to_delete)
            changed = True
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Couldn't remove tags from subnet group.")

    return changed


def main():
    argument_spec = dict(
        state=dict(required=True, choices=['present', 'absent']),
        name=dict(required=True),
        description=dict(required=False),
        subnets=dict(required=False, type='list', elements='str'),
        tags=dict(required=False, type='dict', default={}),
        purge_tags=dict(type='bool', default=True),
    )
    required_if = [('state', 'present', ['description', 'subnets'])]

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        required_if=required_if,
        supports_check_mode=True
    )

    state = module.params.get('state')
    group_name = module.params.get('name').lower()
    group_description = module.params.get('description')
    group_subnets = module.params.get('subnets') or []

    try:
        connection = module.client('rds', retry_decorator=AWSRetry.jittered_backoff())
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        module.fail_json_aws(e, 'Failed to instantiate AWS connection.')

    # Default.
    changed = None
    result = create_result(False)
    tags_update = False
    subnet_update = False

    try:
        matching_groups = get_subnet_group(connection, module)
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        module.fail_json_aws(e, 'Failed to get subnet groups description.')
    
    if state == 'present':
        if matching_groups:
            # We have one or more subnets at this point.

            # Check if there is a tags update
            tags_update = update_tags(connection, module, matching_groups)

            # Sort the subnet groups before we compare them
            existing_subnets = create_subnet_list(matching_groups['subnets'])
            existing_subnets.sort()
            group_subnets.sort()

            # See if anything changed.
            if (matching_groups['db_subnet_group_name'] != group_name or
                matching_groups['db_subnet_group_description'] != group_description or
                existing_subnets != group_subnets
            ):
                if not module.check_mode:
                    # Modify existing group.
                    try:
                        changed_group = connection.modify_db_subnet_group(
                            DBSubnetGroupName=group_name,
                            DBSubnetGroupDescription=group_description,
                            SubnetIds=group_subnets
                        )
                    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
                        module.fail_json_aws(e, 'Failed to update a subnet group.')
                subnet_update = True
        else:
            if not module.check_mode:
                try:
                    new_group = connection.create_db_subnet_group(
                        DBSubnetGroupName=group_name,
                        DBSubnetGroupDescription=group_description,
                        SubnetIds=group_subnets,
                        Tags=ansible_dict_to_boto3_tag_list(module.params.get("tags"))
                    )
                except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
                    module.fail_json_aws(e, 'Failed to create a new subnet group.')
            subnet_update = True        
    elif state == 'absent':
        if not module.check_mode:
            try:
                connection.delete_db_subnet_group(DBSubnetGroupName=group_name)
            except is_boto3_error_code('DBSubnetGroupNotFoundFault'):
                module.exit_json(**result)
            except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:  # pylint: disable=duplicate-except
                module.fail_json_aws(e, 'Failed to delete a subnet group.')
        subnet_update = True    

    try:
        subnet_group = get_subnet_group(connection, module)
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        module.fail_json_aws(e, 'Failed to get subnet groups description.')
    
    changed = tags_update or subnet_update
    result = create_result(changed, subnet_group)
    module.exit_json(**result)


if __name__ == '__main__':
    main()
