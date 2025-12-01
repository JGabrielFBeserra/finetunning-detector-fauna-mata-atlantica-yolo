# 📝 Guia de Anotação do Dataset

## 🎯 Estrutura Criada

```
dataset/
├── images/
│   ├── train/    # Coloque suas imagens de treino aqui (80% das imagens)
│   └── val/      # Coloque suas imagens de validação aqui (20% das imagens)
├── labels/
│   ├── train/    # Arquivos .txt com anotações de treino
│   └── val/      # Arquivos .txt com anotações de validação
└── data.yaml     # Configuração do dataset
```

## 🖼️ Passo a Passo

### 1. Coletar Imagens
- Tire fotos ou use imagens de câmeras trap
- Coloque 80% em `images/train/`
- Coloque 20% em `images/val/`

### 2. Anotar com LabelImg ou Roboflow

#### Opção A: LabelImg (Local)
```bash
pip install labelImg
labelImg
```

#### Opção B: Roboflow (Online - Recomendado!)
1. Acesse https://roboflow.com
2. Crie conta gratuita
3. Crie novo projeto
4. Faça upload das imagens
5. Anote diretamente no navegador
6. Exporte no formato YOLO v8

### 3. Formato de Anotação YOLO

Cada imagem `img001.jpg` precisa de um arquivo `img001.txt` com:

```
class_id x_center y_center width height
```

**Exemplo:**
```
0 0.5 0.5 0.3 0.4
1 0.2 0.3 0.15 0.2
```

Onde:
- `class_id`: número da classe (veja data.yaml)
- Todos os valores são **normalizados** (0 a 1)
- `x_center, y_center`: centro do objeto
- `width, height`: largura e altura da bounding box

## 🦁 Classes Configuradas (data.yaml)

```
0: capivara
1: onca-pintada
2: tatu
3: tamandua
4: veado
5: macaco
6: quati
7: anta
```

**Edite `data.yaml` para adicionar/remover classes!**

## ✅ Checklist

- [ ] Coletar imagens
- [ ] Separar treino (80%) e validação (20%)
- [ ] Anotar todas as imagens
- [ ] Verificar se cada .jpg tem seu .txt correspondente
- [ ] Atualizar classes em `data.yaml`
- [ ] Testar com comando de treino

## 🚀 Treinar Depois de Anotar

```bash
yolo detect train data=.\dataset\data.yaml model=yolov8n.pt epochs=100 imgsz=640
```

## 🛠️ Ferramentas Recomendadas

1. **Roboflow** (https://roboflow.com) - Melhor opção!
   - Interface web
   - Colaboração
   - Auto-augmentation
   - Exporta direto para YOLO

2. **LabelImg** - Ferramenta local
3. **CVAT** - Para projetos maiores
4. **Makesense.ai** - Alternativa web gratuita

## 📊 Dicas

- Mínimo: 100 imagens por classe
- Ideal: 500-1000+ imagens por classe
- Variedade: diferentes ângulos, iluminação, poses
- Balanceamento: tente ter número similar de imagens por classe
