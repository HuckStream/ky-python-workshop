import pulumi
import pulumi_aws as aws
import json

from lib.ping_instance import PingInstance
from lib.aurora_postgres import AuroraPostgres
from lib.encrypted_bucket import EncryptedBucket

def main():
    # Assemble resource name from context pieces
    config = pulumi.Config()
    namespace = config.require("namespace")
    environment = config.require("environment")
    name = config.require("name")
    base_name = f"{namespace}-{environment}-{name}"

    ######
    # Step 1
    #
    # Retrieve stack references and outputs for main VPC infrastructure deployment stack.
    ######

    # Get the current AWS region
    region = aws.get_region().name

    ##
    # ALT: Reference via Stack Name
    ##
    
    # vpc_stack = pulumi.StackReference(config.require("vpcStack"))

    # # Get the peering info
    # vpc_id = vpc_stack.get_output("vpc_id")
    # vpc_cidr = vpc_stack.get_output("vpc_cidr")
    # # Need to cast from Output[any] to Output[RouteTable[]]
    # vpc_rtbls = vpc_stack.get_output("route_tables").apply(
    #     lambda rtbls: rtbls
    # )
    # s3_endpoint_id = vpc_stack.get_output("s3_endpoint_id")
    # public_subnet_ids = vpc_stack.get_output("public_subnet_ids")

    ##
    # ALT: Reference via Environment
    ##

    # vpc_id = config.require("vpcId")
    # vpc_cidr = config.require("vpcCidr")
    # vpc_rtbls = json.loads(config.require("routeTables"))
    # s3_endpoint_id = config.require("s3Endpoint")
    # public_subnet_ids = json.loads(config.require("publicSubnetIds"))

   
   
    # subnet_id = public_subnet_ids[0]

    ######
    # Step 2
    #
    # Deploy compute instances
    ######

    # Get latest WordPress-ready AMI (Amazon Linux 2 for WordPress hosting)
    ping_ami_id = "ami-00a255e7ed399f977"

    # # Create main ping instances
    # public_app_ping = PingInstance("ping-public-app", {
    #     # Context
    #     "namespace": namespace,
    #     "environment": environment,
    #     "name": f"{name}-ping-public-app",

    #     # Networking
    #     "vpc_id": vpc_id,
    #     "subnet_id": subnet_id,
    #     "myIP": config.require("my_ip"),

    #     # Instance config
    #     "ami_id": ping_ami_id,
    #     "public": True
    # })

    ######
    # Step 3
    #
    # Deploy encrypted S3 bucket
    #
    # Also uncomment outputs labeled 'S3 Bucket Outputs' at the bottom
    ######
    # S3 Bucket
    # s3_bucket = EncryptedBucket("encrypted-bucket", {
    #     "namespace": namespace,
    #     "environment": environment,
    #     "name": name,

    #     ######
    #     # Step 4
    #     #
    #     # Provide the S3 VPC gateway endpoint to lock the S3 bucket down to only the VPC
    #     #
    #     # Also uncomment outputs labeled 'S3 Bucket Outputs' at the bottom
    #     ######

    #     "vpce_id": s3_endpoint_id,
    # })

    ######
    # Step 5
    #
    # Deploy Aurora Postgres DB Cluster
    #
    # Also uncomment outputs labeled 'RDS Outputs' at the bottom
    ######
    # RDS Cluster
    # db = AuroraPostgres("postgres", {
    #     "namespace": namespace,
    #     "environment": environment,
    #     "name": name,

    #     "db_instance_class": "db.t4g.medium",
    #     "version": "16.4",

    #     "vpc_id": vpc_id,
    #     "vpc_cidr": vpc_cidr,
    #     "subnet_ids": public_subnet_ids
    # })

    ######
    # Step 1
    #
    # VPC Outputs
    ######
    # pulumi.export("vpc_id", vpc_id)
    # pulumi.export("vpc_cidr", vpc_cidr)
    # pulumi.export("s3_endpoint_id", s3_endpoint_id)
    # pulumi.export("route_tables", vpc_rtbls)
    # pulumi.export("route_tables", vpc_rtbls)
    # pulumi.export("subnet_id", subnet_id)

    ######
    # Step 2
    #
    # EC2 Instance Outputs
    ######
    # pulumi.export("public_ip", public_app_ping.public_ip)
    # pulumi.export("private_ip", public_app_ping.private_ip)

    ######
    # Step 3
    #
    # S3 Bucket Outputs
    ######
    # pulumi.export("bucket_name", s3_bucket.bucket_name)
    # pulumi.export("bucket_arn", s3_bucket.bucket_arn)

    ######
    # Step 5
    #
    # RDS Outputs
    ######
    # pulumi.export("db_cluster_name", db.cluster_name)
    # pulumi.export("db_cluster_port", db.cluster_port)
    # pulumi.export("db_cluster_endpoint", db.cluster_endpoint)
    # pulumi.export("db_admin_user", db.admin_user)
    # pulumi.export("db_admin_password", db.admin_password)


if __name__ == "__main__":
    main()