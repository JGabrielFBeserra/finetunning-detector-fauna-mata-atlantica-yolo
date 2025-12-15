from ultralytics import YOLO
import cv2
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import random
import string


class VideoDetectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("visualizador e detector de videos - yolov8")
        self.root.geometry("900x700")
        
        self.folder_path = tk.StringVar()
        self.model_path = tk.StringVar(value="yolov8n-detector-gamba.pt")
        
        self.video_files = []
        self.current_video_index = 0
        self.cap = None
        self.is_playing = False
        self.is_paused = False
        self.total_frames = 0
        self.current_frame = 0
        self.fps = 30
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(main_frame, text="modelo (.pt):").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        model_frame = ttk.Frame(main_frame)
        model_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Entry(model_frame, textvariable=self.model_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(model_frame, text="procurar modelo", command=self.browse_model).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(main_frame, text="pasta de videos:").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Entry(folder_frame, textvariable=self.folder_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(folder_frame, text="selecionar pasta", command=self.browse_folder).pack(side=tk.LEFT, padx=5)
        
        list_frame = ttk.LabelFrame(main_frame, text="videos encontrados", padding="5")
        list_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=10)
        
        self.video_listbox = tk.Listbox(list_frame, height=6)
        self.video_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.video_listbox.bind('<<ListboxSelect>>', self.on_video_select)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.video_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.video_listbox.config(yscrollcommand=scrollbar.set)
        
        controls_frame = ttk.LabelFrame(main_frame, text="controles", padding="10")
        controls_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=10)
        
        nav_frame = ttk.Frame(controls_frame)
        nav_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(nav_frame, text="⏮ anterior", command=self.previous_video, width=15).pack(side=tk.LEFT, padx=5)
        self.play_pause_button = ttk.Button(nav_frame, text="▶ play", command=self.toggle_play_pause, width=15)
        self.play_pause_button.pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="proximo ⏭", command=self.next_video, width=15).pack(side=tk.LEFT, padx=5)
        
        timeline_frame = ttk.Frame(controls_frame)
        timeline_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(timeline_frame, text="posicao do video:").pack(anchor=tk.W)
        
        self.timeline_scale = tk.Scale(
            timeline_frame, 
            from_=0, 
            to=100, 
            orient=tk.HORIZONTAL,
            command=self.on_timeline_change,
            length=600
        )
        self.timeline_scale.pack(fill=tk.X, pady=5)
        
        self.time_label = ttk.Label(timeline_frame, text="00:00 / 00:00")
        self.time_label.pack(anchor=tk.W)
        
        rename_frame = ttk.LabelFrame(main_frame, text="renomear video", padding="10")
        rename_frame.grid(row=7, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(rename_frame, text="classificacao:").pack(anchor=tk.W, pady=2)
        
        self.classification_var = tk.StringVar()
        classification_combo = ttk.Combobox(
            rename_frame,
            textvariable=self.classification_var,
            values=["positivo_positivo", "falso_positivo", "falso_negativo", "negativo_negativo"],
            state="readonly",
            width=30
        )
        classification_combo.pack(fill=tk.X, pady=5)
        classification_combo.current(0)
        
        ttk.Button(rename_frame, text="💾 salvar nome do video", command=self.rename_video).pack(pady=5)
        
        self.status_label = ttk.Label(main_frame, text="selecione uma pasta com videos", foreground="blue")
        self.status_label.grid(row=8, column=0, sticky=tk.W, pady=5)
        
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
    
    def browse_folder(self):
        folder = filedialog.askdirectory(title="selecionar pasta com videos")
        if folder:
            self.folder_path.set(folder)
            self.load_videos(folder)
    
    def load_videos(self, folder):
        self.video_listbox.delete(0, tk.END)
        self.video_files = []
        
        folder_path = Path(folder)
        for ext in ['*.mp4', '*.avi', '*.mov', '*.mkv', '*.MP4', '*.AVI', '*.MOV', '*.MKV']:
            self.video_files.extend(list(folder_path.glob(ext)))
        
        if not self.video_files:
            self.status_label.config(text="nenhum video encontrado na pasta")
            return
        
        for video in self.video_files:
            self.video_listbox.insert(tk.END, video.name)
        
        self.status_label.config(text=f"{len(self.video_files)} videos encontrados")
    
    def on_video_select(self, event):
        selection = self.video_listbox.curselection()
        if selection:
            self.current_video_index = selection[0]
            if self.is_playing:
                self.stop_playback()
            self.load_current_video()
    
    def previous_video(self):
        if not self.video_files:
            return
        self.current_video_index = (self.current_video_index - 1) % len(self.video_files)
        self.video_listbox.selection_clear(0, tk.END)
        self.video_listbox.selection_set(self.current_video_index)
        self.video_listbox.see(self.current_video_index)
        if self.is_playing:
            self.stop_playback()
        self.load_current_video()
    
    def next_video(self):
        if not self.video_files:
            return
        self.current_video_index = (self.current_video_index + 1) % len(self.video_files)
        self.video_listbox.selection_clear(0, tk.END)
        self.video_listbox.selection_set(self.current_video_index)
        self.video_listbox.see(self.current_video_index)
        if self.is_playing:
            self.stop_playback()
        self.load_current_video()
    
    def load_current_video(self):
        if not self.video_files or self.current_video_index >= len(self.video_files):
            return
        
        video_path = str(self.video_files[self.current_video_index])
        
        if self.cap:
            self.cap.release()
        
        self.cap = cv2.VideoCapture(video_path)
        self.total_frames = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        self.current_frame = 0
        
        self.timeline_scale.config(to=self.total_frames - 1)
        self.timeline_scale.set(0)
        
        duration = self.total_frames / self.fps if self.fps > 0 else 0
        self.time_label.config(text=f"00:00 / {self.format_time(duration)}")
        
        self.status_label.config(text=f"video carregado: {self.video_files[self.current_video_index].name}")
    
    def toggle_play_pause(self):
        if not self.video_files or not self.cap:
            messagebox.showwarning("aviso", "selecione um video primeiro")
            return
        
        model_path = self.model_path.get()
        if not model_path or not Path(model_path).exists():
            messagebox.showerror("erro", "selecione um modelo valido")
            return
        
        if not self.is_playing:
            self.is_playing = True
            self.is_paused = False
            self.play_pause_button.config(text="⏸ pausar")
            threading.Thread(target=self.play_video, daemon=True).start()
        else:
            if self.is_paused:
                self.is_paused = False
                self.play_pause_button.config(text="⏸ pausar")
            else:
                self.is_paused = True
                self.play_pause_button.config(text="▶ continuar")
    
    def stop_playback(self):
        self.is_playing = False
        self.is_paused = False
        self.play_pause_button.config(text="▶ play")
    
    def on_timeline_change(self, value):
        if self.cap and not self.is_playing:
            frame_pos = int(float(value))
            self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_pos)
            self.current_frame = frame_pos
            
            current_time = frame_pos / self.fps if self.fps > 0 else 0
            duration = self.total_frames / self.fps if self.fps > 0 else 0
            self.time_label.config(text=f"{self.format_time(current_time)} / {self.format_time(duration)}")
    
    def format_time(self, seconds):
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins:02d}:{secs:02d}"
    
    def generate_hash(self, length=4):
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    def rename_video(self):
        if not self.video_files or self.current_video_index >= len(self.video_files):
            messagebox.showwarning("aviso", "nenhum video selecionado")
            return
        
        if self.is_playing:
            messagebox.showwarning("aviso", "pause o video antes de renomear")
            return
        
        classification = self.classification_var.get()
        if not classification:
            messagebox.showwarning("aviso", "selecione uma classificacao")
            return
        
        current_video = self.video_files[self.current_video_index]
        video_hash = self.generate_hash(4)
        new_name = f"{classification}_{video_hash}{current_video.suffix}"
        new_path = current_video.parent / new_name
        
        if new_path.exists():
            messagebox.showerror("erro", f"arquivo ja existe: {new_name}")
            return
        
        try:
            if self.cap:
                self.cap.release()
                self.cap = None
            
            current_video.rename(new_path)
            
            self.video_files[self.current_video_index] = new_path
            
            self.video_listbox.delete(self.current_video_index)
            self.video_listbox.insert(self.current_video_index, new_name)
            self.video_listbox.selection_set(self.current_video_index)
            
            self.status_label.config(text=f"✓ renomeado para: {new_name}", foreground="green")
            messagebox.showinfo("sucesso", f"video renomeado para:\n{new_name}")
            
            self.load_current_video()
            
        except Exception as e:
            messagebox.showerror("erro", f"erro ao renomear: {str(e)}")
            if self.cap is None:
                self.load_current_video()
    
    def play_video(self):
        try:
            model = YOLO(self.model_path.get())
            
            window_name = 'detector - pressione q para sair'
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, 1280, 720)
            
            process_interval = 0.5
            frame_skip = int(self.fps * process_interval)
            
            last_annotated_frame = None
            
            while self.is_playing and self.cap.isOpened():
                if not self.is_paused:
                    ret, frame = self.cap.read()
                    
                    if not ret:
                        self.stop_playback()
                        break
                    
                    if self.current_frame % frame_skip == 0:
                        results = model(frame, imgsz=1920, verbose=False)
                        last_annotated_frame = results[0].plot()
                        
                        if len(results[0].boxes) > 0:
                            print(f"\nFrame {self.current_frame}:")
                            for box in results[0].boxes:
                                class_id = int(box.cls[0])
                                confidence = float(box.conf[0])
                                class_name = results[0].names[class_id]
                                print(f"  🎯 {class_name}: {confidence*100:.1f}%")
                    
                    if last_annotated_frame is not None:
                        cv2.imshow(window_name, last_annotated_frame)
                    
                    self.current_frame += 1
                    self.timeline_scale.set(self.current_frame)
                    
                    current_time = self.current_frame / self.fps if self.fps > 0 else 0
                    duration = self.total_frames / self.fps if self.fps > 0 else 0
                    self.time_label.config(text=f"{self.format_time(current_time)} / {self.format_time(duration)}")
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.stop_playback()
                    break
            
            cv2.destroyAllWindows()
            
        except Exception as e:
            messagebox.showerror("erro", f"erro: {str(e)}")
            cv2.destroyAllWindows()
            self.stop_playback()


def main():
    root = tk.Tk()
    app = VideoDetectorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
