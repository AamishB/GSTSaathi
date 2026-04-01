/**
 * Reconciliation API calls.
 */
import apiClient from "./axios";

/**
 * Run reconciliation.
 * @returns {Promise} - Reconciliation job response
 */
export const runReconciliation = async () => {
  const response = await apiClient.post("/reconcile/run");
  return response.data;
};

/**
 * Get reconciliation status.
 * @param {string} jobId - Job ID
 * @returns {Promise} - Reconciliation status
 */
export const getReconciliationStatus = async (jobId) => {
  const response = await apiClient.get(`/reconcile/status/${jobId}`);
  return response.data;
};

/**
 * Get reconciliation results.
 * @param {string} statusFilter - Filter by status (all, matched, mismatched)
 * @returns {Promise} - Reconciliation results
 */
export const getReconciliationResults = async (statusFilter = "all") => {
  const response = await apiClient.get("/reconcile/results", {
    params: { status_filter: statusFilter },
  });
  return response.data;
};

/**
 * Get reconciliation run logs.
 * @returns {Promise} - Reconciliation logs
 */
export const getReconciliationLog = async () => {
  const response = await apiClient.get("/reconcile/log");
  return response.data;
};
