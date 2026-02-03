import os
import pandas as pd
import psycopg2
from google.cloud import storage
from datetime import datetime, timedelta

# Config
DB_HOST = "10.0.0.5" # Internal IP of Cloud SQL or use Proxy
DB_NAME = "iot_db"
DB_USER = "postgres"
DB_PASS = "password123"
BUCKET_NAME = os.getenv("GCS_BUCKET", "iot-raw-data-your-project")

def generate_report():
    print("Generating Daily Report...")
    
    conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    
    # Query last 24h data
    query = """
    SELECT device_id, AVG(temperature) as avg_temp, MAX(temperature) as max_temp, AVG(humidity) as avg_hum
    FROM sensor_measurements 
    WHERE timestamp > NOW() - INTERVAL '1 day'
    GROUP BY device_id
    """
    
    df = pd.read_sql(query, conn)
    conn.close()
    
    # Save to CSV
    filename = f"daily_report_{datetime.now().strftime('%Y-%m-%d')}.csv"
    df.to_csv(filename, index=False)
    
    # Upload to GCS
    client = storage.Client()
    bucket = client.bucket(BUCKET_NAME)
    blob = bucket.blob(f"reports/{filename}")
    blob.upload_from_filename(filename)
    
    print(f"Report uploaded to gs://{BUCKET_NAME}/reports/{filename}")

if __name__ == "__main__":
    generate_report()
