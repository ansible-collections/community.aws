#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

try:
    import botocore
except ImportError:
    pass  # Modules are responsible for handling this

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.amazon.aws.plugins.module_utils.botocore import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.exceptions import AnsibleAWSError
from ansible_collections.amazon.aws.plugins.module_utils.retries import AWSRetry
from ansible_collections.amazon.aws.plugins.module_utils.tagging import boto3_tag_list_to_ansible_dict

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule


class AnsibleIAMError(AnsibleAWSError):
    pass


@AWSRetry.jittered_backoff()
def _get_iam_instance_profiles_with_backoff(client, **kwargs):
    return client.get_instance_profile(**kwargs)["InstanceProfile"]


@AWSRetry.jittered_backoff()
def _list_iam_instance_profiles_with_backoff(client, **kwargs):
    paginator = client.get_paginator("list_instance_profiles")
    return paginator.paginate(**kwargs).build_full_result()["InstanceProfiles"]


@AWSRetry.jittered_backoff()
def _list_iam_instance_profiles_for_role_with_backoff(client, **kwargs):
    paginator = client.get_paginator("list_instance_profiles_for_role")
    return paginator.paginate(**kwargs).build_full_result()["InstanceProfiles"]


@AWSRetry.jittered_backoff()
def _delete_instance_profile(client, **kwargs):
    client.delete_instance_profile(**kwargs)


@AWSRetry.jittered_backoff()
def _remove_role_from_instance_profile(client, **kwargs):
    client.remove_role_from_instance_profile(**kwargs)


def delete_iam_instance_profile(client, name):
    try:
        _delete_instance_profile(client, InstanceProfileName=name)
    except is_boto3_error_code("NoSuchEntity"):
        # Deletion already happened.
        return False
    except (
        botocore.exceptions.BotoCoreError,
        botocore.exceptions.ClientError,
    ) as e:  # pylint: disable=duplicate-except
        raise AnsibleIAMError(message="Unable to delete instance profile", exception=e)
    return True


def remove_role_from_iam_instance_profile(client, profile_name, role_name):
    try:
        _remove_role_from_instance_profile(client, InstanceProfileName=profile_name, RoleName=role_name)
    except is_boto3_error_code("NoSuchEntity"):
        # Deletion already happened.
        return False
    except (
        botocore.exceptions.BotoCoreError,
        botocore.exceptions.ClientError,
    ) as e:  # pylint: disable=duplicate-except
        raise AnsibleIAMError(
            message="Unable to delete instance profile",
            exception=e,
            profile_name=profile_name,
            role_name=role_name,
        )
    return True


def list_iam_instance_profiles(client, name=None, prefix=None, role=None):
    """
    Returns a list of IAM instance profiles in boto3 format.
    Profiles need to be converted to Ansible format using normalize_profile before being displayed.

    See also: normalize_profile
    """
    try:
        if role:
            return _list_iam_instance_profiles_for_role_with_backoff(client, RoleName=role)
        if name:
            # Unlike the others this returns a single result, make this a list with 1 element.
            return [_get_iam_instance_profiles_with_backoff(client, InstanceProfileName=name)]
        if prefix:
            return _list_iam_instance_profiles_with_backoff(client, PathPrefix=prefix)
        return _list_iam_instance_profiles_with_backoff(client)
    except is_boto3_error_code("NoSuchEntity"):
        return []
    except (
        botocore.exceptions.BotoCoreError,
        botocore.exceptions.ClientError,
    ) as e:  # pylint: disable=duplicate-except
        raise AnsibleIAMError(message="Unable to list instance profiles", exception=e)


def normalize_profile(profile):
    """
    Converts a boto3 format IAM instance profile into "Ansible" format
    """

    new_profile = camel_dict_to_snake_dict(profile, ignore_list=["tags"])
    if profile.get("Roles"):
        new_profile["roles"] = [normalize_role(role) for role in profile.get("Roles")]
    if profile.get("Tags"):
        new_profile["tags"] = boto3_tag_list_to_ansible_dict(profile.get("Tags"))
    else:
        new_profile["tags"] = {}
    return new_profile


def normalize_role(role):
    """
    Converts a boto3 format IAM instance role into "Ansible" format
    """

    new_role = camel_dict_to_snake_dict(role, ignore_list=["tags"])
    new_role["assume_role_policy_document_raw"] = role.get("AssumeRolePolicyDocument")
    if role.get("InstanceProfiles"):
        new_role["instance_profiles"] = [normalize_profile(profile) for profile in role.get("InstanceProfiles")]
    if role.get("Tags"):
        new_role["tags"] = boto3_tag_list_to_ansible_dict(role.get("Tags"))
    else:
        new_role["tags"] = {}
    return new_role
