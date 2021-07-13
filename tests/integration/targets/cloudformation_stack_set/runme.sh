#!/usr/bin/env bash

set -eux
# Run full test suite
ansible-playbook -i ../../inventory -v playbooks/full_test.yml "$@"
