import pygame
import math
from settings import *

class LeagueSelectScene:
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        
        self.leagues = [
            {"id": "EN", "name": "Premier League",    "flag": "[ENG]", "region": "EU"},
            {"id": "ES", "name": "La Liga",           "flag": "[ESP]", "region": "EU"},
            {"id": "IT", "name": "Serie A",           "flag": "[ITA]", "region": "EU"},
            {"id": "DE", "name": "Bundesliga",        "flag": "[GER]", "region": "EU"},
            {"id": "FR", "name": "Ligue 1",           "flag": "[FRA]", "region": "EU"},
            {"id": "PT", "name": "Primeira Liga",     "flag": "[POR]", "region": "EU"},
            {"id": "BR", "name": "Brasileirão",       "flag": "[BRA]", "region": "SA"},
            {"id": "AR", "name": "Liga Profesional",  "flag": "[ARG]", "region": "SA"},
            {"id": "CO", "name": "Liga BetPlay",      "flag": "[COL]", "region": "SA"},
            {"id": "US", "name": "MLS",               "flag": "[USA]", "region": "NA"},
            {"id": "JP", "name": "J-League",          "flag": "[JPN]", "region": "AS"},
            {"id": "TR", "name": "Süper Lig",          "flag": "[TUR]", "region": "EU"},
            {"id": "BE", "name": "Pro League",         "flag": "[BEL]", "region": "EU"},
            {"id": "NT", "name": "Selecciones",       "flag": "[INT]", "region": "INT"}
        ]
        
        # New: add LIB league if viewing squads
        if self.context.get("mode") == "viewer":
            self.leagues.append({"id": "LIB", "name": "Agentes Libres", "flag": "[LIB]", "region": "INT"})
        
        self.tournament_type = self.context.get("tournament_type", None)
        if self.tournament_type == "champions":
            self.leagues = [l for l in self.leagues if l["region"] == "EU"]
        elif self.tournament_type == "libertadores":
            self.leagues = [l for l in self.leagues if l["region"] == "SA"]
            
        self.selected_idx = 0
        self.time = 0
        
        try:
            self.font_title = pygame.font.SysFont("Arial", 48, bold=True)
            self.font_name = pygame.font.SysFont("Arial", 20, bold=True)
            self.font_flag = pygame.font.SysFont("Segoe UI Emoji", 40)
            self.font_hint = pygame.font.SysFont("Arial", 16)
        except:
            self.font_title = pygame.font.Font(None, 48)
            self.font_name = pygame.font.Font(None, 20)
            self.font_flag = pygame.font.Font(None, 40)
            self.font_hint = pygame.font.Font(None, 16)
            
        self.cols = 5
        self.rows = math.ceil(len(self.leagues) / self.cols)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                col = self.selected_idx % self.cols
                row = self.selected_idx // self.cols
                
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    col = (col - 1) % self.cols
                    self._set_selected(row * self.cols + col)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    col = (col + 1) % self.cols
                    self._set_selected(row * self.cols + col)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    row = (row - 1) % self.rows
                    self._set_selected(row * self.cols + col)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    row = (row + 1) % self.rows
                    self._set_selected(row * self.cols + col)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self._proceed()
                elif event.key == pygame.K_ESCAPE:
                    if self.tournament_type:
                        from scenes.tournament_type_select import TournamentTypeSelectScene
                        self.manager.set_scene(TournamentTypeSelectScene, context=self.context)
                    else:
                        from scenes.mode_select import ModeSelectScene
                        self.manager.set_scene(ModeSelectScene, context=self.context)

    def _set_selected(self, val):
        self.selected_idx = val % len(self.leagues)

    def _proceed(self):
        lg = self.leagues[self.selected_idx]
        self.context["league"] = lg["id"]
        
        if self.context.get("mode") == "viewer":
            from scenes.team_viewer import TeamViewerScene
            self.manager.set_scene(TeamViewerScene, context=self.context)
        else:
            from scenes.team_select import TeamSelectScene
            self.manager.set_scene(TeamSelectScene, context=self.context)

    def update(self, dt):
        self.time += dt

    def draw(self, surface):
        surface.fill((10, 15, 25))
        
        # Draw background
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(15 + ratio * 8)
            g = int(15 + ratio * 5)
            b = int(30 + ratio * 15)
            pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

        title = "Selecciona Región"
        if self.tournament_type == "champions": title = "Ligas Europeas (Champions)"
        elif self.tournament_type == "libertadores": title = "Ligas Sudamericanas (Libertadores)"
            
        tsurf = self.font_title.render(title, True, UI_TEXT)
        surface.blit(tsurf, (WIDTH // 2 - tsurf.get_width() // 2, 50))
        
        pygame.draw.line(surface, UI_ACCENT, (WIDTH // 2 - 200, 100), (WIDTH // 2 + 200, 100), 2)
        
        # Grid variables
        card_w = 140
        card_h = 160
        gap = 25
        
        grid_w = self.cols * card_w + (self.cols - 1) * gap
        grid_h = self.rows * card_h + (self.rows - 1) * gap
        
        start_x = (WIDTH - grid_w) // 2
        start_y = (HEIGHT - grid_h) // 2 + 40
        
        for i, lg in enumerate(self.leagues):
            col = i % self.cols
            row = i // self.cols
            
            x = start_x + col * (card_w + gap)
            y = start_y + row * (card_h + gap)
            
            is_selected = i == self.selected_idx
            
            # Draw card
            card_rect = pygame.Rect(x, y, card_w, card_h)
            bg_color = UI_CARD_HOVER if is_selected else UI_CARD_BG
            pygame.draw.rect(surface, bg_color, card_rect, border_radius=12)
            
            if is_selected:
                pulse = (math.sin(self.time * 5) + 1) / 2
                bcol = (int(0 + pulse * 100), int(150 + pulse * 105), int(200 + pulse * 55))
                pygame.draw.rect(surface, bcol, card_rect, 3, border_radius=12)
            else:
                pygame.draw.rect(surface, (50, 50, 70), card_rect, 1, border_radius=12)
                
            # Content
            cx = x + card_w // 2
            
            # Flag circle
            pygame.draw.circle(surface, (40, 45, 60), (cx, y + 60), 45)
            pygame.draw.circle(surface, (70, 75, 90), (cx, y + 60), 45, 2)
            
            try:
                sz = 16 if len(lg["flag"]) > 1 else 32
                font = pygame.font.SysFont("Arial", sz, bold=True) if len(lg["flag"]) > 1 else self.font_flag
                fsurf = font.render(lg["flag"], True, (255, 255, 255))
                surface.blit(fsurf, (cx - fsurf.get_width()//2, y + 60 - fsurf.get_height()//2))
            except:
                pass
                
            # League Name
            nsurf = self.font_name.render(lg["name"], True, WHITE if is_selected else UI_TEXT_DIM)
            surface.blit(nsurf, (cx - nsurf.get_width()//2, y + 120))
            
        # Help text
        help_t = self.font_hint.render("↑↓←→ Navegar   ·   ENTER Seleccionar   ·   ESC Volver", True, UI_TEXT_DIM)
        surface.blit(help_t, (WIDTH // 2 - help_t.get_width() // 2, HEIGHT - 40))
