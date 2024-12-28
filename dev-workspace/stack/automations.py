from aws_cdk import CfnTag
from aws_cdk import aws_iam as iam, aws_s3 as s3, aws_ec2 as ec2, aws_logs as logs, aws_ssm as ssm
from constructs import Construct
import yaml
import os

from common.constants import RESOURCE_NAME_PREFIX, RESOURCES_DIR
from common.file_utils import render_template
from stack.logs import SimpleLogGroup
from stack.permissions import (
    get_policy_document_to_pass_role,
    get_policy_document_to_enforce_imdsv2,
    get_policy_document_to_write_ssm_parameters,
)


class SimpleAutomation:
    def __init__(self, scope: Construct, vpc: ec2.Vpc, bucket: s3.IBucket):
        region = scope.region
        account = scope.account

        self.name = f"{RESOURCE_NAME_PREFIX}-SimpleAutomation"

        self.log_group = SimpleLogGroup(scope, name=f"{self.name}-{region}")

        self.automation_role = self._add_automation_role(scope)
        self.ec2_instance_profile = self._add_instance_profile(scope)

        document_content = yaml.safe_load(
            render_template(
                os.path.join(RESOURCES_DIR, "automations/simple-automation.yaml"),
                {
                    "SSM_ASSUME_ROLE": self.automation_role.role_arn,
                    "CLOUDWATCH_LOG_GROUP_NAME": self.log_group.log_group_name,
                    "SCRIPTS_FOLDER_S3_URI": f"s3://{bucket.bucket_name}/scripts",
                },
            )
        )

        self._add_ssm_document(
            scope,
            "SimpleAutomation",
            document_content,
            [vpc, self.log_group, self.ec2_instance_profile, self.automation_role],
        )

    def _add_automation_role(self, scope: Construct) -> iam.Role:
        region = scope.region
        account = scope.account

        return iam.Role(
            scope,
            "SsmAutomationRole",
            role_name=f"{RESOURCE_NAME_PREFIX}-{region}-automation-{self.name}",
            assumed_by=iam.ServicePrincipal("ssm.amazonaws.com"),
            description="This is the role assumed by SSM automations.",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("ReadOnlyAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonSSMFullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2FullAccess"),
                iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchLogsFullAccess"),
            ],
            inline_policies={
                "PassRole": get_policy_document_to_pass_role(account),
                "EnforceIMDSv2": get_policy_document_to_enforce_imdsv2(),
            },
        )

    def _add_instance_profile(
        self,
        scope: Construct,
    ) -> iam.CfnInstanceProfile:

        region = scope.region
        account = scope.account

        ec2_instance_role = iam.Role(
            scope,
            "Ec2InstanceRoleSimpleAutomation",
            role_name=f"{RESOURCE_NAME_PREFIX}-{region}-simple-automation",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            description="This is the role that allows the actions to execute the simple automation on EC2.",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name("AdministratorAccess"),
            ],
            inline_policies={
                "WriteSsmParameter": get_policy_document_to_write_ssm_parameters(region, account),
                "EnforceIMDSv2": get_policy_document_to_enforce_imdsv2(),
            },
        )

        ec2_instance_role.node.add_dependency(self.log_group)

        return iam.CfnInstanceProfile(
            scope,
            "Ec2InstanceProfileIntegTestExecutor",
            instance_profile_name=f"{ec2_instance_role.role_name}.profile",
            roles=[ec2_instance_role.role_name],
        )

    def _add_ssm_document(
        self, scope: Construct, name: str, content: str, dependencies: list = None
    ) -> ssm.CfnDocument:
        if dependencies is None:
            dependencies = []

        document = ssm.CfnDocument(
            scope,
            name,
            content=content,
            document_type="Automation",
            target_type="/AWS::EC2::Instance",
            version_name="1.0.0",
            update_method="Replace",
            tags=[
                CfnTag(key="Source", value="ParallelClusterDevInfrastructure"),
                CfnTag(key="Identifier", value=name),
            ],
        )

        for dependency in dependencies:
            document.node.add_dependency(dependency)

        return document
