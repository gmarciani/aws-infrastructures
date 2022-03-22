from aws_cdk import RemovalPolicy
from aws_cdk import aws_s3 as s3
from constructs import Construct


class SimpleBucket(s3.Bucket):
    def __init__(self, scope: Construct, name: str):
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
            removal_policy=RemovalPolicy.RETAIN,
            versioned=True,
        )
