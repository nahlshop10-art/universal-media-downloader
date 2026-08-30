import re
import time
import yt_dlp
from typing import Dict, Any, List, Optional

class ExtractorError(Exception):
    """Exception raised when media extraction fails."""
    pass

_INFO_CACHE: Dict[str, Dict[str, Any]] = {}
CACHE_TTL = 300  # 5 minutes cache

def get_cached_raw_info(url: str) -> Optional[Dict[str, Any]]:
    """Retrieve raw yt-dlp info from cache if valid."""
    entry = _INFO_CACHE.get(url)
    if entry and (time.time() - entry["timestamp"] < CACHE_TTL):
        return entry["info"]
    return None

def set_cached_raw_info(url: str, info: Dict[str, Any]):
    """Cache raw yt-dlp info dictionary."""
    if len(_INFO_CACHE) > 100:
        _INFO_CACHE.clear()
    _INFO_CACHE[url] = {
        "info": info,
        "timestamp": time.time()
    }

def detect_platform(url: str) -> str:
    """Identify the source platform from the URL."""
    url_lower = url.lower()
    if "youtube.com" in url_lower or "youtu.be" in url_lower:
        return "youtube"
    elif "instagram.com" in url_lower:
        return "instagram"
    elif "twitter.com" in url_lower or "x.com" in url_lower:
        return "twitter"
    elif "facebook.com" in url_lower or "fb.watch" in url_lower or "fb.com" in url_lower:
        return "facebook"
    elif "tiktok.com" in url_lower:
        return "tiktok"
    elif "reddit.com" in url_lower:
        return "reddit"
    elif "soundcloud.com" in url_lower:
        return "soundcloud"
    elif "vimeo.com" in url_lower:
        return "vimeo"
    return "generic"

def format_filesize(size_bytes: Optional[int]) -> str:
    """Format bytes into readable size string."""
    if not size_bytes or size_bytes <= 0:
        return "N/A"
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"

def extract_media_info(url: str) -> Dict[str, Any]:
    """Extract metadata and available video/audio formats using yt-dlp."""
    cached_info = get_cached_raw_info(url)
    if cached_info:
        info = cached_info
    else:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
            'skip_download': True,
            'socket_timeout': 15,
            'extractor_args': {
                'youtube': {'player_client': ['android', 'web']}
            },
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise ExtractorError("Could not retrieve media info.")
                set_cached_raw_info(url, info)
        except Exception as e:
            raise ExtractorError(f"Extraction failed: {str(e)}")

    platform = detect_platform(url)
    raw_formats = info.get('formats', [])

    video_formats: List[Dict[str, Any]] = []
    audio_formats: List[Dict[str, Any]] = []
    seen_resolutions = set()

    for f in raw_formats:
        vcodec = f.get('vcodec', 'none')
        acodec = f.get('acodec', 'none')
        ext = f.get('ext', 'mp4')
        format_id = f.get('format_id')
        height = f.get('height')
        filesize = f.get('filesize') or f.get('filesize_approx')

        # Video stream
        if vcodec != 'none' and height and height >= 144:
            res_label = f"{height}p"
            if res_label not in seen_resolutions:
                seen_resolutions.add(res_label)
                video_formats.append({
                    "format_id": format_id,
                    "resolution": res_label,
                    "height": height,
                    "ext": ext,
                    "filesize": filesize,
                    "filesize_str": format_filesize(filesize),
                    "note": f.get('format_note', res_label),
                    "has_audio": acodec != 'none'
                })

        # Audio stream
        if acodec != 'none' and vcodec == 'none':
            abr = f.get('abr') or 128
            audio_formats.append({
                "format_id": format_id,
                "ext": "mp3",  # We can convert audio to MP3
                "quality": f"{int(abr)} kbps",
                "abr": abr,
                "filesize": filesize,
                "filesize_str": format_filesize(filesize),
            })

    # Sort video formats descending by resolution height
    video_formats.sort(key=lambda x: x.get('height', 0), reverse=True)
    
    # If no separated audio formats found, provide default best audio option
    if not audio_formats:
        audio_formats.append({
            "format_id": "bestaudio/best",
            "ext": "mp3",
            "quality": "Best Quality (320kbps MP3)",
            "abr": 320,
            "filesize_str": "Dynamic"
        })

    # If no specific video formats, provide best video fallback
    if not video_formats:
        video_formats.append({
            "format_id": "bestvideo+bestaudio/best",
            "resolution": "Highest Quality",
            "height": 1080,
            "ext": "mp4",
            "filesize_str": "Dynamic",
            "note": "Best Available",
            "has_audio": True
        })

    return {
        "id": info.get("id"),
        "title": info.get("title", "Untitled Media"),
        "uploader": info.get("uploader") or info.get("channel") or "Unknown Creator",
        "duration": info.get("duration", 0),
        "thumbnail": info.get("thumbnail"),
        "webpage_url": info.get("webpage_url", url),
        "platform": platform,
        "formats": {
            "video": video_formats,
            "audio": audio_formats
        }
    }
