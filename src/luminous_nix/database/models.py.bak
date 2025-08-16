"""Database models for Nix for Humanity using SQLAlchemy ORM."""

from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class NixKnowledge(Base):
    """Store NixOS knowledge and documentation."""
    
    __tablename__ = "nix_knowledge"
    
    id = Column(Integer, primary_key=True)
    command = Column(String(255), nullable=False, index=True)
    description = Column(Text)
    category = Column(String(100), index=True)
    examples = Column(JSON)  # List of example usages
    related_commands = Column(JSON)  # List of related command IDs
    tags = Column(JSON)  # List of tags for search
    documentation_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_command_category", "command", "category"),
    )


class CommandHistory(Base):
    """Track user command history for learning."""
    
    __tablename__ = "command_history"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), index=True)
    natural_query = Column(Text, nullable=False)
    intent_type = Column(String(50))
    executed_command = Column(Text)
    success = Column(Boolean, default=True)
    error_message = Column(Text)
    execution_time_ms = Column(Float)
    confidence_score = Column(Float)
    feedback_score = Column(Integer)  # User rating 1-5
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    learning_patterns = relationship("LearningPattern", back_populates="command")


class LearningPattern(Base):
    """Store learned patterns from user interactions."""
    
    __tablename__ = "learning_patterns"
    
    id = Column(Integer, primary_key=True)
    command_id = Column(Integer, ForeignKey("command_history.id"))
    pattern_type = Column(String(50))  # 'alias', 'preference', 'correction'
    pattern_data = Column(JSON)
    frequency = Column(Integer, default=1)
    confidence = Column(Float, default=0.5)
    last_used = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    command = relationship("CommandHistory", back_populates="learning_patterns")
    
    __table_args__ = (
        Index("idx_pattern_type_confidence", "pattern_type", "confidence"),
    )


class PackageCache(Base):
    """Cache for NixOS package information."""
    
    __tablename__ = "package_cache"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    version = Column(String(100))
    description = Column(Text)
    homepage = Column(String(500))
    license = Column(String(100))
    platforms = Column(JSON)  # List of supported platforms
    dependencies = Column(JSON)  # List of dependency names
    search_terms = Column(Text)  # Full-text search field
    popularity_score = Column(Float, default=0.0)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index("idx_package_search", "name", "search_terms"),
    )


class UserProfile(Base):
    """User profiles for personalization."""
    
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(String(100), unique=True, nullable=False)
    persona_type = Column(String(50))  # 'grandma_rose', 'maya_adhd', etc.
    preferences = Column(JSON)  # User preferences dict
    skill_level = Column(Integer, default=1)  # 1-10 scale
    preferred_verbosity = Column(String(20), default="normal")
    accessibility_needs = Column(JSON)  # List of accessibility requirements
    learning_style = Column(String(50))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    # Statistics
    total_commands = Column(Integer, default=0)
    success_rate = Column(Float, default=0.0)
    avg_confidence = Column(Float, default=0.0)


class SessionState(Base):
    """Track active session states."""
    
    __tablename__ = "session_states"
    
    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), unique=True, nullable=False)
    user_id = Column(String(100), index=True)
    context = Column(JSON)  # Current context dict
    active = Column(Boolean, default=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow)
    ended_at = Column(DateTime)
    
    __table_args__ = (
        Index("idx_active_sessions", "active", "user_id"),
    )


class ErrorPattern(Base):
    """Track error patterns for intelligent error handling."""
    
    __tablename__ = "error_patterns"
    
    id = Column(Integer, primary_key=True)
    error_type = Column(String(100), index=True)
    error_message = Column(Text)
    solution = Column(Text)
    explanation = Column(Text)
    frequency = Column(Integer, default=1)
    last_seen = Column(DateTime, default=datetime.utcnow)
    tags = Column(JSON)
    
    __table_args__ = (
        UniqueConstraint("error_type", "error_message", name="uq_error_pattern"),
    )


class PerformanceMetric(Base):
    """Track performance metrics."""
    
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True)
    operation = Column(String(100), index=True)
    execution_time_ms = Column(Float)
    memory_usage_mb = Column(Float)
    cpu_percent = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    metadata = Column(JSON)
    
    __table_args__ = (
        Index("idx_metrics_timestamp", "operation", "timestamp"),
    )