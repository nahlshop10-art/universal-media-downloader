# Universal Social Media Downloader (Audio & Video)

A modern full-stack web application for extracting metadata, previewing media, and downloading high-quality video (MP4) and audio (MP3) from 1,000+ social media and streaming platforms (YouTube, Facebook, Twitter/X, Instagram, TikTok, Reddit, SoundCloud, and more).

---

## 🌟 Key Features

- **Multi-Platform Support**: YouTube, Instagram Reels/Posts, Facebook Videos, Twitter/X Videos, TikTok, SoundCloud, and 1000+ other websites.
- **Video Downloads**: Choose resolutions (1080p, 720p, 480p, 360p MP4).
- **Audio Extraction**: High bitrate MP3 audio conversion (320kbps, 256kbps, 128kbps) via `ffmpeg`.
- **Live Metadata & Previews**: Instant thumbnail display, video title, author, duration, and stream inspection before downloading.
- **Fast & Modern UI**: Dark-mode glassmorphic interface built with Next.js 14, Tailwind CSS, and Lucide icons.
- **REST API**: Powered by FastAPI and asynchronous `yt-dlp`.

---

## 🚀 Quick Start

### 1. Launch Everything with Single Command
```bash
./run.sh
```

- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **Backend API**: [http://localhost:8000](http://localhost:8000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🧪 Testing

### Run Backend Unit & Integration Tests:
```bash
cd backend
./venv/bin/pytest tests/
```

---

## 📁 Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── extractor.py    # yt-dlp metadata extraction & format parsing
│   │   ├── downloader.py   # Streaming media downloader & ffmpeg transcode
│   │   └── main.py         # FastAPI endpoints & CORS configuration
│   ├── tests/
│   │   ├── test_extractor.py
│   │   └── test_api.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/            # Next.js App Router (page.tsx, layout.tsx, globals.css)
│   │   └── components/     # UI Components (Navbar, UrlInput, MediaPreview, FormatSelector)
│   ├── package.json
│   └── tailwind.config.js
├── docs/superpowers/
│   ├── specs/              # Design specification document
│   └── plans/              # Step-by-step implementation plan
└── run.sh                  # One-click startup script
```
