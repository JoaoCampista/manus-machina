"""Crew implementation for multi-agent collaboration."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum

from manus_machina.core.agent import Agent
from manus_machina.core.task import Task


class ProcessType(str, Enum):
    """Type of process for crew execution."""
    SEQUENTIAL = "sequential"
    HIERARCHICAL = "hierarchical"
    PARALLEL = "parallel"


class CrewConfig(BaseModel):
    """Configuration for a crew."""
    
    name: str = Field(..., description="Crew name")
    agents: List[str] = Field(default_factory=list, description="Agent names in crew")
    process: ProcessType = Field(default=ProcessType.SEQUENTIAL)
    verbose: bool = Field(default=False)
    memory: bool = Field(default=False)
    cache: bool = Field(default=True)


class Crew:
    """
    A crew is a collection of agents working together on tasks.
    
    Similar to CrewAI's Crew concept.
    """
    
    def __init__(self, config: CrewConfig, agents: Optional[List[Agent]] = None):
        self.config = config
        self.agents = agents or []
        self.tasks: List[Task] = []
    
    def add_agent(self, agent: Agent) -> None:
        """Add an agent to the crew."""
        self.agents.append(agent)
    
    def add_task(self, task: Task) -> None:
        """Add a task to the crew."""
        self.tasks.append(task)
    
    async def kickoff(self, inputs: Optional[Dict[str, Any]] = None) -> Any:
        """
        Start the crew execution.
        
        Args:
            inputs: Initial inputs for the crew
            
        Returns:
            Final result
        """
        if self.config.process == ProcessType.SEQUENTIAL:
            return await self._execute_sequential(inputs or {})
        elif self.config.process == ProcessType.PARALLEL:
            return await self._execute_parallel(inputs or {})
        else:
            raise NotImplementedError(f"Process type {self.config.process} not implemented")
    
    async def _execute_sequential(self, inputs: Dict[str, Any]) -> Any:
        """Execute tasks sequentially."""
        context = inputs.copy()
        results = []
        
        for task in self.tasks:
            # Find agent for task
            agent = self._find_agent(task.config.agent)
            if not agent:
                raise ValueError(f"Agent {task.config.agent} not found in crew")
            
            # Execute task
            result = await agent.execute(task.config.description, context)
            results.append(result)
            
            # Update context for next task
            context["previous_result"] = result
        
        return results[-1] if results else None
    
    async def _execute_parallel(self, inputs: Dict[str, Any]) -> List[Any]:
        """Execute tasks in parallel."""
        import asyncio
        
        tasks_coroutines = []
        for task in self.tasks:
            agent = self._find_agent(task.config.agent)
            if not agent:
                raise ValueError(f"Agent {task.config.agent} not found in crew")
            
            tasks_coroutines.append(agent.execute(task.config.description, inputs))
        
        results = await asyncio.gather(*tasks_coroutines)
        return results
    
    def _find_agent(self, agent_name: Optional[str]) -> Optional[Agent]:
        """Find agent by name."""
        if not agent_name:
            return self.agents[0] if self.agents else None
        
        for agent in self.agents:
            if agent.config.name == agent_name:
                return agent
        return None
    
    def __repr__(self) -> str:
        return f"Crew(name={self.config.name}, agents={len(self.agents)}, tasks={len(self.tasks)})"

