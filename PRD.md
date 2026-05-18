# AgentOS: The Machine-Readable Tool Layer
## Product Requirements Document

---

# Executive Summary

AgentOS is the machine-readable tool layer that bridges the gap between autonomous AI agents and human-centric SaaS applications. As AI agents proliferate, they lack a standardized, semantic way to discover, authenticate with, and interact with the APIs of everyday SaaS tools. AgentOS solves this by providing:

- **Universal Registry**: Machine-readable tool descriptions for every major SaaS platform
- **Semantic API Wrappers**: Convert REST/GraphQL APIs into natural-language-understandable tool definitions
- **MCP Server Layer**: Plug-and-play integration with all major LLM agents via Model Context Protocol
- **Autonomous Onboarding**: Agents can self-configure within SaaS applications without human intervention

This directly addresses Y Combinator's RFS focus area: agent tooling and the infrastructure needed for agents to interact reliably with human software.

---

# Target Persona

## Primary: AI Agent System Builders
- Engineering teams at AI companies building autonomous agents (e.g., Cognition, Adept, LangChain teams)
- Developer tool teams building agent orchestration frameworks
- Enterprise AI teams deploying multi-agent workflows
- **Technical capability**: Advanced (TypeScript/Python, API development, LLM integration)
- **Pain point**: Agents fail at 60-80% of SaaS interactions due to non-standard APIs, ambiguous authentication, and missing semantic tool definitions
- **Current workaround**: Hand-coded browser automation (Playwright/Selenium) or brittle custom API integrations

## Secondary: SaaS Platform Teams
- Product/Engineering teams at SaaS companies who want their platform to be agent-accessible
- **Technical capability**: Advanced (API design, developer experience, OpenAPI/Swagger)
- **Pain point**: No standard way to publish machine-readable API capabilities for agent consumption; building ad-hoc MCP servers is fragmented and requires deep LLM knowledge
- **Desired outcome**: One integration -> visible to all agent frameworks

## Tertiary: Enterprise IT / Automation Teams
- Technical operations teams deploying autonomous agents for internal workflows (Salesforce + Slack + Jira + Zoom pipelines)
- **Pain point**: Cannot reliably chain agent actions across multiple SaaS tools without brittle custom integrations
- **Desired outcome**: Declarative workflow definitions that agents can execute across tool boundaries

---

# Core Technical Specifications

## 1. Machine-Readable Tool Schema

Every tool is described using an extended JSON Schema that captures:

```json
{
  "tool_id": "stripe-create-customer",
  "name": "Create Customer",
  "description": "Creates a new customer in Stripe billing",
  "input_schema": { ...JSON Schema... },
  "output_schema": { ...JSON Schema... },
  "authentication": {
    "type": "oauth2 | api_key | bearer",
    "scopes": ["read", "write:customers"],
    "onboarding_flow": "guidable_steps"
  },
  "capabilities": ["idempotent", "rate_limited", "async_supported"],
  "mcp_tool_name": "stripe_create_customer",
  "categories": ["billing", "payments"]
}
```

## 2. MCP Server Protocol

