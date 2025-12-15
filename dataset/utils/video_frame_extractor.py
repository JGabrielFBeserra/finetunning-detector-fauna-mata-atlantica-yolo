from ultralytics import YOLO
import cv2
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import random
import string


class VideoFrameExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("extrair frames com deteccoes de videos")
        self.root.geometry("700x500")
        
        self.video_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.model_path = tk.StringVar(value="yolo11n-v1.pt")
        self.confidence_threshold = tk.DoubleVar(value=0.40)
        self.classification_var = tk.StringVar()
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(main_frame, text="modelo (.pt):").grid(row=0, column=0, sticky=tk.W, pady=5)
        model_frame = ttk.Frame(main_frame)
        model_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        ttk.Entry(model_frame, textvariable=self.model_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(model_frame, text="procurar", command=self.browse_model).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(main_frame, text="pasta de videos:").grid(row=2, column=0, sticky=tk.W, pady=5)
        video_frame = ttk.Frame(main_frame)
        video_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        ttk.Entry(video_frame, textvariable=self.video_folder, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(video_frame, text="procurar", command=self.browse_video_folder).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(main_frame, text="pasta de saida:").grid(row=4, column=0, sticky=tk.W, pady=5)
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=5)
        ttk.Entry(output_frame, textvariable=self.output_folder, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="procurar", command=self.browse_output_folder).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(main_frame, text="confianca minima:").grid(row=6, column=0, sticky=tk.W, pady=5)
        conf_frame = ttk.Frame(main_frame)
        conf_frame.grid(row=7, column=0, sticky=(tk.W, tk.E), pady=5)
        ttk.Label(conf_frame, text="0.40 (40%)").pack(side=tk.LEFT, padx=5)
        ttk.Scale(
            conf_frame, 
            from_=0.1, 
            to=0.95, 
            variable=self.confidence_threshold,
            orient=tk.HORIZONTAL,
            length=300
        ).pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.conf_label = ttk.Label(conf_frame, text="0.40")
        self.conf_label.pack(side=tk.LEFT, padx=5)
        self.confidence_threshold.trace_add('write', self.update_conf_label)
        
        ttk.Label(main_frame, text="classificacao dos frames:").grid(row=8, column=0, sticky=tk.W, pady=5)
        classification_combo = ttk.Combobox(
            main_frame,
            textvariable=self.classification_var,
            values=["positivo_positivo", "falso_positivo", "falso_negativo", "negativo_negativo"],
            state="readonly",
            width=30
        )
        classification_combo.grid(row=9, column=0, sticky=(tk.W, tk.E), pady=5)
        classification_combo.current(0)
        
        info_frame = ttk.LabelFrame(main_frame, text="informacao", padding="10")
        info_frame.grid(row=10, column=0, sticky=(tk.W, tk.E), pady=10)
        ttk.Label(info_frame, text="• processa todos os videos da pasta").pack(anchor=tk.W)
        ttk.Label(info_frame, text="• salva 2 versoes de cada frame com deteccao:").pack(anchor=tk.W)
        ttk.Label(info_frame, text="  - {classificacao}_{hash}_foto_normal.jpg (sem caixa)").pack(anchor=tk.W)
        ttk.Label(info_frame, text="  - {classificacao}_{hash}_foto_modelo.jpg (com caixa)").pack(anchor=tk.W)
        ttk.Label(info_frame, text="• apenas frames com confianca >= threshold sao salvos").pack(anchor=tk.W)
        
        ttk.Button(main_frame, text="🚀 extrair frames", command=self.start_extraction).grid(row=11, column=0, pady=15)
        
        self.status_label = ttk.Label(main_frame, text="configure as opcoes acima", foreground="blue")
        self.status_label.grid(row=12, column=0, sticky=tk.W, pady=5)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
    
    def update_conf_label(self, *args):
        self.conf_label.config(text=f"{self.confidence_threshold.get():.2f}")
    
    def browse_model(self):
        file_path = filedialog.askopenfilename(
            title="selecionar modelo yolo",
            filetypes=[("modelo yolo", "*.pt"), ("todos os arquivos", "*.*")]
        )
        if file_path:
            self.model_path.set(file_path)
    
    def browse_video_folder(self):
        folder = filedialog.askdirectory(title="selecionar pasta com videos")
        if folder:
            self.video_folder.set(folder)
    
    def browse_output_folder(self):
        folder = filedialog.askdirectory(title="selecionar pasta de saida")
        if folder:
            self.output_folder.set(folder)
    
    def generate_hash(self, length=4):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    def start_extraction(self):
        model_path = self.model_path.get()
        video_folder = self.video_folder.get()
        output_folder = self.output_folder.get()
        classification = self.classification_var.get()
        
        if not model_path or not Path(model_path).exists():
            messagebox.showerror("erro", "selecione um modelo valido")
            return
        
        if not video_folder or not Path(video_folder).exists():
            messagebox.showerror("erro", "selecione uma pasta de videos valida")
            return
        
        if not output_folder or not Path(output_folder).exists():
            messagebox.showerror("erro", "selecione uma pasta de saida valida")
            return
        
        if not classification:
            messagebox.showerror("erro", "selecione uma classificacao")
            return
        
        self.status_label.config(text="processando videos...", foreground="orange")
        self.root.update()
        
        try:
            model = YOLO(model_path)
            output_path = Path(output_folder)
            video_path = Path(video_folder)
            
            video_files = []
            for ext in ['*.mp4', '*.avi', '*.mov', '*.mkv', '*.MP4', '*.AVI', '*.MOV', '*.MKV']:
                video_files.extend(list(video_path.glob(ext)))
            
            if not video_files:
                messagebox.showwarning("aviso", "nenhum video encontrado na pasta")
                self.status_label.config(text="nenhum video encontrado", foreground="red")
                return
            
            total_frames_saved = 0
            threshold = self.confidence_threshold.get()
            
            for video_idx, video_file in enumerate(video_files):
                self.status_label.config(
                    text=f"processando video {video_idx + 1}/{len(video_files)}: {video_file.name}",
                    foreground="blue"
                )
                self.root.update()
                
                print(f"\n{'='*60}")
                print(f"processando: {video_file.name}")
                print(f"{'='*60}")
                
                cap = cv2.VideoCapture(str(video_file))
                fps = cap.get(cv2.CAP_PROP_FPS)
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                duration_seconds = total_frames / fps if fps > 0 else 0
                
                process_interval = 0.5
                frame_skip = int(fps * process_interval)
                expected_checks = int(duration_seconds / process_interval)
                
                print(f"fps: {fps:.2f}")
                print(f"duracao: {duration_seconds:.2f}s")
                print(f"verificacoes esperadas: ~{expected_checks}")
                print(f"processando 1 frame a cada {frame_skip} frames (a cada {process_interval}s)")
                
                frame_count = 0
                checks_made = 0
                
                while cap.isOpened():
                    ret, frame = cap.read()
                    
                    if not ret:
                        break
                    
                    if frame_count % frame_skip == 0:
                        checks_made += 1
                        results = model(frame, imgsz=1920, verbose=False)
                        
                        for box in results[0].boxes:
                            confidence = float(box.conf[0])
                            
                            if confidence >= threshold:
                                class_id = int(box.cls[0])
                                class_name = results[0].names[class_id]
                                frame_hash = self.generate_hash(4)
                                
                                frame_normal_name = f"{classification}_{frame_hash}_foto_normal.jpg"
                                frame_modelo_name = f"{classification}_{frame_hash}_foto_modelo.jpg"
                                
                                frame_normal_path = output_path / frame_normal_name
                                frame_modelo_path = output_path / frame_modelo_name
                                
                                cv2.imwrite(str(frame_normal_path), frame)
                                
                                annotated_frame = results[0].plot()
                                cv2.imwrite(str(frame_modelo_path), annotated_frame)
                                
                                total_frames_saved += 2
                                
                                print(f"  ✓ frame {frame_count}: {class_name} ({confidence*100:.1f}%) - salvos:")
                                print(f"    • {frame_normal_name}")
                                print(f"    • {frame_modelo_name}")
                    
                    frame_count += 1
                
                print(f"video processado: {checks_made} verificacoes feitas em {duration_seconds:.1f}s")
                cap.release()
            
            print(f"\n{'='*60}")
            print(f"✅ concluido!")
            print(f"total de arquivos salvos: {total_frames_saved}")
            print(f"pasta de saida: {output_folder}")
            print(f"{'='*60}\n")
            
            self.status_label.config(
                text=f"✅ concluido! {total_frames_saved} arquivos salvos",
                foreground="green"
            )
            
            messagebox.showinfo(
                "concluido",
                f"extracao concluida!\n\n"
                f"videos processados: {len(video_files)}\n"
                f"arquivos salvos: {total_frames_saved}\n\n"
                f"pasta de saida:\n{output_folder}"
            )
            
        except Exception as e:
            self.status_label.config(text=f"erro: {str(e)}", foreground="red")
            messagebox.showerror("erro", f"erro durante processamento:\n{str(e)}")


def main():
    root = tk.Tk()
    app = VideoFrameExtractorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
