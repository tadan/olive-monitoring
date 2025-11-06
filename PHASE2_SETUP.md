# Phase 2 Setup Guide - Analysis Engine

**Status:** Implementation Complete ✅ | Testing Pending ⏳

This guide covers the deployment and testing of Phase 2, which adds satellite data processing, health analysis, and alert generation.

---

## What's New in Phase 2

### Core Functionality

1. **Image Processor** (`app/image_processor.py`)
   - Extracts Red, NIR, SWIR bands from Sentinel-2 products
   - Clips imagery to zone boundaries
   - Calculates NDVI and NDMI vegetation indices
   - Computes health scores and statistics
   - Stores results in database

2. **Alert System** (`app/alerts.py`)
   - NDVI drop detection (vegetation loss)
   - Drought stress detection (low moisture)
   - Waterlogging detection (excessive moisture)
   - Health score monitoring
   - Email notifications with HTML formatting

3. **Baseline Manager** (`app/baseline.py`)
   - Seasonal baseline calculation (spring/summer/fall/winter)
   - Overall baseline across all seasons
   - Anomaly detection (2σ threshold)
   - Automatic baseline updates

4. **Main Orchestrator** (`scripts/process_satellite_data.py`)
   - Queries new Sentinel-2 products from Copernicus
   - Downloads products
   - Processes all zones
   - Detects and stores alerts
   - Updates baselines
   - Sends email notifications
   - Comprehensive logging

---

## Prerequisites

Before deploying Phase 2, ensure Phase 1 is complete:

- [x] Docker containers running (postgres, processor, api)
- [x] Database initialized with schema
- [x] Field zones loaded (3 zones)
- [x] API responding on port 8001
- [ ] Copernicus Data Space account created
- [ ] Copernicus credentials configured in .env

---

## Step 1: Register for Copernicus Data Space

1. Go to https://dataspace.copernicus.eu/
2. Click "Register" and create a free account
3. Verify your email address
4. Log in and note your credentials

**Important:** The new Copernicus Data Space replaced the old SciHub system. Make sure you're using the new platform.

---

## Step 2: Configure Credentials

### On Your NAS

SSH into your NAS and edit the `.env` file:

```bash
ssh daniele@NAS_Irisgatan
cd /volume1/docker/olive-monitoring
nano .env
```

Add these lines (replace with your actual credentials):

```bash
# Copernicus Data Space credentials
COPERNICUS_USERNAME=your_email@example.com
COPERNICUS_PASSWORD=your_password

# Email notifications (optional but recommended)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
ALERT_EMAIL=your_email@gmail.com
```

**For Gmail:** You'll need to use an "App Password" instead of your regular password:
1. Go to Google Account → Security → 2-Step Verification → App passwords
2. Generate a new app password for "Mail"
3. Use that 16-character password in SMTP_PASSWORD

Save and exit (`Ctrl+X`, then `Y`, then `Enter`).

---

## Step 3: Deploy Phase 2 Code

### Option A: Copy Files Directly (Recommended for Testing)

From your local machine:

```bash
# Navigate to project root
cd /Users/danieletatasciore/Documents/repos/claude/olive-monitoring

# Copy Phase 2 files to NAS
scp backend/app/image_processor.py daniele@NAS_Irisgatan:/volume1/docker/olive-monitoring/backend/app/
scp backend/app/alerts.py daniele@NAS_Irisgatan:/volume1/docker/olive-monitoring/backend/app/
scp backend/app/baseline.py daniele@NAS_Irisgatan:/volume1/docker/olive-monitoring/backend/app/
scp backend/scripts/process_satellite_data.py daniele@NAS_Irisgatan:/volume1/docker/olive-monitoring/backend/scripts/
scp backend/scripts/test_copernicus_access.py daniele@NAS_Irisgatan:/volume1/docker/olive-monitoring/backend/scripts/
```

### Option B: Git Pull (After Committing Changes)

```bash
ssh daniele@NAS_Irisgatan
cd /volume1/docker/olive-monitoring
git pull origin main
```

---

## Step 4: Restart Processor Container

The processor container needs to be restarted to load the new `.env` variables:

