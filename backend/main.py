import asyncio
import cv2
from fastapi import FastAPI, WebSocket
from fastapi.responses import Response, StreamingResponse
from threading import Condition, Thread, Lock
from contextlib import asynccontextmanager


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
            self.ref_count -= 1
            if self.ref_count <= 0:
                if self.cap:
                    self.cap.release()
                    self.cap = None
                self.ref_count = 0

    def read(self):
        with self.lock:
            if self.cap and self.cap.isOpened():
                return self.cap.read()
            return False, None


camera = Camera()


class StreamingOutput:
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def update(self, jpeg_bytes):
        with self.condition:
            self.frame = jpeg_bytes
            self.condition.notify_all()

    def read(self):
        with self.condition:
            self.condition.wait()
            return self.frame


class JpegStream:
    def __init__(self):
        self.active = False
        self.connections: set[WebSocket] = set()
        self.output = StreamingOutput()
        self.capture_thread = None

    def _capture_loop(self):
        camera.open()
        try:
            while self.active:
                ret, frame = camera.read()
                if ret:
                    _, buf = cv2.imencode(".jpg", frame)
                    self.output.update(buf.tobytes())
        finally:
            camera.close()

    async def _broadcast_loop(self):
        loop = asyncio.get_event_loop()
        while self.active:
            jpeg_data = await loop.run_in_executor(None, self.output.read)
            for ws in self.connections.copy():
                try:
                    await ws.send_bytes(jpeg_data)
                except Exception:
                    self.connections.discard(ws)

    async def start(self):
        if not self.active:
            self.active = True
            self.capture_thread = Thread(target=self._capture_loop, daemon=True)
            self.capture_thread.start()
            asyncio.create_task(self._broadcast_loop())

    async def stop(self):
        if self.active:
            self.active = False
            if self.capture_thread:
                self.capture_thread.join(timeout=5)
                self.capture_thread = None


jpeg_stream = JpegStream()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await jpeg_stream.stop()


app = FastAPI(lifespan=lifespan)


@app.get("/image")
def get_image():
    camera.open()
    try:
        ret, frame = camera.read()
        if not ret or frame is None:
            return Response(content="Camera unavailable", status_code=503)
        _, buffer = cv2.imencode(".jpg", frame)
        return Response(content=buffer.tobytes(), media_type="image/jpeg")
    finally:
        camera.close()


def generate_frames():
    camera.open()
    try:
        while True:
            ret, frame = camera.read()
            if not ret:
                break
            _, buffer = cv2.imencode(".jpg", frame)
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
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
    if not jpeg_stream.active:
        await jpeg_stream.start()
    try:
        while True:
            await websocket.receive_text()
    except Exception:
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
