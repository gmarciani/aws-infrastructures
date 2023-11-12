from aws_cdk import RemovalPolicy
from aws_cdk import aws_iam as iam
from aws_cdk import aws_s3 as s3
from common.iam_utils import parse_principal
from constructs import Construct


class SimpleBucket(s3.Bucket):
    def __init__(self, scope: Construct, config: dict):
        name = config["Name"]
        super().__init__(
            scope,
            f"Bucket-{name}",
            bucket_name=name,
            access_control=s3.BucketAccessControl.PRIVATE,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            enforce_ssl=True,
            object_ownership=s3.ObjectOwnership.BUCKET_OWNER_ENFORCED,
            public_read_access=False,
            removal_policy=RemovalPolicy.DESTROY,
            versioned=True,
        )

        for permission in config.get("Permissions", []):
            resource = f"{self.bucket_arn}/{permission['Path']}"
            statement = iam.PolicyStatement(
                effect=iam.Effect.ALLOW,
                actions=["s3:Get*", "s3:List*"],
                resources=[resource, f"{resource}/*"],
                principals=[parse_principal(principal_str) for principal_str in permission["Allowed"].split(",")],
            )
            self.add_to_resource_policy(statement)
