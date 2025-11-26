"""Load Ridgedale Farm zone from JSON configuration file."""
import json
import sys
from pathlib import Path

# Add backend to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import FieldZone


def load_zone_from_json(json_path: str) -> dict:
    """Load zone configuration from JSON file."""
    with open(json_path, 'r') as f:
        return json.load(f)


def add_zone_to_database(zone: dict):
    """Add zone to database."""
    db = SessionLocal()

    try:
        # Check if Ridgedale zone already exists
        existing = db.query(FieldZone).filter(
            FieldZone.name.like('%Ridgedale%')
        ).first()

        if existing:
            print(f"⚠️  Ridgedale zone already exists in database (ID: {existing.id})")
            print("   Updating existing zone...")
            existing.description = zone['description']
            existing.geometry = zone['geometry']
            existing.area_hectares = zone['area_hectares']
            db.commit()
            print(f"✓ Updated zone: {zone['name']} (ID: {existing.id})")
            return existing.id

        # Create new zone
        new_zone = FieldZone(
            name=zone['name'],
            description=zone['description'],
            geometry=zone['geometry'],
            area_hectares=zone['area_hectares']
        )

        db.add(new_zone)
        db.commit()
        db.refresh(new_zone)

        print(f"✓ Added zone: {zone['name']} (ID: {new_zone.id})")
        print(f"  Area: {zone['area_hectares']} hectares")
        print(f"  Location: {zone['location']['region']}")
        print(f"  Coordinates: {len(zone['geometry']['coordinates'][0])} points")

        return new_zone.id

    except Exception as e:
        db.rollback()
        print(f"✗ Error adding zone: {e}")
        raise
    finally:
        db.close()


def main():
    """Main function to load Ridgedale zone from JSON and add to database."""
    # JSON config file (in the config directory)
    json_file = Path(__file__).parent.parent / "config" / "ridgedale_zone.json"

    print(f"Reading configuration file: {json_file}")

    if not json_file.exists():
        print(f"✗ Configuration file not found: {json_file}")
        print(f"   Expected location: backend/config/ridgedale_zone.json")
        return

    # Load zone from JSON
    zone = load_zone_from_json(str(json_file))

    print(f"\n✓ Loaded Ridgedale Farm configuration")
    print(f"  Name: {zone['name']}")
    print(f"  Area: {zone['area_hectares']} hectares")
    print(f"  Location: {zone['location']['name']}, {zone['location']['region']}")

    # Add to database
    print("\nAdding zone to database...")
    zone_id = add_zone_to_database(zone)

    print(f"\n✓ Ridgedale Farm zone ready for monitoring!")
    print(f"\nNext steps:")
    print(f"1. Run satellite data processing: docker-compose exec processor python scripts/process_satellite_data.py")
    print(f"2. View Ridgedale data in the dashboard under 'Ridgedale Farm' tab")
    print(f"3. Restart dashboard: docker-compose restart dashboard")


if __name__ == "__main__":
    main()
