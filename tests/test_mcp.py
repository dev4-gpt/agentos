"""Tests for the MCP (Model Context Protocol) server endpoints."""

from __future__ import annotations
from fastapi.testclient import TestClient


class TestMCPEndpoints:
    """Tests for MCP protocol endpoints on the registry server."""

    def test_mcp_tools_list(self, client: TestClient) -> None:
        """MCP tools/list should return registered tools in MCP format."""
        # First register a tool
        payload = {
            "name": "mcp-search",
            "description": "Search tool exposed via MCP",
            "input_schema": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "Search query"}},
                "required": ["query"],
            },
            "endpoint": "http://localhost:9001",
            "protocols": ["mcp"],
        }
        client.post("/tools", json=payload)

        response = client.get("/mcp/tools/list")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        tool_names = [t["name"] for t in data["tools"]]
        assert "mcp-search" in tool_names

    def test_mcp_tool_call(self, client: TestClient) -> None:
        """MCP tools/call should route a tool invocation."""
        # Register a tool first
        payload = {
            "name": "echo-tool",
            "description": "Echoes input back",
            "input_schema": {
                "type": "object",
                "properties": {"message": {"type": "string"}},
                "required": ["message"],
            },
            "endpoint": "http://localhost:9001",
            "protocols": ["mcp"],
        }
        client.post("/tools", json=payload)
        call_payload = {
            "name": "echo-tool",
            "arguments": {"message": "hello world"},
        }
        response = client.post("/mcp/tools/call", json=call_payload)
        # Should return 200 or a proxy error - not 404/405
        assert response.status_code != 404
        assert response.status_code != 405

    def test_mcp_agents_list(self, client: TestClient) -> None:
        """MCP agents/list should return registered agents."""
        # Register an agent
        payload = {
            "name": "mcp-agent",
            "version": "1.0.0",
            "description": "Agent exposed via MCP",
            "capabilities": ["search"],
            "tools": [],
            "endpoint": "http://localhost:9002",
            "protocols": ["mcp"],
        }
        client.post("/agents", json=payload)
        response = client.get("/mcp/agents/list")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data

    def test_mcp_initialize(self, client: TestClient) -> None:
        """MCP initialize handshake should return server capabilities."""
        payload = {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0.0"},
        }
        response = client.post("/mcp/initialize", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert "protocolVersion" in data
        assert "capabilities" in data
        assert "serverInfo" in data
