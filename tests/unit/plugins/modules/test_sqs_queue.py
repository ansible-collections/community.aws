# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import json
from unittest.mock import MagicMock, call, patch

import botocore.exceptions
import pytest

from ansible_collections.community.aws.plugins.modules.sqs_queue import create_or_update_sqs_queue
from ansible_collections.community.aws.plugins.modules.sqs_queue import delete_sqs_queue
from ansible_collections.community.aws.plugins.modules.sqs_queue import describe_queue
from ansible_collections.community.aws.plugins.modules.sqs_queue import get_queue_name
from ansible_collections.community.aws.plugins.modules.sqs_queue import update_sqs_queue
from ansible_collections.community.aws.plugins.modules.sqs_queue import update_tags


QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/123456789012/test-queue"
QUEUE_ARN = "arn:aws:sqs:us-east-1:123456789012:test-queue"
FIFO_QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/123456789012/test-queue.fifo"
FIFO_QUEUE_ARN = "arn:aws:sqs:us-east-1:123456789012:test-queue.fifo"

BASE_ATTRIBUTES = {
    "QueueArn": QUEUE_ARN,
    "VisibilityTimeout": "30",
    "MaximumMessageSize": "262144",
    "MessageRetentionPeriod": "345600",
    "DelaySeconds": "0",
    "ReceiveMessageWaitTimeSeconds": "0",
}


def _make_module(
    name="test-queue",
    queue_type="standard",
    check_mode=False,
    state="present",
    visibility_timeout=None,
    delay_seconds=None,
    maximum_message_size=None,
    message_retention_period=None,
    receive_message_wait_time_seconds=None,
    policy=None,
    redrive_policy=None,
    kms_master_key_id=None,
    kms_data_key_reuse_period_seconds=None,
    content_based_deduplication=None,
    deduplication_scope=None,
    fifo_throughput_limit=None,
    tags=None,
    purge_tags=True,
):
    params = {
        "name": name,
        "region": "us-east-1",
        "state": state,
        "queue_type": queue_type,
        "visibility_timeout": visibility_timeout,
        "delay_seconds": delay_seconds,
        "maximum_message_size": maximum_message_size,
        "message_retention_period": message_retention_period,
        "receive_message_wait_time_seconds": receive_message_wait_time_seconds,
        "policy": policy,
        "redrive_policy": redrive_policy,
        "kms_master_key_id": kms_master_key_id,
        "kms_data_key_reuse_period_seconds": kms_data_key_reuse_period_seconds,
        "content_based_deduplication": content_based_deduplication,
        "deduplication_scope": deduplication_scope,
        "fifo_throughput_limit": fifo_throughput_limit,
        "tags": tags,
        "purge_tags": purge_tags,
    }
    module = MagicMock()
    module.params = params
    module.check_mode = check_mode
    return module


def _make_client(attributes=None, existing_tags=None):
    client = MagicMock()
    attrs = dict(BASE_ATTRIBUTES)
    if attributes:
        attrs.update(attributes)
    client.get_queue_attributes.return_value = {"Attributes": attrs}
    client.create_queue.return_value = {"QueueUrl": QUEUE_URL}
    client.list_queue_tags.return_value = {"Tags": existing_tags or {}}
    return client


# ---------------------------------------------------------------------------
# get_queue_name
# ---------------------------------------------------------------------------


class TestGetQueueName:
    def test_standard_queue_name_unchanged(self):
        module = _make_module(name="my-queue", queue_type="standard")
        assert get_queue_name(module) == "my-queue"

    def test_fifo_queue_appends_suffix(self):
        module = _make_module(name="my-queue", queue_type="fifo")
        assert get_queue_name(module, is_fifo=True) == "my-queue.fifo"

    def test_fifo_queue_already_has_suffix(self):
        module = _make_module(name="my-queue.fifo", queue_type="fifo")
        assert get_queue_name(module, is_fifo=True) == "my-queue.fifo"

    def test_standard_queue_ignores_is_fifo_false(self):
        module = _make_module(name="my-queue", queue_type="standard")
        assert get_queue_name(module, is_fifo=False) == "my-queue"

    def test_default_is_fifo_is_false(self):
        # Calling without is_fifo should not append .fifo
        module = _make_module(name="my-queue", queue_type="standard")
        assert get_queue_name(module) == "my-queue"


# ---------------------------------------------------------------------------
# describe_queue
# ---------------------------------------------------------------------------


