#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
#
# This module is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this software.  If not, see <http://www.gnu.org/licenses/>.
#
# Author:
#   - Matthew Davis <Matthew.Davis.2@team.telstra.com>
#     on behalf of Telstra Corporation Limited

from __future__ import (absolute_import, division, print_function)
__metaclass__ = type


DOCUMENTATION = r'''
---
module: aws_acm
short_description: >
  Request, upload and delete certificates in the AWS Certificate Manager service.
version_added: 1.0.0
description:
  - >
    Request, renew, import and delete certificates in Amazon Web Service's
    Certificate Manager (AWS ACM).
  - The ACM API allows users to upload multiple certificates for the same domain
    name, and even multiple identical certificates. This module attempts to
    restrict such freedoms, to be idempotent, as per the Ansible philosophy.
    It does this through applying AWS resource "Name" tags to ACM certificates.
  - >
    When I(state=present),
    if there is one certificate in ACM
    with a C(Name) tag equal to the C(name_tag) parameter,
    and an identical body and chain,
    this task will succeed without effect.
  - >
    When I(state=present),
    if there is one certificate in ACM
    a I(Name) tag equal to the I(name_tag) parameter,
    and a different body,
    this task will overwrite that certificate.
  - >
    When I(state=present),
    if there are multiple certificates in ACM
    with a I(Name) tag equal to the I(name_tag) parameter,
    this task will fail.
  - >
    When I(state=absent) and I(certificate_arn) is defined,
    this module will delete the ACM resource with that ARN if it exists in this
    region, and succeed without effect if it doesn't exist.
  - >
    When I(state=absent) and I(domain_name) is defined, this module will delete
    all ACM resources in this AWS region with a corresponding domain name.
    If there are none, it will succeed without effect.
  - >
    When I(state=absent) and I(certificate_arn) is not defined,
    and I(domain_name) is not defined, this module will delete all ACM resources
    in this AWS region with a corresponding I(Name) tag.
    If there are none, it will succeed without effect.
  - >
    Note that this may not work properly with keys of size 4096 bits, due to a
    limitation of the ACM API.
options:
  certificate:
    description:
      - The body of the PEM encoded public certificate.
      - Required when I(state) is not C(absent) and the certificate does not exist.
      - >
        If your certificate is in a file,
        use C(lookup('file', 'path/to/cert.pem')).
    type: str
  certificate_arn:
    description:
      - The ARN of a certificate in ACM to modify or delete.
      - >
        If I(state=present), the certificate with the specified ARN can be updated.
        For example, this can be used to add/remove tags to an existing certificate.
      - >
        If I(state=absent), you must provide one of
        I(certificate_arn), I(domain_name) or I(name_tag).
      - >
        If I(state=absent) and no resource exists with this ARN in this region,
        the task will succeed with no effect.
      - >
        If I(state=absent) and the corresponding resource exists in a different
        region, this task may report success without deleting that resource.
    type: str
    aliases: [arn]
  certificate_chain:
    description:
      - The body of the PEM encoded chain for your certificate.
      - >
        If your certificate chain is in a file,
        use C(lookup('file', 'path/to/chain.pem')).
      - Ignored when I(state=absent)
    type: str
  domain_name:
    description:
      - The domain name of the certificate.
      - >
        If I(state=absent) and I(domain_name) is specified,
        this task will delete all ACM certificates with this domain.
      - >
        Exactly one of I(domain_name), I(name_tag) and I(certificate_arn)
        must be provided.
      - >
        If I(state=present) and I(certificate_request) is not specified, this must not be specified.
        In that case, a certificate is imported to ACM; the domain name is encoded within
        the public certificate's body.
      - >
        If I(state=present) and I(certificate_request) is specified, this must be specified.
        A certificate is requested from ACM. In that case, the I(domain_name) is the fully
        qualified domain name (FQDN), such as www.example.com, that you want to secure with
        an ACM certificate.
      - >
        Use an asterisk (*) to create a wildcard certificate that protects several sites
        in the same domain.
        For example, *.example.com protects www.example.com, site.example.com
        and images.example.com.
      - >
        The first domain name you enter cannot exceed 64 octets, including periods.
        Each subsequent Subject Alternative Name (SAN), however, can be up to 253 octets
        in length.
    type: str
    aliases: [domain]
  name_tag:
    description:
      - >
        The unique identifier for tagging resources using AWS tags,
        with key I(Name).
      - This can be any set of characters accepted by AWS for tag values.
      - >
        This is to ensure Ansible can treat certificates idempotently,
        even though the ACM API allows duplicate certificates.
      - If I(state=preset), this must be specified.
      - >
        If I(state=absent) and I(name_tag) is specified,
        this task will delete all ACM certificates with this Name tag.
      - >
        If I(state=absent), you must provide exactly one of
        I(certificate_arn), I(domain_name) or I(name_tag).
    type: str
    aliases: [name]
  private_key:
    description:
      - The body of the PEM encoded private key.
      - Required when I(state=present) and the certificate does not exist.
      - Ignored when I(state=absent).
      - >
        If your private key is in a file,
        use C(lookup('file', 'path/to/key.pem')).
    type: str

  certificate_request:
    description:
      - >
        Requests an ACM certificate for use with other Amazon Web Services services.
        To request an ACM certificate, you must specify a fully qualified domain name (FQDN)
        in the I(domain_name) parameter.
        You can also specify additional FQDNs in the I(subject_alternative_names) parameter.
      - >
        If you are requesting a private certificate, domain validation is not required.
      - >
        If you are requesting a public certificate, each domain name that you specify must
        be validated to verify that you own or control the domain.
      - >
        You can use DNS validation or email validation.
        ACM issues public certificates after receiving approval from the domain owner.
      - >
        At this time, only exported private certificates can be renewed.
    version_added: 3.1.0
    suboptions:
      subject_alternative_names:
        description:
          - >
            Additional FQDNs to be included in the Subject Alternative Name extension of
            the ACM certificate.
          - >
            For example, add the name www.example.net to a certificate for which the
            I(domain_name) parameter is www.example.com if users can reach your site by
            using either name.
        type: list
        elements: str
        version_added: 3.1.0
      validation_method:
        description:
          - >
            The method you want to use if you are requesting a public certificate to validate
            that you own or control domain.
          - >
            You can validate with DNS or validate with email.
        choices: ['DNS', 'EMAIL']
        type: str
        version_added: 3.1.0
      certificate_authority_arn:
        description:
          - >
            The Amazon Resource Name (ARN) of the private certificate authority (CA) that will
            be used to issue the certificate.
          - >
            If you do not provide an ARN and you are trying to request a private certificate,
            ACM will attempt to issue a public certificate.
        type: str
        version_added: 3.1.0
      options:
        description:
          - >
            Currently, you can use this parameter to specify whether to add the certificate
            to a certificate transparency log.
          - >
            Certificate transparency makes it possible to detect SSL/TLS certificates that
            have been mistakenly or maliciously issued. Certificates that have not been logged
            typically produce an error message in a browser.
        version_added: 3.1.0
        suboptions:
          certificate_transparency_logging_preference:
            description:
              - >
                You can opt out of certificate transparency logging by specifying the DISABLED
                option. Opt in by specifying ENABLED.
            choices: ['ENABLED', 'DISABLED']
            type: str
            default: 'ENABLED'
            version_added: 3.1.0
        type: dict
    type: dict

  state:
    description:
      - >
        If I(state=present), the specified public certificate and private key
        will be uploaded, with I(Name) tag equal to I(name_tag).
      - >
        If I(state=absent), any certificates in this region
        with a corresponding I(domain_name), I(name_tag) or I(certificate_arn)
        will be deleted.
    choices: [present, absent]
    default: present
    type: str

  tags:
    description:
      - Tags to apply to certificates imported in ACM.
      - >
        If both I(name_tag) and the 'Name' tag in I(tags) are set,
        the values must be the same.
      - >
        If the 'Name' tag in I(tags) is not set and I(name_tag) is set,
        the I(name_tag) value is copied to I(tags).
    type: dict
    version_added: 3.1.0

  purge_tags:
    description:
      - whether to remove tags not present in the C(tags) parameter.
    default: false
    type: bool
    version_added: 3.1.0

  wait:
    description:
      - >
        Whether or not to wait for the certificate operation to complete.
      - >
        When a certificate request is submitted, the certificate is created,
        then the validation records. It may take some time for the validation
        records to be generated.
    type: bool
    default: 'no'
    version_added: 3.1.0

  wait_timeout:
    description:
      - how long before wait gives up, in seconds.
    default: 15
    type: int
    version_added: 3.1.0

author:
  - Matthew Davis (@matt-telstra) on behalf of Telstra Corporation Limited
extends_documentation_fragment:
  - amazon.aws.aws
  - amazon.aws.ec2

'''

