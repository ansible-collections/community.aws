#!/usr/bin/python
# This file is part of Ansible
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r'''
---
module: ec2_asg_tag
version_added: 1.5.0
short_description: Create and remove tags on AWS AutoScaling Groups (ASGs)
description:
  - Creates, modifies and removes tags for AutoScaling Groups
author: "Jonathan Sokolowski (@jsok)"
requirements: [ "boto3", "botocore" ]
options:
  name:
    description:
      - The ASG name.
    required: true
    type: str
  state:
    description:
      - Whether the tags should be present or absent on the ASG.
    default: present
    choices: ['present', 'absent']
    type: str
  tags:
    description:
      - A list of tags to add or remove from the ASG.
      - If the value provided for a key is not set and I(state=absent), the tag will be removed regardless of its current value.
      - Optional key is I(propagate_at_launch), which defaults to true.
    type: list
    elements: dict
  purge_tags:
    description:
      - Whether unspecified tags should be removed from the resource.
      - Note that when combined with I(state=absent), specified tags with non-matching values are not purged.
    type: bool
    default: false
extends_documentation_fragment:
- amazon.aws.aws
- amazon.aws.ec2
'''

EXAMPLES = r'''
- name: Ensure tags are present on an ASG
  community.aws.ec2_asg_tag:
    name: my-auto-scaling-group
    state: present
    tags:
      - environment: production
        propagate_at_launch: true
      - role: webserver
        propagate_at_launch: true

- name: Ensure tag is absent on an ASG
  community.aws.ec2_asg_tag:
    name: my-auto-scaling-group
    state: absent
    tags:
      - environment: development

- name: Remove all tags except Name from an ASG
  community.aws.ec2_asg_tag:
    name: my-auto-scaling-group
    state: absent
    tags:
      - Name: ''
    purge_tags: true
'''

RETURN = r'''
---
tags:
  description: A list containing the tags on the resource
  returned: always
  type: list
  sample: [
      {
          "key": "Name",
          "value": "public-webapp-production-1",
          "resource_id": "public-webapp-production-1",
          "resource_type": "auto-scaling-group",
          "propagate_at_launch": "true"
      },
      {
          "key": "env",
          "value": "production",
          "resource_id": "public-webapp-production-1",
          "resource_type": "auto-scaling-group",
          "propagate_at_launch": "true"
      }
  ]
added_tags:
  description: A list of tags that were added to the ASG
  returned: If tags were added
  type: list
removed_tags:
  description: A list of tags that were removed from the ASG
  returned: If tags were removed
  type: list
'''

try:
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:
    pass  # Handled by AnsibleAWSModule

from ansible.module_utils._text import to_native

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AWSRetry


def to_boto3_tag_list(tags, group_name):
    tag_list = []
    for tag in tags:
        for k, v in tag.items():
            if k == 'propagate_at_launch':
                continue
            tag_list.append(dict(Key=k,
                                 Value=to_native(v) if v else v,
                                 PropagateAtLaunch=bool(tag.get('propagate_at_launch', True)),
                                 ResourceType='auto-scaling-group',
                                 ResourceId=group_name))
    return tag_list


def compare_asg_tags(current_tags_dict, new_tags_dict, purge_tags=True):
    """
    Compare two ASG tag dicts.

    :param current_tags_dict: dict of currently defined boto3 tags.
    :param new_tags_dict: dict of new boto3 tags to apply.
    :param purge_tags: whether to consider tags not in new_tags_dict for removal.
    :return: tags_to_set: a dict of boto3 tags to set. If all tags are identical this list will be empty.
    :return: tags_keys_to_unset: a list of tag keys to be unset. If no tags need to be unset this list will be empty.
    """

    tags_to_set = {}
    tag_keys_to_unset = []

    for key in current_tags_dict.keys():
        if key not in new_tags_dict and purge_tags:
            tag_keys_to_unset.append(key)

    for key in set(new_tags_dict.keys()) - set(tag_keys_to_unset):
        if new_tags_dict[key] != current_tags_dict.get(key):
            tags_to_set[key] = new_tags_dict[key]

    return tags_to_set, tag_keys_to_unset


def tag_list_to_dict(tag_list):
    tags = {}
    for tag in tag_list:
        tags[tag['Key']] = tag
    return tags


def get_tags(autoscaling, module, group_name):
    filters = [{'Name': 'auto-scaling-group', 'Values': [group_name]}]
    try:
        result = AWSRetry.jittered_backoff()(autoscaling.describe_tags)(Filters=filters)
        return result['Tags']
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg='Failed to fetch tags for ASG {0}'.format(group_name))


def main():
    argument_spec = dict(
        name=dict(required=True, type='str'),
        tags=dict(type='list', default=[], elements='dict'),
        purge_tags=dict(type='bool', default=False),
        state=dict(default='present', choices=['present', 'absent']),
    )

    module = AnsibleAWSModule(argument_spec=argument_spec, supports_check_mode=True)

    group_name = module.params['name']
    state = module.params['state']
    tags = module.params['tags']
    purge_tags = module.params['purge_tags']

    result = {'changed': False}

    autoscaling = module.client('autoscaling')
    current_tag_list = get_tags(autoscaling, module, group_name)
    new_tag_list = to_boto3_tag_list(tags, group_name)

    # convert to a dict keyed by the tag Key to simplify existence checks
    current_tags = tag_list_to_dict(current_tag_list)
    new_tags = tag_list_to_dict(new_tag_list)

    add_tags, remove_keys = compare_asg_tags(current_tags, new_tags, purge_tags=purge_tags)

    remove_tags = {}
    if state == 'absent':
        for key in new_tags:
            tag_value = new_tags[key].get('Value')
            if key in current_tags:
                if tag_value is None or current_tags[key] == new_tags[key]:
                    remove_tags[key] = current_tags[key]

    for key in remove_keys:
        remove_tags[key] = current_tags[key]

    if remove_tags:
        remove_tag_list = remove_tags.items()
        result['changed'] = True
        result['removed_tags'] = remove_tag_list
        if not module.check_mode:
            try:
                AWSRetry.jittered_backoff()(autoscaling.delete_tags)(Tags=remove_tag_list)
            except (BotoCoreError, ClientError) as e:
                module.fail_json_aws(e, msg='Failed to remove tags {0} from ASG {1}'.format(remove_tag_list, group_name))

    if state == 'present' and add_tags:
        add_tag_list = add_tags.items()
        result['changed'] = True
        result['added_tags'] = add_tag_list
        if not module.check_mode:
            try:
                AWSRetry.jittered_backoff()(autoscaling.create_or_update_tags)(Tags=add_tag_list)
            except (BotoCoreError, ClientError) as e:
                module.fail_json_aws(e, msg='Failed to add tags {0} from ASG {1}'.format(add_tag_list, group_name))

    result['tags'] = get_tags(autoscaling, module, group_name)
    module.exit_json(**result)


if __name__ == '__main__':
    main()
