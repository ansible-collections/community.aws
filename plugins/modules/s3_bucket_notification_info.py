#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: s3_bucket_notification_info
version_added: 11.1.0
short_description: Retrieve notification configuration for S3 buckets
description:
  - Retrieve notification configuration for S3 buckets.
author:
  - Mark Chappell (@tremble)
options:
  name:
    description:
      - Name of the S3 bucket.
    required: true
    type: str
    aliases: ['bucket_name']
extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details, see the AWS Guide for details.

- name: Retrieve notification configuration for a bucket
  community.aws.s3_bucket_notification_info:
    name: my-bucket
  register: result

- name: Display notification configuration
  ansible.builtin.debug:
    var: result.notification_configuration
"""

RETURN = r"""
notification_configuration:
  description: Notification configuration for the bucket
  returned: always
  type: dict
  contains:
    lambda_function_configurations:
      description: List of Lambda function notification configurations
      returned: when configured
      type: list
      elements: dict
      contains:
        id:
          description: Unique identifier for the configuration
          returned: when configured
          type: str
          sample: "lambda-notification-1"
        lambda_function_arn:
          description: ARN of the Lambda function
          returned: always
          type: str
          sample: "arn:aws:lambda:us-east-1:123456789012:function:my-function"
        events:
          description: S3 bucket events for which to send notifications
          returned: always
          type: list
          elements: str
          sample: ["s3:ObjectCreated:*"]
        filter:
          description: Filtering rules to determine which objects trigger notifications
          returned: when configured
          type: dict
    queue_configurations:
      description: List of SQS queue notification configurations
      returned: when configured
      type: list
      elements: dict
      contains:
        id:
          description: Unique identifier for the configuration
          returned: when configured
          type: str
          sample: "sqs-notification-1"
        queue_arn:
          description: ARN of the SQS queue
          returned: always
          type: str
          sample: "arn:aws:sqs:us-east-1:123456789012:my-queue"
        events:
          description: S3 bucket events for which to send notifications
          returned: always
          type: list
          elements: str
          sample: ["s3:ObjectCreated:*"]
        filter:
          description: Filtering rules to determine which objects trigger notifications
          returned: when configured
          type: dict
    topic_configurations:
      description: List of SNS topic notification configurations
      returned: when configured
      type: list
      elements: dict
      contains:
        id:
          description: Unique identifier for the configuration
          returned: when configured
          type: str
          sample: "sns-notification-1"
        topic_arn:
          description: ARN of the SNS topic
          returned: always
          type: str
          sample: "arn:aws:sns:us-east-1:123456789012:my-topic"
        events:
          description: S3 bucket events for which to send notifications
          returned: always
          type: list
          elements: str
          sample: ["s3:ObjectCreated:*"]
        filter:
          description: Filtering rules to determine which objects trigger notifications
          returned: when configured
          type: dict
"""

from ansible_collections.amazon.aws.plugins.module_utils.s3 import AnsibleS3Error

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule
from ansible_collections.community.aws.plugins.module_utils.s3 import get_bucket_notification_configuration
from ansible_collections.community.aws.plugins.module_utils.s3 import normalize_notification_configuration


def main():
    argument_spec = dict(
        name=dict(required=True, type="str", aliases=["bucket_name"]),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    bucket_name = module.params.get("name")

    try:
        client = module.client("s3")
        notification_config = get_bucket_notification_configuration(client, bucket_name)

        # Convert to snake_case
        result = normalize_notification_configuration(notification_config)

        module.exit_json(changed=False, notification_configuration=result)

    except AnsibleS3Error as e:
        module.fail_json_aws_error(e)


if __name__ == "__main__":
    main()
