from fastapi import HTTPException, status
from datetime import datetime
from typing import Optional, Dict, Any


class CustomHTTPException(HTTPException):
    """Base custom HTTP exception with additional context"""

    def __init__(
        self,
        status_code: int,
        detail: str,
        error_type: str = "generic_error",
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(status_code=status_code, detail=detail)
        self.error_type = error_type
        self.context = context or {}
        self.timestamp = datetime.utcnow()


class ValidationError(CustomHTTPException):
    """Validation error exception"""

    def __init__(self, detail: str, field: str = None):
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail,
            error_type="validation_error",
            context={"field": field} if field else {}
        )


class AuthenticationError(CustomHTTPException):
    """Authentication error exception"""

    def __init__(self, detail: str = "Authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_type="authentication_error"
        )


class AuthorizationError(CustomHTTPException):
    """Authorization error exception"""

    def __init__(self, detail: str = "Access denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_type="authorization_error"
        )


class NotFoundError(CustomHTTPException):
    """Resource not found exception"""

    def __init__(self, detail: str = "Resource not found", resource_type: str = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_type="not_found_error",
            context={"resource_type": resource_type} if resource_type else {}
        )


class ConflictError(CustomHTTPException):
    """Resource conflict exception"""

    def __init__(self, detail: str = "Resource conflict", resource_id: str = None):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_type="conflict_error",
            context={"resource_id": resource_id} if resource_id else {}
        )


class RateLimitError(CustomHTTPException):
    """Rate limit exceeded exception"""

    def __init__(self, detail: str = "Rate limit exceeded", retry_after: int = None):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_type="rate_limit_error",
            context={"retry_after": retry_after} if retry_after else {}
        )


class DatabaseError(CustomHTTPException):
    """Database operation error exception"""

    def __init__(self, detail: str = "Database operation failed"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_type="database_error"
        )


class AIServiceError(CustomHTTPException):
    """AI service error exception"""

    def __init__(self, detail: str = "AI service unavailable", service: str = None):
        super().__init__(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=detail,
            error_type="ai_service_error",
            context={"service": service} if service else {}
        )


class SafetyViolationError(CustomHTTPException):
    """Safety violation exception"""

    def __init__(self, detail: str = "Content violates safety guidelines", violation_type: str = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_type="safety_violation",
            context={"violation_type": violation_type} if violation_type else {}
        )


class CrisisDetectionError(CustomHTTPException):
    """Crisis situation detected exception"""

    def __init__(self, detail: str = "Crisis situation detected", keywords: list = None):
        super().__init__(
            status_code=status.HTTP_200_OK,  # Not an error, but needs special handling
            detail=detail,
            error_type="crisis_detection",
            context={"keywords": keywords} if keywords else {}
        )


class InvalidMoodDataError(ValidationError):
    """Invalid mood data exception"""

    def __init__(self, detail: str = "Invalid mood data provided"):
        super().__init__(detail=detail, field="mood_data")


class UserNotFoundError(NotFoundError):
    """User not found exception"""

    def __init__(self, user_id: str = None):
        detail = f"User {user_id} not found" if user_id else "User not found"
        super().__init__(detail=detail, resource_type="user")


class MoodLogNotFoundError(NotFoundError):
    """Mood log not found exception"""

    def __init__(self, log_id: str = None):
        detail = f"Mood log {log_id} not found" if log_id else "Mood log not found"
        super().__init__(detail=detail, resource_type="mood_log")


class ChatSessionError(CustomHTTPException):
    """Chat session error exception"""

    def __init__(self, detail: str = "Chat session error", session_id: str = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_type="chat_session_error",
            context={"session_id": session_id} if session_id else {}
        )


class EmotionDetectionError(AIServiceError):
    """Emotion detection error exception"""

    def __init__(self, detail: str = "Failed to detect emotion from input"):
        super().__init__(detail=detail, service="emotion_detection")


class CopingToolError(CustomHTTPException):
    """Coping tool error exception"""

    def __init__(self, detail: str = "Coping tool unavailable", tool_type: str = None):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_type="coping_tool_error",
            context={"tool_type": tool_type} if tool_type else {}
        )


class DataPrivacyError(CustomHTTPException):
    """Data privacy violation exception"""

    def __init__(self, detail: str = "Data privacy violation detected"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_type="data_privacy_error"
        )


class ConfigurationError(CustomHTTPException):
    """Configuration error exception"""

    def __init__(self, detail: str = "Application configuration error", config_key: str = None):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_type="configuration_error",
            context={"config_key": config_key} if config_key else {}
        )


class ExternalServiceError(CustomHTTPException):
    """External service error exception"""

    def __init__(self, detail: str = "External service unavailable", service_name: str = None):
        super().__init__(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=detail,
            error_type="external_service_error",
            context={"service_name": service_name} if service_name else {}
        )


# Custom exception for business logic violations
class BusinessLogicError(CustomHTTPException):
    """Business logic violation exception"""

    def __init__(self, detail: str, rule: str = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_type="business_logic_error",
            context={"rule": rule} if rule else {}
        )


class DailyCheckInError(BusinessLogicError):
    """Daily check-in related error"""

    def __init__(self, detail: str = "Daily check-in error"):
        super().__init__(detail=detail, rule="daily_check_in")


class MoodTrackingError(BusinessLogicError):
    """Mood tracking related error"""

    def __init__(self, detail: str = "Mood tracking error"):
        super().__init__(detail=detail, rule="mood_tracking")


# Exception handler helpers
def create_error_response(exc: CustomHTTPException) -> dict:
    """Create standardized error response"""
    return {
        "error": True,
        "message": exc.detail,
        "type": exc.error_type,
        "timestamp": exc.timestamp.isoformat(),
        "context": exc.context
    }


def handle_database_exception(exc: Exception) -> DatabaseError:
    """Convert database exceptions to custom format"""
    return DatabaseError(f"Database operation failed: {str(exc)}")


def handle_ai_exception(exc: Exception, service: str = None) -> AIServiceError:
    """Convert AI service exceptions to custom format"""
    return AIServiceError(f"AI service error: {str(exc)}", service=service)
