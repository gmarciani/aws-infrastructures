from aws_cdk import aws_codecommit as codecommit
from constructs import Construct


class SimpleRepository(codecommit.Repository):
    def __init__(self, scope: Construct, name: str):
        super().__init__(scope, name, repository_name=name)
