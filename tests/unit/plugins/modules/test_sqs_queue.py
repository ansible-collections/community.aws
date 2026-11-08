# -*- coding: utf-8 -*-

# Copyright: Contributors to the Ansible project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

import json
from unittest.mock import MagicMock

import pytest

from ansible_collections.community.aws.plugins.modules.sqs_queue import update_sqs_queue

QUEUE_URL = "https://sqs.us-east-1.amazonaws.com/123456789012/my-queue"
REDRIVE_POLICY = {
    "maxReceiveCount": 5,
    "deadLetterTargetArn": "arn:aws:sqs:us-east-1:123456789012:my-dead-queue",
}


def _module(redrive_policy):
    module = MagicMock()
    module.check_mode = False
    module.params = {"redrive_policy": redrive_policy, "policy": None}
    return module


def _client(attributes):
    client = MagicMock()
    client.get_queue_attributes.return_value = {"Attributes": attributes}
    return client


def test_empty_redrive_policy_removes_existing_policy():
    client = _client({"RedrivePolicy": json.dumps(REDRIVE_POLICY)})

    changed, _ = update_sqs_queue(_module({}), client, QUEUE_URL)

    assert changed is True
    # SQS rejects "{}" (maxReceiveCount is mandatory), an empty string removes the policy
    client.set_queue_attributes.assert_called_once_with(
        QueueUrl=QUEUE_URL, Attributes={"RedrivePolicy": ""}, aws_retry=True
    )


@pytest.mark.parametrize("attributes", [{}, {"RedrivePolicy": ""}])
def test_empty_redrive_policy_without_existing_policy(attributes):
    client = _client(attributes)

    changed, _ = update_sqs_queue(_module({}), client, QUEUE_URL)

    assert changed is False
    client.set_queue_attributes.assert_not_called()


def test_redrive_policy_is_set_as_json():
    client = _client({})

    changed, _ = update_sqs_queue(_module(REDRIVE_POLICY), client, QUEUE_URL)

    assert changed is True
    attributes = client.set_queue_attributes.call_args.kwargs["Attributes"]
    assert json.loads(attributes["RedrivePolicy"]) == REDRIVE_POLICY