class TestDescribeQueue:
    def test_basic_attributes_snake_cased(self):
        client = _make_client()
        result = describe_queue(client, QUEUE_URL)

        assert result["queue_arn"] == QUEUE_ARN
        assert result["visibility_timeout"] == 30
        assert result["maximum_message_size"] == 262144
        assert result["message_retention_period"] == 345600
        assert result["delay_seconds"] == 0
        assert result["receive_message_wait_time_seconds"] == 0

    def test_string_integers_converted_to_int(self):
        client = _make_client(attributes={"VisibilityTimeout": "120"})
        result = describe_queue(client, QUEUE_URL)
        assert result["visibility_timeout"] == 120
        assert isinstance(result["visibility_timeout"], int)

    def test_policy_parsed_from_json_string(self):
        policy = {"Version": "2012-10-17", "Statement": []}
        client = _make_client(attributes={"Policy": json.dumps(policy)})
        result = describe_queue(client, QUEUE_URL)
        assert result["policy"] == policy

    def test_redrive_policy_parsed_from_json_string(self):
        redrive = {"maxReceiveCount": 5, "deadLetterTargetArn": QUEUE_ARN}
        client = _make_client(attributes={"RedrivePolicy": json.dumps(redrive)})
        result = describe_queue(client, QUEUE_URL)
        assert result["redrive_policy"] == redrive

    def test_policy_none_when_absent(self):
        client = _make_client()
        result = describe_queue(client, QUEUE_URL)
        assert result["policy"] is None

    def test_redrive_policy_none_when_absent(self):
        client = _make_client()
        result = describe_queue(client, QUEUE_URL)
        assert result["redrive_policy"] is None

    def test_policy_excluded_from_camel_conversion(self):
        policy = {"Version": "2012-10-17", "Statement": []}
        client = _make_client(attributes={"Policy": json.dumps(policy)})
        result = describe_queue(client, QUEUE_URL)
        # Should not appear as camel-cased key alongside snake-cased policy
        assert "Policy" not in result

    def test_calls_get_queue_attributes_for_all_attrs(self):
        client = _make_client()
        describe_queue(client, QUEUE_URL)
        client.get_queue_attributes.assert_called_once_with(
            QueueUrl=QUEUE_URL, AttributeNames=["All"], aws_retry=True
        )

    def test_kms_key_id_included(self):
        client = _make_client(attributes={"KmsMasterKeyId": "alias/MyKey"})
        result = describe_queue(client, QUEUE_URL)
        assert result["kms_master_key_id"] == "alias/MyKey"

    def test_kms_data_key_reuse_period_converted_to_int(self):
        client = _make_client(attributes={"KmsDataKeyReusePeriodSeconds": "300"})
        result = describe_queue(client, QUEUE_URL)
        assert result["kms_data_key_reuse_period_seconds"] == 300
        assert isinstance(result["kms_data_key_reuse_period_seconds"], int)


# ---------------------------------------------------------------------------
# update_sqs_queue
# ---------------------------------------------------------------------------


