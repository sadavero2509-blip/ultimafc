import pygame
import random
import math
import time
from settings import *
from .main_menu import MenuScene
from data.teams import TEAMS, draw_badge
from systems.ultimate_manager import ultimate_manager

class UltimateSetupScene(MenuScene):
    def __init__(self, manager):
        super().__init__(manager)
        
        self.auto_skip = False

        self.step = "INTRO" # INTRO, BADGE, KIT, NAME, STARTER
        self.fade = 0
        self.selected = 0
        
        # Opciones para Badge y Kit
        self.options_badges = self._generate_options("badge")
        self.options_kits = self._generate_options("kit")
        
        self.team_name = ""
        self.team_short = ""
        self.active_input = "NAME" # NAME, SHORT
        
        self.starter_items = []
        self.pack_opened = False

    def _generate_options(self, type):
        # Filtrar solo los equipos paródicos reales (los 30 originales creados manualmente)
        real_parodies = [t for t in TEAMS if t.get("is_real_parody") or not t.get("is_procedural")]
        db_options = random.sample(real_parodies, min(4, len(real_parodies)))
        
        # 2 diseños procedurales únicos
        proc_options = []
        prefixes = ["Nova", "Apex", "Zenith", "Titan", "Vanguard", "Atlas"]
        suffixes = ["United", "City", "F.C.", "Athletic", "Sporting", "Real"]
        
        for i in range(2):
            name = f"{random.choice(prefixes)} {random.choice(suffixes)}"
            # Colores vibrantes y estéticos
            p_col = (random.randint(20, 200), random.randint(20, 200), random.randint(20, 200))
            s_col = (random.randint(150, 255), random.randint(150, 255), random.randint(150, 255))
            
            proc = {
                "name": name,
                "short": name[:3].upper(),
                "primary": p_col,
                "secondary": s_col,
                "accent": (255, 215, 0),
                "badge_shape": random.choice(["shield", "circle", "diamond"]),
                "is_procedural": True
            }
            proc_options.append(proc)
            
        final_options = db_options + proc_options
        random.shuffle(final_options) # Mezclar para que los procedurales no estén siempre al final
        return final_options

    def update(self, dt):
        if self.auto_skip or (ultimate_manager.badge and ultimate_manager.kit and ultimate_manager.team_name != "Mi Club"):
            from .ultimate_hub import UltimateHubScene
            self.manager.transition_to(UltimateHubScene)
            return

        if self.fade < 255:
            self.fade += dt * 500
            if self.fade > 255: self.fade = 255

    def draw(self, screen):
        screen.fill((10, 15, 25))
        
        if self.step == "INTRO":
            self.draw_text(screen, "ULTIMA FC CLUB", WIDTH//2 - 200, HEIGHT//2 - 50, size=50, bold=True, color=UI_ACCENT)
            self.draw_text(screen, "Crea tu legado. Domina el mundo.", WIDTH//2 - 150, HEIGHT//2 + 20, size=24, color=UI_TEXT_DIM)
            self.draw_text(screen, "PRESIONA ENTER PARA COMENZAR", WIDTH//2 - 140, HEIGHT - 100, size=18, alpha=int(abs(math.sin(time.time()*3))*255))
            
        elif self.step == "BADGE":
            self.draw_text(screen, "ELIGE TU ESCUDO FUNDACIONAL", 50, 50, size=30, bold=True)
            self._draw_grid(screen, self.options_badges, "badge")
            
        elif self.step == "KIT":
            self.draw_text(screen, "ELIGE TUS COLORES", 50, 50, size=30, bold=True)
            self._draw_grid(screen, self.options_kits, "kit")
            
        elif self.step == "NAME":
            self.draw_text(screen, "IDENTIDAD DEL CLUB", WIDTH//2 - 150, 150, size=40, bold=True)
            
            # Nombre
            col_n = UI_ACCENT if self.active_input == "NAME" else WHITE
            self.draw_text(screen, "NOMBRE DEL CLUB:", WIDTH//2 - 300, 300, size=25, color=col_n)
            pygame.draw.rect(screen, (30, 40, 60), (WIDTH//2 - 50, 290, 350, 45), border_radius=5)
            self.draw_text(screen, self.team_name + ("|" if time.time()%1 > 0.5 and self.active_input=="NAME" else ""), WIDTH//2 - 40, 300, size=25)
            
            # Abreviatura
            col_s = UI_ACCENT if self.active_input == "SHORT" else WHITE
            self.draw_text(screen, "ABREVIATURA (3):", WIDTH//2 - 300, 380, size=25, color=col_s)
            pygame.draw.rect(screen, (30, 40, 60), (WIDTH//2 - 50, 370, 100, 45), border_radius=5)
            self.draw_text(screen, self.team_short + ("|" if time.time()%1 > 0.5 and self.active_input=="SHORT" else ""), WIDTH//2 - 40, 380, size=25)
            
            self.draw_text(screen, "PRESIONA ENTER PARA CONFIRMAR", WIDTH//2 - 150, 500, size=20, color=UI_TEXT_DIM)

        elif self.step == "STARTER":
            self.draw_text(screen, "¡TU SOBRE INICIAL!", WIDTH//2 - 150, 50, size=40, bold=True, color=(255, 215, 0))
            if not self.pack_opened:
                self.draw_text(screen, "PRESIONA ESPACIO PARA ABRIR", WIDTH//2 - 150, HEIGHT//2, size=25)
            else:
                # Dibujar los items del sobre
                self._draw_starter_items(screen)

    def _draw_grid(self, screen, options, type):
        for i, opt in enumerate(options):
            x = 100 + (i % 3) * 300
            y = 150 + (i // 3) * 250
            rect = pygame.Rect(x, y, 250, 200)
            
            is_sel = (self.selected == i)
            bg_col = (40, 60, 90) if is_sel else (25, 35, 50)
            pygame.draw.rect(screen, bg_col, rect, border_radius=15)
            if is_sel: pygame.draw.rect(screen, UI_ACCENT, rect, 3, border_radius=15)
            
            if type == "badge":
                draw_badge(screen, opt, x + 125, y + 100, size=100)
            else:
                from data.teams import draw_uniform_preview
                draw_uniform_preview(screen, opt, x + 125, y + 50, scale=1.5)
            
            name = opt["name"]
            # Fondo para el nombre para evitar que se pierda con colores claros
            label_bg = pygame.Rect(x + 5, y + 165, 240, 30)
            pygame.draw.rect(screen, (0, 0, 0, 150), label_bg, border_radius=5)
            self.draw_text(screen, name, x + 125, y + 170, size=18, center=True, bold=True)

    def _draw_starter_items(self, screen):
        from systems.card_renderer import card_renderer
        # Mostrar los primeros 5 jugadores del sobre
        players = [item["data"] for item in self.starter_items if item["type"] == "player"][:5]
        for i, p in enumerate(players):
            card_renderer.render_card(screen, p, 50 + i * 190, 150, scale=1.0)
            
        self.draw_text(screen, "¡TU CLUB HA SIDO CREADO!", WIDTH//2 - 150, HEIGHT - 100, size=25, color=UI_ACCENT)
        self.draw_text(screen, "ENTER PARA CONTINUAR", WIDTH//2 - 100, HEIGHT - 50, size=18)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.manager.pop_scene()
            elif self.step == "INTRO" and event.key == pygame.K_RETURN:
                self.step = "BADGE"
            elif self.step == "BADGE":
                if event.key == pygame.K_LEFT: self.selected = (self.selected - 1) % 6
                elif event.key == pygame.K_RIGHT: self.selected = (self.selected + 1) % 6
                elif event.key == pygame.K_UP: self.selected = (self.selected - 3) % 6
                elif event.key == pygame.K_DOWN: self.selected = (self.selected + 3) % 6
                elif event.key == pygame.K_RETURN:
                    ultimate_manager.badge = self.options_badges[self.selected]
                    self.step = "KIT"
                    self.selected = 0
            elif self.step == "KIT":
                if event.key == pygame.K_LEFT: self.selected = (self.selected - 1) % 6
                elif event.key == pygame.K_RIGHT: self.selected = (self.selected + 1) % 6
                elif event.key == pygame.K_UP: self.selected = (self.selected - 3) % 6
                elif event.key == pygame.K_DOWN: self.selected = (self.selected + 3) % 6
                elif event.key == pygame.K_RETURN:
                    kit_data = self.options_kits[self.selected]
                    ultimate_manager.kit = kit_data
                    ultimate_manager.primary = kit_data.get("primary", (0, 100, 200))
                    ultimate_manager.secondary = kit_data.get("secondary", (255, 255, 255))
                    ultimate_manager.accent = kit_data.get("accent", (255, 215, 0))
                    self.step = "NAME"
                    self.selected = 0
            elif self.step == "NAME":
                if event.key == pygame.K_TAB:
                    self.active_input = "SHORT" if self.active_input == "NAME" else "NAME"
                elif event.key == pygame.K_RETURN:
                    if self.active_input == "NAME" and self.team_name:
                        # Si no hay abreviatura, generar una automática (3 primeras letras)
                        if not self.team_short:
                            name_clean = "".join(c for c in self.team_name if c.isalnum()).upper()
                            self.team_short = name_clean[:3].ljust(3, "X")
                        self.active_input = "SHORT"
                    elif self.active_input == "SHORT" and len(self.team_short) == 3:
                        ultimate_manager.team_name = self.team_name
                        ultimate_manager.abbreviation = self.team_short
                        self.step = "STARTER"
                        
                elif event.key == pygame.K_BACKSPACE:
                    if self.active_input == "NAME": self.team_name = self.team_name[:-1]
                    else: self.team_short = self.team_short[:-1]
                else:
                    if self.active_input == "NAME" and len(self.team_name) < 20:
                        if event.unicode.isprintable(): self.team_name += event.unicode
                    elif self.active_input == "SHORT" and len(self.team_short) < 3:
                        if event.unicode.isalpha(): self.team_short += event.unicode.upper()
            elif self.step == "STARTER":
                if event.key == pygame.K_SPACE and not self.pack_opened:
                    self.starter_items = ultimate_manager.create_starter_pack()
                    self.pack_opened = True
                elif event.key == pygame.K_RETURN and self.pack_opened:
                    from .ultimate_hub import UltimateHubScene
                    self.manager.transition_to(UltimateHubScene)
