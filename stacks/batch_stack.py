from aws_cdk import (
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_events as events,
    aws_events_targets as targets,
    aws_rds as rds,
    aws_ec2 as ec2,
    Stack,
)
from constructs import Construct


class BatchUpdateStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create an S3 bucket for datasets
        dataset_bucket = s3.Bucket(self, "DatasetBucket")

        # Create a VPC for the RDS instance
        vpc = ec2.Vpc(self, "RDSVpc", max_azs=2)

        # Create an RDS instance for storing historic data
        rds_instance = rds.DatabaseInstance(
            self,
            "RDSInstance",
            engine=rds.DatabaseInstanceEngine.postgres(
                version=rds.PostgresEngineVersion.VER_13_3
            ),
            vpc=vpc,
            allocated_storage=20,
            max_allocated_storage=100,
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO
            ),
            credentials=rds.Credentials.from_generated_secret("postgres"),
            database_name="HistoricDataDB",
            vpc_subnets={"subnet_type": ec2.SubnetType.PUBLIC},
            publicly_accessible=True,
        )

        # Create a Lambda function to process the data
        lambda_function = _lambda.Function(
            self,
            "DataProcessingLambda",
            runtime=_lambda.Runtime.PYTHON_3_9,
            handler="lambda_function.lambda_handler",
            code=_lambda.Code.from_asset("lambda"),
            environment={
                "DATASET_BUCKET": dataset_bucket.bucket_name,
                "RDS_ENDPOINT": rds_instance.db_instance_endpoint_address,
                "RDS_PORT": rds_instance.db_instance_endpoint_port,
                "RDS_DB_NAME": "HistoricDataDB",
                "RDS_SECRET_NAME": rds_instance.secret.secret_name,
            },
            vpc=vpc,
            vpc_subnets={"subnet_type": ec2.SubnetType.PUBLIC},
        )

        # Grant the Lambda function permissions to read/write to S3 and access RDS
        dataset_bucket.grant_read_write(lambda_function)
        rds_instance.grant_connect(lambda_function)

        # Create a CloudWatch EventBridge rule to trigger the Lambda function daily
        rule = events.Rule(
            self,
            "ScheduleRule",
            schedule=events.Schedule.cron(
                minute="0", hour="2"
            ),  # Every day at midnight UTC
        )

        # Add the Lambda function as the target of the EventBridge rule
        rule.add_target(targets.LambdaFunction(lambda_function))

        # Output the RDS endpoint and S3 bucket names for reference
        self.output = Stack.of(self).stack_outputs.add(
            f"RDSInstanceEndpoint",
            description="The endpoint address of the RDS instance",
            value=rds_instance.db_instance_endpoint_address,
        )
        self.output = Stack.of(self).stack_outputs.add(
            f"DatasetBucketName",
            description="The name of the S3 bucket for datasets",
            value=dataset_bucket.bucket_name,
        )
