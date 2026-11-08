#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
module: medialive_cluster
short_description: Gather MediaLive Anywhere cluster info
version_added: 10.1.0
description:
  - Get details about a AWS MediaLive Anywhere cluster.
  - This module requires boto3 >= 1.35.17.
author:
  - Sergey Papyan (@r363x)
options:
  id:
    description:
      - The ID of the cluster.
      - Exactly one of I(id) or I(name) must be provided.
    required: false
    type: str
    aliases: ['cluster_id']
  name:
    description:
      - The name of the cluster.
      - Exactly one of I(id) or I(name) must be provided.
    required: false
    type: str
    aliases: ['cluster_name']

extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
# Find a MediaLive Anywhere cluster by ID
- community.aws.medialive_cluster_info:
    id: '1234567'
  register: found_cluster

# Find a MediaLive Anywhere cluster by name
- community.aws.medialive_cluster_info:
    name: 'ExampleCluster'
  register: found_cluster
"""

RETURN = r"""
cluster:
  description: The details of the cluster
  returned: success
  type: dict
  contains:
    arn:
      description: The ARN of the cluster.
      type: str
      returned: success
      example: "arn:aws:medialive:us-east-1:123456789012:cluster/1234abcd-12ab-34cd-56ef-1234567890ab"
    channel_ids:
      description: The IDs of channels associated with the cluster.
      type: list
      elements: str
      returned: success
      example: ["channel-1234abcd"]
    cluster_type:
      description: The hardware type for the cluster.
      type: str
      returned: success
      example: "ON_PREMISES"
    id:
      description: The ID of the cluster.
      type: str
      returned: success
      example: "1234abcd-12ab-34cd-56ef-1234567890ab"
    instance_role_arn:
      description: The ARN of the IAM role for the Node in this Cluster.
      type: str
      returned: success
      example: "arn:aws:iam::123456789012:role/MediaLiveAnywhereNodeRole"
    name:
      description: The name of the cluster.
      type: str
      returned: success
      example: "ExampleCluster"
    network_settings:
      description: Network settings that connect the Nodes in the Cluster to Networks.
      type: dict
      returned: success
      contains:
        default_route:
          description: The network interface that is the default route for traffic.
          type: str
          returned: success
          example: "management"
        interface_mappings:
          description: An array of interface mapping objects for this Cluster.
          type: list
          elements: dict
          returned: success
          contains:
            logical_interface_name:
              description: The logical name for one interface.
              type: str
              returned: success
              example: "management"
            network_id:
              description: The ID of the network connected to the interface.
              type: str
              returned: success
              example: "network-1234abcd"
    state:
      description: The state of the cluster.
      type: str
      returned: success
      example: "ACTIVE"
"""

from typing import Dict

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict
from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.botocore import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.exceptions import AnsibleAWSError


class MediaLiveClusterGetter:
    '''Look up AWS MediaLive Anywhere clusters'''

    def __init__(self, module: AnsibleAWSModule):
        '''
        Initialize the MediaLiveClusterGetter

        Args:
            module: AnsibleAWSModule instance
        '''
        self.module = module
        self.client = self.module.client('medialive')
        self._cluster = {}

    @property
    def cluster(self):
        return self._cluster

    @cluster.setter
    def cluster(self, cluster: Dict):
        cluster = camel_dict_to_snake_dict(cluster)
        if cluster.get('response_metadata'):
            del cluster['response_metadata']
        if cluster.get('id'):
            cluster['cluster_id'] = cluster.get('id')
            del cluster['id']
        self._cluster = cluster

    def get_cluster_by_name(self, name: str):
        """
        Find a cluster by name

        Args:
            name: The name of the cluster to find
        """
        try:
            paginator = self.client.get_paginator('list_clusters') # type: ignore
            for page in paginator.paginate():
                found = []
                for cluster in page.get('Clusters', []):
                    if cluster.get('Name') == name:
                        found.append(cluster.get('Id'))
                if len(found) > 1:
                    raise AnsibleAWSError(message='Found more than one Clusters under the same name')
                elif len(found) == 1:
                    self.get_cluster_by_id(found[0])
        except (ClientError, BotoCoreError) as e: # type: ignore
            raise AnsibleAWSError(
                message='Unable to get MediaLive Cluster',
                exception=e
            )

    def get_cluster_by_id(self, id: str):
        """
        Get a cluster by ID

        Args:
            id: The ID of the cluster to retrieve
        """
        try:
            self.cluster = self.client.describe_cluster(ClusterId=id) # type: ignore
        except is_boto3_error_code('ResourceNotFoundException'):
            self.cluster = {}

def get_arg(arg:str, params:dict, spec:dict):
    if arg in spec.keys():
        aliases = spec[arg].get('aliases', [])
        for k, v in params.items():
            if k in [arg, *aliases] and v:
                return v

def main():
    """Main entry point for the module"""
    argument_spec = dict(
        id=dict(type='str', required=False, aliases=['cluster_id']),
        name=dict(type='str', required=False, aliases=['cluster_name']),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[('id', 'cluster_id', 'name', 'cluster_name')]
    )

    # Extract module parameters
    cluster_id = get_arg('id', module.params, argument_spec)
    cluster_name = get_arg('name', module.params, argument_spec)

    # Initialize the manager
    getter = MediaLiveClusterGetter(module)

    # Find the cluster by ID or name
    if cluster_id:
        getter.get_cluster_by_id(cluster_id)
    elif cluster_name:
        getter.get_cluster_by_name(cluster_name)

    module.exit_json(changed=False, cluster=getter.cluster)

if __name__ == '__main__':
    main()
