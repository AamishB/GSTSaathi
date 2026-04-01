/**
 * Dashboard API calls.
 */
import apiClient from './axios';

/**
 * Get dashboard metrics.
 * @returns {Promise} - Dashboard metrics
 */
export const getMetrics = async () => {
  const response = await apiClient.get('/dashboard/metrics');
  return response.data;
};

/**
 * Get dashboard summary.
 * @returns {Promise} - Dashboard summary
 */
export const getSummary = async () => {
  const response = await apiClient.get('/dashboard/summary');
  return response.data;
};
