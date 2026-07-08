import pygame
import math
from settings import *
from data.teams import TEAMS

class CareerSetupScene:
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        self.time = 0
        
        self.step = 0 # 0: Type, 1: Name, 2: Nationality, 3: League, 4: Team
        
        # Step 0
        from data.career_manager import career_manager
        self.modes = [
            {"id": "manager", "name": "NUEVA CARRERA MÁNAGER", "desc": "Toma las riendas del club, haz fichajes y sube promesas.", "avail": True},
            {"id": "manager_load", "name": "CARGAR MÁNAGER", "desc": "Continuar con tu última partida guardada de Mánager.", "avail": career_manager.has_any_save()},
            {"id": "player", "name": "NUEVA CARRERA JUGADOR", "desc": "Crea o elige un jugador y guiálo hasta la gloria.", "avail": True},
            {"id": "player_load", "name": "CARGAR JUGADOR", "desc": "Continuar con tu última partida guardada de Jugador.", "avail": career_manager.has_any_save()},
            {"id": "settings", "name": "AJUSTES", "desc": "Activa o desactiva opciones globales como el Autoguardado.", "avail": True}
        ]
        self.mode_idx = 0
        self.show_legacy_popup = False
        self.legacy_match = None
        
        # Step 1
        self.mgr_name = ""
        self.text_active = True
        
        # Step 2 & 3 (Leverage existing Team Viewer logic somewhat, but built-in)
        self.leagues = ["EN", "ES", "IT", "DE", "FR", "PT", "TR", "BR", "AR", "CO", "US", "JP", "AF", "NT"]
        self.league_names = {"EN": "Premier League", "ES": "La Liga", "IT": "Serie A", "DE": "Bundesliga", 
                             "FR": "Ligue 1", "PT": "Primeira Liga", "BR": "Brasileirão", "AR": "Liga Profesional", 
                             "CO": "Liga BetPlay", "US": "MLS", "JP": "J-League", "AF": "African League", "NT": "Internacional (Selecciones)"}
        self.lg_idx = 0
        
        self.filtered_teams = []
        self.team_idx = 0
        self.nat_idx = 0
        
        try:
            self.font_title = pygame.font.SysFont("Impact", 48)
            self.font_btn = pygame.font.SysFont("Arial", 28, bold=True)
            self.font_text = pygame.font.SysFont("Arial", 18)
            self.font_hint = pygame.font.SysFont("Arial", 14)
            self.font_input = pygame.font.SysFont("Consolas", 32, bold=True)
        except:
            self.font_title = pygame.font.Font(None, 48)
            self.font_btn = pygame.font.Font(None, 28)
            self.font_text = pygame.font.Font(None, 18)
            self.font_hint = pygame.font.Font(None, 14)
            self.font_input = pygame.font.Font(None, 32)
            


    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if getattr(self, 'show_legacy_popup', False):
                    if event.key == pygame.K_y or event.key == pygame.K_s or event.key == pygame.K_RETURN:
                        from data.career_manager import career_manager
                        career_manager.start_year_offset = 30
                        self.show_legacy_popup = False
                        self.step = 2
                    elif event.key == pygame.K_n or event.key == pygame.K_ESCAPE:
                        from data.career_manager import career_manager
                        career_manager.start_year_offset = 0
                        self.show_legacy_popup = False
                        self.step = 2
                    continue
                if self.step == 0:
                    self._handle_step0(event)
                elif self.step == 1:
                    self._handle_step1(event)
                elif self.step == 2:
                    self._handle_step_nationality(event)
                elif self.step == 3:
                    self._handle_step_league(event)
                elif self.step == 4:
                    self._handle_step_difficulty(event)
                elif self.step == 5:
                    self._handle_step_team(event)

    def _handle_step0(self, event):
        from data.career_manager import career_manager
        if event.key in (pygame.K_UP, pygame.K_w):
            self.mode_idx = (self.mode_idx - 1) % len(self.modes)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.mode_idx = (self.mode_idx + 1) % len(self.modes)
        elif event.key == pygame.K_RETURN:
            m = self.modes[self.mode_idx]
            if m["avail"]:
                if m["id"] == "manager_load":
                    from scenes.career_slots import CareerSlotsScene
                    self.manager.set_scene(CareerSlotsScene, context={"slot_mode": "load", "career_type": "manager"})
                elif m["id"] == "player_load":
                    from scenes.career_slots import CareerSlotsScene
                    self.manager.set_scene(CareerSlotsScene, context={"slot_mode": "load", "career_type": "player"})
                elif m["id"] == "player":
                    from scenes.career_player_setup import CareerPlayerSetupScene
                    self.manager.set_scene(CareerPlayerSetupScene)
                elif m["id"] == "settings":
                    career_manager.autosave_enabled = not getattr(career_manager, 'autosave_enabled', True)
                    career_manager.save_config()
                else:
                    self.step = 1
        elif event.key == pygame.K_ESCAPE:
            from scenes.mode_select import ModeSelectScene
            self.manager.set_scene(ModeSelectScene)

    # --- Nacionalidad (nuevo paso) ---
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

    def _handle_step1(self, event):
        from data.career_manager import career_manager
        if event.key == pygame.K_RETURN and len(self.mgr_name) > 0:
            match = career_manager.check_legacy_match(self.mgr_name)
            if match:
                self.legacy_match = match
                self.show_legacy_popup = True
            else:
                self.step = 2
        elif event.key == pygame.K_BACKSPACE:
            self.mgr_name = self.mgr_name[:-1]
        elif event.key == pygame.K_ESCAPE:
            self.step = 0
        elif event.key == pygame.K_TAB:
            career_manager.autosave_enabled = not getattr(career_manager, 'autosave_enabled', True)
            career_manager.save_config()
        else:
            ch = event.unicode
            if os.name == 'nt' and ch.isprintable() and len(self.mgr_name) < 20:
                self.mgr_name += ch
            elif ch.isprintable() and len(self.mgr_name) < 20:
                self.mgr_name += ch
                
    def _handle_step_nationality(self, event):
        if not hasattr(self, 'nat_idx'): self.nat_idx = 0
        if event.key in (pygame.K_LEFT, pygame.K_a):
            self.nat_idx = (self.nat_idx - 1) % len(self.COUNTRIES)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.nat_idx = (self.nat_idx + 1) % len(self.COUNTRIES)
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

    def _handle_step_difficulty(self, event):
        if not hasattr(self, 'diff_idx'): self.diff_idx = 2
        if event.key in (pygame.K_LEFT, pygame.K_a):
            self.diff_idx = (self.diff_idx - 1) % len(DIFFICULTY_NAMES)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.diff_idx = (self.diff_idx + 1) % len(DIFFICULTY_NAMES)
        elif event.key == pygame.K_RETURN:
            self._filter_teams()
            self.step = 5
        elif event.key == pygame.K_ESCAPE:
            self.step = 3
            
    def _handle_step_team(self, event):
        if event.key in (pygame.K_LEFT, pygame.K_a):
            self.team_idx = (self.team_idx - 1) % len(self.filtered_teams)
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.team_idx = (self.team_idx + 1) % len(self.filtered_teams)
        elif event.key == pygame.K_RETURN:
            self._start_career()
        elif event.key == pygame.K_ESCAPE:
            self.step = 4
            
    def _filter_teams(self):
        lg = self.leagues[self.lg_idx]
        self.filtered_teams = [t for t in TEAMS if t.get("league") == lg]
        if not self.filtered_teams:
             self.filtered_teams = TEAMS[:] # Fallback
        self.team_idx = 0

    def _start_career(self):
        # Initialize career manager
        from data.career_manager import career_manager
        sel_team = self.filtered_teams[self.team_idx]
        
        career_manager.start_new_career(self.mgr_name, sel_team["short"])
        career_manager.nationality = self.COUNTRIES[getattr(self, 'nat_idx', 0)]
        diff_name = DIFFICULTY_NAMES[getattr(self, 'diff_idx', 2)]
        career_manager.difficulty = DIFFICULTY_PRESETS[diff_name]["level"]
        
        # Presentación Oficial
        from scenes.presentation import PresentationScene
        from scenes.career_hub import CareerHubScene
        self.manager.set_scene(PresentationScene, context={
            "team": sel_team,
            "player_name": self.mgr_name,
            "is_manager": True,
            "next_scene": CareerHubScene
        })

    def update(self, dt):
        self.time += dt

    def draw(self, surface):
        surface.fill((10, 15, 25))
        for y in range(HEIGHT):
            r, g, b = 10 + y//40, 15 + y//60, 25 + y//30
            pygame.draw.line(surface, (r,g,b), (0,y), (WIDTH,y))
            
        title = self.font_title.render("CREAR NUEVA CARRERA", True, UI_ACCENT)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 40))
        
        if self.step == 0:
            from data.career_manager import career_manager
            a_state = "ON" if getattr(career_manager, 'autosave_enabled', True) else "OFF"
            
            for i, m in enumerate(self.modes):
                cy = 150 + i * 110
                rect = pygame.Rect(WIDTH//2 - 250, cy, 500, 90)
                is_sel = (self.mode_idx == i)
                bg = UI_CARD_HOVER if is_sel else UI_CARD_BG
                if not m["avail"]: bg = (30, 30, 35)
                
                pygame.draw.rect(surface, bg, rect, border_radius=12)
                if is_sel:
                    pygame.draw.rect(surface, UI_ACCENT, rect, 3, border_radius=12)
                    
                color = m.get("color", WHITE) if m["avail"] else (100, 100, 100)
                
                # Dynamic text for settings
                disp_name = f"{m['name']} (AUTOSAVE: {a_state})" if m["id"] == "settings" else m["name"]
                
                ns = self.font_btn.render(disp_name + ("" if m["avail"] else " 🔒"), True, color)
                surface.blit(ns, (rect.left + 20, rect.top + 15))
                ds = self.font_text.render(m["desc"], True, UI_TEXT_DIM)
                surface.blit(ds, (rect.left + 20, rect.top + 50))
                
        elif self.step == 1:
            lbl = self.font_btn.render("Nombre del Entrenador:", True, WHITE)
            surface.blit(lbl, (WIDTH//2 - lbl.get_width()//2, 250))
            
            w = 400
            rect = pygame.Rect(WIDTH//2 - w//2, 300, w, 60)
            pygame.draw.rect(surface, (20, 25, 40), rect, border_radius=8)
            pygame.draw.rect(surface, UI_ACCENT, rect, 2, border_radius=8)
            
            cursor = "_" if int(self.time * 2) % 2 == 0 else ""
            txt = self.font_input.render(self.mgr_name + cursor, True, WHITE)
            surface.blit(txt, (rect.left + 20, rect.centery - txt.get_height()//2))
            
        elif self.step == 2:
            lbl = self.font_btn.render("Nacionalidad del Entrenador:", True, WHITE)
            surface.blit(lbl, (WIDTH//2 - lbl.get_width()//2, 250))
            
            nat_code = self.COUNTRIES[self.nat_idx]
            nat_name = self.COUNTRY_NAMES.get(nat_code, nat_code)
            ns = self.font_title.render(nat_name, True, UI_ACCENT_ALT)
            surface.blit(ns, (WIDTH//2 - ns.get_width()//2, 320))
            
            nav = self.font_btn.render("◀ ▶", True, UI_TEXT_DIM)
            surface.blit(nav, (WIDTH//2 - nav.get_width()//2, 400))
            
        elif self.step == 3:
            lbl = self.font_btn.render("Selecciona la Liga:", True, WHITE)
            surface.blit(lbl, (WIDTH//2 - lbl.get_width()//2, 250))
            
            lg = self.leagues[self.lg_idx]
            name = self.league_names.get(lg, lg)
            
            ns = self.font_title.render(name, True, UI_ACCENT_ALT)
            surface.blit(ns, (WIDTH//2 - ns.get_width()//2, 320))
            
            nav = self.font_btn.render("◀ ▶", True, UI_TEXT_DIM)
            surface.blit(nav, (WIDTH//2 - nav.get_width()//2, 400))
            
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
            
            nav = self.font_btn.render("◀ ▶", True, UI_TEXT_DIM)
            surface.blit(nav, (WIDTH//2 - nav.get_width()//2, 430))
            
        elif self.step == 5:
            lbl = self.font_btn.render("Selecciona tu Club:", True, WHITE)
            surface.blit(lbl, (WIDTH//2 - lbl.get_width()//2, 180))
            
            t = self.filtered_teams[self.team_idx]
            from data.teams import draw_badge, draw_uniform_preview
            draw_badge(surface, t, WIDTH//2, 280, size=80)
            
            ns = self.font_title.render(t["name"], True, WHITE)
            surface.blit(ns, (WIDTH//2 - ns.get_width()//2, 380))
            
            nav = self.font_btn.render("◀ ▶", True, UI_TEXT_DIM)
            surface.blit(nav, (WIDTH//2 - nav.get_width()//2, 450))
            
        hint = self.font_hint.render("ENTER Continuar  ·  ESC Volver", True, UI_TEXT_DIM)
        surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 40))
        
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
            
            surname = self.mgr_name.strip().split()[-1].upper() if self.mgr_name else "N/A"
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
