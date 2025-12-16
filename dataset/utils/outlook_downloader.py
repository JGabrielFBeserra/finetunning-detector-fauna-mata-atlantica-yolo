import pyautogui
import time
import keyboard
import cv2
import numpy as np
from PIL import ImageGrab

"""
AUTOMAÇÃO PARA BAIXAR ANEXOS DE EMAILS DO OUTLOOK

INSTRUÇÕES ANTES DE EXECUTAR:
1. Abra o Outlook e selecione a pasta "DeteccaoFauna"
2. Clique no PRIMEIRO email que você quer baixar
3. Configure a pasta de download padrão do Outlook (Arquivo > Opções > Geral > "Salvar anexos em...")
4. Execute este script
5. Pressione ESC para parar a qualquer momento

O script irá:
- Clicar no anexo do email atual
- Baixar o anexo
- Ir para o próximo email (seta para baixo)
- Repetir o processo
"""

# CONFIGURAÇÕES
DELAY_ENTRE_ACOES = 1.0  # segundos de espera entre ações
DELAY_ANTES_ENTER = 6.0  # tempo de espera antes de pressionar Enter
TOTAL_EMAILS = 10000  # total de emails para processar (ou menos se quiser parar antes)
QUANTIDADE_SCROLL_UP = 10  # quantas vezes rolar para cima

# POSIÇÕES NA TELA (você pode ajustar se necessário)
# Ajuste essas coordenadas conforme necessário
COORD1_X = 1812  # primeira coordenada X para clicar
COORD1_Y = 487  # primeira coordenada Y para clicar

COORD2_X = 1629  # segunda coordenada X para clicar
COORD2_Y = 675  # segunda coordenada Y para clicar

ANEXO_X = 1153  # posição X do ícone do anexo
ANEXO_Y = 512  # posição Y do ícone do anexo (área do anexo)

