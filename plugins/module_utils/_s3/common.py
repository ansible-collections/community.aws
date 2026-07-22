# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
S3-specific error handling extensions for community.aws modules.

Extends amazon.aws S3ErrorHandler to include additional error codes
specific to S3 bucket configuration operations.
"""

from __future__ import annotations

import typing

if typing.TYPE_CHECKING:
    from typing import Callable

from ansible_collections.amazon.aws.plugins.module_utils.botocore import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.s3 import S3ErrorHandler as BaseS3ErrorHandler


class S3ErrorHandler(BaseS3ErrorHandler):
    """
    Extended S3 error handler with support for additional configuration error codes.

    Extends amazon.aws.S3ErrorHandler to include error codes specific to
    S3 bucket configuration operations (CORS, lifecycle, metrics, website, etc.).
    """

    @classmethod
    def _is_missing(cls) -> Callable:
        """
        Check if a boto3 exception indicates a missing/not found resource.

        Extends the base implementation to include additional S3 configuration
        error codes:
        - NoSuchConfiguration: Metrics configuration not found
        - NoSuchWebsiteConfiguration: Website configuration not found
        - NoSuchLifecycleConfiguration: Lifecycle configuration not found
        - NoSuchCORSConfiguration: CORS configuration not found

        Returns:
            A matcher function for boto3 error codes indicating missing resources.
        """
        # Get the base error codes by calling the parent implementation
        # We need to extract the codes and add our additional ones
        return is_boto3_error_code(
            [
                # Base error codes from amazon.aws.S3ErrorHandler
                "404",
                "NoSuchTagSet",
                "NoSuchTagSetError",
                "ObjectLockConfigurationNotFoundError",
                "NoSuchBucketPolicy",
                "ServerSideEncryptionConfigurationNotFoundError",
                "NoSuchBucket",
                "NoSuchPublicAccessBlockConfiguration",
                "OwnershipControlsNotFoundError",
                "NoSuchOwnershipControls",
                # Additional configuration error codes for community.aws
                "NoSuchConfiguration",
                "NoSuchWebsiteConfiguration",
                "NoSuchLifecycleConfiguration",
                "NoSuchCORSConfiguration",
            ]
        )
