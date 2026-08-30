import os
import urllib.parse
import re
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional

from app.extractor import extract_media_info, ExtractorError, get_cached_raw_info
from app.downloader import download_media, cleanup_file, DownloaderError
from app.streamer import get_fast_media_stream, get_content_disposition
from fastapi.responses import StreamingResponse

app = FastAPI(
    title="Universal Social Media Downloader API",
    version="1.0.0",
    description="API for extracting media metadata and downloading audio/video from 1000+ social platforms."
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InfoRequest(BaseModel):
    url: str

class DownloadRequest(BaseModel):
    url: str
    type: str = "video"  # "video" or "audio"
    format_id: Optional[str] = None
    ext: Optional[str] = "mp4"

@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "media-downloader"}

@app.post("/api/info")
async def get_media_info(req: InfoRequest):
    if not req.url or not req.url.strip():
        raise HTTPException(status_code=400, detail={"error": "URL parameter is required."})
    try:
        data = extract_media_info(req.url.strip())
        return data
    except ExtractorError as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})
    except Exception as e:
        raise HTTPException(status_code=400, detail={"error": f"Failed to extract info: {str(e)}"})

@app.get("/api/download")
@app.head("/api/download")
async def download_endpoint_get(
    url: str,
    type: str = "video",
    format_id: Optional[str] = None,
    ext: Optional[str] = "mp4"
):
    if not url or not url.strip():
        raise HTTPException(status_code=400, detail={"error": "URL parameter is required."})

    try:
        stream_gen, filename, media_type_header, content_length = await get_fast_media_stream(
            url=url.strip(),
            media_type=type,
            format_id=format_id,
            ext=ext
        )

        headers = {
            "Content-Disposition": get_content_disposition(filename),
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
        if content_length:
            headers["Content-Length"] = str(content_length)

        return StreamingResponse(
            stream_gen,
            media_type=media_type_header,
            headers=headers
        )
    except DownloaderError as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": f"Download failed: {str(e)}"})

@app.post("/api/download")
async def download_endpoint(req: DownloadRequest):
    if not req.url or not req.url.strip():
        raise HTTPException(status_code=400, detail={"error": "URL is required."})

    try:
        stream_gen, filename, media_type_header, content_length = await get_fast_media_stream(
            url=req.url.strip(),
            media_type=req.type,
            format_id=req.format_id,
            ext=req.ext
        )

        headers = {
            "Content-Disposition": get_content_disposition(filename),
            "Access-Control-Expose-Headers": "Content-Disposition"
        }
        if content_length:
            headers["Content-Length"] = str(content_length)

        return StreamingResponse(
            stream_gen,
            media_type=media_type_header,
            headers=headers
        )
    except DownloaderError as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": f"Download failed: {str(e)}"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
