#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2022, TachTech LLC <info@tachtech.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = r"""
---
module: create_cluster
short_description: Create or delete HSM Cluster(s) in AWS.
author:
  - Armen Martirosyan (@armartirosyan)
requirements:
  - boto3
description:
  - Create HSM Cluster in AWS.
  - Delete HSM Cluster in AWS.
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
  backup_retention_days:
    description:
      - Backup retention days for the cluster.
      - Must be a value between 7 and 379.
    type: str
    required: false
    default: 90
  source_backup_id:
    description:
      -  Cluster backup ID to restore the cluster from.
    type: str
    required: false
  subnet_ids:
    description:
      - The ID(s) of subnets where the cluster is being created.
    type: str
    required: false
  tags:
    description:
      - Tags to apply to the HSM cluster.
    type: dict
    required: false
  name:
    description:
      - The name of the cluster.
      - The name will be added as a tag for state keeping.
    type: str
    required: true
  state:
    description:
      - The state of the HSM Cluster. If present, the device will be created, if absent, the device will be removed.
    type: str
    required: true
    choices:
      - present
      - absent
"""


EXAMPLES = r"""
- name: "Create an HSM Cluster"
  aws.hsm.create_cluster:
    aws_access_key: HKHKHOIU
    aws_secret_key: 123dkj973&^871623
    region: us-west-2c
    backup_retention_days: 7
    subnet_ids:
      - subnet-5855b205
    state: present
    name: "West2a_Cluster"

- name: "Create an HSM Cluster With Tags"
  aws.hsm.create_cluster:
    subnet_ids:
      - subnet-5855b205
    state: present
    name: "West2a_Cluster"
    tags:
      zone: west
      sec: none

- name: "Remove HSM Cluster"
  aws.hsm.create_cluster:
    state: absent
    name: "West2a_Cluster"
"""

RETURN = r"""
changed:
  description: Boolean that is true if the command changed the state.
  returned: always
  type: bool
  sample: True
data:
  description: HSM cluster creation information returned by the AWS.
  returned: always
  type: list
  sample:
    - BackupPolicy: DEFAULT
      BackupRetentionPolicy:
      Type: DAYS
      Value: '90'
      Certificates: {}
      ClusterId: cluster-test
      CreateTimestamp: 2022-05-29 21:37:34 -0800
      HsmType: hsm1.medium
      Hsms: []
      State: CREATE_IN_PROGRESS
      SubnetMapping:
      us-west-2c: subnet-test123
      VpcId: vpc-test123
"""
