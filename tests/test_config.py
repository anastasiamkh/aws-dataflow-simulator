import os
from pathlib import Path
import pytest
from unittest.mock import patch, mock_open

# Assuming the configuration functions are in a module named config
from src.config import (
    get_dataset_filepath,
    get_s3_bucket_name,
    get_kinesis_stream_name,
    get_ecr_repo_name,
    get_notifications_email,
    billing_alarm_threshold,
)

# Importing mocked values from the mocked_config file
mock_aws_config = {
    "aws": {
        "s3_bucket_name": "test-bucket",
        "ecr_repo_name": "test-ecr-repo",
        "notifications_email": "test@example.com",
        "cloudwatch_billing_alarm_threshold_eur": 100,
    },
    "dataset": {"filepath": "/data/test.csv"},
}


@pytest.fixture
def mock_config():
    with patch.dict("src.config.aws_config", mock_aws_config):
        yield


def test_get_dataset_filepath(mock_config):
    assert get_dataset_filepath() == "/data/test.csv"


def test_get_s3_bucket_name(mock_config):
    assert get_s3_bucket_name() == "test-bucket"


def test_get_s3_bucket_name_missing_value(mock_config):
    broken_yaml_content_missing_s3 = {
        "aws": {
            "s3_bucket_name": "",
        },
        "dataset": {"filepath": "/data/test.csv"},
    }
    with patch.dict("src.config.aws_config", broken_yaml_content_missing_s3):
        with pytest.raises(
            KeyError, match="No value set for aws s3_bucket_name in config.yaml"
        ):
            get_s3_bucket_name()


def test_get_kinesis_stream_name():
    with patch.dict(os.environ, {"KINESIS_STREAM_NAME": "test-stream"}):
        assert get_kinesis_stream_name() == "test-stream"


def test_get_kinesis_stream_name_missing_env():
    with patch.dict(os.environ, {}, clear=True):
        with pytest.raises(KeyError, match="KINESIS_STREAM_NAME not set in container."):
            get_kinesis_stream_name()


def test_get_ecr_repo_name(mock_config):
    assert get_ecr_repo_name() == "test-ecr-repo"


def test_get_ecr_repo_name_missing_value(mock_config):
    broken_yaml_content_missing_ecr = {
        "aws": {
            "ecr_repo_name": "",
        },
        "dataset": {"filepath": "/data/test.csv"},
    }
    with patch.dict("src.config.aws_config", broken_yaml_content_missing_ecr):
        with pytest.raises(
            KeyError, match="No value set for aws ecr_repo_name in config.yaml"
        ):
            get_ecr_repo_name()


def test_get_notifications_email(mock_config):
    assert get_notifications_email() == "test@example.com"


def test_billing_alarm_threshold(mock_config):
    assert billing_alarm_threshold() == 100
