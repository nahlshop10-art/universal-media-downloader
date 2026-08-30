import pytest
from unittest.mock import patch, MagicMock
from app.extractor import extract_media_info, detect_platform, ExtractorError

def test_detect_platform():
    assert detect_platform("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "youtube"
    assert detect_platform("https://youtu.be/dQw4w9WgXcQ") == "youtube"
    assert detect_platform("https://www.instagram.com/reel/C3_abc123/") == "instagram"
    assert detect_platform("https://twitter.com/user/status/123456789") == "twitter"
    assert detect_platform("https://x.com/user/status/123456789") == "twitter"
    assert detect_platform("https://www.facebook.com/watch/?v=123456") == "facebook"
    assert detect_platform("https://www.tiktok.com/@user/video/123456") == "tiktok"
    assert detect_platform("https://example.com/video") == "generic"

def test_extract_media_info_success():
    mock_info = {
        "id": "test_video_123",
        "title": "Amazing Video Tutorial",
        "uploader": "Tech Channel",
        "duration": 360,
        "thumbnail": "https://img.youtube.com/vi/test_video_123/maxresdefault.jpg",
        "webpage_url": "https://www.youtube.com/watch?v=test_video_123",
        "formats": [
            {
                "format_id": "137",
                "ext": "mp4",
                "resolution": "1920x1080",
                "height": 1080,
                "vcodec": "avc1.640028",
                "acodec": "none",
                "filesize": 50000000,
                "format_note": "1080p"
            },
            {
                "format_id": "22",
                "ext": "mp4",
                "resolution": "1280x720",
                "height": 720,
                "vcodec": "avc1.64001F",
                "acodec": "mp4a.40.2",
                "filesize": 25000000,
                "format_note": "720p"
            },
            {
                "format_id": "140",
                "ext": "m4a",
                "vcodec": "none",
                "acodec": "mp4a.40.2",
                "abr": 128,
                "filesize": 5000000
            }
        ]
    }

    with patch("yt_dlp.YoutubeDL") as mock_ydl_class:
        mock_ydl = MagicMock()
        mock_ydl.extract_info.return_value = mock_info
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl

        result = extract_media_info("https://www.youtube.com/watch?v=test_video_123")

        assert result["id"] == "test_video_123"
        assert result["title"] == "Amazing Video Tutorial"
        assert result["uploader"] == "Tech Channel"
        assert result["duration"] == 360
        assert result["platform"] == "youtube"
        assert len(result["formats"]["video"]) >= 2
        assert len(result["formats"]["audio"]) >= 1

def test_extract_media_info_invalid_url():
    with patch("yt_dlp.YoutubeDL") as mock_ydl_class:
        mock_ydl = MagicMock()
        mock_ydl.extract_info.side_effect = Exception("Unsupported URL or private video")
        mock_ydl_class.return_value.__enter__.return_value = mock_ydl

        with pytest.raises(ExtractorError):
            extract_media_info("https://invalid-video-url-example.com/bad")
