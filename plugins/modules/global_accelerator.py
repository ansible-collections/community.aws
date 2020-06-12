from ansible_collections.amazon.aws.plugins.module_utils.aws.core import AnsibleAWSModule
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import (
    AWSRetry,
    camel_dict_to_snake_dict,
    boto3_tag_list_to_ansible_dict,
    compare_aws_tags,
    ansible_dict_to_boto3_tag_list,
)

# Non-ansible imports
try:
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:
    pass

def get_accelerator(connection, module, name, arn):
    accelerator = None

    if name and not arn:
        module.debug("Looking up Accelerators with Name {}".format(name))
        # There is no direct way to look up Accelerators by ARN
        # So we fetch them all and do client side filtering
        try:
            paginator = connection.get_paginator('list_accelerators')

            accelerators = AWSRetry.jittered_backoff()(paginator.paginate)().build_full_result()['Accelerators']

        except (BotoCoreError, ClientError) as e:
            module.fail_json_aws(e)

        # Filter all results for the specified name
        accelerators = [a for a in accelerators if a['Name'] == name]

        if len(accelerators) > 1:
            module.fail_json(
                msg="More then one accelerator found with name {}. Refusing to act".format(name)
            )

        if not accelerators:
            module.warn("No accelerator found with name {}".format(name))
        else:
            accelerator = accelerators[0]

    if arn:
        accelerator = AWSRetry.jittered_backoff()(
            connection.describe_accelerator
        )(AcceleratorArn=arn)['Accelerator']

    if accelerator:
        accelerator = camel_dict_to_snake_dict(accelerator)

    return accelerator


class GlobalAccelerator(object):
    def __init__(self, connection, module):
        self.connection = connection
        self.module = module
        self.changed = False
        self.accelerator = None
        self.new_accelerator = False

        self.name = module.params.get("name")
        self.arn = module.params.get("arn")
        self.ip_address_type = module.params.get("ip_address_type")
        self.ip_addresses = module.params.get("ip_addresses")
        self.enabled = module.params.get("enabled")
        self.idempotency_token = module.params.get("idempotency_token")
        self.state = module.params.get("state")

        self.flow_logs_enabled = module.params.get('flow_logs_enabled')
        self.flow_logs_s3_bucket = module.params.get('flow_logs_s3_bucket')
        self.flow_logs_s3_prefix = module.params.get('flow_logs_s3_prefix')


        self.purge_tags = module.params.get("purge_tags")
        if module.params.get("tags") is not None:
            self.tags = ansible_dict_to_boto3_tag_list(module.params.get("tags"))
        else:
            self.tags = None

        self.accelerator = get_accelerator(connection, module, self.name, self.arn)
        if self.accelerator is not None:
            self.accelerator_attributes = self.get_accelerator_attributes()
            self.accelerator['tags'] = self.get_accelerator_tags()
        else:
            self.accelerator_attributes = None

    def create_accelerator(self):
        params = {
            'Enabled': self.enabled,
            'IdempotencyToken': self.idempotency_token,
            'IpAddressType': self.ip_address_type,
            'Name': self.name,
        }

        if self.tags:
            params['Tags'] = self.tags

        if self.ip_addresses:
            params['IpAddresses'] = self.ip_addresses

        try:
            accelerator = AWSRetry.jittered_backoff()(
                self.connection.create_accelerator
            )(**params)['Accelerator']

            self.accelerator = camel_dict_to_snake_dict(accelerator)

            self.changed = True
            self.new_accelerator = True
        except (BotoCoreError, ClientError) as e:
            self.module.fail_json_aws(e)

    def update_accelerator_attributes(self):
        self.accelerator_attributes = self.get_accelerator_attributes()

    def get_accelerator_attributes(self):
        try:
            attr_list = AWSRetry.jittered_backoff()(
                self.connection.describe_accelerator_attributes
            )(AcceleratorArn=self.accelerator['accelerator_arn'])['AcceleratorAttributes']

            ga_attributes = camel_dict_to_snake_dict(attr_list)
        except (BotoCoreError, ClientError) as e:
            self.module.fail_json_aws(e)

        # Replace '.' with '_' in attribute key names to make it more Ansibley
        return dict((k.replace('.', '_'), v) for k, v in ga_attributes.items())

    def get_accelerator_tags(self):
        try:
            tags_list = AWSRetry.jittered_backoff()(
                self.connection.list_tags_for_resource
            )(ResourceArn=self.accelerator['accelerator_arn'])['Tags']

            return tags_list

        except (BotoCoreError, ClientError) as e:
            self.module.fail_json_aws(e)

    def modify_accelerator_attributes(self):
        update_attributes = {}

        if self.flow_logs_enabled is not None and self.flow_logs_enabled != self.accelerator_attributes['flow_logs_enabled']:
            update_attributes['flow_logs_enabled'] = self.flow_logs_enabled

        if self.flow_logs_s3_bucket is not None and self.flow_logs_s3_bucket != self.accelerator_attributes['flow_logs_s3_bucket']:
            update_attributes['flow_logs_s3_bucket'] = self.flow_logs_s3_bucket

        if self.flow_logs_s3_prefix is not None and self.flow_logs_s3_prefix != self.accelerator_attributes['flow_logs_s3_prefix']:
            update_attributes['flow_logs_s3_prefix'] = self.flow_logs_s3_prefix

        if update_attributes:
            try:
                AWSRetry.jittered_backoff()(
                    self.connection.update_accelerator_attributes
                )(LoadBalancerArn=self.accelerator['accelerator_arn'], Attributes=update_attributes)
                self.changed = True
            except (BotoCoreError, ClientError) as e:
                # Something went wrong setting attributes. If this ELB was created during this task, delete it to leave a consistent state
                if self.new_load_balancer:
                    AWSRetry.jittered_backoff()(self.connection.delete_load_balancer)(LoadBalancerArn=self.elb['LoadBalancerArn'])
                self.module.fail_json_aws(e)


    def compare_enabled(self):
        return self.enabled == self.accelerator['enabled']

    def compare_ip_type(self):
        return self.ip_address_type == self.accelerator['ip_address_type']

    def update_accelerator(self, skip_enabled=True, skip_ip_type=True):
        if skip_enabled and skip_ip_type:
            self.module.debug('Skipping updates to both enabled and ip_type')
            return

        kwargs = {}
        if not skip_enabled:
            self.module.debug('Updating enabled attribute')
            kwargs['Enabled'] = self.enabled

        if not skip_ip_type:
            self.module.debug('Updating ip_address_type')
            kwargs['IpAddressType'] = self.ip_address_type

        try:
            AWSRetry.jittered_backoff()(self.connection.update_accelerator)(
                AcceleratorArn=self.accelerator['accelerator_arn'],
                **kwargs
            )
        except (BotoCoreError, ClientError) as e:
            self.module.fail_json_aws(e)

        self.changed = True

    def delete_tags(self, tags_to_delete):
        try:
            AWSRetry.jittered_backoff()(
                self.connection.untag_resource
            )(ResourceArn=self.accelerator['accelerator_arn'], TagKeys=tags_to_delete)
        except (BotoCoreError, ClientError) as e:
            self.module.fail_json_aws(e)

        self.changed = True

    def modify_tags(self):
        try:
            AWSRetry.jittered_backoff()(
                self.connection.tag_resource
            )(ResourceArn=self.accelerator['accelerator_arn'], Tags=self.tags)
        except (BotoCoreError, ClientError) as e:
            self.module.fail_json_aws(e)

        self.changed = True

    def delete(self):
        try:
            AWSRetry.jittered_backoff()(
                self.connection.delete_accelerator
            )(AcceleratorArn=self.accelerator['accelerator_arn'])
        except (BotoCoreError, ClientError) as e:
            self.module.fail_json_aws(e)

        self.changed = True


