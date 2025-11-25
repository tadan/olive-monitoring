# Olive Farm Satellite Monitoring - Claude Code Context

**Project:** Satellite-based monitoring system for Tatasciore Olive Farm (Abruzzo, Italy)
**Status:** Phase 1 Complete ✅ | Phase 2 Complete ✅ | Phase 3 Complete ✅ | Historical Analysis ✅
**Last Updated:** 2025-11-25
**Location:** /Users/danieletatasciore/Documents/repos/claude/olive-monitoring
**Live Dashboard:** https://farms.daniele.is

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

**Docker Containers (4):**
- `olive-monitoring-db` - PostgreSQL 15 (port 5432 internal only)
- `olive-monitoring-processor` - Python 3.11 + GDAL for satellite processing
- `olive-monitoring-api` - FastAPI REST API (internal only)
- `olive-monitoring-dashboard` - nginx serving React frontend (port 8080 → Cloudflare Tunnel)

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

**Frontend:**
- React 18 + Vite
- Leaflet (interactive maps)
- Chart.js (time-series visualization)
- Tailwind CSS (styling)
- Deployed via nginx reverse proxy
- Publicly accessible via Cloudflare Tunnel

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

### ✅ Phase 2: Analysis Engine (COMPLETE)

**Completed Components:**
1. `backend/app/image_processor.py` - Sentinel-2 band extraction and processing
2. `backend/app/alerts.py` - Anomaly detection and alert generation
3. `backend/scripts/process_satellite_data.py` - Main processing orchestration
4. Band resolution resampling (SWIR 20m → 10m)
5. Historical data comparison capability
6. NDVI/NDMI calculation and storage

**Key Features:**
- Automatic tile selection using zone centroids
- Multi-band processing with resolution normalization
- Health score calculation (0-100)
- Alert generation based on thresholds
- Historical comparison (e.g., July 2015 vs July 2025)

### ✅ Phase 3: Dashboard (COMPLETE)

**Completed Components:**
1. React 18 + Vite application setup
2. Interactive Leaflet map with zone overlays (color-coded by health)
3. Chart.js time-series health charts (NDVI, NDMI, Health Score)
4. Alert viewer interface with severity badges
5. Responsive dashboard layout
6. nginx reverse proxy for API routing
7. Cloudflare Tunnel integration for public access

**Files Created:**
- `frontend/src/components/Dashboard.jsx` - Main dashboard component
- `frontend/src/components/FarmMap.jsx` - Leaflet map with zone visualization
- `frontend/src/components/HealthChart.jsx` - Chart.js time-series visualization
- `frontend/src/components/AlertViewer.jsx` - Alert display component
- `frontend/src/services/api.js` - API client with relative URL support
- `docker/nginx.conf` - nginx reverse proxy configuration
- `frontend/.env.production` - Production environment configuration

---

## API Endpoints

### Public Access (via nginx reverse proxy)

```bash
GET https://farms.daniele.is/              # Dashboard UI
GET https://farms.daniele.is/health        # Health check
GET https://farms.daniele.is/api/zones     # List all field zones
GET https://farms.daniele.is/api/zones/{zone_id}          # Get specific zone details
GET https://farms.daniele.is/api/zones/{zone_id}/health   # Zone health history (recent)
GET https://farms.daniele.is/api/zones/{zone_id}/history  # Historical health data (year-over-year)
GET https://farms.daniele.is/api/zones/{zone_id}/alerts   # Zone alerts
GET https://farms.daniele.is/api/dashboard/summary        # Dashboard summary
```

### Internal Access (NAS only)

```bash
# On NAS via SSH
curl http://localhost:8080/health                    # Through nginx
curl http://localhost:8080/api/zones                 # Through nginx
curl http://localhost:8000/health                    # Direct to API (internal network only)
```

### Architecture Notes

- nginx (port 8080) serves React frontend and proxies `/api/*` requests to FastAPI backend
- FastAPI backend (port 8000) is internal only, not exposed externally
- Cloudflare Tunnel exposes nginx on port 8080 as https://farms.daniele.is
- Database (port 5432) is internal only, no external access

---

## Recent Sessions

### Session 2025-11-25: Historical Health Analysis Feature

