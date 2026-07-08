import { render } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';

// Mock child components with heavy deps (Leaflet, Chart.js)
vi.mock('../FarmMap', () => ({ default: () => <div data-testid="farm-map" /> }));
vi.mock('../HealthChart', () => ({ default: () => <div data-testid="health-chart" /> }));
vi.mock('../HistoricalChart', () => ({ default: () => <div data-testid="historical-chart" /> }));

// Mock API module
vi.mock('../../services/api', () => ({
  getZones: vi.fn().mockResolvedValue([]),
  getZoneHealth: vi.fn().mockResolvedValue([]),
  getZoneAlerts: vi.fn().mockResolvedValue([]),
  getDashboardSummary: vi.fn().mockResolvedValue({ total_zones: 0, active_alerts: 0 }),
  getZoneHistory: vi.fn().mockResolvedValue([]),
}));

import Dashboard from '../Dashboard';

describe('Dashboard', () => {
  it('renders without crashing', () => {
    render(<Dashboard />);
    // The loading or content state — either way it renders
    expect(document.body).toBeTruthy();
  });
});
