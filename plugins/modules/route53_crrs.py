#!/usr/bin/python
# This file is part of Ansible
# GNU General Public License v3.0+ (see COPYING or
# https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
from ansible_collections.amazon.aws.plugins.module_utils.aws.core import (
    AnsibleAWSModule,
)

__metaclass__ = type

DOCUMENTATION = '''
module: route53_crrs
short_description: create, update or delete route53 resource record sets.
description: create, update or delete route53 resource record sets.
requirements: [boto3, botocore, python>=3.5]
options:
  action:
    description: >
      - The action to perform:
        CREATE  Creates a resource record set that has the specified values.
        DELETE  Deletes a existing resource record set.
        UPSERT  If a resource record set doesn't already exist, Route 53
                creates it. If a resource record set does exist, Route 53
                updates it with the values in the request.
    required: true
    choices: ['CREATE', 'DELETE', 'UPSERT']
    type: str
  name:
    description: >
      - The name of the record that you want to create, update, or delete.
    required: true
    type: str
  type:
    description: >
      - The DNS record type.
    required: true
    choices: ['SOA', 'A', 'TXT', 'NS', 'CNAME', 'MX',
              'NAPTR', 'PTR', 'SRV', 'SPF', 'AAAA', 'CAA']
    type: str
  ttl:
    description: >
      - The resource record cache time to live (TTL), in seconds.
    required: true
    type: int
  resource_records:
    description: >
      - list of the current or new DNS record value(ip address).
    required: true
    type: list
  hosted_zone_id:
    description: >
      - The ID of the hosted zone that contains the resource
        record sets that you want to change.
    required: true
    type: str
  set_identifier:
    description: >
      - A unique string to identify each resource record set.
        it is required if acting upon any of the 'weight', 'region',
        'failover', 'geo_location', 'multi_value_answer'.
    type: str
  weight:
    description: >
      - A value that determines the proportion of DNS queries
        that Amazon Route 53 responds to using the current
        resource record set.
    required: true
    type: int
  region:
    description: >
      - Route 53 selects the latency resource record set that has the
        lowest latency between the end user and the associated Amazon
        EC2 Region.
    required: true
    choices: [
      'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
      'ca-central-1', 'eu-west-1', 'eu-west-2', 'eu-west-3',
      'eu-central-1', 'ap-southeast-1', 'ap-southeast-2',
      'ap-northeast-1', 'ap-northeast-2', 'ap-northeast-3',
      'eu-north-1', 'sa-east-1', 'cn-north-1', 'cn-northwest-1',
      'ap-east-1', 'me-south-1', 'ap-south-1', 'af-south-1',
      'eu-south-1'
    ]
    type: str
  geo_location:
    description: >
      - A complex type that lets you control how Amazon Route 53 responds
        to DNS queries based on the geographic origin of the query.
        Select either of continent_code or country_code.
        subdivision_code is only acceptable when country_code is US.
        continent_code:
            type: str
        country_code:
            type: str
        subdivision_code:
            type:str
    type: dict
  failover:
    description: >
      - Add the Failover element to resource record sets.
        One has to be PRIMARY and one has to be SECONDARY.
        In addition, you include the HealthCheckId element and specify
        the health check that you want Amazon Route 53 to perform for
        each resource record set.
    choices: ['PRIMARY', 'SECONDARY']
    type: str
  health_check_id:
    description: >
      - If you want Amazon Route 53 to return this resource record set
        in response to a DNS query only when the status of a health check
        is healthy, include the HealthCheckId element and specify the ID
        of the applicable health check.
    type: str
  multi_value_answer:
    description: >
      - To route traffic approximately randomly to multiple resources.
    type: bool
  alias_target:
    description: >
      - Alias resource record set.
        hosted_zone_id:
        type: str
        dns_name:
        type: str
        evaluate_target_health:
        type: str
    type: dict
author:
    - Sydo Luciani (@sydoluciani)
extends_documentation_fragment:
    - aws
    - ec2
'''

