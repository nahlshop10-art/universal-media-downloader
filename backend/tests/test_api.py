import pytest
import os
import tempfile
from httpx import AsyncClient, ASGITransport
from unittest.mock import patch, AsyncMock
from app.main import app
from app.streamer import get_content_disposition

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
    header = get_content_disposition(filename, unicode_title)
    
    # Must be encodeable in latin-1 without exception
    header.encode('latin-1')
    assert "filename=" in header
    assert "filename*=" in header

@pytest.mark.asyncio
async def test_download_streaming_response():
    async def dummy_gen():
        yield b"chunk_one"
        yield b"_chunk_two"

    with patch("app.main.get_fast_media_stream", return_value=(dummy_gen(), "song.mp3", "audio/mpeg", 19)):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            response = await ac.get("/api/download?url=https://youtube.com/watch?v=test&type=audio")
        assert response.status_code == 200
        assert "Content-Disposition" in response.headers
        assert response.content == b"chunk_one_chunk_two"
