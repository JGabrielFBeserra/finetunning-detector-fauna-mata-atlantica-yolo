from ultralytics import YOLO
import os

#garantindo commit 3

# Garantir que estamos no diretório correto
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

#garantindo o commit dnovo, po to na ccxp vei
# model = YOLO('yolov8x-seg.pt') # modelo de segmentacao
# model = YOLO('yolov8x-cls.pt') # modelo de classificao

model = YOLO('yolo11n-v1.pt') # modelo de deteccao com meu dataset proprio
# predizer uma pasta inteira
model.predict(source="dataset/all-images/Teste", save=True)

# treinar o modelo
#model.train(data='dataset/data.yaml', epochs=20, batch=16, workers=1)
print(f"Resultados salvos em: {model.predictor.save_dir}")
