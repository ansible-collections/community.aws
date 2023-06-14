#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: iam_instance_profile
version_added: 6.2.0
short_description: manage IAM instance profiles
description:
  - Manage IAM instance profiles.
author:
  - Mark Chappell (@tremble)
options:
  state:
    description:
      - Desired state of the instance profile.
    type: str
    choices: ["absent", "present"]
    default: "present"
  name:
    description:
      - Name of an instance profile.
    aliases:
      - instance_profile_name
    type: str
    required: True
  prefix:
    description:
      - The path prefix for filtering the results.
    aliases: ["path_prefix", "path"]
    type: str
    default: "/"

extends_documentation_fragment:
    - amazon.aws.common.modules
    - amazon.aws.region.modules
    - amazon.aws.boto3
"""

EXAMPLES = r"""
- name: Find all existing IAM instance profiles
  community.aws.iam_instance_profile_info:
  register: result

- name: Describe a single instance profile
  community.aws.iam_instance_profile_info:
    name: MyIAMProfile
  register: result

- name: Find all IAM instance profiles starting with /some/path/
  community.aws.iam_instance_profile_info:
    prefile: /some/path/
  register: result
"""

RETURN = r"""
iam_instance_profile:
  description: List of IAM instance profiles
  returned: always
  type: complex
  contains:
    arn:
      description: Amazon Resource Name for the instance profile.
      returned: always
      type: str
      sample: arn:aws:iam::123456789012:instance-profile/AnsibleTestProfile
    create_date:
      description: Date instance profile was created.
      returned: always
      type: str
      sample: '2023-01-12T11:18:29+00:00'
    instance_profile_id:
      description: Amazon Identifier for the instance profile.
      returned: always
      type: str
      sample: AROA12345EXAMPLE54321
    instance_profile_name:
      description: Name of instance profile.
      returned: always
      type: str
      sample: AnsibleTestEC2Policy
    path:
      description: Path of instance profile.
      returned: always
      type: str
      sample: /
    roles:
      description: List of roles associated with this instance profile.
      returned: always
      type: list
      sample: []
    tags:
      description: Instance profile tags.
      type: dict
      returned: always
      sample: '{"Env": "Prod"}'
"""

from ansible_collections.amazon.aws.plugins.module_utils.retries import AWSRetry

from ansible_collections.community.aws.plugins.module_utils.iam import AnsibleIAMError
from ansible_collections.community.aws.plugins.module_utils.iam import delete_iam_instance_profile
from ansible_collections.community.aws.plugins.module_utils.iam import list_iam_instance_profiles
from ansible_collections.community.aws.plugins.module_utils.iam import normalize_profile
from ansible_collections.community.aws.plugins.module_utils.iam import remove_role_from_iam_instance_profile
from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule


def describe_iam_instance_profile(client, name, prefix):
    profiles = []
    profiles = list_iam_instance_profiles(client, name=name, prefix=prefix)

    if not profiles:
        return None

    return normalize_profile(profiles[0])


def ensure_present(
    original_profile,
    client,
    name,
    prefix,
    check_mode,
):
    return False, None


def ensure_absent(
    original_profile,
    client,
    name,
    prefix,
    check_mode,
):
    if not original_profile:
        return False

    if check_mode:
        return True

    roles = original_profile.get("roles") or []
    for role in roles:
        remove_role_from_iam_instance_profile(client, name, role.get("role_name"))

    return delete_iam_instance_profile(client, name)


def main():
    """
    Module action handler
    """
    argument_spec = dict(
        name=dict(aliases=["instance_profile_name"], required=True),
        prefix=dict(aliases=["path_prefix", "path"], default="/"),
        state=dict(choices=["absent", "present"], default="present"),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    client = module.client("iam", retry_decorator=AWSRetry.jittered_backoff())

    try:
        name = module.params["name"]
        prefix = module.params["prefix"]
        state = module.params["state"]

        original_profile = describe_iam_instance_profile(client, name, prefix)

        if state == "absent":
            changed = ensure_absent(
                original_profile,
                client,
                name,
                prefix,
                module.check_mode,
            )
            final_profile = None
        else:
            changed, final_profile = ensure_present(
                original_profile,
                client,
                name,
                prefix,
                module.check_mode,
            )

        if not module.check_mode:
            final_profile = describe_iam_instance_profile(client, name, prefix)

    except AnsibleIAMError as e:
        if e.exception:
            module.fail_json_aws(e.exception, msg=e.message)
        module.fail_json(msg=e.message)

    results = {
        "changed": changed,
        "iam_instance_profile": final_profile,
    }
    if changed:
        results["diff"] = {
            "before": original_profile,
            "after": final_profile,
        }
    module.exit_json(**results)


if __name__ == "__main__":
    main()
