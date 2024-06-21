#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: s3_logging
version_added: 1.0.0
short_description: Manage logging facility of an s3 bucket in AWS
description:
  - Manage logging facility of an s3 bucket in AWS
author:
  - Rob White (@wimnat)
options:
  name:
    description:
      - "Name of the s3 bucket."
    required: true
    type: str
  state:
    description:
      - "Enable or disable logging."
    default: present
    choices: [ 'present', 'absent' ]
    type: str
  target_bucket:
    description:
      - "The bucket to log to. Required when state=present."
    type: str
  target_prefix:
    description:
      - "The prefix that should be prepended to the generated log files written to the target_bucket."
    default: ""
    type: str
  target_access:
    description:
      - "Permissions type for log delivery"
    default: policy
    choices: [ 'policy', 'acl' ]
    type: str
extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

RETURN = r""" # """

EXAMPLES = r"""
# Note: These examples do not set authentication details, see the AWS Guide for details.

- name: Enable logging of s3 bucket mywebsite.com to s3 bucket mylogs
  community.aws.s3_logging:
    name: mywebsite.com
    target_bucket: mylogs
    target_prefix: logs/mywebsite.com
    state: present

- name: Remove logging on an s3 bucket
  community.aws.s3_logging:
    name: mywebsite.com
    state: absent
"""

import json

try:
    import botocore
except ImportError:
    pass  # Handled by AnsibleAWSModule

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.amazon.aws.plugins.module_utils.botocore import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.retries import AWSRetry

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule


def compare_bucket_logging(bucket_logging, target_bucket, target_prefix):
    if not bucket_logging.get("LoggingEnabled", False):
        if target_bucket:
            return True
        return False

    logging = bucket_logging["LoggingEnabled"]
    if logging["TargetBucket"] != target_bucket:
        return True
    if logging["TargetPrefix"] != target_prefix:
        return True
    return False


def verify_acls(connection, module, bucket_name, target_access, target_bucket):
    current_obj_ownership = "BucketOwnerEnforced"
    try:
        current_ownership = connection.get_bucket_ownership_controls(aws_retry=True, Bucket=target_bucket)
        rules = current_ownership["OwnershipControls"]["Rules"]
        for rule in rules:
            if "ObjectOwnership" in rule:
                current_obj_ownership = rule["ObjectOwnership"]
        if target_access == "acl" and current_obj_ownership == "BucketOwnerEnforced":
            module.fail_json_aws(msg="The access type is set to ACL but it is disabled on target bucket")
        current_acl = connection.get_bucket_acl(aws_retry=True, Bucket=target_bucket)
        current_grants = current_acl["Grants"]
    except is_boto3_error_code("NoSuchBucket"):
        module.fail_json(msg=f"Target Bucket '{target_bucket}' not found")
    except (
        botocore.exceptions.BotoCoreError,
        botocore.exceptions.ClientError,
    ) as e:  # pylint: disable=duplicate-except
        module.fail_json_aws(e, msg="Failed to fetch target bucket ownership")

    required_grant = {
        "Grantee": {"URI": "http://acs.amazonaws.com/groups/s3/LogDelivery", "Type": "Group"},
        "Permission": "FULL_CONTROL",
    }

    updated_grants = []
    if target_access == "acl":
        if required_grant not in list(current_grants):
            updated_grants = list(current_grants)
            updated_grants.append(required_grant)
        else:
            return False
    else:
        if required_grant in list(current_grants):
            for grant in current_grants:
                if grant != required_grant:
                    updated_grants.append(grant)
        else:
            return False

    updated_acl = dict(current_acl)
    updated_acl["Grants"] = updated_grants
    del updated_acl["ResponseMetadata"]
    module.warn(json.dumps(updated_acl))

    if module.check_mode:
        return True

    try:
        connection.put_bucket_acl(aws_retry=True, Bucket=target_bucket, AccessControlPolicy=updated_acl)
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        module.fail_json_aws(e, msg="Failed to update target bucket ACL to allow log delivery")

    return True


