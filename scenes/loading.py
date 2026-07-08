import pygame
import time
import math
from settings import *
from systems.updater import Updater
from .main_menu import MenuScene, BaseScene

class LoadingScene(MenuScene):
    def __init__(self, manager):
        super().__init__(manager)
        self.start_time = time.time()
        self.timeout = 5.0 # Segundos antes de rendirse con el servidor
        self.status = "Iniciando sistemas..."
        self.server_ready = False
        self.can_continue = False
        self.dots = ""
        self.last_dot_time = time.time()
        
        # Sistema de Auto-Actualización
        # Sistema de Auto-Actualización
        from systems.network import NetworkManager
        self.updater = Updater(NetworkManager().server_url)
        self.update_checked = False
        self.major_update_needed = False
        self.major_update_ver = ""

    def update(self, dt):
        # Si se requiere actualización mayor obligatoria, bloquear la ejecución de cualquier otra lógica
        if self.major_update_needed:
            return

        # Animación de puntitos
        if time.time() - self.last_dot_time > 0.5:
            self.dots = "." * ((len(self.dots) + 1) % 4)
            self.last_dot_time = time.time()

        from systems.network import NetworkManager
        nm = NetworkManager()

        # 1. PASO PREVIO: AUTO-ACTUALIZACIÓN
        import sys
        if not self.update_checked:
            success, msg = self.updater.check_and_update(lambda m: setattr(self, 'status', m))
            self.update_checked = True
            
            if not success and "MAJOR_UPDATE_REQUIRED" in msg:
                self.major_update_needed = True
                self.major_update_ver = msg.split("|")[1] if "|" in msg else "1.2.0"
                self.status = f"Nueva versión obligatoria requerida: v{self.major_update_ver}"
                return
            elif success:
                if "MINOR_UPDATE_APPLIED" in msg:
                    self.status = "Actualización en vivo aplicada. Reiniciando..."
                    self.draw(pygame.display.get_surface())
                    pygame.display.flip()
                    time.sleep(1.5)
                    sys.exit(99)  # 99 le dice a JUGAR.bat que debe reiniciar
                elif "EXE_UPDATE_PENDING" in msg:
                    # Nueva versión descargada — lanzar bat de reemplazo y cerrar
                    self.status = "Nueva versión lista. Aplicando actualización..."
                    self.draw(pygame.display.get_surface())
                    pygame.display.flip()
                    time.sleep(1.0)
                    # Lanzar el bat que reemplazará el exe mientras estamos cerrados
                    import subprocess
                    import os
                    exe_dir  = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.getcwd()
                    bat_path = os.path.join(exe_dir, "_apply_update.bat")
                    if os.path.exists(bat_path):
                        subprocess.Popen(["cmd", "/c", "start", "", bat_path], shell=True)
                    sys.exit(0)  # Cerrar limpiamente — el bat relanzará el exe actualizado
                elif "ALREADY_UP_TO_DATE" in msg:
                    self.status = "Archivos sincronizados con el servidor."
        
        if not self.server_ready:
            elapsed = time.time() - self.start_time
            if elapsed > self.timeout:
                self.status = "Servidor no detectado (Modo Offline)"
                self.server_ready = True
                self.can_continue = True
            else:
                # Comprobar si NetworkManager ya está conectado
                if nm.connected:
                    # Verificar Versión
                    try:
                        import requests
                        from settings import GAME_VERSION
                        # Usar la URL del servidor directamente
                        r = requests.get(nm.server_url, timeout=1)
                        if r.status_code == 200:
                            try:
                                res_data = r.json()
                            except (ValueError, Exception):
                                res_data = {}
                            srv_ver = res_data.get("version", "0.0.0")
                            srv_update_type = res_data.get("update_type", "minor")
                            
                            # Si es una actualización mayor, bloquear aquí también por seguridad
                            if srv_ver != GAME_VERSION and srv_update_type == "major":
                                self.major_update_needed = True
                                self.major_update_ver = srv_ver
                                self.status = f"Versión obligatoria requerida: v{srv_ver}"
                                return
                            elif srv_ver != GAME_VERSION:
                                self.status = f"Jugando con parches en vivo (v{srv_ver})"
                            else:
                                self.status = "¡Conexión establecida y validada!"
                        else:
                            self.status = "¡Conexión establecida!"
                    except:
                        self.status = "¡Conexión establecida!"
                        
                    self.server_ready = True
                    self.can_continue = True
                else:
                    self.status = f"Conectando al servidor central{self.dots}"

    def draw(self, screen):
        screen.fill((10, 15, 25))
        
        # CASO 1: PANTALLA DE BLOQUEO POR ACTUALIZACIÓN MAYOR
        if self.major_update_needed:
            # Título llamativo en rojo
            self.draw_text(screen, "ACTUALIZACIÓN OBLIGATORIA", WIDTH//2, HEIGHT//2 - 140, size=40, bold=True, color=RED, center=True)
            self.draw_text(screen, f"Tu versión: {GAME_VERSION}  ·  Versión requerida: {self.major_update_ver}", WIDTH//2, HEIGHT//2 - 80, size=20, color=WHITE, center=True)
            
            # Línea decorativa
            pygame.draw.line(screen, RED, (WIDTH//2 - 250, HEIGHT//2 - 40), (WIDTH//2 + 250, HEIGHT//2 - 40), 2)
            
            # Mensajes informativos
            self.draw_text(screen, "Esta versión del juego ya no es compatible con el servidor central.", WIDTH//2, HEIGHT//2, size=18, color=UI_TEXT_DIM, center=True)
            self.draw_text(screen, "Para poder jugar, debes descargar e instalar la última versión desde la tienda.", WIDTH//2, HEIGHT//2 + 30, size=18, color=UI_TEXT_DIM, center=True)
            
            # Botón visual
            btn_rect = pygame.Rect(WIDTH//2 - 220, HEIGHT//2 + 100, 440, 50)
            pygame.draw.rect(screen, (220, 50, 50), btn_rect, border_radius=10)
            self.draw_text(screen, "ABRIR CARPETA DEL INSTALADOR", WIDTH//2, HEIGHT//2 + 115, size=18, bold=True, color=WHITE, center=True)
            
            # Atajo / Hint
            self.draw_text(screen, "Presiona [ESPACIO] para abrir la carpeta de instalación", WIDTH//2, HEIGHT - 100, size=16, color=GOLD, center=True)
            return

        # CASO 2: PANTALLA DE CARGA NORMAL
        # Logo o Título
        self.draw_text(screen, "ULTIMA FC", WIDTH//2, HEIGHT//2 - 100, size=60, bold=True, color=UI_ACCENT, center=True)
        
        # Barra de progreso (decorativa)
        bar_w = 400
        pygame.draw.rect(screen, (30, 40, 60), (WIDTH//2 - bar_w//2, HEIGHT//2 + 20, bar_w, 10), border_radius=5)
        if not self.can_continue:
            prog = min(1.0, (time.time() - self.start_time) / self.timeout)
            pygame.draw.rect(screen, UI_ACCENT, (WIDTH//2 - bar_w//2, HEIGHT//2 + 20, int(bar_w * prog), 10), border_radius=5)
        else:
            pygame.draw.rect(screen, (50, 200, 100), (WIDTH//2 - bar_w//2, HEIGHT//2 + 20, bar_w, 10), border_radius=5)

        self.draw_text(screen, self.status, WIDTH//2, HEIGHT//2 + 50, size=18, color=WHITE, center=True)
        
        if self.can_continue:
            alpha = int(abs(math.sin(time.time() * 4) * 255))
            self.draw_text(screen, "PRESIONA ENTER PARA COMENZAR", WIDTH//2, HEIGHT - 100, size=22, alpha=alpha, center=True, color=UI_ACCENT)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.major_update_needed:
                # Si requiere actualización mayor, abrir la carpeta contenedora con ESPACIO
                if event.key == pygame.K_SPACE:
                    import os
                    import sys
                    path = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.getcwd()
                    try:
                        os.startfile(path)
                    except Exception as e:
                        print(f"Error al abrir carpeta: {e}")
                return

            if event.key == pygame.K_RETURN and self.can_continue:
                from .main_menu import MainMenuScene
                self.manager.transition_to(MainMenuScene)
