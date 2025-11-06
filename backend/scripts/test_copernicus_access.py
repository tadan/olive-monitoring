#!/usr/bin/env python3
"""
Test script to verify Copernicus Data Space credentials and satellite data access.

This script verifies:
1. Copernicus credentials are configured correctly
2. Can connect to Copernicus Data Space API
3. Can query Sentinel-2 products for farm location
4. Products are available for the olive grove zones
"""
import sys
import logging
from pathlib import Path
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import get_db
from app.models import FieldZone
from app.satellite_fetcher import SatelliteFetcher
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_credentials():
    """Test that Copernicus credentials are configured."""
    logger.info("=" * 80)
    logger.info("Step 1: Checking Copernicus credentials")
    logger.info("=" * 80)

    if not settings.copernicus_username or not settings.copernicus_password:
        logger.error("❌ Copernicus credentials not configured!")
        logger.error("Please set COPERNICUS_USERNAME and COPERNICUS_PASSWORD in .env")
        return False

    logger.info(f"✅ Username: {settings.copernicus_username}")
    logger.info("✅ Password: ***configured***")
    return True


def test_database_connection():
    """Test database connection and zone availability."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("Step 2: Checking database connection and zones")
    logger.info("=" * 80)

    try:
        db = next(get_db())
        zones = db.query(FieldZone).all()

        if not zones:
            logger.error("❌ No zones found in database!")
            logger.error("Please load zones using: python scripts/load_field_zones.py")
            return False

        logger.info(f"✅ Database connected")
        logger.info(f"✅ Found {len(zones)} zones:")
        for zone in zones:
            logger.info(f"   - Zone {zone.id}: {zone.name} ({zone.area_hectares} ha)")

        db.close()
        return True

    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False


def test_api_connection():
    """Test connection to Copernicus API."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("Step 3: Testing Copernicus API connection")
    logger.info("=" * 80)

    try:
        fetcher = SatelliteFetcher()

        # Test OAuth2 authentication
        token = fetcher._get_access_token()

        logger.info("✅ Successfully obtained OAuth2 access token")
        logger.info(f"   Auth endpoint: {fetcher.AUTH_URL}")
        logger.info(f"   Token expires at: {fetcher.token_expires_at.strftime('%Y-%m-%d %H:%M:%S')}")
        return True

    except Exception as e:
        logger.error(f"❌ Failed to connect to Copernicus API: {e}")
        logger.error("")
        logger.error("Common issues:")
        logger.error("  - Invalid credentials (check username/password)")
        logger.error("  - Account not activated at https://dataspace.copernicus.eu")
        logger.error("  - Email not verified - check your inbox")
        logger.error("  - Network connectivity issues")
        return False


def test_query_products():
    """Test querying Sentinel-2 products for farm location."""
    logger.info("")
    logger.info("=" * 80)
    logger.info("Step 4: Querying Sentinel-2 products for olive groves")
    logger.info("=" * 80)

    try:
        # Get first zone geometry
        db = next(get_db())
        zone = db.query(FieldZone).first()

        if not zone:
            logger.error("❌ No zones available for testing")
            return False

        logger.info(f"Using zone: {zone.name}")
        logger.info(f"Location: ~42.303°N, 14.187°E (Abruzzo, Italy)")

        # Query last 30 days with relaxed cloud coverage
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)

        logger.info(f"Searching for products from {start_date} to {end_date}")
        logger.info("Cloud coverage: < 50% (relaxed for testing)")

        fetcher = SatelliteFetcher()
        products = fetcher.query_products(
            geometry=zone.geometry,
            start_date=start_date,
            end_date=end_date,
            cloud_coverage_max=50  # Relaxed for testing
        )

        if not products:
            logger.warning("⚠️  No products found in last 30 days")
            logger.warning("This might be due to:")
            logger.warning("  - High cloud coverage in recent days")
            logger.warning("  - Satellite orbit schedule")
            logger.warning("Try extending the search period with --days-back 60")
            return False

        logger.info(f"✅ Found {len(products)} Sentinel-2 products!")
        logger.info("")
        logger.info("Most recent products:")

        for i, product in enumerate(products[:5], 1):
            logger.info(
                f"  {i}. {product['date']} - "
                f"Cloud: {product['cloud_coverage']:.1f}% - "
                f"Size: {product['size_mb']} MB"
            )

        if len(products) > 5:
            logger.info(f"  ... and {len(products) - 5} more products")

        # Count by cloud coverage
        clear = sum(1 for p in products if p['cloud_coverage'] < 10)
        partly_cloudy = sum(1 for p in products if 10 <= p['cloud_coverage'] < 30)
        cloudy = sum(1 for p in products if p['cloud_coverage'] >= 30)

        logger.info("")
        logger.info("Cloud coverage distribution:")
        logger.info(f"  Clear (< 10%): {clear} products")
        logger.info(f"  Partly cloudy (10-30%): {partly_cloudy} products")
        logger.info(f"  Cloudy (> 30%): {cloudy} products")

        db.close()
        return True

    except Exception as e:
        logger.error(f"❌ Failed to query products: {e}")
        logger.error(f"Error details: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Test Copernicus Data Space access for olive monitoring'
    )
    parser.add_argument(
        '--days-back',
        type=int,
        default=30,
        help='Number of days to search back (default: 30)'
    )

    args = parser.parse_args()

    logger.info("Copernicus Data Space Access Test")
    logger.info("")

    # Run tests
    tests = [
        test_credentials,
        test_database_connection,
        test_api_connection,
        test_query_products
    ]

    results = []
    for test_func in tests:
        try:
            result = test_func()
            results.append(result)
            if not result:
                break  # Stop on first failure
        except Exception as e:
            logger.error(f"❌ Unexpected error in {test_func.__name__}: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
            break

    # Summary
    logger.info("")
    logger.info("=" * 80)
    logger.info("TEST SUMMARY")
    logger.info("=" * 80)

    test_names = [
        "Credentials configured",
        "Database connection",
        "Copernicus API access",
        "Query satellite products"
    ]

    for name, result in zip(test_names, results):
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {name}")

    # Overall result
    all_passed = all(results)
    logger.info("")
    if all_passed:
        logger.info("🎉 All tests passed! System is ready for satellite data processing.")
        logger.info("")
        logger.info("Next steps:")
        logger.info("  1. Run processing script: python scripts/process_satellite_data.py")
        logger.info("  2. Monitor logs: tail -f /app/data/processing.log")
        logger.info("  3. Check API for health data: curl http://localhost:8001/api/zones/5/health")
        sys.exit(0)
    else:
        logger.error("❌ Some tests failed. Please fix the issues above before proceeding.")
        sys.exit(1)


if __name__ == '__main__':
    main()
