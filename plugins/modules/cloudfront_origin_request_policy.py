#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
version_added: 7.2.0
module: cloudfront_origin_request_policy

short_description: Create, update and delete origin request policies to be used in a Cloudfront distribution's cache behavior

description:
  - Create, update and delete origin request policies to be used in a Cloudfront distribution's cache behavior
    for determining the values that CloudFront includes in requests that it sends to the origin.
  - See docs at U(https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/client/create_origin_request_policy.html).

author:
  - Zac Lovoy (@zwlovoy)

options:
  state:
    description: Decides if the named policy should be absent or present.
    choices:
      - present
      - absent
    default: present
    type: str
  name:
    description: A unique name to identify the origin request policy.
    required: true
    type: str
  comment:
    description: A comment to describe the origin request policy. The comment cannot be longer than 128 characters.
    required: false
    type: str
  headers_config:
    description:
      - The HTTP headers to include in origin requests. These can include headers from viewer requests and additional headers added by CloudFront.
      - For more information see the CloudFront documentation at
        U(https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_OriginRequestPolicyHeadersConfig.html)
    type: dict
    required: false
    suboptions:
      header_behavior:
        description: Determines whether any HTTP headers are included in requests that CloudFront sends to the origin.
        choices: ['none', 'whitelist', 'allViewer', 'allViewerAndWhitelistCloudFront', 'allExcept']
        type: str
        required: true
      headers:
        description:
          - Contains a list of HTTP header names.
          - For more information see the CloudFront documentation at U(https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_Headers.html)
        type: list
        elements: str
        required: false
  cookies_config:
    description:
      - The cookies from viewer requests to include in origin requests.
      - For more information see the CloudFront documentation at
        U(https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_OriginRequestPolicyCookiesConfig.html).
    type: dict
    required: false
    suboptions:
      cookie_behavior:
        description: Determines whether cookies in viewer requests are included in requests that CloudFront sends to the origin.
        choices: ['none', 'whitelist', 'all', 'allExcept']
        type: str
        required: true
      cookies:
        description:
          - Contains a list of cookie names.
          - For more information see the CloudFront documentation at U(https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_CookieNames.html).
        type: list
        elements: str
        required: false
  query_strings_config:
    description:
      - The URL query strings from viewer requests to include in origin requests.
      - For more information see the CloudFront documentation at
        U(https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_OriginRequestPolicyQueryStringsConfig.html).
    required: false
    type: dict
    suboptions:
      query_string_behavior:
        description: Determines whether any URL query strings in viewer requests are included in requests that CloudFront sends to the origin.
        choices: ['none', 'whitelist', 'all', 'allExcept']
        type: str
        required: true
      query_strings:
        description:
          - Contains the specific query strings in viewer requests that either are or are not included in requests that CloudFront sends to the origin.
          - For more information see the CloudFront documentation at U(https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_QueryStringNames.html)
        type: list
        elements: str
        required: false

extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
- name: Creating a basic CloudFront origin request policy with required fields for demonstration
  community.aws.cloudfront_origin_request_policy:
    name: my-origin-request-policy
    comment: My origin request policy for my CloudFront distribution
    headers_config:
      header_behavior: none
    cookies_config:
      cookie_behavior: none
    query_strings_config:
      query_string_behavior: none
    state: present

- name: Creating a CloudFront origin request policy using all predefined properties for demonstration
  community.aws.cloudfront_origin_request_policy:
    name: my-origin-request-policy
    comment: My origin request policy for my CloudFront distribution
    headers_config:
      header_behavior: whitelist
      headers:
        items:
          - accept
          - accept-language
          - host
          - user-agent
    cookies_config:
      cookie_behavior: whitelist
      cookies:
        items:
          - my-cookie
    query_strings_config:
      query_string_behavior: whitelist
      query_strings:
        items:
          - my-query-string
    state: present

- name: Delete header policy
  community.aws.cloudfront_origin_request_policy:
    name: my-origin-request-policy
    state: absent
