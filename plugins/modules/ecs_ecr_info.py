#!/usr/bin/python
# -*- coding: utf-8 -*

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = '''
---
module: ecs_ecr_info
version_added: 2.1.0
short_description: List or Describe Elastic Container Registry repositories
description:
    - List or Describe Elastic Container Registry repositories.
options:
    

'''

EXAMPLES = '''

'''

RETURN = '''

'''

import json
import traceback

try:
    import botocore
except ImportError:
    pass  # Handled by AnsibleAWSModule

from ansible.module_utils.six import string_types

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.core import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import boto_exception
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import compare_policies
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import sort_json_policy_dict


def build_kwargs(params):
    """
    Builds a kwargs dict which may contain the optional registryId.

    :param registry_id: Optional string containing the registryId.
    :return: kwargs dict with registryId, if given
    """
    registry_id = params['registry_id']
    repository_names = params['repository_names']
    repository_name = params['repository_name']

    repositoryNames = []
    return_dict = {}

    repositoryNames = [ *repositoryNames, *repository_names]

    if len(repositoryNames) > 0:
        return_dict['repositoryNames'] = repositoryNames
    if registry_id:
        return_dict['registryId'] = registry_id
    
    return return_dict


def main():

    argument_spec = dict(
        registry_id=dict(required=False),
        repository_names=dict(required=False, type='list', default=[]),
        repository_name=dict(required=False)
    )

    mutually_exclusive = [['repository_name','repository_names']]

    module = AnsibleAWSModule(argument_spec=argument_spec, supports_check_mode=True, mutually_exclusive=mutually_exclusive)


    ecr_module = module.client('ecr')
    
    repositories = []

    get_repos = {}

    get_repos = ecr_module.describe_repositories(**build_kwargs(module.params))

    if get_repos['ResponseMetadata']['HTTPStatusCode'] == 200:
        repositories = [ *repositories, *get_repos['repositories'] ]

    if get_repos.get('nextToken')

    result = {}
    result['msg'] = repositories

    module.exit_json(**result)

if __name__ == '__main__':
    main()
