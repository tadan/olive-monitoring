/**
 * Interactive map showing olive grove zones
 */
import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, GeoJSON, Popup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import './FarmMap.css';

// Health score color mapping
const getHealthColor = (score) => {
  if (score >= 70) return '#22c55e'; // Green - Healthy
  if (score >= 50) return '#eab308'; // Yellow - Warning
  if (score >= 30) return '#f97316'; // Orange - Poor
  return '#ef4444'; // Red - Critical
};

const FarmMap = ({ zones, healthData }) => {
  const [map, setMap] = useState(null);

  // Abruzzo region center coordinates (for privacy)
  const abruzzoCenter = [42.35, 13.39]; // [lat, lng]

  if (!zones || zones.length === 0) {
    return (
      <div className="farm-map-placeholder">
        <p>Loading map...</p>
      </div>
    );
  }

  return (
    <div className="farm-map-container">
      <MapContainer
        center={abruzzoCenter}
        zoom={9}
        style={{ height: '100%', width: '100%' }}
        whenCreated={setMap}
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
                fillOpacity: 0.7,
                color: getHealthColor(healthScore),
                weight: 4,
              }}
            >
              <Popup>
                <div className="zone-popup">
                  <h3>{zone.name}</h3>
                  <p><strong>Area:</strong> {zone.area_hectares} ha</p>
                  {zoneHealth && (
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
