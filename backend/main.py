import cv2
from fastapi import FastAPI
from fastapi.responses import Response

app = FastAPI()


@app.get("/image")
def get_image():
    cap = cv2.VideoCapture(0)
    ret, frame = cap.read()
    cap.release()
    _, buffer = cv2.imencode(".jpg", frame)
    return Response(content=buffer.tobytes(), media_type="image/jpeg")
