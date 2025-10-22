"""
Example: Research Workflow with Manus Machina

This example demonstrates:
- Creating agents with different roles
- Using resilience patterns (circuit breaker, retry)
- Applying guardrails for safety
- Orchestrating a multi-agent workflow
- Using saga pattern for distributed transactions
"""

import asyncio
from manus_machina import (
    Agent,
    AgentConfig,
    Saga,
    CircuitBreaker,
    CircuitBreakerConfig,
    RetryPolicy,
    RetryConfig,
    BackoffStrategy,
    JitterType,
    GuardrailEngine,
    GuardrailConfig,
    PromptInjectionGuard,
    ToxicityGuard,
    FactualityGuard,
    State,
)


# Simulated LLM client
class MockLLMClient:
    """Mock LLM client for demonstration."""
    
    async def complete(self, prompt: str, **kwargs) -> str:
        """Simulate LLM completion."""
        await asyncio.sleep(0.1)  # Simulate API call
        return f"Response to: {prompt[:50]}..."


async def main():
    print("=" * 80)
    print("Manus Machina - Research Workflow Example")
    print("=" * 80)
    
    # 1. Setup Guardrail Engine
    print("\n1. Setting up Guardrail Engine...")
    guardrail_engine = GuardrailEngine(GuardrailConfig(fail_fast=True))
    
    # Register guards
    guardrail_engine.register_input_guard(
        PromptInjectionGuard("prompt_injection")
    )
    guardrail_engine.register_output_guard(
        ToxicityGuard("toxicity", config={"threshold": 0.3})
    )
    guardrail_engine.register_output_guard(
        FactualityGuard("factuality")
    )
    
    print(f"   ✓ Registered {len(guardrail_engine.input_guards)} input guards")
    print(f"   ✓ Registered {len(guardrail_engine.output_guards)} output guards")
    
    # 2. Create Agents
    print("\n2. Creating Agents...")
    
    # Research Agent
    researcher_config = AgentConfig(
        name="researcher",
        role="Senior Research Analyst",
        goal="Conduct thorough research on given topics",
        backstory="Expert in academic research with 10+ years experience",
        llm_model="gpt-4.1-mini",
        verbose=True,
        enable_retry=True,
        enable_circuit_breaker=True,
        enable_guardrails=True,
        input_guards=["prompt_injection"],
        output_guards=["toxicity", "factuality"],
    )
    researcher = Agent(config=researcher_config)
    researcher.set_llm_client(MockLLMClient())
    researcher.set_guardrail_engine(guardrail_engine)
    
    print(f"   ✓ Created agent: {researcher.config.name} ({researcher.config.role})")
    
    # Writer Agent
    writer_config = AgentConfig(
        name="writer",
        role="Technical Writer",
        goal="Write clear and engaging content",
        backstory="Experienced technical writer specializing in AI topics",
        llm_model="gpt-4.1-mini",
        verbose=True,
        enable_guardrails=True,
        output_guards=["toxicity"],
    )
    writer = Agent(config=writer_config)
    writer.set_llm_client(MockLLMClient())
    writer.set_guardrail_engine(guardrail_engine)
    
    print(f"   ✓ Created agent: {writer.config.name} ({writer.config.role})")
    
    # 3. Setup Resilience Patterns
    print("\n3. Setting up Resilience Patterns...")
    
    # Circuit Breaker for external API calls
    api_circuit_breaker = CircuitBreaker(
        name="research_api",
        config=CircuitBreakerConfig(
            failure_threshold=3,
            success_threshold=2,
            timeout_seconds=30.0
        )
    )
    print(f"   ✓ Circuit Breaker: {api_circuit_breaker.name} (state: {api_circuit_breaker.state})")
    
    # Retry Policy with exponential backoff
    retry_policy = RetryPolicy(
        name="api_retry",
        config=RetryConfig(
            max_attempts=5,
            base_delay=1.0,
            max_delay=30.0,
            backoff_strategy=BackoffStrategy.EXPONENTIAL,
            jitter_type=JitterType.FULL
        )
    )
    print(f"   ✓ Retry Policy: {retry_policy.name} (max_attempts: {retry_policy.config.max_attempts})")
    
    # 4. Execute Research Workflow
    print("\n4. Executing Research Workflow...")
    
    try:
        # Research phase
        print("\n   Phase 1: Research")
        research_result = await researcher.execute(
            task="Research the latest developments in multi-agent AI systems",
            context={"sources": ["arxiv.org", "papers.nips.cc"]}
        )
        print(f"   ✓ Research completed: {research_result[:100]}...")
        
        # Writing phase
        print("\n   Phase 2: Writing")
        article_result = await writer.execute(
            task="Write a summary article based on the research",
            context={"research": research_result}
        )
        print(f"   ✓ Article completed: {article_result[:100]}...")
        
    except Exception as e:
        print(f"   ✗ Workflow failed: {e}")
    
    # 5. Demonstrate Saga Pattern
    print("\n5. Demonstrating Saga Pattern (Distributed Transaction)...")
    
    async def book_flight(context):
        """Simulate booking a flight."""
        print("   → Booking flight...")
        await asyncio.sleep(0.1)
        context["flight_booking_id"] = "FL123"
        return "Flight booked successfully"
    
    async def cancel_flight(context):
        """Compensate: cancel flight booking."""
        print("   ← Canceling flight...")
        await asyncio.sleep(0.1)
        return "Flight booking canceled"
    
    async def book_hotel(context):
        """Simulate booking a hotel."""
        print("   → Booking hotel...")
        await asyncio.sleep(0.1)
        context["hotel_booking_id"] = "HT456"
        return "Hotel booked successfully"
    
    async def cancel_hotel(context):
        """Compensate: cancel hotel booking."""
        print("   ← Canceling hotel...")
        await asyncio.sleep(0.1)
        return "Hotel booking canceled"
    
    async def charge_payment(context):
        """Simulate charging payment."""
        print("   → Charging payment...")
        await asyncio.sleep(0.1)
        # Simulate failure
        raise Exception("Payment declined")
    
    async def refund_payment(context):
        """Compensate: refund payment."""
        print("   ← Refunding payment...")
        await asyncio.sleep(0.1)
        return "Payment refunded"
    
    # Create saga
    booking_saga = Saga(name="trip_booking")
    booking_saga.add_step("book_flight", book_flight, cancel_flight)
    booking_saga.add_step("book_hotel", book_hotel, cancel_hotel)
    booking_saga.add_step("charge_payment", charge_payment, refund_payment)
    
    try:
        result = await booking_saga.execute({"user_id": "user123"})
        print(f"   ✓ Saga completed: {result}")
    except Exception as e:
        print(f"   ✗ Saga failed: {e}")
        print(f"   Status: {booking_saga.status}")
    
    # 6. Display Metrics
    print("\n6. Metrics Summary")
    print("=" * 80)
    
    print("\nCircuit Breaker Metrics:")
    cb_metrics = api_circuit_breaker.get_metrics()
    for key, value in cb_metrics.items():
        print(f"   {key}: {value}")
    
    print("\nRetry Policy Metrics:")
    retry_metrics = retry_policy.get_metrics()
    for key, value in retry_metrics.items():
        print(f"   {key}: {value}")
    
    print("\nGuardrail Engine Metrics:")
    guard_metrics = guardrail_engine.get_metrics()
    for key, value in guard_metrics.items():
        print(f"   {key}: {value}")
    
    print("\nSaga Status:")
    saga_status = booking_saga.get_status()
    print(f"   Name: {saga_status['name']}")
    print(f"   Status: {saga_status['status']}")
    print(f"   Steps: {len(saga_status['steps'])}")
    for step in saga_status['steps']:
        print(f"      - {step['name']}: {step['status']}")
    
    print("\n" + "=" * 80)
    print("Example completed!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

