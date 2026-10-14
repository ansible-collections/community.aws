#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2025 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: ses_configuration_set
version_added: "11.0.0"
short_description: Manage AWS SES configuration sets
description:
  - Create, update, or delete AWS SES configuration sets.

author:
  - Nicolas Boutet (@boutetnico)

options:
  name:
    description:
      - Name of the SES configuration set.
    required: true
    type: str
  state:
    description:
      - Desired state of the configuration set.
      - C(present) ensures the configuration set exists.
      - C(absent) ensures the configuration set is deleted.
    choices: [present, absent]
    default: present
    type: str
  delivery_options:
    description:
      - Delivery options for the configuration set.
    type: dict
    suboptions:
      tls_policy:
        description:
          - Whether to require TLS for the configuration set.
          - If enabled, Amazon SES will establish a secure connection with the receiving mail server.
        type: bool
      sending_pool_name:
        description:
          - Name of the dedicated IP pool to associate with the configuration set.
        type: str
  reputation_options:
    description:
      - Reputation options for the configuration set.
    type: dict
    suboptions:
      reputation_metrics_enabled:
        description:
          - Whether reputation metrics are enabled for the configuration set.
        type: bool
  sending_options:
    description:
      - Sending options for the configuration set.
    type: dict
    suboptions:
      sending_enabled:
        description:
          - Whether email sending is enabled for the configuration set.
        type: bool
  suppression_options:
    description:
      - Suppression list options for the configuration set.
    type: dict
    suboptions:
      suppressed_reasons:
        description:
          - List of reasons for which emails should be suppressed.
          - Valid values are BOUNCE and COMPLAINT.
        type: list
        elements: str
  tracking_options:
    description:
      - Tracking options for the configuration set.
    type: dict
    suboptions:
      custom_redirect_domain:
        description:
          - Custom domain to use for open and click tracking.
        type: str
        required: true
      https_policy:
        description:
          - HTTPS policy for tracking links.
          - C(REQUIRE) - HTTPS will be used for both open and click tracking links.
          - C(OPTIONAL) - Open tracking links will use HTTP and click tracking links will use the protocol of the link.
          - C(REQUIRE_OPEN_ONLY) - HTTPS will be used for open tracking links and click tracking links will use the protocol of the link.
        type: str
        choices: [REQUIRE, OPTIONAL, REQUIRE_OPEN_ONLY]
  vdm_options:
    description:
      - Virtual Deliverability Manager options for the configuration set.
    type: dict
    suboptions:
      dashboard_options:
        description:
          - Dashboard options for VDM.
        type: dict
        suboptions:
          engagement_metrics:
            description:
              - Whether engagement metrics are enabled.
            type: bool
      guardian_options:
        description:
          - Guardian options for VDM.
        type: dict
        suboptions:
          optimized_shared_delivery:
            description:
              - Whether optimized shared delivery is enabled.
            type: bool
  archiving_options:
    description:
      - MailManager archiving options for the configuration set.
    type: dict
    suboptions:
      archive_arn:
        description:
          - ARN of the MailManager archive.
        type: str
        required: true
  event_destinations:
    description:
      - List of event destinations for this configuration set.
      - Each destination can send events to CloudWatch, Kinesis Firehose, or SNS.
    type: list
    elements: dict
    suboptions:
      name:
        description:
          - Name of the event destination.
        required: true
        type: str
      enabled:
        description:
          - Whether the event destination is enabled.
        type: bool
        default: true
      matching_event_types:
        description:
          - List of event types to match.
          - Valid values are send, reject, bounce, complaint, delivery, open, click, renderingFailure, deliveryDelay, subscription.
          - Event types are case-insensitive and will be automatically converted to the required format.
        type: list
        elements: str
        required: true
      cloudwatch_destination:
        description:
          - CloudWatch destination configuration.
        type: dict
        suboptions:
          dimension_configurations:
            description:
              - List of dimension configurations for CloudWatch.
            type: list
            elements: dict
            required: true
            suboptions:
              dimension_name:
                description:
                  - Name of the dimension.
                type: str
                required: true
              dimension_value_source:
                description:
                  - Source of the dimension value (messageTag, emailHeader, linkTag).
                type: str
                required: true
                choices: [messageTag, emailHeader, linkTag]
              default_dimension_value:
                description:
                  - Default value for the dimension.
                type: str
                required: true
      kinesis_firehose_destination:
        description:
          - Kinesis Firehose destination configuration.
        type: dict
        suboptions:
          delivery_stream_arn:
            description:
              - ARN of the Kinesis Firehose delivery stream.
            type: str
            required: true
          iam_role_arn:
            description:
              - ARN of the IAM role for SES to assume.
            type: str
            required: true
      sns_destination:
        description:
          - SNS destination configuration.
        type: dict
        suboptions:
          topic_arn:
            description:
              - ARN of the SNS topic.
            type: str
            required: true

extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
- name: Create an SES configuration set with basic options
  ses_configuration_set:
    name: my-config-set
    state: present

- name: Create an SES configuration set with all options
  ses_configuration_set:
    name: my-config-set
    state: present
    delivery_options:
      tls_policy: true
      sending_pool_name: my-dedicated-pool
    tracking_options:
      custom_redirect_domain: track.example.com
      https_policy: REQUIRE_OPEN_ONLY
    reputation_options:
      reputation_metrics_enabled: true
    sending_options:
      sending_enabled: true
    suppression_options:
      suppressed_reasons:
        - BOUNCE
        - COMPLAINT
    vdm_options:
      dashboard_options:
        engagement_metrics: true
      guardian_options:
        optimized_shared_delivery: true
    archiving_options:
      archive_arn: "arn:aws:ses:us-east-1:123456789012:archive/my-archive"

- name: Create an SES configuration set with different HTTPS policies
  ses_configuration_set:
    name: my-config-set-optional
    state: present
    tracking_options:
      custom_redirect_domain: track.example.com
      https_policy: OPTIONAL  # HTTP for open tracking, click tracking uses link protocol

- name: Create an SES configuration set with CloudWatch event destination
  ses_configuration_set:
    name: my-config-set
    state: present
    event_destinations:
      - name: cloudwatch-destination
        enabled: true
        matching_event_types:
          - send
          - bounce
          - complaint
        cloudwatch_destination:
          dimension_configurations:
            - dimension_name: ses:configuration-set
              dimension_value_source: messageTag
              default_dimension_value: my-config-set

- name: Create an SES configuration set with Kinesis Firehose event destination
  ses_configuration_set:
    name: my-config-set
    state: present
    event_destinations:
      - name: firehose-destination
        enabled: true
        matching_event_types:
          - send
          - delivery
          - open
          - click
        kinesis_firehose_destination:
          delivery_stream_arn: "arn:aws:firehose:us-east-1:123456789012:deliverystream/ses-events"
          iam_role_arn: "arn:aws:iam::123456789012:role/ses-firehose-role"

- name: Create an SES configuration set with SNS event destination
  ses_configuration_set:
    name: my-config-set
    state: present
    event_destinations:
      - name: sns-destination
        enabled: true
        matching_event_types:
          - bounce
          - complaint
        sns_destination:
          topic_arn: "arn:aws:sns:us-east-1:123456789012:ses-events"

- name: Create an SES configuration set with multiple event destinations
  ses_configuration_set:
    name: my-config-set
    state: present
    event_destinations:
      - name: cloudwatch-metrics
        enabled: true
        matching_event_types:
          - send
          - bounce
          - complaint
          - delivery
        cloudwatch_destination:
          dimension_configurations:
            - dimension_name: ses:configuration-set
              dimension_value_source: messageTag
              default_dimension_value: my-config-set
      - name: sns-notifications
        enabled: true
        matching_event_types:
          - bounce
          - complaint
        sns_destination:
          topic_arn: "arn:aws:sns:us-east-1:123456789012:ses-events"

- name: Remove an SES configuration set
  ses_configuration_set:
    name: my-config-set
    state: absent
"""

RETURN = r"""
changed:
  description: Whether a change occurred.
  type: bool
  returned: always
msg:
  description: Operation result message.
  type: str
  returned: always
