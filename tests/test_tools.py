"""Tests for the Tools API endpoints."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


class TestTools:
    def test_list_tools_empty(self, client: TestClient) -> None:
        response = client.get("/tools")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert isinstance(data["tools"], list)

    def test_register_tool(self, client: TestClient) -> None:
        payload = {
            "name": "test-tool",
            "description": "A test tool",
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"}
                },
                "required": ["query"],
            },
            "endpoint": "http://localhost:9001",
            "protocols": ["http"],
        }
        response = client.post("/tools", json=payload)
        assert response.status_code in (200, 201)
        data = response.json()
        assert "id" in data
        assert data["name"] == "test-tool"

    def test_get_tool(self, client: TestClient) -> None:
        payload = {
            "name": "get-tool",
            "description": "Tool for get test",
            "input_schema": {"type": "object", "properties": {}},
            "endpoint": "http://localhost:9001",
            "protocols": ["http"],
        }
        create_resp = client.post("/tools", json=payload)
        tool_id = create_resp.json()["id"]

        get_resp = client.get(f"/tools/{tool_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == tool_id

    def test_get_tool_not_found(self, client: TestClient) -> None:
        response = client.get("/tools/nonexistent-id")
        assert response.status_code == 404

    def test_delete_tool(self, client: TestClient) -> None:
        payload = {
            "name": "delete-tool",
            "description": "Tool for delete test",
            "input_schema": {"type": "object", "properties": {}},
            "endpoint": "http://localhost:9001",
            "protocols": ["http"],
        }
        create_resp = client.post("/tools", json=payload)
        tool_id = create_resp.json()["id"]

        delete_resp = client.delete(f"/tools/{tool_id}")
        assert delete_resp.status_code == 200

        get_resp = client.get(f"/tools/{tool_id}")
        assert get_resp.status_code == 404

    def test_list_tools_after_register(self, client: TestClient) -> None:
        payload = {
            "name": "list-tool",
            "description": "Tool for list test",
            "input_schema": {"type": "object", "properties": {}},
            "endpoint": "http://localhost:9001",
            "protocols": ["http"],
        }
        client.post("/tools", json=payload)
        response = client.get("/tools")
        assert response.status_code == 200
        tools = response.json()["tools"]
        names = [t["name"] for t in tools]
        assert "list-tool" in names
