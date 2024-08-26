import os
import boto3
import json
import logging
import psycopg2
import pandas as pd
from tqdm import tqdm

from dotenv import load_dotenv

from botocore.exceptions import ClientError

# Load environment variables from .env file
load_dotenv()


def get_db_secret(secret_name: str) -> dict:
    """Retrieve the database password from AWS Secrets Manager."""
    client = boto3.client("secretsmanager")
    try:
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
        secret = get_secret_value_response["SecretString"]
        # Parse the JSON string into a dictionary
        secret_dict = json.loads(secret)
        return secret_dict
    except ClientError as e:
        logging.error(f"Failed to retrieve secret {secret_name}: {e}")


def generate_create_table_query(table_name: str, df: pd.DataFrame, index_colname: str):
    """Generate a SQL CREATE TABLE statement based on the DataFrame."""
    sql_types = {
        "object": "VARCHAR",
        "int64": "INT",
        "float64": "FLOAT",
        "datetime64[ns]": "TIMESTAMP",
        "bool": "BOOLEAN",
    }

    columns = []
    for col, dtype in df.dtypes.items():
        sql_type = sql_types.get(str(dtype), "VARCHAR")
        if col != index_colname:
            columns.append(f"{col} {sql_type}")

    columns_sql = ",\n".join([col for col in columns if col != index_colname])

    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {index_colname} SERIAL PRIMARY KEY,
        {columns_sql}
    );
    """
    return create_table_query


def create_table(table_name: str, file_path: str, index_colname: str):
    """Connect to the RDS instance and create tables."""
    secret_name = os.getenv("DB_SECRET_NAME")
    secret_dict = get_db_secret(secret_name)

    db_host = secret_dict["host"]
    db_name = secret_dict["dbname"]
    db_user = secret_dict["username"]
    db_port = secret_dict["port"]
    db_password = secret_dict["password"]

    try:
        # Connect to RDS instance
        connection = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port=db_port,
        )
        cursor = connection.cursor()

        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path)

        # Generate SQL CREATE TABLE query based on the DataFrame
        create_table_query = generate_create_table_query(table_name, df, index_colname)

        # Execute the CREATE TABLE query
        cursor.execute(create_table_query)
        connection.commit()

        logging.info(f"Table '{table_name}' created successfully in the database.")

        # Insert the data from the CSV into the table
        for i, row in df.iterrows():
            cols = ", ".join(list(df.columns))
            vals = ", ".join(["%s"] * len(row))
            insert_query = f"INSERT INTO {table_name} ({cols}) VALUES ({vals})"
            cursor.execute(insert_query, tuple(row))
        connection.commit()

        logging.info(
            f"Data from '{file_path}' inserted successfully into '{table_name}'."
        )

    except Exception as e:
        logging.warning(f"Error creating table or inserting data: {e}")

    finally:
        # Clean up the connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()
