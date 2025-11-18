# Deployment Guide - Olive Farm Satellite Monitoring

## Prerequisites Checklist

- ✅ Synology DS716+II NAS with 8GB RAM (in Sweden)
- ✅ Docker and Docker Compose installed on NAS
- ✅ Cloudflare tunnel configured (`cloudflared` systemd service)
- ✅ Copernicus Data Space account (username: work@daniele.is)
- ✅ Olive grove boundaries defined (3 zones in Abruzzo, Italy)
- ✅ `.env` file configured with credentials (see password requirements below)
- ✅ Node.js and npm installed locally (for frontend development)

## Important: Database Password Requirements

**CRITICAL:** The database password in `.env` must not contain URL-special characters:
- ❌ Avoid: `@`, `&`, `:`, `/`, `?`, `#`, `[`, `]`
- ✅ Use: Letters, numbers, underscores, hyphens
- Example: `OliveMonitoring2025` or `Secure_Password_2025`

**Why:** These characters break PostgreSQL connection URL parsing and cause authentication failures.

## Deployment Steps

### 1. Transfer Project to NAS

```bash
# From your local machine
cd /Users/danieletatasciore/Documents/repos/claude
scp -r olive-monitoring your_nas_user@your_nas_ip:/volume1/docker/
```

### 2. SSH into NAS

```bash
ssh your_nas_user@your_nas_ip
cd /volume1/docker/olive-monitoring
```

### 3. Verify Configuration

```bash
# Check .env file exists and has credentials
cat .env | grep -v PASSWORD

# Check field zones configuration
cat config/field_zones.json | grep "name"

# Verify Docker Compose configuration
docker-compose config
```

Expected: Valid YAML output with no errors

### 4. Build Docker Images

```bash
docker-compose build
```

Expected output:
- Successfully built processor image (~5-10 min due to GDAL)
- Successfully built api image (~2-3 min)
- postgres:15-alpine pulled

**Note:** Processor image is large (~1.5GB) due to GDAL geospatial libraries.

### 5. Start Containers

```bash
docker-compose up -d
```

Expected: All 4 containers start successfully
- `olive-monitoring-db` (PostgreSQL)
- `olive-monitoring-processor` (Python satellite processor)
- `olive-monitoring-api` (FastAPI backend)
- `olive-monitoring-dashboard` (nginx serving React frontend)

### 6. Verify Containers

```bash
docker-compose ps
```

Expected output:
```
NAME                          STATUS    PORTS
olive-monitoring-db           Up        (internal only)
olive-monitoring-processor    Up
olive-monitoring-api          Up        8000/tcp (internal only)
olive-monitoring-dashboard    Up        0.0.0.0:8080->80/tcp
```

**Architecture Notes:**
- PostgreSQL (port 5432) is internal only - no external access
- API (port 8000) is internal only - accessed via nginx proxy
- nginx (port 8080) serves frontend and proxies `/api/*` to backend
- Cloudflare Tunnel exposes nginx port 8080 as https://farms.daniele.is
- All external traffic goes through nginx → API is never directly exposed

### 7. Check Database Initialization

```bash
docker-compose exec postgres psql -U olive_user -d olive_monitoring -c "\dt"
```

Expected: 5 tables listed
- field_zones
- satellite_images
- health_indices
- alerts
- baseline_statistics

```bash
docker-compose exec postgres psql -U olive_user -d olive_monitoring -c "SELECT COUNT(*) FROM field_zones;"
```

Expected: count = 1 (default placeholder zone from init script)

### 8. Run Tests Inside Processor Container

```bash
docker-compose exec processor python -m pytest tests/ -v
```

Expected: All tests pass
- test_config.py: 3 tests ✓
- test_database.py: 6 tests ✓
- test_satellite_fetcher.py: 4 tests ✓
- test_vegetation_indices.py: 5 tests ✓

**Total: 18 tests should pass**

### 9. Build and Deploy Frontend

The frontend must be built locally and deployed to the NAS:

```bash
# On your local machine
cd /Users/danieletatasciore/Documents/repos/claude/olive-monitoring/frontend

# Install dependencies (first time only)
npm install

# Build for production
npm run build

# Deploy to NAS
rsync -av dist/ daniele@192.168.1.112:/volume1/docker/olive-monitoring/frontend/dist/

# Restart dashboard container on NAS
ssh daniele@192.168.1.112
cd /volume1/docker/olive-monitoring
docker-compose restart dashboard
```

