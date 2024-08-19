"""Helper functions to interact with AWS S3."""

import boto3
import fire
from typing import Any

from aws_dataflow_simulator.exceptions import (
    CouldNotUploadFileToS3,
    CouldNotLoadFileFromS3,
)


def upload_file_to_s3(bucket_name: str, filepath: str):
    """Upload a file to an S3 bucket.

    :param bucket_name: Bucket to upload to
    :param file_path: File to upload
    """
    s3_client = boto3.client("s3")
    try:
        s3_client.upload_file(filepath, bucket_name, filepath)
    except Exception as e:
        raise CouldNotUploadFileToS3(f"Failed to upload {filepath} to {bucket_name}: {e}")
    print(f"Successfully uploaded {filepath} to {bucket_name}")
    return


def download_file_from_s3(bucket_name: str, filepath: str) -> Any:
    """Download a file from an S3 bucket.

    :param bucket_name: Bucket from which to download the file
    :param file_path: filepath on s3 bucket
    """
    s3_client = boto3.client("s3")

    # response = s3_client.get_object(Bucket=bucket_name, Key=filepath)
    try:
        # Download the CSV file from S3 into memory
        csv_obj = s3_client.get_object(Bucket=bucket_name, Key=filepath)
        body = csv_obj["Body"].read().decode("utf-8")

    except Exception as e:
        raise CouldNotLoadFileFromS3(
            f"Could not load file {filepath} from bucket {bucket_name}: {str(e)}"
        )
    return body


if __name__ == "__main__":
    fire.Fire()
