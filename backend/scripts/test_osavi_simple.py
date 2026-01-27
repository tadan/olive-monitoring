"""Simple test of calculate_osavi with known values."""
import sys
from pathlib import Path

# Add app directory to path
if Path("/app/app").exists():
    sys.path.insert(0, "/app")
else:
    sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.vegetation_indices import calculate_osavi, calculate_ndvi
import numpy as np

# Test with values that should give NDVI=0.491
red = np.array([0.2], dtype=np.float32)
nir = np.array([0.586], dtype=np.float32)

ndvi = calculate_ndvi(red, nir)
osavi = calculate_osavi(red, nir)

print(f'Red: {red[0]:.3f}, NIR: {nir[0]:.3f}')
print(f'NDVI result: {ndvi[0]:.6f}')
print(f'OSAVI result: {osavi[0]:.6f}')
print(f'OSAVI Expected: ~0.408')
print()

# Also calculate manually
manual_ndvi = (nir[0] - red[0]) / (nir[0] + red[0])
manual_osavi = (nir[0] - red[0]) / (nir[0] + red[0] + 0.16)

print(f'Manual NDVI: {manual_ndvi:.6f}')
print(f'Manual OSAVI: {manual_osavi:.6f}')
print()

print(f'Function matches manual? {abs(osavi[0] - manual_osavi) < 0.000001}')
