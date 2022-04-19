import aws_cdk.aws_ssm as ssm
from constructs import Construct


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

        self.tasks = [
            ssm.CfnMaintenanceWindowTask(
                scope,
                f"{name}-Task-{idx}",
                name=f"DevWorkspace-{name}-Task-{idx}",
                window_id=self.window.ref,
                targets=[
                    ssm.CfnMaintenanceWindowTask.TargetProperty(
                        key="WindowTargetIds", values=[target.ref for target in self.targets]
                    )
                ],
                priority=idx,
                task_type=task.get("Type", "RUN_COMMAND"),
                task_arn=task["Name"],
                task_invocation_parameters=self._get_task_parmeters(task),
                cutoff_behavior="CONTINUE_TASK",
                max_concurrency="10",
                max_errors="0",
            )
            for idx, task in enumerate(config["Tasks"])
        ]

    def _get_task_parmeters(self, task):
        type = task.get("Type", "RUN_COMMAND")
        parameters = task.get("Parameters", [])

        if len(parameters) == 0:
            return None

        if type == "AUTOMATION":
            return ssm.CfnMaintenanceWindowTask.TaskInvocationParametersProperty(
                maintenance_window_automation_parameters=ssm.CfnMaintenanceWindowTask.MaintenanceWindowAutomationParametersProperty(
                    parameters=parameters
                )
            )
        elif type == "RUN_COMMAND":
            return ssm.CfnMaintenanceWindowTask.TaskInvocationParametersProperty(
                maintenance_window_run_command_parameters=ssm.CfnMaintenanceWindowTask.MaintenanceWindowRunCommandParametersProperty(
                    parameters=parameters
                )
            )
        else:
            raise RuntimeError(f"Unsupported task type: {type}")
