/**
 * Main dashboard component for Olive Farm Monitoring
 */
import { useEffect, useState } from 'react'
import FarmMap from './FarmMap'
import HealthChart from './HealthChart'
import HistoricalChart from './HistoricalChart'
import AlertViewer from './AlertViewer'
import FarmSelector from './FarmSelector'
import {
    getZones,
    getZoneHealth,
    getZoneAlerts,
    getDashboardSummary,
    getZoneHistory,
} from '../services/api'
import './Dashboard.css'

// Define farms for comparison
const FARMS = [
    { id: 'olive', name: "Cuppino's Olive Farm", location: 'Abruzzo, Italy' },
    { id: 'ruzzi', name: 'Ruzzi Family Farm', location: 'Abruzzo, Italy' },
    { id: 'ruzzi-aunt', name: "Ruzzi Aunt's Farm", location: 'Abruzzo, Italy' },
]

const Dashboard = () => {
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState(null)
    const [zones, setZones] = useState([])
    const [selectedFarm, setSelectedFarm] = useState('olive')
    const [selectedZone, setSelectedZone] = useState(null)
    const [healthData, setHealthData] = useState([])
    const [historicalData, setHistoricalData] = useState(null)
    const [alerts, setAlerts] = useState([])
    const [summary, setSummary] = useState(null)

    // Load initial data
    useEffect(() => {
        loadDashboardData()
    }, [])

    // Reset selected zone when farm changes
    useEffect(() => {
        const farmZones = zones.filter((zone) => {
            if (selectedFarm === 'ruzzi') return zone.name.startsWith('Ruzzi - ') || zone.name === 'Ruzzi Home'
            if (selectedFarm === 'ruzzi-aunt') return zone.name.includes('Ruzzi Aunt')
            return !zone.name.includes('Ruzzi')
        })
        if (farmZones.length > 0) {
            setSelectedZone(farmZones[0].id)
        } else {
            setSelectedZone(null)
        }
    }, [selectedFarm, zones])

    // Load health data when zone is selected
    useEffect(() => {
        if (selectedZone) {
            loadZoneData(selectedZone)
        } else {
            setHealthData([])
            setAlerts([])
            setHistoricalData(null)
        }
    }, [selectedZone])

    // Filter zones by selected farm
    const getFilteredZones = () => {
        return zones.filter((zone) => {
            if (selectedFarm === 'ruzzi') {
                // Ruzzi farm: zones with "Ruzzi -" or "Ruzzi Home" (NOT "Ruzzi Aunt")
                return zone.name.startsWith('Ruzzi - ') || zone.name === 'Ruzzi Home'
            }
            if (selectedFarm === 'ruzzi-aunt') {
                return zone.name.includes('Ruzzi Aunt')
            }
            // Cuppino's Olive Farm: original zones (Below Natural, Below Falling Houses, House)
            return !zone.name.includes('Ruzzi')
        })
    }

    const loadDashboardData = async () => {
        try {
            setLoading(true)
            setError(null)

            // Load zones and summary
            const [zonesData, summaryData] = await Promise.all([
                getZones(),
                getDashboardSummary(),
            ])

            setZones(zonesData)
            setSummary(summaryData)

            // Select first zone by default
            if (zonesData.length > 0) {
                setSelectedZone(zonesData[0].id)
            }

            setLoading(false)
        } catch (err) {
            console.error('Error loading dashboard:', err)
            setError(
                'Failed to load dashboard data. Please check your backend connection.'
            )
            setLoading(false)
        }
    }

    const loadZoneData = async (zoneId) => {
        try {
            const [health, alerts, history] = await Promise.all([
                getZoneHealth(zoneId, 30),
                getZoneAlerts(zoneId, true),
                getZoneHistory(zoneId),
            ])

            setHealthData(health)
            setAlerts(alerts)
            setHistoricalData(history)
        } catch (err) {
            console.error('Error loading zone data:', err)
            setError('Failed to load zone details')
        }
    }

    if (loading) {
        return (
            <div className='dashboard-loading'>
                <div className='loading-spinner'></div>
                <p>Loading olive grove data...</p>
            </div>
        )
    }

    if (error) {
        return (
            <div className='dashboard-error'>
                <h2>⚠️ Error</h2>
                <p>{error}</p>
                <button onClick={loadDashboardData}>Retry</button>
            </div>
        )
    }

    const filteredZones = getFilteredZones()
    const selectedZoneData = filteredZones.find((z) => z.id === selectedZone)
    const summaryByZone =
        summary?.zones.reduce((acc, zone) => {
            acc[zone.zone_id] = zone
            return acc
        }, {}) || {}

    const currentFarm = FARMS.find((f) => f.id === selectedFarm)

    return (
        <div className='dashboard'>
            <header className='dashboard-header'>
                <div className='header-content'>
                    <h1>Farm Health Monitoring</h1>
                    <p>
                        Sentinel-2 Satellite • 10m Resolution • 5-Day Revisit
                    </p>
                </div>
                <div className='header-stats'>
                    <div className='stat-card'>
                        <span className='stat-label'>Total Area</span>
                        <span className='stat-value'>
                            {filteredZones
                                .reduce(
                                    (sum, z) =>
                                        sum + parseFloat(z.area_hectares),
                                    0
                                )
                                .toFixed(2)}{' '}
                            ha
                        </span>
                    </div>
                    <div className='stat-card'>
                        <span className='stat-label'>Active Zones</span>
                        <span className='stat-value'>{filteredZones.length}</span>
                    </div>
                    <div className='stat-card'>
                        <span className='stat-label'>Active Alerts</span>
                        <span className='stat-value alert-count'>
                            {alerts.length}
                        </span>
                    </div>
                </div>
            </header>

            <nav aria-label="Farm selection">
                <FarmSelector
                    farms={FARMS}
                    selectedFarm={selectedFarm}
                    onSelectFarm={setSelectedFarm}
                />
            </nav>

            <main className='dashboard-content'>
                <div className='left-panel'>
                    <section className='map-section'>
                        <FarmMap zones={filteredZones} healthData={summaryByZone} />
                    </section>

                    {filteredZones.length > 0 ? (
                        <>
                            <section className='zone-selector' aria-labelledby="zone-selector-heading">
                                <h3 id="zone-selector-heading">Select Zone</h3>
                                <div className='zone-buttons' role="tablist" aria-label="Farm zones">
                                    {filteredZones.map((zone) => (
                                        <button
                                            key={zone.id}
                                            role="tab"
                                            aria-selected={selectedZone === zone.id}
                                            aria-controls={`zone-panel-${zone.id}`}
                                            className={`zone-button ${
                                                selectedZone === zone.id ? 'active' : ''
                                            }`}
                                            onClick={() => setSelectedZone(zone.id)}
                                        >
                                            <div className='zone-button-name'>
                                                {zone.name}
                                            </div>
                                            <div className='zone-button-area'>
                                                {zone.area_hectares} ha
                                            </div>
                                            {summaryByZone[zone.id]
                                                ?.latest_health_score && (
                                                <div className='zone-button-health'>
                                                    Health:{' '}
                                                    {
                                                        summaryByZone[zone.id]
                                                            .latest_health_score
                                                    }
                                                    /100
                                                </div>
                                            )}
                                        </button>
                                    ))}
                                </div>
                            </section>

                            <section className='chart-section'>
                                <HealthChart healthData={healthData} />
                            </section>

                            <section className='historical-section'>
                                <HistoricalChart historyData={historicalData} />
                            </section>
                        </>
                    ) : (
                        <section className='no-data-message' aria-label="No data available">
                            <div className='message-box'>
                                <h3>No Data Available</h3>
                                <p>
                                    No zones found for {currentFarm?.name}.
                                    Please add zones to see health monitoring data.
                                </p>
                            </div>
                        </section>
                    )}
                </div>

                <aside className='right-panel' aria-label="Zone information and alerts">
                    <section className='alerts-section'>
                        <AlertViewer alerts={alerts} />
                    </section>

                    {selectedZoneData && (
                        <section className='zone-info'>
                            <h3>Zone Details</h3>
                            <div className='info-grid'>
                                <div className='info-item'>
                                    <span className='info-label'>Name</span>
                                    <span className='info-value'>
                                        {selectedZoneData.name}
                                    </span>
                                </div>
                                <div className='info-item'>
                                    <span className='info-label'>Area</span>
                                    <span className='info-value'>
                                        {selectedZoneData.area_hectares}{' '}
                                        hectares
                                    </span>
                                </div>
                                {healthData.length > 0 && (
                                    <>
                                        <div className='info-item'>
                                            <span className='info-label'>
                                                Latest NDVI
                                            </span>
                                            <span className='info-value'>
                                                {healthData[0].ndvi_mean.toFixed(
                                                    3
                                                )}
                                            </span>
                                        </div>
                                        <div className='info-item'>
                                            <span className='info-label'>
                                                Latest NDMI
                                            </span>
                                            <span className='info-value'>
                                                {healthData[0].ndmi_mean.toFixed(
                                                    3
                                                )}
                                            </span>
                                        </div>
                                        <div className='info-item'>
                                            <span className='info-label'>
                                                Last Updated
                                            </span>
                                            <span className='info-value'>
                                                {new Date(
                                                    healthData[0].date
                                                ).toLocaleDateString()}
                                            </span>
                                        </div>
                                    </>
                                )}
                            </div>
                        </section>
                    )}
                </aside>
            </main>

            <footer className='dashboard-footer'>
                <p>
                    Data: Sentinel-2 ESA • Resolution: 10m • Revisit: 5 Days • Source: Copernicus Programme
                </p>
            </footer>
        </div>
    )
}

export default Dashboard
