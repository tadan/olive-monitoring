"""Test script to verify correct tile selection using Point geometry."""
import sys
from pathlib import Path
from datetime import date, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.satellite_fetcher import SatelliteFetcher

# Farm center coordinates
FARM_LAT = 42.303
FARM_LON = 14.187

def test_polygon_query():
    """Test tile selection with polygon geometry (current approach)."""
    print("=" * 60)
    print("TEST 1: Polygon Geometry (Current Approach)")
    print("=" * 60)

    # Create a small polygon around the farm (current approach)
    # This mimics what the zone geometry would look like
    polygon_geometry = {
        "type": "Polygon",
        "coordinates": [[
            [FARM_LON - 0.005, FARM_LAT - 0.005],  # SW corner
            [FARM_LON + 0.005, FARM_LAT - 0.005],  # SE corner
            [FARM_LON + 0.005, FARM_LAT + 0.005],  # NE corner
            [FARM_LON - 0.005, FARM_LAT + 0.005],  # NW corner
            [FARM_LON - 0.005, FARM_LAT - 0.005],  # Close polygon
        ]]
    }

    fetcher = SatelliteFetcher()

    # Query last 10 days
    end_date = date.today()
    start_date = end_date - timedelta(days=10)

    print(f"Farm center: {FARM_LAT}°N, {FARM_LON}°E")
    print(f"Query period: {start_date} to {end_date}")
    print(f"Geometry type: Polygon (±0.005° buffer)")
    print()

    try:
        products = fetcher.query_products(
            geometry=polygon_geometry,
            start_date=start_date,
            end_date=end_date,
            cloud_coverage_max=30
        )

        if products:
            print(f"Found {len(products)} products")
            print("\nFirst 3 products:")
            for product in products[:3]:
                # Extract tile ID from product name
                # Format: S2A_MSIL2A_YYYYMMDDTHHMMSS_N9999_R123_T33TVG_...
                parts = product['name'].split('_')
                tile_id = next((p for p in parts if p.startswith('T')), 'UNKNOWN')

                print(f"  - Date: {product['date']}, Cloud: {product['cloud_coverage']:.1f}%, "
                      f"Tile: {tile_id}, Size: {product['size_mb']} MB")
        else:
            print("No products found")

    except Exception as e:
        print(f"ERROR: {e}")

    print()


def test_point_query():
    """Test tile selection with point geometry (proposed fix)."""
    print("=" * 60)
    print("TEST 2: Point Geometry (Proposed Fix)")
    print("=" * 60)

    # Use exact farm center point
    point_geometry = {
        "type": "Point",
        "coordinates": [FARM_LON, FARM_LAT]
    }

    fetcher = SatelliteFetcher()

    # Query last 10 days
    end_date = date.today()
    start_date = end_date - timedelta(days=10)

    print(f"Farm center: {FARM_LAT}°N, {FARM_LON}°E")
    print(f"Query period: {start_date} to {end_date}")
    print(f"Geometry type: Point (exact coordinates)")
    print()

    try:
        products = fetcher.query_products(
            geometry=point_geometry,
            start_date=start_date,
            end_date=end_date,
            cloud_coverage_max=30
        )

        if products:
            print(f"Found {len(products)} products")
            print("\nFirst 3 products:")
            for product in products[:3]:
                # Extract tile ID from product name
                parts = product['name'].split('_')
                tile_id = next((p for p in parts if p.startswith('T')), 'UNKNOWN')

                print(f"  - Date: {product['date']}, Cloud: {product['cloud_coverage']:.1f}%, "
                      f"Tile: {tile_id}, Size: {product['size_mb']} MB")
        else:
            print("No products found")

    except Exception as e:
        print(f"ERROR: {e}")

    print()


def main():
    """Run both tests and compare results."""
    print("\n" + "=" * 60)
    print("TILE SELECTION TEST")
    print("Testing Point vs Polygon geometry for correct tile selection")
    print("=" * 60)
    print()

    # Test 1: Current approach with polygon
    test_polygon_query()

    # Test 2: Proposed fix with point
    test_point_query()

    print("=" * 60)
    print("ANALYSIS")
    print("=" * 60)
    print("Compare the tile IDs from both approaches:")
    print("- If Polygon returns T33TVG: confirms the bug")
    print("- If Point returns different tile: confirms the fix")
    print("- The Point approach should return the correct tile for the farm")
    print()


if __name__ == "__main__":
    main()
