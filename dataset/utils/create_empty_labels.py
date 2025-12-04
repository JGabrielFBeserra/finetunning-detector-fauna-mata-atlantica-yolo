import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading


def find_images_without_labels(folder_path, progress_callback=None):
    """
    verifica todas as imagens .jpg na pasta e retorna aquelas que nao tem arquivo .txt correspondente
    """
    folder = Path(folder_path)
    
    if not folder.exists():
        return [], f"pasta nao encontrada: {folder_path}"
    
    jpg_files = list(folder.glob("*.jpg"))
    
    if not jpg_files:
        return [], "nenhuma imagem .jpg encontrada na pasta"
    
    images_without_txt = []
    
    for idx, img_file in enumerate(jpg_files):
        txt_file = img_file.with_suffix('.txt')
        
        if not txt_file.exists():
            images_without_txt.append(img_file)
        
        if progress_callback:
            progress = (idx + 1) / len(jpg_files) * 50
            progress_callback(progress, f"verificando: {img_file.name}")
    
    return images_without_txt, None


def create_empty_txt_files(images_list, progress_callback=None):
    """
    cria arquivos .txt vazios para cada imagem da lista
    """
    created_count = 0
    
    for idx, img_file in enumerate(images_list):
        txt_file = img_file.with_suffix('.txt')
        
        try:
            txt_file.touch()
            created_count += 1
            
            if progress_callback:
                progress = 50 + (idx + 1) / len(images_list) * 50
                progress_callback(progress, f"criando: {txt_file.name}")
        except Exception as e:
            if progress_callback:
                progress_callback(None, f"erro ao criar {txt_file.name}: {str(e)}")
    
    return created_count


class EmptyLabelsCreatorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("criar arquivos de label vazios")
        self.root.geometry("600x400")
        
        self.folder_path = tk.StringVar()
        self.is_processing = False
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(main_frame, text="selecionar pasta com imagens e labels:").grid(row=0, column=0, sticky=tk.W, pady=5)
        
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Entry(folder_frame, textvariable=self.folder_path, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(folder_frame, text="procurar", command=self.browse_folder).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(main_frame, text="o script vai criar arquivos .txt vazios para imagens .jpg que nao tem label").grid(
            row=2, column=0, sticky=tk.W, pady=10
        )
        
        self.process_button = ttk.Button(main_frame, text="processar", command=self.start_processing)
        self.process_button.grid(row=3, column=0, pady=10)
        
        ttk.Label(main_frame, text="progresso:").grid(row=4, column=0, sticky=tk.W, pady=5)
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate', length=400)
        self.progress_bar.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.status_label = ttk.Label(main_frame, text="aguardando...", foreground="blue")
        self.status_label.grid(row=6, column=0, sticky=tk.W, pady=5)
        
        log_frame = ttk.LabelFrame(main_frame, text="log", padding="5")
        log_frame.grid(row=7, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.log_text = tk.Text(log_frame, height=10, width=70)
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
            self.log_message(f"pasta selecionada: {folder}")
    
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
    
    def start_processing(self):
        if self.is_processing:
            messagebox.showwarning("aviso", "processamento ja em andamento")
            return
        
        folder = self.folder_path.get()
        
        if not folder:
            messagebox.showerror("erro", "selecione uma pasta primeiro")
            return
        
        self.is_processing = True
        self.process_button.config(state='disabled')
        self.progress_bar['value'] = 0
        self.log_text.delete(1.0, tk.END)
        
        thread = threading.Thread(target=self.process_folder, args=(folder,))
        thread.start()
    
    def process_folder(self, folder_path):
        try:
            self.log_message("iniciando verificacao...")
            self.update_progress(0, "verificando imagens...")
            
            images_without_txt, error = find_images_without_labels(
                folder_path, 
                progress_callback=self.update_progress
            )
            
            if error:
                self.log_message(f"erro: {error}")
                messagebox.showerror("erro", error)
                return
            
            total_images = len(list(Path(folder_path).glob("*.jpg")))
            images_missing = len(images_without_txt)
            
            self.log_message(f"\ntotal de imagens .jpg: {total_images}")
            self.log_message(f"imagens com .txt: {total_images - images_missing}")
            self.log_message(f"imagens sem .txt: {images_missing}")
            
            if images_missing == 0:
                self.log_message("\ntodas as imagens ja possuem arquivo .txt correspondente")
                self.update_progress(100, "concluido - nenhum arquivo criado")
                messagebox.showinfo("concluido", "todas as imagens ja possuem arquivo .txt")
                return
            
            self.log_message(f"\ncriando {images_missing} arquivos .txt vazios...")
            self.update_progress(50, "criando arquivos .txt...")
            
            created_count = create_empty_txt_files(
                images_without_txt,
                progress_callback=self.update_progress
            )
            
            self.log_message(f"\nprocessamento concluido!")
            self.log_message(f"arquivos .txt criados: {created_count}")
            
            self.update_progress(100, "concluido com sucesso")
            
            messagebox.showinfo(
                "concluido", 
                f"{created_count} arquivo(s) .txt vazio(s) criado(s) com sucesso"
            )
            
        except Exception as e:
            self.log_message(f"\nerro durante processamento: {str(e)}")
            messagebox.showerror("erro", f"erro durante processamento:\n{str(e)}")
        
        finally:
            self.is_processing = False
            self.process_button.config(state='normal')


def main():
    root = tk.Tk()
    app = EmptyLabelsCreatorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
