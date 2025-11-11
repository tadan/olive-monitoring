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

  useEffect(() => {
    if (map && zones && zones.length > 0) {
      // Fit bounds to show all zones
      const bounds = zones.map(zone => {
        const coords = zone.geometry.coordinates[0];
        return coords.map(([lng, lat]) => [lat, lng]);
      }).flat();

      if (bounds.length > 0) {
        map.fitBounds(bounds);
      }
    }
  }, [map, zones]);

  if (!zones || zones.length === 0) {
    return (
      <div className="farm-map-placeholder">
        <p>Loading map...</p>
      </div>
    );
  }

  // Get farm center from first zone
  const firstZone = zones[0];
  const firstCoord = firstZone.geometry.coordinates[0][0];
  const center = [firstCoord[1], firstCoord[0]]; // [lat, lng]

  return (
    <div className="farm-map-container">
      <MapContainer
        center={center}
        zoom={15}
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
                fillOpacity: 0.4,
                color: getHealthColor(healthScore),
                weight: 2,
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
