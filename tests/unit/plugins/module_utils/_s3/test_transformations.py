# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import pytest

from ansible_collections.community.aws.plugins.module_utils.s3 import build_notification_configuration
from ansible_collections.community.aws.plugins.module_utils.s3 import create_metrics_configuration
from ansible_collections.community.aws.plugins.module_utils.s3 import create_website_configuration
from ansible_collections.community.aws.plugins.module_utils.s3 import normalize_cors_rules
from ansible_collections.community.aws.plugins.module_utils.s3 import normalize_lifecycle_rules
from ansible_collections.community.aws.plugins.module_utils.s3 import normalize_metrics_configuration
from ansible_collections.community.aws.plugins.module_utils.s3 import normalize_notification_configuration
from ansible_collections.community.aws.plugins.module_utils.s3 import normalize_website_configuration


class MockConfig:
    """Mock Config object for testing notification configuration."""

    def __init__(self, raw_dict):
        self.raw = raw_dict
        self.name = raw_dict.get("Id")


class TestBuildNotificationConfiguration:
    """Test the build_notification_configuration function."""

    def test_builds_empty_notification_config(self):
        """Test that empty configuration returns proper structure."""
        bucket_config = {
            "QueueConfigurations": [],
            "TopicConfigurations": [],
            "LambdaFunctionConfigurations": [],
        }

        result = build_notification_configuration(bucket_config)

        assert result == {
            "queue_configurations": [],
            "topic_configurations": [],
            "lambda_function_configurations": [],
        }

    def test_builds_queue_notification_config(self):
        """Test that queue configuration is properly transformed."""
        bucket_config = {
            "QueueConfigurations": [
                MockConfig(
                    {
                        "Id": "test-queue-event",
                        "QueueArn": "arn:aws:sqs:us-east-1:123456789012:test-queue",
                        "Events": ["s3:ObjectCreated:*"],
                        "Filter": {
                            "Key": {
                                "FilterRules": [
                                    {"Name": "Prefix", "Value": "images/"},
                                    {"Name": "Suffix", "Value": ".jpg"},
                                ]
                            }
                        },
                    }
                )
            ],
            "TopicConfigurations": [],
            "LambdaFunctionConfigurations": [],
        }

        result = build_notification_configuration(bucket_config)

        assert len(result["queue_configurations"]) == 1
        assert result["queue_configurations"][0]["id"] == "test-queue-event"
        assert result["queue_configurations"][0]["queue_arn"] == "arn:aws:sqs:us-east-1:123456789012:test-queue"
        assert result["queue_configurations"][0]["events"] == ["s3:ObjectCreated:*"]

    def test_builds_topic_notification_config(self):
        """Test that topic configuration is properly transformed."""
        bucket_config = {
            "QueueConfigurations": [],
            "TopicConfigurations": [
                MockConfig(
                    {
                        "Id": "test-topic-event",
                        "TopicArn": "arn:aws:sns:us-east-1:123456789012:test-topic",
                        "Events": ["s3:ObjectRemoved:*"],
                    }
                )
            ],
            "LambdaFunctionConfigurations": [],
        }

        result = build_notification_configuration(bucket_config)

        assert len(result["topic_configurations"]) == 1
        assert result["topic_configurations"][0]["id"] == "test-topic-event"
        assert result["topic_configurations"][0]["topic_arn"] == "arn:aws:sns:us-east-1:123456789012:test-topic"

    def test_builds_lambda_notification_config(self):
        """Test that lambda configuration is properly transformed."""
        bucket_config = {
            "QueueConfigurations": [],
            "TopicConfigurations": [],
            "LambdaFunctionConfigurations": [
                MockConfig(
                    {
                        "Id": "test-lambda-event",
                        "LambdaFunctionArn": "arn:aws:lambda:us-east-1:123456789012:function:test-function",
                        "Events": ["s3:ObjectCreated:Put", "s3:ObjectCreated:Post"],
                    }
                )
            ],
        }

        result = build_notification_configuration(bucket_config)

        assert len(result["lambda_function_configurations"]) == 1
        assert result["lambda_function_configurations"][0]["id"] == "test-lambda-event"
        assert (
            result["lambda_function_configurations"][0]["lambda_function_arn"]
            == "arn:aws:lambda:us-east-1:123456789012:function:test-function"
        )

    def test_builds_mixed_notification_config(self):
        """Test that mixed configuration with multiple targets is properly transformed."""
        bucket_config = {
            "QueueConfigurations": [
                MockConfig(
                    {
                        "Id": "queue-event",
                        "QueueArn": "arn:aws:sqs:us-east-1:123456789012:queue",
                        "Events": ["s3:ObjectCreated:*"],
                    }
                )
            ],
            "TopicConfigurations": [
                MockConfig(
                    {
                        "Id": "topic-event",
                        "TopicArn": "arn:aws:sns:us-east-1:123456789012:topic",
                        "Events": ["s3:ObjectRemoved:*"],
                    }
                )
            ],
            "LambdaFunctionConfigurations": [
                MockConfig(
                    {
                        "Id": "lambda-event",
                        "LambdaFunctionArn": "arn:aws:lambda:us-east-1:123456789012:function:func",
                        "Events": ["s3:ObjectRestore:*"],
                    }
                )
            ],
        }

        result = build_notification_configuration(bucket_config)

        assert len(result["queue_configurations"]) == 1
        assert len(result["topic_configurations"]) == 1
        assert len(result["lambda_function_configurations"]) == 1

    def test_transforms_camel_case_to_snake_case(self):
        """Test that all keys are properly transformed from CamelCase to snake_case."""
        bucket_config = {
            "QueueConfigurations": [
                MockConfig(
                    {
                        "Id": "test-event",
                        "QueueArn": "arn:aws:sqs:us-east-1:123456789012:queue",
                        "Events": ["s3:ObjectCreated:*"],
                        "Filter": {
                            "Key": {"FilterRules": [{"Name": "Prefix", "Value": "test/"}]},
                        },
                    }
                )
            ],
            "TopicConfigurations": [],
            "LambdaFunctionConfigurations": [],
        }

        result = build_notification_configuration(bucket_config)

        # Check all keys are snake_case
        assert "queue_configurations" in result
        config = result["queue_configurations"][0]
        assert "id" in config
        assert "queue_arn" in config
        assert "events" in config
        assert "filter" in config
        assert "filter_rules" in config["filter"]["key"]


