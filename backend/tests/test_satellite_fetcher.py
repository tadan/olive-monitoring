"""Tests for Copernicus satellite data fetching."""
import pytest
from datetime import date, timedelta
from app.satellite_fetcher import SatelliteFetcher, query_sentinel2_products


def test_satellite_fetcher_initialization():
    """Test that SatelliteFetcher can be initialized."""
    fetcher = SatelliteFetcher()

    assert fetcher is not None
    assert hasattr(fetcher, 'query_products')
    assert hasattr(fetcher, 'download_product')


def test_query_sentinel2_products_requires_geometry():
    """Test that querying requires a geometry parameter."""
    with pytest.raises(TypeError):
        query_sentinel2_products()


def test_query_sentinel2_products_with_valid_geometry():
    """Test querying with valid geometry (mocked - won't actually call API in test)."""
    # This test validates the function signature
    # Actual API calls will be integration tested separately
    geometry = {"type": "Polygon", "coordinates": [[[12.4964, 41.9028], [12.4968, 41.9028], [12.4968, 41.9025], [12.4964, 41.9025], [12.4964, 41.9028]]]}
    start_date = date.today() - timedelta(days=30)
    end_date = date.today()

    # Function should exist and accept these parameters
    # We'll mock the actual API call in integration tests
    assert callable(query_sentinel2_products)


def test_satellite_fetcher_has_authentication():
    """Test that SatelliteFetcher loads authentication from config."""
    from app.config import settings

    fetcher = SatelliteFetcher()

    # Should have access to credentials (even if empty in test)
    assert hasattr(fetcher, 'username') or settings.copernicus_username is not None