"""

RETURN = r"""
origin_request_policy:
  description: The policy's information
  returned: success
  type: complex
  contains:
    id:
      description: The unique identifier for the origin request policy.
      returned: always
      type: str
      sample: '216adef6-5c7f-47e4-b989-5492eafa07d3'
    last_modified_time:
      description: The timestamp when the origin request policy was last modified.
      returned: always
      type: str
      sample: '2022-02-04T13:23:27.304000+00:00'
    origin_request_policy_config:
      description: The origin request policy configuration.
      returned: always
      type: complex
      contains:
        name:
          description: A unique name to identify the origin request policy.
          type: str
        comment:
          description: A comment to describe the origin request policy. The comment cannot be longer than 128 characters.
          type: str
        headers_config:
          description:
            - The HTTP headers to include in origin requests. These can include headers from viewer requests and additional headers added by CloudFront.
            - For more information see the CloudFront documentation at
              U(https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_OriginRequestPolicyHeadersConfig.html).
          type: dict
          contains:
            header_behavior:
              description: Determines whether any HTTP headers are included in requests that CloudFront sends to the origin.
              choices: ['none', 'whitelist', 'allViewer', 'allViewerAndWhitelistCloudFront', 'allExcept']
              type: str
            headers:
              description:
                - Contains a list of HTTP header names.
                - For more information see the CloudFront documentation at U(https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_Headers.html)
              type: list
              elements: str
        cookies_config:
          description:
            - The cookies from viewer requests to include in origin requests.
            - For more information see the CloudFront documentation at
              U(https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_OriginRequestPolicyCookiesConfig.html).
          type: dict
          contains:
            cookie_behavior:
              description: Determines whether cookies in viewer requests are included in requests that CloudFront sends to the origin.
              choices: ['none', 'whitelist', 'all', 'allExcept']
              type: str
            cookies:
              description:
                - Contains a list of cookie names.
                - For more information see the CloudFront documentation at U(https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_CookieNames.html)
              type: list
              elements: str
        query_strings_config:
          description:
            - The URL query strings from viewer requests to include in origin requests.
            - For more information see the CloudFront documentation at
              U(https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_OriginRequestPolicyQueryStringsConfig.html).
          type: dict
          contains:
            query_string_behavior:
              description: Determines whether any URL query strings in viewer requests are included in requests that CloudFront sends to the origin.
              choices: ['none', 'whitelist', 'all', 'allExcept']
              type: str
            query_strings:
              description:
                - Contains the specific query strings in viewer requests that either are or are not included in requests that CloudFront sends to the origin.
                - For more information see the CloudFront documentation at
                  U(https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_QueryStringNames.html).
              type: list
              elements: str
