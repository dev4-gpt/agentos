"""Tests for the AgentOS Registry API."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


class TestHealth:
    def test_health_returns_200(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_response_structure(self, client: TestClient) -> None:
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"


class TestAgents:
    def test_list_agents_empty(self, client: TestClient) -> None:
        response = client.get("/agents")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert isinstance(data["agents"], list)

    def test_register_agent(self, client: TestClient) -> None:
        payload = {
            "name": "test-agent",
            "version": "1.0.0",
            "description": "A test agent",
            "capabilities": [],
            "tools": [],
            "endpoint": "http://localhost:9000",
            "protocols": ["http"],
        }
        response = client.post("/agents", json=payload)
        assert response.status_code in (200, 201)
        data = response.json()
        assert "id" in data
        assert data["name"] == "test-agent"

    def test_get_agent_not_found(self, client: TestClient) -> None:
        response = client.get("/agents/nonexistent-id")
        assert response.status_code == 404

    def test_register_then_get_agent(self, client: TestClient) -> None:
        payload = {
            "name": "get-test-agent",
            "version": "1.0.0",
            "description": "Agent for get test",
            "capabilities": [],
            "tools": [],
            "endpoint": "http://localhost:9001",
            "protocols": ["http"],
        }
        create_resp = client.post("/agents", json=payload)
        assert create_resp.status_code in (200, 201)
        agent_id = create_resp.json()["id"]

        get_resp = client.get(f"/agents/{agent_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["id"] == agent_id

    def test_delete_agent(self, client: TestClient) -> None:
        payload = {
            "name": "delete-test-agent",
            "version": "1.0.0",
            "description": "Agent for delete test",
            "capabilities": [],
            "tools": [],
            "endpoint": "http://localhost:9002",
            "protocols": ["http"],
        }
        create_resp = client.post("/agents", json=payload)
        agent_id = create_resp.json()["id"]

        delete_resp = client.delete(f"/agents/{agent_id}")
        assert delete_resp.status_code == 200

        get_resp = client.get(f"/agents/{agent_id}")
        assert get_resp.status_code == 404


class TestTools:
    def test_list_tools_empty(self, client: TestClient) -> None:
        response = client.get("/tools")
        assert response.status_code == 200
        data = response.json()
        assert "tools" in data
        assert isinstance(data["tools"], list)
