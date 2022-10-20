# Copyright: (c) 2022, TachTech <info@tachtech.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


try:
    import botocore
except ImportError:
    pass  # Handled by AnsibleAWSModule

import os

from ansible_collections.amazon.aws.plugins.module_utils.tagging import (
    ansible_dict_to_boto3_tag_list,
)

STATE = ["present", "absent"]

CLUSTER_STATES = [
    "CREATE_IN_PROGRESS",
    "UNINITIALIZED",
    "INITIALIZE_IN_PROGRESS",
    "INITIALIZED",
    "ACTIVE",
    "UPDATE_IN_PROGRESS",
    "DELETE_IN_PROGRESS",
    "DELETED",
    "DEGRADED",
]

HSM_STATES = [
    "CREATE_IN_PROGRESS",
    "ACTIVE",
    "DEGRADED",
    "DELETE_IN_PROGRESS",
    "DELETED",
]


class CloudHsmCluster:
    """Handles CloudHSM Clusters"""

    def __init__(self, module):
        self.module = module
        try:
            self.client = module.client("cloudhsmv2")
        except (
            botocore.exceptions.ClientError,
            botocore.exceptions.BotoCoreError,
        ) as e:
            self.module.fail_json(e, msg="Failed to connect to AWS")

    def describe_cluster(self):
        """Returns cluster information from the provided data.

        Returns:
            (list): Cluster information
        """
        filter_dict = {"Filters": {}}
        cluster_ids = self.module.params.get("cluster_id", [])
        states = self.module.params.get("state", [])
        name = self.module.params.get("name")
        cluster_data = []
        if isinstance(states, str):
            states = []
        try:
            if cluster_ids:
                if isinstance(cluster_ids, str):
                    cluster_ids = cluster_ids.split()
                for cluster_id in cluster_ids:
                    filter_dict["Filters"].update({"clusterIds": [cluster_id]})
                    cluster_data.extend(
                        self.client.describe_clusters(**filter_dict)["Clusters"]
                    )
            if states:
                for state in states:
                    filter_dict["Filters"].update({"states": [state]})
                    cluster_data.extend(
                        self.client.describe_clusters(**filter_dict)["Clusters"]
                    )
            if not cluster_ids and not states:
                cluster_data.extend(
                    self.client.describe_clusters(**filter_dict)["Clusters"]
                )
        except Exception as catch_all:
            self.module.fail_json(
                msg=f"Exception raised while obtaining cluster information: {str(catch_all)}"
            )
        if name:
            clusters = []
            for cluster in cluster_data:
                for tag in cluster["TagList"]:
                    if tag["Key"] == "name" and tag["Value"] == name:
                        clusters.append(cluster)
            return clusters
        return cluster_data

    def create_cluster(self):
        """Creates CloudHSM Cluster

        Returns:
            (dict): Created cluster information
        """
        cluster_body = {
            "BackupRetentionPolicy": {
                "Type": "DAYS",
                "Value": self.module.params["backup_retention_days"],
            },
            "HsmType": "hsm1.medium",
            "SubnetIds": self.module.params["subnet_ids"],
            "TagList": [
                {"Key": "name", "Value": self.module.params["name"]},
            ],
        }
        if self.module.params.get("tags"):
            cluster_body["TagList"].extend(
                ansible_dict_to_boto3_tag_list(self.module.params.get("tags"))
            )
        try:
            return self.client.create_cluster(**cluster_body)["Cluster"]
        except Exception as catch_all:
            self.module.fail_json(
                msg=f"Exception raised while creating cluster '{self.module.params['name']}': {str(catch_all)}"
            )

    def delete_cluster(self, cluster_id):
        """Deletes CloudHsm Cluster

        Args:
            cluster_id (str): CloudHSM Cluster ID

        Returns:
            (dict): Information about deleted cluster
        """
        try:
            return self.client.delete_cluster(ClusterId=cluster_id)
        except Exception as catch_all:
            self.module.fail_json(
                msg=f"Exception raised while deleting cluster '{self.module.params['name']}': {str(catch_all)}"
            )

    def initialize(self, cluster_id):
        """Initializes the HSM Cluster.

        Args:
            cluster_id (str): Cluster_ID to initialize
        """
        init_body = {"ClusterId": cluster_id}
        signed_cert = self.module.params["signed_cert"]
        trust_anchor = self.module.params["trust_anchor"]
        if os.path.isfile(signed_cert):
            with open(signed_cert) as _file:
                init_body["SignedCert"] = _file.read()
        else:
            init_body["SignedCert"] = signed_cert
        if os.path.isfile(trust_anchor):
            with open(trust_anchor) as _file:
                init_body["TrustAnchor"] = _file.read()
        else:
            init_body["TrustAnchor"] = trust_anchor
        try:
            self.client.initialize_cluster(**init_body)
            return True
        except Exception as catch_all:
            self.module.fail_json(
                msg=f"Exception raised while initializing cluster: {str(catch_all)}"
            )

    def create_hsm(self, request_body):
        """Creates HSM Devices

        Args:
            request_body (dict): Dictionary containing information to create new HSM

        Returns:
            dict[str, Any]: Returns dictionary of data
        """
        try:
            return self.client.create_hsm(**request_body)["Hsm"]
        except Exception as catch_all:
            self.module.fail_json(
                msg=f"Exception raised while creating HSM: {catch_all}"
            )

    def delete_hsm(self, request_body):
        """Deletes HSM Devices

        Args:
            request_body (dict): Dictionary containing information to delete HSM

        Returns:
            None
        """
        try:
            self.client.delete_hsm(**request_body)
        except Exception as catch_all:
            self.module.json_fail(f"Exception raised while deleting HSM: {catch_all}")

    def describe_hsm(self, extend_search=False):
        """Returns all available HSMs for particular HSM Cluster.

        Args:
            extend_search (bool): Do extended search for particular HSM. Defaults to False.

        Returns:
            (list): List of HSM if any available
        """

        def _find_hsm(key_name, expected_value):
            """Find a particular HSM

            Args:
                key_name (str): HSM key names 'EniId', 'EniIp', 'HsmId', 'State'
                expected_value (str): Value to check for match

            Returns:
                Union[list[Any], list[None]]: If found desired HSM return as list, if not return empty list
            """
            hsms_to_return = []
            for hsm in hsms:
                if hsm[key_name] == expected_value:
                    hsms_to_return.append(hsm)
            return hsms_to_return

        hsm_cluster = self.describe_cluster()
        hsms_to_return = []
        # TODO: Find better logic on how to do this
        if hsm_cluster:
            hsms = [
                hsm for cluster in hsm_cluster for hsm in cluster["Hsms"]
            ]  # All HSMs across all HSM Clusters
            temp_hsms = []
            eni_id = self.module.params.get("eni_id")
            hsm_id = self.module.params.get("hsm_id")
            eni_ip = self.module.params.get("eni_ip")
            state = self.module.params.get("state")
            if isinstance(state, str):
                state = []
            if not extend_search:
                return hsms
            if not hsms:
                return hsms
            if not eni_id and not state and not hsm_id and not eni_ip:
                return hsms
            filters = {
                "EniId": eni_id,
                "State": state,
                "EniIp": eni_ip,
                "HsmId": hsm_id,
            }

            # Example Data:
            # filters = {
            #     "EniId": None,
            #     "State": ["ACTIVE", "CREATE_IN_PROGRESS"],
            #     "EniIp": ["192.168.0.1"],
            #     "HsmId": None
            #     }
            for key, value in filters.items():
                for _value in value:
                    temp_hsms.extend(_find_hsm(key, _value))
            if temp_hsms:
                for hsm in temp_hsms:
                    if hsm not in hsms_to_return:
                        hsms_to_return.append(hsm)
            return hsms_to_return
        elif not extend_search:
            self.module.fail_json(
                msg=f"Unable to find CloudHSM Cluster with given argument \
                    '{'name: '+self.module.params['name'] if self.module.params['name'] else 'cluster_id:'+self.module.params['cluster_id'] }'. \
                        Please check the value and re-run the task. {hsm_cluster}"
            )
        return []
