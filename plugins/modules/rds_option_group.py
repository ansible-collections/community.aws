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
- name: Create an RDS Mysql Option Group
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
        - option_name: MEMCACHED
          port: 11211
          vpc_security_group_memberships:
            - "sg-d188c123"
          option_settings:
            - name: MAX_SIMULTANEOUS_CONNECTIONS
              value: "20"
            - name: CHUNK_SIZE_GROWTH_FACTOR
              value: "1.25"
  register: new_rds_mysql_option_group

# Remove currently configured options for an option group by removing options argument
- name: Create an RDS Mysql Option Group
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
- name: Delete an RDS Mysql Option Group
  community.aws.rds_option_group:
    region: ap-southeast-2
    profile: production
    state: absent
    option_group_name: test-mysql-option-group
  register: deleted_rds_mysql_option_group
'''

RETURN = r'''
allows_vpc_and_non_vpc_instance_memberships:
    description: Indicates whether this option group can be applied to both VPC and non-VPC instances.
    returned: I(state=present)
    type: bool
    sample: false
changed:
    description: If the Option Group has changed.
    type: bool
    returned: always
    sample: true
engine_name:
    description: Indicates the name of the engine that this option group can be applied to.
    returned: I(state=present)
    type: str
    sample: "mysql"
major_engine_version:
    description: Indicates the major engine version associated with this option group.
    returned: I(state=present)
    type: str
    sample: "5.6"
option_group_arn:
    description: The Amazon Resource Name (ARN) for the option group.
    returned: I(state=present)
    type: str
    sample: "arn:aws:rds:ap-southeast-2:721066863947:og:ansible-test-option-group"
option_group_description:
    description: Provides a description of the option group.
    returned: I(state=present)
    type: str
    sample: "test mysql option group"
option_group_name:
    description: Specifies the name of the option group.
    returned: I(state=present)
    type: str
    sample: "test-mysql-option-group"
options:
    description: Indicates what options are available in the option group.
    returned: I(state=present)
    type: complex
    contains:
        db_security_group_memberships:
            description: If the option requires access to a port, then this DB security group allows access to the port.
            returned: I(state=present)
            type: complex
            sample: list
            elements: dict
            contains:
                status:
                    description: The status of the DB security group.
                    returned: I(state=present)
                    type: str
                    sample: "available"
                db_security_group_name:
                    description: The name of the DB security group.
                    returned: I(state=present)
                    type: str
                    sample: "mydbsecuritygroup"
        option_description:
            description: The description of the option.
            returned: I(state=present)
            type: str
            sample: "Innodb Memcached for MySQL"
        option_name:
            description: The name of the option.
            returned: I(state=present)
            type: str
            sample: "MEMCACHED"
        option_settings:
            description: The name of the option.
            returned: I(state=present)
            type: complex
            contains:
                allowed_values:
                    description: The allowed values of the option setting.
                    returned: I(state=present)
                    type: str
                    sample: "1-2048"
                apply_type:
                    description: The DB engine specific parameter type.
                    returned: I(state=present)
                    type: str
                    sample: "STATIC"
                data_type:
                    description: The data type of the option setting.
                    returned: I(state=present)
                    type: str
                    sample: "INTEGER"
                default_value:
                    description: The default value of the option setting.
                    returned: I(state=present)
                    type: str
                    sample: "1024"
                description:
                    description: The description of the option setting.
                    returned: I(state=present)
                    type: str
                    sample: "Verbose level for memcached."
                is_collection:
                    description: Indicates if the option setting is part of a collection.
                    returned: I(state=present)
                    type: bool
                    sample: true
                is_modifiable:
                    description: A Boolean value that, when true, indicates the option setting can be modified from the default.
                    returned: I(state=present)
                    type: bool
                    sample: true
                name:
                    description: The name of the option that has settings that you can set.
                    returned: I(state=present)
                    type: str
                    sample: "INNODB_API_ENABLE_MDL"
                value:
                    description: The current value of the option setting.
                    returned: I(state=present)
                    type: str
                    sample: "0"
        permanent:
            description: Indicate if this option is permanent.
            returned: I(state=present)
            type: bool
            sample: true
        persistent:
            description: Indicate if this option is persistent.
            returned: I(state=present)
            type: bool
            sample: true
        port:
            description: If required, the port configured for this option to use.
            returned: I(state=present)
            type: int
            sample: 11211
        vpc_security_group_memberships:
            description: If the option requires access to a port, then this VPC security group allows access to the port.
            returned: I(state=present)
            type: list
            elements: dict
            contains:
                status:
                    description: The status of the VPC security group.
                    returned: I(state=present)
                    type: str
                    sample: "available"
                vpc_security_group_id:
                    description: The name of the VPC security group.
                    returned: I(state=present)
                    type: str
                    sample: "sg-0cd636a23ae76e9a4"
