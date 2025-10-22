"""Base tool implementation."""

from typing import Any, Dict, Optional, Callable, Awaitable
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod


class ToolConfig(BaseModel):
    """Configuration for a tool."""
    
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Tool parameters schema")
    
    # Resilience configuration
    enable_retry: bool = Field(default=True)
    enable_circuit_breaker: bool = Field(default=True)
    max_retries: int = Field(default=3)
    timeout_seconds: float = Field(default=30.0)


class Tool(ABC):
    """
    Base class for all tools.
    
    Tools are functions that agents can use to interact with the world.
    """
    
    def __init__(self, config: ToolConfig):
        self.config = config
    
    @abstractmethod
    async def execute(self, **kwargs: Any) -> Any:
        """
        Execute the tool.
        
        Args:
            **kwargs: Tool parameters
            
        Returns:
            Tool result
        """
        pass
    
    def get_schema(self) -> Dict[str, Any]:
        """Get OpenAPI schema for the tool."""
        return {
            "name": self.config.name,
            "description": self.config.description,
            "parameters": self.config.parameters
        }
    
    def __repr__(self) -> str:
        return f"Tool(name={self.config.name})"


class FunctionTool(Tool):
    """
    Tool that wraps a Python function.
    """
    
    def __init__(
        self,
        config: ToolConfig,
        func: Callable[..., Awaitable[Any]]
    ):
        super().__init__(config)
        self.func = func
    
    async def execute(self, **kwargs: Any) -> Any:
        """Execute the wrapped function."""
        return await self.func(**kwargs)

