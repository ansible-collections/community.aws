#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
module: medialive_cluster
short_description: Manage AWS MediaLive Anywhere clusters
version_added: 10.1.0
description:
  - A module for creating, updating and deleting AWS MediaLive Anywhere clusters.
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
  state:
    description:
      - Create/update or remove the cluster.
    required: false
    choices: ['present', 'absent']
    default: 'present'
    type: str
  cluster_type:
    description:
      - The hardware type for the cluster.
      - Currently only 'ON_PREMISES' is supported.
      - Required when creating a new cluster.
    type: str
    required: false
    default: 'ON_PREMISES'
    choices: ['ON_PREMISES']
  instance_role_arn:
    description:
      - The ARN of the IAM role for the Node in this Cluster.
      - The role must include all the operations that you expect these Nodes to perform.
      - Required when creating a new cluster.
    type: str
    required: false
  network_settings:
    description:
      - Network settings that connect the Nodes in the Cluster to one or more of the Networks.
      - Required when creating a new cluster.
    type: dict
    required: false
    suboptions:
      default_route:
        description:
          - The network interface that is the default route for traffic to and from the node.
          - This should match one of the logical interface names defined in interface_mappings.
        type: str
        required: true
      interface_mappings:
        description:
          - An array of interface mapping objects for this Cluster.
          - Each mapping logically connects one interface on the nodes with one Network.
        type: list
        elements: dict
        required: true
        suboptions:
          logical_interface_name:
            description:
              - The logical name for one interface that handles a specific type of traffic.
            type: str
            required: true
          network_id:
            description:
              - The ID of the network to connect to the specified logical interface name.
            type: str
            required: true
  wait:
    description:
      - Whether to wait for the cluster to reach the desired state.
      - When I(state=present), wait for the cluster to reach the ACTIVE state.
      - When I(state=absent), wait for the cluster to be deleted.
    type: bool
    required: false
    default: true
  wait_timeout:
    description:
      - The maximum time in seconds to wait for the cluster to reach the desired state.
      - Defaults to 600 seconds.
    type: int
    required: false
    default: 600

extends_documentation_fragment:
  - amazon.aws.common.modules
  - amazon.aws.region.modules
  - amazon.aws.boto3
"""

EXAMPLES = r"""
# Create a MediaLive Anywhere cluster
- community.aws.medialive_cluster:
    name: 'ExampleCluster'
    state: present
    cluster_type: 'ON_PREMISES'
    instance_role_arn: 'arn:aws:iam::123456789012:role/MediaLiveAnywhereNodeRole'
    network_settings:
      default_route: 'management'
      interface_mappings:
        - logical_interface_name: 'management'
          network_id: 'network-1234abcd'
        - logical_interface_name: 'input'
          network_id: 'network-5678efgh'
    tags:
      Environment: 'Production'
      Project: 'MediaLive'

# Delete a MediaLive Anywhere cluster
- community.aws.medialive_cluster:
    name: 'ExampleCluster'
    state: absent
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
    tags:
      description: The tags assigned to the cluster.
      type: dict
      returned: success
      example: {"Environment": "Production", "Project": "MediaLive"}
