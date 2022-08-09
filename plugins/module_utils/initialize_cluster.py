# -*- coding: utf-8 -*-
# Copyright: (c) 2022, TachTech  LLC <info@tachtech.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""AWS HSM Cluster Initialization Module Plugin Utilities."""


from __future__ import absolute_import, division, print_function

import os

from ansible.errors import AnsibleActionFail
from OpenSSL import crypto
from OpenSSL.crypto import Error

__metaclass__ = type


from ansible_collections.community.aws.plugins.module_utils.aws_hsm import (
    AwsHsm,
    Validator,
)


class HsmClusterInitValidator(Validator):
    """HsmClusterInitValidator module args validation."""

    def signed_cert(self):
        """Validates if necessary signed_cert info is provided."""
        try:
            signed_cert = self.module_args["signed_cert"]
            if not isinstance(signed_cert, str):
                raise TypeError
            if os.path.isfile(signed_cert):
                cert = crypto.load_certificate(
                    crypto.FILETYPE_PEM, open(signed_cert).read()
                )
            else:
                cert = crypto.load_certificate(crypto.FILETYPE_PEM, signed_cert)
            if not cert.get_subject().CN or "HSM" not in cert.get_subject().CN:
                raise ValueError
        except TypeError as type_error:
            raise AnsibleActionFail(
                f"Wrong type was provided for the 'signed_cert' argument. Must be a string. Provided: {type(signed_cert).__name__}"
            ) from type_error
        except KeyError as key_error:
            raise AnsibleActionFail(
                "'signed_cert' is a mandatory argument."
            ) from key_error
        except Error as error:
            raise AnsibleActionFail(
                "Provided signed certificate is not valid."
            ) from error
        except ValueError as value_error:
            raise AnsibleActionFail(
                "Provided certificate is valid, but the CommonName (CN) does not contain 'HSM' in it. Make sure to use the certificate which was signed using the HSM Cluster generated CSR."
            ) from value_error

    def trust_anchor(self):
        """Validates if necessary trust_anchor info is provided."""
        try:
            trust_anchor = self.module_args["trust_anchor"]
            if not isinstance(trust_anchor, str):
                raise TypeError
            if os.path.isfile(trust_anchor):
                crypto.load_certificate(crypto.FILETYPE_PEM, open(trust_anchor).read())
            else:
                crypto.load_certificate(crypto.FILETYPE_PEM, trust_anchor)
        except TypeError as type_error:
            raise AnsibleActionFail(
                f"Wrong type was provided for the 'trust_anchor' argument. Must be a string. Provided: {type(trust_anchor).__name__}"
            ) from type_error
        except KeyError as key_error:
            raise AnsibleActionFail(
                "'trust_anchor' is a mandatory argument."
            ) from key_error
        except Error as error:
            raise AnsibleActionFail(
                "Provided trust anchor (CA) certificate is not valid."
            ) from error

    def validate(self):
        """Validate all."""
        self.auth()
        self.region()
        self.cluster_id(mandatory=True)
        self.signed_cert()
        self.trust_anchor()


class HsmClusterInit(AwsHsm):
    """Class to initialize the HSM Cluster"""

    def __init__(self, module_args, play_vars) -> None:
        super().__init__()
        self.play_vars = play_vars
        self.module_args = module_args
        HsmClusterInitValidator(self.module_args, self.play_vars).validate()

    def init(self):
        """Initializes the HSM Cluster.

        Returns:
            dict:
        """
        init_body = {"ClusterId": self.module_args["cluster_id"]}
        signed_cert = self.module_args["signed_cert"]
        trust_anchor = self.module_args["trust_anchor"]
        if os.path.isfile(signed_cert):
            with open(signed_cert) as _file:
                init_body["SignedCert"] = _file.read()
        else:
            init_body["SignedCert"] = signed_cert
        if os.path.isfile(trust_anchor):
            with open(trust_anchor) as _file:
                init_body["TrustAnchor"] = _file.read()
        else:
            init_body["TrustAnchor"] = trust_anchor
        try:
            response = self.client.initialize_cluster(**init_body)
            response.pop("ResponseMetadata")
            return {"changed": True, "data": response}
        except Exception as catch_all:
            raise AnsibleActionFail(
                f"Something went wrong while initializing the cluster. Reason: {catch_all}"
            ) from catch_all
