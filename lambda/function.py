import os
import psycopg2
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def handler(event, context):
    """Lambda function handler for batch updating the RDS database."""

    # Fetch environment variables
    db_host = os.environ["DB_HOST"]
    db_name = os.environ["DB_NAME"]
    db_user = os.environ["DB_USER"]
    db_port = os.environ["DB_PORT"]

    # It's recommended to store and retrieve the password securely using AWS Secrets Manager
    db_password = os.environ[
        "DB_PASSWORD"
    ]  # Replace with actual retrieval from Secrets Manager

    try:
        # Establish connection to the RDS instance
        connection = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password,
            port=db_port,
        )
        cursor = connection.cursor()

        # Example of a batch update query
        update_query = """
        UPDATE your_table
        SET some_column = some_value
        WHERE some_condition = true;
        """

        # Execute the query
        cursor.execute(update_query)
        connection.commit()

        logger.info("Batch update successful.")
        return {"statusCode": 200, "body": "Batch update successful"}

    except Exception as e:
        logger.error(f"Error during batch update: {e}")
        return {"statusCode": 500, "body": f"Batch update failed: {e}"}

    finally:
        # Clean up the connection
        if cursor:
            cursor.close()
        if connection:
            connection.close()
