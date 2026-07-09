"""Tests for configuration management."""
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


def test_settings_has_jwt_defaults():
    """Test that JWT/auth settings expose sensible defaults (PRD-001)."""
    settings = Settings()

    assert settings.jwt_algorithm == "HS256"
    assert settings.access_token_ttl_minutes == 15
    assert settings.refresh_token_ttl_days == 30
    assert settings.email_verification_ttl_hours == 24
    # A secret always exists so local/test runs work; it must be overridable.
    assert settings.jwt_secret


def test_jwt_settings_load_from_environment(monkeypatch):
    """Test that JWT settings can be overridden from the environment."""
    monkeypatch.setenv("JWT_SECRET", "super-secret")
    monkeypatch.setenv("ACCESS_TOKEN_TTL_MINUTES", "5")
    monkeypatch.setenv("REFRESH_TOKEN_TTL_DAYS", "7")

    settings = Settings()

    assert settings.jwt_secret == "super-secret"
    assert settings.access_token_ttl_minutes == 5
    assert settings.refresh_token_ttl_days == 7