"""

import uuid
from typing import Dict, Literal

try:
    from botocore.exceptions import WaiterError, ClientError, BotoCoreError
except ImportError:
    pass # caught by AnsibleAWSModule

from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict, snake_dict_to_camel_dict, recursive_diff
from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.botocore import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.exceptions import AnsibleAWSError


class MediaLiveClusterManager:
    """Manage AWS MediaLive Anywhere clusters"""

    def __init__(self, module: AnsibleAWSModule):
        """
        Initialize the MediaLiveClusterManager

        Args:
            module: AnsibleAWSModule instance
        """
        self.module = module
        self.client = module.client('medialive')
        self._cluster = {}
        self.changed = False

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

    def do_create_cluster(self, params):
        """
        Create a new MediaLive cluster
        
        Args:
            params: Parameters for cluster creation
        """
        allowed_params = ['cluster_type', 'instance_role_arn', 'name', 'network_settings', 'request_id']
        required_params = ['instance_role_arn', 'name', 'network_settings']

        for param in required_params:
            if not params.get(param):
                raise AnsibleAWSError(message=f'The {param} parameter is required when creating a new cluster')

        create_params = { k: v for k, v in params.items() if k in allowed_params and v }
        create_params = snake_dict_to_camel_dict(create_params, capitalize_first=True)

        try:
            response = self.client.create_cluster(**create_params)  # type: ignore
            self.cluster = camel_dict_to_snake_dict(response)
            self.changed = True
        except (ClientError, BotoCoreError) as e: # type: ignore
            raise AnsibleAWSError(
                message='Unable to create Medialive Cluster',
                exception=e
            )

    def do_update_cluster(self, params):
        """
        Update a new MediaLive cluster
        
        Args:
            params: Parameters for cluster update
        """
        if not params.get('cluster_id'):
            raise AnsibleAWSError(message='The cluster_id parameter is required during cluster update.')

        allowed_params = ['cluster_id', 'name', 'network_settings']


        current_params = { k: v for k, v in self.cluster.items() if k in allowed_params }
        update_params = { k: v for k, v in params.items() if k in allowed_params and v }

        # Short circuit
        if not recursive_diff(current_params, update_params):
            return

        update_params = snake_dict_to_camel_dict(update_params, capitalize_first=True)

        try:
            response = self.client.update_cluster(**update_params)  # type: ignore
            self.cluster = camel_dict_to_snake_dict(response)
            self.changed = True
        except (ClientError, BotoCoreError) as e: # type: ignore
            raise AnsibleAWSError(
                message='Unable to update Medialive Cluster',
                exception=e
            )

    def get_cluster_by_name(self, name: str):
        """
        Find a cluster by name

        Args:
            name: The name of the cluster to find
        """
        try:
            paginator = self.client.get_paginator('list_clusters') # type: ignore
            found = []
            for page in paginator.paginate():
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
            return True
        except is_boto3_error_code('ResourceNotFoundException'):
            self.cluster = {}

    def delete_cluster(self, cluster_id: str):
        """
        Delete a MediaLive cluster
        
        Args:
            cluster_id: ID of the cluster to delete
        """
        try:
            self.client.delete_cluster(ClusterId=cluster_id)  # type: ignore
            self.changed = True
        except is_boto3_error_code('ResourceNotFoundException'):
            self.cluster = {}
        except (ClientError, BotoCoreError) as e: # type: ignore
            raise AnsibleAWSError(
                message='Unable to delete Medialive Cluster',
                exception=e
            )

    def wait_for(
        self,
        want: Literal['cluster_created', 'cluster_deleted'],
        cluster_id: str,
        wait_timeout = 60
    ):
        """
        Invoke one of the custom waiters and wait

        Args:
            want: the name of the waiter
            cluster_id: the ID of the cluster
            wait_timeout: the maximum amount of time to wait in seconds (default: 60)
        """

        try:
            waiter = self.client.get_waiter(want) # type: ignore
            config = {
                'Delay': min(5, wait_timeout),
                'MaxAttempts': wait_timeout // 5
            }
            waiter.wait(
                ClusterId=cluster_id,
                WaiterConfig=config
            )
        except WaiterError as e: # type: ignore
            raise AnsibleAWSError(
                message=f'Timeout waiting for cluster state to become {cluster_id}',
                exception=e
            )

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
        state=dict(type='str', default='present', choices=['present', 'absent']),
        cluster_type=dict(type='str', required=False, default='ON_PREMISES', choices=['ON_PREMISES']),
        instance_role_arn=dict(type='str', required=False),
        network_settings=dict(
            type='dict',
            required=False,
            options=dict(
                default_route=dict(type='str', required=True),
                interface_mappings=dict(
                    type='list',
                    elements='dict',
                    required=True,
                    options=dict(
                        logical_interface_name=dict(type='str', required=True),
                        network_id=dict(type='str', required=True),
                    )
                )
            )
        ),
        wait=dict(type='bool', default=True),
        wait_timeout=dict(type='int', default=600),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[('id', 'cluster_id', 'name', 'cluster_name')]
    )

    # Extract module parameters
    cluster_id = get_arg('id', module.params, argument_spec)
    cluster_name = get_arg('name', module.params, argument_spec)
    state = get_arg('state', module.params, argument_spec)
    cluster_type = get_arg('cluster_type', module.params, argument_spec)
    instance_role_arn = get_arg('instance_role_arn', module.params, argument_spec)
    network_settings = get_arg('network_settings', module.params, argument_spec)
    wait = get_arg('wait', module.params, argument_spec)
    wait_timeout = get_arg('wait_timeout', module.params, argument_spec)

    # Initialize the manager
    manager = MediaLiveClusterManager(module)

    # Find the cluster by ID or name
    # Update manager.cluster with the details
    if cluster_id:
        manager.get_cluster_by_id(cluster_id)
    elif cluster_name:
        manager.get_cluster_by_name(cluster_name)
        cluster_id = manager.cluster.get('cluster_id')

    # Do nothing in check mode
    if module.check_mode:
        module.exit_json(changed=True)

    # Handle present state
    if state == 'present':

        # Case update
        if manager.cluster:
            update_params = {
                'name': cluster_name,
                'network_settings': network_settings,
                'cluster_id': cluster_id
            }

            manager.do_update_cluster(update_params)

        # Case create
        else:
            create_params = {
                'name': cluster_name,
                'cluster_type': cluster_type,
                'instance_role_arn': instance_role_arn,
                'network_settings': network_settings,
                'cluster_id': cluster_id,
                'request_id': str(uuid.uuid4())
            }

            manager.do_create_cluster(create_params)
            cluster_id = manager.cluster.get('cluster_id')

            # Wait for the cluster to be created
            if wait and cluster_id:
                manager.wait_for('cluster_created', cluster_id, wait_timeout) # type: ignore
                manager.get_cluster_by_id(cluster_id)

    # Handle absent state
    elif state == 'absent':
        if manager.cluster:
            # Cluster exists, delete it
            cluster_id = manager.cluster.get('cluster_id')
            manager.delete_cluster(cluster_id) # type: ignore
            
            # Wait for the cluster to be deleted if requested
            if wait and cluster_id:
                manager.wait_for('cluster_deleted', cluster_id, wait_timeout) # type: ignore

    module.exit_json(changed=manager.changed, cluster=manager.cluster)

if __name__ == '__main__':
    main()
