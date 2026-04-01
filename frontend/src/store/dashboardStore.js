/**
 * Dashboard store using Zustand.
 */
import { create } from "zustand";
import { getMetrics, getSummary } from "../api/dashboard";

const useDashboardStore = create((set) => ({
  // State
  metrics: null,
  summary: null,
  loading: false,
  error: null,

  // Actions
  loadMetrics: async () => {
    // Reset cached metrics before loading to avoid showing another user's data.
    set({ loading: true, error: null, metrics: null });
    try {
      const metrics = await getMetrics();
      set({ metrics, loading: false });
      return metrics;
    } catch (error) {
      set({
        metrics: null,
        loading: false,
        error: error.response?.data?.detail || "Failed to load metrics",
      });
      throw error;
    }
  },

  loadSummary: async () => {
    set({ loading: true, error: null, summary: null });
    try {
      const summary = await getSummary();
      set({ summary, loading: false });
      return summary;
    } catch (error) {
      set({
        summary: null,
        loading: false,
        error: error.response?.data?.detail || "Failed to load summary",
      });
      throw error;
    }
  },

  clearDashboard: () => {
    set({
      metrics: null,
      summary: null,
      loading: false,
      error: null,
    });
  },
}));

export default useDashboardStore;
