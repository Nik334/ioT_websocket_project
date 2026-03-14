import { clsx } from 'clsx';
import type { IoTDataBrief } from '../../types/iotData';

interface MetricCardProps {
  label: string;
  value: number;
  unit?: string;
  color?: 'blue' | 'green' | 'purple' | 'orange';
}

export function MetricCard({ label, value, unit = '', color = 'blue' }: MetricCardProps) {
  const colors = {
    blue: 'bg-blue-500',
    green: 'bg-green-500',
    purple: 'bg-purple-500',
    orange: 'bg-orange-500',
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <div className="flex items-center gap-3">
        <div className={clsx('w-3 h-3 rounded-full', colors[color])} />
        <span className="text-sm text-gray-500">{label}</span>
      </div>
      <p className="mt-2 text-2xl font-semibold text-gray-900">
        {value.toFixed(1)}
        {unit && <span className="text-sm text-gray-500 ml-1">{unit}</span>}
      </p>
    </div>
  );
}

export function LatestDataCard({ data }: { data: IoTDataBrief }) {
  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
      <h4 className="text-sm font-medium text-gray-500 mb-3">Latest Reading</h4>
      <div className="grid grid-cols-3 gap-4">
        <MetricCard label="Metric 1" value={data.metric_1} color="blue" />
        <MetricCard label="Metric 2" value={data.metric_2} color="green" />
        <MetricCard label="Metric 3" value={data.metric_3} color="purple" />
      </div>
      <p className="mt-3 text-xs text-gray-400">
        Timestamp: {new Date(data.timestamp * 1000).toLocaleString()}
      </p>
    </div>
  );
}