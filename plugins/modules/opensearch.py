#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = """
---
module: opensearch
short_description: Creates OpenSearch or ElasticSearch domain.
description:
  - Creates a new Amazon OpenSearch Service domain.
version_added: "2.1"
options:
  domain_name:
    description:
      - The name of the Amazon OpenSearch/ElasticSearch Service domain.
        Domain names are unique across the domains owned by an account within an AWS region.
    required: true
    type: str
  engine_type:
    description:
      - The engine type to use. "ElasticSearch" | "OpenSearch"
    required: false
    type: str
    choices: ['OpenSearch', 'Elasticsearch']    
    default: OpenSearch
  version:
    description:
      - The version of ElasticSearch or OpenSearch to deploy.
    required: false
    type: str
    default: "1.1"
  instance_type:
    description:
      - Type of the instances to use for the domain.
    required: false
    type: str
    default: t2.small.search
  instance_count:
    description:
      - Number of instances for the domain.
    required: true
    type: int
  dedicated_master:
    description:
      - A boolean value to indicate whether a dedicated master node is enabled.
    required: true
    type: bool
  zone_awareness:
    description:
      - A boolean value to indicate whether zone awareness is enabled.
    required: true
    type: bool
  availability_zone_count:
    description: An integer value to indicate the number of availability zones for a domain when zone awareness is enabled.
      This should be equal to number of subnets if VPC endpoints is enabled.
    required: false
    type: int
  ebs:
    description:
      - Specifies whether EBS-based storage is enabled.
    required: true
    type: bool
  warm_enabled:
    description: True to enable UltraWarm storage.
    required: false
    type: bool
    default: false
  warm_type:
    description: The instance type for the OpenSearch domain's warm nodes.
    required: false
    type: str
  warm_count:
    description: The number of UltraWarm nodes in the domain.
    required: false
    type: int
  cold_storage_enabled:
    description: True to enable cold storage. Elasticsearch 7.9 or above.
    required: false
    type: bool
  dedicated_master_instance_type:
    description:
      - The instance type for a dedicated master node.
    required: false
    type: str
  dedicated_master_instance_count:
    description:
      - Total number of dedicated master nodes, active and on standby, for the domain.
    required: false
    type: int
  volume_type:
    description:
      - Specifies the volume type for EBS-based storage. "standard"|"gp2"|"io1"
    required: true
    type: str
  volume_size:
    description:
      - Integer to specify the size of an EBS volume.
    required: true
    type: int
  iops:
    description:
      - The IOPD for a Provisioned IOPS EBS volume (SSD).
    required: false
    type: int
  vpc_subnets:
    description:
      - Specifies the subnet ids for VPC endpoint.
    required: false
    type: list
  vpc_security_groups:
    description:
      - Specifies the security group ids for VPC endpoint.
    required: false
    type: list
  snapshot_hour:
    description:
      - Integer value from 0 to 23 specifying when the service takes a daily automated snapshot of the specified Elasticsearch domain.
    required: false
    type: int
    default: 0
  access_policies:
    description:
      - IAM access policy as a JSON-formatted string.
    required: true
    type: dict
  encryption_at_rest_enabled:
    description:
      - Should data be encrypted while at rest.
    required: false
    type: bool
  encryption_at_rest_kms_key_id:
    description:
      - If encryption_at_rest_enabled is True, this identifies the encryption key to use 
    required: false
    type: str
  cognito_enabled:
    description:
      - The option to enable Cognito for OpenSearch Dashboards authentication.
    required: false
    type: bool
    default: false
  cognito_user_pool_id:
    description:
      - The Cognito user pool ID for OpenSearch Dashboards authentication.
    required: false
    type: str
  cognito_identity_pool_id:
    description:
      - The Cognito identity pool ID for OpenSearch Dashboards authentication.
    required: false
    type: str
  cognito_role_arn:
    description:
      - The role ARN that provides OpenSearch permissions for accessing Cognito resources.
    required: false
    type: str
  domain_endpoint_options:
    description:
      - Options to specify configuration that will be applied to the domain endpoint.
    suboptions:
      enforce_https:
        description:
          - Whether only HTTPS endpoint should be enabled for the domain.
        type: bool
      tls_security_policy:
        description:
          - Specify the TLS security policy to apply to the HTTPS endpoint of the domain.
        type: str
      custom_endpoint_enabled:
        description:
          - Whether to enable a custom endpoint for the domain.
        type: bool
      custom_endpoint:
        description:
          - The fully qualified domain for your custom endpoint.
        type: str
      custom_endpoint_certificate_arn:
        description:
          - The ACM certificate ARN for your custom endpoint.
        type: str
    type: dict
  advanced_security_options:
    description:
      - Specifies advanced security options.
    suboptions:
      enabled:
        description:
          - True if advanced security is enabled.
        type: bool
      internal_user_database_enabled:
        description:
          - True if the internal user database is enabled.
        type: bool
      master_user_options:
        description:
          - Credentials for the master user: username and password, ARN, or both.
        suboptions:
          master_user_arn:
            description:
              - ARN for the master user (if IAM is enabled).
            type: str
          master_user_name:
            description:
              - The master user's username, which is stored in the Amazon OpenSearch Service domain's internal database.
            type: str
          master_user_password:
            description:
              - The master user's password, which is stored in the Amazon OpenSearch Service domain's internal database.
            type: str
        type: dict
      saml_options:
        description:
          - The SAML application configuration for the domain.
        subptions:
          enabled:
            description:
              - True if SAML is enabled.
            type: bool
          idp:
            description:
              - The SAML Identity Provider's information.
            suboptions:
              metadata_content:
                description:
                  - The metadata of the SAML application in XML format.
                type: str
              entity_id:
                description:
                  - The unique entity ID of the application in SAML identity provider.
                type: str
            type: dict
          master_user_name:
            description:
              - The SAML master username, which is stored in the Amazon OpenSearch Service domain's internal database.
            type: str
          master_backend_role:
            description:
              - The backend role that the SAML master user is mapped to.
            type: str
          subject_key:
            description:
              - Element of the SAML assertion to use for username. Default is NameID.
            type: str
          roles_key:
            description:
              - Element of the SAML assertion to use for backend roles. Default is roles.
            type: str
          session_timeout_minutes:
            description:
              - The duration, in minutes, after which a user session becomes inactive. Acceptable values are between 1 and 1440, and the default value is 60.
            type: int
        type: dict
    type: dict
  auto_tune_options:
    description:
      - Specifies Auto-Tune options.
    suboptions:
      desired_state:
        description:
          - The Auto-Tune desired state. Valid values are ENABLED and DISABLED.
        type: str
        choices: ['ENABLED', 'DISABLED']    
      maintenance_schedules:  
        description:
          - A list of maintenance schedules.
        suboptions:
          start_at:
            description:
              - The timestamp at which the Auto-Tune maintenance schedule starts.
            type: str
          duration:
            suboptions:
              value:
                description:
                  - Integer to specify the value of a maintenance schedule duration.
                type: int
              unit:
                description:
                  - The unit of a maintenance schedule duration. Valid value is HOURS.
                choices: ['HOURS'] 
                type: str
          cron_expression_for_recurrence:
            description:
              - A cron expression for a recurring maintenance schedule.
            type: str
        type: list
        elements: dict
        default: []
    type: dict
  wait:
    description:
      - Whether or not to wait for snapshot creation or deletion.
    type: bool
    default: 'no'
  wait_timeout:
    description:
      - how long before wait gives up, in seconds.
    default: 300
    type: int
  tags:
    description:
      - tags dict to apply to a snapshot.
    type: dict
  purge_tags:
    description:
      - whether to remove tags not present in the C(tags) parameter.
    default: True
    type: bool
