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
    duration = info.get('duration', 0) or 0

    # Extract all real video resolutions available for this specific media
    video_map: Dict[str, Dict[str, Any]] = {}
    audio_map: Dict[str, Dict[str, Any]] = {}

    for f in raw_formats:
        vcodec = f.get('vcodec', 'none')
        acodec = f.get('acodec', 'none')
        ext = f.get('ext', 'mp4')
        format_id = f.get('format_id')
        height = f.get('height')

        # 1. Video formats
        if vcodec != 'none' and height and height >= 144:
            res_label = f"{height}p"
            if height >= 2160:
                res_label = "2160p (4K)"
            elif height >= 1440:
                res_label = "1440p (2K)"
            elif height == 1080:
                res_label = "1080p (Full HD)"
            elif height == 720:
                res_label = "720p (HD)"

            # Estimate or get file size
            size = f.get('filesize') or f.get('filesize_approx')
            if not size and f.get('tbr') and duration > 0:
                size = int((f.get('tbr') * 1024 / 8) * duration)
            elif not size and f.get('vbr') and duration > 0:
                size = int(((f.get('vbr') + 128) * 1024 / 8) * duration)

            # Prioritize MP4 formats and higher bitrates for each resolution
            if res_label not in video_map or (ext == 'mp4' and video_map[res_label]['ext'] != 'mp4'):
                video_map[res_label] = {
                    "format_id": format_id,
                    "resolution": res_label,
                    "height": height,
                    "ext": ext,
                    "filesize": size,
                    "filesize_str": format_filesize(size),
                    "note": f.get('format_note') or f"{height}p",
                    "has_audio": acodec != 'none'
                }

        # 2. Audio formats
        if acodec != 'none' and vcodec == 'none':
            abr = int(f.get('abr') or 128)
            if abr > 0:
                quality_label = f"{abr} kbps"
                size = f.get('filesize') or f.get('filesize_approx')
                if not size and duration > 0:
                    size = int((abr * 1024 / 8) * duration)

                if quality_label not in audio_map or abr > audio_map[quality_label]['abr']:
                    audio_map[quality_label] = {
                        "format_id": format_id,
                        "ext": "mp3",
                        "quality": quality_label,
                        "abr": abr,
                        "filesize": size,
                        "filesize_str": format_filesize(size),
                    }

    # Sort video resolutions descending (4K -> 1080p -> 720p -> 480p -> 360p -> 240p -> 144p)
    video_formats = sorted(video_map.values(), key=lambda x: x.get('height', 0), reverse=True)

    # Sort audio formats descending (320kbps -> 256kbps -> 192kbps -> 128kbps -> 64kbps)
    audio_formats = sorted(audio_map.values(), key=lambda x: x.get('abr', 0), reverse=True)

    # If platform only has single audio stream or none separated, provide standard high-quality MP3 presets
    if not audio_formats:
        presets = [
            ("320 kbps (Studio MP3)", 320),
            ("256 kbps (High Quality MP3)", 256),
            ("192 kbps (Standard MP3)", 192),
            ("128 kbps (Compact MP3)", 128)
        ]
        for label, abr in presets:
            est_size = int((abr * 1024 / 8) * duration) if duration > 0 else None
            audio_formats.append({
                "format_id": "bestaudio/best",
                "ext": "mp3",
                "quality": label,
                "abr": abr,
                "filesize": est_size,
                "filesize_str": format_filesize(est_size)
            })

    # If platform only has single video format (like direct TikTok/Instagram/Facebook mp4)
    if not video_formats:
        best_size = info.get('filesize') or info.get('filesize_approx')
        video_formats.append({
            "format_id": "bestvideo+bestaudio/best",
            "resolution": "Original / Best Quality",
            "height": info.get('height') or 1080,
            "ext": "mp4",
            "filesize": best_size,
            "filesize_str": format_filesize(best_size),
            "note": "HD Video",
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