EXAMPLES = '''

- name: upload a self-signed certificate
  community.aws.aws_acm:
    certificate: "{{ lookup('file', 'cert.pem' ) }}"
    privateKey: "{{ lookup('file', 'key.pem' ) }}"
    name_tag: my_cert # to be applied through an AWS tag as  "Name":"my_cert"
    region: ap-southeast-2 # AWS region

- name: create/update a certificate with a chain
  community.aws.aws_acm:
    certificate: "{{ lookup('file', 'cert.pem' ) }}"
    privateKey: "{{ lookup('file', 'key.pem' ) }}"
    name_tag: my_cert
    certificate_chain: "{{ lookup('file', 'chain.pem' ) }}"
    state: present
    region: ap-southeast-2
  register: cert_create

- name: print ARN of cert we just created
  ansible.builtin.debug:
    var: cert_create.certificate.arn

- name: delete the cert we just created
  community.aws.aws_acm:
    name_tag: my_cert
    state: absent
    region: ap-southeast-2

- name: delete a certificate with a particular ARN
  community.aws.aws_acm:
    certificate_arn: "arn:aws:acm:ap-southeast-2:123456789012:certificate/01234567-abcd-abcd-abcd-012345678901"
    state: absent
    region: ap-southeast-2

- name: delete all certificates with a particular domain name
  community.aws.aws_acm:
    domain_name: acm.ansible.com
    state: absent
    region: ap-southeast-2

- name: add tags to an existing certificate with a particular ARN
  community.aws.aws_acm:
    certificate_arn: "arn:aws:acm:ap-southeast-2:123456789012:certificate/01234567-abcd-abcd-abcd-012345678901"
    tags:
      Name: my_certificate
      Application: search
      Environment: development
    purge_tags: true

- name: request a certificate issued by ACM
  community.aws.aws_acm:
    certificate_request:
      domain_name: acm.ansible.com
      subject_alternative_names:
      - acm-east.ansible.com
      - acm-west.ansible.com
      validation_method: DNS
      options:
        certificate_transparency_logging_preference: ENABLED
    tags:
      Name: my_cert
      Application: search
      Environment: development
'''

