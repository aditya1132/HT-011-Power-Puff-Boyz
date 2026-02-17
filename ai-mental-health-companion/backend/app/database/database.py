from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from typing import Generator
import logging

from app.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# Create SQLAlchemy engine
if settings.DATABASE_URL.startswith("sqlite"):
    # SQLite configuration for development
    engine = create_engine(
        settings.DATABASE_URL,
        connect_args={
            "check_same_thread": False,
            "timeout": 20
        },
        poolclass=StaticPool,
        echo=settings.DATABASE_ECHO
    )
else:
    # SQL Server configuration for production
    engine = create_engine(
        settings.DATABASE_URL,
        pool_size=settings.DATABASE_POOL_SIZE,
        pool_pre_ping=True,
        pool_recycle=3600,
        max_overflow=settings.DATABASE_POOL_OVERFLOW,
        echo=settings.DATABASE_ECHO,
        connect_args={
            "timeout": 30,
            "isolation_level": "READ_COMMITTED"
        }
    )

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

# Metadata for schema management
metadata = MetaData()


def get_db() -> Generator[Session, None, None]:
    """
    Database dependency for FastAPI

    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    except Exception as e:
        logger.error(f"Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()


def create_tables():
    """Create all database tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Failed to create database tables: {e}")
        raise


def drop_tables():
    """Drop all database tables (use with caution)"""
    try:
        Base.metadata.drop_all(bind=engine)
        logger.warning("All database tables dropped")
    except Exception as e:
        logger.error(f"Failed to drop database tables: {e}")
        raise


def test_connection():
    """Test database connection"""
    try:
        with engine.connect() as connection:
            result = connection.execute("SELECT 1")
            logger.info("Database connection test successful")
            return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        return False


class DatabaseManager:
    """Database management utilities"""

    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal

    def get_session(self) -> Session:
        """Get a new database session"""
        return SessionLocal()

    def execute_raw_sql(self, sql: str, params: dict = None):
        """Execute raw SQL query"""
        with engine.connect() as connection:
            return connection.execute(sql, params or {})

    def backup_database(self, backup_path: str):
        """Create database backup (implementation depends on database type)"""
        if settings.DATABASE_URL.startswith("sqlite"):
            import shutil
            db_path = settings.DATABASE_URL.replace("sqlite:///", "")
            shutil.copy2(db_path, backup_path)
            logger.info(f"SQLite database backed up to {backup_path}")
        else:
            logger.warning("Database backup not implemented for non-SQLite databases")

    def get_table_info(self):
        """Get information about database tables"""
        inspector = engine.inspect(engine)
        tables = {}
        for table_name in inspector.get_table_names():
            tables[table_name] = {
                "columns": [col["name"] for col in inspector.get_columns(table_name)],
                "indexes": [idx["name"] for idx in inspector.get_indexes(table_name)]
            }
        return tables


# Global database manager instance
db_manager = DatabaseManager()
