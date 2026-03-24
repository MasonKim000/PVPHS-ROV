from ultralytics import YOLO

model = YOLO("yolov8n.pt")
model.export(format="ncnn")  # creates 'yolov8n_ncnn_model/'
