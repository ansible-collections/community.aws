#!/usr/bin/python

# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: ec2_lgw_route_table_association
version_added: 1.0.0
short_description: Associate a VPC to a Local Gateway Route Table
description:
  - Associate a VPC to a Local Gateway Route Table
author:
  - Joel Bento Valenca (@joe1368)
options:
  lgw_route_table_id:
    description:
      - The ID of the local gateway route table to associate.
      - Required when O(state=present).
    type: str
  vpc_id:
    description:
      - VPC ID of the VPC in which to associate.
      - Required when O(state=present).
    type: str
  lgw_route_table_vpc_association_id:
    description:
      - The ID of the association between the VPC and the Local Gateway Route Table.
      - Required when O(state=absent).
    type: str
  state:
    description: Create or destroy the Local Gateway Route Table association with the VPC.
    default: present
    choices: [ 'present', 'absent' ]
    type: str
extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.tags
  - amazon.aws.boto3
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details, see the AWS Guide for details.

# Creation example:
- name: Create local gateway route table association
  community.aws.ec2_lgw_route_table_association:
    vpc_id: vpc-xxxxxxxxx
    lgw_route_table_id: lgw-rtb-xxxxxxxxxxxxxxxxx
    tags:
      Name: LGW-RT-vpc-1245678
  register: lgw_route_table_association

# Deletion example:
- name: Delete local gateway route table association
  community.aws.ec2_lgw_route_table_association:
    lgw_route_table_vpc_association_id: lgw-vpc-assoc-xxxxxxxxxxx
    state: absent

- name: Delete local gateway route table association
  community.aws.ec2_lgw_route_table_association:
    vpc_id: vpc-xxxxxxxxx
    lgw_route_table_id: lgw-rtb-xxxxxxxxxxxxxxxxx
    state: absent
"""

RETURN = r"""
result:
  description: Returns an array of complex objects as described below.
  returned: success
  type: complex
  contains:
    LocalGatewayRouteTableVpcAssociationId:
      description: The ID of the association.
      returned: always
      type: str
      sample: lgw-vpc-assoc-xxxxxxxxxxx
    LocalGatewayRouteTableId :
      description: The ID of the local gateway route table.
      returned: always
      type: str
      sample: lgw-rtb-xxxxxxxxxxxxxxxxx
    LocalGatewayRouteTableArn:
      description: The ARN of the local gateway route table.
      returned: always
      type: str
      sample: arn:aws:ec2:us-east-1:123456789012:local-gateway-route-table/lgw-rtb-xxxxxxxxxxxxxxxxx
    LocalGatewayId:
      description: The ID of the local gateway.
      returned: always
      type: str
      sample: lgw-xxxxxxxxxxxxxxxxx
    vpc_id:
      description: ID for the VPC in which the route lives.
      returned: always
      type: str
      sample: vpc-6e2d2407
    owner_id:
        description: AWS account owning resource.
        type: str
        sample: 123456789012
    state:
      description: The state of the local gateway route table association.
      returned: always
      type: str
      sample: associated
    tags:
      description: Tags applied to the route table.
      returned: always
      type: dict
      sample:
        Name: LGW-RT-vpc-1245678
