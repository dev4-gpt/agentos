"""AgentOS CLI - Command-line interface for the AgentOS Registry."""
from __future__ import annotations
from typing import Optional

import asyncio
import json
import os

import typer
from rich.console import Console

from ..sdk import AgentOSClient

app = typer.Typer(name="agentos", help="AgentOS CLI - Manage agents and tools")
console = Console()

def _ensure_json(data: object) -> str:
    if isinstance(data, (dict, list)):
        return json.dumps(data, indent=2, default=str)
    return str(data)

def _print_json(data: object) -> None:
    console.print_json(_ensure_json(data))

def get_client(registry_url: str) -> AgentOSClient:
    return AgentOSClient(base_url=registry_url)

# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------
@app.command()
def health(
    registry_url: str = typer.Option(
        "http://localhost:8000", "--registry", "-r", help="Registry URL"
    ),
) -> None:
    """Check the health of the AgentOS Registry."""

    async def _run() -> None:
        async with get_client(registry_url) as client:
            result = await client.health()
            _print_json(result)

    asyncio.run(_run())

@app.command()
def register_agent(
    name: str = typer.Option(..., "--name", "-n", help="Agent name"),
    description: str = typer.Option(
        "", "--description", "-d", help="Agent description"
    ),
    registry_url: str = typer.Option(
        "http://localhost:8000", "--registry", "-r", help="Registry URL"
    ),
) -> None:
    """Register a new agent."""

    async def _run() -> None:
        async with get_client(registry_url) as client:
            result = await client.register_agent(
                {"name": name, "description": description}
            )
            _print_json(result)

    asyncio.run(_run())

@app.command()
def list_agents(
    registry_url: str = typer.Option(
        "http://localhost:8000", "--registry", "-r", help="Registry URL"
    ),
    page: int = typer.Option(1, "--page", "-p", help="Page number"),
    page_size: int = typer.Option(20, "--page-size", "-s", help="Page size"),
) -> None:
    """List all registered agents."""

    async def _run() -> None:
        async with get_client(registry_url) as client:
            result = await client.list_agents(page=page, page_size=page_size)
            _print_json(result)

    asyncio.run(_run())

@app.command()
def get_agent(
    agent_id: str = typer.Option(..., "--id", "-i", help="Agent ID"),
    registry_url: str = typer.Option(
        "http://localhost:8000", "--registry", "-r", help="Registry URL"
    ),
) -> None:
    """Get details for a specific agent."""

    async def _run() -> None:
        async with get_client(registry_url) as client:
            result = await client.get_agent(agent_id)
            _print_json(result)

    asyncio.run(_run())

@app.command()
def deregister_agent(
    agent_id: str = typer.Option(..., "--id", "-i", help="Agent ID"),
    registry_url: str = typer.Option(
        "http://localhost:8000", "--registry", "-r", help="Registry URL"
    ),
) -> None:
    """Remove an agent from the registry."""

    async def _run() -> None:
        async with get_client(registry_url) as client:
            await client.deregister_agent(agent_id)
            console.print(f"Agent '{agent_id}' successfully deregistered.")

    asyncio.run(_run())

# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------
@app.command()
def register_tool(
    name: str = typer.Option(..., "--name", "-n", help="Tool name"),
    description: str = typer.Option(
        "", "--description", "-d", help="Tool description"
    ),
    endpoint: Optional[str] = typer.Option(
        None, "--endpoint", "-e", help="Tool endpoint URL"
    ),
    schema_file: Optional[str] = typer.Option(
        None, "--schema", "-s", help="JSON schema file path"
    ),
    registry_url: str = typer.Option(
        "http://localhost:8000", "--registry", "-r", help="Registry URL"
    ),
) -> None:
    """Register a standalone tool in the global tools registry."""
    input_schema: dict = {}
    if schema_file:
        with open(schema_file) as f:
            input_schema = json.load(f)
    payload = {
        "name": name,
        "description": description,
        "input_schema": input_schema,
        "endpoint": endpoint,
    }

    async def _run() -> None:
        async with get_client(registry_url) as client:
            result = await client.register_tool(payload)
            _print_json(result)

    asyncio.run(_run())

@app.command()
def list_tools(
    registry_url: str = typer.Option(
        "http://localhost:8000", "--registry", "-r", help="Registry URL"
    ),
) -> None:
    """List all globally registered tools."""

    async def _run() -> None:
        async with get_client(registry_url) as client:
            tools = await client.list_tools()
            _print_json({"tools": tools})

    asyncio.run(_run())

# ---------------------------------------------------------------------------
# MCP
# ---------------------------------------------------------------------------
@app.command()
def mcp_init(
    registry_url: str = typer.Option(
        "http://localhost:8000", "--registry", "-r", help="Registry URL"
    ),
    protocol_version: str = typer.Option(
        "2024-11-05", "--protocol", "-p", help="MCP protocol version"
    ),
) -> None:
    """Perform MCP initialize handshake with the registry."""

    async def _run() -> None:
        async with get_client(registry_url) as client:
            result = await client.mcp_initialize(protocol_version)
            _print_json(result)

    asyncio.run(_run())

@app.command()
def mcp_tools(
    registry_url: str = typer.Option(
        "http://localhost:8000", "--registry", "-r", help="Registry URL"
    ),
) -> None:
    """List tools in MCP format."""

    async def _run() -> None:
        async with get_client(registry_url) as client:
            tools = await client.mcp_list_tools()
            _print_json({"tools": tools})

    asyncio.run(_run())

@app.command()
def mcp_call(
    tool_name: str = typer.Option(..., "--name", "-n", help="Tool name to call"),
    args_json: str = typer.Option("{}", "--args", "-a", help="JSON arguments for the tool"),
    registry_url: str = typer.Option(
        "http://localhost:8000", "--registry", "-r", help="Registry URL"
    ),
) -> None:
    """Call a tool via MCP."""
    arguments: dict = json.loads(args_json) if args_json else {}

    async def _run() -> None:
        async with get_client(registry_url) as client:
            result = await client.mcp_call_tool(tool_name, arguments)
            _print_json(result)

    asyncio.run(_run())

@app.command()
def mcp_agents(
    registry_url: str = typer.Option(
        "http://localhost:8000", "--registry", "-r", help="Registry URL"
    ),
) -> None:
    """List agents in MCP format."""

    async def _run() -> None:
        async with get_client(registry_url) as client:
            agents = await client.mcp_list_agents()
            _print_json({"agents": agents})

    asyncio.run(_run())

@app.command()
def mcp_serve(
    registry_url: str = typer.Option(
        "http://localhost:8000", "--registry", "-r", help="Registry URL"
    ),
) -> None:
    """Serve the MCP stdio server."""
    os.environ["AGENTOS_REGISTRY_URL"] = registry_url
    from ..mcp import server as mcp_server

    mcp_server.main()

if __name__ == "__main__":
    app()
