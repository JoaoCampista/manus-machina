"""
Advanced Crew Example - Software Development Team

This example demonstrates a complete software development workflow
with multiple specialized agents working together.
"""

import os
import asyncio
import sys

sys.path.insert(0, '/home/ubuntu/manus_machina')

from manus_machina.core.simple_agent import SimpleAgent, SimpleAgentConfig


class SoftwareDevCrew:
    """A crew of agents for software development tasks."""
    
    def __init__(self, api_key: str):
        """Initialize the development crew."""
        self.api_key = api_key
        
        # Create specialized agents
        self.product_manager = SimpleAgent(
            config=SimpleAgentConfig(
                name="product_manager",
                role="Product Manager",
                goal="Define product requirements and user stories",
                backstory="Experienced PM with deep understanding of user needs and business goals."
            ),
            api_key=api_key
        )
        
        self.architect = SimpleAgent(
            config=SimpleAgentConfig(
                name="architect",
                role="Software Architect",
                goal="Design scalable and maintainable system architectures",
                backstory="Senior architect specializing in distributed systems and microservices."
            ),
            api_key=api_key
        )
        
        self.backend_dev = SimpleAgent(
            config=SimpleAgentConfig(
                name="backend_developer",
                role="Backend Developer",
                goal="Implement robust backend services and APIs",
                backstory="Expert backend developer proficient in Python, Node.js, and database design."
            ),
            api_key=api_key
        )
        
        self.frontend_dev = SimpleAgent(
            config=SimpleAgentConfig(
                name="frontend_developer",
                role="Frontend Developer",
                goal="Build responsive and user-friendly interfaces",
                backstory="Frontend specialist with expertise in React, Vue, and modern web technologies."
            ),
            api_key=api_key
        )
        
        self.qa_engineer = SimpleAgent(
            config=SimpleAgentConfig(
                name="qa_engineer",
                role="QA Engineer",
                goal="Ensure software quality through comprehensive testing",
                backstory="QA expert with experience in test automation and quality assurance."
            ),
            api_key=api_key
        )
        
        self.devops = SimpleAgent(
            config=SimpleAgentConfig(
                name="devops_engineer",
                role="DevOps Engineer",
                goal="Design deployment pipelines and infrastructure",
                backstory="DevOps specialist with expertise in CI/CD, Docker, Kubernetes, and cloud platforms."
            ),
            api_key=api_key
        )
    
    async def develop_feature(self, feature_description: str):
        """
        Complete workflow for developing a new feature.
        
        Args:
            feature_description: Description of the feature to develop
        """
        print("\n" + "=" * 100)
        print(f"🚀 DEVELOPING FEATURE: {feature_description}")
        print("=" * 100)
        
        # Phase 1: Requirements
        print("\n📋 PHASE 1: Requirements Analysis")
        print("-" * 100)
        
        requirements_result = await self.product_manager.execute(
            task=f"Analyze this feature request and create detailed requirements: {feature_description}. Include user stories, acceptance criteria, and success metrics."
        )
        
        print(f"\n✅ Requirements defined by {requirements_result['agent']}")
        print(requirements_result['response'])
        
        # Phase 2: Architecture
        print("\n\n🏗️ PHASE 2: Architecture Design")
        print("-" * 100)
        
        architecture_result = await self.architect.execute(
            task="Based on these requirements, design the system architecture. Include components, data flow, APIs, and technology stack.",
            context={"requirements": requirements_result['response']}
        )
        
        print(f"\n✅ Architecture designed by {architecture_result['agent']}")
        print(architecture_result['response'])
        
        # Phase 3: Backend Implementation
        print("\n\n⚙️ PHASE 3: Backend Implementation")
        print("-" * 100)
        
        backend_result = await self.backend_dev.execute(
            task="Create the backend implementation plan. Include API endpoints, database schema, and key code structures.",
            context={
                "requirements": requirements_result['response'],
                "architecture": architecture_result['response']
            }
        )
        
        print(f"\n✅ Backend plan created by {backend_result['agent']}")
        print(backend_result['response'])
        
        # Phase 4: Frontend Implementation
        print("\n\n🎨 PHASE 4: Frontend Implementation")
        print("-" * 100)
        
        frontend_result = await self.frontend_dev.execute(
            task="Create the frontend implementation plan. Include UI components, state management, and API integration.",
            context={
                "requirements": requirements_result['response'],
                "architecture": architecture_result['response'],
                "backend": backend_result['response']
            }
        )
        
        print(f"\n✅ Frontend plan created by {frontend_result['agent']}")
        print(frontend_result['response'])
        
        # Phase 5: QA Strategy
        print("\n\n🧪 PHASE 5: QA & Testing Strategy")
        print("-" * 100)
        
        qa_result = await self.qa_engineer.execute(
            task="Create a comprehensive testing strategy. Include unit tests, integration tests, and test scenarios.",
            context={
                "requirements": requirements_result['response'],
                "backend": backend_result['response'],
                "frontend": frontend_result['response']
            }
        )
        
        print(f"\n✅ QA strategy created by {qa_result['agent']}")
        print(qa_result['response'])
        
        # Phase 6: Deployment
        print("\n\n🚢 PHASE 6: Deployment Strategy")
        print("-" * 100)
        
        devops_result = await self.devops.execute(
            task="Create the deployment and CI/CD strategy. Include containerization, orchestration, and monitoring.",
            context={
                "architecture": architecture_result['response'],
                "backend": backend_result['response'],
                "frontend": frontend_result['response']
            }
        )
        
        print(f"\n✅ Deployment strategy created by {devops_result['agent']}")
        print(devops_result['response'])
        
        # Summary
        print("\n\n" + "=" * 100)
        print("📊 DEVELOPMENT WORKFLOW SUMMARY")
        print("=" * 100)
        
        print("\n✅ All phases completed successfully!")
        print("\nPhases executed:")
        print("  1. ✓ Requirements Analysis (Product Manager)")
        print("  2. ✓ Architecture Design (Architect)")
        print("  3. ✓ Backend Implementation (Backend Developer)")
        print("  4. ✓ Frontend Implementation (Frontend Developer)")
        print("  5. ✓ QA & Testing Strategy (QA Engineer)")
        print("  6. ✓ Deployment Strategy (DevOps Engineer)")
        
        return {
            "requirements": requirements_result,
            "architecture": architecture_result,
            "backend": backend_result,
            "frontend": frontend_result,
            "qa": qa_result,
            "devops": devops_result
        }


async def main():
    """Run the advanced crew example."""
    print("\n")
    print("╔" + "=" * 98 + "╗")
    print("║" + " " * 25 + "MANUS MACHINA - ADVANCED CREW EXAMPLE" + " " * 36 + "║")
    print("║" + " " * 30 + "Software Development Team" + " " * 43 + "║")
    print("╚" + "=" * 98 + "╝")
    
    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("\n❌ ERROR: GOOGLE_API_KEY not found")
        return
    
    # Create crew
    crew = SoftwareDevCrew(api_key=api_key)
    
    # Example feature
    feature = "User authentication system with email/password login, social login (Google, GitHub), and two-factor authentication"
    
    # Execute workflow
    try:
        result = await crew.develop_feature(feature)
        
        print("\n\n" + "=" * 100)
        print("🎉 FEATURE DEVELOPMENT COMPLETED!")
        print("=" * 100)
        
    except Exception as e:
        print(f"\n\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Set API key
    os.environ["GOOGLE_API_KEY"] = "AIzaSyDnPpDi28kiO3lqxOVqfopCxgaOxSQYHFM"
    
    # Run example
    asyncio.run(main())

