"""Test file for initialize_cluster.py method"""

from __future__ import absolute_import, division, print_function

import pytest
from ansible.errors import AnsibleActionFail

__metaclass__ = type

import json
import sys

sys.path.append("./plugins/module_utils")

from constants import *
from initialize_cluster import HsmClusterInit, HsmClusterInitValidator


@pytest.mark.parametrize(
    "module_args, play_vars",
    [
        (
            {
                "signed_cert": "-----BEGIN CERTIFICATE-----\nMIIDUDCCAjgCCQCZHZUWolGMLjANBgkqhkiG9w0BAQsFADBJMQswCQYDVQQGEwJV\nUzELMAkGA1UECAwCTlYxEjAQBgNVBAcMCUxhcyBWZWdhczEMMAoGA1UECgwDSVRV\nMQswCQYDVQQLDAJJVDAeFw0yMjA3MjkwODQ1MjhaFw0zMjA3MjgwODQ1MjhaMIGK\nMUQwCQYDVQQGEwJVUzAJBgNVBAgMAkNBMA0GA1UECgwGQ2F2aXVtMA0GA1UECwwG\nTjNGSVBTMA4GA1UEBwwHU2FuSm9zZTFCMEAGA1UEAww5SFNNOkZCRTBGNTE4MEEz\nMDYyN0VEQkVGOUUwRTBEQTE3NDpQQVJUTjo0LCBmb3IgRklQUyBtb2RlMIIBIjAN\nBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArHDakGPyf54vEXbnADKxkUxZpfHF\n4RLjXfp7zBPNzAi1DePSUckxdKyaqK9VsJ16COky6/XpCinTCsKET5j011FK9oE4\n2ArhEs1/mb6EL3KQvdd7BSeYnBS0L1JHhIXK/rEpjeD52xvyCz3eOh39/asRi+YQ\nCl2CBXaLdmQROVLilMmYh+OmnWFCnhT7S14h4HENsqYgbbUZLiyt+3v/2rVDUbFw\nLjqP5ZHJemsamyHwzuXUJiOEN6KJ2l5dXEtprr/zHfteWL1yM5Ne0vE72XiXoMqS\nqAZYsttV7yZ/lRJQzCvPynrQPd+4k8x3LC1R3zVbPsqdLcjuzpOh67M3+QIDAQAB\nMA0GCSqGSIb3DQEBCwUAA4IBAQBcQUfYITGtqc8PoYw+mNfwRBxPG7LjzgY9gwu0\nP5O6OtdSns1PpaTrF2dSqPljxcJF3Xoh1hQUy7y4LKafUweip1QujlAr0Z8AToAq\nxyFP2CcjuTiaE59nfLwcXE5ynK9T8FjqWPQU3+L8rYu4f+oBHiesKRNCwjB1aW0t\n2Ja7Ojb/nk3dsaG8KiSBfhnsC0XqOZF9cZOZ4ZUSU8Hqr7r5J9OUVlbRqbSSeVgy\ny+FjoxuQ6fxXJ+jBo1Ld0+E1UCKANpLg+18oUkMtm4pewn1xyIp2jLamJSDdLWO0\nRcj7jVxeSK23f67oQs5z8md3mcjw61zSAof+DMbRuvzCQTbm\n-----END CERTIFICATE-----",
            },
            {},
        ),
        ({"signed_cert": "./tests/unit/plugins/module_utils/mocks/signed.crt"}, {}),
    ],
    ids=["Valid Signed Cert", "Valid Signed Cert File"],
)
def test_signed_cert(module_args, play_vars):
    """Testing HsmClusterInitValidator.signed_cert method
    Valid Signed Cert is provided, no exception is raised
    """
    HsmClusterInitValidator(module_args, play_vars).signed_cert()


