import pygame
import time
from .main_menu import MenuScene
from settings import *
from systems.network import NetworkManager

class OnlineHubScene(MenuScene):
    def __init__(self, manager):
        super().__init__(manager)
        self.network = NetworkManager()
        self.connected = self.network.connected
        self.input_text = ""
        self.active_input = False
        
        # UI State
        self.tab = "CHAT" # CHAT o LEADERBOARD
        self.leaderboard_data = []
        
        # Estética Premium
        self.colors = {
            "bg": (15, 20, 30),
            "panel": (25, 35, 50),
            "accent": (0, 200, 255),
            "text": (240, 240, 250),
            "msg_bg": (40, 55, 75),
            "user_msg": (0, 100, 150)
        }

        if not self.connected:
            # Intentar conectar con un nombre por defecto si no hay uno
            # En una implementación real, esto vendría de un perfil de usuario
            user = getattr(manager, "username", "Jugador_" + str(int(time.time()) % 1000))
            self.network.connect(user)

    def update(self, dt):
        self.connected = self.network.connected
        
        # Si acabamos de conectar y el leaderboard está vacío, pedirlo
        if self.connected and not self.leaderboard_data and self.tab == "LEADERBOARD":
            self.leaderboard_data = self.network.get_leaderboard()

    def draw(self, screen):
        screen.fill(self.colors["bg"])
        
        # Dibujar Header
        self.draw_header(screen)
        
        # Dibujar Paneles laterales
        self.draw_players_panel(screen)
        
        # Contenido Principal
        if self.tab == "CHAT":
            self.draw_chat(screen)
        else:
            self.draw_leaderboard(screen)
            
        # Barra de estado
        status_color = (0, 255, 100) if self.connected else (255, 50, 50)
        status_text = "CONECTADO" if self.connected else "DESCONECTADO"
        pygame.draw.circle(screen, status_color, (WIDTH - 150, 40), 8)
        self.draw_text(screen, status_text, WIDTH - 130, 30, color=status_color, size=20)

    def draw_header(self, screen):
        pygame.draw.rect(screen, self.colors["panel"], (0, 0, WIDTH, 80))
        self.draw_text(screen, "ONLINE HUB", 40, 20, size=40, bold=True)
        
        # Tabs
        btn_chat_col = self.colors["accent"] if self.tab == "CHAT" else (100, 100, 100)
        btn_rank_col = self.colors["accent"] if self.tab == "LEADERBOARD" else (100, 100, 100)
        
        self.draw_text(screen, "[C] CHAT", 300, 30, color=btn_chat_col, size=25)
        self.draw_text(screen, "[L] RANKING MUNDIAL", 450, 30, color=btn_rank_col, size=25)
        self.draw_text(screen, "[P] BUSCAR PARTIDO", 720, 30, color=(100, 255, 100), size=25)
        self.draw_text(screen, "[ESC] VOLVER", WIDTH - 150, 70, size=20)

    def draw_players_panel(self, screen):
        panel_rect = pygame.Rect(WIDTH - 250, 100, 230, HEIGHT - 150)
        pygame.draw.rect(screen, self.colors["panel"], panel_rect, border_radius=10)
        self.draw_text(screen, "JUGADORES ONLINE", WIDTH - 240, 115, size=20, color=self.colors["accent"])
        
        y = 150
        for player in self.network.online_players:
            pygame.draw.circle(screen, (0, 255, 100), (WIDTH - 230, y + 12), 5)
            self.draw_text(screen, player, WIDTH - 215, y, size=18)
            y += 30

    def draw_chat(self, screen):
        chat_rect = pygame.Rect(40, 100, WIDTH - 320, HEIGHT - 220)
        pygame.draw.rect(screen, self.colors["panel"], chat_rect, border_radius=10)
        
        # Mensajes
        y = chat_rect.bottom - 40
        for msg in reversed(self.network.chat_messages[-15:]):
            txt = f"[{msg['time']}] {msg['user']}: {msg['msg']}"
            self.draw_text(screen, txt, 60, y, size=18)
            y -= 25
            
        # Input box
        input_rect = pygame.Rect(40, HEIGHT - 100, WIDTH - 320, 50)
        border_col = self.colors["accent"] if self.active_input else (100, 100, 100)
        pygame.draw.rect(screen, self.colors["panel"], input_rect, border_radius=5)
        pygame.draw.rect(screen, border_col, input_rect, 2, border_radius=5)
        
        display_text = self.input_text + ("|" if time.time() % 1 > 0.5 else "")
        self.draw_text(screen, display_text if self.input_text or self.active_input else "Escribe un mensaje...", 55, HEIGHT - 85, size=20)

    def draw_leaderboard(self, screen):
        rect = pygame.Rect(40, 100, WIDTH - 320, HEIGHT - 150)
        pygame.draw.rect(screen, self.colors["panel"], rect, border_radius=10)
        
        self.draw_text(screen, "POS   JUGADOR          EQUIPO            PUNTUACIÓN", 60, 120, color=self.colors["accent"], size=22, bold=True)
        
        y = 160
        for i, entry in enumerate(self.leaderboard_data):
            color = (255, 215, 0) if i == 0 else self.colors["text"]
            self.draw_text(screen, f"#{i+1}", 60, y, color=color)
            self.draw_text(screen, entry["username"], 130, y, color=color)
            self.draw_text(screen, entry.get("team", "S/E"), 300, y, color=color)
            self.draw_text(screen, str(entry["score"]), 500, y, color=color, bold=True)
            y += 40

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.manager.pop_scene()
            elif event.key == pygame.K_c:
                self.tab = "CHAT"
            elif event.key == pygame.K_l:
                self.tab = "LEADERBOARD"
                self.leaderboard_data = self.network.get_leaderboard()
            elif event.key == pygame.K_p:
                from scenes.online_team_select import OnlineTeamSelectScene
                self.manager.transition_to(OnlineTeamSelectScene)
            
            # Chat Input
            if self.tab == "CHAT":
                if event.key == pygame.K_RETURN:
                    if self.input_text.strip():
                        self.network.send_chat(self.input_text)
                        self.input_text = ""
                    self.active_input = not self.active_input
                elif event.key == pygame.K_BACKSPACE:
                    self.input_text = self.input_text[:-1]
                else:
                    if len(self.input_text) < 50 and event.unicode.isprintable():
                        self.input_text += event.unicode
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            input_rect = pygame.Rect(40, HEIGHT - 100, WIDTH - 320, 50)
            self.active_input = input_rect.collidepoint(event.pos)

    def draw_text(self, surface, text, x, y, size=24, color=(255, 255, 255), bold=False):
        font = pygame.font.SysFont("Arial", size, bold=bold)
        img = font.render(text, True, color)
        surface.blit(img, (x, y))
