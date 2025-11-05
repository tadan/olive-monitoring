# Olive Farm Satellite Monitoring - Claude Code Context

**Project:** Satellite-based monitoring system for Tatasciore Olive Farm (Abruzzo, Italy)
**Status:** Phase 1 Complete ✅ | Phase 2 Pending ⏳
**Last Updated:** 2025-11-05
**Location:** /Users/danieletatasciore/Documents/repos/claude/olive-monitoring

---

## Project Overview

A self-hosted satellite monitoring portal that automatically tracks olive grove health using free Copernicus Sentinel-2 satellite data. The system runs on a Synology DS716+II NAS in Sweden (remote from the Italian farm), processes imagery every 5 days, and provides a public dashboard for transparency with Swedish customers.

**Farm Details:**
- **Name:** Tatasciore Olive Farm
- **Location:** Abruzzo, Italy (42.303°N, 14.187°E)
- **Total Area:** 1.00 hectare across 3 zones
- **Varieties:** Frantoio, Leccino

**Zones:**
1. **Below Natural** - 0.33 ha (ID: 5)
2. **Below Falling Houses** - 0.35 ha (ID: 6)
3. **House** - 0.32 ha (ID: 7)

---

## Current Architecture

### Infrastructure (Running on Synology NAS in Sweden)

**Docker Containers (3):**
- `olive-monitoring-db` - PostgreSQL 15 (port 5432 internal only)
- `olive-monitoring-processor` - Python 3.11 + GDAL for satellite processing
- `olive-monitoring-api` - FastAPI REST API (port 8001)

**Database Schema (6 tables):**
- `field_zones` - Olive grove boundaries (GeoJSON)
- `satellite_images` - Sentinel-2 metadata
- `health_indices` - NDVI/NDMI time-series data
- `alerts` - Health anomaly alerts
- `baseline_statistics` - Seasonal baseline data
- Indexes for performance optimization

### Tech Stack

**Backend:**
- Python 3.11
- FastAPI (REST API)
- PostgreSQL 15 + SQLAlchemy ORM
- sentinelsat (Copernicus API client)
- rasterio + GDAL (geospatial processing)
- numpy, scipy, scikit-learn (analysis)

**Frontend:** Not yet implemented (Phase 3)

**Data Source:** Copernicus Sentinel-2 satellites (free, 10m resolution, 5-day revisit)

---

## Implementation Status

### ✅ Phase 1: Data Pipeline Foundation (COMPLETE)

**Completed Components:**
1. Docker Compose setup with 3 services
2. PostgreSQL database with complete schema
3. Configuration management (Pydantic settings)
4. Database models (7 SQLAlchemy models)
5. Copernicus Sentinel-2 data fetcher
6. NDVI/NDMI calculation functions
7. FastAPI with 8 endpoints
8. Unit tests (18 tests, all passing)
9. KML parsing and field zone loading

**Files Created:**
- `docker-compose.yml` - Container orchestration
- `docker/processor.Dockerfile` - Processor container (Python + GDAL)
- `docker/api.Dockerfile` - API container (Python lightweight)
- `backend/app/config.py` - Configuration management
- `backend/app/database.py` - SQLAlchemy engine
- `backend/app/models.py` - Database models
- `backend/app/satellite_fetcher.py` - Copernicus API client
- `backend/app/vegetation_indices.py` - NDVI/NDMI calculations
- `backend/app/main.py` - FastAPI application
- `backend/scripts/init_db.sql` - Database schema
- `backend/scripts/parse_kml_zones.py` - KML to GeoJSON converter
- `backend/scripts/load_field_zones.py` - Load zones into database
- `backend/config/field_zones.json` - Real farm zone data
- `backend/requirements.txt` - Python dependencies (full)
- `backend/requirements-api.txt` - API dependencies (lightweight)
- `.env.example` - Environment template
- `README.md` - Project documentation
- `DEPLOYMENT.md` - Comprehensive deployment guide

### ⏳ Phase 2: Analysis Engine (NOT STARTED)

**Missing Components:**
1. `backend/app/image_processor.py` - Sentinel-2 band extraction and processing
2. `backend/app/alerts.py` - Anomaly detection and alert generation
3. `backend/app/baseline.py` - Seasonal baseline calculation
4. `backend/scripts/process_satellite_data.py` - Main processing orchestration

### ❌ Phase 3: Dashboard (NOT STARTED)

**Missing Components:**
1. React application setup
2. Interactive map with Leaflet
3. Time-series charts with Chart.js
4. Alert viewer interface
5. Farm story page

---

## API Endpoints (Port 8001)

### Working Endpoints ✅

```bash
GET /                              # Service info
GET /health                        # Health check + DB connectivity
GET /api/zones                     # List all field zones
GET /api/zones/{zone_id}          # Get specific zone details
GET /api/zones/{zone_id}/health    # Zone health history (empty until processing)
GET /api/zones/{zone_id}/alerts    # Zone alerts (empty until processing)
GET /api/dashboard/summary         # Dashboard summary with all zones
```

### Testing Commands

```bash
# On NAS via SSH
curl http://localhost:8001/health
curl http://localhost:8001/api/zones
curl http://localhost:8001/api/zones/5
curl http://localhost:8001/api/dashboard/summary
```

---

## Recent Sessions

### Session 2025-11-05: API Testing & KML Integration

