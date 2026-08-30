import pytest
import os
import tempfile
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock
from app.main import app, get_safe_content_disposition

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
        "title": "Test Title ｜ Artist 🎵",
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
        assert "Test Title" in response.json()["title"]

def test_safe_content_disposition():
    unicode_title = "Song Title ｜ Official Video 🎵 日本語 العربية"
    filename = "Song_Title_Official_Video.mp4"
    header = get_safe_content_disposition(filename, unicode_title)
    
    # Must be encodeable in latin-1 without exception
    header.encode('latin-1')
    assert "filename=" in header
    assert "filename*=" in header

@pytest.mark.asyncio
async def test_download_get_with_unicode_title():
    # Create temporary file
    with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
        tmp.write(b"dummy video content")
        tmp_path = tmp.name

    mock_result = {
        "filepath": tmp_path,
        "filename": "Song_Title.mp4",
        "title": "Song Title ｜ Official Video \uff5c 🎵"
    }

    with patch("app.main.download_media", return_value=mock_result):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/download?url=https://youtube.com/watch?v=test&type=video")
        assert response.status_code == 200
        assert "Content-Disposition" in response.headers
        # Check header latin-1 encodability
        cd = response.headers["Content-Disposition"]
        cd.encode("latin-1")
        assert response.content == b"dummy video content"
