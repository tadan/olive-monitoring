/**
 * API service for interacting with the olive monitoring backend
 */
import axios from 'axios';

// API base URL - configure based on environment
// Empty string means use relative URLs (same origin)
const API_BASE_URL = import.meta.env.VITE_API_URL !== undefined
  ? import.meta.env.VITE_API_URL
  : 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Get all field zones
 */
export const getZones = async () => {
  const response = await api.get('/api/zones');
  return response.data;
};

/**
 * Get a specific zone by ID
 */
export const getZone = async (zoneId) => {
  const response = await api.get(`/api/zones/${zoneId}`);
  return response.data;
};

/**
 * Get health history for a zone
 */
export const getZoneHealth = async (zoneId, limit = 30) => {
  const response = await api.get(`/api/zones/${zoneId}/health`, {
    params: { limit },
  });
  return response.data;
};

/**
 * Get alerts for a zone
 */
export const getZoneAlerts = async (zoneId, activeOnly = true) => {
  const response = await api.get(`/api/zones/${zoneId}/alerts`, {
    params: { active_only: activeOnly },
  });
  return response.data;
};

/**
 * Get dashboard summary
 */
export const getDashboardSummary = async () => {
  const response = await api.get('/api/dashboard/summary');
  return response.data;
};

/**
 * Get historical health data for a zone
 */
export const getZoneHistory = async (zoneId, params = {}) => {
  const response = await api.get(`/api/zones/${zoneId}/history`, {
    params: {
      start_year: params.startYear || 2015,
      end_year: params.endYear || new Date().getFullYear(),
      month: params.month || 9,
      day_start: params.dayStart || 10,
      day_end: params.dayEnd || 25,
    },
  });
  return response.data;
};

/**
 * Health check
 */
export const healthCheck = async () => {
  const response = await api.get('/health');
  return response.data;
};

export default api;
