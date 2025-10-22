"""
Database Models - SQLAlchemy ORM

Defines the database schema for sessions, state, events, and artifacts.
Supports PostgreSQL, MySQL, and SQLite.
"""

from datetime import datetime
from sqlalchemy import (
    Column, String, DateTime, Boolean, Integer, Text,
    ForeignKey, Index, JSON
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from uuid import uuid4
import uuid

Base = declarative_base()


class SessionModel(Base):
    """Session table"""
    __tablename__ = "sessions"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    
    # Metadata
    user_id = Column(String(255), nullable=True, index=True)
    app_name = Column(String(255), nullable=False, index=True)
    tags = Column(JSON, nullable=False, default=list)
    custom_fields = Column(JSON, nullable=False, default=dict)
    
    # Status
    is_active = Column(Boolean, nullable=False, default=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow, index=True)
    
    # Relationships
    state_entries = relationship("StateModel", back_populates="session", cascade="all, delete-orphan")
    events = relationship("EventModel", back_populates="session", cascade="all, delete-orphan")
    artifacts = relationship("ArtifactModel", back_populates="session", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_session_user_app', 'user_id', 'app_name'),
        Index('idx_session_active_updated', 'is_active', 'updated_at'),
    )


class StateModel(Base):
    """State table - stores key-value pairs for sessions"""
    __tablename__ = "state"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign key
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Key-value
    key = Column(String(255), nullable=False, index=True)
    value = Column(JSON, nullable=False)
    
    # Scope (extracted from key prefix)
    scope = Column(String(50), nullable=False, default="session", index=True)  # session, user, app, temp
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    session = relationship("SessionModel", back_populates="state_entries")
    
    # Indexes
    __table_args__ = (
        Index('idx_state_session_key', 'session_id', 'key', unique=True),
        Index('idx_state_scope', 'scope'),
    )


class EventModel(Base):
    """Event table - stores domain events"""
    __tablename__ = "events"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    
    # Foreign key
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=True, index=True)
    
    # Event data
    event_type = Column(String(100), nullable=False, index=True)
    agent_name = Column(String(255), nullable=True, index=True)
    data = Column(JSON, nullable=False, default=dict)
    
    # Tracing
    correlation_id = Column(String(36), nullable=True, index=True)
    
    # Timestamp
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationship
    session = relationship("SessionModel", back_populates="events")
    
    # Indexes
    __table_args__ = (
        Index('idx_event_session_type', 'session_id', 'event_type'),
        Index('idx_event_timestamp', 'timestamp'),
    )


class ArtifactModel(Base):
    """Artifact table - stores generated artifacts"""
    __tablename__ = "artifacts"
    
    # Primary key
    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    
    # Foreign key
    session_id = Column(String(36), ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Artifact data
    type = Column(String(100), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    content = Column(Text, nullable=False)
    metadata = Column(JSON, nullable=False, default=dict)
    
    # Versioning
    version = Column(Integer, nullable=False, default=1)
    parent_id = Column(String(36), nullable=True, index=True)
    
    # Context
    agent_name = Column(String(255), nullable=True, index=True)
    tags = Column(JSON, nullable=False, default=list)
    
    # Timestamp
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationship
    session = relationship("SessionModel", back_populates="artifacts")
    
    # Indexes
    __table_args__ = (
        Index('idx_artifact_session_type', 'session_id', 'type'),
        Index('idx_artifact_parent', 'parent_id'),
    )


class UserStateModel(Base):
    """User state table - cross-session user preferences"""
    __tablename__ = "user_state"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # User and app
    user_id = Column(String(255), nullable=False, index=True)
    app_name = Column(String(255), nullable=False, index=True)
    
    # Key-value
    key = Column(String(255), nullable=False, index=True)
    value = Column(JSON, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_user_state_unique', 'user_id', 'app_name', 'key', unique=True),
    )


class AppStateModel(Base):
    """App state table - application-wide settings"""
    __tablename__ = "app_state"
    
    # Primary key
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # App
    app_name = Column(String(255), nullable=False, index=True)
    
    # Key-value
    key = Column(String(255), nullable=False, index=True)
    value = Column(JSON, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_app_state_unique', 'app_name', 'key', unique=True),
    )

