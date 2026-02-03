# GCP Real-Time IoT Pipeline

A scalable, cloud-native system to ingest, process, and analyze simulated IoT sensor data using Google Cloud Platform.

## Architecture

```mermaid
graph LR
    S[Sensor Simulator] -->|HTTP POST| API[Ingestion API\n(App Engine)]
    API -->|Publish| PS[Pub/Sub\n(telemetry-topic)]
    PS -->|Pull| W[Worker Service\n(GKE)]
    W -->|Raw JSON| GCS[Cloud Storage]
    W -->|Structured Data| DB[(Cloud SQL\nPostgreSQL)]
    
    subgraph Analytics
        VM[Compute Engine] -->|Daily Cron| DB
        VM -->|Generate Report| R[CSV Report]
        R --> GCS
    end
```

## Folder Structure

- `ingestion_api/`: FastAPI app for App Engine.
- `processing_worker/`: Dockerized worker for GKE.
- `sensor_simulator/`: Python script to generate fake traffic.
- `k8s/`: Kubernetes deployment manifests.
- `database/`: SQL schema initialization.
- `scripts/`: Setup utilities.

## Deployment Guide

### 1. Prerequisites
- Google Cloud SDK (`gcloud`) installed.
- Docker installed.
- Python 3.10+ installed.

### 2. Setup Infrastructure
Run the helper script to provision GKE, Cloud SQL, Pub/Sub, and GCS:
```bash
./scripts/setup_gcp_resources.sh
```

### 3. Deploy Ingestion API (App Engine)
```bash
cd ingestion_api
gcloud app deploy app.yaml --project=YOUR_PROJECT_ID
```
*Note the URL of the deployed app.*

### 4. Deploy Processing Worker (GKE)
Build and push the image:
```bash
cd processing_worker
docker build -t gcr.io/YOUR_PROJECT_ID/processing-worker:latest .
docker push gcr.io/YOUR_PROJECT_ID/processing-worker:latest
```
Deploy to Kubernetes:
```bash
# Update k8s/deployment.yaml with your specific DB credentials/secrets first!
kubectl apply -f ../k8s/deployment.yaml
```

### 5. Run Sensor Simulator
Update `API_URL` in `sensor_simulator/main.py` with your App Engine URL.
```bash
cd sensor_simulator
pip install -r requirements.txt
python main.py
```

## Monitoring
- **Logs**: Check `gcloud app logs tail` or the Logs Explorer for GKE container logs.
- **Metrics**: View Pub/Sub queue depth and GKE CPU usage in Cloud Monitoring.
