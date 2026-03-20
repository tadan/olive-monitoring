/**
 * Alert viewer component showing health alerts for olive groves
 */
import { format } from 'date-fns';
import './AlertViewer.css';

const getSeverityColor = (severity) => {
  switch (severity.toLowerCase()) {
    case 'critical':
      return '#ef4444'; // Red
    case 'high':
      return '#f97316'; // Orange
    case 'medium':
    case 'warning':
      return '#eab308'; // Yellow
    default:
      return '#3b82f6'; // Blue
  }
};

const getSeverityIcon = (severity) => {
  switch (severity.toLowerCase()) {
    case 'critical':
      return '!';
    case 'high':
      return '!';
    case 'medium':
    case 'warning':
      return '!';
    default:
      return 'i';
  }
};

const AlertViewer = ({ alerts }) => {
  if (!alerts || alerts.length === 0) {
    return (
      <div className="alert-viewer-container" role="status" aria-live="polite">
        <h2>All Clear</h2>
        <p>No active alerts for your olive groves</p>
      </div>
    );
  }

  // Group alerts by severity
  const groupedAlerts = {
    critical: alerts.filter(a => a.severity.toLowerCase() === 'critical'),
    high: alerts.filter(a => a.severity.toLowerCase() === 'high'),
    medium: alerts.filter(a => ['medium', 'warning'].includes(a.severity.toLowerCase())),
    low: alerts.filter(a => !['critical', 'high', 'medium', 'warning'].includes(a.severity.toLowerCase())),
  };

  return (
    <div className="alert-viewer-container" role="region" aria-labelledby="alerts-heading">
      <div className="alert-header">
        <h2 id="alerts-heading">Active Alerts ({alerts.length})</h2>
      </div>

      <div className="alert-list" role="list">
        {alerts.map((alert) => (
          <div
            key={alert.id}
            className="alert-item"
            role="listitem"
            style={{ borderLeftColor: getSeverityColor(alert.severity) }}
            aria-label={`${alert.severity} alert: ${alert.title}`}
          >
            <div className="alert-icon" aria-hidden="true">
              {getSeverityIcon(alert.severity)}
            </div>
            <div className="alert-content">
              <div className="alert-title-row">
                <h3>{alert.title}</h3>
                <span
                  className="alert-severity-badge"
                  style={{ backgroundColor: getSeverityColor(alert.severity) + '20', color: getSeverityColor(alert.severity) }}
                >
                  {alert.severity}
                </span>
              </div>
              {alert.description && (
                <p className="alert-description">{alert.description}</p>
              )}
              <div className="alert-meta">
                <span className="alert-type">{alert.type}</span>
                <span className="alert-date">
                  {format(new Date(alert.detected_at), 'MMM dd, yyyy HH:mm')}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {Object.entries(groupedAlerts).map(([severity, severityAlerts]) => {
        if (severityAlerts.length === 0) return null;
        return (
          <div key={severity} className="alert-summary-item">
            <span style={{ color: getSeverityColor(severity) }}>
              {getSeverityIcon(severity)} {severityAlerts.length} {severity}
            </span>
          </div>
        );
      })}
    </div>
  );
};

export default AlertViewer;
