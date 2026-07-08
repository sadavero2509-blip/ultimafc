import pygame
import time
from settings import *
from scene_manager import BaseScene
from systems.network import NetworkManager

class LoginScene(BaseScene):
    def __init__(self, manager):
        super().__init__(manager)
        self.net = NetworkManager()
        self.username = ""
        self.password = ""
        self.mode = "LOGIN" # o "REGISTER"
        self.active_field = 0 # 0: username, 1: password
        self.message = "BIENVENIDO A ULTIMA FC"
        self.msg_color = WHITE
        self.loading = False
        
        # Cargar credenciales guardadas si existen
        self._load_local_creds()

    def _load_local_creds(self):
        import json, os
        path = "saves/creds.json"
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    data = json.load(f)
                    self.username = data.get("user", "")
                    self.password = data.get("pass", "")
            except: pass

    def _save_local_creds(self):
        import json, os
        if not os.path.exists("saves"): os.makedirs("saves")
        with open("saves/creds.json", "w") as f:
            json.dump({"user": self.username, "pass": self.password}, f)

    def handle_events(self, events):
        if self.loading: return
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.active_field = (self.active_field + 1) % 2
                elif event.key == pygame.K_RETURN:
                    self._attempt_auth()
                elif event.key == pygame.K_BACKSPACE:
                    if self.active_field == 0: self.username = self.username[:-1]
                    else: self.password = self.password[:-1]
                elif event.key == pygame.K_DOWN:
                    self.active_field = 1
                elif event.key == pygame.K_UP:
                    self.active_field = 0
                elif event.key == pygame.K_F1:
                    self.mode = "REGISTER" if self.mode == "LOGIN" else "LOGIN"
                    self.message = f"MODO: {self.mode}"
                elif event.key == pygame.K_ESCAPE:
                    # OMITIR LOGIN -> Ir al menú principal en modo offline
                    from scenes.main_menu import MainMenuScene
                    self.manager.transition_to(MainMenuScene)
                else:
                    if len(event.unicode) > 0 and event.unicode.isprintable():
                        if self.active_field == 0:
                            if len(self.username) < 16: self.username += event.unicode
                        else:
                            if len(self.password) < 16: self.password += event.unicode

    def _attempt_auth(self):
        if not self.username or not self.password:
            self.message = "COMPLETA TODOS LOS CAMPOS"; self.msg_color = (255, 100, 100)
            return

        self.loading = True
        self.message = "CONECTANDO..."
        self.msg_color = GOLD
        
        import threading
        def worker():
            if self.mode == "LOGIN":
                success, msg = self.net.login(self.username, self.password)
            else:
                success, msg = self.net.register(self.username, self.password)
            
            if success:
                self.message = "¡ÉXITO!"; self.msg_color = (100, 255, 100)
                self._save_local_creds()
                
                # Iniciar la carga del modo Ultimate de inmediato para el nuevo usuario
                try:
                    from systems.ultimate_manager import ultimate_manager
                    import threading
                    threading.Thread(target=ultimate_manager.load_ultimate, daemon=True).start()
                except Exception as e:
                    print(f"Error iniciando sincronización inicial del club: {e}")
                
                time.sleep(1.0)
                from scenes.main_menu import MainMenuScene
                self.manager.transition_to(MainMenuScene)
            else:
                self.message = msg.upper(); self.msg_color = (255, 100, 100)
                self.loading = False

        threading.Thread(target=worker, daemon=True).start()

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((10, 15, 30))
        
        # Título
        try: f_title = pygame.font.SysFont("Impact", 60)
        except: f_title = pygame.font.Font(None, 60)
        t_surf = f_title.render("ULTIMA FC", True, GOLD)
        surface.blit(t_surf, t_surf.get_rect(center=(WIDTH//2, 100)))
        
        # Mensaje de estado
        try: f_msg = pygame.font.SysFont("Arial", 20, bold=True)
        except: f_msg = pygame.font.Font(None, 20)
        m_surf = f_msg.render(self.message, True, self.msg_color)
        surface.blit(m_surf, m_surf.get_rect(center=(WIDTH//2, 180)))
        
        # Campos
        try: f_label = pygame.font.SysFont("Arial", 18)
        except: f_label = pygame.font.Font(None, 18)
        
        # Username
        u_col = GOLD if self.active_field == 0 else (100, 100, 100)
        surface.blit(f_label.render("USUARIO:", True, u_col), (WIDTH//2 - 150, 250))
        pygame.draw.rect(surface, u_col, (WIDTH//2 - 150, 275, 300, 40), 2, border_radius=5)
        surface.blit(f_label.render(self.username, True, WHITE), (WIDTH//2 - 140, 285))
        
        # Password
        p_col = GOLD if self.active_field == 1 else (100, 100, 100)
        surface.blit(f_label.render("CONTRASEÑA:", True, p_col), (WIDTH//2 - 150, 340))
        pygame.draw.rect(surface, p_col, (WIDTH//2 - 150, 365, 300, 40), 2, border_radius=5)
        stars = "*" * len(self.password)
        surface.blit(f_label.render(stars, True, WHITE), (WIDTH//2 - 140, 375))
        
        # Botón / Instrucciones
        hint = "PRESIONA ENTER PARA " + ("ENTRAR" if self.mode == "LOGIN" else "REGISTRARSE")
        if self.loading: hint = "CARGANDO..."
        h_surf = f_label.render(hint, True, GOLD)
        surface.blit(h_surf, h_surf.get_rect(center=(WIDTH//2, 480)))
        
        mode_hint = "F1: CAMBIAR A " + ("REGISTRO" if self.mode == "LOGIN" else "LOGIN")
        mh_surf = f_label.render(mode_hint, True, (150, 150, 150))
        surface.blit(mh_surf, mh_surf.get_rect(center=(WIDTH//2, 520)))
        
        esc_hint = "ESC: JUGAR EN MODO OFFLINE (OMITIR)"
        eh_surf = f_label.render(esc_hint, True, (150, 150, 180))
        surface.blit(eh_surf, eh_surf.get_rect(center=(WIDTH//2, 555)))
        
        if not self.net.connected and not self.loading:
            off_surf = f_label.render("[!] MODO OFFLINE DETECTADO (Reintentando...)", True, (255, 100, 100))
            surface.blit(off_surf, off_surf.get_rect(center=(WIDTH//2, HEIGHT - 50)))
