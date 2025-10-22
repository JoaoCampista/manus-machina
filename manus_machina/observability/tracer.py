"""Distributed tracing for observability."""

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, BatchSpanProcessor


def get_tracer(name: str) -> trace.Tracer:
    """
    Get a distributed tracer.
    
    Args:
        name: Tracer name (usually __name__)
        
    Returns:
        Tracer instance
    """
    # Setup tracer provider
    provider = TracerProvider()
    processor = BatchSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(processor)
    trace.set_tracer_provider(provider)
    
    return trace.get_tracer(name)