**Accomplishments:**
1. ✅ Reviewed and enhanced user's `backend/app/analyse_history.py` script
2. ✅ Created new API endpoint `GET /api/zones/{zone_id}/history` with configurable date ranges
3. ✅ Built HistoricalChart component with bar chart visualization and trend indicators
4. ✅ Integrated historical analysis into Dashboard (loads in parallel with zone data)
5. ✅ Deployed backend to production NAS and restarted API service
6. ✅ Ran historical data processing script - downloaded September satellite data (2015-2025)
7. ⏳ Frontend rebuild in progress on NAS (`npm run build`)

**Feature Implemented:**
- **Historical Health Analysis** for year-over-year comparison (2015-2025)
- Default target: mid-September (Sept 10-25) - optimal harvest assessment period
- Configurable time windows via API query parameters
- Trend calculation: Improving (↗️), Stable (➡️), Declining (↘️), Baseline (⏺️)
- Color-coded bar chart: Green (improving), Yellow (stable), Red (declining), Blue (baseline)
- Detailed tooltips with health score, NDVI, NDMI, and acquisition date

**API Endpoint:**
```
GET /api/zones/{zone_id}/history
Query params: start_year, end_year, month, day_start, day_end
Returns: Year-over-year health data with trend indicators
```

**Files Modified:**
- `backend/app/analyse_history.py` - Enhanced with flexible parameters
- `backend/app/main.py` - Added history endpoint, added `extract` import from SQLAlchemy
- `frontend/src/components/HistoricalChart.jsx` - New component (bar chart)
- `frontend/src/components/HistoricalChart.css` - New styling
- `frontend/src/components/Dashboard.jsx` - Integrated historical chart
- `frontend/src/components/Dashboard.css` - Added historical-section styling
- `frontend/src/services/api.js` - Added getZoneHistory() function

**Git Commit:** `aaf12e9` feat: Add historical health analysis for mid-September data (2015-2025)

**Issues Encountered:**

1. **"Zone not found" API Error:**
   - Problem: API endpoint returned 404 after deployment
   - Root Cause: API container hadn't loaded new endpoint code
   - Solution: Restarted API container with `docker-compose restart api`

2. **Wrong Docker Path for Script:**
   - Problem: `docker-compose exec processor python backend/app/analyse_history.py` failed
   - Root Cause: In container, files are at `/app/app/` not `/app/backend/app/`
   - Solution: Correct command is `python app/analyse_history.py`

3. **Frontend Not Updating:**
   - Problem: User reported historical chart not appearing
   - Root Cause: Frontend hadn't been rebuilt after code changes
   - Solution: Running `npm run build` in frontend directory, then restart dashboard

**Next Steps:**
- Complete frontend rebuild and verify historical chart displays
- Check map zone color overlays are working properly
- Test historical chart with all 3 zones
- Verify trend indicators display correctly

**Historical Data Status:**
- Downloaded and processed September satellite imagery for years 2015-2025
- ~8-10 images processed (~3-5 GB of data)
- Health indices calculated for all 3 zones for each year
- Data now available via `/api/zones/{zone_id}/history` endpoint

---

### Session 2025-11-17: Dashboard Update Issue & Privacy Enhancement

**Accomplishments:**
1. ✅ Diagnosed Task Scheduler failure (status 127 - command not found)
2. ✅ Identified root cause: docker-compose not in PATH for Synology Task Scheduler
3. ✅ Provided solution: use full path `/usr/local/bin/docker-compose` in scheduled task
4. ✅ Manually processed 3 new satellite images (Nov 12, 14, 15 - 3.1 GB total)
5. ✅ Dashboard updated with fresh data - 10 new alerts generated
6. ✅ Enhanced privacy: changed map to show Abruzzo region instead of farm location
7. ✅ Committed and pushed map privacy changes to GitHub

**Issues Resolved:**

1. **Task Scheduler Status 127 Error:**
   - Problem: Synology Task Scheduler job failed immediately with "command not found"
   - Root Cause: `docker-compose` not in PATH when Task Scheduler runs (minimal environment)
   - Solution: Use full path `/usr/local/bin/docker-compose` in scheduled task script
   - Files: Synology Task Scheduler configuration (updated by user on NAS)

