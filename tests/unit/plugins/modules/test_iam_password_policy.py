# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
import pytest

from ansible_collections.community.aws.tests.unit.plugins.modules.utils import set_module_args

from ansible_collections.community.aws.plugins.modules import iam_password_policy


def test_warn_if_state_not_specified(capsys):
    set_module_args({
        "min_pw_length": "8",
        "require_symbols": "false",
        "require_numbers": "true",
        "require_uppercase": "true",
        "require_lowercase": "true",
        "allow_pw_change": "true",
        "pw_max_age": "60",
        "pw_reuse_prevent": "5",
        "pw_expire": "false"
    })
    with pytest.raises(SystemExit):
        iam_password_policy.main()
    captured = capsys.readouterr()

    output = json.loads(captured.out)
    assert 'missing required arguments' in output.get('msg', '')
