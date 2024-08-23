from aws_cdk import (
    Stack,
    aws_rds as rds,
    aws_ec2 as ec2,
    aws_lambda as _lambda,
    aws_iam as iam,
    aws_events as events,
    aws_events_targets as targets,
    Duration,
    RemovalPolicy,
)
from constructs import Construct

DB_NAME = "dataflow"


class BatchStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a VPC for the RDS instance and Lambda function
        vpc = ec2.Vpc(self, "MyVpc", max_azs=2)

        # # Create an RDS database instance (PostgreSQL in this example)
        # rds_instance = rds.DatabaseInstance(
        #     self,
        #     "RDSInstance",
        #     database_name=DB_NAME,
        #     engine=rds.DatabaseInstanceEngine.postgres(
        #         version=rds.PostgresEngineVersion.VER_13_3
        #     ),
        #     instance_type=ec2.InstanceType.of(
        #         ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO
        #     ),
        #     vpc=vpc,
        #     vpc_subnets={
        #         "subnet_type": ec2.SubnetType.PUBLIC,
        #     },
        #     multi_az=False,
        #     allocated_storage=20,
        #     storage_type=rds.StorageType.GP2,
        #     publicly_accessible=True,
        #     removal_policy=RemovalPolicy.DESTROY,
        #     deletion_protection=False,
        #     backup_retention=Duration.days(7),
        #     credentials=rds.Credentials.from_generated_secret("postgres"),
        # )

        # # Create a Lambda function
        # lambda_function = _lambda.Function(
        #     self,
        #     "UpdateDatabaseunction",
        #     runtime=_lambda.Runtime.PYTHON_3_11,
        #     handler="lambda_function.handler",
        #     code=_lambda.Code.from_asset(
        #         "lambda"
        #     ),  # assumes code is in the lambda/ directory
        #     environment={
        #         "DB_HOST": rds_instance.db_instance_endpoint_address,
        #         "DB_NAME": DB_NAME,
        #         "DB_USER": "postgres",
        #         "DB_PORT": "5432",
        #         # 'DB_PASSWORD': stored in Secrets Manager, referenced by Lambda
        #     },
        #     vpc=vpc,
        #     security_groups=[rds_instance.connections.security_groups[0]],
        #     timeout=Duration.minutes(10),
        # )

        # # Grant the Lambda function permission to access the RDS instance
        # rds_instance.grant_connect(lambda_function)

        # # Create an EventBridge rule to trigger the Lambda function at 2 AM daily
        # rule = events.Rule(
        #     self,
        #     "Rule",
        #     schedule=events.Schedule.cron(minute="0", hour="2"),
        # )

        # rule.add_target(targets.LambdaFunction(lambda_function))
