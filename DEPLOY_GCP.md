# AgentOS → GCP Deployment Guide

**Deploy the entire AgentOS platform to Google Cloud for FREE using the always-free tier + your $300 credits.**

---

## 🎯 What You Get with GCP Free Tier

### Always-Free (Never Expires)

| Service | Free Quota | AgentOS Use Case |
|---------|------------|------------------|
| **Cloud Run** | 2M requests/month, 240K vCPU-seconds | Main registry API server |
| **Firestore** | 1GB storage, 50K reads/day, 20K writes/day | Tool registry, agents, tokens |
| **Cloud Functions** | 2M invocations/month | OAuth2 callbacks, webhooks |
| **Secret Manager** | 6 active secrets free | Store OpenAI API key, OAuth client secrets |
| **Cloud Scheduler** | 3 jobs free | Token refresh cron (every hour) |
| **Cloud Storage** | 5GB regional storage | Tool schemas, MCP resource docs |
| **BigQuery** | 10GB storage + 1TB queries/month | Analytics on tool usage |
| **Cloud Logging** | 50GB/month | Request logs, errors |
| **Cloud Trace** | First 10GB free | Observability for tool execution |

### $300 Trial Credits (90 Days)

Use for:
- **Cloud SQL (Postgres)** — If you prefer SQL over Firestore ($~8/month for smallest instance)
- **Memorystore (Redis)** — For rate limiting cache ($~5/month)
- **Cloud Run with more memory** — If you need >512MB for embedding generation

**You won't be charged after the $300 runs out unless you manually upgrade.**

---

## 🏗️ Architecture on GCP

```
┌─────────────────────────────────────────────────────────────┐
│  AI Agents (Claude Desktop, LangChain, etc.)                │
└────────────────┬────────────────────────────────────────────┘
                 │ HTTPS / stdio
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  Cloud Run: AgentOS Registry API                            │
│  • FastAPI on port 8080                                     │
│  • Semantic search with OpenAI embeddings                   │
│  • OAuth2 flows, tool execution proxy                       │
│  • Auto-scales 0→1000 instances                             │
└────────────────┬────────────────────────────────────────────┘
                 │ Read/Write
                 ▼
┌─────────────────────────────────────────────────────────────┐
│  Firestore (NoSQL Database)                                 │
│  Collections:                                               │
│  • agents/        • integrations/                           │
│  • tools/         • stored_tokens/                          │
│  • logs/          • oauth_states/                           │
└─────────────────────────────────────────────────────────────┘
                 ┌───────────────────┐
                 │  Secret Manager    │
                 │  • OPENAI_API_KEY  │
                 │  • OAuth secrets   │
                 └───────────────────┘
                 ┌───────────────────┐
                 │ Cloud Scheduler    │
                 │ Token Refresh Cron │
                 └───────────────────┘
```

---

## 📋 Prerequisites

