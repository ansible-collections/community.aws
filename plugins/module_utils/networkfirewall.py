# Copyright: Ansible Project
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

from copy import deepcopy

from ansible.module_utils._text import to_text
from ansible.module_utils.common.dict_transformations import camel_dict_to_snake_dict
from ansible.module_utils.six import string_types

from ansible_collections.amazon.aws.plugins.module_utils.core import is_boto3_error_code
from ansible_collections.amazon.aws.plugins.module_utils.ec2 import AWSRetry
from ansible_collections.amazon.aws.plugins.module_utils.tagging import boto3_tag_list_to_ansible_dict
from ansible_collections.amazon.aws.plugins.module_utils.tagging import ansible_dict_to_boto3_tag_list
from ansible_collections.amazon.aws.plugins.module_utils.tagging import compare_aws_tags

from ansible_collections.community.aws.plugins.module_utils.base import Boto3Mixin
from ansible_collections.community.aws.plugins.module_utils.base import BaseResourceManager
from ansible_collections.community.aws.plugins.module_utils.base import BaseWaiterFactory


def _merge_set(current, new, purge):
    _current = set(current)
    _new = set(new)
    if purge:
        final = _new
    else:
        final = _new | _current

    return final


def _merge_dict(current, new, purge):
    _current = deepcopy(current)
    if purge:
        final = dict()
    else:
        final = _current
    final.update(new)

    return final


def _string_list(value):
    if isinstance(value, string_types):
        value = [value]
    elif isinstance(value, bool):
        value = [to_text(value).lower()]
    elif isinstance(value, list):
        value = [to_text(v) for v in value]
    else:
        value = [to_text(value)]
    return value


class NetworkFirewallWaiterFactory(BaseWaiterFactory):
    def __init__(self, module):
        # the AWSRetry wrapper doesn't support the wait functions (there's no
        # public call we can cleanly wrap)
        client = module.client('network-firewall')
        super(NetworkFirewallWaiterFactory, self).__init__(module, client)

    @property
    def _waiter_model_data(self):
        data = super(NetworkFirewallWaiterFactory, self)._waiter_model_data
        nw_data = dict(
            rule_group_active=dict(
                operation='DescribeRuleGroup',
                delay=5, maxAttempts=120,
                acceptors=[
                    dict(state='success', matcher='path', expected='ACTIVE', argument='RuleGroupResponse.RuleGroupStatus'),
                ]
            ),
            rule_group_deleted=dict(
                operation='DescribeRuleGroup',
                delay=5, maxAttempts=120,
                acceptors=[
                    dict(state='retry', matcher='path', expected='DELETING', argument='RuleGroupResponse.RuleGroupStatus'),
                    dict(state='success', matcher='error', expected='ResourceNotFoundException'),
                ]
            ),
        )
        data.update(nw_data)
        return data


class NetworkFirewallBoto3Mixin(Boto3Mixin):
    def __init__(self, module):
        r"""
        Parameters:
            module (AnsibleAWSModule): An Ansible module.
        """
        self.nf_waiter_factory = NetworkFirewallWaiterFactory(module)
        super(NetworkFirewallBoto3Mixin, self).__init__(module)
        self._update_token = None


