"""Test script to verify OSAVI calculation for Jan 26, 2026 data."""
from app.database import get_session_local
from app.models import SatelliteImage, FieldZone
from app.image_processor import ImageProcessor
from datetime import date
from pathlib import Path

db = next(get_session_local())

# Find the Jan 26 image
image = db.query(SatelliteImage).filter(
    SatelliteImage.acquisition_date == date(2026, 1, 26)
).first()

if image:
    print(f'Found image: {image.scene_id}')
    print(f'Download path: {image.download_path}')

    # Get one zone to test
    zone = db.query(FieldZone).filter(FieldZone.id == 2).first()
    if zone:
        processor = ImageProcessor()

        # Test the calculation manually
        product_path = Path(image.download_path)

        if product_path.exists():
            print(f'Product path exists: {product_path}')
            bands = processor.extract_bands(product_path, zone.geometry)

            if bands:
                print(f'Bands extracted successfully')
                print(f'Band keys: {bands.keys()}')

                # Calculate indices
                indices = processor.calculate_indices_for_zone(bands)

                if indices:
                    ndvi, ndmi, arvi, osavi = indices
                    print('')
                    print('CALCULATION RESULTS:')
                    print(f'NDVI mean: {float(ndvi.mean()):.6f}')
                    print(f'ARVI mean: {float(arvi.mean()):.6f}')
                    print(f'OSAVI mean: {float(osavi.mean()):.6f}')
                    print('')
                    print(f'Are NDVI and OSAVI equal? {ndvi.mean() == osavi.mean()}')
                    print(f'Difference: {abs(float(osavi.mean()) - float(ndvi.mean())):.6f}')
                    print('')
                    print('DATABASE VALUES:')
                    from app.models import HealthIndex
                    db_record = db.query(HealthIndex).filter(
                        HealthIndex.zone_id == 2,
                        HealthIndex.acquisition_date == date(2026, 1, 26)
                    ).first()
                    if db_record:
                        print(f'DB NDVI mean: {float(db_record.ndvi_mean):.6f}')
                        print(f'DB ARVI mean: {float(db_record.arvi_mean):.6f}')
                        print(f'DB OSAVI mean: {float(db_record.osavi_mean):.6f}')
            else:
                print('Failed to extract bands')
        else:
            print(f'Product path does NOT exist: {product_path}')
    else:
        print('Zone 2 not found')
else:
    print('No image found for 2026-01-26')
