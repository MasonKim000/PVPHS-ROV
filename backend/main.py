import asyncio
import cv2
from fastapi import FastAPI, WebSocket
from fastapi.responses import Response, StreamingResponse
from threading import Condition, Thread
from contextlib import asynccontextmanager


class StreamingOutput:
    def __init__(self):
        self.frame = None
        self.condition = Condition()

    def update(self, frame):
        with self.condition:
            _, buf = cv2.imencode(".jpg", frame)
            self.frame = buf.tobytes()
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
        cap = cv2.VideoCapture(0)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        try:
            while self.active:
                ret, frame = cap.read()
                if ret:
                    self.output.update(frame)
        finally:
            cap.release()

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
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    _, buffer = cv2.imencode(".jpg", frame)
    return Response(content=buffer.tobytes(), media_type="image/jpeg")


def generate_frames():
    cap = cv2.VideoCapture(0)
    while True:
        ret, frame = cap.read()
        _, buffer = cv2.imencode(".jpg", frame)
        yield (
            b"--frame\r\n"
            b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n"
        )


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
