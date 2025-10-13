#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2025 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: cloudfront_function
version_added: 10.1.0
short_description: Manage AWS CloudFront Functions
description:
  - Create, update, publish, or delete AWS CloudFront Functions.
  - Idempotent and supports check mode.

author:
  - Nicolas Boutet (@boutetnico)

options:
  name:
    description:
      - Name of the CloudFront Function.
    required: true
    type: str
  state:
    description:
      - Desired state of the function.
      - C(present) ensures the function exists but may be in DEVELOPMENT stage.
      - C(published) ensures the function exists and is published to LIVE stage.
      - C(absent) ensures the function is deleted.
    choices: [present, published, absent]
    default: present
    type: str
  comment:
    description:
      - Comment for the function.
      - Required when creating a new function.
    type: str
    default: ''
  runtime:
    description:
      - Runtime of the function.
    type: str
    default: cloudfront-js-2.0
    choices: ['cloudfront-js-1.0', 'cloudfront-js-2.0']
  code:
    description:
      - The JavaScript source code for the CloudFront function.
      - Can be provided as inline code or loaded from a file using the C(lookup) plugin.
      - Required when I(state=present) or I(state=published) and function does not exist.
      - If not provided for existing functions, only metadata will be updated.
    type: str

extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
- name: Create a CloudFront function with inline code
  community.aws.cloudfront_function:
    name: simple-redirect
    state: present
    comment: "Simple redirect function"
    runtime: cloudfront-js-2.0
    code: |
      function handler(event) {
        var request = event.request;
        var response = {
          statusCode: 301,
          statusDescription: 'Moved Permanently',
          headers: {
            'location': { value: 'https://example.com/' }
          }
        };
        return response;
      }

- name: Create a CloudFront function from file
  community.aws.cloudfront_function:
    name: edge-logic
    state: present
    comment: "Edge logic for viewer requests"
    runtime: cloudfront-js-2.0
    code: "{{ lookup('file', 'files/cloudfront_functions/edge-logic.js') }}"

- name: Update and publish function code
  community.aws.cloudfront_function:
    name: edge-logic
    state: published
    comment: "Updated edge logic"
    code: "{{ lookup('file', 'files/cloudfront_functions/edge-logic-v2.js') }}"

- name: Publish an existing function to LIVE (without code update)
  community.aws.cloudfront_function:
    name: edge-logic
    state: published
    code: "{{ lookup('file', 'files/cloudfront_functions/edge-logic.js') }}"

- name: Remove a function
  community.aws.cloudfront_function:
    name: edge-logic
    state: absent
"""

RETURN = r"""
changed:
  description: Whether a change occurred.
  type: bool
  returned: always
msg:
  description: Operation result message.
  type: str
  returned: always
function:
  description: Details of the CloudFront Function.
  type: dict
  returned: when state != absent
  contains:
    name:
      description: Name of the function.
      type: str
      returned: always
    arn:
      description: ARN of the function.
      type: str
      returned: always
    status:
      description: Status of the function (DEVELOPMENT or LIVE).
      type: str
      returned: always
    stage:
      description: Stage of the function (DEVELOPMENT or LIVE).
      type: str
      returned: always
    comment:
      description: Comment for the function.
      type: str
      returned: always
    runtime:
      description: Runtime of the function.
      type: str
      returned: always
    etag:
      description: ETag of the function.
      type: str
      returned: always
"""

from ansible_collections.amazon.aws.plugins.module_utils.retries import AWSRetry

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule

try:
    from botocore.exceptions import BotoCoreError
    from botocore.exceptions import ClientError
except ImportError:
    pass  # Handled by AnsibleAWSModule

import hashlib


def get_function(client, name, stage="DEVELOPMENT"):
    """Get function description or None if it doesn't exist."""
    try:
        return client.describe_function(Name=name, Stage=stage)
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchFunctionExists":
            return None
        raise


def is_function_published(client, name):
    """Check if function exists in LIVE stage."""
    try:
        client.describe_function(Name=name, Stage="LIVE")
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchFunctionExists":
            return False
        raise


def get_function_code_hash(client, name, stage="DEVELOPMENT"):
    """Get SHA256 hash of function code."""
    try:
        resp = client.get_function(Name=name, Stage=stage)
        # FunctionCode is a StreamingBody object, read it directly
        code_data = resp["FunctionCode"].read()
        return hashlib.sha256(code_data).hexdigest()
    except ClientError as e:
        if e.response["Error"]["Code"] == "NoSuchFunctionExists":
            return None
        raise


def create_function(client, module, name, comment, runtime, code_bytes):
    """Create a new CloudFront function."""
    if module.check_mode:
        return True, None

    try:
        response = client.create_function(
            Name=name,
            FunctionConfig={
                "Comment": comment,
                "Runtime": runtime,
            },
            FunctionCode=code_bytes,
        )
        return True, response
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg=f"Failed to create function {name}")


def update_function(client, module, name, etag, comment, runtime, code_bytes):
    """Update an existing CloudFront function."""
    if module.check_mode:
        return True, None

    try:
        response = client.update_function(
            Name=name,
            IfMatch=etag,
            FunctionConfig={
                "Comment": comment,
                "Runtime": runtime,
            },
            FunctionCode=code_bytes,
        )
        return True, response
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg=f"Failed to update function {name}")