```bash
ssh daniele@NAS_Irisgatan
cd /volume1/docker/olive-monitoring
docker-compose restart processor

# Verify it's running
docker-compose ps
```

---

## Step 5: Test Copernicus Access

Before running the full pipeline, test that everything is configured correctly:

```bash
ssh daniele@NAS_Irisgatan
cd /volume1/docker/olive-monitoring

# Run test script inside processor container
docker-compose exec processor python scripts/test_copernicus_access.py
```

**Expected output:**
```
✅ Username: your_email@example.com
✅ Password: ***configured***
✅ Database connected
✅ Found 3 zones
✅ Successfully connected to Copernicus Data Space API
✅ Found XX Sentinel-2 products!

🎉 All tests passed! System is ready for satellite data processing.
```

**If tests fail:**
- Check credentials in `.env`
- Verify Copernicus account is activated
- Ensure processor container restarted after `.env` changes

---

## Step 6: Run Initial Processing

### First Run (Manual Execution)

Process the last 30 days to build initial baselines:

```bash
ssh daniele@NAS_Irisgatan
cd /volume1/docker/olive-monitoring

# Run processing script with extended history
docker-compose exec processor python scripts/process_satellite_data.py --days-back 30 --cloud-coverage-max 40
```

This will:
1. Query Sentinel-2 products for the last 30 days
2. Download cloud-free imagery (< 40% cloud coverage)
3. Process all 3 zones
4. Calculate NDVI, NDMI, health scores
5. Detect any anomalies
6. Generate initial baselines
7. Send alert emails (if configured)

**Expected duration:** 10-30 minutes depending on number of products and download speeds.

---

## Step 7: Verify Results

### Check Database

```bash
# View processed images
docker-compose exec postgres psql -U olive_user -d olive_monitoring -c "SELECT id, acquisition_date, cloud_coverage_percent, processed FROM satellite_images ORDER BY acquisition_date DESC;"

# View health indices
docker-compose exec postgres psql -U olive_user -d olive_monitoring -c "SELECT zone_id, acquisition_date, vegetation_health_score, ndvi_mean, ndmi_mean FROM health_indices ORDER BY acquisition_date DESC LIMIT 10;"

# View alerts
docker-compose exec postgres psql -U olive_user -d olive_monitoring -c "SELECT zone_id, alert_type, severity, title, detected_at FROM alerts ORDER BY detected_at DESC LIMIT 10;"

# View baselines
docker-compose exec postgres psql -U olive_user -d olive_monitoring -c "SELECT zone_id, metric, season, mean_value, std_dev, sample_count FROM baseline_statistics ORDER BY zone_id, metric, season;"
```

### Check API

```bash
# Get zone health history
curl http://localhost:8001/api/zones/5/health | jq

# Get dashboard summary
curl http://localhost:8001/api/dashboard/summary | jq

# Get alerts
curl http://localhost:8001/api/zones/5/alerts | jq
```

### Check Logs

```bash
# View processing logs
docker-compose exec processor tail -f /app/data/processing.log

# Or view all logs
docker-compose exec processor cat /app/data/processing.log
```

---

## Step 8: Schedule Regular Processing

### Option A: Manual Cron Job on NAS

Edit crontab on NAS:

```bash
ssh daniele@NAS_Irisgatan
crontab -e
```

Add this line to run every 5 days at 2 AM:

```bash
0 2 */5 * * cd /volume1/docker/olive-monitoring && docker-compose exec -T processor python scripts/process_satellite_data.py --days-back 7 >> /volume1/docker/olive-monitoring/cron.log 2>&1
```

### Option B: Docker Container Scheduling (Future Enhancement)

Modify `docker-compose.yml` to use a scheduler inside the processor container:

```yaml
processor:
  command: sh -c "python scripts/schedule_processing.py"  # Run scheduler loop
```

Would require creating `schedule_processing.py` with:
```python
import schedule
import time

def run_processing():
    # Run process_satellite_data.py
    pass

schedule.every(5).days.at("02:00").do(run_processing)

while True:
    schedule.run_pending()
    time.sleep(3600)  # Check every hour
```

---

## Monitoring & Maintenance

### View Processing Status

