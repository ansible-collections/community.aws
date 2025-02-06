#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = """
module: ssm_document_info
version_added: 9.1.0
short_description: Describes the specified Amazon Web Services Systems Manager document

description:
    - Retrieves information for the specified Amazon Web Services Systems Manager document.

author: 'Aubin Bikouo (@abikouo)'

options:
  name:
    description:
      - The name of the SSM document.
    required: true
    type: str
  document_version:
    description:
      - The document version for which you want information.
    type: str
  document_version_name:
    description:
      - The version of the artifact associated with the document.
    type: str
    aliases:
      - version_name

extends_documentation_fragment:
- amazon.aws.common.modules
- amazon.aws.region.modules
- amazon.aws.boto3
"""

EXAMPLES = """
- name: Retrieve information about SSM Document
  community.aws.ssm_inventory_info:
    name: SSM-SessionManagerRunShell

- name: Retrieve information about SSM Document using document_version
  community.aws.ssm_inventory_info:
    name: SSM-SessionManagerRunShell
    document_version: 1
"""


RETURN = """
document:
    returned: on success
    description: Information about the SSM document.
    type: dict
    contains:
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
"""


from typing import Any
from typing import Dict

try:
    import botocore
except ImportError:
    pass  # Handled by AnsibleAWSModule


from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.amazon.aws.plugins.module_utils.modules import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.tagging import boto3_tag_list_to_ansible_dict


def get_document(module: AnsibleAWSModule, ssm_client: Any) -> Dict[str, Any]:
    params = {}
    name = module.params.get("name")
    document_version = module.params.get("document_version")
    version_name = module.params.get("version_name")
    if document_version:
        params.update({"DocumentVersion": document_version})
    if version_name:
        params.update({"VersionName": version_name})

    try:
        return ssm_client.describe_document(Name=name, **params)["Document"]
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg=f"Failed to describe SSM document with name '{name}'")


def main():
    argument_spec = dict(
        name=dict(required=True),
        document_version=dict(),
        document_version_name=dict(type="str", aliases=["version_name"]),
    )

    module = AnsibleAWSModule(argument_spec=argument_spec, supports_check_mode=True)

    ssm_client = module.client("ssm")
    document = get_document(module, ssm_client)

    tags = boto3_tag_list_to_ansible_dict(document.pop("Tags"))
    document = camel_dict_to_snake_dict(document)
    document.update({"tags": tags})
    module.exit_json(document=document)


if __name__ == "__main__":
    main()
