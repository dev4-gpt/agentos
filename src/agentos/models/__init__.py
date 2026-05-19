"""AgentOS Core Data Models (CDM).

Defines the canonical Pydantic schemas for agents, tools, capabilities,
communication protocols, auth flows, integrations, responses, and logs.
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


class AuthType(str, Enum):
    API_KEY = "api_key"
    OAUTH2 = "oauth2"
    BEARER = "bearer"
    BASIC = "basic"
    NONE = "none"


class ErrorCategory(str, Enum):
    AUTH_EXPIRED = "AUTH_EXPIRED"
    RATE_LIMITED = "RATE_LIMITED"
    SCHEMA_MISMATCH = "SCHEMA_MISMATCH"
    TOOL_UNAVAILABLE = "TOOL_UNAVAILABLE"
    AMBIGUOUS_INTENT = "AMBIGUOUS_INTENT"


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


# =========== Auth Models ===========


class OAuthScope(BaseModel):
    """An OAuth2 scope definition."""

    name: str
    description: str
    required: bool = False


class AuthConfig(BaseModel):
    """Authentication configuration for a tool/integration."""

    type: AuthType = AuthType.NONE
    scopes: List[str] = Field(default_factory=list)
    auth_url: Optional[str] = None
    token_url: Optional[str] = None
    onboarding_flow: str = "none"  # "api_key_paste", "oauth2_redirect", "guidable_steps"
    docs_url: Optional[str] = None


class StoredToken(BaseModel):
    """A stored OAuth2 / API key credential."""

    id: Optional[str] = None
    provider: str
    auth_type: AuthType
    access_token: str
    refresh_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    scopes: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


# =========== Tool Models ===========


class Tool(BaseModel):
    """A registered tool/schema for agent tool interaction."""

    name: str
    description: str
    type: ToolType = Field(default=ToolType.TOOL)
    inputSchema: Optional[ToolSchema] = None
    input_schema: Optional[ToolSchema] = None  # snake_case alias
    output_schema: Optional[Dict[str, Any]] = None
    annotations: Optional[Dict[str, Any]] = None
    tags: List[str] = Field(default_factory=list)
    categories: List[str] = Field(default_factory=list)
    capabilities: List[str] = Field(default_factory=list)  # e.g. ["idempotent", "rate_limited"]
    authentication: Optional[AuthConfig] = None
    mcp_tool_name: Optional[str] = None
    endpoint: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ToolRecord(BaseModel):
    """Standalone tool registration record (global /tools endpoints)."""

    id: Optional[str] = None
    name: str
    description: str
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None
    endpoint: Optional[str] = None
    protocols: Optional[List[str]] = None
    categories: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    capabilities: List[str] = Field(default_factory=list)
    authentication: Optional[AuthConfig] = None
    mcp_tool_name: Optional[str] = None
    integration_id: Optional[str] = None  # link to parent integration
    embedding: Optional[List[float]] = None  # cached embedding vector
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# =========== Integration / SaaS Models ===========


class Integration(BaseModel):
    """A SaaS platform integration (e.g. Slack, Stripe, GitHub)."""

    id: Optional[str] = None
    name: str
    slug: str  # e.g. "slack", "stripe", "github"
    description: str
    logo_url: Optional[str] = None
    docs_url: Optional[str] = None
    base_url: Optional[str] = None
    auth: AuthConfig = Field(default_factory=AuthConfig)
    categories: List[str] = Field(default_factory=list)
    tool_count: int = 0
    is_active: bool = True
    created_at: Optional[str] = None


# =========== MCP Models ===========


class MCPResource(BaseModel):
    """An MCP resource (documentation, schema reference, auth guide)."""

    uri: str
    name: str
    description: Optional[str] = None
    mimeType: str = "text/markdown"
    content: Optional[str] = None


class MCPPrompt(BaseModel):
    """A pre-built MCP prompt template for common agent tasks."""

    name: str
    description: str
    arguments: List[Dict[str, Any]] = Field(default_factory=list)
    template: str


# =========== Agent Models ===========


class Agent(BaseModel):
    """An autonomous agent registered in the AgentOS registry."""

    id: Optional[str] = None
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


# =========== Response Models ===========


class AgentResponse(BaseModel):
    """Response returned by an agent tool execution."""

    success: bool
    data: Any = None
    error: Optional[str] = None
    error_category: Optional[ErrorCategory] = None
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


class ToolSearchResult(BaseModel):
    """A single semantic search result."""

    tool: ToolRecord
    score: float  # cosine similarity 0.0 - 1.0
    rank: int


class ToolSearchResponse(BaseModel):
    """Response from POST /tools/search."""

    intent: str
    results: List[ToolSearchResult]
    total: int


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str = "healthy"
    version: str = Field(default="0.1.0")
    uptime_seconds: Optional[float] = None
    tool_count: int = 0
    agent_count: int = 0
    integration_count: int = 0


class OAuthInitResponse(BaseModel):
    """Response from POST /auth/:provider to start OAuth2."""

    provider: str
    auth_url: str
    state: str
    scopes: List[str]


class OAuthCallbackRequest(BaseModel):
    """Callback payload after user completes OAuth2 consent."""

    provider: str
    code: str
    state: str


class ToolExecutionRequest(BaseModel):
    """Request to execute a tool via the proxy."""

    tool_id: str
    arguments: Dict[str, Any] = Field(default_factory=dict)
    token_id: Optional[str] = None  # stored credential to use


class ToolExecutionResponse(BaseModel):
    """Response from tool execution proxy."""

    success: bool
    tool_id: str
    result: Any = None
    error: Optional[str] = None
    error_category: Optional[ErrorCategory] = None
    latency_ms: Optional[float] = None


# Re-exports for convenience
__all__ = [
    "Agent",
    "AgentStatus",
    "AgentListResponse",
    "AgentLog",
    "AgentResponse",
    "AuthConfig",
    "AuthType",
    "Capability",
    "CommunicationProtocol",
    "ErrorCategory",
    "HealthResponse",
    "Integration",
    "MCPPrompt",
    "MCPResource",
    "OAuthCallbackRequest",
    "OAuthInitResponse",
    "OAuthScope",
    "Parameter",
    "Protocol",
    "StoredToken",
    "Tool",
    "ToolExecutionRequest",
    "ToolExecutionResponse",
    "ToolRecord",
    "ToolSchema",
    "ToolSearchResponse",
    "ToolSearchResult",
    "ToolType",
]
