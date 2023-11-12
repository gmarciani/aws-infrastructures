from aws_cdk import Fn
from aws_cdk import aws_iam as iam
from common.iam_utils import parse_principal
from constructs import Construct

DEFAULT_PRINCIPAL = "ec2.${AWS::URLSuffix}"


class SimpleRole(iam.Role):
    def __init__(self, scope: Construct, config: dict):
        role_name = config["Name"]
        super().__init__(
            scope,
            role_name,
            role_name=role_name,
            assumed_by=parse_principal(str(config.get("AssumedBy", [Fn.sub(DEFAULT_PRINCIPAL)])[0])),
            description=config.get("Description", ""),
        )

        for principal_str in config.get("AssumedBy", []):
            self.grant_assume_role(parse_principal(str(principal_str)))

        for policy_name in config.get("AwsManagedPolicies", []):
            super().add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name(policy_name))

        for policy_statement in config.get("PolicyStatements", []):
            self.add_to_policy(
                iam.PolicyStatement(
                    actions=policy_statement.get("Actions", []),
                    resources=[Fn.sub(resource_arn) for resource_arn in policy_statement.get("Resources", [])],
                    conditions=policy_statement.get("Conditions", None),
                )
            )

        profile_name = f"{self.role_name}.instance-profile"
        iam.CfnInstanceProfile(
            scope, f"Profile-{role_name}", instance_profile_name=profile_name, roles=[self.role_name], path="/"
        )
