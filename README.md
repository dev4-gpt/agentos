# AgentOS: The Machine-Readable Tool Layer for Autonomous AI Agents

**AgentOS** is a complete infrastructure platform that bridges autonomous AI agents with human-centric SaaS applications. It provides semantic tool discovery, OAuth2 authentication flows, and a plug-and-play Model Context Protocol (MCP) server for Claude, GPT, LangChain, and other agent frameworks.

## 🎯 What Problem Does AgentOS Solve?

As AI agents become more capable, they need standardized ways to:

- **Discover tools semantically** — "Send a Slack message" → finds `slack-send-message` tool
- **Authenticate autonomously** — Handle OAuth2/API-key flows without human copy-paste
- **Execute reliably** — Proxy tool calls with proper auth, error handling, and retries
- **Integrate universally** — Work with Claude Desktop, custom agents, and any MCP-compatible client

AgentOS solves all of this.

---

## ✨ Features (100% PRD-Complete)

###  **Semantic Tool Search**
- `POST /tools/search` with OpenAI embeddings or keyword fallback
- Natural language intent matching: _"create a GitHub issue"_ → ranks tools by relevance
- Cosine similarity scoring for vector search

### **SaaS Integrations Catalog**
- 5 production integrations: **Slack, Stripe, GitHub, Notion, Linear**
- 15+ tool definitions with full JSON schemas
- OAuth2 configs, API key flows, and onboarding documentation

### **OAuth2 & Auth Management**
- `POST /auth/{provider}` to initiate OAuth2 flows
- `POST /auth/callback` for token exchange
- Secure token storage with expiry tracking
- Support for API-key, Bearer, OAuth2, and Basic auth

### **Tool Execution Proxy**
- `POST /tools/execute` routes tool calls to real SaaS APIs
- Automatic auth header injection from stored tokens
- Structured error responses (`AUTH_EXPIRED`, `RATE_LIMITED`, `SCHEMA_MISMATCH`)
- Latency tracking and retry logic

### **Model Context Protocol (MCP) Server**
- Full MCP spec compliance (2024-11-05)
- `initialize`, `tools/list`, `tools/call`, `resources/list`, `prompts/list`
- Stdio JSON-RPC server for local Claude Desktop integration
- HTTP endpoints for remote agent access

### **Registry API**
- Agent CRUD: register, list, update, deregister agents
- Tool CRUD: global and agent-scoped tools
- Capabilities tracking: `idempotent`, `rate_limited`, `paginated`, `async_supported`
- Audit logs for all agent actions

### **Schema Endpoints**
- `GET /schemas/tool` — Canonical tool JSON Schema
- `GET /schemas/registry` — Full registry schema

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- (Optional) OpenAI API key for semantic search embeddings

### Installation

```bash
# Clone the repo
git clone https://github.com/dev4-gpt/agentos.git
cd agentos

# Install with uv (recommended) or pip
uv pip install -e ".[dev]"

# Or with pip
pip install -e ".[dev]"
```

### Running the Registry Server

```bash
# Start the FastAPI server
uvicorn agentos.registry.server:app --reload --port 8000

# Server runs at http://localhost:8000
# API docs: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

### Seeding Real Tool Data

The registry starts empty. To populate it with Slack, Stripe, GitHub, Notion, and Linear tools:

```python
import asyncio
from agentos.registry.seed_data import INTEGRATIONS, TOOLS
from agentos.sdk import AgentOSClient

async def seed():
    async with AgentOSClient() as client:
        # Register integrations
        for integration in INTEGRATIONS:
            await client.register_integration(integration.model_dump())
        
        # Register tools
        for tool in TOOLS:
            await client.register_tool(tool.model_dump())
        
        print(f"Seeded {len(INTEGRATIONS)} integrations and {len(TOOLS)} tools")

asyncio.run(seed())
```

### Testing Semantic Search

```bash
# With embeddings (requires OPENAI_API_KEY env var)
export OPENAI_API_KEY=sk-...
curl -X POST http://localhost:8000/tools/search \
  -H "Content-Type: application/json" \
  -d '{"intent": "send a message in Slack", "limit": 3}'

