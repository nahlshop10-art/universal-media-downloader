# Universal Social Media Downloader Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a full-stack web application to extract and download audio & video from all major social media platforms (YouTube, Facebook, Twitter/X, Instagram, TikTok, etc.) with quality/format options and real-time preview.

**Architecture:** Next.js (TypeScript, Tailwind CSS, Lucide Icons) frontend with a FastAPI (Python, `yt-dlp`, `ffmpeg`) backend service. Asynchronous metadata extraction and streaming media downloads with automated cleanup.

**Tech Stack:** Python 3.10+, FastAPI, Uvicorn, yt-dlp, ffmpeg, Next.js 14, React 18, Tailwind CSS, TypeScript, Axios.

**Spec:** [`docs/superpowers/specs/2026-08-30-universal-media-downloader-design.md`](file:///root/Documents/antigravity/busy-pythagoras/docs/superpowers/specs/2026-08-30-universal-media-downloader-design.md)

## Global Constraints
- Python backend in `/backend`, Next.js frontend in `/frontend`.
- Complete error handling for invalid/unsupported/private URLs.
- Test-driven: Backend tests in `/backend/tests`, Frontend tests in `/frontend/__tests__`.

---

### Task 1: Backend Foundation & Media Extractor (`yt-dlp`)

**Files:**
- Create: `backend/requirements.txt`
- Create: `backend/app/extractor.py`
- Create: `backend/tests/test_extractor.py`

**Interfaces:**
- Produces: `extract_media_info(url: str) -> dict` returning sanitized metadata and formats.

- [ ] **Step 1: Write failing test for media extraction**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Implement `extractor.py` with `yt-dlp` integration**
- [ ] **Step 4: Run tests and ensure 100% pass**
- [ ] **Step 5: Commit changes**

---

### Task 2: FastAPI REST API & Streaming Downloader

**Files:**
- Create: `backend/app/downloader.py`
- Create: `backend/app/main.py`
- Create: `backend/tests/test_api.py`

**Interfaces:**
- Produces: `POST /api/info` and `POST /api/download` endpoints.

- [ ] **Step 1: Write failing API route integration tests**
- [ ] **Step 2: Run test to verify it fails**
- [ ] **Step 3: Implement `main.py` and `downloader.py` with streaming file responses and cleanup**
- [ ] **Step 4: Run tests and ensure all pass**
- [ ] **Step 5: Commit changes**

---

### Task 3: Next.js Frontend Scaffolding & Design System

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/src/app/layout.tsx`
- Create: `frontend/src/app/globals.css`
- Create: `frontend/src/components/Navbar.tsx`

- [ ] **Step 1: Set up Next.js configuration and Tailwind CSS styling**
- [ ] **Step 2: Implement responsive layout and modern dark-mode header**
- [ ] **Step 3: Verify build and component rendering**
- [ ] **Step 4: Commit changes**

---

### Task 4: Interactive Downloader UI (Input, Preview & Format Selector)

**Files:**
- Create: `frontend/src/components/UrlInput.tsx`
- Create: `frontend/src/components/MediaPreview.tsx`
- Create: `frontend/src/components/FormatSelector.tsx`
- Create: `frontend/src/components/DownloadStatus.tsx`
- Create: `frontend/src/app/page.tsx`

- [ ] **Step 1: Build URL input with auto platform badge detection**
- [ ] **Step 2: Build MediaPreview card with thumbnail, duration, and title**
- [ ] **Step 3: Build FormatSelector tabs for Video (MP4) and Audio (MP3)**
- [ ] **Step 4: Wire download triggers with progress feedback**
- [ ] **Step 5: Verify full user flow and test UI interactions**
- [ ] **Step 6: Commit changes**

---

### Task 5: End-to-End Verification & Documentation

**Files:**
- Create: `README.md`
- Create: `run.sh`

- [ ] **Step 1: Write end-to-end launch script (`run.sh`)**
- [ ] **Step 2: Execute full stack tests and verify live download flows**
- [ ] **Step 3: Commit and document project usage**
