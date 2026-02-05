#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2023, JIHUN KIM <jihunkimkw@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: codedeploy_deployment_group
version_added: 6.4.0
short_description: Manage deployment groups in AWS CodeDeploy
description:
  - The M(community.aws.codedeploy_deployment_group) module allows you to create, update, and delete of CodeDeploy deployment groups.
author:
  - JIHUN KIM (@shblue21)
options:
  application_name:
    description: The name of the codedeploy application.
    required: true
    type: str
  deployment_group_name:
    description: The name of the deployment group.
    required: true
    type: str
  new_deployment_group_name:
    description: The new name of the deployment group, if you want to update the deployment group name.
    required: false
    type: str
  deployment_config_name:
    description: The name of the group's deployment config (e.g. CodeDeployDefault.OneAtATime).
    required: false
    type: str
  service_role:
    description: A service role ARN that allows AWS CodeDeploy to act on the user's behalf when interacting with AWS services.
    required: false
    type: str
  state:
    description: Create (C(present)) or delete (C(absent)) application.
    required: true
    choices: ['present', 'absent']
    default: 'present'
    type: str
  trigger_configuration:
    description: Information about triggers to create when the deployment group is created. Can not be used with
    required: false
    type: dict
    elements: dict
    suboptions:
      trigger_name:
        description: The name of the trigger.
        required: true
        type: str
      trigger_target_arn:
        description: The ARN of the resource that is the target for a trigger (Amazon SNS topic).
        required: true
        type: str
      trigger_events:
        description: The event type or types for which notifications are triggered.
        required: true
        type: list
        elements: str
        choices: ['DeploymentStart', 'DeploymentSuccess', 'DeploymentFailure', 'DeploymentStop', 'DeploymentRollback', 'DeploymentReady', 'InstanceStart', 'InstanceSuccess', 'InstanceFailure', 'InstanceReady']
  alarm_configuration:
    description: Information to add about Amazon CloudWatch alarms when the deployment group is created.
    required: false
    type: dict
    suboptions:
      enabled:
        description: Indicates whether the alarm configuration is enabled.
        required: false
        type: bool
      alarm_names:
        description: A list of alarms configured for the deployment group. A maximum of 10 alarms can be added to a deployment group.
        required: false
        type: list
        elements: str
      ignore_poll_alarm_failure:
        description: Indicates whether a deployment should continue if information about the current state of alarms cannot be retrieved from Amazon CloudWatch.
        required: false
        type: bool
  auto_rollback_configuration:
    description: Information about the automatic rollback configuration associated with the deployment group.
    required: false
    type: dict
    suboptions:
      enabled:
        description: Indicates whether a defined automatic rollback configuration is currently enabled for this Deployment Group.
        required: false
        type: bool
      events:
        description: The event type or types that trigger a rollback.
        required: false
        type: list
        elements: str
        choices: ['DEPLOYMENT_FAILURE', 'DEPLOYMENT_STOP_ON_ALARM', 'DEPLOYMENT_STOP_ON_REQUEST']
  outdated_instances_strategy:
    description: Indicates what happens when new EC2 instances are launched into the AWS CodeDeploy deployment group.
    required: false
    type: str
    choices: ['UPDATE', 'IGNORE']
  deployment_style:
    description: Information about the type of deployment, either in-place or blue/green, you want to run and whether to route deployment traffic behind a load balancer.
    required: false
    type: dict
    suboptions:
      deployment_type:
        description: Indicates whether to route deployment traffic behind a load balancer.
        required: false
        type: str
        choices: ['IN_PLACE', 'BLUE_GREEN']
        default: 'IN_PLACE'
      deployment_option:
        description: Indicate wheter to route deployment traffic behind a load balancer.
        required: false
        type: str
        choices: ['WITH_TRAFFIC_CONTROL', 'WITHOUT_TRAFFIC_CONTROL']
        default: 'WITHOUT_TRAFFIC_CONTROL'
  blue_green_deployment_configuration:
    description: Information about blue/green deployment options for a deployment group.
    required: false
    type: dict
    suboptions:
      terminate_blue_instances_on_deployment_success:
        description: Information about whether to terminate instances in the original fleet during a blue/green deployment.
        required: false
        type: dict
        suboptions:
          action:
            description: The action to take on instances in the original environment after a successful blue/green deployment.
            required: false
            type: str
            choices: ['TERMINATE', 'KEEP_ALIVE']
          termination_wait_time_in_minutes:
            description: The number of minutes to wait after a successful blue/green deployment before terminating instances from the original environment.
            required: false
            type: int
      deployment_ready_option:
        description: Information about the action to take when newly provisioned instances are ready to receive traffic in a blue/green deployment.
        required: false
        type: dict
        suboptions:
          action_on_timeout:
            description: Information about the action to take when newly provisioned instances are ready to receive traffic in a blue/green deployment.
            required: false
            type: str
            choices: ['CONTINUE_DEPLOYMENT', 'STOP_DEPLOYMENT']
          wait_time_in_minutes:
            description: The number of minutes to wait before the status of a blue/green deployment changed to Stopped if rerouting is not started manually.
            required: false
            type: int
  load_balancer_info:
    description: Information about the load balancer used in a deployment.
    required: false
    type: dict
    suboptions:
      elb_info_name:
        description:
          - The Classic Elastic Load Balancer to use in a deployment. Can not be used with target_group_info_name. and target_group_pair_info.
          -  Instances are registered directly with a load balancer, and traffic is routed to the load balancer.
          - For blue/green deployments, the name of the load balancer that is used to route traffic from original instances to replacement instances in a blue/green deployment. For in-place deployments, the name of the load balancer that instances are deregistered from so they are not serving traffic during a deployment, and then re-registered with after the deployment is complete.
        required: false
        type: str
      target_group_info_name:
        description:
          - Information about the target group to use in a deployment. Can not be used with elb_info_name and target_group_pair_info.
          - Instances are registered as targets in a target group, and traffic is routed to the target group.
          - For blue/green deployments, the name of the target group that instances in the original environment are deregistered from, and instances in the replacement environment are registered with. For in-place deployments, the name of the target group that instances are deregistered from, so they are not serving traffic during a deployment, and then re-registered with after the deployment is complete.
        required: false
        type: str
      target_group_pair_info:
        description:
          - The path used by a load balancer to route production traffic when an Amazon ECS deployment is complete.
          - Information about two target groups and how traffic is routed during an Amazon ECS deployment. An optional test traffic route can be specified.
        required: false
        type: list
        suboptions:
          target_groups_name:
            description: One pair of target groups. One is associated with the original task set. The second target is associated with the task set that serves traffic after the deployment is complete.
            required: true
            type: list
            elements: str
          prod_traffic_route:
            description: The path used by a load balancer to route production traffic when an Amazon ECS deployment is complete.
            required: false
            type: dict
            suboptions:
              listener_arns:
                description: The listener information for the target group, such as the listener protocol and port.
                required: true
                type: list
                elements: str
          test_traffic_route:
            description: An optional path used by a load balancer to route test traffic after an Amazon ECS deployment. Validation can occur while test traffic is served during a deployment.
            required: false
            type: dict
            suboptions:
              listener_arns:
                description: The listener information for the target group, such as the listener protocol and port.
                required: true
                type: list
                elements: str
  auto_scaling_groups:
    description: A list of associated Auto Scaling groups.
    required: false
    type: list
    elements: str       
  ### Deployment Target
  ec2_tag_filters:
    description: The EC2 tag filter key and value pairs to identify EC2 instances in the deployment group. Can not be used in the same call as ec2_tag_set.
    required: false
    type: list
    elements: dict
    suboptions:
      key:
        description: The tag filter key.
        required: false
        type: str
      value:
        description: The tag filter value.
        required: false
        type: str
      type:
        description: The tag filter type.
        required: false
        type: str
        choices: ['KEY_ONLY', 'VALUE_ONLY', 'KEY_AND_VALUE']
  on_premises_instance_tag_filters:
    description: The on-premises instance tag filter key and value pairs to identify on-premises instances in the deployment group. Can not be used in the same call as on_premises_instance_tag_set.
    required: false
    type: list
    elements: dict
    suboptions:
      key:
        description: The tag filter key.
        required: false
        type: str
      value:
        description: The tag filter value.
        required: false
        type: str
      type:
        description: The tag filter type.
        required: false
        type: str
        choices: ['KEY_ONLY', 'VALUE_ONLY', 'KEY_AND_VALUE']
  ec2_tag_set:
    description: Information about groups of EC2 instance tags.
    required: false
    type: dict
    suboptions:
      ec2_tag_set_list:
        description: A list containing other lists of EC2 instance tag groups. In order for an instance to be included in the deployment group, it must be identified by all the tag groups in the list.
        required: true
        type: list
        elements: dict
        suboptions:
          key:
            description: A tag filter key.
            required: false
            type: str
          value:
            description: A tag filter value.
            required: false
            type: str
          type:
            description: The type of the tag filter.
            required: false
            type: str
            choices: ['KEY_ONLY', 'VALUE_ONLY', 'KEY_AND_VALUE']
  on_premises_instance_tag_set:
    description: Information about groups of on-premises instance tags.
    required: false
    type: dict
    suboptions:
      on_premises_instance_tag_set_list:
        description: A list containing other lists of on-premises instance tag groups. In order for an instance to be included in the deployment group, it must be identified by all the tag groups in the list.
        required: true
        type: list
        elements: dict
        suboptions:
          key:
            description: A tag filter key.
            required: false
            type: str
          value:
            description: A tag filter value.
            required: false
            type: str
          type:
            description: The type of the tag filter.
            required: false
            type: str
            choices: ['KEY_ONLY', 'VALUE_ONLY', 'KEY_AND_VALUE']
  ecs_services:
    description: The target Amazon ECS services in the deployment group. This applies only to deployment groups that use the Amazon ECS compute platform.
    required: false
    type: list
    elements: dict
    suboptions:
      service_name:
        description: The name of the target Amazon ECS service.
        required: true
        type: str
      cluster_name:
        description: The name of the cluster that the Amazon ECS service is associated with.
        required: true
        type: str
extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
# Create a new codedeploy group
- codedeploy_deployment_group:
    application_name: codedeploy-app
    deployment_group_name: codedeploy-app-dg
    service_role: arn:aws:iam::123456789012:role/ansible-test-codedeploy-role
    deployment_config_name: CodeDeployDefault.AllAtOnce
    alarm_configuration:
      enabled: True
      ignore_poll_alarm_failure: True
      alarm_names:
        - "codedeploy-app-dg-alarm-1"
        - "codedeploy-app-dg-alarm-2"
    outdated_instances_strategy: UPDATE
    deployment_style:
      deployment_type: IN_PLACE
      deployment_option: WITHOUT_TRAFFIC_CONTROL
    auto_rollback_configuration:
      enabled: True
      events:
        - DEPLOYMENT_STOP_ON_ALARM
        - DEPLOYMENT_FAILURE
    ec2_tag_set:
      ec2_tag_set_list:
        - ec2_tag:
            - key: Name
              value: ec2_instance_1
              type: KEY_AND_VALUE
            - key: Env
              value: Dev
              type: KEY_AND_VALUE
        - ec2_tag:
            - key: Name
              value: ec2_instance_2
              type: KEY_AND_VALUE
            - key: Env
              value: Dev
              type: KEY_AND_VALUE
    on_premises_tag_set:
      on_premises_tag_set_list:
        - on_premises_tag:
            - key: Name
              value: on_premises_instance_1
              type: KEY_AND_VALUE
            - key: Env
              value: Dev
              type: KEY_AND_VALUE
        - on_premises_tag:
            - key: Name
              value: on_premises_instance_2
              type: KEY_AND_VALUE
            - key: Env
              value: Dev
              type: KEY_AND_VALUE
    state: present


