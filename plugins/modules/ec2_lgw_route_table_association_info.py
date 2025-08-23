#!/usr/bin/python

# GNU General Public License v3.0+ (see https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
---
module: ec2_lgw_route_table_association_info
version_added: 1.0.0
short_description: Get information about a Local Gateway Route Table association
description:
  - Get information about a Local Gateway Route Table association
author:
  - Joel Bento Valenca (@joe1368)
options:
  lgw_route_table_id:
    description:
      - The ID of the local gateway route table.
      - Required when no other options are specified.
    type: str
  vpc_id:
    description:
      - VPC ID of the VPC.
      - Required when no other options are specified.
    type: str
  lgw_route_table_vpc_association_id:
    description:
      - The ID of the association between the VPC and the Local Gateway Route Table.
      - Required when no other options are specified.
    type: str
extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.tags
  - amazon.aws.boto3
"""

EXAMPLES = r"""
# Note: These examples do not set authentication details, see the AWS Guide for details.

# Getting example:
- name: Get local gateway route table associations by ID
  community.aws.ec2_lgw_route_table_association_info:
    lgw_route_table_vpc_association_id: lgw-vpc-assoc-xxxxxxxxxxx
  register: lgw_route_table_associations

- name: Get local gateway route table associations by VPC ID
  community.aws.ec2_lgw_route_table_association_info:
    vpc_id: vpc-xxxxxxxxxxx
  register: lgw_route_table_associations

- name: Get local gateway route table associations by Local Gateway Route Table ID
  community.aws.ec2_lgw_route_table_association_info:
    lgw_route_table_id: lgw-rtb-xxxxxxxxxxxxxxxxx
  register: lgw_route_table_associations

- name: Get local gateway route table associations by Local Gateway Route Table ID and VPC ID
  community.aws.ec2_lgw_route_table_association_info:
    lgw_route_table_id: lgw-rtb-xxxxxxxxxxxxxxxxx
    vpc_id: vpc-xxxxxxxxxxx
  register: lgw_route_table_associations
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


from typing import Any
from typing import Dict
from typing import List
from typing import Union

from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AnsibleEC2Error
from ansible_collections.amazon.aws.plugins.module_utils.retries import AWSRetry
from ansible_collections.amazon.aws.plugins.module_utils.tagging import boto3_tag_list_to_ansible_dict
from ansible_collections.amazon.aws.plugins.module_utils.transformation import ansible_dict_to_boto3_filter_list

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule


@AWSRetry.jittered_backoff()
def describe_lgw_route_table_associations(
    client, **params: Dict[str, Union[List[str], bool, List[Dict[str, Union[str, List[str]]]]]]
) -> List[Dict[str, Any]]:
    paginator = client.get_paginator("describe_local_gateway_route_table_vpc_associations")
    return paginator.paginate(**params).build_full_result()["LocalGatewayRouteTableVpcAssociations"]

def list_ec2_lgw_route_tables_associations(connection, module: AnsibleAWSModule) -> None:
    lgw_route_table_id = module.params.get("lgw_route_table_id")
    vpc_id = module.params.get("vpc_id")
    lgw_route_table_vpc_association_id = module.params.get("lgw_route_table_vpc_association_id")

    if lgw_route_table_vpc_association_id:
        filters = ansible_dict_to_boto3_filter_list({"local-gateway-route-table-vpc-association-id": lgw_route_table_vpc_association_id})
    elif vpc_id and lgw_route_table_id:
        filters = ansible_dict_to_boto3_filter_list({"vpc-id": vpc_id, "local-gateway-route-table-id": lgw_route_table_id})
    elif vpc_id:
        filters = ansible_dict_to_boto3_filter_list({"vpc-id": vpc_id})
    elif lgw_route_table_id:
      filters = ansible_dict_to_boto3_filter_list({"local-gateway-route-table-id": lgw_route_table_id})

    try:
        lgw_route_table_associations = describe_lgw_route_table_associations(connection, Filters=filters)
    except AnsibleEC2Error as e:
        module.fail_json_aws_error(e)

    for i in range(len(lgw_route_table_associations)):
        lgw_route_table_associations[i]["Tags"] = boto3_tag_list_to_ansible_dict(lgw_route_table_associations[i]["Tags"])

    module.exit_json(changed=False, result=lgw_route_table_associations)


def main() -> None:
    argument_spec = dict(
        vpc_id=dict(),
        lgw_route_table_vpc_association_id=dict(type="str"),
        lgw_route_table_id=dict(type="str"),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        required_one_of=[
            ["vpc_id", "lgw_route_table_vpc_association_id", "lgw_route_table_id"],
        ],
        supports_check_mode=True,
    )

    connection = module.client("ec2")

    list_ec2_lgw_route_tables_associations(connection, module)


if __name__ == "__main__":
    main()