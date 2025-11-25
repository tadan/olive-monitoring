"""Parse Ridgedale Farm KML file and add to database."""
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List
import math
import os
import sys

# Add backend to path so we can import app modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import SessionLocal
from app.models import FieldZone


def parse_coordinates(coord_string: str) -> List[List[float]]:
    """
    Parse KML coordinates string to GeoJSON format.

    KML format: lon,lat,alt lon,lat,alt ...
    GeoJSON format: [[lon, lat], [lon, lat], ...]
    """
    coords = []
    for coord in coord_string.strip().split():
        parts = coord.split(',')
        if len(parts) >= 2:
            lon, lat = float(parts[0]), float(parts[1])
            coords.append([lon, lat])
    return coords


def calculate_polygon_area_hectares(coordinates: List[List[float]]) -> float:
    """
    Calculate area of polygon in hectares using spherical geometry.

    Uses the spherical excess formula for accurate area calculation on Earth's surface.
    """
    # Earth's radius in meters
    EARTH_RADIUS = 6371000

    # Convert to radians
    coords_rad = [[math.radians(lon), math.radians(lat)] for lon, lat in coordinates]

    # Calculate area using spherical excess (more accurate for lat/lon)
    n = len(coords_rad)
    area = 0.0

    for i in range(n):
        j = (i + 1) % n
        lon1, lat1 = coords_rad[i]
        lon2, lat2 = coords_rad[j]
        area += (lon2 - lon1) * (2 + math.sin(lat1) + math.sin(lat2))

    area = abs(area * EARTH_RADIUS * EARTH_RADIUS / 2.0)

    # Convert square meters to hectares
    hectares = area / 10000.0

    return round(hectares, 2)


def parse_ridgedale_kml(kml_path: str) -> dict:
    """Parse Ridgedale Farm KML file and extract zone."""
    tree = ET.parse(kml_path)
    root = tree.getroot()

    # KML namespace
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}

    # Find the Placemark
    placemark = root.find('.//kml:Placemark', ns)
    if placemark is None:
        raise ValueError("No Placemark found in KML file")

    name_elem = placemark.find('kml:name', ns)
    coords_elem = placemark.find('.//kml:coordinates', ns)

    if name_elem is None or coords_elem is None:
        raise ValueError("Invalid KML structure")

    name = name_elem.text
    coordinates = parse_coordinates(coords_elem.text)

    # Calculate area
    area_hectares = calculate_polygon_area_hectares(coordinates)

    # Create GeoJSON polygon
    # Note: GeoJSON requires first and last coordinate to be the same (closed polygon)
    if coordinates[0] != coordinates[-1]:
        coordinates.append(coordinates[0])

    zone = {
        "name": f"Ridgedale Farm",
        "description": "Regenerative agriculture farm in Sweden for comparison with olive farming practices",
        "geometry": {
            "type": "Polygon",
            "coordinates": [coordinates]  # GeoJSON Polygon requires array of rings
        },
        "area_hectares": area_hectares
    }

    return zone


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
        print(f"  Coordinates: {len(zone['geometry']['coordinates'][0])} points")

        return new_zone.id

    except Exception as e:
        db.rollback()
        print(f"✗ Error adding zone: {e}")
        raise
    finally:
        db.close()


def main():
    """Main function to parse Ridgedale KML and add to database."""
    # Input KML file
    kml_file = Path(__file__).parent.parent.parent.parent / "03 - RegenAg" / "Ridgedale Farm.kml"

    print(f"Reading KML file: {kml_file}")

    if not kml_file.exists():
        print(f"✗ KML file not found: {kml_file}")
        return

    # Parse KML
    zone = parse_ridgedale_kml(str(kml_file))

    print(f"\n✓ Parsed Ridgedale Farm zone")
    print(f"  Area: {zone['area_hectares']} hectares")

    # Add to database
    print("\nAdding zone to database...")
    zone_id = add_zone_to_database(zone)

    print(f"\n✓ Ridgedale Farm zone ready for monitoring!")
    print(f"\nNext steps:")
    print(f"1. Run satellite data processing for Ridgedale (zone ID: {zone_id})")
    print(f"2. View Ridgedale data in the dashboard under 'Ridgedale Farm' tab")


if __name__ == "__main__":
    main()
