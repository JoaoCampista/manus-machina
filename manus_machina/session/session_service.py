"""
SessionService - Port (Interface) and Adapters

Manages the lifecycle of sessions:
- Create, retrieve, update, delete sessions
- Persist state and events
- Support multiple storage backends

Implementations:
- InMemorySessionService: For testing/development
- DatabaseSessionService: For production (PostgreSQL, MySQL, SQLite)
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from uuid import UUID

from .session import Session, SessionMetadata


class SessionService(ABC):
    """
    SessionService interface (Port in Hexagonal Architecture).
    
    Defines the contract for session management.
    """
    
    @abstractmethod
    async def create_session(
        self,
        user_id: Optional[str] = None,
        app_name: str = "default",
        tags: Optional[List[str]] = None
    ) -> Session:
        """
        Create a new session.
        
        Args:
            user_id: Optional user identifier
            app_name: Application name for scoping
            tags: Optional tags for organization
            
        Returns:
            Created session
        """
        pass
    
    @abstractmethod
    async def get_session(self, session_id: UUID) -> Optional[Session]:
        """
        Retrieve a session by ID.
        
        Args:
            session_id: Session identifier
            
        Returns:
            Session if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def update_session(self, session: Session) -> None:
        """
        Update an existing session.
        
        Args:
            session: Session to update
        """
        pass
    
    @abstractmethod
    async def delete_session(self, session_id: UUID) -> bool:
        """
        Delete a session.
        
        Args:
            session_id: Session identifier
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    async def list_sessions(
        self,
        user_id: Optional[str] = None,
        app_name: Optional[str] = None,
        is_active: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Session]:
        """
        List sessions with optional filtering.
        
        Args:
            user_id: Filter by user
            app_name: Filter by application
            is_active: Filter by active status
            limit: Maximum number of results
            offset: Pagination offset
            
        Returns:
            List of sessions
        """
        pass
    
    @abstractmethod
    async def get_user_sessions(
        self,
        user_id: str,
        app_name: Optional[str] = None,
        limit: int = 100
    ) -> List[Session]:
        """
        Get all sessions for a specific user.
        
        Args:
            user_id: User identifier
            app_name: Optional app filter
            limit: Maximum results
            
        Returns:
            List of user's sessions
        """
        pass


class InMemorySessionService(SessionService):
    """
    In-memory implementation of SessionService.
    
    ⚠️ WARNING: All data is lost when the application restarts.
    Use only for testing and local development.
    """
    
    def __init__(self):
        self._sessions: dict[UUID, Session] = {}
    
    async def create_session(
        self,
        user_id: Optional[str] = None,
        app_name: str = "default",
        tags: Optional[List[str]] = None
    ) -> Session:
        """Create a new session in memory"""
        metadata = SessionMetadata(
            user_id=user_id,
            app_name=app_name,
            tags=tags or []
        )
        
        session = Session(metadata=metadata)
        self._sessions[session.id] = session
        
        return session
    
    async def get_session(self, session_id: UUID) -> Optional[Session]:
        """Retrieve session from memory"""
        return self._sessions.get(session_id)
    
    async def update_session(self, session: Session) -> None:
        """Update session in memory"""
        self._sessions[session.id] = session
    
    async def delete_session(self, session_id: UUID) -> bool:
        """Delete session from memory"""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False
    
    async def list_sessions(
        self,
        user_id: Optional[str] = None,
        app_name: Optional[str] = None,
        is_active: Optional[bool] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Session]:
        """List sessions from memory with filtering"""
        sessions = list(self._sessions.values())
        
        # Apply filters
        if user_id:
            sessions = [s for s in sessions if s.metadata.user_id == user_id]
        if app_name:
            sessions = [s for s in sessions if s.metadata.app_name == app_name]
        if is_active is not None:
            sessions = [s for s in sessions if s.is_active == is_active]
        
        # Sort by updated_at descending
        sessions.sort(key=lambda s: s.updated_at, reverse=True)
        
        # Pagination
        return sessions[offset:offset + limit]
    
    async def get_user_sessions(
        self,
        user_id: str,
        app_name: Optional[str] = None,
        limit: int = 100
    ) -> List[Session]:
        """Get user sessions from memory"""
        return await self.list_sessions(
            user_id=user_id,
            app_name=app_name,
            limit=limit
        )
    
    def clear_all(self) -> None:
        """Clear all sessions (for testing)"""
        self._sessions.clear()
    
    def count(self) -> int:
        """Get total number of sessions"""
        return len(self._sessions)


# Note: DatabaseSessionService will be implemented in infrastructure/database/
# It will use SQLAlchemy for persistence and support PostgreSQL, MySQL, SQLite