class TestUpdateSqsQueue:
    def test_no_change_when_params_match_existing(self):
        client = _make_client()
        module = _make_module(visibility_timeout=30)
        changed, _ = update_sqs_queue(module, client, QUEUE_URL)
        assert changed is False
        client.set_queue_attributes.assert_not_called()

    def test_changed_when_visibility_timeout_differs(self):
        client = _make_client()
        module = _make_module(visibility_timeout=60)
        changed, _ = update_sqs_queue(module, client, QUEUE_URL)
        assert changed is True
        client.set_queue_attributes.assert_called_once()
        attrs_sent = client.set_queue_attributes.call_args[1]["Attributes"]
        assert attrs_sent["VisibilityTimeout"] == "60"

    def test_changed_when_delay_seconds_differs(self):
        client = _make_client()
        module = _make_module(delay_seconds=10)
        changed, _ = update_sqs_queue(module, client, QUEUE_URL)
        assert changed is True
        attrs_sent = client.set_queue_attributes.call_args[1]["Attributes"]
        assert attrs_sent["DelaySeconds"] == "10"

    def test_changed_when_message_retention_period_differs(self):
        client = _make_client()
        module = _make_module(message_retention_period=86400)
        changed, _ = update_sqs_queue(module, client, QUEUE_URL)
        assert changed is True
        attrs_sent = client.set_queue_attributes.call_args[1]["Attributes"]
        assert attrs_sent["MessageRetentionPeriod"] == "86400"

    def test_changed_when_maximum_message_size_differs(self):
        client = _make_client()
        module = _make_module(maximum_message_size=1024)
        changed, _ = update_sqs_queue(module, client, QUEUE_URL)
        assert changed is True
        attrs_sent = client.set_queue_attributes.call_args[1]["Attributes"]
        assert attrs_sent["MaximumMessageSize"] == "1024"

    def test_check_mode_does_not_call_set_attributes(self):
        client = _make_client()
        module = _make_module(visibility_timeout=60, check_mode=True)
        changed, _ = update_sqs_queue(module, client, QUEUE_URL)
        assert changed is True
        client.set_queue_attributes.assert_not_called()

    def test_no_change_when_no_params_set(self):
        client = _make_client()
        module = _make_module()
        changed, _ = update_sqs_queue(module, client, QUEUE_URL)
        assert changed is False
        client.set_queue_attributes.assert_not_called()

    def test_policy_change_detected(self):
        client = _make_client()
        new_policy = {"Version": "2012-10-17", "Statement": [{"Effect": "Allow"}]}
        module = _make_module(policy=new_policy)
        changed, _ = update_sqs_queue(module, client, QUEUE_URL)
        assert changed is True
        attrs_sent = client.set_queue_attributes.call_args[1]["Attributes"]
        assert json.loads(attrs_sent["Policy"]) == new_policy

    def test_policy_no_change_when_same(self):
        existing_policy = {"Version": "2012-10-17", "Statement": []}
        client = _make_client(attributes={"Policy": json.dumps(existing_policy)})
        module = _make_module(policy=existing_policy)
        changed, _ = update_sqs_queue(module, client, QUEUE_URL)
        assert changed is False
        client.set_queue_attributes.assert_not_called()

    def test_redrive_policy_change_detected(self):
        client = _make_client()
        redrive = {"maxReceiveCount": 5, "deadLetterTargetArn": QUEUE_ARN}
        module = _make_module(redrive_policy=redrive)
        changed, _ = update_sqs_queue(module, client, QUEUE_URL)
        assert changed is True
        attrs_sent = client.set_queue_attributes.call_args[1]["Attributes"]
        assert json.loads(attrs_sent["RedrivePolicy"]) == redrive

    def test_redrive_policy_empty_dict_clears_policy(self):
        existing_redrive = {"maxReceiveCount": 3, "deadLetterTargetArn": QUEUE_ARN}
        client = _make_client(attributes={"RedrivePolicy": json.dumps(existing_redrive)})
        module = _make_module(redrive_policy={})
        changed, _ = update_sqs_queue(module, client, QUEUE_URL)
        assert changed is True

    def test_bool_attribute_converted_for_comparison(self):
        client = _make_client(attributes={"ContentBasedDeduplication": "false"})
        module = _make_module(content_based_deduplication=True)
        changed, _ = update_sqs_queue(module, client, QUEUE_URL)
        assert changed is True
        attrs_sent = client.set_queue_attributes.call_args[1]["Attributes"]
        # Booleans are lowercased via str(bool).lower() before storing
        assert attrs_sent["ContentBasedDeduplication"] == "true"

    def test_bool_no_change_when_value_matches(self):
        client = _make_client(attributes={"ContentBasedDeduplication": "true"})
        module = _make_module(content_based_deduplication=True)
        changed, _ = update_sqs_queue(module, client, QUEUE_URL)
        assert changed is False

    def test_multiple_attributes_changed_in_one_call(self):
        client = _make_client()
        module = _make_module(visibility_timeout=60, delay_seconds=5)
        changed, _ = update_sqs_queue(module, client, QUEUE_URL)
        assert changed is True
        client.set_queue_attributes.assert_called_once()
        attrs_sent = client.set_queue_attributes.call_args[1]["Attributes"]
        assert "VisibilityTimeout" in attrs_sent
        assert "DelaySeconds" in attrs_sent

    def test_deduplication_scope_change_detected(self):
        client = _make_client(attributes={"DeduplicationScope": "queue"})
        module = _make_module(deduplication_scope="messageGroup")
        changed, _ = update_sqs_queue(module, client, QUEUE_URL)
        assert changed is True

    def test_fifo_throughput_limit_change_detected(self):
        client = _make_client(attributes={"FifoThroughputLimit": "perQueue"})
        module = _make_module(fifo_throughput_limit="perMessageGroupId")
        changed, _ = update_sqs_queue(module, client, QUEUE_URL)
        assert changed is True

    def test_kms_master_key_id_change_detected(self):
        client = _make_client(attributes={"KmsMasterKeyId": "alias/OldKey"})
        module = _make_module(kms_master_key_id="alias/NewKey")
        changed, _ = update_sqs_queue(module, client, QUEUE_URL)
        assert changed is True
        attrs_sent = client.set_queue_attributes.call_args[1]["Attributes"]
        assert attrs_sent["KmsMasterKeyId"] == "alias/NewKey"

    def test_receive_message_wait_time_change_detected(self):
        client = _make_client()
        module = _make_module(receive_message_wait_time_seconds=20)
        changed, _ = update_sqs_queue(module, client, QUEUE_URL)
        assert changed is True
        attrs_sent = client.set_queue_attributes.call_args[1]["Attributes"]
        assert attrs_sent["ReceiveMessageWaitTimeSeconds"] == "20"