AgentOS implements the [Anthropic Model Context Protocol](https://modelcontextprotocol.io/) specification:

- **Tools**: Each SaaS tool is exposed as an MCP tool with `name`, `description`, and `inputSchema`
- **Resources**: API documentation, schema references, and auth guides exposed as MCP resources
- **Prompts**: Pre-built prompt templates for common agent tasks per integration
- **Sampling**: Optional sampling support for agent-to-agent delegation

## 3. Agent Registry API

REST API at `registry.agentos.io`:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/v1/tools` | GET | List all registered tools |
| `/v1/tools/:id` | GET | Get full tool definition |
| `/v1/tools/search` | POST | Semantic search for tools |
| `/v1/integrations` | GET | List SaaS integrations |
| `/v1/auth/:provider` | POST | Initiate OAuth flow |
| `/v1/schemas/tool` | GET | Get canonical tool JSON Schema |
| `/v1/schemas/registry` | GET | Get registry schema |

## 4. Supported Authentication Flows

| Flow | SaaS Examples | Agent Complexity |
|------|--------------|-----------------|
| API Key | Stripe, SendGrid, Twilio | Low - paste token |
| OAuth2 | Google, Slack, GitHub, Notion | Medium - redirect flow |
| OAuth2 + Scopes | Linear, Jira, Asana | Medium-High - scope negotiation |
| Service Auth | Salesforce, HubSpot | High - enterprise SSO/SCIM |
| Browser Session | Tools without APIs | Very High - Playwright fallback |

---

# Autonomous Onboarding & Discovery Architecture

## Phase 1: Tool Discovery

When an agent needs to accomplish a task (e.g., "send a Slack message"), it:

1. **Queries the Registry**: POST `/v1/tools/search` with `{ intent: "send a message in slack" }`
2. **Receives Ranked Results**: Tools ranked by semantic relevance + auth complexity
3. **Selects Tool**: Chooses `slack-send-message` tool with `auth.type = "oauth2"`

## Phase 2: Authentication Handshake

1. Agent reads `onboarding_flow` from tool definition
2. For OAuth2: redirects user to consent screen (or uses stored token if admin config)
3. Token stored securely, scoped to minimum necessary permissions
4. Token refresh handled automatically via AgentOS proxy

## Phase 3: Tool Execution

1. Agent invokes tool via MCP `tools/call` with structured arguments
2. AgentOS validates input against `input_schema`
3. Request proxied to SaaS API with proper auth headers
4. Response validated against `output_schema`
5. Structured response returned to agent

## Phase 4: Error Recovery

AgentOS provides structured error categories:

| Error | Agent Action |
|-------|-------------|
| `AUTH_EXPIRED` | Re-initiate auth flow |
| `RATE_LIMITED` | Backoff and retry |
| `SCHEMA_MISMATCH` | Retry with corrected params |
| `TOOL_UNAVAILABLE` | Fall back to browser automation |
| `AMBIGUOUS_INTENT` | Request clarification from user |

## Fallback: Browser Automation Layer

For SaaS tools without APIs, AgentOS maintains Playwright scripts that:

- Navigate to specific SaaS UI paths
- Use DOM selectors to find and interact with elements
- Extract structured data from rendered pages
- Return results in the same schema format as API-based tools

---

# Success Metrics & KPIs

## Product Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| SaaS integrations launched | 50 in 6 months | Count of tools in registry |
| Tool call success rate | >95% | Ratio of successful tool executions |
| Auth setup completion rate | >80% | Users who complete OAuth flows |
| Mean time to integration | <1 week per SaaS | From API review to published tool |
| Agent frameworks supported | 5 (Claude, GPT, LangChain, LlamaIndex, CrewAI) | # of compatible frameworks |

## Technical Metrics

| Metric | Target |
|--------|--------|
| Tool discovery latency | <100ms p95 |
| Tool execution latency (API) | <2s p95 |
| Tool execution latency (browser) | <30s p95 |
| Registry uptime | 99.9% |
| Schema validation pass rate | >99% |

## Adoption Metrics

| Metric | 3-Month Target | 12-Month Target |
|--------|---------------|-----------------|
| Active agents connecting | 100 | 5,000 |
| Tool calls/week | 10,000 | 1M |
| SaaS vendors publishing | 5 | 50 |
| Open-source GitHub stars | 500 | 5,000 |
| Enterprise pilots | 3 | 20 |

## Monetization Metrics (Future)

| Metric | Target |
|--------|--------|
| Free tier: public tools access | Unlimited |
| Pro tier: private tools, SSO | $49/agent/month |
| Enterprise: SLA, dedicated support | Custom |
| Vendor tier: publish your API | $499/month |