Expected: `dist/` folder copied to NAS, nginx serving React app

### 10. Configure Cloudflare Tunnel

Edit the Cloudflare tunnel configuration on your NAS:

```bash
# SSH into NAS
ssh daniele@192.168.1.112

# Edit tunnel config (MUST use spaces, NOT tabs!)
sudo nano /volume1/docker/cloudflared/config.yml
```

Add your hostname:
```yaml
ingress:
  - hostname: "farms.daniele.is"
    service: "http://localhost:8080"
    originRequest:
      noTLSVerify: true
  - service: "http_status:404"
```

**IMPORTANT:** YAML requires spaces for indentation, never tabs. Use 2 spaces per level.

Restart the tunnel:
```bash
sudo systemctl restart cloudflared
sudo systemctl status cloudflared
```

Expected: Service running without errors, farms.daniele.is accessible

### 11. Test API Access

```bash
# Test nginx (internal)
curl http://localhost:8080/health

# Test API through nginx (internal)
curl http://localhost:8080/api/zones

# Test via Cloudflare tunnel (from anywhere)
curl https://farms.daniele.is/health
curl https://farms.daniele.is/api/zones
```

Expected: JSON responses from all endpoints

### 12. View Logs

```bash
# View all logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View specific service
docker-compose logs processor
docker-compose logs api
docker-compose logs postgres
```

## Troubleshooting

### Database Password Authentication Fails

**Symptom:** API returns 500 errors, logs show `password authentication failed for user "olive_user"`

**Common Causes:**
1. Password contains URL-special characters (`@`, `&`, `:`, etc.)
2. Password mismatch between `.env` and database

**Solution:**
```bash
# Stop containers
docker-compose down

# Remove database volume
docker volume rm olive-monitoring_postgres-data

# Edit .env with password containing NO special characters
nano .env

# Start fresh
docker-compose up -d

# Reload field zones
docker-compose exec -T processor python scripts/load_field_zones.py
```

### Frontend Shows "localhost:8001" Errors

**Symptom:** Browser console shows connection refused to localhost:8001

**Cause:** Frontend was built with wrong environment configuration

**Solution:**
```bash
# Verify .env.production has empty VITE_API_URL
cat frontend/.env.production
# Should show: VITE_API_URL=

# Rebuild frontend
cd frontend
npm run build

# Redeploy
rsync -av dist/ daniele@192.168.1.112:/volume1/docker/olive-monitoring/frontend/dist/
ssh daniele@192.168.1.112 "cd /volume1/docker/olive-monitoring && docker-compose restart dashboard"
```

### Cloudflare Tunnel YAML Parsing Error

**Symptom:** `found a tab character that violates indentation`

**Cause:** YAML file contains tab characters instead of spaces

**Solution:**
```bash
# SSH into NAS
ssh daniele@192.168.1.112

# Convert tabs to spaces
sudo expand -t 2 /volume1/docker/cloudflared/config.yml > /tmp/config_fixed.yml
sudo mv /tmp/config_fixed.yml /volume1/docker/cloudflared/config.yml

# Or edit carefully ensuring spaces only
sudo nano /volume1/docker/cloudflared/config.yml

# Restart tunnel
sudo systemctl restart cloudflared
```

### Container Won't Start

```bash
# Check logs for errors
docker-compose logs <service_name>

# Restart specific service
docker-compose restart <service_name>

# Rebuild and restart
docker-compose down
docker-compose build --no-cache <service_name>
docker-compose up -d
```

### Database Connection Errors

```bash
# Check postgres is running
docker-compose ps postgres

# Check postgres logs
docker-compose logs postgres

# Verify credentials in .env
cat .env | grep DB_

# Test connection manually
docker-compose exec postgres psql -U olive_user -d olive_monitoring
```

### Python Dependencies Missing

```bash
# Rebuild processor with no cache
docker-compose build --no-cache processor

# Check requirements installation
docker-compose exec processor pip list | grep sentinel
```

**Note on Requirements Files:**
- **Processor**: Uses `requirements.txt` (includes GDAL, rasterio, geospatial libs)
- **API**: Uses `requirements-api.txt` (lightweight, no GDAL)
- API doesn't need GDAL since it only serves data from the database

### Disk Space Issues

```bash
# Check available space
df -h | grep volume1

# Clean up old images
docker system prune -a

# Remove unused volumes
docker volume prune
```

