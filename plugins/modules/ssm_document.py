#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: ssm_document
version_added: 9.2.0
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
      - Specify this option with O(state=present) to create a new document or a new document version.
      - Mutually exclusive with O(content_path).
    type: raw
  content_path:
    description:
      - The path to a file containing the data for the new SSM document in JSON or YAML format.
      - Specify this option with O(state=present) to create a new document or a new document version.
      - Mutually exclusive with O(content).
    type: path
  document_default_version:
    description:
      - The version of a custom document that you want to set as the default version.
      - If not provided, all versions of the document are deleted.
    type: str
  document_version:
    description:
      - When O(state=absent), The version of the document that you want to delete, if not provided,
        all versions of the document are deleted.
      - When O(state=present) and the document exists, this value corresponds to the document version
        to update, default to V($LATEST) when not provided.
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
  document_format:
    description:
        - Specify the document format. The document format can be JSON, YAML, or TEXT.
    type: str
    default: 'JSON'
    choices: ['JSON', 'YAML', 'TEXT']
  document_type:
    description:
        - The type of document to create.
    type: str
    choices:
        - 'Command'
        - 'Policy'
        - 'Automation'
        - 'Session'
        - 'Package'
        - 'ApplicationConfiguration'
        - 'ApplicationConfigurationSchema'
        - 'DeploymentStrategy'
        - 'ChangeCalendar'
        - 'Automation.ChangeTemplate'
        - 'ProblemAnalysis'
        - 'ProblemAnalysisTemplate'
        - 'CloudFormation'
        - 'ConformancePackTemplate'
        - 'QuickSetup'
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
- name: Delete SSM document
  community.aws.ssm_parameter:
    name: "Hello"
    state: absent

- name: Create SSM Command document
  community.aws.ssm_document:
    name: "SampleDocument"
    content_path: ssm-custom-document.json
    document_type: Command

- name: Update SSM document tags
  community.aws.ssm_document:
    name: "SampleDocument"
    state: present
    resource_tags:
      foo: bar
    purge_tags: true
"""

RETURN = r"""
document:
    description: Information about the SSM document created or updated.
    type: dict
    returned: On success
    contains:
        created_date:
            description: The date when the document was created.
            returned: always.
            type: str
            sample: "2025-03-17T19:07:14.611000+01:00"
        sha1:
            description: The SHA1 hash of the document, which you can use for verification.
            returned: if defined
            type: str
        hash:
            description: The Sha256 or Sha1 hash created by the system when the document was created..
            returned: always.
            type: str
            sample: "087cfdbb52b14aca6d357272426521c327cdccbf59a40ca77f8d53d367a6095b"
        hash_type:
            description: The hash type of the document. Valid values include Sha256 or Sha1.
            returned: always.
            type: str
            sample: "Sha256"
        name:
            description: The name of the SSM document.
            returned: always.
            type: str
            sample: "DocumentName"
        display_name:
            description: The friendly name of the SSM document.
            returned: if defined
            type: str
        version_name:
            description: The version of the artifact associated with the document.
            returned: if defined
            type: str
        owner:
            description: The Amazon Web Services user that created the document.
            returned: always.
            type: str
            sample: "0123456789"
        status:
            description: The status of the SSM document.
            returned: always.
            type: str
            sample: "Creating"
        status_information:
            description: A message returned by Amazon Web Services Systems Manager that explains the RV(document.status) value.
            returned: always.
            type: str
        document_version:
            description: The document version.
            returned: always.
            type: str
            sample: "1"
        description:
            description: A description of the document.
            returned: always.
            type: str
            sample: "A document description"
        parameters:
            description: A description of the parameters for a document.
            returned: if defined
            type: list
            elements: dict
            sample: [
                {
                    "default_value": "Ansible is super",
                    "description": "message to display",
                    "name": "Message",
                    "type": "String"
                }
            ]
        platform_types:
            description: The list of operating system (OS) platforms compatible with this SSM document.
            returned: always.
            type: str
            sample: [
                "Windows",
                "Linux",
                "MacOS"
            ]
        document_type:
            description: The type of document.
            returned: always.
            type: str
            sample: "Command"
        schema_version:
            description: The schema version.
            returned: always.
            type: str
            sample: "Creating"
        latest_version:
            description: The latest version of the document.
            returned: always.
            type: str
            sample: "1"
        default_version:
            description: The default version.
            returned: always.
            type: str
            sample: "1"
        document_format:
            description: The document format, either JSON or YAML.
            returned: always.
            type: str
            sample: "JSON"
        target_type:
            description: The target type which defines the kinds of resources the document can run on.
            returned: if defined
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
from typing import Optional

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict
from ansible.module_utils.common.dict_transformations import snake_dict_to_camel_dict

from ansible_collections.amazon.aws.plugins.module_utils.exceptions import is_ansible_aws_error_code
from ansible_collections.amazon.aws.plugins.module_utils.modules import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.tagging import ansible_dict_to_boto3_tag_list
from ansible_collections.amazon.aws.plugins.module_utils.tagging import boto3_tag_list_to_ansible_dict
from ansible_collections.amazon.aws.plugins.module_utils.transformation import scrub_none_parameters

