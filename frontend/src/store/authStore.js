/**
 * Authentication store using Zustand.
 */
import { create } from "zustand";
import { login, register, logout, getCurrentUser } from "../api/auth";
import useDashboardStore from "./dashboardStore";

const formatErrorDetail = (detail) => {
  if (!detail) return null;

  if (typeof detail === "string") {
    return detail;
  }

  // FastAPI/Pydantic validation errors are often arrays of objects.
  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        if (typeof item === "string") return item;
        if (item && typeof item.msg === "string") return item.msg;
        return null;
      })
      .filter(Boolean);

    if (messages.length > 0) {
      return messages.join("; ");
    }
  }

  if (typeof detail === "object") {
    if (typeof detail.message === "string") return detail.message;
    try {
      return JSON.stringify(detail);
    } catch {
      return "Unexpected error";
    }
  }

  return String(detail);
};

const getApiErrorMessage = (error, fallback) => {
  const responseData = error?.response?.data;
  const detailMessage = formatErrorDetail(responseData?.detail);
  const message = formatErrorDetail(responseData?.message);

  return detailMessage || message || error?.message || fallback;
};

const useAuthStore = create((set) => ({
  // State
  user: JSON.parse(localStorage.getItem("user")) || null,
  token: localStorage.getItem("token") || null,
  isAuthenticated: !!localStorage.getItem("token"),
  loading: false,
  error: null,

  // Actions
  login: async (email, password) => {
    set({ loading: true, error: null });
    try {
      const response = await login(email, password);
      localStorage.setItem("token", response.access_token);
      const user = await getCurrentUser();
      localStorage.setItem("user", JSON.stringify(user));
      set({
        user,
        token: response.access_token,
        isAuthenticated: true,
        loading: false,
      });
      return response;
    } catch (error) {
      set({
        error: getApiErrorMessage(error, "Login failed"),
        loading: false,
      });
      throw error;
    }
  },

  register: async (email, password) => {
    set({ loading: true, error: null });
    try {
      const response = await register(email, password);
      set({ loading: false });
      return response;
    } catch (error) {
      set({
        error: getApiErrorMessage(error, "Registration failed"),
        loading: false,
      });
      throw error;
    }
  },

  logout: () => {
    logout();
    useDashboardStore.getState().clearDashboard();
    set({
      user: null,
      token: null,
      isAuthenticated: false,
      error: null,
    });
  },

  clearError: () => {
    set({ error: null });
  },

  loadCurrentUser: async () => {
    const token = localStorage.getItem("token");
    if (!token) return null;

    set({ loading: true, error: null });
    try {
      const user = await getCurrentUser();
      localStorage.setItem("user", JSON.stringify(user));
      set({ user, isAuthenticated: true, loading: false });
      return user;
    } catch (error) {
      logout();
      set({
        user: null,
        token: null,
        isAuthenticated: false,
        loading: false,
        error: null,
      });
      return null;
    }
  },
}));

export default useAuthStore;