@pytest.mark.parametrize(
    "module_args, play_vars, match",
    [
        ({}, {}, "'signed_cert'\\s+is\\s+a\\s+mandatory\\s+argument."),
        ({"signed_cert": 1}, {}, "Wrong\\s+type\\s+was\\s+provided.*Provided:\\s+int"),
        (
            {
                "signed_cert": "-----BEGIN CERTIFICATE-----\nAIIDUDCCAjgCCQCZHZUWolGMLjANBgkqhkiG9w0BAQsFADBJMQswCQYDVQQGEwJV\nUzELMAkGA1UECAwCTlYxEjAQBgNVBAcMCUxhcyBWZWdhczEMMAoGA1UECgwDSVRV\nMQswCQYDVQQLDAJJVDAeFw0yMjA3MjkwODQ1MjhaFw0zMjA3MjgwODQ1MjhaMIGK\nMUQwCQYDVQQGEwJVUzAJBgNVBAgMAkNBMA0GA1UECgwGQ2F2aXVtMA0GA1UECwwG\nTjNGSVBTMA4GA1UEBwwHU2FuSm9zZTFCMEAGA1UEAww5SFNNOkZCRTBGNTE4MEEz\nMDYyN0VEQkVGOUUwRTBEQTE3NDpQQVJUTjo0LCBmb3IgRklQUyBtb2RlMIIBIjAN\nBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArHDakGPyf54vEXbnADKxkUxZpfHF\n4RLjXfp7zBPNzAi1DePSUckxdKyaqK9VsJ16COky6/XpCinTCsKET5j011FK9oE4\n2ArhEs1/mb6EL3KQvdd7BSeYnBS0L1JHhIXK/rEpjeD52xvyCz3eOh39/asRi+YQ\nCl2CBXaLdmQROVLilMmYh+OmnWFCnhT7S14h4HENsqYgbbUZLiyt+3v/2rVDUbFw\nLjqP5ZHJemsamyHwzuXUJiOEN6KJ2l5dXEtprr/zHfteWL1yM5Ne0vE72XiXoMqS\nqAZYsttV7yZ/lRJQzCvPynrQPd+4k8x3LC1R3zVbPsqdLcjuzpOh67M3+QIDAQAB\nMA0GCSqGSIb3DQEBCwUAA4IBAQBcQUfYITGtqc8PoYw+mNfwRBxPG7LjzgY9gwu0\nP5O6OtdSns1PpaTrF2dSqPljxcJF3Xoh1hQUy7y4LKafUweip1QujlAr0Z8AToAq\nxyFP2CcjuTiaE59nfLwcXE5ynK9T8FjqWPQU3+L8rYu4f+oBHiesKRNCwjB1aW0t\n2Ja7Ojb/nk3dsaG8KiSBfhnsC0XqOZF9cZOZ4ZUSU8Hqr7r5J9OUVlbRqbSSeVgy\ny+FjoxuQ6fxXJ+jBo1Ld0+E1UCKANpLg+18oUkMtm4pewn1xyIp2jLamJSDdLWO0\nRcj7jVxeSK23f67oQs5z8md3mcjw61zSAof+DMbRuvzCQTbm\n-----END CERTIFICATE-----",
            },
            {},
            "Provided\\s+signed\\s+certificate\\s+is\\s+not\\s+valid.",
        ),
        (
            {"signed_cert": "./tests/unit/plugins/module_utils/mocks/hsms.json"},
            {},
            "Provided\\s+signed\\s+certificate\\s+is\\s+not\\s+valid.",
        ),
        (
            {"signed_cert": "./tests/unit/plugins/module_utils/mocks/signing_ca.crt"},
            {},
            "Provided\\s+certificate\\s+is\\s+valid.*CSR",
        ),
    ],
    ids=[
        "Missing Signed Cert",
        "Invalid Signed Cert Type Int",
        "Invalid Signed Cert",
        "Invalid Signed Cert File",
        "Valid Wrong Signed Cert",
    ],
)
def test_signed_cert_exception(module_args, play_vars, match):
    """Testing HsmClusterInitValidator.signed_cert method
    Invalid Signed Cert is provided, exception is raised
    """
    with pytest.raises(AnsibleActionFail, match=rf"{match}"):
        HsmClusterInitValidator(module_args, play_vars).signed_cert()


#################################################################################################


