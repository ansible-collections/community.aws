import pytest

from ansible_collections.community.aws.plugins.modules import eks_nodegroup


class _ArgumentSpecCaptured(Exception):
    pass


class _CapturingModule:
    """Stands in for AnsibleAWSModule: records the argument spec main() builds, then stops."""

    argument_spec = None

    def __init__(self, argument_spec, **kwargs):
        _CapturingModule.argument_spec = argument_spec
        raise _ArgumentSpecCaptured()


def _argument_spec(monkeypatch):
    monkeypatch.setattr(eks_nodegroup, "AnsibleAWSModule", _CapturingModule)
    with pytest.raises(_ArgumentSpecCaptured):
        eks_nodegroup.main()
    return _CapturingModule.argument_spec


def test_module_import():
    """Check module can be imported."""
    assert eks_nodegroup is not None


def test_ami_choices(monkeypatch):
    """Ensure AL2023 AMI types are included."""
    ami_choices = _argument_spec(monkeypatch)["ami_type"]["choices"]
    assert "AL2023_x86_64_STANDARD" in ami_choices
    assert "AL2023_ARM_64_STANDARD" in ami_choices
