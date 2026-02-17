from pydantic_settings import BaseSettings
from pydantic import Field, validator
from typing import List, Optional
from functools import lru_cache
import os


class Settings(BaseSettings):
    """Application settings with environment variable support"""

    # Application settings
    APP_NAME: str = Field(default="AI Mental Health Companion", description="Application name")
    VERSION: str = Field(default="1.0.0", description="Application version")
    ENVIRONMENT: str = Field(default="development", description="Environment (development/staging/production)")
    DEBUG: bool = Field(default=True, description="Debug mode")

    # Server settings
    HOST: str = Field(default="0.0.0.0", description="Server host")
    PORT: int = Field(default=8000, description="Server port")

    # Security settings
    SECRET_KEY: str = Field(..., description="Secret key for JWT tokens")
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30, description="Token expiration time")

    # CORS settings
    ALLOWED_ORIGINS: List[str] = Field(
        default=[
            "http://localhost:3000",
            "http://localhost:3001",
            "http://127.0.0.1:3000",
            "https://your-frontend-domain.com"
        ],
        description="Allowed CORS origins"
    )
    ALLOWED_HOSTS: List[str] = Field(
        default=["localhost", "127.0.0.1", "your-api-domain.com"],
        description="Allowed hosts"
    )

    # Database settings
    DATABASE_URL: str = Field(..., description="Database connection URL")
    DATABASE_POOL_SIZE: int = Field(default=5, description="Database connection pool size")
    DATABASE_POOL_OVERFLOW: int = Field(default=10, description="Database pool overflow")
    DATABASE_ECHO: bool = Field(default=False, description="Echo SQL queries")

    # AI/NLP settings
    AI_MODEL_TYPE: str = Field(default="rule_based", description="AI model type (rule_based/ml)")
    EMOTION_DETECTION_THRESHOLD: float = Field(default=0.6, description="Emotion detection confidence threshold")
    SAFETY_KEYWORDS_ENABLED: bool = Field(default=True, description="Enable safety keyword detection")

    # Safety settings
    CRISIS_KEYWORDS: List[str] = Field(
        default=[
            "suicide", "kill myself", "end my life", "hurt myself",
            "self-harm", "cutting", "overdose", "die", "death wish",
            "worthless", "hopeless", "can't go on", "no point in living"
        ],
        description="Crisis detection keywords"
    )

    # Rate limiting
    RATE_LIMIT_ENABLED: bool = Field(default=True, description="Enable rate limiting")
    RATE_LIMIT_REQUESTS: int = Field(default=100, description="Requests per minute per IP")
    RATE_LIMIT_WINDOW: int = Field(default=60, description="Rate limit window in seconds")

    # Logging settings
    LOG_LEVEL: str = Field(default="INFO", description="Logging level")
    LOG_FORMAT: str = Field(default="json", description="Log format (json/text)")
    LOG_FILE: Optional[str] = Field(default=None, description="Log file path")

    # External API settings
    OPENAI_API_KEY: Optional[str] = Field(default=None, description="OpenAI API key (optional)")
    HUGGINGFACE_API_KEY: Optional[str] = Field(default=None, description="HuggingFace API key (optional)")

    # Cache settings
    REDIS_URL: Optional[str] = Field(default=None, description="Redis URL for caching")
    CACHE_TTL: int = Field(default=300, description="Cache TTL in seconds")

    # Monitoring settings
    PROMETHEUS_METRICS_ENABLED: bool = Field(default=False, description="Enable Prometheus metrics")
    HEALTH_CHECK_ENABLED: bool = Field(default=True, description="Enable health check endpoint")

    # Privacy settings
    DATA_RETENTION_DAYS: int = Field(default=365, description="Data retention period in days")
    ENCRYPT_SENSITIVE_DATA: bool = Field(default=True, description="Encrypt sensitive user data")
    ANONYMOUS_USAGE_ANALYTICS: bool = Field(default=False, description="Collect anonymous usage analytics")

    # Feature flags
    CHAT_HISTORY_ENABLED: bool = Field(default=True, description="Enable chat history storage")
    MOOD_TRENDS_ENABLED: bool = Field(default=True, description="Enable mood trend analysis")
    DAILY_CHECKIN_ENABLED: bool = Field(default=True, description="Enable daily check-in feature")
    COPING_TOOLS_ENABLED: bool = Field(default=True, description="Enable coping tools feature")

    @validator("ENVIRONMENT")
    def validate_environment(cls, v):
        """Validate environment value"""
        allowed_envs = ["development", "staging", "production"]
        if v.lower() not in allowed_envs:
            raise ValueError(f"Environment must be one of: {allowed_envs}")
        return v.lower()

    @validator("LOG_LEVEL")
    def validate_log_level(cls, v):
        """Validate log level"""
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"Log level must be one of: {allowed_levels}")
        return v.upper()

    @validator("DATABASE_URL")
    def validate_database_url(cls, v):
        """Validate database URL format"""
        if not v:
            raise ValueError("DATABASE_URL is required")
        if not v.startswith(("mssql://", "mssql+pyodbc://", "sqlite:///")):
            raise ValueError("DATABASE_URL must be a valid SQL Server or SQLite connection string")
        return v

    @validator("SECRET_KEY")
    def validate_secret_key(cls, v):
        """Validate secret key strength"""
        if not v:
            raise ValueError("SECRET_KEY is required")
        if len(v) < 32:
            raise ValueError("SECRET_KEY must be at least 32 characters long")
        return v

    @validator("ALLOWED_ORIGINS")
    def validate_allowed_origins(cls, v):
        """Validate CORS origins"""
        if not v:
            raise ValueError("At least one CORS origin must be specified")
        return v

    @validator("EMOTION_DETECTION_THRESHOLD")
    def validate_emotion_threshold(cls, v):
        """Validate emotion detection threshold"""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Emotion detection threshold must be between 0.0 and 1.0")
        return v

    def is_development(self) -> bool:
        """Check if running in development environment"""
        return self.ENVIRONMENT == "development"

    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.ENVIRONMENT == "production"

    def get_database_url(self) -> str:
        """Get formatted database URL"""
        if self.is_development() and self.DATABASE_URL.startswith("sqlite:///"):
            # Ensure SQLite database directory exists
            db_path = self.DATABASE_URL.replace("sqlite:///", "")
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
        return self.DATABASE_URL

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

        # Example .env file content
        env_example = """
# Application Configuration
SECRET_KEY=your-super-secret-key-here-min-32-characters-long
ENVIRONMENT=development
DEBUG=True

# Database Configuration (Choose one)
# SQL Server (Production)
DATABASE_URL=mssql+pyodbc://username:password@server/database?driver=ODBC+Driver+17+for+SQL+Server

# SQLite (Development)
# DATABASE_URL=sqlite:///./data/mental_health_companion.db

# Optional AI/ML APIs
OPENAI_API_KEY=your-openai-key
HUGGINGFACE_API_KEY=your-huggingface-key

# Optional Redis for caching
REDIS_URL=redis://localhost:6379/0

# CORS Origins (comma-separated)
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001

# Monitoring
PROMETHEUS_METRICS_ENABLED=False
LOG_LEVEL=INFO
        """


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()


# Development settings override
class DevelopmentSettings(Settings):
    """Development-specific settings"""
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    DATABASE_ECHO: bool = True
    LOG_LEVEL: str = "DEBUG"
    RATE_LIMIT_ENABLED: bool = False


# Production settings override
class ProductionSettings(Settings):
    """Production-specific settings"""
    ENVIRONMENT: str = "production"
    DEBUG: bool = False
    DATABASE_ECHO: bool = False
    LOG_LEVEL: str = "INFO"
    RATE_LIMIT_ENABLED: bool = True
    PROMETHEUS_METRICS_ENABLED: bool = True


def get_settings_by_environment(env: str = None) -> Settings:
    """Get settings based on environment"""
    if env is None:
        env = os.getenv("ENVIRONMENT", "development")

    if env == "production":
        return ProductionSettings()
    elif env == "development":
        return DevelopmentSettings()
    else:
        return Settings()
