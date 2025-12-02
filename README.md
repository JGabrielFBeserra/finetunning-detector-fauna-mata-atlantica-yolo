# Fine-tuning Detector de Fauna da Mata Atlântica - YOLOv8

Projeto de detecção e classificação de animais da Mata Atlântica em passagens de fauna utilizando YOLOv8 para estudo.

## 🚀 Setup do Ambiente

### 1. Criar diretório do projeto pra usar e testar
```bash
# 1. Criar Ambiente
python -m venv yolo
cd yolo

# 2. Ativar ambiente
.\Scripts\activate  # Windows

# 3. Clonar Repo
cd finetuning-detector-fauna-mata-atlantica-yolov8
git clone https://github.com/seu-usuario/finetuning-detector-fauna-mata-atlantica-yolov8.git

# 4. Instalar dependências]
pip install -r requirements.txt

# 5. Pronto para usar!
```

## 📊 Preparação do Dataset

> **[EM DESENVOLVIMENTO]**
> 
> Adicionar informações sobre:
> - Coleta de imagens
> - Anotação dos dados
> - Estrutura do dataset
> - Classes de animais

## 🎯 Uso do YOLOv8 via CLI or instrucoes.py

### Detection (Detecção de Objetos)
```bash
# Fazer predições | modelo yolov8x.pt usado para deteccao
yolo task=detect mode=predict model=yolov8x.pt source="images/image.jpeg"
```

### Segmentation (Segmentação)
```bash 
# Fazer predições | modelo yolov8x-seg.pt para segmentacao
yolo task=segment mode=predict model=yolov8x-seg.pt source="images/image.jpeg"
```

### Classification (Classificação)
```bash
# Fazer predições
yolo task=classify mode=predict model=yolov8x-cls.pt source="images/image.jpeg"
```

## 🔬 Fine-tuning

> **[EM DESENVOLVIMENTO]**
>
> Adicionar:
> - Parâmetros de treinamento
> - Augmentação de dados
> - Métricas de avaliação
> - Resultados

## 📁 Estrutura do Projeto

```
yolo/
├── data/               # Dataset e configurações
├── images/            # Imagens para inferência
├── runs/              # Resultados dos treinamentos
│   ├── detect/
│   ├── segment/
│   └── classify/
├── models/            # Modelos treinados
└── README.md
```

## 🐆 Espécies Identificadas

> **[EM DESENVOLVIMENTO]**
>
> Lista de animais da Mata Atlântica a serem identificados:
> - [ ] Bicho-Preguica
> - [ ] Cachorro
> - [ ] Cachorro do Mato
> - [ ] Capivara
> - [ ] Cutia
> - [ ] Gamba'
> - [ ] Gato do Mato
> - [ ] Guaxinim
> - [ ] Lagarto Teiu'
> - [ ] Lobo Guara'
> - [ ] Onca
> - [ ] Oucico Cacheiro
> - [ ] Paca
> - [ ] Tamandu'a Mirim
> - [ ] Tatu

## 📈 Resultados

> **[EM DESENVOLVIMENTO]**

## 🤝 Contribuindo

Contribuições são bem-vindas! Este é um projeto de pesquisa em VLMs e Biologia focado na conservação da fauna da Mata Atlântica.

## 📚 Referências

- [Ultralytics YOLOv8 Documentation](https://docs.ultralytics.com/)
- [YOLOv8 GitHub](https://github.com/ultralytics/ultralytics)
- [Playlist ensinando tudo sobre YOLOV8](https://www.youtube.com/playlist?list=PLv8Cp2NvcY8ClWpGlPJ9tmBmUhlA94Umy)

## 📝 Licença


**Projeto:** Monitoramento de Passagens de Fauna - Mata Atlântica/SP  
**Objetivo:** Classificação automática de animais silvestres para estudos de conservação
