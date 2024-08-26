# `aws-dataflow-simulator`
`aws-dataflow-simulator` is a Python package that simplifies the creation of AWS infrastructure for simulating real-time data streams and batch processing, particularly useful for machine learning (ML) projects. This guide will walk you through the setup of a real-time data streaming solution, where rows from a CSV file are streamed as events using AWS services provisioned with AWS CDK.

### Prerequisites
Before you start, ensure you have the following:

* **AWS Account**: You need an active AWS account with permissions to create and manage resources like S3, Kinesis, and IAM roles.
* **CSV File**: Have a CSV file ready that you want to stream as events.
* **Python 3.11+**: Ensure you have Python installed on your machine.
* **AWS CLI**: Install and configure the AWS CLI with credentials and region.
* **Node.js**: Install Node.js (needed for AWS CDK).

### Installation
1. Install the Package
First, install the `aws-dataflow-simulator` package using pip: `pip install aws-dataflow-simulator`

2. Install AWS CDK: `npm install -g aws-cdk`
3. Configure aws cli on your machine with `aws configure` or using environmental variables.
# TODO: add link or detailed instructions

4. Set Up Your Project
1. Create config using cli commands -> YAML config #TODO
2. Add your file
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

# dummy

# To Do List
- [x] Add time delay to streaming based on timestamp difference between rows
- [x] add interactive config.yaml generator that overwrites the template
- [] Add digrams (CDK Stack & Pipeline)
- [] Add installation instructions & usage with other AWS account & csv files
- [] Add support for other data formats
- [] Add usage ideas
- [] make sure no extra files are packages
- [] add unit tests
- [] add basic CI/CD pipeine for linting-testing-publishing
