# AI Object Detection Guide

## What does this do?

The camera stream can detect objects in real-time using AI (YOLOv8).
When detection is turned on, the camera draws boxes around objects it recognizes
(people, cups, phones, etc.) and labels them on the video stream.

## How it works (simple version)

```
Camera captures a frame (picture)
        |
        v
YOLO AI model looks at the picture
        |
        v
Draws boxes + labels on objects it finds
        |
        v
Sends the annotated picture to your browser
```

**YOLO** (You Only Look Once) is an AI model that can recognize 80+ types of objects.
We use the smallest version called **YOLOv8n** ("n" = nano) so it can run on a Raspberry Pi.

## NCNN - Making it faster

The YOLO model comes in PyTorch format (`.pt`), which is slow on a Raspberry Pi.
We convert it to **NCNN** format, which is optimized for ARM CPUs like the Pi's.

| Format | Speed on Pi |
|--------|-------------|
| `.pt` (PyTorch) | ~1-2 FPS (slideshow) |
| NCNN | ~5-8 FPS (usable) |

To convert (only need to do this once):

```sh
uv run python convert.py
```

This creates a `yolov8n_ncnn_model/` folder that the server uses automatically.

## API Endpoints

| Action | Command |
|--------|---------|
| Turn detection ON | `curl -X POST http://localhost:8000/detect/on` |
| Turn detection OFF | `curl -X POST http://localhost:8000/detect/off` |
| Check status | `curl http://localhost:8000/detect/status` |

Detection is **OFF by default**. Turn it on when you need it.

## Important notes

- Detection uses a lot of CPU (~100%). Turn it off when not needed.
- The model file (`yolov8n.pt`, `yolov8n_ncnn_model/`) is NOT in git. Run `convert.py` on each new Pi.
- YOLO can detect 80 object types (people, cars, animals, furniture, etc.). Full list: https://docs.ultralytics.com/datasets/detect/coco/

## Setup on a new Raspberry Pi

```sh
cd backend
uv sync                       # install all dependencies
apt install -y libgl1          # system library needed by OpenCV
uv run python convert.py       # download + convert YOLO model
uv run uvicorn main:app --host 0.0.0.0 --port 8000  # start server
```
