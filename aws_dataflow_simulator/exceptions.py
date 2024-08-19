"""Custom Exceptions."""


class CouldNotLoadFileFromS3(Exception):
    """Could not load file from AWS S3."""


class CouldNotUploadFileToS3(Exception):
    """Could not upload file to AWS S3."""
