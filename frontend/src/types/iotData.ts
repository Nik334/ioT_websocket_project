export interface IoTData {
  user_id: string;
  metric_1: number;
  metric_2: number;
  metric_3: number;
  timestamp: number;
}

export interface IoTDataBrief {
  metric_1: number;
  metric_2: number;
  metric_3: number;
  timestamp: number;
}

export interface WebSocketMessage {
  event: string;
  data: IoTData;
}