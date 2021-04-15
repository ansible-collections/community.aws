#!/usr/bin/python
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: rds_option_group_info
version_added: 1.5.0
description:
    - Gather information about RDS option groups.
requirements: [ boto3 ]
author: "Alina Buzachis (@alinabuzachis)"
options:
    option_group_name:
        description:
            - The name of the option group to describe.
            - Can't be supplied together with EngineName or MajorEngineVersion.
        type: str
        required: true
    marker:
        description:
            - If this parameter is specified, the response includes only records beyond the marker, up to the value specified by MaxRecords.
            - Constraints: minimum 20, maximum 100.
        type: str
        required: false
    max_records:
        description:
            - The maximum number of records to include in the response.
        type: int
        default: 100
        required: true
    engine_name:
        description: Filters the list of option groups to only include groups associated with a specific database engine.
        type: str
        required: false
    major_engine_version:
        description:
            - Filters the list of option groups to only include groups associated with a specific database engine version.
            - If specified, then EngineName must also be specified.
        type: str
        required: false
extends_documentation_fragment:
- amazon.aws.aws
- amazon.aws.ec2
'''

EXAMPLES = r'''
# Note: These examples do not set authentication details, see the AWS Guide for details.

- name: List all the option groups
  community.aws.rds_option_group_info:
    region: ap-southeast-2
    profile: production
    option_group_name: test-mysql-option-group
  register: option_group
'''

RETURN = r'''
changed:
    description: True if listing the internet gateways succeeds.
    type: bool
    returned: always
    sample: "false"
option_groups_list:
    description: The internet gateways for the account.
    returned: always
    type: complex
    contains:
        allows_vpc_and_non_vpc_instance_memberships:
            description: Indicates whether this option group can be applied to both VPC and non-VPC instances.
            returned: I(state=present)
            type: bool
            sample: false
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

try:
    import botocore
except ImportError:
    pass  # Handled by AnsibleAWSModule

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.core import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AWSRetry
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import boto3_tag_list_to_ansible_dict
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import camel_dict_to_snake_dict


def list_option_groups(client, module):
    params = dict()
    params['OptionGroupName'] = module.params.get('option_group_name')

    if module.params.get('marker'):
        params['Marker'] = module.params.get('marker')
        if params['Marker'] < 20 or params['Marker'] > 100:
            module.fail_json(msg="marker must be between 10 and 100 minutes")

    if module.params.get('max_records'):
        params['MaxRecords'] = module.params.get('max_records')
        if params['MaxRecords'] > 100:
            module.fail_json(msg="The maximum number of records to include in the response is 100.")

    params['EngineName'] = module.params.get('engine_name')
    params['MajorEngineVersion'] = module.params.get('major_engine_version')

    try:
        result = client.describe_option_groups(aws_retry=True, **params)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't describe option groups.")

    return result


def main():
    argument_spec = dict(
        option_group_name=dict(default='', type='str'),
        marker=dict(type='str', default=''),
        max_records=dict(type=int, default=100),
        engine_name=dict(type='str', default=''),
        major_engine_version=dict(type='str', default=''),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[
            ['option_group_name', 'engine_name'],
            ['option_group_name', 'major_engine_version'],
        ],
        required_together=[
            ['engine_name', 'major_engine_version'],
        ],
    )

    # Validate Requirements
    try:
        connection = module.client('rds', retry_decorator=AWSRetry.jittered_backoff())
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg='Failed to connect to AWS')

    results = list_option_groups(connection, module)

    module.exit_json(**camel_dict_to_snake_dict(results))


if __name__ == '__main__':
    main()
