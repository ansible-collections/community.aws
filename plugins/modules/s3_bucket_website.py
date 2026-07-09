#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: s3_bucket_website
version_added: 1.0.0
short_description: Configure an s3 bucket as a website
description:
  - Configure an s3 bucket as a website
  - Since release 11.1.0 the preferred name is C(community.aws.s3_bucket_website), C(community.aws.s3_website) remains as an alias.
author:
  - Rob White (@wimnat)
options:
  name:
    description:
      - "Name of the s3 bucket"
    required: true
    type: str
  error_key:
    description:
      - "The object key name to use when a 4XX class error occurs. To remove an error key, set to None."
    type: str
  redirect_all_requests:
    description:
      - "Describes the redirect behavior for every request to this s3 bucket website endpoint"
    type: str
  state:
    description:
      - "Add or remove s3 website configuration"
    choices: [ 'present', 'absent' ]
    required: true
    type: str
  suffix:
    description:
      - >
        Suffix that is appended to a request that is for a directory on the website endpoint (e.g. if the suffix is index.html and you make a request to
        samplebucket/images/ the data that is returned will be for the object with the key name images/index.html). The suffix must not include a slash
        character.
    default: index.html
    type: str

extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details, see the AWS Guide for details.

- name: Configure an s3 bucket to redirect all requests to example.com
  community.aws.s3_website:
    name: mybucket.com
    redirect_all_requests: example.com
    state: present

- name: Remove website configuration from an s3 bucket
  community.aws.s3_website:
    name: mybucket.com
    state: absent

- name: Configure an s3 bucket as a website with index and error pages
  community.aws.s3_website:
    name: mybucket.com
    suffix: home.htm
    error_key: errors/404.htm
    state: present
"""

RETURN = r"""
index_document:
    description: index document
    type: complex
    returned: always
    contains:
        suffix:
            description: suffix that is appended to a request that is for a directory on the website endpoint
            returned: success
            type: str
            sample: index.html
error_document:
    description: error document
    type: complex
    returned: always
    contains:
        key:
            description:  object key name to use when a 4XX class error occurs
            returned: when error_document parameter set
            type: str
            sample: error.html
redirect_all_requests_to:
    description: where to redirect requests
    type: complex
    returned: always
    contains:
        host_name:
            description: name of the host where requests will be redirected.
            returned: when redirect all requests parameter set
            type: str
            sample: ansible.com
        protocol:
            description: protocol to use when redirecting requests.
            returned: when redirect all requests parameter set
            type: str
            sample: https
routing_rules:
    description: routing rules
    type: list
    returned: always
    contains:
        condition:
            type: complex
            description: A container for describing a condition that must be met for the specified redirect to apply.
            contains:
                http_error_code_returned_equals:
                    description: The HTTP error code when the redirect is applied.
                    returned: always
                    type: str
                key_prefix_equals:
                    description: object key name prefix when the redirect is applied. For example, to redirect
                                 requests for ExamplePage.html, the key prefix will be ExamplePage.html
                    returned: when routing rule present
                    type: str
                    sample: docs/
        redirect:
            type: complex
            description: Container for redirect information.
            returned: always
            contains:
                host_name:
                    description: name of the host where requests will be redirected.
                    returned: when host name set as part of redirect rule
                    type: str
                    sample: ansible.com
                http_redirect_code:
                    description: The HTTP redirect code to use on the response.
                    returned: when routing rule present
                    type: str
                protocol:
                    description: Protocol to use when redirecting requests.
                    returned: when routing rule present
                    type: str
                    sample: http
                replace_key_prefix_with:
                    description: object key prefix to use in the redirect request
                    returned: when routing rule present
                    type: str
                    sample: documents/
                replace_key_with:
                    description: object key prefix to use in the redirect request
                    returned: when routing rule present
                    type: str
                    sample: documents/
"""

import time

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict

from ansible_collections.amazon.aws.plugins.module_utils.s3 import AnsibleS3Error

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule
from ansible_collections.community.aws.plugins.module_utils.s3 import create_website_configuration
from ansible_collections.community.aws.plugins.module_utils.s3 import delete_bucket_website
from ansible_collections.community.aws.plugins.module_utils.s3 import get_bucket_website
from ansible_collections.community.aws.plugins.module_utils.s3 import put_bucket_website


def create_or_update_bucket_website(module, client):
    """Create or update bucket website configuration."""
    bucket_name = module.params.get("name")
    redirect_all_requests = module.params.get("redirect_all_requests")

    # If redirect_all_requests is set then don't use the default suffix that has been set
    if redirect_all_requests is not None:
        suffix = None
    else:
        suffix = module.params.get("suffix")
    error_key = module.params.get("error_key")

    website_config = get_bucket_website(client, bucket_name)

    # Check if update needed
    needs_update = False

    if not website_config:
        needs_update = True
    else:
        try:
            # Compare against what the new configuration would be
            new_configuration = create_website_configuration(suffix, error_key, redirect_all_requests)
            if website_config != new_configuration:
                needs_update = True
        except (KeyError, ValueError):
            # If config is malformed, update it
            needs_update = True

    if not needs_update:
        return False

    if module.check_mode:
        return True

    try:
        new_config = create_website_configuration(suffix, error_key, redirect_all_requests)
        put_bucket_website(client, bucket_name, new_config)
    except ValueError as e:
        module.fail_json(msg=str(e))

    # Wait 5 secs before returning to give it time to update
    time.sleep(5)
    return True


def delete_bucket_website_configuration(module, client):
    """Delete bucket website configuration."""
    bucket_name = module.params.get("name")

    website_config = get_bucket_website(client, bucket_name)

    # Check if already absent
    if not website_config:
        return False

    if module.check_mode:
        return True

    delete_bucket_website(client, bucket_name)
    return True


def main():
    argument_spec = dict(
        name=dict(type="str", required=True),
        state=dict(type="str", required=True, choices=["present", "absent"]),
        suffix=dict(type="str", required=False, default="index.html"),
        error_key=dict(type="str", required=False, no_log=False),
        redirect_all_requests=dict(type="str", required=False),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[
            ["redirect_all_requests", "suffix"],
            ["redirect_all_requests", "error_key"],
        ],
    )

    try:
        client = module.client("s3")
        state = module.params.get("state")

        if state == "present":
            changed = create_or_update_bucket_website(module, client)
        else:  # absent
            changed = delete_bucket_website_configuration(module, client)

        # Get final config for return value
        website_config = get_bucket_website(client, module.params["name"])
        module.exit_json(changed=changed, **camel_dict_to_snake_dict(website_config))
    except AnsibleS3Error as e:
        module.fail_json_aws_error(e)


if __name__ == "__main__":
    main()
