# AI Mental Health Companion - Models Module
# This file makes the models directory a Python package and exports database models

from .models import (
    # Base classes and enums
    Base,
    EmotionCategory,
    MoodScale,

    # Main models
    User,
    MoodLog,
    ChatHistory,
    CopingSession,
    SystemMetrics,
    SafetyLog
)

__all__ = [
    # Base and enums
    "Base",
    "EmotionCategory",
    "MoodScale",

    # Database models
    "User",
    "MoodLog",
    "ChatHistory",
    "CopingSession",
    "SystemMetrics",
    "SafetyLog"
]

# Model version for migrations
MODEL_VERSION = "1.0.0"

# Model metadata
MODELS_INFO = {
    "User": {
        "description": "User profiles and preferences",
        "primary_key": "user_id",
        "relationships": ["mood_logs", "chat_history", "coping_sessions"]
    },
    "MoodLog": {
        "description": "Daily mood tracking entries",
        "primary_key": "log_id",
        "foreign_keys": ["user_id"]
    },
    "ChatHistory": {
        "description": "AI chat conversation records",
        "primary_key": "chat_id",
        "foreign_keys": ["user_id"]
    },
    "CopingSession": {
        "description": "Coping tool usage sessions",
        "primary_key": "session_id",
        "foreign_keys": ["user_id"]
    },
    "SystemMetrics": {
        "description": "System performance and usage metrics",
        "primary_key": "metric_id"
    },
    "SafetyLog": {
        "description": "Safety events and crisis interventions",
        "primary_key": "log_id"
    }
}