RETURN = '''
certificate:
  description: Information about the certificate which was uploaded
  type: complex
  returned: when I(state=present)
  contains:
    arn:
      description: The ARN of the certificate in ACM
      type: str
      returned: when I(state=present) and not in check mode
      sample: "arn:aws:acm:ap-southeast-2:123456789012:certificate/01234567-abcd-abcd-abcd-012345678901"
    domain_name:
      description: The domain name encoded within the public certificate
      type: str
      returned: when I(state=present)
      sample: acm.ansible.com
arns:
  description: A list of the ARNs of the certificates in ACM which were deleted
  type: list
  elements: str
  returned: when I(state=absent)
  sample:
   - "arn:aws:acm:ap-southeast-2:123456789012:certificate/01234567-abcd-abcd-abcd-012345678901"
'''


import base64
from copy import deepcopy
import datetime
import random
import string
import re  # regex library
import time

try:
    import botocore
except ImportError:
    pass  # handled by AnsibleAWSModule

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.acm import ACMServiceManager
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import compare_aws_tags
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import (
    boto3_tag_list_to_ansible_dict,
    ansible_dict_to_boto3_tag_list,
)
from ansible.module_utils._text import to_text
from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict
from ansible.module_utils.six.moves import xrange


def ensure_tags(client, module, resource_arn, existing_tags, tags, purge_tags):
    if tags is None:
        return (False, existing_tags)

    tags_to_add, tags_to_remove = compare_aws_tags(existing_tags, tags, purge_tags)
    changed = bool(tags_to_add or tags_to_remove)
    if tags_to_add:
        if module.check_mode:
            module.exit_json(
                changed=True, msg="Would have added tags to domain if not in check mode"
            )
        try:
            client.add_tags_to_certificate(
                CertificateArn=resource_arn,
                Tags=ansible_dict_to_boto3_tag_list(tags_to_add),
            )
        except (
            botocore.exceptions.ClientError,
            botocore.exceptions.BotoCoreError,
        ) as e:
            module.fail_json_aws(
                e, "Couldn't add tags to certificate {0}".format(resource_arn)
            )
    if tags_to_remove:
        if module.check_mode:
            module.exit_json(
                changed=True, msg="Would have removed tags if not in check mode"
            )
        try:
            # remove_tags_from_certificate wants a list of key, value pairs, not a list of keys.
            tags_list = [{'Key': key, 'Value': existing_tags.get(key)} for key in tags_to_remove]
            client.remove_tags_from_certificate(
                CertificateArn=resource_arn,
                Tags=tags_list,
            )
        except (
            botocore.exceptions.ClientError,
            botocore.exceptions.BotoCoreError,
        ) as e:
            module.fail_json_aws(
                e, "Couldn't remove tags from certificate {0}".format(resource_arn)
            )
    new_tags = deepcopy(existing_tags)
    for key, value in tags_to_add.items():
        new_tags[key] = value
    for key in tags_to_remove:
        new_tags.pop(key, None)
    return (changed, new_tags)