class TestCreateWebsiteConfiguration:
    """Test the create_website_configuration function."""

    def test_creates_config_with_suffix_only(self):
        """Test creating configuration with only index document suffix."""
        result = create_website_configuration(suffix="index.html", error_key=None, redirect_all_requests=None)

        assert result == {"IndexDocument": {"Suffix": "index.html"}}

    def test_creates_config_with_error_key(self):
        """Test creating configuration with error document."""
        result = create_website_configuration(suffix="index.html", error_key="error.html", redirect_all_requests=None)

        assert result == {
            "IndexDocument": {"Suffix": "index.html"},
            "ErrorDocument": {"Key": "error.html"},
        }

    def test_creates_config_with_redirect_hostname_only(self):
        """Test creating configuration with redirect to hostname only."""
        result = create_website_configuration(suffix=None, error_key=None, redirect_all_requests="example.com")

        assert result == {"RedirectAllRequestsTo": {"HostName": "example.com"}}

    def test_creates_config_with_redirect_protocol_and_hostname(self):
        """Test creating configuration with redirect including protocol."""
        result = create_website_configuration(suffix=None, error_key=None, redirect_all_requests="https://example.com")

        assert result == {
            "RedirectAllRequestsTo": {
                "Protocol": "https",
                "HostName": "example.com",
            }
        }

    def test_creates_config_with_http_redirect(self):
        """Test creating configuration with HTTP redirect."""
        result = create_website_configuration(suffix=None, error_key=None, redirect_all_requests="http://example.com")

        assert result == {
            "RedirectAllRequestsTo": {
                "Protocol": "http",
                "HostName": "example.com",
            }
        }

    def test_handles_redirect_with_multiple_slashes(self):
        """Test that double slashes in redirect URL are properly handled."""
        result = create_website_configuration(
            suffix=None, error_key=None, redirect_all_requests="https://www.example.com"
        )

        assert result["RedirectAllRequestsTo"]["HostName"] == "www.example.com"
        assert result["RedirectAllRequestsTo"]["Protocol"] == "https"

    def test_raises_error_on_invalid_redirect_url(self):
        """Test that invalid redirect URL raises ValueError."""
        with pytest.raises(ValueError, match="Redirect URL appears invalid"):
            create_website_configuration(suffix=None, error_key=None, redirect_all_requests="invalid:url:with:colons")

    def test_creates_empty_config(self):
        """Test creating empty configuration when all parameters are None."""
        result = create_website_configuration(suffix=None, error_key=None, redirect_all_requests=None)

        assert result == {}

    def test_creates_config_with_custom_suffix(self):
        """Test creating configuration with custom index document suffix."""
        result = create_website_configuration(suffix="home.htm", error_key=None, redirect_all_requests=None)

        assert result == {"IndexDocument": {"Suffix": "home.htm"}}

    def test_creates_config_with_nested_error_path(self):
        """Test creating configuration with nested error document path."""
        result = create_website_configuration(
            suffix="index.html", error_key="errors/404.html", redirect_all_requests=None
        )

        assert result["ErrorDocument"]["Key"] == "errors/404.html"


