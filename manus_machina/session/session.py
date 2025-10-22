"""
Session Entity - Domain Layer

Represents a single, ongoing interaction between a user and the agent system.
Contains the chronological sequence of events and maintains state.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from pydantic import BaseModel, Field

from ..state.state import State
from ..artifacts.artifact import Artifact
from ..core.events import DomainEvent


class SessionMetadata(BaseModel):
    """Metadata associated with a session"""
    user_id: Optional[str] = None
    app_name: str
    tags: List[str] = Field(default_factory=list)
    custom_fields: Dict[str, Any] = Field(default_factory=dict)


class Session(BaseModel):
    """
    Session represents a conversation thread between user and agent.
    
    A session is the primary unit of conversational context, containing:
    - Unique identifier
    - State (scratchpad for this conversation)
    - Events (chronological history)
    - Artifacts (generated content)
    - Metadata (user_id, app_name, tags)
    
    Inspired by Google ADK's session model.
    """
    
    # Identity
    id: UUID = Field(default_factory=uuid4)
    
    # Metadata
    metadata: SessionMetadata
    
    # State management
    state: State = Field(default_factory=State)
    
    # Event history
    events: List[DomainEvent] = Field(default_factory=list)
    
    # Artifacts
    artifacts: List[Artifact] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    # Status
    is_active: bool = True
    
    class Config:
        arbitrary_types_allowed = True
    
    def add_event(self, event: DomainEvent) -> None:
        """Add an event to the session history"""
        self.events.append(event)
        self.updated_at = datetime.utcnow()
    
    def add_artifact(self, artifact: Artifact) -> None:
        """Add an artifact to the session"""
        self.artifacts.append(artifact)
        self.updated_at = datetime.utcnow()
    
    def get_state(self, key: str, default: Any = None) -> Any:
        """Get a value from session state"""
        return self.state.get(key, default)
    
    def set_state(self, key: str, value: Any) -> None:
        """Set a value in session state"""
        self.state.set(key, value)
        self.updated_at = datetime.utcnow()
    
    def get_user_state(self, key: str, default: Any = None) -> Any:
        """Get a value from user state (user: prefix)"""
        return self.state.get(f"user:{key}", default)
    
    def set_user_state(self, key: str, value: Any) -> None:
        """Set a value in user state (user: prefix)"""
        self.state.set(f"user:{key}", value)
        self.updated_at = datetime.utcnow()
    
    def get_app_state(self, key: str, default: Any = None) -> Any:
        """Get a value from app state (app: prefix)"""
        return self.state.get(f"app:{key}", default)
    
    def set_app_state(self, key: str, value: Any) -> None:
        """Set a value in app state (app: prefix)"""
        self.state.set(f"app:{key}", value)
        self.updated_at = datetime.utcnow()
    
    def get_temp_state(self, key: str, default: Any = None) -> Any:
        """Get a value from temporary invocation state (temp: prefix)"""
        return self.state.get(f"temp:{key}", default)
    
    def set_temp_state(self, key: str, value: Any) -> None:
        """Set a value in temporary invocation state (temp: prefix)"""
        self.state.set(f"temp:{key}", value)
        # Note: temp state is not persisted, so we don't update updated_at
    
    def clear_temp_state(self) -> None:
        """Clear all temporary state after invocation completes"""
        self.state.clear_prefix("temp:")
    
    def get_event_history(self, event_type: Optional[str] = None) -> List[DomainEvent]:
        """Get event history, optionally filtered by type"""
        if event_type:
            return [e for e in self.events if e.event_type == event_type]
        return self.events.copy()
    
    def get_artifacts_by_type(self, artifact_type: str) -> List[Artifact]:
        """Get artifacts filtered by type"""
        return [a for a in self.artifacts if a.type == artifact_type]
    
    def close(self) -> None:
        """Mark session as inactive"""
        self.is_active = False
        self.updated_at = datetime.utcnow()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for serialization"""
        return {
            "id": str(self.id),
            "metadata": self.metadata.model_dump(),
            "state": self.state.to_dict(),
            "events": [e.model_dump() for e in self.events],
            "artifacts": [a.model_dump() for a in self.artifacts],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_active": self.is_active,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Session":
        """Create session from dictionary"""
        return cls(
            id=UUID(data["id"]),
            metadata=SessionMetadata(**data["metadata"]),
            state=State.from_dict(data["state"]),
            events=[DomainEvent(**e) for e in data["events"]],
            artifacts=[Artifact(**a) for a in data["artifacts"]],
            created_at=datetime.fromisoformat(data["created_at"]),
            updated_at=datetime.fromisoformat(data["updated_at"]),
            is_active=data["is_active"],
        )

