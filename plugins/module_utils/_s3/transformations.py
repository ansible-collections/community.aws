# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

"""
S3 transformation and normalization functions.

This module contains functions for transforming S3 API responses into
Ansible-friendly formats and vice versa.
"""

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.amazon.aws.plugins.module_utils.tagging import ansible_dict_to_boto3_tag_list
from ansible_collections.amazon.aws.plugins.module_utils.transformation import boto3_resource_list_to_ansible_dict
from ansible_collections.amazon.aws.plugins.module_utils.transformation import boto3_resource_to_ansible_dict


def build_notification_configuration(bucket_config):
    """
    Build notification configuration dict for return value.

    Args:
        bucket_config: Dictionary with QueueConfigurations, TopicConfigurations,
                      LambdaFunctionConfigurations keys containing Config objects

    Returns:
        Dictionary with snake_case keys suitable for module return
    """
    notification_configs = dict(QueueConfigurations=[], TopicConfigurations=[], LambdaFunctionConfigurations=[])
    for target_configs in bucket_config:
        for cfg in bucket_config[target_configs]:
            notification_configs[target_configs].append(camel_dict_to_snake_dict(cfg.raw))
    return camel_dict_to_snake_dict(notification_configs)


def create_website_configuration(suffix, error_key, redirect_all_requests):
    """
    Create website configuration payload for S3 API.

    Args:
        suffix: Index document suffix (e.g., 'index.html')
        error_key: Error document key
        redirect_all_requests: Redirect URL (format: 'protocol://hostname' or 'hostname')

    Returns:
        Dictionary suitable for put_bucket_website API call

    Raises:
        ValueError: If redirect_all_requests URL format is invalid
    """
    website_configuration = {}

    if error_key is not None:
        website_configuration["ErrorDocument"] = {"Key": error_key}

    if suffix is not None:
        website_configuration["IndexDocument"] = {"Suffix": suffix}

    if redirect_all_requests is not None:
        website_configuration["RedirectAllRequestsTo"] = _create_redirect_dict(redirect_all_requests)

    return website_configuration


def _create_redirect_dict(url):
    """
    Parse redirect URL into protocol and hostname components.

    Args:
        url: Redirect URL (format: 'protocol://hostname' or 'hostname')

    Returns:
        Dictionary with Protocol and/or HostName keys

    Raises:
        ValueError: If URL format is invalid
    """
    redirect_dict = {}
    url_split = url.split(":")

    # Did we split anything?
    if len(url_split) == 2:
        redirect_dict["Protocol"] = url_split[0]
        redirect_dict["HostName"] = url_split[1].replace("//", "")
    elif len(url_split) == 1:
        redirect_dict["HostName"] = url_split[0]
    else:
        raise ValueError("Redirect URL appears invalid")

    return redirect_dict


def normalize_cors_rules(cors_rules):
    """
    Normalize CORS rules to snake_case.

    Args:
        cors_rules: List of CORS rule dictionaries from AWS API (CamelCase)

    Returns:
        List of normalized CORS rule dictionaries with snake_case keys
    """
    return boto3_resource_list_to_ansible_dict(cors_rules, transform_tags=False)


def normalize_lifecycle_rules(lifecycle_config):
    """
    Normalize lifecycle configuration to snake_case.

    Args:
        lifecycle_config: Lifecycle configuration dictionary from AWS API (CamelCase)

    Returns:
        List of normalized lifecycle rule dictionaries with snake_case keys
    """
    rules = lifecycle_config.get("Rules", [])
    return boto3_resource_list_to_ansible_dict(rules, transform_tags=False)


def normalize_notification_configuration(notification_config):
    """
    Normalize notification configuration to snake_case.

    Args:
        notification_config: Notification configuration dictionary from AWS API (CamelCase)

    Returns:
        Normalized notification configuration dictionary with snake_case keys
    """
    return boto3_resource_to_ansible_dict(notification_config, transform_tags=False)


def normalize_website_configuration(website_config):
    """
    Normalize website configuration to snake_case.

    Args:
        website_config: Website configuration dictionary from AWS API (CamelCase)

    Returns:
        Normalized website configuration dictionary with snake_case keys
    """
    return boto3_resource_to_ansible_dict(website_config, transform_tags=False)


def normalize_metrics_configuration(config):
    """
    Normalize a metrics configuration to snake_case.

    Args:
        config: Raw metrics configuration from AWS API (CamelCase)

    Returns:
        Normalized configuration dictionary with snake_case keys
    """
    if not config:
        return None

    normalized = {"id": config.get("Id")}

    if "Filter" in config:
        filter_config = config["Filter"]
        normalized_filter = {}

        if "Prefix" in filter_config:
            normalized_filter["prefix"] = filter_config["Prefix"]

        if "Tag" in filter_config:
            tag = filter_config["Tag"]
            normalized_filter["tags"] = {tag["Key"]: tag["Value"]}

        if "And" in filter_config:
            and_filter = filter_config["And"]
            if "Prefix" in and_filter:
                normalized_filter["prefix"] = and_filter["Prefix"]
            if "Tags" in and_filter:
                normalized_filter["tags"] = {tag["Key"]: tag["Value"] for tag in and_filter["Tags"]}

        if normalized_filter:
            normalized["filter"] = normalized_filter

    return normalized


def create_metrics_configuration(mc_id, filter_prefix, filter_tags):
    """
    Create metrics configuration payload for S3 API.

    Args:
        mc_id: Metrics configuration ID
        filter_prefix: Prefix filter for metrics
        filter_tags: Tag filters as Ansible dictionary

    Returns:
        Dictionary suitable for put_bucket_metrics_configuration API call
    """
    payload = {"Id": mc_id}
    # Just a filter_prefix or just a single tag filter is a special case
    if filter_prefix and not filter_tags:
        payload["Filter"] = {"Prefix": filter_prefix}
    elif not filter_prefix and len(filter_tags) == 1:
        payload["Filter"] = {"Tag": ansible_dict_to_boto3_tag_list(filter_tags)[0]}
    # Otherwise we need to use 'And'
    elif filter_tags:
        payload["Filter"] = {"And": {"Tags": ansible_dict_to_boto3_tag_list(filter_tags)}}
        if filter_prefix:
            payload["Filter"]["And"]["Prefix"] = filter_prefix

    return payload
