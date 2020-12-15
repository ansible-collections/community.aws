#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Davinder Pal <dpsangwal@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = """
module: sns_platform_info
short_description: Get Infomation about AWS SNS Platforms.
description:
  - Get Information about AWS SNS Platforms.
version_added: 1.4.0
options:
  enabled:
    description:
      - filter to look for enabled or disabled endpoints?
    required: false
    type: str
    choices: ['true', 'false']
author:
  - "Davinder Pal <dpsangwal@gmail.com>"
extends_documentation_fragment:
  - amazon.aws.ec2
  - amazon.aws.aws
requirements:
  - boto3
  - botocore
"""

EXAMPLES = """
- name: Get list of SNS platform applications.
  community.aws.sns_platform_info:

- name: Get list of SNS platform applications but enabled only.
  community.aws.sns_platform_info:
    enabled: 'true'
"""

RETURN = """
platforms:
  description: List of SNS Platform Applications.
  returned: when success
  type: list
  sample: [{
    "Attributes": {
      "AppleCertificateExpirationDate": "2021-10-10T16:56:51Z",
      "Enabled": "true",
      "SuccessFeedbackSampleRate": "100"
    }, 
    "PlatformApplicationArn": "arn:aws:sns:us-east-1:xxxxx:app/APNS/xxxxx-platform-app"
  }]
"""

try:
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:
    pass    # Handled by AnsibleAWSModule

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule


def main():
    argument_spec = dict(
        enabled=dict(required=False, choices=['true', 'false']),
    )

    module = AnsibleAWSModule(argument_spec=argument_spec)
    sns = module.client('sns')

    __default_return = []

    try:
        paginator = sns.get_paginator('list_platform_applications')
        platform_iterator = paginator.paginate()
        for response in platform_iterator:
            __default_return += response['PlatformApplications']
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg='Failed to fetch sns platform applications')

    if module.params['enabled'] is not None:
        __override_default_return = []
        for application in __default_return:
            if application['Attributes']['Enabled'] == module.params['enabled']:
                __override_default_return.append(application)

        module.exit_json(platforms=__override_default_return)

    module.exit_json(platforms=__default_return)


if __name__ == '__main__':
    main()