# Without embeddings (keyword fallback)
curl -X POST http://localhost:8000/tools/search \
  -H "Content-Type: application/json" \
  -d '{"intent": "create GitHub issue", "limit": 3}'
```

### Running the MCP Server (Claude Desktop)

Add to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "agentos": {
      "command": "python",
      "args": ["-m", "agentos.cli.main", "mcp-serve"],
      "env": {
        "AGENTOS_REGISTRY_URL": "http://localhost:8000"
      }
    }
  }
}
```

Restart Claude Desktop. All tools from the registry will appear in Claude's tool palette.

---

## 📚 Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  AI Agents (Claude, GPT, LangChain, CrewAI, etc.)          │
└──────────────────┬──────────────────────────────────────────┘
                   │ MCP Protocol (stdio / HTTP)
                   ▼
┌─────────────────────────────────────────────────────────────┐
│            AgentOS MCP Server (mcp/server.py)               │
│  • tools/list  • tools/call  • resources  • prompts         │
└──────────────────┬──────────────────────────────────────────┘
                   │ REST API calls
                   ▼
┌─────────────────────────────────────────────────────────────┐
│         AgentOS Registry API (registry/server.py)           │
│  • Semantic Search  • Auth Flows  • Tool Execution Proxy    │
│  • Integrations Catalog  • Agent CRUD  • Audit Logs         │
└──────────────────┬──────────────────────────────────────────┘
                   │ HTTP POST w/ auth headers
                   ▼
┌─────────────────────────────────────────────────────────────┐
│  Real SaaS APIs (Slack, Stripe, GitHub, Notion, Linear)     │
└─────────────────────────────────────────────────────────────┘
```

### Key Components

- **`src/agentos/registry/server.py`** — FastAPI backend (842 lines)
- **`src/agentos/mcp/server.py`** — MCP stdio bridge
- **`src/agentos/models/__init__.py`** — Pydantic schemas for all entities
- **`src/agentos/registry/seed_data.py`** — Production tool catalog
- **`src/agentos/sdk/client.py`** — Python SDK for registry interaction
- **`src/agentos/cli/main.py`** — Typer-based CLI

---

## 🔧 CLI Usage

```bash
# Check health
agentos health

# List all tools
agentos list-tools

# Register a new agent
agentos register-agent --name "my-agent" --description "My custom agent"

# List all integrations
curl http://localhost:8000/integrations | jq

# Initiate OAuth2 for Slack
curl -X POST http://localhost:8000/auth/slack \
  -H "Content-Type: application/json" \
  -d '{"scopes": ["chat:write", "channels:read"]}'

# Execute a tool (requires stored token)
curl -X POST http://localhost:8000/tools/execute \
  -H "Content-Type: application/json" \
  -d '{
    "tool_id": "slack-send-message",
    "arguments": {"channel": "#general", "text": "Hello from AgentOS!"},
    "token_id": "<your_token_id>"
  }'
```

---

## 🧪 Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=agentos --cov-report=html

# Lint
ruff check src/ tests/
ruff format src/ tests/

# Type check
mypy src/agentos
```

---

## 📖 API Reference

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check with uptime + tool/agent/integration counts |
| `/agents` | GET, POST | List/register agents |
| `/agents/{id}` | GET, PUT, DELETE | Get/update/delete agent |
| `/tools` | GET, POST | List/register global tools |
| `/tools/{id}` | GET, DELETE | Get/delete tool |
| `/tools/search` | POST | **Semantic search** by intent |
| `/tools/execute` | POST | **Proxy tool execution** to SaaS API |
| `/integrations` | GET, POST | List/register SaaS integrations |
| `/auth/{provider}` | POST | Initiate OAuth2 flow |
| `/auth/callback` | POST | Handle OAuth2 callback |
| `/auth/tokens` | GET | List stored tokens |
| `/schemas/tool` | GET | Canonical tool JSON Schema |
| `/schemas/registry` | GET | Full registry schema |

### MCP Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/mcp/initialize` | POST | MCP handshake |
| `/mcp/tools/list` | GET | List tools in MCP format |
| `/mcp/tools/call` | POST | Route tool call via execution proxy |
| `/mcp/resources/list` | GET | List documentation resources |
| `/mcp/prompts/list` | GET | List pre-built prompt templates |
| `/mcp/agents/list` | GET | List agents in MCP format |