1. **GCP Account with $300 Credits**  
   Sign up at [cloud.google.com/free](https://cloud.google.com/free)

2. **gcloud CLI**  
   ```bash
   # Install gcloud
   curl https://sdk.cloud.google.com | bash
   exec -l $SHELL
   gcloud init
   ```

3. **Enable Required APIs**  
   ```bash
   gcloud services enable run.googleapis.com \
     firestore.googleapis.com \
     secretmanager.googleapis.com \
     cloudscheduler.googleapis.com \
     cloudbuild.googleapis.com
   ```

---

## 🚀 Step-by-Step Deployment

### 1. Set Up GCP Project

```bash
# Set project ID
export PROJECT_ID="agentos-prod"
gcloud config set project $PROJECT_ID

# Set default region
export REGION="us-central1"
gcloud config set run/region $REGION
```

### 2. Initialize Firestore

```bash
# Create Firestore database (Native mode)
gcloud firestore databases create --region=$REGION

# Firestore is now available at:
# https://console.cloud.google.com/firestore/databases
```

### 3. Store Secrets

```bash
# Store OpenAI API key
echo -n "sk-your-openai-key" | gcloud secrets create OPENAI_API_KEY --data-file=-

# Grant Cloud Run access to secrets
gcloud secrets add-iam-policy-binding OPENAI_API_KEY \
  --member="serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

### 4. Update Code for Firestore

Create `src/agentos/storage/firestore.py`:

```python
"""Firestore storage backend for AgentOS."""
import os
from google.cloud import firestore

db = firestore.Client()

class FirestoreBackend:
    def __init__(self):
        self.agents = db.collection('agents')
        self.tools = db.collection('tools')
        self.integrations = db.collection('integrations')
        self.tokens = db.collection('stored_tokens')
        self.logs = db.collection('logs')
    
    async def get_tool(self, tool_id: str):
        doc = self.tools.document(tool_id).get()
        return doc.to_dict() if doc.exists else None
    
    async def list_tools(self):
        return [doc.to_dict() for doc in self.tools.stream()]
    
    async def create_tool(self, tool_id: str, data: dict):
        self.tools.document(tool_id).set(data)
        return data
    
    # ... implement other CRUD methods
```

Update `src/agentos/registry/server.py` to use Firestore:

```python
from agentos.storage.firestore import FirestoreBackend

def create_app() -> FastAPI:
    app = FastAPI(...)
    
    # Replace in-memory dicts with Firestore
    storage = FirestoreBackend()
    
    @app.get("/tools")
    async def list_tools_global(...):
        all_tools = await storage.list_tools()
        # ... rest of logic
```

### 5. Create Dockerfile for Cloud Run

Update `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Cloud Run expects port 8080
ENV PORT=8080

# Run the server
CMD uvicorn agentos.registry.server:app --host 0.0.0.0 --port $PORT
```

### 6. Deploy to Cloud Run

```bash
# Build and deploy
gcloud run deploy agentos-registry \
  --source . \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --set-secrets=OPENAI_API_KEY=OPENAI_API_KEY:latest \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --min-instances 0

# Get the deployed URL
export AGENTOS_URL=$(gcloud run services describe agentos-registry \
  --region $REGION --format 'value(status.url)')

echo "AgentOS deployed at: $AGENTOS_URL"
```

### 7. Seed the Registry

```bash
# Run seeding script against deployed URL
python -c "
import asyncio
import os
from agentos.registry.seed_data import INTEGRATIONS, TOOLS
from agentos.sdk import AgentOSClient

async def seed():
    async with AgentOSClient(base_url=os.environ['AGENTOS_URL']) as client:
        for integration in INTEGRATIONS:
            await client.register_integration(integration.model_dump())
        for tool in TOOLS:
            await client.register_tool(tool.model_dump())
        print(f'Seeded {len(INTEGRATIONS)} integrations and {len(TOOLS)} tools')

asyncio.run(seed())
"
```

### 8. Set Up Token Refresh Cron

```bash
# Create Cloud Function for token refresh
gcloud functions deploy refresh-oauth-tokens \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point refresh_tokens \
  --set-env-vars AGENTOS_URL=$AGENTOS_URL

# Schedule it to run every hour
gcloud scheduler jobs create http refresh-tokens-hourly \
  --schedule "0 * * * *" \
  --uri "$(gcloud functions describe refresh-oauth-tokens --format='value(httpsTrigger.url)')" \
  --http-method POST
```

Create `functions/token_refresh/main.py`:

```python
import functions_framework
import httpx
import os

@functions_framework.http
def refresh_tokens(request):
    """Refresh expired OAuth tokens."""
    agentos_url = os.environ['AGENTOS_URL']
    
    # Get all tokens that are about to expire
    response = httpx.get(f"{agentos_url}/auth/tokens")
    tokens = response.json()["tokens"]
    
    refreshed_count = 0
    for token in tokens:
        if needs_refresh(token):
            # Call provider's token refresh endpoint
            # ... refresh logic here
            refreshed_count += 1
    
    return {"refreshed": refreshed_count}

def needs_refresh(token):
    # Check if token expires in < 1 hour
    from datetime import datetime, timedelta
    if not token.get("expires_at"):
        return False
    expires = datetime.fromisoformat(token["expires_at"])
    return expires < datetime.utcnow() + timedelta(hours=1)
```

---

## 🔒 Security Best Practices

### 1. Enable Authentication (Optional)

For production, restrict access:

```bash
# Deploy with authentication required
gcloud run deploy agentos-registry \
  --source . \
  --platform managed \
  --region $REGION \
  --no-allow-unauthenticated  # Require auth

# Create service account for clients
gcloud iam service-accounts create agentos-client

# Grant invoke permission
gcloud run services add-iam-policy-binding agentos-registry \
  --member="serviceAccount:agentos-client@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/run.invoker"
```

### 2. Set Up Firestore Security Rules

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Only allow authenticated Cloud Run requests
    match /tools/{toolId} {
      allow read: if request.auth != null;
      allow write: if request.auth.token.email.matches('.*@appspot.gserviceaccount.com');
    }
    
    match /stored_tokens/{tokenId} {
      // Tokens are sensitive - extra protection
      allow read, write: if request.auth.token.email.matches('.*@appspot.gserviceaccount.com');
    }
  }
}
```

Apply rules:

```bash
gcloud firestore indexes create --collection-group=tools
```

---

## 📊 Monitoring & Observability

### 1. View Logs

```bash
# Stream logs in real-time
gcloud run services logs tail agentos-registry --region $REGION

# View in Cloud Console
# https://console.cloud.google.com/run/detail/$REGION/agentos-registry/logs
```

### 2. Set Up Alerts

```bash
# Create alert for error rate > 5%
gcloud alpha monitoring policies create \
  --notification-channels=YOUR_CHANNEL_ID \
  --display-name="AgentOS Error Rate" \
  --condition-display-name="Error rate > 5%" \
  --condition-threshold-value=0.05 \
  --condition-threshold-duration=300s
```

### 3. Add Cloud Trace

Install OpenTelemetry:

```bash
pip install opentelemetry-exporter-gcp-trace
```

Update `server.py`:

```python
from opentelemetry import trace
from opentelemetry.exporter.cloud_trace import CloudTraceSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

tracer_provider = TracerProvider()
trace.set_tracer_provider(tracer_provider)
tracer_provider.add_span_processor(
    BatchSpanProcessor(CloudTraceSpanExporter())
)

tracer = trace.get_tracer(__name__)

@app.post("/tools/execute")
async def execute_tool(request: ToolExecutionRequest):
    with tracer.start_as_current_span("execute_tool"):
        # ... tool execution logic
```

---

## 💰 Cost Breakdown (After Free Tier)

If you exceed free tier (unlikely for MVP):

| Service | Free Tier | Overage Cost | Expected MVP Cost |
|---------|-----------|--------------|-------------------|
| Cloud Run | 2M requests/month | $0.40 per M requests | **$0** (under 2M) |
| Firestore | 50K reads/day | $0.06 per 100K reads | **$0** (under quota) |
| Cloud Functions | 2M invokes/month | $0.40 per M invokes | **$0** |
| Secret Manager | 6 secrets free | $0.06 per secret/month | **$0** (< 6 secrets) |
| Cloud Scheduler | 3 jobs free | $0.10 per job/month | **$0** (only 1 job) |
| **TOTAL** | | | **$0/month** |

---

## 🔥 Performance Optimizations

### 1. Enable Firestore Caching

```python
from google.cloud.firestore_v1 import Client

db = Client()
db._cache_enabled = True  # Enable client-side cache
```

### 2. Use Cloud CDN for Static Assets

```bash
# If serving MCP resource docs as static files
gcloud compute backend-buckets create agentos-static \
  --gcs-bucket-name=${PROJECT_ID}-static

gcloud compute url-maps create agentos-cdn \
  --default-backend-bucket=agentos-static
```

### 3. Optimize Embedding Generation

Cache embeddings in Firestore to avoid re-computing:

```python
async def get_embedding_cached(text: str) -> list[float]:
    # Check cache first
    cache_key = hashlib.sha256(text.encode()).hexdigest()
    cached = await db.collection('embeddings').document(cache_key).get()
    
    if cached.exists:
        return cached.to_dict()['vector']
    
    # Generate new embedding
    vector = await get_embedding(text)
    
    # Store in cache
    await db.collection('embeddings').document(cache_key).set({
        'text': text,
        'vector': vector,
        'created_at': datetime.utcnow()
    })
    
    return vector
```

---

## 🧪 Testing the Deployment

```bash
# Test health endpoint
curl $AGENTOS_URL/health

# Test semantic search
curl -X POST $AGENTOS_URL/tools/search \
  -H "Content-Type: application/json" \
  -d '{"intent": "send a Slack message", "limit": 3}'

# Test MCP endpoint
curl $AGENTOS_URL/mcp/tools/list

# Load test with Apache Bench
ab -n 1000 -c 10 $AGENTOS_URL/health
```

---

## 🚨 Troubleshooting

### Issue: "Permission Denied" on Firestore

```bash
# Grant Cloud Run service account Firestore access
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_ID}@appspot.gserviceaccount.com" \
  --role="roles/datastore.user"
```

### Issue: Cold Starts Taking > 5 Seconds

```bash
# Set minimum instances to 1 to keep warm
gcloud run services update agentos-registry \
  --min-instances 1 \
  --region $REGION

# Note: This uses ~$5/month but eliminates cold starts
```

### Issue: Out of Memory

```bash
# Increase memory allocation
gcloud run services update agentos-registry \
  --memory 1Gi \
  --region $REGION
```

---

## 🎓 Next Steps

1. **Custom Domain**  
   ```bash
   gcloud run domain-mappings create \
     --service agentos-registry \
     --domain api.yourdomain.com \
     --region $REGION
   ```

2. **Add Browser Automation**  
   Deploy separate Cloud Run service with Playwright + Chromium

3. **Set Up CI/CD**  
   Use Cloud Build to auto-deploy on git push:
   
   ```yaml
   # cloudbuild.yaml
   steps:
   - name: 'gcr.io/cloud-builders/gcloud'
     args:
     - 'run'
     - 'deploy'
     - 'agentos-registry'
     - '--source=.'
     - '--region=$_REGION'
   ```

4. **Enable CORS for Web Clients**  
   Already configured in FastAPI middleware!

---

## 📚 Resources

- [Cloud Run Pricing](https://cloud.google.com/run/pricing)
- [Firestore Free Quota](https://cloud.google.com/firestore/quotas)
- [Secret Manager Pricing](https://cloud.google.com/secret-manager/pricing)
- [Cloud Scheduler Free Tier](https://cloud.google.com/scheduler/pricing)
- [GCP Always Free](https://cloud.google.com/free/docs/free-cloud-features#free-tier-usage-limits)

---

**Total Setup Time: ~30 minutes | Total Cost: $0/month for MVP** 🎉
