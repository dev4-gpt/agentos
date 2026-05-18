"""AgentOS - The Machine-Readable Tool Layer for Autonomous AI Agents."""

__version__ = "0.1.0"
__author__ = "Aryaman Singh"

# Re-export key classes and functions
from agentos.models import (
    Agent,
    Tool,
    ToolSchema,
    Capability,
    CommunicationProtocol,
    AgentResponse,
    AgentLog,
)
from agentos.sdk import AgentOSClient

__all__ = [
    "Agent",
    "Tool",
    "ToolSchema",
    "Capability",
    "CommunicationProtocol",
    "AgentResponse",
    "AgentLog",
    "AgentOSClient",
]
