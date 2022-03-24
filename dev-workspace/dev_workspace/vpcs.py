from aws_cdk import aws_ec2 as ec2
from constructs import Construct


class SimpleVpc(ec2.Vpc):
    def __init__(self, scope: Construct, name: str, cidr: str):
        super().__init__(
            scope=scope,
            id=f"VPC-{name}",
            vpc_name=name,
            cidr=cidr,
            enable_dns_hostnames=True,
            enable_dns_support=True,
        )
