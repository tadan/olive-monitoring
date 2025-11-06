"""Satellite image processing for vegetation index calculation."""
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple
from datetime import date
import zipfile

import numpy as np
import rasterio
from rasterio.mask import mask
from shapely.geometry import shape
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import FieldZone, SatelliteImage, HealthIndex
from app.vegetation_indices import (
    calculate_ndvi,
    calculate_ndmi,
    calculate_health_score,
    calculate_statistics
)

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Processes Sentinel-2 satellite imagery to extract vegetation indices."""

    # Sentinel-2 band mappings (10m and 20m resolution)
    BAND_MAPPING = {
        'red': 'B04',      # Red band (10m resolution)
        'nir': 'B08',      # Near-infrared (10m resolution)
        'swir': 'B11'      # Shortwave infrared (20m resolution)
    }

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize the image processor.

        Args:
            data_dir: Directory containing satellite data (defaults to /app/data)
        """
        self.data_dir = data_dir or Path("/app/data")
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"

        # Ensure directories exist
        self.processed_dir.mkdir(parents=True, exist_ok=True)

    def extract_product_path(self, product_zip: Path) -> Path:
        """
        Extract Sentinel-2 product zip if needed.

        Args:
            product_zip: Path to .zip file

        Returns:
            Path to extracted .SAFE directory
        """
        if product_zip.suffix == '.zip':
            # Extract to same directory
            extract_dir = product_zip.parent
            safe_dir_name = product_zip.stem + '.SAFE'
            safe_dir = extract_dir / safe_dir_name

            # Check if already extracted
            if safe_dir.exists():
                logger.info(f"Product already extracted: {safe_dir}")
                return safe_dir

            logger.info(f"Extracting {product_zip.name}")
            with zipfile.ZipFile(product_zip, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)

            return safe_dir
        elif product_zip.suffix == '.SAFE':
            return product_zip
        else:
            raise ValueError(f"Unknown product format: {product_zip.suffix}")

    def find_band_file(self, product_path: Path, band_name: str) -> Optional[Path]:
        """
        Find the band file within a Sentinel-2 product.

        Args:
            product_path: Path to .SAFE directory
            band_name: Band identifier (e.g., 'B04', 'B08')

        Returns:
            Path to band GeoTIFF file, or None if not found
        """
        # Sentinel-2 structure: .SAFE/GRANULE/*/IMG_DATA/R10m/*_B04_10m.jp2
        # Or for L2A: .SAFE/GRANULE/*/IMG_DATA/R10m/*_B04_10m.jp2

        # Try both possible resolutions
        for resolution in ['R10m', 'R20m', 'R60m']:
            img_data_dir = product_path / "GRANULE" / "*" / "IMG_DATA" / resolution

            # Use glob to find the band file
            pattern = f"*_{band_name}_*.jp2"
            matches = list(product_path.glob(f"GRANULE/*/IMG_DATA/{resolution}/{pattern}"))

            if matches:
                logger.debug(f"Found {band_name} at {matches[0]}")
                return matches[0]

        logger.warning(f"Band {band_name} not found in {product_path}")
        return None

    def extract_bands(
        self,
        product_path: Path,
        zone_geometry: Dict
    ) -> Optional[Dict[str, np.ndarray]]:
        """
        Extract and clip required bands for a zone.

        Args:
            product_path: Path to Sentinel-2 product (.SAFE or .zip)
            zone_geometry: GeoJSON geometry defining the zone boundary

        Returns:
            Dictionary with 'red', 'nir', 'swir' numpy arrays, or None if failed
        """
        try:
            # Extract if zipped
            if product_path.suffix == '.zip':
                product_path = self.extract_product_path(product_path)

            # Convert GeoJSON to shapely geometry
            geom = shape(zone_geometry)

            bands = {}
            for band_key, band_name in self.BAND_MAPPING.items():
                band_file = self.find_band_file(product_path, band_name)

                if band_file is None:
                    logger.error(f"Missing {band_key} band ({band_name})")
                    return None

                # Read and clip band to zone
                with rasterio.open(band_file) as src:
                    # Clip to zone geometry
                    out_image, out_transform = mask(src, [geom], crop=True, nodata=0)

                    # Extract first band (imagery is often single-band per file)
                    band_data = out_image[0]

                    # Convert nodata values to NaN
                    band_data = band_data.astype(np.float32)
                    band_data[band_data == 0] = np.nan

                    bands[band_key] = band_data

            logger.info(f"Extracted {len(bands)} bands for zone")
            return bands

        except Exception as e:
            logger.error(f"Failed to extract bands: {e}", exc_info=True)
            return None

    def calculate_indices_for_zone(
        self,
        bands: Dict[str, np.ndarray]
    ) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """
        Calculate NDVI and NDMI from extracted bands.

        Args:
            bands: Dictionary with 'red', 'nir', 'swir' arrays

        Returns:
            Tuple of (ndvi_array, ndmi_array), or None if failed
        """
        try:
            # Calculate NDVI
            ndvi = calculate_ndvi(bands['red'], bands['nir'])

            # Calculate NDMI
            ndmi = calculate_ndmi(bands['nir'], bands['swir'])

            logger.info(
                f"Calculated indices - NDVI: {np.nanmean(ndvi):.3f}, "
                f"NDMI: {np.nanmean(ndmi):.3f}"
            )

            return ndvi, ndmi

        except Exception as e:
            logger.error(f"Failed to calculate indices: {e}", exc_info=True)
            return None

    def process_zone(
        self,
        db: Session,
        image_id: int,
        zone_id: int,
        product_path: Path
    ) -> Optional[HealthIndex]:
        """
        Process a satellite image for a specific zone.

        Complete pipeline: extract bands → calculate indices → compute statistics → save to DB

        Args:
            db: Database session
            image_id: ID of satellite image record
            zone_id: ID of field zone
            product_path: Path to Sentinel-2 product

        Returns:
            HealthIndex record if successful, None otherwise
        """
        try:
            logger.info(f"Processing zone {zone_id} for image {image_id}")

            # Get zone geometry
            zone = db.query(FieldZone).filter(FieldZone.id == zone_id).first()
            if not zone:
                logger.error(f"Zone {zone_id} not found")
                return None

            # Get image metadata
            image = db.query(SatelliteImage).filter(SatelliteImage.id == image_id).first()
            if not image:
                logger.error(f"Image {image_id} not found")
                return None

            # Extract bands for this zone
            bands = self.extract_bands(product_path, zone.geometry)
            if bands is None:
                return None

            # Calculate vegetation indices
            indices = self.calculate_indices_for_zone(bands)
            if indices is None:
                return None

            ndvi, ndmi = indices

            # Calculate statistics
            ndvi_mean, ndvi_std, ndvi_min, ndvi_max = calculate_statistics(ndvi)
            ndmi_mean, ndmi_std, ndmi_min, ndmi_max = calculate_statistics(ndmi)

            # Calculate overall health score
            health_score = calculate_health_score(ndvi_mean, ndmi_mean)

            # Create health index record
            health_index = HealthIndex(
                zone_id=zone_id,
                image_id=image_id,
                acquisition_date=image.acquisition_date,
                ndvi_mean=ndvi_mean,
                ndvi_std=ndvi_std,
                ndvi_min=ndvi_min,
                ndvi_max=ndvi_max,
                ndmi_mean=ndmi_mean,
                ndmi_std=ndmi_std,
                ndmi_min=ndmi_min,
                ndmi_max=ndmi_max,
                vegetation_health_score=health_score
            )

            db.add(health_index)
            db.commit()
            db.refresh(health_index)

            logger.info(
                f"Zone {zone_id}: Health score {health_score}/100 "
                f"(NDVI: {ndvi_mean:.3f}, NDMI: {ndmi_mean:.3f})"
            )

            return health_index

        except Exception as e:
            logger.error(f"Failed to process zone {zone_id}: {e}", exc_info=True)
            db.rollback()
            return None

    def process_all_zones(
        self,
        db: Session,
        image_id: int,
        product_path: Path
    ) -> int:
        """
        Process all zones for a satellite image.

        Args:
            db: Database session
            image_id: ID of satellite image record
            product_path: Path to Sentinel-2 product

        Returns:
            Number of zones successfully processed
        """
        zones = db.query(FieldZone).all()
        success_count = 0

        for zone in zones:
            result = self.process_zone(db, image_id, zone.id, product_path)
            if result is not None:
                success_count += 1

        logger.info(f"Processed {success_count}/{len(zones)} zones")

        # Mark image as processed
        if success_count > 0:
            image = db.query(SatelliteImage).filter(SatelliteImage.id == image_id).first()
            if image:
                image.processed = True
                db.commit()

        return success_count


def process_satellite_image(
    image_id: int,
    product_path: Path,
    data_dir: Optional[Path] = None
) -> int:
    """
    Convenience function to process all zones for an image.

    Args:
        image_id: Database ID of satellite image
        product_path: Path to Sentinel-2 product
        data_dir: Optional data directory path

    Returns:
        Number of zones successfully processed
    """
    processor = ImageProcessor(data_dir)

    # Get database session
    db = next(get_db())
    try:
        return processor.process_all_zones(db, image_id, product_path)
    finally:
        db.close()
