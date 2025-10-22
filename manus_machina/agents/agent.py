"""Core agent implementation."""

from typing import Any, Dict, List, Optional, Callable, Awaitable
from pydantic import BaseModel, Field
from enum import Enum
import asyncio

from manus_machina.core.state import State
from manus_machina.tools.base import Tool


class AgentRole(str, Enum):
    """Predefined agent roles."""
    RESEARCHER = "researcher"
    ANALYST = "analyst"
    WRITER = "writer"
    REVIEWER = "reviewer"
    COORDINATOR = "coordinator"
    SPECIALIST = "specialist"


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    CUSTOM = "custom"


class AgentConfig(BaseModel):
    """Configuration for an agent."""
    
    name: str = Field(..., description="Agent name")
    role: str = Field(..., description="Agent role")
    goal: str = Field(..., description="Agent goal")
    backstory: Optional[str] = Field(None, description="Agent backstory for context")
    
    # LLM Configuration
    llm_provider: LLMProvider = Field(default=LLMProvider.OPENAI)
    llm_model: str = Field(default="gpt-4.1-mini")
    llm_temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    llm_max_tokens: Optional[int] = Field(default=None)
    
    # Memory Configuration
    short_term_memory: bool = Field(default=True)
    long_term_memory: bool = Field(default=False)
    memory_collection: Optional[str] = Field(None)
    
    # Behavior Configuration
    verbose: bool = Field(default=False)
    max_iterations: int = Field(default=10, gt=0)
    allow_delegation: bool = Field(default=False)
    
    # Tool Configuration
    tools: List[str] = Field(default_factory=list)
    
    # Resilience Configuration
    enable_retry: bool = Field(default=True)
    enable_circuit_breaker: bool = Field(default=True)
    
    # Guardrails Configuration
    enable_guardrails: bool = Field(default=True)
    input_guards: List[str] = Field(default_factory=list)
    output_guards: List[str] = Field(default_factory=list)
    action_guards: List[str] = Field(default_factory=list)


class AgentStatus(str, Enum):
    """Agent execution status."""
    IDLE = "idle"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    STOPPED = "stopped"