author:
  - "Jose Armesto (@fiunchinho)"
  - "Sebastien Rosset (@sebastien.rosset)"
extends_documentation_fragment:
- amazon.aws.aws
- amazon.aws.ec2
"""

EXAMPLES = """

- name: Create OpenSearch domain
  community.aws.opensearch:
    domain_name: "my-domain"
    engine_type: OpenSearch
    version: "1.1"
    instance_type: "m3.medium.search"
    instance_count: 2
    dedicated_master: True
    zone_awareness: True
    availability_zone_count: 2
    dedicated_master_instance_type: "t2.micro.search"
    dedicated_master_instance_count: 2
    ebs: True
    volume_type: "io1"
    volume_size: 10
    iops: 1000
    warm_enabled: true
    warm_type: "ultrawarm1.medium.search"
    warm_count: 1
    cold_storage_enabled: false
    vpc_subnets:
      - "subnet-e537d64a"
      - "subnet-e537d64b"
    vpc_security_groups:
      - "sg-dd2f13cb"
      - "sg-dd2f13cc"
    snapshot_hour: 13
    access_policies: "{{ lookup('file', 'policy.json') | from_json }}"
    encryption_at_rest_enabled: false
    auto_tune_options:
      desired_state: "ENABLED"
      maintenance_schedules:
      - start_at: "2025-01-12"
        duration:
          value: 1
          unit: "HOURS"
        cron_expression_for_recurrence: "cron(0 12 * * ? *)"
      - start_at: "2032-01-12"
        duration:
          value: 2
          unit: "HOURS"
        cron_expression_for_recurrence: "cron(0 12 * * ? *)"
    tags:
      Environment: Development
      Application: foo
    wait: true