class TestCreateMetricsConfiguration:
    """Test the create_metrics_configuration function."""

    def test_creates_config_with_id_only(self):
        """Test creating configuration with ID only (entire bucket metrics)."""
        result = create_metrics_configuration(mc_id="EntireBucket", filter_prefix=None, filter_tags={})

        assert result == {"Id": "EntireBucket"}

    def test_creates_config_with_prefix_filter(self):
        """Test creating configuration with prefix filter."""
        result = create_metrics_configuration(mc_id="Assets", filter_prefix="assets/", filter_tags={})

        assert result == {
            "Id": "Assets",
            "Filter": {"Prefix": "assets/"},
        }

    def test_creates_config_with_single_tag_filter(self):
        """Test creating configuration with single tag filter."""
        result = create_metrics_configuration(mc_id="Tagged", filter_prefix=None, filter_tags={"kind": "asset"})

        assert result == {
            "Id": "Tagged",
            "Filter": {"Tag": {"Key": "kind", "Value": "asset"}},
        }

    def test_creates_config_with_multiple_tag_filters(self):
        """Test creating configuration with multiple tag filters."""
        result = create_metrics_configuration(
            mc_id="MultiTag", filter_prefix=None, filter_tags={"priority": "high", "class": "blue"}
        )

        assert result["Id"] == "MultiTag"
        assert "Filter" in result
        assert "And" in result["Filter"]
        assert "Tags" in result["Filter"]["And"]
        assert len(result["Filter"]["And"]["Tags"]) == 2

        # Check tags are present (order may vary)
        tags = result["Filter"]["And"]["Tags"]
        tag_dict = {tag["Key"]: tag["Value"] for tag in tags}
        assert tag_dict == {"priority": "high", "class": "blue"}

    def test_creates_config_with_prefix_and_multiple_tags(self):
        """Test creating configuration with both prefix and multiple tags."""
        result = create_metrics_configuration(
            mc_id="PrefixAndTags", filter_prefix="documents/", filter_tags={"priority": "high", "class": "blue"}
        )

        assert result["Id"] == "PrefixAndTags"
        assert "Filter" in result
        assert "And" in result["Filter"]
        assert result["Filter"]["And"]["Prefix"] == "documents/"
        assert len(result["Filter"]["And"]["Tags"]) == 2

    def test_creates_config_with_empty_prefix(self):
        """Test that empty prefix is treated as no prefix."""
        result = create_metrics_configuration(mc_id="Test", filter_prefix="", filter_tags={})

        # Empty string is falsy, so no Filter should be added
        assert result == {"Id": "Test"}

    def test_prefix_not_added_with_single_tag(self):
        """Test that prefix alone with single tag doesn't use And structure."""
        result = create_metrics_configuration(mc_id="Test", filter_prefix=None, filter_tags={"env": "prod"})

        assert "Filter" in result
        assert "Tag" in result["Filter"]
        assert "And" not in result["Filter"]

    def test_tag_keys_and_values_preserved(self):
        """Test that tag keys and values are correctly preserved."""
        result = create_metrics_configuration(
            mc_id="Test", filter_prefix=None, filter_tags={"Environment": "Production", "Application": "WebServer"}
        )

        tags = result["Filter"]["And"]["Tags"]
        tag_dict = {tag["Key"]: tag["Value"] for tag in tags}
        assert tag_dict["Environment"] == "Production"
        assert tag_dict["Application"] == "WebServer"

    def test_creates_config_with_nested_prefix(self):
        """Test creating configuration with nested prefix path."""
        result = create_metrics_configuration(mc_id="Nested", filter_prefix="path/to/files/", filter_tags={})

        assert result["Filter"]["Prefix"] == "path/to/files/"

    def test_creates_config_with_special_characters_in_tags(self):
        """Test creating configuration with special characters in tag values."""
        result = create_metrics_configuration(
            mc_id="Special", filter_prefix=None, filter_tags={"owner": "user@example.com"}
        )

        assert result["Filter"]["Tag"]["Value"] == "user@example.com"


