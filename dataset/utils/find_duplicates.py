import os
import hashlib
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading


def calculate_file_hash(file_path):
    """calcula o hash MD5 de um arquivo"""
    hash_md5 = hashlib.md5()
    try:
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception as e:
        return None


def find_duplicate_images(folder_path, progress_callback=None):
    """
    encontra imagens duplicadas comparando hash MD5
    retorna dict: {hash: [lista de arquivos com mesmo hash]}
    """
    folder = Path(folder_path)
    
    if not folder.exists():
        return {}, "pasta nao encontrada"
    
    jpg_files = list(folder.glob("*.jpg"))
    
    if not jpg_files:
        return {}, "nenhuma imagem .jpg encontrada na pasta"
    
    hash_dict = {}
    
    for idx, img_file in enumerate(jpg_files):
        file_hash = calculate_file_hash(img_file)
        
        if file_hash:
            if file_hash not in hash_dict:
                hash_dict[file_hash] = []
            hash_dict[file_hash].append(img_file)
        
        if progress_callback:
            progress = (idx + 1) / len(jpg_files) * 100
            progress_callback(progress, f"analisando: {img_file.name}")
    
    # filtra apenas hashes com mais de 1 arquivo (duplicatas)
    duplicates = {h: files for h, files in hash_dict.items() if len(files) > 1}
    
    return duplicates, None


def find_duplicate_videos(folder_path, progress_callback=None):
    """
    encontra videos duplicados comparando hash MD5
    retorna dict: {hash: [lista de arquivos com mesmo hash]}
    """
    folder = Path(folder_path)
    
    if not folder.exists():
        return {}, "pasta nao encontrada"
    
    video_extensions = ['*.mp4', '*.avi', '*.mov', '*.mkv', '*.MP4', '*.AVI', '*.MOV', '*.MKV']
    video_files = []
    for ext in video_extensions:
        video_files.extend(list(folder.glob(ext)))
    
    if not video_files:
        return {}, "nenhum video encontrado na pasta"
    
    hash_dict = {}
    
    for idx, video_file in enumerate(video_files):
        file_hash = calculate_file_hash(video_file)
        
        if file_hash:
            if file_hash not in hash_dict:
                hash_dict[file_hash] = []
            hash_dict[file_hash].append(video_file)
        
        if progress_callback:
            progress = (idx + 1) / len(video_files) * 100
            progress_callback(progress, f"analisando video: {video_file.name}")
    
    # filtra apenas hashes com mais de 1 arquivo (duplicatas)
    duplicates = {h: files for h, files in hash_dict.items() if len(files) > 1}
    
    return duplicates, None


class DuplicateFinderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("detector de imagens e videos duplicados")
        self.root.geometry("800x600")
        
        self.folder_path = tk.StringVar()
        self.is_processing = False
        self.duplicates_images = {}
        self.duplicates_videos = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(main_frame, text="selecionar pasta com imagens e videos:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Entry(folder_frame, textvariable=self.folder_path, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(folder_frame, text="procurar", command=self.browse_folder).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(main_frame, text="o script compara hash MD5 de cada .jpg e video (.mp4, .avi, .mov, .mkv) para encontrar duplicatas exatas").grid(
            row=2, column=0, sticky=tk.W, pady=5
        )
        
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=10)
        
        self.scan_button = ttk.Button(buttons_frame, text="🔍 escanear duplicatas", command=self.start_scanning)
        self.scan_button.pack(side=tk.LEFT, padx=5)
        
        self.delete_button = ttk.Button(buttons_frame, text="🗑️ deletar duplicatas", command=self.delete_duplicates, state='disabled')
        self.delete_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(main_frame, text="progresso:").grid(row=4, column=0, sticky=tk.W, pady=5)
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate', length=600)
        self.progress_bar.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.status_label = ttk.Label(main_frame, text="aguardando...", foreground="blue")
        self.status_label.grid(row=6, column=0, sticky=tk.W, pady=5)
        
        log_frame = ttk.LabelFrame(main_frame, text="resultados", padding="5")
        log_frame.grid(row=7, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.log_text = tk.Text(log_frame, height=20, width=90, font=("Courier New", 9))
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)
    
    def browse_folder(self):
        folder = filedialog.askdirectory(title="selecionar pasta com imagens")
        if folder:
            self.folder_path.set(folder)
            self.log_message(f"pasta selecionada: {folder}\n")
    
    def log_message(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_progress(self, value, status):
        if value is not None:
            self.progress_bar['value'] = value
        if status:
            self.status_label.config(text=status)
        self.root.update_idletasks()
    
    def start_scanning(self):
        if self.is_processing:
            messagebox.showwarning("aviso", "processamento ja em andamento")
            return
        
        folder = self.folder_path.get()
        
        if not folder:
            messagebox.showerror("erro", "selecione uma pasta primeiro")
            return
        
        self.is_processing = True
        self.scan_button.config(state='disabled')
        self.delete_button.config(state='disabled')
        self.progress_bar['value'] = 0
        self.log_text.delete(1.0, tk.END)
        
        thread = threading.Thread(target=self.scan_folder, args=(folder,))
        thread.start()
    
    def scan_folder(self, folder_path):
        try:
            self.log_message("="*70)
            self.log_message("ESCANEANDO IMAGENS E VIDEOS DUPLICADOS")
            self.log_message("="*70 + "\n")
            
            # Escanear imagens
            self.log_message("📷 FASE 1: ESCANEANDO IMAGENS...\n")
            self.update_progress(0, "calculando hash das imagens...")
            
            duplicates_images, error_img = find_duplicate_images(
                folder_path,
                progress_callback=self.update_progress
            )
            
            if error_img:
                self.log_message(f"AVISO IMAGENS: {error_img}\n")
            
            # Escanear videos
            self.log_message("🎥 FASE 2: ESCANEANDO VIDEOS...\n")
            self.update_progress(0, "calculando hash dos videos...")
            
            duplicates_videos, error_vid = find_duplicate_videos(
                folder_path,
                progress_callback=self.update_progress
            )
            
            if error_vid:
                self.log_message(f"AVISO VIDEOS: {error_vid}\n")
            
            self.duplicates_images = duplicates_images
            self.duplicates_videos = duplicates_videos
            
            # Contadores
            total_images = len(list(Path(folder_path).glob("*.jpg")))
            video_extensions = ['*.mp4', '*.avi', '*.mov', '*.mkv', '*.MP4', '*.AVI', '*.MOV', '*.MKV']
            total_videos = sum(len(list(Path(folder_path).glob(ext))) for ext in video_extensions)
            
            duplicate_groups_images = len(duplicates_images)
            duplicate_groups_videos = len(duplicates_videos)
            total_duplicates_images = sum(len(files) - 1 for files in duplicates_images.values())
            total_duplicates_videos = sum(len(files) - 1 for files in duplicates_videos.values())
            
            duplicate_groups = duplicate_groups_images + duplicate_groups_videos
            total_duplicates = total_duplicates_images + total_duplicates_videos
            
            self.log_message(f"RESUMO:")
            self.log_message(f"  📷 Imagens analisadas: {total_images}")
            self.log_message(f"  🎥 Videos analisados: {total_videos}")
            self.log_message(f"  📷 Grupos de imagens duplicadas: {duplicate_groups_images}")
            self.log_message(f"  🎥 Grupos de videos duplicados: {duplicate_groups_videos}")
            self.log_message(f"  📷 Imagens duplicadas: {total_duplicates_images}")
            self.log_message(f"  🎥 Videos duplicados: {total_duplicates_videos}")
            self.log_message(f"  💾 Espaço que pode ser liberado: ~{self.calculate_wasted_space(duplicates_images, duplicates_videos)}\n")
            
            if duplicate_groups == 0:
                self.log_message("✅ NENHUMA DUPLICATA ENCONTRADA!\n")
                self.update_progress(100, "nenhuma duplicata encontrada")
                messagebox.showinfo("resultado", "nenhuma imagem ou video duplicado encontrado!")
                return
            
            self.log_message("="*70)
            self.log_message("DETALHES DAS DUPLICATAS:")
            self.log_message("="*70 + "\n")
            
            # Mostrar duplicatas de imagens
            if duplicates_images:
                self.log_message("📷 IMAGENS DUPLICADAS:\n")
                for idx, (file_hash, files) in enumerate(duplicates_images.items(), 1):
                    file_size = files[0].stat().st_size / 1024  # KB
                    self.log_message(f"GRUPO IMG-{idx} (hash: {file_hash[:12]}...):")
                    self.log_message(f"  tamanho: {file_size:.1f} KB")
                    self.log_message(f"  quantidade: {len(files)} arquivos identicos")
                    self.log_message(f"  arquivos:")
                    
                    for file in files:
                        txt_file = file.with_suffix('.txt')
                        has_txt = "✓ tem .txt" if txt_file.exists() else "✗ sem .txt"
                        self.log_message(f"    • {file.name} ({has_txt})")
                    
                    self.log_message("")
            
            # Mostrar duplicatas de videos
            if duplicates_videos:
                self.log_message("🎥 VIDEOS DUPLICADOS:\n")
                for idx, (file_hash, files) in enumerate(duplicates_videos.items(), 1):
                    file_size = files[0].stat().st_size / (1024 * 1024)  # MB
                    self.log_message(f"GRUPO VID-{idx} (hash: {file_hash[:12]}...):")
                    self.log_message(f"  tamanho: {file_size:.1f} MB")
                    self.log_message(f"  quantidade: {len(files)} arquivos identicos")
                    self.log_message(f"  arquivos:")
                    
                    for file in files:
                        self.log_message(f"    • {file.name}")
                    
                    self.log_message("")
            
            self.update_progress(100, f"{duplicate_groups} grupo(s) de duplicatas encontrado(s)")
            self.delete_button.config(state='normal')
            
            messagebox.showinfo(
                "resultado",
                f"📷 Imagens: {duplicate_groups_images} grupo(s), {total_duplicates_images} duplicada(s)\n"
                f"🎥 Videos: {duplicate_groups_videos} grupo(s), {total_duplicates_videos} duplicado(s)\n\n"
                f"Total: {duplicate_groups} grupo(s), {total_duplicates} arquivo(s)\n\n"
                f"Use o botao 'deletar duplicatas' para remover as copias"
            )
            
        except Exception as e:
            self.log_message(f"\nERRO durante escaneamento: {str(e)}")
            messagebox.showerror("erro", f"erro durante escaneamento:\n{str(e)}")
        
        finally:
            self.is_processing = False
            self.scan_button.config(state='normal')
    
    def calculate_wasted_space(self, duplicates_images, duplicates_videos):
        """calcula espaco desperdicado com duplicatas"""
        total_bytes = 0
        
        # Calcular espaço de imagens
        for files in duplicates_images.values():
            file_size = files[0].stat().st_size
            wasted = file_size * (len(files) - 1)
            total_bytes += wasted
        
        # Calcular espaço de videos
        for files in duplicates_videos.values():
            file_size = files[0].stat().st_size
            wasted = file_size * (len(files) - 1)
            total_bytes += wasted
        
        # converte para unidade apropriada
        if total_bytes < 1024:
            return f"{total_bytes} bytes"
        elif total_bytes < 1024 * 1024:
            return f"{total_bytes / 1024:.1f} KB"
        else:
            return f"{total_bytes / (1024 * 1024):.1f} MB"
    
    def delete_duplicates(self):
        if not self.duplicates_images and not self.duplicates_videos:
            messagebox.showwarning("aviso", "nenhuma duplicata para deletar")
            return
        
        total_duplicates = sum(len(files) - 1 for files in self.duplicates_images.values()) + \
                          sum(len(files) - 1 for files in self.duplicates_videos.values())
        
        response = messagebox.askyesno(
            "confirmar delecao",
            f"Deseja deletar {total_duplicates} arquivo(s) duplicado(s)?\n\n"
            f"Para cada grupo, o PRIMEIRO arquivo sera mantido\n"
            f"e os demais serao DELETADOS (junto com seus .txt para imagens).\n\n"
            f"Esta acao NAO pode ser desfeita!"
        )
        
        if not response:
            return
        
        self.log_text.delete(1.0, tk.END)
        self.log_message("="*70)
        self.log_message("DELETANDO DUPLICATAS")
        self.log_message("="*70 + "\n")
        
        deleted_images = 0
        deleted_videos = 0
        deleted_txt_count = 0
        
        # Deletar imagens duplicadas
        if self.duplicates_images:
            self.log_message("📷 DELETANDO IMAGENS DUPLICADAS:\n")
            for file_hash, files in self.duplicates_images.items():
                keep_file = files[0]
                self.log_message(f"GRUPO IMG (hash: {file_hash[:12]}...):")
                self.log_message(f"  ✓ MANTENDO: {keep_file.name}")
                
                for file in files[1:]:
                    try:
                        # deleta .txt correspondente se existir
                        txt_file = file.with_suffix('.txt')
                        if txt_file.exists():
                            txt_file.unlink()
                            deleted_txt_count += 1
                            self.log_message(f"  ✗ DELETADO: {txt_file.name}")
                        
                        # deleta .jpg
                        file.unlink()
                        deleted_images += 1
                        self.log_message(f"  ✗ DELETADO: {file.name}")
                        
                    except Exception as e:
                        self.log_message(f"  ❌ ERRO ao deletar {file.name}: {str(e)}")
                
                self.log_message("")
        
        # Deletar videos duplicados
        if self.duplicates_videos:
            self.log_message("🎥 DELETANDO VIDEOS DUPLICADOS:\n")
            for file_hash, files in self.duplicates_videos.items():
                keep_file = files[0]
                self.log_message(f"GRUPO VID (hash: {file_hash[:12]}...):")
                self.log_message(f"  ✓ MANTENDO: {keep_file.name}")
                
                for file in files[1:]:
                    try:
                        file.unlink()
                        deleted_videos += 1
                        self.log_message(f"  ✗ DELETADO: {file.name}")
                        
                    except Exception as e:
                        self.log_message(f"  ❌ ERRO ao deletar {file.name}: {str(e)}")
                
                self.log_message("")
        
        self.log_message("="*70)
        self.log_message("RESULTADO:")
        self.log_message(f"  📷 Imagens deletadas: {deleted_images}")
        self.log_message(f"  🎥 Videos deletados: {deleted_videos}")
        self.log_message(f"  📄 Labels .txt deletados: {deleted_txt_count}")
        self.log_message("="*70)
        
        self.duplicates_images = {}
        self.duplicates_videos = {}
        self.delete_button.config(state='disabled')
        
        messagebox.showinfo(
            "concluido",
            f"Delecao concluida!\n\n"
            f"📷 Imagens deletadas: {deleted_images}\n"
            f"🎥 Videos deletados: {deleted_videos}\n"
            f"📄 Labels .txt deletados: {deleted_txt_count}"
        )


def main():
    root = tk.Tk()
    app = DuplicateFinderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
