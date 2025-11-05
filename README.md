# Olive Farm Satellite Monitoring Portal

Remote satellite monitoring system for Italian olive farm using Copernicus Sentinel-2 data, processed on Synology NAS in Sweden.

## Overview

- **Farm Location:** Italy
- **Processing Location:** Synology DS716+II NAS (8GB RAM) in Sweden
- **Data Source:** Copernicus Sentinel-2 satellites (free, 10m resolution, 5-day revisit)
- **Purpose:** Health monitoring, transparency for Swedish customers, operational optimization

## Architecture

- **Backend:** Python 3.11+, Docker, PostgreSQL, FastAPI
- **Frontend:** React 18, Leaflet (maps), Chart.js (visualizations)
- **Deployment:** Self-hosted on Synology NAS, accessible via Cloudflare tunnel
- **Processing:** Automated every 5 days, NDVI/NDMI calculations, anomaly detection

## Project Structure

```
olive-monitoring/
├── backend/           # Python processing and API
│   ├── app/          # Application code
│   ├── tests/        # Test suite
│   ├── scripts/      # Processing scripts
│   └── data/         # Satellite data storage
├── frontend/         # React dashboard
│   ├── src/          # Source code
│   └── public/       # Static assets
├── docker/           # Dockerfiles
├── config/           # Configuration files
└── docs/             # Documentation
```

## Prerequisites

- Synology DS716+II with Docker installed
- Copernicus Data Space account (free)
- Olive farm GPS coordinates
- Python 3.11+, Node.js 18+, Git

## Implementation Timeline

- **Weeks 1-2:** Data pipeline foundation
- **Weeks 3-4:** Analysis engine (alerts, baseline)
- **Weeks 5-6:** Dashboard development
- **Weeks 7-8:** Integration and deployment

## Getting Started

See [Implementation Plan](../docs/plans/2025-11-04-olive-farm-satellite-monitoring.md) for detailed setup instructions.

## License

Private project - not for distribution

---

*Project started: 2025-11-05*
