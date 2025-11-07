"""Copernicus Sentinel-2 satellite data fetching using the new Data Space API."""
from typing import Dict, List, Optional
from datetime import date, datetime, timedelta
from pathlib import Path
import logging
import requests
from requests.auth import HTTPBasicAuth
import json

from shapely.geometry import shape
from app.config import settings

logger = logging.getLogger(__name__)


class SatelliteFetcher:
    """Fetches Sentinel-2 satellite imagery from Copernicus Data Space."""

    # New Copernicus Data Space API endpoints
    AUTH_URL = "https://identity.dataspace.copernicus.eu/auth/realms/CDSE/protocol/openid-connect/token"
    ODATA_URL = "https://catalogue.dataspace.copernicus.eu/odata/v1"
    DOWNLOAD_URL = "https://zipper.dataspace.copernicus.eu/odata/v1"

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
        self.access_token = None
        self.token_expires_at = None

        # Create data directories
        self.data_dir.mkdir(parents=True, exist_ok=True)
        (self.data_dir / "raw").mkdir(exist_ok=True)
        (self.data_dir / "processed").mkdir(exist_ok=True)

    def _get_access_token(self) -> str:
        """
        Get OAuth2 access token for Copernicus Data Space API.

        Returns:
            Access token string
        """
        # Check if we have a valid token
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                return self.access_token

        # Request new token
        data = {
            "grant_type": "password",
            "username": self.username,
            "password": self.password,
            "client_id": "cdse-public"
        }

        try:
            response = requests.post(self.AUTH_URL, data=data, timeout=30)
            response.raise_for_status()

            token_data = response.json()
            self.access_token = token_data["access_token"]

            # Set expiration time (subtract 60 seconds for safety margin)
            expires_in = token_data.get("expires_in", 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 60)

            logger.info("Successfully obtained access token")
            return self.access_token

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to get access token: {e}")
            raise

    def query_products(
        self,
        geometry: Dict,
        start_date: date,
        end_date: date,
        cloud_coverage_max: int = 30
    ) -> List[Dict]:
        """
        Query available Sentinel-2 products using OData API.

        Args:
            geometry: GeoJSON geometry defining area of interest
            start_date: Start date for search
            end_date: End date for search
            cloud_coverage_max: Maximum cloud coverage percentage

        Returns:
            List of product dictionaries with metadata
        """
        # Convert geometry to WKT
        geom = shape(geometry)
        wkt = geom.wkt

        # Format dates for OData query
        start_str = start_date.strftime("%Y-%m-%dT00:00:00.000Z")
        end_str = end_date.strftime("%Y-%m-%dT23:59:59.999Z")

        # Build OData filter
        # Collection: SENTINEL-2 (S2MSI2A is L2A processing level, S2MSI1C is L1C)
        # Only get L2A products (atmospherically corrected, has proper band structure)
        filter_parts = [
            "Collection/Name eq 'SENTINEL-2'",
            f"OData.CSC.Intersects(area=geography'SRID=4326;{wkt}')",
            f"ContentDate/Start gt {start_str}",
            f"ContentDate/Start lt {end_str}",
            f"Attributes/OData.CSC.DoubleAttribute/any(att:att/Name eq 'cloudCover' and att/OData.CSC.DoubleAttribute/Value lt {cloud_coverage_max})",
            "Attributes/OData.CSC.StringAttribute/any(att:att/Name eq 'productType' and att/OData.CSC.StringAttribute/Value eq 'S2MSI2A')"
        ]

        filter_query = " and ".join(filter_parts)

        # OData query parameters
        params = {
            "$filter": filter_query,
            "$orderby": "ContentDate/Start desc",
            "$top": 100,  # Maximum results
            "$expand": "Attributes"
        }

        try:
            # Get access token
            token = self._get_access_token()

            # Query products
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(
                f"{self.ODATA_URL}/Products",
                params=params,
                headers=headers,
                timeout=60
            )
            response.raise_for_status()

            data = response.json()
            products_data = data.get("value", [])

            logger.info(f"Found {len(products_data)} Sentinel-2 products")

            # Parse products
            products = []
            for product in products_data:
                # Extract attributes
                attributes = {
                    attr["Name"]: attr.get("Value")
                    for attr in product.get("Attributes", [])
                }

                # Parse content date
                content_date_str = product.get("ContentDate", {}).get("Start", "")
                content_date = datetime.fromisoformat(content_date_str.replace("Z", "+00:00"))

                products.append({
                    "id": product["Id"],
                    "name": product["Name"],
                    "title": product["Name"],  # For compatibility
                    "date": content_date.date(),
                    "cloud_coverage": float(attributes.get("cloudCover", 0)),
                    "size_mb": round(product.get("ContentLength", 0) / (1024 * 1024), 2),
                    "product_type": attributes.get("productType", ""),
                    "processing_level": attributes.get("processingLevel", "")
                })

            return sorted(products, key=lambda x: x["date"], reverse=True)

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to query products: {e}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response status: {e.response.status_code}")
                logger.error(f"Response body: {e.response.text[:500]}")
            raise

    def download_product(
        self,
        product_id: str,
        output_dir: Optional[Path] = None
    ) -> Path:
        """
        Download a Sentinel-2 product.

        Args:
            product_id: Product ID from query results
            output_dir: Directory to save product (defaults to data/raw)

        Returns:
            Path to downloaded product
        """
        if output_dir is None:
            output_dir = self.data_dir / "raw"

        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Get access token
            token = self._get_access_token()

            # Download URL for the product
            download_url = f"{self.DOWNLOAD_URL}/Products({product_id})/$value"

            logger.info(f"Downloading product {product_id}")

            # Stream download
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(download_url, headers=headers, stream=True, timeout=300)
            response.raise_for_status()

            # Get filename from Content-Disposition header or use product_id
            filename = f"{product_id}.zip"
            if "Content-Disposition" in response.headers:
                content_disp = response.headers["Content-Disposition"]
                if "filename=" in content_disp:
                    filename = content_disp.split("filename=")[1].strip('"')

            output_path = output_dir / filename

            # Download with progress
            total_size = int(response.headers.get("content-length", 0))
            downloaded = 0

            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            if downloaded % (10 * 1024 * 1024) < 8192:  # Log every 10MB
                                logger.info(f"Download progress: {progress:.1f}%")

            logger.info(f"Downloaded to {output_path} ({downloaded / (1024*1024):.1f} MB)")
            return output_path

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to download product {product_id}: {e}")
            raise


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
