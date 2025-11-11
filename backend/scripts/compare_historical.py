#!/usr/bin/env python3
"""Compare olive grove health between July 2015 and July 2025."""
import sys
from pathlib import Path
from datetime import date

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_db
from app.models import FieldZone, SatelliteImage, HealthIndex

def get_health_data_for_month(db, year: int, month: int):
    """Get health indices for a specific month."""
    from sqlalchemy import extract

    health_data = (
        db.query(HealthIndex, FieldZone.name)
        .join(FieldZone, HealthIndex.zone_id == FieldZone.id)
        .filter(extract('year', HealthIndex.acquisition_date) == year)
        .filter(extract('month', HealthIndex.acquisition_date) == month)
        .order_by(HealthIndex.zone_id, HealthIndex.acquisition_date)
        .all()
    )

    return health_data

def process_month(year: int, month: int):
    """Process satellite data for a specific month only."""
    print(f"\n{'='*60}")
    print(f"PROCESSING: {year}-{month:02d}")
    print(f"{'='*60}")

    from datetime import timedelta

    # Query only this specific month
    start_date = date(year, month, 1)
    # Last day of month
    if month == 12:
        end_date = date(year, 12, 31)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)

    print(f"Date range: {start_date} to {end_date}")

    # Get all zones
    db = next(get_db())
    zones = db.query(FieldZone).all()

    if not zones:
        print("❌ No zones found")
        return None

    # Use Point geometry (zone centroid) like main processor
    from shapely.geometry import shape
    zone_shape = shape(zones[0].geometry)
    centroid = zone_shape.centroid

    query_geometry = {
        "type": "Point",
        "coordinates": [centroid.x, centroid.y]
    }

    # Query products for this month only
    from app.satellite_fetcher import SatelliteFetcher
    from app.image_processor import ImageProcessor

    fetcher = SatelliteFetcher()

    print(f"Querying products...")
    products = fetcher.query_products(
        geometry=query_geometry,
        start_date=start_date,
        end_date=end_date,
        cloud_coverage_max=20  # Strict for best quality
    )

    print(f"Found {len(products)} products for {year}-{month:02d}")

    if not products:
        print("⚠️  No products found for this month")
        return None

    # Filter out already processed
    from app.models import SatelliteImage
    existing_scenes = set(
        row[0] for row in db.query(SatelliteImage.scene_id).all()
    )
    new_products = [p for p in products if p['name'] not in existing_scenes]

    print(f"New products to download: {len(new_products)}")

    if not new_products:
        print("✅ All products already processed")
        db.close()
        return {'products_downloaded': 0, 'zones_processed': 0}

    # Download and process each product
    processor = ImageProcessor()
    stats = {
        'products_downloaded': 0,
        'zones_processed': 0
    }

    for i, product in enumerate(new_products, 1):
        print(f"\n[{i}/{len(new_products)}] {product['name']}")
        print(f"  Date: {product['date']}, Cloud: {product['cloud_coverage']:.1f}%")

        try:
            # Download with retry
            max_retries = 3
            download_path = None

            for attempt in range(max_retries):
                try:
                    print(f"  Downloading (attempt {attempt + 1}/{max_retries})...")
                    download_path = fetcher.download_product(
                        product_id=product['id'],
                        output_dir=Path('/app/data/raw')
                    )
                    break
                except Exception as e:
                    if attempt < max_retries - 1:
                        print(f"  ⚠️  Download failed: {e}")
                        print(f"  Retrying in 10 seconds...")
                        import time
                        time.sleep(10)
                    else:
                        print(f"  ❌ Download failed after {max_retries} attempts")
                        raise

            if not download_path:
                continue

            stats['products_downloaded'] += 1

            # Register in database
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

            # Process all zones
            zones_processed = processor.process_all_zones(
                db=db,
                image_id=satellite_image.id,
                product_path=download_path
            )

            stats['zones_processed'] += zones_processed
            print(f"  ✅ Processed {zones_processed}/3 zones")

        except Exception as e:
            print(f"  ❌ Error: {e}")
            continue

    db.close()

    print(f"\n{'='*60}")
    print(f"COMPLETED: {year}-{month:02d}")
    print(f"  Products downloaded: {stats['products_downloaded']}")
    print(f"  Zones processed: {stats['zones_processed']}")
    print(f"{'='*60}")

    return stats

