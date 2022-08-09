# -*- coding: utf-8 -*-
# Copyright: (c) 2022, TachTech  LLC <info@tachtech.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
"""AWS HSM Module Plugin Utilities."""

from __future__ import absolute_import, division, print_function

from ctypes import Union
from ipaddress import ip_address as ip_checker
from typing import Any

from ansible.errors import AnsibleActionFail
from ansible.utils.display import Display
from ansible_collections.community.aws.plugins.module_utils.aws_hsm import (
    AwsHsm,
    Validator,
)
from ansible_collections.community.aws.plugins.module_utils.constants import *

__metaclass__ = type

display = Display()


class CreateHsmValidator(Validator):
    """HsmValidator module args validation."""

    def _ip_check(self, ip: str) -> None:
        """Checks if provided ip is valid

        Args:
            ip (str): IP Address to validate.
        """
        try:
            ip_checker(ip)
        except ValueError as value_error:
            raise AnsibleActionFail(value_error) from value_error

    def availability_zone(self):
        """Validate if necessary availability_zone information is provided."""
        availability_zone: str = self.module_args.get("availability_zone", None)
        state: str = self.module_args["state"]
        if availability_zone and state == "present":
            if not isinstance(availability_zone, str):
                raise AnsibleActionFail(
                    f"Wrong type was provided for the 'availability_zone' argument. Must be a string. Provided: {type(availability_zone).__name__}"
                )
            if availability_zone not in AVAILABILITY_ZONES:
                raise AnsibleActionFail(
                    f"Invalid value was provided to the 'availability_zone' argument. Allowed values are: {', '.join(AVAILABILITY_ZONES)}. Provided: '{availability_zone}'"
                )
        elif availability_zone and state == "absent":
            display.warning(
                "Since state is set to 'absent', the 'availability_zone' will be ignored."
            )
        elif not availability_zone and state == "present":
            raise AnsibleActionFail("'availability_zone' is a mandatory argument.")

    def count(self):
        """Validates if necessary count info is provided."""
        count = self.module_args.get("count")
        if count:
            if not isinstance(count, int):
                try:
                    int(count)
                except TypeError as value_error:
                    raise AnsibleActionFail(
                        f"Wrong type was provided for the 'count' argument. Must be a integer. Provided: {type(count).__name__}"
                    ) from value_error
            if int(count) > 3 or int(count) < 0:
                raise AnsibleActionFail(
                    f"'count' value cannot be less than 0 and more than 3. Provided: {count}"
                )

    def ip_address(self):
        """Validates if necessary ip_address info is provided."""
        ip_addr: str = self.module_args.get("ip_address")
        count = int(self.module_args.get("count", 1))
        state: str = self.module_args["state"]
        if ip_addr and state == "present":
            if not isinstance(ip_addr, (str, list)):
                raise AnsibleActionFail(
                    f"Wrong type was provided for the 'ip_address' argument. Must be either a string or a list. Provided: {type(ip_addr).__name__}"
                )
            if isinstance(ip_addr, str):
                if count != 1:
                    raise AnsibleActionFail(
                        f"Since only one 'ip_address' is provided, 'count' value cannot be more than 1. Provided: {count}"
                    )
                self._ip_check(ip_addr)
            if isinstance(ip_addr, list):
                if len(ip_addr) != count:
                    raise AnsibleActionFail(
                        "Number of provided IPs in the list must be equal to the 'count' value."
                    )
                for ip in ip_addr:
                    self._ip_check(ip)
        elif ip_addr and state == "absent":
            display.warning(
                "Since state is set to 'absent', the 'ip_addr' will be ignored."
            )

    def eni_id(self):
        """Validates if necessary eni_id info is provided."""
        eni_id: Union[str, list[str], None] = self.module_args.get("eni_id")
        state: str = self.module_args["state"]
        count: int = int(self.module_args.get("count", 1))
        if eni_id and state == "absent" and count > 1:
            display.warning(
                "For simplicity, if count is set to more than 1 then 'eni_id' argument will be ignored."
            )
            return
        if eni_id and state == "absent":
            if not isinstance(eni_id, (str, list)):
                raise AnsibleActionFail(
                    f"Wrong type was provided for the 'eni_id' argument. Must be either a string or a list. Provided: {type(eni_id).__name__}"
                )
            if isinstance(eni_id, str):
                self._regex_check("eni_id", eni_id, "eni-[0-9a-z].*")
            if isinstance(eni_id, list):
                for _eni_id in eni_id:
                    self._regex_check("eni_id", _eni_id, "eni-[0-9a-z].*")
        elif eni_id and state == "present":
            display.warning(
                "Since state is set to 'present', the 'eni_id' will be ignored."
            )

    def eni_ip(self):
        """Validates if necessary eni_ip info is provided."""
        eni_ip: Union[str, list, None] = self.module_args.get("eni_ip")
        state: str = self.module_args["state"]
        count: int = int(self.module_args.get("count", 1))
        if eni_ip and state == "absent" and count > 1:
            display.warning(
                "For simplicity, if count is set to more than 1 then 'eni_ip' argument will be ignored."
            )
            return
        if eni_ip and state == "absent":
            if not isinstance(eni_ip, (str, list)):
                raise AnsibleActionFail(
                    f"Wrong type was provided for the 'eni_ip' argument. Must be either a string or a list. Provided: {type(eni_ip).__name__}"
                )
            if isinstance(eni_ip, str):
                self._ip_check(eni_ip)
            elif isinstance(eni_ip, list):
                for ip in eni_ip:
                    self._ip_check(ip)
        elif eni_ip and state == "present":
            display.warning(
                "Since state is set to 'present', the 'eni_ip' will be ignored."
            )

    def hsm_id(self):
        """Validates if necessary hsm_id info is provided."""
        hsm_id: Union[str, list, None] = self.module_args.get("hsm_id")
        state: str = self.module_args["state"]
        count: int = int(self.module_args.get("count", 1))
        if hsm_id and state == "absent" and count > 1:
            display.warning(
                "For simplicity, if count is set to more than 1 then 'hsm_id' argument will be ignored."
            )
            return
        if hsm_id and state == "absent":
            if not isinstance(hsm_id, (str, list)):
                raise AnsibleActionFail(
                    f"Wrong type was provided for the 'hsm_id' argument. Must be either a string or a list. Provided: {type(hsm_id).__name__}"
                )
            if isinstance(hsm_id, str):
                self._regex_check("hsm_id", hsm_id, "hsm-[0-9a-z].*")
            elif isinstance(hsm_id, list):
                for _hsm_id in hsm_id:
                    self._regex_check("hsm_id", _hsm_id, "hsm-[0-9a-z].*")
        elif hsm_id and state == "present":
            display.warning(
                "Since state is set to 'present', the 'hsm_id' will be ignored."
            )

    def validate(self):
        """Validate all."""
        self.main_validation()
        self.availability_zone()
        self.cluster_id(mandatory=True)
        self.count()
        self.ip_address()
        self.eni_id()
        self.eni_ip()
        self.hsm_id()


