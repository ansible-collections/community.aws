#!/usr/bin/python
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule, is_boto3_error_code, get_boto3_client_method_parameters
from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict
__metaclass__ = type


DOCUMENTATION = r'''
---
module: rds_subnet_group
version_added: 1.0.0
short_description: manage RDS database subnet groups
description:
     - Creates, modifies, and deletes RDS database subnet groups. This module has a dependency on python-boto >= 2.5.
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
author: "Scott Anderson (@tastychutney)"
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

- name: Remove a subnet group
  community.aws.rds_subnet_group:
    state: absent
    name: norwegian-blue
'''

RETURN = r'''
subnet_group:
    description: Dictionary of DB subnet group values
    returned: I(state=present)
    type: complex
    contains:
        db_subnet_group_name:
            description: The name of the DB subnet group
            returned: I(state=present)
            type: str
        db_subnet_group_description:
            description: The description of the DB subnet group
            returned: I(state=present)
            type: str
        vpc_id:
            description: The VpcId of the DB subnet group
            returned: I(state=present)
            type: str
        subnets:
            description: Contains a list of Subnet descriptions.
            returned: I(state=present)
            type: list
        subnet_group_status:
            description: The status of the DB subnet group
            returned: I(state=present)
            type: str
        db_subnet_group_arn:
            description: The ARN of the DB subnet group
            returned: I(state=present)
            type: str
'''
try:
    import botocore
except ImportError:
    pass  # Handled by AnsibleAWSModule


def create_result(changed, subnet_group=None):
    if subnet_group is None:
        return dict(
            changed=changed
        )
    return dict(
        changed=changed,
        subnet_group=camel_dict_to_snake_dict(subnet_group)
    )


def main():
    argument_spec = dict(
        state=dict(required=True, choices=['present', 'absent']),
        name=dict(required=True),
        description=dict(required=False),
        subnets=dict(required=False, type='list', elements='str'),
    )
    required_if = [('state', 'present', ['description', 'subnets'])]
    module = AnsibleAWSModule(
        argument_spec=argument_spec, required_if=required_if)
    state = module.params.get('state')
    group_name = module.params.get('name').lower()
    group_description = module.params.get('description')
    group_subnets = module.params.get('subnets') or []

    try:
        conn = module.client('rds')
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        module.fail_json_aws(e)
    # Default.
    result = create_result(False)

    try:
        matching_groups = conn.describe_db_subnet_groups(
            DBSubnetGroupName=group_name, MaxRecords=100).get('DBSubnetGroups')
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        # Boto3 now throws an exception instead of returning an empty list.
        if e.response['Error']['Code'] == 'DBSubnetGroupNotFoundFault':
            # No existing subnet, create it if needed, else we can just exit.
            if state == 'present':
                try:
                    new_group = conn.create_db_subnet_group(
                        DBSubnetGroupName=group_name, DBSubnetGroupDescription=group_description, SubnetIds=group_subnets)
                    result = create_result(True, new_group)
                except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
                    module.fail_json_aws(e)
            module.exit_json(**result)
        else:
            module.fail_json_aws(e)
    # We have one or more subnets at this point.
    if state == 'absent':
        try:
            conn.delete_db_subnet_group(DBSubnetGroupName=group_name)
            result = create_result(True)
            module.exit_json(**result)
        except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
            module.fail_json_aws(e)

    # Sort the subnet groups before we compare them
    existing_subnets = []
    for subnet in matching_groups[0].get('Subnets'):
        existing_subnets.append(subnet.get('SubnetIdentifier'))
    existing_subnets.sort()
    group_subnets.sort()
    # See if anything changed.
    if (matching_groups[0].get('DBSubnetGroupName') == group_name and
        matching_groups[0].get('DBSubnetGroupDescription') == group_description and
            existing_subnets == group_subnets):
        result = create_result(False, matching_groups[0])
        module.exit_json(**result)
    # Modify existing group.
    try:
        changed_group = conn.modify_db_subnet_group(
            DBSubnetGroupName=group_name, DBSubnetGroupDescription=group_description, SubnetIds=group_subnets)
        result = create_result(True, changed_group)
        module.exit_json(**result)
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        module.fail_json_aws(e)


if __name__ == '__main__':
    main()
