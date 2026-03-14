import { useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { userApi } from '../services/userApi';
import { iotApi } from '../services/iotApi';
import { useIoTStore } from '../stores/iotStore';
import { useAuthStore } from '../stores/authStore';
import { wsService } from '../services/websocket';
import { Card, CardHeader, CardContent } from '../components/ui/Card';
import { IoTLineChart } from '../components/iot/LineChart';
import { LatestDataCard } from '../components/iot/MetricCard';
import { IoTDataTable } from '../components/iot/DataTable';
import type { IoTData } from '../types/iotData';

export function IoTDataPage() {
  const token = useAuthStore((state) => state.token);
  const { selectedUserId, setSelectedUserId, realtimeData, addRealtimeData } = useIoTStore();

  const { data: users } = useQuery({
    queryKey: ['users'],
    queryFn: userApi.getUsers,
  });

  const { data: latestData } = useQuery({
    queryKey: ['iotLatest', selectedUserId],
    queryFn: () => (selectedUserId ? iotApi.getLatestData(selectedUserId) : null),
    enabled: !!selectedUserId,
  });

  const { data: historyData } = useQuery({
    queryKey: ['iotHistory', selectedUserId],
    queryFn: () => (selectedUserId ? iotApi.getHistory(selectedUserId, 50) : null),
    enabled: !!selectedUserId,
  });

  const activeUsers = users?.filter((u) => u.status === 'active') || [];

  useEffect(() => {
    if (token && selectedUserId) {
      wsService.connect();
      wsService.subscribe(selectedUserId, (data) => {
        addRealtimeData(data);
      });
    }

    return () => {
      if (selectedUserId) {
        wsService.unsubscribe(selectedUserId);
      }
    };
  }, [token, selectedUserId, addRealtimeData]);

  const formattedHistory = historyData?.map(h => ({ ...h, user_id: selectedUserId || '' })) || [];
  
  const mergedMap = new Map<number, IoTData>();
  formattedHistory.forEach(d => mergedMap.set(d.timestamp, d));
  realtimeData.forEach(d => mergedMap.set(d.timestamp, d));

  const mergedData = Array.from(mergedMap.values())
    .sort((a, b) => b.timestamp - a.timestamp)
    .slice(0, 100);

  const currentLatestData = mergedData.length > 0 ? mergedData[0] : latestData;

  return (
    <div>
      <h2 className="text-2xl font-bold text-gray-900 mb-6">IoT Data</h2>

      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Select User
        </label>
        <div className="flex gap-4">
          <select
            value={selectedUserId || ''}
            onChange={(e) => setSelectedUserId(e.target.value || null)}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="">Select a user...</option>
            {activeUsers.map((user) => (
              <option key={user.user_id} value={user.user_id}>
                {user.name} ({user.user_id})
              </option>
            ))}
          </select>
        </div>
      </div>

      {selectedUserId ? (
        <div className="space-y-6">
          {currentLatestData && <LatestDataCard data={currentLatestData} />}

          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">
                  Real-Time Data
                </h3>
                <div className="flex items-center gap-2">
                  <span className="flex h-3 w-3">
                    <span className="animate-ping absolute inline-flex h-3 w-3 rounded-full bg-green-400 opacity-75"></span>
                    <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                  </span>
                  <span className="text-sm text-gray-500">Live</span>
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {mergedData.length > 0 ? (
                <IoTLineChart data={mergedData} />
              ) : (
                <p className="text-center text-gray-500 py-8">
                  No data available yet
                </p>
              )}
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <h3 className="text-lg font-semibold text-gray-900">Data History</h3>
            </CardHeader>
            <CardContent>
              {mergedData.length > 0 ? (
                <IoTDataTable data={mergedData} />
              ) : (
                <p className="text-center text-gray-500 py-8">
                  No historical data available
                </p>
              )}
            </CardContent>
          </Card>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
          <svg
            className="mx-auto h-12 w-12 text-gray-400"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
            />
          </svg>
          <h3 className="mt-4 text-lg font-medium text-gray-900">
            Select a user to view IoT data
          </h3>
          <p className="mt-2 text-sm text-gray-500">
            Choose a user from the dropdown above to see their real-time and
            historical IoT data.
          </p>
        </div>
      )}
    </div>
  );
}