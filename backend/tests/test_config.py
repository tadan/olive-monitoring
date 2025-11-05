"""Tests for configuration management."""
import pytest
from app.config import Settings


def test_settings_loads_from_environment(monkeypatch):
    """Test that settings load from environment variables."""
    monkeypatch.setenv("DB_HOST", "testhost")
    monkeypatch.setenv("DB_PORT", "5555")
    monkeypatch.setenv("DB_NAME", "testdb")
    monkeypatch.setenv("DB_USER", "testuser")
    monkeypatch.setenv("DB_PASSWORD", "testpass")

    settings = Settings()

    assert settings.db_host == "testhost"
    assert settings.db_port == 5555
    assert settings.db_name == "testdb"
    assert settings.db_user == "testuser"
    assert settings.db_password == "testpass"


def test_settings_has_database_url():
    """Test that settings provides a database URL."""
    settings = Settings()

    assert "postgresql://" in settings.database_url
    assert settings.db_name in settings.database_url


def test_settings_has_copernicus_credentials(monkeypatch):
    """Test that Copernicus credentials are loaded."""
    monkeypatch.setenv("COPERNICUS_USERNAME", "testuser")
    monkeypatch.setenv("COPERNICUS_PASSWORD", "testpass")

    settings = Settings()

    assert settings.copernicus_username == "testuser"
    assert settings.copernicus_password == "testpass"
