import boto3
import csv
import json
import logging
import time

import aws_dataflow_simulator.config as config
from aws_dataflow_simulator.utils_s3 import download_file_from_s3

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CSVtoStream:
    def __init__(self):
        """Read the environmental variables."""
        self.bucket_name: str = config.get_s3_bucket_name()
        self.dataset_filepath: str = config.get_dataset_filepath(processed=True)
        self.kinesis_stream_name: str = config.get_kinesis_stream_name()

        # clients to connect to AWS services
        self._kinesis_client = boto3.client("kinesis")

    def load_dataset(self):
        decoded_cdv_data = download_file_from_s3(
            bucket_name=self.bucket_name, filepath=self.dataset_filepath
        )

        # parse the file
        file_content = decoded_cdv_data.splitlines()

        return file_content

    def start_stream(self) -> None:
        """Conevrt rows in csv file on AWS S3 to events in AWS Kinesis stream."""

        csv_reader = csv.DictReader(self.load_dataset())

        logger.info(
            {
                "message": "Starting Kinesis stream",
                "dataset_filepath": self.dataset_filepath,
                "s3_bucket": self.bucket_name,
                "kinesis_stream_name": self.kinesis_stream_name,
            }
        )
        # Skip the header row
        header = next(csv_reader, None)

        # Process each row in the CSV file and send it to the Kinesis stream
        for row in csv_reader:
            data = json.dumps(row)
            logging.info(f"Streaming row to Kinesis: {data}")
            self._kinesis_client.put_record(
                StreamName=self.kinesis_stream_name,
                Data=data,
                PartitionKey=row[
                    next(iter(row))
                ],  # Assuming the first column can be used as a partition key
            )

            if "time_till_next_event_ms" in row:
                delay_ms = int(float(row["time_till_next_event_ms"]))
                logging.info(f"Applying delay of {delay_ms} ms before next event.")
                time.sleep(delay_ms / 1000.0)

        logger.info(
            {
                "message": "Streaming to Kinesis complete. No more rows to stream",
                "dataset_filepath": self.dataset_filepath,
                "s3_bucket": self.bucket_name,
                "kinesis_stream_name": self.kinesis_stream_name,
            }
        )

        return {"statusCode": 200, "body": "Finished streaming data."}


if __name__ == "__main__":
    CSVtoStream().start_stream()
