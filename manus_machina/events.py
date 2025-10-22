"""
Domain Events System

Events represent things that have happened in the domain.
They are immutable and provide a complete audit trail.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Types of domain events"""
    
    # Session events
    SESSION_CREATED = "session.created"
    SESSION_UPDATED = "session.updated"
    SESSION_CLOSED = "session.closed"
    
    # Agent events
    AGENT_STARTED = "agent.started"
    AGENT_COMPLETED = "agent.completed"
    AGENT_FAILED = "agent.failed"
    
    # Task events
    TASK_ASSIGNED = "task.assigned"
    TASK_STARTED = "task.started"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    
    # Tool events
    TOOL_CALL_STARTED = "tool.call.started"
    TOOL_CALL_COMPLETED = "tool.call.completed"
    TOOL_CALL_FAILED = "tool.call.failed"
    
    # State events
    STATE_UPDATED = "state.updated"
    STATE_CLEARED = "state.cleared"
    
    # Artifact events
    ARTIFACT_CREATED = "artifact.created"
    ARTIFACT_UPDATED = "artifact.updated"
    
    # Message events
    MESSAGE_RECEIVED = "message.received"
    MESSAGE_SENT = "message.sent"
    
    # LLM events
    LLM_REQUEST_STARTED = "llm.request.started"
    LLM_REQUEST_COMPLETED = "llm.request.completed"
    LLM_REQUEST_FAILED = "llm.request.failed"
    
    # Memory events
    MEMORY_STORED = "memory.stored"
    MEMORY_RETRIEVED = "memory.retrieved"


class DomainEvent(BaseModel):
    """
    Domain Event represents something that happened in the domain.
    
    Events are:
    - Immutable (no setters)
    - Timestamped
    - Uniquely identified
    - Serializable
    """
    
    # Identity
    id: UUID = Field(default_factory=uuid4)
    event_type: EventType
    
    # Context
    session_id: Optional[UUID] = None
    agent_name: Optional[str] = None
    
    # Payload
    data: Dict[str, Any] = Field(default_factory=dict)
    
    # Metadata
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[UUID] = None  # For tracing related events
    
    class Config:
        frozen = True  # Make immutable
        arbitrary_types_allowed = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary"""
        return {
            "id": str(self.id),
            "event_type": self.event_type.value,
            "session_id": str(self.session_id) if self.session_id else None,
            "agent_name": self.agent_name,
            "data": self.data,
            "timestamp": self.timestamp.isoformat(),
            "correlation_id": str(self.correlation_id) if self.correlation_id else None,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DomainEvent":
        """Create event from dictionary"""
        return cls(
            id=UUID(data["id"]),
            event_type=EventType(data["event_type"]),
            session_id=UUID(data["session_id"]) if data.get("session_id") else None,
            agent_name=data.get("agent_name"),
            data=data.get("data", {}),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            correlation_id=UUID(data["correlation_id"]) if data.get("correlation_id") else None,
        )


# Event factories for common events

def session_created_event(session_id: UUID, user_id: Optional[str] = None) -> DomainEvent:
    """Create a session created event"""
    return DomainEvent(
        event_type=EventType.SESSION_CREATED,
        session_id=session_id,
        data={"user_id": user_id}
    )


def agent_started_event(
    session_id: UUID,
    agent_name: str,
    task_description: str
) -> DomainEvent:
    """Create an agent started event"""
    return DomainEvent(
        event_type=EventType.AGENT_STARTED,
        session_id=session_id,
        agent_name=agent_name,
        data={"task_description": task_description}
    )


def agent_completed_event(
    session_id: UUID,
    agent_name: str,
    result: str,
    duration_ms: float
) -> DomainEvent:
    """Create an agent completed event"""
    return DomainEvent(
        event_type=EventType.AGENT_COMPLETED,
        session_id=session_id,
        agent_name=agent_name,
        data={
            "result": result,
            "duration_ms": duration_ms
        }
    )


def tool_call_started_event(
    session_id: UUID,
    agent_name: str,
    tool_name: str,
    arguments: Dict[str, Any]
) -> DomainEvent:
    """Create a tool call started event"""
    return DomainEvent(
        event_type=EventType.TOOL_CALL_STARTED,
        session_id=session_id,
        agent_name=agent_name,
        data={
            "tool_name": tool_name,
            "arguments": arguments
        }
    )


def tool_call_completed_event(
    session_id: UUID,
    agent_name: str,
    tool_name: str,
    result: Any,
    duration_ms: float
) -> DomainEvent:
    """Create a tool call completed event"""
    return DomainEvent(
        event_type=EventType.TOOL_CALL_COMPLETED,
        session_id=session_id,
        agent_name=agent_name,
        data={
            "tool_name": tool_name,
            "result": result,
            "duration_ms": duration_ms
        }
    )


def state_updated_event(
    session_id: UUID,
    key: str,
    value: Any,
    agent_name: Optional[str] = None
) -> DomainEvent:
    """Create a state updated event"""
    return DomainEvent(
        event_type=EventType.STATE_UPDATED,
        session_id=session_id,
        agent_name=agent_name,
        data={
            "key": key,
            "value": value
        }
    )


def artifact_created_event(
    session_id: UUID,
    artifact_id: UUID,
    artifact_type: str,
    title: str,
    agent_name: Optional[str] = None
) -> DomainEvent:
    """Create an artifact created event"""
    return DomainEvent(
        event_type=EventType.ARTIFACT_CREATED,
        session_id=session_id,
        agent_name=agent_name,
        data={
            "artifact_id": str(artifact_id),
            "artifact_type": artifact_type,
            "title": title
        }
    )


def message_received_event(
    session_id: UUID,
    message: str,
    user_id: Optional[str] = None
) -> DomainEvent:
    """Create a message received event"""
    return DomainEvent(
        event_type=EventType.MESSAGE_RECEIVED,
        session_id=session_id,
        data={
            "message": message,
            "user_id": user_id
        }
    )


def message_sent_event(
    session_id: UUID,
    message: str,
    agent_name: str
) -> DomainEvent:
    """Create a message sent event"""
    return DomainEvent(
        event_type=EventType.MESSAGE_SENT,
        session_id=session_id,
        agent_name=agent_name,
        data={"message": message}
    )


def llm_request_started_event(
    session_id: UUID,
    agent_name: str,
    model: str,
    prompt_tokens: int
) -> DomainEvent:
    """Create an LLM request started event"""
    return DomainEvent(
        event_type=EventType.LLM_REQUEST_STARTED,
        session_id=session_id,
        agent_name=agent_name,
        data={
            "model": model,
            "prompt_tokens": prompt_tokens
        }
    )


def llm_request_completed_event(
    session_id: UUID,
    agent_name: str,
    model: str,
    prompt_tokens: int,
    completion_tokens: int,
    duration_ms: float
) -> DomainEvent:
    """Create an LLM request completed event"""
    return DomainEvent(
        event_type=EventType.LLM_REQUEST_COMPLETED,
        session_id=session_id,
        agent_name=agent_name,
        data={
            "model": model,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens,
            "duration_ms": duration_ms
        }
    )

