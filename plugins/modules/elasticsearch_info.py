#!/usr/bin/python
# Copyright (c) 2021 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = '''
---
module: aws_elasticsearch_info
version_added: 1.0.0

short_description: Describe AWS Elasticsearch domains
description: Describe AWS Elasticsearch domains
options:
  domain_name:
    description: The name of the AWS Elasticsearch domain.
    type: str

author:
  - Kévin Masseix (@mkcg)
extends_documentation_fragment:
- amazon.aws.aws
- amazon.aws.ec2
'''

EXAMPLES = '''
# Retrieve informations about some cluster
- community.aws.elasticsearch_info:
    domain_name: name
'''

RETURN = '''
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
