import os
import yaml
import hashlib
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image, ImageTk


def generate_hash():
    import random
    import time
    content = f"{time.time()}{random.random()}".encode()
    hash_obj = hashlib.md5(content)
    return hash_obj.hexdigest()[:4]


def load_classes_from_yaml(yaml_path):
    try:
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
            return data.get('names', [])
    except Exception as e:
        return []


class ImageRenamerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("renomeador de imagens - dataset")
        self.root.geometry("900x700")
        
        self.folder_path = None
        self.image_files = []
        self.current_index = 0
        self.classes = []
        self.yaml_path = None
        
        self.setup_ui()
        self.bind_shortcuts()
    
    def setup_ui(self):
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        ttk.Button(top_frame, text="selecionar pasta de imagens", command=self.select_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="carregar data.yaml", command=self.load_yaml).pack(side=tk.LEFT, padx=5)
        
        self.yaml_label = ttk.Label(top_frame, text="yaml: nao carregado", foreground="red")
        self.yaml_label.pack(side=tk.LEFT, padx=10)
        
        image_frame = ttk.LabelFrame(self.root, text="imagem atual", padding="10")
        image_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.image_label = ttk.Label(image_frame, text="nenhuma imagem carregada", anchor=tk.CENTER)
        self.image_label.pack(fill=tk.BOTH, expand=True)
        
        info_frame = ttk.Frame(self.root, padding="10")
        info_frame.pack(fill=tk.X)
        
        self.filename_label = ttk.Label(info_frame, text="arquivo: -", font=("Arial", 10, "bold"))
        self.filename_label.pack(anchor=tk.W)
        
        self.counter_label = ttk.Label(info_frame, text="imagem 0 de 0")
        self.counter_label.pack(anchor=tk.W)
        
        control_frame = ttk.LabelFrame(self.root, text="controles", padding="10")
        control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        class_frame = ttk.Frame(control_frame)
        class_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(class_frame, text="classe:").pack(side=tk.LEFT, padx=5)
        
        self.class_var = tk.StringVar()
        self.class_combo = ttk.Combobox(class_frame, textvariable=self.class_var, state="readonly", width=20)
        self.class_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Label(class_frame, text="periodo:").pack(side=tk.LEFT, padx=5)
        
        self.period_var = tk.StringVar(value="dia")
        self.period_combo = ttk.Combobox(class_frame, textvariable=self.period_var, state="readonly", width=10)
        self.period_combo['values'] = ['dia', 'noite']
        self.period_combo.current(0)
        self.period_combo.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(class_frame, text="salvar (enter)", command=self.rename_image).pack(side=tk.LEFT, padx=5)
        
        nav_frame = ttk.Frame(control_frame)
        nav_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(nav_frame, text="< anterior (seta esq)", command=self.previous_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="proxima > (seta dir)", command=self.next_image).pack(side=tk.LEFT, padx=5)
        ttk.Button(nav_frame, text="excluir (delete)", command=self.delete_image).pack(side=tk.LEFT, padx=5)
        
        help_frame = ttk.LabelFrame(self.root, text="atalhos", padding="5")
        help_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(help_frame, text="enter: salvar | delete: excluir | seta esq: anterior | seta dir: proxima").pack()
    
    def bind_shortcuts(self):
        self.root.bind('<Return>', lambda e: self.rename_image())
        self.root.bind('<Delete>', lambda e: self.delete_image())
        self.root.bind('<Left>', lambda e: self.previous_image())
        self.root.bind('<Right>', lambda e: self.next_image())
    
    def load_yaml(self):
        yaml_path = filedialog.askopenfilename(
            title="selecionar data.yaml",
            filetypes=[("yaml", "*.yaml"), ("todos", "*.*")]
        )
        
        if not yaml_path:
            return
        
        classes = load_classes_from_yaml(yaml_path)
        
        if not classes:
            messagebox.showerror("erro", "nenhuma classe encontrada no yaml")
            return
        
        self.yaml_path = yaml_path
        self.classes = classes
        self.class_combo['values'] = classes
        
        if classes:
            self.class_combo.current(0)
        
        self.yaml_label.config(text=f"yaml: {Path(yaml_path).name} ({len(classes)} classes)", foreground="green")
        messagebox.showinfo("sucesso", f"{len(classes)} classes carregadas:\n" + ", ".join(classes))
    
    def select_folder(self):
        folder = filedialog.askdirectory(title="selecionar pasta com imagens")
        
        if not folder:
            return
        
        self.folder_path = Path(folder)
        self.image_files = sorted([f for f in self.folder_path.glob("*.jpg")])
        
        if not self.image_files:
            messagebox.showerror("erro", "nenhuma imagem .jpg encontrada na pasta")
            return
        
        self.current_index = 0
        self.load_current_image()
        messagebox.showinfo("sucesso", f"{len(self.image_files)} imagens encontradas")
    
    def load_current_image(self):
        if not self.image_files:
            return
        
        if self.current_index < 0:
            self.current_index = 0
        elif self.current_index >= len(self.image_files):
            self.current_index = len(self.image_files) - 1
        
        current_file = self.image_files[self.current_index]
        
        try:
            img = Image.open(current_file)
            
            label_width = self.image_label.winfo_width()
            label_height = self.image_label.winfo_height()
            
            if label_width > 1 and label_height > 1:
                img.thumbnail((label_width - 20, label_height - 20), Image.Resampling.LANCZOS)
            else:
                img.thumbnail((800, 600), Image.Resampling.LANCZOS)
            
            photo = ImageTk.PhotoImage(img)
            
            self.image_label.config(image=photo, text="")
            self.image_label.image = photo
            
            self.filename_label.config(text=f"arquivo: {current_file.name}")
            self.counter_label.config(text=f"imagem {self.current_index + 1} de {len(self.image_files)}")
            
        except Exception as e:
            messagebox.showerror("erro", f"erro ao carregar imagem:\n{str(e)}")
    
    def next_image(self):
        if not self.image_files:
            return
        
        self.current_index += 1
        
        if self.current_index >= len(self.image_files):
            self.current_index = len(self.image_files) - 1
            messagebox.showinfo("fim", "esta e a ultima imagem")
        
        self.load_current_image()
    
    def previous_image(self):
        if not self.image_files:
            return
        
        self.current_index -= 1
        
        if self.current_index < 0:
            self.current_index = 0
            messagebox.showinfo("inicio", "esta e a primeira imagem")
        
        self.load_current_image()
    
    def rename_image(self):
        if not self.image_files:
            messagebox.showerror("erro", "nenhuma imagem carregada")
            return
        
        if not self.classes:
            messagebox.showerror("erro", "carregue o data.yaml primeiro")
            return
        
        selected_class = self.class_var.get()
        selected_period = self.period_var.get()
        
        if not selected_class:
            messagebox.showerror("erro", "selecione uma classe")
            return
        
        if not selected_period:
            messagebox.showerror("erro", "selecione um periodo")
            return
        
        current_file = self.image_files[self.current_index]
        class_name = selected_class.lower().replace(" ", "_")
        hash_code = generate_hash()
        new_name = f"{class_name}_{selected_period}_{hash_code}.jpg"
        new_path = current_file.parent / new_name
        
        try:
            current_file.rename(new_path)
            
            self.image_files[self.current_index] = new_path
            
            messagebox.showinfo("sucesso", f"renomeado para:\n{new_name}")
            
            self.next_image()
            
        except Exception as e:
            messagebox.showerror("erro", f"erro ao renomear:\n{str(e)}")
    
    def delete_image(self):
        if not self.image_files:
            messagebox.showerror("erro", "nenhuma imagem carregada")
            return
        
        current_file = self.image_files[self.current_index]
        
        try:
            current_file.unlink()
            
            self.image_files.pop(self.current_index)
            
            if not self.image_files:
                self.image_label.config(image="", text="nenhuma imagem restante")
                self.filename_label.config(text="arquivo: -")
                self.counter_label.config(text="imagem 0 de 0")
                messagebox.showinfo("concluido", "todas as imagens foram processadas")
                return
            
            if self.current_index >= len(self.image_files):
                self.current_index = len(self.image_files) - 1
            
            self.load_current_image()
            
        except Exception as e:
            messagebox.showerror("erro", f"erro ao excluir:\n{str(e)}")


def main():
    root = tk.Tk()
    app = ImageRenamerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