def display_comparison():
    """Display comparison between July 2015 and July 2025."""
    db = next(get_db())

    print("\n" + "="*80)
    print("OLIVE GROVE HEALTH COMPARISON: JULY 2015 vs JULY 2025")
    print("="*80)

    # Get data for both periods
    july_2015 = get_health_data_for_month(db, 2015, 7)
    july_2025 = get_health_data_for_month(db, 2025, 7)

    if not july_2015:
        print("\n⚠️  No data for July 2015 - needs processing")
        return False

    if not july_2025:
        print("\n⚠️  No data for July 2025 - needs processing")
        return False

    # Group by zone
    zones_2015 = {}
    zones_2025 = {}

    for health, zone_name in july_2015:
        if zone_name not in zones_2015:
            zones_2015[zone_name] = []
        zones_2015[zone_name].append(health)

    for health, zone_name in july_2025:
        if zone_name not in zones_2025:
            zones_2025[zone_name] = []
        zones_2025[zone_name].append(health)

    # Compare each zone
    print("\nZONE-BY-ZONE COMPARISON:\n")

    for zone_name in zones_2015.keys():
        print(f"{'='*60}")
        print(f"ZONE: {zone_name}")
        print(f"{'='*60}")

        if zone_name not in zones_2025:
            print("  ⚠️  No 2025 data for this zone")
            continue

        # Average metrics for each period
        ndvi_2015 = sum(h.ndvi_mean for h in zones_2015[zone_name]) / len(zones_2015[zone_name])
        ndmi_2015 = sum(h.ndmi_mean for h in zones_2015[zone_name]) / len(zones_2015[zone_name])
        health_2015 = sum(h.vegetation_health_score for h in zones_2015[zone_name]) / len(zones_2015[zone_name])

        ndvi_2025 = sum(h.ndvi_mean for h in zones_2025[zone_name]) / len(zones_2025[zone_name])
        ndmi_2025 = sum(h.ndmi_mean for h in zones_2025[zone_name]) / len(zones_2025[zone_name])
        health_2025 = sum(h.vegetation_health_score for h in zones_2025[zone_name]) / len(zones_2025[zone_name])

        # Calculate changes
        ndvi_change = ndvi_2025 - ndvi_2015
        ndmi_change = ndmi_2025 - ndmi_2015
        health_change = health_2025 - health_2015

        print(f"\nJULY 2015:")
        print(f"  NDVI:   {ndvi_2015:.3f}")
        print(f"  NDMI:   {ndmi_2015:.3f}")
        print(f"  Health: {health_2015:.0f}/100")
        print(f"  Images: {len(zones_2015[zone_name])}")

        print(f"\nJULY 2025:")
        print(f"  NDVI:   {ndvi_2025:.3f}")
        print(f"  NDMI:   {ndmi_2025:.3f}")
        print(f"  Health: {health_2025:.0f}/100")
        print(f"  Images: {len(zones_2025[zone_name])}")

        print(f"\n10-YEAR CHANGE:")
        print(f"  NDVI:   {ndvi_change:+.3f} ({ndvi_change/ndvi_2015*100:+.1f}%)")
        print(f"  NDMI:   {ndmi_change:+.3f} ({ndmi_change/ndmi_2015*100:+.1f}%)")
        print(f"  Health: {health_change:+.0f} ({health_change/health_2015*100:+.1f}%)")

        # Interpretation
        print(f"\nINTERPRETATION:")
        if health_change > 10:
            print(f"  ✅ Significant improvement in grove health")
        elif health_change > 0:
            print(f"  ↗️  Slight improvement in grove health")
        elif health_change > -10:
            print(f"  ↘️  Slight decline in grove health")
        else:
            print(f"  ⚠️  Significant decline in grove health")

        if ndvi_change > 0.1:
            print(f"  🌿 More vigorous vegetation")
        elif ndvi_change < -0.1:
            print(f"  🍂 Less vigorous vegetation")

        if ndmi_change > 0.1:
            print(f"  💧 Higher moisture content")
        elif ndmi_change < -0.1:
            print(f"  🌵 Lower moisture content")

        print()

    db.close()
    return True

def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Compare olive grove health between July 2015 and July 2025'
    )
    parser.add_argument(
        '--process',
        action='store_true',
        help='Process both months before comparison'
    )
    parser.add_argument(
        '--2015-only',
        action='store_true',
        dest='only_2015',
        help='Only process July 2015'
    )
    parser.add_argument(
        '--2025-only',
        action='store_true',
        dest='only_2025',
        help='Only process July 2025'
    )

    args = parser.parse_args()

    if args.process or args.only_2015:
        print("\n🛰️  Processing July 2015...")
        process_month(2015, 7)

    if args.process or args.only_2025:
        print("\n🛰️  Processing July 2025...")
        process_month(2025, 7)

    # Display comparison
    print("\n" + "="*80)
    print("GENERATING COMPARISON REPORT")
    print("="*80)

    success = display_comparison()

    if not success:
        print("\n❌ Comparison incomplete. Run with --process to process missing data.")
        print("\nUsage:")
        print("  --process      Process both months and show comparison")
        print("  --2015-only    Process only July 2015")
        print("  --2025-only    Process only July 2025")
        sys.exit(1)

    print("\n✅ Comparison complete!")

if __name__ == "__main__":
    main()
