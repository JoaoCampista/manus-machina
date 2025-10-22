"""Circuit Breaker pattern implementation."""

from typing import Callable, Any, Optional, TypeVar, ParamSpec
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime, timedelta
import asyncio
from functools import wraps

T = TypeVar('T')
P = ParamSpec('P')


class CircuitState(str, Enum):
    """Circuit breaker states."""
    CLOSED = "closed"  # Normal operation
    OPEN = "open"  # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreakerConfig(BaseModel):
    """Configuration for circuit breaker."""
    
    failure_threshold: int = Field(
        default=5,
        description="Number of consecutive failures to open circuit",
        gt=0
    )
    success_threshold: int = Field(
        default=2,
        description="Number of consecutive successes to close circuit from half-open",
        gt=0
    )
    timeout_seconds: float = Field(
        default=60.0,
        description="Seconds to wait before attempting recovery (half-open)",
        gt=0
    )
    expected_exceptions: tuple = Field(
        default=(Exception,),
        description="Exceptions that count as failures"
    )


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass


class CircuitBreaker:
    """
    Circuit Breaker pattern implementation.
    
    Prevents cascading failures by stopping calls to a failing service
    and allowing it time to recover.
    
    States:
    - CLOSED: Normal operation, calls pass through
    - OPEN: Too many failures, calls fail immediately
    - HALF_OPEN: Testing recovery, limited calls allowed
    """
    
    def __init__(self, name: str, config: CircuitBreakerConfig):
        self.name = name
        self.config = config
        self.state = CircuitState.CLOSED
        
        self._failure_count = 0
        self._success_count = 0
        self._last_failure_time: Optional[datetime] = None
        self._last_state_change: datetime = datetime.utcnow()
        
        # Metrics
        self._total_calls = 0
        self._total_failures = 0
        self._total_successes = 0
        self._total_rejected = 0
    
    async def call(self, func: Callable[P, T], *args: P.args, **kwargs: P.kwargs) -> T:
        """
        Execute a function with circuit breaker protection.
        
        Args:
            func: Function to execute
            *args: Positional arguments
            **kwargs: Keyword arguments
            
        Returns:
            Function result
            
        Raises:
            CircuitBreakerOpenError: If circuit is open
            Exception: Original exception if call fails
        """
        self._total_calls += 1
        
        # Check if circuit should transition from OPEN to HALF_OPEN
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self._transition_to_half_open()
            else:
                self._total_rejected += 1
                raise CircuitBreakerOpenError(
                    f"Circuit breaker '{self.name}' is OPEN. "
                    f"Last failure: {self._last_failure_time}"
                )
        
        try:
            # Execute the function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            
            # Record success
            self._on_success()
            return result
            
        except self.config.expected_exceptions as e:
            # Record failure
            self._on_failure()
            raise
    
    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self._last_failure_time is None:
            return True
        
        elapsed = datetime.utcnow() - self._last_failure_time
        return elapsed >= timedelta(seconds=self.config.timeout_seconds)
    
    def _on_success(self) -> None:
        """Handle successful call."""
        self._total_successes += 1
        self._failure_count = 0
        self._success_count += 1
        
        if self.state == CircuitState.HALF_OPEN:
            if self._success_count >= self.config.success_threshold:
                self._transition_to_closed()
    
    def _on_failure(self) -> None:
        """Handle failed call."""
        self._total_failures += 1
        self._failure_count += 1
        self._success_count = 0
        self._last_failure_time = datetime.utcnow()
        
        if self.state == CircuitState.CLOSED:
            if self._failure_count >= self.config.failure_threshold:
                self._transition_to_open()
        
        elif self.state == CircuitState.HALF_OPEN:
            self._transition_to_open()
    
    def _transition_to_open(self) -> None:
        """Transition to OPEN state."""
        self.state = CircuitState.OPEN
        self._last_state_change = datetime.utcnow()
        self._success_count = 0
    
    def _transition_to_half_open(self) -> None:
        """Transition to HALF_OPEN state."""
        self.state = CircuitState.HALF_OPEN
        self._last_state_change = datetime.utcnow()
        self._failure_count = 0
        self._success_count = 0
    
    def _transition_to_closed(self) -> None:
        """Transition to CLOSED state."""
        self.state = CircuitState.CLOSED
        self._last_state_change = datetime.utcnow()
        self._failure_count = 0
        self._success_count = 0
    
    def reset(self) -> None:
        """Manually reset the circuit breaker to CLOSED state."""
        self._transition_to_closed()
    
    def get_metrics(self) -> dict:
        """Get circuit breaker metrics."""
        return {
            "name": self.name,
            "state": self.state,
            "total_calls": self._total_calls,
            "total_successes": self._total_successes,
            "total_failures": self._total_failures,
            "total_rejected": self._total_rejected,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "last_failure_time": self._last_failure_time.isoformat() if self._last_failure_time else None,
            "last_state_change": self._last_state_change.isoformat(),
        }
    
    def __repr__(self) -> str:
        return f"CircuitBreaker(name={self.name}, state={self.state})"


def circuit_breaker(name: str, config: Optional[CircuitBreakerConfig] = None):
    """
    Decorator to wrap a function with circuit breaker protection.
    
    Usage:
        @circuit_breaker("my_service")
        async def call_external_service():
            ...
    """
    if config is None:
        config = CircuitBreakerConfig()
    
    cb = CircuitBreaker(name, config)
    
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            return await cb.call(func, *args, **kwargs)
        return wrapper
    
    return decorator