## Resource Monitoring

### Check Memory Usage

```bash
free -h
docker stats --no-stream
```

Expected usage:
- PostgreSQL: ~200-300MB
- Processor: ~500MB-1GB (when running)
- API: ~100-200MB
- **Total:** ~1-1.5GB (well within 8GB limit)

### Check CPU Usage

```bash
top
```

Expected: Low CPU usage when idle, spikes during satellite processing

### Check Disk Usage

```bash
# Check Docker volumes
docker system df

# Check satellite data directory
du -sh /volume1/docker/olive-monitoring/backend/data
```

Expected growth: ~5GB per year of satellite data

## Scheduled Processing

### Option 1: Synology Task Scheduler (Recommended)

1. Open Synology DSM Control Panel
2. Go to Task Scheduler
3. Create → Scheduled Task → User-defined script
4. Schedule: Every 5 days at 2:00 AM
5. Script:
```bash
cd /volume1/docker/olive-monitoring
docker-compose exec -T processor python scripts/process_satellite_data.py
```

### Option 2: Cron Inside Processor Container

```bash
# Enter processor container
docker-compose exec processor bash

# Add cron job
echo "0 2 */5 * * python /app/scripts/process_satellite_data.py" | crontab -
```

## Backup Strategy

### Database Backup

```bash
# Create backup
docker-compose exec postgres pg_dump -U olive_user olive_monitoring > backup_$(date +%Y%m%d).sql

# Restore from backup
docker-compose exec -T postgres psql -U olive_user -d olive_monitoring < backup_20251105.sql
```

### Configuration Backup

```bash
# Backup .env and config
tar -czf config_backup_$(date +%Y%m%d).tar.gz .env config/
```

## Updating the Application

```bash
# 1. Pull latest code (when available)
cd /volume1/docker/olive-monitoring
git pull

# 2. Rebuild containers
docker-compose build

# 3. Restart with new images
docker-compose down
docker-compose up -d

# 4. Verify health
docker-compose ps
docker-compose logs
```

## Performance Tuning

### PostgreSQL

Edit `docker-compose.yml` to add:
```yaml
postgres:
  environment:
    POSTGRES_SHARED_BUFFERS: 512MB
    POSTGRES_EFFECTIVE_CACHE_SIZE: 2GB
```

### Processor

Adjust memory limits in `docker-compose.yml`:
```yaml
processor:
  deploy:
    resources:
      limits:
        memory: 2G
```

## Security Considerations

1. **Firewall:** Ensure only Cloudflare tunnel can access port 8001
2. **Database:** PostgreSQL only accessible internally (not exposed outside Docker network)
3. **Credentials:** Never commit `.env` file to git
4. **Updates:** Regularly update Docker images for security patches

## Deployment Checklist

After successful deployment:
1. ✅ Verify all tests pass
2. ✅ Check database tables are created
3. ✅ Test Copernicus data fetching
4. ✅ Process satellite images
5. ✅ Configure Cloudflare tunnel endpoint
6. ✅ Build and deploy React dashboard
7. ✅ Dashboard live at https://farms.daniele.is
8. ⬜ Set up automated scheduled processing (every 5 days)
9. ⬜ Configure email alerts for health threshold violations
10. ⬜ Set up database backup schedule

## Ongoing Maintenance

### Daily/Weekly
- Monitor dashboard for data updates
- Check container health: `docker-compose ps`
- Review logs for errors: `docker-compose logs --tail 50`

### Monthly
- Backup database: `docker-compose exec postgres pg_dump -U olive_user olive_monitoring > backup_$(date +%Y%m%d).sql`
- Review disk usage: `docker system df`
- Check for Docker image updates

### As Needed
- Process historical data: `docker-compose exec processor python scripts/compare_historical.py`
- Update frontend: Rebuild and rsync to NAS
- Restart services after updates: `docker-compose restart`

## Support

If you encounter issues:
1. Check logs: `docker-compose logs <service>`
2. Verify configuration: `docker-compose config`
3. Check resources: `docker stats`
4. Review this guide's troubleshooting section

---

**Deployment Location:** Synology DS716+II NAS in Sweden
**Monitored Location:** Olive groves in Abruzzo, Italy (42.303°N, 14.187°E)
**Data Source:** Copernicus Sentinel-2 (free, 10m resolution, 5-day revisit)
**Architecture:** Remote processing model - zero hardware at farm
