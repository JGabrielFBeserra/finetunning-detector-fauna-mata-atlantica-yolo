import cv2
import numpy as np
from ultralytics import YOLO
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import threading
import time
from datetime import datetime
import mss
import mss.tools
import gc
import os


class ScreenDetectorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("detector de tela - yolov8")
        self.root.geometry("900x700")
        
        self.model_path = tk.StringVar(value="yolov8n-detector-gamba.pt")
        self.detection_interval = tk.DoubleVar(value=0.5)  # meio segundo
        self.confidence_threshold = tk.DoubleVar(value=0.50)
        self.log_file_path = tk.StringVar(value="screen_detections.txt")
        self.save_folder = tk.StringVar(value="detections_images")  # Pasta para salvar imagens
        
        self.is_running = False
        self.detection_thread = None
        self.total_detections = 0
        self.frames_processed = 0
        self.frames_since_gc = 0  # Contador para garbage collection
        
        # Coordenadas da região a capturar
        self.capture_region = None
        self.selecting = False
        
        self.setup_ui()
    
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # INSTRUÇÕES
        instructions = ttk.LabelFrame(main_frame, text="📋 Como usar", padding="10")
        instructions.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Label(
            instructions, 
            text="1. Abra o vídeo da câmera no navegador em tela cheia ou janela grande\n"
                 "2. Clique em 'Selecionar Região' e arraste o mouse sobre o vídeo\n"
                 "3. Configure o modelo e intervalo\n"
                 "4. Clique em 'Iniciar Detecção'",
            justify=tk.LEFT,
            font=("Arial", 9)
        ).pack(anchor=tk.W)
        
        # SELEÇÃO DE REGIÃO
        region_frame = ttk.LabelFrame(main_frame, text="🎯 Região da Tela", padding="10")
        region_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=10)
        
        btn_frame = ttk.Frame(region_frame)
        btn_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(btn_frame, text="🖱️ SELECIONAR REGIÃO", command=self.select_region, width=25).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="👁️ Visualizar", command=self.preview_region, width=15).pack(side=tk.LEFT, padx=5)
        
        self.region_label = ttk.Label(
            region_frame,
            text="Nenhuma região selecionada",
            foreground="red",
            font=("Arial", 9)
        )
        self.region_label.pack(pady=5)
        
        # MODELO YOLO
        ttk.Label(main_frame, text="🤖 Modelo YOLO (.pt):").grid(row=2, column=0, sticky=tk.W, pady=5)
        
        model_frame = ttk.Frame(main_frame)
        model_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=5)
        
        ttk.Entry(model_frame, textvariable=self.model_path, width=60).pack(side=tk.LEFT, fill=tk.X, expand=True)
        ttk.Button(model_frame, text="procurar", command=self.browse_model).pack(side=tk.LEFT, padx=5)
        
        # CONFIGURAÇÕES
        config_frame = ttk.LabelFrame(main_frame, text="⚙️ Configurações", padding="10")
        config_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=10)
        
        # Intervalo de detecção
        interval_frame = ttk.Frame(config_frame)
        interval_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(interval_frame, text="Intervalo entre detecções (segundos):").pack(side=tk.LEFT, padx=5)
        interval_spin = ttk.Spinbox(
            interval_frame, 
            from_=0.1, 
            to=10.0, 
            increment=0.1,
            textvariable=self.detection_interval,
            width=10
        )
        interval_spin.pack(side=tk.LEFT, padx=5)
        ttk.Label(interval_frame, text="(0.5 = 2 capturas/seg)").pack(side=tk.LEFT, padx=5)
        
        # Confiança
        conf_frame = ttk.Frame(config_frame)
        conf_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(conf_frame, text="Confiança mínima:").pack(side=tk.LEFT, padx=5)
        
        self.confidence_scale = tk.Scale(
            conf_frame,
            from_=0.0,
            to=1.0,
            resolution=0.01,
            orient=tk.HORIZONTAL,
            variable=self.confidence_threshold,
            command=self.update_confidence_label,
            showvalue=False,
            length=300
        )
        self.confidence_scale.pack(side=tk.LEFT, padx=5)
        
        self.confidence_label = ttk.Label(conf_frame, text="50%", foreground="blue", font=("Arial", 9, "bold"))
        self.confidence_label.pack(side=tk.LEFT, padx=5)
        
        # Arquivo de log
        log_frame = ttk.Frame(config_frame)
        log_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(log_frame, text="Arquivo de log:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(log_frame, textvariable=self.log_file_path, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(log_frame, text="escolher", command=self.browse_log_file).pack(side=tk.LEFT, padx=5)
        
        # Pasta para salvar imagens
        save_frame = ttk.Frame(config_frame)
        save_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(save_frame, text="Pasta p/ imagens:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(save_frame, textvariable=self.save_folder, width=40).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Button(save_frame, text="escolher", command=self.browse_save_folder).pack(side=tk.LEFT, padx=5)
        
        # CONTROLES
        controls_frame = ttk.Frame(main_frame)
        controls_frame.grid(row=5, column=0, pady=10)
        
        self.start_button = ttk.Button(controls_frame, text="▶ INICIAR DETECÇÃO", command=self.start_detection, width=25)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(controls_frame, text="⏹ PARAR", command=self.stop_detection, state='disabled', width=25)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # ESTATÍSTICAS
        stats_frame = ttk.LabelFrame(main_frame, text="📊 Estatísticas", padding="10")
        stats_frame.grid(row=6, column=0, sticky=(tk.W, tk.E), pady=10)
        
        self.stats_label = ttk.Label(
            stats_frame, 
            text="Frames processados: 0 | Detecções totais: 0 | Status: Aguardando...",
            font=("Arial", 9)
        )
        self.stats_label.pack()
        
        # LOG
        log_display_frame = ttk.LabelFrame(main_frame, text="📝 Log de Detecções (últimas 20 linhas)", padding="5")
        log_display_frame.grid(row=7, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.log_text = tk.Text(log_display_frame, height=15, width=100, font=("Courier New", 8))
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(log_display_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(7, weight=1)
    
    def browse_model(self):
        file_path = filedialog.askopenfilename(
            title="Selecionar modelo YOLO",
            filetypes=[("Modelo YOLO", "*.pt"), ("Todos os arquivos", "*.*")]
        )
        if file_path:
            self.model_path.set(file_path)
    
    def browse_log_file(self):
        file_path = filedialog.asksaveasfilename(
            title="Escolher arquivo de log",
            defaultextension=".txt",
            filetypes=[("Arquivo de texto", "*.txt"), ("Todos os arquivos", "*.*")]
        )
        if file_path:
            self.log_file_path.set(file_path)
    
    def browse_save_folder(self):
        folder_path = filedialog.askdirectory(title="Escolher pasta para salvar imagens")
        if folder_path:
            self.save_folder.set(folder_path)
    
    def update_confidence_label(self, value):
        threshold = float(value)
        percentage = int(threshold * 100)
        self.confidence_label.config(text=f"{percentage}%")
    
    def select_region(self):
        """Permite usuário selecionar região da tela"""
        # Minimizar janela
        self.root.iconify()
        time.sleep(0.5)
        
        # Capturar tela inteira
        with mss.mss() as sct:
            monitor = sct.monitors[1]  # Monitor principal
            screenshot = sct.grab(monitor)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        # Adicionar instruções na imagem
        instructions_img = img.copy()
        
        # Fundo semi-transparente para as instruções
        overlay = instructions_img.copy()
        cv2.rectangle(overlay, (50, 50), (800, 200), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, instructions_img, 0.3, 0, instructions_img)
        
        # Texto das instruções
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(instructions_img, "COMO SELECIONAR A REGIAO:", (60, 90), font, 0.8, (0, 255, 0), 2)
        cv2.putText(instructions_img, "1. Clique e arraste o mouse sobre a area do video", (60, 120), font, 0.6, (255, 255, 255), 1)
        cv2.putText(instructions_img, "2. Solte o botao do mouse", (60, 150), font, 0.6, (255, 255, 255), 1)
        cv2.putText(instructions_img, "3. Pressione ENTER para confirmar ou ESC para cancelar", (60, 180), font, 0.6, (255, 255, 255), 1)
        
        # Variáveis para seleção
        self.selecting = True
        start_point = None
        end_point = None
        drawing = False
        temp_img = instructions_img.copy()
        
        def mouse_callback(event, x, y, flags, param):
            nonlocal start_point, end_point, drawing, temp_img
            
            if event == cv2.EVENT_LBUTTONDOWN:
                start_point = (x, y)
                drawing = True
                # Remover instruções quando começar a desenhar
                temp_img = img.copy()
            
            elif event == cv2.EVENT_MOUSEMOVE and drawing:
                temp_img = img.copy()
                cv2.rectangle(temp_img, start_point, (x, y), (0, 255, 0), 3)
                # Mostrar coordenadas
                cv2.putText(temp_img, f"Largura: {abs(x - start_point[0])} px | Altura: {abs(y - start_point[1])} px", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.imshow("ARRASTE O MOUSE E PRESSIONE ENTER", temp_img)
            
            elif event == cv2.EVENT_LBUTTONUP:
                end_point = (x, y)
                drawing = False
                temp_img = img.copy()
                cv2.rectangle(temp_img, start_point, end_point, (0, 255, 0), 3)
                # Mostrar dimensões finais
                width = abs(end_point[0] - start_point[0])
                height = abs(end_point[1] - start_point[1])
                cv2.putText(temp_img, f"Regiao: {width}x{height} px - PRESSIONE ENTER PARA CONFIRMAR", 
                           (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                cv2.imshow("ARRASTE O MOUSE E PRESSIONE ENTER", temp_img)
        
        # Criar janela de seleção
        cv2.namedWindow("ARRASTE O MOUSE E PRESSIONE ENTER", cv2.WINDOW_NORMAL)
        cv2.setWindowProperty("ARRASTE O MOUSE E PRESSIONE ENTER", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        cv2.setMouseCallback("ARRASTE O MOUSE E PRESSIONE ENTER", mouse_callback)
        cv2.imshow("ARRASTE O MOUSE E PRESSIONE ENTER", instructions_img)
        
        # Aguardar seleção (ENTER = 13, ESC = 27)
        key = cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        # Restaurar janela
        self.root.deiconify()
        
        # Se apertou ESC, cancelar
        if key == 27:
            self.log_message("❌ Seleção cancelada")
            return
        
        if start_point and end_point:
            # Normalizar coordenadas
            x1 = min(start_point[0], end_point[0])
            y1 = min(start_point[1], end_point[1])
            x2 = max(start_point[0], end_point[0])
            y2 = max(start_point[1], end_point[1])
            
            # Validar região mínima
            width = x2 - x1
            height = y2 - y1
            
            if width < 50 or height < 50:
                messagebox.showwarning("Aviso", "Região muito pequena! Selecione uma área maior.")
                self.log_message("❌ Região muito pequena")
                return
            
            self.capture_region = {
                "left": x1,
                "top": y1,
                "width": width,
                "height": height
            }
            
            self.region_label.config(
                text=f"✓ Região: {width}x{height} px em ({x1}, {y1})",
                foreground="green"
            )
            self.log_message(f"✓ Região selecionada: {width}x{height} px")
        else:
            messagebox.showwarning("Aviso", "Você precisa ARRASTAR o mouse para selecionar uma região!")
            self.log_message("❌ Nenhuma região foi desenhada")
    
    def preview_region(self):
        """Mostra preview da região selecionada"""
        if not self.capture_region:
            messagebox.showwarning("Aviso", "Selecione uma região primeiro")
            return
        
        with mss.mss() as sct:
            screenshot = sct.grab(self.capture_region)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        cv2.imshow("Preview da Região - Pressione qualquer tecla", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    def capture_screen(self):
        """Captura a região selecionada da tela"""
        if not self.capture_region:
            return None
        
        with mss.mss() as sct:
            screenshot = sct.grab(self.capture_region)
            img = np.array(screenshot)
            img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        
        return img
    
    def log_message(self, message):
        """Adiciona mensagem ao log visual"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_message = f"[{timestamp}] {message}"
        
        self.log_text.insert(tk.END, full_message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
        # Limitar a 20 linhas
        lines = self.log_text.get("1.0", tk.END).split("\n")
        if len(lines) > 20:
            self.log_text.delete("1.0", "2.0")
    
    def log_to_file(self, message):
        """Salva detecção no arquivo de log com rotação automática"""
        try:
            log_path = self.log_file_path.get()
            
            # Verificar tamanho do arquivo (rotacionar se > 10 MB)
            if os.path.exists(log_path):
                file_size = os.path.getsize(log_path) / (1024 * 1024)  # MB
                if file_size > 10:
                    # Criar backup com timestamp
                    backup_name = log_path.replace('.txt', f'_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt')
                    os.rename(log_path, backup_name)
                    self.log_message(f"📦 Log rotacionado: {os.path.basename(backup_name)}")
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(f"[{timestamp}] {message}\n")
        except Exception as e:
            print(f"Erro ao salvar log: {e}")
    
    def update_stats(self):
        """Atualiza estatísticas na interface"""
        status = "🟢 RODANDO" if self.is_running else "🔴 PARADO"
        self.stats_label.config(
            text=f"Frames processados: {self.frames_processed} | "
                 f"Detecções totais: {self.total_detections} | "
                 f"Status: {status}"
        )
    
    def save_detection_frame(self, frame_original, frame_annotated, detections_info, frame_number):
        """Salva frame com e sem detecção em arquivos separados"""
        try:
            # Criar pasta se não existir
            save_folder = Path(self.save_folder.get())
            save_folder.mkdir(parents=True, exist_ok=True)
            
            # Gerar nome do arquivo com formato: classe-DD/MM/YYYY HH:MM:SS
            timestamp = datetime.now().strftime("%d-%m-%Y_%H-%M-%S")
            
            # Pegar primeira classe detectada
            first_class = detections_info[0].split("(")[0].strip().replace(" ", "-") if detections_info else "unknown"
            
            # Nome base
            base_name = f"{first_class}_{timestamp}"
            
            # Salvar ORIGINAL (sem detecção)
            filename_original = f"{base_name}_original.jpg"
            filepath_original = save_folder / filename_original
            cv2.imwrite(str(filepath_original), frame_original)
            
            # Salvar ANOTADO (com detecção)
            filename_annotated = f"{base_name}_detected.jpg"
            filepath_annotated = save_folder / filename_annotated
            cv2.imwrite(str(filepath_annotated), frame_annotated)
            
            return base_name
        except Exception as e:
            print(f"Erro ao salvar imagem: {e}")
            return None
    
    def start_detection(self):
        """Inicia o loop de detecção"""
        if not self.capture_region:
            messagebox.showerror("Erro", "Selecione uma região da tela primeiro")
            return
        
        model_path = self.model_path.get()
        
        if not model_path or not Path(model_path).exists():
            messagebox.showerror("Erro", "Selecione um modelo válido")
            return
        
        self.is_running = True
        self.frames_processed = 0
        self.total_detections = 0
        
        self.start_button.config(state='disabled')
        self.stop_button.config(state='normal')
        
        # Criar pasta de imagens se não existir
        save_folder = Path(self.save_folder.get())
        save_folder.mkdir(parents=True, exist_ok=True)
        
        # Criar cabeçalho do log
        self.log_to_file("="*80)
        self.log_to_file(f"NOVA SESSÃO DE DETECÇÃO INICIADA")
        self.log_to_file(f"Região: {self.capture_region['width']}x{self.capture_region['height']}")
        self.log_to_file(f"Modelo: {model_path}")
        self.log_to_file(f"Intervalo: {self.detection_interval.get()}s")
        self.log_to_file(f"Confiança: {self.confidence_threshold.get()}")
        self.log_to_file(f"Pasta de imagens: {save_folder.absolute()}")
        self.log_to_file("="*80)
        
        self.log_message("🚀 Detecção iniciada!")
        
        # Iniciar thread de detecção
        self.detection_thread = threading.Thread(target=self.detection_loop, daemon=True)
        self.detection_thread.start()
    
    def stop_detection(self):
        """Para o loop de detecção"""
        self.is_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        
        self.log_to_file("="*80)
        self.log_to_file(f"SESSÃO ENCERRADA - Frames: {self.frames_processed}, Detecções: {self.total_detections}")
        self.log_to_file("="*80 + "\n")
        
        self.log_message("⏹ Detecção parada!")
        self.update_stats()
    
    def detection_loop(self):
        """Loop principal de detecção"""
        try:
            # Carregar modelo
            model = YOLO(self.model_path.get())
            interval = self.detection_interval.get()
            threshold = self.confidence_threshold.get()
            
            self.log_message("✓ Modelo YOLO carregado")
            
            window_name = 'Screen Detector - Pressione Q para fechar janela'
            cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(window_name, 1280, 720)
            
            while self.is_running:
                start_time = time.time()
                
                # Capturar tela
                frame = self.capture_screen()
                
                if frame is None:
                    self.log_message("❌ Erro ao capturar tela")
                    time.sleep(interval)
                    continue
                
                # Processar com YOLO
                results = model(frame, imgsz=1920, verbose=False, conf=threshold)
                
                # Contador de detecções neste frame
                detections_in_frame = len(results[0].boxes)
                
                # Mostrar frame com detecções
                annotated_frame = results[0].plot()
                
                if detections_in_frame > 0:
                    self.total_detections += detections_in_frame
                    
                    # Logar cada detecção
                    detection_summary = []
                    for box in results[0].boxes:
                        class_id = int(box.cls[0])
                        confidence = float(box.conf[0])
                        class_name = results[0].names[class_id]
                        
                        detection_info = f"{class_name} ({confidence*100:.1f}%)"
                        detection_summary.append(detection_info)
                    
                    # Salvar AMBAS versões: original e anotada
                    saved_basename = self.save_detection_frame(frame, annotated_frame, detection_summary, self.frames_processed)
                    
                    # Log no arquivo
                    summary_text = f"Frame {self.frames_processed}: {detections_in_frame} detecção(ões) - {', '.join(detection_summary)}"
                    if saved_basename:
                        summary_text += f" | Salvo: {saved_basename}_original.jpg + {saved_basename}_detected.jpg"
                    self.log_to_file(summary_text)
                    
                    # Log visual
                    log_msg = f"🎯 {detections_in_frame} detecção(ões): {', '.join(detection_summary)}"
                    if saved_basename:
                        log_msg += f" | 💾 Salvo (2 versões)"
                    self.log_message(log_msg)
                else:
                    self.log_to_file(f"Frame {self.frames_processed}: Nenhuma detecção")
                
                # Adicionar info no frame
                info_text = f"Frame: {self.frames_processed} | Deteccoes: {detections_in_frame} | Total: {self.total_detections}"
                cv2.putText(annotated_frame, info_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                
                cv2.imshow(window_name, annotated_frame)
                
                self.frames_processed += 1
                self.frames_since_gc += 1
                self.update_stats()
                
                # Limpeza de memória a cada 100 frames (~50 segundos em 0.5s/frame)
                if self.frames_since_gc >= 100:
                    gc.collect()  # Garbage collection manual
                    cv2.destroyWindow(window_name)  # Recriar janela para limpar cache
                    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
                    cv2.resizeWindow(window_name, 1280, 720)
                    self.frames_since_gc = 0
                    self.log_message("🧹 Limpeza de memória executada")
                
                # Aguardar intervalo
                elapsed = time.time() - start_time
                wait_time = max(int((interval - elapsed) * 1000), 1)
                
                if cv2.waitKey(wait_time) & 0xFF == ord('q'):
                    self.is_running = False
                    break
            
            cv2.destroyAllWindows()
            
            # Limpeza final de memória
            gc.collect()
            self.log_message("🧹 Limpeza final de memória executada")
            
        except Exception as e:
            error_msg = f"❌ Erro no loop de detecção: {str(e)}"
            self.log_message(error_msg)
            self.log_to_file(error_msg)
            messagebox.showerror("Erro", error_msg)
        
        finally:
            self.is_running = False
            self.start_button.config(state='normal')
            self.stop_button.config(state='disabled')
            cv2.destroyAllWindows()
            gc.collect()  # Garantir limpeza


def main():
    root = tk.Tk()
    app = ScreenDetectorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
