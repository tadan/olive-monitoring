/**
 * Interactive satellite map showing farm zones
 */
import { useEffect, useRef } from 'react';
import { MapContainer, TileLayer, GeoJSON, Popup, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import './FarmMap.css';

// Health score color mapping
const getHealthColor = (score) => {
  if (!score || score === 0) return '#94a3b8';
  if (score >= 70) return '#22c55e';
  if (score >= 50) return '#eab308';
  if (score >= 30) return '#f97316';
  return '#ef4444';
};

const getBorderColor = (score) => {
  if (!score || score === 0) return '#475569';
  if (score >= 70) return '#15803d';
  if (score >= 50) return '#a16207';
  if (score >= 30) return '#c2410c';
  return '#b91c1c';
};

// Fit map bounds to displayed zones
const FitBounds = ({ zones }) => {
  const map = useMap();

  useEffect(() => {
    if (!zones || zones.length === 0) return;

    const bounds = L.latLngBounds([]);
    zones.forEach((zone) => {
      const coords = zone.geometry.coordinates[0];
      coords.forEach(([lng, lat]) => bounds.extend([lat, lng]));
    });

    map.fitBounds(bounds, { padding: [30, 30], maxZoom: 18 });
  }, [zones, map]);

  return null;
};

const FarmMap = ({ zones, healthData }) => {
  if (!zones || zones.length === 0) {
    return (
      <div className="farm-map-placeholder" role="status" aria-live="polite">
        <p>Loading map data...</p>
      </div>
    );
  }

  return (
    <div className="farm-map-container" role="region" aria-label="Farm zones map visualization">
      <MapContainer
        center={[42.305, 14.185]}
        zoom={15}
        style={{ height: '100%', width: '100%' }}
        aria-label="Interactive satellite map of monitored farm zones"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>'
          url="https://{s}.google.com/vt/lyrs=s&x={x}&y={y}&z={z}"
          subdomains={['mt0', 'mt1', 'mt2', 'mt3']}
          maxZoom={20}
        />

        <FitBounds zones={zones} />

        {zones.map((zone) => {
          const zoneHealth = healthData[zone.id];
          const healthScore = zoneHealth?.latest_health_score || 0;

          return (
            <GeoJSON
              key={zone.id}
              data={zone.geometry}
              style={{
                fillColor: getHealthColor(healthScore),
                fillOpacity: 0.35,
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
