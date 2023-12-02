#
# (c) 2016 Michael De La Rue
#
# This file is part of Ansible
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Make coding more python3-ish
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

__metaclass__ = type

import sys

import pytest

from ansible_collections.amazon.aws.plugins.module_utils import modules as aws_modules
from ansible_collections.amazon.aws.plugins.module_utils.botocore import HAS_BOTO3

import ansible_collections.community.aws.plugins.modules.api_gateway as agw
from ansible_collections.community.aws.tests.unit.plugins.modules.utils import set_module_args

if not HAS_BOTO3:
    pytestmark = pytest.mark.skip("test_api_gateway.py requires the `boto3` and `botocore` modules")


exit_return_dict = {}


def fake_exit_json(self, **kwargs):
    """store the kwargs given to exit_json rather than putting them out to stdout"""
    global exit_return_dict
    exit_return_dict = kwargs
    sys.exit(0)


def test_upload_api(monkeypatch):
    class FakeConnection:
        def put_rest_api(self, *args, **kwargs):
            assert kwargs["body"] == "the-swagger-text-is-fake"
            return {"msg": "success!"}

    def return_fake_connection(*args, **kwargs):
        return FakeConnection()

    # Because it's imported into the aws_modules namespace we need to override
    # it there, even though the function itself lives in module_utils.botocore
    monkeypatch.setattr(aws_modules, "boto3_conn", return_fake_connection)
    monkeypatch.setattr(aws_modules.AnsibleAWSModule, "exit_json", fake_exit_json)

    set_module_args(
        {
            "api_id": "fred",
            "state": "present",
            "swagger_text": "the-swagger-text-is-fake",
            "region": "mars-north-1",
            "_ansible_tmpdir": "/tmp/ansibl-abcdef",
        }
    )
    with pytest.raises(SystemExit):
        agw.main()
    assert exit_return_dict["changed"]


def test_warn_if_region_not_specified():
    set_module_args(
        {
            "name": "api_gateway",
            "state": "present",
            "runtime": "python2.7",
            "role": "arn:aws:iam::123456789012:role/lambda_basic_execution",
            "handler": "lambda_python.my_handler",
        }
    )
    with pytest.raises(SystemExit):
        print(agw.main())
