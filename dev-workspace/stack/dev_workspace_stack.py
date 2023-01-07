from aws_cdk import Stack, Tags
from constructs import Construct
from stack.buckets import SimpleBucket
from stack.budgets import SimpleBudget
from stack.lambdas import CleanupLambda
from stack.maintenance import SimpleMaintenance
from stack.pipelines import CodeToBucketPipeline
from stack.repositories import SimpleRepository
from stack.roles import SimpleRole
from stack.secrets import SimpleSecret
from stack.security_groups import (AllVpcTrafficSecurityGroup, EfsSecurityGroup, EmptySecurityGroup, FsxSecurityGroup,
                                   RDPSecurityGroup, SSHSecurityGroup)
from stack.vpcs import SimpleVpc


class DevWorkspaceStack(Stack):
    def __init__(self, scope: Construct, construct_id: str, config: dict, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Region
        region = self.region

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
            bucket = SimpleBucket(self, name=config["Bucket"]["Name"])

            # Roles
            for role_config in config.get("Roles", []):
                SimpleRole(self, role_config)

            # Repositories
            repositories = {
                repository_name: SimpleRepository(self, name=repository_name)
                for repository_name in config["Repositories"]
            }

            # CodeToBucket
            CodeToBucketPipeline(
                self,
                name="DevWorkspace-CodeToBucket",
                repositories=repositories,
                bucket=bucket,
                config=config["CodeToBucket"],
            )

        # Resources to deploy in all regions
        # Networking
        vpc = SimpleVpc(
            self,
            cidr=config["Vpc"]["Cidr"],
            region_metadata=config["Regions"][region],
        )

        # Security Groups
        AllVpcTrafficSecurityGroup(self, vpc=vpc)
        EmptySecurityGroup(self, vpc=vpc)
        SSHSecurityGroup(self, vpc=vpc, prefix_list=config["PrefixLists"][self.region])
        RDPSecurityGroup(self, vpc=vpc, prefix_list=config["PrefixLists"][self.region])
        EfsSecurityGroup(self, vpc=vpc)
        FsxSecurityGroup(self, vpc=vpc)

        # Cleanup Function
        CleanupLambda(self, config=config["Cleanup"])

        # Maintenance
        for maintenance_config in config.get("Maintenance", []):
            if maintenance_config.get("Region", region) == region:
                SimpleMaintenance(self, config=maintenance_config)

        # Secrets
        for secret_config in config.get("Secrets", []):
            SimpleSecret(self, name=secret_config["Name"], value=secret_config["Value"])