vpc_id:
    description: If present, this option group can only be applied to instances that are in the VPC indicated by this field.
    returned: I(state=present)
    type: str
    sample: "vpc-bf07e9d6"
'''

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AWSRetry
from ansible_collections.amazon.aws.plugins.module_utils.core import is_boto3_error_code
from ansible.module_utils.ec2 import camel_dict_to_snake_dict
from ansible.module_utils.ec2 import snake_dict_to_camel_dict


try:
    import botocore
except ImportError:
    pass  # caught by AnsibleAWSModule


def get_option_group(client, module):
    params = dict()
    params['OptionGroupName'] = module.params.get('option_group_name')

    try:
        _result = client.describe_option_groups(aws_retry=True, **params)
    except is_boto3_error_code('OptionGroupNotFoundFault'):
        return {}
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:  # pylint: disable=duplicate-except
        module.fail_json_aws(e, msg="Couldn't describe option groups.")

    result = _result['OptionGroupsList'][0]
    return result


def create_option_group_options(client, module):
    changed = True
    params = dict()
    params['OptionGroupName'] = module.params.get('option_group_name')
    _options_to_include = module.params.get('options')
    params['OptionsToInclude'] = snake_dict_to_camel_dict(_options_to_include, capitalize_first=True)

    if module.params.get('apply_immediately'):
        params['ApplyImmediately'] = module.params.get('apply_immediately')

    try:
        _result = client.modify_option_group(aws_retry=True, **params)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Unable to update Option Group.")

    return changed


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

    return changed


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
        module.fail_json_aws(e, msg='Unable to create Option Group.')

    return changed


def match_option_group_options(client, module):
    requires_update = False
    _new_options = module.params.get('options')
    new_options = snake_dict_to_camel_dict(_new_options, capitalize_first=True)

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


def compare_option_group(client, module):
    to_be_added = None
    to_be_removed = None
    current_option = get_option_group(client, module)
    _new_options = module.params.get('options')
    new_options = snake_dict_to_camel_dict(_new_options, capitalize_first=True)
    new_settings = set([item['OptionName'] for item in new_options])
    old_settings = set([item['OptionName'] for item in current_option['Options']])

    if new_settings != old_settings:
        to_be_added = list(new_settings - old_settings)
        to_be_removed = list(old_settings - new_settings)

    return to_be_added, to_be_removed


def setup_option_group(client, module):
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
                changed = create_option_group_options(client, module)

            if to_be_removed:
                changed = remove_option_group_options(client, module, to_be_removed)

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

                changed = remove_option_group_options(client, module, options_to_remove)

                # If changed, get updated version of option group
                if changed:
                    results = get_option_group(client, module)

    else:
        changed = create_option_group(client, module)

        if module.params.get('options'):
            changed = create_option_group_options(client, module)

        results = get_option_group(client, module)

    return changed, results


def remove_option_group(client, module):
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
            module.fail_json_aws(e, msg="Unable to delete Option Group.")

    return changed, {}


def main():
    argument_spec = dict(
            option_group_name=dict(required=True, type='str'),
            engine_name=dict(type='str'),
            major_engine_version=dict(type='str'),
            option_group_description=dict(type='str'),
            options=dict(type='list'),
            apply_immediately=dict(type='bool', default=False),
            state=dict(required=True, choices=['present', 'absent']),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[['state', 'present', ['engine_name', 'major_engine_version', 'option_group_description']]],
    )

    try:
        client = module.client('rds', retry_decorator=AWSRetry.jittered_backoff())
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg='Failed to connect to AWS.')

    state = module.params.get('state')

    if state == 'present':
        changed, results = setup_option_group(client, module)
    else:
        changed, results = remove_option_group(client, module)

    module.exit_json(changed=changed, **camel_dict_to_snake_dict(results))


if __name__ == '__main__':
    main()
