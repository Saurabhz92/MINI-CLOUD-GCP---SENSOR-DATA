import time
import random
import json
import requests
import os
from datetime import datetime

# Configuration
API_URL = os.getenv("API_URL", "http://localhost:8080/ingest")
DEVICE_ID = os.getenv("DEVICE_ID", "device-001")
INTERVAL = int(os.getenv("INTERVAL", 2))

def generate_telemetry():
    """Generates fake sensor data."""
    return {
        "device_id": DEVICE_ID,
        "timestamp": datetime.utcnow().isoformat(),
        "temperature": round(random.uniform(20.0, 30.0), 2),
        "humidity": round(random.uniform(40.0, 70.0), 2),
        "battery_level": round(random.uniform(10.0, 100.0), 2)
    }

def main():
    print(f"Starting sensor simulator for {DEVICE_ID}...")
    print(f"Targeting API: {API_URL}")
    
    while True:
        data = generate_telemetry()
        try:
            response = requests.post(API_URL, json=data)
            if response.status_code == 200:
                print(f"Sent: {data} | Status: {response.status_code}")
            else:
                print(f"Failed: {response.status_code} | {response.text}")
        except Exception as e:
            print(f"Error sending data: {e}")
        
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
