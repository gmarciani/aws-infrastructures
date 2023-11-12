from aws_cdk import aws_iam as iam


def parse_principal(principal_str: str):
    return iam.AccountPrincipal(principal_str) if principal_str.isnumeric() else iam.ServicePrincipal(principal_str)
