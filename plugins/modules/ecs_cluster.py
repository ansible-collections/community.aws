#!/usr/bin/python
# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = '''
---
module: ecs_cluster
version_added: 1.0.0
short_description: Create or terminate ECS clusters.
notes:
    - When deleting a cluster, the information returned is the state of the cluster prior to deletion.
    - It will also wait for a cluster to have instances registered to it.
description:
    - Creates or terminates ecs clusters.
author: Mark Chance (@Java1Guy)
options:
    state:
        description:
            - The desired state of the cluster.
        required: true
        choices: ['present', 'absent', 'has_instances']
        type: str
    name:
        description:
            - The cluster name.
        required: true
        type: str
    delay:
        description:
            - Number of seconds to wait.
        required: false
        type: int
        default: 10
    repeat:
        description:
            - The number of times to wait for the cluster to have an instance.
        required: false
        type: int
        default: 10
    capacity_providers:
        description:
            - List of capacity providers to use for the cluster.
        required: false
        type: list
        elements: str
    capacity_provider_strategy:
        description:
            - List of capacity provider strategies to use for the cluster.
        required: false
        type: list
        elements: dict
        suboptions:
            capacity_provider:
                description:
                  - Name of capacity provider.
                type: str
            weight:
                description:
                  - The relative percentage of the total number of launched tasks that should use the specified provider.
                type: int
            base:
                description:
                  - How many tasks, at a minimum, should use the specified provider.
                type: int
extends_documentation_fragment:
- amazon.aws.aws
- amazon.aws.ec2
- amazon.aws.boto3

'''

EXAMPLES = '''
# Note: These examples do not set authentication details, see the AWS Guide for details.

- name: Cluster creation
  community.aws.ecs_cluster:
    name: default
    state: present

- name: Cluster creation with capacity providers and strategies.
  community.aws.ecs_cluster:
    name: default
    state: present
    capacity_providers:
      - FARGATE
      - FARGATE_SPOT
    capacity_provider_strategy:
      - capacity_provider: FARGATE
        base: 1
        weight: 1
      - capacity_provider: FARGATE_SPOT
        weight: 100

- name: Cluster deletion
  community.aws.ecs_cluster:
    name: default
    state: absent

- name: Wait for register
  community.aws.ecs_cluster:
    name: "{{ new_cluster }}"
    state: has_instances
    delay: 10
    repeat: 10
  register: task_output

'''
RETURN = '''
activeServicesCount:
    description: how many services are active in this cluster
    returned: 0 if a new cluster
    type: int
capacityProviders:
    description: list of capacity providers used in this cluster
    returned: always
    type: list
defaultCapacityProviderStrategy:
    description: list of capacity provider strategies used in this cluster
    returned: always
    type: list
clusterArn:
    description: the ARN of the cluster just created
    type: str
    returned: 0 if a new cluster
    sample: arn:aws:ecs:us-west-2:123456789012:cluster/test-cluster
clusterName:
    description: name of the cluster just created (should match the input argument)
    type: str
    returned: always
    sample: test-cluster
pendingTasksCount:
    description: how many tasks are waiting to run in this cluster
    returned: 0 if a new cluster
    type: int
registeredContainerInstancesCount:
    description: how many container instances are available in this cluster
    returned: 0 if a new cluster
    type: int
runningTasksCount:
    description: how many tasks are running in this cluster
    returned: 0 if a new cluster
    type: int
status:
    description: the status of the new cluster
    returned: always
    type: str
    sample: ACTIVE
