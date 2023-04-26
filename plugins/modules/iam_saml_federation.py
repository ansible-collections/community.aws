#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: iam_saml_federation
version_added: 1.0.0
short_description: Maintain IAM SAML federation configuration.
description:
    - Provides a mechanism to manage AWS IAM SAML Identity Federation providers (create/update/delete metadata).
options:
    name:
        description:
            - The name of the provider to create.
        required: true
        type: str
    saml_metadata_document:
        description:
            - The XML document generated by an identity provider (IdP) that supports SAML 2.0.
        type: str
    state:
        description:
            - Whether to create or delete identity provider. If 'present' is specified it will attempt to update the identity provider matching the name field.
        default: present
        choices: [ "present", "absent" ]
        type: str

author:
    - Tony (@axc450)
    - Aidan Rowe (@aidan-)

extends_documentation_fragment:
    - amazon.aws.common.modules
    - amazon.aws.region.modules
    - amazon.aws.boto3
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details, see the AWS Guide for details.
# It is assumed that their matching environment variables are set.
# Creates a new iam saml identity provider if not present
- name: saml provider
  community.aws.iam_saml_federation:
      name: example1
      # the > below opens an indented block, so no escaping/quoting is needed when in the indentation level under this key
      saml_metadata_document: >
          <?xml version="1.0"?>...
          <md:EntityDescriptor
# Creates a new iam saml identity provider if not present
- name: saml provider
  community.aws.iam_saml_federation:
      name: example2
      saml_metadata_document: "{{ item }}"
  with_file: /path/to/idp/metdata.xml
# Removes iam saml identity provider
- name: remove saml provider
  community.aws.iam_saml_federation:
      name: example3
      state: absent
"""

RETURN = r"""
saml_provider:
    description: Details of the SAML Identity Provider that was created/modified.
    type: complex
    returned: present
    contains:
        arn:
            description: The ARN of the identity provider.
            type: str
            returned: present
            sample: "arn:aws:iam::123456789012:saml-provider/my_saml_provider"
        metadata_document:
            description: The XML metadata document that includes information about an identity provider.
            type: str
            returned: present
        create_date:
            description: The date and time when the SAML provider was created in ISO 8601 date-time format.
            type: str
            returned: present
            sample: "2017-02-08T04:36:28+00:00"
        expire_date:
            description: The expiration date and time for the SAML provider in ISO 8601 date-time format.
            type: str
            returned: present
            sample: "2017-02-08T04:36:28+00:00"
"""

try:
    import botocore
except ImportError:
    pass

from ansible_collections.amazon.aws.plugins.module_utils.retries import AWSRetry

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule


class SAMLProviderManager:
    """Handles SAML Identity Provider configuration"""

    def __init__(self, module):
        self.module = module

        try:
            self.conn = module.client("iam")
        except botocore.exceptions.ClientError as e:
            self.module.fail_json_aws(e, msg="Unknown AWS SDK error")

    # use retry decorator for boto3 calls
    @AWSRetry.jittered_backoff(retries=3, delay=5)
    def _list_saml_providers(self):
        return self.conn.list_saml_providers()

    @AWSRetry.jittered_backoff(retries=3, delay=5)
    def _get_saml_provider(self, arn):
        return self.conn.get_saml_provider(SAMLProviderArn=arn)

    @AWSRetry.jittered_backoff(retries=3, delay=5)
    def _update_saml_provider(self, arn, metadata):
        return self.conn.update_saml_provider(SAMLProviderArn=arn, SAMLMetadataDocument=metadata)

    @AWSRetry.jittered_backoff(retries=3, delay=5)
    def _create_saml_provider(self, metadata, name):
        return self.conn.create_saml_provider(SAMLMetadataDocument=metadata, Name=name)

    @AWSRetry.jittered_backoff(retries=3, delay=5)
    def _delete_saml_provider(self, arn):
        return self.conn.delete_saml_provider(SAMLProviderArn=arn)

    def _get_provider_arn(self, name):
        providers = self._list_saml_providers()
        for p in providers["SAMLProviderList"]:
            provider_name = p["Arn"].split("/", 1)[1]
            if name == provider_name:
                return p["Arn"]

        return None

    def create_or_update_saml_provider(self, name, metadata):
        if not metadata:
            self.module.fail_json(msg="saml_metadata_document must be defined for present state")

        res = {"changed": False}
        try:
            arn = self._get_provider_arn(name)
        except (botocore.exceptions.ValidationError, botocore.exceptions.ClientError) as e:
            self.module.fail_json_aws(e, msg="Could not get the ARN of the identity provider '{0}'".format(name))

        if arn:  # see if metadata needs updating
            try:
                resp = self._get_saml_provider(arn)
            except (botocore.exceptions.ValidationError, botocore.exceptions.ClientError) as e:
                self.module.fail_json_aws(e, msg="Could not retrieve the identity provider '{0}'".format(name))

            if metadata.strip() != resp["SAMLMetadataDocument"].strip():
                # provider needs updating
                res["changed"] = True
                if not self.module.check_mode:
                    try:
                        resp = self._update_saml_provider(arn, metadata)
                        res["saml_provider"] = self._build_res(resp["SAMLProviderArn"])
                    except botocore.exceptions.ClientError as e:
                        self.module.fail_json_aws(e, msg="Could not update the identity provider '{0}'".format(name))
            else:
                res["saml_provider"] = self._build_res(arn)

        else:  # create
            res["changed"] = True
            if not self.module.check_mode:
                try:
                    resp = self._create_saml_provider(metadata, name)
                    res["saml_provider"] = self._build_res(resp["SAMLProviderArn"])
                except botocore.exceptions.ClientError as e:
                    self.module.fail_json_aws(e, msg="Could not create the identity provider '{0}'".format(name))

        self.module.exit_json(**res)

    def delete_saml_provider(self, name):
        res = {"changed": False}
        try:
            arn = self._get_provider_arn(name)
        except (botocore.exceptions.ValidationError, botocore.exceptions.ClientError) as e:
            self.module.fail_json_aws(e, msg="Could not get the ARN of the identity provider '{0}'".format(name))

        if arn:  # delete
            res["changed"] = True
            if not self.module.check_mode:
                try:
                    self._delete_saml_provider(arn)
                except botocore.exceptions.ClientError as e:
                    self.module.fail_json_aws(e, msg="Could not delete the identity provider '{0}'".format(name))

        self.module.exit_json(**res)

    def _build_res(self, arn):
        saml_provider = self._get_saml_provider(arn)
        return {
            "arn": arn,
            "metadata_document": saml_provider["SAMLMetadataDocument"],
            "create_date": saml_provider["CreateDate"].isoformat(),
            "expire_date": saml_provider["ValidUntil"].isoformat(),
        }


def main():
    argument_spec = dict(
        name=dict(required=True),
        saml_metadata_document=dict(default=None, required=False),
        state=dict(default="present", required=False, choices=["present", "absent"]),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[("state", "present", ["saml_metadata_document"])],
    )

    name = module.params["name"]
    state = module.params.get("state")
    saml_metadata_document = module.params.get("saml_metadata_document")

    sp_man = SAMLProviderManager(module)

    if state == "present":
        sp_man.create_or_update_saml_provider(name, saml_metadata_document)
    elif state == "absent":
        sp_man.delete_saml_provider(name)


if __name__ == "__main__":
    main()
