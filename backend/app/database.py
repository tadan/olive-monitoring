"""Database connection and session management."""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from app.config import settings

# Create database engine
engine = None

def get_db_engine():
    """Get or create database engine."""
    global engine
    if engine is None:
        engine = create_engine(
            settings.database_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10
        )
    return engine


# Create SessionLocal class
SessionLocal = None

def get_session_local():
    """Get or create SessionLocal class."""
    global SessionLocal
    if SessionLocal is None:
        engine = get_db_engine()
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return SessionLocal


def get_session() -> Session:
    """Get a database session."""
    SessionLocal = get_session_local()
    session = SessionLocal()
    try:
        return session
    finally:
        pass  # Session will be closed by caller


def get_db():
    """
    FastAPI dependency for database sessions.
    Yields a database session and ensures it's closed after use.
    """
    SessionLocal = get_session_local()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Base class for models
Base = declarative_base()
