"""Tests for vegetation index calculations."""
import pytest
import numpy as np
from app.vegetation_indices import calculate_ndvi, calculate_ndmi, calculate_health_score


def test_calculate_ndvi_with_valid_data():
    """Test NDVI calculation with valid band data."""
    # Create sample band data
    red = np.array([[100, 150, 200]], dtype=np.float32)
    nir = np.array([[200, 300, 400]], dtype=np.float32)

    ndvi = calculate_ndvi(red, nir)

    # Check shape matches input
    assert ndvi.shape == red.shape

    # Check values are in expected range [-1, 1]
    assert np.all(ndvi >= -1)
    assert np.all(ndvi <= 1)

    # Check specific calculation
    # NDVI = (NIR - Red) / (NIR + Red)
    # For first pixel: (200 - 100) / (200 + 100) = 100 / 300 = 0.333...
    assert pytest.approx(ndvi[0, 0], abs=0.01) == 0.333


def test_calculate_ndvi_handles_zero_division():
    """Test that NDVI handles zero division gracefully."""
    red = np.array([[0, 0]], dtype=np.float32)
    nir = np.array([[0, 0]], dtype=np.float32)

    ndvi = calculate_ndvi(red, nir)

    # Should return NaN or 0 for division by zero
    assert np.all(np.isnan(ndvi) | (ndvi == 0))


def test_calculate_ndmi_with_valid_data():
    """Test NDMI calculation with valid band data."""
    nir = np.array([[800, 900]], dtype=np.float32)
    swir = np.array([[200, 300]], dtype=np.float32)

    ndmi = calculate_ndmi(nir, swir)

    # Check shape matches input
    assert ndmi.shape == nir.shape

    # Check values are in expected range [-1, 1]
    assert np.all(ndmi >= -1)
    assert np.all(ndmi <= 1)

    # NDMI = (NIR - SWIR) / (NIR + SWIR)
    # For first pixel: (800 - 200) / (800 + 200) = 600 / 1000 = 0.6
    assert pytest.approx(ndmi[0, 0], abs=0.01) == 0.6


def test_calculate_health_score_from_ndvi():
    """Test health score calculation from NDVI values."""
    # NDVI of 0.7 should give high health score
    high_health = calculate_health_score(ndvi_mean=0.7, ndmi_mean=0.3)
    assert 70 <= high_health <= 100

    # NDVI of 0.3 should give medium health score
    medium_health = calculate_health_score(ndvi_mean=0.3, ndmi_mean=0.2)
    assert 30 <= medium_health <= 70

    # NDVI of 0.1 should give low health score
    low_health = calculate_health_score(ndvi_mean=0.1, ndmi_mean=0.0)
    assert 0 <= low_health <= 30


def test_calculate_health_score_considers_ndmi():
    """Test that health score considers moisture (NDMI)."""
    # Same NDVI but different NDMI should affect score
    score_good_moisture = calculate_health_score(ndvi_mean=0.6, ndmi_mean=0.3)
    score_poor_moisture = calculate_health_score(ndvi_mean=0.6, ndmi_mean=-0.2)

    # Good moisture should result in higher score
    assert score_good_moisture > score_poor_moisture
