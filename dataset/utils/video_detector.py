from ultralytics import YOLO
import cv2
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk, messagebox


class VideoDetectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("deteccao em video - yolov8")
        self.root.geometry("1920x1080")
        
        self.video_path = tk.StringVar()
        self.model_path = tk.StringVar(value="yolov8n-detector-gamba.pt")
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(main_frame, text="modelo (.pt):").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        model_frame = ttk.Frame(main_frame)
        model_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Entry(model_frame, textvariable=self.model_path, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(model_frame, text="procurar", command=self.browse_model).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(main_frame, text="video:").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        video_frame = ttk.Frame(main_frame)
        video_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Entry(video_frame, textvariable=self.video_path, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(video_frame, text="procurar", command=self.browse_video).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(main_frame, text="pressione 'q' no video para sair").grid(
            row=4, column=0, sticky=tk.W, pady=10
        )
        
        ttk.Button(main_frame, text="iniciar deteccao", command=self.start_detection).grid(row=5, column=0, pady=10)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
    
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
            filetypes=[("videos", "*.mp4 *.avi *.mov *.mkv"), ("todos os arquivos", "*.*")]
        )
        if file_path:
            self.video_path.set(file_path)
    
    def start_detection(self):
        model_path = self.model_path.get()
        video_path = self.video_path.get()
        
        if not model_path or not Path(model_path).exists():
            messagebox.showerror("erro", "selecione um modelo valido")
            return
        
        if not video_path or not Path(video_path).exists():
            messagebox.showerror("erro", "selecione um video valido")
            return
        
        self.root.withdraw()
        
        try:
            print("carregando modelo...")
            model = YOLO(model_path)
            
            print("abrindo video...")
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                messagebox.showerror("erro", "nao foi possivel abrir o video")
                self.root.deiconify()
                return
            
            # Criar janela redimensionavel para exibir video completo
            window_name = 'deteccao - pressione q para sair'
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, 1920, 1080)
            
            print("processando video - pressione 'q' para sair")
            
            while cap.isOpened():
                ret, frame = cap.read()
                
                if not ret:
                    break
                
                # imgsz define o tamanho da imagem para inferencia (maior = mais detalhes, mais lento)
                # o video continua na resolucao original, imgsz afeta apenas o processamento
                results = model(frame, imgsz=1920, verbose=False)
                annotated_frame = results[0].plot()
                
                cv2.imshow(window_name, annotated_frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            
            print("video finalizado")
            
        except Exception as e:
            messagebox.showerror("erro", f"erro: {str(e)}")
            cv2.destroyAllWindows()
        
        finally:
            self.root.deiconify()


def main():
    root = tk.Tk()
    app = VideoDetectorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
