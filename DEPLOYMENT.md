# Deployment Guide - Olive Farm Satellite Monitoring

## Prerequisites Checklist

- ✅ Synology DS716+II NAS with 8GB RAM (in Sweden)
- ✅ Docker and Docker Compose installed on NAS
- ✅ Cloudflare tunnel configured
- ✅ Copernicus Data Space account (username: work@daniele.is)
- ✅ Olive grove boundaries defined (3 zones in Abruzzo, Italy)
- ✅ `.env` file configured with credentials

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

Expected: All 3 containers start successfully
- `olive-monitoring-db` (PostgreSQL)
- `olive-monitoring-processor` (Python satellite processor)
- `olive-monitoring-api` (FastAPI backend)

### 6. Verify Containers

```bash
docker-compose ps
```

Expected output:
```
NAME                          STATUS    PORTS
olive-monitoring-db           Up        0.0.0.0:5432->5432/tcp
olive-monitoring-processor    Up
olive-monitoring-api          Up        0.0.0.0:8000->8000/tcp
```

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

### 9. Test API Access

```bash
# Test from NAS
curl http://localhost:8000/

# Test via Cloudflare tunnel (from anywhere)
curl https://your-cloudflare-url.com/
```

Expected: FastAPI response (even if 404, means it's running)

### 10. View Logs

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

1. **Firewall:** Ensure only Cloudflare tunnel can access port 8000
2. **Database:** PostgreSQL only accessible internally (not exposed outside Docker network)
3. **Credentials:** Never commit `.env` file to git
4. **Updates:** Regularly update Docker images for security patches

## Next Steps

After successful deployment:
1. ✅ Verify all tests pass
2. ✅ Check database tables are created
3. ⬜ Test Copernicus data fetching (requires API call)
4. ⬜ Process first satellite image
5. ⬜ Configure Cloudflare tunnel endpoint
6. ⬜ Build and deploy React dashboard (Phase 2)
7. ⬜ Set up scheduled processing

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
