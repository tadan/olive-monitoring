"""Reprocess satellite data for a specific date."""
import sys
from pathlib import Path
from datetime import datetime

# Add app directory to path (works both locally and in Docker)
script_dir = Path(__file__).parent
project_root = script_dir.parent

# Check if we're in Docker (app directory at /app)
if Path("/app/app").exists():
    sys.path.insert(0, "/app")
else:
    # Running locally
    sys.path.insert(0, str(project_root / "backend"))

from app.database import get_session_local
from app.models import SatelliteImage, HealthIndex
from app.image_processor import ImageProcessor

def reprocess_date(date_str):
    """Reprocess satellite data for a specific date.

    Args:
        date_str: Date in format YYYY-MM-DD
    """
    SessionLocal = get_session_local()
    db = SessionLocal()

    try:
        # Parse date
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()

        print(f"Looking for satellite images from {date_str}...")

        # Find images for this date
        images = db.query(SatelliteImage).filter(
            SatelliteImage.acquisition_date == date_obj
        ).all()

        if not images:
            print(f"No images found for {date_str}")
            return

        print(f"Found {len(images)} image(s)")
        print()

        for image in images:
            print(f"Image: {image.scene_id}")
            print(f"  Acquisition: {image.acquisition_date}")
            print(f"  Cloud coverage: {image.cloud_coverage_percent}%")

            # Check if product file exists
            product_path = Path(image.download_path)
            if not product_path.exists():
                print(f"  ⚠️  Product file not found: {product_path}")
                continue

            # Delete existing health indices for this image
            deleted = db.query(HealthIndex).filter(
                HealthIndex.image_id == image.id
            ).delete()
            db.commit()
            print(f"  🗑️  Deleted {deleted} old health record(s)")

            # Reprocess all zones
            processor = ImageProcessor()
            print(f"  🔄 Reprocessing zones...")

            success_count = processor.process_all_zones(db, image.id, product_path)
            print(f"  ✅ Successfully processed {success_count} zone(s)")
            print()

        # Show updated values
        print("=" * 70)
        print("UPDATED DATABASE VALUES:")
        print("=" * 70)

        records = db.query(HealthIndex).filter(
            HealthIndex.acquisition_date == date_obj
        ).order_by(HealthIndex.zone_id).all()

        for record in records:
            print(f"Zone {record.zone_id}:")
            print(f"  NDVI:  {float(record.ndvi_mean):.6f}")
            print(f"  ARVI:  {float(record.arvi_mean):.6f}")
            print(f"  OSAVI: {float(record.osavi_mean):.6f}")
            print(f"  Health Score: {record.vegetation_health_score}/100")
            print(f"  OSAVI < NDVI? {record.osavi_mean < record.ndvi_mean}")
            print()

    finally:
        db.close()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python reprocess_date.py YYYY-MM-DD")
        print("Example: python reprocess_date.py 2026-01-26")
        sys.exit(1)

    reprocess_date(sys.argv[1])
