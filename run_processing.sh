#!/bin/bash
# Olive Monitoring - Satellite Data Processing Script
# Run by Synology Task Scheduler every 5 days at 02:00 AM

# Exit on error
set -e

# Change to project directory
cd /volume1/docker/olive-monitoring || {
    echo "ERROR: Could not change to /volume1/docker/olive-monitoring"
    exit 1
}

# Log start time
echo "=================================================="
echo "Processing started at: $(date)"
echo "=================================================="

# Run the processing inside the Docker container
# -T flag disables pseudo-TTY allocation (required for cron/scheduler)
/usr/local/bin/docker-compose exec -T processor python scripts/process_satellite_data.py

# Log completion
echo "=================================================="
echo "Processing completed at: $(date)"
echo "=================================================="
