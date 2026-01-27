"""Detailed OSAVI calculation test with manual numpy calculation."""
import sys
from pathlib import Path
from datetime import date
import numpy as np

# Add app directory to path (works both locally and in Docker)
script_dir = Path(__file__).parent
project_root = script_dir.parent

# Check if we're in Docker (app directory at /app)
if Path("/app/app").exists():
    sys.path.insert(0, "/app")
else:
    # Running locally
    sys.path.insert(0, str(project_root / "backend"))

from app.vegetation_indices import calculate_ndvi, calculate_osavi

# Test the functions with simple values
print("=" * 60)
print("MANUAL CALCULATION TEST")
print("=" * 60)

# Create test arrays with realistic values
red = np.array([0.1, 0.2, 0.15, 0.18], dtype=np.float32)
nir = np.array([0.5, 0.6, 0.55, 0.58], dtype=np.float32)

print(f"Red band sample: {red}")
print(f"NIR band sample: {nir}")
print()

# Calculate NDVI
ndvi = calculate_ndvi(red, nir)
print(f"NDVI formula: (NIR - Red) / (NIR + Red)")
print(f"NDVI result: {ndvi}")
print(f"NDVI mean: {ndvi.mean():.6f}")
print()

# Calculate OSAVI
osavi = calculate_osavi(red, nir)
print(f"OSAVI formula: (NIR - Red) / (NIR + Red + 0.16)")
print(f"OSAVI result: {osavi}")
print(f"OSAVI mean: {osavi.mean():.6f}")
print()

# Manual calculation to verify
manual_ndvi = (nir - red) / (nir + red)
manual_osavi = (nir - red) / (nir + red + 0.16)

print(f"Manual NDVI: {manual_ndvi}")
print(f"Manual NDVI mean: {manual_ndvi.mean():.6f}")
print()

print(f"Manual OSAVI: {manual_osavi}")
print(f"Manual OSAVI mean: {manual_osavi.mean():.6f}")
print()

print("COMPARISON:")
print(f"  NDVI mean:  {ndvi.mean():.6f}")
print(f"  OSAVI mean: {osavi.mean():.6f}")
print(f"  Difference: {abs(osavi.mean() - ndvi.mean()):.6f}")
print(f"  Are they equal? {ndvi.mean() == osavi.mean()}")
print()

print("EXPECTED BEHAVIOR:")
print("  OSAVI should be LOWER than NDVI (denominator has +0.16)")
print(f"  OSAVI < NDVI? {osavi.mean() < ndvi.mean()}")
print()

# Now test with values similar to the database
print("=" * 60)
print("DATABASE VALUES TEST (Zone 2: NDVI=0.491)")
print("=" * 60)

# If NDVI = 0.491, what are typical Red/NIR values?
# NDVI = (NIR - Red) / (NIR + Red) = 0.491
# This means NIR/(NIR+Red) = (1 + 0.491)/2 = 0.7455
# Let's use Red=0.2, NIR=0.586 which gives NDVI ≈ 0.491

red_real = np.array([0.2])
nir_real = np.array([0.586])

ndvi_real = calculate_ndvi(red_real, nir_real)
osavi_real = calculate_osavi(red_real, nir_real)

print(f"Red: {red_real[0]:.3f}, NIR: {nir_real[0]:.3f}")
print(f"NDVI:  {ndvi_real[0]:.6f}")
print(f"OSAVI: {osavi_real[0]:.6f}")
print(f"Difference: {abs(osavi_real[0] - ndvi_real[0]):.6f}")
print()

print("EXPECTED IN DATABASE:")
print(f"  NDVI:  0.491000")
print(f"  OSAVI: ~0.450000 (should be lower)")
print()

print("ACTUAL IN DATABASE:")
print(f"  NDVI:  0.491000")
print(f"  OSAVI: 0.491000 ← BUG! Should not equal NDVI!")
