import { create } from 'zustand';
import type { IoTData } from '../types/iotData';

interface IoTStore {
  selectedUserId: string | null;
  realtimeData: IoTData[];
  setSelectedUser: (userId: string | null) => void;
  setSelectedUserId: (userId: string | null) => void;
  addRealtimeData: (data: IoTData) => void;
  clearRealtimeData: () => void;
}

export const useIoTStore = create<IoTStore>((set) => ({
  selectedUserId: null,
  realtimeData: [],
  setSelectedUser: (userId) => set({ selectedUserId: userId, realtimeData: [] }),
  setSelectedUserId: (userId) => set({ selectedUserId: userId, realtimeData: [] }),
  addRealtimeData: (data) =>
    set((state) => ({
      realtimeData: [data, ...state.realtimeData].slice(0, 100),
    })),
  clearRealtimeData: () => set({ realtimeData: [] }),
}));