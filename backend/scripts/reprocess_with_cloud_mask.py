#!/usr/bin/env python3
"""
Reprocess all satellite images with SCL cloud masking.

Recalculates health indices for all stored images using the new cloud mask.
Replaces existing health_indices rows for each (image_id, zone_id) pair.

Usage:
    # Dry run — show cloud stats without writing to DB
    python scripts/reprocess_with_cloud_mask.py --dry-run

    # Full reprocess
    python scripts/reprocess_with_cloud_mask.py

    # Reprocess only a specific zone
    python scripts/reprocess_with_cloud_mask.py --zone-id 5

    # Reprocess only images from a date range
    python scripts/reprocess_with_cloud_mask.py --start-date 2025-06-01 --end-date 2025-12-31
"""
import sys
import argparse
import logging
from pathlib import Path
from datetime import datetime, date

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_db
from app.models import SatelliteImage, FieldZone, HealthIndex
from app.image_processor import ImageProcessor
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/app/data/cloud_mask_reprocess.log')
    ]
)
logger = logging.getLogger(__name__)


def reprocess_all(dry_run: bool = False, zone_id: int = None,
                  start_date: date = None, end_date: date = None):
    start_time = datetime.now()
    logger.info("=" * 80)
    logger.info(f"{'DRY RUN — ' if dry_run else ''}Cloud mask reprocessing — {start_time}")
    logger.info("=" * 80)

    stats = {
        'images_total': 0,
        'zones_processed': 0,
        'zones_skipped_cloudy': 0,
        'zones_skipped_missing': 0,
        'zones_updated': 0,
        'errors': []
    }

    db = next(get_db())
    processor = ImageProcessor()

    try:
        query = db.query(SatelliteImage).order_by(SatelliteImage.acquisition_date)
        if start_date:
            query = query.filter(SatelliteImage.acquisition_date >= start_date)
        if end_date:
            query = query.filter(SatelliteImage.acquisition_date <= end_date)

        images = query.all()
        stats['images_total'] = len(images)

        zones = db.query(FieldZone).all()
        if zone_id:
            zones = [z for z in zones if z.id == zone_id]

        logger.info(f"Reprocessing {len(images)} images × {len(zones)} zones")

        for idx, image in enumerate(images, 1):
            logger.info(f"\n[{idx}/{len(images)}] {image.scene_id} ({image.acquisition_date})")

            product_path = Path(image.download_path)
            if not product_path.exists():
                logger.warning(f"  File missing: {product_path}")
                stats['zones_skipped_missing'] += len(zones)
                continue

            for zone in zones:
                try:
                    bands = processor.extract_bands(product_path, zone.geometry)

                    if bands is None:
                        stats['zones_skipped_cloudy'] += 1
                        continue

                    indices = processor.calculate_indices_for_zone(bands)
                    if indices is None:
                        stats['errors'].append(f"Index calc failed: image {image.id}, zone {zone.id}")
                        continue

                    stats['zones_processed'] += 1

                    import numpy as np
                    from app.vegetation_indices import calculate_statistics, calculate_health_score
                    ndvi, ndmi, arvi, osavi = indices
                    ndvi_mean, ndvi_std, ndvi_min, ndvi_max = calculate_statistics(ndvi)
                    ndmi_mean, ndmi_std, ndmi_min, ndmi_max = calculate_statistics(ndmi)
                    arvi_mean, arvi_std, arvi_min, arvi_max = calculate_statistics(arvi)
                    osavi_mean, osavi_std, osavi_min, osavi_max = calculate_statistics(osavi)
                    health = calculate_health_score(ndvi_mean, ndmi_mean, arvi_mean, osavi_mean)

                    logger.info(
                        f"  Zone {zone.id} ({zone.name}): "
                        f"Health={health}, NDVI={ndvi_mean:.3f}, NDMI={ndmi_mean:.3f}"
                    )

                    if dry_run:
                        continue

                    # Delete existing record for this image+zone and write new one
                    db.query(HealthIndex).filter(
                        HealthIndex.image_id == image.id,
                        HealthIndex.zone_id == zone.id
                    ).delete()

                    health_index = HealthIndex(
                        zone_id=zone.id,
                        image_id=image.id,
                        acquisition_date=image.acquisition_date,
                        ndvi_mean=ndvi_mean, ndvi_std=ndvi_std,
                        ndvi_min=ndvi_min, ndvi_max=ndvi_max,
                        ndmi_mean=ndmi_mean, ndmi_std=ndmi_std,
                        ndmi_min=ndmi_min, ndmi_max=ndmi_max,
                        arvi_mean=arvi_mean, arvi_std=arvi_std,
                        arvi_min=arvi_min, arvi_max=arvi_max,
                        osavi_mean=osavi_mean, osavi_std=osavi_std,
                        osavi_min=osavi_min, osavi_max=osavi_max,
                        vegetation_health_score=health
                    )
                    db.add(health_index)
                    db.commit()
                    stats['zones_updated'] += 1

                except Exception as e:
                    error_msg = f"Error image {image.id}, zone {zone.id}: {e}"
                    logger.error(error_msg, exc_info=True)
                    stats['errors'].append(error_msg)
                    db.rollback()

    finally:
        db.close()

    duration = datetime.now() - start_time
    logger.info("\n" + "=" * 80)
    logger.info("Summary:")
    logger.info(f"  Duration: {duration}")
    logger.info(f"  Images scanned: {stats['images_total']}")
    logger.info(f"  Zones processed (clear): {stats['zones_processed']}")
    logger.info(f"  Zones skipped (too cloudy): {stats['zones_skipped_cloudy']}")
    logger.info(f"  Zones skipped (file missing): {stats['zones_skipped_missing']}")
    if not dry_run:
        logger.info(f"  Zones updated in DB: {stats['zones_updated']}")
    if stats['errors']:
        logger.info(f"  Errors: {len(stats['errors'])}")
        for err in stats['errors'][:10]:
            logger.info(f"    - {err}")
    logger.info("=" * 80)

    return stats


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Reprocess all images with SCL cloud masking')
    parser.add_argument('--dry-run', action='store_true',
                        help='Show cloud stats without modifying the database')
    parser.add_argument('--zone-id', type=int, help='Only reprocess a specific zone')
    parser.add_argument('--start-date', type=str, help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', type=str, help='End date (YYYY-MM-DD)')

    args = parser.parse_args()

    start = date.fromisoformat(args.start_date) if args.start_date else None
    end = date.fromisoformat(args.end_date) if args.end_date else None

    reprocess_all(
        dry_run=args.dry_run,
        zone_id=args.zone_id,
        start_date=start,
        end_date=end
    )
