from aws_cdk import aws_ec2 as ec2
from constructs import Construct

SUBNET_TYPES = (ec2.SubnetType.PUBLIC, ec2.SubnetType.PRIVATE_ISOLATED)


class SimpleVpc(ec2.Vpc):
    def __init__(self, scope: Construct, name: str, cidr: str, azs: list, region_metadata: dict):
        super().__init__(
            scope=scope,
            id=f"VPC-{name}",
            vpc_name=name,
            cidr=cidr,
            enable_dns_hostnames=True,
            enable_dns_support=True,
            subnet_configuration=[
                ec2.SubnetConfiguration(
                    name=f"{type.name}-{region_metadata['AvailabilityZones'][az]}".lower(), subnet_type=type
                )
                for az in azs
                for type in SUBNET_TYPES
            ],
        )
