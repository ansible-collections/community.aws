#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: s3_bucket
version_added: 9.1.0
short_description: Manage SSM document
description:
  - Create, update or delete a Amazon Web Services Systems Manager (SSM document).
author:
  - Aubin Bikouo (@abikouo)
options:
  name:
    description:
      - The name of the document.
    required: true
    type: str
  state:
    description:
      - Create or delete SSM document.
    required: false
    default: present
    choices: [ 'present', 'absent' ]
    type: str
  content:
    description:
      - The content for the new SSM document in JSON or YAML format.
      - Required if O(state=present).
    type: raw
  document_version:
    description:
      - The version of the document that you want to delete.
      - If not provided, all versions of the document are deleted.
      - Ignored if O(state=present).
    type: str
  force_delete:
    description:
      - Some SSM document types require that you specify a Force flag before you can delete the document.
      - Ignored if O(state=present).
    type: bool
    default: false
  document_version_name:
    description:
      - When O(state=absent), specify the version name of the document that you want to delete.
      - When O(state=present), specify the version of the artifact you are creating with the document.
    type: str
    aliases: ['version_name']
  document_parameters:
    description:
      - Specify the parameters to use when creating the document.
      - Ignored if O(state=absent).
    type: dict
    suboptions:
      document_type:
        description:
          - The type of document to create.
        type: str
      document_format:
        description:
          - Specify the document format. The document format can be JSON, YAML, or TEXT.
        type: str
        default: 'JSON'
        choices: ['JSON', 'YAML', 'TEXT']
      target_type:
        description:
          - Specify a target type to define the kinds of resources the document can run on.
        type: str
      display_name:
        description:
          - Specify a friendly name for the SSM document. This value can differ for each version of the document.
        type: str
      attachments:
        description:
          - A list of key-value pairs that describe attachments to a version of a document.
        type: list
        elements: dict
        suboptions:
        key:
          description:
            - The key of a key-value pair that identifies the location of an attachment to a document.
          type: str
        values:
          description:
            - The value of a key-value pair that identifies the location of an attachment to a document.
          type: list
          elements: str
        name:
          description:
            - The name of the document attachment file.
          type: str
      requires:
        description:
          - A list of SSM documents required by a document.
        type: list
        elements: dict
        suboptions:
          name:
            description:
              - The name of the required SSM document. The name can be an Amazon Resource Name (ARN).
            type: str
            required: true
          version:
            description:
              - The document version required by the current document.
            type: str
          require_type:
            description:
              - The document type of the required SSM document.
            type: str
          version_name:
            description:
              - The version of the artifact associated with the document.
            type: str
extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.tags
  - amazon.aws.boto3

"""

EXAMPLES = r"""
# Note: These examples do not set authentication details, see the AWS Guide for details.

"""

RETURN = r"""
document:
    description: Information about the SSM document created or updated.
    type: dict
    returned: when O(state=present)
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
from typing import Tuple

try:
    import botocore
except ImportError:
    pass  # Handled by AnsibleAWSModule


from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict
from ansible.module_utils.common.dict_transformations import snake_dict_to_camel_dict

from ansible_collections.amazon.aws.plugins.module_utils.botocore import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.modules import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.tagging import ansible_dict_to_boto3_tag_list
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
    except is_boto3_error_code("InvalidDocument"):
        return None
    except (
        botocore.exceptions.ClientError,
        botocore.exceptions.BotoCoreError,
    ) as e:  # pylint: disable=duplicate-except
        module.fail_json_aws(e, msg=f"Failed to describe SSM document {name}")


def delete_document(module: AnsibleAWSModule, ssm_client: Any, existing_document: Dict[str, Any]) -> None:
    if not existing_document:
        module.exit_json(changed=False)
    if module.check_mode:
        module.exit_json(msg="Would have delete SSM document if not in check mode.", changed=True)

    params = {}
    name = module.params.get("name")
    document_version = module.params.get("document_version")
    version_name = module.params.get("version_name")
    force_delete = module.params.get("force_delete")
    if document_version:
        params.update({"DocumentVersion": document_version})
    if version_name:
        params.update({"VersionName": version_name})
    if force_delete:
        params.update({"Force": force_delete})

    changed = False
    try:
        ssm_client.delete_document(Name=name, **params)
    except is_boto3_error_code("InvalidDocument"):
        changed = True
    except (
        botocore.exceptions.ClientError,
        botocore.exceptions.BotoCoreError,
    ) as e:  # pylint: disable=duplicate-except
        module.fail_json_aws(e, msg=f"Failed to delete SSM document {name}")

    module.exit_json(changed=changed)


