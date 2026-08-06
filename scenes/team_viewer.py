import pygame
import math
from settings import *
from data.teams import TEAMS, draw_badge, draw_uniform_preview
from data.career_manager import career_manager


class TeamViewerScene:
    """Escena de visualización de equipos: escudo, uniforme, plantel y stats."""

    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        self.league = self.context.get("league", None)
        self.time = 0

        all_teams = TEAMS[:]
        if hasattr(career_manager, "teams") and career_manager.teams:
            # Combine without duplicates
            for ct in career_manager.teams:
                if not any(t["short"] == ct["short"] for t in all_teams):
                    all_teams.append(ct)

        if self.league:
            self.teams = [t for t in all_teams if t.get("league") == self.league]
        else:
            self.teams = all_teams
        if not self.teams:
            self.teams = all_teams[:]

        self.team_idx = 0
        self.scroll_offset = 0  # For roster scrolling
        self.max_visible_players = 11

        try:
            self.font_title = pygame.font.SysFont("Arial", 36, bold=True)
            self.font_team_name = pygame.font.SysFont("Arial", 28, bold=True)
            self.font_section = pygame.font.SysFont("Arial", 20, bold=True)
            self.font_player = pygame.font.SysFont("Arial", 15)
            self.font_player_bold = pygame.font.SysFont("Arial", 15, bold=True)
            self.font_stat = pygame.font.SysFont("Arial", 13)
            self.font_hint = pygame.font.SysFont("Arial", 14)
            self.font_ovr_big = pygame.font.SysFont("Impact", 52)
            self.font_label = pygame.font.SysFont("Arial", 16, bold=True)
        except:
            self.font_title = pygame.font.Font(None, 36)
            self.font_team_name = pygame.font.Font(None, 28)
            self.font_section = pygame.font.Font(None, 20)
            self.font_player = pygame.font.Font(None, 15)
            self.font_player_bold = pygame.font.Font(None, 15)
            self.font_stat = pygame.font.Font(None, 13)
            self.font_hint = pygame.font.Font(None, 14)
            self.font_ovr_big = pygame.font.Font(None, 52)
            self.font_label = pygame.font.Font(None, 16)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.team_idx = (self.team_idx - 1) % len(self.teams)
                    self.scroll_offset = 0
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.team_idx = (self.team_idx + 1) % len(self.teams)
                    self.scroll_offset = 0
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.scroll_offset = max(0, self.scroll_offset - 1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    roster = self.teams[self.team_idx].get("roster", [])
                    max_scroll = max(0, len(roster) - self.max_visible_players)
                    self.scroll_offset = min(max_scroll, self.scroll_offset + 1)
                elif event.key == pygame.K_e:
                    from scenes.team_editor import TeamEditorScene
                    editor_ctx = dict(self.context)
                    editor_ctx["team_idx"] = self.team_idx
                    self.manager.set_scene(TeamEditorScene, context=editor_ctx)
                elif event.key == pygame.K_ESCAPE:
                    from scenes.league_select import LeagueSelectScene
                    self.manager.set_scene(LeagueSelectScene, context=self.context)

    def update(self, dt):
        self.time += dt

    def draw(self, surface):
        team = self.teams[self.team_idx]
        
        # Get roster from team object or career_manager
        roster = team.get("roster", [])
        if not roster and hasattr(career_manager, "rosters"):
            roster = career_manager.rosters.get(team["short"], [])
            
        stats = team.get("stats", {})

        # Background
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(12 + ratio * 8)
            g = int(14 + ratio * 6)
            b = int(28 + ratio * 14)
            pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

        # ── TOP BAR ──
        title_surf = self.font_title.render("BASE DE DATOS DE EQUIPOS", True, UI_TEXT)
        surface.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 12))
        pygame.draw.line(surface, UI_ACCENT, (WIDTH // 2 - 180, 48), (WIDTH // 2 + 180, 48), 2)

        # Team navigation indicator
        nav_text = f"◀  {self.team_idx + 1} / {len(self.teams)}  ▶"
        nav_surf = self.font_hint.render(nav_text, True, UI_TEXT_DIM)
        surface.blit(nav_surf, (WIDTH // 2 - nav_surf.get_width() // 2, 54))

        # ═══════════════════════════════════════════════
        # LEFT PANEL: Identity (badge, name, uniform, global OVR)
        # ═══════════════════════════════════════════════
        left_x = 40
        left_w = 260
        panel_rect = pygame.Rect(left_x, 80, left_w, HEIGHT - 120)
        pygame.draw.rect(surface, UI_CARD_BG, panel_rect, border_radius=12)
        pulse = (math.sin(self.time * 3) + 1) / 2
        bcol = (int(team["primary"][0] * (0.4 + 0.3 * pulse)),
                int(team["primary"][1] * (0.4 + 0.3 * pulse)),
                int(team["primary"][2] * (0.4 + 0.3 * pulse)))
        pygame.draw.rect(surface, bcol, panel_rect, 2, border_radius=12)

        cx = left_x + left_w // 2

        # Badge
        draw_badge(surface, team, cx, 140, size=70)

        # Team Name
        name_surf = self.font_team_name.render(team["name"], True, WHITE)
        surface.blit(name_surf, (cx - name_surf.get_width() // 2, 190))

        # League tag
        league_names = {"EN": "Premier League", "ES": "La Liga", "IT": "Serie A",
                        "DE": "Bundesliga", "FR": "Ligue 1", "PT": "Primeira Liga",
                        "BR": "Brasileirão", "AR": "Liga Profesional", "CO": "Liga BetPlay",
                        "US": "MLS", "JP": "J-League"}
        lg_name = league_names.get(team.get("league", ""), "Desconocida")
        lg_surf = self.font_stat.render(lg_name, True, UI_TEXT_DIM)
        surface.blit(lg_surf, (cx - lg_surf.get_width() // 2, 220))

        # Uniform
        draw_uniform_preview(surface, team, cx, 248, scale=1.0)

        # Global OVR (big number)
        if roster:
            starters = roster[:11]
            avg_ovr = sum(p.get("ovr", 75) for p in starters) / max(1, len(starters))
        else:
            avg_ovr = sum(stats.values()) / max(1, len(stats))

        ovr_label = self.font_label.render("MEDIA GENERAL", True, UI_TEXT_DIM)
        surface.blit(ovr_label, (cx - ovr_label.get_width() // 2, 375))

        ovr_color = (0, 200, 100) if avg_ovr >= 82 else (200, 200, 0) if avg_ovr >= 75 else (200, 80, 40)
        ovr_surf = self.font_ovr_big.render(str(int(avg_ovr)), True, ovr_color)
        surface.blit(ovr_surf, (cx - ovr_surf.get_width() // 2, 395))

        # Stars
        stars = self._calc_stars(avg_ovr)
        star_start_x = cx - 55
        for s_idx in range(5):
            sx = star_start_x + s_idx * 24
            fill = 0.0
            if stars >= s_idx + 1:
                fill = 1.0
            elif stars == s_idx + 0.5:
                fill = 0.5
            self._draw_star(surface, sx, 455, 12, fill)

        # Team Stats Bars
        stat_names = {"speed": "VEL", "shot": "TIR", "defense": "DEF", "passing": "PAS"}
        sy = 485
        for key, label in stat_names.items():
            val = stats.get(key, 70)
            sl = self.font_stat.render(label, True, UI_TEXT_DIM)
            surface.blit(sl, (left_x + 20, sy))
            bar_x = left_x + 60
            bar_w = 130
            bar_h = 8
            pygame.draw.rect(surface, (40, 40, 50), (bar_x, sy + 4, bar_w, bar_h), border_radius=4)
            fill_w = int((val / 99) * bar_w)
            bc = (0, 200, 100) if val >= 82 else (200, 200, 0) if val >= 70 else (200, 80, 40)
            pygame.draw.rect(surface, bc, (bar_x, sy + 4, fill_w, bar_h), border_radius=4)
            vs = self.font_stat.render(str(val), True, bc)
            surface.blit(vs, (bar_x + bar_w + 8, sy))
            sy += 26

        # ═══════════════════════════════════════════════
        # RIGHT PANEL: Roster Table
        # ═══════════════════════════════════════════════
        right_x = 330
        right_w = WIDTH - right_x - 30
        table_rect = pygame.Rect(right_x, 80, right_w, HEIGHT - 120)
        pygame.draw.rect(surface, UI_CARD_BG, table_rect, border_radius=12)
        pygame.draw.rect(surface, (50, 55, 70), table_rect, 1, border_radius=12)

        # Header
        header_y = 92
        roster_label = self.font_section.render("PLANTEL COMPLETO", True, UI_ACCENT)
        surface.blit(roster_label, (right_x + 15, header_y))

        count_label = self.font_stat.render(f"{len(roster)} jugadores", True, UI_TEXT_DIM)
        surface.blit(count_label, (right_x + right_w - count_label.get_width() - 15, header_y + 4))

        # Column headers
        col_y = header_y + 30
        cols = [
            (right_x + 10, "#", 20),
            (right_x + 35, "POS", 35),
            (right_x + 75, "NOMBRE", 130),
            (right_x + 235, "EDAD", 40),
            (right_x + 285, "POT", 35),
            (right_x + 325, "OVR", 35),
            (right_x + 370, "VEL", 35),
            (right_x + 410, "TIR", 35),
            (right_x + 450, "PAS", 35),
            (right_x + 490, "DEF", 35),
            (right_x + 530, "POR", 35),
        ]

        # Separator before headers
        pygame.draw.line(surface, (50, 55, 70), (right_x + 10, col_y - 2), (right_x + right_w - 10, col_y - 2), 1)

        for cx_col, label, w in cols:
            hs = self.font_stat.render(label, True, UI_ACCENT)
            surface.blit(hs, (cx_col, col_y))

        pygame.draw.line(surface, (50, 55, 70), (right_x + 10, col_y + 18), (right_x + right_w - 10, col_y + 18), 1)

        # Player rows
        row_h = 28
        start_y = col_y + 24
        visible_roster = roster[self.scroll_offset:self.scroll_offset + self.max_visible_players]

        for i, p in enumerate(visible_roster):
            real_idx = i + self.scroll_offset
            py = start_y + i * row_h
            is_starter = real_idx < 11

            # Alternating row bg
            if i % 2 == 0:
                row_rect = pygame.Rect(right_x + 5, py - 2, right_w - 10, row_h)
                pygame.draw.rect(surface, (30, 33, 45), row_rect, border_radius=4)

            # Starter/Sub divider
            if real_idx == 11 and self.scroll_offset <= 11:
                div_y = start_y + (11 - self.scroll_offset) * row_h - 6
                if div_y > start_y and div_y < start_y + self.max_visible_players * row_h:
                    pygame.draw.line(surface, UI_ACCENT, (right_x + 10, div_y), (right_x + right_w - 10, div_y), 1)
                    sub_label = self.font_stat.render("── SUPLENTES ──", True, UI_ACCENT)
                    # We'll skip a visual label and rely on the line

            # Number
            num_font = self.font_player_bold if is_starter else self.font_player
            num_color = WHITE if is_starter else UI_TEXT_DIM
            ns = num_font.render(str(p.get("num", "")), True, num_color)
            surface.blit(ns, (right_x + 10, py))

            # Position badge
            pos = p.get("pos", "?")
            pos_colors = {"GK": (220, 200, 50), "CB": (50, 150, 250), "LB": (50, 150, 250),
                          "RB": (50, 150, 250), "CM": (50, 200, 100), "CDM": (50, 200, 100),
                          "CAM": (50, 200, 100), "LW": (250, 80, 80), "RW": (250, 80, 80),
                          "ST": (250, 80, 80)}
            pc = pos_colors.get(pos, (150, 150, 150))
            pos_rect = pygame.Rect(right_x + 35, py, 32, 18)
            pygame.draw.rect(surface, pc, pos_rect, border_radius=4)
            ps = self.font_stat.render(pos, True, (0, 0, 0))
            surface.blit(ps, (pos_rect.centerx - ps.get_width() // 2, py + 1))

            # Name
            name_color = WHITE if is_starter else (180, 180, 190)
            
            # Truncate real long names
            raw_name = p["name"]
            if len(raw_name) > 17: raw_name = raw_name[:15] + ".."
            
            nms = self.font_player_bold.render(raw_name, True, name_color) if is_starter else self.font_player.render(raw_name, True, name_color)
            surface.blit(nms, (right_x + 75, py))
            
            # Edad
            try:
                age = int(p.get("age", 25))
            except (ValueError, TypeError):
                age = 25
            ac = (200, 200, 200) if age <= 28 else (150, 150, 150)
            as_ = self.font_stat.render(str(age), True, ac)
            surface.blit(as_, (right_x + 235, py + 1))
            
            # POT
            try:
                pot = int(p.get("pot", p.get("ovr", 75)))
            except (ValueError, TypeError):
                pot = 75
            pot_c = (0, 220, 255) if pot >= 88 else (0, 200, 100) if pot >= 82 else (200, 200, 200) if pot >= 75 else (150, 150, 150)
            pots_ = self.font_player_bold.render(str(pot), True, pot_c)
            surface.blit(pots_, (right_x + 285, py))

            # OVR
            try:
                ovr = int(p.get("ovr", 75))
            except (ValueError, TypeError):
                ovr = 75
            ovr_c = (0, 220, 100) if ovr >= 85 else (255, 215, 0) if ovr >= 80 else (200, 200, 200) if ovr >= 75 else (180, 100, 60)
            ovr_s = self.font_player_bold.render(str(ovr), True, ovr_c)
            surface.blit(ovr_s, (right_x + 325, py))

            # Individual stats
            stat_keys = ["speed", "shot", "passing", "defense", "gk"]
            stat_positions = [370, 410, 450, 490, 530]
            for sk, sx in zip(stat_keys, stat_positions):
                try:
                    val = int(p["s"].get(sk, 0))
                except (ValueError, TypeError):
                    val = 0
                vc = (0, 200, 100) if val >= 85 else (200, 200, 0) if val >= 70 else (180, 180, 180) if val >= 50 else (120, 60, 60)
                vs = self.font_stat.render(str(val), True, vc)
                surface.blit(vs, (right_x + sx, py + 1))

        # Scroll indicator
        if len(roster) > self.max_visible_players:
            total = len(roster)
            bar_total_h = self.max_visible_players * row_h
            bar_x = right_x + right_w - 12
            bar_y = start_y
            pygame.draw.rect(surface, (40, 40, 50), (bar_x, bar_y, 6, bar_total_h), border_radius=3)
            handle_h = max(20, int(bar_total_h * (self.max_visible_players / total)))
            handle_y = bar_y + int((bar_total_h - handle_h) * (self.scroll_offset / max(1, total - self.max_visible_players)))
            pygame.draw.rect(surface, UI_ACCENT, (bar_x, handle_y, 6, handle_h), border_radius=3)

        # ── BOTTOM HINTS ──
        hint = "←→/AD Cambiar Equipo   ·   ↑ ↓ Scroll Plantel   ·   E Editar   ·   ESC Volver"
        hint_surf = self.font_hint.render(hint, True, UI_TEXT_DIM)
        surface.blit(hint_surf, (WIDTH // 2 - hint_surf.get_width() // 2, HEIGHT - 25))

    def _calc_stars(self, avg):
        if avg >= 88: return 5.0
        elif avg >= 84: return 4.5
        elif avg >= 80: return 4.0
        elif avg >= 76: return 3.5
        elif avg >= 72: return 3.0
        elif avg >= 68: return 2.5
        elif avg >= 64: return 2.0
        elif avg >= 60: return 1.5
        return 1.0

    def _draw_star(self, surface, x, y, size, fill):
        points = []
        outer_r = size
        inner_r = size * 0.45
        for i in range(10):
            angle = math.pi / 2 - i * math.pi / 5
            r = outer_r if i % 2 == 0 else inner_r
            points.append((x + r * math.cos(angle), y - r * math.sin(angle)))

        color_empty = (60, 60, 70)
        color_filled = (255, 215, 0)

        if fill == 1.0:
            pygame.draw.polygon(surface, color_filled, points)
        elif fill == 0.0:
            pygame.draw.polygon(surface, color_empty, points)
        else:
            pygame.draw.polygon(surface, color_empty, points)
            rect = pygame.Rect(x - outer_r, y - outer_r, outer_r, outer_r * 2)
            orig_clip = surface.get_clip()
            surface.set_clip(rect)
            pygame.draw.polygon(surface, color_filled, points)
            surface.set_clip(orig_clip)