# Delete a codedeploy group
- codedeploy_deployment_group:
    application_name: codedeploy-app
    deployment_group_name: codedeploy-app-dg
    state: absent
"""

RETURN = r"""
deployment_group:
  description: Returns information about the deployment group.
  returned: When I(state) is C(present)
  type: complex
  contains:
    alarm_configuration:
      description: Information about alarms associated with the deployment group.
      returned: when I(alarm_configuration) is defined
      type: complex
      contains:
        alarms:
          description: A list of alarms configured for the deployment group. A maximum of 10 alarms can be added to a deployment group.
          returned: when I(alarm_configuration) is defined
          type: list
          elements: str
        enabled:
          description: Indicates whether the alarm configuration is enabled.
          returned: when I(alarm_configuration) is defined
          type: bool
        ignore_poll_alarm_failure:
          description: Indicates whether a deployment should continue if information about the current state of alarms cannot be retrieved from Amazon CloudWatch.
          returned: when I(alarm_configuration) is defined
          type: bool
    application_name:
      description: The application name.
      returned: always
      type: str
    auto_rollback_configuration:
      description: Information about the automatic rollback configuration associated with the deployment group.
      returned: when I(auto_rollback_configuration) is defined
      type: complex
      contains:
        enabled:
          description: Indicates whether a defined automatic rollback configuration is currently enabled for this Deployment Group.
          returned: when I(auto_rollback_configuration) is defined
          type: bool
        events:
          description: The event type or types that trigger a rollback.
          returned: when I(auto_rollback_configuration) is defined
          type: list
          elements: str
    auto_scaling_groups:
      description: A list of associated Auto Scaling groups.
      returned: when I(auto_scaling_groups) is defined
      type: list
      elements: str
    blue_green_deployment_configuration:
      description: Information about blue/green deployment options for a deployment group.
      returned: when I(blue_green_deployment_configuration) is defined
      type: complex
    load_balancer_info:
      description: Information about the load balancer used in a deployment.
      returned: when I(load_balancer_info) is defined
      type: complex
    auto_scaling_groups:
      description: A list of associated Auto Scaling groups.
      returned: when I(auto_scaling_groups) is defined
      type: list
      elements: str
    compute_platform:
      description: The destination platform type for deployment of the application.
      returned: always
      type: str
    deployment_config_name:
      description: The deployment configuration name.
      returned: always
      type: str
    deployment_group_id:
      description: The deployment group ID.
      returned: always
      type: str
    deployment_group_name:
      description: The deployment group name.
      returned: always
      type: str
    deployment_style:
      description: Information about the type of deployment, either in-place or blue/green, you want to run and whether to route deployment traffic behind a load balancer.
      returned: when I(deployment_style) is defined
      type: complex
    ecs_services:
      description: The target Amazon ECS services in the deployment group. This applies only to deployment groups that use the Amazon ECS compute platform.
      returned: when I(ecs_services) is defined
      type: list
      elements: complex
    ec2_tag_filters:
      description: The EC2 tag filter key and value pairs to identify EC2 instances in the deployment group. Can not be used in the same call as ec2_tag_set.
      returned: when I(ec2_tag_filters) is defined
      type: list
      elements: complex
    on_premises_instance_tag_filters:
      description: The on-premises instance tag filter key and value pairs to identify on-premises instances in the deployment group. Can not be used in the same call as on_premises_instance_tag_set.
      returned: when I(on_premises_instance_tag_filters) is defined
      type: list
      elements: complex
    ec2_tag_set:
      description: Information about groups of EC2 instance tags.
      returned: when I(ec2_tag_set) is defined
      type: complex
    on_premises_instance_tag_set:
      description: Information about groups of on-premises instance tags.
      returned: when I(on_premises_instance_tag_set) is defined
      type: complex
    last_attempted_deployment:
      description: Information about the most recent attempted deployment to the deployment group.
      type: complex
    last_successful_deployment:
      description: Information about the most recent successful deployment to the deployment group.
      type: complex
