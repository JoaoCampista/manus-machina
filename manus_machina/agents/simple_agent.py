"""Simplified functional agent implementation."""

import os
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import google.generativeai as genai


class SimpleAgentConfig(BaseModel):
    """Simple agent configuration."""
    name: str
    role: str
    goal: str
    backstory: Optional[str] = None
    model: str = "gemini-2.0-flash-exp"
    temperature: float = 0.7
    max_tokens: int = 2048


class SimpleAgent:
    """
    Simplified functional agent for testing.
    
    This is a working implementation that uses Google Gemini API.
    """
    
    def __init__(self, config: SimpleAgentConfig, api_key: Optional[str] = None):
        """
        Initialize agent.
        
        Args:
            config: Agent configuration
            api_key: Google API key (defaults to GOOGLE_API_KEY env var)
        """
        self.config = config
        self.memory: List[Dict[str, Any]] = []
        
        # Setup Gemini
        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(config.model)
    
    async def execute(self, task: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a task.
        
        Args:
            task: Task description
            context: Optional context
            
        Returns:
            Result dictionary
        """
        # Build system instruction
        system_instruction = self._build_system_instruction()
        
        # Build full prompt
        full_prompt = f"{system_instruction}\n\nTask: {task}"
        if context:
            full_prompt += f"\n\nContext: {context}"
        
        try:
            # Generate response
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.config.temperature,
                    max_output_tokens=self.config.max_tokens
                )
            )
            
            # Extract text
            result_text = response.text if hasattr(response, 'text') else str(response)
            
            # Store in memory
            self.memory.append({
                "task": task,
                "response": result_text,
                "context": context
            })
            
            return {
                "agent": self.config.name,
                "task": task,
                "response": result_text,
                "result": result_text,
                "status": "success"
            }
            
        except Exception as e:
            return {
                "agent": self.config.name,
                "task": task,
                "response": f"Error: {str(e)}",
                "result": None,
                "status": "error",
                "error": str(e)
            }
    
    def _build_system_instruction(self) -> str:
        """Build system instruction."""
        instruction = f"""You are {self.config.name}, a {self.config.role}.

Your goal: {self.config.goal}"""
        
        if self.config.backstory:
            instruction += f"\n\nBackstory: {self.config.backstory}"
        
        instruction += "\n\nYou should act according to your role and help accomplish the given task professionally and effectively."
        
        return instruction
    
    def get_memory(self) -> List[Dict[str, Any]]:
        """Get agent memory."""
        return self.memory
    
    def __repr__(self) -> str:
        return f"SimpleAgent(name={self.config.name}, role={self.config.role})"

