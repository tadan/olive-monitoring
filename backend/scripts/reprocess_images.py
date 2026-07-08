#!/usr/bin/env python3
"""
Reprocess existing satellite images that have incomplete or failed processing.

This script finds all images with processed=false and reprocesses them,
calculating health indices for all zones.
"""
import sys
import logging
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_db
from app.models import SatelliteImage, FieldZone
from app.image_processor import ImageProcessor
from app.alerts import AlertDetector
from app.baseline import BaselineManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/app/data/reprocessing.log')
    ]
)
logger = logging.getLogger(__name__)


def reprocess_unprocessed_images():
    """
    Find and reprocess all satellite images with processed=false.

    Returns:
        Dictionary with processing statistics
    """
    start_time = datetime.now()
    logger.info("=" * 80)
    logger.info(f"Starting reprocessing - {start_time}")
    logger.info("=" * 80)

    stats = {
        'start_time': start_time,
        'images_found': 0,
        'images_processed': 0,
        'zones_processed': 0,
        'alerts_generated': 0,
        'baselines_updated': 0,
        'errors': []
    }

    db = next(get_db())
    processor = ImageProcessor()
    all_alerts = []

    try:
        # Find all unprocessed images
        unprocessed_images = (
            db.query(SatelliteImage)
            .filter(SatelliteImage.processed == False)
            .order_by(SatelliteImage.acquisition_date)
            .all()
        )

        stats['images_found'] = len(unprocessed_images)
        logger.info(f"Found {len(unprocessed_images)} unprocessed images")

        if not unprocessed_images:
            logger.info("No unprocessed images found")
            return stats

        # Get total zone count for progress tracking
        total_zones = db.query(FieldZone).count()

        # Process each image
        for idx, image in enumerate(unprocessed_images, 1):
            try:
                logger.info(f"\n[{idx}/{len(unprocessed_images)}] Processing image {image.id}")
                logger.info(f"  Scene: {image.scene_id}")
                logger.info(f"  Date: {image.acquisition_date}")
                logger.info(f"  Path: {image.download_path}")

                product_path = Path(image.download_path)

                # Check if file exists
                if not product_path.exists():
                    error_msg = f"Product file not found: {product_path}"
                    logger.error(error_msg)
                    stats['errors'].append(error_msg)
                    continue

                # Process all zones for this image
                zones_processed = processor.process_all_zones(
                    db=db,
                    image_id=image.id,
                    product_path=product_path
                )

                stats['zones_processed'] += zones_processed

                if zones_processed > 0:
                    stats['images_processed'] += 1
                    logger.info(f"  Successfully processed {zones_processed}/{total_zones} zones")

                    # Detect alerts for this image
                    detector = AlertDetector(db)
                    from app.models import HealthIndex

                    health_indices = (
                        db.query(HealthIndex)
                        .filter(HealthIndex.image_id == image.id)
                        .all()
                    )

                    for health_index in health_indices:
                        alerts = detector.check_all_alerts(
                            zone_id=health_index.zone_id,
                            health_index=health_index
                        )
                        all_alerts.extend(alerts)

                    if alerts:
                        stats['alerts_generated'] += len(alerts)
                        logger.info(f"  Generated {len(alerts)} alerts")
                else:
                    logger.warning(f"  No zones successfully processed")

            except Exception as e:
                error_msg = f"Error processing image {image.id} ({image.scene_id}): {e}"
                logger.error(error_msg, exc_info=True)
                stats['errors'].append(error_msg)

        # Update baselines if we processed any data
        if stats['images_processed'] > 0:
            logger.info("\nUpdating baseline statistics...")
            manager = BaselineManager(db)
            zones = db.query(FieldZone).all()

            for zone in zones:
                count = manager.update_all_baselines(zone.id)
                stats['baselines_updated'] += count

            logger.info(f"Updated {stats['baselines_updated']} baselines")

    except Exception as e:
        error_msg = f"Critical error in reprocessing: {e}"
        logger.error(error_msg, exc_info=True)
        stats['errors'].append(error_msg)

    finally:
        db.close()

    # Log summary
    end_time = datetime.now()
    duration = end_time - start_time

    logger.info("\n" + "=" * 80)
    logger.info("Reprocessing Summary:")
    logger.info(f"  Duration: {duration}")
    logger.info(f"  Images found: {stats['images_found']}")
    logger.info(f"  Images processed: {stats['images_processed']}")
    logger.info(f"  Zones processed: {stats['zones_processed']}")
    logger.info(f"  Alerts generated: {stats['alerts_generated']}")
    logger.info(f"  Baselines updated: {stats['baselines_updated']}")
    if stats['errors']:
        logger.info(f"  Errors: {len(stats['errors'])}")
        for error in stats['errors']:
            logger.info(f"    - {error}")
    logger.info("=" * 80)

    stats['end_time'] = end_time
    stats['duration'] = duration

    return stats


if __name__ == '__main__':
    reprocess_unprocessed_images()
