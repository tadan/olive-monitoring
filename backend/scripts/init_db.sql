-- Enable PostGIS extension (optional, for future spatial queries)
-- CREATE EXTENSION IF NOT EXISTS postgis;

-- Field zones table (olive grove boundaries)
CREATE TABLE field_zones (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    geometry JSONB NOT NULL,  -- GeoJSON format
    area_hectares DECIMAL(10, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Satellite images metadata
CREATE TABLE satellite_images (
    id SERIAL PRIMARY KEY,
    acquisition_date DATE NOT NULL,
    satellite VARCHAR(50) NOT NULL,  -- e.g., 'Sentinel-2A'
    cloud_coverage_percent DECIMAL(5, 2),
    scene_id VARCHAR(255) UNIQUE NOT NULL,
    download_path TEXT,
    processed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Health indices time-series data
CREATE TABLE health_indices (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER REFERENCES field_zones(id) ON DELETE CASCADE,
    image_id INTEGER REFERENCES satellite_images(id) ON DELETE CASCADE,
    acquisition_date DATE NOT NULL,
    ndvi_mean DECIMAL(5, 4),
    ndvi_std DECIMAL(5, 4),
    ndvi_min DECIMAL(5, 4),
    ndvi_max DECIMAL(5, 4),
    ndmi_mean DECIMAL(5, 4),
    ndmi_std DECIMAL(5, 4),
    ndmi_min DECIMAL(5, 4),
    ndmi_max DECIMAL(5, 4),
    vegetation_health_score INTEGER CHECK (vegetation_health_score BETWEEN 0 AND 100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(zone_id, image_id)
);

-- Alerts table
CREATE TABLE alerts (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER REFERENCES field_zones(id) ON DELETE CASCADE,
    alert_type VARCHAR(50) NOT NULL,  -- 'critical', 'warning', 'info'
    severity VARCHAR(20) NOT NULL,  -- 'high', 'medium', 'low'
    title VARCHAR(255) NOT NULL,
    description TEXT,
    metric VARCHAR(50),  -- 'ndvi', 'ndmi', etc.
    metric_value DECIMAL(10, 4),
    threshold_value DECIMAL(10, 4),
    status VARCHAR(20) DEFAULT 'active',  -- 'active', 'resolved', 'dismissed'
    detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Baseline statistics (for anomaly detection)
CREATE TABLE baseline_statistics (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER REFERENCES field_zones(id) ON DELETE CASCADE,
    metric VARCHAR(50) NOT NULL,  -- 'ndvi', 'ndmi'
    season VARCHAR(20),  -- 'spring', 'summer', 'fall', 'winter'
    mean_value DECIMAL(5, 4),
    std_dev DECIMAL(5, 4),
    min_value DECIMAL(5, 4),
    max_value DECIMAL(5, 4),
    sample_count INTEGER,
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(zone_id, metric, season)
);

-- Create indices for performance
CREATE INDEX idx_health_indices_zone_date ON health_indices(zone_id, acquisition_date);
CREATE INDEX idx_health_indices_date ON health_indices(acquisition_date);
CREATE INDEX idx_alerts_zone_status ON alerts(zone_id, status);
CREATE INDEX idx_alerts_detected ON alerts(detected_at);
CREATE INDEX idx_satellite_images_date ON satellite_images(acquisition_date);

-- Insert default field zone (to be updated with actual coordinates)
INSERT INTO field_zones (name, description, geometry, area_hectares)
VALUES (
    'Main Olive Grove',
    'Primary olive grove area',
    '{"type":"Polygon","coordinates":[[[0,0],[0,1],[1,1],[1,0],[0,0]]]}',
    10.0
);

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for field_zones
CREATE TRIGGER update_field_zones_updated_at BEFORE UPDATE ON field_zones
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
