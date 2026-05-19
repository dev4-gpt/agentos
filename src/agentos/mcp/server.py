"""AgentOS MCP Server.

Implements a Model Context Protocol (MCP) server that bridges the AgentOS
Registry API with MCP-compatible AI clients (Claude, etc.).
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List

import httpx

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Registry HTTP client (thin wrapper around the REST API)
# ---------------------------------------------------------------------------


class RegistryClient:
    """Thin async HTTP client for the AgentOS Registry API."""

    def __init__(self, base_url: str = "http://localhost:8000") -> None:
        self.base_url = base_url.rstrip("/")

    async def list_tools(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/tools")
            resp.raise_for_status()
            return resp.json().get("tools", [])

    async def get_tool(self, tool_id: str) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/tools/{tool_id}")
            resp.raise_for_status()
            return resp.json()

    async def list_agents(self) -> List[Dict[str, Any]]:
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{self.base_url}/agents")
            resp.raise_for_status()
            return resp.json().get("agents", [])

# ---------------------------------------------------------------------------
# MCP handler functions (used by registry /mcp/* endpoints AND standalone)
# ---------------------------------------------------------------------------


def build_mcp_tool_entry(tool: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a ToolRecord dict to MCP tool format."""
    return {
        "name": tool.get("name", ""),
        "description": tool.get("description", ""),
        "inputSchema": tool.get("input_schema")
        or {"type": "object", "properties": {}, "required": []},
    }


def mcp_initialize_response(protocol_version: str = "2024-11-05") -> Dict[str, Any]:
    """Return a standard MCP initialize response payload."""
    return {
        "protocolVersion": protocol_version,
        "capabilities": {"tools": {"listChanged": True}, "agents": {}},
        "serverInfo": {"name": "agentos-registry", "version": "1.0.0"},
    }


def mcp_tool_call_response(
    tool_name: str, arguments: Dict[str, Any]
) -> Dict[str, Any]:
    """Build a minimal MCP tool call response."""
    return {
        "content": [
            {
                "type": "text",
                "text": f"Tool '{tool_name}' invoked with arguments: {arguments}",
            }
        ],
        "isError": False,
    }

# ---------------------------------------------------------------------------
# Standalone async runner (stdio-based MCP server via httpx bridge)
# ---------------------------------------------------------------------------


async def run_stdio_server(registry_url: str = "http://localhost:8000") -> None:
    """Run a simple line-delimited JSON MCP server over stdio.
    Each line of stdin is a JSON-RPC 2.0 request; responses are written to
    stdout. This is the minimal transport required by the MCP spec for
    local tool use with Claude Desktop.
    """
    registry = RegistryClient(base_url=registry_url)
    logger.info("AgentOS MCP stdio server started (registry=%s)", registry_url)
    for raw_line in sys.stdin:
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            request = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {exc}"},
            }
            print(json.dumps(response), flush=True)
            continue

        req_id = request.get("id")
        method = request.get("method", "")
        params = request.get("params", {})
        try:
            if method == "initialize":
                result = mcp_initialize_response(
                    params.get("protocolVersion", "2024-11-05")
                )
            elif method == "tools/list":
                raw_tools = await registry.list_tools()
                result = {"tools": [build_mcp_tool_entry(t) for t in raw_tools]}
            elif method == "tools/call":
                tool_name = params.get("name", "")
                arguments = params.get("arguments", {})
                result = mcp_tool_call_response(tool_name, arguments)
            elif method == "agents/list":
                agents = await registry.list_agents()
                result = {"agents": agents}
            else:
                raise ValueError(f"Unknown method: {method}")
            response = {"jsonrpc": "2.0", "id": req_id, "result": result}
        except Exception as exc:  # noqa: BLE001
            logger.exception("Error handling method %s", method)
            response = {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32603, "message": str(exc)},
            }
        print(json.dumps(response), flush=True)


def main() -> None:
    """Entry point for the AgentOS MCP stdio server."""
    registry_url = os.environ.get(
        "AGENTOS_REGISTRY_URL", "http://localhost:8000"
    )
    asyncio.run(run_stdio_server(registry_url=registry_url))


if __name__ == "__main__":
    main()
