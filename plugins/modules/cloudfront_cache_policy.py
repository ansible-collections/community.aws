#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2024 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
version_added: 7.2.0
module: cloudfront_cache_policy

short_description: Create, update and delete cache policies to be used in a Cloudfront distribution's cache behavior

description:
  - Create, update and delete cache policies to be used in a Cloudfront distribution's cache behavior for configurating the cache key as well as the default, minimum, and maximum time to live (TTL) values that you want objects to stay in the CloudFront cache.
  - See docs at U(https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudfront/client/create_cache_policy.html)

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
      description: A unique name to identify the cache policy.
      required: true
      type: str
    comment:
      description: A comment to describe the cache policy. The comment cannot be longer than 128 characters.
      required: false
      type: str
    default_ttl:
      description: The default amount of time, in seconds, that you want objects to stay in the CloudFront cache before CloudFront sends another request to the origin to see if the object has been updated.
      required: false
      type: int
    min_ttl:
      description: The minimum amount of time, in seconds, that you want objects to stay in the CloudFront cache before CloudFront sends another request to the origin to see if the object has been updated.
      required: true
      type: int
    max_ttl:
      description: The maximum amount of time, in seconds, that objects stay in the CloudFront cache before CloudFront sends another request to the origin to see if the object has been updated.
      required: false
      type: int
    parameters_in_cache_key_and_forwarded_to_origin:
      description:
        - The HTTP headers, cookies, and URL query strings to include in the cache key.
          The values included in the cache key are also included in requests that CloudFront sends to the origin.
        - For more information see the CloudFront documentation at U(https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_ParametersInCacheKeyAndForwardedToOrigin.html)
      required: false
      type: dict
      suboptions:
        enable_accept_encoding_gzip:
          description: A flag that can affect whether the Accept-Encoding HTTP header is included in the cache key and included in requests that CloudFront sends to the origin.
          type: bool
          required: true
        enable_accept_encoding_brotli:
          description: A flag that can affect whether the Accept-Encoding HTTP header is included in the cache key and included in requests that CloudFront sends to the origin.
          type: bool
          required: true
        headers_config:
          description:
            - An object that determines whether any HTTP headers (and if so, which headers) are included in the cache key and in requests that CloudFront sends to the origin.
            - For more information see the CloudFront documentation at U(https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_CachePolicyHeadersConfig.html)
          type: dict
          required: true
          suboptions:
            header_behavior:
              description: Determines whether any HTTP headers are included in the cache key and in requests that CloudFront sends to the origin.
              choices: ['none', 'whitelist']
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
            - An object that determines whether any cookies in viewer requests (and if so, which cookies) are included in the cache key and in requests that CloudFront sends to the origin.
            - For more information see the CloudFront documentation at U(https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_CachePolicyCookiesConfig.html)
          required: true
          type: dict
          suboptions:
            cookie_behavior:
              description: Determines whether any cookies in viewer requests are included in the cache key and in requests that CloudFront sends to the origin.
              choices: ['none', 'whitelist', 'allExcept', 'all']
              required: true
              type: str
            cookies:
              description:
                - Contains a list of cookie names.
                - For more information see the CloudFront documentation at U(https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_CookieNames.html)
              type: list
              elements: str
              required: false
        query_strings_config:
          description:
            - An object that determines whether any URL query strings in viewer requests (and if so, which query strings) are included in the cache key and in requests that CloudFront sends to the origin.
            - For more information see the CloudFront documentation at U(https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_CachePolicyQueryStringsConfig.html)
          required: true
          type: dict
          suboptions:
            query_string_behavior:
              description: Determines whether any URL query strings in viewer requests are included in the cache key and in requests that CloudFront sends to the origin.
              choices: ['none', 'whitelist', 'allExcept', 'all']
              required: true
              type: str
            query_strings:
              description:
                - Contains the specific query strings in viewer requests that either are or are not included in the cache key and in requests that CloudFront sends to the origin.
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
- name: Creating a basic CloudFront cache policy with required fields and basic parameters_in_cache_key_and_forwarded_to_origin for demonstration
  community.aws.cloudfront_cache_policy:
    name: my-cache-policy
    min_ttl: 1
    max_ttl: 31536000
    parameters_in_cache_key_and_forwarded_to_origin:
      enable_accept_encoding_gzip: true
      enable_accept_encoding_brotli: true
      headers_config:
        header_behavior: none
      cookies_config:
        cookie_behavior: none
      query_strings_config:
        query_string_behavior: none
    state: present

