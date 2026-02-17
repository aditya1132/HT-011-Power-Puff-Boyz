# AI Mental Health Companion - Database Module
# This file makes the database directory a Python package and exports database functionality

from .database import (
    Base,
    engine,
    SessionLocal,
    metadata,
    get_db,
    create_tables,
    drop_tables,
    test_connection,
    DatabaseManager,
    db_manager
)

from .init_db import (
    create_database_if_not_exists,
    seed_initial_data,
    verify_installation,
    reset_database,
    main as init_main
)

__all__ = [
    # Database core
    "Base",
    "engine",
    "SessionLocal",
    "metadata",
    "get_db",
    "create_tables",
    "drop_tables",
    "test_connection",
    "DatabaseManager",
    "db_manager",

    # Database initialization
    "create_database_if_not_exists",
    "seed_initial_data",
    "verify_installation",
    "reset_database",
    "init_main"
]

# Database module version
DATABASE_MODULE_VERSION = "1.0.0"

# Database schema version
SCHEMA_VERSION = "1.0.0"

# Supported database types
SUPPORTED_DATABASES = [
    "sqlite",
    "mssql",
    "postgresql"
]

def get_database_info():
    """Get information about the database configuration"""
    from app.core.config import get_settings
    settings = get_settings()

    db_type = "unknown"
    if settings.DATABASE_URL.startswith("sqlite"):
        db_type = "sqlite"
    elif "mssql" in settings.DATABASE_URL:
        db_type = "mssql"
    elif "postgresql" in settings.DATABASE_URL:
        db_type = "postgresql"

    return {
        "module_version": DATABASE_MODULE_VERSION,
        "schema_version": SCHEMA_VERSION,
        "database_type": db_type,
        "connection_url": settings.DATABASE_URL.split("@")[0] + "@***" if "@" in settings.DATABASE_URL else "Local Database",
        "pool_size": getattr(settings, 'DATABASE_POOL_SIZE', 5),
        "echo_enabled": getattr(settings, 'DATABASE_ECHO', False)
    }

def validate_database_setup():
    """Validate that the database is properly configured and accessible"""
    try:
        # Test connection
        if not test_connection():
            return False, "Database connection failed"

        # Check if tables exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()

        required_tables = ["users", "mood_logs", "chat_history", "coping_sessions"]
        missing_tables = [table for table in required_tables if table not in tables]

        if missing_tables:
            return False, f"Missing required tables: {', '.join(missing_tables)}"

        return True, "Database setup is valid"

    except Exception as e:
        return False, f"Database validation failed: {str(e)}"

# Database connection health check
def health_check():
    """Perform a quick health check on the database"""
    try:
        # Test basic connectivity
        connection_ok = test_connection()
        if not connection_ok:
            return {
                "status": "unhealthy",
                "message": "Database connection failed",
                "details": None
            }

        # Test basic query
        with SessionLocal() as session:
            result = session.execute("SELECT 1")
            result.fetchone()

        # Get basic stats
        with SessionLocal() as session:
            from app.models import User, MoodLog
            user_count = session.query(User).count()
            mood_count = session.query(MoodLog).count()

        return {
            "status": "healthy",
            "message": "Database is operational",
            "details": {
                "total_users": user_count,
                "total_mood_logs": mood_count,
                "connection_pool_size": getattr(engine.pool, 'size', 'N/A')
            }
        }

    except Exception as e:
        return {
            "status": "unhealthy",
            "message": f"Database health check failed: {str(e)}",
            "details": None
        }
