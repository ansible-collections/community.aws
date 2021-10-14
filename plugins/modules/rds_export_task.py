#!/usr/bin/python

# Copyright: (c) 2017, Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: rds_export_task
version_added: 2.1.0
short_description: rds_export_task
author: Alina Buzachis (@alinabuzachis)
description:
    - Starts an export of a snapshot to Amazon S3.
    - Cancels an export task in progress that is exporting a snapshot to Amazon S3.
options:
    state:
        description:
            - Specifies whether the export task should be C(present) or C(absent).
        required: true
        choices: [ 'present', 'absent' ]
        type: str
    export_task_id:
        description:
            - A unique identifier for the snapshot export task.
        required: true
        type: str
    source_arn:
        description:
            - The Amazon Resource Name (ARN) of the snapshot to export to Amazon S3.
        required: true
        type: str
    s3_bucket_name:
        description:
            - The name of the Amazon S3 bucket to export the snapshot to.
        required: true
        type: str
    iam_role_arn:
        description:
            - The name of the IAM role to use for writing to the Amazon S3 bucket when exporting a snapshot.
        required: true
        type: str
    kms_key_id:
        description:
            - The ID of the Amazon Web Services KMS customer master key (CMK) to use to encrypt the snapshot exported to Amazon S3.
        required: true
        type: str
    s3_prefix:
        description:
            - The Amazon S3 bucket prefix to use as the file name and path of the exported snapshot.
        required: true
        type: str
    export_only:
        description:
            - The data to be exported from the snapshot.
            - If this parameter is not provided, all the snapshot data is exported.
            - Valid values are the following
            - 'C(database): Export all the data from a specified database'
            - 'C(database.table) table-name: Export a table of the snapshot.
               This format is valid only for RDS for MySQL, RDS for MariaDB, and Aurora MySQL.'
            - 'C(database.schema) schema: Export a database schema of the snapshot.
               This format is valid only for RDS for PostgreSQL and Aurora PostgreSQL.'
            - 'C(database.schema) table-name: Export a table of the database schema.
               This format is valid only for RDS for PostgreSQL and Aurora PostgreSQL.'
        required: true
        type: list
    wait:
        description:
            - Wait for the copied Snapshot to be in C(Available) state before returning.
        type: bool
        default: true
    wait_timeout:
        description:
            - How long before wait gives up, in seconds.
        default: 600
        type: int
    tags:
        description:
            - A dictionary of tags to be added to the new Snapshot.
        type: dict
extends_documentation_fragment:
- amazon.aws.aws
- amazon.aws.ec2
"""

EXAMPLES = r"""

"""

RETURN = r"""

"""

try:
    import botocore
except ImportError:
    pass  # Handled by AnsibleAWSModule

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ..module_utils.core import AnsibleAWSModule
from ..module_utils.core import is_boto3_error_code
from ..module_utils.ec2 import AWSRetry


def list_export_tasks():
    result = {}

    try:
        _result = client.describe_export_tasks(
            aws_retry=True, ExportTaskIdentifier=module.params.get("export_task_id")
        )
    except is_boto3_error_code("ExportTaskNotFound"):
        return {}
    except (
        botocore.exceptions.ClientError,
        botocore.exceptions.BotoCoreError,
    ) as e:  # pylint: disable=duplicate-except
        module.fail_json_aws(e, msg="Couldn't get export task")

    if _result:
        result = camel_dict_to_snake_dict(_result["ExportTasks"][0])


def start_export_task():
    results = {}
    params = {}
    params = {
        "ExportTaskIdentifier": module.params.get("export_task_id"),
        "SourceArn": module.params.get("source_arn"),
        "S3BucketName": module.params.get("s3_bucket_name"),
        "IamRoleArn": module.params.get("iam_role_arn"),
        "KmsKeyId": module.params.get("kms_key_id"),
    }

    if module.params.get("s3_prefix"):
        params["S3Prefix"] = module.params.get("s3_prefix")

    if module.params.get("export_only"):
        params["ExportOnly"] = module.params.get("export_only")

    try:
        if module.check_mode:
            return changed, results
        results = client.start_export_task(aws_retry=True, **params)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't start export task")


def cancel_export_task():
    results = {}
    try:
        if module.check_mode:
            return changed, results
        results = client.cancel_export_task(
            aws_retry=True, ExportTaskIdentifier=module.params.get("export_task_id")
        )
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Couldn't cancel export task")


def main():
    global module
    global client

    argument_spec = dict(
        state=dict(choices=["present", "absent"], required=True),
        export_task_id=dict(type="str", required=True),
        source_arn=dict(type="str", required=True),
        s3_bucket_name=dict(type="str", required=True),
        iam_role_arn=dict(type="str", required=True),
        kms_key_id=dict(type="str", required=True),
        s3_prefix=dict(type="str"),
        export_only=dict(ype="list"),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    try:
        client = module.client("rds", retry_decorator=AWSRetry.jittered_backoff())
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Failed to connect to AWS")

    state = module.params.get("state")

    if state == "present":
        changed, results = start_export_task()
    else:
        changed, results = cancel_export_task()

    module.exit_json(changed=changed, **results)


if __name__ == "__main__":
    main()
