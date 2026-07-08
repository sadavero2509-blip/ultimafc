import pygame
import math
from settings import *
from scene_manager import BaseScene
from data.positions import get_pos_desc

class TacticsScene(BaseScene):
    """Menú de gestión táctica del equipo local."""

    def __init__(self, manager, in_match=False, match_scene=None):
        super().__init__(manager)
        self.in_match = in_match
        self.match_scene = match_scene
        self.team = manager.shared_data["player_team"]
        self.roster = list(self.team.get("roster", []))
        
        # Load saved config if available
        from data.save_manager import load_user_data
        ud = load_user_data()
        tc = ud.get("team_configs", {}).get(self.team.get("short", ""), {})
        
        # Apply saved formation
        saved_formation = tc.get("formation", None)
        
        # Add extra reserve players if any
        extras = tc.get("extra_players", [])
        full_roster = self.roster + [p for p in extras if p not in self.roster]
        
        # Apply saved lineup order if present
        saved_order = tc.get("lineup_order", None)
        if saved_order:
            ordered = []
            remaining = list(full_roster)
            for name in saved_order:
                match = next((p for p in remaining if p["name"] == name), None)
                if match:
                    ordered.append(match)
                    remaining.remove(match)
            ordered.extend(remaining)
            full_roster = ordered
        
        # El roster asume los primeros 11 como titulares
        self.starters = full_roster[:11]
        self.subs = full_roster[11:]
        
        self.formations = list(FORMATIONS.keys())
        self.formation_idx = 0
        if saved_formation and saved_formation in self.formations:
            self.formation_idx = self.formations.index(saved_formation)
        self.manager.shared_data["formation"] = self.formations[self.formation_idx]
        self.manager.shared_data["starters"] = self.starters
        
        self.selected_starter_idx = None
        self.selected_sub_idx = None
        
        try:
            self.font_title = pygame.font.SysFont("Impact", 42)
            self.font_btn = pygame.font.SysFont("Arial", 22, bold=True)
            self.font_text = pygame.font.SysFont("Arial", 16)
            self.font_card_name = pygame.font.SysFont("Arial", 24, bold=True)
            self.font_card_ovr = pygame.font.SysFont("Impact", 36)
        except:
            self.font_title = pygame.font.Font(None, 42)
            self.font_btn = pygame.font.Font(None, 24)
            self.font_text = pygame.font.Font(None, 16)
            self.font_card_name = pygame.font.Font(None, 24)
            self.font_card_ovr = pygame.font.Font(None, 36)
            
        self.field_rect = pygame.Rect(WIDTH//2, 100, WIDTH//2 - 50, HEIGHT - 150)
        
        self.btn_form_rect = pygame.Rect(WIDTH//2 + 10, HEIGHT - 70, 180, 40)
        self.btn_diff_rect = pygame.Rect(WIDTH//2 + 200, HEIGHT - 70, 220, 40)
        self.btn_play_rect = pygame.Rect(WIDTH - 220, HEIGHT - 70, 180, 40)
        self.btn_cap_rect = pygame.Rect(50, 210, 180, 25)
        
        self.difficulty = self.manager.shared_data.get("difficulty", 5)
        
        # Keyboard Navigation state
        self.nav_section = "starters" # starters, subs, formation, difficulty, play
        self.nav_idx = 0
        
    def _get_player_color(self, pos):
        if pos == "GK": return (220, 200, 50)
        if pos in ["CB", "LB", "RB"]: return (50, 150, 250)
        if pos in ["CM", "CDM", "CAM"]: return (50, 200, 100)
        return (250, 80, 80) # Ataque

    def handle_events(self, events):
        mx, my = pygame.mouse.get_pos()
        self.hovered_player = None
        
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.btn_play_rect.collidepoint(mx, my):
                        self._action_play()
                    elif self.btn_form_rect.collidepoint(mx, my):
                        self._action_toggle_formation()
                    elif self.btn_diff_rect.collidepoint(mx, my):
                        self._action_toggle_difficulty()
                    elif self.btn_cap_rect.collidepoint(mx, my):
                        self._action_set_captain()
                    else:
                        # Check clicks on players (existing logic simplified to calls)
                        self._check_mouse_player_clicks(mx, my)

            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self._nav_move("up")
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self._nav_move("down")
                elif event.key in (pygame.K_LEFT, pygame.K_a):
                    self._nav_move("left")
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self._nav_move("right")
                elif event.key == pygame.K_RETURN:
                    self._nav_select()
                elif event.key == pygame.K_ESCAPE:
                    if self.in_match: self.manager.pop_scene()

    def _nav_move(self, dir):
        if self.nav_section == "starters":
            if dir == "down": self.nav_idx = (self.nav_idx + 1) % 11
            elif dir == "up": self.nav_idx = (self.nav_idx - 1) % 11
            elif dir == "left": 
                self.nav_section = "subs"; self.nav_idx = 0
        elif self.nav_section == "subs":
            if dir == "down":
                if len(self.subs) > 0: self.nav_idx = (self.nav_idx + 1) % len(self.subs)
                else: self.nav_idx = 0
            elif dir == "up":
                if len(self.subs) > 0: self.nav_idx = (self.nav_idx - 1) % len(self.subs)
                else: self.nav_idx = 0
            elif dir == "right":
                self.nav_section = "starters"; self.nav_idx = 0
            elif dir == "left":
                self.nav_section = "formation"; self.nav_idx = 0
        elif self.nav_section == "formation":
            if dir == "right": self.nav_section = "difficulty"; self.nav_idx = 0
            elif dir == "down": self.nav_section = "play"; self.nav_idx = 0
        elif self.nav_section == "difficulty":
            if dir == "left": self.nav_section = "formation"; self.nav_idx = 0
            elif dir == "right": self.nav_section = "play"; self.nav_idx = 0
            elif dir == "down": self.nav_section = "play"; self.nav_idx = 0
        elif self.nav_section == "play":
            if dir == "up": self.nav_section = "formation"; self.nav_idx = 0
            elif dir == "left": self.nav_section = "difficulty"; self.nav_idx = 0

    def _nav_select(self):
        if self.nav_section == "starters":
            if self.selected_starter_idx == self.nav_idx: self.selected_starter_idx = None
            else: self.selected_starter_idx = self.nav_idx
            if self.selected_starter_idx is not None and self.selected_sub_idx is not None: self._swap_players()
        elif self.nav_section == "subs":
            if self.selected_sub_idx == self.nav_idx: self.selected_sub_idx = None
            else: self.selected_sub_idx = self.nav_idx
            if self.selected_starter_idx is not None and self.selected_sub_idx is not None: self._swap_players()
        elif self.nav_section == "formation":
            self._action_toggle_formation()
        elif self.nav_section == "difficulty":
            self._action_toggle_difficulty()
        elif self.nav_section == "play":
            self._action_play()

    def _action_play(self):
        if self.in_match:
            self.manager.pop_scene()
        else:
            self.manager.shared_data["starters"] = self.starters
            self.manager.shared_data["formation"] = self.formations[self.formation_idx]
            self.manager.shared_data["difficulty"] = self.difficulty
            from scenes.pre_match_presentation import PreMatchPresentationScene
            self.manager.transition_to(PreMatchPresentationScene)

    def _action_toggle_difficulty(self):
        levels = [1, 3, 5, 7, 9]
        if self.difficulty in levels:
            idx = levels.index(self.difficulty)
            self.difficulty = levels[(idx + 1) % len(levels)]
        else:
            self.difficulty = 5
        self.manager.shared_data["difficulty"] = self.difficulty

    def _action_toggle_formation(self):
        self.formation_idx = (self.formation_idx + 1) % len(self.formations)
        self.manager.shared_data["formation"] = self.formations[self.formation_idx]
        if self.in_match and self.match_scene:
            self.match_scene.apply_formation(self.formations[self.formation_idx])
        self.selected_starter_idx = None

    def _action_set_captain(self):
        p = self.hovered_player if self.hovered_player else self.starters[self.selected_starter_idx] if self.selected_starter_idx is not None else None
        if p: self._set_captain(p)

    def _check_mouse_player_clicks(self, mx, my):
        form_coords = FORMATIONS[self.formations[self.formation_idx]]
        for i, player in enumerate(self.starters):
            if player["pos"] == "GK":
                px, py = self.field_rect.left + 30, self.field_rect.centery
            else:
                fx, fy = form_coords[i-1]
                px, py = self.field_rect.left + self.field_rect.width * fx, self.field_rect.top + self.field_rect.height * fy
            if pygame.Rect(px - 15, py - 15, 30, 30).collidepoint(mx, my):
                self.selected_starter_idx = i if self.selected_starter_idx != i else None
                self.nav_section = "starters"; self.nav_idx = i
                if self.selected_starter_idx is not None and self.selected_sub_idx is not None: self._swap_players()
                return

        sub_y_start = 300
        for i, player in enumerate(self.subs):
            if pygame.Rect(50, sub_y_start + i * 40, 300, 35).collidepoint(mx, my):
                self.selected_sub_idx = i if self.selected_sub_idx != i else None
                self.nav_section = "subs"; self.nav_idx = i
                if self.selected_starter_idx is not None and self.selected_sub_idx is not None: self._swap_players()
                return

    def _swap_players(self):
        # Efectuar cambio
        titular = self.starters[self.selected_starter_idx]
        suplente = self.subs[self.selected_sub_idx]
        self.starters[self.selected_starter_idx] = suplente
        self.subs[self.selected_sub_idx] = titular
        
        if self.in_match and self.match_scene:
            self.match_scene.queue_manual_substitution(titular, suplente)
            
        # Limpiar
        self.selected_starter_idx = None
        self.selected_sub_idx = None

    def _set_captain(self, player):
        # Limpiar todos
        for p in self.starters + self.subs:
            p["is_captain"] = False
        # Asignar nuevo
        player["is_captain"] = True

    def update(self, dt):
        mx, my = pygame.mouse.get_pos()
        self.hovered_player = None
        
        # Hover logic (Mouse)
        form_coords = FORMATIONS[self.formations[self.formation_idx]]
        for i, player in enumerate(self.starters):
            if player["pos"] == "GK": px, py = self.field_rect.left + 30, self.field_rect.centery
            else:
                fx, fy = form_coords[i-1]
                px, py = self.field_rect.left + self.field_rect.width * fx, self.field_rect.top + self.field_rect.height * fy
            if pygame.Rect(px - 15, py - 15, 30, 30).collidepoint(mx, my):
                self.hovered_player = player
                
        sub_y_start = 300
        for i, player in enumerate(self.subs):
            if pygame.Rect(50, sub_y_start + i * 40, 300, 35).collidepoint(mx, my):
                self.hovered_player = player
                
        # Override hover if using keyboard
        if self.nav_section == "starters":
            self.hovered_player = self.starters[self.nav_idx]
        elif self.nav_section == "subs" and self.nav_idx < len(self.subs):
            self.hovered_player = self.subs[self.nav_idx]

    def draw(self, surface):
        surface.fill(UI_BG)
        
        title = self.font_title.render("ESTRATEGIA", True, UI_TEXT)
        surface.blit(title, (50, 30))
        
        self._draw_left_panel(surface)
        self._draw_field(surface)
        self._draw_card(surface)
        
        # Botones
        pygame.draw.rect(surface, UI_ACCENT if self.nav_section == "formation" else (40, 45, 60), self.btn_form_rect, border_radius=8)
        if self.nav_section == "formation": pygame.draw.rect(surface, WHITE, self.btn_form_rect, 2, border_radius=8)
        form_surf = self.font_btn.render(f"F: {self.formations[self.formation_idx]}", True, WHITE if self.nav_section=="formation" else UI_TEXT_DIM)
        surface.blit(form_surf, form_surf.get_rect(center=self.btn_form_rect.center))
        
        # Dificultad
        pygame.draw.rect(surface, UI_ACCENT if self.nav_section == "difficulty" else (40, 45, 60), self.btn_diff_rect, border_radius=8)
        if self.nav_section == "difficulty": pygame.draw.rect(surface, WHITE, self.btn_diff_rect, 2, border_radius=8)
        
        diff_name = "PROFESIONAL"
        for name, data in DIFFICULTY_PRESETS.items():
            if data["level"] == self.difficulty:
                diff_name = name
                break
        diff_surf = self.font_btn.render(f"DIF: {diff_name}", True, WHITE if self.nav_section=="difficulty" else UI_TEXT_DIM)
        surface.blit(diff_surf, diff_surf.get_rect(center=self.btn_diff_rect.center))
        
        pygame.draw.rect(surface, UI_ACCENT_ALT if self.nav_section == "play" else (40, 45, 60), self.btn_play_rect, border_radius=8)
        if self.nav_section == "play": pygame.draw.rect(surface, WHITE, self.btn_play_rect, 2, border_radius=8)
        btn_text = "VOLVER AL JUEGO" if getattr(self, "in_match", False) else "JUGAR PARTIDO"
        play_surf = self.font_btn.render(btn_text, True, WHITE)
        surface.blit(play_surf, play_surf.get_rect(center=self.btn_play_rect.center))

    def _draw_left_panel(self, surface):
        header = self.font_btn.render("Banquillo y Reservas (Click para cambiar)", True, UI_TEXT_DIM)
        surface.blit(header, (50, 260))
        
        sy = 300
        for i, player in enumerate(self.subs):
            rect = pygame.Rect(50, sy + i * 40, 300, 35)
            # Selection/Nav Logic
            is_nav = (self.nav_section == "subs" and self.nav_idx == i)
            bg = UI_CARD_HOVER if is_nav or self.selected_sub_idx == i else UI_CARD_BG
            pygame.draw.rect(surface, bg, rect, border_radius=5)
            
            if is_nav or self.selected_sub_idx == i:
                pygame.draw.rect(surface, UI_ACCENT if self.selected_sub_idx == i else WHITE, rect, 2, border_radius=5)
            
            pcol = self._get_player_color(player["pos"])
            # Pos badge
            pygame.draw.rect(surface, pcol, (55, sy + i * 40 + 5, 40, 25), border_radius=4)
            pos_surf = self.font_text.render(player["pos"], True, BLACK)
            surface.blit(pos_surf, pos_surf.get_rect(center=(75, sy + i * 40 + 17)))
            
            # Name
            name_txt = f"{player.get('num', '-')}. {player['name']}"
            if player.get("is_captain"):
                name_txt = "(C) " + name_txt
            name_surf = self.font_text.render(name_txt, True, UI_TEXT)
            surface.blit(name_surf, (105, sy + i * 40 + 8))
            
            # OVR
            ovr_surf = self.font_text.render(f"OVR: {player['ovr']}", True, UI_TEXT_DIM)
            surface.blit(ovr_surf, (270, sy + i * 40 + 8))

            # --- STAMINA BAR (Subs) ---
            energy = player.get("energy", 100.0)
            s_rect = pygame.Rect(105, sy + i * 40 + 26, 120, 4)
            pygame.draw.rect(surface, (30, 30, 30), s_rect, border_radius=2)
            ratio = energy / 100.0
            s_col = (50, 200, 50) if ratio > 0.6 else (200, 200, 50) if ratio > 0.3 else (200, 50, 50)
            pygame.draw.rect(surface, s_col, (s_rect.x, s_rect.y, int(s_rect.width * ratio), s_rect.height), border_radius=2)

    def _draw_field(self, surface):
        # Dibuja la cancha y los titulares
        pygame.draw.rect(surface, GREEN_PITCH, self.field_rect)
        pygame.draw.rect(surface, WHITE, self.field_rect, 2)
        
        # Center line
        pygame.draw.line(surface, WHITE, (self.field_rect.centerx, self.field_rect.top), (self.field_rect.centerx, self.field_rect.bottom), 2)
        pygame.draw.circle(surface, WHITE, self.field_rect.center, 40, 2)
        
        # Área izquierda (siempre mostramos táctica como si atacaras hacia la derecha)
        pygame.draw.rect(surface, WHITE, (self.field_rect.left, self.field_rect.centery - 80, 100, 160), 2)
        
        form_coords = FORMATIONS[self.formations[self.formation_idx]]
        
        for i, player in enumerate(self.starters):
            if player["pos"] == "GK":
                px, py = self.field_rect.left + 30, self.field_rect.centery
            else:
                fx, fy = form_coords[i-1]
                px = self.field_rect.left + self.field_rect.width * fx
                py = self.field_rect.top + self.field_rect.height * fy
                
            color = self._get_player_color(player["pos"])
            
            pygame.draw.circle(surface, color, (int(px), int(py)), 14)
            is_nav = (self.nav_section == "starters" and self.nav_idx == i)
            if is_nav or self.selected_starter_idx == i:
                pygame.draw.circle(surface, UI_ACCENT if self.selected_starter_idx == i else WHITE, (int(px), int(py)), 16, 3)
            else:
                pygame.draw.circle(surface, BLACK, (int(px), int(py)), 14, 2)
                
            num_txt = str(player.get("num", "-"))
            if player.get("is_captain"):
                num_txt = "C"
            num_surf = self.font_text.render(num_txt, True, WHITE)
            surface.blit(num_surf, num_surf.get_rect(center=(int(px), int(py))))
            
            name_surf = self.font_text.render(player["name"], True, WHITE)
            # Fondo negro para visibilidad
            name_bg = pygame.Surface((name_surf.get_width() + 4, name_surf.get_height() + 2))
            name_bg.fill(BLACK)
            name_bg.set_alpha(150)
            n_x = int(px) - name_surf.get_width()//2
            n_y = int(py) + 16
            surface.blit(name_bg, (n_x - 2, n_y - 1))
            surface.blit(name_surf, (n_x, n_y))

            # Stamina bar under name in field
            energy = player.get("energy", 100.0)
            fs_w = 30
            fs_h = 3
            fs_x = int(px) - fs_w // 2
            fs_y = n_y + name_surf.get_height() + 2
            pygame.draw.rect(surface, (20, 20, 20), (fs_x, fs_y, fs_w, fs_h))
            ratio = energy / 100.0
            fs_col = (0, 255, 0) if ratio > 0.6 else (255, 255, 0) if ratio > 0.3 else (255, 0, 0)
            pygame.draw.rect(surface, fs_col, (fs_x, fs_y, int(fs_w * ratio), fs_h))

    def _draw_card(self, surface):
        # Tarjeta de display superior izquierda
        p = self.hovered_player if self.hovered_player else self.starters[self.selected_starter_idx] if self.selected_starter_idx is not None else None
        if not p:
            hint = self.font_text.render("Pasa el mouse sobre un jugador para ver Stats", True, UI_TEXT_DIM)
            surface.blit(hint, (50, 120))
            return
            
        rect = pygame.Rect(50, 80, 320, 320) # Made it taller to fit desc
        pygame.draw.rect(surface, UI_CARD_BG, rect, border_radius=12)
        pygame.draw.rect(surface, self._get_player_color(p["pos"]), rect, 2, border_radius=12)
        
        name = self.font_card_name.render(p["name"], True, UI_TEXT)
        surface.blit(name, (65, 90))
        
        ovr = self.font_card_ovr.render(str(p["ovr"]), True, UI_ACCENT_ALT)
        surface.blit(ovr, (rect.right - 60, 90))
        
        # Position label
        ps = self.font_btn.render(p["pos"], True, self._get_player_color(p["pos"]))
        surface.blit(ps, (65, 125))

        # Descripcion de posicion (Nuevo)
        desc_text = get_pos_desc(p["pos"])
        words = desc_text.split()
        lines = []
        cur = ""
        for w in words:
            if len(cur + w) < 30: cur += w + " "
            else:
                lines.append(cur)
                cur = w + " "
        lines.append(cur)
        
        dy = 160
        for l in lines:
            ls = self.font_text.render(l, True, UI_TEXT_DIM)
            surface.blit(ls, (65, dy))
            dy += 20

        # Stamina Card Info
        energy = p.get("energy", 100.0)
        e_txt = self.font_text.render(f"ENERGÍA: {int(energy)}%", True, WHITE if energy > 30 else RED)
        surface.blit(e_txt, (65, 235))
        # Large Stamina Bar
        es_rect = pygame.Rect(165, 240, 120, 10)
        pygame.draw.rect(surface, (20, 20, 20), es_rect, border_radius=5)
        ratio = energy / 100.0
        es_col = (0, 255, 100) if ratio > 0.6 else (255, 220, 0) if ratio > 0.3 else (255, 0, 0)
        pygame.draw.rect(surface, es_col, (es_rect.x, es_rect.y, int(es_rect.width * ratio), es_rect.height), border_radius=5)

        # Botón Designar Capitán
        is_cap = p.get("is_captain", False)
        self.btn_cap_rect.y = 265
        pygame.draw.rect(surface, (40, 150, 80) if not is_cap else (200, 150, 50), self.btn_cap_rect, border_radius=4)
        cap_txt = "CAPITÁN ASIGNADO" if is_cap else "DESIGNAR CAPITÁN"
        cap_surf = self.font_text.render(cap_txt, True, WHITE)
        surface.blit(cap_surf, cap_surf.get_rect(center=self.btn_cap_rect.center))
        
        # Stats bars
        stat_names = ["speed", "shot", "passing", "defense", "gk"]
        labels = ["VEL", "TIR", "PAS", "DEF", "POR"]
        
        for idx, (st, lbl) in enumerate(zip(stat_names, labels)):
            val = p["s"][st]
            sy = 300 + (idx // 2) * 25
            sx = 65 + (idx % 2) * 130
            
            lsc = self.font_text.render(f"{lbl}: {val}", True, UI_TEXT_DIM)
            surface.blit(lsc, (sx, sy))
            
            # Barrita
            pygame.draw.rect(surface, (50, 50, 50), (sx + 50, sy + 5, 60, 8), border_radius=3)
            col = (0, 200, 100) if val >= 80 else (200, 200, 0) if val >= 60 else (200, 50, 50)
            pygame.draw.rect(surface, col, (sx + 50, sy + 5, int((val/100)*60), 8), border_radius=3)
