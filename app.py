#!/usr/bin/env python3
import aws_cdk as core

from stacks.streaming_stack import StreamingStack
from stacks.s3_stack import S3BucketStack

app = core.App()

# Deploy the first stack and create the S3 bucket
s3_stack = S3BucketStack(app, "S3BucketStack")

# Deploy the second stack, passing the S3 bucket from the first stack
main_stack = StreamingStack(app, "StreamingStack", bucket=s3_stack.bucket)

app.synth()
