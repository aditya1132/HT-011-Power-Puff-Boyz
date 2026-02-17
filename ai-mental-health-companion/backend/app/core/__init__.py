# AI Mental Health Companion - Core Module
# This file makes the core directory a Python package and exports core functionality

from .config import get_settings, Settings
from .exceptions import (
    CustomHTTPException,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ConflictError,
    RateLimitError,
    DatabaseError,
    AIServiceError,
    SafetyViolationError,
    CrisisDetectionError,
    UserNotFoundError,
    MoodLogNotFoundError,
    ChatSessionError,
    EmotionDetectionError,
    CopingToolError
)
from .logging import (
    setup_logging,
    get_logger,
    get_security_logger,
    get_audit_logger,
    get_performance_logger,
    get_privacy_logger
)

__all__ = [
    # Configuration
    "get_settings",
    "Settings",

    # Exceptions
    "CustomHTTPException",
    "ValidationError",
    "AuthenticationError",
    "AuthorizationError",
    "NotFoundError",
    "ConflictError",
    "RateLimitError",
    "DatabaseError",
    "AIServiceError",
    "SafetyViolationError",
    "CrisisDetectionError",
    "UserNotFoundError",
    "MoodLogNotFoundError",
    "ChatSessionError",
    "EmotionDetectionError",
    "CopingToolError",

    # Logging
    "setup_logging",
    "get_logger",
    "get_security_logger",
    "get_audit_logger",
    "get_performance_logger",
    "get_privacy_logger"
]
