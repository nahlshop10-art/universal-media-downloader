# Universal Social Media Downloader - Specification & Design Document

**Date:** 2026-08-30
**Status:** Approved
**Author:** Antigravity + User

---

## 1. Goal & Vision

Build a responsive, modern, full-stack Universal Social Media Downloader web application capable of extracting media info, previewing content, and downloading video and audio from popular platforms (YouTube, Facebook, Twitter/X, Instagram, TikTok, Reddit, Vimeo, SoundCloud, etc.) with format and quality selection.

---

## 2. Architecture & Tech Stack

### 2.1 Frontend
- **Framework**: Next.js 14+ (App Router, React 18/19, TypeScript)
- **Styling**: Tailwind CSS + Modern Glassmorphism/Dark UI + Lucide Icons
- **Key Views/Components**:
  - `Hero & UrlInput`: Direct URL paste input with automatic platform icon detection.
  - `MediaPreview`: Displays media thumbnail, title, uploader/channel name, duration, and inline preview.
  - `FormatSelector`: Tabs for Video (MP4: 1080p, 720p, 480p, 360p) and Audio (MP3: 320kbps, 256kbps, 128kbps, M4A, WAV).
  - `DownloadProgress`: Status updates and progress indicators with direct browser file download trigger.

### 2.2 Backend
- **Framework**: FastAPI (Python 3.10+) with Uvicorn
- **Media Engine**: `yt-dlp` (regularly updated) + `ffmpeg` for post-processing/transcoding
- **Endpoints**:
  - `GET /api/health` — Health and engine status.
  - `POST /api/info` — Extracts URL metadata, formats, duration, and thumbnail without downloading.
  - `POST /api/download` — Initiates stream/download with selected format ID, streams data, or converts audio to MP3.

---

## 3. Data Contracts

### 3.1 `POST /api/info`
- **Request**:
  ```json
  { "url": "https://www.youtube.com/watch?v=..." }
  ```
- **Response**:
  ```json
  {
    "id": "videoId",
    "title": "Video Title",
    "uploader": "Channel Name",
    "duration": 180,
    "thumbnail": "https://...",
    "platform": "youtube",
    "formats": {
      "video": [
        { "format_id": "137+140", "resolution": "1080p", "ext": "mp4", "filesize": 45000000 },
        { "format_id": "22", "resolution": "720p", "ext": "mp4", "filesize": 25000000 }
      ],
      "audio": [
        { "format_id": "140", "quality": "320kbps", "ext": "mp3" },
        { "format_id": "251", "quality": "128kbps", "ext": "mp3" }
      ]
    }
  }
  ```

### 3.2 `POST /api/download`
- **Request**:
  ```json
  {
    "url": "https://...",
    "type": "video" | "audio",
    "format_id": "137+140",
    "ext": "mp4" | "mp3"
  }
  ```
- **Response**: Binary File Stream (`application/octet-stream` with `Content-Disposition: attachment`).

---

## 4. Error Handling & Edge Cases

1. **Invalid / Private URLs**: Catch `yt-dlp` extraction errors and return a clean HTTP 400 with a user-friendly error message.
2. **Platform Rate-Limiting**: Configure `yt-dlp` headers (user-agent spoofing, geo-bypass options).
3. **Temporary Storage Management**: Any temporary files generated during `ffmpeg` transcoding are cleaned up automatically via Python background tasks after streaming finishes.

---

## 5. Verification Plan

1. **Backend Unit & Integration Tests (`pytest`)**:
   - Test `/api/info` endpoint parsing mock and real URLs.
   - Test `/api/download` endpoint format handling.
2. **Frontend UI Tests (`vitest` / React Testing Library)**:
   - Test URL input validation and platform detection.
   - Test format selection and download button dispatch.
3. **End-to-End Test**:
   - Start backend + frontend, paste a sample link, inspect metadata rendering and trigger download.
