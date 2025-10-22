"""Evaluation framework for agents."""

from typing import Any, Dict, List, Optional, Callable
from pydantic import BaseModel, Field
from enum import Enum
import json


class EvaluationCriteria(str, Enum):
    """Built-in evaluation criteria."""
    TOOL_TRAJECTORY_MATCH = "tool_trajectory_avg_score"
    RESPONSE_MATCH = "response_match_score"
    FINAL_RESPONSE_MATCH = "final_response_match_v2"
    RUBRIC_RESPONSE_QUALITY = "rubric_based_final_response_quality_v1"
    RUBRIC_TOOL_QUALITY = "rubric_based_tool_use_quality_v1"
    HALLUCINATION_DETECTION = "hallucinations_v1"
    SAFETY_SCORE = "safety_v1"


class Turn(BaseModel):
    """A single turn in a conversation."""
    user_content: str = Field(..., description="User query")
    expected_tool_trajectory: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Expected tool calls"
    )
    expected_intermediate_responses: List[str] = Field(
        default_factory=list,
        description="Expected intermediate agent responses"
    )
    expected_final_response: str = Field(..., description="Expected final response")


class TestCase(BaseModel):
    """A single test case for evaluation."""
    name: str = Field(..., description="Test case name")
    description: Optional[str] = Field(None, description="Test case description")
    turns: List[Turn] = Field(..., description="Conversation turns")
    initial_state: Dict[str, Any] = Field(
        default_factory=dict,
        description="Initial session state"
    )
    
    @classmethod
    def from_file(cls, path: str) -> "TestCase":
        """Load test case from JSON file."""
        with open(path, 'r') as f:
            data = json.load(f)
        return cls(**data)


class EvalSet(BaseModel):
    """A set of evaluation cases."""
    name: str = Field(..., description="Eval set name")
    description: Optional[str] = Field(None, description="Eval set description")
    test_cases: List[TestCase] = Field(..., description="Test cases")
    
    @classmethod
    def from_file(cls, path: str) -> "EvalSet":
        """Load eval set from JSON file."""
        with open(path, 'r') as f:
            data = json.load(f)
        return cls(**data)


class EvaluationResult(BaseModel):
    """Result of a single evaluation."""
    test_case_name: str
    passed: bool
    scores: Dict[str, float] = Field(default_factory=dict)
    details: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)


class Evaluator:
    """
    Evaluator for agent performance.
    
    Evaluates agents against test cases and eval sets using various criteria.
    """
    
    def __init__(
        self,
        agent: Any,
        eval_set: Optional[EvalSet] = None,
        test_case: Optional[TestCase] = None,
        criteria: Optional[List[str]] = None,
        thresholds: Optional[Dict[str, float]] = None
    ):
        """
        Initialize evaluator.
        
        Args:
            agent: Agent to evaluate
            eval_set: Eval set to use
            test_case: Single test case to use
            criteria: List of criteria to evaluate
            thresholds: Threshold for each criterion
        """
        self.agent = agent
        self.eval_set = eval_set
        self.test_case = test_case
        
        # Default criteria
        self.criteria = criteria or [
            EvaluationCriteria.TOOL_TRAJECTORY_MATCH,
            EvaluationCriteria.RESPONSE_MATCH
        ]
        
        # Default thresholds
        self.thresholds = thresholds or {
            EvaluationCriteria.TOOL_TRAJECTORY_MATCH: 1.0,
            EvaluationCriteria.RESPONSE_MATCH: 0.8,
            EvaluationCriteria.FINAL_RESPONSE_MATCH: 0.7,
            EvaluationCriteria.HALLUCINATION_DETECTION: 0.9,
            EvaluationCriteria.SAFETY_SCORE: 0.9
        }
    
    async def run(self) -> List[EvaluationResult]:
        """
        Run evaluation.
        
        Returns:
            List of evaluation results
        """
        results = []
        
        if self.test_case:
            result = await self._evaluate_test_case(self.test_case)
            results.append(result)
        
        if self.eval_set:
            for test_case in self.eval_set.test_cases:
                result = await self._evaluate_test_case(test_case)
                results.append(result)
        
        return results
    
    async def _evaluate_test_case(self, test_case: TestCase) -> EvaluationResult:
        """Evaluate a single test case."""
        scores = {}
        details = {}
        errors = []
        
        try:
            # Run agent for each turn
            for turn in test_case.turns:
                # Execute agent
                result = await self.agent.execute(
                    task=turn.user_content,
                    context=test_case.initial_state
                )
                
                # Evaluate each criterion
                for criterion in self.criteria:
                    score = await self._evaluate_criterion(
                        criterion,
                        turn,
                        result
                    )
                    scores[criterion] = score
                    
                    # Check threshold
                    threshold = self.thresholds.get(criterion, 0.0)
                    if score < threshold:
                        errors.append(
                            f"{criterion} score {score} below threshold {threshold}"
                        )
            
            passed = len(errors) == 0
            
        except Exception as e:
            passed = False
            errors.append(f"Execution error: {str(e)}")
        
        return EvaluationResult(
            test_case_name=test_case.name,
            passed=passed,
            scores=scores,
            details=details,
            errors=errors
        )
    
    async def _evaluate_criterion(
        self,
        criterion: str,
        turn: Turn,
        result: Any
    ) -> float:
        """Evaluate a single criterion."""
        if criterion == EvaluationCriteria.TOOL_TRAJECTORY_MATCH:
            return self._evaluate_tool_trajectory(turn, result)
        
        elif criterion == EvaluationCriteria.RESPONSE_MATCH:
            return self._evaluate_response_match(turn, result)
        
        elif criterion == EvaluationCriteria.FINAL_RESPONSE_MATCH:
            return await self._evaluate_final_response_llm(turn, result)
        
        elif criterion == EvaluationCriteria.HALLUCINATION_DETECTION:
            return await self._evaluate_hallucination(turn, result)
        
        elif criterion == EvaluationCriteria.SAFETY_SCORE:
            return await self._evaluate_safety(turn, result)
        
        return 0.0
    
    def _evaluate_tool_trajectory(self, turn: Turn, result: Any) -> float:
        """Evaluate tool trajectory match."""
        expected = turn.expected_tool_trajectory
        actual = result.get("tool_calls", [])
        
        if not expected:
            return 1.0 if not actual else 0.0
        
        if len(expected) != len(actual):
            return 0.0
        
        matches = 0
        for exp, act in zip(expected, actual):
            if exp.get("name") == act.get("name"):
                matches += 1
        
        return matches / len(expected)
    
    def _evaluate_response_match(self, turn: Turn, result: Any) -> float:
        """Evaluate response match using ROUGE."""
        expected = turn.expected_final_response
        actual = result.get("response", "")
        
        # Simple word overlap (ROUGE-1 approximation)
        expected_words = set(expected.lower().split())
        actual_words = set(actual.lower().split())
        
        if not expected_words:
            return 1.0
        
        overlap = len(expected_words & actual_words)
        return overlap / len(expected_words)
    
    async def _evaluate_final_response_llm(self, turn: Turn, result: Any) -> float:
        """Evaluate final response using LLM as judge."""
        # This would use an LLM to judge semantic similarity
        # Placeholder implementation
        return 0.8
    
    async def _evaluate_hallucination(self, turn: Turn, result: Any) -> float:
        """Evaluate hallucination (groundedness)."""
        # This would check if response is grounded in context
        # Placeholder implementation
        return 0.9
    
    async def _evaluate_safety(self, turn: Turn, result: Any) -> float:
        """Evaluate safety of response."""
        # This would check for unsafe content
        # Placeholder implementation
        return 1.0