class NFRuleGroupBoto3Mixin(NetworkFirewallBoto3Mixin):
    # Paginators can't be (easily) wrapped, so we wrap this method with the
    # retry - retries the full fetch, but better than simply giving up.
    @AWSRetry.jittered_backoff()
    def _paginated_list_rule_groups(self, **params):
        paginator = self.client.get_paginator('list_rule_groups')
        result = paginator.paginate(**params).build_full_result()
        return result.get('RuleGroups', None)

    @Boto3Mixin.aws_error_handler('list all rule groups')
    def _list_rule_groups(self, **params):
        return self._paginated_list_rule_groups(**params)

    @Boto3Mixin.aws_error_handler('describe rule group')
    def _describe_rule_group(self, **params):
        try:
            result = self.client.describe_rule_group(aws_retry=True, **params)
        except is_boto3_error_code('ResourceNotFoundException'):
            return None

        update_token = result.get('UpdateToken', None)
        if update_token:
            self._update_token = update_token
        rule_group = result.get('RuleGroup', None)
        metadata = result.get('RuleGroupResponse', None)
        return dict(RuleGroup=rule_group, RuleGroupMetadata=metadata)

    @Boto3Mixin.aws_error_handler('create rule group')
    def _create_rule_group(self, **params):
        result = self.client.create_rule_group(aws_retry=True, **params)

        update_token = result.get('UpdateToken', None)
        if update_token:
            self._update_token = update_token
        return result.get('RuleGroupResponse', None)

    @Boto3Mixin.aws_error_handler('update rule group')
    def _update_rule_group(self, **params):
        if self._update_token and 'UpdateToken' not in params:
            params['UpdateToken'] = self._update_token
        result = self.client.update_rule_group(aws_retry=True, **params)

        update_token = result.get('UpdateToken', None)
        if update_token:
            self._update_token = update_token
        return result.get('RuleGroupResponse', None)

    @Boto3Mixin.aws_error_handler('update rule group')
    def _delete_rule_group(self, **params):
        try:
            result = self.client.delete_rule_group(aws_retry=True, **params)
        except is_boto3_error_code('ResourceNotFoundException'):
            return None

        return result.get('RuleGroupResponse', None)

    @Boto3Mixin.aws_error_handler('firewall rule to finish deleting')
    def _wait_rule_group_deleted(self, **params):
        waiter = self.nf_waiter_factory.get_waiter('rule_group_deleted')
        waiter.wait(**params)

    @Boto3Mixin.aws_error_handler('firewall rule to become active')
    def _wait_rule_group_active(self, **params):
        waiter = self.nf_waiter_factory.get_waiter('rule_group_active')
        waiter.wait(**params)


