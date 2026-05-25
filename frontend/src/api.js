import axios from 'axios';

// In production (Vercel) set VITE_API_URL to the Render backend URL.
// Locally it falls back to the Flask dev server.
const BASE_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';
export const TOKEN_KEY = 'cf_token';

const api = axios.create({
  baseURL: BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// Attach the saved login token to every request, if present.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem(TOKEN_KEY);
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ---- Auth ----
export async function registerUser(payload) {
  const response = await api.post('/auth/register', payload);
  return response.data;
}

export async function loginUser(payload) {
  const response = await api.post('/auth/login', payload);
  return response.data;
}

export async function getMe() {
  const response = await api.get('/auth/me');
  return response.data;
}

// ---- Assessment ----
// Send the assessment to the backend and get top-3 recommendations.
// Saved to history automatically when the request carries a login token.
export async function getRecommendations(payload) {
  const response = await api.post('/predict', payload);
  return response.data;
}

// Fetch the logged-in user's past recommendations (for the dashboard).
export async function getHistory() {
  const response = await api.get('/history');
  return response.data;
}

// Fetch overall system stats.
export async function getStats() {
  const response = await api.get('/stats');
  return response.data;
}

export default api;
