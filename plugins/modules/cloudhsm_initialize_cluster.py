#!/usr/bin/python
# Copyright: (c) 2022, TachTech <info@tachtech.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: cloudhsm_initialize_cluster
short_description: Initialize HSM Cluster.
author:
    - Armen Martirosyan (@armartirosyan)
requirements:
    - boto3
description:
    - Using signed certificate and singing CA's public key, initialize the AWS Cluster
options:
    cluster_id:
        description:
            - The HSM cluster's identifier.
        type: str
        required: false
    signed_cert:
        description:
            - Signed x509 certificate.
        type: str
        required: true
    trust_anchor:
        description:
            - Singing CA's public x509 certificate.
        type: str
        required: true
    name:
        description:
            - The name of the cluster
        type: str
        required: false
extends_documentation_fragment:
  - amazon.aws.aws
  - amazon.aws.cloudhsm
"""


EXAMPLES = """
# Note: These examples do not set authentication details, see the AWS Guide for details

- name: "Initialize HSM Cluster"
  community.aws.cloudhsm_initialize_cluster:
    cluster_id: cluster_a3231231
    signed_cert: |
    -----BEGIN CERTIFICATE-----
    MIIDUDCCAjgCCQCZHZUWolGMLjANBgkqhkiG9w0BAQsFADBJMQswCQYDVQQGEwJV
    UzELMAkGA1UECAwCTlYxEjAQBgNVBAcMCUxhcyBWZWdhczEMMAoGA1UECgwDSVRV
    MQswCQYDVQQLDAJJVDAeFw0yMjA3MjkwODQ1MjhaFw0zMjA3MjgwODQ1MjhaMIGK
    MUQwCQYDVQQGEwJVUzAJBgNVBAgMAkNBMA0GA1UECgwGQ2F2aXVtMA0GA1UECwwG
    TjNGSVBTMA4GA1UEBwwHU2FuSm9zZTFCMEAGA1UEAww5SFNNOkZCRTBGNTE4MEEz
    MDYyN0VEQkVGOUUwRTBEQTE3NDpQQVJUTjo0LCBmb3IgRklQUyBtb2RlMIIBIjAN
    BgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArHDakGPyf54vEXbnADKxkUxZpfHF
    4RLjXfp7zBPNzAi1DePSUckxdKyaqK9VsJ16COky6/XpCinTCsKET5j011FK9oE4
    2ArhEs1/mb6EL3KQvdd7BSeYnBS0L1JHhIXK/rEpjeD52xvyCz3eOh39/asRi+YQ
    Cl2CBXaLdmQROVLilMmYh+OmnWFCnhT7S14h4HENsqYgbbUZLiyt+3v/2rVDUbFw
    LjqP5ZHJemsamyHwzuXUJiOEN6KJ2l5dXEtprr/zHfteWL1yM5Ne0vE72XiXoMqS
    qAZYsttV7yZ/lRJQzCvPynrQPd+4k8x3LC1R3zVbPsqdLcjuzpOh67M3+QIDAQAB
    MA0GCSqGSIb3DQEBCwUAA4IBAQBcQUfYITGtqc8PoYw+mNfwRBxPG7LjzgY9gwu0
    P5O6OtdSns1PpaTrF2dSqPljxcJF3Xoh1hQUy7y4LKafUweip1QujlAr0Z8AToAq
    xyFP2CcjuTiaE59nfLwcXE5ynK9T8FjqWPQU3+L8rYu4f+oBHiesKRNCwjB1aW0t
    2Ja7Ojb/nk3dsaG8KiSBfhnsC0XqOZF9cZOZ4ZUSU8Hqr7r5J9OUVlbRqbSSeVgy
    y+FjoxuQ6fxXJ+jBo1Ld0+E1UCKANpLg+18oUkMtm4pewn1xyIp2jLamJSDdLWO0
    Rcj7jVxeSK23f67oQs5z8md3mcjw61zSAof+DMbRuvzCQTbm
    -----END CERTIFICATE-----
    trust_anchor: |
    -----BEGIN CERTIFICATE-----
    MIIDZTCCAk2gAwIBAgIJALZ5lWBXvUBxMA0GCSqGSIb3DQEBCwUAMEkxCzAJBgNV
    BAYTAlVTMQswCQYDVQQIDAJOVjESMBAGA1UEBwwJTGFzIFZlZ2FzMQwwCgYDVQQK
    DANJVFUxCzAJBgNVBAsMAklUMB4XDTIyMDcyOTAzMTUzMFoXDTMyMDcyODAzMTUz
    MFowSTELMAkGA1UEBhMCVVMxCzAJBgNVBAgMAk5WMRIwEAYDVQQHDAlMYXMgVmVn
    YXMxDDAKBgNVBAoMA0lUVTELMAkGA1UECwwCSVQwggEiMA0GCSqGSIb3DQEBAQUA
    A4IBDwAwggEKAoIBAQC8b6kHTUuwreduFDJ8Og2gD3q/8cz+nj0q54XEi6BNBU3i
    A0ykeH6PF0igGGlVGKZYOvBzCdz0lT5andRtDQ5ysQ9gTrQYsoSnCLXLa7MU+IvV
    o4YLskNsflg/FGcURdKS+QzcCXWf5MIPv3rnPzPkFf6VFmk3uIGr3PVRUCs9tNZa
    fT5aejGUbnvHLq5YQo0mALCrObTCYTQ1GiohvkE+yEyKSzSVjlMY8lCbCHiHxsef
    LhwDQBlvZDP0h3FqYA8xXs/Av+G4cx25jf7GaB40gKq44mxs/JZQCTuCAlrq6wYJ
    78dZZXHrZF8JWPaDEQ/KVglJ5qy6sbpYgp8p9t0PAgMBAAGjUDBOMB0GA1UdDgQW
    BBQ7Fj4T61iO41BJ2HiMMCgq8+VeGDAfBgNVHSMEGDAWgBQ7Fj4T61iO41BJ2HiM
    MCgq8+VeGDAMBgNVHRMEBTADAQH/MA0GCSqGSIb3DQEBCwUAA4IBAQCZExIIsM9i
    M5DES1o/wfLPVuTKlMjirLPrLnoCoytT9G6ou/yvS5UnjPlHjczN5Bxb3/yU/n6p
    +1AwQTfhkocqB1TCv4PqDttVy/P7k1ZS3dFnMU95gTYStJKjbSEp4tymWSBJY1qS
    3MZyC0dVRsfeCqpnTmafTx8Q0Gjl0FWukIOH/ZH7T0HeZvZxjinlwtblHUYA/VCy
    Rw//vKcv5YvPNOpDUrdaUongI9fZyuFV14c+ZOdCHfqGjVJh5I9euYmK9JxHp/OF
    8xRAtuoXinJa9t2FmDrsQSadL4theqOINNC42vmedsTgkYKcOfl9qLk6mV2JSjWc
    1pGHxwLvryHc
    -----END CERTIFICATE-----


