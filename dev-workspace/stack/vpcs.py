from aws_cdk import Aspects, Tag
from aws_cdk import aws_ec2 as ec2
from common.regions import get_az_name
from constructs import Construct

SUBNET_TYPES = (ec2.SubnetType.PUBLIC, ec2.SubnetType.PRIVATE_WITH_EGRESS)


class SimpleVpc(ec2.Vpc):
    def __init__(self, scope: Construct, name: str, cidr: str, region_metadata: dict):
        super().__init__(
            scope=scope,
            id=name,
            vpc_name=name,
            ip_addresses=ec2.IpAddresses.cidr(cidr),
            enable_dns_hostnames=True,
            enable_dns_support=True,
            max_azs=3,
            subnet_configuration=[
                ec2.SubnetConfiguration(name=f"{name}/{subnet_type}", cidr_mask=24, subnet_type=subnet_type)
                for subnet_type in SUBNET_TYPES
            ],
        )

        Aspects.of(self).add(Tag("Name", name))
        for subnet in self.public_subnets:
            Aspects.of(subnet).add(
                Tag("Name", f"{name}/{get_az_name(subnet.availability_zone, region_metadata)}/Public")
            )
        for subnet in self.private_subnets:
            Aspects.of(subnet).add(
                Tag("Name", f"{name}/{get_az_name(subnet.availability_zone, region_metadata)}/Private")
            )
        for subnet in self.isolated_subnets:
            Aspects.of(subnet).add(
                Tag("Name", f"{name}/{get_az_name(subnet.availability_zone, region_metadata)}/Isolated")
            )