# ---------------------------------------------------------------------------
# create_or_update_sqs_queue
# ---------------------------------------------------------------------------


class TestCreateOrUpdateSqsQueue:
    @patch("ansible_collections.community.aws.plugins.modules.sqs_queue.get_queue_url", return_value=None)
    def test_create_new_standard_queue(self, _mock_url):
        client = _make_client()
        module = _make_module()
        result = create_or_update_sqs_queue(client, module)
        client.create_queue.assert_called_once()
        assert result["changed"] is True

    @patch("ansible_collections.community.aws.plugins.modules.sqs_queue.get_queue_url", return_value=None)
    def test_create_fifo_queue_sets_fifo_attribute(self, _mock_url):
        client = _make_client()
        module = _make_module(name="my-queue", queue_type="fifo")
        create_or_update_sqs_queue(client, module)
        attrs_sent = client.create_queue.call_args[1]["Attributes"]
        assert attrs_sent.get("FifoQueue") == "True"

    @patch("ansible_collections.community.aws.plugins.modules.sqs_queue.get_queue_url", return_value=None)
    def test_create_standard_queue_no_fifo_attribute(self, _mock_url):
        client = _make_client()
        module = _make_module()
        create_or_update_sqs_queue(client, module)
        attrs_sent = client.create_queue.call_args[1]["Attributes"]
        assert "FifoQueue" not in attrs_sent

    @patch("ansible_collections.community.aws.plugins.modules.sqs_queue.get_queue_url", return_value=None)
    def test_create_with_kms_key_sets_attribute(self, _mock_url):
        client = _make_client()
        module = _make_module(kms_master_key_id="alias/MyKey")
        create_or_update_sqs_queue(client, module)
        attrs_sent = client.create_queue.call_args[1]["Attributes"]
        assert attrs_sent.get("KmsMasterKeyId") == "alias/MyKey"

    @patch("ansible_collections.community.aws.plugins.modules.sqs_queue.get_queue_url", return_value=None)
    def test_create_without_kms_key_omits_attribute(self, _mock_url):
        client = _make_client()
        module = _make_module()
        create_or_update_sqs_queue(client, module)
        attrs_sent = client.create_queue.call_args[1]["Attributes"]
        assert "KmsMasterKeyId" not in attrs_sent

    @patch(
        "ansible_collections.community.aws.plugins.modules.sqs_queue.get_queue_url",
        return_value=None,
    )
    def test_check_mode_does_not_create_queue(self, _mock_url):
        client = _make_client()
        module = _make_module(check_mode=True)
        result = create_or_update_sqs_queue(client, module)
        client.create_queue.assert_not_called()
        assert result["changed"] is True

    @patch(
        "ansible_collections.community.aws.plugins.modules.sqs_queue.get_queue_url",
        return_value=QUEUE_URL,
    )
    def test_update_existing_queue_does_not_call_create(self, _mock_url):
        client = _make_client()
        module = _make_module()
        create_or_update_sqs_queue(client, module)
        client.create_queue.assert_not_called()

    @patch(
        "ansible_collections.community.aws.plugins.modules.sqs_queue.get_queue_url",
        return_value=QUEUE_URL,
    )
    def test_no_change_on_existing_queue_with_same_params(self, _mock_url):
        client = _make_client()
        module = _make_module()
        result = create_or_update_sqs_queue(client, module)
        assert result["changed"] is False

    @patch(
        "ansible_collections.community.aws.plugins.modules.sqs_queue.get_queue_url",
        return_value=QUEUE_URL,
    )
    def test_changed_when_updating_attribute(self, _mock_url):
        client = _make_client()
        module = _make_module(visibility_timeout=60)
        result = create_or_update_sqs_queue(client, module)
        assert result["changed"] is True

    @patch("ansible_collections.community.aws.plugins.modules.sqs_queue.get_queue_url", return_value=None)
    def test_result_includes_queue_name(self, _mock_url):
        client = _make_client()
        module = _make_module(name="test-queue")
        result = create_or_update_sqs_queue(client, module)
        assert result["name"] == "test-queue"

    @patch("ansible_collections.community.aws.plugins.modules.sqs_queue.get_queue_url", return_value=None)
    def test_fifo_result_includes_fifo_queue_name(self, _mock_url):
        client = _make_client()
        module = _make_module(name="my-queue", queue_type="fifo")
        result = create_or_update_sqs_queue(client, module)
        assert result["name"] == "my-queue.fifo"

    @patch("ansible_collections.community.aws.plugins.modules.sqs_queue.get_queue_url", return_value=None)
    def test_result_includes_region(self, _mock_url):
        client = _make_client()
        module = _make_module()
        result = create_or_update_sqs_queue(client, module)
        assert result["region"] == "us-east-1"

    @patch(
        "ansible_collections.community.aws.plugins.modules.sqs_queue.get_queue_url",
        return_value=QUEUE_URL,
    )
    def test_result_includes_compatibility_aliases(self, _mock_url):
        client = _make_client()
        module = _make_module()
        result = create_or_update_sqs_queue(client, module)
        # These compatibility keys must be present alongside the canonical names
        assert "delivery_delay" in result
        assert "receive_message_wait_time" in result
        assert "default_visibility_timeout" in result

    @patch(
        "ansible_collections.community.aws.plugins.modules.sqs_queue.get_queue_url",
        return_value=QUEUE_URL,
    )
    def test_tags_included_in_result(self, _mock_url):
        client = _make_client(existing_tags={"Env": "prod"})
        module = _make_module(tags={"Env": "prod"})
        result = create_or_update_sqs_queue(client, module)
        assert result["tags"] == {"Env": "prod"}


