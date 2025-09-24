import pulumi
import pulumi_aws as aws
from typing import Optional, Dict, Any


class PingInstance(pulumi.ComponentResource):
    def __init__(self, name: str, args: Dict[str, Any], opts: Optional[pulumi.ResourceOptions] = None):
        super().__init__("huckstream:aws:pingback", name, {}, opts)

        # Set context details
        self.namespace = args["namespace"]
        self.environment = args["environment"]
        self.name = args["name"]
        self.ip = args["myIP"]

        self.base_name = f"{self.namespace}-{self.environment}-{self.name}"

        # Set tags
        base_tags = {
            "Namespace": self.namespace,
            "Environment": self.environment,
            "Name": self.base_name
        }

        # Set networking config
        self.vpc_id = args["vpc_id"]
        self.subnet_id = args["subnet_id"]
        self.public = args.get("public", False)

        self.ami_id = args["ami_id"]
        self.instance_type = args.get("instance_type", "t3.micro")

        # Create the security group
        sg_name = f"{self.base_name}-sg"
        sg = aws.ec2.SecurityGroup(sg_name,
            name=sg_name,
            vpc_id=self.vpc_id,
            description="Allow private ICMP",
            ingress=[
                aws.ec2.SecurityGroupIngressArgs(
                    protocol="icmp",
                    from_port=-1,               # -1 specifies all ICMP types
                    to_port=-1,                 # -1 specifies all ICMP codes
                    cidr_blocks=["10.0.0.0/8"], # Allow all ICMP traffic on private subnets
                ),
                aws.ec2.SecurityGroupIngressArgs(
                    protocol="tcp",
                    from_port=80,                 # HTTP
                    to_port=80,                 # HTTP
                    cidr_blocks=[self.ip], # Allow my ip
                ),
                aws.ec2.SecurityGroupIngressArgs(
                    protocol="tcp",
                    from_port=443,                 # HTTPS
                    to_port=443,                 # HTTPS
                    cidr_blocks=[self.ip],  # Allow my ip
                ),
                aws.ec2.SecurityGroupIngressArgs(
                    protocol="tcp",
                    from_port=22,                 # SSH
                    to_port=22,                 # SSH
                    cidr_blocks=[self.ip],  # Allow my ip
                ),
            ],
            egress=[
                aws.ec2.SecurityGroupEgressArgs(
                    protocol="-1",
                    from_port=0,
                    to_port=0,
                    cidr_blocks=["0.0.0.0/0"],
                ),
            ],
            tags={
                **base_tags,
                "Name": sg_name
            },
            opts=pulumi.ResourceOptions(parent=self)
        )

        self.security_group_id = sg.id

        # Create the EC2 instance
        ec2 = aws.ec2.Instance(self.base_name,
            # Networking config
            subnet_id=self.subnet_id,
            vpc_security_group_ids=[self.security_group_id],
            associate_public_ip_address=self.public,

            # Instance config
            ami=self.ami_id,
            instance_type=self.instance_type,
            key_name="ky-workshop",
            metadata_options=aws.ec2.InstanceMetadataOptionsArgs(
                http_tokens="required",  # Require the use of IMDSv2
                http_endpoint="enabled",
                http_put_response_hop_limit=2,
            ),

            # Set root storage
            root_block_device=aws.ec2.InstanceRootBlockDeviceArgs(
                delete_on_termination=True,
                volume_type="gp3",
                volume_size=8,  # Size in GB
                # encrypted=True,
                # kms_key_id=kms_key.id,
                tags=base_tags
            ),

            # Set tags
            tags=base_tags,
            opts=pulumi.ResourceOptions(parent=self)
        )

        self.public_ip = ec2.public_ip
        self.private_ip = ec2.private_ip

        # Register outputs
        self.register_outputs({
            "security_group_id": self.security_group_id,
            "public_ip": self.public_ip,
            "private_ip": self.private_ip
        })