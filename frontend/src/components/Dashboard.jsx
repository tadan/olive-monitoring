/**
 * Main dashboard component for Olive Farm Monitoring
 */
import { useEffect, useState } from 'react';
import FarmMap from './FarmMap';
import HealthChart from './HealthChart';
import AlertViewer from './AlertViewer';
import { getZones, getZoneHealth, getZoneAlerts, getDashboardSummary } from '../services/api';
import './Dashboard.css';

const Dashboard = () => {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [zones, setZones] = useState([]);
  const [selectedZone, setSelectedZone] = useState(null);
  const [healthData, setHealthData] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [summary, setSummary] = useState(null);

  // Load initial data
  useEffect(() => {
    loadDashboardData();
  }, []);

  // Load health data when zone is selected
  useEffect(() => {
    if (selectedZone) {
      loadZoneData(selectedZone);
    }
  }, [selectedZone]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Load zones and summary
      const [zonesData, summaryData] = await Promise.all([
        getZones(),
        getDashboardSummary(),
      ]);

      setZones(zonesData);
      setSummary(summaryData);

      // Select first zone by default
      if (zonesData.length > 0) {
        setSelectedZone(zonesData[0].id);
      }

      setLoading(false);
    } catch (err) {
      console.error('Error loading dashboard:', err);
      setError('Failed to load dashboard data. Please check your backend connection.');
      setLoading(false);
    }
  };

  const loadZoneData = async (zoneId) => {
    try {
      const [health, alerts] = await Promise.all([
        getZoneHealth(zoneId, 30),
        getZoneAlerts(zoneId, true),
      ]);

      setHealthData(health);
      setAlerts(alerts);
    } catch (err) {
      console.error('Error loading zone data:', err);
      setError('Failed to load zone details');
    }
  };

  if (loading) {
    return (
      <div className="dashboard-loading">
        <div className="loading-spinner"></div>
        <p>Loading olive grove data...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <h2>⚠️ Error</h2>
        <p>{error}</p>
        <button onClick={loadDashboardData}>Retry</button>
      </div>
    );
  }

  const selectedZoneData = zones.find(z => z.id === selectedZone);
  const summaryByZone = summary?.zones.reduce((acc, zone) => {
    acc[zone.zone_id] = zone;
    return acc;
  }, {}) || {};

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>🫒 Tatasciore Olive Farm Monitoring</h1>
          <p>Real-time satellite health monitoring • Abruzzo, Italy</p>
        </div>
        <div className="header-stats">
          <div className="stat-card">
            <span className="stat-label">Total Area</span>
            <span className="stat-value">
              {zones.reduce((sum, z) => sum + parseFloat(z.area_hectares), 0).toFixed(2)} ha
            </span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Active Zones</span>
            <span className="stat-value">{zones.length}</span>
          </div>
          <div className="stat-card">
            <span className="stat-label">Active Alerts</span>
            <span className="stat-value alert-count">{alerts.length}</span>
          </div>
        </div>
      </header>

      <div className="dashboard-content">
        <div className="left-panel">
          <section className="map-section">
            <FarmMap zones={zones} healthData={summaryByZone} />
          </section>

          <section className="zone-selector">
            <h3>Select Zone</h3>
            <div className="zone-buttons">
              {zones.map(zone => (
                <button
                  key={zone.id}
                  className={`zone-button ${selectedZone === zone.id ? 'active' : ''}`}
                  onClick={() => setSelectedZone(zone.id)}
                >
                  <div className="zone-button-name">{zone.name}</div>
                  <div className="zone-button-area">{zone.area_hectares} ha</div>
                  {summaryByZone[zone.id]?.latest_health_score && (
                    <div className="zone-button-health">
                      Health: {summaryByZone[zone.id].latest_health_score}/100
                    </div>
                  )}
                </button>
              ))}
            </div>
          </section>

          <section className="chart-section">
            <HealthChart healthData={healthData} />
          </section>
        </div>

        <div className="right-panel">
          <section className="alerts-section">
            <AlertViewer alerts={alerts} />
          </section>

          {selectedZoneData && (
            <section className="zone-info">
              <h3>Zone Details</h3>
              <div className="info-grid">
                <div className="info-item">
                  <span className="info-label">Name</span>
                  <span className="info-value">{selectedZoneData.name}</span>
                </div>
                <div className="info-item">
                  <span className="info-label">Area</span>
                  <span className="info-value">{selectedZoneData.area_hectares} hectares</span>
                </div>
                {healthData.length > 0 && (
                  <>
                    <div className="info-item">
                      <span className="info-label">Latest NDVI</span>
                      <span className="info-value">{healthData[0].ndvi_mean.toFixed(3)}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Latest NDMI</span>
                      <span className="info-value">{healthData[0].ndmi_mean.toFixed(3)}</span>
                    </div>
                    <div className="info-item">
                      <span className="info-label">Last Updated</span>
                      <span className="info-value">
                        {new Date(healthData[0].date).toLocaleDateString()}
                      </span>
                    </div>
                  </>
                )}
              </div>
            </section>
          )}
        </div>
      </div>

      <footer className="dashboard-footer">
        <p>Data from Sentinel-2 satellites • Updated every 5 days • Powered by Copernicus</p>
      </footer>
    </div>
  );
};

export default Dashboard;
