"""Tests for AlertDetector arithmetic against the DECIMAL-backed health columns.

Regression cover for DAN-52: values read back from `health_indices` are
`decimal.Decimal`, the class thresholds are `float`, and Python refuses to mix
the two. Ten images lost their alerts to this during the 2026-08-15 rebuild.
"""
from datetime import date, timedelta
from decimal import Decimal

from app.alerts import AlertDetector
from app.models import FieldZone, HealthIndex


def _make_zone(db_session):
    zone = FieldZone(name="Ruzzi", geometry={"type": "Polygon", "coordinates": []})
    db_session.add(zone)
    db_session.flush()
    return zone


def _make_health_index(db_session, zone_id, acquisition_date, ndvi_mean, ndmi_mean="0.2"):
    health = HealthIndex(
        zone_id=zone_id,
        acquisition_date=acquisition_date,
        ndvi_mean=Decimal(ndvi_mean),
        ndmi_mean=Decimal(ndmi_mean),
    )
    db_session.add(health)
    db_session.flush()
    return health


def test_ndvi_drop_alert_is_built_from_decimal_columns(db_session):
    """A qualifying drop must produce an Alert, not a Decimal/float TypeError."""
    zone = _make_zone(db_session)
    today = date(2026, 8, 15)

    _make_health_index(db_session, zone.id, today - timedelta(days=10), "0.5500")
    current = _make_health_index(db_session, zone.id, today, "0.3000")

    alert = AlertDetector(db_session).detect_ndvi_drop(zone.id, current)

    assert alert is not None
    assert alert.alert_type == "ndvi_drop"
    # 0.55 previous + (-0.15) threshold = the NDVI at which the alert would trip
    assert float(alert.threshold_value) == 0.40


def test_ndvi_drop_returns_none_when_change_is_within_threshold(db_session):
    """A small drop must stay silent — and must not raise on the way there."""
    zone = _make_zone(db_session)
    today = date(2026, 8, 15)

    _make_health_index(db_session, zone.id, today - timedelta(days=10), "0.4000")
    current = _make_health_index(db_session, zone.id, today, "0.3500")

    assert AlertDetector(db_session).detect_ndvi_drop(zone.id, current) is None
