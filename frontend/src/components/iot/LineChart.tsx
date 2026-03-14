import {
  LineChart as RechartsLineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { IoTData } from '../../types/iotData';

interface LineChartProps {
  data: IoTData[];
  height?: number;
}

export function IoTLineChart({ data, height = 300 }: LineChartProps) {
  const chartData = [...data].reverse().map((item) => ({
    timestamp: new Date(item.timestamp * 1000).toLocaleTimeString(),
    metric_1: item.metric_1,
    metric_2: item.metric_2,
    metric_3: item.metric_3,
  }));

  return (
    <ResponsiveContainer width="100%" height={height}>
      <RechartsLineChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
        <XAxis
          dataKey="timestamp"
          tick={{ fontSize: 12 }}
          stroke="#6b7280"
        />
        <YAxis tick={{ fontSize: 12 }} stroke="#6b7280" />
        <Tooltip
          contentStyle={{
            backgroundColor: 'white',
            border: '1px solid #e5e7eb',
            borderRadius: '8px',
          }}
        />
        <Legend />
        <Line
          type="monotone"
          dataKey="metric_1"
          stroke="#3b82f6"
          strokeWidth={2}
          dot={false}
          name="Metric 1"
        />
        <Line
          type="monotone"
          dataKey="metric_2"
          stroke="#10b981"
          strokeWidth={2}
          dot={false}
          name="Metric 2"
        />
        <Line
          type="monotone"
          dataKey="metric_3"
          stroke="#8b5cf6"
          strokeWidth={2}
          dot={false}
          name="Metric 3"
        />
      </RechartsLineChart>
    </ResponsiveContainer>
  );
}