**Accomplishments:**
1. ✅ Checked project implementation status (Phase 1 complete)
2. ✅ Parsed KML file from Google Earth with 3 olive grove zones
3. ✅ Loaded field zones into PostgreSQL database on NAS
4. ✅ Tested API endpoints - all working correctly
5. ✅ Fixed missing GET /api/zones/{zone_id} endpoint
6. ✅ Verified Docker containers running on NAS

**Key Decisions:**
- API uses port 8001 (not 8000) to avoid conflicts
- PostgreSQL port not exposed externally (security)
- Real farm coordinates loaded from KML (Tatasciore farm data)

**Issues Resolved:**
- KML parser path corrected (needed one more ../ to reach claude directory)
- Added missing GET /api/zones/{zone_id} endpoint to main.py

**Files Modified:**
- `backend/scripts/parse_kml_zones.py` - Fixed KML file path
- `backend/app/main.py` - Added GET /api/zones/{zone_id} endpoint

**Database Status:**
- ✅ 3 zones loaded (IDs: 5, 6, 7)
- ✅ Total area: 1.00 hectare
- ⏳ No health data yet (awaiting satellite processing)
- ⏳ No alerts yet (awaiting processing)

---

## Next Steps

### Immediate (Ready to Deploy)

1. **Deploy updated API to NAS:**
   ```bash
   # Copy updated main.py to NAS
   scp backend/app/main.py daniele@NAS_Irisgatan:/volume1/docker/olive-monitoring/backend/app/

   # Restart API container
   ssh daniele@NAS_Irisgatan
   cd /volume1/docker/olive-monitoring
   docker-compose restart api

   # Test new endpoint
   curl http://localhost:8001/api/zones/5
   ```

2. **Test Copernicus access:**
   - Verify Copernicus Data Space credentials in .env
   - Test querying Sentinel-2 data for farm coordinates
   - Check available imagery dates

### Phase 2 Implementation (Next Major Task)

**Task 9: Satellite Image Processor** (Week 3)
- Create `backend/app/image_processor.py`
- Extract Red, NIR, SWIR bands from Sentinel-2 products
- Calculate NDVI/NDMI for each zone
- Store results in database

**Task 10: Alert Detection System** (Week 3)
- Create `backend/app/alerts.py`
- Implement threshold-based alerts (NDVI drop, NDMI drought)
- Generate email notifications
- Store alerts in database

**Task 11: Baseline Statistics** (Week 3)
- Create `backend/app/baseline.py`
- Calculate seasonal baselines from historical data
- Enable anomaly detection

**Task 12: Main Processing Script** (Week 4)
- Create `backend/scripts/process_satellite_data.py`
- Orchestrate: query → download → process → analyze → alert
- Schedule to run every 5 days

### Phase 3 Dashboard (Weeks 5-6)

- Initialize React application
- Create Leaflet map component with zone overlays
- Create Chart.js time-series health charts
- Build alert viewer interface
- Add farm story page for customer transparency

---

## Configuration Files

### Environment Variables (.env)

```bash
# Database
DB_PASSWORD=your_secure_password

# Copernicus Data Space
COPERNICUS_USERNAME=your_copernicus_username
COPERNICUS_PASSWORD=your_copernicus_password

# Email Alerts (Optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
ALERT_EMAIL=your_email@gmail.com
```

### Field Zones (backend/config/field_zones.json)

Contains 3 real olive grove zones with GeoJSON polygons and calculated areas.

---

## Useful Commands

### Local Development

```bash
cd /Users/danieletatasciore/Documents/repos/claude/olive-monitoring

# Parse KML file
python3 backend/scripts/parse_kml_zones.py

# Run tests
cd backend
python3 -m pytest tests/ -v
```

### NAS Management (via SSH)

```bash
# SSH into NAS
ssh daniele@NAS_Irisgatan

# Navigate to project
cd /volume1/docker/olive-monitoring

# Container management
docker-compose ps                    # Check status
docker-compose logs api              # View API logs
docker-compose logs processor        # View processor logs
docker-compose restart api           # Restart API
docker-compose up -d                 # Start all containers

# Load field zones into database
docker-compose exec -T processor python scripts/load_field_zones.py

# Database access
docker-compose exec postgres psql -U olive_user -d olive_monitoring

# Test API
curl http://localhost:8001/health
curl http://localhost:8001/api/zones
```

---

## Design Documents

- **Design Document:** `/Users/danieletatasciore/Documents/repos/claude/03 - RegenAg/2025-11-04-olive-farm-satellite-monitoring-design.md`
- **Implementation Plan:** `/Users/danieletatasciore/Documents/repos/claude/docs/plans/2025-11-04-olive-farm-satellite-monitoring.md`

---

## Git Repository

**Location:** /Users/danieletatasciore/Documents/repos/claude/olive-monitoring
**Branch:** main
**Remote:** origin (GitHub)

**Recent Commits:**
- `24babfb` - fix: Make load_field_zones.py handle config without location key
- `0763f0f` - refactor: Move scripts and config into backend folder for Docker access
- `3bfbf26` - fix: Make load_field_zones.py work inside Docker container
- `7e23558` - feat: Add real olive grove zones from KML file

---

## Resources

- **Copernicus Data Space:** https://dataspace.copernicus.eu/
- **Sentinel-2 Documentation:** https://sentinels.copernicus.eu/web/sentinel/missions/sentinel-2
- **FastAPI Docs:** https://fastapi.tiangolo.com/
- **Leaflet Maps:** https://leafletjs.com/

---

*This context file is updated at the end of each coding session to maintain continuity.*
