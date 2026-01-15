-- Migration: Add ARVI and OSAVI vegetation indices
-- Date: 2026-01-15
-- Description: Adds ARVI (Atmospherically Resistant Vegetation Index) and OSAVI (Optimized Soil-Adjusted Vegetation Index)
--              columns to the health_indices table for enhanced vegetation monitoring accuracy.

-- Add ARVI columns
ALTER TABLE health_indices ADD COLUMN IF NOT EXISTS arvi_mean DECIMAL(5, 4);
ALTER TABLE health_indices ADD COLUMN IF NOT EXISTS arvi_std DECIMAL(5, 4);
ALTER TABLE health_indices ADD COLUMN IF NOT EXISTS arvi_min DECIMAL(5, 4);
ALTER TABLE health_indices ADD COLUMN IF NOT EXISTS arvi_max DECIMAL(5, 4);

-- Add OSAVI columns
ALTER TABLE health_indices ADD COLUMN IF NOT EXISTS osavi_mean DECIMAL(5, 4);
ALTER TABLE health_indices ADD COLUMN IF NOT EXISTS osavi_std DECIMAL(5, 4);
ALTER TABLE health_indices ADD COLUMN IF NOT EXISTS osavi_min DECIMAL(5, 4);
ALTER TABLE health_indices ADD COLUMN IF NOT EXISTS osavi_max DECIMAL(5, 4);

-- Add comments for documentation
COMMENT ON COLUMN health_indices.arvi_mean IS 'Mean ARVI (Atmospherically Resistant Vegetation Index) - reduced atmospheric interference';
COMMENT ON COLUMN health_indices.arvi_std IS 'Standard deviation of ARVI';
COMMENT ON COLUMN health_indices.arvi_min IS 'Minimum ARVI value in zone';
COMMENT ON COLUMN health_indices.arvi_max IS 'Maximum ARVI value in zone';

COMMENT ON COLUMN health_indices.osavi_mean IS 'Mean OSAVI (Optimized Soil-Adjusted Vegetation Index) - reduced soil background effects';
COMMENT ON COLUMN health_indices.osavi_std IS 'Standard deviation of OSAVI';
COMMENT ON COLUMN health_indices.osavi_min IS 'Minimum OSAVI value in zone';
COMMENT ON COLUMN health_indices.osavi_max IS 'Maximum OSAVI value in zone';
