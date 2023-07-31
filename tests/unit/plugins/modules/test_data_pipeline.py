# (c) 2017 Red Hat Inc.
#
# This file is part of Ansible
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# Make coding more python3-ish
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import collections
import os
import json
import pytest

from ansible.module_utils._text import to_text

try:
    import boto3
except ImportError:
    pass

# Magic...  Incorrectly identified by pylint as unused
from ansible_collections.amazon.aws.tests.unit.utils.amazon_placebo_fixtures import maybe_sleep  # pylint: disable=unused-import
from ansible_collections.amazon.aws.tests.unit.utils.amazon_placebo_fixtures import placeboify  # pylint: disable=unused-import

from ansible_collections.amazon.aws.plugins.module_utils.botocore import HAS_BOTO3
from ansible_collections.community.aws.plugins.modules import data_pipeline

if not HAS_BOTO3:
    pytestmark = pytest.mark.skip("test_data_pipeline.py requires the python modules 'boto3' and 'botocore'")


class FailException(Exception):
    pass


@pytest.fixture(scope='module')
def dp_setup():
    """
    Yield a FakeModule object, data pipeline id of a vanilla data pipeline, and data pipeline objects

    This fixture is module-scoped, since this can be reused for multiple tests.
    """
    Dependencies = collections.namedtuple("Dependencies", ["module", "data_pipeline_id", "objects"])

    # get objects to use to test populating and activating the data pipeline
    if not os.getenv('PLACEBO_RECORD'):
        objects = [{"name": "Every 1 day",
                    "id": "DefaultSchedule",
                    "fields": []},
                   {"name": "Default",
                    "id": "Default",
                    "fields": []}]
    else:
        s3 = boto3.client('s3')
        data = s3.get_object(Bucket="ansible-test-datapipeline", Key="pipeline-object/new.json")
        objects = json.loads(to_text(data['Body'].read()))

    # create a module with vanilla data pipeline parameters
    params = {'name': 'ansible-test-create-pipeline',
              'description': 'ansible-datapipeline-unit-test',
              'state': 'present',
              'timeout': 300,
              'objects': [],
              'tags': {},
              'parameters': [],
              'values': []}
    module = FakeModule(**params)

    # yield a module, the data pipeline id, and the data pipeline objects (that are not yet defining the vanilla data pipeline)
    if not os.getenv('PLACEBO_RECORD'):
        yield Dependencies(module=module, data_pipeline_id='df-0590406117G8DPQZY2HA', objects=objects)
    else:
        connection = boto3.client('datapipeline')
        _changed, result = data_pipeline.create_pipeline(connection, module)
        data_pipeline_id = result['data_pipeline']['pipeline_id']
        yield Dependencies(module=module, data_pipeline_id=data_pipeline_id, objects=objects)

    # remove data pipeline
    if os.getenv('PLACEBO_RECORD'):
        module.params.update(state='absent')
        data_pipeline.delete_pipeline(connection, module)


class FakeModule(object):
    def __init__(self, **kwargs):
        self.params = kwargs

    def fail_json(self, *args, **kwargs):
        self.exit_args = args
        self.exit_kwargs = kwargs
        raise FailException('FAIL')

    def exit_json(self, *args, **kwargs):
        self.exit_args = args
        self.exit_kwargs = kwargs


def test_create_pipeline_already_exists(placeboify, maybe_sleep, dp_setup):
    connection = placeboify.client('datapipeline')
    changed, result = data_pipeline.create_pipeline(connection, dp_setup.module)
    assert changed is False
    assert "Data Pipeline ansible-test-create-pipeline is present" in result['msg']


def test_pipeline_field(placeboify, maybe_sleep, dp_setup):
    connection = placeboify.client('datapipeline')
    pipeline_field_info = data_pipeline.pipeline_field(connection, dp_setup.data_pipeline_id, "@pipelineState")
    assert pipeline_field_info == "PENDING"


def test_define_pipeline(placeboify, maybe_sleep, dp_setup):
    connection = placeboify.client('datapipeline')
    changed, result = data_pipeline.define_pipeline(connection, dp_setup.module, dp_setup.objects, dp_setup.data_pipeline_id)
    assert changed is True
    assert 'has been updated' in result


def test_deactivate_pipeline(placeboify, maybe_sleep, dp_setup):
    connection = placeboify.client('datapipeline')
    _changed, result = data_pipeline.deactivate_pipeline(connection, dp_setup.module)
    # XXX possible bug
    # assert changed is True
    assert "Data Pipeline ansible-test-create-pipeline deactivated" in result['msg']


def test_activate_without_population(placeboify, maybe_sleep, dp_setup):
    connection = placeboify.client('datapipeline')
    with pytest.raises(FailException):
        _changed, _result = data_pipeline.activate_pipeline(connection, dp_setup.module)
    assert dp_setup.module.exit_kwargs.get('msg') == "You need to populate your pipeline before activation."


def test_create_pipeline(placeboify, maybe_sleep):
    connection = placeboify.client('datapipeline')
    params = {'name': 'ansible-unittest-create-pipeline',
              'description': 'ansible-datapipeline-unit-test',
              'state': 'present',
              'timeout': 300,
              'tags': {}}
    m = FakeModule(**params)
    changed, result = data_pipeline.create_pipeline(connection, m)
    assert changed is True
    assert result['msg'] == "Data Pipeline ansible-unittest-create-pipeline created."

    data_pipeline.delete_pipeline(connection, m)


