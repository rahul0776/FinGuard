import axios from 'axios';
import { Alert, KPIMetrics } from '../types';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getAlerts = async (page = 1, pageSize = 50, riskLevel?: string) => {
  const params: any = { page, page_size: pageSize };
  if (riskLevel) params.risk_level = riskLevel;
  
  const response = await api.get('/api/alerts', { params });
  return response.data;
};

export const getAlert = async (alertId: string): Promise<Alert> => {
  const response = await api.get(`/api/alerts/${alertId}`);
  return response.data;
};

export const getMetrics = async (): Promise<KPIMetrics> => {
  const response = await api.get('/api/metrics');
  return response.data;
};

export const generateReport = async (alertId: string) => {
  const response = await api.get(`/api/reports/${alertId}`);
  return response.data.download_url;
};

export const triggerReplay = async (replayFile = 'replay_day_01.csv', speedMultiplier = 1.0) => {
  const response = await api.post('/api/replay', {
    replay_file: replayFile,
    speed_multiplier: speedMultiplier,
    webhook_signature: 'demo-signature',
  });
  return response.data;
};

export default api;



