/**
 * Interactive map showing farm zones
 */
import { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, GeoJSON, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import './FarmMap.css';

// Health score color mapping
const getHealthColor = (score) => {
  if (!score || score === 0) return '#94a3b8'; // Gray - No data
  if (score >= 70) return '#22c55e'; // Green - Healthy
  if (score >= 50) return '#eab308'; // Yellow - Warning
  if (score >= 30) return '#f97316'; // Orange - Poor
  return '#ef4444'; // Red - Critical
};

// Border color - darker version for visibility
const getBorderColor = (score) => {
  if (!score || score === 0) return '#475569'; // Dark gray - No data
  if (score >= 70) return '#15803d'; // Dark green
  if (score >= 50) return '#a16207'; // Dark yellow
  if (score >= 30) return '#c2410c'; // Dark orange
  return '#b91c1c'; // Dark red
};

const FarmMap = ({ zones, healthData }) => {
  const mapRef = useRef(null);

  if (!zones || zones.length === 0) {
    return (
      <div className="farm-map-placeholder">
        <p>Loading map...</p>
      </div>
    );
  }

  // Detect if this is Ridgedale Farm (Swedish coordinates)
  const isRidgedale = zones.some(zone => zone.name.includes('Ridgedale'));

  // Calculate map center and zoom based on farm type
  let mapCenter, mapZoom;

  if (isRidgedale) {
    // Ridgedale Farm - show actual location (public farm)
    // Calculate center from zone geometries
    const coords = zones[0].geometry.coordinates[0];
    const lats = coords.map(c => c[1]);
    const lngs = coords.map(c => c[0]);
    const centerLat = (Math.min(...lats) + Math.max(...lats)) / 2;
    const centerLng = (Math.min(...lngs) + Math.max(...lngs)) / 2;
    mapCenter = [centerLat, centerLng];
    mapZoom = 15; // Zoomed in to show farm
  } else {
    // Olive farm - show Abruzzo region (for privacy)
    mapCenter = [42.35, 13.39];
    mapZoom = 9;
  }

  return (
    <div className="farm-map-container">
      <MapContainer
        center={mapCenter}
        zoom={mapZoom}
        style={{ height: '100%', width: '100%' }}
        ref={mapRef}
        key={`${mapCenter[0]}-${mapCenter[1]}`} // Force remount when center changes
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />

        {zones.map((zone) => {
          const zoneHealth = healthData[zone.id];
          const healthScore = zoneHealth?.latest_health_score || 0;

          return (
            <GeoJSON
              key={zone.id}
              data={zone.geometry}
              style={{
                fillColor: getHealthColor(healthScore),
                fillOpacity: 0.5,
                color: getBorderColor(healthScore),
                weight: 3,
                opacity: 1,
              }}
            >
              <Popup>
                <div className="zone-popup">
                  <h3>{zone.name}</h3>
                  <p><strong>Area:</strong> {zone.area_hectares} ha</p>
                  {zoneHealth && healthScore > 0 ? (
                    <>
                      <p><strong>Health Score:</strong> {healthScore}/100</p>
                      <p>
                        <strong>Last Updated:</strong>{' '}
                        {new Date(zoneHealth.latest_health_date).toLocaleDateString()}
                      </p>
                      {zoneHealth.active_alerts > 0 && (
                        <p className="alert-badge">
                          ⚠️ {zoneHealth.active_alerts} active alert(s)
                        </p>
                      )}
                    </>
                  ) : (
                    <p className="no-data">No health data available yet</p>
                  )}
                </div>
              </Popup>
            </GeoJSON>
          );
        })}
      </MapContainer>
    </div>
  );
};

export default FarmMap;
