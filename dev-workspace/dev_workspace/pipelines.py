from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_codepipeline as codepipeline
from aws_cdk import aws_codepipeline_actions as codepipeline_actions
from constructs import Construct


class CodeToBucketPipeline(codepipeline.Pipeline):
    def __init__(self, scope: Construct, name: str, repositories: dict, config: dict):
        super().__init__(scope, name, pipeline_name=name)

        # Source
        source_stage = self.add_stage(stage_name="Source")
        source_output = codepipeline.Artifact("source_output")
        for repository_config in config:
            repository = repositories[repository_config["Repository"]]
            source_stage.add_action(
                codepipeline_actions.CodeCommitSourceAction(
                    action_name=repository.repository_name,
                    output=source_output,
                    repository=repository,
                    branch=repository_config["Branch"],
                    trigger=codepipeline_actions.CodeCommitTrigger.EVENTS,
                )
            )

        # Build
        build_stage = self.add_stage(stage_name="Build")
        build_output = codepipeline.Artifact("build_output")
        project = codebuild.PipelineProject(self, name)
        build_stage.add_action(
            codepipeline_actions.CodeBuildAction(
                action_name="CodeBuild",
                project=project,
                input=source_output,
                outputs=[build_output],  # optional
                execute_batch_build=True,  # optional, defaults to false
                combine_batch_build_artifacts=True,
            )
        )
