"""Task implementation for agents."""

from typing import Any, Dict, Optional
from pydantic import BaseModel, Field
from enum import Enum


class TaskStatus(str, Enum):
    """Task execution status."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskConfig(BaseModel):
    """Configuration for a task."""
    
    description: str = Field(..., description="Task description")
    expected_output: Optional[str] = Field(None, description="Expected output format")
    agent: Optional[str] = Field(None, description="Agent assigned to task")
    context: Dict[str, Any] = Field(default_factory=dict, description="Task context")
    output_file: Optional[str] = Field(None, description="File to save output")


class Task:
    """
    Represents a task to be executed by an agent.
    """
    
    def __init__(self, config: TaskConfig):
        self.config = config
        self.status = TaskStatus.PENDING
        self.result: Optional[Any] = None
        self.error: Optional[str] = None
    
    def __repr__(self) -> str:
        return f"Task(description={self.config.description[:50]}..., status={self.status})"

