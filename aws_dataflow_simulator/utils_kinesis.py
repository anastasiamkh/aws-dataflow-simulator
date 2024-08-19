import boto3
import base64
import os

from aws_dataflow_simulator.config import get_dataset_filepath
import csv

# AWS Kinesis Stream configuration
STREAM_NAME = os.getenv("KINESIS_STREAM_NAME")

# Initialize a Kinesis client
kinesis_client = boto3.client("kinesis")


# Read the header from the CSV file
def get_csv_header(file_path=get_dataset_filepath()):
    with open(file_path, newline="") as csvfile:
        reader = csv.reader(csvfile)
        header = next(reader)  # Read the first line, which is the header
    return header


# Convert row data to a dictionary
def row_to_dict(row_data, header):
    # Split the row data by commas (assuming it is comma-separated)
    row_values = row_data.split(",")
    # Map the row values to the header (column names) and create a dictionary
    return dict(zip(header, row_values))


def get_shard_iterator(stream_name, shard_id):
    response = kinesis_client.get_shard_iterator(
        StreamName=stream_name,
        ShardId=shard_id,
        ShardIteratorType="TRIM_HORIZON",  # You can change this to "LATEST" to get only the latest events
    )
    return response["ShardIterator"]


def get_records(shard_iterator):
    response = kinesis_client.get_records(
        ShardIterator=shard_iterator,
        Limit=10,  # Adjust the limit as needed
    )
    return response


def decode_data(base64_data):
    return base64.b64decode(base64_data).decode("utf-8")


def process_stream():
    header = get_csv_header()
    # Describe the stream to get shard IDs
    stream_description = kinesis_client.describe_stream(StreamName=STREAM_NAME)
    shards = stream_description["StreamDescription"]["Shards"]

    for shard in shards:
        shard_id = shard["ShardId"]
        print(f"Processing shard: {shard_id}")

        # Get the shard iterator
        shard_iterator = get_shard_iterator(STREAM_NAME, shard_id)

        while shard_iterator:
            # Get records from the shard
            records_response = get_records(shard_iterator)
            records = records_response["Records"]

            first_record = True  # Flag to check the first record
            for record in records:
                if first_record:
                    first_record = False  # Skip the first record
                    continue
                print(record)
                # Decode the base64-encoded data
                decoded_data = record["Data"].decode("utf-8")

                # Convert the row data to a dictionary using the header
                row_dict = row_to_dict(decoded_data, header)
                print(f"Event data: {row_dict}")

            # Move to the next shard iterator
            shard_iterator = records_response.get("NextShardIterator")
            if not shard_iterator:
                print(f"No more records in shard: {shard_id}")
                break


if __name__ == "__main__":
    process_stream()
