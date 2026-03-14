import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch

from app.main import app


@pytest.fixture
def mock_db():
    mock = AsyncMock()
    mock.users = AsyncMock()
    mock.iot_data = AsyncMock()
    return mock


@pytest.fixture
def auth_token():
    from app.auth.jwt_handler import create_access_token
    return create_access_token(data={"sub": "admin"})


@pytest.fixture
async def client(mock_db, auth_token):
    with patch("app.database.get_database", return_value=mock_db):
        with patch("app.auth.jwt_handler.verify_token", return_value={"sub": "admin"}):
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                yield ac, mock_db, auth_token


@pytest.mark.asyncio
async def test_login_success():
    with patch("app.config.settings") as mock_settings:
        mock_settings.ADMIN_USERNAME = "admin"
        mock_settings.ADMIN_PASSWORD = "password"
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/auth/login", json={"username": "admin", "password": "password"})
            assert response.status_code == 200
            assert "access_token" in response.json()


@pytest.mark.asyncio
async def test_login_invalid_credentials():
    with patch("app.config.settings") as mock_settings:
        mock_settings.ADMIN_USERNAME = "admin"
        mock_settings.ADMIN_PASSWORD = "password"
        
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/auth/login", json={"username": "admin", "password": "wrong"})
            assert response.status_code == 401