configuration_set:
  description: Details of the SES configuration set.
  type: dict
  returned: when state=present
  contains:
    name:
      description: Name of the configuration set.
      type: str
      returned: always
    event_destinations:
      description: List of event destinations.
      type: list
      returned: always
"""

from ansible_collections.amazon.aws.plugins.module_utils.retries import AWSRetry

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule

try:
    from botocore.exceptions import BotoCoreError
    from botocore.exceptions import ClientError
except ImportError:
    pass  # Handled by AnsibleAWSModule


def get_configuration_set(client, name):
    """Get configuration set or None if it doesn't exist."""
    try:
        response = client.get_configuration_set(ConfigurationSetName=name)
        return response
    except ClientError as e:
        if e.response["Error"]["Code"] == "NotFoundException":
            return None
        raise


def create_configuration_set(client, module, name):
    """Create a new SES configuration set."""
    if module.check_mode:
        return True

    try:
        client.create_configuration_set(ConfigurationSetName=name)
        return True
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg=f"Failed to create configuration set {name}")


def delete_configuration_set(client, module, name):
    """Delete an SES configuration set."""
    if module.check_mode:
        return True

    try:
        client.delete_configuration_set(ConfigurationSetName=name)
        return True
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg=f"Failed to delete configuration set {name}")


def update_configuration_set_delivery_options(client, module, name, delivery_options):
    """Update delivery options for a configuration set."""
    if module.check_mode:
        return True

    try:
        params = {"ConfigurationSetName": name}
        if delivery_options.get("tls_policy") is not None:
            # Convert boolean to AWS API format: True -> REQUIRE, False -> OPTIONAL
            params["TlsPolicy"] = "REQUIRE" if delivery_options["tls_policy"] else "OPTIONAL"
        if delivery_options.get("sending_pool_name"):
            params["SendingPoolName"] = delivery_options["sending_pool_name"]

        client.put_configuration_set_delivery_options(**params)
        return True
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg=f"Failed to update delivery options for {name}")


def update_configuration_set_reputation_options(client, module, name, reputation_options):
    """Update reputation options for a configuration set."""
    if module.check_mode:
        return True

    try:
        if reputation_options.get("reputation_metrics_enabled") is not None:
            client.put_configuration_set_reputation_options(
                ConfigurationSetName=name,
                ReputationMetricsEnabled=reputation_options["reputation_metrics_enabled"],
            )
        return True
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg=f"Failed to update reputation options for {name}")


def update_configuration_set_sending_options(client, module, name, sending_options):
    """Update sending options for a configuration set."""
    if module.check_mode:
        return True

    try:
        if sending_options.get("sending_enabled") is not None:
            client.put_configuration_set_sending_options(
                ConfigurationSetName=name, SendingEnabled=sending_options["sending_enabled"]
            )
        return True
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg=f"Failed to update sending options for {name}")


def update_configuration_set_suppression_options(client, module, name, suppression_options):
    """Update suppression options for a configuration set."""
    if module.check_mode:
        return True

    try:
        if suppression_options.get("suppressed_reasons"):
            client.put_configuration_set_suppression_options(
                ConfigurationSetName=name, SuppressedReasons=suppression_options["suppressed_reasons"]
            )
        return True
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg=f"Failed to update suppression options for {name}")


def update_configuration_set_tracking_options(client, module, name, tracking_options):
    """Update tracking options for a configuration set."""
    if module.check_mode:
        return True

    try:
        if tracking_options.get("custom_redirect_domain"):
            params = {
                "ConfigurationSetName": name,
                "CustomRedirectDomain": tracking_options["custom_redirect_domain"],
            }
            if tracking_options.get("https_policy"):
                params["HttpsPolicy"] = tracking_options["https_policy"]

            client.put_configuration_set_tracking_options(**params)
        return True
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg=f"Failed to update tracking options for {name}")


