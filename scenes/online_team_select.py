import pygame
import math
from settings import *
from .main_menu import MenuScene
from data.teams import TEAMS, draw_badge

class OnlineTeamSelectScene(MenuScene):
    def __init__(self, manager):
        super().__init__(manager)
        # Agrupar equipos reales por liga
        all_real = [t for t in TEAMS if not t.get("is_filler", False)]
        self.leagues = {}
        for t in all_real:
            lg = t.get("league", "Otros")
            if lg not in self.leagues: self.leagues[lg] = []
            self.leagues[lg].append(t)
            
        self.league_list = sorted(list(self.leagues.keys()))
        self.league_names = {
            "AR": "LIGA PROFESIONAL (ARG)", 
            "BR": "BRASILEIRÃO (BRA)", 
            "CO": "LIGA BETPLAY (COL)", 
            "DE": "BUNDESLIGA (GER)",
            "EN": "PREMIER LEAGUE (ENG)", 
            "ES": "LA LIGA (ESP)", 
            "FR": "LIGUE 1 (FRA)", 
            "IT": "SERIE A (ITA)",
            "NT": "SELECCIONES NACIONALES", 
            "PT": "PRIMEIRA LIGA (POR)", 
            "US": "MLS (USA)", 
            "JP": "J-LEAGUE (JPN)",
            "TR": "SÜPER LIG (TUR)", 
            "BE": "PRO LEAGUE (BEL)", 
            "Otros": "OTROS"
        }
        
        self.sel_lg_idx = 0
        self.sel_tm_idx = 0
        self.hovered_idx = -1
        self.cols = 4
        
        # Soft-scrolling camera parameters
        self.scroll_y = 0.0
        self.target_scroll_y = 0.0
        
        # Time for aesthetic animations
        self.time = 0.0

    def update(self, dt):
        self.time += dt
        
        # Camera smooth-scroll interpolation
        self.scroll_y += (self.target_scroll_y - self.scroll_y) * 12.0 * dt
        
        # Keep hovered_idx updated for mouse hover preview
        mx, my = pygame.mouse.get_pos()
        current_lg_code = self.league_list[self.sel_lg_idx]
        teams = self.leagues[current_lg_code]
        
        self.hovered_idx = -1
        for i, team in enumerate(teams):
            row, col = divmod(i, self.cols)
            x, y = 80 + col * 230, 180 + row * 160 - self.scroll_y
            rect = pygame.Rect(x, y, 200, 140)
            if rect.collidepoint(mx, my):
                # Only hover if within the viewport bounds
                if 170 <= my <= HEIGHT - 75:
                    self.hovered_idx = i
                    break

    def draw(self, screen):
        # Premium dark space aesthetic background with a subtle blue/purple gradient
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(10 + ratio * 8)
            g = int(12 + ratio * 6)
            b = int(24 + ratio * 14)
            pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))
            
        # Draw dynamic ambient light glow behind the center
        glow_size = 400 + int(math.sin(self.time * 2.0) * 30.0)
        glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        pygame.draw.circle(glow_surface, (*UI_ACCENT, 8), (glow_size//2, glow_size//2), glow_size//2)
        screen.blit(glow_surface, (WIDTH//2 - glow_size//2, HEIGHT//2 - glow_size//2))
        
        # Header title
        self.draw_text(screen, "SELECCIÓN DE EQUIPO ONLINE", WIDTH//2, 35, size=36, color=UI_ACCENT, center=True, bold=True)
        
        current_lg_code = self.league_list[self.sel_lg_idx]
        current_lg_name = self.league_names.get(current_lg_code, current_lg_code)
        
        # Premium League selector at top
        sel_rect = pygame.Rect(WIDTH//2 - 250, 85, 500, 52)
        pygame.draw.rect(screen, (24, 30, 50), sel_rect, border_radius=12)
        pygame.draw.rect(screen, (40, 52, 85), sel_rect, 1, border_radius=12)
        
        # Clickable Arrow Indicators
        left_arrow_hover = pygame.Rect(WIDTH//2 - 250, 85, 50, 52).collidepoint(pygame.mouse.get_pos())
        right_arrow_hover = pygame.Rect(WIDTH//2 + 200, 85, 50, 52).collidepoint(pygame.mouse.get_pos())
        
        self.draw_text(screen, "◀", WIDTH//2 - 220, 97, size=22, color=UI_ACCENT if left_arrow_hover else UI_TEXT_DIM, center=True)
        self.draw_text(screen, current_lg_name.upper(), WIDTH//2, 97, size=22, color=WHITE, center=True, bold=True)
        self.draw_text(screen, "▶", WIDTH//2 + 220, 97, size=22, color=UI_ACCENT if right_arrow_hover else UI_TEXT_DIM, center=True)
        
        self.draw_text(screen, "Cambia de Liga usando [Q / E] o haz clic en las flechas", WIDTH//2, 142, size=13, color=UI_TEXT_DIM, center=True)

        # Draw Teams grid inside clipped viewport to prevent overlap with header and instructions
        teams = self.leagues[current_lg_code]
        
        # Clipping area
        viewport_y = 168
        viewport_h = HEIGHT - viewport_y - 75
        screen.set_clip(pygame.Rect(0, viewport_y, WIDTH, viewport_h))
        
        for i, team in enumerate(teams):
            row, col = divmod(i, self.cols)
            x, y = 80 + col * 230, 180 + row * 160 - self.scroll_y
            rect = pygame.Rect(x, y, 200, 140)
            
            is_sel = (self.sel_tm_idx == i)
            is_hov = (self.hovered_idx == i)
            
            # Premium card design
            bg_col = (40, 55, 90) if is_sel else ((30, 40, 65) if is_hov else (20, 26, 42))
            border_col = UI_ACCENT if is_sel else ((100, 150, 255) if is_hov else (45, 55, 78))
            border_w = 3 if is_sel else (2 if is_hov else 1)
            
            # Subtle card glow for selected team
            if is_sel:
                glow_val = int(10 + math.sin(self.time * 6) * 6)
                card_glow = pygame.Surface((220, 160), pygame.SRCALPHA)
                pygame.draw.rect(card_glow, (*UI_ACCENT, glow_val), (10, 10, 200, 140), border_radius=16)
                screen.blit(card_glow, (x - 10, y - 10))
                
            pygame.draw.rect(screen, bg_col, rect, border_radius=14)
            pygame.draw.rect(screen, border_col, rect, border_w, border_radius=14)
            
            # Badge drawing
            draw_badge(screen, team, x + 100, y + 55, size=65)
            
            # Team Name
            text_color = WHITE if (is_sel or is_hov) else UI_TEXT_DIM
            self.draw_text(screen, team["name"].upper(), x + 100, y + 105, size=16, color=text_color, center=True, bold=is_sel)

        # Clear clip rect
        screen.set_clip(None)
        
        # Footer hints
        pygame.draw.line(screen, (35, 45, 70), (50, HEIGHT - 70), (WIDTH - 50, HEIGHT - 70), 1)
        
        self.draw_text(screen, "↑↓←→ Navegar Cuadrícula   ·   Q/E Cambiar Liga   ·   ENTER Confirmar Selección", WIDTH//2, HEIGHT - 55, size=16, color=WHITE, center=True)
        self.draw_text(screen, "[Clic] Seleccionar / Confirmar   ·   [ESC] Volver al Menú Principal", WIDTH//2, HEIGHT - 32, size=14, color=UI_TEXT_DIM, center=True)

    def _confirm_team(self, team):
        from .online_matchmaking import OnlineMatchmakingScene
        team_data = {
            "name": team["name"],
            "short": team["short"],
            "roster": team.get("roster", [])
        }
        self.manager.transition_to(OnlineMatchmakingScene, team_data=team_data)

    def handle_event(self, event):
        if not self.league_list:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.manager.pop_scene()
            return

        current_lg_code = self.league_list[self.sel_lg_idx]
        teams = self.leagues[current_lg_code]
        n_teams = len(teams)

        if event.type == pygame.KEYDOWN:
            # 2D Grid navigation of teams
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.sel_tm_idx = (self.sel_tm_idx - 1) % n_teams
                self._update_scroll_target()
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.sel_tm_idx = (self.sel_tm_idx + 1) % n_teams
                self._update_scroll_target()
            elif event.key in (pygame.K_UP, pygame.K_w):
                new_idx = self.sel_tm_idx - self.cols
                if new_idx >= 0:
                    self.sel_tm_idx = new_idx
                else:
                    # Wrap to bottom row in the same column if possible
                    total_rows = math.ceil(n_teams / self.cols)
                    target_row = total_rows - 1
                    target_idx = target_row * self.cols + (self.sel_tm_idx % self.cols)
                    if target_idx >= n_teams:
                        target_idx = n_teams - 1
                    self.sel_tm_idx = target_idx
                self._update_scroll_target()
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                new_idx = self.sel_tm_idx + self.cols
                if new_idx < n_teams:
                    self.sel_tm_idx = new_idx
                else:
                    # Wrap to top row in the same column
                    self.sel_tm_idx = self.sel_tm_idx % self.cols
                self._update_scroll_target()
                
            # League cycling keys
            elif event.key in (pygame.K_q, pygame.K_PAGEUP):
                self.sel_lg_idx = (self.sel_lg_idx - 1) % len(self.league_list)
                self._reset_selection_and_scroll()
            elif event.key in (pygame.K_e, pygame.K_PAGEDOWN):
                self.sel_lg_idx = (self.sel_lg_idx + 1) % len(self.league_list)
                self._reset_selection_and_scroll()
            
            elif event.key == pygame.K_RETURN:
                self._confirm_team(teams[self.sel_tm_idx])
                
            elif event.key == pygame.K_ESCAPE:
                self.manager.pop_scene()
                
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = pygame.mouse.get_pos()
            
            # Click Left League Selector Arrow
            if pygame.Rect(WIDTH//2 - 250, 85, 60, 52).collidepoint(mx, my):
                self.sel_lg_idx = (self.sel_lg_idx - 1) % len(self.league_list)
                self._reset_selection_and_scroll()
                
            # Click Right League Selector Arrow
            elif pygame.Rect(WIDTH//2 + 190, 85, 60, 52).collidepoint(mx, my):
                self.sel_lg_idx = (self.sel_lg_idx + 1) % len(self.league_list)
                self._reset_selection_and_scroll()
                
            # Click Team card
            else:
                for i in range(n_teams):
                    row, col = divmod(i, self.cols)
                    x, y = 80 + col * 230, 180 + row * 160 - self.scroll_y
                    rect = pygame.Rect(x, y, 200, 140)
                    if rect.collidepoint(mx, my) and 168 <= my <= HEIGHT - 75:
                        if self.sel_tm_idx == i:
                            self._confirm_team(teams[i])
                        else:
                            self.sel_tm_idx = i
                            self._update_scroll_target()
                        break

    def _reset_selection_and_scroll(self):
        self.sel_tm_idx = 0
        self.scroll_y = 0.0
        self.target_scroll_y = 0.0

    def _update_scroll_target(self):
        """Calculates self.target_scroll_y to keep the selected card fully inside the visible viewport."""
        row = self.sel_tm_idx // self.cols
        card_top = row * 160
        card_bottom = card_top + 140
        
        # Viewport constraints relative to the grid start (y=180)
        viewport_h = HEIGHT - 180 - 75 # roughly 465 pixels
        
        if card_top < self.target_scroll_y:
            self.target_scroll_y = float(card_top)
        elif card_bottom > self.target_scroll_y + viewport_h:
            self.target_scroll_y = float(card_bottom - viewport_h)
