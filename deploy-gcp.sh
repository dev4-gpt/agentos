#!/bin/bash
# AgentOS GCP Deployment Script
# This automates the deployment process from DEPLOY_GCP.md

set -e  # Exit on error

echo "🚀 AgentOS GCP Deployment Script"
echo "================================="

# Configuration
export PROJECT_ID="agentos-mvp"
export REGION="us-central1"

echo "📋 Step 1: Setting up GCP project..."
gcloud config set project $PROJECT_ID

echo "📋 Step 2: Enabling required APIs..."
gcloud services enable \
  run.googleapis.com \
  firestore.googleapis.com \
  secretmanager.googleapis.com \
  cloudscheduler.googleapis.com \
  cloudbuild.googleapis.com

echo "✅ APIs enabled!"

echo "📋 Step 3: Initializing Firestore..."
gcloud firestore databases create --region=$REGION || echo "Firestore already exists"

echo "✅ Firestore initialized!"

echo ""
echo "⚠️  MANUAL STEPS REQUIRED:"
echo "1. Store your OpenAI API key:"
echo "   echo -n 'your-api-key' | gcloud secrets create OPENAI_API_KEY --data-file=-"
echo ""
echo "2. Grant Cloud Run access to secrets:"
echo "   gcloud projects add-iam-policy-binding $PROJECT_ID \\"
echo "     --member=serviceAccount:$PROJECT_ID@appspot.gserviceaccount.com \\"
echo "     --role=roles/secretmanager.secretAccessor"
echo ""
echo "3. Deploy to Cloud Run:"
echo "   gcloud run deploy agentos-registry \\"
echo "     --source=. \\"
echo "     --region=$REGION \\"
echo "     --allow-unauthenticated \\"
echo "     --set-secrets=OPENAI_API_KEY=OPENAI_API_KEY:latest"
echo ""
echo "📚 See DEPLOY_GCP.md for complete instructions"
