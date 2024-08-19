from aws_cdk import (
    Stack,
    aws_cloudwatch as cloudwatch,
    aws_iam as iam,
    aws_kinesis as kinesis,
    aws_sns as sns,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_sns_subscriptions as subscriptions,
)
from aws_cdk.aws_ecr_assets import DockerImageAsset, Platform
from constructs import Construct

import aws_cdk as core
from aws_cdk import aws_cloudwatch_actions as cloudwatch_actions

import os

import src.config as config


class StreamingStack(Stack):
    def __init__(self, scope: Construct, id: str, bucket: s3.Bucket, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.bucket = bucket  # from S3BucketStack
        self.kinesis_stream = self._add_kinesis_stream()
        self.docker_image = self._build_docker_image()
        self.fargate_service = self._get_fargate_service()

        if config.get_billing_alarm_threshold() > 0:
            self._add_cloudwatch_alarm()

        return None

    def _add_kinesis_stream(self):
        kinesis_stream = kinesis.Stream(
            self, "DataStream", shard_count=1, removal_policy=core.RemovalPolicy.DESTROY
        )
        os.environ["KINESIS_STREAM_NAME"] = kinesis_stream.stream_name
        core.CfnOutput(self, "KinesisStreamName", value=kinesis_stream.stream_name)
        return kinesis_stream

    def _build_docker_image(self):
        docker_image = DockerImageAsset(
            self,
            "CsvToKinesisImage",
            platform=Platform.LINUX_AMD64,
            directory=".",  # Directory containing the Dockerfile
        )

        return docker_image

    def _get_fargate_service(self):
        # Create an ECS cluster
        vpc = ec2.Vpc(self, "Vpc", max_azs=2)  # VPC for ECS
        vpc.apply_removal_policy(core.RemovalPolicy.DESTROY)
        cluster = ecs.Cluster(self, "EcsCluster", vpc=vpc)
        cluster.node.add_dependency(self.kinesis_stream)

        # Define a Fargate task definition with the necessary IAM role
        task_role = iam.Role(
            self,
            "FargateTaskExecutionRole",
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AmazonECSTaskExecutionRolePolicy"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonKinesisFullAccess"
                ),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AmazonS3ReadOnlyAccess"
                ),
            ],
        )

        task_definition = ecs.FargateTaskDefinition(
            self,
            "FargateTaskDefinition",
            memory_limit_mib=1024,
            cpu=512,
            task_role=task_role,
        )

        # Add the container to the task definition
        container = task_definition.add_container(
            "FargateContainer",
            image=ecs.ContainerImage.from_docker_image_asset(self.docker_image),
            logging=ecs.LogDrivers.aws_logs(stream_prefix="FargateContainer"),
            environment={"KINESIS_STREAM_NAME": self.kinesis_stream.stream_name},
        )
        # Add a port mapping to the container
        container.add_port_mappings(ecs.PortMapping(container_port=80, host_port=80))
        # Define the Fargate service
        fargate_service = ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            "FargateService",
            cluster=cluster,
            task_definition=task_definition,
            public_load_balancer=False,  # This sets whether the load balancer should be public or not
        )
        # Grant the necessary permissions to the task
        self.bucket.grant_read(task_role)
        return fargate_service

    def _add_cloudwatch_alarm(self):
        """Setup CloudWatch Billing Alarm"""
        # Create an SNS Topic for sending the alarm notification
        topic = sns.Topic(self, "BillingAlarmTopic")

        # Add an email subscription to the SNS Topic
        topic.add_subscription(
            subscriptions.EmailSubscription(config.get_notifications_email())
        )
        # Define a CloudWatch Billing Alarm
        cost_alarm = cloudwatch.Alarm(
            self,
            "BillingAlarm",
            metric=cloudwatch.Metric(
                namespace="AWS/Billing",
                metric_name="EstimatedCharges",
                dimensions_map={"Currency": "EUR"},
                period=core.Duration.hours(6),
                statistic="Maximum",
            ),
            threshold=config.get_billing_alarm_threshold(),  # Set your threshold here (e.g., 100 USD)
            evaluation_periods=1,
            alarm_description=f"Alarm when estimated charges exceed {config.billing_alarm_threshold()}",
            actions_enabled=True,
        )

        # Add the SNS Topic as an alarm action
        cost_alarm.add_alarm_action(cloudwatch_actions.SnsAction(topic))
