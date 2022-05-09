#!/usr/bin/python
# Copyright (c) 2014 Ansible Project
# Copyright (c) 2021 Alina Buzachis (@alinabuzachis)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = r'''
---
module: rds_cluster_snapshot
version_added: 3.3.0
short_description: Manage Amazon RDS snapshots of DB clusters
description:
  - Creates or deletes RDS snapshots of DB clusters.
options:
  state:
    description:
      - Specify the desired state of the snapshot.
    default: present
    choices: [ 'present', 'absent']
    type: str
  db_snapshot_identifier:
    description:
      - The identifier of the DB cluster snapshot.
    required: true
    aliases:
      - snapshot_id
      - id
      - snapshot_name
    type: str
  db_cluster_identifier:
    description:
      - The identifier of the DB cluster to create a snapshot for.
      - Required when I(state=present).
    aliases:
      - cluster_id
      - cluster_name
    type: str
  wait:
    description:
      - Whether or not to wait for snapshot creation or deletion.
    type: bool
    default: false
  wait_timeout:
    description:
      - How long before wait gives up, in seconds.
    default: 300
    type: int
  tags:
    description:
      - The tags to be assigned to the DB cluster snapshot.
    type: dict
  purge_tags:
    description:
      - Whether to remove tags not present in the C(tags) parameter.
    default: true
    type: bool
author:
    - "Alina Buzachis (@alinabuzachis)"
extends_documentation_fragment:
- amazon.aws.aws
- amazon.aws.ec2
'''

EXAMPLES = r'''
- name: Create a DB cluster snapshot
  community.aws.rds_cluster_snapshot:
    db_cluster_identifier: "{{ cluster_id }}"
    db_snapshot_identifier: new-cluster-snapshot

- name: Delete a DB cluster snapshot
  community.aws.rds_cluster_snapshot:
    db_snapshot_identifier: new-cluster-snapshot
    state: absent
'''

RETURN = r'''
allocated_storage:
  description: Specifies the allocated storage size in gibibytes (GiB).
  returned: always
  type: int
  sample: 20
availability_zone:
  description: Availability zone of the database from which the snapshot was created.
  returned: always
  type: str
  sample: us-west-2a
cluster_create_time:
  description: Specifies the time when the DB cluster was created, in Universal Coordinated Time (UTC).
  returned: always
  type: str
  sample: '2019-06-15T10:15:56.221000+00:00'
db_cluster_identifier:
  description: Specifies the DB cluster identifier of the DB cluster that this DB cluster snapshot was created from.
  returned: always
  type: str
  sample: ansible-test-16638696
db_cluster_snapshot_arn:
  description: Amazon Resource Name for the snapshot.
  returned: always
  type: str
  sample: arn:aws:rds:us-west-2:123456789012:snapshot:ansible-test-16638696-test-snapshot
db_cluster_snapshot_identifier:
  description: Specifies the identifier for the DB cluster snapshot.
  returned: always
  type: str
  sample: ansible-test-16638696-test-snapshot
engine:
  description: Specifies the name of the database engine for this DB cluster snapshot.
  returned: always
  type: str
  sample: "aurora"
engine_mode:
  description: Provides the engine mode of the database engine for this DB cluster snapshot.
  returned: always
  type: str
  sample: "5.6.mysql_aurora.1.22.5"
engine_version:
  description: Version of the cluster from which the snapshot was created.
  returned: always
  type: str
  sample: "5.6.mysql_aurora.1.22.5"
iam_database_authentication_enabled:
  description: Whether IAM database authentication is enabled.
  returned: always
  type: bool
  sample: false
license_model:
  description: Provides the license model information for this DB cluster snapshot.
  returned: always
  type: str
  sample: general-public-license
master_username:
  description: Provides the master username for this DB cluster snapshot.
  returned: always
  type: str
  sample: test
percent_progress:
  description: Specifies the percentage of the estimated data that has been transferred.
  returned: always
  type: int
  sample: 100
port:
  description: Port on which the database is listening.
  returned: always
  type: int
  sample: 3306
snapshot_create_time:
  description: Provides the time when the snapshot was taken, in Universal Coordinated Time (UTC).
  returned: always
  type: str
  sample: '2019-06-15T10:46:23.776000+00:00'
snapshot_type:
  description: How the snapshot was created (always manual for this module!).
  returned: always
  type: str
  sample: manual
status:
  description: Specifies the status of this DB cluster snapshot.
  returned: always
  type: str
  sample: available
storage_encrypted:
  description: Specifies whether the DB cluster snapshot is encrypted.
  returned: always
  type: bool
  sample: false
