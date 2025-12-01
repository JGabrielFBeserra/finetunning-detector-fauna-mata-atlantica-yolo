from ultralytics import YOLO

model = YOLO('yolov8x.pt') # modelo de deteccao
model = YOLO('yolov8x-seg.pt') # modelo de segmentacao
model = YOLO('yolov8x-cls.pt') # modelo de classificao


model.predict(source="images/image.jpeg", save=True)

print(f"Resultados salvos em: {model.predictor.save_dir}")
