from aws_cdk import aws_secretsmanager as secretsmanager
from constructs import Construct


class SimpleSecret(secretsmanager.Secret):
    def __init__(self, scope: Construct, name: str, value: str):
        super().__init__(
            scope=scope,
            id=name,
            secret_name=name,
            secret_string_beta1=secretsmanager.SecretStringValueBeta1.from_unsafe_plaintext(value),
        )
