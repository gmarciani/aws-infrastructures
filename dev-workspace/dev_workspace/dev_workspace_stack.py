from aws_cdk import Stack, Tags
from constructs import Construct
from dev_workspace.buckets import SimpleBucket
from dev_workspace.budgets import SimpleBudget
from dev_workspace.pipelines import CodeToBucketPipeline
from dev_workspace.repositories import SimpleRepository
from dev_workspace.roles import SimpleRole
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

        # Resources to deploy only to the main region
        if region == config["MainRegion"]:
            # Budgets
            SimpleBudget(
                self,
                amount=config["Budget"]["Amount"],
                threshold=config["Budget"]["Threshold"],
                email=config["Budget"]["Email"],
            )

            # Buckets
            SimpleBucket(self, name=config["BucketName"])

            # Roles
            for role_config in config.get("Roles", []):
                SimpleRole(self, role_config)

            # Repositories
            repositories = {
                repository_name: SimpleRepository(self, name=repository_name)
                for repository_name in config["Repositories"]
            }

            # CodeToBucket
            pipeline = CodeToBucketPipeline(
                self, name="DevWorkspace-CodeToBucket", repositories=repositories, config=config["CodeToBucket"]
            )

        # Resources to deploy in all regions
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
