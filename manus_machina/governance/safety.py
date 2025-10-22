"""Safety and governance mechanisms."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum
import time


class SafetyCategory(str, Enum):
    """Safety categories for content filtering."""
    HATE = "hate"
    VIOLENCE = "violence"
    SEXUAL = "sexual"
    DANGEROUS = "dangerous"
    HARASSMENT = "harassment"
    SELF_HARM = "self_harm"


class SafetyThreshold(str, Enum):
    """Safety threshold levels."""
    BLOCK_NONE = "BLOCK_NONE"
    BLOCK_LOW_AND_ABOVE = "BLOCK_LOW_AND_ABOVE"
    BLOCK_MEDIUM_AND_ABOVE = "BLOCK_MEDIUM_AND_ABOVE"
    BLOCK_HIGH_AND_ABOVE = "BLOCK_HIGH_AND_ABOVE"


class SafetyResult(BaseModel):
    """Result of safety check."""
    passed: bool
    blocked_categories: List[SafetyCategory] = Field(default_factory=list)
    scores: Dict[SafetyCategory, float] = Field(default_factory=dict)
    reason: Optional[str] = None


class SafetyFilter:
    """
    Safety filter for content moderation.
    
    Filters content based on safety categories and thresholds.
    """
    
    def __init__(
        self,
        categories: Optional[List[SafetyCategory]] = None,
        threshold: SafetyThreshold = SafetyThreshold.BLOCK_MEDIUM_AND_ABOVE
    ):
        """
        Initialize safety filter.
        
        Args:
            categories: Categories to check
            threshold: Threshold for blocking
        """
        self.categories = categories or [
            SafetyCategory.HATE,
            SafetyCategory.VIOLENCE,
            SafetyCategory.SEXUAL,
            SafetyCategory.DANGEROUS
        ]
        self.threshold = threshold
    
    async def check(self, content: str) -> SafetyResult:
        """
        Check content for safety violations.
        
        Args:
            content: Content to check
            
        Returns:
            Safety result
        """
        scores = {}
        blocked = []
        
        # In production, this would call a safety API
        # For now, use simple keyword detection
        for category in self.categories:
            score = self._check_category(content, category)
            scores[category] = score
            
            if self._should_block(score):
                blocked.append(category)
        
        passed = len(blocked) == 0
        reason = None if passed else f"Blocked categories: {', '.join(blocked)}"
        
        return SafetyResult(
            passed=passed,
            blocked_categories=blocked,
            scores=scores,
            reason=reason
        )
    
    def _check_category(self, content: str, category: SafetyCategory) -> float:
        """Check content for a specific category."""
        # Placeholder implementation
        # In production, this would use ML models
        content_lower = content.lower()
        
        keywords = {
            SafetyCategory.HATE: ["hate", "racist", "discriminat"],
            SafetyCategory.VIOLENCE: ["kill", "murder", "attack"],
            SafetyCategory.SEXUAL: ["sexual", "explicit"],
            SafetyCategory.DANGEROUS: ["bomb", "weapon", "poison"]
        }
        
        category_keywords = keywords.get(category, [])
        matches = sum(1 for kw in category_keywords if kw in content_lower)
        
        return min(matches * 0.3, 1.0)
    
    def _should_block(self, score: float) -> bool:
        """Determine if score should trigger blocking."""
        if self.threshold == SafetyThreshold.BLOCK_NONE:
            return False
        elif self.threshold == SafetyThreshold.BLOCK_LOW_AND_ABOVE:
            return score >= 0.25
        elif self.threshold == SafetyThreshold.BLOCK_MEDIUM_AND_ABOVE:
            return score >= 0.5
        elif self.threshold == SafetyThreshold.BLOCK_HIGH_AND_ABOVE:
            return score >= 0.75
        return False


class RateLimiter:
    """
    Rate limiter for API calls.
    
    Limits requests per minute and tokens per minute.
    """
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        tokens_per_minute: int = 100000
    ):
        """
        Initialize rate limiter.
        
        Args:
            requests_per_minute: Max requests per minute
            tokens_per_minute: Max tokens per minute
        """
        self.requests_per_minute = requests_per_minute
        self.tokens_per_minute = tokens_per_minute
        
        self.request_timestamps: List[float] = []
        self.token_usage: List[tuple] = []  # (timestamp, tokens)
    
    def check_request(self) -> bool:
        """Check if a new request is allowed."""
        now = time.time()
        minute_ago = now - 60
        
        # Remove old timestamps
        self.request_timestamps = [
            ts for ts in self.request_timestamps if ts > minute_ago
        ]
        
        # Check limit
        if len(self.request_timestamps) >= self.requests_per_minute:
            return False
        
        self.request_timestamps.append(now)
        return True
    
    def check_tokens(self, tokens: int) -> bool:
        """Check if token usage is within limit."""
        now = time.time()
        minute_ago = now - 60
        
        # Remove old usage
        self.token_usage = [
            (ts, t) for ts, t in self.token_usage if ts > minute_ago
        ]
        
        # Calculate current usage
        current_usage = sum(t for _, t in self.token_usage)
        
        # Check limit
        if current_usage + tokens > self.tokens_per_minute:
            return False
        
        self.token_usage.append((now, tokens))
        return True


class CostTracker:
    """
    Cost tracker for LLM usage.
    
    Tracks costs and enforces budget limits.
    """
    
    def __init__(
        self,
        budget_limit: float,
        alert_threshold: float = 0.8
    ):
        """
        Initialize cost tracker.
        
        Args:
            budget_limit: Maximum budget in USD
            alert_threshold: Threshold for alerts (0-1)
        """
        self.budget_limit = budget_limit
        self.alert_threshold = alert_threshold
        self.total_cost = 0.0
        self.cost_by_model: Dict[str, float] = {}
    
    def track(self, model: str, cost: float) -> None:
        """Track cost for a model."""
        self.total_cost += cost
        
        if model not in self.cost_by_model:
            self.cost_by_model[model] = 0.0
        self.cost_by_model[model] += cost
    
    def check_budget(self) -> bool:
        """Check if budget limit is exceeded."""
        return self.total_cost < self.budget_limit
    
    def should_alert(self) -> bool:
        """Check if alert threshold is reached."""
        return self.total_cost >= (self.budget_limit * self.alert_threshold)
    
    def get_remaining_budget(self) -> float:
        """Get remaining budget."""
        return max(0.0, self.budget_limit - self.total_cost)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cost statistics."""
        return {
            "total_cost": self.total_cost,
            "budget_limit": self.budget_limit,
            "remaining_budget": self.get_remaining_budget(),
            "utilization": self.total_cost / self.budget_limit,
            "cost_by_model": self.cost_by_model
        }

