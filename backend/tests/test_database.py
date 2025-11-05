"""Tests for database connection and models."""
import pytest
from app.database import get_db_engine, get_session
from app.models import FieldZone, SatelliteImage, HealthIndex, Alert
from sqlalchemy import text


def test_database_engine_creation():
    """Test that database engine can be created."""
    engine = get_db_engine()

    assert engine is not None
    assert "postgresql" in str(engine.url)


def test_database_connection():
    """Test that we can connect to the database."""
    engine = get_db_engine()

    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
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
