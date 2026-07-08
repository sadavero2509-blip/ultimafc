import pygame
import math
from settings import *
from data.save_manager import (
    ALL_POSITIONS, POS_LABELS, POS_CATEGORIES,
    save_team_config, get_team_config, add_created_player, add_player_to_team,
    load_user_data
)
from data.teams import TEAMS


class TeamEditorScene:
    """Editor de equipos: formación, alineación y creación de jugadores."""

    # Sub-modos del editor
    MODE_MENU = "menu"
    MODE_FORMATION = "formation"
    MODE_LINEUP = "lineup"
    MODE_CREATE = "create"
    MODE_ASSIGN = "assign"

    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        self.league = self.context.get("league", None)
        self.time = 0

        # Equipos disponibles
        if self.league:
            self.teams = [t for t in TEAMS if t.get("league") == self.league]
        else:
            self.teams = TEAMS[:]
        if not self.teams:
            self.teams = TEAMS[:]

        self.team_idx = 0
        self.mode = self.MODE_MENU
        self.menu_idx = 0
        self.menu_items = [
            {"id": "formation", "name": "FORMACIÓN", "icon": "[FORM]", "desc": "Cambiar la formación táctica"},
            {"id": "lineup", "name": "ALINEACIÓN", "icon": "[LINEUP]", "desc": "Intercambiar titulares y suplentes"},
            {"id": "create", "name": "CREAR JUGADOR", "icon": "[NEW]", "desc": "Crear un nuevo jugador personalizado"},
        ]

        # Formation editor
        self.formations = list(FORMATIONS.keys())
        self.form_idx = 0

        # Lineup editor
        self.lineup_cursor = 0
        self.lineup_selected = None
        self.lineup_roster = []

        # Create player
        self.create_step = 0  # 0=name, 1=pos_cat, 2=pos, 3=stats, 4=assign
        self.create_name = ""
        self.create_pos_cat_idx = 0
        self.create_pos_idx = 0
        self.create_num = 99
        self.create_stats = {"age": 21, "speed": 70, "shot": 70, "passing": 70, "defense": 70, "gk": 10}
        self.create_stat_idx = 0
        self.create_stat_keys = ["age", "speed", "shot", "passing", "defense", "gk"]
        self.create_assign_team_idx = 0
        self.text_input_active = False

        # Fonts
        try:
            self.font_title = pygame.font.SysFont("Impact", 40)
            self.font_section = pygame.font.SysFont("Arial", 22, bold=True)
            self.font_text = pygame.font.SysFont("Arial", 16)
            self.font_text_bold = pygame.font.SysFont("Arial", 16, bold=True)
            self.font_hint = pygame.font.SysFont("Arial", 14)
            self.font_big = pygame.font.SysFont("Impact", 48)
            self.font_input = pygame.font.SysFont("Consolas", 28, bold=True)
            self.font_icon = pygame.font.SysFont("Segoe UI Emoji", 28)
        except:
            self.font_title = pygame.font.Font(None, 40)
            self.font_section = pygame.font.Font(None, 22)
            self.font_text = pygame.font.Font(None, 16)
            self.font_text_bold = pygame.font.Font(None, 16)
            self.font_hint = pygame.font.Font(None, 14)
            self.font_big = pygame.font.Font(None, 48)
            self.font_input = pygame.font.Font(None, 28)
            self.font_icon = pygame.font.Font(None, 28)

    def _current_team(self):
        return self.teams[self.team_idx]

    def _get_full_roster(self, team):
        """Get roster including any custom players added."""
        roster = list(team.get("roster", []))
        ud = load_user_data()
        tc = ud.get("team_configs", {}).get(team["short"], {})
        extras = tc.get("extra_players", [])
        return roster + extras

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.mode == self.MODE_MENU:
                    self._handle_menu(event)
                elif self.mode == self.MODE_FORMATION:
                    self._handle_formation(event)
                elif self.mode == self.MODE_LINEUP:
                    self._handle_lineup(event)
                elif self.mode == self.MODE_CREATE:
                    self._handle_create(event)

    def _handle_menu(self, event):
        if event.key in (pygame.K_UP, pygame.K_w):
            self.menu_idx = (self.menu_idx - 1) % len(self.menu_items)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.menu_idx = (self.menu_idx + 1) % len(self.menu_items)
        elif event.key in (pygame.K_LEFT, pygame.K_a):
            self.team_idx = (self.team_idx - 1) % len(self.teams)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.team_idx = (self.team_idx + 1) % len(self.teams)
        elif event.key == pygame.K_RETURN:
            sel = self.menu_items[self.menu_idx]["id"]
            if sel == "formation":
                self.mode = self.MODE_FORMATION
                self._load_formation()
            elif sel == "lineup":
                self.mode = self.MODE_LINEUP
                self._load_lineup()
            elif sel == "create":
                self.mode = self.MODE_CREATE
                self._reset_create()
        elif event.key == pygame.K_ESCAPE:
            from scenes.team_viewer import TeamViewerScene
            self.manager.set_scene(TeamViewerScene, context=self.context)

    def _handle_formation(self, event):
        if event.key in (pygame.K_LEFT, pygame.K_a):
            self.form_idx = (self.form_idx - 1) % len(self.formations)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.form_idx = (self.form_idx + 1) % len(self.formations)
        elif event.key == pygame.K_RETURN:
            team = self._current_team()
            save_team_config(team["short"], {
                "formation": self.formations[self.form_idx],
                **self._get_existing_config(team["short"])
            })
        elif event.key == pygame.K_ESCAPE:
            self.mode = self.MODE_MENU

    def _handle_lineup(self, event):
        roster = self.lineup_roster
        if event.key in (pygame.K_UP, pygame.K_w):
            self.lineup_cursor = max(0, self.lineup_cursor - 1)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.lineup_cursor = min(len(roster) - 1, self.lineup_cursor + 1)
        elif event.key == pygame.K_RETURN:
            if self.lineup_selected is None:
                self.lineup_selected = self.lineup_cursor
            else:
                # SWAP
                a, b = self.lineup_selected, self.lineup_cursor
                roster[a], roster[b] = roster[b], roster[a]
                self.lineup_selected = None
                # Save
                team = self._current_team()
                team["roster"] = roster
                # Also save indices
                save_team_config(team["short"], {
                    "lineup_order": [p["name"] for p in roster],
                    **self._get_existing_config(team["short"])
                })
        elif event.key == pygame.K_ESCAPE:
            self.mode = self.MODE_MENU

    def _handle_create(self, event):
        if self.create_step == 0:
            # Name input
            if event.key == pygame.K_RETURN and len(self.create_name) > 0:
                self.create_step = 1
            elif event.key == pygame.K_BACKSPACE:
                self.create_name = self.create_name[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.mode = self.MODE_MENU
            else:
                ch = event.unicode
                if ch and ch.isprintable() and len(self.create_name) < 20:
                    self.create_name += ch

        elif self.create_step == 1:
            # Position category
            cats = list(POS_CATEGORIES.keys())
            if event.key in (pygame.K_UP, pygame.K_w):
                self.create_pos_cat_idx = (self.create_pos_cat_idx - 1) % len(cats)
                self.create_pos_idx = 0
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.create_pos_cat_idx = (self.create_pos_cat_idx + 1) % len(cats)
                self.create_pos_idx = 0
            elif event.key == pygame.K_RETURN:
                self.create_step = 2
            elif event.key == pygame.K_ESCAPE:
                self.create_step = 0

        elif self.create_step == 2:
            # Exact position
            cat = list(POS_CATEGORIES.keys())[self.create_pos_cat_idx]
            positions = POS_CATEGORIES[cat]
            if event.key in (pygame.K_UP, pygame.K_w):
                self.create_pos_idx = (self.create_pos_idx - 1) % len(positions)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.create_pos_idx = (self.create_pos_idx + 1) % len(positions)
            elif event.key == pygame.K_RETURN:
                selected_pos = positions[self.create_pos_idx]
                if selected_pos == "GK":
                    self.create_stats = {"age": self.create_stats.get("age", 21), "speed": 40, "shot": 10, "passing": 65, "defense": 30, "gk": 75}
                else:
                    self.create_stats = {"age": self.create_stats.get("age", 21), "speed": 70, "shot": 70, "passing": 70, "defense": 70, "gk": 10}
                self.create_step = 3
                self.create_stat_idx = 0
            elif event.key == pygame.K_ESCAPE:
                self.create_step = 1

        elif self.create_step == 3:
            # Stats editor
            if event.key in (pygame.K_UP, pygame.K_w):
                self.create_stat_idx = (self.create_stat_idx - 1) % len(self.create_stat_keys)
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self.create_stat_idx = (self.create_stat_idx + 1) % len(self.create_stat_keys)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                k = self.create_stat_keys[self.create_stat_idx]
                self.create_stats[k] = min(99, self.create_stats[k] + 1)
            elif event.key in (pygame.K_LEFT, pygame.K_a):
                k = self.create_stat_keys[self.create_stat_idx]
                self.create_stats[k] = max(1, self.create_stats[k] - 1)
            elif event.key == pygame.K_RETURN:
                self.create_step = 4
                self.create_assign_team_idx = self.team_idx
            elif event.key == pygame.K_ESCAPE:
                self.create_step = 2

        elif self.create_step == 4:
            # Assign to team
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.create_assign_team_idx = (self.create_assign_team_idx - 1) % len(self.teams)
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.create_assign_team_idx = (self.create_assign_team_idx + 1) % len(self.teams)
            elif event.key == pygame.K_RETURN:
                self._finalize_player()
            elif event.key == pygame.K_ESCAPE:
                self.create_step = 3

    def _finalize_player(self):
        cat = list(POS_CATEGORIES.keys())[self.create_pos_cat_idx]
        pos = POS_CATEGORIES[cat][self.create_pos_idx]

        player_data = {
            "name": self.create_name,
            "pos": pos,
            "num": self.create_num,
            "s": dict(self.create_stats),
        }

        # Calculate OVR and POT
        s = self.create_stats
        age = s["age"]
        if pos == "GK":
            ovr = int(s["gk"] * 0.5 + s["passing"] * 0.2 + s["speed"] * 0.15 + s["defense"] * 0.15)
        else:
            ovr = int((s["speed"] + s["shot"] + s["passing"] + s["defense"]) / 4)
            
        ovr = ovr + 3 # Emulating the offset used in calculated OVR
        if ovr > 94: ovr = 94
            
        if age <= 18:
            pot = ovr + min(12, 94 - ovr)
        elif age <= 22:
            pot = ovr + min(8, 94 - ovr)
        elif age <= 25:
            pot = ovr + min(4, 94 - ovr)
        elif age <= 28:
            pot = ovr + min(1, 94 - ovr)
        else:
            pot = ovr

        player_data["ovr"] = ovr
        player_data["age"] = age
        player_data["pot"] = pot
        
        # Remove age from s dict
        player_s = dict(s)
        if "age" in player_s: del player_s["age"]
        player_data["s"] = player_s

        # Save globally
        add_created_player(player_data)

        # Add to team's reserves
        team = self.teams[self.create_assign_team_idx]
        add_player_to_team(team["short"], player_data)
        # Also add to runtime roster
        team.setdefault("roster", []).append(player_data)

        self.mode = self.MODE_MENU

    def _reset_create(self):
        self.create_step = 0
        self.create_name = ""
        self.create_pos_cat_idx = 0
        self.create_pos_idx = 0
        self.create_num = 99
        self.create_stats = {"age": 21, "speed": 70, "shot": 70, "passing": 70, "defense": 70, "gk": 10}
        self.create_stat_idx = 0

    def _load_formation(self):
        team = self._current_team()
        tc = self._get_existing_config(team["short"])
        raw_form = tc.get("formation", "4-3-3")
        
        # Migración de Nombres (Inglés -> Español)
        old_to_new = {
            "4-3-3 ATTACK": "4-3-3 OFENSIVA",
            "4-3-3 DEFEND": "4-3-3 DEFENSIVA",
            "4-3-3 FALSE 9": "4-3-3 FALSO 9",
            "4-4-2 HOLDING": "4-4-2 CONTENCIÓN",
            "4-2-3-1 NARROW": "4-2-3-1 CERRADA",
            "4-2-3-1 WIDE": "4-2-3-1 ANCHA",
            "4-1-2-1-2 NARROW": "4-1-2-1-2 CERRADA",
            "4-1-2-1-2 WIDE": "4-1-2-1-2 ANCHA",
            "4-3-2-1": "4-3-2-1 ÁRBOL"
        }
        saved_form = old_to_new.get(raw_form, raw_form)
        
        if saved_form in self.formations:
            self.form_idx = self.formations.index(saved_form)
        else:
            self.form_idx = 0

    def _load_lineup(self):
        team = self._current_team()
        self.lineup_roster = list(self._get_full_roster(team))
        self.lineup_cursor = 0
        self.lineup_selected = None

    def _get_existing_config(self, short):
        ud = load_user_data()
        return ud.get("team_configs", {}).get(short, {})

    def update(self, dt):
        self.time += dt

    def draw(self, surface):
        # Background
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(12 + ratio * 8)
            g = int(14 + ratio * 6)
            b = int(28 + ratio * 14)
            pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

        if self.mode == self.MODE_MENU:
            self._draw_menu(surface)
        elif self.mode == self.MODE_FORMATION:
            self._draw_formation(surface)
        elif self.mode == self.MODE_LINEUP:
            self._draw_lineup(surface)
        elif self.mode == self.MODE_CREATE:
            self._draw_create(surface)

    # ═══════════════════════════════════════════
    # MENU
    # ═══════════════════════════════════════════
    def _draw_menu(self, surface):
        team = self._current_team()
        from data.teams import draw_badge

        # Title
        title = self.font_title.render("EDITOR DE EQUIPOS", True, UI_ACCENT)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 15))
        pygame.draw.line(surface, UI_ACCENT, (WIDTH//2 - 180, 55), (WIDTH//2 + 180, 55), 2)

        # Team selector
        draw_badge(surface, team, WIDTH//2, 110, size=50)
        name_s = self.font_section.render(team["name"], True, WHITE)
        surface.blit(name_s, (WIDTH//2 - name_s.get_width()//2, 150))
        nav = self.font_hint.render("◀ ▶  Cambiar Equipo", True, UI_TEXT_DIM)
        surface.blit(nav, (WIDTH//2 - nav.get_width()//2, 175))

        # Menu cards
        card_y = 220
        for i, item in enumerate(self.menu_items):
            is_sel = (i == self.menu_idx)
            rect = pygame.Rect(WIDTH//2 - 220, card_y, 440, 60)
            bg = UI_CARD_HOVER if is_sel else UI_CARD_BG
            pygame.draw.rect(surface, bg, rect, border_radius=12)
            if is_sel:
                pulse = (math.sin(self.time * 4) + 1) / 2
                bc = (int(pulse * 100), int(150 + pulse * 100), int(150 + pulse * 50))
                pygame.draw.rect(surface, bc, rect, 2, border_radius=12)
            else:
                pygame.draw.rect(surface, (50, 55, 70), rect, 1, border_radius=12)

            try:
                sz = 14 if len(item["icon"]) > 1 else 28
                font = pygame.font.SysFont("Arial", sz, bold=True) if len(item["icon"]) > 1 else self.font_icon
                icon_s = font.render(item["icon"], True, WHITE)
                surface.blit(icon_s, (rect.left + 15, rect.centery - icon_s.get_height()//2))
            except:
                pass
            icon_offset = 85 if len(item["icon"]) > 1 else 60
            ns = self.font_section.render(item["name"], True, WHITE if is_sel else UI_TEXT_DIM)
            surface.blit(ns, (rect.left + icon_offset, rect.top + 8))
            ds = self.font_hint.render(item["desc"], True, UI_TEXT_DIM)
            surface.blit(ds, (rect.left + icon_offset, rect.top + 34))
            card_y += 75

        hint = self.font_hint.render("↑↓/WS Navegar  ·  ENTER Seleccionar  ·  ESC Volver", True, UI_TEXT_DIM)
        surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 30))

    # ═══════════════════════════════════════════
    # FORMATION EDITOR
    # ═══════════════════════════════════════════
    def _draw_formation(self, surface):
        team = self._current_team()
        formation = self.formations[self.form_idx]

        title = self.font_title.render(f"FORMACIÓN — {team['name']}", True, UI_ACCENT)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 15))

        # Big formation name
        form_s = self.font_big.render(formation, True, WHITE)
        surface.blit(form_s, (WIDTH//2 - form_s.get_width()//2, 80))

        nav = self.font_section.render("◀  ▶  para cambiar", True, UI_TEXT_DIM)
        surface.blit(nav, (WIDTH//2 - nav.get_width()//2, 140))

        # Preview field
        field_rect = pygame.Rect(WIDTH//2 - 220, 180, 440, 400)
        pygame.draw.rect(surface, (34, 100, 34), field_rect, border_radius=8)
        pygame.draw.rect(surface, (80, 150, 80), field_rect, 2, border_radius=8)
        pygame.draw.line(surface, (80, 150, 80), (field_rect.centerx, field_rect.top), (field_rect.centerx, field_rect.bottom), 1)
        pygame.draw.circle(surface, (80, 150, 80), field_rect.center, 40, 1)

        # GK
        gk_x = field_rect.left + 25
        gk_y = field_rect.centery
        pygame.draw.circle(surface, (220, 200, 50), (gk_x, gk_y), 10)
        gs = self.font_hint.render("GK", True, (0, 0, 0))
        surface.blit(gs, (gk_x - gs.get_width()//2, gk_y - gs.get_height()//2))

        # Field players from formation
        coords = FORMATIONS[formation]
        pos_colors = {"D": (50, 150, 250), "M": (50, 200, 100), "A": (250, 80, 80)}
        for i, (fx, fy) in enumerate(coords):
            px = field_rect.left + int(field_rect.width * fx)
            py = field_rect.top + int(field_rect.height * fy)
            # Determine color by zone
            if fx < 0.20:
                c = pos_colors["D"]
            elif fx < 0.35:
                c = pos_colors["M"]
            else:
                c = pos_colors["A"]
            pygame.draw.circle(surface, c, (px, py), 10)

        # Save hint
        saved_form = self._get_existing_config(team["short"]).get("formation", "4-3-3")
        status = "[OK] Guardada" if formation == saved_form else "ENTER para guardar"
        ss = self.font_text.render(status, True, (0, 200, 100) if "[OK]" in status else UI_TEXT_DIM)
        surface.blit(ss, (WIDTH//2 - ss.get_width()//2, HEIGHT - 65))

        hint = self.font_hint.render("←→/AD Cambiar  ·  ENTER Guardar  ·  ESC Volver", True, UI_TEXT_DIM)
        surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 30))

    # ═══════════════════════════════════════════
    # LINEUP EDITOR
    # ═══════════════════════════════════════════
    def _draw_lineup(self, surface):
        team = self._current_team()
        roster = self.lineup_roster

        title = self.font_title.render(f"ALINEACIÓN — {team['name']}", True, UI_ACCENT)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 15))
        pygame.draw.line(surface, UI_ACCENT, (WIDTH//2 - 200, 55), (WIDTH//2 + 200, 55), 2)

        # Instructions
        instr = self.font_text.render("Los primeros 11 son titulares. Selecciona 2 jugadores para intercambiarlos.", True, UI_TEXT_DIM)
        surface.blit(instr, (WIDTH//2 - instr.get_width()//2, 65))

        # Player list
        col_x = 80
        row_h = 28
        start_y = 100
        max_visible = 20
        scroll = max(0, self.lineup_cursor - max_visible + 3)

        # Column headers
        headers = [("#", 30), ("POS", 50), ("NOMBRE", 200), ("OVR", 40), ("VEL", 40), ("TIR", 40), ("PAS", 40), ("DEF", 40), ("POR", 40)]
        hx = col_x
        for label, w in headers:
            hs = self.font_text_bold.render(label, True, UI_ACCENT)
            surface.blit(hs, (hx, start_y - 20))
            hx += w + 10

        # Division line for starters/subs
        for i, p in enumerate(roster[scroll:scroll+max_visible]):
            real_i = i + scroll
            y = start_y + i * row_h

            # Division
            if real_i == 11:
                pygame.draw.line(surface, UI_ACCENT, (col_x, y - 4), (col_x + 600, y - 4), 2)
                label = self.font_hint.render("─── SUPLENTES / RESERVAS ───", True, UI_ACCENT)
                surface.blit(label, (col_x + 150, y - 18))
                y += 6

            is_cursor = (real_i == self.lineup_cursor)
            is_selected = (real_i == self.lineup_selected)
            is_starter = (real_i < 11)

            # Row bg
            if is_selected:
                row_rect = pygame.Rect(col_x - 5, y - 2, 620, row_h)
                pygame.draw.rect(surface, (80, 40, 20), row_rect, border_radius=4)
                pygame.draw.rect(surface, (255, 100, 60), row_rect, 2, border_radius=4)
            elif is_cursor:
                row_rect = pygame.Rect(col_x - 5, y - 2, 620, row_h)
                pygame.draw.rect(surface, UI_CARD_HOVER, row_rect, border_radius=4)
                pygame.draw.rect(surface, UI_ACCENT, row_rect, 1, border_radius=4)
            elif i % 2 == 0:
                row_rect = pygame.Rect(col_x - 5, y - 2, 620, row_h)
                pygame.draw.rect(surface, (25, 28, 40), row_rect, border_radius=4)

            text_color = WHITE if is_starter else UI_TEXT_DIM
            cx = col_x
            # Num
            ns = self.font_text.render(str(p.get("num", "")), True, text_color)
            surface.blit(ns, (cx, y))
            cx += 40
            # Pos badge
            pos = p.get("pos", "?")
            pc = self._pos_color(pos)
            pos_rect = pygame.Rect(cx, y, 36, 18)
            pygame.draw.rect(surface, pc, pos_rect, border_radius=4)
            ps = self.font_hint.render(pos, True, (0, 0, 0))
            surface.blit(ps, (pos_rect.centerx - ps.get_width()//2, y + 1))
            cx += 60
            # Name
            nm = self.font_text_bold.render(p["name"], True, text_color) if is_starter else self.font_text.render(p["name"], True, text_color)
            surface.blit(nm, (cx, y))
            cx += 210
            # OVR
            ovr = p.get("ovr", 75)
            ovr_c = (0, 220, 100) if ovr >= 85 else (255, 215, 0) if ovr >= 80 else UI_TEXT_DIM
            os_ = self.font_text_bold.render(str(ovr), True, ovr_c)
            surface.blit(os_, (cx, y))
            cx += 50
            # Stats
            for sk in ["speed", "shot", "passing", "defense", "gk"]:
                val = p["s"].get(sk, 0)
                vc = (0, 200, 100) if val >= 85 else (200, 200, 0) if val >= 70 else (150, 150, 150)
                vs = self.font_hint.render(str(val), True, vc)
                surface.blit(vs, (cx, y + 1))
                cx += 50

        hint = self.font_hint.render("↑↓ Mover  ·  ENTER Seleccionar/Intercambiar  ·  ESC Volver", True, UI_TEXT_DIM)
        surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 30))

    # ═══════════════════════════════════════════
    # CREATE PLAYER
    # ═══════════════════════════════════════════
    def _draw_create(self, surface):
        # Card background
        card = pygame.Rect(WIDTH//2 - 300, 60, 600, HEIGHT - 120)
        pygame.draw.rect(surface, UI_CARD_BG, card, border_radius=16)
        pulse = (math.sin(self.time * 3) + 1) / 2
        bc = (int(80 + 40 * pulse), int(60 + 60 * pulse), int(180 + 40 * pulse))
        pygame.draw.rect(surface, bc, card, 2, border_radius=16)

        title = self.font_title.render("CREAR JUGADOR", True, (180, 120, 255))
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 75))

        steps = ["Nombre", "Categoría", "Posición", "Estadísticas", "Asignar a Equipo"]
        # Step indicator
        for i, s in enumerate(steps):
            color = UI_ACCENT if i == self.create_step else UI_TEXT_DIM if i < self.create_step else (60, 60, 70)
            if i < self.create_step:
                color = (0, 200, 100)
            sx = card.left + 30 + i * 115
            pygame.draw.circle(surface, color, (sx + 10, 125), 12)
            ns = self.font_hint.render(str(i+1), True, (0, 0, 0))
            surface.blit(ns, (sx + 10 - ns.get_width()//2, 125 - ns.get_height()//2))
            ls = self.font_hint.render(s, True, color)
            surface.blit(ls, (sx - 10, 145))

        content_y = 180

        if self.create_step == 0:
            # NAME INPUT
            label = self.font_section.render("Nombre del Jugador:", True, WHITE)
            surface.blit(label, (card.left + 50, content_y))

            input_rect = pygame.Rect(card.left + 50, content_y + 40, 500, 50)
            pygame.draw.rect(surface, (20, 20, 40), input_rect, border_radius=8)
            pygame.draw.rect(surface, UI_ACCENT, input_rect, 2, border_radius=8)

            cursor_blink = "_" if int(self.time * 2) % 2 == 0 else ""
            name_s = self.font_input.render(self.create_name + cursor_blink, True, WHITE)
            surface.blit(name_s, (input_rect.left + 15, input_rect.centery - name_s.get_height()//2))

            hint = self.font_hint.render("Escribe el nombre  ·  ENTER Confirmar", True, UI_TEXT_DIM)
            surface.blit(hint, (card.left + 50, content_y + 110))

        elif self.create_step == 1:
            # POSITION CATEGORY
            label = self.font_section.render("Categoría de Posición:", True, WHITE)
            surface.blit(label, (card.left + 50, content_y))
            cats = list(POS_CATEGORIES.keys())
            for i, cat in enumerate(cats):
                is_sel = (i == self.create_pos_cat_idx)
                cy = content_y + 40 + i * 50
                rect = pygame.Rect(card.left + 50, cy, 500, 40)
                bg = UI_CARD_HOVER if is_sel else (30, 30, 50)
                pygame.draw.rect(surface, bg, rect, border_radius=8)
                if is_sel:
                    pygame.draw.rect(surface, UI_ACCENT, rect, 2, border_radius=8)
                positions_str = ", ".join(POS_LABELS.get(p, p) for p in POS_CATEGORIES[cat])
                cs = self.font_text_bold.render(cat, True, WHITE if is_sel else UI_TEXT_DIM)
                surface.blit(cs, (rect.left + 15, cy + 3))
                ps = self.font_hint.render(positions_str, True, UI_TEXT_DIM)
                surface.blit(ps, (rect.left + 15, cy + 22))

        elif self.create_step == 2:
            # EXACT POSITION
            cat = list(POS_CATEGORIES.keys())[self.create_pos_cat_idx]
            positions = POS_CATEGORIES[cat]
            label = self.font_section.render(f"Posición en {cat}:", True, WHITE)
            surface.blit(label, (card.left + 50, content_y))
            for i, pos in enumerate(positions):
                is_sel = (i == self.create_pos_idx)
                py = content_y + 40 + i * 45
                rect = pygame.Rect(card.left + 50, py, 500, 38)
                bg = UI_CARD_HOVER if is_sel else (30, 30, 50)
                pygame.draw.rect(surface, bg, rect, border_radius=8)
                if is_sel:
                    pygame.draw.rect(surface, self._pos_color(pos), rect, 2, border_radius=8)
                # Pos badge
                pb_rect = pygame.Rect(rect.left + 15, py + 8, 44, 22)
                pygame.draw.rect(surface, self._pos_color(pos), pb_rect, border_radius=4)
                ps = self.font_text_bold.render(pos, True, (0, 0, 0))
                surface.blit(ps, (pb_rect.centerx - ps.get_width()//2, py + 10))
                # Full name
                fn = self.font_text.render(POS_LABELS.get(pos, pos), True, WHITE if is_sel else UI_TEXT_DIM)
                surface.blit(fn, (rect.left + 75, py + 10))

        elif self.create_step == 3:
            # STATS EDITOR
            label = self.font_section.render(f"Estadísticas y Edad de {self.create_name}:", True, WHITE)
            surface.blit(label, (card.left + 50, content_y))
            stat_labels = {"age": "Edad", "speed": "Velocidad", "shot": "Tiro", "passing": "Pase", "defense": "Defensa", "gk": "Portero"}
            for i, key in enumerate(self.create_stat_keys):
                is_sel = (i == self.create_stat_idx)
                sy = content_y + 35 + i * 45
                val = self.create_stats[key]

                # Label
                sl = self.font_text_bold.render(stat_labels[key], True, WHITE if is_sel else UI_TEXT_DIM)
                surface.blit(sl, (card.left + 60, sy))

                # Bar
                bar_x = card.left + 200
                bar_w = 250
                bar_h = 16
                pygame.draw.rect(surface, (40, 40, 55), (bar_x, sy + 2, bar_w, bar_h), border_radius=8)
                
                max_val = 40 if key == "age" else 99
                min_val = 15 if key == "age" else 1
                fill_w = int(max(0, (val - min_val) / max(1, max_val - min_val)) * bar_w)
                
                if key == "age":
                    bc_bar = (150, 150, 200)
                else:
                    bc_bar = (0, 200, 100) if val >= 85 else (200, 200, 0) if val >= 70 else (180, 100, 60)
                
                pygame.draw.rect(surface, bc_bar, (bar_x, sy + 2, fill_w, bar_h), border_radius=8)

                # Value
                vs = self.font_section.render(str(val), True, bc_bar)
                surface.blit(vs, (bar_x + bar_w + 15, sy - 2))

                if is_sel:
                    # Arrows
                    al = self.font_text_bold.render("◀", True, UI_ACCENT)
                    ar = self.font_text_bold.render("▶", True, UI_ACCENT)
                    surface.blit(al, (bar_x - 20, sy))
                    surface.blit(ar, (bar_x + bar_w + 50, sy))

            hint = self.font_hint.render("↑↓ Stat  ·  ← → Ajustar  ·  ENTER Confirmar", True, UI_TEXT_DIM)
            surface.blit(hint, (card.left + 50, card.bottom - 50))

        elif self.create_step == 4:
            # ASSIGN TO TEAM
            from data.teams import draw_badge
            team = self.teams[self.create_assign_team_idx]
            label = self.font_section.render("Asignar a equipo (reservas):", True, WHITE)
            surface.blit(label, (card.left + 50, content_y))

            draw_badge(surface, team, WIDTH//2, content_y + 90, size=60)
            tn = self.font_section.render(team["name"], True, WHITE)
            surface.blit(tn, (WIDTH//2 - tn.get_width()//2, content_y + 140))
            nav = self.font_hint.render("◀ ▶  Cambiar equipo", True, UI_TEXT_DIM)
            surface.blit(nav, (WIDTH//2 - nav.get_width()//2, content_y + 170))

            # Preview card
            cat = list(POS_CATEGORIES.keys())[self.create_pos_cat_idx]
            pos = POS_CATEGORIES[cat][self.create_pos_idx]
            preview_y = content_y + 210
            ps = self.font_text.render(f"{self.create_name}  |  {pos}  |  #{self.create_num}", True, UI_TEXT)
            surface.blit(ps, (WIDTH//2 - ps.get_width()//2, preview_y))
            stat_str = "  ".join(f"{k[:3].upper()}:{v}" for k, v in self.create_stats.items())
            ss = self.font_hint.render(stat_str, True, UI_TEXT_DIM)
            surface.blit(ss, (WIDTH//2 - ss.get_width()//2, preview_y + 24))

            hint = self.font_hint.render("ENTER Confirmar y Guardar  ·  ESC Volver", True, UI_TEXT_DIM)
            surface.blit(hint, (card.left + 50, card.bottom - 50))

    def _pos_color(self, pos):
        if pos == "GK": return (220, 200, 50)
        if pos in ["CB", "LB", "RB", "LWB", "RWB"]: return (50, 150, 250)
        if pos in ["CDM", "CM", "CAM", "LM", "RM"]: return (50, 200, 100)
        return (250, 80, 80)