def test_create_pipeline_with_tags(placeboify, maybe_sleep):
    connection = placeboify.client('datapipeline')
    params = {'name': 'ansible-unittest-create-pipeline_tags',
              'description': 'ansible-datapipeline-unit-test',
              'state': 'present',
              'tags': {'ansible': 'test'},
              'timeout': 300}
    m = FakeModule(**params)
    changed, result = data_pipeline.create_pipeline(connection, m)
    assert changed is True
    assert result['msg'] == "Data Pipeline ansible-unittest-create-pipeline_tags created."

    data_pipeline.delete_pipeline(connection, m)


def test_delete_nonexistent_pipeline(placeboify, maybe_sleep):
    connection = placeboify.client('datapipeline')
    params = {'name': 'ansible-test-nonexistent',
              'description': 'ansible-test-nonexistent',
              'state': 'absent',
              'objects': [],
              'tags': {'ansible': 'test'},
              'timeout': 300}
    m = FakeModule(**params)
    changed, _result = data_pipeline.delete_pipeline(connection, m)
    assert changed is False


def test_delete_pipeline(placeboify, maybe_sleep):
    connection = placeboify.client('datapipeline')
    params = {'name': 'ansible-test-nonexistent',
              'description': 'ansible-test-nonexistent',
              'state': 'absent',
              'objects': [],
              'tags': {'ansible': 'test'},
              'timeout': 300}
    m = FakeModule(**params)
    data_pipeline.create_pipeline(connection, m)
    changed, _result = data_pipeline.delete_pipeline(connection, m)
    assert changed is True


def test_build_unique_id_different():
    m = FakeModule(**{'name': 'ansible-unittest-1', 'description': 'test-unique-id'})
    m2 = FakeModule(**{'name': 'ansible-unittest-1', 'description': 'test-unique-id-different'})
    assert data_pipeline.build_unique_id(m) != data_pipeline.build_unique_id(m2)


def test_build_unique_id_same():
    m = FakeModule(**{'name': 'ansible-unittest-1', 'description': 'test-unique-id', 'tags': {'ansible': 'test'}})
    m2 = FakeModule(**{'name': 'ansible-unittest-1', 'description': 'test-unique-id', 'tags': {'ansible': 'test'}})
    assert data_pipeline.build_unique_id(m) == data_pipeline.build_unique_id(m2)


def test_build_unique_id_obj():
    # check that the object can be different and the unique id should be the same; should be able to modify objects
    m = FakeModule(**{'name': 'ansible-unittest-1', 'objects': [{'first': 'object'}]})
    m2 = FakeModule(**{'name': 'ansible-unittest-1', 'objects': [{'second': 'object'}]})
    assert data_pipeline.build_unique_id(m) == data_pipeline.build_unique_id(m2)


def test_format_tags():
    unformatted_tags = {'key1': 'val1', 'key2': 'val2', 'key3': 'val3'}
    formatted_tags = data_pipeline.format_tags(unformatted_tags)
    for tag_set in formatted_tags:
        assert unformatted_tags[tag_set['key']] == tag_set['value']


def test_format_empty_tags():
    unformatted_tags = {}
    formatted_tags = data_pipeline.format_tags(unformatted_tags)
    assert formatted_tags == []


def test_pipeline_description(placeboify, maybe_sleep, dp_setup):
    connection = placeboify.client('datapipeline')
    dp_id = dp_setup.data_pipeline_id
    pipelines = data_pipeline.pipeline_description(connection, dp_id)
    assert dp_id == pipelines['pipelineDescriptionList'][0]['pipelineId']


def test_pipeline_description_nonexistent(placeboify, maybe_sleep):
    hypothetical_pipeline_id = "df-015440025PF7YGLDK47C"
    connection = placeboify.client('datapipeline')
    with pytest.raises(data_pipeline.DataPipelineNotFound):
        data_pipeline.pipeline_description(connection, hypothetical_pipeline_id)


def test_check_dp_exists_true(placeboify, maybe_sleep, dp_setup):
    connection = placeboify.client('datapipeline')
    exists = data_pipeline.check_dp_exists(connection, dp_setup.data_pipeline_id)
    assert exists is True


def test_check_dp_exists_false(placeboify, maybe_sleep):
    hypothetical_pipeline_id = "df-015440025PF7YGLDK47C"
    connection = placeboify.client('datapipeline')
    exists = data_pipeline.check_dp_exists(connection, hypothetical_pipeline_id)
    assert exists is False


def test_check_dp_status(placeboify, maybe_sleep, dp_setup):
    inactive_states = ['INACTIVE', 'PENDING', 'FINISHED', 'DELETING']
    connection = placeboify.client('datapipeline')
    state = data_pipeline.check_dp_status(connection, dp_setup.data_pipeline_id, inactive_states)
    assert state is True


def test_activate_pipeline(placeboify, maybe_sleep, dp_setup):
    # use objects to define pipeline before activating
    connection = placeboify.client('datapipeline')
    data_pipeline.define_pipeline(connection,
                                  module=dp_setup.module,
                                  objects=dp_setup.objects,
                                  dp_id=dp_setup.data_pipeline_id)
    changed, _result = data_pipeline.activate_pipeline(connection, dp_setup.module)
    assert changed is True
