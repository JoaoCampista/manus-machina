"""Guardrail engine for orchestrating guards."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from manus_machina.guardrails.guards import (
    BaseGuard,
    InputGuard,
    OutputGuard,
    ActionGuard,
    GuardResult,
)


class GuardrailConfig(BaseModel):
    """Configuration for guardrail engine."""
    
    fail_fast: bool = Field(
        default=True,
        description="Stop on first guard failure"
    )
    log_violations: bool = Field(
        default=True,
        description="Log all guard violations"
    )


class GuardrailViolation(Exception):
    """Raised when a guardrail check fails."""
    
    def __init__(self, guard_name: str, message: str, metadata: Dict[str, Any]):
        self.guard_name = guard_name
        self.message = message
        self.metadata = metadata
        super().__init__(f"Guardrail '{guard_name}' failed: {message}")


class GuardrailEngine:
    """
    Guardrail engine for validating inputs, outputs, and actions.
    
    Orchestrates multiple guards and provides a unified interface
    for validation.
    """
    
    def __init__(self, config: Optional[GuardrailConfig] = None):
        self.config = config or GuardrailConfig()
        
        self.input_guards: Dict[str, InputGuard] = {}
        self.output_guards: Dict[str, OutputGuard] = {}
        self.action_guards: Dict[str, ActionGuard] = {}
        
        # Metrics
        self._total_validations = 0
        self._total_violations = 0
    
    def register_input_guard(self, guard: InputGuard) -> None:
        """Register an input guard."""
        self.input_guards[guard.name] = guard
    
    def register_output_guard(self, guard: OutputGuard) -> None:
        """Register an output guard."""
        self.output_guards[guard.name] = guard
    
    def register_action_guard(self, guard: ActionGuard) -> None:
        """Register an action guard."""
        self.action_guards[guard.name] = guard
    
    async def validate_input(
        self,
        content: str,
        guard_names: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Validate input content against input guards.
        
        Args:
            content: Input content to validate
            guard_names: Specific guards to run (None = all)
            context: Additional context
            
        Returns:
            Validated content (potentially modified)
            
        Raises:
            GuardrailViolation: If validation fails
        """
        guards_to_run = self._select_guards(self.input_guards, guard_names)
        return await self._run_guards(guards_to_run, content, context)
    
    async def validate_output(
        self,
        content: str,
        guard_names: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Validate output content against output guards.
        
        Args:
            content: Output content to validate
            guard_names: Specific guards to run (None = all)
            context: Additional context
            
        Returns:
            Validated content (potentially modified)
            
        Raises:
            GuardrailViolation: If validation fails
        """
        guards_to_run = self._select_guards(self.output_guards, guard_names)
        return await self._run_guards(guards_to_run, content, context)
    
    async def validate_action(
        self,
        action: str,
        guard_names: Optional[List[str]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Validate action against action guards.
        
        Args:
            action: Action to validate
            guard_names: Specific guards to run (None = all)
            context: Additional context
            
        Returns:
            Validated action (potentially modified)
            
        Raises:
            GuardrailViolation: If validation fails
        """
        guards_to_run = self._select_guards(self.action_guards, guard_names)
        return await self._run_guards(guards_to_run, action, context)
    
    def _select_guards(
        self,
        guard_dict: Dict[str, BaseGuard],
        guard_names: Optional[List[str]]
    ) -> List[BaseGuard]:
        """Select guards to run."""
        if guard_names is None:
            return list(guard_dict.values())
        
        return [
            guard_dict[name]
            for name in guard_names
            if name in guard_dict
        ]
    
    async def _run_guards(
        self,
        guards: List[BaseGuard],
        content: str,
        context: Optional[Dict[str, Any]]
    ) -> str:
        """Run guards and collect results."""
        self._total_validations += 1
        violations = []
        
        for guard in guards:
            result = await guard.validate(content, context)
            
            if not result.passed:
                self._total_violations += 1
                violation = GuardrailViolation(
                    guard_name=guard.name,
                    message=result.message or "Validation failed",
                    metadata=result.metadata
                )
                
                if self.config.fail_fast:
                    raise violation
                
                violations.append(violation)
        
        # If not fail_fast and there were violations, raise combined error
        if violations:
            raise GuardrailViolation(
                guard_name="multiple",
                message=f"{len(violations)} guard(s) failed",
                metadata={"violations": [
                    {
                        "guard": v.guard_name,
                        "message": v.message,
                        "metadata": v.metadata
                    }
                    for v in violations
                ]}
            )
        
        return content
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get guardrail engine metrics."""
        return {
            "total_validations": self._total_validations,
            "total_violations": self._total_violations,
            "violation_rate": self._total_violations / self._total_validations 
                if self._total_validations > 0 else 0,
            "input_guards": len(self.input_guards),
            "output_guards": len(self.output_guards),
            "action_guards": len(self.action_guards),
        }
    
    def __repr__(self) -> str:
        return (
            f"GuardrailEngine("
            f"input_guards={len(self.input_guards)}, "
            f"output_guards={len(self.output_guards)}, "
            f"action_guards={len(self.action_guards)})"
        )

