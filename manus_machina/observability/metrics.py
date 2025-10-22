"""Metrics collection for observability."""

from typing import Dict, List, Optional
from prometheus_client import Counter, Histogram, Gauge
from contextlib import contextmanager
import time


class MetricsCollector:
    """
    Metrics collector using Prometheus.
    
    Collects and exports metrics for monitoring.
    """
    
    def __init__(self):
        # Define metrics
        self.agent_executions = Counter(
            'agent_executions_total',
            'Total number of agent executions',
            ['agent_name', 'status']
        )
        
        self.agent_execution_duration = Histogram(
            'agent_execution_duration_seconds',
            'Agent execution duration in seconds',
            ['agent_name']
        )
        
        self.circuit_breaker_state = Gauge(
            'circuit_breaker_state',
            'Circuit breaker state (0=closed, 1=open, 2=half_open)',
            ['circuit_breaker_name']
        )
        
        self.retry_attempts = Counter(
            'retry_attempts_total',
            'Total number of retry attempts',
            ['retry_policy_name']
        )
        
        self.guardrail_violations = Counter(
            'guardrail_violations_total',
            'Total number of guardrail violations',
            ['guard_name', 'guard_type']
        )
    
    def increment(self, metric_name: str, tags: Optional[Dict[str, str]] = None) -> None:
        """Increment a counter metric."""
        if metric_name == "agent.executions":
            self.agent_executions.labels(**tags or {}).inc()
        elif metric_name == "retry.attempts":
            self.retry_attempts.labels(**tags or {}).inc()
        elif metric_name == "guardrail.violations":
            self.guardrail_violations.labels(**tags or {}).inc()
    
    @contextmanager
    def timer(self, metric_name: str, tags: Optional[Dict[str, str]] = None):
        """Context manager for timing operations."""
        start_time = time.time()
        try:
            yield
        finally:
            duration = time.time() - start_time
            if metric_name == "agent.execution_time":
                self.agent_execution_duration.labels(**tags or {}).observe(duration)
    
    def set_gauge(self, metric_name: str, value: float, tags: Optional[Dict[str, str]] = None) -> None:
        """Set a gauge metric value."""
        if metric_name == "circuit_breaker.state":
            self.circuit_breaker_state.labels(**tags or {}).set(value)

