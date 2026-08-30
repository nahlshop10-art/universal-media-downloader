import os
import tempfile
import uuid
import asyncio
import yt_dlp
from typing import Dict, Any, Optional, AsyncGenerator

class DownloaderError(Exception):
    pass

DOWNLOAD_DIR = tempfile.gettempdir()

async def download_media(url: str, media_type: str = "video", format_id: Optional[str] = None) -> Dict[str, Any]:
    """Download media file and return filepath and filename."""
    file_id = str(uuid.uuid4())[:8]
    out_tmpl = os.path.join(DOWNLOAD_DIR, f"download_{file_id}_%(title).50s.%(ext)s")

    ydl_opts: Dict[str, Any] = {
        'outtmpl': out_tmpl,
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 30,
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    }

    if media_type == "audio":
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
        })
    else:
        if format_id and format_id != "auto":
            # If video format without audio is selected, merge with best audio
            ydl_opts['format'] = f"{format_id}+bestaudio/best"
        else:
            ydl_opts['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
        ydl_opts['merge_output_format'] = 'mp4'

    def _sync_download():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if media_type == "audio":
                filename = os.path.splitext(filename)[0] + ".mp3"
            return filename, info.get('title', 'downloaded_media')

    try:
        filepath, title = await asyncio.to_thread(_sync_download)
        if not os.path.exists(filepath):
            # Scan directory for matching prefix
            prefix = f"download_{file_id}_"
            for f in os.listdir(DOWNLOAD_DIR):
                if f.startswith(prefix):
                    filepath = os.path.join(DOWNLOAD_DIR, f)
                    break
        
        if not os.path.exists(filepath):
            raise DownloaderError("Downloaded file could not be located.")

        return {
            "filepath": filepath,
            "filename": os.path.basename(filepath),
            "title": title
        }
    except Exception as e:
        raise DownloaderError(f"Download error: {str(e)}")

async def cleanup_file(filepath: str):
    """Clean up downloaded temporary file after response streaming."""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
    except Exception:
        pass
