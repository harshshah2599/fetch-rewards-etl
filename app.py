import hashlib
import json
import psycopg2
import boto3
from botocore.config import Config
from datetime import datetime

# Database connection parameters
DB_HOST = "localhost"
DB_PORT = 5432
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "postgres"

# AWS SQS Queue URL
SQS_QUEUE_URL = "http://localhost:4566/000000000000/login-queue"

# Initialize the SQS client to interact with Localstack SQS
# Localstack simulates AWS services locally
sqs = boto3.client(
    'sqs',
    endpoint_url='http://localhost:4566',  # URL for Localstack
    region_name='us-east-1',  # Dummy region
    aws_access_key_id='dummy',  # Dummy credentials
    aws_secret_access_key='dummy',
    config=Config(retries={'max_attempts': 10, 'mode': 'standard'})  # Config for retries
)

def get_sqs_messages():
    """
    Fetch messages from the SQS queue.

    Returns:
        list: A list of messages retrieved from the SQS queue.
    """
    response = sqs.receive_message(
        QueueUrl=SQS_QUEUE_URL,
        MaxNumberOfMessages=10,  # Fetch up to 10 messages at a time
        WaitTimeSeconds=10  # Long polling to wait for messages
    )
    messages = response.get('Messages', [])
    return messages

def mask_value(value):
    """
    Mask PII by hashing with SHA-256.

    Args:
        value (str): The value to be masked.

    Returns:
        str: The masked (hashed) value.
    """
    return hashlib.sha256(value.encode()).hexdigest()

def transform_message(message_body):
    """
    Transform the message: flatten the JSON and mask PII fields.

    Args:
        message_body (str): The JSON string of the message body.

    Returns:
        dict: The transformed message with masked PII fields.
    """
    try:
        data = json.loads(message_body)
        transformed_data = {
            'user_id': data['user_id'],
            'device_type': data['device_type'],
            'masked_ip': mask_value(data['ip']),
            'masked_device_id': mask_value(data['device_id']),
            'locale': data['locale'],
            'app_version': int(data['app_version'].split('.')[0]),  # Extract major version
            'create_date': datetime.strptime(data['create_date'], '%Y-%m-%d').date() if data.get('create_date') else None
        }
        return transformed_data
    except KeyError as e:
        print(f"Missing key {e} in message: {message_body}")
        return None
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None
    except Exception as e:
        print(f"Error processing message: {e}")
        return None

def insert_into_db(data):
    """
    Insert transformed data into Postgres.

    Args:
        data (dict): The transformed data to be inserted into the database.
    """
    try:
        # Establish a connection to the Postgres database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        insert_query = """
        INSERT INTO user_logins (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        # Execute the insert query with data
        cursor.execute(insert_query, (
            data['user_id'],
            data['device_type'],
            data['masked_ip'],
            data['masked_device_id'],
            data['locale'],
            data['app_version'],
            data['create_date']
        ))
        conn.commit()  # Commit the transaction
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error inserting into database: {e}")

def extract_messages():
    """
    Extract messages from SQS and print raw data.

    Returns:
        list: A list of raw data extracted from the SQS queue.
    """
    messages = get_sqs_messages()
    raw_data = [json.loads(message['Body']) for message in messages]
    for data in raw_data:
        print(data)  # Print raw data for verification
    return raw_data

def transform_messages():
    """
    Transform messages from SQS and print transformed data.

    Returns:
        list: A list of transformed data ready for loading into the database.
    """
    messages = get_sqs_messages()
    transformed_data = []
    for message in messages:
        body = message['Body']
        transformed = transform_message(body)
        if transformed:
            transformed_data.append(transformed)
            print(transformed)  # Print transformed data for verification
    return transformed_data

def load_messages():
    """
    Load transformed messages into Postgres and delete processed messages from SQS.
    """
    messages = get_sqs_messages()
    for message in messages:
        body = message['Body']
        transformed_data = transform_message(body)
        if transformed_data:
            insert_into_db(transformed_data)
            # Delete the message from the queue after processing
            sqs.delete_message(
                QueueUrl=SQS_QUEUE_URL,
                ReceiptHandle=message['ReceiptHandle']
            )

def display_raw_data():
    """
    Display raw data from SQS messages.

    Returns:
        list: A list of raw data extracted from the SQS queue.
    """
    messages = get_sqs_messages()
    raw_data = [json.loads(message['Body']) for message in messages]
    return raw_data

def display_transformed_data():
    """
    Display transformed data from Postgres.

    Returns:
        list: A list of rows fetched from the user_logins table in Postgres.
    """
    try:
        # Establish a connection to the Postgres database
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_logins")  # Fetch all rows from the user_logins table
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"Error fetching from database: {e}")
        return []

# If this script is run directly, execute the load_messages function
if __name__ == "__main__":
    load_messages()