EXAMPLES = '''
- name: Create a simple resource record set
  route53_crrs:
    action: CREATE
    name: www.domain_name.com.
    type: A
    ttl: 987
    resource_records:
      - 1.1.1.1
    hosted_zone_id: XXXXXXXXXXXXXXXXXXXXX
    set_identifier: "Unique Identifier String"
  register: std_out_of_above

- name: Update a simple resource record set
  route53_crrs:
    action: UPSERT
    name: www.domain_name.com.
    type: A
    ttl: 987
    resource_records:
      - 1.1.1.1
      - 2.2.2.2
    hosted_zone_id: XXXXXXXXXXXXXXXXXXXXX
    set_identifier: "Unique Identifier String"
  register: std_out_of_above

- name: Create a geo location resource record set
  route53_crrs:
    action: CREATE
    name: www.domain_name.com.
    type: A
    ttl: 987
    resource_records:
      - 1.1.1.1
    hosted_zone_id: XXXXXXXXXXXXXXXXXXXXX
    set_identifier: "Unique Identifier String"
    geo_location:
      continent_code: NA
  register: std_out_of_above

- name: Update a geo location resource record set
  route53_crrs:
    action: UPSERT
    name: www.domain_name.com.
    type: A
    ttl: 987
    resource_records:
      - 1.1.1.1
    hosted_zone_id: XXXXXXXXXXXXXXXXXXXXX
    set_identifier: "Unique Identifier String"
    geo_location:
      country_code: US
      subdivision_code: TX
  register: std_out_of_above

- name: Update to a failover resource record set
  route53_crrs:
    action: UPSERT
    name: www.domain_name.com.
    type: A
    ttl: 987
    resource_records:
      - 1.1.1.1
    hosted_zone_id: XXXXXXXXXXXXXXXXXXXXX
    set_identifier: "Unique Identifier String"
    failover: PRIMARY
    health_check_id: cdac2615-e127-4ede-ba91-298908970560
  register: std_out_of_above

- name: Update to a weighted resource record set
  route53_crrs:
    action: UPSERT
    name: www.domain_name.com.
    type: A
    ttl: 987
    resource_records:
      - 1.1.1.1
    hosted_zone_id: XXXXXXXXXXXXXXXXXXXXX
    set_identifier: "Unique Identifier String"
    weight: 123
  register: std_out_of_above

- name: Update to a multi variable resource record set
  route53_crrs:
    action: UPSERT
    name: www.domain_name.com.
    type: A
    ttl: 987
    resource_records:
      - 1.1.1.1
    hosted_zone_id: XXXXXXXXXXXXXXXXXXXXX
    set_identifier: "Unique Identifier String"
    multi_value_answer: true
  register: std_out_of_above

- name: Delete a resource record set
  route53_crrs:
    action: DELETE
    name: www.domain_name.com.
    type: A
    ttl: 987
    resource_records:
      - 1.1.1.1
      - 2.2.2.2
      - 3.3.3.3
    hosted_zone_id: XXXXXXXXXXXXXXXXXXXXX
    set_identifier: "Unique Identifier String"
  register: std_out_of_above

- name: Delete an alias target
  route53_crrs:
    action: DELETE
    name: www.domain_name.com.
    type: A
    hosted_zone_id: XXXXXXXXXXXXXXXXXXXXX
    alias_target:
      hosted_zone_id: XXXXXXXXXXXXXXXXXXXXX
      dns_name: www.domain_name.com
      evaluate_target_health: false
  register: std_out_of_above
'''

RETURN = '''
sample:
    {
        'ChangeInfo': {
            'Id': 'string',
            'Status': 'PENDING OR INSYNC',
            'SubmittedAt': datetime(2015, 1, 1),
            'Comment': 'string'
        }
    }
'''

try:
    from botocore.exceptions import BotoCoreError, ClientError  # noqa
except ImportError:
    pass  # caught by AnsibleAWSModule


