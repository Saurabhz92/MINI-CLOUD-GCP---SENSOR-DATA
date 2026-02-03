#!/bin/bash
# GCP Resource Setup Script
# Make sure you are authenticated: gcloud auth login && gcloud config set project YOUR_PROJECT_ID

PROJECT_ID="your-project-id"
REGION="us-central1"
ZONE="us-central1-a"
BUCKET_NAME="iot-raw-data-${PROJECT_ID}"
SQL_INSTANCE="iot-sql-instance"
DB_NAME="iot_db"
Topic_NAME="telemetry-topic"
SUB_NAME="telemetry-sub"

echo "Enabling Services..."
gcloud services enable container.googleapis.com sqladmin.googleapis.com compute.googleapis.com pubsub.googleapis.com appengine.googleapis.com

echo "Creating GCS Bucket..."
gsutil mb -l ${REGION} gs://${BUCKET_NAME}/

echo "Creating Pub/Sub..."
gcloud pubsub topics create ${Topic_NAME}
gcloud pubsub subscriptions create ${SUB_NAME} --topic=${Topic_NAME}

echo "Creating Cloud SQL Instance (PostgreSQL)..."
gcloud sql instances create ${SQL_INSTANCE} \
    --database-version=POSTGRES_14 \
    --tier=db-f1-micro \
    --region=${REGION} \
    --root-password=password123

echo "Creating Database..."
gcloud sql databases create ${DB_NAME} --instance=${SQL_INSTANCE}

echo "Creating GKE Autopilot Cluster..."
gcloud container clusters create-auto iot-cluster \
    --region=${REGION}

echo "Getting Cluster Credentials..."
gcloud container clusters get-credentials iot-cluster --region ${REGION}

echo "Creating Secrets for K8s..."
kubectl create secret generic db-secrets \
    --from-literal=username=postgres \
    --from-literal=password=password123

echo "Setup Complete! Next Steps:"
echo "1. Build and Push Docker images."
echo "2. Deploy App Engine API."
echo "3. Apply Kubernetes manifests."
echo "4. Create Compute Engine VM for analytics."