2. **Dashboard Privacy Enhancement:**
   - Problem: Map displayed exact farm location with visible landmarks
   - Solution: Changed map center to Abruzzo region (42.35°N, 13.39°E) with zoom level 9
   - Files: `frontend/src/components/FarmMap.jsx`

**Processing Results:**
- Products found: 4 (1 already processed, 3 new)
- Downloaded: 3 new Sentinel-2 images (~3.1 GB)
- Zones processed: 9 (3 zones × 3 images)
- Alerts generated: 10 new alerts
- Baselines updated: 12
- Duration: 6 minutes 18 seconds

**Current Grove Health Status (as of 2025-11-15):**
- Zone 2 (Below Natural): 58/100 - Warning (Waterlogging alert, NDMI: 0.563)
- Zone 3 (Below Falling Houses): 57/100 - Warning (Low health)
- Zone 4 (House): 50/100 - Warning (Low health)

**Files Modified:**
- `frontend/src/components/FarmMap.jsx` - Changed map to regional view for privacy
- `SESSION-2025-11-17.md` - Created comprehensive session log
- `Claude.md` - Updated with this session

**Next Steps:**
- User to update Synology Task Scheduler with corrected script (full path to docker-compose)
- User to deploy updated frontend with privacy-enhanced map to NAS
- Verify automated processing runs successfully on next scheduled execution

### Session 2025-11-11: Phase 2 & 3 Complete - Dashboard Live! 🎉

**Accomplishments:**
1. ✅ Fixed tile selection issue (Polygon → Point geometry using zone centroid)
2. ✅ Fixed band resolution mismatch (resampled SWIR 20m → 10m)
3. ✅ Implemented satellite data processing pipeline
4. ✅ Built complete React dashboard with Leaflet maps and Chart.js
5. ✅ Deployed frontend with nginx reverse proxy
6. ✅ Configured Cloudflare Tunnel for public access
7. ✅ Fixed database password authentication issue
8. ✅ **Dashboard is now live at https://farms.daniele.is**

**Issues Resolved:**

1. **Tile Selection Error:**
   - Problem: Polygon geometry with Intersects operator returned wrong tile (T33TVG instead of correct tile)
   - Root Cause: Adjacent tiles were matching the query
   - Solution: Changed to Point geometry using zone centroid (frontend/src/components/FarmMap.jsx:712)
   - Files: `backend/scripts/process_satellite_data.py`, `backend/scripts/test_copernicus_access.py`

2. **Band Resolution Mismatch:**
   - Problem: `operands could not be broadcast together with shapes (21,13) (11,7)`
   - Root Cause: SWIR band at 20m resolution, Red/NIR at 10m resolution
   - Solution: Resampled SWIR band to 10m using rasterio.warp.reproject with bilinear interpolation
   - Files: `backend/app/image_processor.py:110-229`

3. **Frontend API Connection:**
   - Problem: Production build was using localhost:8001 instead of relative URLs
   - Root Cause: JavaScript `||` operator treats empty string as falsy
   - Solution: Changed to explicit `undefined` check in API client
   - Files: `frontend/src/services/api.js:7-10`

4. **Database Authentication:**
   - Problem: Password authentication failed, API returning 500 errors
   - Root Cause: Database password contained special characters (`&`, `@`) that broke connection URL parsing
   - Solution: Changed to password without special URL characters
   - Files: `.env` on NAS

**Key Decisions:**
- Used nginx reverse proxy to eliminate CORS issues and simplify deployment
- Frontend uses relative URLs in production (empty VITE_API_URL)
- Cloudflare Tunnel points to nginx on port 8080 (not directly to API)
- All database ports kept internal for security

**Architecture Changes:**
- Added `olive-monitoring-dashboard` container (nginx:alpine)
- Created `docker/nginx.conf` for frontend serving and API proxying
- Removed direct API port exposure (8001) - nginx handles all traffic
- API now runs on internal port 8000, only accessible via nginx proxy

**Files Modified:**
- `backend/scripts/process_satellite_data.py` - Fixed tile selection, notification naming
- `backend/app/image_processor.py` - Added SWIR band resampling
- `frontend/src/services/api.js` - Fixed API URL fallback logic
- `docker-compose.yml` - Added dashboard service, updated API port
- `docker/nginx.conf` - Created nginx reverse proxy configuration
- `/volume1/docker/cloudflared/config.yml` - Added farms.daniele.is hostname