def create_or_update_accelerator(accelerator_obj):
    if accelerator_obj.accelerator:

        accelerator_obj.update_accelerator(
            accelerator_obj.compare_enabled(),
            accelerator_obj.compare_ip_type()
        )

        if accelerator_obj.tags is not None:
            tags_need_modify, tags_to_delete = compare_aws_tags(
                boto3_tag_list_to_ansible_dict(accelerator_obj.accelerator['tags']),
                boto3_tag_list_to_ansible_dict(accelerator_obj.tags),
                accelerator_obj.purge_tags
            )

            if tags_to_delete:
                accelerator_obj.delete_tags(tags_to_delete)
            if tags_need_modify:
                accelerator_obj.modify_tags()

    else:
        accelerator_obj.create_accelerator()

    accelerator_obj.update_accelerator_attributes()
    accelerator_obj.modify_accelerator_attributes()

    snaked_accelerator = camel_dict_to_snake_dict(accelerator_obj.accelerator)
    snaked_accelerator.update(camel_dict_to_snake_dict(accelerator_obj.accelerator_attributes))

    accelerator_obj.module.exit_json(changed=accelerator_obj.changed, **snaked_accelerator)


def delete_accelerator(accelerator_obj):
    if accelerator_obj.accelerator:
        accelerator_obj.delete()


def main():
    argument_spec = dict(
        name=dict(type='str'),
        arn=dict(type='str'),
        ip_address_type=dict(default='IPV4', choices=['IPV4']),  # I assume there will eventually be ipv6 but not yet. Case matters.
        ip_addresses=dict(type='list', default=[]),  # Max 2
        enabled=dict(type='bool', default=True),
        idempotency_token=dict(type='str', required=False),
        tags=dict(type='dict'),
        state=dict(choices=['present', 'absent'], default='present'),
        purge_tags=dict(type='bool', default=False),
        flow_logs_enabled=dict(type='bool', default=False),
        flow_logs_s3_bucket=dict(type='str'),
        flow_logs_s3_prefix=dict(type='str'),
        region=dict(default='us-west-2', choices=['us-west-2']),  # Only supported in us-west-2
    )

    module = AnsibleAWSModule(argument_spec=argument_spec,
                              mutually_exclusive=[['name', 'arn']],
                              required_if=[
                                  ('flow_logs_enabled', True, ['flow_logs_s3_bucket', 'flow_logs_s3_prefix']),
                              ])

    ip_addresses = module.params.get('ip_addresses')
    if len(ip_addresses) > 2:
        module.fail_json(msg="Up to 2 'ip_addresses' are allowed")

    state = module.params.get("state")
    enabled = module.params.get("enabled")

    if enabled and state == 'absent':
        module.fail_json(msg="Can not delete a Global Accelerator if it is enabled")

    connection = module.client('globalaccelerator')

    accelerator = GlobalAccelerator(connection, module)

    if state == 'present':
        create_or_update_accelerator(accelerator)
    else:
        delete_accelerator(accelerator)


if __name__ == '__main__':
    main()
