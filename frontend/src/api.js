import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// API Functions
export const uploadInvoice = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  
  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const getAnalysis = async (workflowId = null) => {
  const params = workflowId ? { workflow_id: workflowId } : {};
  const response = await api.get('/analysis', { params });
  return response.data;
};

export const sendWhatsApp = async (vendorGstins = [], language = 'hi') => {
  const response = await api.post('/send-whatsapp', {
    vendor_gstins: vendorGstins,
    language,
  });
  return response.data;
};

export const fileGST = async (approvalStatus, notes = null) => {
  const response = await api.post('/file-gst', {
    approval_status: approvalStatus,
    notes,
  });
  return response.data;
};

export const getAuditTrail = async () => {
  const response = await api.get('/audit-trail');
  return response.data;
};

export const getDemoData = async () => {
  const response = await api.get('/demo-data');
  return response.data;
};

export default api;
