import pytest
import time
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock

from app.main import app


def get_auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_ingest_valid_iot_data():
    mock_db = AsyncMock()
    mock_db.users.find_one = AsyncMock(return_value={"_id": "U1001", "name": "Test", "status": "active"})
    mock_db.iot_data.insert_one = AsyncMock()
    
    mock_ws_manager = AsyncMock()
    
    with patch("app.routers.iot.get_database", return_value=mock_db):
        with patch("app.auth.dependencies.verify_token", return_value={"sub": "admin"}):
            with patch("app.routers.iot.websocket_manager", mock_ws_manager):
                async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                    token = "test_token"
                    response = await ac.post(
                        "/data",
                        json={
                            "user_id": "U1001",
                            "metric_1": 34.5,
                            "metric_2": 78,
                            "metric_3": 1,
                            "timestamp": int(time.time()) - 100
                        },
                        headers=get_auth_header(token)
                    )
                    assert response.status_code == 201
                    assert response.json()["user_id"] == "U1001"


@pytest.mark.asyncio
async def test_ingest_invalid_metric_1():
    mock_db = AsyncMock()
    mock_db.users.find_one = AsyncMock(return_value={"_id": "U1001", "name": "Test", "status": "active"})
    
    with patch("app.routers.iot.get_database", return_value=mock_db):
        with patch("app.auth.dependencies.verify_token", return_value={"sub": "admin"}):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                token = "test_token"
                response = await ac.post(
                    "/data",
                    json={
                        "user_id": "U1001",
                        "metric_1": 150,
                        "metric_2": 78,
                        "metric_3": 1,
                        "timestamp": int(time.time()) - 100
                    },
                    headers=get_auth_header(token)
                )
                assert response.status_code == 422


@pytest.mark.asyncio
async def test_ingest_future_timestamp():
    mock_db = AsyncMock()
    mock_db.users.find_one = AsyncMock(return_value={"_id": "U1001", "name": "Test", "status": "active"})
    
    with patch("app.routers.iot.get_database", return_value=mock_db):
        with patch("app.auth.dependencies.verify_token", return_value={"sub": "admin"}):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                token = "test_token"
                response = await ac.post(
                    "/data",
                    json={
                        "user_id": "U1001",
                        "metric_1": 34.5,
                        "metric_2": 78,
                        "metric_3": 1,
                        "timestamp": int(time.time()) + 1000
                    },
                    headers=get_auth_header(token)
                )
                assert response.status_code == 422


@pytest.mark.asyncio
async def test_ingest_future_timestamp():
    mock_db = AsyncMock()
    mock_db.users.find_one = AsyncMock(return_value={"_id": "U1001", "name": "Test", "status": "active"})
    
    with patch("app.routers.iot.get_database", return_value=mock_db):
        with patch("app.auth.dependencies.verify_token", return_value={"sub": "admin"}):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                token = "test_token"
                response = await ac.post(
                    "/data",
                    json={
                        "user_id": "U1001",
                        "metric_1": 34.5,
                        "metric_2": 78,
                        "metric_3": 1,
                        "timestamp": int(time.time()) + 1000
                    },
                    headers=get_auth_header(token)
                )
                assert response.status_code == 422


@pytest.mark.asyncio
async def test_ingest_user_not_found():
    mock_db = AsyncMock()
    mock_db.users.find_one = AsyncMock(return_value=None)
    
    with patch("app.routers.iot.get_database", return_value=mock_db):
        with patch("app.auth.dependencies.verify_token", return_value={"sub": "admin"}):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                token = "test_token"
                response = await ac.post(
                    "/data",
                    json={
                        "user_id": "U9999",
                        "metric_1": 34.5,
                        "metric_2": 78,
                        "metric_3": 1,
                        "timestamp": int(time.time()) - 100
                    },
                    headers=get_auth_header(token)
                )
                assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_latest_iot_data():
    mock_db = AsyncMock()
    mock_db.users.find_one = AsyncMock(return_value={"_id": "U1001", "name": "Test", "status": "active"})
    mock_db.iot_data.find_one = AsyncMock(return_value={
        "user_id": "U1001",
        "metric_1": 34.5,
        "metric_2": 78,
        "metric_3": 1,
        "timestamp": 1234567890
    })
    
    with patch("app.routers.iot.get_database", return_value=mock_db):
        with patch("app.auth.dependencies.verify_token", return_value={"sub": "admin"}):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                token = "test_token"
                response = await ac.get("/users/U1001/iot/latest", headers=get_auth_header(token))
                assert response.status_code == 200
                assert response.json()["metric_1"] == 34.5


@pytest.mark.asyncio
async def test_get_iot_history():
    from unittest.mock import Mock
    
    mock_db = Mock()
    mock_db.users = Mock()
    mock_db.users.find_one = AsyncMock(return_value={"_id": "U1001", "name": "Test", "status": "active"})
    mock_db.iot_data = Mock()
    
    class MockCursor:
        def __init__(self, data):
            self._data = data
        
        def sort(self, key, direction):
            return self
        
        def limit(self, n):
            return self
        
        async def to_list(self, length):
            return self._data
    
    mock_cursor = MockCursor([
        {"metric_1": 34.5, "metric_2": 78, "metric_3": 1, "timestamp": 1234567890},
        {"metric_1": 35.0, "metric_2": 80, "metric_3": 2, "timestamp": 1234567880},
    ])
    mock_db.iot_data.find.return_value = mock_cursor
    
    with patch("app.routers.iot.get_database", return_value=mock_db):
        with patch("app.auth.dependencies.verify_token", return_value={"sub": "admin"}):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                token = "test_token"
                response = await ac.get("/users/U1001/iot/history?limit=10", headers=get_auth_header(token))
                assert response.status_code == 200
                assert len(response.json()) == 2