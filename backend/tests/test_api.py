import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock
from app.main import app

@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

@pytest.mark.asyncio
async def test_info_endpoint_success():
    mock_data = {
        "id": "vid123",
        "title": "Test Title",
        "uploader": "Test Channel",
        "duration": 120,
        "thumbnail": "https://img.jpg",
        "webpage_url": "https://youtube.com/watch?v=vid123",
        "platform": "youtube",
        "formats": {"video": [], "audio": []}
    }
    with patch("app.main.extract_media_info", return_value=mock_data):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/api/info", json={"url": "https://youtube.com/watch?v=vid123"})
        assert response.status_code == 200
        assert response.json()["title"] == "Test Title"

@pytest.mark.asyncio
async def test_info_endpoint_invalid_url():
    with patch("app.main.extract_media_info", side_effect=Exception("Invalid URL")):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.post("/api/info", json={"url": "invalid-url"})
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "error" in data["detail"]

@pytest.mark.asyncio
async def test_download_get_endpoint_missing_url():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/api/download?url=")
    assert response.status_code == 400
