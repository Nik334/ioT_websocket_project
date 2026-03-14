import pytest
import json
import time
from unittest.mock import AsyncMock, patch

from app.services.websocket_manager import WebSocketManager


@pytest.mark.asyncio
async def test_websocket_manager_connect():
    manager = WebSocketManager()
    mock_websocket = AsyncMock()
    await manager.connect(mock_websocket)
    assert mock_websocket in manager._connections


@pytest.mark.asyncio
async def test_websocket_manager_subscribe():
    manager = WebSocketManager()
    mock_websocket = AsyncMock()
    await manager.subscribe(mock_websocket, "U1001")
    assert mock_websocket in manager._subscriptions["U1001"]


@pytest.mark.asyncio
async def test_websocket_manager_unsubscribe():
    manager = WebSocketManager()
    mock_websocket = AsyncMock()
    await manager.subscribe(mock_websocket, "U1001")
    await manager.unsubscribe(mock_websocket, "U1001")
    assert mock_websocket not in manager._subscriptions["U1001"]


@pytest.mark.asyncio
async def test_websocket_manager_disconnect():
    manager = WebSocketManager()
    mock_websocket = AsyncMock()
    await manager.connect(mock_websocket)
    await manager.subscribe(mock_websocket, "U1001")
    manager.disconnect(mock_websocket)
    assert mock_websocket not in manager._connections
    assert mock_websocket not in manager._subscriptions.get("U1001", set())


@pytest.mark.asyncio
async def test_websocket_manager_broadcast():
    manager = WebSocketManager()
    mock_websocket = AsyncMock()
    await manager.subscribe(mock_websocket, "U1001")
    test_data = {"metric_1": 45.2, "metric_2": 88, "timestamp": 1234567890}
    await manager.broadcast("U1001", test_data)
    mock_websocket.send_text.assert_called_once()


@pytest.mark.asyncio
async def test_websocket_manager_broadcast_no_subscribers():
    manager = WebSocketManager()
    test_data = {"metric_1": 45.2, "metric_2": 88, "timestamp": 1234567890}
    await manager.broadcast("U1001", test_data)


def get_auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_websocket_ingest_invalid_token():
    from fastapi import WebSocket
    from app.websockets.ingest import websocket_ingest
    
    mock_websocket = AsyncMock(spec=WebSocket)
    mock_websocket.close = AsyncMock()
    
    with patch("app.auth.jwt_handler.verify_token", return_value=None):
        await websocket_ingest(mock_websocket, token="invalid")
        mock_websocket.close.assert_called_once_with(code=4001)