import os
import urllib.parse
import re
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, HttpUrl
from typing import Optional

from app.extractor import extract_media_info, ExtractorError
from app.downloader import download_media, cleanup_file, DownloaderError

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

def get_safe_content_disposition(filename: str, title: Optional[str] = None) -> str:
    """Generate RFC 6266 compliant Content-Disposition header with ASCII fallback."""
    # ASCII fallback filename (strictly latin-1 / ASCII safe)
    ascii_name = re.sub(r'[^\x20-\x7E]', '_', filename)
    ascii_name = re.sub(r'["\\]', '_', ascii_name)
    
    # UTF-8 encoded filename
    utf8_target = title if title else filename
    ext = os.path.splitext(filename)[1]
    if not utf8_target.endswith(ext):
        utf8_target = f"{utf8_target}{ext}"
    encoded_name = urllib.parse.quote(utf8_target)
    
    return f'attachment; filename="{ascii_name}"; filename*=UTF-8\'\'{encoded_name}'

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
    ext: Optional[str] = "mp4",
    background_tasks: BackgroundTasks = BackgroundTasks()
):
    if not url or not url.strip():
        raise HTTPException(status_code=400, detail={"error": "URL parameter is required."})

    try:
        result = await download_media(
            url=url.strip(),
            media_type=type,
            format_id=format_id
        )
        filepath = result["filepath"]
        filename = result["filename"]
        title = result.get("title")

        background_tasks.add_task(cleanup_file, filepath)
        media_type_header = "audio/mpeg" if type == "audio" else "video/mp4"

        cd_header = get_safe_content_disposition(filename, title)

        return FileResponse(
            path=filepath,
            filename=filename,
            media_type=media_type_header,
            headers={
                "Content-Disposition": cd_header,
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except DownloaderError as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": f"Download failed: {str(e)}"})

@app.post("/api/download")
async def download_endpoint(req: DownloadRequest, background_tasks: BackgroundTasks):
    if not req.url or not req.url.strip():
        raise HTTPException(status_code=400, detail={"error": "URL is required."})

    try:
        result = await download_media(
            url=req.url.strip(),
            media_type=req.type,
            format_id=req.format_id
        )
        filepath = result["filepath"]
        filename = result["filename"]
        title = result.get("title")

        background_tasks.add_task(cleanup_file, filepath)

        media_type_header = "audio/mpeg" if req.type == "audio" else "video/mp4"
        cd_header = get_safe_content_disposition(filename, title)

        return FileResponse(
            path=filepath,
            filename=filename,
            media_type=media_type_header,
            headers={
                "Content-Disposition": cd_header,
                "Access-Control-Expose-Headers": "Content-Disposition"
            }
        )
    except DownloaderError as e:
        raise HTTPException(status_code=400, detail={"error": str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail={"error": f"Download failed: {str(e)}"})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
