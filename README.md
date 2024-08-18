# `aws-dataflow-simulator`
`aws-dataflow-simulator` is a Python package that simplifies the creation of AWS infrastructure for simulating real-time data streams and batch processing, particularly useful for machine learning (ML) projects. This guide will walk you through the setup of a real-time data streaming solution, where rows from a CSV file are streamed as events using AWS CDK.

### Prerequisites
Before you start, ensure you have the following:

* **AWS Account**: You need an active AWS account with permissions to create and manage resources like S3, Kinesis, and IAM roles.
* **CSV File**: Have a CSV file ready that you want to stream as events.
* **Python 3.11+**: Ensure you have Python installed on your machine.
* **AWS CLI**: Install and configure the AWS CLI with credentials and region.
* **Node.js**: Install Node.js (needed for AWS CDK).

### Installation
1. Install the Package
First, install the aws-dataflow-simulator package using pip:

bash
Copy code
pip install aws-dataflow-simulator
2. Install AWS CDK
Ensure that AWS CDK is installed globally on your machine:

bash
Copy code
npm install -g aws-cdk
3. Set Up Your Project
Initialize your project with the AWS CDK:

bash
Copy code
mkdir my-dataflow-project
cd my-dataflow-project
cdk init app --language python
Then, add the aws-dataflow-simulator package to your project’s dependencies.

## Testing CDK stack locally
https://github.com/aws-samples/localstack-aws-cdk-example
1. Install awslocal, localstack, cdklocal
`brew install localstack/tap/localstack-cli awscli-local && npm install -g aws-cdk-local`
2. Bootstrap local env
`cdklocal bootstrap`
3. Deploy local stack
`cdk deploy --require-approval never`
