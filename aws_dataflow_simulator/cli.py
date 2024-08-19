import click
import boto3
import yaml
import os
from datetime import datetime

from aws_dataflow_simulator import config, utils_dataset


@click.group()
def cli():
    """AWS Dataflow Simulator CLI"""
    pass


@cli.command()
@click.option(
    "--aws-s3-bucket-name",
    prompt="AWS S3 Bucket Name",
    help="The name of the S3 bucket",
    required=True,
)
@click.option(
    "--aws-ecr-repo-name",
    prompt="AWS ECR Repo Name",
    help="The name of the ECR repository",
    required=True,
)
@click.option(
    "--aws-notifications-email",
    prompt="AWS Notifications Email",
    help="The email address for notifications",
    required=False,
)
@click.option(
    "--cloudwatch-alarm-thresh",
    prompt="CloudWatch Billing Alarm Threshold (EUR)",
    help="The billing alarm threshold in EUR",
    type=float,
    default=10,
    required=False,
)
@click.option(
    "--dataset-filepath",
    prompt="Dataset File Path",
    help="The local path to the dataset file",
    required=True,
)
@click.option(
    "--dataset-s3-filepath",
    prompt="S3 File Path for Dataset",
    help="The S3 path for the dataset",
    required=True,
)
@click.option(
    "--streaming-start-datetime",
    prompt="First Event Date (YYYY-MM-DD HH-MM-SS)",
    help="The first event date and time in the dataset",
    required=False,
    default=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
)
@click.option(
    "--dataset-apply-delay",
    prompt="Do you want to apply delay between streamed events?",
    help="True if you want to specify delay in ms or use timestamp column for calculations.",
    is_flag=True,
)
@click.option(
    "--dataset-delay-ms",
    prompt="(Optional) Delay between events in milliseconds",
    help="Delay between events in millieseconds",
    default=-1,
    required=False,
    show_default=True,
    type=int,
)
@click.option(
    "--dataset-dt-column",
    prompt="(Optional) Dataset Column Name for Transactions",
    help="The column name for transaction dates",
    default="",
    show_default=True,
    required=False,
)
def configure(
    aws_s3_bucket_name,
    aws_ecr_repo_name,
    aws_notifications_email,
    cloudwatch_alarm_thresh,
    dataset_filepath,
    dataset_s3_filepath,
    streaming_start_datetime,
    dataset_apply_delay,
    dataset_delay_ms,
    dataset_dt_column,
):
    """Interactively generate the YAML config file."""

    # Check if --apply-delay is provided, then require --delay-duration
    if dataset_apply_delay and ((dataset_delay_ms < 0) and (dataset_dt_column == "")):
        raise click.UsageError(
            "--delay_ms OR --dataset-dt-column is required when --apply-delay is used."
        )

    base_name, ext = os.path.splitext(dataset_filepath)
    processed_filepath = f"{base_name}_processed{ext}"

    config_data = {
        "aws": {
            "s3_bucket_name": aws_s3_bucket_name,
            "ecr_repo_name": aws_ecr_repo_name,
            "notifications_email": aws_notifications_email,
            "cloudwatch_alarm_thresh": cloudwatch_alarm_thresh,
        },
        "dataset": {
            "filepath": dataset_filepath,
            "filepath_processed": processed_filepath,
            "s3_filepath": dataset_s3_filepath,
            "first_event_dt": streaming_start_datetime,
            "colname_dt": dataset_dt_column.lower(),
            "apply_delay": dataset_apply_delay,
            "delay_ms": dataset_delay_ms,
        },
    }

    with open("dataflow_config.yaml", "w") as file:
        yaml.dump(config_data, file)

    click.echo("dataflow_config.yaml file generated successfully.")


@click.group()
def s3():
    """Commands for S3 operations."""
    pass


@s3.command()
@click.argument("file_path")
@click.argument("s3_key")
@click.argument("bucket_name")
@click.option("--confirm", is_flag=True, help="Confirm before uploading")
def upload(file_path, s3_key, bucket_name, confirm):
    """Upload a file to S3."""
    if not os.path.isfile(file_path):
        click.echo(f"Error: File '{file_path}' does not exist.")
        return

    if confirm:
        if not click.confirm(
            f"Are you sure you want to upload {file_path} to s3://{bucket_name}/{s3_key}?"
        ):
            click.echo("Upload cancelled.")
            return
    s3 = boto3.client("s3")
    try:
        s3.upload_file(file_path, bucket_name, s3_key)
        click.echo(f"File {file_path} uploaded to s3://{bucket_name}/{s3_key}")
    except Exception as e:
        click.echo(f"Error uploading file: {e}")


@s3.command()
@click.argument("s3_key")
@click.argument("file_path")
@click.argument("bucket_name")
def download(s3_key, file_path, bucket_name):
    """Download a file from S3."""
    s3 = boto3.client("s3")
    try:
        s3.download_file(bucket_name, s3_key, file_path)
        click.echo(f"File s3://{bucket_name}/{s3_key} downloaded to {file_path}")
    except Exception as e:
        click.echo(f"Error downloading file: {e}")


@click.group()
def dataset():
    """Commands for dataset operations."""
    pass


@dataset.command()
def prepare():
    """Preparing dataset for streaming."""
    click.echo("Preparing dataset for streaming.")
    dataset_path = config.get_dataset_filepath(processed=False)
    apply_delay = config.get_apply_delay()
    delay_ms = config.get_delay_ms()
    timestamp_column_name = config.get_colname_dt()
    start_datetime = config.get_first_event_dt()

    click.echo(f"Preparing dataset {dataset_path} for streaming.")
    if apply_delay:
        if delay_ms:
            click.echo(f"Calculating event delay using static value (ms): {delay_ms}")
        else:
            click.echo(f"Calculating event delay using dt column {timestamp_column_name}")

    df_processed = utils_dataset.preprocess_dataset(
        dataset_path=dataset_path,
        start_datetime=start_datetime,
        apply_delay=apply_delay,
        delay_ms=delay_ms,
        timestamp_column_name=timestamp_column_name,
    )

    base_name, ext = os.path.splitext(dataset_path)
    new_filepath = f"{base_name}_processed{ext}"
    df_processed.to_csv(new_filepath, index=False)


# Add the s3 and dataset groups to the main CLI group
cli.add_command(s3)
cli.add_command(dataset)

# Usage example
# `poetry run dataflowsim s3 upload path/to/local/file.csv s3_key --bucket-name your-s3-bucket``
# `poetry run dataflowsim dataset normalize_timestamps "2024-08-19 09-00-00" --apply-delay`


if __name__ == "__main__":
    cli()
