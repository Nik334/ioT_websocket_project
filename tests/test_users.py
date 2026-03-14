import pytest
import time
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock

from app.main import app


def get_auth_header(token: str):
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.asyncio
async def test_create_user():
    mock_db = AsyncMock()
    mock_db.users.find_one = AsyncMock(return_value=None)
    mock_db.users.insert_one = AsyncMock()
    
    with patch("app.routers.users.get_database", return_value=mock_db):
        with patch("app.auth.dependencies.verify_token", return_value={"sub": "admin"}):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                token = "test_token"
                response = await ac.post(
                    "/users",
                    json={"user_id": "U1001", "name": "Test User", "status": "active"},
                    headers=get_auth_header(token)
                )
                assert response.status_code == 201
                assert response.json()["user_id"] == "U1001"


@pytest.mark.asyncio
async def test_create_user_duplicate():
    mock_db = AsyncMock()
    mock_db.users.find_one = AsyncMock(return_value={"_id": "U1001", "name": "Test", "status": "active"})
    
    with patch("app.routers.users.get_database", return_value=mock_db):
        with patch("app.auth.dependencies.verify_token", return_value={"sub": "admin"}):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                token = "test_token"
                response = await ac.post(
                    "/users",
                    json={"user_id": "U1001", "name": "Test User", "status": "active"},
                    headers=get_auth_header(token)
                )
                assert response.status_code == 409


@pytest.mark.asyncio
async def test_get_user():
    mock_db = AsyncMock()
    mock_db.users.find_one = AsyncMock(return_value={"_id": "U1001", "name": "Test User", "status": "active"})
    
    with patch("app.routers.users.get_database", return_value=mock_db):
        with patch("app.auth.dependencies.verify_token", return_value={"sub": "admin"}):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                token = "test_token"
                response = await ac.get("/users/U1001", headers=get_auth_header(token))
                assert response.status_code == 200
                assert response.json()["user_id"] == "U1001"


@pytest.mark.asyncio
async def test_get_user_not_found():
    mock_db = AsyncMock()
    mock_db.users.find_one = AsyncMock(return_value=None)
    
    with patch("app.routers.users.get_database", return_value=mock_db):
        with patch("app.auth.dependencies.verify_token", return_value={"sub": "admin"}):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                token = "test_token"
                response = await ac.get("/users/U9999", headers=get_auth_header(token))
                assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_user():
    mock_db = AsyncMock()
    mock_db.users.find_one = AsyncMock(side_effect=[
        {"_id": "U1001", "name": "Test", "status": "active"},
        {"_id": "U1001", "name": "Updated", "status": "active"}
    ])
    mock_db.users.update_one = AsyncMock()
    
    with patch("app.routers.users.get_database", return_value=mock_db):
        with patch("app.auth.dependencies.verify_token", return_value={"sub": "admin"}):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                token = "test_token"
                response = await ac.put(
                    "/users/U1001",
                    json={"name": "Updated"},
                    headers=get_auth_header(token)
                )
                assert response.status_code == 200
                assert response.json()["name"] == "Updated"