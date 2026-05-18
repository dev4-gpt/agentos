"""AgentOS Python SDK Client."""

from __future__ import annotations

import asyncio
from typing import Any, Dict, List, Optional

import httpx

from ..models import Agent, AgentListResponse, HealthResponse, Tool


class AgentOSClient:
    """Async HTTP client for the AgentOS Registry API."""

    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=timeout)

    async def __aenter__(self) -> "AgentOSClient":
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def close(self) -> None:
        await self._client.aclose()

    # ---- Health ----

    async def health(self) -> HealthResponse:
        resp = await self._client.get("/health")
        resp.raise_for_status()
        return HealthResponse(**resp.json())

    # ---- Agents ----

    async def list_agents(self, status: Optional[str] = None) -> AgentListResponse:
        params: Dict[str, Any] = {}
        if status:
            params["status"] = status
        resp = await self._client.get("/agents", params=params)
        resp.raise_for_status()
        return AgentListResponse(**resp.json())

    async def register_agent(self, agent: Agent) -> Agent:
        resp = await self._client.post("/agents", json=agent.model_dump())
        resp.raise_for_status()
        return Agent(**resp.json())

    async def get_agent_async(self, agent_id: str) -> Agent:
        resp = await self._client.get(f"/agents/{agent_id}")
        resp.raise_for_status()
        return Agent(**resp.json())

    async def update_agent(self, agent_id: str, updates: Dict[str, Any]) -> Agent:
        resp = await self._client.put(f"/agents/{agent_id}", json=updates)
        resp.raise_for_status()
        return Agent(**resp.json())

    async def delete_agent(self, agent_id: str) -> bool:
        resp = await self._client.delete(f"/agents/{agent_id}")
        resp.raise_for_status()
        return resp.json().get("success", False)

    async def heartbeat(self, agent_id: str) -> Agent:
        resp = await self._client.post(f"/agents/{agent_id}/heartbeat")
        resp.raise_for_status()
        return Agent(**resp.json())

    # ---- Tools ----

    async def list_tools(self, agent_id: Optional[str] = None) -> List[Tool]:
        params: Dict[str, Any] = {}
        if agent_id:
            params["agent_id"] = agent_id
        resp = await self._client.get("/tools", params=params)
        resp.raise_for_status()
        return [Tool(**t) for t in resp.json().get("tools", [])]

    async def register_tool(self, tool: Tool) -> Tool:
        resp = await self._client.post("/tools", json=tool.model_dump())
        resp.raise_for_status()
        return Tool(**resp.json())

    async def get_tool(self, tool_id: str) -> Tool:
        resp = await self._client.get(f"/tools/{tool_id}")
        resp.raise_for_status()
        return Tool(**resp.json())

    async def execute_tool(self, tool_id: str, agent_id: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        payload = {"agent_id": agent_id, "arguments": arguments}
        resp = await self._client.post(f"/tools/{tool_id}/execute", json=payload)
        resp.raise_for_status()
        return resp.json()

    # ---- Capabilities ----

    async def discover_capabilities(self, query: Optional[str] = None) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {}
        if query:
            params["query"] = query
        resp = await self._client.get("/capabilities", params=params)
        resp.raise_for_status()
        return resp.json().get("capabilities", [])


def create_client(base_url: str = "http://localhost:8000") -> AgentOSClient:
    """Create an AgentOS client instance."""
    return AgentOSClient(base_url=base_url)
