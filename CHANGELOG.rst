===========================
community.aws Release Notes
===========================

.. contents:: Topics


v2.4.0
======

Release Summary
---------------

This is the minor release of the ``community.aws`` collection.
This changelog contains all changes to the modules and plugins in this collection
that have been made after the previous release.

Minor Changes
-------------

- Added suport for retries (AWSRetry.jittered_backoff) for cloudfront_distribution (https://github.com/ansible-collections/community.aws/issues/296)

Bugfixes
--------

- Add backoff retry logic to elb_application_lb_info (https://github.com/ansible-collections/community.aws/pull/977)
- ecs_taskdefinition - include launch_type comparison when comparing task definitions (https://github.com/ansible-collections/community.aws/pull/840)
- elb_target_group_info - Add backoff retry logic (https://github.com/ansible-collections/community.aws/pull/1001)
- iam_role - Removes unnecessary removal of permission boundary from a role when deleting a role. Unlike inline policies, permission boundaries do not need to be removed from an IAM role before deleting the IAM role. This behavior causes issues when a permission boundary is inherited that prevents removal of the permission boundary. (https://github.com/ansible-collections/community.aws/pull/961)
- redshift_info - fix invalid import path for botocore exceptions (https://github.com/ansible-collections/community.aws/issues/968).
- wafv2_web_acl - fix exception when a rule contains lists values (https://github.com/ansible-collections/community.aws/pull/962).

v2.3.0
======

Release Summary
---------------

This is the minor release of the ``community.aws`` collection.
This changelog contains all changes to the modules and plugins in this collection
that have been made after the previous release.

Minor Changes
-------------

- elb_instance - `wait` parameter is no longer ignored (https://github.com/ansible-collections/community.aws/pull/826)

Bugfixes
--------

- cloudfront_distribution - Dont pass ``s3_origin_access_identity_enabled`` to API request (https://github.com/ansible-collections/community.aws/pull/881).
- execute_lambda - Wait for Lambda function State = Active before executing (https://github.com/ansible-collections/community.aws/pull/857)
- lambda - Wait for Lambda function State = Active & LastUpdateStatus = Successful before updating (https://github.com/ansible-collections/community.aws/pull/857)

v2.2.0
======

Release Summary
---------------

This is a backport release of the ``community.aws`` collection.

Minor Changes
-------------

- aws_msk_config - remove duplicated and unspecific requirements (https://github.com/ansible-collections/community.aws/pull/863).
- aws_ssm connection plugin - add parameters to explicitly specify SSE mode and KMS key id for uploads on the file transfer bucket. (https://github.com/ansible-collections/community.aws/pull/763)
- ecs_taskdefinition - remove duplicated and unspecific requirements (https://github.com/ansible-collections/community.aws/pull/863).
- iam_user - add boto3 waiter for iam user creation (https://github.com/ansible-collections/community.aws/pull/822).
- iam_user - add password management support bringing parity with `iam` module (https://github.com/ansible-collections/community.aws/pull/822).
- s3_lifecycle - Add ``abort_incomplete_multipart_upload_days`` and ``expire_object_delete_marker`` parameters (https://github.com/ansible-collections/community.aws/pull/794).

Bugfixes
--------

- aws_eks - Fix EKS cluster creation with short names (https://github.com/ansible-collections/community.aws/pull/818).

New Modules
-----------

- ec2_asg_scheduled_action - Create, modify and delete ASG scheduled scaling actions.

v2.1.0
======

Minor Changes
-------------

- aws_config_delivery_channel - replaced use of deprecated backoff decorator (https://github.com/ansible-collections/community.aws/pull/764).
- aws_direct_connect_confirm_connection - replaced use of deprecated backoff decorator (https://github.com/ansible-collections/community.aws/pull/764).
- aws_direct_connect_connection - replaced use of deprecated backoff decorator (https://github.com/ansible-collections/community.aws/pull/764).
- aws_direct_connect_link_aggregation_group - replaced use of deprecated backoff decorator (https://github.com/ansible-collections/community.aws/pull/764).
- aws_direct_connect_virtual_interface - replaced use of deprecated backoff decorator (https://github.com/ansible-collections/community.aws/pull/764).
- aws_inspector_target - replaced use of deprecated backoff decorator (https://github.com/ansible-collections/community.aws/pull/764).
- aws_kms - add support for ``kms_spec`` and ``kms_usage`` parameter (https://github.com/ansible-collections/community.aws/pull/774).
- aws_kms - replaced use of deprecated backoff decorator (https://github.com/ansible-collections/community.aws/pull/764).
- aws_kms_info - replaced use of deprecated backoff decorator (https://github.com/ansible-collections/community.aws/pull/764).
- cloudformation_stack_set - replaced use of deprecated backoff decorator (https://github.com/ansible-collections/community.aws/pull/764).
- cloudfront_distribution - add ``TLSv1.2_2021`` security policy for viewer connections (https://github.com/ansible-collections/community.aws/pull/707).
- dms_endpoint - replaced use of deprecated backoff decorator (https://github.com/ansible-collections/community.aws/pull/764).
- dms_replication_subnet_group - replaced use of deprecated backoff decorator (https://github.com/ansible-collections/community.aws/pull/764).
- dynamodb_table - add support for setting the `billing_mode` option (https://github.com/ansible-collections/community.aws/pull/753).
- dynamodb_table - the module has been updated to use the boto3 AWS SDK (https://github.com/ansible-collections/community.aws/pull/726).
- ec2_asg - replaced use of deprecated backoff decorator (https://github.com/ansible-collections/community.aws/pull/764).
- ec2_eip - added support for tagging EIPs (https://github.com/ansible-collections/community.aws/pull/332).
- ec2_eip_info - added automatic retries for common temporary API failures (https://github.com/ansible-collections/community.aws/pull/332).
- ec2_eip_info - added support for tagging EIPs (https://github.com/ansible-collections/community.aws/pull/332).
- ec2_elb_info - replaced use of deprecated backoff decorator (https://github.com/ansible-collections/community.aws/pull/764).
- ec2_win_password - module updated to use the boto3 AWS SDK (https://github.com/ansible-collections/community.aws/pull/759).
- ecs_service - added support for forcing deletion of a service (https://github.com/ansible-collections/community.aws/pull/228).
- ecs_service_info - replaced use of deprecated backoff decorator (https://github.com/ansible-collections/community.aws/pull/764).
- ecs_taskdefinition - add ``placement_constraints`` option (https://github.com/ansible-collections/community.aws/pull/741).
- efs - add ``transition_to_ia`` parameter to support specifying the number of days before transitioning data to inactive storage (https://github.com/ansible-collections/community.aws/pull/522).
- elb_instance - added new ``updated_elbs`` return value (https://github.com/ansible-collections/community.aws/pull/773).
- elb_instance - the module has been migrated to the boto3 AWS SDK (https://github.com/ansible-collections/community.aws/pull/773).
- elb_target_group - add ``preserve_client_ip_enabled`` option (https://github.com/ansible-collections/community.aws/pull/670).
- elb_target_group - add ``proxy_protocol_v2_enabled`` option (https://github.com/ansible-collections/community.aws/pull/670).
- iam_managed_policy - replaced use of deprecated backoff decorator (https://github.com/ansible-collections/community.aws/pull/764).
- iam_role - Added `wait` option for IAM role creation / updates (https://github.com/ansible-collections/community.aws/pull/767).
- iam_saml_federation - replaced use of deprecated backoff decorator (https://github.com/ansible-collections/community.aws/pull/764).
- iam_server_certificate - add support for check_mode (https://github.com/ansible-collections/community.aws/pull/737).
- iam_server_certificate - migrate module to using the boto3 SDK (https://github.com/ansible-collections/community.aws/pull/737).
- lambda_info - add automatic retries for recoverable errors (https://github.com/ansible-collections/community.aws/pull/777).
- lambda_info - add support for tags (https://github.com/ansible-collections/community.aws/pull/375).
- lambda_info - use paginator for list queries (https://github.com/ansible-collections/community.aws/pull/777).
- rds - replaced use of deprecated backoff decorator (https://github.com/ansible-collections/community.aws/pull/764).
- redshift_subnet_group - added support for check_mode (https://github.com/ansible-collections/community.aws/pull/724).
- redshift_subnet_group - the ``group_description`` option has been renamed to ``description`` and is now optional. The old parameter name will continue to work (https://github.com/ansible-collections/community.aws/pull/724).
- redshift_subnet_group - the ``group_subnets`` option has been renamed to ``subnets`` and is now only required when creating a new group. The old parameter name will continue to work (https://github.com/ansible-collections/community.aws/pull/724).
- redshift_subnet_group - the module has been migrated to the boto3 AWS SDK (https://github.com/ansible-collections/community.aws/pull/724).
- route53_health_check - add support for tagging health checks (https://github.com/ansible-collections/community.aws/pull/765).
- route53_health_check - added support for check_mode (https://github.com/ansible-collections/community.aws/pull/734).
- route53_health_check - added support for disabling health checks (https://github.com/ansible-collections/community.aws/pull/756).
- route53_health_check - migrated to boto3 SDK (https://github.com/ansible-collections/community.aws/pull/734).
- route53_zone - add support for tagging Route 53 zones (https://github.com/ansible-collections/community.aws/pull/565).
- sqs_queue - Providing a kms_master_key_id will now enable SSE properly (https://github.com/ansible-collections/community.aws/pull/762)

Deprecated Features
-------------------

- dynamodb_table - DynamoDB does not support specifying non-key-attributes when creating an ``ALL`` index.  Passing ``includes`` for such indexes is currently ignored but will result in failures after version 3.0.0 (https://github.com/ansible-collections/community.aws/pull/726).
- dynamodb_table - DynamoDB does not support updating the primary indexes on a table.  Attempts to make such changes are currently ignored but will result in failures after version 3.0.0 (https://github.com/ansible-collections/community.aws/pull/726).
- elb_instance - setting of the ``ec2_elb`` fact has been deprecated and will be removed in release 4.0.0 of the collection. See the module documentation for an alternative example using the register keyword (https://github.com/ansible-collections/community.aws/pull/773).
- iam_cert - the iam_cert module has been renamed to iam_server_certificate for consistency with the companion iam_server_certificate_info module. The usage of the module has not changed.  The iam_cert alias will be removed in version 4.0.0 (https://github.com/ansible-collections/community.aws/pull/728).
- iam_server_certificate - Passing file names to the ``cert``, ``chain_cert`` and ``key`` parameters has been deprecated. We recommend using a lookup plugin to read the files instead, see the documentation for an example (https://github.com/ansible-collections/community.aws/pull/735).
- iam_server_certificate - the default value for the ``dup_ok`` parameter is currently ``false``, in version 4.0.0 this will be updated to ``true``.  To preserve the current behaviour explicitly set the ``dup_ok`` parameter to ``false`` (https://github.com/ansible-collections/community.aws/pull/737).
- rds_snapshot - the rds_snapshot module has been renamed to rds_instance_snapshot. The usage of the module has not changed. The rds_snapshot alias will be removed in version 4.0.0 (https://github.com/ansible-collections/community.aws/pull/783).

Bugfixes
--------

- AWS action group - added missing ``aws_direct_connect_confirm_connection`` and ``efs_tag`` entries (https://github.com/ansible-collections/amazon.aws/issues/557).
- cloudfront_info - Switch to native boto3 paginators to fix reported bug when over 100 distributions exist (https://github.com/ansible-collections/community.aws/issues/769).
- ec2_eip - fix bug when allocating an EIP but not associating it to a VPC (https://github.com/ansible-collections/community.aws/pull/731).
- elb_classic_lb_info - fix empty list returned when names not defined (https://github.com/ansible-collections/community.aws/pull/693).
- elb_instance - Python 3 compatability fix (https://github.com/ansible-collections/community.aws/issues/384).
- iam_role_info - switch to jittered backoff to reduce rate limiting failures (https://github.com/ansible-collections/community.aws/pull/748).
- rds_instance - Fixed issue with enabling enhanced monitoring on a pre-existing RDS instance (https://github.com/ansible-collections/community.aws/pull/747).
- route53 - add missing set identifier in resource_record_set (https://github.com/ansible-collections/community.aws/pull/595).
- route53 - fix diff mode when deleting records (https://github.com/ansible-collections/community.aws/pull/802).
- route53 - return empty result for nonexistent records (https://github.com/ansible-collections/community.aws/pull/799).
- sns_topic - define suboptions for delivery_policy option (https://github.com/ansible-collections/community.aws/issues/713).

New Modules
-----------

- iam_access_key - Manage AWS IAM User access keys
- iam_access_key_info - fetch information about AWS IAM User access keys
- rds_option_group - rds_option_group module
- rds_option_group_info - rds_option_group_info module

v2.0.0
======

Major Changes
-------------

- community.aws collection - The community.aws collection has dropped support for ``botocore<1.18.0`` and ``boto3<1.15.0`` (https://github.com/ansible-collections/community.aws/pull/711). Most modules will continue to work with older versions of the AWS SDK, however compatability with older versions of the SDK is not guaranteed and will not be tested. When using older versions of the SDK a warning will be emitted by Ansible (https://github.com/ansible-collections/amazon.aws/pull/442).

Minor Changes
-------------

- aws_eks_cluster - Tests for compatability with older versions of the AWS SDKs have been removed (https://github.com/ansible-collections/community.aws/pull/675).
- aws_kms_info - use a generator rather than list comprehension (https://github.com/ansible-collections/community.aws/pull/688).
- aws_s3_bucket_info - added test for botocore>=1.18.11 when attempting to fetch bucket ownership controls (https://github.com/ansible-collections/community.aws/pull/682)
- aws_ses_rule_set - use a generator rather than list comprehension (https://github.com/ansible-collections/community.aws/pull/688).
- aws_sgw_info - ensure module runs in check_mode (https://github.com/ansible-collections/community.aws/issues/659).
- cloudformation_exports_info - ensure module runs in check_mode (https://github.com/ansible-collections/community.aws/issues/659).
- cloudformation_stack_set - Tests for compatability with older versions of the AWS SDKs have been removed (https://github.com/ansible-collections/community.aws/pull/675).
- cloudfront_info - ensure module runs in check_mode (https://github.com/ansible-collections/community.aws/issues/659).
- cloudwatchevent_rule - use a generator rather than list comprehension (https://github.com/ansible-collections/community.aws/pull/688).
- dynamodb_table - Tests for compatability with older versions of the AWS SDKs have been removed (https://github.com/ansible-collections/community.aws/pull/675).
- dynamodb_ttl - Tests for compatability with older versions of the AWS SDKs have been removed (https://github.com/ansible-collections/community.aws/pull/675).
- ec2_ami_copy - Tests for compatability with older versions of the AWS SDKs have been removed (https://github.com/ansible-collections/community.aws/pull/675).
- ec2_asg - Tests for compatability with older versions of the AWS SDKs have been removed (https://github.com/ansible-collections/community.aws/pull/675).
- ec2_asg_info - ensure module runs in check_mode (https://github.com/ansible-collections/community.aws/issues/659).
- ec2_launch_template - Tests for compatability with older versions of the AWS SDKs have been removed (https://github.com/ansible-collections/community.aws/pull/675).
- ec2_lc_info - ensure module runs in check_mode (https://github.com/ansible-collections/community.aws/issues/659).
- ec2_transit_gateway - Tests for compatability with older versions of the AWS SDKs have been removed (https://github.com/ansible-collections/community.aws/pull/675).
- ec2_transit_gateway_info - Tests for compatability with older versions of the AWS SDKs have been removed (https://github.com/ansible-collections/community.aws/pull/675).
- ec2_vpc_peer - Tests for compatability with older versions of the AWS SDKs have been removed (https://github.com/ansible-collections/community.aws/pull/675).
- ec2_vpc_peer - use shared code for tagging peering connections (https://github.com/ansible-collections/community.aws/pull/614).
- ec2_vpc_route_table - use shared code for tagging route tables (https://github.com/ansible-collections/community.aws/pull/616).
- ec2_vpc_vgw - fix arguments-renamed pylint issue (https://github.com/ansible-collections/community.aws/pull/686).
- ec2_vpc_vpn - fix arguments-renamed pylint issue (https://github.com/ansible-collections/community.aws/pull/686).
- ecs_ecr - Tests for compatability with older versions of the AWS SDKs have been removed (https://github.com/ansible-collections/community.aws/pull/675).
- ecs_service - Tests for compatability with older versions of the AWS SDKs have been removed (https://github.com/ansible-collections/community.aws/pull/675).
- ecs_task - Tests for compatability with older versions of the AWS SDKs have been removed (https://github.com/ansible-collections/community.aws/pull/675).
- ecs_task - remove unused import (https://github.com/ansible-collections/community.aws/pull/686).
- ecs_taskdefinition - Tests for compatability with older versions of the AWS SDKs have been removed (https://github.com/ansible-collections/community.aws/pull/675).
- efs - Tests for compatability with older versions of the AWS SDKs have been removed (https://github.com/ansible-collections/community.aws/pull/675).
- efs_info - Tests for compatability with older versions of the AWS SDKs have been removed (https://github.com/ansible-collections/community.aws/pull/675).
- elasticache_subnet_group - add return values (https://github.com/ansible-collections/community.aws/pull/723).
- elasticache_subnet_group - add support for check_mode (https://github.com/ansible-collections/community.aws/pull/723).
- elasticache_subnet_group - module migrated to boto3 AWS SDK (https://github.com/ansible-collections/community.aws/pull/723).
- elb_application_lb - added ``ip_address_type`` parameter to support changing application load balancer configuration (https://github.com/ansible-collections/community.aws/pull/499).
- elb_application_lb_info - added ``ip_address_type`` in output when gathering application load balancer parameters (https://github.com/ansible-collections/community.aws/pull/499).
- elb_instance - make elb_instance idempotent when deregistering instances.  Merged from ec2_elb U(https://github.com/ansible/ansible/pull/31660).
- elb_network_lb - added ``ip_address_type`` parameter to support changing network load balancer configuration (https://github.com/ansible-collections/community.aws/pull/499).
- elb_target_group - Tests for compatability with older versions of the AWS SDKs have been removed (https://github.com/ansible-collections/community.aws/pull/675).
- elb_target_group - use a generator rather than list comprehension (https://github.com/ansible-collections/community.aws/pull/688).
- iam - use a generator rather than list comprehension (https://github.com/ansible-collections/community.aws/pull/688).
- iam_group - use a generator rather than list comprehension (https://github.com/ansible-collections/community.aws/pull/688).
- iam_mfa_device_info - ensure module runs in check_mode (https://github.com/ansible-collections/community.aws/issues/659).
- iam_role - Tests for compatability with older versions of the AWS SDKs have been removed (https://github.com/ansible-collections/community.aws/pull/675).
- iam_role - use a generator rather than list comprehension (https://github.com/ansible-collections/community.aws/pull/688).
- iam_server_certificate_info - ensure module runs in check_mode (https://github.com/ansible-collections/community.aws/issues/659).
- iam_user - use a generator rather than list comprehension (https://github.com/ansible-collections/community.aws/pull/688).
- kms_info - added a new ``keys_attr`` parameter to continue returning the key details in the ``keys`` attribute as well as the ``kms_keys`` attribute (https://github.com/ansible-collections/community.aws/pull/648).
- lambda - Tests for compatability with older versions of the AWS SDKs have been removed (https://github.com/ansible-collections/community.aws/pull/675).
- rds_instance - Tests for compatability with older versions of the AWS SDKs have been removed (https://github.com/ansible-collections/community.aws/pull/675).
- rds_instance - convert ``preferred_maintenance_window`` days into lowercase so changed returns properly (https://github.com/ansible-collections/community.aws/pull/516).
- rds_instance - use a generator rather than list comprehension (https://github.com/ansible-collections/community.aws/pull/688).
- route53 - add rate-limiting retries while waiting for changes to propagate (https://github.com/ansible-collections/community.aws/pull/564).
- route53 - add retries on ``PriorRequestNotComplete`` errors (https://github.com/ansible-collections/community.aws/pull/564).
- route53 - update retry ``max_delay`` setting so that it can be set above 60 seconds (https://github.com/ansible-collections/community.aws/pull/564).
- sns_topic - Added ``topic_type`` parameter to select type of SNS topic (either FIFO or Standard) (https://github.com/ansible-collections/community.aws/pull/599).
- sqs_queue - Tests for compatability with older versions of the AWS SDKs have been removed (https://github.com/ansible-collections/community.aws/pull/675).
- various community.aws modules - remove unused imports (https://github.com/ansible-collections/community.aws/pull/629)
- wafv2_resources_info - ensure module runs in check_mode (https://github.com/ansible-collections/community.aws/issues/659).
- wafv2_web_acl_info - ensure module runs in check_mode (https://github.com/ansible-collections/community.aws/issues/659).

Breaking Changes / Porting Guide
--------------------------------

- ec2_instance - The module has been migrated to the ``amazon.aws`` collection. Playbooks using the Fully Qualified Collection Name for this module should be updated to use ``amazon.aws.ec2_instance``.
- ec2_instance_info - The module has been migrated to the ``amazon.aws`` collection. Playbooks using the Fully Qualified Collection Name for this module should be updated to use ``amazon.aws.ec2_instance_info``.
- ec2_vpc_endpoint - The module has been migrated from the ``community.aws`` collection. Playbooks using the Fully Qualified Collection Name for this module should be updated to use ``amazon.aws.ec2_vpc_endpoint``.
- ec2_vpc_endpoint_facts - The module has been migrated from the ``community.aws`` collection. Playbooks using the Fully Qualified Collection Name for this module should be updated to use ``amazon.aws.ec2_vpc_endpoint_info``.
- ec2_vpc_endpoint_info - The module has been migrated from the ``community.aws`` collection. Playbooks using the Fully Qualified Collection Name for this module should be updated to use ``amazon.aws.ec2_vpc_endpoint_info``.
- ec2_vpc_endpoint_service_info - The module has been migrated from the ``community.aws`` collection. Playbooks using the Fully Qualified Collection Name for this module should be updated to use ``amazon.aws.ec2_vpc_endpoint_service_info``.
- ec2_vpc_igw - The module has been migrated from the ``community.aws`` collection. Playbooks using the Fully Qualified Collection Name for this module should be updated to use ``amazon.aws.ec2_vpc_igw``.
- ec2_vpc_igw_facts - The module has been migrated from the ``community.aws`` collection. Playbooks using the Fully Qualified Collection Name for this module should be updated to use ``amazon.aws.ec2_vpc_igw_info``.
- ec2_vpc_igw_info - The module has been migrated from the ``community.aws`` collection. Playbooks using the Fully Qualified Collection Name for this module should be updated to use ``amazon.aws.ec2_vpc_igw_info``.
- ec2_vpc_nat_gateway - The module has been migrated from the ``community.aws`` collection. Playbooks using the Fully Qualified Collection Name for this module should be updated to use ``amazon.aws.ec2_vpc_nat_gateway``.
- ec2_vpc_nat_gateway_facts - The module has been migrated from the ``community.aws`` collection. Playbooks using the Fully Qualified Collection Name for this module should be updated to use ``amazon.aws.ec2_vpc_nat_gateway_info``.
- ec2_vpc_nat_gateway_info - The module has been migrated from the ``community.aws`` collection. Playbooks using the Fully Qualified Collection Name for this module should be updated to use ``amazon.aws.ec2_vpc_nat_gateway_info``.
- kms_info - key details are now returned in the ``kms_keys`` attribute rather than the ``keys`` attribute (https://github.com/ansible-collections/community.aws/pull/648).

Deprecated Features
-------------------

- ec2_elb - the ``ec2_elb`` module has been removed and redirected to the ``elb_instance`` module which functions identically. The original ``ec2_elb`` name is now deprecated and will be removed in release 3.0.0 (https://github.com/ansible-collections/community.aws/pull/586).
- ec2_elb_info - the boto based ``ec2_elb_info`` module has been deprecated in favour of the boto3 based ``elb_classic_lb_info`` module. The ``ec2_elb_info`` module will be removed in release 3.0.0 (https://github.com/ansible-collections/community.aws/pull/586).
- elb_classic_lb - the ``elb_classic_lb`` module has been removed and redirected to the ``amazon.aws.ec2_elb_lb`` module which functions identically.
- iam - the boto based ``iam`` module has been deprecated in favour of the boto3 based ``iam_user``, ``iam_group`` and ``iam_role`` modules. The ``iam`` module will be removed in release 3.0.0 (https://github.com/ansible-collections/community.aws/pull/664).
- rds - the boto based ``rds`` module has been deprecated in favour of the boto3 based ``rds_instance`` module. The ``rds`` module will be removed in release 3.0.0 (https://github.com/ansible-collections/community.aws/pull/663).
- script_inventory_ec2 - The ec2.py inventory script is being moved to a new repository. The script can now be downloaded from https://github.com/ansible-community/contrib-scripts/blob/main/inventory/ec2.py and will be removed from this collection in the 3.0 release. We recommend migrating from the script to the `amazon.aws.ec2` inventory plugin.

Bugfixes
--------

- aws_secret - fix deletion idempotency when not using instant deletion (https://github.com/ansible-collections/community.aws/pull/681).
- aws_ssm - rename ``retries`` to ``reconnection_retries`` to avoid conflict with task retries
- ec2_vpc_peer - automatically retry when attempting to tag freshly created peering connections (https://github.com/ansible-collections/community.aws/pull/614).
- ec2_vpc_route_table - automatically retry when attempting to modify freshly created route tables (https://github.com/ansible-collections/community.aws/pull/616).
- ecs_taskdefinition - ensure cast to integer (https://github.com/ansible-collections/community.aws/pull/574).
- ecs_taskdefinition - fix idempotency (https://github.com/ansible-collections/community.aws/pull/574).
- ecs_taskdefinition - fix typo in ecs task defination for env file validations (https://github.com/ansible-collections/community.aws/pull/600).
- iam_role - Modified iam_role internal code to replace update_role_description with update_role (https://github.com/ansible-collections/community.aws/pull/697).
- route53 - fix typo in waiter configuration that prevented management of the delays (https://github.com/ansible-collections/community.aws/pull/564).
- s3_sync - fix handling individual file path to upload a individual file to s3 bucket (https://github.com/ansible-collections/community.aws/pull/692).
- sqs_queue - fix queue attribute comparison to make module idempotent (https://github.com/ansible-collections/community.aws/pull/592).

New Modules
-----------

- aws_msk_cluster - Manage Amazon MSK clusters.
- aws_msk_config - Manage Amazon MSK cluster configurations.
- efs_tag - create and remove tags on Amazon EFS resources

v1.5.0
======

Minor Changes
-------------

- aws_config_aggregator - Fix typos in attribute names (https://github.com/ansible-collections/community.aws/pull/553).
- aws_glue_connection - Added multple connection types (https://github.com/ansible-collections/community.aws/pull/503).
- aws_glue_connection - Added support for check mode (https://github.com/ansible-collections/community.aws/pull/503).
- aws_glue_job - added ``number_of_workers``, ``worker_type`` and ``glue_version`` attributes to the module (https://github.com/ansible-collections/community.aws/pull/370).
- aws_region_info - Add retries on common AWS failures (https://github.com/ansible-collections/community.aws/pull/422).
- aws_s3_bucket_info - new module options ``name``, ``name_filter``, ``bucket_facts`` and ``transform_location`` (https://github.com/ansible-collections/community.aws/pull/260).
- aws_ssm connection plugin - add support for specifying a profile to be used when connecting (https://github.com/ansible-collections/community.aws/pull/278).
- aws_ssm_parameter_store - added tier parameter option (https://github.com/ansible/ansible/issues/59738).
- ec2_asg module - add support for all mixed_instances_policy parameters (https://github.com/ansible-collections/community.aws/issues/231).
- ec2_asg_info - gather information about asg lifecycle hooks (https://github.com/ansible-collections/community.aws/pull/233).
- ec2_instance - wait for new instances to return a status before attempting to set additional parameters (https://github.com/ansible-collections/community.aws/pull/533).
- ec2_instance_info - add retries on common AWS failures (https://github.com/ansible-collections/community.aws/pull/521).
- ec2_launch_template - added ``metadata_options`` parameter to support changing the IMDS configuration for instances (https://github.com/ansible-collections/community.aws/pull/322).
- ec2_metric_alarm - Added support for check mode (https://github.com/ansible-collections/community.aws/pull/470).
- ec2_metric_alarm - Made ``unit`` parameter optional (https://github.com/ansible-collections/community.aws/pull/470).
- ec2_vpc_egress_igw - Add retries on common AWS failures (https://github.com/ansible-collections/community.aws/pull/421).
- ec2_vpc_endpoint - Add retries on common AWS failures. (https://github.com/ansible-collections/community.aws/pull/473)
- ec2_vpc_endpoint - Added support for specifying ``vpc_endpoint_type`` (https://github.com/ansible-collections/community.aws/pull/460).
- ec2_vpc_endpoint - The module now supports tagging endpoints. (https://github.com/ansible-collections/community.aws/pull/473)
- ec2_vpc_endpoint - The module will now lookup existing endpoints and try to match on the provided parameters before creating a new endpoint for better idempotency.  (https://github.com/ansible-collections/community.aws/pull/473)
- ec2_vpc_endpoint_info - ensure paginated endpoint description is retried on common AWS failures (https://github.com/ansible-collections/community.aws/pull/537).
- ec2_vpc_endpoint_info - use boto3 paginator when fetching services (https://github.com/ansible-collections/community.aws/pull/537).
- ec2_vpc_endpoint_service_info - new module added for fetching information about available VPC endpoint services (https://github.com/ansible-collections/community.aws/pull/346).
- ec2_vpc_nacl - add support for IPv6 (https://github.com/ansible-collections/community.aws/pull/398).
- ec2_vpc_nat_gateway - add AWSRetry decorators to improve reliability (https://github.com/ansible-collections/community.aws/pull/427).
- ec2_vpc_nat_gateway - code cleaning (https://github.com/ansible-collections/community.aws/pull/445)
- ec2_vpc_nat_gateway - imporove documentation (https://github.com/ansible-collections/community.aws/pull/445)
- ec2_vpc_nat_gateway - improve error handling (https://github.com/ansible-collections/community.aws/pull/445)
- ec2_vpc_nat_gateway - use custom waiters to manage NAT gateways states (deleted and available) (https://github.com/ansible-collections/community.aws/pull/445)
- ec2_vpc_nat_gateway - use pagination on describe calls to ensure all results are fetched (https://github.com/ansible-collections/community.aws/pull/427).
- ec2_vpc_nat_gateway_info - Add paginator (https://github.com/ansible-collections/community.aws/pull/472).
- ec2_vpc_nat_gateway_info - Improve documentation (https://github.com/ansible-collections/community.aws/pull/472).
- ec2_vpc_nat_gateway_info - Improve error handling (https://github.com/ansible-collections/community.aws/pull/472)
- ec2_vpc_nat_gateway_info - Use normalize_boto3_result (https://github.com/ansible-collections/community.aws/pull/472)
- ec2_vpc_nat_gateway_info - solve RequestLimitExceeded error by adding retry decorator (https://github.com/ansible-collections/community.aws/pull/446)
- ec2_vpc_peer - More return info added, also simplified module code a bit and extended tests (https://github.com/ansible-collections/community.aws/pull/355)
- ec2_vpc_peer - add support for waiting on state changes (https://github.com/ansible-collections/community.aws/pull/501).
- ec2_vpc_peering_info - add ``vpc_peering_connections`` return value to be consistent with boto3 modules (https://github.com/ansible-collections/community.aws/pull/501).
- ec2_vpc_peering_info - add retries on common AWS failures (https://github.com/ansible-collections/community.aws/pull/536).
- ec2_vpc_route_table - add AWSRetry decorators to improve reliability (https://github.com/ansible-collections/community.aws/pull/442).
- ec2_vpc_route_table - add boto3 pagination for some searches (https://github.com/ansible-collections/community.aws/pull/442).
- ec2_vpc_route_table_info - migrate to boto3 (https://github.com/ansible-collections/community.aws/pull/442).
- ec2_vpc_vgw - Add automatic retries for recoverable errors (https://github.com/ansible-collections/community.aws/pull/162).
- ec2_vpc_vpn - Add automatic retries for recoverable errors (https://github.com/ansible-collections/community.aws/pull/162).
- ecs_service - Add ``platform_version`` parameter to ``ecs_service`` (https://github.com/ansible-collections/community.aws/pull/353).
- ecs_task - added ``assign_public_ip`` option for network_configuration (https://github.com/ansible-collections/community.aws/pull/395).
- ecs_taskdefinition - Documentation improvement (https://github.com/ansible-collections/community.aws/issues/520)
- elasticache - Improve docs a little, add intgration tests (https://github.com/ansible-collections/community.aws/pull/410).
- elb_classic_info - If the provided load balancer doesn't exist, return an empty list instead of throwing an error. (https://github.com/ansible-collections/community.aws/pull/215).
- elb_target_group - Add elb target group attributes ``stickiness_app_cookie_name`` and ``stickiness_app_cookie_duration_seconds``. Also update docs for stickiness_type to mention application cookie (https://github.com/ansible-collections/community.aws/pull/548)
- iam - Make iam module more predictable when returning the ``user_name`` it creates or deletes (https://github.com/ansible-collections/community.aws/pull/369).
- iam_saml_federation - module now returns the state of the provider when no changes are made (https://github.com/ansible-collections/community.aws/pull/419).
- kinesis_stream - check_mode is now based on the live settings rather than comparisons with a hard coded/fake stream definition (https://github.com/ansible-collections/community.aws/pull/27).
- kinesis_stream - now returns changed more accurately (https://github.com/ansible-collections/community.aws/pull/27).
- kinesis_stream - now returns tags consistently (https://github.com/ansible-collections/community.aws/pull/27).
- kinesis_stream - return values are now the same format when working with both encrypted and un-encrypted streams (https://github.com/ansible-collections/community.aws/pull/27).
- lambda_alias - add retries on common AWS failures (https://github.com/ansible-collections/community.aws/pull/396).
- lambda_alias - use common helper functions to create AWS connections (https://github.com/ansible-collections/community.aws/pull/396).
- lambda_alias - use common helper functions to perform snake_case to CamelCase conversions (https://github.com/ansible-collections/community.aws/pull/396).
- rds_instance - new ``purge_security_groups`` parameter (https://github.com/ansible-collections/community.aws/issues/385).
- rds_param_group - Add AWSRetry (https://github.com/ansible-collections/community.aws/pull/532).
- rds_param_group - Fix integration tests (https://github.com/ansible-collections/community.aws/pull/532).
- rds_param_group - Support check_mode (https://github.com/ansible-collections/community.aws/pull/532).
- rds_snapshot - added to the aws module_defaults group (https://github.com/ansible-collections/community.aws/pull/515).
- route53 - fixes AWS API error when attempting to create Alias records (https://github.com/ansible-collections/community.aws/issues/434).
- s3_lifecycle - Add a ``wait`` parameter to wait for changes to propagate after being set (https://github.com/ansible-collections/community.aws/pull/448).
- s3_lifecycle - Add retries on common AWS failures (https://github.com/ansible-collections/community.aws/pull/448).
- s3_lifecycle - Fix idempotency when using dates instead of days (https://github.com/ansible-collections/community.aws/pull/448).
- s3_logging - added support for check_mode (https://github.com/ansible-collections/community.aws/pull/447).
- s3_logging - migrated from boto to boto3 (https://github.com/ansible-collections/community.aws/pull/447).
- s3_sync - new ``storage_class`` feature allowing to specify the storage class when any object is added to an S3 bucket (https://github.com/ansible-collections/community.aws/issues/358).
- sanity tests - add ignore.txt for 2.12 (https://github.com/ansible-collections/community.aws/pull/527).
- state_machine_arn - return ``state_machine_arn`` when state is unchanged (https://github.com/ansible-collections/community.aws/pull/302).

Deprecated Features
-------------------

- ec2_vpc_endpoint_info - the ``query`` option has been deprecated and will be removed after 2022-12-01 (https://github.com/ansible-collections/community.aws/pull/346). The ec2_vpc_endpoint_info now defaults to listing information about endpoints. The ability to search for information about available services has been moved to the dedicated module ``ec2_vpc_endpoint_service_info``.

Security Fixes
--------------

- aws_direct_connect_virtual_interface - mark the ``authentication_key`` parameter as ``no_log`` to avoid accidental leaking of secrets in logs (https://github.com/ansible-collections/community.aws/pull/475).
- aws_secret - flag the ``secret`` parameter as containing sensitive data which shouldn't be logged (https://github.com/ansible-collections/community.aws/pull/471).
- sts_assume_role - mark the ``mfa_token`` parameter as ``no_log`` to avoid accidental leaking of secrets in logs (https://github.com/ansible-collections/community.aws/pull/475).
- sts_session_token - mark the ``mfa_token`` parameter as ``no_log`` to avoid accidental leaking of secrets in logs (https://github.com/ansible-collections/community.aws/pull/475).

Bugfixes
--------

- aws_ssm - Adds destructor to SSM connection plugin to ensure connections are properly cleaned up after usage (https://github.com/ansible-collections/community.aws/pull/542).
- aws_ssm - enable aws ssm connections if **AWS_SESSION_TOKEN** is missing (https://github.com/ansible-collections/community.aws/pull/535).
- cloudtrail - fix always reporting changed = true when kms alias used (https://github.com/ansible-collections/community.aws/pull/506).
- cloudtrail - fix lower casing of tag keys (https://github.com/ansible-collections/community.aws/pull/506).
- ec2_asg - fix target group update logic (https://github.com/ansible-collections/community.aws/pull/493).
- ec2_instance - ensure that termination protection isn't modified when using check_mode (https://github.com/ansible/ansible/issues/67716).
- ec2_instance - fix key errors when instance has no tags (https://github.com/ansible-collections/community.aws/pull/476).
- ec2_launch_template - ensure that empty parameters are properly removed before passing to AWS (https://github.com/ansible-collections/community.aws/issues/230).
- ec2_launch_template - fixes parameter validation failure when passing a instance profile ARN instead of just the role name (https://github.com/ansible-collections/community.aws/pull/371).
- ec2_vpc_peer - fix idempotency when rejecting and deleting peering connections (https://github.com/ansible-collections/community.aws/pull/501).
- ec2_vpc_route_table - catch RouteAlreadyExists error when rerunning same task twice to make module idempotent (https://github.com/ansible-collections/community.aws/issues/357).
- elasticache - Fix ``KeyError`` issue when updating security group (https://github.com/ansible-collections/community.aws/pull/410).
- kinesis_stream - fixed issue where streams get marked as changed even if no encryption actions were necessary (https://github.com/ansible/ansible/issues/65928).
- rds_instance - fixes bug preventing the use of tags when creating an RDS instance from a snapshot (https://github.com/ansible-collections/community.aws/issues/530).
- route53 - ensure that the old return values are re-added along side the new ones (https://github.com/ansible-collections/community.aws/issues/523).
- route53 - fix ``AttributeError`` in ``get_zone_id_by_name`` when a vpc_id on a private zone is provided (https://github.com/ansible-collections/community.aws/issues/509).
- route53 - fix handling for characters escaped by AWS in record names, like ``*`` and ``@``. This fixes idempotency for such record names (https://github.com/ansible-collections/community.aws/issues/524).
- route53 - fix when using ``state=get`` on private DNS zones and add tests to cover this scenario (https://github.com/ansible-collections/community.aws/pull/424).
- route53 - make sure that CAA values order is again ignored during idempotency comparsion (https://github.com/ansible-collections/community.aws/issues/524).
- sns_topic - Add ``+`` to allowable characters in SMS endpoints (https://github.com/ansible-collections/community.aws/pull/454).
- sqs_queue - fix UnboundLocalError when passing a boolean parameter (https://github.com/ansible-collections/community.aws/issues/172).

New Modules
-----------

- ec2_vpc_endpoint_service_info - retrieves AWS VPC endpoint service details
- wafv2_ip_set - wafv2_ip_set
- wafv2_ip_set_info - Get information about wafv2 ip sets
- wafv2_resources - wafv2_web_acl
- wafv2_resources_info - wafv2_resources_info
- wafv2_rule_group - wafv2_web_acl
- wafv2_rule_group_info - wafv2_web_acl_info
- wafv2_web_acl - wafv2_web_acl
- wafv2_web_acl_info - wafv2_web_acl

v1.4.0
======

Minor Changes
-------------

- aws_kms - add support for setting the deletion window using `pending_window` (PendingWindowInDays) (https://github.com/ansible-collections/community.aws/pull/200).
- aws_kms_info - Add ``key_id`` and ``alias`` parameters to support fetching a single key (https://github.com/ansible-collections/community.aws/pull/200).
- dynamodb_ttl - use ``botocore_at_least`` helper for checking the available botocore version (https://github.com/ansible-collections/community.aws/pull/280).
- ec2_instance - add automatic retries on all paginated queries for temporary errors (https://github.com/ansible-collections/community.aws/pull/373).
- ec2_instance - migrate to shared implementation of get_ec2_security_group_ids_from_names. The module will now return an error if the subnet provided isn't in the requested VPC. (https://github.com/ansible-collections/community.aws/pull/214)
- ec2_instance_info - added ``minimum_uptime`` option with alias ``uptime`` for filtering instances that have only been online for certain duration of time in minutes (https://github.com/ansible-collections/community.aws/pull/356).
- ec2_launch_template - Add retries on common AWS failures (https://github.com/ansible-collections/community.aws/pull/326).
- ec2_vpc_peer - use ``botocore_at_least`` helper for checking the available botocore version (https://github.com/ansible-collections/community.aws/pull/280).
- ecs_task - use ``botocore_at_least`` helper for checking the available botocore version (https://github.com/ansible-collections/community.aws/pull/280).
- route53 - migrated from boto to boto3 (https://github.com/ansible-collections/community.aws/pull/405).
- various community.aws modules - cleanup error handling to use ``is_boto3_error_code`` and ``is_boto3_error_message`` helpers (https://github.com/ansible-collections/community.aws/pull/268).
- various community.aws modules - cleanup of Python imports (https://github.com/ansible-collections/community.aws/pull/360).
- various community.aws modules - improve consistency of handling Boto3 exceptions (https://github.com/ansible-collections/community.aws/pull/268).
- various community.aws modules - migrate exception error message handling from fail_json to fail_json_aws (https://github.com/ansible-collections/community.aws/pull/361).

Deprecated Features
-------------------

- ec2_eip - formally deprecate the ``instance_id`` alias for ``device_id`` (https://github.com/ansible-collections/community.aws/pull/349).
- ec2_vpc_endpoint - deprecate the policy_file option and recommend using policy with a lookup (https://github.com/ansible-collections/community.aws/pull/366).

Bugfixes
--------

- aws_kms - fixes issue where module execution fails without the kms:GetKeyRotationStatus permission. (https://github.com/ansible-collections/community.aws/pull/200).
- aws_kms_info - ensure that searching by tag works when tag only exists on some CMKs (https://github.com/ansible-collections/community.aws/issues/276).
- aws_s3_cors - fix element type for rules parameter. (https://github.com/ansible-collections/community.aws/pull/408).
- aws_ssm - fix the generation of CURL URL used to download Ansible Python file from S3 bucket by ```_get_url()``` due to due to non-assignment of aws region in the URL and not using V4 signature as specified for AWS S3 signature URL by ```_get_boto_client()``` in (https://github.com/ansible-collections/community.aws/pull/352).
- aws_ssm - fixed ``UnicodeEncodeError`` error when using unicode file names (https://github.com/ansible-collections/community.aws/pull/295).
- ec2_eip - fix eip association by instance id & private ip address due to case-sensitivity of the ``PrivateIpAddress`` parameter (https://github.com/ansible-collections/community.aws/pull/328).
- ec2_vpc_endpoint - ensure ``changed`` is correctly set when deleting an endpoint (https://github.com/ansible-collections/community.aws/pull/362).
- ec2_vpc_endpoint - fix exception when attempting to delete an endpoint which has already been deleted (https://github.com/ansible-collections/community.aws/pull/362).
- ecs_task - use `required_if` to enforce mandatory parameters based on specified operation (https://github.com/ansible-collections/community.aws/pull/402).
- elb_application_lb - during the removal of an instance, the associated listeners are also removed.

v1.3.0
======

Minor Changes
-------------

- ec2_vpc_igw - Add AWSRetry decorators to improve reliability (https://github.com/ansible-collections/community.aws/pull/318).
- ec2_vpc_igw - Add ``purge_tags`` parameter so that tags can be added without purging existing tags to match the collection standard tagging behaviour (https://github.com/ansible-collections/community.aws/pull/318).
- ec2_vpc_igw_info - Add AWSRetry decorators to improve reliability (https://github.com/ansible-collections/community.aws/pull/318).
- ec2_vpc_igw_info - Add ``convert_tags`` parameter so that tags can be returned in standard dict format rather than the both list of dict format (https://github.com/ansible-collections/community.aws/pull/318).
- rds_instance - set ``no_log=False`` on ``force_update_password`` to clear warning (https://github.com/ansible-collections/community.aws/issues/241).
- redshift - add support for setting tags.
- s3_lifecycle - Add support for intelligent tiering and deep archive storage classes (https://github.com/ansible-collections/community.aws/issues/270)

Deprecated Features
-------------------

- ec2_vpc_igw_info - After 2022-06-22 the ``convert_tags`` parameter default value will change from ``False`` to ``True`` to match the collection standard behavior (https://github.com/ansible-collections/community.aws/pull/318).

Bugfixes
--------

- aws_kms_info - fixed incompatibility with external and custom key-store keys. The module was attempting to call `GetKeyRotationStatus`, which raises `UnsupportedOperationException` for these key types (https://github.com/ansible-collections/community.aws/pull/311).
- ec2_win_password - on success return state as not changed (https://github.com/ansible-collections/community.aws/issues/145)
- ec2_win_password - return failed if unable to decode the password (https://github.com/ansible-collections/community.aws/issues/142)
- ecs_service - fix element type for ``load_balancers`` parameter (https://github.com/ansible-collections/community.aws/issues/265).
- ecs_taskdefinition - fixes elements type for ``containers`` parameter (https://github.com/ansible-collections/community.aws/issues/264).
- iam_policy - Added jittered_backoff to handle AWS rate limiting (https://github.com/ansible-collections/community.aws/pull/324).
- iam_policy_info - Added jittered_backoff to handle AWS rate limiting (https://github.com/ansible-collections/community.aws/pull/324).
- kinesis_stream - fixes issue where kinesis streams with > 100 shards get stuck in an infinite loop (https://github.com/ansible-collections/community.aws/pull/93)
- s3_sync - fix chunk_size calculation (https://github.com/ansible-collections/community.aws/issues/272)

New Modules
-----------

- s3_metrics_configuration - Manage s3 bucket metrics configuration in AWS

v1.2.1
======

Minor Changes
-------------

- aws_ssm connection plugin - Change the (internal) variable name from timeout to plugin_timeout to avoid conflicts with ansible/ansible default timeout (#69284,
- aws_ssm connection plugin - add STS token options to aws_ssm connection plugin.
- ec2_scaling_policy - Add support for step_adjustments
- ec2_scaling_policy - Migrate from boto to boto3
- rds_subnet_group module - Add Boto3 support and remove Boto support.

Bugfixes
--------

- aws_ssm connection plugin - namespace file uploads to S3 into unique folders per host, to prevent name collisions. Also deletes files from S3 to ensure temp files are not left behind. (https://github.com/ansible-collections/community.aws/issues/221, https://github.com/ansible-collections/community.aws/issues/222)
- rds_instance - fixed tag type conversion issue for creating read replicas.

v1.2.0
======

Minor Changes
-------------

- Add retries for aws_api_gateway when AWS throws `TooManyRequestsException`
- Migrate the remaning boto3 based modules to the module based helpers for creating AWS connections.

Bugfixes
--------

- aws_codecommit - fixes issue where module execution would fail if an existing repository has empty description (https://github.com/ansible-collections/community.aws/pull/195)
- aws_kms_info - fixes issue where module execution fails because certain AWS KMS keys (e.g. aws/acm) do not permit the calling the API kms:GetKeyRotationStatus (example - https://forums.aws.amazon.com/thread.jspa?threadID=312992) (https://github.com/ansible-collections/community.aws/pull/199)
- ec2_instance - Fix a bug where tags were updated in check_mode.
- ec2_instance - fixes issue where security groups were not changed if the instance already existed.  https://github.com/ansible-collections/community.aws/pull/22
- iam - Fix false positive warning regarding use of ``no_log`` on ``update_password``

v1.1.0
======

Minor Changes
-------------

- Remaining community.aws AnsibleModule based modules migrated to AnsibleAWSModule.
- sanity - add future imports in all missing places.

Deprecated Features
-------------------

- data_pipeline - the ``version`` option has been deprecated and will be removed in a later release. It has always been ignored by the module.
- ec2_eip - the ``wait_timeout`` option has been deprecated and will be removed in a later release. It has had no effect since Ansible 2.3.
- ec2_lc - the ``associate_public_ip_address`` option has been deprecated and will be removed after a later release. It has always been ignored by the module.
- elb_network_lb - in a later release, the default behaviour for the ``state`` option will change from ``absent`` to ``present``.  To maintain the existing behavior explicitly set state to ``absent``.
- iam_managed_policy - the ``fail_on_delete`` option has been deprecated and will be removed after a later release.  It has always been ignored by the module.
- iam_policy - in a later release, the default value for the ``skip_duplicates`` option will change from ``true`` to ``false``.  To maintain the existing behavior explicitly set it to ``true``.
- iam_policy - the ``policy_document`` option has been deprecated and will be removed after a later release. To maintain the existing behavior use the ``policy_json`` option and read the file with the ``lookup`` plugin.
- iam_role - in a later release, the ``purge_policies`` option (also know as ``purge_policy``) default value will change from ``true`` to ``false``
- s3_lifecycle - the ``requester_pays`` option has been deprecated and will be removed after a later release. It has always been ignored by the module.
- s3_sync - the ``retries`` option has been deprecated and will be removed after 2022-06-01. It has always been ignored by the module.

v1.0.0
======

Minor Changes
-------------

- Allow all params that boto support in aws_api_gateway module
- aws_acm - Add the module to group/aws for module_defaults.
- aws_acm - Update automatic retries to stabilize the integration tests.
- aws_codecommit - Support updating the description
- aws_kms - Adds the ``enable_key_rotation`` option to enable or disable automatically key rotation.
- aws_kms - code refactor, some error messages updated
- aws_kms_info - Adds the ``enable_key_rotation`` info to the return value.
- ec2_asg - Add support for Max Instance Lifetime
- ec2_asg - Add the ability to use mixed_instance_policy in launch template driven autoscaling groups
- ec2_asg - Migrated to AnsibleAWSModule
- ec2_placement_group - make ``name`` a required field.
- ecs_task_definition - Add network_mode=default to support Windows ECS tasks.
- elb_network_lb - added support to UDP and TCP_UDP protocols
- elb_target - add awsretry to prevent rate exceeded errors (https://github.com/ansible/ansible/issues/51108)
- elb_target_group - allow UDP and TCP_UDP protocols; permit only HTTP/HTTPS health checks using response codes and paths
- iam - make ``name`` a required field.
- iam_cert - make ``name`` a required field.
- iam_policy - The iam_policy module has been migrated from boto to boto3.
- iam_policy - make ``iam_name`` a required field.
- iam_role - Add support for managing the maximum session duration
- iam_role - Add support for removing the related instance profile when we delete the role
- iam_role, iam_user and iam_group - the managed_policy option has been renamed to managed_policies (with an alias added)
- iam_role, iam_user and iam_group - the purge_policy option has been renamed to purge_policies (with an alias added)
- lambda - add a tracing_mode parameter to set the TracingConfig for AWS X-Ray. Also allow updating Lambda runtime.
- purefa_volume - Change I(qos) parameter to I(bw_iops), but retain I(qos) as an alias for backwards compatability (https://github.com/ansible/ansible/pull/61577).
- redshift - Add AWSRetry calls for errors outside our control
- route53 - the module now has diff support.
- sns_topic - Add backoff when we get Topic ``NotFound`` exceptions while listing the subscriptions.
- sqs_queue - Add support for tagging, KMS and FIFO queues
- sqs_queue - updated to use boto3 instead of boto

Deprecated Features
-------------------

- cloudformation - The ``template_format`` option had no effect since Ansible 2.3 and will be removed after 2022-06-01
- data_pipeline - The ``version`` option had no effect and will be removed after 2022-06-01
- ec2_eip - The ``wait_timeout`` option had no effect and will be removed after 2022-06-01
- ec2_key - The ``wait_timeout`` option had no effect and will be removed after 2022-06-01
- ec2_key - The ``wait`` option had no effect and will be removed after 2022-06-01
- ec2_lc - The ``associate_public_ip_address`` option had no effect and will be removed after 2022-06-01
- elb_network_lb - The current default value of the ``state`` option has been deprecated and will change from absent to present after 2022-06-01
- iam_managed_policy - The ``fail_on_delete`` option had no effect and will be removed after 2022-06-01
- iam_policy - The ``policy_document`` will be removed after 2022-06-01.  To maintain the existing behavior use the ``policy_json`` option and read the file with the ``lookup`` plugin.
- iam_policy - The default value of ``skip_duplicates`` will change after 2022-06-01 from ``true`` to ``false``.
- iam_role - The default value of the purge_policies has been deprecated and will change from true to false after 2022-06-01
- s3_lifecycle - The ``requester_pays`` option had no effect and will be removed after 2022-06-01
- s3_sync - The ``retries`` option had no effect and will be removed after 2022-06-01

Bugfixes
--------

- **security issue** - Convert CLI provided passwords to text initially, to prevent unsafe context being lost when converting from bytes->text during post processing of PlayContext. This prevents CLI provided passwords from being incorrectly templated (CVE-2019-14856)
- **security issue** - Update ``AnsibleUnsafeText`` and ``AnsibleUnsafeBytes`` to maintain unsafe context by overriding ``.encode`` and ``.decode``. This prevents future issues with ``to_text``, ``to_bytes``, or ``to_native`` removing the unsafe wrapper when converting between string types (CVE-2019-14856)
- azure_rm_dnsrecordset_info - no longer returns empty ``azure_dnsrecordset`` facts when called as ``_info`` module.
- azure_rm_resourcegroup_info - no longer returns ``azure_resourcegroups`` facts when called as ``_info`` module.
- azure_rm_storageaccount_info - no longer returns empty ``azure_storageaccounts`` facts when called as ``_info`` module.
- azure_rm_virtualmachineimage_info - no longer returns empty ``azure_vmimages`` facts when called as ``_info`` module.
- azure_rm_virtualmachinescaleset_info - fix wrongly empty result, or ``ansible_facts`` result, when called as ``_info`` module.
- azure_rm_virtualnetwork_info - no longer returns empty ``azure_virtualnetworks`` facts when called as ``_info`` module.
- cloudfront_distribution - Always add field_level_encryption_id to cache behaviour to match AWS requirements
- cloudwatchlogs_log_group - Fix a KeyError when updating a log group that does not have a retention period (https://github.com/ansible/ansible/issues/47945)
- cloudwatchlogs_log_group_info - remove limitation of max 50 results
- ec2_asg - Ensure "wait" is honored during replace operations
- ec2_launch_template - Update output to include latest_version and default_version, matching the documentation
- ec2_transit_gateway - Use AWSRetry before ClientError is handled when describing transit gateways
- ec2_transit_gateway - fixed issue where auto_attach set to yes was not being honored (https://github.com/ansible/ansible/issues/61907)
- edgeos_config - fix issue where module would silently filter out encrypted passwords
- fixed issue with sns_topic's delivery_policy option resulting in changed always being true
- lineinfile - properly handle inserting a line when backrefs are enabled and the line already exists in the file (https://github.com/ansible/ansible/issues/63756)
- route53 - improve handling of octal encoded characters
- win_credential - Fix issue that errors when trying to add a ``name`` with wildcards.

New Modules
-----------

- aws_acm - Upload and delete certificates in the AWS Certificate Manager service
- aws_acm_info - Retrieve certificate information from AWS Certificate Manager service
- aws_api_gateway - Manage AWS API Gateway APIs
- aws_application_scaling_policy - Manage Application Auto Scaling Scaling Policies
- aws_batch_compute_environment - Manage AWS Batch Compute Environments
- aws_batch_job_definition - Manage AWS Batch Job Definitions
- aws_batch_job_queue - Manage AWS Batch Job Queues
- aws_codebuild - Create or delete an AWS CodeBuild project
- aws_codecommit - Manage repositories in AWS CodeCommit
- aws_codepipeline - Create or delete AWS CodePipelines
- aws_config_aggregation_authorization - Manage cross-account AWS Config authorizations
- aws_config_aggregator - Manage AWS Config aggregations across multiple accounts
- aws_config_delivery_channel - Manage AWS Config delivery channels
- aws_config_recorder - Manage AWS Config Recorders
- aws_config_rule - Manage AWS Config resources
- aws_direct_connect_connection - Creates, deletes, modifies a DirectConnect connection
- aws_direct_connect_gateway - Manage AWS Direct Connect gateway
- aws_direct_connect_link_aggregation_group - Manage Direct Connect LAG bundles
- aws_direct_connect_virtual_interface - Manage Direct Connect virtual interfaces
- aws_eks_cluster - Manage Elastic Kubernetes Service Clusters
- aws_elasticbeanstalk_app - Create, update, and delete an elastic beanstalk application
- aws_glue_connection - Manage an AWS Glue connection
- aws_glue_job - Manage an AWS Glue job
- aws_inspector_target - Create, Update and Delete Amazon Inspector Assessment Targets
- aws_kms - Perform various KMS management tasks.
- aws_kms_info - Gather information about AWS KMS keys
- aws_region_info - Gather information about AWS regions.
- aws_s3_bucket_info - Lists S3 buckets in AWS
- aws_s3_cors - Manage CORS for S3 buckets in AWS
- aws_secret - Manage secrets stored in AWS Secrets Manager.
- aws_ses_identity - Manages SES email and domain identity
- aws_ses_identity_policy - Manages SES sending authorization policies
- aws_ses_rule_set - Manages SES inbound receipt rule sets
- aws_sgw_info - Fetch AWS Storage Gateway information
- aws_ssm_parameter_store - Manage key-value pairs in aws parameter store.
- aws_step_functions_state_machine - Manage AWS Step Functions state machines
- aws_step_functions_state_machine_execution - Start or stop execution of an AWS Step Functions state machine.
- aws_waf_condition - Create and delete WAF Conditions
- aws_waf_info - Retrieve information for WAF ACLs, Rule , Conditions and Filters.
- aws_waf_rule - Create and delete WAF Rules
- aws_waf_web_acl - Create and delete WAF Web ACLs.
- cloudformation_exports_info - Read a value from CloudFormation Exports
- cloudformation_stack_set - Manage groups of CloudFormation stacks
- cloudfront_distribution - Create, update and delete AWS CloudFront distributions.
- cloudfront_info - Obtain facts about an AWS CloudFront distribution
- cloudfront_invalidation - create invalidations for AWS CloudFront distributions
- cloudfront_origin_access_identity - Create, update and delete origin access identities for a CloudFront distribution
- cloudtrail - manage CloudTrail create, delete, update
- cloudwatchevent_rule - Manage CloudWatch Event rules and targets
- cloudwatchlogs_log_group - create or delete log_group in CloudWatchLogs
- cloudwatchlogs_log_group_info - Get information about log_group in CloudWatchLogs
- cloudwatchlogs_log_group_metric_filter - Manage CloudWatch log group metric filter
- data_pipeline - Create and manage AWS Datapipelines
- dms_endpoint - Creates or destroys a data migration services endpoint
- dms_replication_subnet_group - creates or destroys a data migration services subnet group
- dynamodb_table - Create, update or delete AWS Dynamo DB tables
- dynamodb_ttl - Set TTL for a given DynamoDB table
- ec2_ami_copy - copies AMI between AWS regions, return new image id
- ec2_asg - Create or delete AWS AutoScaling Groups (ASGs)
- ec2_asg_info - Gather information about ec2 Auto Scaling Groups (ASGs) in AWS
- ec2_asg_lifecycle_hook - Create, delete or update AWS ASG Lifecycle Hooks.
- ec2_customer_gateway - Manage an AWS customer gateway
- ec2_customer_gateway_info - Gather information about customer gateways in AWS
- ec2_eip - manages EC2 elastic IP (EIP) addresses.
- ec2_eip_info - List EC2 EIP details
- ec2_elb - De-registers or registers instances from EC2 ELBs
- ec2_elb_info - Gather information about EC2 Elastic Load Balancers in AWS
- ec2_instance - Create & manage EC2 instances
- ec2_instance_info - Gather information about ec2 instances in AWS
- ec2_launch_template - Manage EC2 launch templates
- ec2_lc - Create or delete AWS Autoscaling Launch Configurations
- ec2_lc_find - Find AWS Autoscaling Launch Configurations
- ec2_lc_info - Gather information about AWS Autoscaling Launch Configurations.
- ec2_metric_alarm - Create/update or delete AWS Cloudwatch 'metric alarms'
- ec2_placement_group - Create or delete an EC2 Placement Group
- ec2_placement_group_info - List EC2 Placement Group(s) details
- ec2_scaling_policy - Create or delete AWS scaling policies for Autoscaling groups
- ec2_snapshot_copy - Copies an EC2 snapshot and returns the new Snapshot ID.
- ec2_transit_gateway - Create and delete AWS Transit Gateways
- ec2_transit_gateway_info - Gather information about ec2 transit gateways in AWS
- ec2_vpc_egress_igw - Manage an AWS VPC Egress Only Internet gateway
- ec2_vpc_endpoint - Create and delete AWS VPC Endpoints.
- ec2_vpc_endpoint_info - Retrieves AWS VPC endpoints details using AWS methods.
- ec2_vpc_igw - Manage an AWS VPC Internet gateway
- ec2_vpc_igw_info - Gather information about internet gateways in AWS
- ec2_vpc_nacl - create and delete Network ACLs.
- ec2_vpc_nacl_info - Gather information about Network ACLs in an AWS VPC
- ec2_vpc_nat_gateway - Manage AWS VPC NAT Gateways.
- ec2_vpc_nat_gateway_info - Retrieves AWS VPC Managed Nat Gateway details using AWS methods.
- ec2_vpc_peer - create, delete, accept, and reject VPC peering connections between two VPCs.
- ec2_vpc_peering_info - Retrieves AWS VPC Peering details using AWS methods.
- ec2_vpc_route_table - Manage route tables for AWS virtual private clouds
- ec2_vpc_route_table_info - Gather information about ec2 VPC route tables in AWS
- ec2_vpc_vgw - Create and delete AWS VPN Virtual Gateways.
- ec2_vpc_vgw_info - Gather information about virtual gateways in AWS
- ec2_vpc_vpn - Create, modify, and delete EC2 VPN connections.
- ec2_vpc_vpn_info - Gather information about VPN Connections in AWS.
- ec2_win_password - Gets the default administrator password for ec2 windows instances
- ecs_attribute - manage ecs attributes
- ecs_cluster - Create or terminate ECS clusters.
- ecs_ecr - Manage Elastic Container Registry repositories
- ecs_service - Create, terminate, start or stop a service in ECS
- ecs_service_info - List or describe services in ECS
- ecs_tag - create and remove tags on Amazon ECS resources
- ecs_task - Run, start or stop a task in ecs
- ecs_taskdefinition - register a task definition in ecs
- ecs_taskdefinition_info - Describe a task definition in ECS
- efs - create and maintain EFS file systems
- efs_info - Get information about Amazon EFS file systems
- elasticache - Manage cache clusters in Amazon ElastiCache
- elasticache_info - Retrieve information for AWS ElastiCache clusters
- elasticache_parameter_group - Manage cache parameter groups in Amazon ElastiCache.
- elasticache_snapshot - Manage cache snapshots in Amazon ElastiCache
- elasticache_subnet_group - manage ElastiCache subnet groups
- elb_application_lb - Manage an Application load balancer
- elb_application_lb_info - Gather information about application ELBs in AWS
- elb_classic_lb - Creates or destroys Amazon ELB.
- elb_classic_lb_info - Gather information about EC2 Elastic Load Balancers in AWS
- elb_instance - De-registers or registers instances from EC2 ELBs
- elb_network_lb - Manage a Network Load Balancer
- elb_target - Manage a target in a target group
- elb_target_group - Manage a target group for an Application or Network load balancer
- elb_target_group_info - Gather information about ELB target groups in AWS
- elb_target_info - Gathers which target groups a target is associated with.
- execute_lambda - Execute an AWS Lambda function
- iam - Manage IAM users, groups, roles and keys
- iam_cert - Manage server certificates for use on ELBs and CloudFront
- iam_group - Manage AWS IAM groups
- iam_managed_policy - Manage User Managed IAM policies
- iam_mfa_device_info - List the MFA (Multi-Factor Authentication) devices registered for a user
- iam_password_policy - Update an IAM Password Policy
- iam_policy - Manage inline IAM policies for users, groups, and roles
- iam_policy_info - Retrieve inline IAM policies for users, groups, and roles
- iam_role - Manage AWS IAM roles
- iam_role_info - Gather information on IAM roles
- iam_saml_federation - Maintain IAM SAML federation configuration.
- iam_server_certificate_info - Retrieve the information of a server certificate
- iam_user - Manage AWS IAM users
- iam_user_info - Gather IAM user(s) facts in AWS
- kinesis_stream - Manage a Kinesis Stream.
- lambda - Manage AWS Lambda functions
- lambda_alias - Creates, updates or deletes AWS Lambda function aliases
- lambda_event - Creates, updates or deletes AWS Lambda function event mappings
- lambda_facts - Gathers AWS Lambda function details as Ansible facts
- lambda_info - Gathers AWS Lambda function details
- lambda_policy - Creates, updates or deletes AWS Lambda policy statements.
- lightsail - Manage instances in AWS Lightsail
- rds - create, delete, or modify Amazon rds instances, rds snapshots, and related facts
- rds_instance - Manage RDS instances
- rds_instance_info - obtain information about one or more RDS instances
- rds_param_group - manage RDS parameter groups
- rds_snapshot - manage Amazon RDS snapshots.
- rds_snapshot_info - obtain information about one or more RDS snapshots
- rds_subnet_group - manage RDS database subnet groups
- redshift_cross_region_snapshots - Manage Redshift Cross Region Snapshots
- redshift_info - Gather information about Redshift cluster(s)
- route53 - add or delete entries in Amazons Route53 DNS service
- route53_health_check - Add or delete health-checks in Amazons Route53 DNS service
- route53_info - Retrieves route53 details using AWS methods
- route53_zone - add or delete Route53 zones
- s3_bucket_notification - Creates, updates or deletes S3 Bucket notification for lambda
- s3_lifecycle - Manage s3 bucket lifecycle rules in AWS
- s3_logging - Manage logging facility of an s3 bucket in AWS
- s3_sync - Efficiently upload multiple files to S3
- s3_website - Configure an s3 bucket as a website
- sns - Send Amazon Simple Notification Service messages
- sns_topic - Manages AWS SNS topics and subscriptions
- sqs_queue - Creates or deletes AWS SQS queues.
- sts_assume_role - Assume a role using AWS Security Token Service and obtain temporary credentials
- sts_session_token - Obtain a session token from the AWS Security Token Service
