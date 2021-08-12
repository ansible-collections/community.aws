#!/usr/bin/python
# Copyright (c) 2018 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
module: rds_cluster_info
version_added: 2.0.0
short_description: Obtain information about one or more RDS clusters
description:
  - Obtain information about one or more RDS clusters.
options:
    db_cluster_identifier:
        description:
          - The user-supplied DB cluster identifier.
          - If this parameter is specified, information from only the specific DB cluster is returned.
        aliases:
          - cluster_id
          - id
        type: str
        required: True
    filters:
        description:
            - A filter that specifies one or more DB clusters to describe.
              See U(https://docs.aws.amazon.com/AmazonRDS/latest/APIReference/API_DescribeDBClusters.html)
        type: dict
author:
    - Alina Buzachis (@alinabuzachis)
extends_documentation_fragment:
- amazon.aws.aws
- amazon.aws.ec2

'''

EXAMPLES = r'''

'''

RETURN = r'''

'''


try:
    import botocore
except ImportError:
    pass  # handled by AnsibleAWSModule

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.core import is_boto3_error_code                                                                     
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import ansible_dict_to_boto3_filter_list                                                                 
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AWSRetry
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import camel_dict_to_snake_dict
from ansible_collections.amazon.aws.plugins.module_utils.rds import get_tags


@AWSRetry.jittered_backoff(retries=10)
def _describe_db_clusters(client, **params):
    try:
        paginator = client.get_paginator('describe_db_clusters')
        return paginator.paginate(**params).build_full_result()['DBClusters']
    except is_boto3_error_code('DBClusterNotFoundFault'):
        return []


def cluster_info(client, module):
    cluster_id = module.params.get('db_cluster_identifier')
    filters = module.params.get('filters')

    params = dict()
    if cluster_id:
        params['DBClusterIdentifier'] = cluster_id
    if filters:
        params['Filters'] = ansible_dict_to_boto3_filter_list(filters)

    try:
        result = _describe_db_clusters(client, **params)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, "Couldn't get RDS cluster information.")

    for cluster in result:
        cluster['Tags'] = get_tags(client, module, cluster['DBClusterArn'])

    return dict(changed=False, clusters=[camel_dict_to_snake_dict(cluster, ignore_list=['Tags']) for cluster in result])


def main():
    argument_spec = dict(
        db_cluster_identifier=dict(aliases=['cluster_id', 'id']),
        filters=dict(type='dict')
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    try:
        client = module.client('rds', retry_decorator=AWSRetry.jittered_backoff(retries=10))
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg='Failed to connect to AWS.')

    module.exit_json(**cluster_info(client, module))


if __name__ == '__main__':
    main()