def mostrar_onde_vai_clicar(x, y, texto="CLIQUE AQUI", duracao=3):
    """Captura a tela e desenha um círculo mostrando onde vai clicar"""
    # Captura a tela
    screenshot = ImageGrab.grab()
    screen = np.array(screenshot)
    screen = cv2.cvtColor(screen, cv2.COLOR_RGB2BGR)
    
    # Desenha círculo vermelho grande
    cv2.circle(screen, (x, y), 50, (0, 0, 255), 5)
    cv2.circle(screen, (x, y), 10, (0, 0, 255), -1)
    
    # Desenha cruz
    cv2.line(screen, (x-60, y), (x+60, y), (0, 0, 255), 3)
    cv2.line(screen, (x, y-60), (x, y+60), (0, 0, 255), 3)
    
    # Adiciona texto
    cv2.putText(screen, texto, (x-100, y-70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)
    cv2.putText(screen, f"X={x}, Y={y}", (x-100, y+90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    # Redimensiona para caber na tela se necessário
    height, width = screen.shape[:2]
    max_width = 1920
    max_height = 1080
    if width > max_width or height > max_height:
        scale = min(max_width/width, max_height/height)
        new_width = int(width * scale)
        new_height = int(height * scale)
        screen = cv2.resize(screen, (new_width, new_height))
    
    # Mostra a imagem
    cv2.imshow('Onde vai clicar - Pressione qualquer tecla para continuar', screen)
    cv2.waitKey(duracao * 1000)
    cv2.destroyAllWindows()

def clicar_com_seguranca(x, y, delay=0.5, mostrar=True):
    """Clica em uma posição com delay de segurança"""
    if mostrar:
        mostrar_onde_vai_clicar(x, y, "CLICANDO AQUI", 2)
    pyautogui.moveTo(x, y, duration=0.3)
    time.sleep(0.2)
    pyautogui.click()
    time.sleep(delay)

def verificar_parada():
    """Verifica se ESC foi pressionado"""
    if keyboard.is_pressed('esc'):
        print("\n⚠️ ESC pressionado - parando...")
        return True
    return False

def processar_email():
    """Executa a sequência completa para processar um email"""
    
    # 1. Clica na primeira coordenada
    print(f"      1️⃣ Clicando em COORD1 (X={COORD1_X}, Y={COORD1_Y})")
    pyautogui.click(COORD1_X, COORD1_Y)
    time.sleep(DELAY_ENTRE_ACOES)
    
    # 2. Clica na segunda coordenada
    print(f"      2️⃣ Clicando em COORD2 (X={COORD2_X}, Y={COORD2_Y})")
    pyautogui.click(COORD2_X, COORD2_Y)
    time.sleep(DELAY_ENTRE_ACOES)
    
    # 3. Rola tudo para cima
    print(f"      3️⃣ Rolando tudo para cima ({QUANTIDADE_SCROLL_UP}x)")
    for _ in range(QUANTIDADE_SCROLL_UP):
        pyautogui.scroll(500)  # Valor positivo = rolar para cima
        time.sleep(0.1)
    time.sleep(DELAY_ENTRE_ACOES)
    
    # 4. Clica no anexo
    print(f"      4️⃣ Clicando no anexo (X={ANEXO_X}, Y={ANEXO_Y})")
    pyautogui.click(ANEXO_X, ANEXO_Y)
    time.sleep(DELAY_ENTRE_ACOES)
    
    # 5. Espera 4 segundos
    print(f"      5️⃣ Aguardando {DELAY_ANTES_ENTER} segundos...")
    time.sleep(DELAY_ANTES_ENTER)
    
    # 6. Pressiona Enter
    print(f"      6️⃣ Pressionando Enter para baixar")
    pyautogui.press('enter')
    time.sleep(DELAY_ENTRE_ACOES)
    
    # 7. Pressiona Shift+Tab 5 vezes para voltar à lista de emails
    print(f"      7️⃣ Voltando à lista de emails (5x Shift+Tab)")
    for i in range(5):
        pyautogui.hotkey('shift', 'tab')
        time.sleep(0.3)
    time.sleep(DELAY_ENTRE_ACOES)
    
    # 8. Pressiona seta para baixo para próximo email
    print(f"      8️⃣ Indo para próximo email (seta ⬇️)")
    pyautogui.press('down')
    time.sleep(DELAY_ENTRE_ACOES)

def baixar_anexo_outlook():
    """Clica no anexo, espera 4 segundos e pressiona Enter"""
    # Clica uma vez no anexo (botão esquerdo)
    pyautogui.click(ANEXO_X, ANEXO_Y)
    print(f"      ✓ Clicou no anexo")
    
    # Espera 4 segundos
    print(f"      ⏳ Aguardando 4 segundos...")
    time.sleep(4)
    
    # Pressiona Enter para baixar
    print(f"      ⏎ Pressionando Enter para baixar")
    pyautogui.press('enter')
    time.sleep(1)

def proximo_email():
    """Vai para o próximo email usando seta para baixo"""
    pyautogui.press('down')
    time.sleep(0.5)

def main():
    print("="*60)
    print("AUTOMAÇÃO DE DOWNLOAD DE ANEXOS - OUTLOOK")
    print("="*60)
    print("\n⚠️ IMPORTANTE:")
    print("1. Certifique-se de que o Outlook está aberto e focado")
    print("2. Clique no PRIMEIRO email que deseja processar")
    print("3. O script mostrará ONDE VAI CLICAR antes de começar")
    print("4. Pressione ESC para parar a qualquer momento\n")
    
    # MOSTRA AS POSIÇÕES QUE VAI CLICAR
    print("🎯 TESTE: Mostrando as posições de clique...")
    print("\n1. COORD1:")
    mostrar_onde_vai_clicar(COORD1_X, COORD1_Y, "COORD1", 3)
    
    print("\n2. COORD2:")
    mostrar_onde_vai_clicar(COORD2_X, COORD2_Y, "COORD2", 3)
    
    print("\n3. ANEXO:")
    mostrar_onde_vai_clicar(ANEXO_X, ANEXO_Y, "ANEXO", 3)
    
    resposta = input("\n✅ Todas as posições estão corretas? (s/n): ")
    if resposta.lower() != 's':
        print("\n❌ Ajuste as coordenadas no código:")
        print(f"   COORD1_X = {COORD1_X}, COORD1_Y = {COORD1_Y}")
        print(f"   COORD2_X = {COORD2_X}, COORD2_Y = {COORD2_Y}")
        print(f"   ANEXO_X = {ANEXO_X}, ANEXO_Y = {ANEXO_Y}")
        return
    
    # Contagem regressiva
    print("\n⏳ Iniciando em:")
    for i in range(5, 0, -1):
        print(f"   {i}...")
        time.sleep(1)
    
    print("\n🚀 INICIANDO AUTOMAÇÃO...\n")
    
    emails_processados = 0
    emails_com_erro = 0
    
    try:
        for i in range(TOTAL_EMAILS):
            if verificar_parada():
                break
            
            print(f"\n📧 Processando email {i+1}/{TOTAL_EMAILS}...")
            
            try:
                # Executa a sequência completa
                processar_email()
                
                emails_processados += 1
                print(f"   ✅ Email {i+1} processado com sucesso\n")
                
            except Exception as e:
                print(f"   ❌ Erro ao processar email {i+1}: {str(e)}")
                emails_com_erro += 1
                # Tenta voltar à lista de emails e continuar
                try:
                    for _ in range(5):
                        pyautogui.hotkey('shift', 'tab')
                        time.sleep(0.3)
                    pyautogui.press('down')
                except:
                    pass
                continue
    
    except KeyboardInterrupt:
        print("\n⚠️ Interrompido pelo usuário")
    
    # Relatório final
    print("\n" + "="*60)
    print("RELATÓRIO FINAL")
    print("="*60)
    print(f"✅ Emails processados com sucesso: {emails_processados}")
    print(f"❌ Emails com erro: {emails_com_erro}")
    print(f"📊 Total processado: {emails_processados + emails_com_erro}/{TOTAL_EMAILS}")
    print("="*60)

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🎯 MODO DE TESTE DE POSIÇÃO")
    print("="*60)
    print("\nEscolha uma opção:")
    print("1 - Ver onde vai clicar (teste visual)")
    print("2 - Capturar posição do mouse (mova até o anexo e pressione CTRL+C)")
    print("3 - Iniciar automação\n")
    
    opcao = input("Opção: ")
    
    if opcao == "1":
        print("\n🎯 Mostrando onde o script vai clicar no anexo...")
        mostrar_onde_vai_clicar(ANEXO_X, ANEXO_Y, "ANEXO AQUI", 10)
        print(f"\n✅ Posição atual: X={ANEXO_X}, Y={ANEXO_Y}")
        print("Se estiver errado, escolha opção 2 para capturar a posição correta")
    
    elif opcao == "2":
        print("\n📍 Mova o mouse até o ícone do ANEXO no email")
        print("Pressione CTRL+C para capturar a posição\n")
        
        try:
            while True:
                x, y = pyautogui.position()
                print(f"\rPosição atual: X={x}, Y={y}   ", end="", flush=True)
                
                if keyboard.is_pressed('ctrl') and keyboard.is_pressed('c'):
                    print(f"\n\n✅ Posição capturada: X={x}, Y={y}")
                    print(f"\n⚠️ Atualize no código:")
                    print(f"ANEXO_X = {x}")
                    print(f"ANEXO_Y = {y}\n")
                    
                    # Mostra onde vai clicar com a nova posição
                    input("Pressione Enter para ver onde ficaria o clique...")
                    mostrar_onde_vai_clicar(x, y, "NOVO ANEXO AQUI", 5)
                    break
                
                if keyboard.is_pressed('esc'):
                    break
                
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
    
    elif opcao == "3":
        main()
    
    else:
        print("\n❌ Opção inválida")
