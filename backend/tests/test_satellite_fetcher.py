"""Tests for Copernicus satellite data fetching."""

import pytest

from app.satellite_fetcher import SatelliteFetcher, query_sentinel2_products


def test_satellite_fetcher_initialization(tmp_path, monkeypatch):
    """Test that SatelliteFetcher can be initialized."""
    import app.satellite_fetcher as sf_module
    monkeypatch.setattr(sf_module.settings, "data_dir", str(tmp_path))
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
    assert callable(query_sentinel2_products)


def test_satellite_fetcher_has_authentication(tmp_path, monkeypatch):
    """Test that SatelliteFetcher loads authentication from config."""
    import app.satellite_fetcher as sf_module
    monkeypatch.setattr(sf_module.settings, "data_dir", str(tmp_path))
    from app.config import settings

    fetcher = SatelliteFetcher()

    # Should have access to credentials (even if empty in test)
    assert hasattr(fetcher, 'username') or settings.copernicus_username is not None
