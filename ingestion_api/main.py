import os
import json
import base64
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google.cloud import pubsub_v1
from datetime import datetime

app = FastAPI(title="IoT Ingestion API")

# Configuration
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "your-project-id")
TOPIC_ID = os.getenv("PUBSUB_TOPIC", "telemetry-topic")

# Initialize Pub/Sub Publisher (only works if creds are set, gracefully handle if not for local test)
publisher = None
try:
    publisher = pubsub_v1.PublisherClient()
    topic_path = publisher.topic_path(PROJECT_ID, TOPIC_ID)
except Exception as e:
    print(f"Warning: Pub/Sub not initialized (Simulated Mode): {e}")

class TelemetryData(BaseModel):
    device_id: str
    timestamp: str
    temperature: float
    humidity: float
    battery_level: float

@app.get("/")
def health_check():
    return {"status": "running", "service": "ingestion-api"}

@app.post("/ingest")
def ingest_data(data: TelemetryData):
    """Receives telemetry data and publishes it to Pub/Sub."""
    payload = data.dict()
    payload_json = json.dumps(payload).encode("utf-8")
    
    if publisher:
        try:
            future = publisher.publish(topic_path, payload_json)
            message_id = future.result()
            return {"status": "success", "message_id": message_id}
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Pub/Sub error: {str(e)}")
    else:
        # Local simulation
        print(f"[SIMULATED PUBSUB] Published: {payload}")
        return {"status": "simulated", "data": payload}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
