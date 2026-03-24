This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PVPHS ROV is a remotely operated vehicle control system for a high school robotics team. It runs on a Raspberry Pi (`192.168.254.245`) with a Python camera backend and a Next.js dashboard frontend.

## Architecture

Two independent applications in one repo:

- `backend/` — FastAPI + OpenCV camera streaming server (Python 3.12, managed with `uv`)
- `frontend/` — Next.js 16 App Router dashboard with shadcn/ui

The frontend proxies `/py/*` requests to the backend at `http://localhost:8000/*` via Next.js rewrites in `next.config.ts`.

**Camera streaming flow:** Backend captures frames via OpenCV and delivers them three ways:

1. Single JPEG snapshot — `GET /image`
2. MJPEG continuous stream — `GET /mjpeg`
3. WebSocket binary frames — `WS /ws` (auto-starts/stops capture based on connected clients)

**Frontend pages:**

- `/` — Landing page
- `/camera` — Live WebSocket camera stream (client component, `react-use-websocket`)
- `/stats` — Raspberry Pi system info (server component, reads CPU/memory/temp)

## Quick Start (on Raspberry Pi)

```sh
# Backend
cd backend && uv sync && uv run uvicorn main:app --host 0.0.0.0 --port 8000 --timeout-graceful-shutdown 3

# Frontend
cd frontend && npm ci && npm run dev
```

## Note

- `frontend/` has its own `.git` directory (separate git history from root)
- See `backend/CLAUDE.md` and `frontend/CLAUDE.md` for app-specific details
