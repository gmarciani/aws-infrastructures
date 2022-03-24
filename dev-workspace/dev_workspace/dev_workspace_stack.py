from aws_cdk import Stack
from constructs import Construct
from dev_workspace.buckets import SimpleBucket
from dev_workspace.security_groups import RDPSecurityGroup, SSHSecurityGroup
from dev_workspace.vpcs import SimpleVpc


class DevWorkspaceStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, config: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Buckets
        SimpleBucket(self, name=config["BucketName"])

        # Networking
        vpc = SimpleVpc(self, name=config["Vpc"]["Name"], cidr=config["Vpc"]["Cidr"])
        SSHSecurityGroup(self, vpc=vpc, prefix_list=config["PrefixLists"][self.region])
        RDPSecurityGroup(self, vpc=vpc, prefix_list=config["PrefixLists"][self.region])
