/**
 * Reconciliation store using Zustand.
 */
import { create } from "zustand";
import {
  runReconciliation,
  getReconciliationResults,
  getReconciliationLog,
  sendWhatsAppReminders,
} from "../api/reconcile";

const useReconcileStore = create((set) => ({
  // State
  reconciling: false,
  reconciliationStatus: null,
  reconciliationResults: [],
  reconciliationLog: [],
  statistics: null,
  sendingWhatsApp: false,
  whatsappSummary: null,
  error: null,

  // Actions
  runReconciliation: async () => {
    set({ reconciling: true, error: null });
    try {
      const result = await runReconciliation();
      set({
        reconciling: false,
        reconciliationStatus: result,
      });
      return result;
    } catch (error) {
      set({
        reconciling: false,
        error: error.response?.data?.detail || "Reconciliation failed",
      });
      throw error;
    }
  },

  loadResults: async (statusFilter = "all") => {
    try {
      const results = await getReconciliationResults(statusFilter);
      set({
        reconciliationResults: results.results,
        statistics: {
          total: results.total,
          matchedCount: results.matched_count,
          mismatchCount: results.mismatch_count,
        },
      });
    } catch (error) {
      console.error("Failed to load reconciliation results:", error);
    }
  },

  loadReconciliationLog: async () => {
    try {
      const response = await getReconciliationLog();
      set({ reconciliationLog: response.logs || [] });
    } catch (error) {
      console.error("Failed to load reconciliation log:", error);
    }
  },

  sendWhatsAppReminders: async (vendorGstins = [], language = "hi") => {
    set({ sendingWhatsApp: true, error: null });
    try {
      const result = await sendWhatsAppReminders(vendorGstins, language);
      set({
        sendingWhatsApp: false,
        whatsappSummary: result,
      });
      return result;
    } catch (error) {
      set({
        sendingWhatsApp: false,
        error: error.response?.data?.detail || "Failed to send WhatsApp reminders",
      });
      throw error;
    }
  },

  clearResults: () => {
    set({
      reconciliationResults: [],
      reconciliationStatus: null,
      reconciliationLog: [],
      statistics: null,
      sendingWhatsApp: false,
      whatsappSummary: null,
      error: null,
    });
  },
}));

export default useReconcileStore;
