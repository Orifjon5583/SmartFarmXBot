import axios from 'axios';
import { io } from 'socket.io-client';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';
export const REALTIME_ENABLED = true;

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 8000,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('greenhouse_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export const greenhouseApi = {
  getSensors: () => api.get('/api/sensors').then(res => res.data),
  getHistory: () => api.get('/api/history').then(res => res.data),
  getStatus: () => api.get('/api/status').then(res => res.data),
  getCamera: () => api.get('/api/camera').then(res => res.data),
  setDevice: (device, enabled, source = 'site') => api.post(`/api/device/${device}`, { enabled, source }),
};

export function createGreenhouseSocket() {
  return io(API_BASE_URL || window.location.origin, {
    path: '/socket.io',
    transports: ['websocket', 'polling'],
    autoConnect: false,
    auth: (callback) => {
      callback({ token: localStorage.getItem('greenhouse_token') || '' });
    },
  });
}
