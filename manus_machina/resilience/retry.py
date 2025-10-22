"""Retry pattern implementation with exponential backoff and jitter."""

from typing import Callable, Any, Optional, TypeVar, ParamSpec, Type
from pydantic import BaseModel, Field
from enum import Enum
import asyncio
import random
import time
from functools import wraps

T = TypeVar('T')
P = ParamSpec('P')


class BackoffStrategy(str, Enum):
    """Backoff strategies for retry."""
    FIXED = "fixed"
    LINEAR = "linear"
    EXPONENTIAL = "exponential"


class JitterType(str, Enum):
    """Jitter types to add randomness to backoff."""
    NONE = "none"
    FULL = "full"  # random(0, backoff)
    EQUAL = "equal"  # backoff/2 + random(0, backoff/2)
    DECORRELATED = "decorrelated"  # random(base, previous_backoff * 3)


class RetryConfig(BaseModel):
    """Configuration for retry policy."""
    
    max_attempts: int = Field(default=3, description="Maximum retry attempts", gt=0)
    base_delay: float = Field(default=1.0, description="Base delay in seconds", gt=0)
    max_delay: float = Field(default=60.0, description="Maximum delay in seconds", gt=0)
    backoff_strategy: BackoffStrategy = Field(default=BackoffStrategy.EXPONENTIAL)
    jitter_type: JitterType = Field(default=JitterType.FULL)
    multiplier: float = Field(default=2.0, description="Backoff multiplier", gt=1.0)
    
    # Retry conditions
    retry_on_exceptions: tuple = Field(
        default=(Exception,),
        description="Exceptions to retry on"
    )
    retry_on_result: Optional[Callable[[Any], bool]] = Field(
        default=None,
        description="Function to determine if result should trigger retry"
    )


class RetryExhaustedError(Exception):
    """Raised when all retry attempts are exhausted."""
    pass


class RetryPolicy:
    """
    Retry policy with exponential backoff and jitter.
    
    Implements various backoff strategies and jitter types to handle
    transient failures gracefully.
    """
    
    def __init__(self, name: str, config: RetryConfig):
        self.name = name
        self.config = config
        
        # Metrics
        self._total_calls = 0
        self._total_retries = 0
        self._total_successes = 0
        self._total_failures = 0
    
    async def execute(
        self,
        func: Callable[P, T],
        *args: P.args,
        **kwargs: P.kwargs
    ) -> T:
        """
        Execute a function with retry logic.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            RetryExhaustedError: If all retry attempts fail
        """
        self._total_calls += 1
        last_exception: Optional[Exception] = None
        previous_delay = self.config.base_delay
        
        for attempt in range(1, self.config.max_attempts + 1):
            try:
                # Execute the function
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)
                
                # Check if result should trigger retry
                if self.config.retry_on_result and self.config.retry_on_result(result):
                    if attempt < self.config.max_attempts:
                        delay = self._calculate_delay(attempt, previous_delay)
                        previous_delay = delay
                        await asyncio.sleep(delay)
                        self._total_retries += 1
                        continue
                
                # Success
                self._total_successes += 1
                return result
                
            except self.config.retry_on_exceptions as e:
                last_exception = e
                
                if attempt < self.config.max_attempts:
                    # Calculate delay and retry
                    delay = self._calculate_delay(attempt, previous_delay)
                    previous_delay = delay
                    await asyncio.sleep(delay)
                    self._total_retries += 1
                else:
                    # Last attempt failed
                    self._total_failures += 1
                    break
        
        # All attempts exhausted
        raise RetryExhaustedError(
            f"Retry policy '{self.name}' exhausted after {self.config.max_attempts} attempts. "
            f"Last exception: {last_exception}"
        ) from last_exception
    
    def _calculate_delay(self, attempt: int, previous_delay: float) -> float:
        """Calculate delay for next retry attempt."""
        # Calculate base delay based on strategy
        if self.config.backoff_strategy == BackoffStrategy.FIXED:
            base_delay = self.config.base_delay
        
        elif self.config.backoff_strategy == BackoffStrategy.LINEAR:
            base_delay = self.config.base_delay * attempt
        
        elif self.config.backoff_strategy == BackoffStrategy.EXPONENTIAL:
            base_delay = self.config.base_delay * (self.config.multiplier ** (attempt - 1))
        
        else:
            base_delay = self.config.base_delay
        
        # Cap at max delay
        base_delay = min(base_delay, self.config.max_delay)
        
        # Apply jitter
        if self.config.jitter_type == JitterType.NONE:
            return base_delay
        
        elif self.config.jitter_type == JitterType.FULL:
            # Full jitter: random(0, base_delay)
            return random.uniform(0, base_delay)
        
        elif self.config.jitter_type == JitterType.EQUAL:
            # Equal jitter: base_delay/2 + random(0, base_delay/2)
            return base_delay / 2 + random.uniform(0, base_delay / 2)
        
        elif self.config.jitter_type == JitterType.DECORRELATED:
            # Decorrelated jitter: random(base, previous_delay * 3)
            return random.uniform(self.config.base_delay, min(previous_delay * 3, self.config.max_delay))
        
        return base_delay
    
    def get_metrics(self) -> dict:
        """Get retry policy metrics."""
        return {
            "name": self.name,
            "total_calls": self._total_calls,
            "total_retries": self._total_retries,
            "total_successes": self._total_successes,
            "total_failures": self._total_failures,
            "success_rate": self._total_successes / self._total_calls if self._total_calls > 0 else 0,
        }
    
    def __repr__(self) -> str:
        return f"RetryPolicy(name={self.name}, max_attempts={self.config.max_attempts})"


def retry(name: str, config: Optional[RetryConfig] = None):
    """
    Decorator to wrap a function with retry logic.
    
    Usage:
        @retry("my_api_call", RetryConfig(max_attempts=5))
        async def call_api():
            ...
    """
    if config is None:
        config = RetryConfig()
    
    policy = RetryPolicy(name, config)
    
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            return await policy.execute(func, *args, **kwargs)
        return wrapper
    
    return decorator


# Convenience function for common retry patterns
def retry_with_exponential_backoff(
    max_attempts: int = 5,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: bool = True
):
    """
    Convenience decorator for exponential backoff with optional jitter.
    
    Usage:
        @retry_with_exponential_backoff(max_attempts=5, jitter=True)
        async def my_function():
            ...
    """
    config = RetryConfig(
        max_attempts=max_attempts,
        base_delay=base_delay,
        max_delay=max_delay,
        backoff_strategy=BackoffStrategy.EXPONENTIAL,
        jitter_type=JitterType.FULL if jitter else JitterType.NONE
    )
    return retry("exponential_backoff", config)