# Takes in two text arguments
# Each a PEM encoded certificate
# Or a chain of PEM encoded certificates
# May include some lines between each chain in the cert, e.g. "Subject: ..."
# Returns True iff the chains/certs are functionally identical (including chain order)
def chain_compare(module, a, b):

    chain_a_pem = pem_chain_split(module, a)
    chain_b_pem = pem_chain_split(module, b)

    if len(chain_a_pem) != len(chain_b_pem):
        return False

    # Chain length is the same
    for (ca, cb) in zip(chain_a_pem, chain_b_pem):
        der_a = PEM_body_to_DER(module, ca)
        der_b = PEM_body_to_DER(module, cb)
        if der_a != der_b:
            return False

    return True


# Takes in PEM encoded data with no headers
# returns equivilent DER as byte array
def PEM_body_to_DER(module, pem):
    try:
        der = base64.b64decode(to_text(pem))
    except (ValueError, TypeError) as e:
        module.fail_json_aws(e, msg="Unable to decode certificate chain")
    return der


# Store this globally to avoid repeated recompilation
pem_chain_split_regex = re.compile(r"------?BEGIN [A-Z0-9. ]*CERTIFICATE------?([a-zA-Z0-9\+\/=\s]+)------?END [A-Z0-9. ]*CERTIFICATE------?")


# Use regex to split up a chain or single cert into an array of base64 encoded data
# Using "-----BEGIN CERTIFICATE-----" and "----END CERTIFICATE----"
# Noting that some chains have non-pem data in between each cert
# This function returns only what's between the headers, excluding the headers
def pem_chain_split(module, pem):

    pem_arr = re.findall(pem_chain_split_regex, to_text(pem))

    if len(pem_arr) == 0:
        # This happens if the regex doesn't match at all
        module.fail_json(msg="Unable to split certificate chain. Possibly zero-length chain?")

    return pem_arr


