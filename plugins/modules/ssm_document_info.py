#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = """
module: ssm_document_info
version_added: 9.2.0
short_description: Obtain information about one or more AWS Systems Manager document
description:
    - Obtain information about one or more AWS Systems Manager document.
author: 'Aubin Bikouo (@abikouo)'
options:
  name:
    description:
      - The name of the SSM document to describe.
      - Mutually exclusive with O(filters).
    required: false
    type: str
  filters:
    description:
      - A dict of filters to apply. Each dict item consists of a filter key and a filter value. See
        U(https://docs.aws.amazon.com/systems-manager/latest/APIReference/API_ListDocuments.html) for possible filters. Filter
        names and values are case sensitive.
      - Mutually exclusive with O(name).
    required: false
    type: dict

extends_documentation_fragment:
- amazon.aws.common.modules
- amazon.aws.region.modules
- amazon.aws.boto3
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details, see the AWS Guide for details.

# Gather information about all SSM documents
- name: Gather information about all SSM documents
  community.aws.ssm_document_info:

# Gather information about all SSM documents owned by 'user-001'
- name: Gather information about all SSM documents owned by 'user-001'
  community.aws.ssm_document_info:
    filters:
      Owner: 'user-001'

# Gather detailed information about one specific SSM document
- name: Gather information about one document
  community.aws.ssm_document_info:
    name: 'sample-document-001'
"""


RETURN = """
document:
    returned: when O(name) is provided.
    description: Information about the SSM document.
    type: dict
    contains:
        sha1:
            description: The SHA1 hash of the document, which you can use for verification.
            returned: always.
            type: str
        hash:
            description: The Sha256 or Sha1 hash created by the system when the document was created..
            returned: always.
            type: str
        hash_type:
            description: The hash type of the document. Valid values include Sha256 or Sha1.
            returned: always.
            type: str
        name:
            description: The name of the SSM document.
            returned: always.
            type: str
        display_name:
            description: The friendly name of the SSM document.
            returned: always.
            type: str
        version_name:
            description: The version of the artifact associated with the document.
            returned: always.
            type: str
        owner:
            description: The Amazon Web Services user that created the document.
            returned: always.
            type: str
        created_date:
            description: The date when the document was created.
            returned: always.
            type: str
        status:
            description: The status of the SSM document.
            returned: always.
            type: str
        status_information:
            description: A message returned by Amazon Web Services Systems Manager that explains the RV(document.status) value.
            returned: always.
            type: str
        document_version:
            description: The document version.
            returned: always.
            type: str
        description:
            description: A description of the document.
            returned: always.
            type: str
        parameters:
            description: A description of the parameters for a document.
            returned: always.
            type: dict
            contains:
                name:
                    description: The name of the parameter.
                    returned: always.
                    type: str
                type:
                    description: The type of parameter.
                    returned: always.
                    type: str
                description:
                    description: A description of what the parameter does, how to use it, the default value, and whether or not the parameter is optional.
                    returned: always.
                    type: str
                default_value:
                    description: The default values for the parameters.
                    returned: If specified.
                    type: str
        platform_types:
            description: The list of operating system (OS) platforms compatible with this SSM document.
            returned: always.
            type: str
        document_type:
            description: The type of document.
            returned: always.
            type: str
        schema_version:
            description: The schema version.
            returned: always.
            type: str
        latest_version:
            description: The latest version of the document.
            returned: always.
            type: str
        default_version:
            description: The default version.
            returned: always.
            type: str
        document_format:
            description: The document format, either JSON or YAML.
            returned: always.
            type: str
        target_type:
            description: The target type which defines the kinds of resources the document can run on.
            returned: always.
            type: str
        attachments_information:
            description: Details about the document attachments, including names, locations, sizes, and so on.
            returned: always.
            type: list
            elements: dict
            contains:
                name:
                    description: The name of the attachment.
                    returned: always.
                    type: str
        requires:
            description: A list of SSM documents required by a document.
            returned: always.
            type: list
            elements: dict
            contains:
                name:
                    description: The name of the required SSM document.
                    returned: always.
                    type: str
                version:
                    description: The document version required by the current document.
                    returned: always.
                    type: str
                require_type:
                    description: The document type of the required SSM document.
                    returned: always.
                    type: str
                version_name:
                    description: An optional field specifying the version of the artifact associated with the document.
                    returned: always.
                    type: str
        author:
            description: The user in your organization who created the document.
            returned: always.
            type: str
        review_information:
            description: Details about the review of a document.
            returned: always.
            type: list
            elements: dict
            contains:
                reviewed_time:
                    description: The time that the reviewer took action on the document review request.
                    returned: always.
                    type: str
                status:
                    description: The current status of the document review request.
                    returned: always.
                    type: str
                reviewer:
                    description: The reviewer assigned to take action on the document review request.
                    returned: always.
                    type: str
        approved_version:
            description: The version of the document currently approved for use in the organization.
            returned: always.
            type: str
        pending_review_version:
            description: The version of the document that is currently under review.
            returned: always.
            type: str
        review_status:
            description: The current status of the review.
            returned: always.
            type: str
        category:
            description: The classification of a document to help you identify and categorize its use.
            returned: always.
            type: list
            elements: str
        category_enum:
            description: The value that identifies a category.
            returned: always.
            type: list
            elements: str
        tags:
            description: Tags of the s3 object.
            returned: always
            type: dict
            sample: {
                        "Owner": "dev001",
                        "env": "test"
                    }
        document_versions:
            description: The document versions.
            returned: always
            type: dict
            elements: list
            contains:
                name:
                    description: The document name.
                    returned: always.
                    type: str
                display_name:
                    description: The friendly name of the SSM document.
                    returned: always.
                    type: str
                document_version:
                    description: The document version.
                    returned: always.
                    type: str
                version_name:
                    description: The version of the artifact associated with the document.
                    returned: always.
                    type: str
                created_data:
                    description: The date the document was created.
                    returned: always.
                    type: str
                is_default_version:
                    description: An identifier for the default version of the document.
                    returned: always.
                    type: bool
                document_format:
                    description: The document format, either JSON or YAML.
                    returned: always.
                    type: str
                status:
                    description: The status of the SSM document, such as Creating, Active, Failed, and Deleting.
                    returned: always.
                    type: str
                status_information:
                    description: A message returned by Amazon Web Services Systems Manager that explains the RV(document.document_versions.status) value.
                    returned: always.
                    type: str
                review_status:
                    description: The current status of the approval review for the latest version of the document.
                    returned: always.
                    type: str
documents:
    returned: when O(filters) is provided.
    description: Information about the SSM document.
    type: list
    elements: dict
    contains:
        name:
            description: The name of the SSM document.
            returned: always.
            type: str
        display_name:
            description: The friendly name of the SSM document.
            returned: always.
            type: str
        version_name:
            description: The version of the artifact associated with the document.
            returned: always.
            type: str
        owner:
            description: The Amazon Web Services user that created the document.
            returned: always.
            type: str
        created_date:
            description: The date when the document was created.
            returned: always.
            type: str
        document_version:
            description: The document version.
            returned: always.
            type: str
        platform_types:
            description: The list of operating system (OS) platforms compatible with this SSM document.
            returned: always.
            type: str
        document_type:
            description: The type of document.
            returned: always.
            type: str
        schema_version:
            description: The schema version.
            returned: always.
            type: str
        document_format:
            description: The document format, either JSON or YAML.
            returned: always.
            type: str
        target_type:
            description: The target type which defines the kinds of resources the document can run on.
            returned: always.
            type: str
        requires:
            description: A list of SSM documents required by a document.
            returned: always.
            type: list
            elements: dict
            contains:
                name:
                    description: The name of the required SSM document.
                    returned: always.
                    type: str
                version:
                    description: The document version required by the current document.
                    returned: always.
                    type: str
                require_type:
                    description: The document type of the required SSM document.
                    returned: always.
                    type: str
                version_name:
                    description: An optional field specifying the version of the artifact associated with the document.
                    returned: always.
                    type: str
        author:
            description: The user in your organization who created the document.
            returned: always.
            type: str
        review_status:
            description: The current status of the review.
            returned: always.
            type: str
        tags:
            description: Tags of the s3 object.
            returned: always
            type: dict
            sample: {
                        "Owner": "dev001",
                        "env": "test"
                    }
"""


from typing import Any
from typing import Dict
from typing import List

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.amazon.aws.plugins.module_utils.modules import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.tagging import boto3_tag_list_to_ansible_dict

from ansible_collections.community.aws.plugins.module_utils.ssm import AnsibleSSMError
from ansible_collections.community.aws.plugins.module_utils.ssm import describe_document
from ansible_collections.community.aws.plugins.module_utils.ssm import list_document_versions
from ansible_collections.community.aws.plugins.module_utils.ssm import list_documents


def format_documents(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    results = []
    for doc in documents:
        tags = boto3_tag_list_to_ansible_dict(doc.pop("Tags", {}))
        doc = camel_dict_to_snake_dict(doc)
        doc.update({"tags": tags})
        results.append(doc)
    return results


def ansible_dict_to_aws_filters_list(filters_dict):
    """Convert an Ansible dict of filters to list of dicts that boto3 can use
    Args:
        filters_dict (dict): Dict of AWS filters.
    Basic Usage:
        >>> filters = {'some-aws-id': 'i-01234567'}
        >>> ansible_dict_to_boto3_filter_list(filters)
        {
            'some-aws-id': 'i-01234567'
        }
    Returns:
        List: List of AWS filters and their values
        [
            {
                'Key': 'some-aws-id',
                'Values': [
                    'i-01234567',
                ]
            }
        ]
    """

    filters_list = []
    for k, v in filters_dict.items():
        filter_dict = {"Key": k}
        if isinstance(v, bool):
            filter_dict["Values"] = [str(v).lower()]
        elif isinstance(v, int):
            filter_dict["Values"] = [str(v)]
        elif isinstance(v, str):
            filter_dict["Values"] = [v]
        else:
            filter_dict["Values"] = v

        filters_list.append(filter_dict)

    return filters_list


def list_ssm_documents(client: Any, module: AnsibleAWSModule) -> None:
    params = {}
    filters = module.params.get("filters")
    if filters:
        params["Filters"] = ansible_dict_to_aws_filters_list(filters)

    documents = list_documents(client, **params)
    module.exit_json(documents=format_documents(documents))


def describe_ssm_document(client: Any, module: AnsibleAWSModule) -> None:
    name = module.params.get("name")
    document = None

    # Describe document
    document = describe_document(client, name)
    if document:
        # Add document version
        document["DocumentVersions"] = list_document_versions(client, name)

        tags = boto3_tag_list_to_ansible_dict(document.pop("Tags", {}))
        document = camel_dict_to_snake_dict(document)
        document.update({"tags": tags})
    module.exit_json(document=document)


def main():
    module = AnsibleAWSModule(
        argument_spec=dict(
            name=dict(type="str"),
            filters=dict(type="dict"),
        ),
        supports_check_mode=True,
        mutually_exclusive=[["name", "filters"]],
    )
    ssm = module.client("ssm")
    name = module.params.get("name")

    try:
        if name:
            describe_ssm_document(ssm, module)
        else:
            list_ssm_documents(ssm, module)
    except AnsibleSSMError as e:
        module.fail_json_aws_error(e)


if __name__ == "__main__":
    main()
