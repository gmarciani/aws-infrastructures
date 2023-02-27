#!/usr/bin/env bash

# Usage: cdk-deploy-to.sh [ACCOUNT_ID] [REGION] (optional args..)
# Examples:
#     cdk-deploy-to.sh 123456789 eu-west-1
#     cdk-deploy-to.sh 123456789 cn-north-1 --profile my-cn-north-1-profile

if [[ $# -ge 2 ]]; then
    export CDK_DEPLOY_ACCOUNT=$1
    export CDK_DEPLOY_REGION=$2
    shift; shift

    CURR_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

    $CURR_DIR/cdk-bootstrap-to.sh $CDK_DEPLOY_ACCOUNT $CDK_DEPLOY_REGION $CDK_DEPLOY_PROFILE

    echo "[INFO] Checking key pair in region $CDK_DEPLOY_REGION"
    KEY_PAIR_CONFIG="$(python -c "from common.config import parse_config;c=parse_config('config');print(c['KeyPair']['Name'] + '=' + c['KeyPair']['Path'])")"
    KEY_PAIR_NAME="$(echo $KEY_PAIR_CONFIG | cut -d '=' -f 1)"
    KEY_PAIR_PATH="$(echo $KEY_PAIR_CONFIG | cut -d '=' -f 2)"
    KEY_PAIR_TAGS='ResourceType=key-pair,Tags=[{Key=Stack,Value=DevWorkspace}]'
    RESPONSE_DESCRIBE_KEY_PAIRS=$(aws ec2 describe-key-pairs --region $CDK_DEPLOY_REGION --key-name $KEY_PAIR_NAME 2>&1)
    DESCRIBE_KEY_PAIR_CODE=$?
    if [[ $DESCRIBE_KEY_PAIR_CODE == "0" ]]; then
        echo "[INFO] Key pair already exists in region $CDK_DEPLOY_REGION: $KEY_PAIR_NAME"
    elif [[ $DESCRIBE_KEY_PAIR_CODE == "254" ]]; then
        echo "[INFO] Importing key pair in region $CDK_DEPLOY_REGION: $KEY_PAIR_NAME with public key $KEY_PAIR_PATH"
        aws ec2 import-key-pair --region $CDK_DEPLOY_REGION --key-name $KEY_PAIR_NAME --public-key-material "fileb://$KEY_PAIR_PATH" --tag-specifications $KEY_PAIR_TAGS
    fi

    echo "[INFO] Deploying CDK for account $CDK_DEPLOY_ACCOUNT in region $CDK_DEPLOY_REGION"
    npx cdk deploy "$@"

#    echo "[INFO] Removing CDK bootstrap resources for account $CDK_DEPLOY_ACCOUNT in region $CDK_DEPLOY_REGION"
#    aws cloudformation delete-stack --region $CDK_DEPLOY_REGION --stack-name CDKToolkit

    exit $?
else
    echo 1>&2 "Provide account and region as first two args."
    echo 1>&2 "Additional args are passed through to cdk deploy."
    exit 1
fi