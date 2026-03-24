This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

```sh
uv sync                                             # install dependencies
uv run uvicorn main:app --host 0.0.0.0 --port 8000  # run API server
uv run main.py                                      # single picture capture (script mode)
uv add <package>                                     # add dependency
```

## Tech Stack

- Python 3.12, managed with `uv` (not pip/poetry)
- FastAPI with uvicorn
- OpenCV (`opencv-python-headless`) for camera capture
- WebSocket support via `websockets` package

## Architecture

Single-file application (`main.py`) with three main classes:

- **`Camera`** — Shared OpenCV VideoCapture wrapper with thread-safe ref-counting. Opens device 0 at 1920x1080. Multiple consumers share one capture instance; device releases when ref count hits 0.
- **`StreamingOutput`** — Thread-safe frame buffer using `Condition`. Capture thread writes frames, readers block until notified.
- **`JpegStream`** — Manages WebSocket streaming lifecycle. Runs a background capture thread and an async broadcast loop. Auto-starts on first WebSocket connection, auto-stops when all clients disconnect.

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/image` | Single JPEG snapshot |
| GET | `/mjpeg` | MJPEG continuous stream |
| WS | `/ws` | WebSocket binary JPEG frames |
| POST | `/start` | Manually start capture |
| POST | `/stop` | Manually stop capture |
| GET | `/docs` | FastAPI auto-generated API docs |

## Key Details

- CORS is fully open (`allow_origins=["*"]`) for local network use
- Camera device index is hardcoded to `0`
- The frontend connects to this server via Next.js rewrites (`/py/*` -> `localhost:8000/*`), but WebSocket connects directly to `:8000/ws`
- No test suite configured
