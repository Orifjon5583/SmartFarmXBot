import axios from 'axios';
import { io } from 'socket.io-client';
import { historySeries, sensorSnapshot } from '../assets/greenhouseData';

const API_BASE_URL = import.meta.env.VITE_API_URL || '';
const USE_LOCAL_MOCKS = !import.meta.env.VITE_API_URL && import.meta.env.VITE_USE_MOCK_API !== 'false';

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

async function withFallback(request, fallback) {
  if (USE_LOCAL_MOCKS) {
    return fallback;
  }

  try {
    const response = await request();
    return response.data;
  } catch (error) {
    if (import.meta.env.DEV) {
      console.info('Using local greenhouse fallback data:', error.message);
    }
    return fallback;
  }
}

export const greenhouseApi = {
  getSensors: () => withFallback(() => api.get('/api/sensors'), sensorSnapshot),
  getHistory: () => withFallback(() => api.get('/api/history'), historySeries),
  getStatus: () =>
    withFallback(() => api.get('/api/status'), {
      raspberryPi: 'onlayn',
      api: 'ulangan',
      database: 'sinxron',
      uptime: '18d 06h',
    }),
  getCamera: () =>
    withFallback(() => api.get('/api/camera'), {
      streamUrl: '/api/camera',
      aiStatus: 'O‘simliklar sog‘lom',
      confidence: 94,
    }),
  setDevice: (device, enabled) => {
    if (USE_LOCAL_MOCKS) {
      return Promise.resolve({ data: { ok: true, device, enabled } });
    }
    return api.post(`/api/device/${device}`, { enabled });
  },
  verifyTelegram: async (payload) => {
    if (USE_LOCAL_MOCKS) {
      return {
        ok: true,
        message: 'Telegram sozlamalari lokal tekshiruvdan otdi.',
      };
    }

    try {
      const response = await api.post('/api/telegram/test', payload);
      return response.data;
    } catch (error) {
      const message = error.response?.data?.message || error.message;
      throw new Error(message);
    }
  },
  saveTelegramSettings: async (payload) => {
    if (USE_LOCAL_MOCKS) {
      return {
        ok: true,
        message: 'Telegram sozlamalari lokal saqlandi.',
      };
    }

    const response = await api.post('/api/telegram/settings', payload);
    return response.data;
  },
  sendTelegramNotification: async (text) => {
    if (USE_LOCAL_MOCKS) {
      return {
        ok: true,
        message: 'Lokal Telegram xabar yuborildi.',
      };
    }

    try {
      const response = await api.post('/api/telegram/notify', { text });
      return response.data;
    } catch (error) {
      const message = error.response?.data?.message || error.message;
      throw new Error(message);
    }
  },
};

export function createGreenhouseSocket() {
  return io(API_BASE_URL || window.location.origin, {
    path: '/socket.io',
    transports: ['websocket', 'polling'],
    autoConnect: false,
  });
}
