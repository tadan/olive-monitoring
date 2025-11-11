#!/usr/bin/env python3
"""Find the oldest available Sentinel-2 image for the farm location."""
import sys
from pathlib import Path
from datetime import date

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.satellite_fetcher import SatelliteFetcher

# Farm center
FARM_POINT = {
    'type': 'Point',
    'coordinates': [14.1868, 42.3014]
}

def find_oldest_images():
    """Find oldest available images for each year from 2015."""
    fetcher = SatelliteFetcher()

    # Check each year from Sentinel-2A launch
    years = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]

    all_products = []

    for year in years:
        print(f"\nChecking {year}...")

        try:
            products = fetcher.query_products(
                geometry=FARM_POINT,
                start_date=date(year, 1, 1),
                end_date=date(year, 12, 31),
                cloud_coverage_max=50  # Lenient for historical
            )

            if products:
                # Sort by date ascending to get oldest first
                products_sorted = sorted(products, key=lambda x: x['date'])
                oldest_in_year = products_sorted[0]

                print(f"  ✓ Found {len(products)} products")
                print(f"  Oldest: {oldest_in_year['date']} (cloud: {oldest_in_year['cloud_coverage']:.1f}%)")

                all_products.extend(products)
            else:
                print(f"  ✗ No products found")

        except Exception as e:
            print(f"  ✗ Error: {e}")

    if all_products:
        # Find absolute oldest
        all_sorted = sorted(all_products, key=lambda x: x['date'])
        oldest = all_sorted[0]
        newest = all_sorted[-1]

        print("\n" + "="*60)
        print("SUMMARY")
        print("="*60)
        print(f"Total products found: {len(all_products)}")
        print(f"\nOldest image:")
        print(f"  Date: {oldest['date']}")
        print(f"  Name: {oldest['name']}")
        print(f"  Cloud coverage: {oldest['cloud_coverage']:.1f}%")
        print(f"  Size: {oldest['size_mb']} MB")
        print(f"\nNewest image:")
        print(f"  Date: {newest['date']}")
        print(f"\nTime span: {(newest['date'] - oldest['date']).days} days (~{(newest['date'] - oldest['date']).days / 365:.1f} years)")
        print("="*60)

        # Count by cloud coverage
        clear = sum(1 for p in all_products if p['cloud_coverage'] < 10)
        partly_cloudy = sum(1 for p in all_products if 10 <= p['cloud_coverage'] < 30)
        cloudy = sum(1 for p in all_products if p['cloud_coverage'] >= 30)

        print(f"\nCloud coverage distribution:")
        print(f"  Clear (< 10%): {clear} ({clear/len(all_products)*100:.1f}%)")
        print(f"  Partly cloudy (10-30%): {partly_cloudy} ({partly_cloudy/len(all_products)*100:.1f}%)")
        print(f"  Cloudy (> 30%): {cloudy} ({cloudy/len(all_products)*100:.1f}%)")

        return oldest
    else:
        print("\n✗ No historical data found")
        return None

if __name__ == "__main__":
    print("="*60)
    print("SENTINEL-2 HISTORICAL DATA SEARCH")
    print("Farm location: 42.3014°N, 14.1868°E (Abruzzo, Italy)")
    print("="*60)

    oldest = find_oldest_images()

    if oldest:
        print(f"\nTo process this oldest image:")
        print(f"  docker-compose exec processor python scripts/process_satellite_data.py --days-back {(date.today() - oldest['date']).days}")