from ansible_collections.community.aws.plugins.module_utils.ssm import AnsibleSSMError
from ansible_collections.community.aws.plugins.module_utils.ssm import create_document
from ansible_collections.community.aws.plugins.module_utils.ssm import delete_document
from ansible_collections.community.aws.plugins.module_utils.ssm import describe_document
from ansible_collections.community.aws.plugins.module_utils.ssm import ensure_ssm_resource_tags
from ansible_collections.community.aws.plugins.module_utils.ssm import list_document_versions
from ansible_collections.community.aws.plugins.module_utils.ssm import update_document
from ansible_collections.community.aws.plugins.module_utils.ssm import update_document_default_version


def format_document(client, name: str) -> Optional[Dict[str, Any]]:
    # Format result
    document = describe_document(client, name)
    if document:
        # Add document version
        document["DocumentVersions"] = list_document_versions(client, name)
        tags = boto3_tag_list_to_ansible_dict(document.pop("Tags", {}))
        document = camel_dict_to_snake_dict(document)
        document.update({"tags": tags})
    return document


def delete_ssm_document(module: AnsibleAWSModule, ssm_client: Any, document: Optional[Dict[str, Any]]) -> bool:
    if not document:
        return False
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

    return delete_document(ssm_client, name, **params)


def build_request_arguments(module: AnsibleAWSModule, document: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    attachments = module.params.get("attachments")
    requires = module.params.get("requires")
    tags = module.params.get("tags")

    # display_name, document_type, document_version_name, document_format, target_type
    params = {
        "DisplayName": module.params.get("display_name"),
        "VersionName": module.params.get("document_version_name"),
        "DocumentFormat": module.params.get("document_format"),
        "TargetType": module.params.get("target_type"),
    }

    # Requires
    if requires:
        params["Requires"] = snake_dict_to_camel_dict(requires)
    # Attachments
    if attachments:
        params["Attachments"] = snake_dict_to_camel_dict(attachments)
    # Tags (The ``update_document()`` does not accept the Tags and DocumentType parameters)
    if not document:
        params["Tags"] = ansible_dict_to_boto3_tag_list(tags)
        params["DocumentType"] = module.params.get("document_type")
    else:
        params["DocumentVersion"] = module.params.get("document_version") or "$LATEST"

    return scrub_none_parameters(params)


def create_or_update_document(module: AnsibleAWSModule, ssm_client: Any, document: Optional[Dict[str, Any]]) -> bool:
    name = module.params.get("name")
    content = module.params.get("content")
    content_path = module.params.get("content_path")
    if content_path:
        with open(content_path) as f:
            content = f.read()

    if not document and not content:
        module.fail_json(msg="One of 'content' or 'content_path' is required to create/update SSM document.")

    changed = False
    # Create/update document
    if content:
        if module.check_mode:
            operation = "create" if not document else "update"
            module.exit_json(changed=True, msg=f"Would have {operation} SSM document if not in check mode.")

        params = build_request_arguments(module, document)
        if not document:
            document = create_document(ssm_client, name=name, content=content, **params)
            changed = True
        else:
            try:
                document = update_document(ssm_client, name=name, content=content, **params)
                changed = True
            except is_ansible_aws_error_code("DuplicateDocumentContent"):
                pass

    # Ensure tags
    tags = module.params.get("tags")
    if tags is not None:
        current_tags = boto3_tag_list_to_ansible_dict(document.get("Tags", {}))
        changed |= ensure_ssm_resource_tags(
            ssm_client, module, current_tags, resource_id=name, resource_type="Document"
        )

    return changed


def main():
    argument_spec = dict(
        name=dict(required=True),
        content=dict(type="raw"),
        content_path=dict(type="path"),
        state=dict(default="present", choices=["present", "absent"]),
        document_version=dict(),
        document_default_version=dict(),
        force_delete=dict(type="bool", default=False),
        document_version_name=dict(type="str", aliases=["version_name"]),
        document_type=dict(
            choices=[
                "Command",
                "Policy",
                "Automation",
                "Session",
                "Package",
                "ApplicationConfiguration",
                "ApplicationConfigurationSchema",
                "DeploymentStrategy",
                "ChangeCalendar",
                "Automation.ChangeTemplate",
                "ProblemAnalysis",
                "ProblemAnalysisTemplate",
                "CloudFormation",
                "ConformancePackTemplate",
                "QuickSetup",
            ]
        ),
        document_format=dict(type="str", default="JSON", choices=["JSON", "YAML", "TEXT"]),
        target_type=dict(),
        display_name=dict(),
        attachments=dict(
            type="list",
            elements="dict",
            options=dict(
                key=dict(no_log=False),
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
        tags=dict(required=False, type="dict", aliases=["resource_tags"]),
        purge_tags=dict(required=False, type="bool", default=True),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        mutually_exclusive=[["content", "content_path"]],
        supports_check_mode=True,
    )

    ssm_client = module.client("ssm")
    state = module.params.get("state")
    name = module.params.get("name")
    document_default_version = module.params.get("document_default_version")
    try:
        document = describe_document(ssm_client, name)

        changed = False
        if state == "absent":
            changed = delete_ssm_document(module, ssm_client, document)
        else:
            changed = create_or_update_document(module, ssm_client, document)

        # document default version
        document = format_document(ssm_client, name)
        if document_default_version and document and document_default_version != document.get("default_version"):
            if not module.check_mode:
                update_document_default_version(ssm_client, name, document_default_version)
            changed = True
            document.update({"default_version": document_default_version})

        module.exit_json(changed=changed, document=document)
    except AnsibleSSMError as e:
        module.fail_json_aws_error(e)


if __name__ == "__main__":
    main()