"""

import datetime

try:
    from botocore.exceptions import BotoCoreError
    from botocore.exceptions import ClientError
except ImportError:
    pass  # caught by imported AnsibleAWSModule

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict
from ansible.module_utils.common.dict_transformations import snake_dict_to_camel_dict

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule


class CloudfrontOriginRequestPolicyService(object):
    def __init__(self, module):
        self.module = module
        self.client = module.client("cloudfront")
        self.check_mode = module.check_mode

    def find_origin_request_policy(self, name):
        try:
            policies = self.client.list_origin_request_policies()["OriginRequestPolicyList"]["Items"]

            for policy in policies:
                if policy["OriginRequestPolicy"]["OriginRequestPolicyConfig"]["Name"] == name:
                    policy_id = policy["OriginRequestPolicy"]["Id"]
                    # as the list_ request does not contain the Etag (which we need), we need to do another get_ request here
                    matching_policy = self.client.get_origin_request_policy(Id=policy["OriginRequestPolicy"]["Id"])
                    break
                else:
                    matching_policy = None

            return matching_policy
        except (ClientError, BotoCoreError) as e:
            self.module.fail_json_aws(e, msg="Error fetching policy information")

    def create_origin_request_policy(self, name, comment, headers_config, cookies_config, query_strings_config):
        headers_config = snake_dict_to_camel_dict(headers_config, capitalize_first=True)
        cookies_config = snake_dict_to_camel_dict(cookies_config, capitalize_first=True)
        query_strings_config = snake_dict_to_camel_dict(query_strings_config, capitalize_first=True)

        config = {
            "Name": name,
            "Comment": comment,
            "HeadersConfig": self.insert_quantities(headers_config),
            "CookiesConfig": self.insert_quantities(cookies_config),
            "QueryStringsConfig": self.insert_quantities(query_strings_config),
        }

        config = {k: v for k, v in config.items() if v}

        matching_policy = self.find_origin_request_policy(name)

        changed = False

        if self.check_mode:
            self.module.exit_json(changed=True, origin_request_policy=camel_dict_to_snake_dict(config))

        if matching_policy is None:
            try:
                result = self.client.create_origin_request_policy(OriginRequestPolicyConfig=config)
                changed = True
            except (ClientError, BotoCoreError) as e:
                self.module.fail_json_aws(e, msg="Error creating policy")
        else:
            policy_id = matching_policy["OriginRequestPolicy"]["Id"]
            etag = matching_policy["ETag"]
            try:
                result = self.client.update_origin_request_policy(
                    Id=policy_id, IfMatch=etag, OriginRequestPolicyConfig=config
                )

                changed_time = result["OriginRequestPolicy"]["LastModifiedTime"]
                seconds = 3  # threshhold for returned timestamp age
                seconds_ago = datetime.datetime.now(changed_time.tzinfo) - datetime.timedelta(0, seconds)

                # consider change made by this execution of the module if returned timestamp was very recent
                if changed_time > seconds_ago:
                    changed = True
            except (ClientError, BotoCoreError) as e:
                self.module.fail_json_aws(e, msg="Updating creating policy")

        self.module.exit_json(changed=changed, **camel_dict_to_snake_dict(result))

    def delete_origin_request_policy(self, name):
        matching_policy = self.find_origin_request_policy(name)

        if matching_policy is None:
            self.module.exit_json(msg="Didn't find a matching policy by that name, not deleting")
        else:
            policy_id = matching_policy["OriginRequestPolicy"]["Id"]
            etag = matching_policy["ETag"]
            if self.check_mode:
                result = {}
            else:
                try:
                    result = self.client.delete_origin_request_policy(Id=policy_id, IfMatch=etag)
                except (ClientError, BotoCoreError) as e:
                    self.module.fail_json_aws(e, msg="Error deleting policy")

            self.module.exit_json(changed=True, **camel_dict_to_snake_dict(result))

    # Inserts a Quantity field into dicts with a list ('Items')
    # Implementation from cloudfront_response_headers_policy.py
    @staticmethod
    def insert_quantities(dict_with_items):
        # Items on top level case
        if "Items" in dict_with_items and isinstance(dict_with_items["Items"], list):
            dict_with_items["Quantity"] = len(dict_with_items["Items"])

        # Recursively check sub-dict
        for k, v in dict_with_items.items():
            if isinstance(v, dict):
                v = CloudfrontOriginRequestPolicyService.insert_quantities(v)

        return dict_with_items


def main():
    argument_spec = dict(
        name=dict(required=True, type="str"),
        comment=dict(type="str"),
        headers_config=dict(type="dict"),
        cookies_config=dict(type="dict"),
        query_strings_config=dict(type="dict"),
        state=dict(choices=["present", "absent"], type="str", default="present"),
    )

    module = AnsibleAWSModule(argument_spec=argument_spec, supports_check_mode=True)

    name = module.params.get("name")
    comment = module.params.get("comment", "")
    headers_config = module.params.get("headers_config")
    cookies_config = module.params.get("cookies_config")
    query_strings_config = module.params.get("query_strings_config")
    state = module.params.get("state")

    service = CloudfrontOriginRequestPolicyService(module)

    if state == "absent":
        service.delete_origin_request_policy(name)
    else:
        service.create_origin_request_policy(name, comment, headers_config, cookies_config, query_strings_config)


if __name__ == "__main__":
    main()