def update_configuration_set_vdm_options(client, module, name, vdm_options):
    """Update VDM options for a configuration set."""
    if module.check_mode:
        return True

    try:
        params = {"ConfigurationSetName": name, "VdmOptions": {}}

        if vdm_options.get("dashboard_options"):
            dashboard = vdm_options["dashboard_options"]
            if dashboard.get("engagement_metrics") is not None:
                params["VdmOptions"]["DashboardOptions"] = {
                    "EngagementMetrics": "ENABLED" if dashboard["engagement_metrics"] else "DISABLED"
                }

        if vdm_options.get("guardian_options"):
            guardian = vdm_options["guardian_options"]
            if guardian.get("optimized_shared_delivery") is not None:
                params["VdmOptions"]["GuardianOptions"] = {
                    "OptimizedSharedDelivery": "ENABLED" if guardian["optimized_shared_delivery"] else "DISABLED"
                }

        if params["VdmOptions"]:
            client.put_configuration_set_vdm_options(**params)
        return True
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg=f"Failed to update VDM options for {name}")


def update_configuration_set_archiving_options(client, module, name, archiving_options):
    """Update archiving options for a configuration set."""
    if module.check_mode:
        return True

    try:
        if archiving_options.get("archive_arn"):
            client.put_configuration_set_archiving_options(
                ConfigurationSetName=name, ArchiveArn=archiving_options["archive_arn"]
            )
        return True
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg=f"Failed to update archiving options for {name}")


def get_event_destinations(client, module, config_set_name):
    """Get event destinations for a configuration set."""
    try:
        response = client.get_configuration_set_event_destinations(ConfigurationSetName=config_set_name)
        return response.get("EventDestinations", [])
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg=f"Failed to get event destinations for {config_set_name}")


def create_event_destination(client, module, config_set_name, destination):
    """Create an event destination."""
    if module.check_mode:
        return True

    try:
        # Convert event types to uppercase as required by SES v2 API
        matching_event_types = [
            event_type.upper().replace("RENDERINGFAILURE", "RENDERING_FAILURE")
            for event_type in destination["matching_event_types"]
        ]

        event_destination_config = {
            "Enabled": destination.get("enabled", True),
            "MatchingEventTypes": matching_event_types,
        }

        # Add CloudWatch destination if specified
        if "cloudwatch_destination" in destination and destination["cloudwatch_destination"] is not None:
            cw_dest = destination["cloudwatch_destination"]
            if cw_dest.get("dimension_configurations"):
                event_destination_config["CloudWatchDestination"] = {
                    "DimensionConfigurations": [
                        {
                            "DimensionName": dim["dimension_name"],
                            "DimensionValueSource": dim["dimension_value_source"],
                            "DefaultDimensionValue": dim["default_dimension_value"],
                        }
                        for dim in cw_dest["dimension_configurations"]
                    ]
                }

        # Add Kinesis Firehose destination if specified
        if "kinesis_firehose_destination" in destination and destination["kinesis_firehose_destination"] is not None:
            kf_dest = destination["kinesis_firehose_destination"]
            if kf_dest.get("delivery_stream_arn") and kf_dest.get("iam_role_arn"):
                event_destination_config["KinesisFirehoseDestination"] = {
                    "DeliveryStreamArn": kf_dest["delivery_stream_arn"],
                    "IamRoleArn": kf_dest["iam_role_arn"],
                }

        # Add SNS destination if specified
        if "sns_destination" in destination and destination["sns_destination"] is not None:
            sns_dest = destination["sns_destination"]
            if sns_dest.get("topic_arn"):
                event_destination_config["SnsDestination"] = {"TopicArn": sns_dest["topic_arn"]}

        client.create_configuration_set_event_destination(
            ConfigurationSetName=config_set_name,
            EventDestinationName=destination["name"],
            EventDestination=event_destination_config,
        )
        return True
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg=f"Failed to create event destination {destination['name']}")


