/**
 * Export API calls.
 */
import apiClient from './axios';

/**
 * Export GSTR-1 JSON.
 * @param {string} month - Month (MM)
 * @param {number} year - Year (YYYY)
 * @returns {Promise} - Download URL
 */
export const exportGSTR1 = async (month, year) => {
  const response = await apiClient.get('/export/gstr1', {
    params: { month, year },
    responseType: 'blob',
  });
  
  // Create download link
  const blob = new Blob([response.data], { type: 'application/json' });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `GSTR1_${month}-${year}.json`;
  link.click();
  window.URL.revokeObjectURL(url);
  
  return response.data;
};

/**
 * Export GSTR-3B Excel.
 * @param {string} month - Month (MM)
 * @param {number} year - Year (YYYY)
 * @returns {Promise} - Download URL
 */
export const exportGSTR3B = async (month, year) => {
  const response = await apiClient.get('/export/gstr3b', {
    params: { month, year },
    responseType: 'blob',
  });
  
  // Create download link
  const blob = new Blob([response.data], { 
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `GSTR3B_${month}-${year}.xlsx`;
  link.click();
  window.URL.revokeObjectURL(url);
  
  return response.data;
};

/**
 * Export mismatch report.
 * @param {string} statusFilter - Filter by status (all, pending, resolved)
 * @returns {Promise} - Download URL
 */
export const exportMismatchReport = async (statusFilter = 'all') => {
  const response = await apiClient.get('/export/mismatch-report', {
    params: { status_filter: statusFilter },
    responseType: 'blob',
  });
  
  // Create download link
  const blob = new Blob([response.data], { 
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `Mismatch_Report_${new Date().toISOString().slice(0, 7)}.xlsx`;
  link.click();
  window.URL.revokeObjectURL(url);
  
  return response.data;
};
