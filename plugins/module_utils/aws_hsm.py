# -*- coding: utf-8 -*-
# Copyright: (c) 2021, TachTech <info@tachtech.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""AWS HSM Module."""
from __future__ import absolute_import, division, print_function

import configparser
import os
import re
from os.path import expanduser
from typing import Any, NoReturn, Union

import boto3
from ansible.errors import AnsibleActionFail
from botocore.exceptions import ClientError

__metaclass__ = type


class Validator(object):
    """Argument validation class."""

    def __init__(self, module_args: dict[str, Any], play_vars: dict[str, Any]):
        self.play_vars = play_vars
        self.module_args = module_args
        self.config = configparser.ConfigParser()

    def _regex_check(self, arg: str, value: str, regex_pattern: str) -> None:
        """Checks if subnet_id start with correct syntax

        Args:
            arg (str): Argument name
            value (str): Value to check
            regex_pattern (str): Regex pattern to check against

        Raises:
            AnsibleActionFail: If value does not match the given regex
        """
        if not re.match(rf"{regex_pattern}", value):
            raise AnsibleActionFail(
                f"The value of the '{arg}' must comply with '{regex_pattern}' regex pattern. Provided: {value}"
            )

    def auth(self) -> NoReturn:  # type: ignore
        """Validates if necessary AWS authentication information is provided."""
        aws_access_key: Any = self.play_vars.get(
            "aws_access_key", self.module_args.get("aws_access_key", None)
        )
        aws_secret_key: Any = self.play_vars.get(
            "aws_secret_key", self.module_args.get("aws_secret_key", None)
        )
        if not self.config.read(f"{expanduser('~')}/.aws/credentials"):
            if aws_access_key:
                os.environ["AWS_ACCESS_KEY_ID"] = aws_access_key
            else:
                if not os.getenv("AWS_ACCESS_KEY_ID"):
                    raise AnsibleActionFail(
                        "AWS Access Key could not be located. Either place the credential in the '~/.aws/credentials' file, or provide it as either a 'aws_access_key' Ansible variable or a 'AWS_ACCESS_KEY_ID' environmental variable."
                    )
            if aws_secret_key:
                os.environ["AWS_SECRET_ACCESS_KEY"] = aws_secret_key
            else:
                if not os.getenv("AWS_SECRET_ACCESS_KEY"):
                    raise AnsibleActionFail(
                        "AWS Secret Access Key could not be located. Either place the credential in the '~/.aws/credentials' file, or provide it as either a 'aws_secret_key' Ansible variable or a 'AWS_SECRET_ACCESS_KEY' environmental variable."
                    )
        elif "default" in self.config.sections():
            if not "aws_access_key_id" in self.config.options(section="default"):
                raise AnsibleActionFail(
                    "AWS Access Key was not located in the '~/.aws/credentials' file. Make sure the key name is set to 'aws_access_key_id'. Also the AWS Access key can be set by using 'aws_access_key' Ansible variable or a 'AWS_ACCESS_KEY_ID' environmental variable."
                )
            if not "aws_secret_access_key" in self.config.options(section="default"):
                raise AnsibleActionFail(
                    "AWS Secret Access Key was not located in the '~/.aws/credentials' file. Make sure the key name is set to 'aws_secret_access_key'. Also the AWS Access key can be set by using 'aws_secret_key' Ansible variable or a 'AWS_SECRET_ACCESS_KEY' environmental variable."
                )
        else:
            raise AnsibleActionFail(
                "Something went wrong. No AWS credentials were found in task arguments ('aws_secret_key' and 'aws_access_key'), in variables ('aws_secret_key' and 'aws_access_key'), in the environmental variables ('AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY'), and/or in ~/.aws/credentials file."
            )

    def region(self) -> NoReturn:  # type: ignore
        """Validate if necessary AWS region information is provided."""
        region: Any = self.play_vars.get(
            "aws_region", self.module_args.get("region", None)
        )
        self.config.read(f"{expanduser('~')}/.aws/config")
        if not self.config.sections():
            if region:
                os.environ["AWS_DEFAULT_REGION"] = region
            elif not os.getenv("AWS_DEFAULT_REGION"):
                raise AnsibleActionFail(
                    "AWS Default Region could not be located. Either place the information in the '~/.aws/config' file, or provide it as either a 'aws_region' Ansible variable or a 'AWS_DEFAULT_REGION' environmental variable."
                )
        elif "default" in self.config.sections():
            if not self.config.get(section="default", option="region"):
                raise AnsibleActionFail(
                    "AWS Default Region could not be located. Either place the information in the '~/.aws/config' file, or provide it as either a 'aws_region' Ansible variable or a 'AWS_DEFAULT_REGION' environmental variable."
                )
        else:
            raise AnsibleActionFail(
                "Something went wrong. No default AWS region was found in task arguments ('region'), in variables ('region'), in the environmental variables ('AWS_DEFAULT_REGION'), and/or in ~/.aws/config file."
            )

    def state(self) -> NoReturn:  # type: ignore
        """Validate if necessary state information is provided."""
        try:
            state = self.module_args["state"]
            if state not in ["present", "absent"]:
                raise ValueError(
                    f"Wrong value was provided to the 'state' argument. Must be either 'present' or 'absent'. Provided: '{str(state)}'"
                )
        except KeyError as key_error:
            raise AnsibleActionFail("'state' is a mandatory argument.") from key_error
        except ValueError as value_error:
            raise AnsibleActionFail(value_error) from value_error

    def cluster_id(self, mandatory: bool = False):
        """Validate if necessary cluster_id information is provided."""
        cluster_id: Any = self.module_args.get("cluster_id")  # type: ignore
        if not cluster_id and mandatory:
            raise AnsibleActionFail("'cluster_id' is a mandatory argument.")
        if cluster_id:
            if not mandatory and not isinstance(cluster_id, (str, list)):
                raise AnsibleActionFail(
                    f"Wrong type was provided for the 'cluster_id' argument. Must be a string or a list. Provided: {type(cluster_id).__name__}"
                )
            if mandatory and not isinstance(cluster_id, str):
                raise AnsibleActionFail(
                    f"Wrong type was provided for the 'cluster_id' argument. Must be a string. Provided: {type(cluster_id).__name__}"
                )
            if isinstance(cluster_id, str):
                self._regex_check("cluster_id", cluster_id, "^cluster-.*")
            elif isinstance(cluster_id, list):
                for cluster in cluster_id:
                    self._regex_check("cluster_id", cluster, "^cluster-.*")

    def name(self, mandatory: bool = False):
        """Validates if necessary name info is provided."""
        name: Any = self.module_args.get("name")  # type: ignore
        if not name and mandatory:
            raise AnsibleActionFail("'name' is a mandatory argument.")
        if name:
            if not isinstance(name, str):
                raise AnsibleActionFail(
                    f"Wrong type was provided for the 'name' argument. Must be a string. Provided: {type(name).__name__}"
                )

    def main_validation(self) -> NoReturn:  # type: ignore
        """Main validator."""
        self.auth()
        self.region()
        self.state()


