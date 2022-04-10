from aws_cdk import aws_ec2 as ec2
from constructs import Construct


class SimpleSecurityGroup(ec2.SecurityGroup):
    def __init__(self, scope: Construct, name: str, description: str, vpc: str):
        super().__init__(
            scope=scope,
            id=f"SecurityGroup-{name}",
            security_group_name=name,
            description=description,
            vpc=vpc,
            allow_all_outbound=True,
        )


class SSHSecurityGroup(SimpleSecurityGroup):
    def __init__(self, scope: Construct, vpc: str, prefix_list: str):
        super().__init__(scope, name="SSH-Secure", description="Allow restricted SSH access", vpc=vpc)
        self.add_ingress_rule(
            peer=ec2.Peer.prefix_list(prefix_list),
            connection=ec2.Port.tcp(22),
            description=f"Allow inbound SSH connections from prefix list {prefix_list}",
        )


class RDPSecurityGroup(SimpleSecurityGroup):
    def __init__(self, scope: Construct, vpc: str, prefix_list: str):
        super().__init__(scope, name="RDP-Secure", description="Allow restricted RDP access", vpc=vpc)
        self.add_ingress_rule(
            peer=ec2.Peer.prefix_list(prefix_list),
            connection=ec2.Port.tcp(3389),
            description=f"Allow inbound RDP connections from prefix list {prefix_list}",
        )
