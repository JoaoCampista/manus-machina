"""Guardrail implementations for input/output validation."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from abc import ABC, abstractmethod
import re


class GuardResult(BaseModel):
    """Result of a guard check."""
    
    passed: bool = Field(..., description="Whether the guard passed")
    message: Optional[str] = Field(None, description="Message if guard failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class BaseGuard(ABC):
    """Base class for all guards."""
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        self.name = name
        self.config = config or {}
    
    @abstractmethod
    async def validate(self, content: str, context: Optional[Dict[str, Any]] = None) -> GuardResult:
        """
        Validate content against the guard.
        
        Args:
            content: Content to validate
            context: Additional context
            
        Returns:
            GuardResult indicating pass/fail
        """
        pass
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name={self.name})"


class InputGuard(BaseGuard):
    """Base class for input guards."""
    pass


class OutputGuard(BaseGuard):
    """Base class for output guards."""
    pass


class ActionGuard(BaseGuard):
    """Base class for action guards."""
    pass


class PromptInjectionGuard(InputGuard):
    """
    Detects potential prompt injection attempts.
    
    Looks for patterns that might indicate attempts to manipulate the prompt.
    """
    
    INJECTION_PATTERNS = [
        r"ignore\s+(previous|above|all)\s+instructions?",
        r"disregard\s+(previous|above|all)\s+instructions?",
        r"forget\s+(previous|above|all)\s+instructions?",
        r"new\s+instructions?:",
        r"system\s*:",
        r"<\s*system\s*>",
        r"you\s+are\s+now",
        r"act\s+as\s+if",
        r"pretend\s+you\s+are",
    ]
    
    async def validate(self, content: str, context: Optional[Dict[str, Any]] = None) -> GuardResult:
        """Check for prompt injection patterns."""
        content_lower = content.lower()
        
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, content_lower):
                return GuardResult(
                    passed=False,
                    message=f"Potential prompt injection detected: pattern '{pattern}'",
                    metadata={"pattern": pattern}
                )
        
        return GuardResult(passed=True)


class PIIDetectionGuard(InputGuard):
    """
    Detects Personally Identifiable Information (PII).
    
    Looks for common PII patterns like emails, phone numbers, SSNs, etc.
    """
    
    PII_PATTERNS = {
        "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
        "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
        "credit_card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
    }
    
    async def validate(self, content: str, context: Optional[Dict[str, Any]] = None) -> GuardResult:
        """Check for PII patterns."""
        detected_pii = []
        
        for pii_type, pattern in self.PII_PATTERNS.items():
            matches = re.findall(pattern, content)
            if matches:
                detected_pii.append({
                    "type": pii_type,
                    "count": len(matches)
                })
        
        if detected_pii:
            return GuardResult(
                passed=False,
                message=f"PII detected: {', '.join([p['type'] for p in detected_pii])}",
                metadata={"detected_pii": detected_pii}
            )
        
        return GuardResult(passed=True)


class ToxicityGuard(OutputGuard):
    """
    Detects toxic or harmful content.
    
    Checks for offensive language, hate speech, etc.
    """
    
    TOXIC_KEYWORDS = [
        "hate", "kill", "violence", "attack", "harm",
        # Add more as needed
    ]
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.threshold = self.config.get("threshold", 0.5)
    
    async def validate(self, content: str, context: Optional[Dict[str, Any]] = None) -> GuardResult:
        """Check for toxic content."""
        content_lower = content.lower()
        
        # Simple keyword-based detection (in production, use ML model)
        toxic_count = sum(1 for keyword in self.TOXIC_KEYWORDS if keyword in content_lower)
        toxicity_score = toxic_count / len(content.split()) if content else 0
        
        if toxicity_score > self.threshold:
            return GuardResult(
                passed=False,
                message=f"Toxic content detected (score: {toxicity_score:.2f})",
                metadata={"toxicity_score": toxicity_score}
            )
        
        return GuardResult(passed=True)


class FactualityGuard(OutputGuard):
    """
    Checks factuality of output against sources.
    
    Verifies that claims in the output are supported by provided sources.
    """
    
    async def validate(self, content: str, context: Optional[Dict[str, Any]] = None) -> GuardResult:
        """Check factuality against sources."""
        # In production, this would use NLI models or fact-checking APIs
        # For now, simple heuristic: check if content mentions sources
        
        sources = context.get("sources", []) if context else []
        
        if not sources:
            return GuardResult(
                passed=True,
                message="No sources provided for factuality check"
            )
        
        # Simple check: does output reference any sources?
        has_references = any(
            source.lower() in content.lower()
            for source in sources
        )
        
        if not has_references:
            return GuardResult(
                passed=False,
                message="Output does not reference provided sources",
                metadata={"sources_count": len(sources)}
            )
        
        return GuardResult(passed=True)


class DomainAllowlistGuard(ActionGuard):
    """
    Restricts actions to allowed domains.
    
    Useful for preventing agents from accessing unauthorized resources.
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.allowed_domains = self.config.get("allowed_domains", [])
    
    async def validate(self, content: str, context: Optional[Dict[str, Any]] = None) -> GuardResult:
        """Check if action targets allowed domain."""
        # Extract domain from URL
        url_pattern = r'https?://([a-zA-Z0-9.-]+)'
        matches = re.findall(url_pattern, content)
        
        for domain in matches:
            if domain not in self.allowed_domains:
                return GuardResult(
                    passed=False,
                    message=f"Domain '{domain}' not in allowlist",
                    metadata={"domain": domain, "allowed_domains": self.allowed_domains}
                )
        
        return GuardResult(passed=True)


class FormatValidationGuard(OutputGuard):
    """
    Validates output format (JSON, XML, etc.).
    
    Ensures output conforms to expected structure.
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.expected_format = self.config.get("format", "json")
    
    async def validate(self, content: str, context: Optional[Dict[str, Any]] = None) -> GuardResult:
        """Validate output format."""
        if self.expected_format == "json":
            import json
            try:
                json.loads(content)
                return GuardResult(passed=True)
            except json.JSONDecodeError as e:
                return GuardResult(
                    passed=False,
                    message=f"Invalid JSON format: {e}",
                    metadata={"error": str(e)}
                )
        
        # Add more format validators as needed
        return GuardResult(passed=True)


class LengthGuard(OutputGuard):
    """
    Validates output length.
    
    Ensures output is within acceptable length bounds.
    """
    
    def __init__(self, name: str, config: Optional[Dict[str, Any]] = None):
        super().__init__(name, config)
        self.min_length = self.config.get("min_length", 0)
        self.max_length = self.config.get("max_length", float('inf'))
    
    async def validate(self, content: str, context: Optional[Dict[str, Any]] = None) -> GuardResult:
        """Validate output length."""
        length = len(content)
        
        if length < self.min_length:
            return GuardResult(
                passed=False,
                message=f"Output too short: {length} < {self.min_length}",
                metadata={"length": length, "min_length": self.min_length}
            )
        
        if length > self.max_length:
            return GuardResult(
                passed=False,
                message=f"Output too long: {length} > {self.max_length}",
                metadata={"length": length, "max_length": self.max_length}
            )
        
        return GuardResult(passed=True)

