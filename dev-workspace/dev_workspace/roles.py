from aws_cdk import aws_iam as iam
from constructs import Construct


class SimpleRole(iam.Role):
    def __init__(self, scope: Construct, config: dict):
        super().__init__(
            scope,
            config["Name"],
            role_name=config["Name"],
            assumed_by=iam.ServicePrincipal(config["AssumedBy"]),
            description=config.get("Description", ""),
        )

        for policy_arn in config.get("ManagedPolicies", []):
            super().add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(policy_arn.split("/")[1]))

        for policy_statement in config.get("PolicyStatements", []):
            self.add_to_policy(
                iam.PolicyStatement(actions=policy_statement["Actions"], resources=policy_statement["Resources"])
            )
