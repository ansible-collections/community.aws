#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2022, TachTech LLC <info@tachtech.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: describe_cluster
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
      - UNINITIALIZED
      - INITIALIZE_IN_PROGRESS
      - INITIALIZED
      - ACTIVE
      - UPDATE_IN_PROGRESS
      - DELETE_IN_PROGRESS
      - DELETED
      - DEGRADE
  name:
    description:
      - Filter based on the name of the HSM cluster.
    type: str
    required: false
"""


EXAMPLES = r"""
- name: "Get All HSM Cluster"
  aws.hsm.describe_cluster:
    aws_access_key: HKHKHOIU
    aws_secret_key: 123dkj973&^871623
    region: us-west-2c


- name: "Get All HSM Clusters in INITIALIZED state"
  aws.hsm.describe_cluster:
    state: INITIALIZED

- name: "Get All HSM Clusters in INITIALIZED and ACTIVE state"
  aws.hsm.describe_cluster:
    state:
      - INITIALIZED
      - ACTIVE

- name: "Get HSM Cluster Based on the Cluster ID"
  aws.hsm.describe_cluster:
    cluster_id: cluster_a3231231

- name: "Get HSM Cluster Based on the Multiple Cluster IDs"
  aws.hsm.describe_cluster:
    cluster_id:
      - cluster_a3231231
      - cluster_a3231232

- name: "Get HSM Cluster Based on the Cluster name"
  aws.hsm.describe_cluster:
    name: WestHSMCluster
"""

RETURN = r"""
changed:
  description: This module does not make any changes. The value is always False
  returned: always
  type: bool
  sample: False
data:
  description: HSM Cluster information returned by the AWS.
  returned: always
  type: list
  sample:
    - BackupPolicy: DEFAULT
      BackupRetentionPolicy:
        Type: DAYS
        Value: '90'
      ClusterId: cluster-test
      CreateTimestamp: '2022-07-23T02:08:23.631000-07:00'
      Hsms: []
      HsmType: hsm1.medium
      SecurityGroup: sg-test
      State: UNINITIALIZED
      SubnetMapping:
        us-east-2b: subnet-test
      VpcId: vpc-test
      Certificates: {}
      TagList:
        - Key: sec
          Value: none
        - Key: name
          Value: WestHSMCluster
        - Key: zone
          Value: west
"""
