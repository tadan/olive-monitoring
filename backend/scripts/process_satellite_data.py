#!/usr/bin/env python3
"""
Main satellite data processing script.

This script orchestrates the complete pipeline:
1. Query new Sentinel-2 products from Copernicus
2. Download products
3. Process each zone (extract bands, calculate indices)
4. Detect health anomalies and generate alerts
5. Update baseline statistics
6. Send email notifications

Can be run manually or scheduled (e.g., every 5 days).
"""
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Optional

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_db
from app.models import SatelliteImage, FieldZone
from app.satellite_fetcher import SatelliteFetcher
from app.image_processor import ImageProcessor
from app.alerts import AlertDetector, AlertNotifier
from app.baseline import BaselineManager
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/app/data/processing.log')
    ]
)
logger = logging.getLogger(__name__)


class SatelliteDataProcessor:
    """Orchestrates the complete satellite data processing pipeline."""

    def __init__(
        self,
        days_back: int = 7,
        cloud_coverage_max: int = 30,
        send_notifications: bool = True
    ):
        """
        Initialize the processor.

        Args:
            days_back: How many days back to search for new imagery
            cloud_coverage_max: Maximum acceptable cloud coverage percentage
            send_notifications: Whether to send email notifications for alerts
        """
        self.days_back = days_back
        self.cloud_coverage_max = cloud_coverage_max
        self.send_notifications = send_notifications

        self.data_dir = Path(settings.data_dir)
        self.fetcher = SatelliteFetcher()
        self.processor = ImageProcessor()

    def query_new_products(self, db) -> List[dict]:
        """
        Query Sentinel-2 products for all zones.

        Args:
            db: Database session

        Returns:
            List of product dictionaries
        """
        logger.info("Querying new Sentinel-2 products...")

        # Get all zones
        zones = db.query(FieldZone).all()
        if not zones:
            logger.error("No zones found in database")
            return []

        # Use first zone's geometry as representative (they're all nearby)
        # For better coverage, could use union of all zones
        zone = zones[0]

        # FIX: Use Point geometry (zone centroid) instead of Polygon
        # This ensures we only get tiles that contain the farm location,
        # not adjacent tiles that merely intersect the search polygon
        from shapely.geometry import shape
        zone_shape = shape(zone.geometry)
        centroid = zone_shape.centroid

        # Create Point geometry for query
        query_geometry = {
            "type": "Point",
            "coordinates": [centroid.x, centroid.y]
        }

        logger.info(f"Query location: {centroid.y:.4f}°N, {centroid.x:.4f}°E")

        # Calculate date range
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=self.days_back)

        logger.info(
            f"Searching for products from {start_date} to {end_date} "
            f"(cloud coverage < {self.cloud_coverage_max}%)"
        )

        # Query products using Point geometry
        products = self.fetcher.query_products(
            geometry=query_geometry,
            start_date=start_date,
            end_date=end_date,
            cloud_coverage_max=self.cloud_coverage_max
        )

        logger.info(f"Found {len(products)} products")
        return products

    def filter_new_products(self, db, products: List[dict]) -> List[dict]:
        """
        Filter out products that have already been processed.

        Args:
            db: Database session
            products: List of product dictionaries

        Returns:
            List of products not yet in database
        """
        # Get list of scene IDs already in database
        existing_scenes = set(
            row[0] for row in db.query(SatelliteImage.scene_id).all()
        )

        # Filter to only new products
        new_products = [
            p for p in products
            if p['name'] not in existing_scenes
        ]

        logger.info(
            f"Found {len(new_products)} new products "
            f"({len(products) - len(new_products)} already processed)"
        )

        return new_products

    def download_product(self, product: dict) -> Optional[Path]:
        """
        Download a Sentinel-2 product.

        Args:
            product: Product dictionary from query

        Returns:
            Path to downloaded product, or None if failed
        """
        try:
            logger.info(f"Downloading {product['name']}")

            product_path = self.fetcher.download_product(
                product_id=product['id'],
                output_dir=self.data_dir / "raw"
            )

            logger.info(f"Downloaded to {product_path}")
            return product_path

        except Exception as e:
            logger.error(f"Failed to download {product['name']}: {e}", exc_info=True)
            return None

    def register_product(self, db, product: dict, download_path: Path) -> SatelliteImage:
        """
        Register a downloaded product in the database.

        Args:
            db: Database session
            product: Product dictionary
            download_path: Path to downloaded file

        Returns:
            SatelliteImage database record
        """
        satellite_image = SatelliteImage(
            acquisition_date=product['date'],
            satellite='Sentinel-2',
            cloud_coverage_percent=product['cloud_coverage'],
            scene_id=product['name'],
            download_path=str(download_path),
            processed=False
        )

        db.add(satellite_image)
        db.commit()
        db.refresh(satellite_image)

        logger.info(f"Registered image {satellite_image.id}: {product['name']}")
        return satellite_image

    def process_image(self, db, image: SatelliteImage) -> int:
        """
        Process all zones for an image.

        Args:
            db: Database session
            image: SatelliteImage record

        Returns:
            Number of zones successfully processed
        """
        logger.info(f"Processing image {image.id} ({image.scene_id})")

        product_path = Path(image.download_path)
        if not product_path.exists():
            logger.error(f"Product file not found: {product_path}")
            return 0

        # Process all zones
        success_count = self.processor.process_all_zones(
            db=db,
            image_id=image.id,
            product_path=product_path
        )

        return success_count

    def detect_alerts_for_image(self, db, image: SatelliteImage) -> List:
        """
        Detect alerts for all zones in an image.

        Args:
            db: Database session
            image: SatelliteImage record

        Returns:
            List of all detected alerts
        """
        from app.models import HealthIndex

        detector = AlertDetector(db)
        all_alerts = []

        # Get all health indices for this image
        health_indices = (
            db.query(HealthIndex)
            .filter(HealthIndex.image_id == image.id)
            .all()
        )

        logger.info(f"Checking alerts for {len(health_indices)} zones")

        for health_index in health_indices:
            alerts = detector.check_all_alerts(
                zone_id=health_index.zone_id,
                health_index=health_index
            )
            all_alerts.extend(alerts)

        logger.info(f"Detected {len(all_alerts)} alerts")
        return all_alerts

    def update_baselines(self, db) -> int:
        """
        Update baseline statistics for all zones.

        Args:
            db: Database session

        Returns:
            Number of baselines updated
        """
        logger.info("Updating baseline statistics...")

        manager = BaselineManager(db)
        zones = db.query(FieldZone).all()

        total_count = 0
        for zone in zones:
            count = manager.update_all_baselines(zone.id)
            total_count += count

        logger.info(f"Updated {total_count} baselines")
        return total_count

    async def send_notifications(self, alerts: List) -> int:
        """
        Send email notifications for alerts.

        Args:
            alerts: List of Alert objects

        Returns:
            Number of emails sent
        """
        if not self.send_notifications or not alerts:
            return 0

        logger.info(f"Sending notifications for {len(alerts)} alerts")

        notifier = AlertNotifier()
        db = next(get_db())
        try:
            count = await notifier.notify_alerts(alerts, db)
            return count
        finally:
            db.close()

    def run(self) -> dict:
        """
        Run the complete processing pipeline.

        Returns:
            Dictionary with processing statistics
        """
        start_time = datetime.now()
        logger.info("=" * 80)
        logger.info(f"Starting satellite data processing - {start_time}")
        logger.info("=" * 80)

        stats = {
            'start_time': start_time,
            'products_found': 0,
            'products_new': 0,
            'products_downloaded': 0,
            'images_processed': 0,
            'zones_processed': 0,
            'alerts_generated': 0,
            'baselines_updated': 0,
            'notifications_sent': 0,
            'errors': []
        }

        db = next(get_db())
        all_alerts = []

        try:
            # Step 1: Query new products
            products = self.query_new_products(db)
            stats['products_found'] = len(products)

            if not products:
                logger.info("No products found in date range")
                return stats

            # Step 2: Filter to new products
            new_products = self.filter_new_products(db, products)
            stats['products_new'] = len(new_products)

            if not new_products:
                logger.info("No new products to process")
                return stats

            # Step 3: Download and process each product
            for product in new_products:
                try:
                    # Download
                    download_path = self.download_product(product)
                    if download_path is None:
                        stats['errors'].append(f"Failed to download: {product['name']}")
                        continue

                    stats['products_downloaded'] += 1

                    # Register in database
                    image = self.register_product(db, product, download_path)

                    # Process all zones
                    zones_processed = self.process_image(db, image)
                    stats['zones_processed'] += zones_processed

                    if zones_processed > 0:
                        stats['images_processed'] += 1

                        # Detect alerts
                        alerts = self.detect_alerts_for_image(db, image)
                        stats['alerts_generated'] += len(alerts)
                        all_alerts.extend(alerts)

                except Exception as e:
                    error_msg = f"Error processing {product['name']}: {e}"
                    logger.error(error_msg, exc_info=True)
                    stats['errors'].append(error_msg)

            # Step 4: Update baselines (if we processed new data)
            if stats['images_processed'] > 0:
                baselines_updated = self.update_baselines(db)
                stats['baselines_updated'] = baselines_updated

            # Step 5: Send notifications
            if all_alerts and self.send_notifications:
                import asyncio
                notifications_sent = asyncio.run(self.send_notifications(all_alerts))
                stats['notifications_sent'] = notifications_sent

        except Exception as e:
            error_msg = f"Critical error in processing pipeline: {e}"
            logger.error(error_msg, exc_info=True)
            stats['errors'].append(error_msg)

        finally:
            db.close()

        # Log summary
        end_time = datetime.now()
        duration = end_time - start_time

        logger.info("=" * 80)
        logger.info("Processing Summary:")
        logger.info(f"  Duration: {duration}")
        logger.info(f"  Products found: {stats['products_found']}")
        logger.info(f"  Products new: {stats['products_new']}")
        logger.info(f"  Products downloaded: {stats['products_downloaded']}")
        logger.info(f"  Images processed: {stats['images_processed']}")
        logger.info(f"  Zones processed: {stats['zones_processed']}")
        logger.info(f"  Alerts generated: {stats['alerts_generated']}")
        logger.info(f"  Baselines updated: {stats['baselines_updated']}")
        logger.info(f"  Notifications sent: {stats['notifications_sent']}")
        if stats['errors']:
            logger.info(f"  Errors: {len(stats['errors'])}")
            for error in stats['errors']:
                logger.info(f"    - {error}")
        logger.info("=" * 80)

        stats['end_time'] = end_time
        stats['duration'] = duration

        return stats


def main():
    """Main entry point for the processing script."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Process Sentinel-2 satellite data for olive grove monitoring'
    )
    parser.add_argument(
        '--days-back',
        type=int,
        default=7,
        help='Number of days back to search for imagery (default: 7)'
    )
    parser.add_argument(
        '--cloud-coverage-max',
        type=int,
        default=30,
        help='Maximum cloud coverage percentage (default: 30)'
    )
    parser.add_argument(
        '--no-notifications',
        action='store_true',
        help='Disable email notifications'
    )

    args = parser.parse_args()

    # Run processor
    processor = SatelliteDataProcessor(
        days_back=args.days_back,
        cloud_coverage_max=args.cloud_coverage_max,
        send_notifications=not args.no_notifications
    )

    stats = processor.run()

    # Exit with error code if there were errors
    if stats['errors']:
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
