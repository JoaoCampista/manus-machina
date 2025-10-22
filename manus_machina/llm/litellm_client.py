"""
LiteLLM Integration

Universal LLM client supporting 100+ LLM providers:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude)
- Google (Gemini)
- Cohere, Replicate, HuggingFace, and more

LiteLLM provides a unified interface for all providers.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import os

try:
    from litellm import completion, acompletion
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False


class LLMMessage(BaseModel):
    """Message in a conversation"""
    role: str  # "system", "user", "assistant"
    content: str


class LLMResponse(BaseModel):
    """Response from LLM"""
    content: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    finish_reason: str
    raw_response: Optional[Dict[str, Any]] = None


class LiteLLMClient:
    """
    Universal LLM client using LiteLLM.
    
    Supports 100+ LLM providers with a unified interface.
    
    Examples:
        # OpenAI
        client = LiteLLMClient(model="gpt-4")
        
        # Anthropic
        client = LiteLLMClient(model="claude-3-opus-20240229")
        
        # Google
        client = LiteLLMClient(model="gemini/gemini-2.0-flash-exp")
        
        # Cohere
        client = LiteLLMClient(model="command-nightly")
    """
    
    def __init__(
        self,
        model: str = "gpt-4",
        temperature: float = 0.7,
        max_tokens: int = 4096,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize LiteLLM client.
        
        Args:
            model: Model identifier (e.g., "gpt-4", "claude-3-opus", "gemini/gemini-2.0-flash")
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate
            api_key: API key (if not set in environment)
            api_base: Custom API base URL
            **kwargs: Additional provider-specific parameters
        """
        if not LITELLM_AVAILABLE:
            raise ImportError(
                "LiteLLM is not installed. Install it with: pip install litellm"
            )
        
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.api_key = api_key
        self.api_base = api_base
        self.extra_params = kwargs
        
        # Set API key in environment if provided
        if api_key:
            self._set_api_key(model, api_key)
    
    def _set_api_key(self, model: str, api_key: str) -> None:
        """Set API key in environment based on model provider"""
        if model.startswith("gpt-") or model.startswith("o1-"):
            os.environ["OPENAI_API_KEY"] = api_key
        elif model.startswith("claude-"):
            os.environ["ANTHROPIC_API_KEY"] = api_key
        elif model.startswith("gemini/"):
            os.environ["GOOGLE_API_KEY"] = api_key
        elif model.startswith("command-"):
            os.environ["COHERE_API_KEY"] = api_key
    
    async def generate(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Generate completion from messages.
        
        Args:
            messages: List of conversation messages
            temperature: Override default temperature
            max_tokens: Override default max tokens
            **kwargs: Additional parameters
            
        Returns:
            LLM response
        """
        # Prepare messages
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        # Prepare parameters
        params = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
            **self.extra_params,
            **kwargs
        }
        
        if self.api_base:
            params["api_base"] = self.api_base
        
        # Call LiteLLM
        response = await acompletion(**params)
        
        # Extract response data
        choice = response.choices[0]
        usage = response.usage
        
        return LLMResponse(
            content=choice.message.content,
            model=response.model,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            finish_reason=choice.finish_reason,
            raw_response=response.model_dump() if hasattr(response, 'model_dump') else None
        )
    
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """
        Simple text generation from a prompt.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            **kwargs: Additional parameters
            
        Returns:
            Generated text
        """
        messages = []
        
        if system_prompt:
            messages.append(LLMMessage(role="system", content=system_prompt))
        
        messages.append(LLMMessage(role="user", content=prompt))
        
        response = await self.generate(messages, **kwargs)
        return response.content
    
    def generate_sync(
        self,
        messages: List[LLMMessage],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """
        Synchronous version of generate.
        
        Args:
            messages: List of conversation messages
            temperature: Override default temperature
            max_tokens: Override default max tokens
            **kwargs: Additional parameters
            
        Returns:
            LLM response
        """
        # Prepare messages
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        # Prepare parameters
        params = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": temperature or self.temperature,
            "max_tokens": max_tokens or self.max_tokens,
            **self.extra_params,
            **kwargs
        }
        
        if self.api_base:
            params["api_base"] = self.api_base
        
        # Call LiteLLM (sync)
        response = completion(**params)
        
        # Extract response data
        choice = response.choices[0]
        usage = response.usage
        
        return LLMResponse(
            content=choice.message.content,
            model=response.model,
            prompt_tokens=usage.prompt_tokens,
            completion_tokens=usage.completion_tokens,
            total_tokens=usage.total_tokens,
            finish_reason=choice.finish_reason,
            raw_response=response.model_dump() if hasattr(response, 'model_dump') else None
        )


# Convenience functions for common providers

def create_openai_client(
    model: str = "gpt-4",
    api_key: Optional[str] = None,
    **kwargs
) -> LiteLLMClient:
    """Create OpenAI client"""
    return LiteLLMClient(
        model=model,
        api_key=api_key or os.getenv("OPENAI_API_KEY"),
        **kwargs
    )


def create_anthropic_client(
    model: str = "claude-3-opus-20240229",
    api_key: Optional[str] = None,
    **kwargs
) -> LiteLLMClient:
    """Create Anthropic client"""
    return LiteLLMClient(
        model=model,
        api_key=api_key or os.getenv("ANTHROPIC_API_KEY"),
        **kwargs
    )


def create_gemini_client(
    model: str = "gemini/gemini-2.0-flash-exp",
    api_key: Optional[str] = None,
    **kwargs
) -> LiteLLMClient:
    """Create Google Gemini client"""
    return LiteLLMClient(
        model=model,
        api_key=api_key or os.getenv("GOOGLE_API_KEY"),
        **kwargs
    )


def create_cohere_client(
    model: str = "command-nightly",
    api_key: Optional[str] = None,
    **kwargs
) -> LiteLLMClient:
    """Create Cohere client"""
    return LiteLLMClient(
        model=model,
        api_key=api_key or os.getenv("COHERE_API_KEY"),
        **kwargs
    )

