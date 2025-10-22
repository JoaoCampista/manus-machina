"""
Complete example demonstrating all major features of Manus Machina.

This example shows:
- Agent creation with resilience features
- Vector memory integration
- Multi-model routing
- Guardrails and safety filters
- Evaluation framework
- Governance (rate limiting, cost tracking)
"""

import asyncio
from manus_machina.core.agent import Agent, AgentConfig
from manus_machina.core.crew import Crew, CrewConfig, ProcessType
from manus_machina.memory.vector_store import VectorMemory, VectorStoreProvider
from manus_machina.models.router import ModelRouter, RoutingStrategy
from manus_machina.governance.safety import SafetyFilter, RateLimiter, CostTracker
from manus_machina.evaluation.framework import Evaluator, EvalSet, EvaluationCriteria
from manus_machina.guardrails.guards import PromptInjectionGuard, ToxicityGuard
from manus_machina.guardrails.engine import GuardrailEngine


async def main():
    print("=" * 80)
    print("Manus Machina v2.0 - Complete Example")
    print("=" * 80)
    
    # 1. Setup Vector Memory
    print("\n1. Setting up Vector Memory...")
    memory = VectorMemory(
        provider=VectorStoreProvider.FAISS,
        index_name="demo_memory",
        embedding_model="text-embedding-3-large"
    )
    
    # Add some initial knowledge
    await memory.add(
        content="Paris is the capital of France.",
        metadata={"type": "fact", "category": "geography"}
    )
    await memory.add(
        content="Machine learning is a subset of artificial intelligence.",
        metadata={"type": "fact", "category": "technology"}
    )
    print("✓ Vector memory initialized with sample data")
    
    # 2. Setup Multi-Model Router
    print("\n2. Setting up Multi-Model Router...")
    router = ModelRouter(
        default="gpt-4.1-mini",
        fallbacks=["claude-3.7-sonnet", "gemini-2.5-flash"],
        routing_strategy=RoutingStrategy.COST_OPTIMIZED
    )
    print("✓ Model router configured with 3 models")
    
    # 3. Setup Guardrails
    print("\n3. Setting up Guardrails...")
    guardrail_engine = GuardrailEngine()
    guardrail_engine.add_guard(PromptInjectionGuard())
    guardrail_engine.add_guard(ToxicityGuard(threshold=0.7))
    print("✓ Guardrails configured (Prompt Injection, Toxicity)")
    
    # 4. Setup Governance
    print("\n4. Setting up Governance...")
    safety_filter = SafetyFilter(
        categories=["hate", "violence", "sexual"],
        threshold="BLOCK_MEDIUM_AND_ABOVE"
    )
    rate_limiter = RateLimiter(
        requests_per_minute=60,
        tokens_per_minute=100000
    )
    cost_tracker = CostTracker(
        budget_limit=10.0,
        alert_threshold=0.8
    )
    print("✓ Governance configured (Safety, Rate Limiting, Cost Tracking)")
    
    # 5. Create Agents
    print("\n5. Creating Agents...")
    
    researcher = Agent(
        config=AgentConfig(
            name="researcher",
            role="Research Specialist",
            goal="Find and analyze information",
            backstory="Expert at finding relevant information",
            memory=memory,
            model_router=router,
            guardrail_engine=guardrail_engine,
            safety_filter=safety_filter,
            rate_limiter=rate_limiter,
            enable_retry=True,
            enable_circuit_breaker=True
        )
    )
    
    writer = Agent(
        config=AgentConfig(
            name="writer",
            role="Content Writer",
            goal="Create engaging content",
            backstory="Expert at writing clear and concise content",
            memory=memory,
            model_router=router,
            guardrail_engine=guardrail_engine,
            safety_filter=safety_filter,
            rate_limiter=rate_limiter,
            enable_retry=True,
            enable_circuit_breaker=True
        )
    )
    
    print("✓ Created 2 agents (researcher, writer)")
    
    # 6. Create Crew
    print("\n6. Creating Crew...")
    crew = Crew(
        config=CrewConfig(
            name="content_team",
            agents=[researcher, writer],
            process=ProcessType.SEQUENTIAL,
            cost_tracker=cost_tracker
        )
    )
    print("✓ Crew created with sequential process")
    
    # 7. Execute Task
    print("\n7. Executing Task...")
    print("Task: 'Write a brief article about machine learning'")
    
    try:
        result = await crew.execute(
            task="Write a brief article about machine learning"
        )
        print(f"\n✓ Task completed successfully!")
        print(f"\nResult:\n{result}")
    except Exception as e:
        print(f"\n✗ Task failed: {str(e)}")
    
    # 8. Check Governance Stats
    print("\n8. Governance Statistics:")
    print(f"   - Remaining budget: ${cost_tracker.get_remaining_budget():.2f}")
    print(f"   - Total cost: ${cost_tracker.total_cost:.2f}")
    print(f"   - Budget utilization: {cost_tracker.total_cost / cost_tracker.budget_limit * 100:.1f}%")
    
    # 9. Model Router Stats
    print("\n9. Model Router Statistics:")
    stats = router.get_stats()
    for model, model_stats in stats.items():
        print(f"   - {model}:")
        print(f"     • Total calls: {model_stats['total_calls']}")
        print(f"     • Success rate: {model_stats['successful_calls'] / max(model_stats['total_calls'], 1) * 100:.1f}%")
        print(f"     • Total cost: ${model_stats['total_cost']:.4f}")
    
    # 10. Evaluation (if eval set exists)
    print("\n10. Running Evaluation...")
    try:
        eval_set = EvalSet.from_file("examples/sample_eval_set.json")
        
        evaluator = Evaluator(
            agent=researcher,
            eval_set=eval_set,
            criteria=[
                EvaluationCriteria.TOOL_TRAJECTORY_MATCH,
                EvaluationCriteria.RESPONSE_MATCH,
                EvaluationCriteria.SAFETY_SCORE
            ]
        )
        
        eval_results = await evaluator.run()
        
        print(f"\n✓ Evaluation completed!")
        for result in eval_results:
            status = "✅ PASSED" if result.passed else "❌ FAILED"
            print(f"   - {result.test_case_name}: {status}")
            print(f"     Scores: {result.scores}")
            
    except FileNotFoundError:
        print("   ⚠ Eval set not found, skipping evaluation")
    except Exception as e:
        print(f"   ✗ Evaluation failed: {str(e)}")
    
    print("\n" + "=" * 80)
    print("Demo completed!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(main())

