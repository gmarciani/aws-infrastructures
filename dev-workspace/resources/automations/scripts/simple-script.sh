#!/bin/bash
set -e

# Usage simple-script.sh \
#   --ssm-parameter-name /ssm-automations/simple-automation/b5742d58-8aa1-423c-a48a-f036178f5b54 \
#   --debug

source ./common.sh

CURRENT_DIR="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

helper() {
  _cmd=$(basename "$0")
  echo "Usage"
  echo "  $_cmd "
  echo "      Executes a simple automation based on the use of an EC2 instance."
  echo ""
  echo "      --ssm-parameter-name [NAME]"
  echo "          The name of the SSM Parameter where information about the output will be stored."
  echo "          Example: /ssm-automations/simple-automation/b5742d58-8aa1-423c-a48a-f036178f5b54"
  echo ""
  echo "      --debug"
  echo "          Enables the debug mode."
  echo ""
  echo ""
  echo "Examples"
  echo "  $_cmd --ssm-parameter-name /ssm-automations/simple-automation/b5742d58-8aa1-423c-a48a-f036178f5b54 \
                --debug"
  echo ""
}

DEBUG="false"

while [ $# -gt 0 ] ; do
  case "$1" in
    --ssm-parameter-name)
      SSM_PARAMETER_NAME="$2"
      shift
    ;;
    --debug)
      DEBUG="true"
    ;;
    --help)
      helper
      exit 0
    ;;
    *)
      fail "[ERROR] Unrecognized option '$1'"
    ;;
  esac
  shift
done

[[ -z "${SSM_PARAMETER_NAME}" ]] && fail "Parameter SSM_PARAMETER_NAME cannot be empty"
[[ "${DEBUG}" == "true"  ]] && info "Configuring debug mode" && set -x

info "Installing OS packages"
sudo yum install -y jq

info "Executing the core actions"
sleep 1

info "Determining output values"
OUTPUT_1="OutputValue"

SSM_PARAMETER_VALUE=$(jq --null-input \
    --arg Output1 "$OUTPUT_1" \
    '{
      "Output1": $Output1
    }'
  )
  info "Storing results into SSM Parameter $SSM_PARAMETER_NAME: $SSM_PARAMETER_VALUE"
  aws ssm put-parameter \
    --name "$SSM_PARAMETER_NAME" \
    --value "$SSM_PARAMETER_VALUE" \
    --type String