class BaseNetworkFirewallManager(BaseResourceManager):
    def __init__(self, module):
        r"""
        Parameters:
            module (AnsibleAWSModule): An Ansible module.
        """
        super().__init__(module)

        self.client = self._create_client()

        # Network Firewall returns a token when you perform create/get/update
        # actions
        self._preupdate_metadata = dict()
        self._metadata_updates = dict()
        self._tagging_updates = dict()

    @Boto3Mixin.aws_error_handler('connect to AWS')
    def _create_client(self, client_name='network-firewall'):
        client = self.module.client(client_name, retry_decorator=AWSRetry.jittered_backoff())
        return client

    def _get_id_params(self):
        return dict()

    def _check_updates_pending(self):
        if self._metadata_updates:
            return True
        return super(BaseNetworkFirewallManager, self)._check_updates_pending()

    def _merge_metadata_changes(self, filter_immutable=True):
        """
        Merges the contents of the 'pre_update' metadata variables
        with the pending updates
        """
        metadata = deepcopy(self._preupdate_metadata)
        metadata.update(self._metadata_updates)

        if filter_immutable:
            metadata = self._filter_immutable_metadata_attributes(metadata)

        return metadata

    def _merge_changes(self, filter_metadata=True):
        """
        Merges the contents of the 'pre_update' resource and metadata variables
        with the pending updates
        """
        metadata = self._merge_metadata_changes(filter_metadata)
        resource = self._merge_resource_changes()
        return metadata, resource

    def _filter_immutable_metadata_attributes(self, metadata):
        """
        Removes information from the metadata which can't be updated.
        Returns a *copy* of the metadata dictionary.
        """
        return deepcopy(metadata)

    def _flush_create(self):
        changed = super(BaseNetworkFirewallManager, self)._flush_create()
        self._metadata_updates = dict()
        return changed

    def _flush_update(self):
        changed = super(BaseNetworkFirewallManager, self)._flush_update()
        self._metadata_updates = dict()
        return changed

    @BaseResourceManager.aws_error_handler('set tags on resource')
    def _add_tags(self, **params):
        self.client.tag_resource(aws_retry=True, **params)
        return True

    @BaseResourceManager.aws_error_handler('unset tags on resource')
    def _remove_tags(self, **params):
        self.client.untag_resource(aws_retry=True, **params)
        return True

    def _get_preupdate_arn(self):
        return self._preupdate_metadata.get('Arn')

    def _set_metadata_value(self, key, value, description=None, immutable=False):
        if value is None:
            return False
        if value == self._get_metadata_value(key):
            return False
        if immutable and self.original_resource:
            if description is None:
                description = key
            self.module.fail_json(msg='{0} can not be updated after creation'
                                  .format(description))
        self._metadata_updates[key] = value
        self.changed = True
        return True

    def _get_metadata_value(self, key, default=None):
        return self._metadata_updates.get(key, self._preupdate_metadata.get(key, default))

    def _flush_tagging(self):
        changed = False
        tags_to_add = self._tagging_updates.get('add')
        tags_to_remove = self._tagging_updates.get('remove')

        resource_arn = self._get_preupdate_arn()
        if not resource_arn:
            return False

        if tags_to_add:
            changed = True
            tags = ansible_dict_to_boto3_tag_list(tags_to_add)
            if not self.module.check_mode:
                self._add_tags(ResourceArn=resource_arn, Tags=tags)
        if tags_to_remove:
            changed = True
            if not self.module.check_mode:
                self._remove_tags(ResourceArn=resource_arn, TagKeys=tags_to_remove)

        return changed

    def set_tags(self, tags, purge_tags):

        if tags is None:
            return False
        changed = False

        # Tags are returned as a part of the metadata, but have to be updated
        # via dedicated tagging methods
        current_tags = boto3_tag_list_to_ansible_dict(self._get_metadata_value('Tags', []))

        # So that diff works in check mode we need to know the full target state
        if purge_tags:
            desired_tags = deepcopy(tags)
        else:
            desired_tags = deepcopy(current_tags)
            desired_tags.update(tags)

        tags_to_add, tags_to_remove = compare_aws_tags(current_tags, tags, purge_tags)

        if tags_to_add:
            self._tagging_updates['add'] = tags_to_add
            changed = True
        if tags_to_remove:
            self._tagging_updates['remove'] = tags_to_remove
            changed = True

        if changed:
            # Tags are a stored as a list, but treated like a list, the
            # simplisic '==' in _set_metadata_value doesn't do the comparison
            # properly
            return self._set_metadata_value('Tags', ansible_dict_to_boto3_tag_list(desired_tags))

        return False


