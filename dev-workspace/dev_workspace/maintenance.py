import aws_cdk.aws_ssm as ssm
from constructs import Construct
from dev_workspace.roles import SimpleRole


class SimpleMaintenance:
    def __init__(self, scope: Construct, config: dict):
        name = config["Name"]
        self.window = ssm.CfnMaintenanceWindow(
            scope,
            f"{name}-Window",
            name=f"DevWorkspace-{name}-Window",
            allow_unassociated_targets=False,
            cutoff=1,
            duration=3,
            schedule=config["Schedule"],
            schedule_timezone="UTC",
        )

        self.targets = [
            ssm.CfnMaintenanceWindowTarget(
                scope,
                f"{name}-Target-{idx}",
                name=f"DevWorkspace-{name}-Target-{idx}",
                window_id=self.window.ref,
                resource_type="INSTANCE",
                targets=[
                    ssm.CfnMaintenanceWindowTarget.TargetsProperty(key=key, values=values)
                    for key, values in target_config.items()
                ],
            )
            for idx, target_config in enumerate(config["Targets"])
        ]

        maintenance_role = SimpleRole(
            scope,
            {
                "Name": f"SSM.Automation.{name}.{scope.region}",
                "AssumedBy": "ssm.amazonaws.com",
                "PolicyStatements": [
                    # Statements from the standard service linked role policy:
                    # arn:aws:iam::aws:policy/aws-service-role/AmazonSSMServiceRolePolicy
                    {
                        "Actions": [
                            "ssm:CancelCommand",
                            "ssm:GetCommandInvocation",
                            "ssm:ListCommandInvocations",
                            "ssm:ListCommands",
                            "ssm:SendCommand",
                            "ssm:GetAutomationExecution",
                            "ssm:GetParameters",
                            "ssm:StartAutomationExecution",
                            "ssm:ListTagsForResource",
                            "ssm:GetCalendarState",
                        ],
                        "Resources": ["*"],
                    },
                    {
                        "Actions": ["ssm:UpdateServiceSetting", "ssm:GetServiceSetting"],
                        "Resources": [
                            "arn:aws:ssm:*:*:servicesetting/ssm/opsitem/*",
                            "arn:aws:ssm:*:*:servicesetting/ssm/opsdata/*",
                        ],
                    },
                    {
                        "Actions": [
                            "ec2:DescribeInstanceAttribute",
                            "ec2:DescribeInstanceStatus",
                            "ec2:DescribeInstances",
                        ],
                        "Resources": ["*"],
                    },
                    {
                        "Actions": ["lambda:InvokeFunction"],
                        "Resources": ["arn:aws:lambda:*:*:function:SSM*", "arn:aws:lambda:*:*:function:*:SSM*"],
                    },
                    {
                        "Actions": ["states:DescribeExecution", "states:StartExecution"],
                        "Resources": ["arn:aws:states:*:*:stateMachine:SSM*", "arn:aws:states:*:*:execution:SSM*"],
                    },
                    {
                        "Actions": [
                            "resource-groups:ListGroups",
                            "resource-groups:ListGroupResources",
                            "resource-groups:GetGroupQuery",
                        ],
                        "Resources": ["*"],
                    },
                    {
                        "Actions": ["cloudformation:DescribeStacks", "cloudformation:ListStackResources"],
                        "Resources": ["*"],
                    },
                    {"Actions": ["tag:GetResources"], "Resources": ["*"]},
                    {"Actions": ["config:SelectResourceConfig"], "Resources": ["*"]},
                    {
                        "Actions": [
                            "compute-optimizer:GetEC2InstanceRecommendations",
                            "compute-optimizer:GetEnrollmentStatus",
                        ],
                        "Resources": ["*"],
                    },
                    {
                        "Actions": [
                            "support:DescribeTrustedAdvisorChecks",
                            "support:DescribeTrustedAdvisorCheckSummaries",
                            "support:DescribeTrustedAdvisorCheckResult",
                            "support:DescribeCases",
                        ],
                        "Resources": ["*"],
                    },
                    {
                        "Actions": [
                            "config:DescribeComplianceByConfigRule",
                            "config:DescribeComplianceByResource",
                            "config:DescribeRemediationConfigurations",
                            "config:DescribeConfigurationRecorders",
                        ],
                        "Resources": ["*"],
                    },
                    {
                        "Actions": ["iam:PassRole"],
                        "Resources": ["*"],
                        "Conditions": {"StringEquals": {"iam:PassedToService": ["ssm.amazonaws.com"]}},
                    },
                    {"Actions": ["organizations:DescribeOrganization"], "Resources": ["*"]},
                    {"Actions": ["cloudformation:ListStackSets"], "Resources": ["*"]},
                    {
                        "Actions": [
                            "cloudformation:ListStackInstances",
                            "cloudformation:DescribeStackSetOperation",
                            "cloudformation:DeleteStackSet",
                        ],
                        "Resources": ["arn:aws:cloudformation:*:*:stackset/AWS-QuickSetup-SSM*:*"],
                    },
                    {
                        "Actions": ["cloudformation:DeleteStackInstances"],
                        "Resources": [
                            "arn:aws:cloudformation:*:*:stackset/AWS-QuickSetup-SSM*:*",
                            "arn:aws:cloudformation:*:*:stackset-target/AWS-QuickSetup-SSM*:*",
                            "arn:aws:cloudformation:*:*:type/resource/*",
                        ],
                    },
                    {
                        "Actions": ["events:PutRule", "events:PutTargets"],
                        "Resources": ["*"],
                        "Conditions": {"StringEquals": {"events:ManagedBy": "ssm.amazonaws.com"}},
                    },
                    {
                        "Actions": ["events:RemoveTargets", "events:DeleteRule"],
                        "Resources": ["arn:aws:events:*:*:rule/SSMExplorerManagedRule"],
                    },
                    {"Actions": ["events:DescribeRule"], "Resources": ["*"]},
                    {"Actions": ["securityhub:DescribeHub"], "Resources": ["*"]},
                    # Additional Statements
                    {"Actions": ["cloudformation:CreateStack"], "Resources": ["*"]},
                ],
            },
        )

        self.tasks = [
            ssm.CfnMaintenanceWindowTask(
                scope,
                f"{name}-Task-{idx}",
                name=f"DevWorkspace-{name}-Task-{idx}",
                window_id=self.window.ref,
                service_role_arn=maintenance_role.role_arn,
                targets=[
                    ssm.CfnMaintenanceWindowTask.TargetProperty(
                        key="WindowTargetIds", values=[target.ref for target in self.targets]
                    )
                ],
                priority=idx,
                task_type="AUTOMATION",
                task_arn=task["Name"],
                task_invocation_parameters=ssm.CfnMaintenanceWindowTask.TaskInvocationParametersProperty(
                    maintenance_window_automation_parameters=ssm.CfnMaintenanceWindowTask.MaintenanceWindowAutomationParametersProperty(
                        parameters=task["Parameters"]
                    )
                )
                if len(task.get("Parameters", {})) > 0
                else None,
                cutoff_behavior="CONTINUE_TASK",
                max_concurrency="10",
                max_errors="0",
            )
            for idx, task in enumerate(config["Tasks"])
        ]
