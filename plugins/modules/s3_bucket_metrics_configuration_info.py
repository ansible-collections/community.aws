#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: s3_bucket_metrics_configuration_info
version_added: 11.1.0
short_description: Retrieve information about S3 bucket metrics configurations
description:
  - Retrieve information about S3 bucket metrics configurations.
  - Metrics configurations allow CloudWatch request metrics for objects in a bucket.
author:
  - Mark Chappell (@tremble)
options:
  name:
    description:
      - Name of the S3 bucket.
    required: true
    type: str
    aliases: ['bucket_name']
  id:
    description:
      - The ID of a specific metrics configuration to retrieve.
      - If not specified, all metrics configurations for the bucket will be returned.
    required: false
    type: str
extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details, see the AWS Guide for details.

- name: Retrieve all metrics configurations for a bucket
  community.aws.s3_metrics_configuration_info:
    name: my-bucket
  register: result

- name: Retrieve a specific metrics configuration
  community.aws.s3_metrics_configuration_info:
    name: my-bucket
    id: EntireBucket
  register: result
"""

RETURN = r"""
metrics_configurations:
  description: List of metrics configurations for the bucket
  returned: always
  type: list
  elements: dict
  contains:
    id:
      description: The ID used to identify the metrics configuration
      returned: always
      type: str
      sample: "EntireBucket"
    filter:
      description: Filter criteria for the metrics configuration
      returned: when filter is configured
      type: dict
      contains:
        prefix:
          description: Prefix filter
          returned: when configured
          type: str
          sample: "documents/"
        tags:
          description: Tag filters
          returned: when configured
          type: dict
          sample: { "priority": "high", "class": "blue" }
"""

from ansible_collections.amazon.aws.plugins.module_utils.botocore import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.retries import AWSRetry
from ansible_collections.amazon.aws.plugins.module_utils.s3 import AnsibleS3Error
from ansible_collections.amazon.aws.plugins.module_utils.s3 import S3ErrorHandler

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule
from ansible_collections.community.aws.plugins.module_utils.s3 import normalize_metrics_configuration


@AWSRetry.jittered_backoff(max_delay=120, catch_extra_error_codes=["OperationAborted"])
def _list_bucket_metrics_configurations_with_token(client, bucket_name, continuation_token=None):
    """List bucket metrics configurations with optional continuation token."""
    params = {"Bucket": bucket_name}
    if continuation_token:
        params["ContinuationToken"] = continuation_token
    return client.list_bucket_metrics_configurations(**params)


@S3ErrorHandler.list_error_handler("list bucket metrics configurations", [])
def list_bucket_metrics_configurations(client, bucket_name):
    """List all metrics configurations for a bucket."""
    configurations = []
    continuation_token = None

    while True:
        response = _list_bucket_metrics_configurations_with_token(client, bucket_name, continuation_token)
        configurations.extend(response.get("MetricsConfigurationList", []))

        if not response.get("IsTruncated"):
            break
        continuation_token = response.get("NextContinuationToken")

    return configurations


@S3ErrorHandler.list_error_handler("get bucket metrics configuration", {})
@AWSRetry.jittered_backoff(max_delay=120, catch_extra_error_codes=["OperationAborted"])
def get_bucket_metrics_configuration(client, bucket_name, metrics_id):
    """Get a specific metrics configuration."""
    try:
        response = client.get_bucket_metrics_configuration(Bucket=bucket_name, Id=metrics_id)
        return response.get("MetricsConfiguration", {})
    except is_boto3_error_code("NoSuchConfiguration"):
        return {}


def main():
    argument_spec = dict(
        name=dict(required=True, type="str", aliases=["bucket_name"]),
        id=dict(required=False, type="str"),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    bucket_name = module.params.get("name")
    metrics_id = module.params.get("id")

    try:
        client = module.client("s3")

        if metrics_id:
            config = get_bucket_metrics_configuration(client, bucket_name, metrics_id)
            if config:
                result = [normalize_metrics_configuration(config)]
            else:
                result = []
        else:
            configs = list_bucket_metrics_configurations(client, bucket_name)
            result = [normalize_metrics_configuration(config) for config in configs]
            result = [r for r in result if r is not None]

        module.exit_json(changed=False, metrics_configurations=result)

    except AnsibleS3Error as e:
        module.fail_json_aws_error(e)


if __name__ == "__main__":
    main()