@pytest.mark.parametrize(
    "module_args, play_vars",
    [
        (
            {
                "trust_anchor": "-----BEGIN CERTIFICATE-----\nMIIDZTCCAk2gAwIBAgIJALZ5lWBXvUBxMA0GCSqGSIb3DQEBCwUAMEkxCzAJBgNV\nBAYTAlVTMQswCQYDVQQIDAJOVjESMBAGA1UEBwwJTGFzIFZlZ2FzMQwwCgYDVQQK\nDANJVFUxCzAJBgNVBAsMAklUMB4XDTIyMDcyOTAzMTUzMFoXDTMyMDcyODAzMTUz\nMFowSTELMAkGA1UEBhMCVVMxCzAJBgNVBAgMAk5WMRIwEAYDVQQHDAlMYXMgVmVn\nYXMxDDAKBgNVBAoMA0lUVTELMAkGA1UECwwCSVQwggEiMA0GCSqGSIb3DQEBAQUA\nA4IBDwAwggEKAoIBAQC8b6kHTUuwreduFDJ8Og2gD3q/8cz+nj0q54XEi6BNBU3i\nA0ykeH6PF0igGGlVGKZYOvBzCdz0lT5andRtDQ5ysQ9gTrQYsoSnCLXLa7MU+IvV\no4YLskNsflg/FGcURdKS+QzcCXWf5MIPv3rnPzPkFf6VFmk3uIGr3PVRUCs9tNZa\nfT5aejGUbnvHLq5YQo0mALCrObTCYTQ1GiohvkE+yEyKSzSVjlMY8lCbCHiHxsef\nLhwDQBlvZDP0h3FqYA8xXs/Av+G4cx25jf7GaB40gKq44mxs/JZQCTuCAlrq6wYJ\n78dZZXHrZF8JWPaDEQ/KVglJ5qy6sbpYgp8p9t0PAgMBAAGjUDBOMB0GA1UdDgQW\nBBQ7Fj4T61iO41BJ2HiMMCgq8+VeGDAfBgNVHSMEGDAWgBQ7Fj4T61iO41BJ2HiM\nMCgq8+VeGDAMBgNVHRMEBTADAQH/MA0GCSqGSIb3DQEBCwUAA4IBAQCZExIIsM9i\nM5DES1o/wfLPVuTKlMjirLPrLnoCoytT9G6ou/yvS5UnjPlHjczN5Bxb3/yU/n6p\n+1AwQTfhkocqB1TCv4PqDttVy/P7k1ZS3dFnMU95gTYStJKjbSEp4tymWSBJY1qS\n3MZyC0dVRsfeCqpnTmafTx8Q0Gjl0FWukIOH/ZH7T0HeZvZxjinlwtblHUYA/VCy\nRw//vKcv5YvPNOpDUrdaUongI9fZyuFV14c+ZOdCHfqGjVJh5I9euYmK9JxHp/OF\n8xRAtuoXinJa9t2FmDrsQSadL4theqOINNC42vmedsTgkYKcOfl9qLk6mV2JSjWc\n1pGHxwLvryHc\n-----END CERTIFICATE-----",
            },
            {},
        ),
        ({"trust_anchor": "./tests/unit/plugins/module_utils/mocks/signing_ca.crt"}, {}),
    ],
    ids=["Valid CA Cert", "Valid CA Cert File"],
)
def test_trust_anchor(module_args, play_vars):
    """Testing HsmClusterInitValidator.trust_anchor method
    Valid CA Public Cert is provided, no exception is raised
    """
    HsmClusterInitValidator(module_args, play_vars).trust_anchor()


