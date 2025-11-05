"""Parse KML file and create field_zones.json configuration."""
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Tuple
import math


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


def parse_kml_file(kml_path: str) -> List[dict]:
    """Parse KML file and extract field zones."""
    tree = ET.parse(kml_path)
    root = tree.getroot()

    # KML namespace
    ns = {'kml': 'http://www.opengis.net/kml/2.2'}

    zones = []

    # Find all Placemark elements
    for placemark in root.findall('.//kml:Placemark', ns):
        name_elem = placemark.find('kml:name', ns)
        coords_elem = placemark.find('.//kml:coordinates', ns)

        if name_elem is not None and coords_elem is not None:
            name = name_elem.text
            coordinates = parse_coordinates(coords_elem.text)

            # Calculate area
            area_hectares = calculate_polygon_area_hectares(coordinates)

            # Create GeoJSON polygon
            # Note: GeoJSON requires first and last coordinate to be the same (closed polygon)
            if coordinates[0] != coordinates[-1]:
                coordinates.append(coordinates[0])

            zone = {
                "name": name,
                "description": f"Olive grove section: {name}",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coordinates]  # GeoJSON Polygon requires array of rings
                },
                "area_hectares": area_hectares
            }

            zones.append(zone)
            print(f"✓ Parsed zone: {name} ({area_hectares} hectares)")

    return zones


def main():
    """Main function to parse KML and create configuration."""
    # Input KML file
    kml_file = Path(__file__).parent.parent.parent / "03 - RegenAg" / "Tatasciore's Olive Fields.kml"

    # Output JSON file
    output_file = Path(__file__).parent.parent / "config" / "field_zones.json"

    print(f"Reading KML file: {kml_file}")

    # Parse KML
    zones = parse_kml_file(str(kml_file))

    print(f"\n✓ Found {len(zones)} zones")
    print(f"Total area: {sum(z['area_hectares'] for z in zones):.2f} hectares")

    # Create config structure
    config = {
        "location": {
            "name": "Tatasciore Olive Farm",
            "region": "Abruzzo, Italy",
            "center_lat": 42.303,
            "center_lon": 14.187
        },
        "zones": zones
    }

    # Write to JSON file
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(config, f, indent=2)

    print(f"\n✓ Configuration written to: {output_file}")
    print("\nZone Summary:")
    for zone in zones:
        print(f"  • {zone['name']}: {zone['area_hectares']} ha")


if __name__ == "__main__":
    main()
