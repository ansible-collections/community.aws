# -*- coding: utf-8 -*-

# Copyright (c) 2018 Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

DOCUMENTATION = r"""
name: aws_ec
short_description: Elasticache/ec inventory source
description:
  - Get Cache from Amazon Web Services Elasticache.
  - Uses a YAML configuration file that ends with aws_ec.(yml|yaml).
options:
  regions:
    description:
      - A list of regions in which to describe Elasticache instances and clusters. Available regions are listed here
        U(https://docs.aws.amazon.com/fr_fr/AmazonElastiCache/latest/red-ug/RegionsAndAZs.html).
    default: []
  filters:
    description:
      - A dictionary of filter value pairs. Available filters are listed here
        U(https://docs.aws.amazon.com/AmazonElastiCache/latest/APIReference/API_Filter.html).
    default: {}
  strict_permissions:
    description:
      - By default if an AccessDenied exception is encountered this plugin will fail. You can set strict_permissions to
        False in the inventory config file which will allow the restrictions to be gracefully skipped.
    type: bool
    default: True
  statuses:
    description: A list of desired states for instances/clusters to be added to inventory. Set to ['all'] as a shorthand to find everything.
    type: list
    elements: str
    default:
      - creating
      - available
  hostvars_prefix:
    description:
      - The prefix for host variables names coming from AWS.
    type: str
    version_added: 3.1.0
  hostvars_suffix:
    description:
      - The suffix for host variables names coming from AWS.
    type: str
    version_added: 3.1.0
notes:
  - Ansible versions prior to 2.10 should use the fully qualified plugin name 'amazon.aws.aws_ec'.
extends_documentation_fragment:
  - inventory_cache
  - constructed
  - amazon.aws.boto3
  - amazon.aws.common.plugins
  - amazon.aws.region.plugins
  - amazon.aws.assume_role.plugins
author:
  - Your friendly neighbourhood Rafael (@Rafjt/@Raf211)
"""

EXAMPLES = r"""
plugin: amazon.aws.aws_ec
regions:
  - us-east-1
  - ca-central-1
hostvars_prefix: aws_
hostvars_suffix: _ec
"""

try:
    import botocore
except ImportError:
    pass  # will be captured by imported HAS_BOTO3

from ansible.errors import AnsibleError
from ansible.module_utils._text import to_native
from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict
from pprint import pprint

from ansible_collections.amazon.aws.plugins.module_utils.botocore import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.tagging import boto3_tag_list_to_ansible_dict
from ansible_collections.amazon.aws.plugins.module_utils.transformation import ansible_dict_to_boto3_filter_list
from ansible_collections.amazon.aws.plugins.plugin_utils.inventory import AWSInventoryBase

def _find_ec_clusters_with_valid_statuses(replication_groups, cache_clusters, statuses):
    if "all" in statuses:
        return(replication_groups,cache_clusters)
    valid_clusters = []
    for replication_group in replication_groups:
        if replication_group.get("Status") in statuses:
            valid_clusters.append(replication_group)
    for cache_cluster in cache_clusters:
        if cache_cluster.get("CacheClusterStatus") in statuses:
            valid_clusters.append(cache_cluster)
    return valid_clusters

def _add_tags_for_ec_clusters(connection, clusters, strict):
    for cluster in clusters:
        if "ReplicationGroupId" in cluster:
            resource_arn = cluster["ARN"]
        try:
            tags = connection.list_tags_for_resource(ResourceName=resource_arn)["TagList"]
        except is_boto3_error_code("AccessDenied") as e:
            if not strict:
                tags = []
            else:
                raise e
        cluster["Tags"] = tags

def describe_resource_with_tags(func):
    def describe_wrapper(connection, strict=False):
        try:
            results = func(connection=connection,)
            if "ReplicationGroups" in results:
                results = results["ReplicationGroups"]
            else:
                results = results["CacheClusters"]
            _add_tags_for_ec_clusters(connection, results, strict)
        except is_boto3_error_code("AccessDenied") as e:  # pylint: disable=duplicate-except
            if not strict:
                return []
            raise AnsibleError(f"Failed to query ElastiCache: {to_native(e)}")
        except (
            botocore.exceptions.BotoCoreError,
            botocore.exceptions.ClientError,
        ) as e:  # pylint: disable=duplicate-except
            raise AnsibleError(f"Failed to query ElastiCache: {to_native(e)}")

        return results

    return describe_wrapper


@describe_resource_with_tags
def _describe_replication_groups(connection):
    paginator = connection.get_paginator("describe_replication_groups")
    return paginator.paginate().build_full_result()

