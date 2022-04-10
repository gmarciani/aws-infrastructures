from aws_cdk import aws_codepipeline as codepipeline
from aws_cdk import aws_codepipeline_actions as codepipeline_actions
from aws_cdk import aws_s3 as s3
from constructs import Construct


class CodeToBucketPipeline(codepipeline.Pipeline):
    def __init__(self, scope: Construct, name: str, repositories: dict, bucket: s3.IBucket, config: dict):
        super().__init__(scope, name, pipeline_name=name)

        # Stages
        source_stage = self.add_stage(stage_name="Source")
        deploy_stage = self.add_stage(stage_name="Deploy")

        for repository_config in config:
            repository = repositories[repository_config["Repository"]]
            repository_name = repository.repository_name

            # Source Stage
            source_output = codepipeline.Artifact(f"source-output-{repository_name}")
            source_stage.add_action(
                codepipeline_actions.CodeCommitSourceAction(
                    action_name=repository_name,
                    output=source_output,
                    repository=repository,
                    branch=repository_config["Branch"],
                    trigger=codepipeline_actions.CodeCommitTrigger.EVENTS,
                )
            )

            # Deploy Stage
            deploy_stage.add_action(
                codepipeline_actions.S3DeployAction(
                    action_name=repository_name,
                    bucket=bucket,
                    input=source_output,
                    extract=True,
                    object_key=repository_name,
                )
            )
