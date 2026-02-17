from sqlalchemy import Column, Integer, String, DateTime, Float, Text, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, Dict, Any
import uuid
from enum import Enum

from app.database.database import Base


class EmotionCategory(str, Enum):
    """Emotion categories for mood tracking"""
    STRESSED = "stressed"
    ANXIOUS = "anxious"
    SAD = "sad"
    OVERWHELMED = "overwhelmed"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    ANGRY = "angry"
    EXCITED = "excited"
    CONFUSED = "confused"
    GRATEFUL = "grateful"


class MoodScale(int, Enum):
    """Mood scale values (1-5)"""
    VERY_LOW = 1
    LOW = 2
    NEUTRAL = 3
    GOOD = 4
    EXCELLENT = 5


class User(Base):
    """User model for storing basic user information"""

    __tablename__ = "users"

    # Primary key
    user_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Basic information
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Check-in tracking
    streak_count = Column(Integer, default=0, nullable=False)
    last_check_in = Column(DateTime(timezone=True), nullable=True)
    total_check_ins = Column(Integer, default=0, nullable=False)

    # User preferences
    preferred_coping_tools = Column(JSON, nullable=True)  # Store as JSON array
    notification_preferences = Column(JSON, nullable=True)
    privacy_settings = Column(JSON, nullable=True)

    # Status tracking
    is_active = Column(Boolean, default=True, nullable=False)
    first_login = Column(DateTime(timezone=True), nullable=True)
    last_activity = Column(DateTime(timezone=True), nullable=True)

    # Safety tracking
    crisis_alerts_count = Column(Integer, default=0, nullable=False)
    last_crisis_alert = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    mood_logs = relationship("MoodLog", back_populates="user", cascade="all, delete-orphan")
    chat_history = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
    coping_sessions = relationship("CopingSession", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(user_id={self.user_id}, created_at={self.created_at})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "streak_count": self.streak_count,
            "last_check_in": self.last_check_in.isoformat() if self.last_check_in else None,
            "total_check_ins": self.total_check_ins,
            "is_active": self.is_active,
            "preferred_coping_tools": self.preferred_coping_tools,
            "notification_preferences": self.notification_preferences,
            "privacy_settings": self.privacy_settings
        }


class MoodLog(Base):
    """Mood log model for tracking daily emotional state"""

    __tablename__ = "mood_logs"

    # Primary key
    log_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign key to user
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)

    # Mood data
    mood_score = Column(Integer, nullable=False)  # 1-5 scale
    emotion_category = Column(String(20), nullable=False)  # Primary detected emotion
    secondary_emotions = Column(JSON, nullable=True)  # Array of additional emotions

    # Context information
    notes = Column(Text, nullable=True)  # User's optional notes
    triggers = Column(JSON, nullable=True)  # Array of identified triggers
    coping_tools_used = Column(JSON, nullable=True)  # Tools used after logging

    # Metadata
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    date_only = Column(String(10), nullable=False)  # YYYY-MM-DD format for daily tracking

    # AI insights
    ai_confidence = Column(Float, nullable=True)  # Confidence in emotion detection
    suggested_activities = Column(JSON, nullable=True)  # AI-suggested coping activities

    # Context factors
    time_of_day = Column(String(10), nullable=True)  # morning, afternoon, evening, night
    weather_impact = Column(String(20), nullable=True)  # if provided by user
    social_context = Column(String(50), nullable=True)  # alone, with_friends, family, etc.

    # Relationships
    user = relationship("User", back_populates="mood_logs")

    def __repr__(self):
        return f"<MoodLog(log_id={self.log_id}, user_id={self.user_id}, mood_score={self.mood_score})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "log_id": self.log_id,
            "user_id": self.user_id,
            "mood_score": self.mood_score,
            "emotion_category": self.emotion_category,
            "secondary_emotions": self.secondary_emotions,
            "notes": self.notes,
            "triggers": self.triggers,
            "coping_tools_used": self.coping_tools_used,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "date_only": self.date_only,
            "ai_confidence": self.ai_confidence,
            "suggested_activities": self.suggested_activities,
            "time_of_day": self.time_of_day,
            "weather_impact": self.weather_impact,
            "social_context": self.social_context
        }


