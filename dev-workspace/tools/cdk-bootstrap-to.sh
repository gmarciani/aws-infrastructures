#!/usr/bin/env bash

# Usage: cdk-bootstrap-to.sh [ACCOUNT_ID] [REGION] (optional args..)
# Examples:
#     cdk-bootstrap-to.sh 123456789 eu-west-1
#     cdk-bootstrap-to.sh 123456789 cn-north-1 --profile my-cn-north-1-profile

if [[ $# -ge 2 ]]; then
    export CDK_DEPLOY_ACCOUNT=$1
    export CDK_DEPLOY_REGION=$2
    shift; shift

    echo "[INFO] Bootstrapping CDK for account $CDK_DEPLOY_ACCOUNT in region $CDK_DEPLOY_REGION"
    cdk bootstrap aws://$CDK_DEPLOY_ACCOUNT/$CDK_DEPLOY_REGION "$@"

#    echo "[INFO] Removing CDK bootstrap resources for account $CDK_DEPLOY_ACCOUNT in region $CDK_DEPLOY_REGION"
#    aws cloudformation delete-stack --region $CDK_DEPLOY_REGION --stack-name CDKToolkit

    exit $?
else
    echo 1>&2 "[ERROR] Missing required arguments. Usage: cdk-bootstrap-to.sh [ACCOUNT_ID] [REGION]" && exit 1
    exit 1
fi