import os
from pathlib import Path
import shutil
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading


def merge_folders(folders, output_folder, progress_callback=None):
    """
    consolida arquivos de multiplas pastas selecionadas
    separa automaticamente images (.jpg, .jpeg, .png) e labels (.txt)
    """
    output_path = Path(output_folder)
    
    output_images = output_path / "images"
    output_labels = output_path / "labels"
    
    output_images.mkdir(parents=True, exist_ok=True)
    output_labels.mkdir(parents=True, exist_ok=True)
    
    total_images = 0
    total_labels = 0
    skipped_images = 0
    skipped_labels = 0
    
    all_files = []
    
    # Varre todas as pastas recursivamente
    for folder in folders:
        folder_path = Path(folder)
        if folder_path.exists():
            # Pega todas as imagens recursivamente
            all_files.extend([(f, 'image') for f in folder_path.rglob("*.jpg")])
            all_files.extend([(f, 'image') for f in folder_path.rglob("*.jpeg")])
            all_files.extend([(f, 'image') for f in folder_path.rglob("*.png")])
            # Pega todos os labels recursivamente
            all_files.extend([(f, 'label') for f in folder_path.rglob("*.txt")])
    
    if not all_files:
        return False, "nenhum arquivo encontrado nas pastas selecionadas"
    
    total_files = len(all_files)
    
    for idx, (file_path, file_type) in enumerate(all_files):
        if file_type == 'image':
            dest_folder = output_images
        else:
            dest_folder = output_labels
        
        dest_path = dest_folder / file_path.name
        
        try:
            if dest_path.exists():
                if file_type == 'image':
                    skipped_images += 1
                else:
                    skipped_labels += 1
                
                if progress_callback:
                    progress = (idx + 1) / total_files * 100
                    progress_callback(progress, f"pulado (ja existe): {file_path.name}")
            else:
                shutil.copy2(file_path, dest_path)
                
                if file_type == 'image':
                    total_images += 1
                else:
                    total_labels += 1
                
                if progress_callback:
                    progress = (idx + 1) / total_files * 100
                    progress_callback(progress, f"copiado: {file_path.name}")
        
        except Exception as e:
            if progress_callback:
                progress_callback(None, f"erro ao copiar {file_path.name}: {str(e)}")
    
    return True, {
        'images_copied': total_images,
        'labels_copied': total_labels,
        'images_skipped': skipped_images,
        'labels_skipped': skipped_labels,
        'folders_count': len(folders),
        'output_images': str(output_images),
        'output_labels': str(output_labels)
    }


class MergeDatasetGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("consolidar arquivos de multiplas pastas")
        self.root.geometry("800x600")
        
        self.output_folder = tk.StringVar()
        self.is_processing = False
        
        self.folders = []
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Seção de seleção de pastas
        folders_label_frame = ttk.LabelFrame(main_frame, text="pastas a consolidar", padding="10")
        folders_label_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        folders_buttons_frame = ttk.Frame(folders_label_frame)
        folders_buttons_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(folders_buttons_frame, text="+ adicionar pasta", command=self.add_folder, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(folders_buttons_frame, text="- remover selecionada", command=self.remove_folder, width=20).pack(side=tk.LEFT, padx=5)
        ttk.Button(folders_buttons_frame, text="limpar tudo", command=self.clear_folders, width=15).pack(side=tk.LEFT, padx=5)
        
        folders_list_frame = ttk.Frame(folders_label_frame)
        folders_list_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.folders_listbox = tk.Listbox(folders_list_frame, height=8)
        self.folders_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        folders_scrollbar = ttk.Scrollbar(folders_list_frame, orient=tk.VERTICAL, command=self.folders_listbox.yview)
        folders_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.folders_listbox.config(yscrollcommand=folders_scrollbar.set)
        
        # Pasta de destino
        ttk.Label(main_frame, text="pasta de destino (onde criar images/ e labels/):").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )
        
        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Entry(output_frame, textvariable=self.output_folder, width=70).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="procurar", command=self.browse_output_folder).pack(side=tk.LEFT, padx=5)
        
        # Info
        info_frame = ttk.LabelFrame(main_frame, text="o que o script faz:", padding="10")
        info_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(info_frame, text="1. você seleciona as pastas que quer mergear (pode adicionar quantas quiser)").pack(anchor=tk.W, pady=2)
        ttk.Label(info_frame, text="2. varre RECURSIVAMENTE todas as pastas procurando arquivos").pack(anchor=tk.W, pady=2)
        ttk.Label(info_frame, text="3. SEPARA AUTOMATICAMENTE: imagens (.jpg, .png) -> images/ | labels (.txt) -> labels/").pack(anchor=tk.W, pady=2)
        ttk.Label(info_frame, text="4. COPIA tudo (nao move) - pastas originais INTACTAS", font=('TkDefaultFont', 9, 'bold')).pack(anchor=tk.W, pady=2)
        ttk.Label(info_frame, text="5. pula arquivos duplicados (nao sobrescreve)").pack(anchor=tk.W, pady=2)
        
        self.process_button = ttk.Button(
            main_frame, 
            text="🚀 mergear tudo", 
            command=self.start_processing
        )
        self.process_button.grid(row=4, column=0, pady=15)
        
        ttk.Label(main_frame, text="progresso:").grid(row=5, column=0, sticky=tk.W, pady=5)
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate', length=400)
        self.progress_bar.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.status_label = ttk.Label(main_frame, text="aguardando...", foreground="blue")
        self.status_label.grid(row=7, column=0, sticky=tk.W, pady=5)
        
        log_frame = ttk.LabelFrame(main_frame, text="log", padding="5")
        log_frame.grid(row=8, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.log_text = tk.Text(log_frame, height=8, width=85)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(8, weight=1)
    
    def add_folder(self):
        folder = filedialog.askdirectory(title="selecionar pasta")
        if folder and folder not in self.folders:
            self.folders.append(folder)
            self.folders_listbox.insert(tk.END, folder)
            self.log_message(f"✓ pasta adicionada: {folder}")
        elif folder in self.folders:
            messagebox.showinfo("info", "essa pasta ja foi adicionada")
    
    def remove_folder(self):
        selection = self.folders_listbox.curselection()
        if selection:
            idx = selection[0]
            folder = self.folders[idx]
            del self.folders[idx]
            self.folders_listbox.delete(idx)
            self.log_message(f"✗ pasta removida: {folder}")
        else:
            messagebox.showinfo("info", "selecione uma pasta na lista para remover")
    
    def clear_folders(self):
        self.folders.clear()
        self.folders_listbox.delete(0, tk.END)
        self.log_message("todas as pastas foram removidas")
    
    def browse_output_folder(self):
        folder = filedialog.askdirectory(title="selecionar pasta de destino")
        if folder:
            self.output_folder.set(folder)
            self.log_message(f"pasta destino: {folder}")
    
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
        
        if not self.folders:
            messagebox.showerror("erro", "adicione pelo menos uma pasta")
            return
        
        output_folder = self.output_folder.get()
        
        if not output_folder:
            messagebox.showerror("erro", "selecione a pasta de destino")
            return
        
        self.is_processing = True
        self.process_button.config(state='disabled')
        self.progress_bar['value'] = 0
        self.log_text.delete(1.0, tk.END)
        
        thread = threading.Thread(target=self.process_folders, args=(output_folder,))
        thread.start()
    
    def process_folders(self, output_folder):
        try:
            self.log_message("🚀 iniciando merge...")
            self.log_message(f"📁 pastas selecionadas: {len(self.folders)}")
            for folder in self.folders:
                self.log_message(f"   • {folder}")
            self.update_progress(0, "varrendo pastas...")
            
            success, result = merge_folders(
                self.folders,
                output_folder,
                progress_callback=self.update_progress
            )
            
            if not success:
                self.log_message(f"\n❌ erro: {result}")
                messagebox.showerror("erro", result)
                return
            
            self.log_message(f"\n✅ merge concluido!")
            self.log_message(f"\n📊 resumo:")
            self.log_message(f"  • pastas processadas: {result['folders_count']}")
            self.log_message(f"  • imagens copiadas: {result['images_copied']}")
            self.log_message(f"  • labels copiados: {result['labels_copied']}")
            self.log_message(f"  • arquivos pulados: {result['images_skipped'] + result['labels_skipped']}")
            self.log_message(f"\n📂 destino:")
            self.log_message(f"  • {result['output_images']}")
            self.log_message(f"  • {result['output_labels']}")
            
            self.update_progress(100, "✅ concluido!")
            
            messagebox.showinfo(
                "✅ concluido!", 
                f"Merge realizado com sucesso!\n\n"
                f"📸 Imagens: {result['images_copied']}\n"
                f"📝 Labels: {result['labels_copied']}\n\n"
                f"📂 Destino:\n{output_folder}"
            )
            
        except Exception as e:
            self.log_message(f"\nerro durante processamento: {str(e)}")
            messagebox.showerror("erro", f"erro durante processamento:\n{str(e)}")
        
        finally:
            self.is_processing = False
            self.process_button.config(state='normal')


def main():
    root = tk.Tk()
    app = MergeDatasetGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
