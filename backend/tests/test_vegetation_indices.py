"""Tests for vegetation index calculations."""
import numpy as np
import pytest

from app.vegetation_indices import (
    calculate_health_score,
    calculate_ndmi,
    calculate_ndvi,
    calculate_osavi,
)


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


def test_osavi_differs_measurably_from_ndvi_on_reflectance_input():
    """The soil adjustment must actually change the number.

    This is the canary for the DN-vs-reflectance defect: L=0.16 only does
    anything when the denominator is reflectance in [0, 1]. Against raw
    digital numbers (~4000) it is inert and OSAVI collapses onto NDVI.
    Realistic whole-grove olive reflectance: red 0.09, NIR 0.20.
    """
    red = np.array([[0.09]], dtype=np.float32)
    nir = np.array([[0.20]], dtype=np.float32)

    ndvi = calculate_ndvi(red, nir)
    osavi = calculate_osavi(red, nir)

    # NDVI  = 0.11 / 0.29        = 0.3793
    # OSAVI = 0.11 / (0.29+0.16) = 0.2444
    assert pytest.approx(ndvi[0, 0], abs=0.001) == 0.379
    assert pytest.approx(osavi[0, 0], abs=0.001) == 0.244

    # Stored at DECIMAL(5,4), so anything below 0.0001 is invisible in the
    # database. Require a difference three orders of magnitude above that.
    assert abs(float(osavi[0, 0] - ndvi[0, 0])) > 0.1


def test_osavi_rejects_digital_number_input():
    """Passing unscaled DN must fail loudly, not silently return NDVI."""
    red_dn = np.array([[900.0]], dtype=np.float32)
    nir_dn = np.array([[2000.0]], dtype=np.float32)

    with pytest.raises(ValueError, match="reflectance"):
        calculate_osavi(red_dn, nir_dn)


def test_osavi_accepts_all_nan_zone():
    """A fully cloud-masked zone is all NaN and must not trip the range check."""
    red = np.full((1, 2), np.nan, dtype=np.float32)
    nir = np.full((1, 2), np.nan, dtype=np.float32)

    osavi = calculate_osavi(red, nir)

    assert np.all(np.isnan(osavi))


def test_osavi_accepts_small_negative_reflectance():
    """Post-offset L2A pixels can go slightly negative; that is valid, not DN."""
    red = np.array([[-0.02, 0.09]], dtype=np.float32)
    nir = np.array([[0.20, 0.20]], dtype=np.float32)

    osavi = calculate_osavi(red, nir)

    assert np.all(np.isfinite(osavi))


def test_calculate_health_score_from_ndvi():
    """Test health score calculation from NDVI values."""
    # NDVI of 0.7 should give high health score
    high_health = calculate_health_score(ndvi_mean=0.7, ndmi_mean=0.3)
    assert 70 <= high_health <= 100

    # NDVI of 0.3 should give medium health score
    medium_health = calculate_health_score(ndvi_mean=0.3, ndmi_mean=0.2)
    assert 30 <= medium_health <= 70

    # NDVI of 0.1 with drought stress (negative NDMI) should give low health score
    low_health = calculate_health_score(ndvi_mean=0.1, ndmi_mean=-0.2)
    assert 0 <= low_health <= 30


def test_calculate_health_score_considers_ndmi():
    """Test that health score considers moisture (NDMI)."""
    # Same NDVI but different NDMI should affect score
    score_good_moisture = calculate_health_score(ndvi_mean=0.6, ndmi_mean=0.3)
    score_poor_moisture = calculate_health_score(ndvi_mean=0.6, ndmi_mean=-0.2)

    # Good moisture should result in higher score
    assert score_good_moisture > score_poor_moisture
