"""FastAPI application for Olive Farm Monitoring."""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
from datetime import date, datetime

from app.config import settings
from app.database import get_db, FieldZone, HealthIndex, Alert
from sqlalchemy.orm import Session
from sqlalchemy import desc

app = FastAPI(
    title="Olive Farm Satellite Monitoring API",
    description="API for monitoring olive grove health using Sentinel-2 satellite data",
    version="1.0.0"
)

# CORS middleware for dashboard access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "online",
        "service": "Olive Farm Monitoring API",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check with database connectivity."""
    try:
        # Test database connection
        db = next(get_db())
        db.execute("SELECT 1")
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return {
        "status": "ok",
        "database": db_status,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/zones")
async def get_zones():
    """Get all field zones."""
    db = next(get_db())
    zones = db.query(FieldZone).all()

    return [{
        "id": zone.id,
        "name": zone.name,
        "area_hectares": float(zone.area_hectares),
        "geometry": zone.geometry
    } for zone in zones]


@app.get("/api/zones/{zone_id}/health")
async def get_zone_health(zone_id: int, limit: int = 10):
    """Get recent health indices for a specific zone."""
    db = next(get_db())

    # Verify zone exists
    zone = db.query(FieldZone).filter(FieldZone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    # Get recent health indices
    health_records = (
        db.query(HealthIndex)
        .filter(HealthIndex.zone_id == zone_id)
        .order_by(desc(HealthIndex.date))
        .limit(limit)
        .all()
    )

    return [{
        "date": record.date.isoformat(),
        "ndvi_mean": float(record.ndvi_mean),
        "ndmi_mean": float(record.ndmi_mean),
        "health_score": record.health_score,
        "cloud_coverage": float(record.cloud_coverage) if record.cloud_coverage else None
    } for record in health_records]


@app.get("/api/zones/{zone_id}/alerts")
async def get_zone_alerts(zone_id: int, active_only: bool = True):
    """Get alerts for a specific zone."""
    db = next(get_db())

    # Verify zone exists
    zone = db.query(FieldZone).filter(FieldZone.id == zone_id).first()
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    # Query alerts
    query = db.query(Alert).filter(Alert.zone_id == zone_id)

    if active_only:
        query = query.filter(Alert.resolved_at.is_(None))

    alerts = query.order_by(desc(Alert.created_at)).all()

    return [{
        "id": alert.id,
        "type": alert.alert_type,
        "severity": alert.severity,
        "message": alert.message,
        "created_at": alert.created_at.isoformat(),
        "resolved_at": alert.resolved_at.isoformat() if alert.resolved_at else None
    } for alert in alerts]


@app.get("/api/dashboard/summary")
async def get_dashboard_summary():
    """Get summary statistics for dashboard."""
    db = next(get_db())

    # Get all zones with their latest health data
    zones = db.query(FieldZone).all()

    summary = []
    for zone in zones:
        # Get latest health index
        latest_health = (
            db.query(HealthIndex)
            .filter(HealthIndex.zone_id == zone.id)
            .order_by(desc(HealthIndex.date))
            .first()
        )

        # Count active alerts
        active_alerts = (
            db.query(Alert)
            .filter(Alert.zone_id == zone.id, Alert.resolved_at.is_(None))
            .count()
        )

        summary.append({
            "zone_id": zone.id,
            "zone_name": zone.name,
            "area_hectares": float(zone.area_hectares),
            "latest_health_score": latest_health.health_score if latest_health else None,
            "latest_health_date": latest_health.date.isoformat() if latest_health else None,
            "active_alerts": active_alerts
        })

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "zones": summary
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
