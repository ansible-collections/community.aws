#!/usr/bin/python
# Copyright (c) 2021 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = '''
---
module: elasticsearch_info
version_added: 1.6.0

short_description: Describe AWS Elasticsearch domains
description: Describe AWS Elasticsearch domains
options:
  domain_name:
    description:
      - The name of the AWS Elasticsearch domain.
    required: false
    type: str

author:
  - Kévin Masseix (@mkcg)
extends_documentation_fragment:
- amazon.aws.aws
- amazon.aws.ec2
'''

EXAMPLES = '''
- name: Retrieve informations about a specific Elasticsearch domain
  community.aws.elasticsearch_info:
    domain_name: app_domain

- name: Retrieve informations about all Elasticsearch domains
  community.aws.elasticsearch_info:
'''

RETURN = '''
elasticsearch_domains:
  description: List of Elasticsearch domains descriptions
  returned: always
  type: complex
  contains:
    access_policies:
      type: str
    advanced_options:
      type: complex
      contains:
        rest.action.multi.allow_explicit_index:
          type: str
          sample: 'true'
    advanced_security_options:
      type: complex
      contains:
        enabled:
          type: bool
          sample: true
        internal_user_database_enabled:
          type: bool
          sample: true
    arn:
      returned: always
      type: str
    cognito_options:
      type: complex
      contains:
        enabled:
          type: bool
          sample: false
    created:
      type: bool
      returned: always
      sample: true
    deleted:
      type: bool
      returned: always
      sample: false
    domain_endpoint_options:
      type: complex
      contains:
        custom_endpoint_enabled:
          type: bool
          sample: false
        enforce_https:
          type: bool
          sample: true
        tls_security_policy:
          type: str
    domain_id:
      type: str
    domain_name:
      type: str
    ebs_options:
      type: complex
      contains:
        ebs_enabled:
          type: bool
        volume_size:
          type: int
        volume_type:
          type: str
    elasticsearch_cluster_config:
      type: complex
      contains:
        dedicated_master_enabled:
          type: bool
          sample: false
        instance_count:
          type: int
          sample: 3
        instance_type:
          type: str
          sample: c5.xlarge.elasticsearch
        warm_enabled:
          type: bool
          sample: false
        zone_awareness_config:
          type: complex
          contains:
            availability_zone_count:
              type: int
              sample: 3
        zone_awareness_enabled:
          type: bool
          sample: true
    elasticsearch_version:
      type: str
      sample: '7.9'
    encryption_at_rest_options:
      type: complex
      contains:
        enabled:
          type: bool
          sample: true
        kms_key_id:
          type: str
    endpoints:
      type: complex
      contains:
        vpc:
          type: str
    log_publishing_options:
      type: complex
      contains:
        es_application_logs:
          type: complex
          contains:
            cloud_watch_logs_log_group_arn:
              type: str
            enabled:
              type: bool
              sample: true
        index_slow_logs:
          type: complex
          contains:
            cloud_watch_logs_log_group_arn:
              type: str
            enabled:
              type: bool
              sample: true
        search_slow_logs:
          type: complex
          contains:
            cloud_watch_logs_log_group_arn:
              type: str
            enabled:
              type: bool
              sample: true
    node_to_node_encryption_options:
      type: complex
      contains:
        enabled:
          type: bool
          sample: true
    processing:
      type: bool
      sample: false
    service_software_options:
      type: complex
      contains:
        automated_update_date:
          type: str
          sample: '2021-07-08T10:15:43+02:00'
        cancellable:
          type: bool
          sample: false
        current_version:
          type: str
          sample: R20210426-P2
        description:
          type: str
          sample: There is no software update available for this domain.
        new_version:
          type: str
        optional_deployment:
          type: bool
          sample: false
        update_available:
          type: bool
          sample: false
        update_status:
          type: str
          sample: COMPLETED
    snapshot_options:
      type: complex
      contains:
        automated_snapshot_start_hour:
          type: int
          sample: 23
    tags:
      returned: always
      type: dict
      sample:
        application: api
        environment: prod
    upgrade_processing:
      type: bool
      sample: false
    vpc_options:
      type: complex
      contains:
        availability_zones:
          type: list
          sample: [ eu-west-3a, eu-west-3b, eu-west-3c ]
        security_group_ids:
          type: list
          sample: [ sg-0123456789abcdef0 ]
        subnet_ids:
          type: list
          sample: [ subnet-0123456789abcdef0 ]
        vpc_id:
          type: str
          sample: vpc-0123456789abcdef0
'''

try:
    import botocore
except ImportError:
    pass  # handled by AnsibleAWSModule

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.core import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AWSRetry
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import boto3_tag_list_to_ansible_dict
from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

@AWSRetry.exponential_backoff()
def list_elasticsearch_domain_names(client):
    domain_names = client.list_domain_names()['DomainNames']
    domain_names = list(map(lambda x: x['DomainName'], domain_names))
    return domain_names

@AWSRetry.exponential_backoff()
def describe_elasticsearch_domains(client, domain_name=None):
    domain_names = []

    if domain_name:
        domain_names.append(domain_name)
    else:
        domain_names = list_elasticsearch_domain_names(client)

    return client.describe_elasticsearch_domains(DomainNames=domain_names)['DomainStatusList']

@AWSRetry.exponential_backoff()
def get_domain_tags(client, arn):
    tags = client.list_tags(ARN=arn)['TagList']
    tags = boto3_tag_list_to_ansible_dict(tags)
    return tags

def enrich_domain(client, domain):
    domain = camel_dict_to_snake_dict(domain)
    domain['tags'] = get_domain_tags(client, domain['arn'])

    return domain

def get_elasticsearch_domains(module, client, domain_name=None):
    try:
        domains = describe_elasticsearch_domains(client, domain_name)
    except is_boto3_error_code('ResourceNotFound'):
        return []
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't obtain Elasticsearch domain info")

    return list(map(lambda domain: enrich_domain(client, domain), domains))

def main():
    argument_spec = dict(
        domain_name=dict(required=False)
    )

    module = AnsibleAWSModule(argument_spec=argument_spec, supports_check_mode=True)
    client = module.client('es')
    domain_name = module.params.get('domain_name')

    domains = elasticache_clusters=get_elasticsearch_domains(module, client, domain_name)
    module.exit_json(elasticsearch_domains=domains)

if __name__ == '__main__':
    main()
