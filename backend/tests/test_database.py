"""Tests for database connection and models."""
from sqlalchemy import text

from app.models import Alert, FieldZone, HealthIndex, SatelliteImage, User


def test_database_engine_creation(test_engine):
    """Test that an engine can be created (uses SQLite fixture in CI)."""
    assert test_engine is not None


def test_database_connection(db_connection):
    """Test that we can execute SQL against the test DB."""
    result = db_connection.execute(text("SELECT 1"))
    assert result.fetchone()[0] == 1


def test_field_zone_model_has_required_fields():
    """Test that FieldZone model has expected attributes."""
    assert hasattr(FieldZone, 'id')
    assert hasattr(FieldZone, 'name')
    assert hasattr(FieldZone, 'geometry')
    assert hasattr(FieldZone, 'area_hectares')


def test_satellite_image_model_has_required_fields():
    """Test that SatelliteImage model has expected attributes."""
    assert hasattr(SatelliteImage, 'id')
    assert hasattr(SatelliteImage, 'acquisition_date')
    assert hasattr(SatelliteImage, 'satellite')
    assert hasattr(SatelliteImage, 'scene_id')


def test_health_index_model_has_required_fields():
    """Test that HealthIndex model has expected attributes."""
    assert hasattr(HealthIndex, 'id')
    assert hasattr(HealthIndex, 'zone_id')
    assert hasattr(HealthIndex, 'image_id')
    assert hasattr(HealthIndex, 'ndvi_mean')
    assert hasattr(HealthIndex, 'ndmi_mean')


def test_alert_model_has_required_fields():
    """Test that Alert model has expected attributes."""
    assert hasattr(Alert, 'id')
    assert hasattr(Alert, 'zone_id')
    assert hasattr(Alert, 'alert_type')
    assert hasattr(Alert, 'severity')
    assert hasattr(Alert, 'title')


def test_user_model_has_required_fields():
    """Test that User model has the auth foundation attributes (PRD-001)."""
    assert hasattr(User, 'id')
    assert hasattr(User, 'email')
    assert hasattr(User, 'password_hash')
    assert hasattr(User, 'is_verified')
    assert hasattr(User, 'created_at')


def test_user_can_be_persisted(db_session):
    """A user row can be created and read back with a unique email."""
    user = User(email="grower@example.com", password_hash="argon2id$fakehash")
    db_session.add(user)
    db_session.flush()

    assert user.id is not None
    fetched = db_session.query(User).filter_by(email="grower@example.com").one()
    assert fetched.password_hash == "argon2id$fakehash"
    # is_verified defaults to False at the application level.
    assert fetched.is_verified is False
