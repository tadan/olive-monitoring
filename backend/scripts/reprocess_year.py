"""Reprocess all satellite data for a specific year."""
import sys
from pathlib import Path
from datetime import date

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
from sqlalchemy import extract

def reprocess_year(year):
    """Reprocess all satellite data for a specific year.

    Args:
        year: Year to reprocess (e.g., 2026)
    """
    SessionLocal = get_session_local()
    db = SessionLocal()

    try:
        print(f"Looking for satellite images from {year}...")
        print()

        # Find all images for this year
        images = db.query(SatelliteImage).filter(
            extract('year', SatelliteImage.acquisition_date) == year
        ).order_by(SatelliteImage.acquisition_date).all()

        if not images:
            print(f"No images found for {year}")
            return

        print(f"Found {len(images)} image(s) from {year}")
        print()

        total_zones_processed = 0
        total_zones_deleted = 0

        for i, image in enumerate(images, 1):
            print(f"[{i}/{len(images)}] {image.acquisition_date} - {image.scene_id[:30]}...")
            print(f"  Cloud coverage: {image.cloud_coverage_percent}%")

            # Check if product file exists
            product_path = Path(image.download_path)
            if not product_path.exists():
                print(f"  ⚠️  Product file not found, skipping")
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
            total_zones_processed += success_count
            print(f"  ✅ Successfully processed {success_count} zone(s)")
            print()

        print("=" * 70)
        print("REPROCESSING COMPLETE")
        print("=" * 70)
        print(f"Total images processed: {len(images)}")
        print(f"Total old records deleted: {total_zones_deleted}")
        print(f"Total zones reprocessed: {total_zones_processed}")
        print()

        # Show sample of updated values
        print("Sample of updated values (latest 5 records):")
        print("-" * 70)

        recent_records = db.query(HealthIndex).filter(
            extract('year', HealthIndex.acquisition_date) == year
        ).order_by(
            HealthIndex.acquisition_date.desc(),
            HealthIndex.zone_id
        ).limit(5).all()

        for record in recent_records:
            print(f"{record.acquisition_date} - Zone {record.zone_id}:")
            print(f"  NDVI: {float(record.ndvi_mean):.4f} | "
                  f"ARVI: {float(record.arvi_mean):.4f} | "
                  f"OSAVI: {float(record.osavi_mean):.4f} | "
                  f"Health: {record.vegetation_health_score}/100")
            print(f"  OSAVI < NDVI? {'✓' if record.osavi_mean < record.ndvi_mean else '✗'}")

    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python reprocess_year.py YYYY")
        print("Example: python reprocess_year.py 2026")
        sys.exit(1)

    try:
        year = int(sys.argv[1])
        reprocess_year(year)
    except ValueError:
        print("Error: Year must be a number")
        sys.exit(1)