@describe_resource_with_tags
def _describe_cache_clusters(connection):
    paginator = connection.get_paginator("describe_cache_clusters")
    return paginator.paginate().build_full_result()


class InventoryModule(AWSInventoryBase):
    NAME = "amazon.aws.aws_ec"
    INVENTORY_FILE_SUFFIXES = ("aws_ec.yml", "aws_ec.yaml")

    def __init__(self):
        super().__init__()
        self.credentials = {}

    def _populate(self, replication_groups, cache_clusters):
        group = "aws_ec"
        cluster_group_name = "cluster_group"
        replication_group_name = "replication_group"

        if replication_groups:
            self.inventory.add_group(replication_group_name)
            self._add_hosts(hosts=replication_groups, group=replication_group_name)
            self.inventory.add_child("all", replication_group_name)
        
        if cache_clusters:
            self.inventory.add_group(cluster_group_name)
            self._add_hosts(hosts=cache_clusters, group=cluster_group_name)
            self.inventory.add_child("all", cluster_group_name)

    def _populate_from_source(self, source_data):
        hostvars = source_data.pop("_meta", {}).get("hostvars", {})
        for group in source_data:
            if group == "all":
                continue
            self.inventory.add_group(group)
            hosts = source_data[group].get("hosts", [])
            for host in hosts:
                self._populate_host_vars([host], hostvars.get(host, {}), group)
            self.inventory.add_child("all", group)


    def _add_hosts(self, hosts, group):
        """
        :param hosts: a list of hosts to be added to a group
        :param group: the name of the group to which the hosts belong
        """
        for host in hosts:
            if "replicationgroup" == host["ARN"].split(":")[5]:
                host_type = "replicationgroup"
                host_name = host["ReplicationGroupId"]
            else:
                host_type = "cluster"
                host_name = host["CacheClusterId"]
            
            host = camel_dict_to_snake_dict(host, ignore_list=["Tags"])
            host["tags"] = boto3_tag_list_to_ansible_dict(host.get("tags", []))
            host["type"] = host_type

            if "availability_zone" in host:
                host["region"] = host["availability_zone"][:-1]
            elif "availability_zones" in host:
                host["region"] = host["availability_zones"][0][:-1]

            self.inventory.add_host(host_name, group=group)
            hostvars_prefix = self.get_option("hostvars_prefix")
            hostvars_suffix = self.get_option("hostvars_suffix")
            new_vars = dict()
            for hostvar, hostval in host.items():
                if hostvars_prefix:
                    hostvar = hostvars_prefix + hostvar
                if hostvars_suffix:
                    hostvar = hostvar + hostvars_suffix
                new_vars[hostvar] = hostval
                self.inventory.set_variable(host_name, hostvar, hostval)
            host.update(new_vars)

            strict = self.get_option("strict")
            self._set_composite_vars(self.get_option("compose"), host, host_name, strict=strict)
            self._add_host_to_composed_groups(self.get_option("groups"), host, host_name, strict=strict)
            self._add_host_to_keyed_groups(self.get_option("keyed_groups"), host, host_name, strict=strict)



    def _get_all_replication_groups(self, regions, strict, statuses):
        replication_groups = []
        for connection, _region in self.all_clients("elasticache"):
            replication_groups += _describe_replication_groups(connection, strict=strict)
        sorted_replication_groups = sorted(replication_groups, key=lambda x: x["ReplicationGroupId"])
        return _find_ec_clusters_with_valid_statuses(sorted_replication_groups, [], statuses)

    def _get_all_cache_clusters(self, regions, strict, statuses):
        cache_clusters = []
        for connection, _region in self.all_clients("elasticache"):
            cache_clusters += _describe_cache_clusters(connection, strict=strict)
        sorted_cache_clusters = sorted(cache_clusters, key=lambda x: x["CacheClusterId"])
        return _find_ec_clusters_with_valid_statuses([], sorted_cache_clusters, statuses)
    

    def parse(self, inventory, loader, path, cache=True):
        super().parse(inventory, loader, path, cache=cache)

        regions = self.get_option("regions")
        strict_permissions = self.get_option("strict_permissions")
        statuses = self.get_option("statuses")

        result_was_cached, cached_result = self.get_cached_result(path, cache)
        if result_was_cached:
            self._populate_from_source(cached_result)
            return

        replication_groups = self._get_all_replication_groups(
            regions=regions,
            strict=strict_permissions,
            statuses=statuses,
        )

        cache_clusters = self._get_all_cache_clusters(
            regions=regions,
            strict=strict_permissions,
            statuses=statuses,
        )

        self._populate(replication_groups, cache_clusters)

