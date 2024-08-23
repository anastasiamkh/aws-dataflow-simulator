import boto3
import csv
import psycopg2
import os

# Configuration
s3_bucket = "your-dataset-bucket"
s3_key = "future.csv"
rds_host = "your-rds-endpoint"
rds_dbname = "HistoricDataDB"
rds_user = "your-rds-username"
rds_password = "your-rds-password"
rds_port = 5432


def upload_csv_to_rds():
    s3_client = boto3.client("s3")

    # Download the CSV file from S3
    response = s3_client.get_object(Bucket=s3_bucket, Key=s3_key)
    csv_data = response["Body"].read().decode("utf-8").splitlines()
    reader = csv.DictReader(csv_data)

    # Connect to the RDS database
    conn = psycopg2.connect(
        host=rds_host,
        database=rds_dbname,
        user=rds_user,
        password=rds_password,
        port=rds_port,
    )
    cur = conn.cursor()

    # Create the table if it doesn't exist
    cur.execute(
        """
    CREATE TABLE IF NOT EXISTS historic_table (
        id SERIAL PRIMARY KEY,
        column1 VARCHAR(255),
        column2 VARCHAR(255),
        date DATE
    )
    """
    )

    # Insert CSV data into RDS
    for row in reader:
        cur.execute(
            "INSERT INTO historic_table (column1, column2, date) VALUES (%s, %s, %s)",
            (row["column1"], row["column2"], row["date"]),
        )

    # Commit the transaction and close the connection
    conn.commit()
    cur.close()
    conn.close()


if __name__ == "__main__":
    upload_csv_to_rds()
