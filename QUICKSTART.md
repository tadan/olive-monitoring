# Olive Monitoring System - Quick Reference

**Dashboard:** https://farms.daniele.is
**Status:** All 3 phases complete ✅

## Common Commands

### Check System Status

```bash
# SSH into NAS
ssh daniele@192.168.1.112

# Check containers
cd /volume1/docker/olive-monitoring
docker-compose ps

# Check logs
docker-compose logs --tail 50
docker-compose logs dashboard --tail 20  # nginx
docker-compose logs api --tail 20        # FastAPI
```

### Update Frontend

```bash
# On local machine
cd /Users/danieletatasciore/Documents/repos/claude/olive-monitoring/frontend
npm run build
rsync -av dist/ daniele@192.168.1.112:/volume1/docker/olive-monitoring/frontend/dist/

# On NAS
ssh daniele@192.168.1.112
cd /volume1/docker/olive-monitoring
docker-compose restart dashboard
```

### Process Satellite Data

```bash
# SSH into NAS
ssh daniele@192.168.1.112
cd /volume1/docker/olive-monitoring

# Process latest available data
docker-compose exec processor python scripts/process_satellite_data.py

# Compare historical periods
docker-compose exec processor python scripts/compare_historical.py
```

### Restart Services

```bash
# SSH into NAS
cd /volume1/docker/olive-monitoring

# Restart all
docker-compose restart

# Restart specific service
docker-compose restart dashboard
docker-compose restart api
```

### Database Operations

```bash
# SSH into NAS
cd /volume1/docker/olive-monitoring

# Access database shell
docker-compose exec postgres psql -U olive_user -d olive_monitoring

# Reload field zones
docker-compose exec -T processor python scripts/load_field_zones.py

# Backup database
docker-compose exec postgres pg_dump -U olive_user olive_monitoring > backup_$(date +%Y%m%d).sql

# Restore database
docker-compose exec -T postgres psql -U olive_user -d olive_monitoring < backup.sql
```

### Cloudflare Tunnel

```bash
# SSH into NAS
ssh daniele@192.168.1.112

# Check tunnel status
sudo systemctl status cloudflared

# View logs
sudo journalctl -u cloudflared -n 50 --no-pager

# Restart tunnel
sudo systemctl restart cloudflared

# Edit config (use spaces, NOT tabs!)
sudo nano /volume1/docker/cloudflared/config.yml
```

## Troubleshooting Quick Fixes

### Dashboard Not Loading

```bash
# Check nginx is running
docker-compose ps dashboard

# Check nginx logs
docker-compose logs dashboard --tail 50

# Restart dashboard
docker-compose restart dashboard
```

### API Errors (500)

```bash
# Check API logs
docker-compose logs api --tail 50

# Check database connection
docker-compose exec api env | grep DB_

# Restart API
docker-compose restart api
```

### Database Connection Failed

```bash
# Check password doesn't have special chars (@, &, :, etc.)
cat .env | grep DB_PASSWORD

# If password has special chars, reset:
docker-compose down
docker volume rm olive-monitoring_postgres-data
nano .env  # Fix password
docker-compose up -d
docker-compose exec -T processor python scripts/load_field_zones.py
```

### Cloudflare Tunnel Not Working

```bash
# Check for YAML errors (no tabs!)
sudo systemctl status cloudflared

# Convert tabs to spaces
sudo expand -t 2 /volume1/docker/cloudflared/config.yml > /tmp/config.yml
sudo mv /tmp/config.yml /volume1/docker/cloudflared/config.yml

# Restart
sudo systemctl restart cloudflared
```

## Architecture Overview

```
┌─────────────────────────────────────────────────┐
│         Cloudflare Tunnel (HTTPS)               │
│         https://farms.daniele.is                │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  nginx (port 8080)                              │
│  - Serves React frontend                        │
│  - Proxies /api/* to backend                    │
└────────────────┬────────────────────────────────┘
                 │
                 ├──────► Static files (React)
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  FastAPI Backend (port 8000, internal)          │
│  - REST API endpoints                           │
│  - Database queries                             │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  PostgreSQL (port 5432, internal)               │
│  - Field zones                                  │
│  - Health indices (NDVI/NDMI)                   │
│  - Satellite images metadata                    │
│  - Alerts                                       │
└─────────────────────────────────────────────────┘
```

## Key Files

- **`CLAUDE.md`** - Project context and session history
- **`DEPLOYMENT.md`** - Comprehensive deployment guide
- **`docker-compose.yml`** - Container orchestration
- **`docker/nginx.conf`** - nginx reverse proxy config
- **`.env`** - Environment variables (not in git)
- **`frontend/.env.production`** - Frontend prod config (empty VITE_API_URL)

## Important Notes

1. **Database Password:** Must NOT contain `@`, `&`, `:`, `/`, `?`, `#`, `[`, `]`
2. **Frontend URLs:** Production uses relative URLs (empty VITE_API_URL)
3. **YAML Config:** Cloudflare tunnel config MUST use spaces, never tabs
4. **Security:** API and database ports are internal only, never exposed
5. **Deployment:** Frontend built locally, rsync'd to NAS

## Monitoring

### Health Checks

```bash
# Internal (from NAS)
curl http://localhost:8080/health
curl http://localhost:8080/api/zones

# External (from anywhere)
curl https://farms.daniele.is/health
curl https://farms.daniele.is/api/zones
```

### Resource Usage

```bash
# Check container resources
docker stats --no-stream

# Check disk usage
docker system df
du -sh /volume1/docker/olive-monitoring
```

## Next Steps

- [ ] Set up automated processing (cron job every 5 days)
- [ ] Configure email alerts for health threshold violations
- [ ] Set up automated database backups
- [ ] Add farm story content to dashboard
- [ ] Document seasonal patterns for Swedish customers

---

**Last Updated:** 2025-11-11
**System Status:** Production - All phases complete
**Public URL:** https://farms.daniele.is
