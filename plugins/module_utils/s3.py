# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
S3 client wrappers for community.aws modules.

These wrappers will eventually be contributed to amazon.aws.
"""

from __future__ import annotations

from ansible_collections.amazon.aws.plugins.module_utils.botocore import is_boto3_error_message
from ansible_collections.amazon.aws.plugins.module_utils.botocore import normalize_boto3_result
from ansible_collections.amazon.aws.plugins.module_utils.retries import AWSRetry

from ansible_collections.community.aws.plugins.module_utils._s3.common import S3ErrorHandler

# Intended for general use / re-import
# pylint: disable=unused-import,useless-import-alias
from ansible_collections.community.aws.plugins.module_utils._s3.transformations import (
    build_notification_configuration as build_notification_configuration,
)
from ansible_collections.community.aws.plugins.module_utils._s3.transformations import (
    create_metrics_configuration as create_metrics_configuration,
)
from ansible_collections.community.aws.plugins.module_utils._s3.transformations import (
    create_website_configuration as create_website_configuration,
)
from ansible_collections.community.aws.plugins.module_utils._s3.transformations import (
    normalize_cors_rules as normalize_cors_rules,
)
from ansible_collections.community.aws.plugins.module_utils._s3.transformations import (
    normalize_lifecycle_rules as normalize_lifecycle_rules,
)
from ansible_collections.community.aws.plugins.module_utils._s3.transformations import (
    normalize_metrics_configuration as normalize_metrics_configuration,
)
from ansible_collections.community.aws.plugins.module_utils._s3.transformations import (
    normalize_notification_configuration as normalize_notification_configuration,
)
from ansible_collections.community.aws.plugins.module_utils._s3.transformations import (
    normalize_website_configuration as normalize_website_configuration,
)

# ========================================
# S3 Bucket Configuration Wrappers
# ========================================


@S3ErrorHandler.list_error_handler("get bucket notification configuration", {})
@AWSRetry.jittered_backoff(max_delay=120, catch_extra_error_codes=["OperationAborted"])
def get_bucket_notification_configuration(client, bucket_name):
    """
    Get the notification configuration for an S3 bucket.

    Parameters:
        client: boto3 S3 client
        bucket_name: Name of the S3 bucket

    Returns:
        Notification configuration dictionary
    """
    return client.get_bucket_notification_configuration(Bucket=bucket_name)


@S3ErrorHandler.common_error_handler("put bucket notification configuration")
@AWSRetry.jittered_backoff(max_delay=120, catch_extra_error_codes=["OperationAborted"])
def put_bucket_notification_configuration(client, bucket_name, notification_configuration):
    """
    Set the notification configuration for an S3 bucket.

    Parameters:
        client: boto3 S3 client
        bucket_name: Name of the S3 bucket
        notification_configuration: Notification configuration dictionary
    """
    return client.put_bucket_notification_configuration(
        Bucket=bucket_name, NotificationConfiguration=notification_configuration
    )


@S3ErrorHandler.list_error_handler("get bucket website configuration", {})
@AWSRetry.jittered_backoff(max_delay=120, catch_extra_error_codes=["OperationAborted"])
def get_bucket_website(client, bucket_name):
    """
    Get the website configuration for an S3 bucket.

    Parameters:
        client: boto3 S3 client
        bucket_name: Name of the S3 bucket

    Returns:
        Website configuration dictionary, or {} if no configuration exists
    """
    return client.get_bucket_website(Bucket=bucket_name)


@S3ErrorHandler.common_error_handler("put bucket website configuration")
@AWSRetry.jittered_backoff(max_delay=120, catch_extra_error_codes=["OperationAborted"])
def put_bucket_website(client, bucket_name, website_configuration):
    """
    Set the website configuration for an S3 bucket.

    Parameters:
        client: boto3 S3 client
        bucket_name: Name of the S3 bucket
        website_configuration: Website configuration dictionary
    """
    return client.put_bucket_website(Bucket=bucket_name, WebsiteConfiguration=website_configuration)


@S3ErrorHandler.deletion_error_handler("delete bucket website configuration")
@AWSRetry.jittered_backoff(max_delay=120, catch_extra_error_codes=["OperationAborted"])
def delete_bucket_website(client, bucket_name):
    """
    Delete the website configuration for an S3 bucket.

    Parameters:
        client: boto3 S3 client
        bucket_name: Name of the S3 bucket
    """
    return client.delete_bucket_website(Bucket=bucket_name)


@S3ErrorHandler.list_error_handler("get bucket CORS configuration", [])
@AWSRetry.jittered_backoff(max_delay=120, catch_extra_error_codes=["OperationAborted"])
def get_bucket_cors(client, bucket_name):
    """
    Get the CORS configuration for an S3 bucket.

    Parameters:
        client: boto3 S3 client
        bucket_name: Name of the S3 bucket

    Returns:
        List of CORS rules, or [] if no configuration exists
    """
    result = client.get_bucket_cors(Bucket=bucket_name)
    return result.get("CORSRules", [])


@S3ErrorHandler.common_error_handler("put bucket CORS configuration")
@AWSRetry.jittered_backoff(max_delay=120, catch_extra_error_codes=["OperationAborted"])
def put_bucket_cors(client, bucket_name, cors_rules):
    """
    Set the CORS configuration for an S3 bucket.

    Parameters:
        client: boto3 S3 client
        bucket_name: Name of the S3 bucket
        cors_rules: List of CORS rules
    """
    return client.put_bucket_cors(Bucket=bucket_name, CORSConfiguration={"CORSRules": cors_rules})


@S3ErrorHandler.deletion_error_handler("delete bucket CORS configuration")
@AWSRetry.jittered_backoff(max_delay=120, catch_extra_error_codes=["OperationAborted"])
def delete_bucket_cors(client, bucket_name):
    """
    Delete the CORS configuration for an S3 bucket.

    Parameters:
        client: boto3 S3 client
        bucket_name: Name of the S3 bucket
    """
    return client.delete_bucket_cors(Bucket=bucket_name)


@S3ErrorHandler.list_error_handler("get bucket metrics configuration", {})
@AWSRetry.jittered_backoff(max_delay=120, catch_extra_error_codes=["OperationAborted"])
def get_bucket_metrics_configuration(client, bucket_name, metrics_id):
    """
    Get a specific metrics configuration for an S3 bucket.

    Parameters:
        client: boto3 S3 client
        bucket_name: Name of the S3 bucket
        metrics_id: ID of the metrics configuration

    Returns:
        Metrics configuration dictionary, or {} if not found
    """
    response = client.get_bucket_metrics_configuration(Bucket=bucket_name, Id=metrics_id)
    return response.get("MetricsConfiguration", {})


@S3ErrorHandler.common_error_handler("put bucket metrics configuration")
@AWSRetry.jittered_backoff(max_delay=120, catch_extra_error_codes=["OperationAborted"])
def put_bucket_metrics_configuration(client, bucket_name, metrics_id, metrics_configuration):
    """
    Set a metrics configuration for an S3 bucket.

    Parameters:
        client: boto3 S3 client
        bucket_name: Name of the S3 bucket
        metrics_id: ID of the metrics configuration
        metrics_configuration: Metrics configuration dictionary
    """
    return client.put_bucket_metrics_configuration(
        Bucket=bucket_name, Id=metrics_id, MetricsConfiguration=metrics_configuration
    )


@S3ErrorHandler.deletion_error_handler("delete bucket metrics configuration")
@AWSRetry.jittered_backoff(max_delay=120, catch_extra_error_codes=["OperationAborted"])
def delete_bucket_metrics_configuration(client, bucket_name, metrics_id):
    """
    Delete a metrics configuration for an S3 bucket.

    Parameters:
        client: boto3 S3 client
        bucket_name: Name of the S3 bucket
        metrics_id: ID of the metrics configuration
    """
    return client.delete_bucket_metrics_configuration(Bucket=bucket_name, Id=metrics_id)


@S3ErrorHandler.list_error_handler("get bucket lifecycle configuration", {"Rules": []})
@AWSRetry.jittered_backoff(max_delay=120, catch_extra_error_codes=["OperationAborted"])
def get_bucket_lifecycle_configuration(client, bucket_name):
    """
    Get the lifecycle configuration for an S3 bucket.

    Parameters:
        client: boto3 S3 client
        bucket_name: Name of the S3 bucket

    Returns:
        Lifecycle configuration dictionary, or {"Rules": []} if not configured
    """
    result = client.get_bucket_lifecycle_configuration(Bucket=bucket_name)
    return normalize_boto3_result(result)


@S3ErrorHandler.common_error_handler("put bucket lifecycle configuration")
@AWSRetry.jittered_backoff(max_delay=120, catch_extra_error_codes=["OperationAborted"])
def put_bucket_lifecycle_configuration(client, bucket_name, lifecycle_configuration):
    """
    Set the lifecycle configuration for an S3 bucket.

    Parameters:
        client: boto3 S3 client
        bucket_name: Name of the S3 bucket
        lifecycle_configuration: Lifecycle configuration dictionary
    """
    try:
        return client.put_bucket_lifecycle_configuration(
            Bucket=bucket_name, LifecycleConfiguration=lifecycle_configuration
        )
    except is_boto3_error_message("At least one action needs to be specified in a rule"):
        # Amazon interpreted this as not changing anything
        return None


@S3ErrorHandler.deletion_error_handler("delete bucket lifecycle configuration")
@AWSRetry.jittered_backoff(max_delay=120, catch_extra_error_codes=["OperationAborted"])
def delete_bucket_lifecycle(client, bucket_name):
    """
    Delete the lifecycle configuration for an S3 bucket.

    Parameters:
        client: boto3 S3 client
        bucket_name: Name of the S3 bucket
    """
    return client.delete_bucket_lifecycle(Bucket=bucket_name)
