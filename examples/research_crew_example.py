"""
Research Crew Example - Academic Research Team

This example demonstrates a research workflow with agents
specialized in different aspects of academic research.
"""

import os
import asyncio
import sys

sys.path.insert(0, '/home/ubuntu/manus_machina')

from manus_machina.core.simple_agent import SimpleAgent, SimpleAgentConfig


class ResearchCrew:
    """A crew of agents for academic research tasks."""
    
    def __init__(self, api_key: str):
        """Initialize the research crew."""
        self.api_key = api_key
        
        # Create specialized research agents
        self.literature_reviewer = SimpleAgent(
            config=SimpleAgentConfig(
                name="literature_reviewer",
                role="Literature Review Specialist",
                goal="Conduct comprehensive literature reviews and identify key research",
                backstory="PhD researcher with expertise in systematic literature reviews and meta-analysis."
            ),
            api_key=api_key
        )
        
        self.methodology_expert = SimpleAgent(
            config=SimpleAgentConfig(
                name="methodology_expert",
                role="Research Methodology Expert",
                goal="Design rigorous research methodologies and experimental designs",
                backstory="Senior researcher specializing in quantitative and qualitative research methods."
            ),
            api_key=api_key
        )
        
        self.data_analyst = SimpleAgent(
            config=SimpleAgentConfig(
                name="data_analyst",
                role="Data Analysis Specialist",
                goal="Analyze research data and extract meaningful insights",
                backstory="Statistician with expertise in advanced data analysis and visualization."
            ),
            api_key=api_key
        )
        
        self.academic_writer = SimpleAgent(
            config=SimpleAgentConfig(
                name="academic_writer",
                role="Academic Writer",
                goal="Write clear, rigorous academic papers",
                backstory="Published researcher skilled in academic writing and scientific communication."
            ),
            api_key=api_key
        )
        
        self.peer_reviewer = SimpleAgent(
            config=SimpleAgentConfig(
                name="peer_reviewer",
                role="Peer Reviewer",
                goal="Provide constructive peer review feedback",
                backstory="Experienced journal reviewer with high standards for research quality."
            ),
            api_key=api_key
        )
    
    async def conduct_research(self, research_topic: str):
        """
        Complete research workflow from literature review to paper writing.
        
        Args:
            research_topic: The research topic to investigate
        """
        print("\n" + "=" * 100)
        print(f"🔬 RESEARCH PROJECT: {research_topic}")
        print("=" * 100)
        
        # Phase 1: Literature Review
        print("\n📚 PHASE 1: Literature Review")
        print("-" * 100)
        
        literature_result = await self.literature_reviewer.execute(
            task=f"Conduct a literature review on: {research_topic}. Identify key papers, main findings, research gaps, and theoretical frameworks."
        )
        
        print(f"\n✅ Literature review completed by {literature_result['agent']}")
        print(literature_result['response'][:1000] + "...\n")
        
        # Phase 2: Methodology Design
        print("\n🔬 PHASE 2: Research Methodology Design")
        print("-" * 100)
        
        methodology_result = await self.methodology_expert.execute(
            task="Based on the literature review, design a research methodology. Include research questions, hypotheses, data collection methods, and analysis approach.",
            context={"literature_review": literature_result['response']}
        )
        
        print(f"\n✅ Methodology designed by {methodology_result['agent']}")
        print(methodology_result['response'][:1000] + "...\n")
        
        # Phase 3: Data Analysis Plan
        print("\n📊 PHASE 3: Data Analysis Strategy")
        print("-" * 100)
        
        analysis_result = await self.data_analyst.execute(
            task="Create a detailed data analysis plan. Include statistical methods, visualization approaches, and interpretation guidelines.",
            context={
                "literature_review": literature_result['response'],
                "methodology": methodology_result['response']
            }
        )
        
        print(f"\n✅ Analysis plan created by {analysis_result['agent']}")
        print(analysis_result['response'][:1000] + "...\n")
        
        # Phase 4: Paper Writing
        print("\n✍️ PHASE 4: Academic Paper Writing")
        print("-" * 100)
        
        paper_result = await self.academic_writer.execute(
            task="Write an academic paper abstract and introduction based on the research. Follow academic writing conventions and include clear research objectives.",
            context={
                "literature_review": literature_result['response'],
                "methodology": methodology_result['response'],
                "analysis_plan": analysis_result['response']
            }
        )
        
        print(f"\n✅ Paper draft created by {paper_result['agent']}")
        print(paper_result['response'][:1000] + "...\n")
        
        # Phase 5: Peer Review
        print("\n🔍 PHASE 5: Peer Review")
        print("-" * 100)
        
        review_result = await self.peer_reviewer.execute(
            task="Provide a comprehensive peer review of this research. Evaluate: 1) Novelty and significance, 2) Methodology rigor, 3) Analysis appropriateness, 4) Writing quality, 5) Recommendations for improvement.",
            context={
                "literature_review": literature_result['response'],
                "methodology": methodology_result['response'],
                "paper": paper_result['response']
            }
        )
        
        print(f"\n✅ Peer review completed by {review_result['agent']}")
        print(review_result['response'])
        
        # Summary
        print("\n\n" + "=" * 100)
        print("📊 RESEARCH WORKFLOW SUMMARY")
        print("=" * 100)
        
        print("\n✅ All research phases completed!")
        print("\nPhases executed:")
        print("  1. ✓ Literature Review")
        print("  2. ✓ Methodology Design")
        print("  3. ✓ Data Analysis Strategy")
        print("  4. ✓ Academic Paper Writing")
        print("  5. ✓ Peer Review")
        
        return {
            "literature_review": literature_result,
            "methodology": methodology_result,
            "analysis": analysis_result,
            "paper": paper_result,
            "review": review_result
        }


async def main():
    """Run the research crew example."""
    print("\n")
    print("╔" + "=" * 98 + "╗")
    print("║" + " " * 28 + "MANUS MACHINA - RESEARCH CREW" + " " * 41 + "║")
    print("║" + " " * 32 + "Academic Research Team" + " " * 45 + "║")
    print("╚" + "=" * 98 + "╝")
    
    # Get API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("\n❌ ERROR: GOOGLE_API_KEY not found")
        return
    
    # Create crew
    crew = ResearchCrew(api_key=api_key)
    
    # Example research topic
    topic = "The impact of large language models on software development productivity and code quality"
    
    # Execute workflow
    try:
        result = await crew.conduct_research(topic)
        
        print("\n\n" + "=" * 100)
        print("🎉 RESEARCH PROJECT COMPLETED!")
        print("=" * 100)
        print("\nThe research workflow has been successfully executed.")
        print("All phases from literature review to peer review are complete.")
        
    except Exception as e:
        print(f"\n\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Set API key
    os.environ["GOOGLE_API_KEY"] = "AIzaSyDnPpDi28kiO3lqxOVqfopCxgaOxSQYHFM"
    
    # Run example
    asyncio.run(main())

