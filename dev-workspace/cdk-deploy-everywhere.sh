#!/usr/bin/env bash

# Usage: cdk-deploy-everywhere.sh [ACCOUNT_ID]

ACCOUNT_ID=$1
shift

[[ -z $ACCOUNT_ID ]] && echo "[ERROR] ACCOUNT_ID is required. Usage: cdk-deploy-everywhere.sh [ACCOUNT_ID]" && exit 1

CURRENT_PATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
CDK_DEPLOY_SCRIPT="$CURRENT_PATH/cdk-deploy-to.sh"
REGIONS=$(aws ec2 describe-regions --all-regions --filter Name=opt-in-status,Values=opt-in-not-required --query "Regions[].{Name:RegionName}" --output text)

for region in $REGIONS; do
    echo "Deploying to $ACCOUNT_ID in region $region"
    check_auth=$(aws sts get-caller-identity --region $region 2>&1)
    [[ $? -ne 0 ]] && echo "[WARNING] Skipping region $region: cannot authenticate with this region" && continue
    bash $CDK_DEPLOY_SCRIPT $ACCOUNT_ID $region "$@"
done