def update_event_destination(client, module, config_set_name, destination):
    """Update an event destination."""
    if module.check_mode:
        return True

    try:
        # Convert event types to uppercase as required by SES v2 API
        matching_event_types = [
            event_type.upper().replace("RENDERINGFAILURE", "RENDERING_FAILURE")
            for event_type in destination["matching_event_types"]
        ]

        event_destination_config = {
            "Enabled": destination.get("enabled", True),
            "MatchingEventTypes": matching_event_types,
        }

        # Add CloudWatch destination if specified
        if "cloudwatch_destination" in destination and destination["cloudwatch_destination"] is not None:
            cw_dest = destination["cloudwatch_destination"]
            if cw_dest.get("dimension_configurations"):
                event_destination_config["CloudWatchDestination"] = {
                    "DimensionConfigurations": [
                        {
                            "DimensionName": dim["dimension_name"],
                            "DimensionValueSource": dim["dimension_value_source"],
                            "DefaultDimensionValue": dim["default_dimension_value"],
                        }
                        for dim in cw_dest["dimension_configurations"]
                    ]
                }

        # Add Kinesis Firehose destination if specified
        if "kinesis_firehose_destination" in destination and destination["kinesis_firehose_destination"] is not None:
            kf_dest = destination["kinesis_firehose_destination"]
            if kf_dest.get("delivery_stream_arn") and kf_dest.get("iam_role_arn"):
                event_destination_config["KinesisFirehoseDestination"] = {
                    "DeliveryStreamArn": kf_dest["delivery_stream_arn"],
                    "IamRoleArn": kf_dest["iam_role_arn"],
                }

        # Add SNS destination if specified
        if "sns_destination" in destination and destination["sns_destination"] is not None:
            sns_dest = destination["sns_destination"]
            if sns_dest.get("topic_arn"):
                event_destination_config["SnsDestination"] = {"TopicArn": sns_dest["topic_arn"]}

        client.update_configuration_set_event_destination(
            ConfigurationSetName=config_set_name,
            EventDestinationName=destination["name"],
            EventDestination=event_destination_config,
        )
        return True
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg=f"Failed to update event destination {destination['name']}")


def delete_event_destination(client, module, config_set_name, dest_name):
    """Delete an event destination."""
    if module.check_mode:
        return True

    try:
        client.delete_configuration_set_event_destination(
            ConfigurationSetName=config_set_name, EventDestinationName=dest_name
        )
        return True
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg=f"Failed to delete event destination {dest_name}")


def normalize_event_destination(dest):
    """Normalize event destination for comparison."""
    # Convert event types to lowercase and handle RENDERING_FAILURE
    event_types = [
        event_type.lower().replace("rendering_failure", "renderingfailure")
        for event_type in dest.get("MatchingEventTypes", [])
    ]

    normalized = {
        "name": dest.get("Name"),
        "enabled": dest.get("Enabled", True),
        "matching_event_types": sorted(event_types),
    }

    if "CloudWatchDestination" in dest:
        cw_dest = dest["CloudWatchDestination"]
        normalized["cloudwatch_destination"] = {
            "dimension_configurations": sorted(
                [
                    {
                        "dimension_name": dim["DimensionName"],
                        "dimension_value_source": dim["DimensionValueSource"],
                        "default_dimension_value": dim["DefaultDimensionValue"],
                    }
                    for dim in cw_dest.get("DimensionConfigurations", [])
                ],
                key=lambda x: x["dimension_name"],
            )
        }

    if "KinesisFirehoseDestination" in dest:
        kf_dest = dest["KinesisFirehoseDestination"]
        normalized["kinesis_firehose_destination"] = {
            "delivery_stream_arn": kf_dest["DeliveryStreamArn"],
            "iam_role_arn": kf_dest["IamRoleArn"],
        }

    if "SnsDestination" in dest:
        sns_dest = dest["SnsDestination"]
        normalized["sns_destination"] = {"topic_arn": sns_dest["TopicArn"]}

    return normalized


def normalize_desired_destination(dest):
    """Normalize desired event destination for comparison."""
    normalized = {
        "name": dest["name"],
        "enabled": dest.get("enabled", True),
        "matching_event_types": sorted(dest["matching_event_types"]),
    }

    if "cloudwatch_destination" in dest and dest["cloudwatch_destination"] is not None:
        cw_dest = dest["cloudwatch_destination"]
        if cw_dest.get("dimension_configurations"):
            normalized["cloudwatch_destination"] = {
                "dimension_configurations": sorted(
                    cw_dest["dimension_configurations"], key=lambda x: x["dimension_name"]
                )
            }

    if "kinesis_firehose_destination" in dest and dest["kinesis_firehose_destination"] is not None:
        normalized["kinesis_firehose_destination"] = dest["kinesis_firehose_destination"]

    if "sns_destination" in dest and dest["sns_destination"] is not None:
        normalized["sns_destination"] = dest["sns_destination"]

    return normalized


