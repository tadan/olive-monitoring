"""Vegetation index calculations for satellite imagery."""
from typing import Tuple

import numpy as np


def calculate_ndvi(red: np.ndarray, nir: np.ndarray) -> np.ndarray:
    """
    Calculate Normalized Difference Vegetation Index (NDVI).

    NDVI = (NIR - Red) / (NIR + Red)

    Range: -1 to +1
    - < 0.2: Bare soil, dead vegetation
    - 0.2-0.5: Sparse vegetation
    - 0.5-0.7: Healthy vegetation
    - > 0.7: Very dense healthy vegetation

    Args:
        red: Red band array (Band 4 for Sentinel-2)
        nir: Near-infrared band array (Band 8 for Sentinel-2)

    Returns:
        NDVI array with same shape as input
    """
    # Convert to float to prevent integer division
    red = red.astype(np.float32)
    nir = nir.astype(np.float32)

    # Calculate NDVI with zero division handling
    with np.errstate(divide='ignore', invalid='ignore'):
        ndvi = (nir - red) / (nir + red)

    # Set invalid values to NaN
    ndvi[~np.isfinite(ndvi)] = np.nan

    return ndvi


def calculate_ndmi(nir: np.ndarray, swir: np.ndarray) -> np.ndarray:
    """
    Calculate Normalized Difference Moisture Index (NDMI).

    NDMI = (NIR - SWIR) / (NIR + SWIR)

    Range: -1 to +1
    - < -0.2: Severe drought stress
    - -0.2 to 0.0: Moderate water stress
    - 0.0 to 0.4: Adequate moisture
    - > 0.4: High moisture/waterlogged

    Args:
        nir: Near-infrared band array (Band 8 for Sentinel-2)
        swir: Shortwave infrared band array (Band 11 for Sentinel-2)

    Returns:
        NDMI array with same shape as input
    """
    # Convert to float
    nir = nir.astype(np.float32)
    swir = swir.astype(np.float32)

    # Calculate NDMI with zero division handling
    with np.errstate(divide='ignore', invalid='ignore'):
        ndmi = (nir - swir) / (nir + swir)

    # Set invalid values to NaN
    ndmi[~np.isfinite(ndmi)] = np.nan

    return ndmi


def calculate_arvi(red: np.ndarray, nir: np.ndarray, blue: np.ndarray) -> np.ndarray:
    """
    Calculate Atmospherically Resistant Vegetation Index (ARVI).

    ARVI = (NIR - (2*Red - Blue)) / (NIR + (2*Red - Blue))

    ARVI is designed to minimize atmospheric effects (aerosols, haze) that
    can affect vegetation index accuracy. It uses the blue band to self-correct
    for atmospheric scattering.

    Range: -1 to +1
    - < 0: Non-vegetated surfaces
    - 0.2-0.4: Sparse vegetation
    - 0.4-0.6: Moderate vegetation
    - > 0.6: Dense healthy vegetation

    Research shows ARVI correlates strongly with disease incidence and severity
    (r²=0.73-0.76) in olive groves, making it excellent for health monitoring.

    Args:
        red: Red band array (Band 4 for Sentinel-2)
        nir: Near-infrared band array (Band 8 for Sentinel-2)
        blue: Blue band array (Band 2 for Sentinel-2)

    Returns:
        ARVI array with same shape as input
    """
    # Convert to float
    red = red.astype(np.float32)
    nir = nir.astype(np.float32)
    blue = blue.astype(np.float32)

    # Calculate ARVI with zero division handling
    with np.errstate(divide='ignore', invalid='ignore'):
        rb = 2 * red - blue
        arvi = (nir - rb) / (nir + rb)

    # Set invalid values to NaN
    arvi[~np.isfinite(arvi)] = np.nan

    return arvi


def calculate_osavi(red: np.ndarray, nir: np.ndarray, soil_factor: float = 0.16) -> np.ndarray:
    """
    Calculate Optimized Soil-Adjusted Vegetation Index (OSAVI).

    OSAVI = (NIR - Red) / (NIR + Red + L)

    OSAVI reduces soil background effects that can interfere with vegetation
    measurements, particularly important for olive groves where soil is visible
    between trees. The soil adjustment factor L is optimized for various
    canopy conditions.

    Range: -1 to +1 (similar to NDVI but soil-adjusted)
    - < 0.2: Bare soil, minimal vegetation
    - 0.2-0.4: Sparse vegetation
    - 0.4-0.6: Moderate vegetation coverage
    - > 0.6: Dense vegetation

    Research shows OSAVI achieves high correlation with field observations
    (r²=0.73-0.76) and is particularly effective for tree crops with soil exposure.

    Args:
        red: Red band array (Band 4 for Sentinel-2)
        nir: Near-infrared band array (Band 8 for Sentinel-2)
        soil_factor: Soil brightness correction factor (default 0.16)
                     Standard value is 0.16 for optimal performance

    Returns:
        OSAVI array with same shape as input
    """
    # Convert to float
    red = red.astype(np.float32)
    nir = nir.astype(np.float32)

    # Calculate OSAVI with zero division handling
    with np.errstate(divide='ignore', invalid='ignore'):
        osavi = (nir - red) / (nir + red + soil_factor)

    # Set invalid values to NaN
    osavi[~np.isfinite(osavi)] = np.nan

    return osavi


