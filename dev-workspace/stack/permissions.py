from aws_cdk import aws_iam as iam, aws_s3 as s3
from constructs import Construct


def get_policy_document_to_pass_role(account: str) -> iam.PolicyDocument:
    return iam.PolicyDocument(
        statements=[iam.PolicyStatement(actions=["iam:PassRole"], resources=[f"arn:*:iam::{account}:role/*"])]
    )


def get_policy_document_to_enforce_imdsv2() -> iam.PolicyDocument:
    return iam.PolicyDocument(
        statements=[
            iam.PolicyStatement(
                effect=iam.Effect.DENY,
                actions=["ec2:RunInstances"],
                resources=["arn:*:ec2:*:*:instance/*"],
                conditions={"StringNotEquals": {"ec2:MetadataHttpTokens": "required"}},
            )
        ]
    )


def get_policy_document_to_write_ssm_parameters(region: str, account: str) -> iam.PolicyDocument:
    return iam.PolicyDocument(
        statements=[
            iam.PolicyStatement(actions=["ssm:PutParameter"], resources=[f"arn:*:ssm:{region}:{account}:parameter/*"])
        ]
    )


def get_policy_document_to_write_bucket(bucket: s3.IBucket) -> iam.PolicyDocument:
    return iam.PolicyDocument(
        statements=[
            iam.PolicyStatement(
                actions=["s3:GetObject", "s3:PutObject"], resources=[bucket.bucket_arn, f"{bucket.bucket_arn}/*"]
            )
        ]
    )


def get_policy_document_to_manage_key_pairs(region: str, account: str) -> iam.PolicyDocument:
    return iam.PolicyDocument(
        statements=[
            iam.PolicyStatement(
                actions=["ec2:CreateKeyPair", "ec2:DeleteKeyPair", "ec2:CreateTags"],
                resources=[f"arn:*:ec2:{region}:{account}:key-pair/*"],
            )
        ]
    )


def add_admin_role_for_ec2(scope: Construct) -> iam.Role:
    return iam.Role(
        scope,
        "AdminRoleForEc2",
        role_name=f"pcluster-devinfra-{scope.region}-admin-for-ec2",
        assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
        description="This is the role that allows admin actions to EC2 instances.",
        managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess")],
    )


def add_admin_role_for_lambda(scope: Construct) -> iam.Role:
    return iam.Role(
        scope,
        "AdminRoleForLambda",
        role_name=f"pcluster-devinfra-{scope.region}-admin-for-lambda",
        assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
        description="This is the role that allows admin actions to EC2 instances.",
        managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess")],
    )
