import pygame
import random
import math
from settings import *
from data.teams import TEAMS

class CareerPlayerSetupScene:
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        self.time = 0
        
        self.step = 0 # 0: Name, 1: Nationality, 2: Position, 3: League, 4: Idol, 5: Review/Sign
        
        # Step 0
        self.player_name = ""
        self.show_legacy_popup = False
        self.legacy_match = None
        
        # Step 1
        self.positions = ["GK", "CB", "LB", "RB", "CM", "CAM", "CDM", "LW", "RW", "ST"]
        self.pos_idx = 9 # Default ST
        
        # Step 2
        self.leagues = ["EN", "ES", "IT", "DE", "FR", "PT", "TR", "BR", "AR", "CO", "US", "JP", "AF"]
        self.league_names = {"EN": "Premier League", "ES": "La Liga", "IT": "Serie A", "DE": "Bundesliga", 
                             "FR": "Ligue 1", "PT": "Primeira Liga", "BR": "Brasileirão", "AR": "Liga Profesional", 
                             "CO": "Liga BetPlay", "US": "MLS", "JP": "J-League", "AF": "African League"}
        self.lg_idx = 0
        
        # Step 3
        self.assigned_team = None
        
        # Step 4 (Idol)
        self.idol_idx = 0
        self.legends = []

        # Appearance Customization (Integrated into Step 5 / Step 6 flow)
        self.skin_idx = 1
        self.hair_style_idx = 0
        self.hair_col_idx = 0
        self.boot_l_idx = 0
        self.boot_r_idx = 1

        try:
            self.font_title = pygame.font.SysFont("Impact", 48)
            self.font_btn = pygame.font.SysFont("Arial", 28, bold=True)
            self.font_text = pygame.font.SysFont("Arial", 18)
            self.font_hint = pygame.font.SysFont("Arial", 14)
            self.font_input = pygame.font.SysFont("Consolas", 32, bold=True)
            self.font_icon = pygame.font.SysFont("Segoe UI Emoji", 42)
        except:
            self.font_title = pygame.font.Font(None, 48)
            self.font_btn = pygame.font.Font(None, 28)
            self.font_text = pygame.font.Font(None, 18)
            self.font_hint = pygame.font.Font(None, 14)
            self.font_input = pygame.font.Font(None, 32)
            self.font_icon = pygame.font.Font(None, 42)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if getattr(self, 'show_legacy_popup', False):
                    if event.key == pygame.K_y or event.key == pygame.K_s or event.key == pygame.K_RETURN:
                        from data.career_manager import career_manager
                        career_manager.start_year_offset = 30
                        self.show_legacy_popup = False
                        self.step = 1
                    elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                        from data.career_manager import career_manager
                        career_manager.start_year_offset = 0
                        self.show_legacy_popup = False
                        self.step = 1
                    continue
                if self.step == 0:
                    self._handle_step0(event)
                elif self.step == 1:
                    self._handle_step_nat(event)
                elif self.step == 2:
                    self._handle_step_pos(event)
                elif self.step == 3:
                    self._handle_step_league(event)
                elif self.step == 4:
                    self._handle_step_diff(event)
                elif self.step == 5:
                    self._handle_step_idol(event)
                elif self.step == 6:
                    self._handle_step_appearance(event)
                elif self.step == 7:
                    self._handle_step_confirm(event)

    def _handle_step0(self, event):
        from data.career_manager import career_manager
        if event.key == pygame.K_RETURN and len(self.player_name) > 0:
            match = career_manager.check_legacy_match(self.player_name)
            if match:
                self.legacy_match = match
                self.show_legacy_popup = True
            else:
                self.step = 1
        elif event.key == pygame.K_BACKSPACE:
            self.player_name = self.player_name[:-1]
        elif event.key == pygame.K_ESCAPE:
            from scenes.mode_select import ModeSelectScene
            self.manager.set_scene(ModeSelectScene)
        else:
            ch = event.unicode
            if ch.isprintable() and len(self.player_name) < 20:
                self.player_name += ch

    COUNTRIES = [
        "AR", "DE", "BR", "CO", "ES", "FR", "IT", "EN", "PT", "UY", 
        "NL", "BE", "HR", "MA", "MX", "US", "CL", "EC", "PY", "JP", 
        "CH", "DK", "NO", "SE", "PL", "UA", "GR", "TR", "SC", "WA", 
        "PE", "VE", "BO", "KR", "AU", "SN", "EG", "NG", "CM", "CA"
    ]
    COUNTRY_NAMES = {
        "AR": "Argentina", "DE": "Alemania", "BR": "Brasil", "CO": "Colombia",
        "ES": "España", "FR": "Francia", "IT": "Italia", "EN": "Inglaterra", 
        "PT": "Portugal", "UY": "Uruguay", "NL": "Países Bajos", "BE": "Bélgica",
        "HR": "Croacia", "MA": "Marruecos", "MX": "México", "US": "Estados Unidos",
        "CL": "Chile", "EC": "Ecuador", "PY": "Paraguay", "JP": "Japón",
        "CH": "Suiza", "DK": "Dinamarca", "NO": "Noruega", "SE": "Suecia",
        "PL": "Polonia", "UA": "Ucrania", "GR": "Grecia", "TR": "Turquía",
        "SC": "Escocia", "WA": "Gales", "PE": "Perú", "VE": "Venezuela",
        "BO": "Bolivia", "KR": "Corea del Sur", "AU": "Australia", "SN": "Senegal",
        "EG": "Egipto", "NG": "Nigeria", "CM": "Camerún", "CA": "Canadá"
    }

    def _handle_step_nat(self, event):
        if not hasattr(self, 'nat_idx'): self.nat_idx = 0
        if event.key in (pygame.K_LEFT, pygame.K_a):
            self.nat_idx = (self.nat_idx - 1) % len(self.COUNTRIES)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.nat_idx = (self.nat_idx + 1) % len(self.COUNTRIES)
        elif event.key == pygame.K_RETURN:
            self.step = 2
        elif event.key == pygame.K_ESCAPE:
            self.step = 0

    def _handle_step_pos(self, event):
        if event.key in (pygame.K_LEFT, pygame.K_a):
            self.pos_idx = (self.pos_idx - 1) % len(self.positions)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.pos_idx = (self.pos_idx + 1) % len(self.positions)
        elif event.key == pygame.K_RETURN:
            self.step = 3
        elif event.key == pygame.K_ESCAPE:
            self.step = 1

    def _handle_step_league(self, event):
        if event.key in (pygame.K_LEFT, pygame.K_a):
            self.lg_idx = (self.lg_idx - 1) % len(self.leagues)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.lg_idx = (self.lg_idx + 1) % len(self.leagues)
        elif event.key == pygame.K_RETURN:
            self.step = 4
        elif event.key == pygame.K_ESCAPE:
            self.step = 2

    def _handle_step_diff(self, event):
        if not hasattr(self, 'diff_idx'): self.diff_idx = 2
        if event.key in (pygame.K_LEFT, pygame.K_a):
            self.diff_idx = (self.diff_idx - 1) % len(DIFFICULTY_NAMES)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.diff_idx = (self.diff_idx + 1) % len(DIFFICULTY_NAMES)
        elif event.key == pygame.K_RETURN:
            self._setup_legends()
            self.step = 5
        elif event.key == pygame.K_ESCAPE:
            self.step = 3
            
    def _setup_legends(self):
        from server.legends_database import LEGENDS_BASE
        # Filtrar para asegurar que solo son leyendas base (sin etiquetas de evento y con nombres limpios)
        all_legends = [l for l in LEGENDS_BASE if "card_type" not in l and "(" not in l["name"]]
        
        # Sort to recommend based on position and nationality
        pos = self.positions[self.pos_idx]
        nat = self.COUNTRIES[getattr(self, 'nat_idx', 0)]
        
        def legend_score(l):
            score = 0
            if l.get("pos") == pos: score += 10
            if l.get("nat") == nat: score += 5
            return score
            
        self.idol_idx = 0

    def _handle_step_idol(self, event):
        if event.key in (pygame.K_LEFT, pygame.K_a):
            self.idol_idx = (self.idol_idx - 1) % len(self.legends)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.idol_idx = (self.idol_idx + 1) % len(self.legends)
        elif event.key == pygame.K_RETURN:
            if not hasattr(self, 'app_option'): self.app_option = 0
            self.step = 6
        elif event.key == pygame.K_ESCAPE:
            self.step = 4

    def _handle_step_appearance(self, event):
        if not hasattr(self, 'app_option'): self.app_option = 0
        from entities.player_appearance import SKIN_PALETTE, HAIR_COLOR_PALETTE, BOOT_PALETTE

        if event.key in (pygame.K_UP, pygame.K_w):
            self.app_option = (self.app_option - 1) % 5
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.app_option = (self.app_option + 1) % 5
        elif event.key in (pygame.K_LEFT, pygame.K_a):
            if self.app_option == 0: self.skin_idx = (self.skin_idx - 1) % len(SKIN_PALETTE)
            elif self.app_option == 1: self.hair_style_idx = (self.hair_style_idx - 1) % 8
            elif self.app_option == 2: self.hair_col_idx = (self.hair_col_idx - 1) % len(HAIR_COLOR_PALETTE)
            elif self.app_option == 3: self.boot_l_idx = (self.boot_l_idx - 1) % len(BOOT_PALETTE)
            elif self.app_option == 4: self.boot_r_idx = (self.boot_r_idx - 1) % len(BOOT_PALETTE)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            if self.app_option == 0: self.skin_idx = (self.skin_idx + 1) % len(SKIN_PALETTE)
            elif self.app_option == 1: self.hair_style_idx = (self.hair_style_idx + 1) % 8
            elif self.app_option == 2: self.hair_col_idx = (self.hair_col_idx + 1) % len(HAIR_COLOR_PALETTE)
            elif self.app_option == 3: self.boot_l_idx = (self.boot_l_idx + 1) % len(BOOT_PALETTE)
            elif self.app_option == 4: self.boot_r_idx = (self.boot_r_idx + 1) % len(BOOT_PALETTE)
        elif event.key == pygame.K_RETURN:
            self._pre_assign_team()
            self.step = 7
        elif event.key == pygame.K_ESCAPE:
            self.step = 5

    def _handle_step_confirm(self, event):
        if event.key == pygame.K_RETURN:
            self._start_career()
        elif event.key == pygame.K_ESCAPE:
            self.step = 6

    def _pre_assign_team(self):
        # Temp assign for preview
        lg = self.leagues[self.lg_idx]
        from data.career_manager import career_manager
        lg_teams = [t for t in TEAMS if t.get("league") == lg]
        if not lg_teams: lg_teams = TEAMS[:10]
        self.assigned_team = random.choice(lg_teams)

    def _get_custom_appearance_dict(self):
        from entities.player_appearance import SKIN_PALETTE, HAIR_COLOR_PALETTE, BOOT_PALETTE
        skin_color = SKIN_PALETTE[self.skin_idx]
        skin_shadow = (max(0, skin_color[0]-40), max(0, skin_color[1]-35), max(0, skin_color[2]-30))
        hair_color = HAIR_COLOR_PALETTE[self.hair_col_idx]
        boot_color_l = BOOT_PALETTE[self.boot_l_idx]
        boot_color_r = BOOT_PALETTE[self.boot_r_idx]
        return {
            "skin_color": skin_color,
            "skin_shadow": skin_shadow,
            "hair_color": hair_color,
            "hair_style": self.hair_style_idx,
            "boot_color_l": boot_color_l,
            "boot_color_r": boot_color_r,
            "has_beard": (self.hair_style_idx % 2 == 1),
            "has_headband": (self.hair_style_idx == 3)
        }

    def _start_career(self):
        from data.career_manager import career_manager
        
        # Create player data (Starting lower as requested)
        ovr = random.randint(54, 59)
        stats = {"speed": 50, "shot": 50, "passing": 50, "dribbling": 48, "defense": 50, "physical": 50, "gk": 10}
        pos = self.positions[self.pos_idx]
        if pos == "ST": stats["shot"] = 64; stats["speed"] = 62; stats["dribbling"] = 58; stats["physical"] = 55
        elif pos == "GK": stats["gk"] = 64; stats["speed"] = 40; stats["dribbling"] = 30; stats["physical"] = 52
        elif pos in ["CB", "LB", "RB"]: stats["defense"] = 64; stats["speed"] = 58; stats["physical"] = 60; stats["dribbling"] = 42
        elif pos in ["LW", "RW"]: stats["speed"] = 64; stats["dribbling"] = 62; stats["shot"] = 56; stats["physical"] = 48
        elif pos in ["CM", "CAM"]: stats["passing"] = 64; stats["speed"] = 60; stats["dribbling"] = 58; stats["physical"] = 52
        elif pos == "CDM": stats["passing"] = 60; stats["defense"] = 62; stats["physical"] = 58; stats["dribbling"] = 50
        else: stats["passing"] = 64; stats["speed"] = 60; stats["dribbling"] = 55; stats["physical"] = 52

        player_data = {
            "name": self.player_name,
            "pos": pos,
            "age": 17,
            "ovr": ovr,
            "pot": ovr + 25, # High potential for growth
            "num": random.randint(10, 40),
            "nat": self.COUNTRIES[getattr(self, 'nat_idx', 0)],
            "s": stats,
            "idol": self.legends[self.idol_idx]["name"] if self.legends else "Nadie",
            "custom_appearance": self._get_custom_appearance_dict()
        }
        
        career_manager.start_player_career(player_data, self.leagues[self.lg_idx], self.assigned_team["short"])
        career_manager.nationality = self.COUNTRIES[getattr(self, 'nat_idx', 0)]
        diff_name = DIFFICULTY_NAMES[getattr(self, 'diff_idx', 2)]
        career_manager.difficulty = DIFFICULTY_PRESETS[diff_name]["level"]
        
        from scenes.career_hub import CareerHubScene
        t_ovr = career_manager.get_team_ovr(self.assigned_team["short"])
        is_star = (player_data.get("ovr", 70) >= 80 or t_ovr >= 78)
        
        if is_star:
            from scenes.stadium_presentation import StadiumPresentationScene
            target_scene = StadiumPresentationScene
            target_context = {
                "team": self.assigned_team,
                "player_name": self.player_name,
                "number": player_data["num"],
                "next_scene": CareerHubScene
            }
        else:
            from scenes.presentation import PresentationScene
            target_scene = PresentationScene
            target_context = {
                "team": self.assigned_team,
                "player_name": self.player_name,
                "is_manager": False,
                "number": player_data["num"],
                "next_scene": CareerHubScene
            }
            
        from scenes.career_change_number import CareerChangeNumberScene
        self.manager.set_scene(CareerChangeNumberScene, context={
            "next_scene": target_scene,
            "next_context": target_context,
            "is_star": is_star
        })

    def update(self, dt):
        self.time += dt

    def draw(self, surface):
        # Background gradient
        for y in range(HEIGHT):
            r, g, b = 10 + y//50, 20 + y//60, 40 + y//40
            pygame.draw.line(surface, (r,g,b), (0,y), (WIDTH,y))
            
        title = self.font_title.render("NUEVA CARRERA DE JUGADOR", True, UI_ACCENT)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 40))

        if self.step == 0:
            lbl = self.font_btn.render("Nombre del Jugador:", True, WHITE)
            surface.blit(lbl, (WIDTH//2 - lbl.get_width()//2, 250))
            
            w = 400
            rect = pygame.Rect(WIDTH//2 - w//2, 300, w, 60)
            pygame.draw.rect(surface, (20, 25, 40), rect, border_radius=8)
            pygame.draw.rect(surface, UI_ACCENT, rect, 2, border_radius=8)
            
            cursor = "_" if int(self.time * 2) % 2 == 0 else ""
            txt = self.font_input.render(self.player_name + cursor, True, WHITE)
            surface.blit(txt, (rect.left + 20, rect.centery - txt.get_height()//2))

        elif self.step == 1:
            lbl = self.font_btn.render("Nacionalidad del Jugador:", True, WHITE)
            surface.blit(lbl, (WIDTH//2 - lbl.get_width()//2, 250))
            
            nat_code = self.COUNTRIES[getattr(self, 'nat_idx', 0)]
            nat_name = self.COUNTRY_NAMES.get(nat_code, nat_code)
            ns = self.font_title.render(nat_name, True, UI_ACCENT_ALT)
            surface.blit(ns, (WIDTH//2 - ns.get_width()//2, 320))
            
            nav = self.font_btn.render("◀  ▶", True, WHITE)
            surface.blit(nav, (WIDTH//2 - nav.get_width()//2, 400))

        elif self.step == 2:
            lbl = self.font_btn.render("Posición Preferida:", True, WHITE)
            surface.blit(lbl, (WIDTH//2 - lbl.get_width()//2, 220))
            
            pos = self.positions[self.pos_idx]
            ps = self.font_title.render(pos, True, UI_ACCENT_ALT)
            surface.blit(ps, (WIDTH//2 - ps.get_width()//2, 280))

        elif self.step == 3:
            lbl = self.font_btn.render("Liga para empezar:", True, WHITE)
            surface.blit(lbl, (WIDTH//2 - lbl.get_width()//2, 220))
            
            lg = self.leagues[self.lg_idx]
            ln = self.league_names.get(lg, lg)
            ls = self.font_title.render(ln, True, UI_ACCENT_ALT)
            surface.blit(ls, (WIDTH//2 - ls.get_width()//2, 280))

        elif self.step == 4:
            lbl = self.font_btn.render("Dificultad de la Carrera:", True, WHITE)
            surface.blit(lbl, (WIDTH//2 - lbl.get_width()//2, 230))
            
            diff_name = DIFFICULTY_NAMES[getattr(self, 'diff_idx', 2)]
            preset = DIFFICULTY_PRESETS[diff_name]
            
            ns = self.font_title.render(diff_name, True, UI_ACCENT_ALT)
            surface.blit(ns, (WIDTH//2 - ns.get_width()//2, 300))
            
            desc_text = preset["desc"]
            ds = self.font_text.render(desc_text, True, UI_TEXT_DIM)
            surface.blit(ds, (WIDTH//2 - ds.get_width()//2, 370))
            
            nav = self.font_btn.render("◀  ▶", True, WHITE)
            surface.blit(nav, (WIDTH//2 - nav.get_width()//2, 430))

        elif self.step == 5:
            lbl = self.font_btn.render("Elige a tu Ídolo Personal:", True, WHITE)
            surface.blit(lbl, (WIDTH//2 - lbl.get_width()//2, 180))
            
            if self.legends:
                idol = self.legends[self.idol_idx]
                pygame.draw.rect(surface, (30, 40, 60), (WIDTH//2 - 200, 240, 400, 160), border_radius=15)
                
                name_s = self.font_btn.render(idol["name"], True, GOLD)
                surface.blit(name_s, (WIDTH//2 - name_s.get_width()//2, 260))
                
                info = f"{idol['pos']} | {idol['nat']} | OVR: {idol['pot']}"
                info_s = self.font_text.render(info, True, WHITE)
                surface.blit(info_s, (WIDTH//2 - info_s.get_width()//2, 310))
                
                hint = "Este ídolo influirá en tu estilo y narrativa inicial."
                hint_s = self.font_hint.render(hint, True, (150, 150, 150))
                surface.blit(hint_s, (WIDTH//2 - hint_s.get_width()//2, 360))

        elif self.step == 6:
            lbl = self.font_btn.render("Personaliza la Apariencia de tu Jugador:", True, WHITE)
            surface.blit(lbl, (WIDTH//2 - lbl.get_width()//2, 120))

            from entities.player_appearance import draw_player_avatar, SKIN_PALETTE, HAIR_COLOR_PALETTE, BOOT_PALETTE
            app_dict = self._get_custom_appearance_dict()

            # Render Avatar Card Preview
            avatar_card = pygame.Rect(WIDTH//2 - 320, 180, 220, 280)
            pygame.draw.rect(surface, (25, 35, 55), avatar_card, border_radius=15)
            pygame.draw.rect(surface, UI_ACCENT, avatar_card, 2, border_radius=15)
            draw_player_avatar(surface, avatar_card.centerx, avatar_card.centery - 10, app_dict, scale=3.2, team_color=(0, 200, 150), number="10")

            # Customization Options List
            opt_labels = [
                f"Tono de Piel: {self.skin_idx + 1}/{len(SKIN_PALETTE)}",
                f"Estilo de Cabello: Estilo {self.hair_style_idx + 1}/8",
                f"Color de Cabello: Color {self.hair_col_idx + 1}/{len(HAIR_COLOR_PALETTE)}",
                f"Bota Izquierda: Color {self.boot_l_idx + 1}/{len(BOOT_PALETTE)}",
                f"Bota Derecha: Color {self.boot_r_idx + 1}/{len(BOOT_PALETTE)}"
            ]

            start_y = 190
            for i, opt in enumerate(opt_labels):
                is_sel = (getattr(self, 'app_option', 0) == i)
                rect = pygame.Rect(WIDTH//2 - 70, start_y + i * 52, 380, 44)
                bg_col = (45, 60, 90) if is_sel else (30, 38, 55)
                border_col = GOLD if is_sel else (60, 70, 95)
                pygame.draw.rect(surface, bg_col, rect, border_radius=8)
                pygame.draw.rect(surface, border_col, rect, 2 if is_sel else 1, border_radius=8)

                txt_col = WHITE if is_sel else UI_TEXT_DIM
                ts = self.font_text.render(opt, True, txt_col)
                surface.blit(ts, (rect.left + 15, rect.centery - ts.get_height()//2))

                nav_ts = self.font_hint.render("◀  ▶", True, GOLD if is_sel else (100, 100, 120))
                surface.blit(nav_ts, (rect.right - nav_ts.get_width() - 15, rect.centery - nav_ts.get_height()//2))

        elif self.step == 7:
            lbl = self.font_btn.render("¿Todo listo para firmar?", True, WHITE)
            surface.blit(lbl, (WIDTH//2 - lbl.get_width()//2, 120))

            from entities.player_appearance import draw_player_avatar
            app_dict = self._get_custom_appearance_dict()

            # Review Card with Avatar preview
            card = pygame.Rect(WIDTH//2 - 280, 170, 560, 290)
            pygame.draw.rect(surface, (25, 30, 50), card, border_radius=20)
            pygame.draw.rect(surface, UI_ACCENT, card, 3, border_radius=20)

            # Left Avatar display
            avatar_x = card.left + 100
            draw_player_avatar(surface, avatar_x, card.centery - 10, app_dict, scale=3.0, team_color=(0, 200, 150), number="10")

            # Right Player Info
            p_name = self.font_btn.render(self.player_name, True, WHITE)
            surface.blit(p_name, (card.left + 220, card.top + 25))

            details = [
                f"Nacionalidad: {self.COUNTRY_NAMES.get(self.COUNTRIES[getattr(self, 'nat_idx', 0)], '')}",
                f"Equipo: {self.assigned_team['name'] if self.assigned_team else '---'}",
                f"Posición: {self.positions[self.pos_idx]}",
                f"Ídolo: {self.legends[self.idol_idx]['name'] if self.legends else 'Nadie'}",
                f"Dificultad: {DIFFICULTY_NAMES[getattr(self, 'diff_idx', 2)]}"
            ]

            for i, d in enumerate(details):
                ds = self.font_text.render(d, True, (200, 200, 200))
                surface.blit(ds, (card.left + 220, card.top + 75 + i * 35))

        # Footer hints
        hint = "ENTER para continuar | ESC para volver"
        hs = self.font_hint.render(hint, True, (120, 120, 120))
        surface.blit(hs, (WIDTH//2 - hs.get_width()//2, HEIGHT - 50))
        
        # Legacy Popup Overlay
        if getattr(self, 'show_legacy_popup', False):
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((5, 10, 20, 230))
            surface.blit(overlay, (0, 0))
            
            box = pygame.Rect(WIDTH//2 - 320, HEIGHT//2 - 200, 640, 400)
            pygame.draw.rect(surface, (20, 30, 50), box, border_radius=15)
            pygame.draw.rect(surface, UI_ACCENT, box, 3, border_radius=15)
            
            icon_y = box.top + 40
            pygame.draw.circle(surface, (0, 200, 150), (WIDTH//2, icon_y), 30)
            
            icon_t = self.font_btn.render("★", True, (255, 215, 0))
            surface.blit(icon_t, (WIDTH//2 - icon_t.get_width()//2, icon_y - icon_t.get_height()//2))
            
            lbl_title = self.font_title.render("¿CARRERA DE LEGADO?", True, UI_ACCENT)
            surface.blit(lbl_title, (WIDTH//2 - lbl_title.get_width()//2, box.top + 90))
            
            surname = self.player_name.strip().split()[-1].upper() if self.player_name else "N/A"
            desc_lines = [
                f"Hemos detectado un pariente en tu base de datos:",
                f"\"{self.legacy_match['name']}\" ({self.legacy_match['team']}, Año {self.legacy_match['year']})",
                "",
                "¿Deseas iniciar una CARRERA GENERACIONAL?",
                "Si aceptas, el tiempo avanzará 30 años (Año 2054).",
                "Todos los planteles se renovarán con nuevas promesas,",
                f"¡pero el legado de los {surname} continuará!",
            ]
            
            for idx, line in enumerate(desc_lines):
                color = GOLD if "CARRERA" in line or "30" in line else (WHITE if "pariente" in line or "\"" in line else UI_TEXT_DIM)
                txt = self.font_text.render(line, True, color)
                surface.blit(txt, (WIDTH//2 - txt.get_width()//2, box.top + 160 + idx * 25))
                
            btn_y = box.bottom - 60
            pulse = (math.sin(self.time * 4) + 1) / 2
            pulse_color = (int(0 + pulse * 100), int(200 + pulse * 55), int(150 + pulse * 105))
            hint_lbl = self.font_text.render("PULSA [ENTER] PARA LEVANTAR EL LEGADO  o  [ESC] PARA CARRERA TRADICIONAL", True, pulse_color)
            surface.blit(hint_lbl, (WIDTH//2 - hint_lbl.get_width()//2, btn_y))