def publish_function(client, module, name, etag):
    """Publish function to LIVE stage."""
    if module.check_mode:
        return True, None

    try:
        response = client.publish_function(
            Name=name,
            IfMatch=etag,
        )
        return True, response
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg=f"Failed to publish function {name}")


def delete_function(client, module, name, etag):
    """Delete a CloudFront function."""
    if module.check_mode:
        return True

    try:
        client.delete_function(
            Name=name,
            IfMatch=etag,
        )
        return True
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg=f"Failed to delete function {name}")


def format_function_output(func_description):
    """Format function details for output."""
    if not func_description:
        return None

    summary = func_description.get("FunctionSummary", {})
    metadata = summary.get("FunctionMetadata", {})
    config = summary.get("FunctionConfig", {})

    return {
        "name": summary.get("Name"),
        "arn": metadata.get("FunctionARN"),
        "status": summary.get("Status"),
        "stage": metadata.get("Stage"),
        "comment": config.get("Comment", ""),
        "runtime": config.get("Runtime"),
        "etag": func_description.get("ETag"),
        "last_modified_time": metadata.get("LastModifiedTime"),
    }


def main():
    argument_spec = dict(
        name=dict(required=True, type="str"),
        state=dict(default="present", choices=["present", "published", "absent"]),
        comment=dict(default="", type="str"),
        runtime=dict(
            default="cloudfront-js-2.0",
            type="str",
            choices=["cloudfront-js-1.0", "cloudfront-js-2.0"],
        ),
        code=dict(type="str"),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ["state", "present", ["code"], True],
            ["state", "published", ["code"], True],
        ],
    )

    name = module.params["name"]
    state = module.params["state"]
    comment = module.params["comment"]
    runtime = module.params["runtime"]
    code_string = module.params["code"]

    # Use module.client() to properly handle AWS credentials and config
    try:
        client = module.client("cloudfront", retry_decorator=AWSRetry.jittered_backoff())
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg="Failed to connect to AWS")

    changed = False
    msg = ""

    # Get current function state
    current = get_function(client, name)

    # Handle absent state
    if state == "absent":
        if not current:
            module.exit_json(changed=False, msg="Function does not exist")

        etag = current["ETag"]
        changed = delete_function(client, module, name, etag)
        module.exit_json(changed=changed, msg="Function deleted")

    # Process code string if provided
    code_bytes = None
    local_hash = None
    if code_string:
        code_bytes = code_string.encode("utf-8")
        local_hash = hashlib.sha256(code_bytes).hexdigest()

    # Handle function creation
    if not current:
        if not code_bytes:
            module.fail_json(msg="code parameter is required when creating a new function")

        changed, create_response = create_function(client, module, name, comment, runtime, code_bytes)

        if not module.check_mode:
            current = get_function(client, name)

            # Publish if state is published
            if state == "published":
                etag = current["ETag"]
                publish_function(client, module, name, etag)
                current = get_function(client, name)

        result = {
            "changed": changed,
            "msg": ("Function created and published" if state == "published" else "Function created"),
        }
        if not module.check_mode:
            result["function"] = format_function_output(current)
        module.exit_json(**result)

    # Function exists - check if update is needed
    etag = current["ETag"]
    summary = current.get("FunctionSummary", {})
    config = summary.get("FunctionConfig", {})

    # Get remote code hash if we have local code to compare
    remote_hash = None
    if local_hash:
        remote_hash = get_function_code_hash(client, name, stage="DEVELOPMENT")

    # Check what needs updating
    needs_config_update = comment != config.get("Comment", "") or runtime != config.get("Runtime")
    needs_code_update = local_hash and local_hash != remote_hash
    needs_update = needs_config_update or needs_code_update

    # Update function if needed
    if needs_update:
        if not code_bytes and needs_code_update:
            # This shouldn't happen but guard against it
            module.fail_json(msg="code parameter is required to update function code")

        # If only config changed, we need to provide existing code
        if needs_config_update and not needs_code_update:
            if not code_bytes:
                module.fail_json(msg="code parameter is required when updating function configuration")

        changed, update_response = update_function(client, module, name, etag, comment, runtime, code_bytes)

        if not module.check_mode:
            # Refresh function details to get new ETag
            current = get_function(client, name)
            etag = current["ETag"]

        msg = "Function updated"

    # Handle publish state
    if state == "published":
        if not module.check_mode:
            # Check if function is already published to LIVE stage
            already_published = is_function_published(client, name)

            # Only publish if not already in LIVE stage
            if not already_published:
                publish_changed, publish_response = publish_function(client, module, name, etag)
                changed = changed or publish_changed
                current = get_function(client, name)
                msg = msg + " and published" if msg else "Function published"
            elif not msg:
                msg = "Function already published"
        else:
            # In check mode, assume we would publish if not already live
            if not changed:
                already_published = is_function_published(client, name)
                if not already_published:
                    changed = True
                    msg = "Function would be published"
                else:
                    msg = "Function already published"

    if not msg:
        msg = "Function is up to date"

    result = {
        "changed": changed,
        "msg": msg,
    }

    if not module.check_mode:
        result["function"] = format_function_output(current)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
