# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from typing import Any
from typing import Dict
from typing import List

from ansible_collections.amazon.aws.plugins.module_utils.botocore import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.errors import AWSErrorHandler
from ansible_collections.amazon.aws.plugins.module_utils.exceptions import AnsibleAWSError
from ansible_collections.amazon.aws.plugins.module_utils.modules import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.retries import AWSRetry
from ansible_collections.amazon.aws.plugins.module_utils.tagging import ansible_dict_to_boto3_tag_list
from ansible_collections.amazon.aws.plugins.module_utils.tagging import compare_aws_tags


class AnsibleSSMError(AnsibleAWSError):
    pass


# SSM Documents
class SSMDocumentErrorHandler(AWSErrorHandler):
    _CUSTOM_EXCEPTION = AnsibleSSMError

    @classmethod
    def _is_missing(cls):
        return is_boto3_error_code("InvalidDocument")


@SSMDocumentErrorHandler.deletion_error_handler("delete document")
@AWSRetry.jittered_backoff()
def delete_document(client, name: str, **kwargs: Dict[str, Any]) -> bool:
    client.delete_document(Name=name, **kwargs)
    return True


@SSMDocumentErrorHandler.list_error_handler("describe document", {})
@AWSRetry.jittered_backoff()
def describe_document(client, name: str, **params: Dict[str, str]) -> Dict[str, Any]:
    return client.describe_document(Name=name, **params)["Document"]


@SSMDocumentErrorHandler.common_error_handler("create document")
@AWSRetry.jittered_backoff()
def create_document(client, name: str, content: str, **params: Dict[str, Any]) -> Dict[str, Any]:
    return client.create_document(Name=name, Content=content, **params)["DocumentDescription"]


@SSMDocumentErrorHandler.common_error_handler("update document")
@AWSRetry.jittered_backoff()
def update_document(client, name: str, content: str, **params: Dict[str, Any]) -> Dict[str, Any]:
    return client.update_document(Name=name, Content=content, **params)["DocumentDescription"]


@SSMDocumentErrorHandler.common_error_handler("update document default version")
@AWSRetry.jittered_backoff()
def update_document_default_version(client, name: str, default_version: str) -> Dict[str, Any]:
    return client.update_document_default_version(Name=name, DocumentVersion=default_version)


@SSMDocumentErrorHandler.list_error_handler("list documents", {})
@AWSRetry.jittered_backoff()
def list_documents(client, **kwargs: Dict[str, Any]) -> List[Dict[str, Any]]:
    paginator = client.get_paginator("list_documents")
    return paginator.paginate(**kwargs).build_full_result()["DocumentIdentifiers"]


@SSMDocumentErrorHandler.list_error_handler("list document versions", {})
@AWSRetry.jittered_backoff()
def list_document_versions(ssm: Any, name: str) -> List[Dict[str, Any]]:
    paginator = ssm.get_paginator("list_document_versions")
    return paginator.paginate(Name=name).build_full_result()["DocumentVersions"]


# Tags
def add_tags_to_resource(client, resource_type: str, resource_id: str, tags: List[Dict[str, Any]]) -> None:
    client.add_tags_to_resource(ResourceType=resource_type, ResourceId=resource_id, Tags=tags)


def remove_tags_from_resource(client, resource_type: str, resource_id: str, tag_keys: List[str]) -> None:
    client.remove_tags_from_resource(ResourceType=resource_type, ResourceId=resource_id, TagKeys=tag_keys)


def ensure_ssm_resource_tags(
    client, module: AnsibleAWSModule, current_tags: Dict[str, str], resource_id: str, resource_type: str
) -> bool:
    """Update resources tags"""
    tags = module.params.get("tags")
    purge_tags = module.params.get("purge_tags")
    tags_to_set, tags_to_unset = compare_aws_tags(current_tags, tags, purge_tags)

    if purge_tags and not tags:
        tags_to_unset = current_tags

    changed = False
    if tags_to_set:
        changed = True
        if not module.check_mode:
            add_tags_to_resource(
                client,
                resource_type=resource_type,
                resource_id=resource_id,
                tags=ansible_dict_to_boto3_tag_list(tags_to_set),
            )
    if tags_to_unset:
        changed = True
        if not module.check_mode:
            remove_tags_from_resource(
                client, resource_type=resource_type, resource_id=resource_id, tag_keys=tags_to_unset
            )
    return changed