class TestNormalizeMetricsConfiguration:
    """Test the normalize_metrics_configuration function."""

    def test_normalizes_simple_config(self):
        """Test normalizing configuration with ID only."""
        config = {"Id": "EntireBucket"}
        result = normalize_metrics_configuration(config)

        assert result == {"id": "EntireBucket"}

    def test_normalizes_config_with_prefix_filter(self):
        """Test normalizing configuration with prefix filter."""
        config = {
            "Id": "Assets",
            "Filter": {"Prefix": "assets/"},
        }
        result = normalize_metrics_configuration(config)

        assert result["id"] == "Assets"
        assert result["filter"]["prefix"] == "assets/"

    def test_normalizes_config_with_single_tag(self):
        """Test normalizing configuration with single tag."""
        config = {
            "Id": "Tagged",
            "Filter": {"Tag": {"Key": "kind", "Value": "asset"}},
        }
        result = normalize_metrics_configuration(config)

        assert result["id"] == "Tagged"
        assert result["filter"]["tags"] == {"kind": "asset"}

    def test_normalizes_config_with_and_prefix_and_tags(self):
        """Test normalizing configuration with And filter (prefix + tags)."""
        config = {
            "Id": "Complex",
            "Filter": {
                "And": {
                    "Prefix": "documents/",
                    "Tags": [
                        {"Key": "priority", "Value": "high"},
                        {"Key": "class", "Value": "blue"},
                    ],
                }
            },
        }
        result = normalize_metrics_configuration(config)

        assert result["id"] == "Complex"
        assert result["filter"]["prefix"] == "documents/"
        assert result["filter"]["tags"] == {"priority": "high", "class": "blue"}

    def test_normalizes_empty_config(self):
        """Test normalizing None/empty configuration."""
        assert normalize_metrics_configuration(None) is None
        assert normalize_metrics_configuration({}) is None


