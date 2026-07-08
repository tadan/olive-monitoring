"""Shared pytest fixtures for the backend test suite."""
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base


@pytest.fixture(scope="session")
def test_engine():
    """SQLite in-memory engine — no PostgreSQL required in CI."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def db_session(test_engine):
    """Transactional session that rolls back after each test."""
    connection = test_engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    yield session
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture
def db_connection(test_engine):
    """Raw connection for tests that need to run raw SQL."""
    with test_engine.connect() as conn:
        yield conn
