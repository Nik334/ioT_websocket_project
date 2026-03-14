import { IoTData } from '../../types/iotData';
import { Table } from '../ui/Table';

interface DataTableProps {
  data: IoTData[];
}

export function IoTDataTable({ data }: DataTableProps) {
  const columns = [
    {
      key: 'timestamp',
      header: 'Timestamp',
      render: (item: IoTData) => (
        <span className="text-gray-500">
          {new Date(item.timestamp * 1000).toLocaleString()}
        </span>
      ),
    },
    {
      key: 'metric_1',
      header: 'Metric 1',
      render: (item: IoTData) => (
        <span className="font-medium text-blue-600">{item.metric_1.toFixed(2)}</span>
      ),
    },
    {
      key: 'metric_2',
      header: 'Metric 2',
      render: (item: IoTData) => (
        <span className="font-medium text-green-600">{item.metric_2.toFixed(2)}</span>
      ),
    },
    {
      key: 'metric_3',
      header: 'Metric 3',
      render: (item: IoTData) => (
        <span className="font-medium text-purple-600">{item.metric_3.toFixed(2)}</span>
      ),
    },
  ];

  return <Table data={data} columns={columns} keyExtractor={(item) => String(item.timestamp)} />;
}