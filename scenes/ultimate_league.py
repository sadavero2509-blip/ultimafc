import pygame
import random
from settings import *
from scene_manager import BaseScene
from systems.ultimate_manager import ultimate_manager

# Definición de umbrales por división
LEAGUE_DATA = {
    10: {"perm": 0, "asc": 12, "title": 18, "diff": 1, "reward_p": "SOBRE BRONCE", "reward_m": 1000},
    9:  {"perm": 0, "asc": 14, "title": 20, "diff": 2, "reward_p": "SOBRE BRONCE PREMIUM", "reward_m": 1500},
    8:  {"perm": 0, "asc": 16, "title": 22, "diff": 3, "reward_p": "SOBRE PLATA", "reward_m": 2500},
    7:  {"perm": 8, "asc": 18, "title": 24, "diff": 4, "reward_p": "SOBRE PLATA PREMIUM", "reward_m": 4000},
    6:  {"perm": 10, "asc": 19, "title": 25, "diff": 5, "reward_p": "SOBRE ORO", "reward_m": 6000},
    5:  {"perm": 11, "asc": 20, "title": 26, "diff": 6, "reward_p": "SOBRE ORO PREMIUM", "reward_m": 8000},
    4:  {"perm": 12, "asc": 21, "title": 27, "diff": 7, "reward_p": "SOBRE ÉLITE LEYENDA", "reward_m": 12000},
    3:  {"perm": 14, "asc": 22, "title": 28, "diff": 8, "reward_p": "SOBRE ÉLITE LEYENDA", "reward_m": 20000},
    2:  {"perm": 15, "asc": 23, "title": 29, "diff": 9, "reward_p": "SOBRE ÉLITE LEYENDA", "reward_m": 35000},
    1:  {"perm": 18, "asc": 99, "title": 30, "diff": 10, "reward_p": "SOBRE ÉLITE LEYENDA", "reward_m": 60000},
}

