#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2022, TachTech LLC <info@tachtech.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: describe_hsm
short_description: Get HSM information from AWS.
author:
  - Armen Martirosyan (@armartirosyan)
requirements:
  - boto3
description:
  - Get HSM information from AWS.
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
  cluster_id:
    description:
      - The HSM cluster's identifier.
    type: str
    required: false
  state:
    description:
      - Filter based on the state of the HSM cluster.
    type: str
    required: false
    choices:
      - CREATE_IN_PROGRESS
      - ACTIVE
      - DEGRADED
      - DELETE_IN_PROGRESS
      - DELETED
"""


EXAMPLES = r"""
- name: "Get All HSMs Across all HSM Clusters"
  community.aws.describe_hsm:
    aws_access_key: HKHKHOIU
    aws_secret_key: 123dkj973&^871623
    region: us-west-2c


- name: "Get All HSMs in ACTIVE state"
  community.aws.describe_hsm:
    state: ACTIVE

- name: "Get All HSMs in DEGRADED and ACTIVE state"
  community.aws.describe_hsm:
    state:
      - DEGRADED
      - ACTIVE

- name: "Get all HSMs For a Particular Cluster ID"
  community.aws.describe_hsm:
    cluster_id: cluster_a3231231
"""

RETURN = r"""
changed:
  description: This module does not make any changes. The value is always False
  returned: always
  type: bool
  sample: False
data:
  description: HSM information returned by the AWS.
  returned: always
  type: list
  sample:
    - AvailabilityZone: us-east-2b
      ClusterId: cluster-test4
      EniId: eni-test1
      EniIp: 127.0.0.2
      HsmId: hsm-test1
      State: ACTIVE
      StateMessage: HSM created.
      SubnetId: subnet-test
"""
