#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Davinder Pal <dpsangwal@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = """
module: sns_platform_endpoint_info
short_description: Get Infomation about AWS SNS Platforms.
description:
  - Get Information about AWS SNS Platform Endpoint.
version_added: 1.4.0
options:
  endpoint_arn:
    description:
      - arn of sns platform application.
    required: true
    aliases: [ "arn" ]
    type: str
  enabled:
    description:
      - filter to look for enabled or disabled endpoints.
    required: false
    type: str
    choices: ['true', 'false']
author: "Davinder Pal <dpsangwal@gmail.com>"
extends_documentation_fragment:
  - amazon.aws.ec2
  - amazon.aws.aws
requirements:
  - boto3
  - botocore
"""

EXAMPLES = """
- name: Get list of Endpoints SNS platform Endpoints.
  community.aws.sns_platform_endpoint_info:
    arn: arn:aws:sns:us-east-1:xxxxx:app/APNS/xxxxx-platform-app

- name: Get list of Endpoints SNS platform Endpoints but enabled only.
  community.aws.sns_platform_endpoint_info:
    arn: arn:aws:sns:us-east-1:xxxxx:app/APNS/xxxxx-platform-app
    enabled: 'true'
"""

RETURN = """
endpoints:
  description: List of SNS Platform Endpoints.
  returned: when success
  type: list
  sample: [{
    "Attributes": {"Enabled": "true", "Token": "coaO_xxxxxxxxxxx"},
    "EndpointArn": "arn:aws:sns:us-east-1:xxxxx:endpoint/GCM/xxxxx-platform-app/xxxxx-971fa6329ac4"
  }]
"""

try:
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:
    pass    # Handled by AnsibleAWSModule

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule


def main():
    argument_spec = dict(
        endpoint_arn=dict(required=True, aliases=['arn']),
        enabled=dict(required=False, choices=['true', 'false']),
    )

    module = AnsibleAWSModule(argument_spec=argument_spec)
    sns = module.client('sns')

    __default_return = []

    try:
        paginator = sns.get_paginator('list_endpoints_by_platform_application')
        iterator = paginator.paginate(PlatformApplicationArn=module.params['arn'])
        for response in iterator:
            __default_return += response['Endpoints']
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg='Failed to fetch sns platform endpoints')

    if module.params['enabled'] is not None:
        __override_default_return = []
        for endpoint in __default_return:
            if endpoint['Attributes']['Enabled'] == module.params['enabled']:
                __override_default_return.append(endpoint)

        module.exit_json(endpoints=__override_default_return)

    module.exit_json(endpoints=__default_return)


if __name__ == '__main__':
    main()
