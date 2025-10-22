"""
Manus Machina v5.0 - Enterprise-Grade Multi-Agent Orchestration Framework
"""

__version__ = "5.0.0"

# Core exports
from manus_machina.session.session import Session
from manus_machina.session.session_service import SessionService, InMemorySessionService
from manus_machina.state.state import State
from manus_machina.artifacts.artifact import Artifact, ArtifactType
from manus_machina.llm.litellm_client import LiteLLMClient, LLMMessage
from manus_machina.agents.simple_agent import SimpleAgent, SimpleAgentConfig

__all__ = [
    "__version__",
    "Session",
    "SessionService",
    "InMemorySessionService",
    "State",
    "Artifact",
    "ArtifactType",
    "LiteLLMClient",
    "LLMMessage",
    "SimpleAgent",
    "SimpleAgentConfig",
]
