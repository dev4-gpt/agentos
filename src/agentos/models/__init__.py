"""AgentOS Core Data Models (CDM).

Defines the canonical Pydantic schemas for agents, tools, capabilities,
communication protocols, responses, and logs.
"""

from __future__ import annotations
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

# =========== Enums ===========


class AgentStatus(str, Enum):
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"


class Protocol(str, Enum):
    MCP = "mcp"
    HTTP = "http"
    GRPC = "grpc"
    WEBSOCKET = "websocket"


class ToolType(str, Enum):
    TOOL = "tool"
    RESOURCE = "resource"
    PROMPT = "prompt"


# =========== Core Models ===========


class ToolSchema(BaseModel):
    """JSON Schema describing a tool's input parameters."""

    type: str = Field(default="object")
    properties: Dict[str, Any] = Field(default_factory=dict)
    required: List[str] = Field(default_factory=list)
    additionalProperties: bool = Field(default=False)


class Parameter(BaseModel):
    """Individual parameter definition."""

    name: str
    type: str
    description: str
    required: bool = False
    default: Any = None


class Capability(BaseModel):
    """Describes a specific capability of an agent."""

    name: str
    description: str
    parameters: List[Parameter] = Field(default_factory=list)


class Tool(BaseModel):
    """A registered tool/schema for agent tool interaction."""

    name: str
    description: str
    type: ToolType = Field(default=ToolType.TOOL)
    inputSchema: Optional[ToolSchema] = None
    input_schema: Optional[ToolSchema] = None  # snake_case alias
    annotations: Optional[Dict[str, Any]] = None
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class Agent(BaseModel):
    """An autonomous agent registered in the AgentOS registry."""

    id: str
    name: str
    description: Optional[str] = None
    status: AgentStatus = Field(default=AgentStatus.IDLE)
    version: str = Field(default="0.1.0")
    author: Optional[str] = None
    url: Optional[str] = None
    capabilities: List[Capability] = Field(default_factory=list)
    tools: List[Tool] = Field(default_factory=list)
    communication_protocols: List[Protocol] = Field(
        default_factory=lambda: [Protocol.MCP]
    )
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CommunicationProtocol(BaseModel):
    """Protocol endpoint configuration for an agent."""

    protocol: Protocol
    endpoint: str
    version: str = "1.0.0"
    config: Dict[str, Any] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    """Response returned by an agent tool execution."""

    success: bool
    data: Any = None
    error: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    latency_ms: Optional[float] = None


class AgentLog(BaseModel):
    """Audit log entry for agent actions."""

    agent_id: str
    action: str
    tool_name: Optional[str] = None
    status: str
    message: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentListResponse(BaseModel):
    """Paginator-style response for listing agents."""

    agents: List[Agent]
    total: int
    page: int
    page_size: int


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = "healthy"
    version: str = Field(default="0.1.0")
    uptime_seconds: Optional[float] = None


# Re-exports for convenience
__all__ = [
    "Agent",
    "AgentStatus",
    "Tool",
    "ToolType",
    "ToolSchema",
    "Parameter",
    "Capability",
    "CommunicationProtocol",
    "Protocol",
    "AgentResponse",
    "AgentLog",
    "AgentListResponse",
    "HealthResponse",
]
