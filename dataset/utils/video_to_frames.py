import cv2
import hashlib
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading


CLASSES = [
    "Bicho-Preguica",
    "Cachorro",
    "Cachorro do Mato",
    "Capivara",
    "Cutia",
    "Gamba",
    "Gato do Mato",
    "Guaxinim",
    "Lagarto Teiu",
    "Lobo Guara",
    "Onca",
    "Oucico Cacheiro",
    "Paca",
    "Tamandua Mirim",
    "Tatu",
    "0-Banco-de-Fotos"
]


def generate_hash(video_name):
    content = video_name.encode()
    hash_obj = hashlib.md5(content)
    return hash_obj.hexdigest()[:4]


def extract_frames_from_video(video_path, animal_class, fps, output_base_dir, progress_callback=None):
    output_dir = Path(output_base_dir) / animal_class
    output_dir.mkdir(parents=True, exist_ok=True)
    
    video = cv2.VideoCapture(video_path)
    
    if not video.isOpened():
        return False, f"Erro ao abrir o video: {video_path}"
    
    video_fps = video.get(cv2.CAP_PROP_FPS)
    total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    
    frame_interval = int(video_fps / fps)
    
    video_name = Path(video_path).stem
    hash_code = generate_hash(video_name)
    frame_count = 0
    saved_count = 0
    
    while True:
        ret, frame = video.read()
        
        if not ret:
            break
        
        if frame_count % frame_interval == 0:
            filename = f"{hash_code}.{saved_count:04d}.jpg"
            output_path = output_dir / filename
            
            cv2.imwrite(str(output_path), frame)
            saved_count += 1
            
            if progress_callback:
                progress_callback(saved_count)
        
        frame_count += 1
    
    video.release()
    return True, f"Extraidos {saved_count} frames em {output_dir}"


class VideoToFramesApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video to Frames - Dataset Generator")
        self.root.geometry("700x500")
        
        self.video_files = []
        self.output_dir = Path("../dataset")
        self.fps = 2
        
        self.create_widgets()
    
    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(main_frame, text="Selecionar Videos:", font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Button(btn_frame, text="Adicionar Videos", command=self.select_videos).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Limpar Lista", command=self.clear_videos).pack(side=tk.LEFT, padx=5)
        
        self.video_listbox = tk.Listbox(main_frame, height=8, width=80)
        self.video_listbox.grid(row=2, column=0, columnspan=2, pady=5, sticky=(tk.W, tk.E))
        
        scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.video_listbox.yview)
        scrollbar.grid(row=2, column=2, sticky=(tk.N, tk.S))
        self.video_listbox.config(yscrollcommand=scrollbar.set)
        
        ttk.Label(main_frame, text="Classe do Animal:", font=('Arial', 10, 'bold')).grid(row=3, column=0, sticky=tk.W, pady=(10, 5))
        
        self.class_var = tk.StringVar(value=CLASSES[0])
        self.class_combo = ttk.Combobox(main_frame, textvariable=self.class_var, values=CLASSES, state='readonly', width=30)
        self.class_combo.grid(row=4, column=0, sticky=tk.W, pady=5)
        
        ttk.Label(main_frame, text="FPS (frames por segundo):", font=('Arial', 10, 'bold')).grid(row=5, column=0, sticky=tk.W, pady=(10, 5))
        
        fps_frame = ttk.Frame(main_frame)
        fps_frame.grid(row=6, column=0, sticky=tk.W, pady=5)
        
        self.fps_var = tk.IntVar(value=2)
        ttk.Spinbox(fps_frame, from_=1, to=10, textvariable=self.fps_var, width=10).pack(side=tk.LEFT)
        
        ttk.Label(main_frame, text="Diretorio de Saida:", font=('Arial', 10, 'bold')).grid(row=7, column=0, sticky=tk.W, pady=(10, 5))
        
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=8, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
        
        self.output_var = tk.StringVar(value=str(self.output_dir))
        ttk.Entry(output_frame, textvariable=self.output_var, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(output_frame, text="Selecionar", command=self.select_output_dir).pack(side=tk.LEFT)
        
        self.process_btn = ttk.Button(main_frame, text="Processar Videos", command=self.process_videos, style='Accent.TButton')
        self.process_btn.grid(row=9, column=0, pady=20)
        
        self.progress_label = ttk.Label(main_frame, text="", foreground="blue")
        self.progress_label.grid(row=10, column=0, columnspan=2)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
    
    def select_videos(self):
        files = filedialog.askopenfilenames(
            title="Selecionar Videos",
            filetypes=[
                ("Video files", "*.mp4 *.avi *.mov *.mkv *.flv *.wmv"),
                ("All files", "*.*")
            ]
        )
        
        for file in files:
            if file not in self.video_files:
                self.video_files.append(file)
                self.video_listbox.insert(tk.END, Path(file).name)
    
    def clear_videos(self):
        self.video_files = []
        self.video_listbox.delete(0, tk.END)
    
    def select_output_dir(self):
        directory = filedialog.askdirectory(title="Selecionar Diretorio de Saida")
        if directory:
            self.output_var.set(directory)
    
    def update_progress(self, message):
        self.progress_label.config(text=message)
        self.root.update_idletasks()
    
    def process_videos_thread(self):
        if not self.video_files:
            messagebox.showwarning("Aviso", "Nenhum video selecionado!")
            self.process_btn.config(state='normal')
            return
        
        animal_class = self.class_var.get()
        fps = self.fps_var.get()
        output_dir = self.output_var.get()
        
        total = len(self.video_files)
        
        for i, video_path in enumerate(self.video_files, 1):
            self.update_progress(f"Processando video {i}/{total}: {Path(video_path).name}")
            
            success, message = extract_frames_from_video(video_path, animal_class, fps, output_dir)
            
            if not success:
                messagebox.showerror("Erro", message)
                continue
        
        self.update_progress(f"Concluido! {total} video(s) processado(s)")
        messagebox.showinfo("Sucesso", f"Processamento concluido!\n\nFrames salvos em:\n{Path(output_dir) / animal_class}")
        self.process_btn.config(state='normal')
    
    def process_videos(self):
        self.process_btn.config(state='disabled')
        thread = threading.Thread(target=self.process_videos_thread, daemon=True)
        thread.start()


if __name__ == "__main__":
    root = tk.Tk()
    app = VideoToFramesApp(root)
    root.mainloop()
