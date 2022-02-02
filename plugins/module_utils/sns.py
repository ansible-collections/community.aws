from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import re
import copy

try:
    import botocore
except ImportError:
    pass  # handled by AnsibleAWSModule

from ansible_collections.amazon.aws.plugins.module_utils.core import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AWSRetry
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import camel_dict_to_snake_dict


@AWSRetry.jittered_backoff()
def _list_topics_with_backoff(client):
    paginator = client.get_paginator('list_topics')
    return paginator.paginate().build_full_result()['Topics']


@AWSRetry.jittered_backoff(catch_extra_error_codes=['NotFound'])
def _list_topic_subscriptions_with_backoff(client, topic_arn):
    paginator = client.get_paginator('list_subscriptions_by_topic')
    return paginator.paginate(TopicArn=topic_arn).build_full_result()['Subscriptions']


@AWSRetry.jittered_backoff(catch_extra_error_codes=['NotFound'])
def _list_subscriptions_with_backoff(client):
    paginator = client.get_paginator('list_subscriptions')
    return paginator.paginate().build_full_result()['Subscriptions']


def list_topic_subscriptions(client, module, topic_arn):
    try:
        return _list_topic_subscriptions_with_backoff(client, topic_arn)
    except is_boto3_error_code('AuthorizationError'):
        try:
            # potentially AuthorizationError when listing subscriptions for third party topic
            return [sub for sub in _list_subscriptions_with_backoff(client)
                    if sub['TopicArn'] == topic_arn]
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg="Couldn't get subscriptions list for topic %s" % topic_arn)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:  # pylint: disable=duplicate-except
        module.fail_json_aws(e, msg="Couldn't get subscriptions list for topic %s" % topic_arn)


def list_topics(client, module):
    try:
        topics = _list_topics_with_backoff(client)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't get topic list")
    return [t['TopicArn'] for t in topics]


def topic_arn_lookup(client, module, name):
    # topic names cannot have colons, so this captures the full topic name
    all_topics = list_topics(client, module)
    lookup_topic = ':%s' % name
    for topic in all_topics:
        if topic.endswith(lookup_topic):
            return topic


def compare_delivery_policies(policy_a, policy_b):
    _policy_a = copy.deepcopy(policy_a)
    _policy_b = copy.deepcopy(policy_b)
    # AWS automatically injects disableSubscriptionOverrides if you set an
    # http policy
    if 'http' in policy_a:
        if 'disableSubscriptionOverrides' not in policy_a['http']:
            _policy_a['http']['disableSubscriptionOverrides'] = False
    if 'http' in policy_b:
        if 'disableSubscriptionOverrides' not in policy_b['http']:
            _policy_b['http']['disableSubscriptionOverrides'] = False
    comparison = (_policy_a != _policy_b)
    return comparison


def canonicalize_endpoint(protocol, endpoint):
    # AWS SNS expects phone numbers in
    # and canonicalizes to E.164 format
    # See <https://docs.aws.amazon.com/sns/latest/dg/sms_publish-to-phone.html>
    if protocol == 'sms':
        return re.sub('[^0-9+]*', '', endpoint)
    return endpoint


def get_info(connection, module, topic_arn):
    name = module.params.get('name')
    topic_type = module.params.get('topic_type')
    state = module.params.get('state')
    subscriptions = module.params.get('subscriptions')
    purge_subscriptions = module.params.get('purge_subscriptions')
    subscriptions_existing = module.params.get('subscriptions_existing', [])
    subscriptions_deleted = module.params.get('subscriptions_deleted', [])
    subscriptions_added = module.params.get('subscriptions_added', [])
    subscriptions_added = module.params.get('subscriptions_added', [])
    topic_created = module.params.get('topic_created', False)
    topic_deleted = module.params.get('topic_deleted', False)
    attributes_set = module.params.get('attributes_set', [])
    check_mode = module.check_mode

    info = {
        'name': name,
        'topic_type': topic_type,
        'state': state,
        'subscriptions_new': subscriptions,
        'subscriptions_existing': subscriptions_existing,
        'subscriptions_deleted': subscriptions_deleted,
        'subscriptions_added': subscriptions_added,
        'subscriptions_purge': purge_subscriptions,
        'check_mode': check_mode,
        'topic_created': topic_created,
        'topic_deleted': topic_deleted,
        'attributes_set': attributes_set,
    }
    if state != 'absent':
        if topic_arn in list_topics(connection, module):
            info.update(camel_dict_to_snake_dict(connection.get_topic_attributes(TopicArn=topic_arn)['Attributes']))
            info['delivery_policy'] = info.pop('effective_delivery_policy')
        info['subscriptions'] = [camel_dict_to_snake_dict(sub) for sub in list_topic_subscriptions(connection, module, topic_arn)]

    return info