@pytest.mark.parametrize(
    "module_args, play_vars, match",
    [
        ({}, {}, "'trust_anchor'\\s+is\\s+a\\s+mandatory\\s+argument."),
        ({"trust_anchor": 1}, {}, "Wrong\\s+type\\s+was\\s+provided.*Provided:\\s+int"),
        (
            {
                "trust_anchor": "-----BEGIN CERTIFICATE-----\nGIIDZTCCAk2gAwIBAgIJALZ5lWBXvUBxMA0GCSqGSIb3DQEBCwUAMEkxCzAJBgNV\nBAYTAlVTMQswCQYDVQQIDAJOVjESMBAGA1UEBwwJTGFzIFZlZ2FzMQwwCgYDVQQK\nDANJVFUxCzAJBgNVBAsMAklUMB4XDTIyMDcyOTAzMTUzMFoXDTMyMDcyODAzMTUz\nMFowSTELMAkGA1UEBhMCVVMxCzAJBgNVBAgMAk5WMRIwEAYDVQQHDAlMYXMgVmVn\nYXMxDDAKBgNVBAoMA0lUVTELMAkGA1UECwwCSVQwggEiMA0GCSqGSIb3DQEBAQUA\nA4IBDwAwggEKAoIBAQC8b6kHTUuwreduFDJ8Og2gD3q/8cz+nj0q54XEi6BNBU3i\nA0ykeH6PF0igGGlVGKZYOvBzCdz0lT5andRtDQ5ysQ9gTrQYsoSnCLXLa7MU+IvV\no4YLskNsflg/FGcURdKS+QzcCXWf5MIPv3rnPzPkFf6VFmk3uIGr3PVRUCs9tNZa\nfT5aejGUbnvHLq5YQo0mALCrObTCYTQ1GiohvkE+yEyKSzSVjlMY8lCbCHiHxsef\nLhwDQBlvZDP0h3FqYA8xXs/Av+G4cx25jf7GaB40gKq44mxs/JZQCTuCAlrq6wYJ\n78dZZXHrZF8JWPaDEQ/KVglJ5qy6sbpYgp8p9t0PAgMBAAGjUDBOMB0GA1UdDgQW\nBBQ7Fj4T61iO41BJ2HiMMCgq8+VeGDAfBgNVHSMEGDAWgBQ7Fj4T61iO41BJ2HiM\nMCgq8+VeGDAMBgNVHRMEBTADAQH/MA0GCSqGSIb3DQEBCwUAA4IBAQCZExIIsM9i\nM5DES1o/wfLPVuTKlMjirLPrLnoCoytT9G6ou/yvS5UnjPlHjczN5Bxb3/yU/n6p\n+1AwQTfhkocqB1TCv4PqDttVy/P7k1ZS3dFnMU95gTYStJKjbSEp4tymWSBJY1qS\n3MZyC0dVRsfeCqpnTmafTx8Q0Gjl0FWukIOH/ZH7T0HeZvZxjinlwtblHUYA/VCy\nRw//vKcv5YvPNOpDUrdaUongI9fZyuFV14c+ZOdCHfqGjVJh5I9euYmK9JxHp/OF\n8xRAtuoXinJa9t2FmDrsQSadL4theqOINNC42vmedsTgkYKcOfl9qLk6mV2JSjWc\n1pGHxwLvryHc\n-----END CERTIFICATE-----",
            },
            {},
            "Provided\\s+trust\\s+anchor\\s+\\(CA\\)\\s+certificate\\s+is\\s+not\\s+valid.",
        ),
        (
            {"trust_anchor": "./tests/unit/plugins/module_utils/mocks/hsms.json"},
            {},
            "Provided\\s+trust\\s+anchor\\s+\\(CA\\)\\s+certificate\\s+is\\s+not\\s+valid.",
        ),
    ],
    ids=[
        "Missing CA Cert",
        "Invalid CA Cert Type Int",
        "Invalid CA Cert ",
        "Invalid CA Cert File",
    ],
)
def test_trust_anchor_exception(module_args, play_vars, match):
    """Testing HsmClusterInitValidator.trust_anchor method
    Invalid CA Cert is provided, exception is raised
    """
    with pytest.raises(AnsibleActionFail, match=rf"{match}"):
        HsmClusterInitValidator(module_args, play_vars).trust_anchor()


#################################################################################################


@pytest.mark.parametrize(
    "module_args, play_vars",
    [
        (
            {
                "cluster_id": "cluster-test123",
                "signed_cert": "./tests/unit/plugins/module_utils/mocks/signed.crt",
                "trust_anchor": "./tests/unit/plugins/module_utils/mocks/signing_ca.crt",
                "aws_access_key": "TESTAWSACCESSKEY",
                "aws_secret_key": "testawssecretkey",
                "region": "us-east-2",
            },
            {},
        )
    ],
    ids=["Full validate"],
)
def test_validate(module_args, play_vars, mock_configparser_sections):
    """Testing HsmClusterInitValidator.validate method"""
    HsmClusterInitValidator(module_args, play_vars).validate()


