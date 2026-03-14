import asyncio
import json
from typing import Any

from fastapi import WebSocket


class WebSocketManager:
    def __init__(self):
        self._subscriptions: dict[str, set[WebSocket]] = {}
        self._connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self._connections.add(websocket)

    def disconnect(self, websocket: WebSocket):
        self._connections.discard(websocket)
        for user_id, sockets in self._subscriptions.items():
            sockets.discard(websocket)
        if not self._subscriptions.get(user_id):
            del self._subscriptions[user_id]

    async def subscribe(self, websocket: WebSocket, user_id: str):
        if user_id not in self._subscriptions:
            self._subscriptions[user_id] = set()
        self._subscriptions[user_id].add(websocket)

    async def unsubscribe(self, websocket: WebSocket, user_id: str):
        if user_id in self._subscriptions:
            self._subscriptions[user_id].discard(websocket)

    async def broadcast(self, user_id: str, data: dict[str, Any]):
        if user_id in self._subscriptions:
            message = json.dumps({
                "event": "NEW_DATA",
                "data": data
            })
            disconnected = set()
            for websocket in self._subscriptions[user_id]:
                try:
                    await websocket.send_text(message)
                except Exception:
                    disconnected.add(websocket)
            for ws in disconnected:
                self._subscriptions[user_id].discard(ws)

    async def send_personal(self, websocket: WebSocket, message: str):
        try:
            await websocket.send_text(message)
        except Exception:
            pass


websocket_manager = WebSocketManager()