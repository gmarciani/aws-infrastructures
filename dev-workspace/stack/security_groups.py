from aws_cdk import aws_ec2 as ec2
from constructs import Construct


class SimpleSecurityGroup(ec2.SecurityGroup):
    def __init__(self, scope: Construct, name: str, description: str, vpc: ec2.Vpc):
        super().__init__(
            scope=scope,
            id=f"SecurityGroup-{name}",
            security_group_name=name,
            description=description,
            vpc=vpc,
            allow_all_outbound=True,
        )


class AllVpcTrafficSecurityGroup(SimpleSecurityGroup):
    def __init__(self, scope: Construct, vpc: ec2.Vpc):
        super().__init__(scope, name="AllVpcTraffic", description="Allow all traffic within the VPC", vpc=vpc)
        self.add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.all_tcp(),
            description=f"Allow inbound traffic from the VPC {vpc.vpc_id}",
        )


class EmptySecurityGroup(SimpleSecurityGroup):
    def __init__(self, scope: Construct, vpc: ec2.Vpc):
        super().__init__(scope, name="Empty", description="Empty Security Group", vpc=vpc)


class SSHSecurityGroup(SimpleSecurityGroup):
    def __init__(self, scope: Construct, vpc: ec2.Vpc, prefix_list: str):
        super().__init__(scope, name="SSH-Secure", description="Allow restricted SSH access", vpc=vpc)
        self.add_ingress_rule(
            peer=ec2.Peer.prefix_list(prefix_list),
            connection=ec2.Port.tcp(22),
            description=f"Allow inbound SSH traffic from prefix list {prefix_list}",
        )


class RDPSecurityGroup(SimpleSecurityGroup):
    def __init__(self, scope: Construct, vpc: ec2.Vpc, prefix_list: str):
        super().__init__(scope, name="RDP-Secure", description="Allow restricted RDP access", vpc=vpc)
        self.add_ingress_rule(
            peer=ec2.Peer.prefix_list(prefix_list),
            connection=ec2.Port.tcp(3389),
            description=f"Allow inbound RDP traffic from prefix list {prefix_list}",
        )


class DcvSecurityGroup(SimpleSecurityGroup):
    def __init__(self, scope: Construct, vpc: ec2.Vpc, prefix_list: str):
        super().__init__(scope, name="DCV-Secure", description="Allow restricted DCV access", vpc=vpc)
        self.add_ingress_rule(
            peer=ec2.Peer.prefix_list(prefix_list),
            connection=ec2.Port.tcp(8443),
            description=f"Allow inbound RDP traffic from prefix list {prefix_list}",
        )


class EfsSecurityGroup(SimpleSecurityGroup):
    def __init__(self, scope: Construct, vpc: ec2.Vpc):
        super().__init__(scope, name="EFS-Secure", description="Allow EFS traffic within the VPC", vpc=vpc)
        self.add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(2049),
            description=f"Allow inbound EFS traffic from the VPC {vpc.vpc_id}",
        )


class FsxSecurityGroup(SimpleSecurityGroup):
    def __init__(self, scope: Construct, vpc: ec2.Vpc):
        super().__init__(scope, name="FSX-Secure", description="Allow FSx traffic within the VPC", vpc=vpc)
        self.add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(988),
            description=f"Allow inbound FSx traffic from the VPC {vpc.vpc_id}",
        )
        self.add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.tcp_range(start_port=1018, end_port=1023),
            description=f"Allow inbound FSx traffic from the VPC {vpc.vpc_id}",
        )


class FileCacheSecurityGroup(SimpleSecurityGroup):
    def __init__(self, scope: Construct, vpc: ec2.Vpc):
        super().__init__(scope, name="FileCache-Secure", description="Allow File Cache traffic within the VPC", vpc=vpc)
        self.add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.tcp(988),
            description=f"Allow inbound File Cache traffic from the VPC {vpc.vpc_id}",
        )
        self.add_ingress_rule(
            peer=ec2.Peer.ipv4(vpc.vpc_cidr_block),
            connection=ec2.Port.tcp_range(start_port=1018, end_port=1023),
            description=f"Allow inbound File Cache traffic from the VPC {vpc.vpc_id}",
        )