#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
module: sns_topic_info
short_description: sns_topic_info module
version_added: 3.1.0
description:
  - The M(community.aws.sns_topic_info) module allows to get all AWS SNS topics or properties of a specific AWS SNS topic.
author:
- "Alina Buzachis (@alinabuzachis)"
options:
  topic_arn:
    description:
      - The ARN of the AWS SNS topic for which you wish to find subscriptions or list attributes.
    required: false
    type: str
extends_documentation_fragment:
- amazon.aws.aws
- amazon.aws.ec2
'''

EXAMPLES = r'''
- name: list all the topics
  community.aws.sns_topic_info:
  register: sns_topic_list

- name: get info on specific topic
  community.aws.sns_topic_info:
    topic_arn: "{{ sns_arn }}"
  register: sns_topic_info
'''

RETURN = r'''
changed:
  description: True if listing the AWS SNS topics succeeds
  type: bool
  returned: always
  sample: false
result:
  description:
    - The result contaning the details of one or all AWS SNS topics.
  returned: suceess
  type: list
  contains:
    sns_arn:
        description: The ARN of the topic.
        type: str
        returned: always
        sample: "arn:aws:sns:us-east-2:111111111111:my_topic_name"
    sns_topic:
        description: Dict of sns topic details
        type: complex
        returned: always
        contains:
            delivery_policy:
                description: Delivery policy for the SNS topic
                returned: when topic is owned by this AWS account
                type: str
                sample: {
                    "http":{"defaultHealthyRetryPolicy":{"minDelayTarget":20,"maxDelayTarget":20,"numRetries":3,"numMaxDelayRetries":0,
                    "numNoDelayRetries":0,"numMinDelayRetries":0,"backoffFunction":"linear"},"disableSubscriptionOverrides":false}
                }
            display_name:
                description: Display name for SNS topic
                returned: when topic is owned by this AWS account
                type: str
                sample: My topic name
            owner:
                description: AWS account that owns the topic
                returned: when topic is owned by this AWS account
                type: str
                sample: '111111111111'
            policy:
                description: Policy for the SNS topic
                returned: when topic is owned by this AWS account
                type: str
                sample: {
                    "Version":"2012-10-17","Id":"SomePolicyId","Statement":[{"Sid":"ANewSid","Effect":"Allow","Principal":{"AWS":"arn:aws:iam::111111111111:root"},
                    "Action":"sns:Subscribe","Resource":"arn:aws:sns:us-east-2:111111111111:ansible-test-dummy-topic","Condition":{"StringEquals":{"sns:Protocol":"email"}}}]
                }
            subscriptions:
                description: List of subscribers to the topic in this AWS account
                returned: always
                type: list
                sample: []
            subscriptions_confirmed:
                description: Count of confirmed subscriptions
                returned: when topic is owned by this AWS account
                type: str
                sample: '0'
            subscriptions_deleted:
                description: Count of deleted subscriptions
                returned: when topic is owned by this AWS account
                type: str
                sample: '0'
            subscriptions_pending:
                description: Count of pending subscriptions
                returned: when topic is owned by this AWS account
                type: str
                sample: '0'
            topic_arn:
                description: ARN of the SNS topic (equivalent to sns_arn)
                returned: when topic is owned by this AWS account
                type: str
                sample: arn:aws:sns:us-east-2:111111111111:ansible-test-dummy-topic
'''


import json

try:
    import botocore
except ImportError:
    pass  # handled by AnsibleAWSModule

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.core import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AWSRetry
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import camel_dict_to_snake_dict


@AWSRetry.jittered_backoff()
def _list_topics_with_backoff(connection):
    paginator = connection.get_paginator('list_topics')
    return paginator.paginate().build_full_result()['Topics']


@AWSRetry.jittered_backoff(catch_extra_error_codes=['NotFound'])
def _list_topic_subscriptions_with_backoff(connection, topic_arn):
    paginator = connection.get_paginator('list_subscriptions_by_topic')
    return paginator.paginate(TopicArn=topic_arn).build_full_result()['Subscriptions']


@AWSRetry.jittered_backoff(catch_extra_error_codes=['NotFound'])
def _list_subscriptions_with_backoff(connection):
    paginator = connection.get_paginator('list_subscriptions')
    return paginator.paginate().build_full_result()['Subscriptions']


def _list_topic_subscriptions(connection, module, topic_arn):
    try:
        return _list_topic_subscriptions_with_backoff(connection, topic_arn)
    except is_boto3_error_code('AuthorizationError'):
        try:
            # potentially AuthorizationError when listing subscriptions for third party topic
            return [sub for sub in _list_subscriptions_with_backoff()
                    if sub['TopicArn'] == topic_arn]
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Couldn't get subscriptions list for topic %s" % topic_arn)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:  # pylint: disable=duplicate-except
        module.fail_json_aws(e, msg="Couldn't get subscriptions list for topic %s" % topic_arn)


def list_topics(connection, module):
    try:
        topics = _list_topics_with_backoff(connection)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't get topic list")

    return [get_info(connection, module, t['TopicArn']) for t in topics]


def get_info(connection, module, topic_arn):
    info = {
        'sns_arn': topic_arn,
    }
    try:
        info['sns_topic'] = camel_dict_to_snake_dict(connection.get_topic_attributes(TopicArn=topic_arn)['Attributes'])
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't get attributes for topic.")

    info['sns_topic']['delivery_policy'] = json.loads(info['sns_topic'].pop('effective_delivery_policy'))
    info['sns_topic']['policy'] = json.loads(info['sns_topic']['policy'])
    info['sns_topic']['subscriptions'] = [camel_dict_to_snake_dict(sub) for sub in _list_topic_subscriptions(connection, module, topic_arn)]

    return info


def main():
    argument_spec = dict(
        topic_arn=dict(type='str', required=False),
    )

    module = AnsibleAWSModule(argument_spec=argument_spec,
                              supports_check_mode=True)

    topic_arn = module.params.get('topic_arn')

    try:
        connection = module.client('sns', retry_decorator=AWSRetry.jittered_backoff())
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg='Failed to connect to AWS.')

    if topic_arn:
        results = get_info(connection, module, topic_arn)
    else:
        results = list_topics(connection, module)

    module.exit_json(result=results)


if __name__ == '__main__':
    main()
