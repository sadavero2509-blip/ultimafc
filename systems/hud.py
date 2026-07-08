import pygame
from settings import *
from data.teams import draw_badge


class HUD:
    """Head-Up Display: marcador, reloj, indicadores de partido."""

    def __init__(self, left_team, right_team, match_duration=MATCH_DURATION, is_free_mode=False):
        self.left_team = left_team
        self.right_team = right_team
        self.left_score = 0
        self.right_score = 0
        self.match_duration = 180 # 3 real minutes approx for 90 game minutes
        self.half_duration = self.match_duration // 2
        self.is_free_mode = is_free_mode
        self.paused = False
        self.half = 1 # 1: First half, 2: Second half
        self.match_time = 0.0

        # Flash de gol
        self.goal_flash_timer = 0
        self.goal_flash_side = None

        try:
            self.font_score = pygame.font.SysFont("Impact", 42)
            self.font_team = pygame.font.SysFont("Arial", 16, bold=True)
            self.font_time = pygame.font.SysFont("Consolas", 28, bold=True)
            self.font_label = pygame.font.SysFont("Arial", 12)
            self.font_info = pygame.font.SysFont("Arial", 14)
        except:
            self.font_score = pygame.font.Font(None, 42)
            self.font_team = pygame.font.Font(None, 16)
            self.font_time = pygame.font.Font(None, 28)
            self.font_label = pygame.font.Font(None, 12)
            self.font_info = pygame.font.Font(None, 14)

    def add_goal(self, side, scorer_name=None, minute=0):
        """Registra un gol."""
        if side == "left":
            self.left_score += 1
        else:
            self.right_score += 1
        self.goal_flash_timer = 3.0 # Más tiempo para leer el nombre y minuto
        self.goal_flash_side = side
        self.last_scorer = scorer_name
        self.last_goal_min = minute

    def update(self, dt):
        if not self.paused and not self.is_free_mode:
            self.match_time += dt

        if self.goal_flash_timer > 0:
            self.goal_flash_timer -= dt

    def is_half_over(self):
        if self.is_free_mode: return False
        limit = self.half_duration if self.half == 1 else self.match_duration
        return self.match_time >= limit

    def is_match_over(self):
        if self.is_free_mode:
            return False
        return self.match_time >= self.match_duration

    def get_time_display(self):
        """Formatea el tiempo como MM' acelerado (0-90)."""
        if self.is_free_mode:
            total_sec = int(self.match_time)
            minutes = total_sec // 60
            seconds = total_sec % 60
            return f"{minutes:02d}:{seconds:02d}"
        
        # Scale: match_duration (180s) -> 90 minutes
        # 1 real second = 0.5 minutes
        game_minutes = int(self.match_time * (90 / self.match_duration))
        game_minutes = min(90, game_minutes)
        
        half_label = "1T" if self.half == 1 else "2T"
        return f"{half_label} {game_minutes}'"

    def draw(self, surface):
        # ── Panel superior (scoreboard) ──
        panel_w = 420
        panel_h = 48
        panel_x = (WIDTH - panel_w) // 2
        panel_y = 2

        # Fondo del panel con transparencia
        panel_surf = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (10, 10, 20, 200), (0, 0, panel_w, panel_h),
                         border_radius=10)
        pygame.draw.rect(panel_surf, (60, 60, 80, 150), (0, 0, panel_w, panel_h),
                         1, border_radius=10)
        surface.blit(panel_surf, (panel_x, panel_y))

        cy = panel_y + panel_h // 2

        # ── Equipo izquierdo ──
        # Escudo mini
        draw_badge(surface, self.left_team, panel_x + 30, cy, size=28)

        # Nombre corto
        left_name = self.font_team.render(self.left_team["short"], True, UI_TEXT)
        surface.blit(left_name, (panel_x + 52, cy - 8))

        # ── Marcador ──
        score_text = f"{self.left_score}  -  {self.right_score}"
        score_surf = self.font_score.render(score_text, True, WHITE)
        score_rect = score_surf.get_rect(center=(WIDTH // 2, cy))
        surface.blit(score_surf, score_rect)

        # Flash de gol en el número y notificación de autor
        if self.goal_flash_timer > 0:
            flash_alpha = min(255, int(255 * (self.goal_flash_timer / 0.8)))
            
            # 1. Resaltar marcador
            flash_surf = self.font_score.render(score_text, True, YELLOW)
            flash_surf.set_alpha(flash_alpha)
            surface.blit(flash_surf, score_rect)
            
            # 2. Notificación debajo (Nombre + Minuto)
            if self.last_scorer:
                info_text = f"GOL: {self.last_scorer} ({self.last_goal_min}')"
                info_surf = self.font_info.render(info_text, True, WHITE)
                
                # Fondo pequeño para la notificación
                bg_w = info_surf.get_width() + 20
                bg_h = 24
                bg_rect = pygame.Rect(WIDTH // 2 - bg_w // 2, panel_y + panel_h + 5, bg_w, bg_h)
                
                bg_surf = pygame.Surface((bg_w, bg_h), pygame.SRCALPHA)
                pygame.draw.rect(bg_surf, (200, 30, 30, flash_alpha) if self.goal_flash_side == "left" else (30, 30, 200, flash_alpha), 
                                 (0, 0, bg_w, bg_h), border_radius=5)
                surface.blit(bg_surf, bg_rect)
                
                info_surf.set_alpha(flash_alpha)
                surface.blit(info_surf, (bg_rect.centerx - info_surf.get_width() // 2, bg_rect.centery - info_surf.get_height() // 2))


        # ── Equipo derecho ──
        right_name = self.font_team.render(self.right_team["short"], True, UI_TEXT)
        rn_rect = right_name.get_rect()
        surface.blit(right_name, (panel_x + panel_w - 52 - rn_rect.width, cy - 8))

        draw_badge(surface, self.right_team, panel_x + panel_w - 30, cy, size=28)

        # ── Reloj ──
        time_text = self.get_time_display()
        time_color = WHITE
        if not self.is_free_mode:
            remaining = self.match_duration - self.match_time
            if remaining < 30:
                time_color = RED  # Últimos 30 segundos en rojo

        time_surf = self.font_time.render(time_text, True, time_color)
        time_rect = time_surf.get_rect(center=(WIDTH // 2, panel_y + panel_h + 16))
        # Fondo del reloj
        time_bg = pygame.Surface((time_rect.width + 16, time_rect.height + 6), pygame.SRCALPHA)
        pygame.draw.rect(time_bg, (10, 10, 20, 180),
                         (0, 0, time_rect.width + 16, time_rect.height + 6),
                         border_radius=6)
        surface.blit(time_bg, (time_rect.x - 8, time_rect.y - 3))
        surface.blit(time_surf, time_rect)

        # ── Controles info (esquina inferior) ──
        controls = "Flechas: Mover  |  S: Pasar/Presión  |  A: Chutar/Entrada  |  W: Al Hueco  |  D: Centro  |  E: Sprint  |  Q: Cambiar"
        ctrl_surf = self.font_info.render(controls, True, (100, 100, 120))
        ctrl_rect = ctrl_surf.get_rect(center=(WIDTH // 2, HEIGHT - 12))
        surface.blit(ctrl_surf, ctrl_rect)

        # ── Info del jugador controlado (Bottom Left) ──
        # Necesitamos obtener el jugador controlado del match_scene
        match_state = getattr(self, 'shared_match_state', None)
        if match_state:
            all_players = match_state.get("left_field", []) + match_state.get("right_field", []) + [match_state.get("left_gk"), match_state.get("right_gk")]
            controlled = next((p for p in all_players if p and p.is_controlled), None)
            
            if controlled:
                # Panel de jugador
                p_rect = pygame.Rect(20, HEIGHT - 80, 200, 50)
                # Fondo degradado o cristal
                p_surf = pygame.Surface((p_rect.width, p_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(p_surf, (10, 10, 25, 180), (0, 0, p_rect.width, p_rect.height), border_radius=10)
                pygame.draw.rect(p_surf, (100, 100, 255, 100), (0, 0, p_rect.width, p_rect.height), 1, border_radius=10)
                surface.blit(p_surf, p_rect)

                # Nombre y OVR
                p_name = self.font_team.render(controlled.player_data["name"].upper(), True, WHITE)
                surface.blit(p_name, (p_rect.x + 15, p_rect.y + 8))
                
                # Barra de Stamina
                s_w = 170
                s_h = 8
                sx = p_rect.x + 15
                sy = p_rect.y + 30
                
                # Fondo barra
                pygame.draw.rect(surface, (30, 30, 40), (sx, sy, s_w, s_h), border_radius=4)
                
                # Proporción
                ratio = controlled.energy / 100.0
                if ratio > 0.6: s_col = (50, 255, 100)
                elif ratio > 0.3: s_col = (255, 220, 50)
                else: s_col = (255, 50, 50)
                
                pygame.draw.rect(surface, s_col, (sx, sy, int(s_w * ratio), s_h), border_radius=4)
                pygame.draw.rect(surface, (255, 255, 255, 50), (sx, sy, s_w, s_h), 1, border_radius=4)
