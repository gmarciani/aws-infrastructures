import json
import logging
import os
import re
from datetime import datetime, timedelta

import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)


REGION = os.environ["REGION"]
ACCOUNT = os.environ["ACCOUNT"]
CONFIG = json.loads(os.environ["CONFIG"])


def parse_date(s):
    return datetime.strptime(s, "%Y-%m-%dT%H:%M:%S.%f%z")


def select_resources_to_delete(resources, filters):
    resources_to_delete = []
    for resource in resources:
        mark_for_deletion = True
        for key, value in filters.items():
            if key in ["CreationDate", "LastAccessedDate", "StartTime"]:
                resource_value = parse_date(resource[key]) if type(resource[key]) is str else resource[key]
                if not resource_value < (datetime.now(resource_value.tzinfo) - timedelta(days=int(value))):
                    mark_for_deletion = False
                    break
            else:
                if not re.match(re.compile(value), resource[key]):
                    mark_for_deletion = False
                    break
        if mark_for_deletion:
            resources_to_delete.append(resource)
    return resources_to_delete


def cleanup_security_groups(filters):
    response = dict(Successes=[], Failures=[])
    logger.info(f"Security Groups cleanup started: filters={filters}")

    ec2_client = boto3.client("ec2", region_name=REGION)

    resources = ec2_client.describe_security_groups(MaxResults=100)["SecurityGroups"]

    resources_to_delete = select_resources_to_delete(resources, filters)

    logger.info(f"Found {len(resources_to_delete)} Security Groups to delete out of {len(resources)}")

    for resource in resources_to_delete:
        resource_id = resource["GroupId"]
        try:
            ec2_client.delete_security_group(GroupId=resource_id)
            response["Successes"].append(resource_id)
        except Exception as e:
            logger.error(f"Cannot delete Security Group {resource_id}: {e}")
            response["Failures"].append(resource_id)

    logger.info(f"Security Groups cleanup complete: {response}")

    return response


def cleanup_images(filters):
    response = dict(Successes=[], Failures=[])
    logger.info(f"Images cleanup started: filters={filters}")

    ec2_client = boto3.client("ec2", region_name=REGION)

    resources = ec2_client.describe_images(
        Owners=[ACCOUNT], IncludeDeprecated=True, Filters=[{"Name": "is-public", "Values": ["false"]}]
    )["Images"]

    resources_to_delete = select_resources_to_delete(resources, filters)

    logger.info(f"Found {len(resources_to_delete)} Images to delete out of {len(resources)}")

    for resource in resources_to_delete:
        resource_id = resource["ImageId"]
        try:
            ec2_client.deregister_image(ImageId=resource_id)
            response["Successes"].append(resource_id)
        except Exception as e:
            logger.error(f"Cannot delete Image {resource_id}: {e}")
            response["Failures"].append(resource_id)

    logger.info(f"Images cleanup complete: {response}")

    return response


def cleanup_snapshots(filters):
    response = dict(Successes=[], Failures=[])
    logger.info(f"Snapshots cleanup started: filters={filters}")

    ec2_client = boto3.client("ec2", region_name=REGION)

    resources = ec2_client.describe_snapshots(OwnerIds=[ACCOUNT], MaxResults=1000)["Snapshots"]

    resources_to_delete = select_resources_to_delete(resources, filters)

    logger.info(f"Found {len(resources_to_delete)} Snapshots to delete out of {len(resources)}")

    for resource in resources_to_delete:
        resource_id = resource["SnapshotId"]
        try:
            ec2_client.delete_snapshot(SnapshotId=resource_id)
            response["Successes"].append(resource_id)
        except Exception as e:
            logger.error(f"Cannot delete Snapshot {resource_id}: {e}")
            response["Failures"].append(resource_id)

    logger.info(f"Snapshots cleanup complete: {response}")

    return response


def cleanup_secrets(filters):
    response = dict(Successes=[], Failures=[])
    logger.info(f"Secrets cleanup started: filters={filters}")

    sm_client = boto3.client("secretsmanager", region_name=REGION)

    resources = sm_client.list_secrets()["SecretList"]

    resources_to_delete = select_resources_to_delete(resources, filters)

    logger.info(f"Found {len(resources_to_delete)} Secrets to delete out of {len(resources)}")

    for resource in resources_to_delete:
        resource_id = resource["ARN"]
        try:
            sm_client.delete_secret(SecretId=resource_id)
            response["Successes"].append(resource_id)
        except Exception as e:
            logger.error(f"Cannot delete Secret {resource_id}: {e}")
            response["Failures"].append(resource_id)

    logger.info(f"Secrets cleanup complete: {response}")

    return response


CLEANUP_FUNCTIONS = {
    "SecurityGroup": cleanup_security_groups,
    "Image": cleanup_images,
    "Snapshot": cleanup_snapshots,
    "Secret": cleanup_secrets,
}


def main(event, lambda_context):
    logger.info(f"Input: event={event}")
    logger.info(f"Input: lambda_context={lambda_context}")
    logger.info(f"Input: REGION={REGION}")
    logger.info(f"Input: CONFIG={CONFIG}")

    response = dict(Successes={}, Failures={})

    for cleanup_config in CONFIG["Targets"]:
        resource_type = cleanup_config["Type"]
        filters = cleanup_config["Filters"]

        if resource_type not in CLEANUP_FUNCTIONS:
            logger.warning(f"[Cannot cleanup resource of type {resource_type}: cleanup function not found. Skipping.")
            continue

        try:
            cleanup_response = CLEANUP_FUNCTIONS[resource_type](filters)
            response["Successes"][resource_type] = list(cleanup_response["Successes"])
            response["Failures"][resource_type] = list(cleanup_response["Failures"])
        except Exception as e:
            logger.error(f" Cannot cleanup resources with type {resource_type}: {e}")

    return response


if __name__ == "__main__":
    main(event=None, lambda_context=None)
