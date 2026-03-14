import pytest
from unittest.mock import patch, AsyncMock

from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport


@pytest.fixture
def mock_db():
    mock = AsyncMock()
    mock.users = AsyncMock()
    mock.iot_data = AsyncMock()
    return mock


@pytest.fixture
def auth_header():
    from app.auth.jwt_handler import create_access_token
    token = create_access_token(data={"sub": "admin"})
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def client(mock_db):
    with patch("app.database.get_database", return_value=mock_db):
        from app.main import app
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            yield ac, mock_db


@pytest.fixture
async def authenticated_client(mock_db, auth_header):
    with patch("app.database.get_database", return_value=mock_db):
        with patch("app.auth.jwt_handler.verify_token", return_value={"sub": "admin"}):
            from app.main import app
            async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
                yield ac, mock_db, auth_header