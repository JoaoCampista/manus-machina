"""LLM integration for agents."""

import os
from typing import Any, Dict, List, Optional
import google.generativeai as genai


class LLMClient:
    """Client for interacting with LLMs."""
    
    def __init__(self, model: str = "gemini-2.0-flash-exp", api_key: Optional[str] = None):
        """
        Initialize LLM client.
        
        Args:
            model: Model name
            api_key: API key (defaults to GOOGLE_API_KEY env var)
        """
        self.model_name = model
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model)
    
    async def generate(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> Dict[str, Any]:
        """
        Generate response from LLM.
        
        Args:
            prompt: User prompt
            system_instruction: System instruction
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            
        Returns:
            Response dict with text and metadata
        """
        try:
            # Build full prompt
            if system_instruction:
                full_prompt = f"{system_instruction}\n\nUser: {prompt}\n\nAssistant:"
            else:
                full_prompt = prompt
            
            # Generate response
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=temperature,
                    max_output_tokens=max_tokens
                )
            )
            
            # Extract text
            text = response.text if hasattr(response, 'text') else str(response)
            
            return {
                "text": text,
                "model": self.model_name,
                "finish_reason": "stop",
                "usage": {
                    "prompt_tokens": len(full_prompt.split()),
                    "completion_tokens": len(text.split()),
                    "total_tokens": len(full_prompt.split()) + len(text.split())
                }
            }
            
        except Exception as e:
            return {
                "text": f"Error: {str(e)}",
                "model": self.model_name,
                "finish_reason": "error",
                "error": str(e)
            }

