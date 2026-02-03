import os
import json
import logging
import psycopg2
from google.cloud import pubsub_v1
from google.cloud import storage
from datetime import datetime

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")
SUBSCRIPTION_ID = os.getenv("PUBSUB_SUBSCRIPTION", "telemetry-sub")
BUCKET_NAME = os.getenv("GCS_BUCKET", "raw-sensor-data")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "password")
DB_NAME = os.getenv("DB_NAME", "iot_db")
DB_CONNECTION_NAME = os.getenv("DB_CONNECTION_NAME")  # e.g., project:region:instance for Cloud SQL Proxy

# Initialize Clients
subscriber = pubsub_v1.SubscriberClient()
storage_client = storage.Client()
subscription_path = subscriber.subscription_path(PROJECT_ID, SUBSCRIPTION_ID)

def get_db_connection():
    """Establishes a database connection."""
    try:
        # If running on cloud with connection name (Unix socket)
        if DB_CONNECTION_NAME:
            conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASS,
                host=f'/cloudsql/{DB_CONNECTION_NAME}'
            )
        else:
            # TCP connection (Local/Testing)
            conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASS,
                host=DB_HOST
            )
        return conn
    except Exception as e:
        logging.error(f"Database connection failed: {e}")
        return None

def save_to_gcs(data, message_id):
    """Saves raw JSON data to GCS."""
    try:
        bucket = storage_client.bucket(BUCKET_NAME)
        timestamp = datetime.utcnow()
        blob_path = f"{timestamp.year}/{timestamp.month:02d}/{timestamp.day:02d}/{message_id}.json"
        blob = bucket.blob(blob_path)
        blob.upload_from_string(json.dumps(data), content_type='application/json')
        logging.info(f"Saved to GCS: qs://{BUCKET_NAME}/{blob_path}")
    except Exception as e:
        logging.error(f"GCS save failed: {e}")

def save_to_db(data):
    """Inserts structured data into Cloud SQL."""
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        query = """
            INSERT INTO sensor_measurements (device_id, timestamp, temperature, humidity, battery_level)
            VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            data.get("device_id"),
            data.get("timestamp"),
            data.get("temperature"),
            data.get("humidity"),
            data.get("battery_level")
        ))
        conn.commit()
        cursor.close()
        conn.close()
        logging.info("Saved to DB")
    except Exception as e:
        logging.error(f"DB insert failed: {e}")

def callback(message):
    """Pub/Sub message callback."""
    logging.info(f"Received message: {message.message_id}")
    try:
        data = json.loads(message.data.decode("utf-8"))
        
        # 1. Archive Raw Data
        save_to_gcs(data, message.message_id)
        
        # 2. Store Structured Data
        save_to_db(data)
        
        message.ack()
    except Exception as e:
        logging.error(f"Error processing message: {e}")
        message.nack()

def main():
    logging.info(f"Listening for messages on {subscription_path}...")
    try:
        streaming_pull_future = subscriber.subscribe(subscription_path, callback=callback)
        streaming_pull_future.result()
    except KeyboardInterrupt:
        streaming_pull_future.cancel()
    except Exception as e:
        logging.error(f"Subscriber failed: {e}")

if __name__ == "__main__":
    main()