#################################################################################################


@pytest.mark.parametrize(
    "module_args, play_vars",
    [
        (
            {
                "cluster_id": "cluster-test",
                "signed_cert": "./tests/unit/plugins/module_utils/mocks/signed.crt",
                "trust_anchor": "./tests/unit/plugins/module_utils/mocks/signing_ca.crt",
                "aws_access_key": "TESTAWSACCESSKEY",
                "aws_secret_key": "testawssecretkey",
                "region": "us-east-2",
            },
            {},
        )
    ],
    ids=["HsmClusterInit Init"],
)
def test_HsmClusterInit_init(module_args, play_vars, mock_configparser_sections):
    """Testing HsmClusterInit.__init__ method"""
    hsm_cluster_init = HsmClusterInit(module_args, play_vars)
    assert hsm_cluster_init.module_args == module_args
    assert hsm_cluster_init.play_vars == play_vars


@pytest.mark.parametrize(
    "signed_cert, trust_anchor",
    [
        (
            "-----BEGIN CERTIFICATE-----\nMIIDUDCCAjgCCQCZHZUWolGMLjANBgkqhkiG9w0BAQsFADBJMQswCQYDVQQGEwJV\nUzELMAkGA1UECAwCTlYxEjAQBgNVBAcMCUxhcyBWZWdhczEMMAoGA1UECgwDSVRV\nMQswCQYDVQQLDAJJVDAeFw0yMjA3MjkwODQ1MjhaFw0zMjA3MjgwODQ1MjhaMIGK\nMUQwCQYDVQQGEwJVUzAJBgNVBAgMAkNBMA0GA1UECgwGQ2F2aXVtMA0GA1UECwwG\nTjNGSVBTMA4GA1UEBwwHU2FuSm9zZTFCMEAGA1UEAww5SFNNOkZCRTBGNTE4MEEz\nMDYyN0VEQkVGOUUwRTBEQTE3NDpQQVJUTjo0LCBmb3IgRklQUyBtb2RlMIIBIjAN\nBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEArHDakGPyf54vEXbnADKxkUxZpfHF\n4RLjXfp7zBPNzAi1DePSUckxdKyaqK9VsJ16COky6/XpCinTCsKET5j011FK9oE4\n2ArhEs1/mb6EL3KQvdd7BSeYnBS0L1JHhIXK/rEpjeD52xvyCz3eOh39/asRi+YQ\nCl2CBXaLdmQROVLilMmYh+OmnWFCnhT7S14h4HENsqYgbbUZLiyt+3v/2rVDUbFw\nLjqP5ZHJemsamyHwzuXUJiOEN6KJ2l5dXEtprr/zHfteWL1yM5Ne0vE72XiXoMqS\nqAZYsttV7yZ/lRJQzCvPynrQPd+4k8x3LC1R3zVbPsqdLcjuzpOh67M3+QIDAQAB\nMA0GCSqGSIb3DQEBCwUAA4IBAQBcQUfYITGtqc8PoYw+mNfwRBxPG7LjzgY9gwu0\nP5O6OtdSns1PpaTrF2dSqPljxcJF3Xoh1hQUy7y4LKafUweip1QujlAr0Z8AToAq\nxyFP2CcjuTiaE59nfLwcXE5ynK9T8FjqWPQU3+L8rYu4f+oBHiesKRNCwjB1aW0t\n2Ja7Ojb/nk3dsaG8KiSBfhnsC0XqOZF9cZOZ4ZUSU8Hqr7r5J9OUVlbRqbSSeVgy\ny+FjoxuQ6fxXJ+jBo1Ld0+E1UCKANpLg+18oUkMtm4pewn1xyIp2jLamJSDdLWO0\nRcj7jVxeSK23f67oQs5z8md3mcjw61zSAof+DMbRuvzCQTbm\n-----END CERTIFICATE-----",
            "-----BEGIN CERTIFICATE-----\nMIIDZTCCAk2gAwIBAgIJALZ5lWBXvUBxMA0GCSqGSIb3DQEBCwUAMEkxCzAJBgNV\nBAYTAlVTMQswCQYDVQQIDAJOVjESMBAGA1UEBwwJTGFzIFZlZ2FzMQwwCgYDVQQK\nDANJVFUxCzAJBgNVBAsMAklUMB4XDTIyMDcyOTAzMTUzMFoXDTMyMDcyODAzMTUz\nMFowSTELMAkGA1UEBhMCVVMxCzAJBgNVBAgMAk5WMRIwEAYDVQQHDAlMYXMgVmVn\nYXMxDDAKBgNVBAoMA0lUVTELMAkGA1UECwwCSVQwggEiMA0GCSqGSIb3DQEBAQUA\nA4IBDwAwggEKAoIBAQC8b6kHTUuwreduFDJ8Og2gD3q/8cz+nj0q54XEi6BNBU3i\nA0ykeH6PF0igGGlVGKZYOvBzCdz0lT5andRtDQ5ysQ9gTrQYsoSnCLXLa7MU+IvV\no4YLskNsflg/FGcURdKS+QzcCXWf5MIPv3rnPzPkFf6VFmk3uIGr3PVRUCs9tNZa\nfT5aejGUbnvHLq5YQo0mALCrObTCYTQ1GiohvkE+yEyKSzSVjlMY8lCbCHiHxsef\nLhwDQBlvZDP0h3FqYA8xXs/Av+G4cx25jf7GaB40gKq44mxs/JZQCTuCAlrq6wYJ\n78dZZXHrZF8JWPaDEQ/KVglJ5qy6sbpYgp8p9t0PAgMBAAGjUDBOMB0GA1UdDgQW\nBBQ7Fj4T61iO41BJ2HiMMCgq8+VeGDAfBgNVHSMEGDAWgBQ7Fj4T61iO41BJ2HiM\nMCgq8+VeGDAMBgNVHRMEBTADAQH/MA0GCSqGSIb3DQEBCwUAA4IBAQCZExIIsM9i\nM5DES1o/wfLPVuTKlMjirLPrLnoCoytT9G6ou/yvS5UnjPlHjczN5Bxb3/yU/n6p\n+1AwQTfhkocqB1TCv4PqDttVy/P7k1ZS3dFnMU95gTYStJKjbSEp4tymWSBJY1qS\n3MZyC0dVRsfeCqpnTmafTx8Q0Gjl0FWukIOH/ZH7T0HeZvZxjinlwtblHUYA/VCy\nRw//vKcv5YvPNOpDUrdaUongI9fZyuFV14c+ZOdCHfqGjVJh5I9euYmK9JxHp/OF\n8xRAtuoXinJa9t2FmDrsQSadL4theqOINNC42vmedsTgkYKcOfl9qLk6mV2JSjWc\n1pGHxwLvryHc\n-----END CERTIFICATE-----",
        ),
        (
            "./tests/unit/plugins/module_utils/mocks/signed.crt",
            "./tests/unit/plugins/module_utils/mocks/signing_ca.crt",
        ),
    ],
    ids=["Signed Cert and CA String", "Signed Cert and CA File"],
)
def test_HsmClusterInit_init_cluster(signed_cert, trust_anchor, mock_HsmClusterInit):
    """Testing HsmClusterInit.init method
    Valid information is provided, no exception is raised
    """
    hsm_cluster_init = mock_HsmClusterInit
    hsm_cluster_init.module_args["signed_cert"] = signed_cert
    hsm_cluster_init.module_args["trust_anchor"] = trust_anchor
    initialized = hsm_cluster_init.init()
    assert initialized["changed"]


def test_HsmClusterInit_init_cluster_exception(mock_HsmClusterInit):
    """Testing HsmClusterInit.init method
    Valid information is provided, but exception is raised
    """
    hsm_cluster_init = mock_HsmClusterInit
    hsm_cluster_init.client.initialize_cluster.side_effect = Exception(
        "Raising an exception for testing"
    )
    with pytest.raises(
        AnsibleActionFail, match=r"Something\s+went\s+wrong.*Reason:\s+Raising.*"
    ):
        hsm_cluster_init.init()
