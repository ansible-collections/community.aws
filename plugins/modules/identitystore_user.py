#!/usr/bin/python

# Copyright (c) 2017 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: identitystore_user
version_added: 10.1.0
short_description: Manage users in Identity Store (IAM Identity Center)
description:
  - Manage users in the Identity Store service.
  - The Identity Store service is used by IAM Identity Center.
author:
  - Christian von Schultz (@vonschultz)
options:
  identity_store_id:
    description:
      - The ID of the identity store.
      - Found on the Settings page in IAM Identity Center.
    type: str
    required: true
  display_name:
    description:
      - A string containing the name of the user.
      - U(https://docs.aws.amazon.com/singlesignon/latest/IdentityStoreAPIReference/API_CreateUser.html).
    type: str
  user_name:
    description:
      - A string containing the user name of the user.
    required: true
    type: str
  name:
    description:
      - A dictionary containing the full name of the user.
      - U(https://docs.aws.amazon.com/singlesignon/latest/IdentityStoreAPIReference/API_Name.html).
    type: dict
    suboptions:
      family_name:
        description:
          - The family name of the user.
        type: str
      given_name:
        description:
          - The given name of the user.
        type: str
  emails:
    description:
      - A list of email dictionaries containing email addresses for the user.
      - U(https://docs.aws.amazon.com/singlesignon/latest/IdentityStoreAPIReference/API_Email.html).
    type: list
    elements: dict
    suboptions:
      value:
        description:
          - The e-mail address.
        required: true
        type: str
      type:
        description:
          - The type of e-mail address (e.g., "work").
        required: true
        type: str
      primary:
        description:
          - Whether this e-mail address is the user's primary address.
        required: true
        type: bool
  state:
    description:
      - Create/Update or Delete a user.
    choices: [ 'present', 'absent' ]
    required: True
    type: str
extends_documentation_fragment:
  - amazon.aws.boto3
  - amazon.aws.common.modules
  - amazon.aws.region.modules
"""

EXAMPLES = r"""
- name: Create/update user
  community.aws.identitystore_user:
    identity_store_id: d-cba0987654
    state: present
    user_name: john.doe@example.com
    name:
      family_name: Doe
      given_name: John
    display_name: John Doe
    emails:
      - value: john.doe@example.com
        type: work
        primary: true

- name: Remove user
  community.aws.identitystore_user:
    identity_store_id: d-c36714741a
    state: absent
    user_name: john.doe@example.com
"""

RETURN = r"""
identity_store_id:
  description:
    - Just echos the identity_store_id.
  type: str
  returned: success
user_id:
  description:
    - The identifier for a user in the identity store.
    - Only present if the user exists when we return.
  type: str
  returned: success
"""

from ansible.module_utils.common.dict_transformations import snake_dict_to_camel_dict

from ansible_collections.amazon.aws.plugins.module_utils.botocore import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.exceptions import AnsibleAWSError
from ansible_collections.amazon.aws.plugins.module_utils.modules import AnsibleAWSModule


def flatten_dict(nested_dict):
    flat = {}
    for key, value in nested_dict.items():
        if isinstance(value, dict):
            for inner_key, inner_value in flatten_dict(value).items():
                flat[f"{key}.{inner_key}"] = inner_value
        else:
            flat[key] = value
    return flat


def create_user(connection, module, user_attributes):
    args = {
        "identity_store_id": module.params.get("identity_store_id"),
        **user_attributes,
    }
    response = connection.create_user(**snake_dict_to_camel_dict(args, capitalize_first=True))
    module.exit_json(
        changed=True,
        user_id=response["UserId"],
        identity_store_id=response["IdentityStoreId"],
    )


def update_user(connection, module, user_id, user_attributes):
    response = connection.describe_user(IdentityStoreId=module.params.get("identity_store_id"), UserId=user_id)
    if all(
        value == response[key]
        for key, value in snake_dict_to_camel_dict(user_attributes, capitalize_first=True).items()
    ):
        module.exit_json(
            changed=False,
            user_id=user_id,
            identity_store_id=response["IdentityStoreId"],
        )
    elif module.check_mode:
        module.exit_json(
            changed=True,
            user_id=user_id,
            identity_store_id=response["IdentityStoreId"],
        )
    else:
        args = {
            "identity_store_id": module.params.get("identity_store_id"),
            "user_id": user_id,
            "operations": [
                {"attribute_path": key, "attribute_value": value}
                for key, value in snake_dict_to_camel_dict(flatten_dict(user_attributes)).items()
            ],
        }

        connection.update_user(**snake_dict_to_camel_dict(args, capitalize_first=True))
        module.exit_json(
            changed=True,
            user_id=args["user_id"],
            identity_store_id=args["identity_store_id"],
        )


def create_or_update_user(connection, module):
    identity_store_id = module.params.get("identity_store_id")
    user_name = module.params.get("user_name")

    user_attributes = {path: module.params.get(path) for path in ("user_name", "display_name", "emails", "name")}
    user_attributes = {key: value for key, value in user_attributes.items() if value is not None}

    try:
        user_id = connection.get_user_id(
            IdentityStoreId=identity_store_id,
            AlternateIdentifier={
                "UniqueAttribute": {
                    "AttributePath": "userName",
                    "AttributeValue": user_name,
                }
            },
        )
        update_user(
            connection=connection,
            module=module,
            user_id=user_id["UserId"],
            user_attributes=user_attributes,
        )
    except is_boto3_error_code("ResourceNotFoundException"):
        if module.check_mode:
            module.exit_json(
                changed=True,
                identity_store_id=identity_store_id,
                msg="Would have created user if not in check mode.",
            )
        else:
            create_user(
                connection=connection,
                module=module,
                user_attributes=user_attributes,
            )


def destroy_user(connection, module):
    identity_store_id = module.params.get("identity_store_id")
    user_name = module.params.get("user_name")

    try:
        user_id = connection.get_user_id(
            IdentityStoreId=identity_store_id,
            AlternateIdentifier={
                "UniqueAttribute": {
                    "AttributePath": "userName",
                    "AttributeValue": user_name,
                }
            },
        )
        if not module.check_mode:
            connection.delete_user(
                IdentityStoreId=identity_store_id,
                UserId=user_id["UserId"],
            )
        module.exit_json(changed=True, identity_store_id=identity_store_id)
    except is_boto3_error_code("ResourceNotFoundException"):
        module.exit_json(changed=False, identity_store_id=identity_store_id)


def main():
    argument_spec = dict(
        user_name=dict(required=True, type="str"),
        display_name=dict(required=False, type="str"),
        name=dict(
            required=False,
            type="dict",
            options=dict(
                family_name=dict(required=False, type="str"),
                given_name=dict(required=False, type="str"),
            ),
        ),
        emails=dict(
            required=False,
            type="list",
            elements="dict",
            options=dict(
                value=dict(required=True, type="str"),
                type=dict(required=True, type="str"),
                primary=dict(required=True, type="bool"),
            ),
        ),
        identity_store_id=dict(required=True, type="str"),
        state=dict(choices=["present", "absent"], required=True),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )

    connection = module.client("identitystore")

    state = module.params.get("state")

    try:
        if state == "present":
            create_or_update_user(connection, module)
        else:
            destroy_user(connection, module)
    except AnsibleAWSError as e:
        module.fail_json_aws_error(e)


if __name__ == "__main__":
    main()
