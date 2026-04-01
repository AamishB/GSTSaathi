/**
 * Upload store using Zustand.
 */
import { create } from 'zustand';
import { uploadInvoices, uploadGSTR2B, getUploadHistory } from '../api/upload';

const useUploadStore = create((set) => ({
  // State
  uploading: false,
  uploadProgress: 0,
  uploadResult: null,
  uploadError: null,
  history: [],

  // Actions
  uploadInvoices: async (file, turnoverSlab) => {
    set({ uploading: true, uploadProgress: 0, uploadError: null });
    try {
      const result = await uploadInvoices(file, turnoverSlab);
      set({
        uploading: false,
        uploadProgress: 100,
        uploadResult: result,
      });
      return result;
    } catch (error) {
      set({
        uploading: false,
        uploadError: error.response?.data?.detail || 'Upload failed',
      });
      throw error;
    }
  },

  uploadGSTR2B: async (file) => {
    set({ uploading: true, uploadProgress: 0, uploadError: null });
    try {
      const result = await uploadGSTR2B(file);
      set({
        uploading: false,
        uploadProgress: 100,
        uploadResult: result,
      });
      return result;
    } catch (error) {
      set({
        uploading: false,
        uploadError: error.response?.data?.detail || 'Upload failed',
      });
      throw error;
    }
  },

  loadHistory: async () => {
    try {
      const history = await getUploadHistory();
      set({ history });
    } catch (error) {
      console.error('Failed to load upload history:', error);
    }
  },

  clearUploadResult: () => {
    set({ uploadResult: null, uploadError: null, uploadProgress: 0 });
  },
}));

export default useUploadStore;
