#!/usr/bin/env python3
"""
Historical analysis of Olive Grove health (2015-2025).
Target: Mid-September data for every year.
"""
import sys
from datetime import date
from pathlib import Path

from sqlalchemy import extract

# Add parent directory to path to ensure imports work
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_db
from app.image_processor import ImageProcessor
from app.models import FieldZone, HealthIndex, SatelliteImage
from app.satellite_fetcher import SatelliteFetcher

# Configuration
TARGET_MONTH = 9  # September
START_YEAR = 2015
END_YEAR = 2025
TARGET_DAY_START = 10  # Look for images starting Sept 10th
TARGET_DAY_END = 25    # Look for images until Sept 25th (Mid-September window)

def get_best_image_for_period(db, zone_id, year, month=TARGET_MONTH, day_start=TARGET_DAY_START, day_end=TARGET_DAY_END):
    """Find the best health record for the specific time window.

    Args:
        db: Database session
        zone_id: ID of the field zone
        year: Year to query
        month: Target month (default: September)
        day_start: Start day of target window (default: 10)
        day_end: End day of target window (default: 25)

    Returns:
        HealthIndex record or None
    """

    # Try to find data within the specific mid-month window first
    health_record = (
        db.query(HealthIndex)
        .filter(HealthIndex.zone_id == zone_id)
        .filter(extract('year', HealthIndex.acquisition_date) == year)
        .filter(extract('month', HealthIndex.acquisition_date) == month)
        .filter(extract('day', HealthIndex.acquisition_date) >= day_start)
        .filter(extract('day', HealthIndex.acquisition_date) <= day_end)
        .order_by(HealthIndex.vegetation_health_score.desc()) # Get the healthiest day (least clouds/shadows)
        .first()
    )

    # Fallback: If no mid-month data, try the whole month
    if not health_record:
        health_record = (
            db.query(HealthIndex)
            .filter(HealthIndex.zone_id == zone_id)
            .filter(extract('year', HealthIndex.acquisition_date) == year)
            .filter(extract('month', HealthIndex.acquisition_date) == month)
            .order_by(HealthIndex.vegetation_health_score.desc())
            .first()
        )

    return health_record

def ensure_data_exists(year):
    """Check if data exists for this month/year, if not, download it."""
    print(f"\n🔍 Checking data for September {year}...")
    
    db = next(get_db())
    
    # Check if we already have ANY images for this month in the DB
    existing_images = (
        db.query(SatelliteImage)
        .filter(extract('year', SatelliteImage.acquisition_date) == year)
        .filter(extract('month', SatelliteImage.acquisition_date) == TARGET_MONTH)
        .count()
    )

    if existing_images > 0:
        print(f"   ✅ Data already exists for Sept {year} ({existing_images} images).")
        db.close()
        return

    print(f"   ⚠️ Data missing for Sept {year}. Initiating download...")
    
    # Define date range (Whole month to ensure we catch a clear day)
    start_date = date(year, TARGET_MONTH, 1)
    end_date = date(year, TARGET_MONTH, 30)

    # Get Zone Geometry (using the first zone found)
    zones = db.query(FieldZone).all()
    if not zones:
        print("   ❌ No zones found in database.")
        return

    from shapely.geometry import shape
    zone_shape = shape(zones[0].geometry)
    centroid = zone_shape.centroid
    query_geometry = {"type": "Point", "coordinates": [centroid.x, centroid.y]}

    # Fetch
    fetcher = SatelliteFetcher()
    products = fetcher.query_products(
        geometry=query_geometry,
        start_date=start_date,
        end_date=end_date,
        cloud_coverage_max=20 # Strict cloud cover for historical analysis
    )
    
    # Filter out products we already have (double check)
    existing_scenes = set(row[0] for row in db.query(SatelliteImage.scene_id).all())
    new_products = [p for p in products if p['name'] not in existing_scenes]

    if not new_products:
        print(f"   ❌ No suitable satellite images found for Sept {year}.")
        db.close()
        return

    # Pick the best one (lowest cloud coverage) to save space/time
    best_product = sorted(new_products, key=lambda x: x['cloud_coverage'])[0]
    print(f"   ⬇️ Downloading best candidate: {best_product['date']} (Cloud: {best_product['cloud_coverage']}%)")

    try:
        # Download
        download_path = fetcher.download_product(best_product['id'], Path('/app/data/raw'))
        if not download_path:
            return

        # Register
        image = SatelliteImage(
            acquisition_date=best_product['date'],
            satellite='Sentinel-2',
            cloud_coverage_percent=best_product['cloud_coverage'],
            scene_id=best_product['name'],
            download_path=str(download_path),
            processed=False
        )
        db.add(image)
        db.commit()
        db.refresh(image)

        # Process
        processor = ImageProcessor()
        processor.process_all_zones(db, image.id, download_path)
        print(f"   ✅ Successfully processed Sept {year}")

    except Exception as e:
        print(f"   ❌ Error processing {year}: {e}")
    finally:
        db.close()

def print_historical_report():
    """Generate the ASCII comparison table."""
    db = next(get_db())
    zones = db.query(FieldZone).all()

    print("\n" + "="*100)
    print(f"🌿 OLIVE GROVE HEALTH REPORT: SEPTEMBERS ({START_YEAR}-{END_YEAR})")
    print("="*100)

    for zone in zones:
        print(f"\n📍 ZONE: {zone.name.upper()}")
        print("-" * 100)
        print(f"{'YEAR':<8} | {'DATE':<12} | {'HEALTH':<10} | {'NDVI':<10} | {'NDMI':<10} | {'STATUS'}")
        print("-" * 100)

        history_data = []

        # Collect data
        for year in range(START_YEAR, END_YEAR + 1):
            record = get_best_image_for_period(db, zone.id, year)
            if record:
                history_data.append({
                    'year': year,
                    'date': record.acquisition_date,
                    'health': record.vegetation_health_score,
                    'ndvi': record.ndvi_mean,
                    'ndmi': record.ndmi_mean
                })
            else:
                history_data.append({'year': year, 'date': None})

        # Print Data with Trend Indicators
        prev_health = None
        
        for row in history_data:
            if row['date'] is None:
                print(f"{row['year']:<8} | {'NO DATA':<12} | {'-':<10} | {'-':<10} | {'-':<10} | ⚪ No Imagery")
                continue

            # Trend Calculation
            trend_icon = "➡️ "
            if prev_health is not None:
                diff = row['health'] - prev_health
                if diff > 5:
                    trend_icon = "↗️ 🟢 Improving"
                elif diff < -5:
                    trend_icon = "↘️ 🔴 Declining"
                else:
                    trend_icon = "➡️ 🟡 Stable"
            else:
                trend_icon = "⏺️ Baseline"

            prev_health = row['health']

            print(
                f"{row['year']:<8} | "
                f"{row['date'].strftime('%Y-%m-%d'):<12} | "
                f"{row['health']:>3.0f}/100     | "
                f"{row['ndvi']:>.3f}      | "
                f"{row['ndmi']:>.3f}      | "
                f"{trend_icon}"
            )
    
    db.close()
    print("\n" + "="*100)

def main():
    print("🚀 Starting Historical Analysis...")
    
    # 1. Ensure we have data for all years
    for year in range(START_YEAR, END_YEAR + 1):
        ensure_data_exists(year)
    
    # 2. Display the comparison
    print_historical_report()

if __name__ == "__main__":
    main()