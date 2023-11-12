from aws_cdk import Aspects, Tag
from aws_cdk import aws_ec2 as ec2
from common.regions import get_az_name
from constructs import Construct

VPC_NAME = "DevWorkspaceVPC"
SUBNET_TYPES = (ec2.SubnetType.PUBLIC, ec2.SubnetType.PRIVATE_WITH_EGRESS)


class SimpleVpc(ec2.Vpc):
    def __init__(self, scope: Construct, cidr: str, region_metadata: dict):
        super().__init__(
            scope=scope,
            id=VPC_NAME,
            vpc_name=VPC_NAME,
            ip_addresses=ec2.IpAddresses.cidr(cidr),
            enable_dns_hostnames=True,
            enable_dns_support=True,
            max_azs=3,
            subnet_configuration=[
                ec2.SubnetConfiguration(name=f"{VPC_NAME}/{type}", subnet_type=type) for type in SUBNET_TYPES
            ],
        )

        Aspects.of(self).add(Tag("Name", VPC_NAME))
        for subnet in self.public_subnets:
            Aspects.of(subnet).add(
                Tag("Name", f"{VPC_NAME}/{get_az_name(subnet.availability_zone, region_metadata)}/Public")
            )
        for subnet in self.private_subnets:
            Aspects.of(subnet).add(
                Tag("Name", f"{VPC_NAME}/{get_az_name(subnet.availability_zone, region_metadata)}/Private")
            )
        for subnet in self.isolated_subnets:
            Aspects.of(subnet).add(
                Tag("Name", f"{VPC_NAME}/{get_az_name(subnet.availability_zone, region_metadata)}/Isolated")
            )