class ChatHistory(Base):
    """Chat history model for storing conversation data (optional feature)"""

    __tablename__ = "chat_history"

    # Primary key
    chat_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign key to user
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)

    # Chat data
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)

    # Analysis data
    emotion_detected = Column(String(20), nullable=True)
    emotion_confidence = Column(Float, nullable=True)
    sentiment_score = Column(Float, nullable=True)  # -1 to 1

    # Safety data
    crisis_keywords_detected = Column(JSON, nullable=True)  # Array of detected keywords
    safety_intervention = Column(Boolean, default=False, nullable=False)

    # Context
    session_id = Column(String(36), nullable=True)  # For grouping conversations
    conversation_turn = Column(Integer, nullable=False, default=1)

    # Metadata
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    response_time_ms = Column(Integer, nullable=True)  # AI response generation time

    # Coping tools
    coping_tools_suggested = Column(JSON, nullable=True)
    tools_used = Column(JSON, nullable=True)

    # Relationships
    user = relationship("User", back_populates="chat_history")

    def __repr__(self):
        return f"<ChatHistory(chat_id={self.chat_id}, user_id={self.user_id}, timestamp={self.timestamp})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary (excluding sensitive data)"""
        return {
            "chat_id": self.chat_id,
            "user_id": self.user_id,
            "emotion_detected": self.emotion_detected,
            "emotion_confidence": self.emotion_confidence,
            "sentiment_score": self.sentiment_score,
            "session_id": self.session_id,
            "conversation_turn": self.conversation_turn,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "response_time_ms": self.response_time_ms,
            "coping_tools_suggested": self.coping_tools_suggested,
            "tools_used": self.tools_used,
            "safety_intervention": self.safety_intervention
        }


class CopingSession(Base):
    """Model for tracking coping tool usage sessions"""

    __tablename__ = "coping_sessions"

    # Primary key
    session_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Foreign key to user
    user_id = Column(String(36), ForeignKey("users.user_id"), nullable=False)

    # Session data
    tool_type = Column(String(50), nullable=False)  # breathing, grounding, journaling, etc.
    tool_name = Column(String(100), nullable=False)  # Specific tool used
    duration_seconds = Column(Integer, nullable=True)  # How long they used the tool

    # Context
    trigger_emotion = Column(String(20), nullable=True)  # What emotion prompted this
    pre_mood_score = Column(Integer, nullable=True)  # Mood before (1-5)
    post_mood_score = Column(Integer, nullable=True)  # Mood after (1-5)

    # Completion data
    completed = Column(Boolean, default=False, nullable=False)
    completion_percentage = Column(Float, nullable=True)  # 0-1

    # User feedback
    helpfulness_rating = Column(Integer, nullable=True)  # 1-5 how helpful was this
    user_notes = Column(Text, nullable=True)

    # Metadata
    started_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    user = relationship("User", back_populates="coping_sessions")

    def __repr__(self):
        return f"<CopingSession(session_id={self.session_id}, tool_type={self.tool_type})>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary"""
        return {
            "session_id": self.session_id,
            "user_id": self.user_id,
            "tool_type": self.tool_type,
            "tool_name": self.tool_name,
            "duration_seconds": self.duration_seconds,
            "trigger_emotion": self.trigger_emotion,
            "pre_mood_score": self.pre_mood_score,
            "post_mood_score": self.post_mood_score,
            "completed": self.completed,
            "completion_percentage": self.completion_percentage,
            "helpfulness_rating": self.helpfulness_rating,
            "user_notes": self.user_notes,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


class SystemMetrics(Base):
    """Model for storing system-wide metrics and analytics"""

    __tablename__ = "system_metrics"

    # Primary key
    metric_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Metric data
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_unit = Column(String(50), nullable=True)

    # Context
    category = Column(String(50), nullable=False)  # performance, usage, safety, etc.
    tags = Column(JSON, nullable=True)  # Additional metadata

    # Metadata
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    date_only = Column(String(10), nullable=False)  # YYYY-MM-DD for daily aggregation

    def __repr__(self):
        return f"<SystemMetrics(metric_name={self.metric_name}, value={self.metric_value})>"


class SafetyLog(Base):
    """Model for logging safety-related events"""

    __tablename__ = "safety_logs"

    # Primary key
    log_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # User context (can be null for system-wide events)
    user_id = Column(String(36), nullable=True)

    # Event data
    event_type = Column(String(50), nullable=False)  # crisis_detection, inappropriate_content, etc.
    severity = Column(String(20), nullable=False)  # low, medium, high, critical
    description = Column(Text, nullable=False)

    # Detection data
    keywords_detected = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True)
    auto_response_triggered = Column(Boolean, default=False, nullable=False)

    # Response data
    intervention_taken = Column(JSON, nullable=True)  # What actions were taken
    resources_provided = Column(JSON, nullable=True)  # What resources were offered

    # Metadata
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    ip_address = Column(String(45), nullable=True)  # For tracking if needed
    user_agent = Column(String(500), nullable=True)

    # Resolution
    resolved = Column(Boolean, default=False, nullable=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)

    def __repr__(self):
        return f"<SafetyLog(event_type={self.event_type}, severity={self.severity})>"
