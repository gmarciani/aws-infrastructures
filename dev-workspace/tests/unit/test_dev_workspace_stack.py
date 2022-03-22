import aws_cdk as core
import aws_cdk.assertions as assertions
from dev_workspace.dev_workspace_stack import DevWorkspaceStack


# example tests. To run these tests, uncomment this file along with the example
# resource in dev_workspace/dev_workspace_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = DevWorkspaceStack(app, "dev-workspace")
    template = assertions.Template.from_stack(stack)


#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
