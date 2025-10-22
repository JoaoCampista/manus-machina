"""State management for agents and workflows."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class State(BaseModel):
    """
    Represents the state of an agent or workflow.
    
    State is immutable by default and creates new instances on updates.
    """
    
    data: Dict[str, Any] = Field(default_factory=dict, description="State data")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="State metadata")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    version: int = Field(default=1, description="State version for optimistic locking")
    
    class Config:
        frozen = False  # Allow mutation for performance
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from state."""
        return self.data.get(key, default)
    
    def set(self, key: str, value: Any) -> "State":
        """Set a value in state (creates new state instance)."""
        new_data = self.data.copy()
        new_data[key] = value
        return State(
            data=new_data,
            metadata=self.metadata.copy(),
            created_at=self.created_at,
            updated_at=datetime.utcnow(),
            version=self.version + 1
        )
    
    def update(self, updates: Dict[str, Any]) -> "State":
        """Update multiple values in state."""
        new_data = self.data.copy()
        new_data.update(updates)
        return State(
            data=new_data,
            metadata=self.metadata.copy(),
            created_at=self.created_at,
            updated_at=datetime.utcnow(),
            version=self.version + 1
        )
    
    def merge(self, other: "State") -> "State":
        """Merge with another state."""
        merged_data = self.data.copy()
        merged_data.update(other.data)
        merged_metadata = self.metadata.copy()
        merged_metadata.update(other.metadata)
        return State(
            data=merged_data,
            metadata=merged_metadata,
            created_at=self.created_at,
            updated_at=datetime.utcnow(),
            version=self.version + 1
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        return {
            "data": self.data,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "State":
        """Create state from dictionary."""
        return cls(
            data=data.get("data", {}),
            metadata=data.get("metadata", {}),
            version=data.get("version", 1)
        )


class StateStore:
    """Abstract base class for state persistence."""
    
    async def save(self, key: str, state: State) -> None:
        """Save state to store."""
        raise NotImplementedError
    
    async def load(self, key: str) -> Optional[State]:
        """Load state from store."""
        raise NotImplementedError
    
    async def delete(self, key: str) -> None:
        """Delete state from store."""
        raise NotImplementedError
    
    async def exists(self, key: str) -> bool:
        """Check if state exists."""
        raise NotImplementedError


class InMemoryStateStore(StateStore):
    """In-memory state store for development and testing."""
    
    def __init__(self) -> None:
        self._store: Dict[str, State] = {}
    
    async def save(self, key: str, state: State) -> None:
        """Save state to memory."""
        self._store[key] = state
    
    async def load(self, key: str) -> Optional[State]:
        """Load state from memory."""
        return self._store.get(key)
    
    async def delete(self, key: str) -> None:
        """Delete state from memory."""
        if key in self._store:
            del self._store[key]
    
    async def exists(self, key: str) -> bool:
        """Check if state exists in memory."""
        return key in self._store

