"""Check actual Red and NIR band values from satellite data."""
import sys
from pathlib import Path
from datetime import date
import numpy as np

if Path("/app/app").exists():
    sys.path.insert(0, "/app")
else:
    sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.database import get_session_local
from app.models import SatelliteImage, FieldZone
from app.image_processor import ImageProcessor

SessionLocal = get_session_local()
db = SessionLocal()

try:
    # Get Jan 26 image
    image = db.query(SatelliteImage).filter(
        SatelliteImage.acquisition_date == date(2026, 1, 26),
        SatelliteImage.scene_id.like('%T33TVG%')
    ).first()

    # Get zone 2
    zone = db.query(FieldZone).filter(FieldZone.id == 2).first()

    if image and zone:
        processor = ImageProcessor()
        bands = processor.extract_bands(Path(image.download_path), zone.geometry)

        if bands:
            red = bands['red']
            nir = bands['nir']

            print("BAND VALUE RANGES:")
            print("=" * 60)
            print(f"Red band:")
            print(f"  Min: {np.nanmin(red):.6f}")
            print(f"  Max: {np.nanmax(red):.6f}")
            print(f"  Mean: {np.nanmean(red):.6f}")
            print()
            print(f"NIR band:")
            print(f"  Min: {np.nanmin(nir):.6f}")
            print(f"  Max: {np.nanmax(nir):.6f}")
            print(f"  Mean: {np.nanmean(nir):.6f}")
            print()

            # Calculate typical sum
            typical_sum = np.nanmean(red) + np.nanmean(nir)
            print(f"Typical (Red + NIR): {typical_sum:.6f}")
            print(f"Soil factor L: 0.16")
            print(f"L as percentage of (Red+NIR): {0.16/typical_sum*100:.2f}%")
            print()

            # Calculate NDVI and OSAVI with actual values
            from app.vegetation_indices import calculate_ndvi, calculate_osavi

            ndvi = calculate_ndvi(red, nir)
            osavi = calculate_osavi(red, nir)

            print("CALCULATED INDICES:")
            print(f"  NDVI mean: {np.nanmean(ndvi):.6f}")
            print(f"  OSAVI mean: {np.nanmean(osavi):.6f}")
            print(f"  Difference: {abs(np.nanmean(osavi) - np.nanmean(ndvi)):.6f}")
            print()

            # Show the denominator issue
            print("DENOMINATOR ANALYSIS:")
            print(f"  NDVI denominator (Red+NIR): {typical_sum:.6f}")
            print(f"  OSAVI denominator (Red+NIR+0.16): {typical_sum + 0.16:.6f}")
            print(f"  Percentage increase: {0.16/typical_sum*100:.2f}%")
            print()
            print("PROBLEM: If Red and NIR are large (e.g., in thousands),")
            print("         then L=0.16 is negligible and OSAVI ≈ NDVI")

finally:
    db.close()
