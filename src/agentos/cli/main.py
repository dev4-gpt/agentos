"""AgentOS CLI - Command-line interface for the AgentOS Registry."""

from __future__ import annotations

import asyncio
import json
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from ..sdk import AgentOSClient
from ..models import Agent, AgentStatus

app = typer.Typer(name="agentos", help="AgentOS CLI - Manage agents and tools")
console = Console()


def get_client(registry_url: str = "http://localhost:8000") -> AgentOSClient:
    return AgentOSClient(base_url=registry_url)


@app.command()
def health(
    registry_url: str = typer.Option("http://localhost:8000", "--registry", "-r", help="Registry URL")
) -> None:
    """Check the health of the AgentOS Registry."""
    async def _run() -> None:
        async with get_client(registry_url) as client:
            result = await client.health()
            console.print_json(result.model_dump_json())

    asyncio.run(_run())


@app.command(name="list-agents")
def list_agents(
    registry_url: str = typer.Option("http://localhost:8000", "--registry", "-r"),
    status: Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status")
) -> None:
    """List all registered agents."""
    async def _run() -> None:
        async with get_client(registry_url) as client:
            result = await client.list_agents(status=status)
            table = Table(title="Agents")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Status", style="yellow")
            table.add_column("Version")
            for agent in result.agents:
                table.add_row(agent.id, agent.name, agent.status.value, agent.version)
            console.print(table)

    asyncio.run(_run())


@app.command(name="list-tools")
def list_tools(
    registry_url: str = typer.Option("http://localhost:8000", "--registry", "-r"),
    agent_id: Optional[str] = typer.Option(None, "--agent", "-a", help="Filter by agent ID")
) -> None:
    """List all registered tools."""
    async def _run() -> None:
        async with get_client(registry_url) as client:
            tools = await client.list_tools(agent_id=agent_id)
            table = Table(title="Tools")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="green")
            table.add_column("Agent ID", style="yellow")
            table.add_column("Description")
            for tool in tools:
                table.add_row(tool.id, tool.name, tool.agent_id, tool.description or "")
            console.print(table)

    asyncio.run(_run())


@app.command(name="start-mcp")
def start_mcp(
    registry_url: str = typer.Option("http://localhost:8000", "--registry", "-r", help="Registry URL")
) -> None:
    """Start the MCP stdio server."""
    from ..mcp import run_mcp_server
    console.print(f"[green]Starting MCP server, connecting to registry: {registry_url}[/green]")
    asyncio.run(run_mcp_server(registry_url=registry_url))


def main() -> None:
    app()


if __name__ == "__main__":
    main()
