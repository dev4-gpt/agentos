"""AgentOS Registry API Server.

FastAPI application implementing the full Agent Registry API as defined in the PRD,
including semantic tool search, OAuth2 auth flows, integrations catalog, schema endpoints,
and tool execution proxy.
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import secrets
import time
import uuid
from datetime import datetime
from typing import Any

import httpx
from fastapi import Body, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware

from agentos.models import (
    Agent,
    AgentListResponse,
    AgentLog,
    AgentStatus,
    AuthConfig,
    AuthType,
    Capability,
    ErrorCategory,
    HealthResponse,
    Integration,
    MCPPrompt,
    MCPResource,
    OAuthCallbackRequest,
    OAuthInitResponse,
    StoredToken,
    Tool,
    ToolExecutionRequest,
    ToolExecutionResponse,
    ToolRecord,
    ToolSearchResponse,
    ToolSearchResult,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")  # for semantic search embeddings
USE_EMBEDDINGS = bool(OPENAI_API_KEY)  # fallback to keyword if no OpenAI

# ---------------------------------------------------------------------------
# Helper: Simple embedding function via OpenAI
# ---------------------------------------------------------------------------


async def get_embedding(text: str) -> list[float]:
    """Get embedding vector for semantic search. Falls back to empty vector if no API key."""
    if not USE_EMBEDDINGS or not OPENAI_API_KEY:
        return []

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.post(
                "https://api.openai.com/v1/embeddings",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                json={"input": text, "model": "text-embedding-3-small"},
            )
            response.raise_for_status()
            data = response.json()
            return data["data"][0]["embedding"]
        except Exception:
            return []


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    if not a or not b or len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(x * x for x in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def keyword_search_score(query: str, tool: ToolRecord) -> float:
    """Fallback keyword-based scoring when embeddings unavailable."""
    query_lower = query.lower()
    score = 0.0
    if query_lower in tool.name.lower():
        score += 3.0
    if query_lower in tool.description.lower():
        score += 2.0
    for cat in tool.categories:
        if query_lower in cat.lower():
            score += 1.0
    for tag in tool.tags:
        if query_lower in tag.lower():
            score += 0.5
    return score


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

_start_time = time.time()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="AgentOS Registry API",
        description=(
            "The Machine-Readable Tool Layer for Autonomous AI Agents. "
            "Provides a centralized registry for agents, tools, integrations, and capabilities."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # In-memory stores (replace with DB in production)
    agents: dict[str, Agent] = {}
    logs: list[AgentLog] = []
    tools: dict[str, ToolRecord] = {}
    integrations: dict[str, Integration] = {}
    stored_tokens: dict[str, StoredToken] = {}
    oauth_states: dict[str, dict[str, Any]] = {}  # state -> {provider, scopes, ...}

    # MCP resources and prompts
    mcp_resources: list[MCPResource] = []
    mcp_prompts: list[MCPPrompt] = []

    # ----------------------------------------------------------------------- 
    # Health
    # -----------------------------------------------------------------------

    @app.get("/health", response_model=HealthResponse, tags=["system"])
    async def health() -> HealthResponse:
        """Return API health status."""
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            uptime_seconds=round(time.time() - _start_time, 2),
            tool_count=len(tools),
            agent_count=len(agents),
            integration_count=len(integrations),
        )

    # -----------------------------------------------------------------------
    # Agents
    # -----------------------------------------------------------------------

    @app.get("/agents", response_model=AgentListResponse, tags=["agents"])
    async def list_agents(
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
        status_filter: AgentStatus | None = Query(default=None, alias="status"),
    ) -> AgentListResponse:
        """List all registered agents with optional filtering."""
        all_agents = list(agents.values())
        if status_filter:
            all_agents = [a for a in all_agents if a.status == status_filter]
        total = len(all_agents)
        start = (page - 1) * page_size
        paginated = all_agents[start : start + page_size]
        return AgentListResponse(
            agents=paginated,
            total=total,
            page=page,
            page_size=page_size,
        )

    @app.post(
        "/agents",
        response_model=Agent,
        status_code=status.HTTP_201_CREATED,
        tags=["agents"],
    )
    async def register_agent(agent: Agent) -> Agent:
        """Register a new agent in the registry."""
        if not agent.id:
            agent.id = str(uuid.uuid4())
        if agent.id in agents:
            raise HTTPException(
                status_code=409,
                detail=f"Agent '{agent.id}' already exists",
            )
        agent.created_at = datetime.utcnow()
        agent.updated_at = datetime.utcnow()
        agents[agent.id] = agent
        logs.append(
            AgentLog(
                agent_id=agent.id,
                action="register",
                status="success",
                message=f"Agent '{agent.name}' registered",
            )
        )
        return agent

    @app.get("/agents/{agent_id}", response_model=Agent, tags=["agents"])
    async def get_agent(agent_id: str) -> Agent:
        """Retrieve a specific agent by ID."""
        if agent_id not in agents:
            raise HTTPException(
                status_code=404,
                detail=f"Agent '{agent_id}' not found",
            )
        return agents[agent_id]

    @app.put("/agents/{agent_id}", response_model=Agent, tags=["agents"])
    async def update_agent(agent_id: str, updates: Agent) -> Agent:
        """Update an existing agent."""
        if agent_id not in agents:
            raise HTTPException(
                status_code=404,
                detail=f"Agent '{agent_id}' not found",
            )
        existing = agents[agent_id]
        updated_data = updates.model_dump(exclude_unset=True)
        updated_data["updated_at"] = datetime.utcnow()
        updated = existing.model_copy(update=updated_data)
        agents[agent_id] = updated
        logs.append(
            AgentLog(
                agent_id=agent_id,
                action="update",
                status="success",
                message=f"Agent '{agent_id}' updated",
            )
        )
        return updated

    @app.delete(
        "/agents/{agent_id}",
        status_code=status.HTTP_204_NO_CONTENT,
        tags=["agents"],
    )
    async def deregister_agent(agent_id: str) -> None:
        """Remove an agent from the registry."""
        if agent_id not in agents:
            raise HTTPException(
                status_code=404,
                detail=f"Agent '{agent_id}' not found",
            )
        del agents[agent_id]
        logs.append(
            AgentLog(
                agent_id=agent_id,
                action="deregister",
                status="success",
                message=f"Agent '{agent_id}' removed",
            )
        )

    # -----------------------------------------------------------------------
    # Agent-scoped Tools
    # -----------------------------------------------------------------------

    @app.get(
        "/agents/{agent_id}/tools",
        response_model=list[Tool],
        tags=["tools"],
    )
    async def list_agent_tools(agent_id: str) -> list[Tool]:
        """List all tools for an agent."""
        if agent_id not in agents:
            raise HTTPException(
                status_code=404,
                detail=f"Agent '{agent_id}' not found",
            )
        return agents[agent_id].tools

    @app.post(
        "/agents/{agent_id}/tools",
        response_model=Tool,
        status_code=status.HTTP_201_CREATED,
        tags=["tools"],
    )
    async def register_agent_tool(agent_id: str, tool: Tool) -> Tool:
        """Register a new tool for an agent."""
        if agent_id not in agents:
            raise HTTPException(
                status_code=404,
                detail=f"Agent '{agent_id}' not found",
            )
        agent = agents[agent_id]
        if any(t.name == tool.name for t in agent.tools):
            raise HTTPException(
                status_code=409,
                detail=f"Tool '{tool.name}' already exists",
            )
        updated_tools = agent.tools + [tool]
        agents[agent_id].tools = updated_tools
        agents[agent_id].updated_at = datetime.utcnow()
        return tool

    @app.get(
        "/agents/{agent_id}/tools/{tool_name}",
        response_model=Tool,
        tags=["tools"],
    )
    async def get_agent_tool(agent_id: str, tool_name: str) -> Tool:
        """Get a specific tool by name."""
        if agent_id not in agents:
            raise HTTPException(
                status_code=404,
                detail=f"Agent '{agent_id}' not found",
            )
        for t in agents[agent_id].tools:
            if t.name == tool_name:
                return t
        raise HTTPException(
            status_code=404,
            detail=f"Tool '{tool_name}' not found",
        )

    # -----------------------------------------------------------------------
    # Capabilities
    # -----------------------------------------------------------------------

    @app.get(
        "/agents/{agent_id}/capabilities",
        response_model=list[Capability],
        tags=["capabilities"],
    )
    async def list_capabilities(agent_id: str) -> list[Capability]:
        """List all capabilities for an agent."""
        if agent_id not in agents:
            raise HTTPException(
                status_code=404,
                detail=f"Agent '{agent_id}' not found",
            )
        return agents[agent_id].capabilities

    # -----------------------------------------------------------------------
    # Logs
    # -----------------------------------------------------------------------

    @app.get("/agents/{agent_id}/logs", response_model=list[AgentLog], tags=["logs"])
    async def get_logs(agent_id: str) -> list[AgentLog]:
        """Get activity logs for an agent."""
        return [log for log in logs if log.agent_id == agent_id]

    # -----------------------------------------------------------------------
    # Global Tools registry
    # -----------------------------------------------------------------------

    @app.get("/tools", tags=["tools"])
    async def list_tools_global(
        category: str | None = Query(default=None),
        integration_id: str | None = Query(default=None),
        limit: int = Query(default=20, ge=1, le=100),
        offset: int = Query(default=0, ge=0),
    ) -> dict:
        """List all registered tools with optional filtering."""
        all_tools = list(tools.values())
        if category:
            all_tools = [t for t in all_tools if category in t.categories]
        if integration_id:
            all_tools = [t for t in all_tools if t.integration_id == integration_id]
        paginated = all_tools[offset : offset + limit]
        return {"tools": paginated, "total": len(all_tools)}

    @app.post("/tools", status_code=201, tags=["tools"])
    async def register_tool_global(tool: ToolRecord) -> ToolRecord:
        """Register a new tool in the global registry."""
        if not tool.id:
            tool.id = str(uuid.uuid4())
        tool.created_at = datetime.utcnow().isoformat() + "Z"
        tool.updated_at = tool.created_at

        # Generate embedding for semantic search
        if USE_EMBEDDINGS:
            search_text = f"{tool.name} {tool.description} {' '.join(tool.categories)} {' '.join(tool.tags)}"
            tool.embedding = await get_embedding(search_text)

        tools[tool.id] = tool
        return tool

    @app.get("/tools/{tool_id}", tags=["tools"])
    async def get_tool_global(tool_id: str) -> ToolRecord:
        """Get a tool by ID."""
        if tool_id not in tools:
            raise HTTPException(
                status_code=404,
                detail=f"Tool '{tool_id}' not found",
            )
        return tools[tool_id]

    @app.delete("/tools/{tool_id}", tags=["tools"])
    async def delete_tool_global(tool_id: str) -> dict:
        """Delete a tool by ID."""
        if tool_id not in tools:
            raise HTTPException(
                status_code=404,
                detail=f"Tool '{tool_id}' not found",
            )
        del tools[tool_id]
        return {"deleted": tool_id}

    # -----------------------------------------------------------------------
    # Semantic Tool Search (POST /tools/search)
    # -----------------------------------------------------------------------

    @app.post("/tools/search", response_model=ToolSearchResponse, tags=["tools"])
    async def search_tools(
        intent: str = Body(..., embed=True),
        limit: int = Body(default=10, ge=1, le=50, embed=True),
    ) -> ToolSearchResponse:
        """Semantic search for tools by natural language intent."""
        if not tools:
            return ToolSearchResponse(intent=intent, results=[], total=0)

        if USE_EMBEDDINGS:
            # Use vector similarity
            query_embedding = await get_embedding(intent)
            if not query_embedding:
                # Fallback to keyword
                return await _keyword_search(intent, limit)

            scores: list[tuple[str, float]] = []
            for tool_id, tool in tools.items():
                if tool.embedding:
                    score = cosine_similarity(query_embedding, tool.embedding)
                else:
                    score = keyword_search_score(intent, tool) / 10.0  # normalize
                scores.append((tool_id, score))

            scores.sort(key=lambda x: x[1], reverse=True)
            top_results = scores[:limit]

            results = [
                ToolSearchResult(
                    tool=tools[tool_id],
                    score=round(score, 4),
                    rank=idx + 1,
                )
                for idx, (tool_id, score) in enumerate(top_results)
                if score > 0
            ]
        else:
            # Fallback to keyword search
            results = await _keyword_search(intent, limit)

        return ToolSearchResponse(
            intent=intent,
            results=results,
            total=len(results),
        )

    async def _keyword_search(intent: str, limit: int) -> ToolSearchResponse:
        """Keyword-based fallback search."""
        scored: list[tuple[ToolRecord, float]] = []
        for tool in tools.values():
            score = keyword_search_score(intent, tool)
            if score > 0:
                scored.append((tool, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        top = scored[:limit]
        results = [
            ToolSearchResult(tool=t, score=round(s, 2), rank=idx + 1)
            for idx, (t, s) in enumerate(top)
        ]
        return ToolSearchResponse(intent=intent, results=results, total=len(results))

    # -----------------------------------------------------------------------
    # Integrations
    # -----------------------------------------------------------------------

    @app.get("/integrations", tags=["integrations"])
    async def list_integrations(
        category: str | None = Query(default=None),
    ) -> dict:
        """List all SaaS integrations."""
        all_integrations = list(integrations.values())
        if category:
            all_integrations = [
                i for i in all_integrations if category in i.categories
            ]
        return {"integrations": all_integrations, "total": len(all_integrations)}

    @app.post("/integrations", status_code=201, tags=["integrations"])
    async def register_integration(integration: Integration) -> Integration:
        """Register a new SaaS integration."""
        if not integration.id:
            integration.id = str(uuid.uuid4())
        integration.created_at = datetime.utcnow().isoformat() + "Z"
        integrations[integration.id] = integration
        return integration

    @app.get("/integrations/{integration_id}", tags=["integrations"])
    async def get_integration(integration_id: str) -> Integration:
        """Get a specific integration by ID."""
        if integration_id not in integrations:
            raise HTTPException(
                status_code=404,
                detail=f"Integration '{integration_id}' not found",
            )
        return integrations[integration_id]

    # -----------------------------------------------------------------------
    # Schemas
    # -----------------------------------------------------------------------

    @app.get("/schemas/tool", tags=["schemas"])
    async def get_tool_schema() -> dict:
        """Get canonical tool JSON Schema."""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "Tool",
            "type": "object",
            "required": ["name", "description"],
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "description": {"type": "string"},
                "input_schema": {"type": "object"},
                "output_schema": {"type": "object"},
                "endpoint": {"type": "string", "format": "uri"},
                "protocols": {"type": "array", "items": {"type": "string"}},
                "categories": {"type": "array", "items": {"type": "string"}},
                "tags": {"type": "array", "items": {"type": "string"}},
                "capabilities": {"type": "array", "items": {"type": "string"}},
                "authentication": {"type": "object"},
                "mcp_tool_name": {"type": "string"},
            },
        }

    @app.get("/schemas/registry", tags=["schemas"])
    async def get_registry_schema() -> dict:
        """Get registry JSON Schema."""
        return {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "title": "AgentOS Registry",
            "type": "object",
            "properties": {
                "agents": {"type": "array", "items": {"$ref": "#/definitions/Agent"}},
                "tools": {"type": "array", "items": {"$ref": "#/definitions/Tool"}},
                "integrations": {
                    "type": "array",
                    "items": {"$ref": "#/definitions/Integration"},
                },
            },
            "definitions": {
                "Agent": {"type": "object"},
                "Tool": {"type": "object"},
                "Integration": {"type": "object"},
            },
        }

    # -----------------------------------------------------------------------
    # OAuth2 / Auth
    # -----------------------------------------------------------------------

    @app.post("/auth/{provider}", response_model=OAuthInitResponse, tags=["auth"])
    async def initiate_oauth(provider: str, scopes: list[str] = Body(default_factory=list)) -> OAuthInitResponse:
        """Initiate OAuth2 flow for a provider."""
        # Look up integration for auth config
        integration = next(
            (i for i in integrations.values() if i.slug == provider), None
        )
        if not integration:
            raise HTTPException(
                status_code=404, detail=f"Provider '{provider}' not found"
            )

        if integration.auth.type != AuthType.OAUTH2:
            raise HTTPException(
                status_code=400, detail="Provider does not support OAuth2"
            )

        # Generate state token
        state = secrets.token_urlsafe(32)
        oauth_states[state] = {
            "provider": provider,
            "scopes": scopes or integration.auth.scopes,
            "created_at": datetime.utcnow().isoformat(),
        }

        # Build OAuth2 URL
        scope_str = "%20".join(scopes or integration.auth.scopes)
        auth_url = (
            f"{integration.auth.auth_url}"
            f"?client_id=YOUR_CLIENT_ID"
            f"&redirect_uri=YOUR_REDIRECT_URI"
            f"&state={state}"
            f"&scope={scope_str}"
            f"&response_type=code"
        )

        return OAuthInitResponse(
            provider=provider,
            auth_url=auth_url,
            state=state,
            scopes=scopes or integration.auth.scopes,
        )

    @app.post("/auth/callback", tags=["auth"])
    async def oauth_callback(request: OAuthCallbackRequest) -> dict:
        """Handle OAuth2 callback and exchange code for token."""
        if request.state not in oauth_states:
            raise HTTPException(status_code=400, detail="Invalid state")

        state_data = oauth_states.pop(request.state)
        provider = state_data["provider"]

        # In production: exchange code for token via provider's token_url
        # For now, store a mock token
        token_id = str(uuid.uuid4())
        stored_tokens[token_id] = StoredToken(
            id=token_id,
            provider=provider,
            auth_type=AuthType.OAUTH2,
            access_token=f"mock_access_token_{request.code}",
            refresh_token=f"mock_refresh_token",
            scopes=state_data["scopes"],
        )

        return {"token_id": token_id, "provider": provider, "success": True}

    @app.get("/auth/tokens", tags=["auth"])
    async def list_tokens() -> dict:
        """List all stored OAuth tokens."""
        return {"tokens": list(stored_tokens.values())}

    @app.delete("/auth/tokens/{token_id}", tags=["auth"])
    async def revoke_token(token_id: str) -> dict:
        """Revoke a stored token."""
        if token_id not in stored_tokens:
            raise HTTPException(status_code=404, detail="Token not found")
        del stored_tokens[token_id]
        return {"revoked": token_id}

    # -----------------------------------------------------------------------
    # Tool Execution Proxy
    # -----------------------------------------------------------------------

    @app.post(
        "/tools/execute",
        response_model=ToolExecutionResponse,
        tags=["tools"],
    )
    async def execute_tool(request: ToolExecutionRequest) -> ToolExecutionResponse:
        """Execute a tool via the registry proxy."""
        if request.tool_id not in tools:
            return ToolExecutionResponse(
                success=False,
                tool_id=request.tool_id,
                error="Tool not found",
                error_category=ErrorCategory.TOOL_UNAVAILABLE,
            )

        tool = tools[request.tool_id]
        start = time.time()

        # Check if tool requires auth
        if tool.authentication and tool.authentication.type != AuthType.NONE:
            if not request.token_id or request.token_id not in stored_tokens:
                return ToolExecutionResponse(
                    success=False,
                    tool_id=request.tool_id,
                    error="Authentication required but no valid token provided",
                    error_category=ErrorCategory.AUTH_EXPIRED,
                )

            token = stored_tokens[request.token_id]
            # In production: use token.access_token for Authorization header
            auth_header = f"Bearer {token.access_token}"
        else:
            auth_header = None

        # Execute the tool by proxying to its endpoint
        if not tool.endpoint:
            return ToolExecutionResponse(
                success=False,
                tool_id=request.tool_id,
                error="Tool has no endpoint configured",
                error_category=ErrorCategory.TOOL_UNAVAILABLE,
            )

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                headers = {}
                if auth_header:
                    headers["Authorization"] = auth_header
                response = await client.post(
                    tool.endpoint,
                    json=request.arguments,
                    headers=headers,
                )
                response.raise_for_status()
                result = response.json()

            latency = round((time.time() - start) * 1000, 2)
            return ToolExecutionResponse(
                success=True,
                tool_id=request.tool_id,
                result=result,
                latency_ms=latency,
            )
        except httpx.HTTPStatusError as e:
            return ToolExecutionResponse(
                success=False,
                tool_id=request.tool_id,
                error=f"HTTP {e.response.status_code}: {e.response.text}",
                error_category=ErrorCategory.TOOL_UNAVAILABLE,
            )
        except Exception as e:
            return ToolExecutionResponse(
                success=False,
                tool_id=request.tool_id,
                error=str(e),
                error_category=ErrorCategory.TOOL_UNAVAILABLE,
            )

    # -----------------------------------------------------------------------
    # MCP endpoints
    # -----------------------------------------------------------------------

    @app.post("/mcp/initialize", tags=["mcp"])
    async def mcp_initialize(payload: dict) -> dict:
        """MCP initialize handshake."""
        return {
            "protocolVersion": payload.get("protocolVersion", "2024-11-05"),
            "capabilities": {
                "tools": {"listChanged": True},
                "resources": {"subscribe": False, "listChanged": False},
                "prompts": {"listChanged": False},
            },
            748 "agentos-registry", "version": "1.0.0"},
        }

    @app.get("/mcp/tools/list", tags=["mcp"])
    async def mcp_list_tools() -> dict:
        """MCP tools/list - return tools in MCP format."""
        mcp_tools = [
            {
                "name": t.mcp_tool_name or t.name.replace("-", "_"),
                "description": t.description,
                "inputSchema": t.input_schema or {},
            }
            for t in tools.values()
        ]
        return {"tools": mcp_tools}

    @app.post("/mcp/tools/call", tags=["mcp"])
    async def mcp_call_tool(payload: dict) -> dict:
        """MCP tools/call - route a tool invocation via execution proxy."""
        tool_name = payload.get("name")
        arguments = payload.get("arguments", {})

        # Find tool by MCP name or regular name
        tool = next(
            (
                t
                for t in tools.values()
                if t.mcp_tool_name == tool_name or t.name == tool_name
            ),
            None,
        )
        if tool is None:
            return {
                "content": [
                    {"type": "text", "text": f"Tool '{tool_name}' not found"}
                ],
                "isError": True,
            }

        # Execute tool via proxy
        exec_req = ToolExecutionRequest(
            tool_id=tool.id or "",
            arguments=arguments,
        )
        exec_result = await execute_tool(exec_req)

        if exec_result.success:
            return {
                "content": [
                    {"type": "text", "text": json.dumps(exec_result.result, indent=2)}
                ],
                "isError": False,
            }
        else:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: {exec_result.error} (category: {exec_result.error_category})",
                    }
                ],
                "isError": True,
            }

    @app.get("/mcp/resources/list", tags=["mcp"])
    async def mcp_list_resources() -> dict:
        """MCP resources/list - return documentation and schemas."""
        return {"resources": [r.model_dump() for r in mcp_resources]}

    @app.post("/mcp/resources/read", tags=["mcp"])
    async def mcp_read_resource(payload: dict) -> dict:
        """MCP resources/read - return resource content."""
        uri = payload.get("uri")
        resource = next((r for r in mcp_resources if r.uri == uri), None)
        if not resource:
            return {"content": "", "mimeType": "text/plain"}
        return {"content": resource.content or "", "mimeType": resource.mimeType}

    @app.get("/mcp/prompts/list", tags=["mcp"])
    async def mcp_list_prompts() -> dict:
        """MCP prompts/list - return pre-built prompt templates."""
        return {"prompts": [p.model_dump() for p in mcp_prompts]}

    @app.get("/mcp/agents/list", tags=["mcp"])
    async def mcp_list_agents() -> dict:
        """MCP agents/list - return agents in MCP format."""
        return {"agents": [a.model_dump() for a in agents.values()]}

    return app


# ---------------------------------------------------------------------------
# Application instance (used by uvicorn)
# ---------------------------------------------------------------------------

app = create_app()
