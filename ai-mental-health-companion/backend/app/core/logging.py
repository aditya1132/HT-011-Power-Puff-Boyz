import logging
import logging.config
import sys
import json
from datetime import datetime
from typing import Dict, Any
import structlog
from pathlib import Path

def setup_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    log_file: str = None
) -> None:
    """
    Setup structured logging configuration

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Log format (json, text)
        log_file: Optional log file path
    """

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer() if log_format == "json" else structlog.dev.ConsoleRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Setup handlers
    handlers = ["console"]
    if log_file:
        handlers.append("file")

    # Logging configuration
    config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "format": "%(asctime)s %(name)s %(levelname)s %(message)s"
            },
            "text": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": log_format,
                "stream": sys.stdout
            }
        },
        "root": {
            "level": log_level,
            "handlers": handlers
        },
        "loggers": {
            "app": {
                "level": log_level,
                "handlers": handlers,
                "propagate": False
            },
            "uvicorn": {
                "level": "INFO",
                "handlers": handlers,
                "propagate": False
            },
            "sqlalchemy": {
                "level": "WARNING",
                "handlers": handlers,
                "propagate": False
            }
        }
    }

    # Add file handler if specified
    if log_file:
        # Ensure log directory exists
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)

        config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": log_level,
            "formatter": log_format,
            "filename": log_file,
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf-8"
        }

    # Apply configuration
    logging.config.dictConfig(config)


class ContextFilter(logging.Filter):
    """Custom filter to add context information to log records"""

    def __init__(self, context: Dict[str, Any] = None):
        super().__init__()
        self.context = context or {}

    def filter(self, record):
        for key, value in self.context.items():
            setattr(record, key, value)
        return True


class SecurityLogger:
    """Logger for security events"""

    def __init__(self):
        self.logger = structlog.get_logger("security")

    def log_failed_auth(self, user_id: str = None, ip_address: str = None):
        """Log failed authentication attempt"""
        self.logger.warning(
            "Failed authentication attempt",
            user_id=user_id,
            ip_address=ip_address,
            event_type="auth_failure"
        )

    def log_crisis_detection(self, user_id: str, message: str, keywords: list):
        """Log crisis keyword detection"""
        # Note: We log the detection but NOT the actual message for privacy
        self.logger.critical(
            "Crisis keywords detected",
            user_id=user_id,
            keywords_detected=keywords,
            event_type="crisis_detection",
            message_length=len(message)
        )

    def log_rate_limit_exceeded(self, ip_address: str, endpoint: str):
        """Log rate limit exceeded"""
        self.logger.warning(
            "Rate limit exceeded",
            ip_address=ip_address,
            endpoint=endpoint,
            event_type="rate_limit_exceeded"
        )

    def log_suspicious_activity(self, user_id: str, activity: str, details: dict):
        """Log suspicious user activity"""
        self.logger.warning(
            "Suspicious activity detected",
            user_id=user_id,
            activity=activity,
            details=details,
            event_type="suspicious_activity"
        )


class AuditLogger:
    """Logger for audit events"""

    def __init__(self):
        self.logger = structlog.get_logger("audit")

    def log_user_action(self, user_id: str, action: str, resource: str = None, details: dict = None):
        """Log user actions for audit purposes"""
        self.logger.info(
            "User action",
            user_id=user_id,
            action=action,
            resource=resource,
            details=details or {},
            event_type="user_action"
        )

    def log_data_access(self, user_id: str, data_type: str, access_type: str):
        """Log data access events"""
        self.logger.info(
            "Data access",
            user_id=user_id,
            data_type=data_type,
            access_type=access_type,
            event_type="data_access"
        )

    def log_system_event(self, event: str, details: dict = None):
        """Log system events"""
        self.logger.info(
            "System event",
            event=event,
            details=details or {},
            event_type="system_event"
        )


class PerformanceLogger:
    """Logger for performance monitoring"""

    def __init__(self):
        self.logger = structlog.get_logger("performance")

    def log_api_response_time(self, endpoint: str, method: str, response_time: float, status_code: int):
        """Log API response times"""
        self.logger.info(
            "API response time",
            endpoint=endpoint,
            method=method,
            response_time_ms=response_time * 1000,
            status_code=status_code,
            event_type="api_performance"
        )

    def log_database_query_time(self, query_type: str, execution_time: float, table: str = None):
        """Log database query performance"""
        self.logger.info(
            "Database query performance",
            query_type=query_type,
            execution_time_ms=execution_time * 1000,
            table=table,
            event_type="db_performance"
        )

    def log_ai_processing_time(self, operation: str, processing_time: float, input_length: int = None):
        """Log AI processing performance"""
        self.logger.info(
            "AI processing performance",
            operation=operation,
            processing_time_ms=processing_time * 1000,
            input_length=input_length,
            event_type="ai_performance"
        )


class PrivacyLogger:
    """Logger for privacy-related events"""

    def __init__(self):
        self.logger = structlog.get_logger("privacy")

    def log_data_anonymization(self, data_type: str, record_count: int):
        """Log data anonymization events"""
        self.logger.info(
            "Data anonymization completed",
            data_type=data_type,
            record_count=record_count,
            event_type="data_anonymization"
        )

    def log_data_deletion(self, user_id: str, data_types: list, reason: str):
        """Log data deletion events"""
        self.logger.info(
            "User data deleted",
            user_id=user_id,
            data_types=data_types,
            reason=reason,
            event_type="data_deletion"
        )

    def log_consent_change(self, user_id: str, consent_type: str, new_value: bool):
        """Log user consent changes"""
        self.logger.info(
            "User consent updated",
            user_id=user_id,
            consent_type=consent_type,
            new_value=new_value,
            event_type="consent_change"
        )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance"""
    return structlog.get_logger(name)


def get_security_logger() -> SecurityLogger:
    """Get security logger instance"""
    return SecurityLogger()


def get_audit_logger() -> AuditLogger:
    """Get audit logger instance"""
    return AuditLogger()


def get_performance_logger() -> PerformanceLogger:
    """Get performance logger instance"""
    return PerformanceLogger()


def get_privacy_logger() -> PrivacyLogger:
    """Get privacy logger instance"""
    return PrivacyLogger()


# Custom log levels for mental health app
CRISIS_LEVEL = 35  # Between WARNING and ERROR
SUPPORT_LEVEL = 25  # Between INFO and WARNING

logging.addLevelName(CRISIS_LEVEL, "CRISIS")
logging.addLevelName(SUPPORT_LEVEL, "SUPPORT")

def crisis(self, message, *args, **kwargs):
    """Log crisis-level events"""
    if self.isEnabledFor(CRISIS_LEVEL):
        self._log(CRISIS_LEVEL, message, args, **kwargs)

def support(self, message, *args, **kwargs):
    """Log support-level events"""
    if self.isEnabledFor(SUPPORT_LEVEL):
        self._log(SUPPORT_LEVEL, message, args, **kwargs)

# Add custom methods to Logger class
logging.Logger.crisis = crisis
logging.Logger.support = support
