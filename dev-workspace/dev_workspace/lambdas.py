import json
import os

from aws_cdk import Duration
from aws_cdk import aws_events as events
from aws_cdk import aws_events_targets as targets
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from constructs import Construct


class CleanupLambda(_lambda.Function):
    def __init__(self, scope: Construct, config: dict):
        super().__init__(
            scope,
            "CleanupLambda",
            function_name="DevWorkspace-Cleanup",
            description="Function that periodically cleans up resources.",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="handler.main",
            code=_lambda.Code.from_asset(os.path.join(os.path.dirname(__file__), "resources/cleanup")),
            memory_size=512,
            timeout=Duration.seconds(900),
            environment={"REGION": scope.region, "ACCOUNT": scope.account, "CONFIG": json.dumps(config)},
        )

        # Scheduling Rule
        rule = events.Rule(
            scope,
            "CleanupLambdaSchedule",
            rule_name="CleanupLambdaSchedule",
            description="Scheduling for function CleanupLambda",
            enabled=True,
            schedule=events.Schedule.expression(config["Schedule"]),
        )

        rule.add_target(targets.LambdaFunction(self))

        if any(element["Type"] == "SecurityGroup" for element in config["Targets"]):
            self.add_to_role_policy(
                iam.PolicyStatement(
                    actions=[
                        "ec2:DescribeSecurityGroups",
                    ],
                    resources=["*"],
                )
            )
            self.add_to_role_policy(
                iam.PolicyStatement(
                    actions=[
                        "ec2:DeleteSecurityGroup",
                    ],
                    resources=[f"arn:aws:ec2:{scope.region}:{scope.account}:security-group/*"],
                )
            )

        if any(element["Type"] == "Image" for element in config["Targets"]):
            self.add_to_role_policy(
                iam.PolicyStatement(
                    actions=[
                        "ec2:DescribeImages",
                    ],
                    resources=["*"],
                )
            )
            self.add_to_role_policy(
                iam.PolicyStatement(
                    actions=[
                        "ec2:DeregisterImage",
                    ],
                    resources=[f"arn:aws:ec2:{scope.region}::image/*"],
                    conditions={"StringEquals": {"ec2:Owner": scope.account}, "Bool": {"ec2:Public": "False"}},
                )
            )

        if any(element["Type"] == "Snapshot" for element in config["Targets"]):
            self.add_to_role_policy(
                iam.PolicyStatement(
                    actions=["ec2:DescribeSnapshots"],
                    resources=["*"],
                )
            )
            self.add_to_role_policy(
                iam.PolicyStatement(
                    actions=[
                        "ec2:DeleteSnapshot",
                    ],
                    resources=[f"arn:aws:ec2:{scope.region}::snapshot/*"],
                    conditions={"StringEquals": {"ec2:Owner": scope.account}},
                )
            )