def renew_certificate(client, module, acm, certificate, desired_tags):
    """
    Renew an existing certificate in ACM.
    """
    response = None
    cert_arn = certificate['certificate_arn']
    if cert_arn is None:
        module.fail_json(msg="Internal error. Certificate ARN not found", certificate=certificate)
    # Rule to decide when to renew certificate.

    cert = acm.describe_certificate_with_backoff(client=client, certificate_arn=cert_arn)
    # 'IMPORTED'|'AMAZON_ISSUED'|'PRIVATE'
    cert_type = cert.get('Type')
    cert_status = cert.get('Status')
    eligible_for_renewal = False
    send_new_certificate_request = False
    if cert_type in ['AMAZON_ISSUED', 'PRIVATE']:
        # Let AWS API do error handling of certificate renewal based on the certificate type.
        # Look at the certificate status to decide whether to:
        # 1) Do nothing.
        # 2) Renew the certificate.
        # 3) Send a new certificate request.
        # 'PENDING_VALIDATION'|'ISSUED'|'INACTIVE'|'EXPIRED'|'VALIDATION_TIMED_OUT'|'REVOKED'|'FAILED'
        if cert_status == 'ISSUED':
            if cert.get('NotAfter') is None:
                module.fail_json(msg="Internal error. Certificate 'NotAfter' date not found", certificate=cert)
            # Do not attempt to renew the certificate indiscriminately.
            # Obtain the account 'DaysBeforeExpiry' parameter to determine if the current date
            # is close enough to the certificate expiration.
            try:
                response = client.get_account_configuration()
            except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
                module.fail_json_aws(e, "Couldn't renew certificate {0}".format(cert_arn))
            days_before_expiry = response['ExpiryEvents']['DaysBeforeExpiry']
            if datetime.now() > (cert.get('NotAfter') - datetime.timedelta(days_before_expiry)):
                eligible_for_renewal = True
        elif cert_status == 'PENDING_VALIDATION':
            # Do nothing. The certificate cannot be renewed since it hasn't been validated yet.
            return (False, cert_arn, response)
        else:
            # All other cases (inactive, expired, timeout...), send a new certificate request.
            send_new_certificate_request = True
    elif cert_type == 'IMPORTED':
        module.fail_json(msg="Cannot renew imported certificate", certificate=cert)
    else:
        module.fail_json(msg="Unsupported certificate type", certificate=cert)

    if eligible_for_renewal:
        if module.check_mode:
            module.exit_json(changed=True, msg="Would have renewed certificate if not in check mode")
        try:
            response = client.renew_certificate(CertificateArn=cert_arn)
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, "Couldn't renew certificate {0}".format(cert_arn))
        return (True, cert_arn, response)
    elif send_new_certificate_request:
        return request_certificate(client, module, desired_tags)


def wait_for_validation_records(client, module, acm, cert_arn):
    """
    Wait until the validation records of a certificate request are present.
    When requesting a public certificate, it may take several seconds for the DNS|EMAIL validation records
    to be generated.
    """
    if not module.params.get('wait'):
        return
    timeout = module.params["wait_timeout"]
    deadline = time.time() + timeout
    while time.time() < deadline:
        cert_data = acm.describe_certificate_with_backoff(client=client, certificate_arn=cert_arn)
        cert_data = camel_dict_to_snake_dict(cert_data)
        has_validation_records = True
        if 'domain_validation_options' not in cert_data or len(cert_data['domain_validation_options']) == 0:
            has_validation_records = False
        else:
            for dvo in cert_data['domain_validation_options']:
                if dvo['validation_status'] == 'PENDING_VALIDATION' and 'resource_record' not in dvo:
                    has_validation_records = False
                    break
        if has_validation_records:
            return
        time.sleep(5)
    # Timeout occured
    module.fail_json(msg="Timeout waiting for validation records")


