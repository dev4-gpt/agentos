"""AgentOS Registry API Server.

FastAPI application implementing the Agent Registry API as defined in
api/spec.yaml. Provides CRUD operations for agents, tools, and capabilities.
"""

from __future__ import annotations

import time
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from agentos.models import (
    Agent,
    AgentListResponse,
    AgentLog,
    
    AgentStatus,
    Capability,
    HealthResponse,
    Tool,
)


# ---------------------------------------------------------------------------
# Lightweight Pydantic model for standalone tool registration
# ---------------------------------------------------------------------------

class ToolRecord(BaseModel):
    """Standalone tool registration record (global /tools endpoints)."""

    id: Optional[str] = None
    name: str
    description: str
    input_schema: Optional[Dict[str, Any]] = None
    endpoint: Optional[str] = None
    protocols: Optional[List[str]] = None
    created_at: Optional[str] = None


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
            "Provides a centralised registry for agents, tools, and capabilities."
        ),
        version="0.1.0",
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
    agents: Dict[str, Agent] = {}
    logs: List[AgentLog] = []
    tools: Dict[str, ToolRecord] = {}

    # -----------------------------------------------------------------------
    # Health
    # -----------------------------------------------------------------------

    @app.get("/health", response_model=HealthResponse, tags=["system"])
    async def health() -> HealthResponse:
        """Return API health status."""
        return HealthResponse(
            status="healthy",
            version="0.1.0",
            uptime_seconds=round(time.time() - _start_time, 2),
        )

    # -----------------------------------------------------------------------
    # Agents
    # -----------------------------------------------------------------------

    @app.get("/agents", response_model=AgentListResponse, tags=["agents"])
    async def list_agents(
        page: int = Query(default=1, ge=1),
        page_size: int = Query(default=20, ge=1, le=100),
        status: Optional[AgentStatus] = None,
    ) -> AgentListResponse:
        """List all registered agents with optional filtering."""
        all_agents = list(agents.values())
        if status:
            all_agents = [a for a in all_agents if a.status == status]
        total = len(all_agents)
        start = (page - 1) * page_size
        paginated = all_agents[start : start + page_size]
        return AgentListResponse(agents=paginated, total=total, page=page, page_size=page_size)

    @app.post("/agents", response_model=Agent, status_code=status.HTTP_201_CREATED, tags=["agents"])
    async def register_agent(agent: Agent) -> Agent:
        """Register a new agent in the registry."""
        if not agent.id:
            agent = agent.model_copy(update={"id": str(uuid.uuid4())})
        if agent.id in agents:
            raise HTTPException(status_code=409, detail=f"Agent '{agent.id}' already exists")
        agent = agent.model_copy(update={"created_at": datetime.utcnow(), "updated_at": datetime.utcnow()})
        agents[agent.id] = agent
        logs.append(AgentLog(agent_id=agent.id, action="register", status="success", message=f"Agent '{agent.name}' registered"))
        return agent

    @app.get("/agents/{agent_id}", response_model=Agent, tags=["agents"])
    async def get_agent(agent_id: str) -> Agent:
        """Retrieve a specific agent by ID."""
        if agent_id not in agents:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
        return agents[agent_id]

    @app.put("/agents/{agent_id}", response_model=Agent, tags=["agents"])
    async def update_agent(agent_id: str, updates: Agent) -> Agent:
        """Update an existing agent."""
        if agent_id not in agents:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
        existing = agents[agent_id]
        updated_data = updates.model_dump(exclude_unset=True)
        updated_data["updated_at"] = datetime.utcnow()
        updated = existing.model_copy(update=updated_data)
        agents[agent_id] = updated
        logs.append(AgentLog(agent_id=agent_id, action="update", status="success", message=f"Agent '{agent_id}' updated"))
        return updated

    @app.delete("/agents/{agent_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["agents"])
    async def deregister_agent(agent_id: str) -> None:
        """Remove an agent from the registry."""
        if agent_id not in agents:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
        del agents[agent_id]
        logs.append(AgentLog(agent_id=agent_id, action="deregister", status="success", message=f"Agent '{agent_id}' removed"))

    # -----------------------------------------------------------------------
    # Tools
    # -----------------------------------------------------------------------

    @app.get("/agents/{agent_id}/tools", response_model=List[Tool], tags=["tools"])
    async def list_tools(agent_id: str) -> List[Tool]:
        """List all tools for an agent."""
        if agent_id not in agents:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
        return agents[agent_id].tools

    @app.post("/agents/{agent_id}/tools", response_model=Tool, status_code=status.HTTP_201_CREATED, tags=["tools"])
    async def register_tool(agent_id: str, tool: Tool) -> Tool:
        """Register a new tool for an agent."""
        if agent_id not in agents:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
        agent = agents[agent_id]
        if any(t.name == tool.name for t in agent.tools):
            raise HTTPException(status_code=409, detail=f"Tool '{tool.name}' already exists")
        updated_tools = agent.tools + [tool]
        agents[agent_id] = agent.model_copy(update={"tools": updated_tools, "updated_at": datetime.utcnow()})
        return tool

    @app.get("/agents/{agent_id}/tools/{tool_name}", response_model=Tool, tags=["tools"])
    async def get_tool(agent_id: str, tool_name: str) -> Tool:
        """Get a specific tool by name."""
        if agent_id not in agents:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
        for t in agents[agent_id].tools:
            if t.name == tool_name:
                return t
        raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")

    # -----------------------------------------------------------------------
    # Capabilities
    # -----------------------------------------------------------------------

    @app.get("/agents/{agent_id}/capabilities", response_model=List[Capability], tags=["capabilities"])
    async def list_capabilities(agent_id: str) -> List[Capability]:
        """List all capabilities for an agent."""
        if agent_id not in agents:
            raise HTTPException(status_code=404, detail=f"Agent '{agent_id}' not found")
        return agents[agent_id].capabilities

    # -----------------------------------------------------------------------
    # Logs
    # -----------------------------------------------------------------------

    @app.get("/agents/{agent_id}/logs", response_model=List[AgentLog], tags=["logs"])
    async def get_logs(agent_id: str) -> List[AgentLog]:
        """Get activity logs for an agent."""
        return [l for l in logs if l.agent_id == agent_id]

    # -----------------------------------------------------------------------
    # Global Tools registry (standalone, not agent-scoped)
    # -----------------------------------------------------------------------

    @app.get("/tools", tags=["tools"])
    async def list_tools_global():
        """List all registered tools."""
        return {"tools": list(tools.values())}

    @app.post("/tools", status_code=201, tags=["tools"])
    async def register_tool_global(tool: ToolRecord):
        """Register a new tool."""
        if not tool.id:
            tool.id = str(uuid.uuid4())
        tool.created_at = datetime.utcnow().isoformat() + "Z"
        tools[tool.id] = tool
        return tool

    @app.get("/tools/{tool_id}", tags=["tools"])
    async def get_tool_global(tool_id: str):
        """Get a tool by ID."""
        if tool_id not in tools:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_id}' not found")
        return tools[tool_id]

    @app.delete("/tools/{tool_id}", tags=["tools"])
    async def delete_tool_global(tool_id: str):
        """Delete a tool by ID."""
        if tool_id not in tools:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_id}' not found")
        del tools[tool_id]
        return {"deleted": tool_id}

    # -----------------------------------------------------------------------
    # MCP (Model Context Protocol) endpoints
    # -----------------------------------------------------------------------

    @app.post("/mcp/initialize", tags=["mcp"])
    async def mcp_initialize(payload: dict):
        """MCP initialize handshake."""
        return {
            "protocolVersion": payload.get("protocolVersion", "2024-11-05"),
            "capabilities": {"tools": {"listChanged": True}, "agents": {}},
            "serverInfo": {"name": "agentos-registry", "version": "1.0.0"},
        }

    @app.get("/mcp/tools/list", tags=["mcp"])
    async def mcp_list_tools():
        """MCP tools/list - return tools in MCP format."""
        mcp_tools = [
            {
                "name": t.name,
                "description": t.description,
                "inputSchema": t.input_schema if hasattr(t, "input_schema") else {},
            }
            for t in tools.values()
        ]
        return {"tools": mcp_tools}

    @app.post("/mcp/tools/call", tags=["mcp"])
    async def mcp_call_tool(payload: dict):
        """MCP tools/call - route a tool invocation."""
        tool_name = payload.get("name")
        arguments = payload.get("arguments", {})
        tool = next((t for t in tools.values() if t.name == tool_name), None)
        if tool is None:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
        return {
            "content": [{"type": "text", "text": f"Tool '{tool_name}' invoked with {arguments}"}],
            "isError": False,
        }

    @app.get("/mcp/agents/list", tags=["mcp"])
    async def mcp_list_agents():
        """MCP agents/list - return agents in MCP format."""
        return {"agents": list(agents.values())}

    return app




# ---------------------------------------------------------------------------
# Application instance (used by uvicorn)
# ---------------------------------------------------------------------------

app = create_app()
