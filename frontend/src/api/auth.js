/**
 * Authentication API calls.
 */
import apiClient from './axios';

/**
 * Register a new user.
 * @param {string} email - User email
 * @param {string} password - User password
 * @returns {Promise} - Registered user data
 */
export const register = async (email, password) => {
  const response = await apiClient.post('/auth/register', { email, password });
  return response.data;
};

/**
 * Login user.
 * @param {string} email - User email
 * @param {string} password - User password
 * @returns {Promise} - Login response with token
 */
export const login = async (email, password) => {
  const response = await apiClient.post('/auth/login', { email, password });
  if (response.data.access_token) {
    localStorage.setItem('token', response.data.access_token);
  }
  return response.data;
};

/**
 * Logout user.
 */
export const logout = () => {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
};

/**
 * Get current user profile.
 * @returns {Promise} - User profile data
 */
export const getCurrentUser = async () => {
  const response = await apiClient.get('/auth/me');
  return response.data;
};
