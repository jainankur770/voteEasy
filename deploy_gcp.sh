#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

echo "🚀 Welcome to the VoteEasy GCP Deployment Script!"
echo "This script will deploy your full-stack application to Google Cloud Run."
echo "------------------------------------------------------------------"

# 1. Gather User Variables
read -p "Enter your Google Cloud Project ID: " PROJECT_ID
read -p "Enter your desired GCP Region (e.g., us-central1): " REGION
read -p "Enter your Gemini API Key: " GEMINI_API_KEY

# Set the GCP Project
echo "\nSetting active project to $PROJECT_ID..."
gcloud config set project $PROJECT_ID

# 2. Enable necessary APIs
echo "\nEnabling required GCP APIs (Cloud Run, Cloud Build, Secret Manager)..."
gcloud services enable run.googleapis.com cloudbuild.googleapis.com secretmanager.googleapis.com

# 3. Create Secret in Secret Manager
echo "\nSetting up Gemini API Key in Secret Manager..."
# Check if secret already exists to avoid errors
if gcloud secrets describe GEMINI_API_KEY --project="$PROJECT_ID" >/dev/null 2>&1; then
    echo "Secret GEMINI_API_KEY already exists. Adding new version..."
    echo -n "$GEMINI_API_KEY" | gcloud secrets versions add GEMINI_API_KEY --data-file=-
else
    echo "Creating new secret GEMINI_API_KEY..."
    echo -n "$GEMINI_API_KEY" | gcloud secrets create GEMINI_API_KEY --replication-policy="automatic" --data-file=-
fi

# 3.5 Grant Secret Access to Cloud Run Default Service Account
echo "\nGranting Secret Manager access to Cloud Run default service account..."
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
SERVICE_ACCOUNT="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
gcloud secrets add-iam-policy-binding GEMINI_API_KEY \
    --member="serviceAccount:${SERVICE_ACCOUNT}" \
    --role="roles/secretmanager.secretAccessor" \
    --project="$PROJECT_ID"

# 4. Build and Submit via Cloud Build
echo "\nBuilding Docker Image via Google Cloud Build..."
IMAGE_URI="gcr.io/$PROJECT_ID/voteeasy-app"
gcloud builds submit --tag $IMAGE_URI .

# 5. Deploy to Cloud Run
echo "\nDeploying to Google Cloud Run..."
gcloud run deploy voteeasy-app \
  --image $IMAGE_URI \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-secrets=GEMINI_API_KEY=GEMINI_API_KEY:latest \
  --memory 1Gi \
  --cpu 1 \
  --port 8080

echo "------------------------------------------------------------------"
echo "✅ Deployment Complete!"
echo "Your application is now live and serverless on Google Cloud."