```bash
# Check recent processing runs
docker-compose exec processor tail -n 100 /app/data/processing.log | grep "Processing Summary"

# Check for errors
docker-compose exec processor grep ERROR /app/data/processing.log | tail -20
```

### Manual Reprocessing

If you need to reprocess specific dates:

```bash
# Process last week with strict cloud coverage
docker-compose exec processor python scripts/process_satellite_data.py --days-back 7 --cloud-coverage-max 20

# Process last 60 days (no notifications)
docker-compose exec processor python scripts/process_satellite_data.py --days-back 60 --no-notifications
```

### Update Baselines

Baselines are automatically updated when new data is processed. To force a baseline update:

```python
# Inside processor container
docker-compose exec processor python

from app.database import get_db
from app.baseline import update_baselines_for_all_zones

db = next(get_db())
count = update_baselines_for_all_zones(db)
print(f"Updated {count} baselines")
db.close()
```

---

## Troubleshooting

### Issue: "No products found"

**Causes:**
- High cloud coverage in recent days
- Sentinel-2 orbit schedule
- Too short search period

**Solutions:**
```bash
# Try longer period with relaxed cloud coverage
docker-compose exec processor python scripts/process_satellite_data.py --days-back 30 --cloud-coverage-max 50
```

### Issue: "Failed to download product"

**Causes:**
- Network issues
- Copernicus server overload
- Large file sizes

**Solutions:**
- Retry the processing script (it will skip already-downloaded products)
- Check NAS disk space: `df -h`
- Check network connectivity

### Issue: "Band not found in product"

**Causes:**
- Incomplete product download
- Wrong Sentinel-2 product level (L1C vs L2A)

**Solutions:**
- Delete corrupted products: `rm -rf /volume1/docker/olive-monitoring/data/raw/S2*.SAFE`
- Re-run processing script

### Issue: "No email notifications received"

**Checks:**
1. SMTP credentials configured in `.env`?
2. Gmail app password (not regular password)?
3. Any alerts actually detected? Check: `SELECT * FROM alerts;`
4. Check logs for email errors: `grep "email" /app/data/processing.log`

---

## Performance & Costs

### Data Download Sizes
- Sentinel-2 product: ~800MB-1.5GB per scene
- 3 bands extracted: ~50-100MB per zone per scene
- Expected storage: ~5GB per month of imagery

### Processing Time
- Query products: 5-10 seconds
- Download product: 5-15 minutes (depends on network)
- Process 3 zones: 2-5 minutes
- Total: ~20-30 minutes per new satellite pass

### Costs
- Copernicus data: **FREE**
- Sentinel-2 imagery: **FREE**
- Email notifications via Gmail: **FREE** (up to Gmail limits)
- **Total cost: $0** (just electricity for NAS)

---

## Next Steps: Phase 3

Once Phase 2 is running successfully:

1. **Dashboard Development**
   - React application with interactive map
   - Time-series charts for NDVI/NDMI
   - Alert viewer and management
   - Farm story page for customer transparency

2. **Advanced Analytics**
   - Machine learning anomaly detection
   - Yield prediction models
   - Disease detection from spectral signatures
   - Comparison with weather data

3. **Mobile Notifications**
   - Push notifications via Telegram/WhatsApp
   - SMS alerts for critical issues
   - Mobile-responsive dashboard

---

## Files Created in Phase 2

| File | Purpose | LOC |
|------|---------|-----|
| `app/image_processor.py` | Satellite band extraction & processing | ~320 |
| `app/alerts.py` | Alert detection & email notifications | ~380 |
| `app/baseline.py` | Baseline statistics & anomaly detection | ~280 |
| `scripts/process_satellite_data.py` | Main orchestration pipeline | ~380 |
| `scripts/test_copernicus_access.py` | Credentials & access testing | ~250 |
| **Total** | | **~1,610 lines** |

---

## Support & Questions

**Issues:** Report bugs or ask questions on the GitHub repository

**Logs:** Always include processing logs when reporting issues:
```bash
docker-compose exec processor tail -500 /app/data/processing.log > logs.txt
```

**Contact:** daniele@example.com (update with your actual email)

---

*Last updated: 2025-11-06*
*Phase 2 implementation: Complete ✅*
*Phase 2 testing: Pending ⏳*
