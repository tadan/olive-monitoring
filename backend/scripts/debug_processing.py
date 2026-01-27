"""Debug script to trace OSAVI calculation through the entire processing pipeline."""
import sys
from pathlib import Path
from datetime import date
import numpy as np

# Add app directory to path
script_dir = Path(__file__).parent
project_root = script_dir.parent

if Path("/app/app").exists():
    sys.path.insert(0, "/app")
else:
    sys.path.insert(0, str(project_root / "backend"))

from app.database import get_session_local
from app.models import SatelliteImage, FieldZone, HealthIndex
from app.vegetation_indices import calculate_ndvi, calculate_osavi, calculate_statistics

# Monkey-patch the calculate_osavi function to add debug output
original_calculate_osavi = calculate_osavi

def debug_calculate_osavi(red, nir, soil_factor=0.16):
    result = original_calculate_osavi(red, nir, soil_factor)
    ndvi_result = calculate_ndvi(red, nir)

    print(f"    [DEBUG calculate_osavi] Red shape: {red.shape}, NIR shape: {nir.shape}")
    print(f"    [DEBUG calculate_osavi] NDVI mean: {np.nanmean(ndvi_result):.6f}")
    print(f"    [DEBUG calculate_osavi] OSAVI mean: {np.nanmean(result):.6f}")
    print(f"    [DEBUG calculate_osavi] Are they equal? {np.nanmean(result) == np.nanmean(ndvi_result)}")

    return result

# Replace the function
import app.vegetation_indices
import app.image_processor
app.vegetation_indices.calculate_osavi = debug_calculate_osavi
app.image_processor.calculate_osavi = debug_calculate_osavi

SessionLocal = get_session_local()
db = SessionLocal()

try:
    # Get Jan 26 image for Italian farm
    image = db.query(SatelliteImage).filter(
        SatelliteImage.acquisition_date == date(2026, 1, 26),
        SatelliteImage.scene_id.like('%T33TVG%')  # Italian farm tile
    ).first()

    if not image:
        print("No image found")
        sys.exit(1)

    print(f"Processing image: {image.scene_id}")
    print(f"Acquisition date: {image.acquisition_date}")
    print()

    # Get zone 2 (Below Natural)
    zone = db.query(FieldZone).filter(FieldZone.id == 2).first()

    if not zone:
        print("Zone 2 not found")
        sys.exit(1)

    print(f"Processing zone: {zone.name} (ID: {zone.id})")
    print()

    # Delete existing record
    deleted = db.query(HealthIndex).filter(
        HealthIndex.zone_id == zone.id,
        HealthIndex.image_id == image.id
    ).delete()
    db.commit()
    print(f"Deleted {deleted} existing record(s)")
    print()

    # Process with debug output
    from app.image_processor import ImageProcessor
    processor = ImageProcessor()

    print("Calling process_zone()...")
    print()

    result = processor.process_zone(db, image.id, zone.id, Path(image.download_path))

    if result:
        print()
        print("=" * 70)
        print("RESULT SAVED TO DATABASE:")
        print("=" * 70)
        print(f"NDVI mean:  {float(result.ndvi_mean):.6f}")
        print(f"ARVI mean:  {float(result.arvi_mean):.6f}")
        print(f"OSAVI mean: {float(result.osavi_mean):.6f}")
        print(f"Health score: {result.vegetation_health_score}/100")
        print()
        print(f"OSAVI < NDVI? {result.osavi_mean < result.ndvi_mean}")
        print(f"OSAVI == NDVI? {result.osavi_mean == result.ndvi_mean}")
    else:
        print("Processing failed!")

finally:
    db.close()