- name: Creating a CloudFront cache policy using all predefined parameters_in_cache_key_and_forwarded_to_origin properties for demonstration
  community.aws.cloudfront_cache_policy:
    name: my-cache-policy
    comment: My cache policy for my CloudFront distribution
    default_ttl: 86400
    min_ttl: 1
    max_ttl: 31536000
    parameters_in_cache_key_and_forwarded_to_origin:
      enable_accept_encoding_gzip: true
      enable_accept_encoding_brotli: true
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
  community.aws.cloudfront_cache_policy:
    name: my-cache-policy
    state: absent
"""

RETURN = r"""
cache_policy:
    description: The policy's information
    returned: success
    type: complex
    contains:
      id:
        description: The unique identifier for the cache policy.
        returned: always
        type: str
        sample: 'b2884449-e4de-46a7-ac36-70bc7f1ddd6d'
      last_modified_time:
        description: The timestamp when the cache policy was last modified.
        returned: always
        type: str
        sample: '2022-02-04T13:23:27.304000+00:00'
      cache_policy_config:
        description: The cache policy configuration.
        returned: always
        type: complex
        contains:
          name:
            description: A unique name to identify the cache policy.
            type: str
            returned: always
            sample: my-cache-policy
          comment:
            description: A comment to describe the cache policy.
            type: str
            returned: always
            sample: My cache policy for my CloudFront distribution
          default_ttl:
            description: The default amount of time, in seconds, that you want objects to stay in the CloudFront cache before CloudFront sends another request to the origin to see if the object has been updated.
            type: int
            returned: always
            sample: 86400
          min_ttl:
            description: The minimum amount of time, in seconds, that you want objects to stay in the CloudFront cache before CloudFront sends another request to the origin to see if the object has been updated.
            type: int
            returned: always
            sample: 1
          max_ttl:
            description: The maximum amount of time, in seconds, that objects stay in the CloudFront cache before CloudFront sends another request to the origin to see if the object has been updated.
            type: int
            returned: always
            sample: 31536000
          parameters_in_cache_key_and_forwarded_to_origin:
            description:
              - The HTTP headers, cookies, and URL query strings to include in the cache key. The values included in the cache key are also included in requests that CloudFront sends to the origin.
              - For more information see the CloudFront documentation at U(https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_ParametersInCacheKeyAndForwardedToOrigin.html)
            type: dict
            contains:
              enable_accept_encoding_gzip:
                description: A flag that can affect whether the Accept-Encoding HTTP header is included in the cache key and included in requests that CloudFront sends to the origin.
                type: bool
              enable_accept_encoding_brotli:
                description: A flag that can affect whether the Accept-Encoding HTTP header is included in the cache key and included in requests that CloudFront sends to the origin.
                type: bool
              headers_config:
                description:
                  - An object that determines whether any HTTP headers (and if so, which headers) are included in the cache key and in requests that CloudFront sends to the origin.
                  - For more information see the CloudFront documentation at U(https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_CachePolicyHeadersConfig.html)
                type: dict
                contains:
                  header_behavior:
                    description: Determines whether any HTTP headers are included in the cache key and in requests that CloudFront sends to the origin.
                    choices: ['none', 'whitelist']
                    type: str
                  headers:
                    description:
                      - Contains a list of HTTP header names.
                      - For more information see the CloudFront documentation at U(https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_Headers.html)
                    type: list
                    elements: str
              cookies_config:
                description:
                  - An object that determines whether any cookies in viewer requests (and if so, which cookies) are included in the cache key and in requests that CloudFront sends to the origin.
                  - For more information see the CloudFront documentation at U(https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_CachePolicyCookiesConfig.html)
                type: dict
                contains:
                  cookie_behavior:
                    description: Determines whether any cookies in viewer requests are included in the cache key and in requests that CloudFront sends to the origin.
                    choices: ['none', 'whitelist', 'allExcept', 'all']
                    type: str
                  cookies:
                    description:
                      - Contains a list of cookie names.
                      - For more information see the CloudFront documentation at U(https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_CookieNames.html)
                    type: list
                    elements: str
              query_strings_config:
                description:
                    - An object that determines whether any URL query strings in viewer requests (and if so, which query strings) are included in the cache key and in requests that CloudFront sends to the origin.
                    - For more information see the CloudFront documentation at U(https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_CachePolicyQueryStringsConfig.html)
                type: dict
                contains:
                  query_string_behavior:
                    description: Determines whether any URL query strings in viewer requests are included in the cache key and in requests that CloudFront sends to the origin.
                    choices: ['none', 'whitelist', 'allExcept', 'all']
                    type: str
                  query_strings:
                    description:
                      - Contains the specific query strings in viewer requests that either are or are not included in the cache key and in requests that CloudFront sends to the origin.
                      - For more information see the CloudFront documentation at U(https://docs.aws.amazon.com/cloudfront/latest/APIReference/API_QueryStringNames.html)
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


class CloudfrontCachePolicyService(object):
    def __init__(self, module):
        self.module = module
        self.client = module.client("cloudfront")
        self.check_mode = module.check_mode

    def find_cache_policy(self, name):
        try:
            policies = self.client.list_cache_policies()["CachePolicyList"]["Items"]

            for policy in policies:
                if policy["CachePolicy"]["CachePolicyConfig"]["Name"] == name:
                    policy_id = policy["CachePolicy"]["Id"]
                    # as the list_ request does not contain the Etag (which we need), we need to do another get_ request here
                    matching_policy = self.client.get_cache_policy(Id=policy["CachePolicy"]["Id"])
                    break
                else:
                    matching_policy = None

            return matching_policy
        except (ClientError, BotoCoreError) as e:
            self.module.fail_json_aws(e, msg="Error fetching policy information")

    def create_cache_policy(
        self, name, comment, default_ttl, min_ttl, max_ttl, parameters_in_cache_key_and_forwarded_to_origin
    ):
        parameters_in_cache_key_and_forwarded_to_origin = snake_dict_to_camel_dict(
            parameters_in_cache_key_and_forwarded_to_origin, capitalize_first=True
        )

        config = {
            "Name": name,
            "Comment": comment,
            "DefaultTTL": default_ttl,
            "MinTTL": min_ttl,
            "MaxTTL": max_ttl,
            "ParametersInCacheKeyAndForwardedToOrigin": self.insert_quantities(
                parameters_in_cache_key_and_forwarded_to_origin
            ),
        }

        config = {k: v for k, v in config.items() if v}

        matching_policy = self.find_cache_policy(name)

        changed = False

        if self.check_mode:
            self.module.exit_json(changed=True, cache_policy=camel_dict_to_snake_dict(config))

        if matching_policy is None:
            try:
                result = self.client.create_cache_policy(CachePolicyConfig=config)
                changed = True
            except (ClientError, BotoCoreError) as e:
                self.module.fail_json_aws(e, msg="Error creating policy")
        else:
            policy_id = matching_policy["CachePolicy"]["Id"]
            etag = matching_policy["ETag"]
            try:
                result = self.client.update_cache_policy(Id=policy_id, IfMatch=etag, CachePolicyConfig=config)

                changed_time = result["CachePolicy"]["LastModifiedTime"]
                seconds = 3  # threshhold for returned timestamp age
                seconds_ago = datetime.datetime.now(changed_time.tzinfo) - datetime.timedelta(0, seconds)

                # consider change made by this execution of the module if returned timestamp was very recent
                if changed_time > seconds_ago:
                    changed = True
            except (ClientError, BotoCoreError) as e:
                self.module.fail_json_aws(e, msg="Updating creating policy")

        self.module.exit_json(changed=changed, **camel_dict_to_snake_dict(result))

    def delete_cache_policy(self, name):
        matching_policy = self.find_cache_policy(name)

        if matching_policy is None:
            self.module.exit_json(msg="Didn't find a matching policy by that name, not deleting")
        else:
            policy_id = matching_policy["CachePolicy"]["Id"]
            etag = matching_policy["ETag"]
            if self.check_mode:
                result = {}
            else:
                try:
                    result = self.client.delete_cache_policy(Id=policy_id, IfMatch=etag)
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

        # Items on second level case
        for k, v in dict_with_items.items():
            if isinstance(v, dict) and "Items" in v:
                v["Quantity"] = len(v["Items"])

        return dict_with_items


def main():
    argument_spec = dict(
        name=dict(required=True, type="str"),
        comment=dict(type="str"),
        default_ttl=dict(type="int"),
        min_ttl=dict(required=True, type="int"),
        max_ttl=dict(type="int"),
        parameters_in_cache_key_and_forwarded_to_origin=dict(),
        state=dict(choices=["present", "absent"], type="str", default="present"),
    )

    module = AnsibleAWSModule(argument_spec=argument_spec, supports_check_mode=True)

    name = module.params.get("name")
    comment = module.params.get("comment", "")
    default_ttl = module.params.get("default_ttl")
    min_ttl = module.params.get("min_ttl")
    max_ttl = module.params.get("max_ttl")
    parameters_in_cache_key_and_forwarded_to_origin = module.params.get(
        "parameters_in_cache_key_and_forwarded_to_origin"
    )
    state = module.params.get("state")

    service = CloudfrontCachePolicyService(module)

    if state == "absent":
        service.delete_cache_policy(name)
    else:
        service.create_cache_policy(
            name, comment, default_ttl, min_ttl, max_ttl, parameters_in_cache_key_and_forwarded_to_origin
        )


if __name__ == "__main__":
    main()
