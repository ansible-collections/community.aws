#!/usr/bin/python
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
module: rds_option_group
version_added: 1.5.0
short_description: Manages RDS option groups
description:
  - Manages the creation, modification, deletion of RDS option groups
author:
  - "Nick Aslanidis (@naslanidis)"
  - "Will Thames (@willthames)"
  - "Alina Buzachis (@alinabuzachis)"
options:
  option_group_name:
    description:
      - Specifies the name of the option group to be created
    required: true
    default: null
  engine_name:
    description:
      - Specifies the name of the engine that this option group should be associated with
    required: true
    default: null
  major_engine_version:
    description:
      - Specifies the major version of the engine that this option group should be associated with
    required: true
    default: null
  option_group_description:
    description:
      - The description of the option group.
    required: true
    default: null
  apply_immediately:
    description:
      - Indicates whether the changes should be applied immediately, or during the next maintenance window
    required: false
    default: false
  options:
    description:
      - Options in this list are added to the option group
      - If already present, the specified configuration is used to update the existing configuration
      - If none are supplied, any existing options are removed
extends_documentation_fragment:
- amazon.aws.aws
- amazon.aws.ec2
'''

EXAMPLES = r'''
# Create an RDS Mysql Option group
- name: Create an RDS Mysql Option group
  community.aws.rds_option_group:
    region: ap-southeast-2
    profile: production
    state: present
    option_group_name: test-mysql-option-group
    engine_name: mysql
    major_engine_version: 5.6
    option_group_description: test mysql option group
    apply_immediately: true
    options:
      - OptionName: MEMCACHED
        Port: 11211
        VpcSecurityGroupMemberships:
          - sg-d188c123
        OptionSettings:
          - Name: MAX_SIMULTANEOUS_CONNECTIONS
            Value: '20'
          - Name: CHUNK_SIZE_GROWTH_FACTOR
            Value: '1.25'
  register: new_rds_mysql_option_group

# Remove currently configured options for an option group by removing options argument
- name: Create an RDS Mysql Option group
  community.aws.rds_option_group:
    region: ap-southeast-2
    profile: production
    state: present
    option_group_name: test-mysql-option-group
    engine_name: mysql
    major_engine_version: 5.6
    option_group_description: test mysql option group
    apply_immediately: true
  register: rds_mysql_option_group

# Delete an RDS Mysql Option group
- name: Delete an RDS Mysql Option group
  community.aws.rds_option_group:
    region: ap-southeast-2
    profile: production
    state: absent
    option_group_name: test-mysql-option-group
  register: deleted_rds_mysql_option_group
'''

RETURN = r'''
allows_vpc_and_non_vpc_instance_memberships:
  description: Specifies the allocated storage size in gigabytes (GB).
  returned: when state=present
  type: boolean
  sample: false
engine_name:
  description: Indicates the name of the engine that this option group can be applied to.
  returned: when state=present
  type: string
  sample: "mysql"
major_engine_version:
  description: Indicates the major engine version associated with this option group.
  returned: when state=present
  type: string
  sample: "5.6"
option_group_description:
  description: Provides a description of the option group.
  returned: when state=present
  type: string
  sample: "test mysql option group"
option_group_name:
  description: Specifies the name of the option group.
  returned: when state=present
  type: string
  sample: "test-mysql-option-group"
options:
  description: Indicates what options are available in the option group.
  returned: when state=present
  type: list
  sample: []
vpc_id:
  description: If present, this option group can only be applied to instances that are in the VPC indicated by this field.
  returned: when state=present
  type: string
  sample: "vpc-aac12acf"