class AwsHsm(object):
    """Main HSM class"""

    def __init__(self) -> None:
        self.client: Any = boto3.client("cloudhsmv2")  # type: ignore

    def _get_cluster(self, filters: dict[str, Any] = dict()) -> list[Any]:
        """Returns cluster information from the provided data.

        Args:
            filters (dict, optional): Query filters. Defaults to empty dict.

        Raises:
            AnsibleActionFail: Raises when authentication information is invalid.

        Returns:
            (list): Cluster information
        """
        filter_dict: dict[str, Any] = {"Filters": {}}
        cluster_ids: Union[dict[str, Any], None] = filters.get(
            "cluster_id", filters.get("hsm_cluster_id")
        )
        states: Any = filters.get("state")
        name: Any = filters.get("name")
        if cluster_ids:
            if isinstance(cluster_ids, str):
                filter_dict["Filters"].update({"clusterIds": [cluster_ids]})
            elif isinstance(cluster_ids, list):
                filter_dict["Filters"].update({"clusterIds": cluster_ids})
        if states:
            if isinstance(states, str) and states not in ["present", "absent"]:
                filter_dict["Filters"].update({"states": [states]})
            elif isinstance(states, list):
                filter_dict["Filters"].update({"states": states})
        try:
            aws_data = self.client.describe_clusters(**filter_dict)
        except ClientError as client_error:
            raise AnsibleActionFail(
                f"Something went wrong while obtaining HSM cluster information. Reason: {client_error}"
            ) from client_error
        if name:
            clusters: list[Any] = []
            for cluster in aws_data["Clusters"]:
                for tag in cluster["TagList"]:
                    if tag["Key"] == "name" and tag["Value"] == name:
                        clusters.append(cluster)
            return clusters
        return aws_data["Clusters"]

    def _get_hsm(
        self, filters: dict[str, Any], extend_search: bool = False
    ) -> list[Any]:
        """Returns all available HSMs for particular HSM Cluster.

        Args:
            filters (dict): Query filters.
            extend_search (bool): Do extended search for particular HSM. Defaults to False.

        Raises:
            AnsibleActionFail: Raises when authentication information is invalid.

        Returns:
            (list): List of HSM if any available
        """

        def _find_hsm(
            key_name: str, expected_value: str
        ) -> Union[dict[str, Any], dict[None]]:
            """Find a particular HSM

            Args:
                hsms (list[dict[str, Any]]): Lists of HSMs
                key_name (str): HSM key names 'EniId', 'EniIp', 'HsmId', 'State'
                expected_value (str): Value to check for match

            Returns:
                Union[dict[str, Any], dict[None]]: If found desired HSM return as dict, if not return empty dict
            """
            hsms_to_return: Any = []
            for hsm in hsms:
                if hsm[key_name] == expected_value:
                    hsms_to_return.append(hsm)
            return hsms_to_return

        hsm_cluster = self._get_cluster(filters)
        # TODO: Find better logic on how to do this
        if hsm_cluster:
            hsms = [
                hsm for cluster in hsm_cluster for hsm in cluster["Hsms"]
            ]  # All HSMs across all HSM Clusters
            hsms_to_return: list[dict[str, Any]] = list()
            temp_hsms: list[Union[list[dict[str, Any]], list[None]]] = list()
            eni_id: Union[str, list[Any], None] = filters.get("eni_id")
            hsm_id: Union[str, list[Any], None] = filters.get("hsm_id")
            eni_ip: Union[str, list[Any], None] = filters.get("eni_ip")
            state: Union[str, list[Any], None] = filters.get("state")
            if not extend_search:
                return hsms
            if not hsms:
                return hsms
            if not eni_id and not state and not hsm_id and not eni_ip and not state:
                return hsms
            filters = {}
            filters["EniId"] = eni_id
            filters["State"] = state
            filters["EniIp"] = eni_ip
            filters["HsmId"] = hsm_id
            for key, value in filters.items():
                if isinstance(value, str):
                    temp_hsms.append(_find_hsm(key, value))
                elif isinstance(value, list):
                    for _value in value:
                        temp_hsms.append(_find_hsm(key, _value))
            for list_of_hsms in temp_hsms:
                if list_of_hsms:
                    for hsm in list_of_hsms:
                        if hsm not in hsms_to_return:
                            hsms_to_return.append(hsm)
            return hsms_to_return
        elif not extend_search:
            raise AnsibleActionFail(
                "None existing HSM Cluster ID was provided. Please check the cluster ID and re-run the task."
            )
        return []
