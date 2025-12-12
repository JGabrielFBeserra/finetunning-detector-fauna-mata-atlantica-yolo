import os
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import re
from urllib.parse import unquote


def remove_hash_from_txt_files(folder_path, progress_callback=None):

    folder = Path(folder_path)
    
    if not folder.exists():
        return False, f"pasta nao encontrada: {folder_path}"
    
    txt_files = list(folder.glob("*.txt"))
    jpg_files = {f.stem: f for f in folder.glob("*.jpg")}
    
    if not txt_files:
        return False, "nenhum arquivo .txt encontrado na pasta"
    
    if not jpg_files:
        return False, "nenhuma imagem .jpg encontrada na pasta"
    
    renamed_count = 0
    not_found_count = 0
    already_correct = 0
    
    hash_pattern = re.compile(r'^[a-f0-9]{8}-')
    
    for idx, txt_file in enumerate(txt_files):
        txt_name = txt_file.stem
        
        match = hash_pattern.match(txt_name)
        
        if not match:
            already_correct += 1
            if progress_callback:
                progress = (idx + 1) / len(txt_files) * 100
                progress_callback(progress, f"ignorado (sem hash): {txt_file.name}")
            continue
        
        name_without_hash = txt_name[9:]
        
        name_decoded = unquote(name_without_hash)
        
        if name_decoded in jpg_files:
            new_txt_name = f"{name_decoded}.txt"
            new_txt_path = folder / new_txt_name
            
            try:
                if new_txt_path.exists():
                    if progress_callback:
                        progress_callback(None, f"aviso: {new_txt_name} ja existe, pulando {txt_file.name}")
                    not_found_count += 1
                    continue
                
                txt_file.rename(new_txt_path)
                renamed_count += 1
                
                if progress_callback:
                    progress = (idx + 1) / len(txt_files) * 100
                    progress_callback(progress, f"renomeado: {txt_file.name} -> {new_txt_name}")
                    
            except Exception as e:
                if progress_callback:
                    progress_callback(None, f"erro ao renomear {txt_file.name}: {str(e)}")
                not_found_count += 1
        else:
            not_found_count += 1
            if progress_callback:
                progress = (idx + 1) / len(txt_files) * 100
                progress_callback(progress, f"imagem nao encontrada para: {name_decoded}")
    
    return True, {
        'renamed': renamed_count,
        'not_found': not_found_count,
        'already_correct': already_correct,
        'total': len(txt_files)
    }


class TxtRenamerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("remover hash do label studio dos arquivos txt")
        self.root.geometry("700x500")
        
        self.folder_path = tk.StringVar()
        self.is_processing = False
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        ttk.Label(main_frame, text="selecionar pasta com imagens e labels:").grid(
            row=0, column=0, sticky=tk.W, pady=5
        )
        
        folder_frame = ttk.Frame(main_frame)
        folder_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Entry(folder_frame, textvariable=self.folder_path, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(folder_frame, text="procurar", command=self.browse_folder).pack(side=tk.LEFT, padx=5)
        
        info_frame = ttk.LabelFrame(main_frame, text="o que o script faz:", padding="10")
        info_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(info_frame, text="1. le todos os arquivos .txt e .jpg da pasta").pack(anchor=tk.W, pady=2)
        ttk.Label(info_frame, text="2. identifica arquivos .txt com hash do label studio (8 caracteres hexadecimais)").pack(anchor=tk.W, pady=2)
        ttk.Label(info_frame, text="3. remove o hash inicial e decodifica url encoding (%C3%BA -> ú)").pack(anchor=tk.W, pady=2)
        ttk.Label(info_frame, text="4. renomeia apenas se existir uma imagem .jpg correspondente").pack(anchor=tk.W, pady=2)
        ttk.Label(info_frame, text="5. mantem o conteudo dos arquivos .txt intacto").pack(anchor=tk.W, pady=2)
        
        example_frame = ttk.LabelFrame(main_frame, text="exemplo:", padding="10")
        example_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=10)
        
        ttk.Label(example_frame, text="txt: ed68c442-lagarto-tei%C3%BA_dia_e368.txt", foreground="blue").pack(anchor=tk.W)
        ttk.Label(example_frame, text="jpg: lagarto-teiú_dia_a44e.jpg", foreground="green").pack(anchor=tk.W)
        ttk.Label(example_frame, text="resultado: lagarto-teiú_dia_e368.txt", foreground="red").pack(anchor=tk.W)
        
        self.process_button = ttk.Button(
            main_frame, 
            text="processar arquivos", 
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
        
        self.log_text = tk.Text(log_frame, height=8, width=80)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(8, weight=1)
    
    def browse_folder(self):
        folder = filedialog.askdirectory(title="selecionar pasta")
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
            self.log_message("iniciando processamento...")
            self.update_progress(0, "analisando arquivos...")
            
            success, result = remove_hash_from_txt_files(
                folder_path, 
                progress_callback=self.update_progress
            )
            
            if not success:
                self.log_message(f"\nerro: {result}")
                messagebox.showerror("erro", result)
                return
            
            self.log_message(f"\nprocessamento concluido!")
            self.log_message(f"total de arquivos .txt: {result['total']}")
            self.log_message(f"arquivos renomeados: {result['renamed']}")
            self.log_message(f"ja estavam corretos: {result['already_correct']}")
            self.log_message(f"nao encontrados/erros: {result['not_found']}")
            
            self.update_progress(100, "concluido com sucesso")
            
            messagebox.showinfo(
                "concluido", 
                f"processamento concluido!\n\n"
                f"renomeados: {result['renamed']}\n"
                f"ja corretos: {result['already_correct']}\n"
                f"nao encontrados: {result['not_found']}"
            )
            
        except Exception as e:
            self.log_message(f"\nerro durante processamento: {str(e)}")
            messagebox.showerror("erro", f"erro durante processamento:\n{str(e)}")
        
        finally:
            self.is_processing = False
            self.process_button.config(state='normal')


def main():
    root = tk.Tk()
    app = TxtRenamerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
