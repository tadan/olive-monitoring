"""Reprocess all satellite data from a specific date onwards."""
import sys
from pathlib import Path
from datetime import datetime

# Add app directory to path
script_dir = Path(__file__).parent
project_root = script_dir.parent

if Path("/app/app").exists():
    sys.path.insert(0, "/app")
else:
    sys.path.insert(0, str(project_root / "backend"))

from app.database import get_session_local
from app.models import SatelliteImage, HealthIndex
from app.image_processor import ImageProcessor

def reprocess_from_date(start_date_str):
    """Reprocess all satellite data from a specific date onwards.

    Args:
        start_date_str: Start date in format YYYY-MM-DD
    """
    SessionLocal = get_session_local()
    db = SessionLocal()

    try:
        # Parse date
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()

        print(f"Reprocessing all satellite data from {start_date} onwards...")
        print()

        # Find all images from this date onwards
        images = db.query(SatelliteImage).filter(
            SatelliteImage.acquisition_date >= start_date
        ).order_by(SatelliteImage.acquisition_date).all()

        if not images:
            print(f"No images found from {start_date} onwards")
            return

        print(f"Found {len(images)} image(s) to reprocess")
        print(f"Date range: {images[0].acquisition_date} to {images[-1].acquisition_date}")
        print()

        # Ask for confirmation
        response = input(f"This will delete and reprocess {len(images)} images. Continue? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Aborted")
            return

        print()
        print("Starting reprocessing...")
        print("=" * 70)
        print()

        total_zones_processed = 0
        total_zones_deleted = 0
        failed_images = []

        for i, image in enumerate(images, 1):
            print(f"[{i}/{len(images)}] {image.acquisition_date} - {image.scene_id[:40]}...")
            print(f"  Cloud coverage: {image.cloud_coverage_percent}%")

            # Check if product file exists
            product_path = Path(image.download_path)
            if not product_path.exists():
                print(f"  ⚠️  Product file not found, skipping")
                failed_images.append((image.acquisition_date, "File not found"))
                print()
                continue

            # Delete existing health indices for this image
            deleted = db.query(HealthIndex).filter(
                HealthIndex.image_id == image.id
            ).delete()
            db.commit()
            total_zones_deleted += deleted
            print(f"  🗑️  Deleted {deleted} old health record(s)")

            # Reprocess all zones
            processor = ImageProcessor()
            success_count = processor.process_all_zones(db, image.id, product_path)

            if success_count == 0:
                failed_images.append((image.acquisition_date, "No zones processed"))
                print(f"  ⚠️  Warning: No zones successfully processed")
            else:
                total_zones_processed += success_count
                print(f"  ✅ Successfully processed {success_count} zone(s)")

            print()

        print("=" * 70)
        print("REPROCESSING COMPLETE")
        print("=" * 70)
        print(f"Total images processed: {len(images)}")
        print(f"Total old records deleted: {total_zones_deleted}")
        print(f"Total zones reprocessed: {total_zones_processed}")

        if failed_images:
            print(f"\nWarnings/Failures: {len(failed_images)}")
            for date, reason in failed_images[:5]:  # Show first 5
                print(f"  - {date}: {reason}")
            if len(failed_images) > 5:
                print(f"  ... and {len(failed_images) - 5} more")

        print()

        # Show sample of updated values
        print("Sample of updated values (latest 10 records):")
        print("-" * 70)

        recent_records = db.query(HealthIndex).filter(
            HealthIndex.acquisition_date >= start_date
        ).order_by(
            HealthIndex.acquisition_date.desc(),
            HealthIndex.zone_id
        ).limit(10).all()

        for record in recent_records:
            arvi_str = f"{float(record.arvi_mean):.4f}" if record.arvi_mean else "null"
            osavi_str = f"{float(record.osavi_mean):.4f}" if record.osavi_mean else "null"

            print(f"{record.acquisition_date} - Zone {record.zone_id}:")
            print(f"  NDVI: {float(record.ndvi_mean):.4f} | "
                  f"ARVI: {arvi_str} | "
                  f"OSAVI: {osavi_str} | "
                  f"Health: {record.vegetation_health_score}/100")

            if record.osavi_mean and record.ndvi_mean:
                print(f"  OSAVI < NDVI? {'✓' if record.osavi_mean < record.ndvi_mean else '✗'}")

    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python reprocess_from_date.py YYYY-MM-DD")
        print("Example: python reprocess_from_date.py 2019-09-01")
        print()
        print("This will reprocess ALL satellite data from the specified date onwards.")
        sys.exit(1)

    reprocess_from_date(sys.argv[1])
