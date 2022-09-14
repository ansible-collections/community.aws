# Community AWS Collection

The Ansible Community AWS collection includes a variety of Ansible content to help automate the management of AWS instances. This collection is maintained by the Ansible community.

AWS related modules and plugins supported by the Ansible Cloud team are in the [amazon.aws](https://github.com/ansible-collections/amazon.aws) collection.

<!--start requires_ansible-->
## Ansible version compatibility

This collection has been tested against following Ansible versions: **>=2.9.10**.

Plugins and modules within a collection may be tested with only specific Ansible versions.
A collection may contain metadata that identifies these versions.
PEP440 is the schema used to describe the versions of Ansible.
<!--end requires_ansible-->

## Python version compatibility

As the AWS SDK for Python (Boto3 and Botocore) has [ceased supporting Python 2.7](https://aws.amazon.com/blogs/developer/announcing-end-of-support-for-python-2-7-in-aws-sdk-for-python-and-aws-cli-v1/), this collection requires Python 3.6 or greater.

Starting with the 2.0.0 releases of amazon.aws and community.aws, it is generally the collection's policy to support the versions of `botocore` and `boto3` that were released 12 months prior to the most recent major collection release, following semantic versioning (for example, 2.0.0, 3.0.0).

Version 3.0.0 of this collection supports `boto3 >= 1.16.0` and `botocore >= 1.19.0`

## Included content
<!--start collection content-->
See the complete list of collection content in the [Plugin Index](https://ansible-collections.github.io/community.aws/branch/stable-3/collections/community/aws/index.html#plugin-index).

<!--end collection content-->

## Installing this collection

You can install the AWS collection with the Ansible Galaxy CLI:

    ansible-galaxy collection install community.aws

You can also include it in a `requirements.yml` file and install it with `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: community.aws

```

A specific version of the collection can be installed by using the `version` keyword in the `requirements.yml` file:

```yaml
---
collections:
  - name: community.aws
    version: 0.1.1
```

You can either call modules by their Fully Qualified Collection Namespace (FQCN), such as `community.aws.ec2_instance`, or you can call modules by their short name if you list the `community.aws` collection in the playbook's `collections` keyword:

```yaml
---
  - name: Create a DB instance using the default AWS KMS encryption key
    community.aws.rds_instance:
      id: test-encrypted-db
      state: present
      engine: mariadb
      storage_encrypted: True
      db_instance_class: db.t2.medium
      username: "{{ username }}"
      password: "{{ password }}"
      allocated_storage: "{{ allocated_storage }}"

```


### See Also:

* [Amazon Web Services Guide](https://docs.ansible.com/ansible/latest/scenario_guides/guide_aws.html)
* [Ansible Using collections](https://docs.ansible.com/ansible/latest/user_guide/collections_using.html) for more details.

## Contributing to this collection

We welcome community contributions to this collection. If you find problems, please open an issue or create a PR against the [Community AWS collection repository](https://github.com/ansible-collections/community.aws).

You can also join us on:

- Libera.Chat IRC - the ``#ansible-aws`` [irc.libera.chat](https://libera.chat/) channel

### More information about contributing

- [Ansible Community Guide](https://docs.ansible.com/ansible/latest/community/index.html) - Details on contributing to Ansible
- [Contributing to Collections](https://docs.ansible.com/ansible/devel/dev_guide/developing_collections.html#contributing-to-collections) - How to check out collection git repositories correctly
- [Guidelines for Ansible Amazon AWS module development](https://docs.ansible.com/ansible/latest/dev_guide/platforms/aws_guidelines.html)
- [Getting Started With AWS Ansible Module Development and Community Contribution](https://www.ansible.com/blog/getting-started-with-aws-ansible-module-development)

## Release notes
<!--Add a link to a changelog.rst file or an external docsite to cover this information. -->

## Roadmap

<!-- Optional. Include the roadmap for this collection, and the proposed release/versioning strategy so users can anticipate the upgrade/update cycle. -->

## More information

- [Ansible Collection overview](https://github.com/ansible-collections/overview)
- [Ansible User guide](https://docs.ansible.com/ansible/latest/user_guide/index.html)
- [Ansible Developer guide](https://docs.ansible.com/ansible/latest/dev_guide/index.html)
- [Ansible Collection Developer Guide](https://docs.ansible.com/ansible/devel/dev_guide/developing_collections.html)
- [Ansible Community code of conduct](https://docs.ansible.com/ansible/latest/community/code_of_conduct.html)

## Licensing

GNU General Public License v3.0 or later.

See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.