def create_document(module: AnsibleAWSModule, ssm_client: Any) -> Dict[str, Any]:
    name = module.params.get("name")
    content = module.params.get("content")
    version_name = module.params.get("version_name")
    document_parameters = module.params.get("document_parameters")
    tags = module.params.get("tags")

    params = {}
    if version_name:
        params["VersionName"] = version_name
    if document_parameters:
        params.update(snake_dict_to_camel_dict(document_parameters))
    if tags:
        params["Tags"] = ansible_dict_to_boto3_tag_list(tags)

    try:
        return ssm_client.create_document(
            Name=name,
            Content=content,
        )["DocumentDescription"]
    except (
        botocore.exceptions.ClientError,
        botocore.exceptions.BotoCoreError,
    ) as e:
        module.fail_json_aws(e, msg=f"Failed to create SSM document '{name}'")


def update_document(
    module: AnsibleAWSModule, ssm_client: Any, existing_document: Dict[str, Any]
) -> Tuple[Dict[str, Any], bool]:
    name = module.params.get("name")
    content = module.params.get("content")
    version_name = module.params.get("version_name")
    document_parameters = module.params.get("document_parameters")
    tags = module.params.get("tags")

    params = {}
    for aws_key, ansible_key in [
        ("DisplayName", "display_name"),
        ("DocumentFormat", "document_format"),
        ("TargetType", "target_type"),
    ]:
        if document_parameters.get(ansible_key) is not None and document_parameters.get(
            ansible_key
        ) != existing_document.get(aws_key):
            params[aws_key] = document_parameters.get(ansible_key)

    if document_parameters.get("attachments"):
        ansible_attachments = sorted([x.get("name") for x in document_parameters.get("attachments")])
        aws_attachments = sorted([x.get("Name") for x in existing_document.get("AttachmentsInformation")])
        if aws_attachments != ansible_attachments:
            params["Attachments"] = document_parameters.get("attachments")

    changed = False
    ssm_document = None
    if params:
        if version_name:
            params["VersionName"] = version_name
        if document_parameters:
            params.update(snake_dict_to_camel_dict(document_parameters))
        if tags:
            params["Tags"] = ansible_dict_to_boto3_tag_list(tags)

        changed = True
        if not module.check_mode:
            try:
                ssm_document = ssm_client.update_document(
                    Name=name,
                    Content=content,
                )["DocumentDescription"]
                changed = True
            except (
                botocore.exceptions.ClientError,
                botocore.exceptions.BotoCoreError,
            ) as e:
                module.fail_json_aws(e, msg=f"Failed to update SSM document '{name}'")

    return ssm_document, changed


def create_or_update_document(module: AnsibleAWSModule, ssm_client: Any, ssm_document: Dict[str, Any]) -> None:
    changed = False
    if ssm_document:
        document, changed = update_document(module, ssm_client, ssm_document)
    else:
        document = create_document(module, ssm_client)
        changed = True

    tags = boto3_tag_list_to_ansible_dict(document.pop("Tags"))
    document = camel_dict_to_snake_dict(document)
    document.update({"tags": tags})
    module.exit_json(changed=changed, document=document)


def main():
    argument_spec = dict(
        name=dict(required=True),
        content=dict(type="raw"),
        state=dict(default="present", choices=["present", "absent"]),
        document_version=dict(),
        force_delete=dict(type="bool", default=False),
        document_version_name=dict(type="str", aliases=["version_name"]),
        document_parameters=dict(
            type="dict",
            options=dict(
                document_type=dict(),
                document_format=dict(type="str", default="JSON", choices=["JSON", "YAML", "TEXT"]),
                target_type=dict(),
                display_name=dict(),
                attachments=dict(
                    type="list",
                    elements="dict",
                    options=dict(
                        key=dict(),
                        values=dict(type="list", elements="str"),
                        name=dict(),
                    ),
                ),
                requires=dict(
                    type="list",
                    elements="dict",
                    options=dict(
                        version_name=dict(),
                        require_type=dict(),
                        version=dict(),
                        name=dict(required=True),
                    ),
                ),
            ),
        ),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        required_if=[
            ["state", "present", ["content"]],
        ],
        supports_check_mode=True,
    )

    ssm_client = module.client("ssm")
    state = module.params.get("state")
    ssm_document = get_document(module, ssm_client)
    module.exit_json(ssm_document=ssm_document)

    if state == "absent":
        delete_document(module, ssm_client, ssm_document)
    else:
        create_or_update_document(module, ssm_client, ssm_document)


if __name__ == "__main__":
    main()
