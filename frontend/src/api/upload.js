/**
 * Upload API calls.
 */
import apiClient from './axios';

/**
 * Upload invoices file.
 * @param {File} file - Invoice Excel/CSV file
 * @param {string} turnoverSlab - Turnover slab
 * @returns {Promise} - Upload response
 */
export const uploadInvoices = async (file, turnoverSlab = '1.5cr_to_5cr') => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('turnover_slab', turnoverSlab);

  const response = await apiClient.post('/upload/invoices', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

/**
 * Upload GSTR-2B file.
 * @param {File} file - GSTR-2B JSON/Excel file
 * @returns {Promise} - Upload response
 */
export const uploadGSTR2B = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await apiClient.post('/upload/gstr2b', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

/**
 * Get upload history.
 * @returns {Promise} - Upload history
 */
export const getUploadHistory = async () => {
  const response = await apiClient.get('/upload/history');
  return response.data;
};