def calculate_health_score(
    ndvi_mean: float,
    ndmi_mean: float,
    arvi_mean: float = None,
    osavi_mean: float = None
) -> int:
    """
    Calculate overall vegetation health score (0-100).

    Combines multiple vegetation indices into a single interpretable score:
    - NDVI: General vegetation vigor
    - NDMI: Moisture status
    - ARVI: Atmospherically-corrected vegetation (optional)
    - OSAVI: Soil-adjusted vegetation (optional)

    When ARVI and OSAVI are provided, uses a multi-index composite score
    for more robust health assessment.

    Args:
        ndvi_mean: Mean NDVI value
        ndmi_mean: Mean NDMI value
        arvi_mean: Mean ARVI value (optional, for enhanced accuracy)
        osavi_mean: Mean OSAVI value (optional, for soil-adjusted assessment)

    Returns:
        Health score from 0 (poor) to 100 (excellent)
    """
    # NDVI contribution
    # Map NDVI from [-1, 1] to [0, 100]
    # Emphasize the 0-1 range where vegetation exists
    if ndvi_mean < 0:
        ndvi_score = 0
    elif ndvi_mean > 1:
        ndvi_score = 100
    else:
        # Linear mapping: 0 NDVI = 0 score, 1 NDVI = 100 score
        ndvi_score = ndvi_mean * 100

    # NDMI contribution
    # Optimal NDMI is around 0.2-0.4 (adequate moisture)
    if ndmi_mean < -0.3:
        # Severe drought
        ndmi_score = 0
    elif ndmi_mean < 0:
        # Moderate stress
        ndmi_score = 40 + (ndmi_mean + 0.3) / 0.3 * 40  # Maps -0.3 to 0 → 40 to 80
    elif ndmi_mean < 0.4:
        # Optimal range
        ndmi_score = 80 + ndmi_mean / 0.4 * 20  # Maps 0 to 0.4 → 80 to 100
    else:
        # Too wet (waterlogged)
        ndmi_score = max(0, 100 - (ndmi_mean - 0.4) * 50)

    # If ARVI and OSAVI are provided, use multi-index composite score
    if arvi_mean is not None and osavi_mean is not None:
        # ARVI contribution (atmospherically resistant)
        # Similar to NDVI but more robust to atmospheric effects
        if arvi_mean < 0:
            arvi_score = 0
        elif arvi_mean > 1:
            arvi_score = 100
        else:
            arvi_score = arvi_mean * 100

        # OSAVI contribution (soil-adjusted)
        # Similar to NDVI but corrects for soil background
        if osavi_mean < 0:
            osavi_score = 0
        elif osavi_mean > 1:
            osavi_score = 100
        else:
            osavi_score = osavi_mean * 100

        # Multi-index composite weighting (research-backed)
        # ARVI: 30% (atmospheric correction for accurate readings)
        # OSAVI: 30% (soil adjustment for olive groves)
        # NDVI: 20% (general vegetation baseline)
        # NDMI: 20% (moisture status)
        health_score = int(
            arvi_score * 0.30 +
            osavi_score * 0.30 +
            ndvi_score * 0.20 +
            ndmi_score * 0.20
        )
    else:
        # Legacy two-index score (NDVI + NDMI only)
        # NDVI: 70% weight, NDMI: 30% weight
        health_score = int(ndvi_score * 0.7 + ndmi_score * 0.3)

    # Clamp to [0, 100]
    return max(0, min(100, health_score))


def calculate_statistics(data: np.ndarray) -> Tuple[float, float, float, float]:
    """
    Calculate statistics for an array, ignoring NaN values.

    Args:
        data: NumPy array of values

    Returns:
        Tuple of (mean, std, min, max)
    """
    return (
        float(np.nanmean(data)),
        float(np.nanstd(data)),
        float(np.nanmin(data)),
        float(np.nanmax(data))
    )