def request_certificate(client, module, acm, desired_tags):
    """
    Request a new certificate from ACM.
    """
    absent_args = ['name_tag', 'domain_name']
    if sum([(module.params[a] is not None) for a in absent_args]) < 2:
        module.fail_json(msg="When requesting a certificate, all of 'name_tag' and 'domain_name' must be specified")
    cert_request = module.params.get('certificate_request')
    ca_arn = cert_request.get('certificate_authority_arn')
    domain_name = module.params.get('domain_name')
    validation_method = cert_request.get('validation_method')
    if ca_arn is None:
        # Public certificate. Domain ownership validation is required.
        if validation_method is None:
            module.fail_json(msg="The 'validation_method' parameter must be specified when requesting a public certificate from ACM")
    else:
        # Private certificate. No domain ownership validation is required.
        # Ignore the 'validation_method'.
        validation_method = None

    cert_options = cert_request.get('options')
    options = {
        'CertificateTransparencyLoggingPreference': 'ENABLED',
    }
    if cert_options is not None and cert_options.get('certificate_transparency_logging_preference') is not None:
        options['CertificateTransparencyLoggingPreference'] = cert_options.get('certificate_transparency_logging_preference')

    response = None
    changed = True
    if module.check_mode:
        module.exit_json(
            changed=changed, msg="Would have requested certificate if not in check mode"
        )
    idempotency_token = "".join([random.choice(string.ascii_letters) for i in xrange(16)])
    # The input 'desired_tags' argument is a dictionary, but ACM request_certificate wants
    # a list of {Key, Value} pairs.
    tags_list = [{'Key': key, 'Value': desired_tags.get(key)} for key in desired_tags]
    parameters = {
        'DomainName': domain_name,
        'IdempotencyToken': idempotency_token,
        'Tags': tags_list,
    }
    if cert_request.get('validation_method') is not None:
        parameters['ValidationMethod'] = cert_request.get('validation_method')
    if cert_request.get('subject_alternative_names') is not None:
        parameters['SubjectAlternativeNames'] = cert_request.get('subject_alternative_names')
    if options is not None:
        parameters['Options'] = options
    if ca_arn is not None:
        parameters['CertificateAuthorityArn'] = ca_arn
    try:
        response = client.request_certificate(**parameters)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, "Couldn't request certificate for {0}".format(domain_name))
    cert_arn = response.get('CertificateArn')
    if ca_arn is None and module.params.get('wait'):
        # Public certificate. Wait for the validation records to be present.
        wait_for_validation_records(client, module, acm, cert_arn)
    return (changed, cert_arn, response)


def update_imported_certificate(client, module, acm, old_cert, desired_tags):
    """
    Update the existing certificate that was previously imported in ACM.
    """
    module.debug("Existing certificate found in ACM")
    if ('tags' not in old_cert) or ('Name' not in old_cert['tags']):
        # shouldn't happen
        module.fail_json(msg="Internal error, unsure which certificate to update", certificate=old_cert)
    if module.params.get('name_tag') is not None and (old_cert['tags']['Name'] != module.params.get('name_tag')):
        # This could happen if the user identified the certificate using 'certificate_arn' or 'domain_name',
        # and the 'Name' tag in the AWS API does not match the ansible 'name_tag'.
        module.fail_json(msg="Internal error, Name tag does not match", certificate=old_cert)
    if 'certificate' not in old_cert:
        # shouldn't happen
        module.fail_json(msg="Internal error, unsure what the existing cert in ACM is", certificate=old_cert)

    cert_arn = None
    # Are the existing certificate in ACM and the local certificate the same?
    same = True
    if module.params.get('certificate') is not None:
        same &= chain_compare(module, old_cert['certificate'], module.params['certificate'])
        if module.params['certificate_chain']:
            # Need to test this
            # not sure if Amazon appends the cert itself to the chain when self-signed
            same &= chain_compare(module, old_cert['certificate_chain'], module.params['certificate_chain'])
        else:
            # When there is no chain with a cert
            # it seems Amazon returns the cert itself as the chain
            same &= chain_compare(module, old_cert['certificate_chain'], module.params['certificate'])

    if same:
        module.debug("Existing certificate in ACM is the same")
        cert_arn = old_cert['certificate_arn']
        changed = False
    else:
        absent_args = ['certificate', 'name_tag', 'private_key']
        if sum([(module.params[a] is not None) for a in absent_args]) < 3:
            module.fail_json(msg="When importing a certificate, all of 'name_tag', 'certificate' and 'private_key' must be specified")
        module.debug("Existing certificate in ACM is different, overwriting")
        changed = True
        if module.check_mode:
            cert_arn = old_cert['certificate_arn']
            # note: returned domain will be the domain of the previous cert
        else:
            # update cert in ACM
            cert_arn = acm.import_certificate(
                client,
                module,
                certificate=module.params['certificate'],
                private_key=module.params['private_key'],
                certificate_chain=module.params['certificate_chain'],
                arn=old_cert['certificate_arn'],
                tags=desired_tags,
            )
    return (changed, cert_arn, cert_arn)