class TestNormalizeCorsRules:
    """Test the normalize_cors_rules function."""

    def test_normalizes_cors_rules(self):
        """Test normalizing CORS rules."""
        cors_rules = [
            {
                "AllowedHeaders": ["Authorization"],
                "AllowedMethods": ["GET", "PUT"],
                "AllowedOrigins": ["https://example.com"],
                "MaxAgeSeconds": 3000,
            }
        ]
        result = normalize_cors_rules(cors_rules)

        assert len(result) == 1
        assert result[0]["allowed_headers"] == ["Authorization"]
        assert result[0]["allowed_methods"] == ["GET", "PUT"]
        assert result[0]["allowed_origins"] == ["https://example.com"]
        assert result[0]["max_age_seconds"] == 3000

    def test_normalizes_empty_cors_rules(self):
        """Test normalizing empty CORS rules list."""
        assert normalize_cors_rules([]) == []
        assert normalize_cors_rules(None) is None


class TestNormalizeLifecycleRules:
    """Test the normalize_lifecycle_rules function."""

    def test_normalizes_lifecycle_rules(self):
        """Test normalizing lifecycle rules."""
        lifecycle_config = {
            "Rules": [
                {
                    "ID": "DeleteOldLogs",
                    "Status": "Enabled",
                    "Prefix": "logs/",
                    "Expiration": {"Days": 30},
                }
            ]
        }
        result = normalize_lifecycle_rules(lifecycle_config)

        assert len(result) == 1
        assert result[0]["id"] == "DeleteOldLogs"
        assert result[0]["status"] == "Enabled"
        assert result[0]["prefix"] == "logs/"
        assert result[0]["expiration"]["days"] == 30

    def test_normalizes_empty_lifecycle_config(self):
        """Test normalizing empty lifecycle configuration."""
        assert normalize_lifecycle_rules({"Rules": []}) == []
        assert normalize_lifecycle_rules({}) == []


class TestNormalizeNotificationConfiguration:
    """Test the normalize_notification_configuration function."""

    def test_normalizes_notification_config(self):
        """Test normalizing notification configuration."""
        notification_config = {
            "TopicConfigurations": [
                {
                    "Id": "test-event",
                    "TopicArn": "arn:aws:sns:us-east-1:123456789012:topic",
                    "Events": ["s3:ObjectCreated:*"],
                }
            ],
            "QueueConfigurations": [],
            "LambdaFunctionConfigurations": [],
        }
        result = normalize_notification_configuration(notification_config)

        assert "topic_configurations" in result
        assert len(result["topic_configurations"]) == 1
        assert result["topic_configurations"][0]["id"] == "test-event"
        assert result["topic_configurations"][0]["topic_arn"] == "arn:aws:sns:us-east-1:123456789012:topic"

    def test_normalizes_empty_notification_config(self):
        """Test normalizing empty notification configuration."""
        assert normalize_notification_configuration({}) == {}
        assert normalize_notification_configuration(None) is None


class TestNormalizeWebsiteConfiguration:
    """Test the normalize_website_configuration function."""

    def test_normalizes_website_config(self):
        """Test normalizing website configuration."""
        website_config = {
            "IndexDocument": {"Suffix": "index.html"},
            "ErrorDocument": {"Key": "error.html"},
        }
        result = normalize_website_configuration(website_config)

        assert result["index_document"]["suffix"] == "index.html"
        assert result["error_document"]["key"] == "error.html"

    def test_normalizes_redirect_config(self):
        """Test normalizing redirect configuration."""
        website_config = {
            "RedirectAllRequestsTo": {
                "HostName": "example.com",
                "Protocol": "https",
            }
        }
        result = normalize_website_configuration(website_config)

        assert result["redirect_all_requests_to"]["host_name"] == "example.com"
        assert result["redirect_all_requests_to"]["protocol"] == "https"

    def test_normalizes_empty_website_config(self):
        """Test normalizing empty website configuration."""
        assert normalize_website_configuration({}) == {}
        assert normalize_website_configuration(None) is None
