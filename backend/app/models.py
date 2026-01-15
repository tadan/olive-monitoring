"""SQLAlchemy models for database tables."""
from sqlalchemy import Column, Integer, String, Text, DECIMAL, Boolean, TIMESTAMP, Date, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class FieldZone(Base):
    """Model for field_zones table."""
    __tablename__ = "field_zones"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    geometry = Column(JSON, nullable=False)  # GeoJSON format
    area_hectares = Column(DECIMAL(10, 2))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    health_indices = relationship("HealthIndex", back_populates="zone")
    alerts = relationship("Alert", back_populates="zone")


class SatelliteImage(Base):
    """Model for satellite_images table."""
    __tablename__ = "satellite_images"

    id = Column(Integer, primary_key=True, index=True)
    acquisition_date = Column(Date, nullable=False)
    satellite = Column(String(50), nullable=False)
    cloud_coverage_percent = Column(DECIMAL(5, 2))
    scene_id = Column(String(255), unique=True, nullable=False)
    download_path = Column(Text)
    processed = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    health_indices = relationship("HealthIndex", back_populates="image")


class HealthIndex(Base):
    """Model for health_indices table."""
    __tablename__ = "health_indices"

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("field_zones.id", ondelete="CASCADE"))
    image_id = Column(Integer, ForeignKey("satellite_images.id", ondelete="CASCADE"))
    acquisition_date = Column(Date, nullable=False)
    ndvi_mean = Column(DECIMAL(5, 4))
    ndvi_std = Column(DECIMAL(5, 4))
    ndvi_min = Column(DECIMAL(5, 4))
    ndvi_max = Column(DECIMAL(5, 4))
    ndmi_mean = Column(DECIMAL(5, 4))
    ndmi_std = Column(DECIMAL(5, 4))
    ndmi_min = Column(DECIMAL(5, 4))
    ndmi_max = Column(DECIMAL(5, 4))
    arvi_mean = Column(DECIMAL(5, 4))
    arvi_std = Column(DECIMAL(5, 4))
    arvi_min = Column(DECIMAL(5, 4))
    arvi_max = Column(DECIMAL(5, 4))
    osavi_mean = Column(DECIMAL(5, 4))
    osavi_std = Column(DECIMAL(5, 4))
    osavi_min = Column(DECIMAL(5, 4))
    osavi_max = Column(DECIMAL(5, 4))
    vegetation_health_score = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    zone = relationship("FieldZone", back_populates="health_indices")
    image = relationship("SatelliteImage", back_populates="health_indices")


class Alert(Base):
    """Model for alerts table."""
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("field_zones.id", ondelete="CASCADE"))
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    metric = Column(String(50))
    metric_value = Column(DECIMAL(10, 4))
    threshold_value = Column(DECIMAL(10, 4))
    status = Column(String(20), default="active")
    detected_at = Column(TIMESTAMP, server_default=func.now())
    resolved_at = Column(TIMESTAMP)
    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships
    zone = relationship("FieldZone", back_populates="alerts")


class BaselineStatistic(Base):
    """Model for baseline_statistics table."""
    __tablename__ = "baseline_statistics"

    id = Column(Integer, primary_key=True, index=True)
    zone_id = Column(Integer, ForeignKey("field_zones.id", ondelete="CASCADE"))
    metric = Column(String(50), nullable=False)
    season = Column(String(20))
    mean_value = Column(DECIMAL(5, 4))
    std_dev = Column(DECIMAL(5, 4))
    min_value = Column(DECIMAL(5, 4))
    max_value = Column(DECIMAL(5, 4))
    sample_count = Column(Integer)
    last_updated = Column(TIMESTAMP, server_default=func.now())
