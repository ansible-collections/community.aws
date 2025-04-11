#!/usr/bin/env bash

PLAYBOOK_DIR=$(pwd)
set -eux

CMD_ARGS=("$@")

# Destroy Environment
cleanup() {

    cd "${PLAYBOOK_DIR}"
    ansible-playbook -c local aws_ssm_integration_test_teardown.yml "${CMD_ARGS[@]}"

}

trap "cleanup" EXIT

# Setup Environment
ansible-playbook -c local aws_ssm_integration_test_setup.yml "$@"

# Export the AWS Keys
set +x
. ./aws-env-vars.sh
set -x

# Execute Integration tests
ansible-playbook ./test.yml -i "${PLAYBOOK_DIR}/ssm_inventory" "$@"