"""


from time import sleep
from typing import Any
from typing import Dict
from typing import List
from typing import Union
from typing import Optional



from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AnsibleEC2Error
from ansible_collections.amazon.aws.plugins.module_utils.retries import AWSRetry
from ansible_collections.amazon.aws.plugins.module_utils.tagging import boto3_tag_specifications
from ansible_collections.amazon.aws.plugins.module_utils.tagging import boto3_tag_list_to_ansible_dict
from ansible_collections.amazon.aws.plugins.module_utils.transformation import ansible_dict_to_boto3_filter_list

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule


@AWSRetry.jittered_backoff()
def describe_lgw_route_table_associations(
    client, **params: Dict[str, Union[List[str], bool, List[Dict[str, Union[str, List[str]]]]]]
) -> List[Dict[str, Any]]:
    paginator = client.get_paginator("describe_local_gateway_route_table_vpc_associations")
    return paginator.paginate(**params).build_full_result()["LocalGatewayRouteTableVpcAssociations"]

@AWSRetry.jittered_backoff()
def create_lgw_route_table_association(client, lgw_route_table_id: str, vpc_id: str, tags: Optional[Dict[str, str]]) -> Dict[str, Any]:
    params = {"LocalGatewayRouteTableId": lgw_route_table_id,
              "VpcId": vpc_id}
    if tags:
        params["TagSpecifications"] = boto3_tag_specifications(tags, types="local-gateway-route-table-vpc-association")
    return client.create_local_gateway_route_table_vpc_association(**params)["LocalGatewayRouteTableVpcAssociation"]

@AWSRetry.jittered_backoff()
def delete_lgw_route_table_association(client, lgw_route_table_vpc_association_id: str) -> bool:
    client.delete_local_gateway_route_table_vpc_association(LocalGatewayRouteTableVpcAssociationId=lgw_route_table_vpc_association_id)
    return True


def ensure_lgw_route_table_vpc_association_present(connection, module: AnsibleAWSModule) -> Dict[str, Any]:
    lgw_route_table_id = module.params.get("lgw_route_table_id")
    tags = module.params.get("tags")
    vpc_id = module.params.get("vpc_id")

    changed = False

    filters = ansible_dict_to_boto3_filter_list({"vpc-id": vpc_id, "local-gateway-route-table-id": lgw_route_table_id})
    lgw_route_table_associations = describe_lgw_route_table_associations(connection, Filters=filters)

    #If not Local Gateway Route Table Association found, create new association
    if lgw_route_table_associations in ([], None):
        changed = True
        if module.check_mode:
            lgw_route_table_associations = {"LocalGatewayRouteTableVpcAssociationId": "lgw-vpc-assoc-xxxxxxxxxxx", 
                                           "LocalGatewayRouteTableId": lgw_route_table_id, 
                                           "LocalGatewayRouteTableArn": f"arn:aws:ec2:us-east-2:xxxxxxxxxxxx:local-gateway-route-table/{lgw_route_table_id}",
                                           "LocalGatewayId": "lgw-xxxxxxxxxxxxxx",
                                           "VpcId": vpc_id,
                                           "OwnerId": "xxxxxxxxxxx",
                                           "State": "associated",
                                           "Tags": tags}
            return dict(changed=changed, result=lgw_route_table_associations)

        create_lgw_route_table_association(connection, lgw_route_table_id, vpc_id, tags)

    if changed:
        #Wait for the local gateway route table association to be created
        lgw_route_table_associations = describe_lgw_route_table_associations(connection, Filters=filters)
        while lgw_route_table_associations[0]["State"] != "associated":
            sleep(5)
            lgw_route_table_associations = describe_lgw_route_table_associations(connection, Filters=filters)

    lgw_route_table_associations[0]["Tags"] = boto3_tag_list_to_ansible_dict(lgw_route_table_associations[0]["Tags"])

    return dict(changed=changed, result=lgw_route_table_associations[0])

def ensure_lgw_route_table_vpc_association_absent(connection, module: AnsibleAWSModule) -> Dict[str, bool]:
    lgw_route_table_vpc_association_id = module.params.get("lgw_route_table_vpc_association_id")
    vpc_id = module.params.get("vpc_id")
    lgw_route_table_id = module.params.get("lgw_route_table_id")

    changed = False

    if lgw_route_table_vpc_association_id:
        filters = ansible_dict_to_boto3_filter_list({"local-gateway-route-table-vpc-association-id": lgw_route_table_vpc_association_id})
    elif vpc_id and lgw_route_table_id:
        filters = ansible_dict_to_boto3_filter_list({"vpc-id": vpc_id, "local-gateway-route-table-id": lgw_route_table_id})

    lgw_route_table_associations = describe_lgw_route_table_associations(connection, Filters=filters)

    if lgw_route_table_associations in ([], None):
        return {"changed": changed}

    if module.check_mode:
        changed = True
        return {"changed": changed}
    else:
        lgw_route_table_vpc_association_id = lgw_route_table_associations[0]["LocalGatewayRouteTableVpcAssociationId"]
        changed = delete_lgw_route_table_association(connection, lgw_route_table_vpc_association_id)

    if changed:
        # Wait for the local gateway route table association to be deleted
        lgw_route_table_associations = describe_lgw_route_table_associations(connection, Filters=filters)
        while lgw_route_table_associations not in ([], None):
            sleep(5)
            lgw_route_table_associations = describe_lgw_route_table_associations(connection, Filters=filters)

    return {"changed": changed}


def main() -> None:
    argument_spec = dict(
        lgw_route_table_id=dict(type="str"),
        vpc_id=dict(),
        tags=dict(type="dict", aliases=["resource_tags"]),
        lgw_route_table_vpc_association_id=dict(type="str"),
        state=dict(default="present", choices=["present", "absent"]),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        required_if=[
            ["state", "absent", ["lgw_route_table_vpc_association_id","vpc_id"],True],
        ],
        required_together=[
            ["lgw_route_table_id", "vpc_id"],
        ],
        supports_check_mode=True,
    )

    connection = module.client("ec2")
    method_operation = (
        ensure_lgw_route_table_vpc_association_present if module.params.get("state") == "present" else ensure_lgw_route_table_vpc_association_absent
    )

    try:
        result = method_operation(connection, module)
    except AnsibleEC2Error as e:
        module.fail_json_aws_error(e)

    module.exit_json(**result)


if __name__ == "__main__":
    main()