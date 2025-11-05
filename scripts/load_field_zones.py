"""Load field zones from configuration into database."""
import json
import sys
from pathlib import Path
import os

# Add app directory to path (works both locally and in Docker)
script_dir = Path(__file__).parent
project_root = script_dir.parent

# Check if we're in Docker (app directory at /app)
if Path("/app/app").exists():
    sys.path.insert(0, "/app")
else:
    # Running locally
    sys.path.insert(0, str(project_root / "backend"))

from app.database import get_db_engine, get_session_local
from app.models import FieldZone, Base


def load_zones_from_config(config_path: str):
    """Load field zones from JSON config file into database."""
    # Read configuration
    with open(config_path, 'r') as f:
        config = json.load(f)

    # Create database engine and session
    engine = get_db_engine()
    SessionLocal = get_session_local()
    db = SessionLocal()

    try:
        print(f"📍 Location: {config['location']['name']}, {config['location']['region']}")
        print(f"   Coordinates: {config['location']['center_lat']:.3f}°N, {config['location']['center_lon']:.3f}°E")
        print()

        # Delete existing zones
        existing_count = db.query(FieldZone).count()
        if existing_count > 0:
            print(f"🗑️  Deleting {existing_count} existing zone(s)...")
            db.query(FieldZone).delete()
            db.commit()
            print("   ✓ Existing zones removed")
            print()

        # Insert new zones
        print(f"📥 Loading {len(config['zones'])} zone(s) from configuration...")
        print()

        for zone_data in config['zones']:
            zone = FieldZone(
                name=zone_data['name'],
                description=zone_data['description'],
                geometry=zone_data['geometry'],
                area_hectares=zone_data['area_hectares']
            )
            db.add(zone)
            print(f"   ✓ {zone_data['name']}: {zone_data['area_hectares']} hectares")

        db.commit()

        # Verify
        total_zones = db.query(FieldZone).count()
        total_area = sum(z.area_hectares for z in db.query(FieldZone).all())

        print()
        print("✅ Configuration loaded successfully!")
        print(f"   Total zones: {total_zones}")
        print(f"   Total area: {total_area:.2f} hectares")

    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
        raise
    finally:
        db.close()


def main():
    """Main function."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # Try Docker path first, then local path
    config_file = project_root / "config" / "field_zones.json"

    if not config_file.exists():
        print(f"❌ Configuration file not found: {config_file}")
        print("   Run parse_kml_zones.py first to generate the configuration.")
        print(f"   Looking in: {config_file.absolute()}")
        sys.exit(1)

    print("=" * 60)
    print("🌳 Loading Olive Grove Field Zones")
    print("=" * 60)
    print()

    load_zones_from_config(str(config_file))

    print()
    print("=" * 60)
    print("🎯 Next steps:")
    print("   1. Verify zones in API: curl http://localhost:8001/api/zones")
    print("   2. Test Copernicus satellite data query")
    print("=" * 60)


if __name__ == "__main__":
    main()
