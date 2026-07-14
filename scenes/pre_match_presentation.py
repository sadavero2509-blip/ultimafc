import pygame
import math
import random
from settings import *
from scene_manager import BaseScene


class PreMatchPresentationScene(BaseScene):
    """Presentación televisiva previa al partido con alineaciones y jugadores destacados."""

    STAGE_INTRO = 0
    STAGE_HOME = 1
    STAGE_AWAY = 2
    STAGE_STARS = 3
    NUM_STAGES = 4

    def __init__(self, manager):
        super().__init__(manager)

        # ── Team data ──
        self.left_team = manager.shared_data.get("player_team", {})
        self.right_team = manager.shared_data.get("rival_team", {})
        self.formation_name = manager.shared_data.get("formation", "4-3-3")
        self.game_mode = manager.shared_data.get("game_mode", "friendly")

        self.left_roster = self.left_team.get("roster", [])
        self.right_roster = self.right_team.get("roster", [])
        self.left_starters = self.left_roster[:11]
        self.right_starters = self.right_roster[:11]

        # ── Competition name & color ──
        self.comp_name = self._get_comp_name()
        self.comp_color = self._get_comp_color()

        # ── Key player data ──
        self.left_key = self._find_key_player(self.left_team, self.left_starters)
        self.right_key = self._find_key_player(self.right_team, self.right_starters)

        # ── Stage management ──
        self.stage = self.STAGE_INTRO
        self.stage_time = 0.0
        self.stage_durations = [4.5, 5.0, 5.0, 4.5]
        self.total_time = 0.0
        self.finished = False

        # ── Visual FX ──
        self.particles = [self._make_particle() for _ in range(60)]

        # ── Slide animation ──
        self.slide_progress = 0.0

        # ── Audio: stadium ambience ──
        from systems.audio_manager import audio_manager
        audio_manager.play_stadium_ambience()

        # ── Fonts ──
        try:
            self.font_comp = pygame.font.SysFont("Impact", 26)
            self.font_team = pygame.font.SysFont("Impact", 34)
            self.font_vs = pygame.font.SysFont("Impact", 72)
            self.font_player = pygame.font.SysFont("Arial", 18, bold=True)
            self.font_pos = pygame.font.SysFont("Arial", 13, bold=True)
            self.font_num = pygame.font.SysFont("Impact", 14)
            self.font_ovr_big = pygame.font.SysFont("Impact", 52)
            self.font_label = pygame.font.SysFont("Arial", 15)
            self.font_small = pygame.font.SysFont("Arial", 12)
            self.font_hint = pygame.font.SysFont("Arial", 13)
            self.font_star_name = pygame.font.SysFont("Impact", 30)
            self.font_star_stat = pygame.font.SysFont("Impact", 22)
            self.font_formation = pygame.font.SysFont("Arial", 16, bold=True)
            self.font_date = pygame.font.SysFont("Arial", 14)
        except Exception:
            self.font_comp = pygame.font.Font(None, 28)
            self.font_team = pygame.font.Font(None, 36)
            self.font_vs = pygame.font.Font(None, 72)
            self.font_player = pygame.font.Font(None, 20)
            self.font_pos = pygame.font.Font(None, 15)
            self.font_num = pygame.font.Font(None, 16)
            self.font_ovr_big = pygame.font.Font(None, 52)
            self.font_label = pygame.font.Font(None, 17)
            self.font_small = pygame.font.Font(None, 14)
            self.font_hint = pygame.font.Font(None, 15)
            self.font_star_name = pygame.font.Font(None, 32)
            self.font_star_stat = pygame.font.Font(None, 24)
            self.font_formation = pygame.font.Font(None, 18)
            self.font_date = pygame.font.Font(None, 16)

    # ════════════════════════ Data Helpers ════════════════════════

    def _get_comp_name(self):
        if self.game_mode == "career":
            try:
                state = self.manager.shared_data.get("career_match_state", {})
                evt = state.get("event", {})
                if evt:
                    return evt.get("type", "PARTIDO DE LIGA")
            except Exception:
                pass
            return "PARTIDO DE LIGA"
        return "PARTIDO AMISTOSO"

    def _get_comp_color(self):
        name = self.comp_name.upper()
        if "CHAMPIONS" in name:
            return (255, 215, 0)
        if "EUROPA" in name:
            return (255, 140, 0)
        if "CONFERENCE" in name:
            return (50, 205, 50)
        if "LIBERTADORES" in name:
            return (173, 255, 47)
        if "SUDAMERICANA" in name:
            return (0, 191, 255)
        if "COPA" in name:
            return (200, 150, 255)
        return (0, 200, 150)

    def _find_key_player(self, team, starters):
        """Encuentra al jugador clave: máximo goleador en carrera o mayor OVR."""
        result = {"player": None, "goals": 0, "is_scorer": False}

        if self.game_mode == "career":
            try:
                from data.career_manager import career_manager
                if career_manager.active:
                    roster_names = {p["name"] for p in starters}
                    best_name, best_goals = None, 0
                    for _stat_key, scorers_dict in career_manager.scorers.items():
                        for pname, goals in scorers_dict.items():
                            if pname in roster_names and goals > best_goals:
                                best_goals = goals
                                best_name = pname
                    if best_name and best_goals > 0:
                        player = next((p for p in starters if p["name"] == best_name), None)
                        if player:
                            return {"player": player, "goals": best_goals, "is_scorer": True}
            except Exception:
                pass

        # Fallback: mayor OVR
        if starters:
            best = max(starters, key=lambda p: p.get("ovr", 0))
            result = {"player": best, "goals": 0, "is_scorer": False}
        return result

    def _make_particle(self):
        return {
            "x": random.randint(0, WIDTH),
            "y": random.randint(0, HEIGHT),
            "r": random.uniform(1, 3),
            "speed": random.uniform(8, 25),
            "alpha": random.randint(40, 120),
            "drift": random.uniform(-15, 15),
        }

    def _get_pos_color(self, pos):
        if pos == "GK":
            return (220, 200, 50)
        if pos in ("CB", "LB", "RB"):
            return (60, 150, 255)
        if pos in ("CM", "CDM", "CAM"):
            return (60, 210, 120)
        return (255, 80, 80)

    def _ease_out(self, t):
        t = min(1.0, max(0.0, t))
        return 1 - (1 - t) ** 3

    # ════════════════════════ Events ════════════════════════

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._start_match()
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._advance_stage()

    def _advance_stage(self):
        from systems.audio_manager import audio_manager
        audio_manager.play_ui("transition")
        if self.stage < self.NUM_STAGES - 1:
            self.stage += 1
            self.stage_time = 0.0
            self.slide_progress = 0.0
        else:
            self._start_match()

    def _start_match(self):
        if self.finished:
            return
        self.finished = True
        from systems.audio_manager import audio_manager
        audio_manager.stop_stadium_ambience()
        from scenes.match import MatchScene
        self.manager.transition_to(MatchScene)

    # ════════════════════════ Update ════════════════════════

    def update(self, dt):
        self.total_time += dt
        self.stage_time += dt
        self.slide_progress = min(1.0, self.stage_time / 0.6)

        # Auto-advance
        if self.stage_time >= self.stage_durations[self.stage]:
            self._advance_stage()

        # Particles
        for p in self.particles:
            p["y"] -= p["speed"] * dt
            p["x"] += p["drift"] * dt
            if p["y"] < -10:
                p["y"] = HEIGHT + 10
                p["x"] = random.randint(0, WIDTH)

    # ════════════════════════ Draw ════════════════════════

    def draw(self, surface):
        self._draw_background(surface)
        self._draw_particles(surface)

        if self.stage == self.STAGE_INTRO:
            self._draw_intro(surface)
        elif self.stage == self.STAGE_HOME:
            self._draw_lineup(surface, self.left_team, self.left_starters, is_home=True)
        elif self.stage == self.STAGE_AWAY:
            self._draw_lineup(surface, self.right_team, self.right_starters, is_home=False)
        elif self.stage == self.STAGE_STARS:
            self._draw_key_players(surface)

        self._draw_hint_bar(surface)
        self._draw_stage_dots(surface)

    # ──────────────── Background ────────────────

    def _draw_background(self, surface):
        surface.fill((8, 10, 18))

        # Top colored glow
        glow = pygame.Surface((WIDTH, 200), pygame.SRCALPHA)
        c = self.comp_color
        for i in range(200):
            alpha = int(30 * (1 - i / 200))
            pygame.draw.line(glow, (c[0], c[1], c[2], alpha), (0, i), (WIDTH, i))
        surface.blit(glow, (0, 0))

        # Bottom dark bar
        bar = pygame.Surface((WIDTH, 60), pygame.SRCALPHA)
        bar.fill((0, 0, 0, 160))
        surface.blit(bar, (0, HEIGHT - 60))

        # Floodlight cones
        for lx in [int(WIDTH * 0.2), int(WIDTH * 0.8)]:
            cone = pygame.Surface((300, 400), pygame.SRCALPHA)
            for j in range(400):
                w = int(20 + j * 0.4)
                a = max(0, int(12 * (1 - j / 400)))
                pygame.draw.line(cone, (255, 255, 220, a), (150 - w, j), (150 + w, j))
            surface.blit(cone, (lx - 150, 0))

    def _draw_particles(self, surface):
        for p in self.particles:
            r = int(p["r"])
            ps = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(ps, (255, 255, 255, p["alpha"]), (r, r), r)
            surface.blit(ps, (int(p["x"]), int(p["y"])))

    # ──────────────── Stage 0: Intro ────────────────

    def _draw_intro(self, surface):
        cx = WIDTH // 2
        ease = self._ease_out(self.slide_progress)

        # ─ Competition banner (slides down) ─
        banner_y = int(-60 + ease * 120)
        banner = pygame.Surface((520, 45), pygame.SRCALPHA)
        banner.fill((0, 0, 0, 180))
        surface.blit(banner, (cx - 260, banner_y))
        pygame.draw.line(surface, self.comp_color,
                         (cx - 260, banner_y + 44), (cx + 260, banner_y + 44), 3)

        comp_surf = self.font_comp.render(self.comp_name, True, self.comp_color)
        surface.blit(comp_surf, (cx - comp_surf.get_width() // 2, banner_y + 8))

        # ─ Date (career mode) ─
        if self.game_mode == "career":
            try:
                from data.career_manager import career_manager
                d = career_manager.current_date
                if d:
                    months = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
                              "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
                    date_str = f"{d.day} de {months[d.month - 1]} {d.year}"
                    ds = self.font_date.render(date_str, True, UI_TEXT_DIM)
                    surface.blit(ds, (cx - ds.get_width() // 2, banner_y + 55))
            except Exception:
                pass

        # ─ Team badges slide in from sides ─
        badge_y = HEIGHT // 2 - 40
        left_offset = int((1 - ease) * -300)
        right_offset = int((1 - ease) * 300)

        from data.teams import draw_badge
        draw_badge(surface, self.left_team, cx - 220 + left_offset, badge_y, size=90)
        draw_badge(surface, self.right_team, cx + 220 + right_offset, badge_y, size=90)

        # ─ Team names (fade in after badges) ─
        if ease > 0.3:
            name_ease = self._ease_out((self.slide_progress - 0.3) / 0.7)
            name_alpha = int(255 * name_ease)

            n1 = self.font_team.render(self.left_team.get("name", "LOCAL"), True, WHITE)
            n2 = self.font_team.render(self.right_team.get("name", "VISITANTE"), True, WHITE)

            # Render with alpha using temp surfaces
            t1 = pygame.Surface(n1.get_size(), pygame.SRCALPHA)
            t1.blit(n1, (0, 0))
            t1.set_alpha(name_alpha)
            t2 = pygame.Surface(n2.get_size(), pygame.SRCALPHA)
            t2.blit(n2, (0, 0))
            t2.set_alpha(name_alpha)

            surface.blit(t1, (cx - 220 + left_offset - n1.get_width() // 2, badge_y + 65))
            surface.blit(t2, (cx + 220 + right_offset - n2.get_width() // 2, badge_y + 65))

        # ─ VS text (pulsing) ─
        if ease > 0.5:
            pulse = 1.0 + 0.05 * math.sin(self.total_time * 4)
            vs_size = int(72 * pulse)
            try:
                vs_font = pygame.font.SysFont("Impact", vs_size)
            except Exception:
                vs_font = pygame.font.Font(None, vs_size)
            vs = vs_font.render("VS", True, UI_ACCENT_ALT)
            surface.blit(vs, (cx - vs.get_width() // 2, badge_y - vs.get_height() // 2))

    # ──────────────── Stage 1 & 2: Lineup ────────────────

    def _draw_lineup(self, surface, team, starters, is_home):
        ease = self._ease_out(self.slide_progress)
        slide_dir = 1 if is_home else -1
        offset_x = int((1 - ease) * slide_dir * 400)

        # ─ Header bar ─
        header_color = team.get("primary", (100, 100, 100))
        header_bar = pygame.Surface((WIDTH, 50), pygame.SRCALPHA)
        header_bar.fill((*header_color, 200))
        surface.blit(header_bar, (0, 40))
        pygame.draw.line(surface, team.get("accent", WHITE), (0, 89), (WIDTH, 89), 2)

        label = "LOCAL" if is_home else "VISITANTE"
        header_text = self.font_team.render(f"{label}  ·  {team.get('name', 'EQUIPO')}", True, WHITE)
        surface.blit(header_text, (50, 48))

        # Formation name
        form_text = self.font_formation.render(f"Formación: {self.formation_name}", True, UI_TEXT_DIM)
        surface.blit(form_text, (WIDTH - form_text.get_width() - 50, 55))

        # ─ Mini pitch (left half) ─
        pitch_rect = pygame.Rect(40 + offset_x, 110, 520, 520)
        self._draw_mini_pitch(surface, pitch_rect, starters, team)

        # ─ Player list (right half) ─
        list_x = 600 + offset_x
        list_y = 115

        tit_label = self.font_comp.render("TITULARES", True, self.comp_color)
        surface.blit(tit_label, (list_x, list_y))
        pygame.draw.line(surface, self.comp_color,
                         (list_x, list_y + 30), (list_x + 310, list_y + 30), 2)
        list_y += 45

        for i, p in enumerate(starters):
            row_alpha = min(255, int(
                255 * self._ease_out(max(0, (self.stage_time - 0.3 - i * 0.08) / 0.4))
            ))
            if row_alpha <= 5:
                list_y += 42
                continue

            # Row background
            row_bg = pygame.Surface((320, 38), pygame.SRCALPHA)
            row_bg.fill((30, 35, 50, min(200, row_alpha)))
            surface.blit(row_bg, (list_x, list_y))

            # Number
            num_s = self.font_num.render(str(p.get("num", i + 1)), True, (200, 200, 200))
            surface.blit(num_s, (list_x + 8, list_y + 11))

            # Position badge
            pos_col = self._get_pos_color(p.get("pos", "CM"))
            pos_badge = pygame.Surface((36, 22), pygame.SRCALPHA)
            pygame.draw.rect(pos_badge, (*pos_col, min(240, row_alpha)), (0, 0, 36, 22), border_radius=4)
            surface.blit(pos_badge, (list_x + 30, list_y + 8))
            ps = self.font_pos.render(p.get("pos", "??"), True, BLACK)
            surface.blit(ps, (list_x + 30 + 18 - ps.get_width() // 2, list_y + 11))

            # Name
            ns = self.font_player.render(p["name"], True, WHITE)
            surface.blit(ns, (list_x + 75, list_y + 9))

            # OVR
            ovr = p.get("ovr", 75)
            ovr_col = (0, 220, 100) if ovr >= 85 else (255, 215, 0) if ovr >= 80 else UI_TEXT_DIM
            os_text = self.font_player.render(str(ovr), True, ovr_col)
            surface.blit(os_text, (list_x + 280, list_y + 9))

            list_y += 42

    def _draw_mini_pitch(self, surface, rect, starters, team):
        """Dibuja una cancha miniatura con las posiciones de los titulares."""
        pitch = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)

        # Field with grass stripes
        for i in range(0, rect.height, 40):
            stripe_h = min(40, rect.height - i)
            color = (30, 100, 35, 200) if (i // 40) % 2 == 0 else (25, 85, 30, 200)
            pygame.draw.rect(pitch, color, (0, i, rect.width, stripe_h))

        # Field lines
        pygame.draw.rect(pitch, (255, 255, 255, 100), (0, 0, rect.width, rect.height), 2)
        pygame.draw.line(pitch, (255, 255, 255, 80),
                         (rect.width // 2, 0), (rect.width // 2, rect.height), 1)
        pygame.draw.circle(pitch, (255, 255, 255, 80),
                           (rect.width // 2, rect.height // 2), 50, 1)
        # Penalty areas
        pygame.draw.rect(pitch, (255, 255, 255, 80),
                         (0, rect.height // 2 - 80, 80, 160), 1)
        pygame.draw.rect(pitch, (255, 255, 255, 80),
                         (rect.width - 80, rect.height // 2 - 80, 80, 160), 1)

        surface.blit(pitch, rect.topleft)

        # Players on pitch
        form_key = self.formation_name if self.formation_name in FORMATIONS else "4-3-3"
        form_coords = FORMATIONS[form_key]
        team_color = team.get("primary", (200, 200, 200))
        accent = team.get("accent", WHITE)

        for i, player in enumerate(starters):
            if i == 0:  # GK
                px = rect.left + 30
                py = rect.top + rect.height // 2
            else:
                if i - 1 < len(form_coords):
                    fx, fy = form_coords[i - 1]
                    px = rect.left + int(rect.width * fx)
                    py = rect.top + int(rect.height * fy)
                else:
                    px = rect.left + rect.width // 2
                    py = rect.top + rect.height // 2

            entry = self._ease_out(max(0, (self.stage_time - 0.2 - i * 0.06) / 0.5))
            if entry <= 0:
                continue

            # Glow
            glow_size = int(20 * entry)
            if glow_size > 0:
                glow = pygame.Surface((glow_size * 2, glow_size * 2), pygame.SRCALPHA)
                pygame.draw.circle(glow, (*team_color, 40), (glow_size, glow_size), glow_size)
                surface.blit(glow, (px - glow_size, py - glow_size))

            # Circle
            radius = int(14 * entry)
            if radius > 0:
                pygame.draw.circle(surface, team_color, (px, py), radius)
                pygame.draw.circle(surface, accent, (px, py), radius, 2)

            # Number
            if entry > 0.5:
                text_color = WHITE if sum(team_color) < 400 else BLACK
                num_s = self.font_num.render(str(player.get("num", i + 1)), True, text_color)
                surface.blit(num_s, (px - num_s.get_width() // 2, py - num_s.get_height() // 2))

            # Name below
            if entry > 0.7:
                name = player["name"]
                if len(name) > 12:
                    name = name[:11] + "."
                name_s = self.font_small.render(name, True, WHITE)
                nbg = pygame.Surface((name_s.get_width() + 4, name_s.get_height() + 2), pygame.SRCALPHA)
                nbg.fill((0, 0, 0, 150))
                surface.blit(nbg, (px - name_s.get_width() // 2 - 2, py + radius + 2))
                surface.blit(name_s, (px - name_s.get_width() // 2, py + radius + 3))

    # ──────────────── Stage 3: Key Players ────────────────

    def _draw_key_players(self, surface):
        ease = self._ease_out(self.slide_progress)
        cx = WIDTH // 2

        # Title
        title_y = int(-40 + ease * 90)
        title = self.font_comp.render("JUGADORES A SEGUIR", True, GOLD)
        surface.blit(title, (cx - title.get_width() // 2, title_y))
        pygame.draw.line(surface, GOLD, (cx - 180, title_y + 35), (cx + 180, title_y + 35), 2)

        # Two cards
        card_w, card_h = 280, 350
        card_y = 130
        self._draw_star_card(surface, cx - 320, card_y, card_w, card_h,
                             self.left_team, self.left_key, 0.0)
        self._draw_star_card(surface, cx + 40, card_y, card_w, card_h,
                             self.right_team, self.right_key, 0.15)

    def _draw_star_card(self, surface, x, y, w, h, team, key_info, delay):
        card_ease = self._ease_out(max(0, (self.stage_time - delay) / 0.6))
        if card_ease <= 0:
            return

        player = key_info.get("player")
        if not player:
            return

        card_y = y + int((1 - card_ease) * 50)

        # ─ Card surface ─
        card = pygame.Surface((w, h), pygame.SRCALPHA)

        # Gold border glow (pulsing)
        glow_i = int(30 + 15 * math.sin(self.total_time * 3))
        pygame.draw.rect(card, (218, 165, 32, glow_i), (-4, -4, w + 8, h + 8), border_radius=14)

        # Main bg (glassmorphism)
        pygame.draw.rect(card, (15, 18, 30, 230), (0, 0, w, h), border_radius=12)

        # Team color accent strip at top
        team_color = team.get("primary", (100, 100, 100))
        pygame.draw.rect(card, (*team_color, 220), (0, 0, w, 6), border_radius=12)

        # Gold border
        pygame.draw.rect(card, (218, 165, 32, 200), (0, 0, w, h), 2, border_radius=12)

        # Small team badge
        from data.teams import draw_badge
        badge_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
        draw_badge(badge_surf, team, 40, 40, size=35)
        card.blit(badge_surf, (w - 70, 15))

        # Team name
        tn = self.font_label.render(team.get("name", ""), True, UI_TEXT_DIM)
        card.blit(tn, (15, 15))

        # OVR big
        ovr = player.get("ovr", 75)
        ovr_col = GOLD if ovr >= 85 else (0, 220, 100) if ovr >= 80 else WHITE
        ovr_s = self.font_ovr_big.render(str(ovr), True, ovr_col)
        card.blit(ovr_s, (15, 45))

        # Position badge
        pos = player.get("pos", "??")
        pos_col = self._get_pos_color(pos)
        pos_bg = pygame.Surface((45, 24), pygame.SRCALPHA)
        pygame.draw.rect(pos_bg, (*pos_col, 220), (0, 0, 45, 24), border_radius=5)
        card.blit(pos_bg, (15, 105))
        pos_s = self.font_pos.render(pos, True, BLACK)
        card.blit(pos_s, (15 + 22 - pos_s.get_width() // 2, 108))

        # Number
        num = player.get("num", "?")
        num_s = self.font_label.render(f"#{num}", True, UI_TEXT_DIM)
        card.blit(num_s, (70, 108))

        # Player name
        pn = self.font_star_name.render(player["name"], True, WHITE)
        card.blit(pn, (15, 140))

        # Divider
        pygame.draw.line(card, (50, 55, 70), (15, 180), (w - 15, 180), 1)

        # Key stat: goals or OVR highlight
        if key_info.get("is_scorer") and key_info["goals"] > 0:
            goal_label = self.font_label.render("MÁXIMO GOLEADOR", True, GOLD)
            card.blit(goal_label, (15, 195))
            goal_count = self.font_star_stat.render(f"{key_info['goals']} GOLES", True, WHITE)
            card.blit(goal_count, (15, 218))
        else:
            lbl = self.font_label.render("JUGADOR DESTACADO", True, (0, 200, 150))
            card.blit(lbl, (15, 195))
            ovr_label = self.font_star_stat.render(f"OVR {ovr} · {pos}", True, WHITE)
            card.blit(ovr_label, (15, 218))

        # Stats bars
        stats = player.get("s", {})
        stat_items = [
            ("VEL", stats.get("speed", 70)),
            ("TIR", stats.get("shot", 70)),
            ("PAS", stats.get("passing", 70)),
            ("DEF", stats.get("defense", 70)),
        ]
        bar_y = 255
        for lbl, val in stat_items:
            ls = self.font_small.render(lbl, True, UI_TEXT_DIM)
            card.blit(ls, (15, bar_y))
            vs = self.font_small.render(str(val), True, WHITE)
            card.blit(vs, (50, bar_y))
            # Bar background
            pygame.draw.rect(card, (30, 35, 50), (80, bar_y + 3, 170, 8), border_radius=4)
            # Bar fill
            bar_col = (0, 220, 100) if val >= 85 else (255, 215, 0) if val >= 75 else (200, 80, 80)
            fill_w = int(170 * (val / 100))
            pygame.draw.rect(card, bar_col, (80, bar_y + 3, fill_w, 8), border_radius=4)
            bar_y += 22

        surface.blit(card, (x, card_y))

    # ──────────────── UI Overlays ────────────────

    def _draw_hint_bar(self, surface):
        hint = self.font_hint.render(
            "ESPACIO / ENTER  Siguiente  ·  ESC  Saltar al partido", True, UI_TEXT_DIM
        )
        surface.blit(hint, (WIDTH // 2 - hint.get_width() // 2, HEIGHT - 25))

    def _draw_stage_dots(self, surface):
        dot_y = HEIGHT - 45
        total_w = self.NUM_STAGES * 20
        start_x = WIDTH // 2 - total_w // 2
        for i in range(self.NUM_STAGES):
            dx = start_x + i * 20
            if i == self.stage:
                pygame.draw.circle(surface, self.comp_color, (dx, dot_y), 5)
            elif i < self.stage:
                pygame.draw.circle(surface, UI_TEXT_DIM, (dx, dot_y), 4)
            else:
                pygame.draw.circle(surface, (40, 45, 60), (dx, dot_y), 4)