# ---------------------------------------------------------------------------
# delete_sqs_queue
# ---------------------------------------------------------------------------


class TestDeleteSqsQueue:
    @patch(
        "ansible_collections.community.aws.plugins.modules.sqs_queue.get_queue_url",
        return_value=QUEUE_URL,
    )
    def test_delete_existing_queue_marks_changed(self, _mock_url):
        client = _make_client()
        module = _make_module(state="absent")
        result = delete_sqs_queue(client, module)
        assert result["changed"] is True

    @patch(
        "ansible_collections.community.aws.plugins.modules.sqs_queue.get_queue_url",
        return_value=QUEUE_URL,
    )
    def test_delete_calls_delete_queue(self, _mock_url):
        client = _make_client()
        module = _make_module(state="absent")
        delete_sqs_queue(client, module)
        client.delete_queue.assert_called_once()

    @patch(
        "ansible_collections.community.aws.plugins.modules.sqs_queue.get_queue_url",
        return_value=None,
    )
    def test_delete_nonexistent_queue_not_changed(self, _mock_url):
        client = _make_client()
        module = _make_module(state="absent")
        result = delete_sqs_queue(client, module)
        assert result["changed"] is False
        client.delete_queue.assert_not_called()

    @patch(
        "ansible_collections.community.aws.plugins.modules.sqs_queue.get_queue_url",
        return_value=QUEUE_URL,
    )
    def test_delete_check_mode_does_not_call_delete_queue(self, _mock_url):
        client = _make_client()
        module = _make_module(state="absent", check_mode=True)
        result = delete_sqs_queue(client, module)
        assert result["changed"] is True
        client.delete_queue.assert_not_called()

    @patch(
        "ansible_collections.community.aws.plugins.modules.sqs_queue.get_queue_url",
    )
    def test_delete_fifo_queue_appends_suffix_in_lookup(self, mock_url):
        mock_url.return_value = FIFO_QUEUE_URL
        client = _make_client()
        module = _make_module(name="test-queue", queue_type="fifo", state="absent")
        delete_sqs_queue(client, module)
        # get_queue_url should be called with the .fifo suffixed name
        mock_url.assert_called_once()
        args = mock_url.call_args
        assert args[0][1] == "test-queue.fifo"

    @patch(
        "ansible_collections.community.aws.plugins.modules.sqs_queue.get_queue_url",
        return_value=QUEUE_URL,
    )
    def test_delete_result_contains_name_and_region(self, _mock_url):
        client = _make_client()
        module = _make_module(name="test-queue", state="absent")
        result = delete_sqs_queue(client, module)
        assert result["name"] == "test-queue"
        assert result["region"] == "us-east-1"


