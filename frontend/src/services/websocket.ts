import { IoTData, WebSocketMessage } from '../types/iotData';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000';

class WebSocketService {
  private sockets: Map<string, WebSocket> = new Map();
  private subscriptions: Map<string, ((data: IoTData) => void)[]> = new Map();

  connect() {
    // Connection is established per-user in subscribe() since backend requires user_id query param
  }

  subscribe(userId: string, callback: (data: IoTData) => void) {
    if (!this.subscriptions.has(userId)) {
      this.subscriptions.set(userId, []);
    }
    this.subscriptions.get(userId)?.push(callback);

    if (!this.sockets.has(userId)) {
      const wsUrlStr = `${WS_URL}/ws/subscribe?user_id=${userId}`;
      const ws = new WebSocket(wsUrlStr);
      
      ws.onopen = () => {
        console.log(`WebSocket connected for user ${userId}`);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as WebSocketMessage;
          if (data.event === 'NEW_DATA') {
            const callbacks = this.subscriptions.get(data.data.user_id) || [];
            callbacks.forEach((cb) => cb(data.data));
          }
        } catch (e) {
          console.error("Failed to parse websocket message", e);
        }
      };

      ws.onclose = () => {
        console.log(`WebSocket disconnected for user ${userId}`);
        this.sockets.delete(userId);
      };

      this.sockets.set(userId, ws);
    }
  }

  unsubscribe(userId: string, callback?: (data: IoTData) => void) {
    const callbacks = this.subscriptions.get(userId);
    if (callbacks) {
      if (callback) {
        const index = callbacks.indexOf(callback);
        if (index > -1) callbacks.splice(index, 1);
      } else {
        this.subscriptions.delete(userId);
      }
    }

    if (!this.subscriptions.has(userId) || this.subscriptions.get(userId)?.length === 0) {
      this.sockets.get(userId)?.close();
      this.subscriptions.delete(userId);
    }
  }

  disconnect() {
    this.sockets.forEach(ws => ws.close());
    this.sockets.clear();
    this.subscriptions.clear();
  }

  isConnected(userId?: string): boolean {
    if (userId) {
      return this.sockets.get(userId)?.readyState === WebSocket.OPEN;
    }
    return this.sockets.size > 0;
  }
}

export const wsService = new WebSocketService();