class CreateHsm(AwsHsm):
    """Class to create the AWS HSM device"""

    def __init__(self, module_args: dict[str, str], play_vars: dict) -> None:
        super().__init__()
        self.play_vars = play_vars
        self.module_args = module_args
        CreateHsmValidator(self.module_args, self.play_vars).validate()

    def present(self):
        """Creates HSM Device.

        Returns:
            dict: HSM Device information
        """

        def _create_hsm(request_body: dict[str, Any]) -> dict[str, Any]:
            """Makes request to create HSM

            Args:
                request_body (dict[str, Any]): Contains data necessary to create the HSM

            Raises:
                AnsibleActionFail: If 'self.client.create_hsm' encounters any error

            Returns:
                dict[str, Any]: Returns dictionary of data
            """
            try:
                return self.client.create_hsm(**request_body)["Hsm"]
            except Exception as catch_all_exceptions:
                raise AnsibleActionFail(
                    f"Something went wrong while creating the HSM. Reason: {catch_all_exceptions}"
                ) from catch_all_exceptions

        hsm_body = {
            "ClusterId": self.module_args["cluster_id"],
            "AvailabilityZone": self.module_args["availability_zone"],
        }
        ip_addr = self.module_args.get("ip_address")
        count = self.module_args.get("count", 1)
        hsms = self._get_hsm(self.module_args)
        return_data = []
        if len(hsms) == count or len(hsms) > count:
            return {"changed": False, "data": hsms}
        if int(count) == 1:
            if ip_addr and isinstance(ip_addr, str):
                hsm_body.update({"IpAddress": ip_addr})
            elif ip_addr and isinstance(ip_addr, list):
                hsm_body.update({"IpAddress": ip_addr[0]})
            return_data.append(_create_hsm(hsm_body))
        else:
            if ip_addr:
                for ip_addr in ip_addr[count - (count - len(hsms)) :]:
                    hsm_body.update({"IpAddress": ip_addr})
                    return_data.append(_create_hsm(hsm_body))
            else:
                for _ in range(0, count - len(hsms)):
                    return_data.append(_create_hsm(hsm_body))

        return {"changed": True, "data": return_data}

    def absent(self):
        """Removes HSM Device.

        Returns:
            dict: Changed true if the HSM device deleted else false.
        """

        def _remove_hsm(body: dict[str, Any]) -> None:
            """Method to remove HSM

            Args:
                body (dict[str, Any]): Dictionary containing necessary data to remove HSM

            Raises:
                AnsibleActionFail: If 'self.client.delete_hsm' encounters an error

            Returns:
                None: Nothing is returned
            """
            try:
                self.client.delete_hsm(**body)
            except Exception as catch_all_exceptions:
                raise AnsibleActionFail(
                    f"Something went wrong while removing the HSM. Reason: {catch_all_exceptions}"
                ) from catch_all_exceptions

        hsm_body = {
            "ClusterId": self.module_args["cluster_id"],
        }
        hsms: list[dict[str, Any]] = self._get_hsm(self.module_args)
        count = int(self.module_args.get("count", 1))
        eni_id: Union[str, list[Any], None] = self.module_args.get("eni_id")
        eni_ip: Union[str, list[Any], None] = self.module_args.get("eni_ip")
        hsm_id: Union[str, list[Any], None] = self.module_args.get("hsm_id")

        if not eni_id and not eni_ip and not hsm_id:
            hsm_ids_to_remove = [
                hsm["HsmId"] for index, hsm in enumerate(hsms) if index <= count
            ]
            if not hsm_ids_to_remove:
                return {
                    "changed": False,
                    "msg": f"HSM Cluster {self.module_args['cluster_id']} does not contain any HSMs.",
                }
            for hsm_id in hsm_ids_to_remove:
                hsm_body.update({"HsmId": hsm_id})
                _remove_hsm(hsm_body)
            return {"changed": True}
        elif hsm_id:
            if isinstance(hsm_id, str):
                hsm_body.update({"HsmId": hsm_id})
                _remove_hsm(hsm_body)
                return {"changed": True}
            if isinstance(hsm_id, list):
                for hsm in hsm_id:
                    hsm_body.update({"HsmId": hsm})
                    _remove_hsm(hsm_body)
                return {"changed": True}
        elif eni_ip:
            if isinstance(eni_ip, str):
                hsm_body.update({"EniIp": eni_ip})
                _remove_hsm(hsm_body)
                return {"changed": True}
            if isinstance(eni_ip, list):
                for eni in eni_ip:
                    hsm_body.update({"EniIp": eni})
                    _remove_hsm(hsm_body)
                return {"changed": True}
        elif eni_id:
            if isinstance(eni_id, str):
                hsm_body.update({"EniId": eni_id})
                _remove_hsm(hsm_body)
                return {"changed": True}
            if isinstance(eni_id, list):
                for eni in eni_id:
                    hsm_body.update({"EniId": eni})
                    _remove_hsm(hsm_body)
                return {"changed": True}
