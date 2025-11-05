FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for geospatial processing
RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set GDAL environment variables
ENV GDAL_CONFIG=/usr/bin/gdal-config
ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

# Copy requirements
COPY backend/requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ .

CMD ["python", "scripts/process_satellite_data.py"]
