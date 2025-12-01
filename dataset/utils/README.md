# 🎬 Utilitários do Dataset

Scripts auxiliares para preparação do dataset.

## 📹 video_to_frames.py

Extrai frames de vídeos para criar dataset de imagens.

### Características
- Extrai **2 frames por segundo** (configurável)
- Gera nomes com **hash de 4 caracteres** único
- Processa vídeos individuais ou pastas inteiras
- Suporta: MP4, AVI, MOV, MKV, FLV, WMV

### Uso


```bash
python dataset/utils/video_to_frames.py 
```

### Exemplos

**Vídeo de 20 segundos com 2 FPS:**
- Resultado: ~40 imagens

**Vídeo de 60 segundos com 2 FPS:**
- Resultado: ~120 imagens

### Formato de Saída

```
video_abc1_0001.jpg
video_abc1_0002.jpg
video_def2_0003.jpg
...
```

Onde:
- `abc1` = hash único de 4 caracteres
- `0001` = número sequencial do frame

## 🛠️ Dependências

O OpenCV já está instalado no projeto:
```bash
pip install opencv-python
```
