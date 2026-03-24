import asyncio
import os
import cv2
import numpy as np
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse
from threading import Condition, Event, Thread, Lock
from contextlib import asynccontextmanager
from ultralytics import YOLO


MODEL_PATH = os.path.join(os.path.dirname(__file__), "yolov8n_ncnn_model")
if not os.path.exists(MODEL_PATH):
  MODEL_PATH = os.path.join(os.path.dirname(__file__), "yolov8n.pt")


class Detector:
  """YOLOv8 object detector. Lazy-loads model on first enable."""

  INFER_SIZE = 640

  def __init__(self):
    self.model = None
    self.enabled = False

  def _ensure_model(self):
    if self.model is None:
      self.model = YOLO(MODEL_PATH)

  def enable(self):
    self._ensure_model()
    self.enabled = True

  def disable(self):
    self.enabled = False

  def annotate(self, frame: np.ndarray) -> np.ndarray:
    if not self.enabled:
      return frame
    h, w = frame.shape[:2]
    scale = self.INFER_SIZE / max(h, w)
    small = cv2.resize(frame, (int(w * scale), int(h * scale)))
    results = self.model(small, verbose=False)
    return results[0].plot()


detector = Detector()


class Camera:
  """Shared camera instance to avoid device conflicts."""

  def __init__(self, device: int = 0):
    self.device = device
    self.cap = None
    self.lock = Lock()
    self.ref_count = 0

  def open(self):
    with self.lock:
      if self.cap is None or not self.cap.isOpened():
        self.cap = cv2.VideoCapture(self.device)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
      self.ref_count += 1

  def close(self):
    with self.lock:
      self.ref_count = max(0, self.ref_count - 1)
      if self.ref_count == 0 and self.cap:
        self.cap.release()
        self.cap = None

  def read_frame(self) -> np.ndarray | None:
    with self.lock:
      if not self.cap or not self.cap.isOpened():
        return None
      ret, frame = self.cap.read()
      if not ret or frame is None:
        return None
      return frame

  def read_jpeg(self) -> bytes | None:
    frame = self.read_frame()
    if frame is None:
      return None
    frame = detector.annotate(frame)
    _, buf = cv2.imencode(".jpg", frame)
    return buf.tobytes()


camera = Camera()


class StreamingOutput:
  def __init__(self):
    self.frame = None
    self.condition = Condition()

  def update(self, jpeg_bytes: bytes):
    with self.condition:
      self.frame = jpeg_bytes
      self.condition.notify_all()

  def read(self, timeout: float = 1.0) -> bytes | None:
    with self.condition:
      if not self.condition.wait(timeout=timeout):
        return None
      return self.frame


class JpegStream:
  def __init__(self):
    self.stop_event = Event()
    self.connections: set[WebSocket] = set()
    self.output = StreamingOutput()
    self.capture_thread: Thread | None = None
    self.broadcast_task: asyncio.Task | None = None

  @property
  def active(self) -> bool:
    return not self.stop_event.is_set()

  def _capture_loop(self):
    camera.open()
    try:
      while not self.stop_event.is_set():
        jpeg = camera.read_jpeg()
        if jpeg:
          self.output.update(jpeg)
    finally:
      camera.close()

  async def _broadcast_loop(self):
    loop = asyncio.get_running_loop()
    while not self.stop_event.is_set():
      jpeg_data = await loop.run_in_executor(None, self.output.read)
      if jpeg_data is None:
        continue
      tasks = [
          ws.send_bytes(jpeg_data) for ws in self.connections.copy()
      ]
      if tasks:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for ws, result in zip(self.connections.copy(), results):
          if isinstance(result, Exception):
            self.connections.discard(ws)

  async def start(self):
    if not self.stop_event.is_set():
      return
    self.stop_event.clear()
    self.capture_thread = Thread(target=self._capture_loop, daemon=True)
    self.capture_thread.start()
    self.broadcast_task = asyncio.create_task(self._broadcast_loop())

  async def stop(self):
    if self.stop_event.is_set():
      return
    self.stop_event.set()
    if self.capture_thread:
      self.capture_thread.join(timeout=5)
      self.capture_thread = None
    if self.broadcast_task:
      await self.broadcast_task
      self.broadcast_task = None


jpeg_stream = JpegStream()
jpeg_stream.stop_event.set()


@asynccontextmanager
async def lifespan(app: FastAPI):
  yield
  await jpeg_stream.stop()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/image")
def get_image():
  camera.open()
  try:
    jpeg = camera.read_jpeg()
    if jpeg is None:
      return Response(content="Camera unavailable", status_code=503)
    return Response(content=jpeg, media_type="image/jpeg")
  finally:
    camera.close()


def generate_frames():
  camera.open()
  try:
    while True:
      jpeg = camera.read_jpeg()
      if jpeg is None:
        break
      yield (
          b"--frame\r\n"
          b"Content-Type: image/jpeg\r\n\r\n" + jpeg + b"\r\n"
      )
  finally:
    camera.close()


@app.get("/mjpeg")
def mjpeg():
  return StreamingResponse(
      generate_frames(),
      media_type="multipart/x-mixed-replace; boundary=frame",
  )


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
  await websocket.accept()
  jpeg_stream.connections.add(websocket)
  if jpeg_stream.stop_event.is_set():
    await jpeg_stream.start()
  try:
    while True:
      await websocket.receive_text()
  except WebSocketDisconnect:
    pass
  finally:
    jpeg_stream.connections.discard(websocket)
    if not jpeg_stream.connections:
      await jpeg_stream.stop()


@app.post("/start")
async def start_stream():
  await jpeg_stream.start()
  return {"message": "Stream started"}


@app.post("/stop")
async def stop_stream():
  await jpeg_stream.stop()
  return {"message": "Stream stopped"}


@app.post("/detect/on")
def detect_on():
  detector.enable()
  return {"detection": True}


@app.post("/detect/off")
def detect_off():
  detector.disable()
  return {"detection": False}


@app.get("/detect/status")
def detect_status():
  return {"detection": detector.enabled}