def import_certificate(client, module, acm, desired_tags):
    """
    Import a certificate to ACM.
    """
    # Validate argument requirements
    absent_args = ['certificate', 'name_tag', 'private_key']
    cert_arn = None
    if sum([(module.params[a] is not None) for a in absent_args]) < 3:
        module.fail_json(msg="When importing a new certificate, all of 'name_tag', 'certificate' and 'private_key' must be specified")
    module.debug("No certificate in ACM. Creating new one.")
    changed = True
    if module.check_mode:
        domain = 'example.com'
        module.exit_json(certificate=dict(domain_name=domain), changed=True)
    else:
        cert_arn = acm.import_certificate(
            client,
            module,
            certificate=module.params['certificate'],
            private_key=module.params['private_key'],
            certificate_chain=module.params['certificate_chain'],
            tags=desired_tags,
        )
    return (changed, cert_arn, cert_arn)


def ensure_certificates_present(client, module, acm, certificates, desired_tags, filter_tags):
    cert_arn = None
    changed = False
    response = None
    if len(certificates) > 1:
        msg = "More than one certificate with Name=%s exists in ACM in this region" % module.params['name_tag']
        module.fail_json(msg=msg, certificates=certificates)
    elif len(certificates) == 1:
        if module.params.get('certificate_request') is not None:
            # Renew existing certificate requested from ACM
            (changed, cert_arn, response) = renew_certificate(client, module, acm, certificates[0], desired_tags)
        else:
            # Update existing certificate that was previously imported to ACM.
            (changed, cert_arn, response) = update_imported_certificate(client, module, acm, certificates[0], desired_tags)
    else:  # len(certificates) == 0
        if module.params.get('certificate_request') is not None:
            # Request certificate from ACM.
            (changed, cert_arn, response) = request_certificate(client, module, acm, desired_tags)
        else:
            # Import new certificate to ACM.
            (changed, cert_arn, response) = import_certificate(client, module, acm, desired_tags)

    if cert_arn is None:
        module.fail_json(msg="Internal error. Could not identify certificate ARN")

    # Add/remove tags to/from certificate
    try:
        existing_tags = boto3_tag_list_to_ansible_dict(client.list_tags_for_certificate(CertificateArn=cert_arn)['Tags'])
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, "Couldn't get tags for certificate")

    purge_tags = module.params.get('purge_tags')
    (c, new_tags) = ensure_tags(client, module, cert_arn, existing_tags, desired_tags, purge_tags)
    changed |= c

    cert_data = acm.describe_certificate_with_backoff(client=client, certificate_arn=cert_arn)
    cert_data = camel_dict_to_snake_dict(cert_data)
    # The dict already contains a 'certificate_arn' attribute which is the same value as 'arn'.
    # This 'aws_acm' module was originally written to return the 'arn' attribute.
    cert_data['arn'] = cert_arn
    cert_data['tags'] = new_tags
    if 'domain_name' not in cert_data:
        # The 'DomainName' attribute may not be present when describing a certificate issued by AWS.
        cert_data['domain_name'] = module.params.get("domain_name")

    module.exit_json(certificate=cert_data, changed=changed)


