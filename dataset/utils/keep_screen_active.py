import pyautogui
import keyboard
import time


def keep_screen_active():
    print("="*60)
    print("MANTEDOR DE TELA ATIVA")
    print("="*60)
    print("\n✓ script iniciado")
    print("• clicando no meio da tela a cada 30 segundos")
    print("• pressione ESC para parar\n")
    
    screen_width, screen_height = pyautogui.size()
    center_x = screen_width // 2
    center_y = screen_height // 2
    
    print(f"resolucao da tela: {screen_width}x{screen_height}")
    print(f"posicao dos cliques: ({center_x}, {center_y})\n")
    
    click_count = 0
    
    try:
        while True:
            if keyboard.is_pressed('esc'):
                print("\n✓ ESC pressionado - parando...")
                break
            
            pyautogui.click(center_x, center_y)
            click_count += 1
            
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] clique #{click_count} - tela mantida ativa")
            
            time.sleep(30)
    
    except KeyboardInterrupt:
        print("\n✓ interrompido pelo usuario")
    
    print(f"\n{'='*60}")
    print(f"total de cliques: {click_count}")
    print(f"tempo ativo: ~{click_count * 30 / 60:.1f} minutos")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    keep_screen_active()
