#!/usr/bin/python
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: s3_metrics_configuration
version_added: 1.0.0
short_description: Manage s3 bucket metrics configuration in AWS
description:
    - Manage s3 bucket metrics configuration in AWS which allows to get the CloudWatch request metrics for the objects in a bucket
author: Dmytro Vorotyntsev (@vorotech)
notes:
    - This modules manages single metrics configuration, the s3 bucket might have up to 1,000 metrics configurations
    - To request metrics for the entire bucket, create a metrics configuration without a filter
    - Metrics configurations are necessary only to enable request metric, bucket-level daily storage metrics are always turned on
options:
  bucket_name:
    description:
      - "Name of the s3 bucket"
    required: true
    type: str
  id:
    description:
      - "The ID used to identify the metrics configuration"
    required: true
    type: str
  filter_prefix:
    description:
      - "A prefix used when evaluating a metrics filter"
    required: false
    type: str
  filter_tags:
    description:
      - "A dictionary of one or more tags used when evaluating a metrics filter"
    required: false
    aliases: ['filter_tag']
    type: dict
  state:
    description:
      - "Create or delete metrics configuration"
    default: present
    choices: ['present', 'absent']
    type: str
extends_documentation_fragment:
- amazon.aws.aws
- amazon.aws.ec2

'''

EXAMPLES = r'''
# Note: These examples do not set authentication details, see the AWS Guide for details.

- name: Create a metrics configuration that enables metrics for an entire bucket
  community.aws.s3_metrics_configuration:
    bucket_name: my-bucket
    id: EntireBucket
    state: present

- name: Put a metrics configuration that enables metrics for objects starting with a prefix
  community.aws.s3_metrics_configuration:
    bucket_name: my-bucket
    id: Assets
    filter_prefix: assets
    state: present

- name: Put a metrics configuration that enables metrics for objects with specific tag
  community.aws.s3_metrics_configuration:
    bucket_name: my-bucket
    id: Assets
    filter_tag:
      kind: asset
    state: present

- name: Put a metrics configuration that enables metrics for objects that start with a particular prefix and have specific tags applied
  community.aws.s3_metrics_configuration:
    bucket_name: my-bucket
    id: ImportantBlueDocuments
    filter_prefix: documents
    filter_tags:
      priority: high
      class: blue
    state: present

- name: Delete metrics configuration
  community.aws.s3_metrics_configuration:
    bucket_name: my-bucket
    id: EntireBucket
    state: absent

'''

try:
    import boto3
    import botocore
    from botocore.exceptions import ClientError, BotoCoreError
except ImportError:
    pass  # Handled by AnsibleAWSModule

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.core import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AWSRetry
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import ansible_dict_to_boto3_tag_list
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import boto3_tag_list_to_ansible_dict


def _create_metrics_configuration(mc_id, filter_prefix, filter_tags):
    payload = {
        'Id': mc_id
    }
    if len(filter_tags) == 1 and filter_prefix is None:
        payload['Filter'] = {
            'Tag': ansible_dict_to_boto3_tag_list(filter_tags)[0]
        }
    elif len(filter_tags) == 0 and filter_prefix is not None:
        payload['Filter'] = {
            'Prefix': filter_prefix
        }
    elif len(filter_tags) > 0:
        payload['Filter'] = {
            'And': {
                'Tags': ansible_dict_to_boto3_tag_list(filter_tags)
            }
        }
    if filter_prefix is not None:
        payload['Filter']['And']['Prefix'] = filter_prefix

    return payload


def _compare_metrics_configuration(metrics_configuration, mc_id, filter_prefix, filter_tags):
    payload = metrics_configuration['MetricsConfiguration']
    parsed = {'mc_id': payload.get('Id')}
    if payload.get('Filter', {}).get('Prefix') is not None:
        parsed['filter_prefix'] = payload['Filter']['Prefix']
    if payload.get('Filter', {}).get('Tag') is not None:
        parsed['filter_tags'] = boto3_tag_list_to_ansible_dict([payload['Filter']['Tag']])
    if payload.get('Filter', {}).get('And') is not None:
        parsed['filter_tags'] = boto3_tag_list_to_ansible_dict(payload['Filter']['And'].get('Tags', []))
        if payload['Filter']['And'].get('Prefix') is not None:
            parsed['filter_prefix'] = payload['Filter']['And']['Prefix']

    if parsed.get('mc_id') != mc_id:
        return False
    if parsed.get('filter_prefix') != filter_prefix:
        return False
    if parsed.get('filter_tags', {}) != filter_tags:
        return False
    return True


def create_or_update_metrics_configuration(client, module):
    changed = False
    bucket_name = module.params.get('bucket_name')
    mc_id = module.params.get('id')
    filter_prefix = module.params.get('filter_prefix')
    filter_tags = module.params.get('filter_tags')

    try:
        metrics_configuration = client.get_bucket_metrics_configuration(Bucket=bucket_name, Id=mc_id)
    except is_boto3_error_code('NoSuchConfiguration'):
        metrics_configuration = None
    except ClientError as e:  # pylint: disable=duplicate-except
        module.fail_json_aws(e, msg="Failed to get bucket metrics configuration")

    if metrics_configuration:
        if not _compare_metrics_configuration(metrics_configuration, mc_id, filter_prefix, filter_tags):
            try:
                if not module.check_mode:
                    client.put_bucket_metrics_configuration(
                        Bucket=bucket_name,
                        Id=mc_id,
                        MetricsConfiguration=_create_metrics_configuration(mc_id, filter_prefix, filter_tags)
                    )
                changed = True
            except (BotoCoreError, ClientError) as e:
                module.fail_json_aws(e, msg="Failed to udpate bucket metrics configuration '%s'" % mc_id)
    else:
        try:
            if not module.check_mode:
                client.put_bucket_metrics_configuration(
                    Bucket=bucket_name,
                    Id=mc_id,
                    MetricsConfiguration=_create_metrics_configuration(mc_id, filter_prefix, filter_tags)
                )
            changed = True
        except (BotoCoreError, ClientError) as e:
            module.fail_json_aws(e, msg="Failed to create bucket metrics configuration '%s'" % mc_id)

    module.exit_json(changed=changed)


def delete_metrics_configuration(client, module):
    changed = False
    bucket_name = module.params.get('bucket_name')
    mc_id = module.params.get('id')

    try:
        client.get_bucket_metrics_configuration(Bucket=bucket_name, Id=mc_id)
    except is_boto3_error_code('NoSuchConfiguration'):
        module.exit_json(changed=changed)
    except ClientError as e:  # pylint: disable=duplicate-except
        module.fail_json_aws(e, msg="Failed to get bucket metrics configuration")

    try:
        if not module.check_mode:
            client.delete_bucket_metrics_configuration(Bucket=bucket_name, Id=mc_id)
        changed = True
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg="Failed to delete bucket metrics configuration '%s'" % mc_id)

    module.exit_json(changed=changed)


def main():
    argument_spec = dict(
        bucket_name=dict(type='str', required=True),
        id=dict(type='str', required=True),
        filter_prefix=dict(type='str', required=False),
        filter_tags=dict(default={}, type='dict', required=False, aliases=['filter_tag']),
        state=dict(default='present', type='str', choices=['present', 'absent']),
    )
    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True
    )

    state = module.params.get('state')

    try:
        client = module.client('s3', retry_decorator=AWSRetry.exponential_backoff(retries=10, delay=3))
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg='Failed to connect to AWS')

    if state == 'present':
        create_or_update_metrics_configuration(client, module)
    elif state == 'absent':
        delete_metrics_configuration(client, module)


if __name__ == '__main__':
    main()