class UltimateLeagueScene(BaseScene):
    """Menú de Division Rivals / Liga en Ultimate Team."""

    def __init__(self, manager, is_online=False):
        super().__init__(manager)
        self.is_online = is_online
        self.state = ultimate_manager.online_league_state if is_online else ultimate_manager.league_state
        self.div = self.state["division"]
        self.data = LEAGUE_DATA[self.div]
        
        self.sel_idx = 0 # 0: Jugar, 1: Volver
        
        try:
            self.font_title = pygame.font.SysFont("Impact", 50)
            self.font_main = pygame.font.SysFont("Arial", 28, bold=True)
            self.font_small = pygame.font.SysFont("Arial", 18)
            self.font_points = pygame.font.SysFont("Impact", 72)
        except:
            self.font_title = pygame.font.Font(None, 60)
            self.font_main = pygame.font.Font(None, 32)
            self.font_small = pygame.font.Font(None, 20)
            self.font_points = pygame.font.Font(None, 80)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.sel_idx = (self.sel_idx - 1) % 2
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.sel_idx = (self.sel_idx + 1) % 2
                elif event.key == pygame.K_RETURN:
                    if self.sel_idx == 0:
                        self._start_league_match()
                    else:
                        self.manager.pop_scene()
                elif event.key == pygame.K_ESCAPE:
                    self.manager.pop_scene()

    def _start_league_match(self):
        starters = [p for p in ultimate_manager.squad[:11] if p]
        if len(starters) < 11:
            # En un entorno real habría un toast o aviso
            return
            
        p_team = {
            "primary": ultimate_manager.primary,
            "secondary": ultimate_manager.secondary,
            "accent": ultimate_manager.accent,
            "roster": [p for p in ultimate_manager.squad if p]
        }
        if ultimate_manager.badge:
            for k in ["badge_shape", "primary", "secondary", "accent"]:
                if k in ultimate_manager.badge:
                    p_team[k] = ultimate_manager.badge[k]
        if ultimate_manager.kit:
            for k in ["primary", "secondary", "accent"]:
                if k in ultimate_manager.kit:
                    p_team[k] = ultimate_manager.kit[k]
        
        # --- FORZAR IDENTIDAD PERSONALIZADA ---
        p_team["name"] = ultimate_manager.team_name
        p_team["short"] = ultimate_manager.abbreviation
        p_team["roster"] = [p for p in ultimate_manager.squad if p]

        if self.is_online:
            self.manager.shared_data["game_mode"] = "ultimate_online_league"
            self.manager.shared_data["match_reward"] = 3500
            self.manager.shared_data["starters"] = starters
            self.manager.shared_data["formation"] = ultimate_manager.formation
            from scenes.online_matchmaking import OnlineMatchmakingScene
            self.manager.transition_to(OnlineMatchmakingScene, team_data=p_team)
        else:
            # Seleccionar rival aleatorio basado en la división
            from data.teams import TEAMS
            club_teams = [t for t in TEAMS if not t.get("is_national", False)]
            rival_team = random.choice(club_teams)
            
            # Generar roster para el rival
            from data.rosters import get_base_rosters
            all_r = get_base_rosters()
            rival_roster = all_r.get(rival_team["short"], [])
            
            # Configurar dificultad según la división
            difficulty = self.data["diff"]
            
            # Iniciar partido
            self.manager.shared_data["game_mode"] = "ultimate_league"
            self.manager.shared_data["player_team"] = p_team
            self.manager.shared_data["rival_team"] = rival_team
            self.manager.shared_data["rival_team"]["roster"] = rival_roster
            self.manager.shared_data["difficulty"] = difficulty
            self.manager.shared_data["starters"] = starters
            self.manager.shared_data["formation"] = ultimate_manager.formation
            
            from scenes.match import MatchScene
            self.manager.transition_to(MatchScene)

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((15, 20, 35)) # Fondo oscuro premium
        
        # Dibujar gradiente sutil
        for i in range(HEIGHT):
            alpha = int(40 * (i / HEIGHT))
            pygame.draw.line(surface, (30, 40, 80, alpha), (0, i), (WIDTH, i))

        # Título
        mode_text = "DIVISION RIVALS (ONLINE)" if self.is_online else "LIGA DE CLUBES (OFFLINE)"
        title_surf = self.font_title.render(f"{mode_text} - DIV {self.div}", True, GOLD)
        surface.blit(title_surf, (50, 40))
        
        # Cuadro de Estado de Temporada
        self._draw_season_progress(surface)
        
        # Historial de partidos
        self._draw_history(surface)
        
        # Recompensas
        self._draw_rewards(surface)
        
        # Botones
        self._draw_buttons(surface)

    def _draw_season_progress(self, surface):
        rect = pygame.Rect(50, 120, 500, 250)
        pygame.draw.rect(surface, (25, 30, 50), rect, border_radius=15)
        pygame.draw.rect(surface, (50, 60, 100), rect, 2, border_radius=15)
        
        # Puntos actuales
        pts_label = self.font_main.render("PUNTOS ACTUALES", True, UI_TEXT_DIM)
        surface.blit(pts_label, (75, 140))
        
        pts_val = self.font_points.render(str(self.state["points"]), True, WHITE)
        surface.blit(pts_val, (75, 170))
        
        # Partidos restantes
        rem = 10 - self.state["matches_played"]
        rem_label = self.font_main.render(f"Partidos restantes: {rem}", True, UI_TEXT)
        surface.blit(rem_label, (250, 180))
        
        # Barra de progreso de puntos
        bar_x, bar_y = 75, 280
        bar_w, bar_h = 450, 30
        pygame.draw.rect(surface, (40, 45, 60), (bar_x, bar_y, bar_w, bar_h), border_radius=5)
        
        # Marcas de objetivos
        for key, color, label in [("perm", (150, 150, 150), "PERM"), ("asc", (100, 200, 255), "ASC"), ("title", GOLD, "TIT")]:
            target = self.data[key]
            if target > 0 and target <= 30:
                tx = bar_x + (target / 30.0) * bar_w
                pygame.draw.line(surface, color, (tx, bar_y - 5), (tx, bar_y + bar_h + 5), 3)
                lbl_s = self.font_small.render(f"{label}: {target}", True, color)
                surface.blit(lbl_s, (tx - lbl_s.get_width()//2, bar_y + bar_h + 8))
        
        # Relleno de la barra
        fill_w = int((self.state["points"] / 30.0) * bar_w)
        if fill_w > 0:
            pygame.draw.rect(surface, (0, 255, 120), (bar_x, bar_y, fill_w, bar_h), border_radius=5)

    def _draw_history(self, surface):
        rect = pygame.Rect(580, 120, 370, 100)
        pygame.draw.rect(surface, (25, 30, 50), rect, border_radius=10)
        
        label = self.font_main.render("HISTORIAL RECIENTE", True, UI_TEXT_DIM)
        surface.blit(label, (595, 130))
        
        history = self.state["history"][-10:] # Ultimos 10
        for i in range(10):
            hx = 600 + i * 35
            hy = 170
            col = (60, 65, 80)
            txt = "-"
            if i < len(history):
                res = history[i]
                if res == "W": col = (0, 200, 80); txt = "V"
                elif res == "D": col = (200, 200, 0); txt = "E"
                else: col = (220, 50, 50); txt = "D"
            
            pygame.draw.rect(surface, col, (hx, hy, 30, 30), border_radius=5)
            t_s = self.font_small.render(txt, True, WHITE)
            surface.blit(t_s, t_s.get_rect(center=(hx+15, hy+15)))

    def _draw_rewards(self, surface):
        rect = pygame.Rect(580, 235, 370, 135)
        pygame.draw.rect(surface, (25, 30, 50), rect, border_radius=10)
        pygame.draw.rect(surface, GOLD, rect, 1, border_radius=10)
        
        label = self.font_main.render("RECOMPENSA ESTIMADA", True, GOLD)
        surface.blit(label, (595, 245))
        
        # Determinar qué recompensa mostraría según su ritmo actual
        # Por ahora mostramos la de Ascenso si está cerca, o Campeonato
        rew_p = self.data["reward_p"]
        rew_m = self.data["reward_m"]
        
        p_surf = self.font_small.render(f"Premio: {rew_p}", True, WHITE)
        m_surf = self.font_small.render(f"Monedas: {rew_m:,}", True, UI_ACCENT)
        surface.blit(p_surf, (600, 285))
        surface.blit(m_surf, (600, 310))

    def _draw_buttons(self, surface):
        opts = ["SIGUIENTE PARTIDO", "VOLVER AL HUB"]
        for i, opt in enumerate(opts):
            color = UI_ACCENT if self.sel_idx == i else (100, 100, 110)
            bg = (40, 50, 80) if self.sel_idx == i else (25, 30, 50)
            
            rect = pygame.Rect(WIDTH//2 - 200, 480 + i * 80, 400, 60)
            pygame.draw.rect(surface, bg, rect, border_radius=10)
            if self.sel_idx == i:
                pygame.draw.rect(surface, color, rect, 3, border_radius=10)
            
            txt = self.font_main.render(opt, True, WHITE if self.sel_idx == i else UI_TEXT_DIM)
            surface.blit(txt, txt.get_rect(center=rect.center))
