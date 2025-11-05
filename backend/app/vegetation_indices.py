"""Vegetation index calculations for satellite imagery."""
import numpy as np
from typing import Tuple


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


def calculate_health_score(ndvi_mean: float, ndmi_mean: float) -> int:
    """
    Calculate overall vegetation health score (0-100).

    Combines NDVI (vegetation vigor) and NDMI (moisture status)
    into a single interpretable score.

    Args:
        ndvi_mean: Mean NDVI value
        ndmi_mean: Mean NDMI value

    Returns:
        Health score from 0 (poor) to 100 (excellent)
    """
    # NDVI contribution (70% weight)
    # Map NDVI from [-1, 1] to [0, 100]
    # Emphasize the 0-1 range where vegetation exists
    if ndvi_mean < 0:
        ndvi_score = 0
    elif ndvi_mean > 1:
        ndvi_score = 100
    else:
        # Linear mapping: 0 NDVI = 0 score, 1 NDVI = 100 score
        ndvi_score = ndvi_mean * 100

    # NDMI contribution (30% weight)
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

    # Combine scores with weights
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