class Agent:
    """
    Core agent implementation.
    
    An agent is an autonomous entity that can:
    - Reason using LLMs
    - Use tools to interact with the world
    - Maintain state and memory
    - Communicate with other agents
    - Execute tasks with resilience patterns
    """
    
    def __init__(
        self,
        config: AgentConfig,
        tools: Optional[List[Tool]] = None,
        state: Optional[State] = None,
    ):
        self.config = config
        self.tools = tools or []
        self.state = state or State()
        self.status = AgentStatus.IDLE
        
        # Lifecycle hooks
        self._on_start_hooks: List[Callable[[Agent], Awaitable[None]]] = []
        self._on_message_hooks: List[Callable[[Agent, Dict[str, Any]], Awaitable[None]]] = []
        self._on_error_hooks: List[Callable[[Agent, Exception], Awaitable[None]]] = []
        self._on_complete_hooks: List[Callable[[Agent], Awaitable[None]]] = []
        
        # Execution context
        self._llm_client: Optional[Any] = None
        self._memory_store: Optional[Any] = None
        self._communication_bus: Optional[Any] = None
        self._resilience_engine: Optional[Any] = None
        self._guardrail_engine: Optional[Any] = None
    
    def set_llm_client(self, client: Any) -> None:
        """Set the LLM client."""
        self._llm_client = client
    
    def set_memory_store(self, store: Any) -> None:
        """Set the memory store."""
        self._memory_store = store
    
    def set_communication_bus(self, bus: Any) -> None:
        """Set the communication bus."""
        self._communication_bus = bus
    
    def set_resilience_engine(self, engine: Any) -> None:
        """Set the resilience engine."""
        self._resilience_engine = engine
    
    def set_guardrail_engine(self, engine: Any) -> None:
        """Set the guardrail engine."""
        self._guardrail_engine = engine
    
    def on_start(self, hook: Callable[["Agent"], Awaitable[None]]) -> None:
        """Register a hook to be called when agent starts."""
        self._on_start_hooks.append(hook)
    
    def on_message(self, hook: Callable[["Agent", Dict[str, Any]], Awaitable[None]]) -> None:
        """Register a hook to be called when agent receives a message."""
        self._on_message_hooks.append(hook)
    
    def on_error(self, hook: Callable[["Agent", Exception], Awaitable[None]]) -> None:
        """Register a hook to be called when agent encounters an error."""
        self._on_error_hooks.append(hook)
    
    def on_complete(self, hook: Callable[["Agent"], Awaitable[None]]) -> None:
        """Register a hook to be called when agent completes."""
        self._on_complete_hooks.append(hook)
    
    async def start(self) -> None:
        """Start the agent."""
        self.status = AgentStatus.RUNNING
        for hook in self._on_start_hooks:
            await hook(self)
    
    async def stop(self) -> None:
        """Stop the agent."""
        self.status = AgentStatus.STOPPED
    
    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """
        Execute a task.
        
        Args:
            task: Task description
            context: Additional context for the task
            
        Returns:
            Task result
        """
        try:
            await self.start()
            
            # Build prompt
            prompt = self._build_prompt(task, context or {})
            
            # Apply input guardrails
            if self._guardrail_engine and self.config.enable_guardrails:
                prompt = await self._guardrail_engine.validate_input(prompt, self.config.input_guards)
            
            # Execute with LLM
            result = await self._execute_with_llm(prompt)
            
            # Apply output guardrails
            if self._guardrail_engine and self.config.enable_guardrails:
                result = await self._guardrail_engine.validate_output(result, self.config.output_guards)
            
            # Update state
            self.state = self.state.set("last_result", result)
            
            self.status = AgentStatus.COMPLETED
            for hook in self._on_complete_hooks:
                await hook(self)
            
            return result
            
        except Exception as e:
            self.status = AgentStatus.FAILED
            for hook in self._on_error_hooks:
                await hook(self, e)
            raise
    
    async def receive_message(self, message: Dict[str, Any]) -> None:
        """Receive a message from another agent or external source."""
        for hook in self._on_message_hooks:
            await hook(self, message)
    
    async def send_message(self, recipient: str, message: Dict[str, Any]) -> None:
        """Send a message to another agent."""
        if self._communication_bus:
            await self._communication_bus.send(
                sender=self.config.name,
                recipient=recipient,
                message=message
            )
    
    def _build_prompt(self, task: str, context: Dict[str, Any]) -> str:
        """Build the prompt for the LLM."""
        system_prompt = f"""You are {self.config.name}, a {self.config.role}.

Goal: {self.config.goal}
"""
        if self.config.backstory:
            system_prompt += f"\nBackstory: {self.config.backstory}"
        
        if self.tools:
            system_prompt += f"\n\nAvailable Tools:\n"
            for tool in self.tools:
                system_prompt += f"- {tool.name}: {tool.description}\n"
        
        user_prompt = f"Task: {task}"
        if context:
            user_prompt += f"\n\nContext:\n{context}"
        
        return f"{system_prompt}\n\n{user_prompt}"
    
    async def _execute_with_llm(self, prompt: str) -> str:
        """Execute the prompt with the LLM."""
        if not self._llm_client:
            raise RuntimeError("LLM client not configured")
        
        # This is a simplified implementation
        # In production, this would handle streaming, tool calls, etc.
        response = await self._llm_client.complete(
            prompt=prompt,
            model=self.config.llm_model,
            temperature=self.config.llm_temperature,
            max_tokens=self.config.llm_max_tokens
        )
        
        return response
    
    def __repr__(self) -> str:
        return f"Agent(name={self.config.name}, role={self.config.role}, status={self.status})"