# ---------------------------------------------------------------------------
# update_tags
# ---------------------------------------------------------------------------


class TestUpdateTags:
    def test_no_tags_param_returns_unchanged(self):
        client = _make_client()
        module = _make_module(tags=None)
        changed, tags = update_tags(client, QUEUE_URL, module)
        assert changed is False
        assert tags == {}

    def test_add_new_tags(self):
        client = _make_client(existing_tags={})
        # list_queue_tags is called twice: once to read existing, once to read final state
        client.list_queue_tags.side_effect = [
            {"Tags": {}},
            {"Tags": {"Env": "prod"}},
        ]
        module = _make_module(tags={"Env": "prod"})
        changed, _ = update_tags(client, QUEUE_URL, module)
        assert changed is True
        client.tag_queue.assert_called_once_with(QueueUrl=QUEUE_URL, Tags={"Env": "prod"})

    def test_remove_tags_with_purge(self):
        client = _make_client(existing_tags={"OldKey": "OldVal"})
        client.list_queue_tags.side_effect = [
            {"Tags": {"OldKey": "OldVal"}},
            {"Tags": {}},
        ]
        module = _make_module(tags={}, purge_tags=True)
        changed, _ = update_tags(client, QUEUE_URL, module)
        assert changed is True
        client.untag_queue.assert_called_once()

    def test_keep_tags_without_purge(self):
        client = _make_client(existing_tags={"OldKey": "OldVal"})
        client.list_queue_tags.return_value = {"Tags": {"OldKey": "OldVal"}}
        module = _make_module(tags={}, purge_tags=False)
        changed, _ = update_tags(client, QUEUE_URL, module)
        assert changed is False
        client.untag_queue.assert_not_called()

    def test_no_change_when_tags_identical(self):
        existing = {"Env": "prod", "Team": "infra"}
        client = _make_client(existing_tags=existing)
        client.list_queue_tags.return_value = {"Tags": existing}
        module = _make_module(tags=existing)
        changed, _ = update_tags(client, QUEUE_URL, module)
        assert changed is False

    def test_check_mode_does_not_call_tag_queue(self):
        client = _make_client(existing_tags={})
        module = _make_module(tags={"Env": "prod"}, check_mode=True)
        changed, _ = update_tags(client, QUEUE_URL, module)
        assert changed is True
        client.tag_queue.assert_not_called()

    def test_check_mode_returns_desired_tags(self):
        client = _make_client(existing_tags={})
        desired = {"Env": "staging"}
        module = _make_module(tags=desired, check_mode=True)
        _, result_tags = update_tags(client, QUEUE_URL, module)
        assert result_tags == desired

    def test_update_existing_tag_value(self):
        client = _make_client(existing_tags={"Env": "dev"})
        client.list_queue_tags.side_effect = [
            {"Tags": {"Env": "dev"}},
            {"Tags": {"Env": "prod"}},
        ]
        module = _make_module(tags={"Env": "prod"})
        changed, _ = update_tags(client, QUEUE_URL, module)
        assert changed is True
        client.tag_queue.assert_called_once_with(QueueUrl=QUEUE_URL, Tags={"Env": "prod"})

    def test_list_queue_tags_error_treated_as_empty(self):
        client = _make_client()
        access_denied = botocore.exceptions.ClientError(
            {"Error": {"Code": "AccessDenied", "Message": "Access denied"}}, "ListQueueTags"
        )
        # First call raises (treated as empty existing tags); second returns final state
        client.list_queue_tags.side_effect = [access_denied, {"Tags": {"Env": "prod"}}]
        module = _make_module(tags={"Env": "prod"})
        changed, _ = update_tags(client, QUEUE_URL, module)
        assert changed is True

    def test_partial_tag_update_leaves_other_tags(self):
        existing = {"Env": "dev", "Team": "infra"}
        client = _make_client(existing_tags=existing)
        client.list_queue_tags.side_effect = [
            {"Tags": existing},
            {"Tags": {"Env": "prod", "Team": "infra"}},
        ]
        module = _make_module(tags={"Env": "prod", "Team": "infra"}, purge_tags=False)
        changed, _ = update_tags(client, QUEUE_URL, module)
        assert changed is True
        # Only Env should be updated; Team was already correct
        client.tag_queue.assert_called_once_with(QueueUrl=QUEUE_URL, Tags={"Env": "prod"})
        client.untag_queue.assert_not_called()
