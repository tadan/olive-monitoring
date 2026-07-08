"""Satellite image processing for vegetation index calculation."""
import logging
import zipfile
from pathlib import Path
from typing import Dict, Optional, Tuple

import numpy as np
import rasterio
from rasterio.mask import mask
from shapely.geometry import shape
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import FieldZone, HealthIndex, SatelliteImage
from app.vegetation_indices import (
    calculate_arvi,
    calculate_health_score,
    calculate_ndmi,
    calculate_ndvi,
    calculate_osavi,
    calculate_statistics,
)

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Processes Sentinel-2 satellite imagery to extract vegetation indices."""

    # Sentinel-2 band mappings (10m and 20m resolution)
    BAND_MAPPING = {
        'blue': 'B02',     # Blue band (10m resolution) - for ARVI
        'red': 'B04',      # Red band (10m resolution)
        'nir': 'B08',      # Near-infrared (10m resolution)
        'swir': 'B11'      # Shortwave infrared (20m resolution)
    }

    # SCL classes to mask (clouds, shadows, cirrus)
    SCL_MASK_CLASSES = {3, 8, 9, 10}  # cloud shadow, cloud medium/high prob, thin cirrus

    # Skip observation if more than this fraction of pixels are cloudy
    MAX_CLOUD_FRACTION = 0.5

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
            # Use glob to find the band file
            pattern = f"*_{band_name}_*.jp2"
            matches = list(product_path.glob(f"GRANULE/*/IMG_DATA/{resolution}/{pattern}"))

            if matches:
                logger.debug(f"Found {band_name} at {matches[0]}")
                return matches[0]

        logger.warning(f"Band {band_name} not found in {product_path}")
        return None

    def extract_cloud_mask(
        self,
        product_path: Path,
        zone_geometry: Dict,
        reference_shape: Tuple,
        reference_transform,
        reference_crs
    ) -> Optional[np.ndarray]:
        """
        Extract the SCL (Scene Classification Layer) band and build a boolean cloud mask.

        SCL classes masked: 3 (cloud shadow), 8 (cloud medium), 9 (cloud high), 10 (thin cirrus)

        Args:
            product_path: Path to .SAFE directory
            zone_geometry: GeoJSON geometry
            reference_shape: Target shape (10m grid)
            reference_transform: Target affine transform
            reference_crs: Target CRS

        Returns:
            Boolean array (True = cloudy pixel to exclude), or None if SCL not found
        """
        scl_file = self.find_band_file(product_path, 'SCL')
        if scl_file is None:
            logger.warning("SCL band not found — skipping cloud masking")
            return None

        from rasterio.warp import Resampling, reproject, transform_geom

        with rasterio.open(scl_file) as src:
            geom_transformed = transform_geom('EPSG:4326', src.crs, zone_geometry)
            geom_in_raster_crs = shape(geom_transformed)

            out_image, out_transform = mask(src, [geom_in_raster_crs], crop=True, nodata=0)
            scl_20m = out_image[0].astype(np.float32)

            # Resample SCL from 20m to 10m using nearest-neighbor (classification data)
            scl_10m = np.zeros(reference_shape, dtype=np.float32)
            reproject(
                source=scl_20m,
                destination=scl_10m,
                src_transform=out_transform,
                src_crs=src.crs,
                dst_transform=reference_transform,
                dst_crs=reference_crs,
                resampling=Resampling.nearest
            )

        cloud_mask = np.isin(scl_10m.astype(np.uint8), list(self.SCL_MASK_CLASSES))

        total_pixels = cloud_mask.size
        cloudy_pixels = int(np.sum(cloud_mask))
        cloud_fraction = cloudy_pixels / total_pixels if total_pixels > 0 else 0

        logger.info(
            f"Cloud mask: {cloudy_pixels}/{total_pixels} pixels masked "
            f"({cloud_fraction:.1%} cloudy)"
        )

        return cloud_mask

    def extract_bands(
        self,
        product_path: Path,
        zone_geometry: Dict
    ) -> Optional[Dict[str, np.ndarray]]:
        """
        Extract and clip required bands for a zone, with SCL cloud masking.

        Handles different band resolutions by resampling all bands to 10m resolution:
        - Blue (B02): 10m native
        - Red (B04): 10m native
        - NIR (B08): 10m native
        - SWIR (B11): 20m native → resampled to 10m

        Cloud/shadow pixels identified by the SCL band are set to NaN.
        If >50% of zone pixels are cloudy, the observation is skipped.

        Args:
            product_path: Path to Sentinel-2 product (.SAFE or .zip)
            zone_geometry: GeoJSON geometry defining the zone boundary

        Returns:
            Dictionary with 'blue', 'red', 'nir', 'swir' numpy arrays (all same shape), or None if failed
        """
        try:
            # Extract if zipped
            if product_path.suffix == '.zip':
                product_path = self.extract_product_path(product_path)

            bands = {}
            reference_shape = None
            reference_transform = None
            reference_crs = None

            # First pass: extract Blue, Red and NIR (10m resolution)
            for band_key in ['blue', 'red', 'nir']:
                band_name = self.BAND_MAPPING[band_key]
                band_file = self.find_band_file(product_path, band_name)

                if band_file is None:
                    logger.error(f"Missing {band_key} band ({band_name})")
                    return None

                # Read and clip band to zone
                with rasterio.open(band_file) as src:
                    # Transform zone geometry from lat/lon (EPSG:4326) to raster CRS
                    from rasterio.warp import transform_geom
                    geom_transformed = transform_geom(
                        'EPSG:4326',  # Source: lat/lon
                        src.crs,      # Target: raster's CRS (usually UTM)
                        zone_geometry
                    )
                    geom_in_raster_crs = shape(geom_transformed)

                    # Clip to zone geometry
                    out_image, out_transform = mask(src, [geom_in_raster_crs], crop=True, nodata=0)

                    # Extract first band (imagery is often single-band per file)
                    band_data = out_image[0]

                    # Convert nodata values to NaN
                    band_data = band_data.astype(np.float32)
                    band_data[band_data == 0] = np.nan

                    bands[band_key] = band_data

                    # Use first band (Blue) as reference for resampling
                    if reference_shape is None:
                        reference_shape = band_data.shape
                        reference_transform = out_transform
                        reference_crs = src.crs
                        logger.debug(f"Reference shape from {band_key}: {reference_shape}")

            # Second pass: extract and resample SWIR (20m → 10m)
            band_key = 'swir'
            band_name = self.BAND_MAPPING[band_key]
            band_file = self.find_band_file(product_path, band_name)

            if band_file is None:
                logger.error(f"Missing {band_key} band ({band_name})")
                return None

            with rasterio.open(band_file) as src:
                # Transform zone geometry
                from rasterio.warp import Resampling, reproject, transform_geom
                geom_transformed = transform_geom(
                    'EPSG:4326',
                    src.crs,
                    zone_geometry
                )
                geom_in_raster_crs = shape(geom_transformed)

                # Clip to zone geometry (at 20m resolution)
                out_image, out_transform = mask(src, [geom_in_raster_crs], crop=True, nodata=0)
                band_data_20m = out_image[0].astype(np.float32)

                # Resample from 20m to 10m to match Red/NIR
                band_data_10m = np.zeros(reference_shape, dtype=np.float32)

                reproject(
                    source=band_data_20m,
                    destination=band_data_10m,
                    src_transform=out_transform,
                    src_crs=src.crs,
                    dst_transform=reference_transform,
                    dst_crs=reference_crs,
                    resampling=Resampling.bilinear
                )

                # Convert nodata values to NaN
                band_data_10m[band_data_10m == 0] = np.nan

                bands[band_key] = band_data_10m
                logger.debug(f"Resampled {band_key} from {band_data_20m.shape} to {band_data_10m.shape}")

            # Apply SCL cloud mask to all bands
            cloud_mask = self.extract_cloud_mask(
                product_path, zone_geometry,
                reference_shape, reference_transform, reference_crs
            )

            if cloud_mask is not None:
                cloud_fraction = np.sum(cloud_mask) / cloud_mask.size
                if cloud_fraction > self.MAX_CLOUD_FRACTION:
                    logger.warning(
                        f"Zone too cloudy ({cloud_fraction:.1%} > {self.MAX_CLOUD_FRACTION:.0%}) "
                        f"— skipping observation"
                    )
                    return None

                for band_key in bands:
                    bands[band_key][cloud_mask] = np.nan

            logger.info(f"Extracted {len(bands)} bands for zone (all {reference_shape})")
            return bands

        except Exception as e:
            logger.error(f"Failed to extract bands: {e}", exc_info=True)
            return None

    def calculate_indices_for_zone(
        self,
        bands: Dict[str, np.ndarray]
    ) -> Optional[Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]:
        """
        Calculate all vegetation indices from extracted bands.

        Args:
            bands: Dictionary with 'blue', 'red', 'nir', 'swir' arrays

        Returns:
            Tuple of (ndvi_array, ndmi_array, arvi_array, osavi_array), or None if failed
        """
        try:
            # Calculate NDVI (general vegetation index)
            ndvi = calculate_ndvi(bands['red'], bands['nir'])

            # Calculate NDMI (moisture index)
            ndmi = calculate_ndmi(bands['nir'], bands['swir'])

            # Calculate ARVI (atmospherically resistant)
            arvi = calculate_arvi(bands['red'], bands['nir'], bands['blue'])

            # Calculate OSAVI (soil-adjusted)
            osavi = calculate_osavi(bands['red'], bands['nir'])

            logger.info(
                f"Calculated indices - NDVI: {np.nanmean(ndvi):.3f}, "
                f"NDMI: {np.nanmean(ndmi):.3f}, "
                f"ARVI: {np.nanmean(arvi):.3f}, "
                f"OSAVI: {np.nanmean(osavi):.3f}"
            )

            return ndvi, ndmi, arvi, osavi

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

            ndvi, ndmi, arvi, osavi = indices

            # Calculate statistics for all indices
            ndvi_mean, ndvi_std, ndvi_min, ndvi_max = calculate_statistics(ndvi)
            ndmi_mean, ndmi_std, ndmi_min, ndmi_max = calculate_statistics(ndmi)
            arvi_mean, arvi_std, arvi_min, arvi_max = calculate_statistics(arvi)
            osavi_mean, osavi_std, osavi_min, osavi_max = calculate_statistics(osavi)

            # Calculate overall health score (uses multi-index composite)
            health_score = calculate_health_score(ndvi_mean, ndmi_mean, arvi_mean, osavi_mean)

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
                arvi_mean=arvi_mean,
                arvi_std=arvi_std,
                arvi_min=arvi_min,
                arvi_max=arvi_max,
                osavi_mean=osavi_mean,
                osavi_std=osavi_std,
                osavi_min=osavi_min,
                osavi_max=osavi_max,
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