- name: "Initialize HSM Cluster"
  community.aws.cloudhsm_initialize_cluster
    cluster_id: cluster_a3231231
    signed_cert: ./signed_cert.crt
    trust_anchor: ./signing_ca.crt

- name: "Initialize HSM Cluster using HSM name"
  community.aws.cloudhsm_initialize_cluster
    name: West2a_Cluster
    signed_cert: ./signed_cert.crt
    trust_anchor: ./signing_ca.crt
"""

RETURN = """
changed:
  description: Boolean that is true if the command changed the state.
  returned: always
  type: bool
  sample: True
"""

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.community.aws.plugins.module_utils.cloudhsm import (
    CloudHsmCluster,
)


def main():
    """Main function for the module."""

    argument_spec = dict(
        cluster_id=dict(required=False, type="str"),
        signed_cert=dict(required=True, type="str"),
        trust_anchor=dict(required=True, type="str"),
        name=dict(required=False, type="str"),
    )
    required_one_of = [("cluster_id", "name")]

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=required_one_of,
    )
    cluster_mgr = CloudHsmCluster(module)
    results = dict(changed=False)

    existing = cluster_mgr.describe_cluster()
    if existing:
        if (
            existing[0]["State"] == "UNINITIALIZED"
            and existing[0]["Certificates"]
            and not cluster_mgr.module.check_mode
        ):
            results["changed"] = cluster_mgr.initialize(existing[0]["ClusterId"])
        elif existing[0]["State"] != "UNINITIALIZED":
            cluster_mgr.module.fail_json(
                msg=f"Unable to initialize the CloudHSM Cluster '{existing[0]['ClusterId']}'. The selected cluster must be in 'UNINITIALIZED' state. Reported state is '{existing[0]['State']}'"
            )
        elif not existing[0]["Certificates"]:
            cluster_mgr.module.fail_json(
                msg=f"Unable to initialize the CloudHSM Cluster '{existing[0]['ClusterId']}'. The selected cluster does not have any HSM devices."
            )
    else:
        if cluster_mgr.module.check_mode:
            results["changed"] = True

    cluster_mgr.module.exit_json(**results)


if __name__ == "__main__":
    main()