---

## 🛠️ Development

### Project Structure

```
agentos/
├── src/agentos/
│   ├── models/__init__.py        # Pydantic schemas (all entities)
│   ├── registry/
│   │   ├── server.py             # FastAPI backend (842 lines)
│   │   └── seed_data.py          # Real SaaS tool catalog
│   ├── mcp/server.py             # MCP stdio server
│   ├── sdk/client.py             # Python SDK
│   └── cli/main.py               # Typer CLI
├── tests/
│   ├── test_registry.py
│   ├── test_mcp.py
│   └── test_tools.py
├── api/spec.yaml                 # OpenAPI 3.0 spec
├── PRD.md                        # Product Requirements Document
├── Dockerfile
├── docker-compose.yml
└── pyproject.toml
```

### Adding a New Integration

1. Add to `seed_data.py` `INTEGRATIONS` list:

```python
Integration(
    id="twilio-integration",
    name="Twilio",
    slug="twilio",
    description="SMS and voice communication platform",
    base_url="https://api.twilio.com",
    auth=AuthConfig(type=AuthType.API_KEY, ...),
    categories=["communication", "sms"],
)
```

2. Add tool definitions to `TOOLS` list:

```python
ToolRecord(
    id="twilio-send-sms",
    name="twilio-send-sms",
    description="Send an SMS via Twilio",
    input_schema={...},
    endpoint="https://api.twilio.com/2010-04-01/Accounts/{AccountSid}/Messages.json",
    integration_id="twilio-integration",
    authentication=AuthConfig(type=AuthType.API_KEY),
)
```

3. Restart server and reseed data.

---

## 🎓 Example Use Cases

### Autonomous Slack Bot

```python
import asyncio
from agentos.sdk import AgentOSClient

async def send_slack_message(channel: str, message: str):
    async with AgentOSClient() as client:
        # Search for Slack send tool
        results = await client.mcp_list_tools()
        slack_tool = next(t for t in results if "slack" in t["name"])
        
        # Execute tool
        response = await client.mcp_call_tool(
            name=slack_tool["name"],
            arguments={"channel": channel, "text": message}
        )
        return response

asyncio.run(send_slack_message("#general", "Hello from AgentOS!"))
```

### Multi-Tool Agent Workflow

```python
# Agent discovers tools by intent
search_result = await client.search_tools(intent="create a customer in billing system")
top_tool = search_result["results"][0]["tool"]  # stripe-create-customer

# Execute discovered tool
exec_result = await client.execute_tool({
    "tool_id": top_tool["id"],
    "arguments": {"email": "user@example.com", "name": "John Doe"},
    "token_id": stored_stripe_token_id
})

if exec_result["success"]:
    customer_id = exec_result["result"]["id"]
    # Continue workflow...
```

---

## 🚧 Roadmap

- [ ] **Persistent Storage** — SQLite/Postgres backend (currently in-memory)
- [ ] **Browser Automation Fallback** — Playwright layer for tools without APIs
- [ ] **Token Refresh Logic** — Auto-refresh OAuth2 tokens before expiry
- [ ] **Rate Limiting** — Per-tool rate limit enforcement
- [ ] **Multi-tenant Support** — Isolate agents and tools by organization
- [ ] **Agent Marketplace** — Public registry of community-contributed tools
- [ ] **Observability** — OpenTelemetry tracing for tool execution chains

---

## 📜 License

MIT License - see [LICENSE](LICENSE)

---

## 🙏 Contributing

Contributions welcome! To add a new integration:

1. Fork the repo
2. Add integration and tools to `seed_data.py`
3. Write tests in `tests/test_tools.py`
4. Submit PR with examples

For major features, open an issue first to discuss.

---

## 🔗 Links

- **PRD**: [PRD.md](PRD.md)
- **API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **MCP Spec**: [modelcontextprotocol.io](https://modelcontextprotocol.io/)
- **Y Combinator RFS**: [Agent Tooling Infrastructure](https://www.ycombinator.com/rfs#agent-tooling)

---

**Built with ❤️ for the AI agent ecosystem** | [GitHub](https://github.com/dev4-gpt/agentos) | Star ⭐ if useful!
