from aws_cdk import Stack, Tags
from constructs import Construct
from dev_workspace.buckets import SimpleBucket
from dev_workspace.security_groups import RDPSecurityGroup, SSHSecurityGroup
from dev_workspace.vpcs import SimpleVpc


class DevWorkspaceStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, config: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Region
        region = self.region
        azs = self.availability_zones

        # Tags
        Tags.of(self).add("Stack", "DevWorkspaceStack")

        # Buckets
        SimpleBucket(self, name=config["BucketName"])

        # Networking
        vpc = SimpleVpc(
            self,
            name=config["Vpc"]["Name"],
            cidr=config["Vpc"]["Cidr"],
            azs=azs,
            region_metadata=config["RegionsMetadata"][region],
        )

        # Security
        SSHSecurityGroup(self, vpc=vpc, prefix_list=config["PrefixLists"][self.region])
        RDPSecurityGroup(self, vpc=vpc, prefix_list=config["PrefixLists"][self.region])