"""

try:
    import botocore
except ImportError:
    pass  # Handled by AnsibleAWSModule

from ansible_collections.amazon.aws.plugins.module_utils.botocore import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.exceptions import AnsibleAWSError

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict
from ansible.module_utils.common.dict_transformations import snake_dict_to_camel_dict


class CodeDeployAnsibleAWSError(AnsibleAWSError):
    pass


def _get_application(client, applicationName):
    try:
        response = client.get_application(applicationName=applicationName)
        return response
    except is_boto3_error_code("ApplicationDoesNotExistException"):
        return None
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        raise CodeDeployAnsibleAWSError(exception=e, message="couldn't get application")


def _get_deployment_group(client, applicationName, deploymentGroupName):
    try:
        response = client.get_deployment_group(applicationName=applicationName, deploymentGroupName=deploymentGroupName)
        return response
    except is_boto3_error_code("DeploymentGroupDoesNotExistException"):
        return None
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        raise CodeDeployAnsibleAWSError(exception=e, message="couldn't get deployment group")


def _create_deployment_group(client, module):
    try:
        params = prepare_present_options(module, state="present")
        response = client.create_deployment_group(**params)
        return response
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        raise CodeDeployAnsibleAWSError(exception=e, message="couldn't create deployment group")


def _update_deployment_group(client, module):
    try:
        params = prepare_present_options(module, state="update")
        response = client.update_deployment_group(**params)
        return response
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        raise CodeDeployAnsibleAWSError(exception=e, message="couldn't update deployment group")
    return response  # It'll be None


def _delete_deployment_group(client, module):
    try:
        response = client.delete_deployment_group(applicationName=module.params["application_name"], deploymentGroupName=module.params["deployment_group_name"])
        return response  # It'll be None
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:
        raise CodeDeployAnsibleAWSError(exception=e, message="couldn't delete deployment group")


def ensure_deployment_group_present(client, module):
    changed = False
    state = None
    application = _get_application(client, module.params["application_name"])
    if application is None:
        raise CodeDeployAnsibleAWSError(message="application does not exist")
    else:
        compute_platform = application["application"]["computePlatform"]
        module.debug("application computed platform: %s" % application["application"]["computePlatform"])

    deployemnt_group_name = module.params["deployment_group_name"]
    if _get_deployment_group(client, module.params["application_name"], module.params["deployment_group_name"]) is None:
        state = "create"
        if not module.check_mode:
            response = _create_deployment_group(client, module)

        changed = True
    else:
        state = "update"
        if not module.check_mode:
            response = _update_deployment_group(client, module)
            module.params.get("new_deployment_group_name") is not None
            deployemnt_group_name = module.params.get("new_deployment_group_name") if module.params.get("new_deployment_group_name") else module.params["deployment_group_name"]

        changed = True

    result = {"changed": changed}

    if module.check_mode and state == "create":
        result["deployment_group"] = None
        return result
    else:
        deployment_group = _get_deployment_group(client, module.params["application_name"], deployemnt_group_name)
        result["deployment_group"] = camel_dict_to_snake_dict(deployment_group["deploymentGroupInfo"])

    return result


def ensure_deployment_group_absent(client, module):
    changed = False
    response = None
    if _get_deployment_group(client, module.params["application_name"], module.params["deployment_group_name"]) is None:
        return {"changed": changed}
    else:
        if not module.check_mode:
            response = _delete_deployment_group(client, module)
        changed = True
        if response is not None and response["hooksNotCleanedUp"]:
            module.debug("AutoScaling LifecycleHook is not deleted. Please delete it manually.")
    return {"changed": changed}


def prepare_present_options(module, state="present"):
    """
    Return data structure for deployment group creation or update
    """
    dg_params = {
        "applicationName": module.params["application_name"],
    }
    if state == "present":
        if module.params["service_role"] is None:
            raise CodeDeployAnsibleAWSError(message="service_role is required")
        dg_params["deploymentGroupName"] = module.params["deployment_group_name"]
        dg_params["serviceRoleArn"] = module.params["service_role"]

    elif state == "update":
        dg_params["currentDeploymentGroupName"] = module.params["deployment_group_name"]
        if module.params["new_deployment_group_name"]:
            dg_params["newDeploymentGroupName"] = module.params["new_deployment_group_name"]

    # Optional parameters for create_deployment_group, Common
    dg_params.update(prepare_alarm_configuration(module))
    dg_params.update(prepare_trigger_configuration(module))
    dg_params.update(prepare_auto_rollback_configuration(module))

    if module.params["deployment_config_name"]:
        dg_params["deploymentConfigName"] = module.params["deployment_config_name"]

    if module.params["outdated_instances_strategy"]:
        dg_params["outdatedInstancesStrategy"] = module.params["outdated_instances_strategy"]

    if module.params["deployment_style"]:
        dg_params["deploymentStyle"] = {}
        if module.params["deployment_style"]["deployment_type"] is not None:
            deployment_type = module.params["deployment_style"]["deployment_type"]
            dg_params["deploymentStyle"]["deploymentType"] = deployment_type
        if module.params["deployment_style"]["deployment_option"] is not None:
            deployment_option = module.params["deployment_style"]["deployment_option"]
            dg_params["deploymentStyle"]["deploymentOption"] = deployment_option

    # Deployment type 'Server'(EC2/On-premises)
    dg_params.update(prepare_deployment_tags(module))

    if module.params["ecs_services"]:
        dg_params["ecsServices"] = []
        for ecs_service in module.params["ecs_services"]:
            ecs_service_params = {}
            if ecs_service["service_name"] is not None:
                ecs_service_params = {"serviceName": ecs_service["service_name"]}
            if ecs_service["cluster_name"] is not None:
                ecs_service_params["clusterName"] = ecs_service["cluster_name"]
            dg_params["ecsServices"].append(ecs_service_params)

    if module.params["load_balancer_info"]:
        dg_params["loadBalancerInfo"] = {}
        if module.params["load_balancer_info"]["elb_info_name"] is not None:  # Compute platform: Server
            dg_params["loadBalancerInfo"]["elbInfoList"] = [{"name": module.params["load_balancer_info"]["elb_info_name"]}]
        if module.params["load_balancer_info"]["target_group_info_name"] is not None:  # Compute platform: Server
            dg_params["loadBalancerInfo"]["targetGroupInfoList"] = [{"name": module.params["load_balancer_info"]["target_group_info_name"]}]
        if module.params["load_balancer_info"]["target_group_pair_info"] is not None:  # Compute platform: ECS
            target_group_pair_info_list = []
            for target_group_pair_info in module.params["load_balancer_info"]["target_group_pair_info"]:
                target_group_pair_info_list.append(snake_dict_to_camel_dict(target_group_pair_info))
            dg_params["loadBalancerInfo"]["targetGroupPairInfoList"] = target_group_pair_info_list

    return dg_params


def prepare_deployment_tags(module):
    if module.params["ec2_tag_set"] is not None and module.params["ec2_tag_filters"] is not None:
        raise CodeDeployAnsibleAWSError(message="ec2_tag_set and ec2_tag_filters can not be used in the same call")

    if module.params["on_premises_tag_set"] is not None and module.params["on_premises_instance_tag_filters"] is not None:
        raise CodeDeployAnsibleAWSError(message="on_premises_tag_set and on_premises_instance_tag_filters can not be used in the same call")

    params = {}
    if module.params["ec2_tag_set"]:
        ec2_tag_set_list = []
        for ec2_tag in module.params["ec2_tag_set"]["ec2_tag_set_list"]:
            ec2_tag_set_list.append(snake_dict_to_camel_dict(ec2_tag["ec2_tag"], capitalize_first=True))
        params["ec2TagSet"] = {"ec2TagSetList": ec2_tag_set_list}

    if module.params["ec2_tag_filters"]:  
        params["ec2TagFilters"] = snake_dict_to_camel_dict(module.params["ec2_tag_filters"], capitalize_first=True)

    if module.params["on_premises_tag_set"]:
        on_premises_tag_set_list = []
        for on_premises_tag in module.params["on_premises_tag_set"]["on_premises_tag_set_list"]:
            on_premises_tag_set_list.append(snake_dict_to_camel_dict(on_premises_tag["on_premises_tag"], capitalize_first=True))
        params["onPremisesTagSet"] = {"onPremisesTagSetList": on_premises_tag_set_list}

    if module.params["on_premises_instance_tag_filters"]:
        params["onPremisesInstanceTagFilters"] = snake_dict_to_camel_dict(module.params["on_premises_instance_tag_filters"], capitalize_first=True)

    return params


def prepare_alarm_configuration(module):
    params = {}
    c_params = {}

    if module.params["alarm_configuration"]:
        alarm_names = []
        if module.params["alarm_configuration"]["enabled"] is not None:
            c_params["enabled"] = module.params["alarm_configuration"]["enabled"]

        if module.params["alarm_configuration"]["alarm_names"] is not None:
            for alarm_name in module.params["alarm_configuration"]["alarm_names"]:
                alarm_names.append({"name": alarm_name})
            c_params["alarms"] = alarm_names

        if module.params["alarm_configuration"]["ignore_poll_alarm_failure"] is not None:
            c_params["ignorePollAlarmFailure"] = module.params["alarm_configuration"]["ignore_poll_alarm_failure"]
        params["alarmConfiguration"] = c_params

    return params


def prepare_trigger_configuration(module):
    params = {}

    if module.params["trigger_configuration"]:
        trigger_configuration = []
        trigger_configuration.append(snake_dict_to_camel_dict(module.params["trigger_configuration"]))
        params["triggerConfigurations"] = trigger_configuration

    return params


def prepare_auto_rollback_configuration(module):
    params = {}
    c_params = {}

    if module.params["auto_rollback_configuration"]:
        if module.params["auto_rollback_configuration"]["enabled"] is not None:
            c_params["enabled"] = module.params["auto_rollback_configuration"]["enabled"]
        if module.params["auto_rollback_configuration"]["events"] is not None:
            c_params["events"] = module.params["auto_rollback_configuration"]["events"]
        params["autoRollbackConfiguration"] = c_params

    return params


def main():
    argument_spec = dict(
        application_name=dict(type="str", required=True),
        deployment_group_name=dict(type="str", required=True),
        new_deployment_group_name=dict(type="str", required=False),
        deployment_config_name=dict(type="str", required=False),
        service_role=dict(),
        state=dict(type="str", choices=["present", "absent"], default="present"),
        trigger_configuration=dict(  # Compute platform: Server, ECS, Lambda
            type="dict",
            options=dict(
                trigger_name=dict(type="str", required=True),
                trigger_target_arn=dict(type="str", required=True),
                trigger_events=dict(type="list", elements="str", choices=["DeploymentStart", "DeploymentSuccess", "DeploymentFailure", "DeploymentStop", "DeploymentRollback", "DeploymentReady", "InstanceStart", "InstanceSuccess", "InstanceFailure", "InstanceReady"], required=True),
            ),
            required=False,
        ),
        alarm_configuration=dict(  # Compute platform: Server, ECS, Lambda
            type="dict",
            options=dict(
                enabled=dict(type="bool", required=False),
                alarm_names=dict(type="list", elements="str", required=False),
                ignore_poll_alarm_failure=dict(type="bool", required=False),
            ),
            required=False,
        ),
        auto_rollback_configuration=dict(  # Compute platform: Server, ECS , Lambda
            type="dict",
            options=dict(
                enabled=dict(type="bool", required=False),
                events=dict(type="list", elements="str", choices=["DEPLOYMENT_FAILURE", "DEPLOYMENT_STOP_ON_ALARM", "DEPLOYMENT_STOP_ON_REQUEST"], required=False),
            ),
            required=False,
        ),
        outdated_instances_strategy=dict(type="str", choices=["UPDATE", "IGNORE"], required=False),  # Compute platform: Server
        deployment_style=dict(
            type="dict",
            options=dict(
                deployment_type=dict(type="str", choices=["IN_PLACE", "BLUE_GREEN"], required=True),
                deployment_option=dict(type="str", choices=["WITH_TRAFFIC_CONTROL", "WITHOUT_TRAFFIC_CONTROL"], required=True),
            ),
            required=False,
        ),
        blue_green_deployment_configuration=dict(
            type="dict",
            options=dict(
                terminate_blue_instances_on_deployment_success=dict(
                    type="dict",
                    options=dict(
                        action=dict(type="str", choices=["TERMINATE", "KEEP_ALIVE"], required=False),
                        termination_wait_time_in_minutes=dict(type="int", required=False),
                    ),
                    required=False,
                ),
                deployment_ready_option=dict(
                    type="dict",
                    options=dict(
                        action_on_timeout=dict(type="str", choices=["CONTINUE_DEPLOYMENT", "STOP_DEPLOYMENT"], required=False),
                        wait_time_in_minutes=dict(type="int", required=False),
                    ),
                    required=False,
                ),
            ),
            required=False,
        ),
        load_balancer_info=dict(
            type="dict",
            options=dict(
                elb_info_name=dict(type="list", elements="str", required=False),
                target_group_info_name=dict(type="str", required=False),
                target_group_pair_info=dict(  # Compute platform: ECS
                    type="list",
                    elements="dict",
                    options=dict(
                        target_groups_name=dict(type="list", elements="str", required=True),
                        prod_traffic_route=dict(
                            type="dict",
                            options=dict(
                                listener_arns=dict(type="list", elements="str", required=True),
                            ),
                            required=False,
                        ),
                        test_traffic_route=dict(
                            type="dict",
                            options=dict(
                                listener_arns=dict(type="list", elements="str", required=True),
                            ),
                            required=False,
                        ),
                    ),
                    required=False,
                ),
            ),
            required=False,
        ),
        auto_scaling_groups=dict(type="list", elements="str", required=False),
        ec2_tag_filters=dict(  # Compute platform: Server
            type="list",
            elements="dict",
            options=dict(
                key=dict(type="str"),
                value=dict(type="str"),
                type=dict(type="str", choices=["KEY_ONLY", "VALUE_ONLY", "KEY_AND_VALUE"]),
            ),
            required=False,
        ),
        on_premises_instance_tag_filters=dict(  # Compute platform: Server
            type="list",
            elements="dict",
            options=dict(
                key=dict(type="str", required=False),
                value=dict(type="str", required=False),
                type=dict(type="str", choices=["KEY_ONLY", "VALUE_ONLY", "KEY_AND_VALUE"], required=False),
            ),
            required=False,
        ),
        ec2_tag_set=dict(
            type="dict",
            options=dict(
                ec2_tag_set_list=dict(
                    type="list",
                    elements="dict",
                    options=dict(
                        ec2_tag=dict(
                            type="list",
                            options=dict(
                                key=dict(type="str", required=False),
                                value=dict(type="str", required=False),
                                type=dict(type="str", choices=["KEY_ONLY", "VALUE_ONLY", "KEY_AND_VALUE"], required=False),
                            ),
                            required=True,
                        ),
                    ),
                    required=True,
                ),
            ),
            required=False,
        ),
        on_premises_tag_set=dict(
            type="dict",
            options=dict(
                on_premises_tag_set_list=dict(
                    type="list",
                    elements="dict",
                    options=dict(
                        on_premises_tag=dict(
                            type="list",
                            options=dict(
                                key=dict(type="str", required=False),
                                value=dict(type="str", required=False),
                                type=dict(type="str", choices=["KEY_ONLY", "VALUE_ONLY", "KEY_AND_VALUE"], required=False),
                            ),
                            required=True,
                        ),
                    ),
                    required=True,
                ),
            ),
            required=False,
        ),
        ecs_services=dict(
            type="list",
            elements="dict",
            options=dict(
                service_name=dict(type="str", required=True),
                cluster_name=dict(type="str", required=True),
            ),
            required=False,
        ),
    )

    module = AnsibleAWSModule(argument_spec=argument_spec, supports_check_mode=True)
    client = module.client("codedeploy")

    try:
        if module.params["state"] == "present":
            result = ensure_deployment_group_present(client, module)
        elif module.params["state"] == "absent":
            result = ensure_deployment_group_absent(client, module)
    except botocore.exceptions.ClientError as e:
        module.fail_json_aws(e)

    module.exit_json(**result)


if __name__ == "__main__":
    main()