**Database Status:**
- ✅ 3 zones loaded (IDs: 5, 6, 7)
- ✅ Historical health data processed (July 2015 comparison complete)
- ✅ Dashboard displaying real satellite data
- ✅ Publicly accessible at https://farms.daniele.is

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

### Operations & Maintenance

1. **Automated Processing Schedule:**
   - Set up cron job to run satellite processing every 5 days
   - Monitor processing logs for errors
   - Verify data is being updated regularly

2. **Monitoring & Alerts:**
   - Configure email alerts for health threshold violations
   - Set up monitoring for Docker container health
   - Create backup schedule for PostgreSQL database

3. **Content Enhancement:**
   - Add farm story page to dashboard (About section)
   - Document olive varieties and farming practices
   - Add seasonal calendar for Swedish customers

### Future Enhancements

**Short-term:**
- Add data export functionality (CSV download)
- Implement date range selector for historical data
- Add comparison view (year-over-year)
- Create mobile-responsive design improvements

**Medium-term:**
- Implement baseline statistics for anomaly detection
- Add predictive analytics for harvest timing
- Create automated email reports for significant changes
- Add weather data integration (temperature, rainfall)

**Long-term:**
- Multi-farm support (if expanding to other locations)
- Machine learning for pest/disease detection
- Integration with farm management system
- Public API for data access

---

## Configuration Files

### Environment Variables (.env)

```bash
# Database
# IMPORTANT: Avoid special characters (@, &, :, /, ?, #, [, ]) in password
# These characters break PostgreSQL connection URL parsing
DB_PASSWORD=YourSecurePassword2025

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

**Security Notes:**
- Database password must not contain URL-special characters
- Never commit `.env` file to git (already in `.gitignore`)
- Store Copernicus credentials securely
- Use app-specific password for Gmail SMTP

### Field Zones (backend/config/field_zones.json)

Contains 3 real olive grove zones with GeoJSON polygons and calculated areas.

---

## Useful Commands

### Local Development

```bash
cd /Users/danieletatasciore/Documents/repos/claude/olive-monitoring

# Frontend development
cd frontend
npm install
npm run dev              # Start dev server (http://localhost:5173)
npm run build            # Build for production

# Backend development
cd backend
python3 -m pytest tests/ -v          # Run tests
python3 backend/scripts/parse_kml_zones.py   # Parse KML file

# Deploy frontend to NAS
rsync -av frontend/dist/ daniele@192.168.1.112:/volume1/docker/olive-monitoring/frontend/dist/
```

### NAS Management (via SSH)

```bash
# SSH into NAS
ssh daniele@NAS_Irisgatan

# Navigate to project
cd /volume1/docker/olive-monitoring

# Container management
docker-compose ps                              # Check status
docker-compose logs dashboard                  # View nginx logs
docker-compose logs api                        # View API logs
docker-compose logs processor                  # View processor logs
docker-compose restart dashboard               # Restart nginx
docker-compose restart api                     # Restart API
docker-compose down && docker-compose up -d    # Recreate all containers

# Database operations
docker-compose exec -T processor python scripts/load_field_zones.py    # Load zones
docker-compose exec postgres psql -U olive_user -d olive_monitoring    # Database shell

# Test endpoints
curl http://localhost:8080/health              # Test through nginx
curl http://localhost:8080/api/zones           # Test API through nginx
curl https://farms.daniele.is/health           # Test public endpoint

# Process satellite data
docker-compose exec processor python scripts/process_satellite_data.py

# Database reset (if needed)
docker-compose down
docker volume rm olive-monitoring_postgres-data
# Edit .env to set new DB_PASSWORD
docker-compose up -d
docker-compose exec -T processor python scripts/load_field_zones.py
```

### Cloudflare Tunnel Management

```bash
# Check tunnel status
sudo systemctl status cloudflared

# View tunnel logs
sudo journalctl -u cloudflared -n 50 --no-pager

# Restart tunnel
sudo systemctl restart cloudflared

# Edit tunnel configuration (MUST use spaces, NOT tabs)
sudo nano /volume1/docker/cloudflared/config.yml
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
