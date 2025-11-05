"""Copernicus Sentinel-2 satellite data fetching."""
from typing import Dict, List, Optional, Tuple
from datetime import date, datetime, timedelta
from pathlib import Path
import logging

from sentinelsat import SentinelAPI
from shapely.geometry import shape
from app.config import settings

logger = logging.getLogger(__name__)


class SatelliteFetcher:
    """Fetches Sentinel-2 satellite imagery from Copernicus Data Space."""

    def __init__(self, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize the satellite fetcher.

        Args:
            username: Copernicus username (defaults to settings)
            password: Copernicus password (defaults to settings)
        """
        self.username = username or settings.copernicus_username
        self.password = password or settings.copernicus_password
        self.data_dir = Path(settings.data_dir)

        # Initialize Sentinel API
        # Note: Copernicus Data Space uses different endpoint than old SciHub
        self.api = None  # Will be initialized on first use

        # Create data directories
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "raw").mkdir(exist_ok=True)
        (self.data_dir / "processed").mkdir(exist_ok=True)

    def _get_api(self) -> SentinelAPI:
        """Get or create SentinelAPI instance."""
        if self.api is None:
            # Copernicus Data Space API endpoint
            self.api = SentinelAPI(
                self.username,
                self.password,
                'https://catalogue.dataspace.copernicus.eu/resto'
            )
        return self.api

    def query_products(
        self,
        geometry: Dict,
        start_date: date,
        end_date: date,
        cloud_coverage_max: int = 30
    ) -> List[Dict]:
        """
        Query available Sentinel-2 products.

        Args:
            geometry: GeoJSON geometry defining area of interest
            start_date: Start date for search
            end_date: End date for search
            cloud_coverage_max: Maximum cloud coverage percentage

        Returns:
            List of product dictionaries with metadata
        """
        api = self._get_api()

        # Convert GeoJSON to WKT
        geom = shape(geometry)
        footprint = geom.wkt

        # Query products
        products = api.query(
            area=footprint,
            date=(start_date, end_date),
            platformname='Sentinel-2',
            cloudcoverpercentage=(0, cloud_coverage_max)
        )

        logger.info(f"Found {len(products)} Sentinel-2 products")

        # Convert to list of dicts
        product_list = []
        for uuid, product in products.items():
            product_list.append({
                'uuid': uuid,
                'title': product['title'],
                'date': product['beginposition'].date(),
                'cloud_coverage': product['cloudcoverpercentage'],
                'size_mb': product['size'].split(' ')[0]
            })

        return sorted(product_list, key=lambda x: x['date'], reverse=True)

    def download_product(
        self,
        product_uuid: str,
        output_dir: Optional[Path] = None
    ) -> Path:
        """
        Download a Sentinel-2 product.

        Args:
            product_uuid: UUID of the product to download
            output_dir: Directory to save product (defaults to data/raw)

        Returns:
            Path to downloaded product
        """
        api = self._get_api()

        if output_dir is None:
            output_dir = self.data_dir / "raw"

        logger.info(f"Downloading product {product_uuid}")

        # Download product
        product_info = api.download(product_uuid, directory_path=str(output_dir))

        downloaded_path = Path(product_info['path'])
        logger.info(f"Downloaded to {downloaded_path}")

        return downloaded_path


def query_sentinel2_products(
    geometry: Dict,
    start_date: date,
    end_date: date,
    cloud_coverage_max: int = 30
) -> List[Dict]:
    """
    Convenience function to query Sentinel-2 products.

    Args:
        geometry: GeoJSON geometry defining area of interest
        start_date: Start date for search
        end_date: End date for search
        cloud_coverage_max: Maximum cloud coverage percentage

    Returns:
        List of product dictionaries
    """
    fetcher = SatelliteFetcher()
    return fetcher.query_products(geometry, start_date, end_date, cloud_coverage_max)
