FROM python:3.11-slim

WORKDIR /app

# Copy API-only requirements (no GDAL)
COPY backend/requirements-api.txt requirements.txt

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/app/ ./app/

# Expose port
EXPOSE 8000

# Run FastAPI with uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