def get_batch_info(module):
    change_batch = dict()
    resource_record_set = dict()
    change_batch['Changes'] = list()

    if (module.params['alias_target'] is not None and
            (module.params.get('ttl') is not None or
                module.params['resource_records'] is not None)):
        module.fail_json(
            msg="ttl and resource_records are not required "
                "when creating alias_target."
        )
    elif (module.params['alias_target'] is None and
            (module.params.get('ttl') is None or
                module.params['resource_records'] is None)):
        module.fail_json(
            msg="ttl and resource_records are required "
                "when creating a resource record set."
        )

    resource_record_set.update({'Name': module.params.get('name')})
    resource_record_set.update({'Type': module.params.get('type')})

    if module.params.get('ttl') is not None:
        resource_record_set.update({'TTL': module.params.get('ttl')})

    if (module.params['resource_records'] is not None and
            isinstance(module.params['resource_records'], list)):
        resource_record_set['ResourceRecords'] = list()
        for rr in module.params['resource_records']:
            resource_record_set['ResourceRecords'].append(
                {'Value': rr}
            )

    if module.params.get('comment') is not None:
        change_batch['Comment'] = module.params.get('comment')

    if (module.params.get('weight') is not None and
            module.params.get('set_identifier') is not None):
        resource_record_set.update(
            {'SetIdentifier': module.params.get('set_identifier')}
        )
        resource_record_set.update({'Weight': module.params.get('weight')})
        if module.params.get('health_check_id') is not None:
            resource_record_set.update(
                {'HealthCheckId': module.params.get('health_check_id')}
            )

    if (module.params.get('region') is not None and
            module.params.get('set_identifier') is not None):
        resource_record_set.update(
            {'SetIdentifier': module.params.get('set_identifier')}
        )
        resource_record_set.update({'Region': module.params.get('region')})
        if module.params.get('health_check_id') is not None:
            resource_record_set.update(
                {'HealthCheckId': module.params.get('health_check_id')}
            )

    if (module.params['geo_location'] is not None and
            module.params.get('set_identifier') is not None and
            isinstance(module.params['geo_location'], dict) and
            len(module.params['geo_location']) < 3):

        resource_record_set['GeoLocation'] = {}

        resource_record_set.update(
            {'SetIdentifier': module.params.get('set_identifier')}
        )

        for key in module.params['geo_location']:
            if key == 'continent_code':
                resource_record_set['GeoLocation'].update(
                    {'ContinentCode':
                        module.params['geo_location']['continent_code']}
                )

            if key == 'country_code':
                resource_record_set['GeoLocation'].update(
                    {'CountryCode':
                        module.params['geo_location']['country_code']}
                )

            if key == 'subdivision_code':
                resource_record_set['GeoLocation'].update(
                    {'SubdivisionCode':
                        module.params['geo_location']['subdivision_code']}
                )

        if module.params.get('health_check_id') is not None:
            resource_record_set.update(
                {'HealthCheckId': module.params.get('health_check_id')}
            )

    elif (module.params['geo_location'] is not None and
            module.params.get('set_identifier') is not None and
            isinstance(module.params['geo_location'], dict) and
            len(module.params['geo_location']) >= 3):
        module.fail_json(
            msg="Either continent_code or country_code needs to be specified."
                "subdivision_code is only supported when country_code is US."
        )

    if (module.params.get('failover') is not None and
            module.params.get('set_identifier') is not None):
        resource_record_set.update(
            {'SetIdentifier': module.params.get('set_identifier')}
        )
        resource_record_set.update(
            {'Failover': module.params.get('failover')})
        if module.params.get('health_check_id') is not None:
            resource_record_set.update(
                {'HealthCheckId': module.params.get('health_check_id')}
            )

    if (module.params.get('multi_value_answer') is not None and
            module.params.get('set_identifier') is not None):
        resource_record_set.update(
            {'SetIdentifier': module.params.get('set_identifier')}
        )
        resource_record_set.update(
            {'MultiValueAnswer': module.params.get('multi_value_answer')})

        if module.params.get('health_check_id') is not None:
            resource_record_set.update(
                {'HealthCheckId': module.params.get('health_check_id')}
            )

    if (module.params['alias_target'] is not None and
            isinstance(module.params['alias_target'], dict)):

        resource_record_set['AliasTarget'] = {}

        for key in module.params['alias_target']:
            if key == 'hosted_zone_id':
                resource_record_set['AliasTarget'].update(
                    {'HostedZoneId':
                        module.params['alias_target']['hosted_zone_id']}
                )

            if key == 'dns_name':
                resource_record_set['AliasTarget'].update(
                    {'DNSName':
                        module.params['alias_target']['dns_name']}
                )

            if key == 'evaluate_target_health':
                resource_record_set['AliasTarget'].update({
                    'EvaluateTargetHealth':
                        module.params['alias_target']['evaluate_target_health']
                })

        if module.params.get('health_check_id') is not None:
            resource_record_set.update(
                {'HealthCheckId': module.params.get('health_check_id')}
            )

    change_batch['Changes'].append({
        'Action': module.params.get('action'),
        'ResourceRecordSet': resource_record_set
    })

    return change_batch


def main():
    argument_spec = dict(
        comment=dict(),
        action=dict(
            choices=['CREATE', 'DELETE', 'UPSERT'], required=True),
        name=dict(),
        type=dict(
            choices=['SOA', 'A', 'TXT', 'NS', 'CNAME', 'MX',
                     'NAPTR', 'PTR', 'SRV', 'SPF', 'AAAA', 'CAA']),
        ttl=dict(type=int),
        resource_records=dict(type=list),
        hosted_zone_id=dict(),
        set_identifier=dict(),
        weight=dict(type=int),
        region=dict(
            choices=[
                'us-east-1', 'us-east-2', 'us-west-1', 'us-west-2',
                'ca-central-1', 'eu-west-1', 'eu-west-2', 'eu-west-3',
                'eu-central-1', 'ap-southeast-1', 'ap-southeast-2',
                'ap-northeast-1', 'ap-northeast-2', 'ap-northeast-3',
                'eu-north-1', 'sa-east-1', 'cn-north-1', 'cn-northwest-1',
            ]
        ),
        geo_location=dict(type=dict),
        failover=dict(choices=['PRIMARY', 'SECONDARY']),
        health_check_id=dict(),
        multi_value_answer=dict(type=bool),
        alias_target=dict(type=dict),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        required_if=(
            ('action', 'CREATE', ['name', 'type', 'hosted_zone_id']),
            ('action', 'DELETE', ['name', 'type', 'hosted_zone_id']),
            ('action', 'UPSERT', ['name', 'type', 'hosted_zone_id']),
        ),
        mutually_exclusive=[
            ('weight', 'region', 'failover',
             'geo_location', 'multi_value_answer')
        ],
        required_by=dict(
            weight=('set_identifier',),
            region=('set_identifier',),
            failover=('set_identifier'),
            geo_location=('set_identifier',),
            multi_value_answer=('set_identifier',),
        ),
        supports_check_mode=False
    )

    client = module.client("route53")

    result = client.change_resource_record_sets(
        HostedZoneId=module.params.get('hosted_zone_id'),
        ChangeBatch=get_batch_info(module)
    )

    module.exit_json(**result)


if __name__ == "__main__":
    main()
