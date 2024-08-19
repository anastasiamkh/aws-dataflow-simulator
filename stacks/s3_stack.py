"""Provisios an S3 bucket to upload the csv file."""

import aws_cdk as core
from aws_cdk import aws_s3 as s3, RemovalPolicy
from constructs import Construct

import aws_dataflow_simulator.config as config


class S3BucketStack(core.Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        self.bucket = s3.Bucket(
            self,
            "CsvKinesisProjectBucket",
            bucket_name=config.get_s3_bucket_name(),
            versioned=False,
            removal_policy=RemovalPolicy.DESTROY,  # Allows bucket deletion
            auto_delete_objects=True,  # Optional: Automatically delete objects in the bucket
        )
        # Outputs
        core.CfnOutput(self, "BucketName", value=self.bucket.bucket_name)
        return