'''

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AWSRetry
from ansible_collections.amazon.aws.plugins.module_utils.core import is_boto3_error_code
from ansible.module_utils.ec2 import camel_dict_to_snake_dict


try:
    import botocore
except ImportError:
    pass  # caught by AnsibleAWSModule

import q


@q
def get_option_group(client, module):
    params = dict()
    params['OptionGroupName'] = module.params.get('option_group_name')

    try:
        _result = client.describe_option_groups(aws_retry=True, **params)
    except is_boto3_error_code('OptionGroupNotFoundFault'):
        return {}
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:  # pylint: disable=duplicate-except
        module.fail_json_aws(e)

    result = _result['OptionGroupsList'][0]
    return result


def create_option_group_options(client, module):
    changed = True
    params = dict()
    params['OptionGroupName'] = module.params.get('option_group_name')
    params['OptionsToInclude'] = module.params.get('options')

    if module.params.get('apply_immediately'):
        params['ApplyImmediately'] = module.params.get('apply_immediately')

    try:
        _result = client.modify_option_group(aws_retry=True, **params)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e)

    result = camel_dict_to_snake_dict(_result['OptionGroup'])

    return changed, result


def remove_option_group_options(client, module, options_to_remove):
    changed = True
    params = dict()
    params['OptionGroupName'] = module.params.get('option_group_name')
    params['OptionsToRemove'] = options_to_remove

    if module.params.get('apply_immediately'):
        params['ApplyImmediately'] = module.params.get('apply_immediately')

    try:
        _result = client.modify_option_group(aws_retry=True, **params)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e)

    result = camel_dict_to_snake_dict(_result['OptionGroup'])

    return changed, result


def create_option_group(client, module):
    changed = True
    params = dict()
    params['OptionGroupName'] = module.params.get('option_group_name')
    params['EngineName'] = module.params.get('engine_name')
    params['MajorEngineVersion'] = str(module.params.get('major_engine_version'))
    params['OptionGroupDescription'] = module.params.get('option_group_description')

    try:
        _result = client.create_option_group(aws_retry=True, **params)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e)

    result = camel_dict_to_snake_dict(_result['OptionGroup'])

    return changed, result


@q
def match_option_group_options(client, module):
    requires_update = False
    new_options = module.params.get('options')

    # Get existing option groups and compare to our new options spec
    current_option = get_option_group(client, module)

    if current_option['Options'] == [] and new_options:
        requires_update = True
    else:
        for option in current_option['Options']:
            for setting_name in new_options:
                if setting_name['OptionName'] == option['OptionName']:

                    # Security groups need to be handled separately due to different keys on request and what is
                    # returned by the API

                    if any(
                        name in option.keys() - ['OptionSettings', 'VpcSecurityGroupMemberships'] and
                        setting_name[name] != option[name]
                        for name in setting_name
                    ):
                        requires_update = True

                    if any(
                        name in option and name == 'VpcSecurityGroupMemberships'
                        for name in setting_name
                    ):
                        current_sg = set(sg['VpcSecurityGroupId'] for sg in option['VpcSecurityGroupMemberships'])
                        new_sg = set(setting_name['VpcSecurityGroupMemberships'])

                        if current_sg != new_sg:
                            requires_update = True

                    if any(
                        new_option_setting['Name'] == current_option_setting['Name'] and
                        new_option_setting['Value'] != current_option_setting['Value']
                        for new_option_setting in setting_name['OptionSettings']
                        for current_option_setting in option['OptionSettings']
                    ):
                        requires_update = True

    return requires_update


@q
def compare_option_group(client, module):
    to_be_added = None
    to_be_removed = None

    current_option = get_option_group(client, module)
    new_options = module.params.get('options')

    new_settings = set([item['OptionName'] for item in new_options])
    old_settings = set([item['OptionName'] for item in current_option['Options']])

    if new_settings != old_settings:
        to_be_added = list(new_settings - old_settings)
        to_be_removed = list(old_settings - new_settings)

    return to_be_added, to_be_removed


@q
def setup_rds_option_group(client, module):
    results = []
    changed = False

    # Check if there is an existing options group
    existing_option_group = get_option_group(client, module)

    if existing_option_group:
        results = existing_option_group

        if module.params.get('options'):
            # Check if existing options require updating
            update_required = match_option_group_options(client, module)

            # Check if there are options to be added or removed
            to_be_added, to_be_removed = compare_option_group(client, module)

            if to_be_added or update_required:
                changed, new_option_group_options = create_option_group_options(client, module)

            if to_be_removed:
                changed, removed_option_group_options = remove_option_group_options(client, module, to_be_removed)

            # If changed, get updated version of option group
            if changed:
                results = get_option_group(client, module)

        else:
            # No options were supplied. If options exist, remove them
            current_option_group = get_option_group(client, module)

            if current_option_group['Options'] != []:
                # Here we would call our remove options function
                options_to_remove = []

                for option in current_option_group['Options']:
                    options_to_remove.append(option['OptionName'])

                changed, removed_option_group_options = remove_option_group_options(client, module, options_to_remove)

                # If changed, get updated version of option group
                if changed:
                    results = get_option_group(client, module)

    else:
        changed, new_option_group = create_option_group(client, module)

        if module.params.get('options'):
            changed, new_option_group_options = create_option_group_options(client, module)
        results = get_option_group(client, module)

    return changed, results


def remove_rds_option_group(client, module):
    changed = False
    params = dict()
    params['OptionGroupName'] = module.params.get('option_group_name')

    # Check if there is an existing options group
    existing_option_group = get_option_group(client, module)

    if existing_option_group:
        changed = True

        try:
            client.delete_option_group(aws_retry=True, **params)
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e)

    return changed, {}


def main():
    argument_spec = dict(
            option_group_name=dict(required=True),
            engine_name=dict(),
            major_engine_version=dict(),
            option_group_description=dict(),
            options=dict(type='list'),
            apply_immediately=dict(type='bool'),
            state=dict(required=True, choices=['present', 'absent']),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    try:
        client = module.client('rds', retry_decorator=AWSRetry.jittered_backoff())
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg='Failed to connect to AWS.')

    state = module.params.get('state')

    if state == 'present':
        changed, results = setup_rds_option_group(client, module)
    else:
        changed, results = remove_rds_option_group(client, module)

    module.exit_json(changed=changed, **camel_dict_to_snake_dict(results))


if __name__ == '__main__':
    main()