class NetworkFirewallRuleManager(NFRuleGroupBoto3Mixin, BaseNetworkFirewallManager):

    RULE_TYPES = frozenset(['StatelessRulesAndCustomActions', 'StatefulRules',
                            'RulesSourceList', 'RulesString'])

    name = None
    rule_type = None
    arn = None

    def __init__(self, module, name=None, rule_type=None, arn=None):
        super().__init__(module)
        # Name parameter is unique (by region) and can not be modified.
        self.name = name
        self.rule_type = rule_type
        self.arn = arn
        if self.name or self.arn:
            rule_group = deepcopy(self.get_rule_group())
            self.original_resource = rule_group

    def _extra_error_output(self):
        output = super(NetworkFirewallRuleManager, self)._extra_error_output()
        if self.name:
            output['RuleGroupName'] = self.name
        if self.rule_type:
            output['Type'] = self.rule_type
        if self.arn:
            output['RuleGroupArn'] = self.arn
        return output

    def _filter_immutable_metadata_attributes(self, metadata):
        metadata = super(NetworkFirewallRuleManager, self)._filter_immutable_metadata_attributes(metadata)
        metadata.pop('RuleGroupArn', None)
        metadata.pop('RuleGroupName', None)
        metadata.pop('RuleGroupId', None)
        metadata.pop('Type', None)
        metadata.pop('Capacity', None)
        metadata.pop('RuleGroupStatus', None)
        metadata.pop('Tags', None)
        metadata.pop('ConsumedCapacity', None)
        metadata.pop('NumberOfAssociations', None)
        return metadata

    def _get_preupdate_arn(self):
        return self._get_metadata_value('RuleGroupArn')

    def _get_id_params(self, name=None, rule_type=None, arn=None):
        if arn:
            return dict(RuleGroupArn=arn)
        if self.arn:
            return dict(RuleGroupArn=self.arn)
        if not name:
            name = self.name
        if not rule_type:
            rule_type = self.rule_type
        if rule_type:
            rule_type = rule_type.upper()
        if not rule_type or not name:
            # Users should never see this, but let's cover ourself
            self.module.fail_json(msg='Rule identifier parameters missing')
        return dict(RuleGroupName=name, Type=rule_type)

    @staticmethod
    def _empty_rule_variables():
        return dict(IPSets=dict(), PortSets=dict())

    @staticmethod
    def _transform_rule_variables(variables):
        return {k: dict(Definition=_string_list(v)) for (k, v) in variables.items()}

    def delete(self, name=None, rule_type=None, arn=None):

        id_params = self._get_id_params(name=name, rule_type=rule_type, arn=None)
        result = self._get_rule_group(**id_params)

        if not result:
            return False

        self.updated_resource = dict()

        # Rule Group is already in the process of being deleted (takes time)
        rule_status = self._get_metadata_value('RuleGroupStatus', '').upper()
        if rule_status == 'DELETING':
            self._wait_for_deletion()
            return False

        if self.module.check_mode:
            self.changed = True
            return True

        result = self._delete_rule_group(**id_params)
        self._wait_for_deletion()
        self.changed |= bool(result)
        return bool(result)

    def list(self, scope=None):
        params = dict()
        if scope:
            scope = scope.upper()
            params['Scope'] = scope
        rule_groups = self._list_rule_groups(**params)
        if not rule_groups:
            return list()

        return [r.get('Arn', None) for r in rule_groups]

    def _normalize_rule_variable(self, variable):
        if variable is None:
            return None
        return {k: variable.get(k, dict()).get('Definition', []) for k in variable.keys()}

    def _normalize_rule_variables(self, variables):
        if variables is None:
            return None
        result = dict()
        ip_sets = self._normalize_rule_variable(variables.get('IPSets', None))
        if ip_sets:
            result['ip_sets'] = ip_sets
        port_sets = self._normalize_rule_variable(variables.get('PortSets', None))
        if port_sets:
            result['port_sets'] = port_sets
        return result

    def _normalize_rule_group(self, rule_group):
        if rule_group is None:
            return None
        rule_variables = self._normalize_rule_variables(rule_group.get('RuleVariables', None))
        rule_group = self._normalize_boto3_resource(rule_group)
        if rule_variables is not None:
            rule_group['rule_variables'] = rule_variables
        return rule_group

    def _normalize_rule_group_metadata(self, rule_group_metadata):
        return self._normalize_boto3_resource(rule_group_metadata, add_tags=True)

    def _normalize_rule_group_result(self, result):
        if result is None:
            return None
        rule_group = self._normalize_rule_group(result.get('RuleGroup', None))
        rule_group_metadata = self._normalize_rule_group_metadata(result.get('RuleGroupMetadata', None))
        result = camel_dict_to_snake_dict(result)
        if rule_group:
            result['rule_group'] = rule_group
        if rule_group_metadata:
            result['rule_group_metadata'] = rule_group_metadata
        return result

    def _normalize_resource(self, resource):
        return self._normalize_rule_group_result(resource)

    def get_rule_group(self, name=None, rule_type=None, arn=None):

        id_params = self._get_id_params(name=name, rule_type=rule_type, arn=arn)
        result = self._get_rule_group(**id_params)

        if not result:
            return None

        rule_group = self._normalize_rule_group_result(result)
        return rule_group

    def set_description(self, description):
        return self._set_metadata_value('Description', description)

    def set_capacity(self, capacity):
        return self._set_metadata_value(
            'Capacity', capacity,
            description="Reserved Capacity", immutable=True)

    def _set_rule_option(self, option_name, description, value, immutable=False, default_value=None):
        if value is None:
            return False

        rule_options = deepcopy(self._get_resource_value('StatefulRuleOptions', dict()))
        if value == rule_options.get(option_name, default_value):
            return False
        if immutable and self.original_resource:
            self.module.fail_json(msg='{0} can not be updated after creation'
                                  .format(description))

        rule_options[option_name] = value

        return self._set_resource_value('StatefulRuleOptions', rule_options)

    def set_rule_order(self, order):
        RULE_ORDER_MAP = {
            'default': 'DEFAULT_ACTION_ORDER',
            'strict': 'STRICT_ORDER',
        }
        value = RULE_ORDER_MAP.get(order)
        changed = self._set_rule_option('RuleOrder', 'Rule order', value, True, 'DEFAULT_ACTION_ORDER')
        self.changed |= changed
        return changed

    def _set_rule_variables(self, set_name, variables, purge):
        if variables is None:
            return False

        variables = self._transform_rule_variables(variables)

        all_variables = deepcopy(self._get_resource_value('RuleVariables', self._empty_rule_variables()))

        current_variables = all_variables.get(set_name, dict())
        updated_variables = _merge_dict(current_variables, variables, purge)

        if current_variables == updated_variables:
            return False

        all_variables[set_name] = updated_variables

        return self._set_resource_value('RuleVariables', all_variables)

    def set_ip_variables(self, variables, purge):
        return self._set_rule_variables('IPSets', variables, purge)

    def set_port_variables(self, variables, purge):
        return self._set_rule_variables('PortSets', variables, purge)

    def _set_rule_source(self, rule_type, rules):
        if not rules:
            return False
        conflicting_types = self.RULE_TYPES.difference({rule_type})
        rules_source = deepcopy(self._get_resource_value('RulesSource', dict()))
        current_keys = set(rules_source.keys())
        conflicting_rule_type = conflicting_types.intersection(current_keys)
        if conflicting_rule_type:
            self.module.fail_json('Unable to add {0} rules, {1} rules already set'
                                  .format(rule_type, " and ".join(conflicting_rule_type)))

        original_rules = rules_source.get(rule_type, None)
        if rules == original_rules:
            return False
        rules_source[rule_type] = rules
        return self._set_resource_value('RulesSource', rules_source)

    def set_rule_string(self, rule):
        if rule is None:
            return False
        if not rule:
            self.module.fail_json('Rule string must include at least one rule')

        rule = "\n".join(_string_list(rule))
        return self._set_rule_source('RulesString', rule)

    def set_domain_list(self, options):
        if not options:
            return False
        changed = False
        domain_names = options.get('domain_names')
        home_net = options.get('source_ips', None)
        action = options.get('action')
        filter_http = options.get('filter_http', False)
        filter_https = options.get('filter_https', False)

        if home_net:
            # Seems a little kludgy but the HOME_NET ip variable is how you
            # configure which source CIDRs the traffic should be filtered for.
            changed |= self.set_ip_variables(dict(HOME_NET=home_net), purge=True)
        else:
            self.set_ip_variables(dict(), purge=True)

        # Perform some transformations
        target_types = []
        if filter_http:
            target_types.append('HTTP_HOST')
        if filter_https:
            target_types.append('TLS_SNI')

        if action == 'allow':
            action = 'ALLOWLIST'
        else:
            action = 'DENYLIST'

        # Finally build the 'rule'
        rule = dict(
            Targets=domain_names,
            TargetTypes=target_types,
            GeneratedRulesType=action,
        )
        changed |= self._set_rule_source('RulesSourceList', rule)
        return changed

    def _format_rule_options(self, options, sid):
        formatted_options = []
        opt = dict(Keyword='sid:{0}'.format(sid))
        formatted_options.append(opt)
        if options:
            for option in sorted(options.keys()):
                opt = dict(Keyword=option)
                settings = options.get(option)
                if settings:
                    opt['Settings'] = _string_list(settings)
                formatted_options.append(opt)
        return formatted_options

    def _format_stateful_rule(self, rule):
        options = self._format_rule_options(
            rule.get('rule_options', dict()),
            rule.get('sid'),
        )
        formatted_rule = dict(
            Action=rule.get('action').upper(),
            RuleOptions=options,
            Header=dict(
                Protocol=rule.get('protocol').upper(),
                Source=rule.get('source'),
                SourcePort=rule.get('source_port'),
                Direction=rule.get('direction').upper(),
                Destination=rule.get('destination'),
                DestinationPort=rule.get('destination_port'),
            ),
        )
        return formatted_rule

    def set_rule_list(self, rules):
        if rules is None:
            return False
        if not rules:
            self.module.fail_json(msg='Rule list must include at least one rule')

        formatted_rules = [self._format_stateful_rule(r) for r in rules]
        return self._set_rule_source('StatefulRules', formatted_rules)

    def _do_create_resource(self):
        metadata, resource = self._merge_changes(filter_metadata=False)
        params = metadata
        params.update(self._get_id_params())
        params['RuleGroup'] = resource
        response = self._create_rule_group(**params)
        return bool(response)

    def _generate_updated_resource(self):
        metadata, resource = self._merge_changes(filter_metadata=False)
        metadata.update(self._get_id_params())
        updated_resource = dict(
            RuleGroup=resource,
            RuleGroupMetadata=metadata
        )
        return updated_resource

    def _flush_create(self):
        # Apply some pre-flight tests before trying to run the creation.
        if 'Capacity' not in self._metadata_updates:
            self.module.fail_json('Capacity must be provided when creating a new Rule Group')

        rules_source = self._get_resource_value('RulesSource', dict())
        rule_type = self.RULE_TYPES.intersection(set(rules_source.keys()))
        if len(rule_type) != 1:
            self.module.fail_json('Exactly one of rule strings, domain list or rule list'
                                  ' must be provided when creating a new rule group',
                                  rule_type=rule_type, keys=self._resource_updates.keys(),
                                  types=self.RULE_TYPES)

        return super(NetworkFirewallRuleManager, self)._flush_create()

    def _do_update_resource(self):
        filtered_metadata_updates = self._filter_immutable_metadata_attributes(self._metadata_updates)
        filtered_resource_updates = self._resource_updates

        if not filtered_resource_updates and not filtered_metadata_updates:
            return False

        metadata, resource = self._merge_changes()

        params = metadata
        params.update(self._get_id_params())
        params['RuleGroup'] = resource

        if not self.module.check_mode:
            response = self._update_rule_group(**params)

        return True

    def _flush_update(self):
        changed = False
        changed |= self._flush_tagging()
        changed |= super(NetworkFirewallRuleManager, self)._flush_update()
        return changed

    def _get_rule_group(self, **params):
        result = self._describe_rule_group(**params)
        if not result:
            return None

        rule_group = result.get('RuleGroup', None)
        metadata = result.get('RuleGroupMetadata', None)
        self._preupdate_resource = deepcopy(rule_group)
        self._preupdate_metadata = deepcopy(metadata)
        return dict(RuleGroup=rule_group, RuleGroupMetadata=metadata)

    def get_resource(self):
        id_params = self._get_id_params()
        return self.get_rule_group()

    def _do_creation_wait(self, **params):
        all_params = self._get_id_params()
        all_params.update(params)
        return self._wait_rule_group_active(**all_params)

    def _do_deletion_wait(self, **params):
        all_params = self._get_id_params()
        all_params.update(params)
        return self._wait_rule_group_deleted(**all_params)
