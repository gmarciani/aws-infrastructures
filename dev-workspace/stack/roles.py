from aws_cdk import aws_iam as iam
from common.iam_utils import parse_principal
from constructs import Construct


class SimpleRole(iam.Role):
    def __init__(self, scope: Construct, config: dict):
        super().__init__(
            scope,
            config["Name"],
            role_name=config["Name"],
            assumed_by=parse_principal(str(config.get("AssumedBy", ["ec2.amazonaws.com"])[0])),
            description=config.get("Description", ""),
        )

        for principal_str in config.get("AssumedBy", []):
            self.grant_assume_role(parse_principal(str(principal_str)))

        for policy_arn in config.get("ManagedPolicies", []):
            super().add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(policy_arn.split("/")[1]))

        for policy_statement in config.get("PolicyStatements", []):
            self.add_to_policy(
                iam.PolicyStatement(
                    actions=policy_statement.get("Actions", []),
                    resources=policy_statement.get("Resources", []),
                    conditions=policy_statement.get("Conditions", None),
                )
            )
