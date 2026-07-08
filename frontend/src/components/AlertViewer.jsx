/**
 * Alert viewer component showing health alerts for olive groves
 */
import { useState } from 'react';
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
  const [showAll, setShowAll] = useState(false);
  const INITIAL_DISPLAY = 5;

  if (!alerts || alerts.length === 0) {
    return (
      <div className="alert-viewer-container" role="status" aria-live="polite">
        <h2>All Clear</h2>
        <p>No active alerts for your olive groves</p>
      </div>
    );
  }

  // Show only first 5 alerts initially, or all if showAll is true
  const displayedAlerts = showAll ? alerts : alerts.slice(0, INITIAL_DISPLAY);
  const hasMore = alerts.length > INITIAL_DISPLAY;

  return (
    <div className="alert-viewer-container" role="region" aria-labelledby="alerts-heading">
      <div className="alert-header">
        <h2 id="alerts-heading">Active Alerts ({alerts.length})</h2>
      </div>

      <div className="alert-list" role="list">
        {displayedAlerts.map((alert) => (
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

      {hasMore && !showAll && (
        <button
          className="load-more-button"
          onClick={() => setShowAll(true)}
          aria-label={`Show ${alerts.length - INITIAL_DISPLAY} more alerts`}
        >
          Load More ({alerts.length - INITIAL_DISPLAY} more)
        </button>
      )}

      {showAll && hasMore && (
        <button
          className="load-more-button"
          onClick={() => setShowAll(false)}
          aria-label="Show fewer alerts"
        >
          Show Less
        </button>
      )}
    </div>
  );
};

export default AlertViewer;
