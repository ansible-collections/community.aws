#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Davinder Pal <dpsangwal@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = """
module: sns_subscriptions_info
short_description: Get Information about AWS SNS Subscriptions.
description:
  - Get Information about AWS SNS Subscriptions.
version_added: 1.4.0
options:
  topic_arn:
    description:
      - topic_arn subscriptions will be returned?
    required: false
    type: str
    aliases: [ "arn" ]
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
- name: Get list of SNS Subscriptions.
  community.aws.sns_subscriptions_info:

- name: Get list of SNS Subscriptions for given topic.
  community.aws.sns_subscriptions_info:
    arn: 'arn:aws:sns:us-east-1:xxx:test'
"""

RETURN = """
subscriptions:
  description: List of SNS Subscriptions.
  returned: when success
  type: list
  sample: [{
    "endpoint": "arn:aws:sqs:us-east-1:xxxxx:test-endpoint",
    "owner": "xxxxx",
    "protocol": "sqs",
    "subscription_arn": "arn:aws:sns:us-east-1:xxxxx:test-sub-arn:xxxxxxxxxxxx-524760c63010",
    "topic_arn": "arn:aws:sns:us-east-1:xxxxx:test-topic-arn"
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
def _sub_it(sns, module):
    try:
        if module.params['topic_arn'] is not None:
            paginator = sns.get_paginator('list_subscriptions_by_topic')
            iterator = paginator.paginate(TopicArn=module.params['arn'])
        else:
            paginator = sns.get_paginator('list_subscriptions')
            iterator = paginator.paginate()
        return iterator
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg='Failed to fetch sns subscriptions')


def main():
    argument_spec = dict(
        topic_arn=dict(required=False, aliases=['arn']),
    )

    module = AnsibleAWSModule(argument_spec=argument_spec)
    sns = module.client('sns')

    __default_return = []

    _it = _sub_it(sns, module)
    if _it is not None:
        for response in _it:
            for sub in response['Subscriptions']:
                __default_return.append(camel_dict_to_snake_dict(sub))

    module.exit_json(subscriptions=__default_return)


if __name__ == '__main__':
    main()