'''

import time

try:
    import botocore
except ImportError:
    pass  # Handled by AnsibleAWSModule

from ansible_collections.community.aws.plugins.module_utils.modules import AnsibleCommunityAWSModule as AnsibleAWSModule
from ansible.module_utils.common.dict_transformations import snake_dict_to_camel_dict


class EcsClusterManager:
    """Handles ECS Clusters"""

    def __init__(self, module):
        self.module = module
        try:
            self.ecs = module.client('ecs')
        except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
            module.fail_json_aws(e, msg='Failed to connect to AWS')

    def find_in_array(self, array_of_clusters, cluster_name, field_name='clusterArn'):
        for c in array_of_clusters:
            if c[field_name].endswith(cluster_name):
                return c
        return None

    def describe_cluster(self, cluster_name):
        response = self.ecs.describe_clusters(clusters=[
            cluster_name
        ])
        if len(response['failures']) > 0:
            c = self.find_in_array(response['failures'], cluster_name, 'arn')
            if c and c['reason'] == 'MISSING':
                return None
            # fall thru and look through found ones
        if len(response['clusters']) > 0:
            c = self.find_in_array(response['clusters'], cluster_name)
            if c:
                return c
        raise Exception("Unknown problem describing cluster %s." % cluster_name)

    def create_cluster(self, cluster_name, capacity_providers, capacity_provider_strategy):
        params = dict(clusterName=cluster_name)
        if capacity_providers:
            params['capacityProviders'] = snake_dict_to_camel_dict(capacity_providers)
        if capacity_provider_strategy:
            params['defaultCapacityProviderStrategy'] = snake_dict_to_camel_dict(capacity_provider_strategy)
        response = self.ecs.create_cluster(**params)
        return response['cluster']

    def update_cluster(self, cluster_name, capacity_providers, capacity_provider_strategy):
        params = dict(cluster=cluster_name)
        if capacity_providers:
            params['capacityProviders'] = snake_dict_to_camel_dict(capacity_providers)
        else:
            params['capacityProviders'] = []
        if capacity_provider_strategy:
            params['defaultCapacityProviderStrategy'] = snake_dict_to_camel_dict(capacity_provider_strategy)
        else:
            params['defaultCapacityProviderStrategy'] = []
        response = self.ecs.put_cluster_capacity_providers(**params)
        return response['cluster']

    def delete_cluster(self, clusterName):
        return self.ecs.delete_cluster(cluster=clusterName)


def main():

    argument_spec = dict(
        state=dict(required=True, choices=['present', 'absent', 'has_instances']),
        name=dict(required=True, type='str'),
        delay=dict(required=False, type='int', default=10),
        repeat=dict(required=False, type='int', default=10),
        capacity_providers=dict(required=False, type='list', elements='str'),
        capacity_provider_strategy=dict(required=False,
                                        type='list',
                                        elements='dict',
                                        options=dict(
                                            capacity_provider=dict(type='str'),
                                            weight=dict(type='int'),
                                            base=dict(type='int')
                                            )
                                        ),
    )
    required_together = [['state', 'name']]

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_together=required_together,
    )

    cluster_mgr = EcsClusterManager(module)
    try:
        existing = cluster_mgr.describe_cluster(module.params['name'])
    except Exception as e:
        module.fail_json(msg="Exception describing cluster '" + module.params['name'] + "': " + str(e))

    results = dict(changed=False)
    if module.params['state'] == 'present':
        if existing and 'status' in existing and existing['status'] == "ACTIVE":
            # Pull requested and existing capacity providers and strategies.
            requested_cp = module.params['capacity_providers']
            requested_cps = module.params['capacity_provider_strategy']
            existing_cp = existing['capacityProviders']
            existing_cps = existing['defaultCapacityProviderStrategy']
            if requested_cp is None:
                requested_cp = []

            # Check if capacity provider strategy needs to trigger an update.
            cps_update_needed = False
            if requested_cps is not None:
                for strategy in requested_cps:
                    if snake_dict_to_camel_dict(strategy) not in existing_cps:
                        cps_update_needed = True

            
            # If either the providers or strategy differ, update the cluster.
            if requested_cp != existing_cp or cps_update_needed:
                if not module.check_mode:
                    results['cluster'] = cluster_mgr.update_cluster(cluster_name=module.params['name'],
                                                                    capacity_providers=requested_cp,
                                                                    capacity_provider_strategy=requested_cps)
                results['changed'] = True
            else:
                results['cluster'] = existing
        else:
            if not module.check_mode:
                # doesn't exist. create it.
                results['cluster'] = cluster_mgr.create_cluster(cluster_name=module.params['name'],
                                                                capacity_providers=module.params['capacity_providers'],
                                                                capacity_provider_strategy=module.params['capacity_provider_strategy'])
            results['changed'] = True

    # delete the cluster
    elif module.params['state'] == 'absent':
        if not existing:
            pass
        else:
            # it exists, so we should delete it and mark changed.
            # return info about the cluster deleted
            results['cluster'] = existing
            if 'status' in existing and existing['status'] == "INACTIVE":
                results['changed'] = False
            else:
                if not module.check_mode:
                    cluster_mgr.delete_cluster(module.params['name'])
                results['changed'] = True
    elif module.params['state'] == 'has_instances':
        if not existing:
            module.fail_json(msg="Cluster '" + module.params['name'] + " not found.")
            return
        # it exists, so we should delete it and mark changed.
        # return info about the cluster deleted
        delay = module.params['delay']
        repeat = module.params['repeat']
        time.sleep(delay)
        count = 0
        for i in range(repeat):
            existing = cluster_mgr.describe_cluster(module.params['name'])
            count = existing['registeredContainerInstancesCount']
            if count > 0:
                results['changed'] = True
                break
            time.sleep(delay)
        if count == 0 and i is repeat - 1:
            module.fail_json(msg="Cluster instance count still zero after " + str(repeat) + " tries of " + str(delay) + " seconds each.")
            return

    module.exit_json(**results)


if __name__ == '__main__':
    main()