def ensure_certificates_absent(client, module, acm, certificates):
    for cert in certificates:
        if not module.check_mode:
            acm.delete_certificate(client, module, cert['certificate_arn'])
    module.exit_json(arns=[cert['certificate_arn'] for cert in certificates], changed=(len(certificates) > 0))


def main():
    argument_spec = dict(
        certificate=dict(),
        certificate_arn=dict(aliases=['arn']),
        certificate_chain=dict(),
        domain_name=dict(aliases=['domain']),
        name_tag=dict(aliases=['name']),
        private_key=dict(no_log=True),
        certificate_request=dict(
            type="dict",
            default=None,
            options=dict(
                subject_alternative_names=dict(type="list", elements="str"),
                validation_method=dict(default=None, choices=['DNS', 'EMAIL']),
                options=dict(
                    type="dict",
                    default=None,
                    options=dict(
                        certificate_transparency_logging_preference=dict(choices=['ENABLED', 'DISABLED'], default='ENABLED'),
                    )
                ),
                certificate_authority_arn=dict(),
            ),
        ),
        tags=dict(type='dict'),
        purge_tags=dict(type='bool', default=False),
        wait=dict(type="bool", default=False),
        wait_timeout=dict(type="int", default=15),
        state=dict(default='present', choices=['present', 'absent']),
    )
    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[
            ['certificate_request', 'private_key'],
            ['certificate_request', 'certificate_chain'],
        ],
    )
    acm = ACMServiceManager(module)

    # Check argument requirements
    if module.params['state'] == 'present':
        # at least one of these should be specified.
        absent_args = ['certificate_arn', 'domain_name', 'name_tag']
        if sum([(module.params[a] is not None) for a in absent_args]) < 1:
            for a in absent_args:
                module.debug("%s is %s" % (a, module.params[a]))
            module.fail_json(msg="If 'state' is specified as 'present' then at least one of 'name_tag', 'certificate_arn' or 'domain_name' must be specified")
    else:  # absent
        # exactly one of these should be specified
        absent_args = ['certificate_arn', 'domain_name', 'name_tag']
        if sum([(module.params[a] is not None) for a in absent_args]) != 1:
            for a in absent_args:
                module.debug("%s is %s" % (a, module.params[a]))
            module.fail_json(msg="If 'state' is specified as 'absent' then exactly one of 'name_tag', 'certificate_arn' or 'domain_name' must be specified")

    filter_tags = None
    desired_tags = None
    if module.params.get('tags') is not None:
        desired_tags = module.params['tags']
    if module.params.get('name_tag') is not None:
        # The module was originally implemented to filter certificates based on the 'Name' tag.
        # Other tags are not used to filter certificates.
        # It would make sense to replace the existing name_tag, domain, certificate_arn attributes
        # with a 'filter' attribute, but that would break backwards-compatibility.
        filter_tags = dict(Name=module.params['name_tag'])
        if desired_tags is not None:
            if 'Name' in desired_tags:
                if desired_tags['Name'] != module.params['name_tag']:
                    module.fail_json(msg="Value of 'name_tag' conflicts with value of 'tags.Name'")
            else:
                desired_tags['Name'] = module.params['name_tag']
        else:
            desired_tags = deepcopy(filter_tags)

    client = module.client('acm')

    # fetch the list of certificates currently in ACM
    certificates = acm.get_certificates(
        client=client,
        module=module,
        domain_name=module.params['domain_name'],
        arn=module.params['certificate_arn'],
        only_tags=filter_tags,
    )

    module.debug("Found %d corresponding certificates in ACM" % len(certificates))
    if module.params['state'] == 'present':
        ensure_certificates_present(client, module, acm, certificates, desired_tags, filter_tags)
    else:  # state == absent
        ensure_certificates_absent(client, module, acm, certificates)


if __name__ == '__main__':
    # tests()
    main()
