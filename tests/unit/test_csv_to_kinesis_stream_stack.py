import aws_cdk as core
import aws_cdk.assertions as assertions

from csv_to_kinesis_stream.csv_to_kinesis_stream_stack import CsvToKinesisStreamStack

# example tests. To run these tests, uncomment this file along with the example
# resource in csv_to_kinesis_stream/csv_to_kinesis_stream_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = CsvToKinesisStreamStack(app, "csv-to-kinesis-stream")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
