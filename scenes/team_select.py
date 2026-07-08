import pygame
import math
import random
from settings import *
from scene_manager import BaseScene
from data.teams import TEAMS, draw_badge, draw_uniform_preview


class TeamSelectScene(BaseScene):
    def __init__(self, manager, context=None):
        super().__init__(manager)
        self.context = context or {}
        self.mode = self.context.get("mode", "friendly")
        self.league = self.context.get("league", None)
        
        self.time = 0
        if self.league:
            self.teams = [t for t in TEAMS if t.get("league") == self.league]
        else:
            self.teams = TEAMS
            
        if not self.teams:
            self.teams = TEAMS # Fallback safe
            
        self.all_leagues = list(sorted(set([t.get("league") for t in TEAMS if t.get("league")])))
        self.player_team_obj = None
        self.rival_team_obj = None
        
        self.player_selection = 0   # Índice del equipo del jugador
        self.rival_selection = 1    # Índice del equipo del rival
        self.active_side = "left"   # Qué lado está seleccionando ("left" = jugador, "right" = rival)
        self.confirmed_player = False
        self.confirmed_rival = False

        # Grid layout dinámico
        self.cols = 5
        self.rows = math.ceil(len(self.teams) / self.cols)
        if len(self.teams) > 16:
            self.cell_w = 80
            self.cell_h = 80
            self.cols = 6
            self.rows = math.ceil(len(self.teams) / self.cols)
        else:
            self.cell_w = 105
            self.cell_h = 100

        try:
            self.font_title = pygame.font.SysFont("Arial", 36, bold=True)
            self.font_team_name = pygame.font.SysFont("Arial", 24, bold=True)
            self.font_stat_label = pygame.font.SysFont("Arial", 14)
            self.font_stat_val = pygame.font.SysFont("Arial", 16, bold=True)
            self.font_hint = pygame.font.SysFont("Arial", 16)
            self.font_label = pygame.font.SysFont("Arial", 20, bold=True)
            self.font_vs = pygame.font.SysFont("Impact", 48)
            self.font_confirm = pygame.font.SysFont("Arial", 18, bold=True)
        except:
            self.font_title = pygame.font.Font(None, 36)
            self.font_team_name = pygame.font.Font(None, 24)
            self.font_stat_label = pygame.font.Font(None, 14)
            self.font_stat_val = pygame.font.Font(None, 16)
            self.font_hint = pygame.font.Font(None, 16)
            self.font_label = pygame.font.Font(None, 20)
            self.font_vs = pygame.font.Font(None, 48)
            self.font_confirm = pygame.font.Font(None, 18)
            
        self.scroll_y = 0.0
        self.target_scroll_y = 0.0

    def _current_selection(self):
        if self.active_side == "left":
            return self.player_selection
        return self.rival_selection

    def _set_current_selection(self, val):
        val = val % len(self.teams)
        if self.active_side == "left":
            self.player_selection = val
        else:
            self.rival_selection = val
        self._update_scroll_target()

    def _update_scroll_target(self):
        if not self.teams: return
        sel = self._current_selection()
        row = sel // self.cols
        cell_y_top = row * (self.cell_h + 8)
        cell_y_bottom = cell_y_top + self.cell_h
        
        # Viewport constraints relative to grid start y (100)
        viewport_h = HEIGHT - 100 - 100
        
        if cell_y_top < self.target_scroll_y:
            self.target_scroll_y = float(cell_y_top)
        elif cell_y_bottom > self.target_scroll_y + viewport_h:
            self.target_scroll_y = float(cell_y_bottom - viewport_h)
            
    def _reset_scroll(self):
        self.scroll_y = 0.0
        self.target_scroll_y = 0.0

    def _go_to_next_phase(self):
        # Transición dependiente del modo
        p_team = self.player_team_obj if self.player_team_obj else self.teams[self.player_selection]
        r_team = self.rival_team_obj if self.rival_team_obj else self.teams[self.rival_selection]
        
        if self.mode == "tournament":
            # Si estamos en modo torneo, vamos al Tournament Hub en lugar del Tactics directo
            from scenes.tournament_hub import TournamentHubScene
            self.context["player_team"] = p_team
            # Generar resto del torneo
            self.manager.set_scene(TournamentHubScene, context=self.context)
        else:
            # Amistoso
            from scenes.tactics import TacticsScene
            self.manager.shared_data["player_team"] = p_team
            self.manager.shared_data["rival_team"] = r_team
            self.manager.set_scene(TacticsScene)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.active_side == "right":
                        # Deshacer confirmación y selección del rival
                        if self.confirmed_rival:
                            self.confirmed_rival = False
                        else:
                            # Volver a jugador
                            self.active_side = "left"
                            self.confirmed_player = False
                    else:
                        from scenes.league_select import LeagueSelectScene
                        self.manager.set_scene(LeagueSelectScene, context=self.context)
                        return

                sel = self._current_selection()
                # Al dar enter estando ambos listos, pasar a tácticas o torneo
                if self.confirmed_player and self.confirmed_rival:
                    self._go_to_next_phase()
                col = sel % self.cols
                row = sel // self.cols

                if event.key in (pygame.K_LEFT, pygame.K_a):
                    col = (col - 1) % self.cols
                    self._set_current_selection(row * self.cols + col)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    col = (col + 1) % self.cols
                    self._set_current_selection(row * self.cols + col)
                elif event.key in (pygame.K_UP, pygame.K_w):
                    row = (row - 1) % self.rows
                    self._set_current_selection(row * self.cols + col)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    row = (row + 1) % self.rows
                    self._set_current_selection(row * self.cols + col)
                elif event.key == pygame.K_r:
                    # Random rival
                    if self.active_side == "right":
                        self.rival_selection = random.randint(0, len(self.teams) - 1)
                elif event.key == pygame.K_l:
                    # Cambiar liga dinámicamente
                    if self.all_leagues:
                        if self.league in self.all_leagues:
                            idx = self.all_leagues.index(self.league)
                            self.league = self.all_leagues[(idx + 1) % len(self.all_leagues)]
                        else:
                            self.league = self.all_leagues[0]
                        self.teams = [t for t in TEAMS if t.get("league") == self.league]
                        if not self.teams: self.teams = TEAMS
                        
                        self.cols = 5
                        self.rows = math.ceil(len(self.teams) / self.cols)
                        if len(self.teams) > 16:
                            self.cell_w = 80
                            self.cell_h = 80
                            self.cols = 6
                            self.rows = math.ceil(len(self.teams) / self.cols)
                        else:
                            self.cell_w = 105
                            self.cell_h = 100
                            
                        self._set_current_selection(0)
                        self._reset_scroll()
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self._confirm()
                elif event.key == pygame.K_TAB:
                    # Cambiar de lado
                    if not self.confirmed_player:
                        pass  # Primero confirma tu equipo
                    elif not self.confirmed_rival:
                        self.active_side = "right" if self.active_side == "left" else "left"

    def _confirm(self):
        if self.active_side == "left" and not self.confirmed_player:
            self.player_team_obj = self.teams[self.player_selection]
            self.confirmed_player = True
            
            if self.mode == "tournament":
                self.rival_team_obj = self.teams[self.rival_selection]
                self.confirmed_rival = True
                self._go_to_next_phase()
            else:
                self.active_side = "right"
        elif self.active_side == "right" and not self.confirmed_rival:
            # Verificar que no sea el mismo equipo
            selected = self.teams[self.rival_selection]
            if selected == self.player_team_obj:
                return  # No permitir mismo equipo
            self.rival_team_obj = selected
            self.confirmed_rival = True
            self._go_to_next_phase()

    def _start_match(self):
        # deprecado
        pass
        self.manager.shared_data["player_team"] = self.teams[self.player_selection]
        self.manager.shared_data["rival_team"] = self.teams[self.rival_selection]
        from scenes.tactics import TacticsScene
        self.manager.transition_to(TacticsScene)

    def update(self, dt):
        self.time += dt
        self.scroll_y += (self.target_scroll_y - self.scroll_y) * 12.0 * dt

    def draw(self, surface):
        # Fondo
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(15 + ratio * 8)
            g = int(15 + ratio * 5)
            b = int(30 + ratio * 15)
            pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

        # Título
        title_surf = self.font_title.render("SELECCIÓN DE EQUIPOS", True, UI_TEXT)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, 40))
        surface.blit(title_surf, title_rect)
        pygame.draw.line(surface, UI_ACCENT, (WIDTH // 2 - 180, 62), (WIDTH // 2 + 180, 62), 2)

        # Layout: [Preview Jugador] [Grid] [Preview Rival]
        preview_w = 220
        
        # Posiciones
        left_preview_x = 40
        right_preview_x = WIDTH - preview_w - 40

        # ── PREVIEW JUGADOR (izquierda) ──
        team_p = self.player_team_obj if self.confirmed_player else self.teams[self.player_selection]
        self._draw_team_preview(surface, team_p,
                                left_preview_x, 85, preview_w, "TU EQUIPO",
                                self.active_side == "left", self.confirmed_player,
                                UI_ACCENT)

        # ── VS ──
        vs_x = WIDTH // 2
        vs_pulse = (math.sin(self.time * 3) + 1) / 2
        vs_color = (
            int(200 + vs_pulse * 55),
            int(50 + vs_pulse * 50),
            int(50 + vs_pulse * 30),
        )
        vs_surf = self.font_vs.render("VS", True, vs_color)
        vs_rect = vs_surf.get_rect(center=(vs_x, HEIGHT // 2 + 20))
        # Solo si ambos confirmados
        if self.confirmed_player:
            surface.blit(vs_surf, vs_rect)

        # ── PREVIEW RIVAL (derecha) ──
        team_r = self.rival_team_obj if self.confirmed_rival else self.teams[self.rival_selection]
        self._draw_team_preview(surface, team_r,
                                right_preview_x, 85, preview_w, "RIVAL",
                                self.active_side == "right", self.confirmed_rival,
                                UI_ACCENT_ALT)

        # Central grid drawing        
        grid_w = self.cols * (self.cell_w + 8)
        grid_x = WIDTH // 2 - grid_w // 2
        grid_start_y = 100
        active_selection = self._current_selection()

        viewport_y = 95
        viewport_h = HEIGHT - viewport_y - 80
        surface.set_clip(pygame.Rect(grid_x - 10, viewport_y, grid_w + 20, viewport_h))

        for i, team in enumerate(self.teams):
            col = i % self.cols
            row = i // self.cols
            cx = grid_x + col * (self.cell_w + 8) + self.cell_w // 2
            cy = grid_start_y + row * (self.cell_h + 8) + self.cell_h // 2 - self.scroll_y

            is_selected = i == active_selection
            is_player = (team == self.player_team_obj) if self.confirmed_player else (i == self.player_selection and self.active_side == "left")
            is_rival = (team == self.rival_team_obj) if self.confirmed_rival else (i == self.rival_selection and self.active_side == "right")

            # Fondo de celda
            cell_rect = pygame.Rect(cx - self.cell_w // 2, cy - self.cell_h // 2,
                                    self.cell_w, self.cell_h)
            if is_selected:
                pygame.draw.rect(surface, UI_CARD_HOVER, cell_rect, border_radius=8)
                border_col = UI_ACCENT if self.active_side == "left" else UI_ACCENT_ALT
                pygame.draw.rect(surface, border_col, cell_rect, 2, border_radius=8)
            else:
                pygame.draw.rect(surface, UI_CARD_BG, cell_rect, border_radius=8)
                pygame.draw.rect(surface, (50, 50, 60), cell_rect, 1, border_radius=8)

            # Marca si está seleccionado como jugador o rival
            if is_player:
                pygame.draw.rect(surface, (*UI_ACCENT, 60), cell_rect, 0, border_radius=8)
                mark = self.font_stat_label.render("P1", True, UI_ACCENT)
                surface.blit(mark, (cell_rect.right - 22, cell_rect.top + 4))
            if is_rival:
                pygame.draw.rect(surface, (*UI_ACCENT_ALT, 60), cell_rect, 0, border_radius=8)
                mark = self.font_stat_label.render("CPU", True, UI_ACCENT_ALT)
                surface.blit(mark, (cell_rect.right - 30, cell_rect.top + 4))

            # Escudo
            draw_badge(surface, team, cx, cy - 12, size=44)

            # Nombre corto
            short_surf = self.font_stat_label.render(team["short"], True, UI_TEXT_DIM)
            short_rect = short_surf.get_rect(center=(cx, cy + 36))
            surface.blit(short_surf, short_rect)

        surface.set_clip(None)

        # ── HINTS ──
        hint_y = HEIGHT - 35
        if not self.confirmed_player:
            hint_text = "↑↓←→ Navegar   ·   L Cambiar Liga   ·   ENTER Confirmar tu equipo   ·   ESC Volver"
        elif not self.confirmed_rival:
            hint_text = "↑↓←→ Navegar   ·   L Cambiar Liga   ·   R Aleatorio   ·   ENTER Confirmar   ·   ESC Reiniciar"
        else:
            hint_text = "¡Preparando partido..."

        hint_surf = self.font_hint.render(hint_text, True, UI_TEXT_DIM)
        hint_rect = hint_surf.get_rect(center=(WIDTH // 2, hint_y))
        surface.blit(hint_surf, hint_rect)

    def _draw_team_preview(self, surface, team, x, y, w, label, active, confirmed, accent_color):
        """Dibuja el panel de vista previa de un equipo."""
        h = 530
        panel_rect = pygame.Rect(x, y, w, h)

        # Fondo
        bg = UI_CARD_HOVER if active else UI_CARD_BG
        pygame.draw.rect(surface, bg, panel_rect, border_radius=12)

        # Borde
        if active and not confirmed:
            pulse = (math.sin(self.time * 4) + 1) / 2
            bc = (
                int(accent_color[0] * (0.6 + 0.4 * pulse)),
                int(accent_color[1] * (0.6 + 0.4 * pulse)),
                int(accent_color[2] * (0.6 + 0.4 * pulse)),
            )
            pygame.draw.rect(surface, bc, panel_rect, 2, border_radius=12)
        elif confirmed:
            pygame.draw.rect(surface, accent_color, panel_rect, 2, border_radius=12)
            # Check mark
            check = self.font_confirm.render("[OK] CONFIRMADO", True, accent_color)
            check_rect = check.get_rect(center=(x + w // 2, y + h - 20))
            surface.blit(check, check_rect)
        else:
            pygame.draw.rect(surface, (50, 50, 60), panel_rect, 1, border_radius=12)

        # Label
        label_surf = self.font_label.render(label, True, accent_color)
        label_rect = label_surf.get_rect(center=(x + w // 2, y + 22))
        surface.blit(label_surf, label_rect)

        # Escudo grande
        draw_badge(surface, team, x + w // 2, y + 85, size=80)

        # Nombre
        name_surf = self.font_team_name.render(team["name"], True, UI_TEXT)
        name_rect = name_surf.get_rect(center=(x + w // 2, y + 150))
        surface.blit(name_surf, name_rect)

        # Uniforme preview
        draw_uniform_preview(surface, team, x + w // 2, y + 175, scale=0.9)

        # Calcular OVR promedio del equipo basado en jugadores
        stats = team["stats"]
        players = team.get("roster", [])
        if players:
            starters = players[:11]
            avg_val = sum(p.get("ovr", 75) for p in starters) / max(1, len(starters))
        else:
            avg_val = sum(stats.values()) / 4.0
        stars = 1.0
        if avg_val >= 88: stars = 5.0
        elif avg_val >= 84: stars = 4.5
        elif avg_val >= 80: stars = 4.0
        elif avg_val >= 76: stars = 3.5
        elif avg_val >= 72: stars = 3.0
        elif avg_val >= 68: stars = 2.5
        elif avg_val >= 64: stars = 2.0
        elif avg_val >= 60: stars = 1.5

        # Dibujar 5 estrellas globales centradas
        star_x = x + w // 2 - 50
        star_y = y + 270
        star_size = 14
        spacing = 25
        for s_idx in range(5):
            cx = star_x + s_idx * spacing
            fill_amt = 0.0
            if stars >= s_idx + 1: fill_amt = 1.0
            elif stars == s_idx + 0.5: fill_amt = 0.5
            self._draw_star_shape(surface, cx, star_y, star_size, fill_amt)

        # Stats en barras
        stat_names = {"speed": "VEL", "shot": "TIR", "defense": "DEF", "passing": "PAS"}
        stat_y = y + 330
        for i, (key, label_str) in enumerate(stat_names.items()):
            sy = stat_y + i * 35
            val = stats[key]

            # Label
            sl = self.font_stat_label.render(label_str, True, UI_TEXT_DIM)
            surface.blit(sl, (x + 15, sy))

            # Dibujar barra
            bar_w = 120
            bar_h = 8
            bx = x + 55
            by = sy + 6
            pygame.draw.rect(surface, (40, 40, 50), (bx, by, bar_w, bar_h), border_radius=4)
            fill_w = int((val / 99) * bar_w)
            pygame.draw.rect(surface, self._stat_color(val), (bx, by, fill_w, bar_h), border_radius=4)

            # Valor
            try: font_v = pygame.font.SysFont("Arial", 14, bold=True)
            except: font_v = pygame.font.Font(None, 16)
            sv = font_v.render(str(val), True, self._stat_color(val))
            surface.blit(sv, (x + w - 35, sy))

    def _draw_star_shape(self, surface, x, y, size, fill):
        # Polígono de estrella de 5 puntas
        points = []
        outer_r = size
        inner_r = size * 0.45
        for i in range(10):
            # Rotar para que la punta superior apunte arriba
            angle = math.pi/2 - i * math.pi/5
            r = outer_r if i % 2 == 0 else inner_r
            points.append((x + r * math.cos(angle), y - r * math.sin(angle)))
            
        color_empty = (60, 60, 70)
        color_filled = (255, 215, 0) # Gold
        
        if fill == 1.0:
            pygame.draw.polygon(surface, color_filled, points)
        elif fill == 0.0:
            pygame.draw.polygon(surface, color_empty, points)
        else: # Media estrella
            pygame.draw.polygon(surface, color_empty, points)
            rect = pygame.Rect(x - outer_r, y - outer_r, outer_r, outer_r * 2)
            orig_clip = surface.get_clip()
            surface.set_clip(rect)
            pygame.draw.polygon(surface, color_filled, points)
            surface.set_clip(orig_clip)

    def _stat_color(self, val):
        """Color de la barra según el valor."""
        if val >= 85:
            return (0, 200, 100)
        elif val >= 70:
            return (200, 200, 0)
        else:
            return (200, 80, 40)
