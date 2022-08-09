#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2022, TachTech LLC <info@tachtech.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: create_hsm
short_description: Create HSM Device in AWS.
author:
  - Armen Martirosyan (@armartirosyan)
requirements:
  - boto3
description:
  - Create HSM Device(s) in AWS's HSM Cluster.
options:
  access_key:
    description:
      - Access Key to authenticate against the AWS.
      - Can be substituted with either aws_access_key ansible variable or AWS_ACCESS_KEY_ID environmental variable.
    type: str
    required: false
  secret_key:
    description:
      - Secret Key to authenticate against the AWS.
      - Can be substituted with either aws_secret_key ansible variable or AWS_SECRET_ACCESS_KEY environmental variable.
    type: str
    required: false
  region:
    description:
      - AWS region setting.
      - Can be substituted with either aws_region ansible variable or AWS_DEFAULT_REGION environmental variable.
    type: str
    required: false
  availability_zone:
    description:
      - Availability Zone where the HSM will be created
    type: str
    required: true
  cluster_id:
    description:
      - The HSM cluster's identifier.
    type: str
    required: true
  ip_address:
    description:
      - IP Address of the HSM device.
    type: str
    required: false
  state:
    description:
      - The state of the HSM Device. If present, the device will be created, if absent, the device will be removed.
    type: str
    required: true
    choices:
      - present
      - absent
  count:
    description:
      - Number of HSM devices that need to be created.
      - The value cannot be greater than 3.
    type: int
    required: true
    default: 1
"""


EXAMPLES = r"""
- name: "Create an HSM Device"
  aws.hsm.create_hsm:
    aws_access_key: HKHKHOIU
    aws_secret_key: 123dkj973&^871623
    region: us-west-2c
    availability_zone: zone_asodaos
    cluster_id: cluster_a3231231
    count: 1
    state: present


- name: "Create an HSM Device with IP"
  aws.hsm.create_hsm:
    availability_zone: zone_asodaos
    cluster_id: cluster_a3231231
    ip_address: 192.168.0.1
    count: 1
    state: present
    vars:
    aws_access_key: HKHKHOIU
    aws_secret_key: 123dkj973&^871623
    aws_region: us-west2

- name: "Create Two HSM Devices with IP"
  aws.hsm.create_hsm:
    availability_zone: zone_asodaos
    cluster_id: cluster_a3231231
    ip_address:
      - 192.168.0.1  # IP address of the first HSM Device
      - 192.168.0.2  # IP address of the second HSM Device
    count: 2
    state: present

- name: "Add Second HSM Devices to the Existing One"
  aws.hsm.create_hsm:
    availability_zone: zone_asodaos
    cluster_id: cluster_a3231231
    count: 2
    state: present

- name: "Remove all HSM Devices"
  aws.hsm.create_hsm:
    cluster_id: cluster_a3231231
    state: absent

- name: "Remove HSM Device Using HSM ID"
  aws.hsm.create_hsm:
    cluster_id: cluster_a3231231
    hsm_id: hsm_asdasd123123
    state: absent

- name: "Remove HSM Device USING ENI ID"
  aws.hsm.create_hsm:
    cluster_id: cluster_a3231231
    eni_id: eni_123asd123
    state: absent

- name: "Remove HSM Device USING ENI IP"
  aws.hsm.create_hsm:
    cluster_id: cluster_a3231231
    eni_ip: 192.168.0.1
    state: absent
"""

RETURN = r"""
changed:
  description: Boolean that is true if the command changed the state.
  returned: always
  type: bool
  sample: True
data:
  description: HSM creation information returned by the AWS.
  returned: always
  type: list
  sample:
    - AvailabilityZone: us-east-2b
      ClusterId: cluster-test4
      EniId: eni-test
      EniIp: 127.0.0.1
      HsmId: hsm-test
      State: ACTIVE
      StateMessage: HSM created.
      SubnetId: subnet-test
"""
