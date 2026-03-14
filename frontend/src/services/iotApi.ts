import { api } from './api';
import { IoTData, IoTDataBrief } from '../types/iotData';

export const iotApi = {
  ingestData: async (data: Omit<IoTData, 'user_id'> & { user_id: string }): Promise<IoTData> => {
    const response = await api.post('/data', data);
    return response.data;
  },

  getLatestData: async (userId: string): Promise<IoTDataBrief> => {
    const response = await api.get(`/users/${userId}/iot/latest`);
    return response.data;
  },

  getHistory: async (userId: string, limit: number = 50): Promise<IoTDataBrief[]> => {
    const response = await api.get(`/users/${userId}/iot/history?limit=${limit}`);
    return response.data;
  },
};