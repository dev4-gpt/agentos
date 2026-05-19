"""AgentOS Python SDK Client. Provides a synchronous and asynchronous interface to the AgentOS Registry API."""

from __future__ import annotations
from typing import Any, dict, list, Optional
import httpx


class AgentOSClient:
    """Async HTTP client for the AgentOS Registry API.

    Usage (async)::

        async with AgentOSClient() as client:
            health = await client.health()

    Usage (sync via httpx)::

        client = AgentOSClient()
        health = client.health_sync()
    """

    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: float = 30.0,
        api_key: Optional[str] = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self._timeout = timeout
        headers: dict[str, str] = {}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
            headers=headers,
        )
        self._sync_client = httpx.Client(
            base_url=self.base_url,
            timeout=timeout,
            headers=headers,
        )

    async def __aenter__(self) -> "AgentOSClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def close(self) -> None:
        await self._client.aclose()
        self._sync_client.close()

    # ------------------------------------------------------------------
    # Health
    # ------------------------------------------------------------------
    async def health(self) -> dict[str, Any]:
        """Return API health status."""
        resp = await self._client.get("/health")
        resp.raise_for_status()
        return resp.json()

    def health_sync(self) -> dict[str, Any]:
        resp = self._sync_client.get("/health")
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # Agents
    # ------------------------------------------------------------------
    async def list_agents(
        self,
        page: int = 1,
        page_size: int = 20,
        status: Optional[str] = None,
    ) -> dict[str, Any]:
        """List all registered agents."""
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if status:
            params["status"] = status
        resp = await self._client.get("/agents", params=params)
        resp.raise_for_status()
        return resp.json()

    async def register_agent(self, agent: dict[str, Any]) -> dict[str, Any]:
        """Register a new agent."""
        resp = await self._client.post("/agents", json=agent)
        resp.raise_for_status()
        return resp.json()

    async def get_agent(self, agent_id: str) -> dict[str, Any]:
        """Get an agent by ID."""
        resp = await self._client.get(f"/agents/{agent_id}")
        resp.raise_for_status()
        return resp.json()

    async def update_agent(self, agent_id: str, updates: dict[str, Any]) -> dict[str, Any]:
        """Update an existing agent."""
        resp = await self._client.put(f"/agents/{agent_id}", json=updates)
        resp.raise_for_status()
        return resp.json()

    async def deregister_agent(self, agent_id: str) -> None:
        """Remove an agent from the registry."""
        resp = await self._client.delete(f"/agents/{agent_id}")
        resp.raise_for_status()

    # ------------------------------------------------------------------
    # Agent-scoped Tools
    # ------------------------------------------------------------------
    async def list_agent_tools(self, agent_id: str) -> list[dict[str, Any]]:
        """List tools for a specific agent."""
        resp = await self._client.get(f"/agents/{agent_id}/tools")
        resp.raise_for_status()
        return resp.json()

    async def register_agent_tool(
        self,
        agent_id: str,
        tool: dict[str, Any],
    ) -> dict[str, Any]:
        """Register a tool for a specific agent."""
        resp = await self._client.post(f"/agents/{agent_id}/tools", json=tool)
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # Global Tools
    # ------------------------------------------------------------------
    async def list_tools(self) -> list[dict[str, Any]]:
        """List all globally registered tools."""
        resp = await self._client.get("/tools")
        resp.raise_for_status()
        return resp.json().get("tools", [])

    async def register_tool(self, tool: dict[str, Any]) -> dict[str, Any]:
        """Register a global tool."""
        resp = await self._client.post("/tools", json=tool)
        resp.raise_for_status()
        return resp.json()

    async def get_tool(self, tool_id: str) -> dict[str, Any]:
        """Get a global tool by ID."""
        resp = await self._client.get(f"/tools/{tool_id}")
        resp.raise_for_status()
        return resp.json()

    async def delete_tool(self, tool_id: str) -> dict[str, Any]:
        """Delete a global tool by ID."""
        resp = await self._client.delete(f"/tools/{tool_id}")
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # MCP endpoints
    # ------------------------------------------------------------------
    async def mcp_initialize(
        self,
        protocol_version: str = "2024-11-05",
    ) -> dict[str, Any]:
        """Send MCP initialize handshake."""
        resp = await self._client.post(
            "/mcp/initialize",
            json={"protocolVersion": protocol_version},
        )
        resp.raise_for_status()
        return resp.json()

    async def mcp_list_tools(self) -> list[dict[str, Any]]:
        """Retrieve tools in MCP format."""
        resp = await self._client.get("/mcp/tools/list")
        resp.raise_for_status()
        return resp.json().get("tools", [])

    async def mcp_call_tool(
        self,
        name: str,
        arguments: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Invoke a tool via MCP."""
        resp = await self._client.post(
            "/mcp/tools/call",
            json={"name": name, "arguments": arguments or {}},
        )
        resp.raise_for_status()
        return resp.json()

    async def mcp_list_agents(self) -> list[dict[str, Any]]:
        """Retrieve agents in MCP format."""
        resp = await self._client.get("/mcp/agents/list")
        resp.raise_for_status()
        return resp.json().get("agents", [])