"""

import json
import time

try:
    import botocore
except ImportError:
    pass  # handled by AnsibleAWSModule

from ansible.module_utils.six import string_types

# import module snippets
from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import (
    camel_dict_to_snake_dict,
    AWSRetry,
    compare_aws_tags,
)
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import (
    boto3_tag_list_to_ansible_dict,
    ansible_dict_to_boto3_tag_list,
)


def get_domain(client, module, domain_name):
    try:
        response = client.describe_domain(DomainName=domain_name)
    except client.exceptions.ResourceNotFoundException:
        return None
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        module.fail_json_aws(e, msg="Couldn't get domain {0}".format(domain_name))
    return response["DomainStatus"]


def get_domain_config(client, module, domain_name):
    try:
        response = client.describe_domain_config(DomainName=domain_name)
    except client.exceptions.ResourceNotFoundException:
        return None
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        module.fail_json_aws(e, msg="Couldn't get domain {0}".format(domain_name))
    return response["DomainConfig"]


def domain_to_facts(client, module, domain):
    try:
        domain["Tags"] = boto3_tag_list_to_ansible_dict(
            client.list_tags(ARN=domain["ARN"], aws_retry=True)["TagList"]
        )
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(
            e, "Couldn't get tags for domain %s" % domain["domain_name"]
        )
    except KeyError:
        module.fail_json(msg=str(domain))

    return camel_dict_to_snake_dict(domain, ignore_list=["Tags"])


def wait_for_domain_status(client, module, domain_name, waiter_name):
    if not module.params["wait"]:
        return
    timeout = module.params["wait_timeout"]
    deadline = time.time() + timeout
    while time.time() < deadline:
        status = get_domain(client, module, domain_name)
        if status is None:
            if waiter_name == "domain_deleted":
                return
        else:
            if (
                waiter_name == "domain_available"
                and status["Created"]
                and not status["Processing"]
                and not status["UpgradeProcessing"]
            ):
                return
        time.sleep(15)


def ensure_domain_absent(client, module):
    domain_name = module.params.get("domain_name")
    changed = False

    domain = get_domain(client, module, domain_name)
    try:
        client.delete_domain(DomainName=domain_name)
        changed = True
    except (
        botocore.exceptions.ClientError,
        botocore.exceptions.BotoCoreError,
    ) as e:
        module.fail_json_aws(e, msg="trying to delete domain")

    # If we're not waiting for a delete to complete then we're all done
    # so just return
    if not domain or not module.params.get("wait"):
        return dict(changed=changed)
    try:
        wait_for_domain_status(client, module, domain_name, "domain_deleted")
        return dict(changed=changed)
    except client.exceptions.ResourceNotFoundException:
        return dict(changed=changed)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, "awaiting domain deletion")


def ensure_tags(client, module, resource_arn, existing_tags, tags, purge_tags):
    if tags is None:
        return False
    tags_to_add, tags_to_remove = compare_aws_tags(existing_tags, tags, purge_tags)
    changed = bool(tags_to_add or tags_to_remove)
    if tags_to_add:
        try:
            client.add_tags(
                ARN=resource_arn,
                TagList=ansible_dict_to_boto3_tag_list(tags_to_add),
            )
        except (
            botocore.exceptions.ClientError,
            botocore.exceptions.BotoCoreError,
        ) as e:
            module.fail_json_aws(
                e, "Couldn't add tags to domain {0}".format(resource_arn)
            )
    if tags_to_remove:
        try:
            client.remove_tags(ARN=resource_arn, TagKeys=tags_to_remove)
        except (
            botocore.exceptions.ClientError,
            botocore.exceptions.BotoCoreError,
        ) as e:
            module.fail_json_aws(
                e, "Couldn't remove tags from domain {0}".format(resource_arn)
            )
    return changed


def upgrade_domain(client, module, current_version, target_engine_version):
    domain_name = module.params.get("domain_name")
    parameters = {
        "DomainName": domain_name,
        "TargetVersion": target_engine_version,
        "PerformCheckOnly": False,
    }
    # If background tasks are in progress, wait until they complete.
    # This can take several hours depending on the cluster size.
    wait_for_domain_status(client, module, domain_name, "domain_available")

    try:
        client.upgrade_domain(**parameters)
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        module.fail_json_aws(
            e,
            msg="Couldn't upgrade domain {0} from {1} to {2}".format(
                domain_name, current_version, target_engine_version
            ),
        )

    if module.params.get("wait"):
        wait_for_domain_status(client, module, domain_name, "domain_available")


def ensure_domain_present(client, module):
    domain_name = module.params.get("domain_name")
    target_engine_version = "%s_%s" % (
        module.params.get("engine_type"),
        module.params.get("version"),
    )

    domain_config = {
        "InstanceType": module.params.get("instance_type"),
        "InstanceCount": int(module.params.get("instance_count")),
        "DedicatedMasterEnabled": module.params.get("dedicated_master"),
        "ZoneAwarenessEnabled": module.params.get("zone_awareness"),
        "WarmEnabled": module.params.get("warm_enabled"),
    }
    if module.params.get("cold_storage_enabled") is not None:
        domain_config["ColdStorageOptions"] = {
            "Enabled": module.params.get("cold_storage_enabled"),
        }

    if module.params.get("zone_awareness"):
        domain_config["ZoneAwarenessConfig"] = {
            "AvailabilityZoneCount": module.params.get("availability_zone_count"),
        }

    if module.params.get("warm_enabled"):
        domain_config["WarmType"] = module.params.get("warm_type")
        domain_config["WarmCount"] = module.params.get("warm_count")

    ebs_options = {"EBSEnabled": module.params.get("ebs")}

    encryption_at_rest_enabled = module.params.get("encryption_at_rest_enabled") == True
    encryption_at_rest_options = {"Enabled": encryption_at_rest_enabled}

    if encryption_at_rest_enabled:
        encryption_at_rest_options["KmsKeyId"] = module.params.get(
            "encryption_at_rest_kms_key_id"
        )

    vpc_options = {}
    vpc_subnets = module.params.get("vpc_subnets")
    if vpc_subnets:
        if isinstance(vpc_subnets, string_types):
            vpc_subnets = [x.strip() for x in vpc_subnets.split(",")]
        vpc_options["SubnetIds"] = vpc_subnets

    vpc_security_groups = module.params.get("vpc_security_groups")
    if vpc_security_groups:
        if isinstance(vpc_security_groups, string_types):
            vpc_security_groups = [x.strip() for x in vpc_security_groups.split(",")]
        vpc_options["SecurityGroupIds"] = vpc_security_groups

    if domain_config["DedicatedMasterEnabled"]:
        domain_config["DedicatedMasterType"] = module.params.get(
            "dedicated_master_instance_type"
        )
        domain_config["DedicatedMasterCount"] = module.params.get(
            "dedicated_master_instance_count"
        )

    if ebs_options["EBSEnabled"]:
        ebs_options["VolumeType"] = module.params.get("volume_type")
        ebs_options["VolumeSize"] = module.params.get("volume_size")

    if module.params.get("iops") is not None:
        ebs_options["Iops"] = module.params.get("iops")

    snapshot_options = {
        "AutomatedSnapshotStartHour": module.params.get("snapshot_hour")
    }

    cognito_options = {}
    if module.params.get("cognito_enabled"):
        cognito_options["Enabled"] = True
        cognito_options["UserPoolId"] = module.params.get("cognito_user_pool_id")
        cognito_options["IdentityPoolId"] = module.params.get(
            "cognito_identity_pool_id"
        )
        cognito_options["RoleArn"] = module.params.get("cognito_role_arn")
    else:
        cognito_options["Enabled"] = False

    auto_tune_options = {}
    opts = module.params.get("auto_tune_options")
    if opts:
        if opts.get("desired_state") is not None:
            auto_tune_options["DesiredState"] = opts.get("desired_state")
        schedules = opts.get("maintenance_schedules")
        if schedules is not None:
            auto_tune_options["MaintenanceSchedules"] = []
            for s in schedules:
                auto_tune_options["MaintenanceSchedules"].append({
                  "StartAt": s.get("start_at"),
                  "Duration": {
                    "Value": s.get("duration").get("value"),
                    "Unit": s.get("duration").get("unit"),
                  },
                  "CronExpressionForRecurrence": s.get("cron_expression_for_recurrence")
                })

    changed = False

    try:
        pdoc = json.dumps(module.params.get("access_policies"))
    except Exception as e:
        module.fail_json(
            msg="Failed to convert the policy into valid JSON: %s" % str(e)
        )

    domain = get_domain(client, module, domain_name)
    if domain is not None:
        if target_engine_version != domain["EngineVersion"]:
            changed = True
            upgrade_domain(
                client, module, domain["EngineVersion"], target_engine_version
            )

        # Modify the provided policy to provide reliable changed detection
        policy_dict = module.params.get("access_policies")
        for statement in policy_dict["Statement"]:
            if "Resource" not in statement:
                # The opensearch APIs will implicitly set this
                statement["Resource"] = "%s/*" % domain["ARN"]
                pdoc = json.dumps(policy_dict)

        if domain["ClusterConfig"] != domain_config:
            changed = True

        if domain["EBSOptions"] != ebs_options:
            changed = True

        if domain["CognitoOptions"] != cognito_options:
            changed = True

        if domain["AutoTuneOptions"] != auto_tune_options:
            changed = True

        if "VPCOptions" in domain:
            if domain["VPCOptions"]["SubnetIds"] != vpc_options["SubnetIds"]:
                changed = True
            if (
                domain["VPCOptions"]["SecurityGroupIds"]
                != vpc_options["SecurityGroupIds"]
            ):
                changed = True

        if domain["SnapshotOptions"] != snapshot_options:
            changed = True

        current_policy_dict = json.loads(domain["AccessPolicies"])
        if current_policy_dict != policy_dict:
            changed = True

        if changed:
            parameters = {
                "DomainName": module.params.get("domain_name"),
                "EncryptionAtRestOptions": encryption_at_rest_options,
                "ClusterConfig": domain_config,
                "EBSOptions": ebs_options,
                "SnapshotOptions": snapshot_options,
                "AccessPolicies": pdoc,
                "CognitoOptions": cognito_options,
                "AutoTuneOptions": auto_tune_options,
            }

            if vpc_options["SubnetIds"] or vpc_options["SecurityGroupIds"]:
                parameters["VPCOptions"] = vpc_options

            try:
                client.update_domain_config(**parameters)
            except (
                botocore.exceptions.BotoCoreError,
                botocore.exceptions.ClientError,
            ) as e:
                module.fail_json_aws(
                    e, msg="Couldn't update domain {0}".format(domain_name)
                )

    else:
        changed = True
        parameters = {
            "DomainName": module.params.get("domain_name"),
            "EngineVersion": target_engine_version,
            "EncryptionAtRestOptions": encryption_at_rest_options,
            "ClusterConfig": domain_config,
            "EBSOptions": ebs_options,
            "SnapshotOptions": snapshot_options,
            "AccessPolicies": pdoc,
            "CognitoOptions": cognito_options,
            "AutoTuneOptions": auto_tune_options,
        }

        if vpc_options["SubnetIds"] or vpc_options["SecurityGroupIds"]:
            parameters["VPCOptions"] = vpc_options

        try:
            client.create_domain(**parameters)
        except (
            botocore.exceptions.BotoCoreError,
            botocore.exceptions.ClientError,
        ) as e:
            module.fail_json_aws(
                e, msg="Couldn't update domain {0}".format(domain_name)
            )

    if module.params.get("wait"):
        wait_for_domain_status(client, module, domain_name, "domain_available")

    try:
        existing_tags = boto3_tag_list_to_ansible_dict(
            client.list_tags(ARN=domain["ARN"], aws_retry=True)["TagList"]
        )
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, "Couldn't get tags for domain %s" % domain_name)

    desired_tags = module.params["tags"]
    purge_tags = module.params["purge_tags"]
    changed |= ensure_tags(
        client, module, domain["ARN"], existing_tags, desired_tags, purge_tags
    )

    domain = get_domain(client, module, domain_name)

    return dict(changed=changed, **domain_to_facts(client, module, domain))


def main():

    domain_endpoint_options = dict(
        enforce_https=dict(type="bool"),
        tls_security_policy=dict(),
        custom_endpoint_enabled=dict(type="bool"),
        custom_endpoint=dict(),
        custom_endpoint_certificate_arn=dict(),
    )

    master_user_options = dict(
        master_user_arn=dict(),
        master_user_name=dict(),
        master_user_password=dict(),
    )
    advanced_security_options = dict(
        enabled=dict(type="bool"),
        internal_user_database_enabled=dict(type="bool"),
        master_user_options=dict(type="dict", options=master_user_options),
    )

    idp = dict(
        metadata_content=dict(),
        entity_id=dict(),
    )
    saml_options = dict(
        enabled=dict(type="bool"),
        idp=dict(type="dict", options=idp),
        master_user_name=dict(),
        master_backend_role=dict(),
        subject_key=dict(),
        roles_key=dict(),
        session_timeout_minutes=dict(type="int"),
    )

    auto_tune_duration = dict(
        value=dict(type="int"),
        unit=dict(choices=["HOURS"]),
    )
    auto_tune_maintenance_schedules = dict(
        start_at=dict(),
        duration=dict(type="dict", options=auto_tune_duration),
        cron_expression_for_recurrence=dict(),
    )
    auto_tune_options = dict(
        desired_state=dict(choices=["ENABLED", "DISABLED"]),
        maintenance_schedules=dict(
            type="list",
            default=[],
            elements="dict",
            options=auto_tune_maintenance_schedules,
        ),
    )

    module = AnsibleAWSModule(
        argument_spec=dict(
            state=dict(choices=["present", "absent"], default="present"),
            domain_name=dict(required=True),
            engine_type=dict(
                default="OpenSearch", choices=["OpenSearch", "Elasticsearch"]
            ),
            version=dict(default="1.1"),
            wait=dict(type="bool", default=False),
            wait_timeout=dict(type="int", default=300),
            instance_type=dict(default="t2.small.search"),
            instance_count=dict(required=True, type="int"),
            dedicated_master=dict(required=True, type="bool"),
            zone_awareness=dict(required=True, type="bool"),
            availability_zone_count=dict(required=False, type="int"),
            dedicated_master_instance_type=dict(),
            dedicated_master_instance_count=dict(type="int"),
            ebs=dict(required=True, type="bool"),
            volume_type=dict(required=True),
            volume_size=dict(required=True, type="int"),
            iops=dict(required=False, type="int"),
            warm_enabled=dict(required=False, type="bool", default=False),
            warm_type=dict(required=False),
            warm_count=dict(required=False, type="int"),
            cold_storage_enabled=dict(required=False, type="bool"),
            access_policies=dict(required=True, type="dict"),
            vpc_subnets=dict(type="list", elements="str", required=False),
            vpc_security_groups=dict(type="list", elements="str", required=False),
            snapshot_hour=dict(required=False, type="int", default=0),
            encryption_at_rest_enabled=dict(type="bool", default=False),
            encryption_at_rest_kms_key_id=dict(required=False),
            cognito_enabled=dict(required=False, type="bool", default=False),
            cognito_user_pool_id=dict(required=False),
            cognito_identity_pool_id=dict(required=False),
            cognito_role_arn=dict(required=False),
            domain_endpoint_options=dict(type="dict", options=domain_endpoint_options),
            advanced_security_options=dict(
                type="dict", options=advanced_security_options
            ),
            saml_options=dict(type="dict", options=saml_options),
            auto_tune_options=dict(type="dict", options=auto_tune_options),
            tags=dict(type="dict"),
            purge_tags=dict(type="bool", default=True),
        ),
        required_if=[
            ["warm_enabled", True, ["warm_type", "warm_count"]],
            ["zone_awareness", True, ["availability_zone_count"]],
            [
                "dedicated_master",
                True,
                ["dedicated_master_instance_type", "dedicated_master_instance_count"],
            ],
            ["ebs", True, ["volume_type", "volume_size"]],
            [
                "cognito_enabled",
                True,
                [
                    "cognito_user_pool_id",
                    "cognito_identity_pool_id",
                    "cognito_role_arn",
                ],
            ],
            ["encryption_at_rest_enabled", True, ["encryption_at_rest_kms_key_id"]],
        ],
    )

    try:
        client = module.client(
            "opensearch", retry_decorator=AWSRetry.jittered_backoff()
        )
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Failed to connect to AWS")

    if module.params["state"] == "absent":
        ret_dict = ensure_domain_absent(client, module)
    else:
        ret_dict = ensure_domain_present(client, module)

    module.exit_json(**ret_dict)


if __name__ == "__main__":
    main()