def verify_policy(connection, module, bucket_name, target_access, target_bucket, target_prefix):
    policy = {"Version": "2012-10-17", "Statement": []}
    policy_statement = {
        "Sid": bucket_name,
        "Effect": "Allow",
        "Principal": {"Service": "logging.s3.amazonaws.com"},
        "Action": "s3:PutObject",
        "Resource": f"arn:aws:s3:::{target_bucket}/{target_prefix}*",
    }

    try:
        current_policy_raw = connection.get_bucket_policy(aws_retry=True, Bucket=target_bucket)
    except is_boto3_error_code("NoSuchBucket"):
        module.fail_json(msg=f"Target Bucket '{target_bucket}' not found")
    except is_boto3_error_code("NoSuchBucketPolicy"):
        current_policy_raw = {"Policy": json.dumps(policy)}
    except (
        botocore.exceptions.BotoCoreError,
        botocore.exceptions.ClientError,
    ) as e:  # pylint: disable=duplicate-except
        module.fail_json_aws(e, msg="Failed to fetch target bucket policy")

    try:
        current_policy = json.loads(current_policy_raw["Policy"])
    except json.JSONDecodeError as e:
        module.fail_json(e, msg="Unable to parse policy")

    new_policy_statements = []
    new_policy = current_policy
    for p in current_policy.get("Statement", []):
        if p == policy_statement and target_access == "policy":
            return False
    if target_access == "acl":
        for p in current_policy.get("Statement", []):
            if p != policy_statement:
                new_policy_statements.append(p)
        new_policy["Statement"] = new_policy_statements
        if new_policy == current_policy:
            return False
    else:
        new_policy = current_policy
        if new_policy["Statement"] is None:
            new_policy["Statement"] = [policy_statement]
        else:
            new_policy["Statement"].append(policy_statement)

    if module.check_mode:
        return True

    try:
        connection.put_bucket_policy(aws_retry=True, Bucket=target_bucket, Policy=json.dumps(new_policy))
    except is_boto3_error_code("MalformedPolicy"):
        module.fail_json(msg=f"Bad policy:\n {new_policy}")
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        module.fail_json_aws(e, msg="Failed to update target bucket policy to allow log delivery")

    return True


def enable_bucket_logging(connection, module: AnsibleAWSModule):
    bucket_name = module.params.get("name")
    target_bucket = module.params.get("target_bucket")
    target_prefix = module.params.get("target_prefix")
    target_access = module.params.get("target_access")
    changed = False

    try:
        bucket_logging = connection.get_bucket_logging(aws_retry=True, Bucket=bucket_name)
    except is_boto3_error_code("NoSuchBucket"):
        module.fail_json(msg=f"Bucket '{bucket_name}' not found")
    except (
        botocore.exceptions.BotoCoreError,
        botocore.exceptions.ClientError,
    ) as e:  # pylint: disable=duplicate-except
        module.fail_json_aws(e, msg="Failed to fetch current logging status")

    try:
        changed |= verify_acls(connection, module, bucket_name, target_access, target_bucket)
        changed |= verify_policy(connection, module, bucket_name, target_access, target_bucket, target_prefix)

        if not compare_bucket_logging(bucket_logging, target_bucket, target_prefix):
            bucket_logging = camel_dict_to_snake_dict(bucket_logging)
            module.exit_json(changed=changed, **bucket_logging)

        if module.check_mode:
            module.exit_json(changed=True)

        result = connection.put_bucket_logging(
            aws_retry=True,
            Bucket=bucket_name,
            BucketLoggingStatus={
                "LoggingEnabled": {
                    "TargetBucket": target_bucket,
                    "TargetPrefix": target_prefix,
                }
            },
        )

    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        module.fail_json_aws(e, msg="Failed to enable bucket logging")

    result = camel_dict_to_snake_dict(result)
    module.exit_json(changed=True, **result)


def disable_bucket_logging(connection, module):
    bucket_name = module.params.get("name")
    changed = False

    try:
        bucket_logging = connection.get_bucket_logging(aws_retry=True, Bucket=bucket_name)
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        module.fail_json_aws(e, msg="Failed to fetch current logging status")

    if not compare_bucket_logging(bucket_logging, None, None):
        module.exit_json(changed=False)

    if module.check_mode:
        module.exit_json(changed=True)

    try:
        response = AWSRetry.jittered_backoff(catch_extra_error_codes=["InvalidTargetBucketForLogging"])(
            connection.put_bucket_logging
        )(Bucket=bucket_name, BucketLoggingStatus={})
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        module.fail_json_aws(e, msg="Failed to disable bucket logging")

    module.exit_json(changed=True)


def main():
    argument_spec = dict(
        name=dict(required=True),
        target_bucket=dict(required=False, default=None),
        target_prefix=dict(required=False, default=""),
        target_access=dict(required=False, default="policy", choices=["policy", "acl"]),
        state=dict(required=False, default="present", choices=["present", "absent"]),
    )

    module = AnsibleAWSModule(argument_spec=argument_spec, supports_check_mode=True)

    connection = module.client("s3", retry_decorator=AWSRetry.jittered_backoff())
    state = module.params.get("state")

    if state == "present":
        enable_bucket_logging(connection, module)
    elif state == "absent":
        disable_bucket_logging(connection, module)


if __name__ == "__main__":
    main()
