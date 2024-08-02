# -*- coding: utf-8 -*-

# Copyright: (c) 2023, Andrew Roth <andrew@andrewjroth.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
name: secretsmanager_random_password
author:
  - Andrew Roth (@andrewjroth) <andrew@andrewjroth.com>

short_description: Generate a random password using AWS Secrets Manager
description:
  - Look up (really generate) a random password using AWS Secrets Manager's
    `secretsmanager:GetRandomPassword` API.
  - Optional parameters can be passed into this lookup; I(password_length) and I(exclude_characters)

options:
  _terms:
    description: As a shortcut, the password_length parameter can be specified as a term instead of using the keyword.
    required: False
    type: integer
  password_length:
    description: The length of the password. If you do not include this parameter, the default length is 32 characters.
    required: False
    type: integer
  exclude_characters:
    description: A string of the characters that you do not want in the password.
    required: False
    type: string
  exclude_numbers:
    description: Specifies whether to exclude numbers from the password (included by default).
    required: False
    type: boolean
  exclude_punctuation:
    description: |-
      Specifies whether to exclude punctuation characters from the password:
      `! " # $ % & ' ( ) * + , - . / : ; < = > ? @ [ \ ] ^ _ ` { | } ~` (included by default).
    required: False
    type: boolean
  exclude_uppercase:
    description: Specifies whether to exclude uppercase letters from the password (included by default).
    required: False
    type: boolean
  exclude_lowercase:
    description: Specifies whether to exclude lowercase letters from the password (included by default).
    required: False
    type: boolean
  include_space:
    description: Specifies whether to include the space character (excluded by default).
    required: False
    type: boolean
  require_each_included_type:
    description: Specifies whether to include at least one upper and lowercase letter, one number, and one punctuation.
    required: False
    type: boolean
  on_denied:
    description:
      - Action to take if access to the secret is denied.
      - C(error) will raise a fatal error when access to the secret is denied.
      - C(skip) will silently ignore the denied secret.
      - C(warn) will skip over the denied secret but issue a warning.
    default: error
    type: string
    choices: ['error', 'skip', 'warn']
extends_documentation_fragment:
  - amazon.aws.boto3
  - amazon.aws.common.plugins
  - amazon.aws.region.plugins
"""

EXAMPLES = r"""
 - name: generate random password
   debug: msg="{{ lookup('secretsmanager_random_password') }}"

 - name: generate random 12-character password without punctuation
   debug: msg="{{ lookup('secretsmanager_random_password', 12, exclude_punctuation=True) }}"

 - name: create a secret using a random password
   community.aws.secretsmanager_secret:
     name: 'test_secret_string'
     state: present
     secret_type: 'string'
     secret: "{{ lookup('secretsmanager_random_password') }}"
"""

RETURN = r"""
_raw:
  description:
    Returns the random password.  This password is not saved and will always be new.
"""

try:
    import botocore
except ImportError:
    pass  # Handled by AWSLookupBase

from ansible.errors import AnsibleLookupError
from ansible.module_utils._text import to_native
from ansible.module_utils.six import string_types
from ansible.module_utils.six import integer_types

from ansible_collections.amazon.aws.plugins.module_utils.botocore import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.retries import AWSRetry
from ansible_collections.amazon.aws.plugins.plugin_utils.lookup import AWSLookupBase


class LookupModule(AWSLookupBase):
    def run(self, terms, variables=None, **kwargs):
        """
        :param terms: a list containing the password length
            e.g. ['example_secret_name', 'example_secret_too' ]
        :param variables: ansible variables active at the time of the lookup
        :returns: A list of parameter values or a list of dictionaries if bypath=True.
        """

        super().run(terms, variables, **kwargs)

        # validate argument terms
        if len(terms) > 1:
            raise AnsibleLookupError("secretsmanager_random_password must have zero or one argument")

        on_denied = self.get_option("on_denied")

        # validate arguments 'on_denied'
        if on_denied is not None and (
            not isinstance(on_denied, string_types) or on_denied.lower() not in ["error", "warn", "skip"]
        ):
            raise AnsibleLookupError(
                f'"on_denied" must be a string and one of "error", "warn" or "skip", not {on_denied}'
            )

        params = {}
        # validate password length argument or option
        self.debug(f"Options: {self.get_options()}")
        password_length = self.get_option("password_length")
        if len(terms) == 1:
            if password_length is not None:
                raise AnsibleLookupError('"password_length" should be provided as argument or keyword, not both')
            password_length = terms[0]
        if password_length is not None:
            if not isinstance(password_length, integer_types) or password_length < 1:
                raise AnsibleLookupError('"password_length" must be an integer greater than zero, if provided')
            params["PasswordLength"] = password_length

        # validate exclude characters
        exclude_characters = self.get_option("exclude_characters")
        if exclude_characters is not None:
            if not isinstance(exclude_characters, string_types):
                raise AnsibleLookupError('"exclude_characters" must be a string, if provided')
            params["ExcludeCharacters"] = exclude_characters

        # validate options for parameters
        bool_options_to_params = {
            "exclude_numbers": "ExcludeNumbers",
            "exclude_punctuation": "ExcludePunctuation",
            "exclude_uppercase": "ExcludeUppercase",
            "exclude_lowercase": "ExcludeLowercase",
            "include_space": "IncludeSpace",
            "require_each_included_type": "RequireEachIncludedType",
        }
        for opt_name in bool_options_to_params.keys():
            opt_value = self.get_option(opt_name)
            if opt_value is not None:
                if not isinstance(opt_value, bool):
                    raise AnsibleLookupError(f'"{opt_name}" must be a boolean value, if provided')
                params[bool_options_to_params[opt_name]] = opt_value

        client = self.client("secretsmanager", AWSRetry.jittered_backoff())

        try:
            response = client.get_random_password(**params)
            return [response["RandomPassword"]]
        except is_boto3_error_code("AccessDeniedException"):  # pylint: disable=duplicate-except
            if on_denied == "error":
                raise AnsibleLookupError("Failed to generate random password (AccessDenied)")
            elif on_denied == "warn":
                self._display.warning("Skipping, access denied to generate random password")
        except (
            botocore.exceptions.ClientError,
            botocore.exceptions.BotoCoreError,
        ) as e:  # pylint: disable=duplicate-except
            raise AnsibleLookupError(f"Failed to retrieve secret: {to_native(e)}")
