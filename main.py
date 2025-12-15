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

# predizer uma pasta inteira (imagens)
# vid_stride=15 = processar 1 frame a cada 15 frames em videos
# funciona para videos .mp4, .avi, etc
results = model.predict(source="dataset/testes/", save=True, verbose=True, vid_stride=15)

# Mostrar detecções com confiança
print("\n" + "="*60)
print("DETECÇÕES ENCONTRADAS:")
print("="*60)

for i, result in enumerate(results):
    print(f"\nimagem {i+1}: {result.path}")
    
    if len(result.boxes) == 0:
        print("   nenhum objeto detectado")
    else:
        for j, box in enumerate(result.boxes):
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            class_name = result.names[class_id]
            
            print(f"   caixa {j+1}: {class_name} - {confidence*100:.2f}% de confiança")

print("\n" + "="*60)

# treinar o modelo
#model.train(data='dataset/data.yaml', epochs=20, batch=16, workers=1)
print(f"\nresultados salvos em: {model.predictor.save_dir}")