tag_list:
  description: A list of tags.
  returned: always
  type: list
  sample: []
tags:
  description: Tags applied to the snapshot.
  returned: always
  type: complex
  contains: {}
vpc_id:
  description: ID of the VPC in which the DB lives.
  returned: always
  type: str
  sample: vpc-09ff232e222710ae0
'''

try:
    import botocore
except ImportError:
    pass  # caught by AnsibleAWSModule

from ansible_collections.amazon.aws.plugins.module_utils.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.core import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AWSRetry
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import camel_dict_to_snake_dict
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import ansible_dict_to_boto3_tag_list
from ansible_collections.amazon.aws.plugins.module_utils.rds import get_tags
from ansible_collections.amazon.aws.plugins.module_utils.rds import ensure_tags
from ansible_collections.amazon.aws.plugins.module_utils.rds import call_method


def get_snapshot(snapshot_id):
    try:
        response = client.describe_db_cluster_snapshots(DBClusterSnapshotIdentifier=snapshot_id)
    except is_boto3_error_code("DBClusterSnapshotNotFoundFault"):
        return None
    except is_boto3_error_code("DBClusterSnapshotNotFound"):  # pylint: disable=duplicate-except
        return None
    except (botocore.exceptions.BotoCoreError, botocore.exceptions.ClientError) as e:  # pylint: disable=duplicate-except
        module.fail_json_aws(e, msg="Couldn't get snapshot {0}".format(snapshot_id))
    return response["DBClusterSnapshots"][0]


def fetch_tags(snapshot):
    snapshot["Tags"] = get_tags(client, module, snapshot["DBClusterSnapshotArn"])
    return camel_dict_to_snake_dict(snapshot, ignore_list=["Tags"])


def ensure_snapshot_absent():
    snapshot_name = module.params.get("db_snapshot_identifier")
    params = {"DBClusterSnapshotIdentifier": snapshot_name}
    changed = False

    snapshot = get_snapshot(snapshot_name)
    if not snapshot:
        return dict(changed=changed)
    elif snapshot and snapshot["Status"] != "deleting":
        snapshot, changed = call_method(client, module, "delete_db_cluster_snapshot", params)

    return dict(changed=changed)


def ensure_snapshot_present():
    db_cluster_identifier = module.params.get("db_cluster_identifier")
    snapshot_name = module.params.get("db_snapshot_identifier")
    changed = False

    snapshot = get_snapshot(snapshot_name)

    if not snapshot:
        params = {
            "DBClusterSnapshotIdentifier": snapshot_name,
            "DBClusterIdentifier": db_cluster_identifier
        }
        if module.params.get("tags"):
            params['Tags'] = ansible_dict_to_boto3_tag_list(module.params.get("tags"))
        _result, changed = call_method(client, module, "create_db_cluster_snapshot", params)

        if module.check_mode:
            return dict(changed=changed)

        return dict(changed=changed, **fetch_tags(get_snapshot(snapshot_name)))

    existing_tags = get_tags(client, module, snapshot["DBClusterSnapshotArn"])
    changed |= ensure_tags(client, module, snapshot["DBClusterSnapshotArn"], existing_tags,
                           module.params["tags"], module.params["purge_tags"])

    if module.check_mode:
        return dict(changed=changed)

    return dict(changed=changed, **fetch_tags(get_snapshot(snapshot_name)))


def main():
    global client
    global module

    argument_spec = dict(
        state=dict(choices=['present', 'absent'], default='present'),
        db_snapshot_identifier=dict(aliases=['id', 'snapshot_id', 'snapshot_name'], required=True),
        db_cluster_identifier=dict(aliases=['cluster_id', 'cluster_name']),
        wait=dict(type='bool', default=False),
        wait_timeout=dict(type='int', default=300),
        tags=dict(type='dict'),
        purge_tags=dict(type='bool', default=True),
    )

    module = AnsibleAWSModule(
        argument_spec=argument_spec,
        required_if=[['state', 'present', ['db_cluster_identifier']]],
        supports_check_mode=True,
    )

    retry_decorator = AWSRetry.jittered_backoff(retries=10)
    try:
        client = module.client('rds', retry_decorator=retry_decorator)
    except (botocore.exceptions.ClientError, botocore.exceptions.BotoCoreError) as e:
        module.fail_json_aws(e, msg="Failed to connect to AWS.")

    result = {}

    if module.params["state"] == "absent":
        result = ensure_snapshot_absent()
    else:
        result = ensure_snapshot_present()

    module.exit_json(**result)


if __name__ == '__main__':
    main()
