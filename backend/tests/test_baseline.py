"""Tests for BaselineManager anomaly arithmetic against DECIMAL-backed baselines.

Regression cover for DAN-52: `baseline.mean_value` and `baseline.std_dev` come
back as `decimal.Decimal` while the incoming value and `std_dev_threshold` are
`float`.
"""
from datetime import date
from decimal import Decimal

from app.baseline import BaselineManager
from app.models import BaselineStatistic, FieldZone


def _make_zone(db_session):
    zone = FieldZone(name="Ruzzi", geometry={"type": "Polygon", "coordinates": []})
    db_session.add(zone)
    db_session.flush()
    return zone


def _make_baseline(db_session, zone_id, metric, season, mean_value, std_dev):
    baseline = BaselineStatistic(
        zone_id=zone_id,
        metric=metric,
        season=season,
        mean_value=Decimal(mean_value),
        std_dev=Decimal(std_dev),
        sample_count=30,
    )
    db_session.add(baseline)
    db_session.flush()
    return baseline


def test_is_anomaly_flags_a_deviation_beyond_the_threshold(db_session):
    """A 4-sigma deviation must read as anomalous, not raise a TypeError."""
    zone = _make_zone(db_session)
    summer_day = date(2026, 8, 15)
    _make_baseline(db_session, zone.id, "ndvi", "summer", "0.4000", "0.0500")

    is_anomalous, baseline = BaselineManager(db_session).is_anomaly(
        zone.id, "ndvi", 0.20, summer_day
    )

    assert is_anomalous is True
    assert baseline is not None


def test_is_anomaly_accepts_a_value_inside_the_threshold(db_session):
    """A 1-sigma deviation must read as normal."""
    zone = _make_zone(db_session)
    summer_day = date(2026, 8, 15)
    _make_baseline(db_session, zone.id, "ndvi", "summer", "0.4000", "0.0500")

    is_anomalous, _ = BaselineManager(db_session).is_anomaly(
        zone.id, "ndvi", 0.45, summer_day
    )

    assert is_anomalous is False
