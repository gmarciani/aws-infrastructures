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


def build_deletion_filter(filters):
    filter_functions = []
    for key, value in filters.items():
        if key == "CreationDate":
            filter_fn = lambda resource: parse_date(resource[key]) < (
                datetime.now(parse_date(resource[key]).tzinfo - timedelta(days=value))
            )
        else:
            value_pattern = re.compile(value)
            filter_fn = lambda resource: re.match(value_pattern, resource[key])
        filter_functions.append(filter_fn)
    deletion_filter = lambda resource: all(filter_fn(resource) for filter_fn in filter_functions)
    return deletion_filter


def cleanup_security_groups(filters):
    response = dict(Successes=[], Failures=[])
    logger.info(f"Security Groups cleanup started: filters={filters}")

    ec2_client = boto3.client("ec2", region_name=REGION)

    resources = ec2_client.describe_security_groups(MaxResults=100)["SecurityGroups"]

    deletion_filter = build_deletion_filter(filters)

    resources_to_delete = list(filter(deletion_filter, resources))

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

    deletion_filter = build_deletion_filter(filters)

    resources_to_delete = list(filter(deletion_filter, resources))

    logger.info(f"Found {len(resources_to_delete)} Images to delete out of {len(resources)}")

    for resource in resources_to_delete:
        resource_id = resource["ImageId"]
        try:
            # ec2_client.deregister_image(ImageId=resource_id)
            response["Successes"].append(resource_id)
        except Exception as e:
            logger.error(f"Cannot delete Image {resource_id}: {e}")
            response["Failures"].append(resource_id)

    logger.info(f"Images cleanup complete: {response}")

    return response


def cleanup_snapshots(filters):
    response = dict(Successes=[], Failures=[])
    logger.info(f"Snapshots cleanup started: filters={filters}")
    resources = []
    resources_to_delete = []
    logger.info(f"Found {len(resources_to_delete)} Snapshots to delete out of {len(resources)}")
    logger.info(f"Snapshots cleanup complete: {response}")
    return response


CLEANUP_FUNCTIONS = {
    "SecurityGroup": cleanup_security_groups,
    "Image": cleanup_images,
    "Snapshot": cleanup_snapshots,
}


def main(event, lambda_context):
    logger.info(f"Input: event={event}")
    logger.info(f"Input: lambda_context={lambda_context}")
    logger.info(f"Input: REGION={REGION}")
    logger.info(f"Input: CONFIG={CONFIG}")

    response = dict(Successes={}, Failures={})

    for cleanup_config in CONFIG:
        resource_type = cleanup_config["Type"]
        filters = cleanup_config["Filters"]

        if resource_type not in CLEANUP_FUNCTIONS:
            logger.warn(f"[Cannot cleanup resource of type {resource_type}: cleanup function not found. Skipping.")
            continue

        try:
            cleanup_response = CLEANUP_FUNCTIONS[resource_type](filters)
            response["Successes"][resource_type] = list(cleanup_response["Successes"])
            response["Failures"][resource_type] = list(cleanup_response["Failures"])
        except Exception as e:
            logger.error(f" Cannot cleanup resources with type {resource_type}: {e}")

    return response


if __name__ == "__main__":
    main(event=None, context=None)
