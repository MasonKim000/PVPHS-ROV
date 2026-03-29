This file provides guidance to AI agents when working with code in this repository.

## Project Overview

PVPHS ROV is a remotely operated vehicle control system for a high school robotics team. It runs on a Raspberry Pi with a Python camera backend and a Next.js dashboard frontend.

## Architecture

Two independent applications in one repo:

- `backend/` — FastAPI + OpenCV camera streaming server (Python 3.12, managed with `uv`)
- `frontend/` — Next.js 16 App Router dashboard with shadcn/ui

The frontend proxies `/py/*` requests to the backend at `http://localhost:8000/*` via Next.js rewrites in `next.config.ts`.

## Quick Start (on Raspberry Pi)

```sh
# Backend
git pull
cd backend && uv sync && uv run uvicorn main:app --host 0.0.0.0 --port 8000 --timeout-graceful-shutdown 3

# Frontend
cd frontend && npm ci && npm run dev
```

See `backend/AGENTS.md` and `frontend/AGENTS.md` for app-specific details.
