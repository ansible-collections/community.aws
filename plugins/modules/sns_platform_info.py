#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Davinder Pal <dpsangwal@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = """
module: sns_platform_info
short_description: Get Information about AWS SNS Platforms.
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
  - "Davinder Pal (@116davinder) <dpsangwal@gmail.com>"
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
    "attributes": {
      "apple_certificate_expiration_date": "2021-10-10T16:56:51Z",
      "enabled": "true",
      "success_feedback_sample_rate": "100"
    },
    "platform_application_arn": "arn:aws:sns:us-east-1:xxxxx:app/APNS/xxxxx-platform-app"
  }]
"""

try:
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:
    pass    # Handled by AnsibleAWSModule

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import camel_dict_to_snake_dict
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AWSRetry


@AWSRetry.exponential_backoff(retries=5, delay=5)
def _platform_it(sns, module):
    try:
        paginator = sns.get_paginator('list_platform_applications')
        iterator = paginator.paginate()
        return iterator
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg='Failed to fetch sns platform applications')


def main():
    argument_spec = dict(
        enabled=dict(required=False, choices=['true', 'false']),
    )

    module = AnsibleAWSModule(argument_spec=argument_spec)
    sns = module.client('sns')

    __default_return = []

    _it = _platform_it(sns, module)
    if _it is not None:
        for response in _it:
            for application in response['PlatformApplications']:
                __default_return.append(camel_dict_to_snake_dict(application))

    if module.params['enabled'] is not None:
        __override_default_return = []
        for application in __default_return:
            if application['attributes']['enabled'] == module.params['enabled']:
                __override_default_return.append(application)

        module.exit_json(platforms=__override_default_return)

    module.exit_json(platforms=__default_return)


if __name__ == '__main__':
    main()
