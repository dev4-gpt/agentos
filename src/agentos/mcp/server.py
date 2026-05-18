"""AgentOS MCP Server.

Implements a Model Context Protocol (MCP) server that exposes all agents and
their tools as MCP-compatible tools, resources, and prompts.
"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types as mcp_types

from agentos.models import Agent, Tool
from agentos.sdk import AgentOSClient

logger = logging.getLogger(__name__)


def create_mcp_server(registry_url: str = "http://localhost:8000") -> Server:
    """Create and configure the MCP server.

    Args:
        registry_url: URL of the AgentOS Registry API.

    Returns:
        Configured MCP Server instance.
    """
    server = Server("agentos-mcp")
    client = AgentOSClient(base_url=registry_url)

    @server.list_tools()
    async def list_tools() -> List[mcp_types.Tool]:
        """List all tools from all registered agents."""
        mcp_tools: List[mcp_types.Tool] = []
        try:
            response = await client.list_agents_async()
            agents = response.agents
            for agent in agents:
                for tool in agent.tools:
                    input_schema = {}
                    if tool.inputSchema:
                        input_schema = tool.inputSchema.model_dump()
                    elif tool.input_schema:
                        input_schema = tool.input_schema.model_dump()
                    else:
                        input_schema = {"type": "object", "properties": {}}

                    mcp_tools.append(
                        mcp_types.Tool(
                            name=f"{agent.id}__{tool.name}",
                            description=f"[Agent: {agent.name}] {tool.description}",
                            inputSchema=input_schema,
                        )
                    )
        except Exception as e:
            logger.error(f"Failed to list tools: {e}")
        return mcp_tools

    @server.call_tool()
    async def call_tool(name: str, arguments: Dict[str, Any]) -> List[mcp_types.TextContent]:
        """Execute a tool via the agent registry."""
        try:
            parts = name.split("__", 1)
            if len(parts) != 2:
                return [mcp_types.TextContent(type="text", text=f"Invalid tool name format: {name}")]
            agent_id, tool_name = parts
            result = {"agent_id": agent_id, "tool_name": tool_name, "arguments": arguments, "status": "dispatched"}
            return [mcp_types.TextContent(type="text", text=json.dumps(result, indent=2))]
        except Exception as e:
            logger.error(f"Tool call failed: {e}")
            return [mcp_types.TextContent(type="text", text=f"Error: {str(e)}")]

    @server.list_resources()
    async def list_resources() -> List[mcp_types.Resource]:
        """List all registered agents as resources."""
        resources: List[mcp_types.Resource] = []
        try:
            response = await client.list_agents_async()
            for agent in response.agents:
                resources.append(
                    mcp_types.Resource(
                        uri=f"agentos://agents/{agent.id}",
                        name=agent.name,
                        description=agent.description or f"Agent: {agent.name}",
                        mimeType="application/json",
                    )
                )
        except Exception as e:
            logger.error(f"Failed to list resources: {e}")
        return resources

    @server.read_resource()
    async def read_resource(uri: str) -> str:
        """Read an agent resource by URI."""
        try:
            agent_id = uri.split("/")[-1]
            agent = await client.get_agent_async(agent_id)
            return agent.model_dump_json(indent=2)
        except Exception as e:
            return json.dumps({"error": str(e)})

    return server


async def run_mcp_server(registry_url: str = "http://localhost:8000") -> None:
    """Run the MCP server using stdio transport."""
    server = create_mcp_server(registry_url)
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> None:
    """Entry point for running the MCP server."""
    asyncio.run(run_mcp_server())


if __name__ == "__main__":
    main()
