from ultralytics import YOLO
import cv2
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading


class VideoAnnotatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("anotador de videos - yolo")
        self.root.geometry("700x600")
        
        self.model_path = tk.StringVar(value="yolov8n-detector-gamba.pt")
        self.video_path = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.confidence_threshold = tk.DoubleVar(value=0.50)
        
        self.is_processing = False
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # MODELO
        ttk.Label(main_frame, text="modelo (.pt):", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        model_frame = ttk.Frame(main_frame)
        model_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Entry(model_frame, textvariable=self.model_path, width=55).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(model_frame, text="procurar", command=self.browse_model).pack(side=tk.LEFT, padx=5)
        
        # VIDEO DE ENTRADA
        ttk.Label(main_frame, text="video de entrada:", font=("Arial", 9, "bold")).grid(row=2, column=0, sticky=tk.W, pady=(15, 5))
        
        video_frame = ttk.Frame(main_frame)
        video_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Entry(video_frame, textvariable=self.video_path, width=55).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(video_frame, text="procurar", command=self.browse_video).pack(side=tk.LEFT, padx=5)
        
        # PASTA DE DESTINO
        ttk.Label(main_frame, text="pasta de destino:", font=("Arial", 9, "bold")).grid(row=4, column=0, sticky=tk.W, pady=(15, 5))
        
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Entry(output_frame, textvariable=self.output_folder, width=55).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="procurar", command=self.browse_output).pack(side=tk.LEFT, padx=5)
        
        # THRESHOLD DE CONFIANÇA
        confidence_frame = ttk.LabelFrame(main_frame, text="🎯 limiar de confiança", padding="10")
        confidence_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=(15, 5))
        
        slider_frame = ttk.Frame(confidence_frame)
        slider_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(slider_frame, text="0%", font=("Arial", 8)).pack(side=tk.LEFT, padx=5)
        
        self.confidence_scale = tk.Scale(
            slider_frame,
            from_=0.0,
            to=1.0,
            resolution=0.01,
            orient=tk.HORIZONTAL,
            variable=self.confidence_threshold,
            command=self.update_confidence_label,
            showvalue=False
        )
        self.confidence_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        ttk.Label(slider_frame, text="100%", font=("Arial", 8)).pack(side=tk.LEFT, padx=5)
        
        self.confidence_label = ttk.Label(
            confidence_frame, 
            text="50% (0.50)", 
            foreground="blue",
            font=("Arial", 10, "bold")
        )
        self.confidence_label.pack(pady=5)
        
        ttk.Label(
            confidence_frame, 
            text="apenas detecções com confiança >= limiar serão anotadas",
            font=("Arial", 8),
            foreground="gray"
        ).pack()
        
        # INFORMAÇÕES
        info_frame = ttk.LabelFrame(main_frame, text="ℹ️ informações", padding="10")
        info_frame.grid(row=7, column=0, sticky=(tk.W, tk.E), pady=15)
        
        ttk.Label(info_frame, text="• processa 2 frames por segundo (mais rápido)", font=("Arial", 8)).pack(anchor=tk.W)
        ttk.Label(info_frame, text="• as detecções do YOLO serão desenhadas nos frames processados", font=("Arial", 8)).pack(anchor=tk.W)
        ttk.Label(info_frame, text="• o vídeo anotado será salvo na pasta de destino", font=("Arial", 8)).pack(anchor=tk.W)
        ttk.Label(info_frame, text="• nome do arquivo: <original>_anotado.mp4", font=("Arial", 8)).pack(anchor=tk.W)
        
        # BOTÃO PROCESSAR
        self.process_button = ttk.Button(
            main_frame, 
            text="🚀 PROCESSAR E SALVAR VIDEO", 
            command=self.start_processing,
            style='Accent.TButton'
        )
        self.process_button.grid(row=8, column=0, pady=20)
        
        # BARRA DE PROGRESSO
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate', length=600)
        self.progress_bar.grid(row=9, column=0, sticky=(tk.W, tk.E), pady=5)
        
        # STATUS
        self.status_label = ttk.Label(
            main_frame, 
            text="configure as opções acima e clique em processar", 
            foreground="blue",
            font=("Arial", 9)
        )
        self.status_label.grid(row=10, column=0, sticky=tk.W, pady=5)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
    
    def update_confidence_label(self, value):
        """atualiza o label do threshold de confiança"""
        threshold = float(value)
        percentage = int(threshold * 100)
        self.confidence_label.config(text=f"{percentage}% ({threshold:.2f})")
    
    def browse_model(self):
        file_path = filedialog.askopenfilename(
            title="selecionar modelo yolo",
            filetypes=[("modelo yolo", "*.pt"), ("todos os arquivos", "*.*")]
        )
        if file_path:
            self.model_path.set(file_path)
    
    def browse_video(self):
        file_path = filedialog.askopenfilename(
            title="selecionar video",
            filetypes=[
                ("videos", "*.mp4 *.avi *.mov *.mkv *.MP4 *.AVI *.MOV *.MKV"),
                ("todos os arquivos", "*.*")
            ]
        )
        if file_path:
            self.video_path.set(file_path)
    
    def browse_output(self):
        folder = filedialog.askdirectory(title="selecionar pasta de destino")
        if folder:
            self.output_folder.set(folder)
    
    def start_processing(self):
        if self.is_processing:
            messagebox.showwarning("aviso", "já existe um processamento em andamento")
            return
        
        # VALIDAÇÕES
        model_path = self.model_path.get()
        if not model_path or not Path(model_path).exists():
            messagebox.showerror("erro", "selecione um modelo válido")
            return
        
        video_path = self.video_path.get()
        if not video_path or not Path(video_path).exists():
            messagebox.showerror("erro", "selecione um vídeo válido")
            return
        
        output_folder = self.output_folder.get()
        if not output_folder or not Path(output_folder).exists():
            messagebox.showerror("erro", "selecione uma pasta de destino válida")
            return
        
        self.is_processing = True
        self.process_button.config(state='disabled')
        self.progress_bar['value'] = 0
        
        # PROCESSA EM THREAD SEPARADA
        thread = threading.Thread(target=self.process_video, daemon=True)
        thread.start()
    
    def update_progress(self, value, status_text):
        """atualiza barra de progresso e status"""
        self.progress_bar['value'] = value
        self.status_label.config(text=status_text)
        self.root.update_idletasks()
    
    def process_video(self):
        try:
            model_path = self.model_path.get()
            video_path = self.video_path.get()
            output_folder = self.output_folder.get()
            threshold = self.confidence_threshold.get()
            
            self.update_progress(0, "carregando modelo...")
            print(f"\n{'='*70}")
            print(f"PROCESSANDO VIDEO COM ANOTAÇÕES")
            print(f"{'='*70}")
            print(f"modelo: {Path(model_path).name}")
            print(f"video: {Path(video_path).name}")
            print(f"threshold: {threshold:.2f} ({threshold*100:.0f}%)")
            print(f"{'='*70}\n")
            
            # CARREGA MODELO
            model = YOLO(model_path)
            
            # ABRE VIDEO DE ENTRADA
            self.update_progress(5, "abrindo vídeo...")
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                messagebox.showerror("erro", "não foi possível abrir o vídeo")
                return
            
            # PROPRIEDADES DO VIDEO
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            print(f"propriedades do vídeo:")
            print(f"  • resolução: {width}x{height}")
            print(f"  • fps: {fps:.2f}")
            print(f"  • total de frames: {total_frames}")
            print(f"  • duração: {total_frames/fps:.2f}s")
            
            # CALCULA FRAME SKIP (2 FRAMES POR SEGUNDO)
            process_fps = 2  # processar 2 frames por segundo
            frame_skip = int(fps / process_fps)
            expected_processed = int(total_frames / frame_skip)
            print(f"  • frame skip: 1 a cada {frame_skip} frames")
            print(f"  • frames que serão processados: ~{expected_processed}\n")
            
            # NOME DO ARQUIVO DE SAIDA
            video_name = Path(video_path).stem
            output_path = Path(output_folder) / f"{video_name}_anotado.mp4"
            
            # Verifica se arquivo já existe
            if output_path.exists():
                print(f"⚠️ arquivo já existe, será sobrescrito: {output_path.name}\n")
            
            # CODEC E VIDEOWRITER
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # codec MP4
            out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
            
            if not out.isOpened():
                messagebox.showerror("erro", "não foi possível criar o vídeo de saída")
                cap.release()
                return
            
            self.update_progress(10, "processando frames...")
            
            frame_count = 0
            processed_count = 0
            detection_count = 0
            last_annotated_frame = None
            
            while cap.isOpened():
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # PROCESSA APENAS A CADA frame_skip FRAMES (2 POR SEGUNDO)
                if frame_count % frame_skip == 0:
                    # PROCESSA FRAME COM YOLO
                    results = model(frame, imgsz=1920, verbose=False, conf=threshold)
                    
                    # DESENHA ANOTAÇÕES
                    last_annotated_frame = results[0].plot()
                    processed_count += 1
                    
                    # CONTA DETECÇÕES
                    if len(results[0].boxes) > 0:
                        detection_count += 1
                        for box in results[0].boxes:
                            class_id = int(box.cls[0])
                            confidence = float(box.conf[0])
                            class_name = results[0].names[class_id]
                            print(f"frame {frame_count}: 🎯 {class_name} - {confidence*100:.1f}%")
                
                # SALVA FRAME ANOTADO (usa último frame processado se não processou este)
                if last_annotated_frame is not None:
                    out.write(last_annotated_frame)
                else:
                    out.write(frame)
                
                frame_count += 1
                
                # ATUALIZA PROGRESSO
                progress = 10 + (frame_count / total_frames * 85)
                self.update_progress(
                    progress,
                    f"processando: {processed_count}/{expected_processed} frames analisados ({progress:.1f}%)"
                )
            
            # LIBERA RECURSOS
            cap.release()
            out.release()
            
            self.update_progress(100, "✅ concluído!")
            
            print(f"\n{'='*70}")
            print(f"PROCESSAMENTO CONCLUÍDO")
            print(f"{'='*70}")
            print(f"frames totais do vídeo: {frame_count}")
            print(f"frames analisados pelo YOLO: {processed_count}")
            print(f"frames com detecções: {detection_count}")
            print(f"vídeo salvo em: {output_path}")
            print(f"{'='*70}\n")
            
            messagebox.showinfo(
                "sucesso",
                f"vídeo processado com sucesso!\n\n"
                f"frames analisados: {processed_count}/{frame_count}\n"
                f"frames com detecções: {detection_count}\n\n"
                f"arquivo salvo:\n{output_path.name}\n\n"
                f"pasta:\n{output_folder}"
            )
            
        except Exception as e:
            print(f"\n❌ ERRO: {str(e)}\n")
            self.update_progress(0, f"erro: {str(e)}")
            messagebox.showerror("erro", f"erro durante processamento:\n\n{str(e)}")
        
        finally:
            self.is_processing = False
            self.process_button.config(state='normal')


def main():
    root = tk.Tk()
    app = VideoAnnotatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
