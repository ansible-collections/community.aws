import pytest
from ansible_collections.community.aws.plugins.modules import eks_nodegroup


def test_module_import():
    """Check module can be imported."""
    assert eks_nodegroup is not None


def test_ami_choices():
    """Ensure AL2023 AMI types are included."""
    arg_spec = eks_nodegroup.argument_spec
    ami_choices = arg_spec['ami_type']['choices']
    assert 'AL2023_x86_64_STANDARD' in ami_choices
    assert 'AL2023_ARM_64_STANDARD' in ami_choices
