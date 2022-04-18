from aws_cdk import Stack, Tags
from constructs import Construct
from dev_workspace.buckets import SimpleBucket
from dev_workspace.budgets import SimpleBudget
from dev_workspace.lambdas import CleanupLambda
from dev_workspace.maintenance import SimpleMaintenance
from dev_workspace.pipelines import CodeToBucketPipeline
from dev_workspace.repositories import SimpleRepository
from dev_workspace.roles import SimpleRole
from dev_workspace.secrets import SimpleSecret
from dev_workspace.security_groups import RDPSecurityGroup, SSHSecurityGroup
from dev_workspace.vpcs import SimpleVpc


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
            bucket = SimpleBucket(self, name=config["BucketName"])

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
            region_metadata=config["RegionsMetadata"][region],
        )

        # Security
        SSHSecurityGroup(self, vpc=vpc, prefix_list=config["PrefixLists"][self.region])
        RDPSecurityGroup(self, vpc=vpc, prefix_list=config["PrefixLists"][self.region])

        # Cleanup Function
        CleanupLambda(self, config=config["Cleanup"])

        # Maintenance
        for maintenance_config in config.get("Maintenance", []):
            if maintenance_config.get("Region", region) == region:
                SimpleMaintenance(self, config=maintenance_config)

        # Secrets
        for secret_config in config.get("Secrets", []):
            if secret_config.get("Region", region) == region:
                SimpleSecret(self, name=secret_config["Name"], value=secret_config["Value"])
