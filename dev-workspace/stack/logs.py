from aws_cdk import (
    aws_logs as logs,
    RemovalPolicy,
)
from constructs import Construct

from common.constants import RESOURCE_NAME_PREFIX


class SimpleLogGroup(logs.LogGroup):
    def __init__(self, scope: Construct, name: str):
        super().__init__(
            scope,
            f"LogGroup-{name}",
            log_group_name=name,
            removal_policy=RemovalPolicy.RETAIN,
            retention=logs.RetentionDays.FIVE_YEARS,
        )