def event_destinations_equal(existing, desired):
    """Compare existing and desired event destinations."""
    existing_norm = normalize_event_destination(existing)
    desired_norm = normalize_desired_destination(desired)

    # Compare all fields except name
    for key in [
        "enabled",
        "matching_event_types",
        "cloudwatch_destination",
        "kinesis_firehose_destination",
        "sns_destination",
    ]:
        if existing_norm.get(key) != desired_norm.get(key):
            return False

    return True


def main():
    argument_spec = dict(
        name=dict(required=True, type="str"),
        state=dict(default="present", choices=["present", "absent"]),
        delivery_options=dict(
            type="dict",
            options=dict(
                tls_policy=dict(type="bool"),
                sending_pool_name=dict(type="str"),
            ),
        ),
        reputation_options=dict(
            type="dict",
            options=dict(
                reputation_metrics_enabled=dict(type="bool"),
            ),
        ),
        sending_options=dict(
            type="dict",
            options=dict(
                sending_enabled=dict(type="bool"),
            ),
        ),
        suppression_options=dict(
            type="dict",
            options=dict(
                suppressed_reasons=dict(type="list", elements="str"),
            ),
        ),
        tracking_options=dict(
            type="dict",
            options=dict(
                custom_redirect_domain=dict(required=True, type="str"),
                https_policy=dict(type="str", choices=["REQUIRE", "OPTIONAL", "REQUIRE_OPEN_ONLY"]),
            ),
        ),
        vdm_options=dict(
            type="dict",
            options=dict(
                dashboard_options=dict(
                    type="dict",
                    options=dict(
                        engagement_metrics=dict(type="bool"),
                    ),
                ),
                guardian_options=dict(
                    type="dict",
                    options=dict(
                        optimized_shared_delivery=dict(type="bool"),
                    ),
                ),
            ),
        ),
        archiving_options=dict(
            type="dict",
            options=dict(
                archive_arn=dict(required=True, type="str"),
            ),
        ),
        event_destinations=dict(
            type="list",
            elements="dict",
            options=dict(
                name=dict(required=True, type="str"),
                enabled=dict(type="bool", default=True),
                matching_event_types=dict(required=True, type="list", elements="str"),
                cloudwatch_destination=dict(
                    type="dict",
                    options=dict(
                        dimension_configurations=dict(
                            required=True,
                            type="list",
                            elements="dict",
                            options=dict(
                                dimension_name=dict(required=True, type="str"),
                                dimension_value_source=dict(
                                    required=True,
                                    type="str",
                                    choices=["messageTag", "emailHeader", "linkTag"],
                                ),
                                default_dimension_value=dict(required=True, type="str"),
                            ),
                        )
                    ),
                ),
                kinesis_firehose_destination=dict(
                    type="dict",
                    options=dict(
                        delivery_stream_arn=dict(required=True, type="str"),
                        iam_role_arn=dict(required=True, type="str"),
                    ),
                ),
                sns_destination=dict(type="dict", options=dict(topic_arn=dict(required=True, type="str"))),
            ),
        ),
    )

    module = AnsibleAWSModule(argument_spec=argument_spec, supports_check_mode=True)

    name = module.params["name"]
    state = module.params["state"]
    archiving_options = module.params.get("archiving_options")
    delivery_options = module.params.get("delivery_options")
    reputation_options = module.params.get("reputation_options")
    sending_options = module.params.get("sending_options")
    suppression_options = module.params.get("suppression_options")
    tracking_options = module.params.get("tracking_options")
    vdm_options = module.params.get("vdm_options")
    desired_destinations = module.params.get("event_destinations") or []

    # Use module.client() to properly handle AWS credentials and config
    try:
        client = module.client("sesv2", retry_decorator=AWSRetry.jittered_backoff())
    except (BotoCoreError, ClientError) as e:
        module.fail_json_aws(e, msg="Failed to connect to AWS")

    changed = False
    msg = ""

    # Get current configuration set state
    current = get_configuration_set(client, name)

    # Handle absent state
    if state == "absent":
        if not current:
            module.exit_json(changed=False, msg="Configuration set does not exist")

        changed = delete_configuration_set(client, module, name)
        module.exit_json(changed=changed, msg="Configuration set deleted")

    # Handle creation
    if not current:
        changed = create_configuration_set(client, module, name)
        msg = "Configuration set created"

        # Update configuration set options
        if delivery_options:
            if update_configuration_set_delivery_options(client, module, name, delivery_options):
                changed = True

        if reputation_options:
            if update_configuration_set_reputation_options(client, module, name, reputation_options):
                changed = True

        if sending_options:
            if update_configuration_set_sending_options(client, module, name, sending_options):
                changed = True

        if suppression_options:
            if update_configuration_set_suppression_options(client, module, name, suppression_options):
                changed = True

        if tracking_options:
            if update_configuration_set_tracking_options(client, module, name, tracking_options):
                changed = True

        if vdm_options:
            if update_configuration_set_vdm_options(client, module, name, vdm_options):
                changed = True

        if archiving_options:
            if update_configuration_set_archiving_options(client, module, name, archiving_options):
                changed = True

        # Create event destinations
        for destination in desired_destinations:
            if create_event_destination(client, module, name, destination):
                changed = True

        if desired_destinations:
            msg = "Configuration set created with event destinations"

        result = {"changed": changed, "msg": msg}
        if not module.check_mode:
            event_destinations = get_event_destinations(client, module, name)
            result["configuration_set"] = {"name": name, "event_destinations": event_destinations}
        module.exit_json(**result)

    # Configuration set exists - update options
    if delivery_options:
        if update_configuration_set_delivery_options(client, module, name, delivery_options):
            changed = True
            msg = "Configuration set options updated"

    if reputation_options:
        if update_configuration_set_reputation_options(client, module, name, reputation_options):
            changed = True
            msg = "Configuration set options updated"

    if sending_options:
        if update_configuration_set_sending_options(client, module, name, sending_options):
            changed = True
            msg = "Configuration set options updated"

    if suppression_options:
        if update_configuration_set_suppression_options(client, module, name, suppression_options):
            changed = True
            msg = "Configuration set options updated"

    if tracking_options:
        if update_configuration_set_tracking_options(client, module, name, tracking_options):
            changed = True
            msg = "Configuration set options updated"

    if vdm_options:
        if update_configuration_set_vdm_options(client, module, name, vdm_options):
            changed = True
            msg = "Configuration set options updated"

    if archiving_options:
        if update_configuration_set_archiving_options(client, module, name, archiving_options):
            changed = True
            msg = "Configuration set options updated"

    # Configuration set exists - manage event destinations
    existing_destinations = get_event_destinations(client, module, name)
    existing_dest_names = {dest["Name"] for dest in existing_destinations}
    desired_dest_names = {dest["name"] for dest in desired_destinations}

    # Delete destinations that shouldn't exist
    for dest_name in existing_dest_names - desired_dest_names:
        if delete_event_destination(client, module, name, dest_name):
            changed = True
            msg = "Event destinations updated"

    # Create or update destinations
    for desired_dest in desired_destinations:
        dest_name = desired_dest["name"]
        existing_dest = next((d for d in existing_destinations if d["Name"] == dest_name), None)

        if existing_dest is None:
            # Create new destination
            if create_event_destination(client, module, name, desired_dest):
                changed = True
                msg = "Event destinations updated"
        else:
            # Update if changed
            if not event_destinations_equal(existing_dest, desired_dest):
                if update_event_destination(client, module, name, desired_dest):
                    changed = True
                    msg = "Event destinations updated"

    if not msg:
        msg = "Configuration set is up to date"

    result = {"changed": changed, "msg": msg}

    if not module.check_mode:
        event_destinations = get_event_destinations(client, module, name)
        result["configuration_set"] = {"name": name, "event_destinations": event_destinations}

    module.exit_json(**result)


if __name__ == "__main__":
    main()
