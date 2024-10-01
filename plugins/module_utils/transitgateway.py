# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from copy import deepcopy
try:
    from botocore.exceptions import BotoCoreError
    from botocore.exceptions import ClientError
except ImportError:
    pass

from typing import NoReturn, Optional
from typing import Dict
from typing import Any
from typing import List

from .modules import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.waiters import get_waiter

from ansible_collections.amazon.aws.plugins.module_utils.transformation import ansible_dict_to_boto3_filter_list

from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AnsibleEC2Error
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import describe_vpc_attachments
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import create_vpc_attachment
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import modify_vpc_attachment
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import delete_vpc_attachment
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import get_tgw_vpc_attachment
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import ensure_ec2_tags
from ansible_collections.amazon.aws.plugins.module_utils.modules import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import describe_subnets
from ansible_collections.amazon.aws.plugins.module_utils.tagging import boto3_tag_list_to_ansible_dict
from ansible_collections.amazon.aws.plugins.module_utils.tagging import boto3_tag_specifications
from ansible_collections.amazon.aws.plugins.module_utils.transformation import boto3_resource_to_ansible_dict


class TransitGatewayVpcAttachmentManager:
    TAG_RESOURCE_TYPE = "transit-gateway-attachment"

    def __init__(self, module: AnsibleAWSModule, id: Optional[str] = None) -> None:
        self.module = module
        self.subnet_updates = dict()
        self.id = id
        self.changed = False
        self.results = {"changed": False}
        self.wait = module.params.get("wait")
        self.connection = self.module.client("ec2")
        self.check_mode = self.module.check_mode
        self.original_resource = dict()
        self.updated_resource = dict()
        self.resource_updates = dict()
        self.preupdate_resource = dict()
        self.wait_timeout = None

        # Name parameter is unique (by region) and can not be modified.
        if self.id:
            resource = deepcopy(self.get_resource())
            self.original_resource = resource

    def get_id_params(self, id: Optional[str] = None, id_list: bool = False) -> Dict[str, List[str]]:
        if not id:
            id = self.id
        if not id:
            # Users should never see this, but let's cover ourself
            self.module.fail_json(msg="Attachment identifier parameter missing")

        if id_list:
            return dict(TransitGatewayAttachmentIds=[id])
        return dict(TransitGatewayAttachmentId=id)

    def filter_immutable_resource_attributes(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        resource = deepcopy(resource)
        resource.pop("TransitGatewayId", None)
        resource.pop("VpcId", None)
        resource.pop("VpcOwnerId", None)
        resource.pop("State", None)
        resource.pop("SubnetIds", None)
        resource.pop("CreationTime", None)
        return resource

    def set_option(self, name: str, value: Optional[bool]) -> bool:
        if value is None:
            return False
        # For now VPC Attachment options are all enable/disable
        if value:
            value = "enable"
        else:
            value = "disable"

        options = deepcopy(self.preupdate_resource.get("Options", dict()))
        options.update(self.resource_updates.get("Options", dict()))
        options[name] = value

        return self.set_resource_value("Options", options)

    def set_tags(self, tags: Dict[str, Any], purge_tags: bool) -> NoReturn:
        if self.id:
            self.changed |= ensure_ec2_tags(self.connection, self.module, self.id, resource_type=self.TAG_RESOURCE_TYPE, tags=tags, purge_tags=purge_tags)

    def set_resource_value(self, key, value, description: Optional[str] = None, immutable: bool = False):
        if value is None:
            return False
        if value == self.get_resource_value(key):
            return False
        if immutable and self.original_resource:
            if description is None:
                description = key
            self.module.fail_json(msg=f"{description} can not be updated after creation")
        self.resource_updates[key] = value
        self.changed = True
        return True

    def get_resource_value(self, key, default=None):
        default_value = self.preupdate_resource.get(key, default)
        return self.resource_updates.get(key, default_value)

    def set_dns_support(self, value: Optional[bool]) -> bool:
        return self.set_option("DnsSupport", value)

    def set_multicast_support(self, value: Optional[bool]) -> bool:
        return self.set_option("MulticastSupport", value)

    def set_ipv6_support(self, value: Optional[bool]) -> bool:
        return self.set_option("Ipv6Support", value)

    def set_appliance_mode_support(self, value: Optional[bool]) -> bool:
        return self.set_option("ApplianceModeSupport", value)

    def set_transit_gateway(self, tgw_id: str) -> bool:
        return self.set_resource_value("TransitGatewayId", tgw_id)

    def set_vpc(self, vpc_id: str) -> bool:
        return self.set_resource_value("VpcId", vpc_id)

    def set_wait(self, wait: bool) -> bool:
        if wait is None:
            return False
        if wait == self.wait:
            return False

        self.wait = wait
        return True

    def set_wait_timeout(self, timeout: int) -> bool:
        if timeout is None:
            return False
        if timeout == self.wait_timeout:
            return False

        self.wait_timeout = timeout
        return True

    def set_subnets(self, subnets: Optional[List[str]] = None, purge: bool = True) -> bool:
        if subnets is None:
            return False

        current_subnets = set(self.preupdate_resource.get("SubnetIds", []))
        desired_subnets = set(subnets)
        if not purge:
            desired_subnets = desired_subnets.union(current_subnets)

        # We'll pull the VPC ID from the subnets, no point asking for
        # information we 'know'.
        try:
            subnet_details = describe_subnets(self.connection, SubnetIds=list(desired_subnets))
        except AnsibleEC2Error as e:
            self.module.fail_json_aws_error(e)
        vpc_id = self.subnets_to_vpc(desired_subnets, subnet_details)
        self.set_resource_value("VpcId", vpc_id, immutable=True)

        # Only one subnet per-AZ is permitted
        azs = [s.get("AvailabilityZoneId") for s in subnet_details]
        if len(azs) != len(set(azs)):
            self.module.fail_json(
                msg="Only one attachment subnet per availability zone may be set.",
                availability_zones=azs,
                subnets=subnet_details,
            )

        subnets_to_add = list(desired_subnets.difference(current_subnets))
        subnets_to_remove = list(current_subnets.difference(desired_subnets))
        if not subnets_to_remove and not subnets_to_add:
            return False
        self.subnet_updates = dict(add=subnets_to_add, remove=subnets_to_remove)
        self.set_resource_value("SubnetIds", list(desired_subnets))
        return True

    def subnets_to_vpc(self, subnets: List[str], subnet_details: Optional[List[Dict[str, Any]]] = None) -> Optional[str]:
        if not subnets:
            return None

        if subnet_details is None:
            try:
                subnet_details = describe_subnets(self.connection, SubnetIds=list(subnets))
            except AnsibleEC2Error as e:
                self.module.fail_json_aws_error(e)

        vpcs = [s.get("VpcId") for s in subnet_details]
        if len(set(vpcs)) > 1:
            self.module.fail_json(
                msg="Attachment subnets may only be in one VPC, multiple VPCs found",
                vpcs=list(set(vpcs)),
                subnets=subnet_details,
            )

        return vpcs[0]

    def merge_resource_changes(self, filter_immutable=True, creation=False):
        resource = deepcopy(self.preupdate_resource)
        resource.update(self.resource_updates)

        if filter_immutable:
            resource = self.filter_immutable_resource_attributes(resource)

        if creation:
            tags = boto3_tag_list_to_ansible_dict(resource.pop('Tags', []))
            tag_specs = boto3_tag_specifications(tags, types=[self.TAG_RESOURCE_TYPE])
            if tag_specs:
                resource["TagSpecifications"] = tag_specs

        return resource

    def wait_tgw_attachment_deleted(self, **params: Any) -> None:
        if self.wait:
            try:
                waiter = get_waiter(self.connection, "transit_gateway_vpc_attachment_deleted")
                waiter.wait(**params)
            except (BotoCoreError, ClientError) as e:
                self.module.fail_json_aws(e)

    def wait_tgw_attachment_available(self, **params: Any) -> None:
        if self.wait:
            try:
                waiter = get_waiter(self.connection, "transit_gateway_vpc_attachment_available")
                waiter.wait(**params)
            except (BotoCoreError, ClientError) as e:
                self.module.fail_json_aws(e)

    def do_deletion_wait(self, id: Optional[str] = None, **params: Any) -> None:
        all_params = self.get_id_params(id=id, id_list=True)
        all_params.update(**params)
        return self.wait_tgw_attachment_deleted(**all_params)

    def do_creation_wait(self, id: Optional[str] = None, **params: Any) -> None:
        all_params = self.get_id_params(id=id, id_list=True)
        all_params.update(**params)
        return self.wait_tgw_attachment_available(**all_params)

    def do_update_wait(self, id: Optional[str] = None, **params: Any) -> None:
        all_params = self.get_id_params(id=id, id_list=True)
        all_params.update(**params)
        return self.wait_tgw_attachment_available(**all_params)

    @property
    def waiter_config(self):
        params = dict()
        if self.wait_timeout:
            delay = min(5, self.wait_timeout)
            max_attempts = self.wait_timeout // delay
            config = dict(Delay=delay, MaxAttempts=max_attempts)
            params["WaiterConfig"] = config
        return params

    def wait_for_deletion(self):
        if not self.wait:
            return
        params = self.waiter_config
        self.do_deletion_wait(**params)

    def wait_for_creation(self):
        if not self.wait:
            return
        params = self.waiter_config
        self.do_creation_wait(**params)

    def wait_for_update(self):
        if not self.wait:
            return
        params = self.waiter_config
        self.do_update_wait(**params)

    def generate_updated_resource(self):
        """
        Merges all pending changes into self.updated_resource
        Used during check mode where it's not possible to get and
        refresh the resource
        """
        return self.merge_resource_changes(filter_immutable=False)

    def flush_create(self):
        changed = True

        if not self.module.check_mode:
            changed = self.do_create_resource()
            self.wait_for_creation()
            self.do_creation_wait()
            self.updated_resource = self.get_resource()
        else:  # (CHECK MODE)
            self.updated_resource = self.normalize_tgw_attachment(self.generate_updated_resource())

        self.resource_updates = dict()
        self.changed = changed
        return True

    def check_updates_pending(self):
        if self.resource_updates:
            return True
        return False

    def do_create_resource(self) -> Optional[Dict[str, Any]]:
        params = self.merge_resource_changes(filter_immutable=False, creation=True)
        try:
            response = create_vpc_attachment(self.connection, **params)
        except AnsibleEC2Error as e:
            self.module.fail_json_aws_error(e)
        if response:
            self.id = response.get("TransitGatewayAttachmentId", None)
        return response

    def do_update_resource(self) -> bool:
        if self.preupdate_resource.get("State", None) == "pending":
            # Resources generally don't like it if you try to update before creation
            # is complete.  If things are in a 'pending' state they'll often throw
            # exceptions.

            self.wait_for_creation()
        elif self.preupdate_resource.get("State", None) == "deleting":
            self.module.fail_json(msg="Deletion in progress, unable to update", route_tables=[self.original_resource])

        updates = self.filter_immutable_resource_attributes(self.resource_updates)
        subnets_to_add = self.subnet_updates.get("add", [])
        subnets_to_remove = self.subnet_updates.get("remove", [])
        if subnets_to_add:
            updates["AddSubnetIds"] = subnets_to_add
        if subnets_to_remove:
            updates["RemoveSubnetIds"] = subnets_to_remove

        if not updates:
            return False

        if self.module.check_mode:
            return True

        updates.update(self.get_id_params(id_list=False))
        try:
            modify_vpc_attachment(self.connection, **updates)
        except AnsibleEC2Error as e:
            self.module.fail_json_aws_error(e)
        return True

    def get_resource(self) -> Optional[Dict[str, Any]]:
        return self.get_attachment()

    def delete(self, id: Optional[str] = None) -> bool:
        if id:
            id_params = self.get_id_params(id=id, id_list=True)
            result = get_tgw_vpc_attachment(self.connection, self.module, **id_params)
        else:
            result = self.preupdate_resource

        self.updated_resource = dict()

        if not result:
            return False

        if result.get("State") == "deleting":
            self.wait_for_deletion()
            return False

        if self.module.check_mode:
            self.changed = True
            return True

        id_params = self.get_id_params(id=id, id_list=False)

        try:
            result = delete_vpc_attachment(self.connection, **id_params)
        except AnsibleEC2Error as e:
            self.module.fail_json_aws_error(e)

        self.changed |= bool(result)

        self.wait_for_deletion()
        return bool(result)

    def list(self, filters: Optional[Dict[str, Any]] = None, id: Optional[str] = None) -> List[Dict[str, Any]]:
        params = dict()
        if id:
            params["TransitGatewayAttachmentIds"] = [id]
        if filters:
            params["Filters"] = ansible_dict_to_boto3_filter_list(filters)
        try:
            attachments = describe_vpc_attachments(self.connection, **params)
        except AnsibleEC2Error as e:
            self.module.fail_json_aws_error(e)
        if not attachments:
            return []

        return [self.normalize_tgw_attachment(a) for a in attachments]

    def get_attachment(self, id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        # RouteTable needs a list, Association/Propagation needs a single ID
        id_params = self.get_id_params(id=id, id_list=True)
        result = get_tgw_vpc_attachment(self.connection, self.module, **id_params)

        if not result:
            return None

        if not id:
            self.preupdate_resource = deepcopy(result)

        attachment = self.normalize_tgw_attachment(result)
        return attachment

    def normalize_tgw_attachment(self, resource: Dict[str, Any]) -> Dict[str, Any]:
        return boto3_resource_to_ansible_dict(resource, force_tags=True)

    def get_states(self) -> List[str]:
        return [
            "available",
            "deleting",
            "failed",
            "failing",
            "initiatingRequest",
            "modifying",
            "pendingAcceptance",
            "pending",
            "rollingBack",
            "rejected",
            "rejecting",
        ]

    def flush_update(self):
        if not self.check_updates_pending():
            self.updated_resource = self.original_resource
            return False

        if not self.module.check_mode:
            self.do_update_resource()
            self.wait_for_update()
            self.updated_resource = self.get_resource()
        else:  # (CHECK_MODE)
            self.updated_resource = self.normalize_tgw_attachment(self.generate_updated_resource())

        self._resource_updates = dict()
        return True

    def flush_changes(self):
        if self.original_resource:
            return self.flush_update()
        else:
            return self.flush_create()
