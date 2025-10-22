"""
State Management System

Implements the session state scratchpad with prefix-based scoping:
- No prefix: Session-specific state
- user:: User-specific state (cross-session)
- app:: Application-wide state (global)
- temp:: Temporary invocation state (non-persistent)

Inspired by Google ADK's state model.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
import orjson


class State(BaseModel):
    """
    State represents the scratchpad for a session.
    
    Stores key-value pairs with different scopes based on prefixes:
    - session state: No prefix (e.g., 'current_intent')
    - user state: 'user:' prefix (e.g., 'user:language')
    - app state: 'app:' prefix (e.g., 'app:api_endpoint')
    - temp state: 'temp:' prefix (e.g., 'temp:calculation')
    
    All values must be JSON-serializable.
    """
    
    _data: Dict[str, Any] = Field(default_factory=dict, alias="data")
    
    class Config:
        arbitrary_types_allowed = True
        populate_by_name = True
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from state"""
        return self._data.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """
        Set a value in state.
        
        Args:
            key: State key (can include prefix)
            value: JSON-serializable value
            
        Raises:
            ValueError: If value is not JSON-serializable
        """
        # Validate serializability
        try:
            orjson.dumps(value)
        except TypeError as e:
            raise ValueError(
                f"State value for key '{key}' must be JSON-serializable. "
                f"Got type: {type(value).__name__}"
            ) from e
        
        self._data[key] = value
    
    def delete(self, key: str) -> None:
        """Delete a key from state"""
        self._data.pop(key, None)
    
    def has(self, key: str) -> bool:
        """Check if a key exists in state"""
        return key in self._data
    
    def keys(self) -> List[str]:
        """Get all keys in state"""
        return list(self._data.keys())
    
    def items(self) -> List[tuple[str, Any]]:
        """Get all key-value pairs"""
        return list(self._data.items())
    
    def clear(self) -> None:
        """Clear all state"""
        self._data.clear()
    
    def clear_prefix(self, prefix: str) -> None:
        """Clear all keys with a specific prefix"""
        keys_to_delete = [k for k in self._data.keys() if k.startswith(prefix)]
        for key in keys_to_delete:
            del self._data[key]
    
    def get_by_prefix(self, prefix: str) -> Dict[str, Any]:
        """Get all key-value pairs with a specific prefix"""
        return {k: v for k, v in self._data.items() if k.startswith(prefix)}
    
    def get_session_state(self) -> Dict[str, Any]:
        """Get all session-specific state (no prefix)"""
        return {
            k: v for k, v in self._data.items()
            if not any(k.startswith(p) for p in ["user:", "app:", "temp:"])
        }
    
    def get_user_state(self) -> Dict[str, Any]:
        """Get all user-specific state (user: prefix)"""
        return self.get_by_prefix("user:")
    
    def get_app_state(self) -> Dict[str, Any]:
        """Get all application-wide state (app: prefix)"""
        return self.get_by_prefix("app:")
    
    def get_temp_state(self) -> Dict[str, Any]:
        """Get all temporary invocation state (temp: prefix)"""
        return self.get_by_prefix("temp:")
    
    def merge(self, other_state: "State") -> None:
        """Merge another state into this one"""
        self._data.update(other_state._data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary"""
        return self._data.copy()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "State":
        """Create state from dictionary"""
        return cls(data=data)
    
    def to_json(self) -> bytes:
        """Serialize state to JSON bytes"""
        return orjson.dumps(self._data)
    
    @classmethod
    def from_json(cls, json_bytes: bytes) -> "State":
        """Deserialize state from JSON bytes"""
        data = orjson.loads(json_bytes)
        return cls(data=data)
    
    def __len__(self) -> int:
        """Get number of keys in state"""
        return len(self._data)
    
    def __contains__(self, key: str) -> bool:
        """Check if key exists (supports 'in' operator)"""
        return key in self._data
    
    def __getitem__(self, key: str) -> Any:
        """Get item (supports dict-like access)"""
        return self._data[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Set item (supports dict-like access)"""
        self.set(key, value)
    
    def __delitem__(self, key: str) -> None:
        """Delete item (supports dict-like access)"""
        self.delete(key)
    
    def __repr__(self) -> str:
        """String representation"""
        return f"State(keys={len(self._data)})"


class StateTemplate:
    """
    Helper for state templating in instructions.
    
    Supports {key} syntax for injecting state values into strings.
    """
    
    @staticmethod
    def render(template: str, state: State) -> str:
        """
        Render a template string with state values.
        
        Args:
            template: Template string with {key} or {key?} placeholders
            state: State object to get values from
            
        Returns:
            Rendered string with placeholders replaced
            
        Raises:
            KeyError: If required key (without ?) is not found in state
            
        Examples:
            >>> state = State(data={"topic": "AI", "style": "formal"})
            >>> StateTemplate.render("Write about {topic} in {style} style", state)
            "Write about AI in formal style"
            
            >>> StateTemplate.render("Optional: {missing?}", state)
            "Optional: "
        """
        import re
        
        # Pattern: {key} or {key?}
        pattern = r'\{([a-zA-Z0-9_:]+)(\?)?\}'
        
        def replacer(match):
            key = match.group(1)
            optional = match.group(2) is not None
            
            if state.has(key):
                value = state.get(key)
                return str(value)
            elif optional:
                return ""
            else:
                raise KeyError(
                    f"Required state key '{key}' not found. "
                    f"Use {{key?}} for optional keys."
                )
        
        return re.sub(pattern, replacer, template)
    
    @staticmethod
    def extract_keys(template: str) -> List[tuple[str, bool]]:
        """
        Extract all state keys referenced in a template.
        
        Args:
            template: Template string
            
        Returns:
            List of (key, is_optional) tuples
            
        Examples:
            >>> StateTemplate.extract_keys("Hello {name}, topic: {topic?}")
            [('name', False), ('topic', True)]
        """
        import re
        
        pattern = r'\{([a-zA-Z0-9_:]+)(\?)?\}'
        matches = re.findall(pattern, template)
        
        return [(key, optional == '?') for key, optional in matches]

