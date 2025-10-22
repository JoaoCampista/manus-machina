"""Saga pattern implementation for distributed transactions."""

from typing import Callable, Any, Dict, List, Optional, Awaitable
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime
import asyncio


class SagaStepStatus(str, Enum):
    """Status of a saga step."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"


class SagaStatus(str, Enum):
    """Status of the entire saga."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    COMPENSATING = "compensating"
    COMPENSATED = "compensated"


class SagaStep(BaseModel):
    """
    A step in a saga transaction.
    
    Each step has:
    - An action to execute (forward transaction)
    - A compensation action to undo (rollback)
    """
    
    name: str = Field(..., description="Step name")
    action: Any = Field(..., description="Forward action callable")
    compensation: Any = Field(..., description="Compensation action callable")
    status: SagaStepStatus = Field(default=SagaStepStatus.PENDING)
    result: Optional[Any] = Field(default=None, description="Step execution result")
    error: Optional[str] = Field(default=None, description="Error message if failed")
    started_at: Optional[datetime] = Field(default=None)
    completed_at: Optional[datetime] = Field(default=None)
    
    class Config:
        arbitrary_types_allowed = True


class SagaCoordinationType(str, Enum):
    """Type of saga coordination."""
    ORCHESTRATION = "orchestration"  # Centralized coordinator
    CHOREOGRAPHY = "choreography"  # Event-driven, decentralized


class Saga:
    """
    Saga pattern implementation for distributed transactions.
    
    A saga is a sequence of local transactions where each transaction
    updates data within a single service. If a step fails, the saga
    executes compensating transactions to undo the changes made by
    preceding steps.
    
    Supports both orchestration (centralized) and choreography (event-driven).
    """
    
    def __init__(
        self,
        name: str,
        coordination_type: SagaCoordinationType = SagaCoordinationType.ORCHESTRATION
    ):
        self.name = name
        self.coordination_type = coordination_type
        self.steps: List[SagaStep] = []
        self.status = SagaStatus.PENDING
        self.context: Dict[str, Any] = {}
        
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.error: Optional[str] = None
    
    def add_step(
        self,
        name: str,
        action: Callable[..., Awaitable[Any]],
        compensation: Callable[..., Awaitable[Any]]
    ) -> "Saga":
        """
        Add a step to the saga.
        
        Args:
            name: Step name
            action: Forward action (async function)
            compensation: Compensation action (async function)
            
        Returns:
            Self for chaining
        """
        step = SagaStep(
            name=name,
            action=action,
            compensation=compensation
        )
        self.steps.append(step)
        return self
    
    async def execute(self, initial_context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute the saga.
        
        Args:
            initial_context: Initial context data
            
        Returns:
            Final result
            
        Raises:
            SagaFailedError: If saga fails and compensation completes
            Exception: If compensation fails
        """
        if initial_context:
            self.context.update(initial_context)
        
        self.status = SagaStatus.RUNNING
        self.started_at = datetime.utcnow()
        
        completed_steps: List[SagaStep] = []
        
        try:
            # Execute each step in sequence
            for step in self.steps:
                step.status = SagaStepStatus.RUNNING
                step.started_at = datetime.utcnow()
                
                try:
                    # Execute the action
                    result = await step.action(self.context)
                    
                    # Store result in context for next steps
                    self.context[f"{step.name}_result"] = result
                    
                    step.result = result
                    step.status = SagaStepStatus.COMPLETED
                    step.completed_at = datetime.utcnow()
                    completed_steps.append(step)
                    
                except Exception as e:
                    # Step failed, trigger compensation
                    step.status = SagaStepStatus.FAILED
                    step.error = str(e)
                    step.completed_at = datetime.utcnow()
                    
                    self.status = SagaStatus.FAILED
                    self.error = f"Step '{step.name}' failed: {e}"
                    
                    # Compensate all completed steps in reverse order
                    await self._compensate(completed_steps)
                    
                    raise SagaFailedError(
                        f"Saga '{self.name}' failed at step '{step.name}': {e}"
                    ) from e
            
            # All steps completed successfully
            self.status = SagaStatus.COMPLETED
            self.completed_at = datetime.utcnow()
            
            # Return final result
            if self.steps:
                return self.steps[-1].result
            return None
            
        except Exception as e:
            if self.status != SagaStatus.COMPENSATED:
                self.status = SagaStatus.FAILED
            self.completed_at = datetime.utcnow()
            raise
    
    async def _compensate(self, completed_steps: List[SagaStep]) -> None:
        """
        Execute compensation for completed steps in reverse order.
        
        Args:
            completed_steps: Steps to compensate
        """
        self.status = SagaStatus.COMPENSATING
        
        # Compensate in reverse order
        for step in reversed(completed_steps):
            step.status = SagaStepStatus.COMPENSATING
            
            try:
                await step.compensation(self.context)
                step.status = SagaStepStatus.COMPENSATED
                
            except Exception as e:
                # Compensation failed - this is critical
                step.error = f"Compensation failed: {e}"
                raise SagaCompensationError(
                    f"Failed to compensate step '{step.name}': {e}"
                ) from e
        
        self.status = SagaStatus.COMPENSATED
    
    def get_status(self) -> Dict[str, Any]:
        """Get saga execution status."""
        return {
            "name": self.name,
            "status": self.status,
            "coordination_type": self.coordination_type,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "error": self.error,
            "steps": [
                {
                    "name": step.name,
                    "status": step.status,
                    "started_at": step.started_at.isoformat() if step.started_at else None,
                    "completed_at": step.completed_at.isoformat() if step.completed_at else None,
                    "error": step.error,
                }
                for step in self.steps
            ]
        }
    
    def __repr__(self) -> str:
        return f"Saga(name={self.name}, status={self.status}, steps={len(self.steps)})"


class SagaFailedError(Exception):
    """Raised when a saga fails after compensation."""
    pass


class SagaCompensationError(Exception):
    """Raised when saga compensation fails."""
    pass


# Example usage helper
class SagaBuilder:
    """Builder for creating sagas with fluent API."""
    
    def __init__(self, name: str):
        self.saga = Saga(name)
    
    def step(
        self,
        name: str,
        action: Callable[..., Awaitable[Any]],
        compensation: Callable[..., Awaitable[Any]]
    ) -> "SagaBuilder":
        """Add a step to the saga."""
        self.saga.add_step(name, action, compensation)
        return self
    
    def build(self) -> Saga:
        """Build and return the saga."""
        return self.saga

