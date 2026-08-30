import asyncio
import os
import re
import urllib.parse
import httpx
from typing import Dict, Any, Optional, AsyncGenerator, Tuple
from fastapi.responses import StreamingResponse

from app.extractor import get_cached_raw_info, extract_media_info, ExtractorError
from app.downloader import sanitize_filename, download_media

def get_content_disposition(filename: str, title: Optional[str] = None) -> str:
    """Generate RFC 6266 compliant Content-Disposition header with ASCII fallback."""
    ascii_name = re.sub(r'[^\x20-\x7E]', '_', filename)
    ascii_name = re.sub(r'["\\]', '_', ascii_name)
    
    utf8_target = title if title else filename
    ext = os.path.splitext(filename)[1]
    if not utf8_target.endswith(ext):
        utf8_target = f"{utf8_target}{ext}"
    encoded_name = urllib.parse.quote(utf8_target)
    
    return f'attachment; filename="{ascii_name}"; filename*=UTF-8\'\'{encoded_name}'

async def stream_http_chunks(url: str, headers: Dict[str, str]) -> AsyncGenerator[bytes, None]:
    """Stream chunks directly from a remote CDN URL."""
    async with httpx.AsyncClient(headers=headers, timeout=120.0, follow_redirects=True) as client:
        async with client.stream("GET", url) as response:
            response.raise_for_status()
            async for chunk in response.aiter_bytes(chunk_size=65536):
                yield chunk

async def stream_ffmpeg_pipe(cmd: list) -> AsyncGenerator[bytes, None]:
    """Stream chunks directly from a live FFmpeg process stdout."""
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL
    )
    try:
        while True:
            chunk = await proc.stdout.read(65536)
            if not chunk:
                break
            yield chunk
    except asyncio.CancelledError:
        pass
    finally:
        try:
            proc.terminate()
            await proc.wait()
        except Exception:
            pass

async def get_fast_media_stream(
    url: str,
    media_type: str = "video",
    format_id: Optional[str] = None,
    ext: Optional[str] = "mp4"
) -> Tuple[AsyncGenerator[bytes, None], str, str, Optional[int]]:
    """
    Produce an ultra-fast streaming generator, filename, content-type, and optional content-length.
    Returns: (async_generator, filename, media_type_header, content_length)
    """
    raw_info = get_cached_raw_info(url)
    if not raw_info:
        try:
            raw_info = extract_media_info(url)
            # Re-check cache after extraction
            raw_info = get_cached_raw_info(url) or raw_info
        except Exception:
            raw_info = {}

    title = raw_info.get("title", "downloaded_media")
    safe_title = sanitize_filename(title)
    formats = raw_info.get("formats", [])
    http_headers = raw_info.get("http_headers") or {}

    # Audio Download Pipeline
    if media_type == "audio":
        audio_format = None
        for f in formats:
            if f.get("format_id") == format_id and f.get("url"):
                audio_format = f
                break
        
        if not audio_format:
            # Pick best audio stream
            audio_formats = [f for f in formats if f.get("acodec") != "none" and f.get("vcodec") == "none" and f.get("url")]
            if audio_formats:
                # Pick highest abr
                audio_format = max(audio_formats, key=lambda x: x.get("abr") or 0)

        if audio_format and audio_format.get("url"):
            audio_url = audio_format["url"]
            filename = f"{safe_title}.mp3"
            media_type_header = "audio/mpeg"
            
            # Pipe via FFmpeg directly to MP3 stream
            cmd = [
                "ffmpeg", "-y",
                "-i", audio_url,
                "-vn", "-c:a", "libmp3lame", "-q:a", "2",
                "-f", "mp3",
                "pipe:1"
            ]
            return stream_ffmpeg_pipe(cmd), filename, media_type_header, None

    # Video Download Pipeline
    else:
        selected_format = None
        for f in formats:
            if f.get("format_id") == format_id and f.get("url"):
                selected_format = f
                break

        if not selected_format:
            video_formats = [f for f in formats if f.get("vcodec") != "none" and f.get("url")]
            if video_formats:
                selected_format = max(video_formats, key=lambda x: x.get("height") or 0)

        if selected_format and selected_format.get("url"):
            video_url = selected_format["url"]
            filename = f"{safe_title}.mp4"
            media_type_header = "video/mp4"
            has_audio = selected_format.get("acodec") != "none"

            # Case A: Progressive video (has both video & audio) -> Instant Direct CDN stream!
            if has_audio:
                filesize = selected_format.get("filesize") or selected_format.get("filesize_approx")
                req_headers = selected_format.get("http_headers") or http_headers
                return stream_http_chunks(video_url, req_headers), filename, media_type_header, filesize

            # Case B: Video-only stream (e.g. YouTube 1080p DASH) -> Instant live FFmpeg mux
            audio_format = None
            audio_formats = [f for f in formats if f.get("acodec") != "none" and f.get("vcodec") == "none" and f.get("url")]
            if audio_formats:
                audio_format = max(audio_formats, key=lambda x: x.get("abr") or 0)

            if audio_format and audio_format.get("url"):
                audio_url = audio_format["url"]
                cmd = [
                    "ffmpeg", "-y",
                    "-i", video_url,
                    "-i", audio_url,
                    "-c:v", "copy",
                    "-c:a", "aac",
                    "-f", "mp4",
                    "-movflags", "frag_keyframe+empty_moov+default_base_moof",
                    "pipe:1"
                ]
                return stream_ffmpeg_pipe(cmd), filename, media_type_header, None

    # Fallback to standard downloader if direct URL extraction was not possible
    result = await download_media(url=url, media_type=media_type, format_id=format_id)
    filepath = result["filepath"]
    filename = result["filename"]
    media_type_header = "audio/mpeg" if media_type == "audio" else "video/mp4"

    async def file_chunks():
        try:
            with open(filepath, "rb") as f:
                while True:
                    chunk = f.read(65536)
                    if not chunk:
                        break
                    yield chunk
        finally:
            if os.path.exists(filepath):
                try:
                    os.remove(filepath)
                except Exception:
                    pass

    return file_chunks(), filename, media_type_header, None
