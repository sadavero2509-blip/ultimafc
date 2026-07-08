import pygame
from settings import *
from data.career_manager import career_manager

class CareerSearchScene:
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        
        self.state = "MENU" # MENU, LEAGUES, TEAMS, ROSTER, PLAYER, FILTER, BID
        
        self.leagues = career_manager.leagues + ["LIB"]
        self.selected_league = 0
        
        self.teams_list = []
        self.selected_team = 0
        self.scroll_y = 0
        
        self.roster_list = []
        self.selected_player = 0
        
        self.player_target = None
        self.draft_bid = 0
        self.draft_val = 0
        
        # Filter config
        self.filter_pos = "CUALQUIERA" # O list
        self.filter_age_max = 40
        self.filter_age_min = 15
        self.filter_results = []
        self.filter_sel = 0
        self.filter_scroll = 0
        
        try:
            self.font_title = pygame.font.SysFont("Impact", 36)
            self.font_btn = pygame.font.SysFont("Arial", 22, bold=True)
            self.font_text = pygame.font.SysFont("Arial", 16)
            self.font_bold = pygame.font.SysFont("Arial", 16, bold=True)
            self.font_hint = pygame.font.SysFont("Arial", 14)
        except:
            self.font_title = pygame.font.Font(None, 36)
            self.font_btn = pygame.font.Font(None, 22)
            self.font_text = pygame.font.Font(None, 16)
            self.font_bold = pygame.font.Font(None, 16)
            self.font_hint = pygame.font.Font(None, 14)
            
        self.sub_msg = ""
        self.sub_msg_timer = 0
            
    def _is_scouted(self, p, short):
        return f"{p['name']}_{short}" in career_manager.scouted_players
        
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.state == "MENU":
                    self._handle_menu(event.key)
                elif self.state == "LEAGUES":
                    self._handle_leagues(event.key)
                elif self.state == "TEAMS":
                    self._handle_teams(event.key)
                elif self.state == "ROSTER":
                    self._handle_roster(event.key)
                elif self.state == "PLAYER":
                    self._handle_player(event.key)
                elif self.state == "FILTER":
                    self._handle_filter(event.key)
                elif self.state == "RESULTS":
                    self._handle_results(event.key)
                elif self.state == "BID":
                    self._handle_bid(event.key)

    def _show_msg(self, text):
        self.sub_msg = text
        self.sub_msg_timer = 2.0

    def update(self, dt):
        if self.sub_msg_timer > 0:
            self.sub_msg_timer -= dt

    # --- INPUT HANDLERS ---
    def _handle_menu(self, key):
        if key == pygame.K_UP:
            self.selected_league = max(0, self.selected_league - 1)
        elif key == pygame.K_DOWN:
            self.selected_league = min(1, self.selected_league + 1)
        elif key == pygame.K_RETURN:
            if self.selected_league == 0:
                self.state = "LEAGUES"
                self.selected_league = 0
            else:
                self.state = "FILTER"
                self.filter_pos_list = ["CUALQUIERA", "GK", "DEF", "MED", "DEL"]
                self.filter_pos_idx = 0
        elif key == pygame.K_ESCAPE:
            from scenes.career_market import CareerMarketScene
            self.manager.set_scene(CareerMarketScene)

    def _handle_leagues(self, key):
        if key == pygame.K_UP:
            self.selected_league = max(0, self.selected_league - 1)
        elif key == pygame.K_DOWN:
            self.selected_league = min(len(self.leagues) - 1, self.selected_league + 1)
        elif key == pygame.K_RETURN:
            lg = self.leagues[self.selected_league]
            if lg == "LIB":
                # Special case: only one team in this 'league'
                self.teams_list = [t for t in career_manager.teams if t["short"] == "LIB"]
            else:
                self.teams_list = [t for t in career_manager.teams if t.get("league", "EN") == lg]
            self.selected_team = 0
            self.scroll_y = 0
            self.state = "TEAMS"
        elif key == pygame.K_ESCAPE:
            self.selected_league = 0
            self.state = "MENU"

    def _handle_teams(self, key):
        if key == pygame.K_UP:
            self.selected_team = max(0, self.selected_team - 1)
            if self.selected_team < self.scroll_y: self.scroll_y = self.selected_team
        elif key == pygame.K_DOWN:
            self.selected_team = min(len(self.teams_list) - 1, self.selected_team + 1)
            if self.selected_team >= self.scroll_y + 12: self.scroll_y = self.selected_team - 11
        elif key == pygame.K_RETURN:
            t = self.teams_list[self.selected_team]
            self.roster_list = career_manager.rosters.get(t["short"], [])
            self.selected_player = 0
            self.scroll_y = 0
            self.state = "ROSTER"
        elif key == pygame.K_ESCAPE:
            self.state = "LEAGUES"

    def _handle_roster(self, key):
        if key == pygame.K_UP:
            self.selected_player = max(0, self.selected_player - 1)
            if self.selected_player < self.scroll_y: self.scroll_y = self.selected_player
        elif key == pygame.K_DOWN:
            self.selected_player = min(len(self.roster_list) - 1, self.selected_player + 1)
            if self.selected_player >= self.scroll_y + 12: self.scroll_y = self.selected_player - 11
        elif key == pygame.K_RETURN:
            p = self.roster_list[self.selected_player]
            t = self.teams_list[self.selected_team]
            if t["short"] == career_manager.player_team["short"]:
                self._show_msg("Es jugador de tu propio equipo. Usa 'Mi Plantel'.")
                return
            self.player_target = (p, t)
            self.state = "PLAYER"
        elif key == pygame.K_ESCAPE:
            self.scroll_y = 0
            self.state = "TEAMS"

    def _handle_filter(self, key):
        if key == pygame.K_UP:
            self.filter_pos_idx = (self.filter_pos_idx - 1) % len(self.filter_pos_list)
        elif key == pygame.K_DOWN:
            self.filter_pos_idx = (self.filter_pos_idx + 1) % len(self.filter_pos_list)
        elif key == pygame.K_LEFT:
            self.filter_age_max = max(16, self.filter_age_max - 1)
        elif key == pygame.K_RIGHT:
            self.filter_age_max = min(40, self.filter_age_max + 1)
        elif key == pygame.K_RETURN:
            self._execute_search()
        elif key == pygame.K_ESCAPE:
            self.state = "MENU"
            
    def _execute_search(self):
        self.filter_results = []
        pos_grp = self.filter_pos_list[self.filter_pos_idx]
        
        for t in career_manager.teams:
            if t["short"] == career_manager.player_team["short"]: continue
            for p in career_manager.rosters.get(t["short"], []):
                # Age filter
                if not (self.filter_age_min <= p.get("age", 25) <= self.filter_age_max):
                    continue
                # Pos filter
                match = False
                if pos_grp == "CUALQUIERA": match = True
                elif pos_grp == "GK" and p["pos"] == "GK": match = True
                elif pos_grp == "DEF" and p["pos"] in ["CB", "LB", "RB", "LWB", "RWB"]: match = True
                elif pos_grp == "MED" and p["pos"] in ["CDM", "CM", "CAM", "LM", "RM"]: match = True
                elif pos_grp == "DEL" and p["pos"] in ["LW", "RW", "ST", "CF", "SS"]: match = True
                
                if match:
                    # Note: We append tuple (player, team)
                    self.filter_results.append((p, t))
                    
        self.filter_sel = 0
        self.filter_scroll = 0
        self.state = "RESULTS"

    def _handle_results(self, key):
        if key == pygame.K_UP:
            self.filter_sel = max(0, self.filter_sel - 1)
            if self.filter_sel < self.filter_scroll: self.filter_scroll = self.filter_sel
        elif key == pygame.K_DOWN:
            self.filter_sel = min(len(self.filter_results) - 1, self.filter_sel + 1)
            if self.filter_sel >= self.filter_scroll + 12: self.filter_scroll = self.filter_sel - 11
        elif key == pygame.K_RETURN:
            if not self.filter_results: return
            p, t = self.filter_results[self.filter_sel]
            self.player_target = (p, t)
            self.state = "PLAYER"
        elif key == pygame.K_ESCAPE:
            self.state = "FILTER"

    def _handle_player(self, key):
        if key == pygame.K_ESCAPE:
            if self.filter_results:
                self.state = "RESULTS"
            else:
                self.state = "ROSTER"
        elif key == pygame.K_RETURN:
            # SCOUT
            p, t = self.player_target
            if t["short"] == "LIB" and career_manager.mode != "manager":
                self._show_msg("❌ Solo los entrenadores pueden investigar agentes libres.")
                return
            scouted = self._is_scouted(p, t['short'])
            if not scouted:
                cost = 1 # $1M
                if career_manager.player_team["budget"] >= cost:
                    career_manager.player_team["budget"] -= cost
                    career_manager.scouted_players.append(f"{p['name']}_{t['short']}")
                    self._show_msg("✅ ¡Jugador Investigado Exitosamente!")
                else:
                    self._show_msg("❌ Presupuesto insuficiente para investigar.")
        elif key == pygame.K_SPACE:
            # NEGOTIATE MODAL
            p, t = self.player_target
            if t["short"] == "LIB" and career_manager.mode != "manager":
                self._show_msg("❌ Los agentes libres no aceptan tratos directos de jugadores.")
                return
            # Check if active
            for n in career_manager.negotiations:
                if n["p_name"] == p["name"] and n["t_short"] == t["short"]:
                    self._show_msg(f"⚠️ Ya hay trato activo o rechazado ({n['state']}).")
                    return
            
            try:
                p_ovr = int(p.get("ovr", 70))
            except (ValueError, TypeError):
                p_ovr = 70
            try:
                p_pot = int(p.get("pot", p_ovr))
            except (ValueError, TypeError):
                p_pot = p_ovr
                
            cost_estimation = max(1, (p_ovr - 60) ** 1.8 * 0.15)
            self.draft_val = int(cost_estimation) * (1.3 if p_pot > p_ovr + 5 else 1.0)
            self.draft_bid = int(cost_estimation)
            self.state = "BID"

    def _handle_bid(self, key):
        if key == pygame.K_UP:
            self.draft_bid += 1
        elif key == pygame.K_DOWN:
            self.draft_bid = max(0, self.draft_bid - 1)
        elif key == pygame.K_RIGHT:
            self.draft_bid += 10
        elif key == pygame.K_LEFT:
            self.draft_bid = max(0, self.draft_bid - 10)
        elif key == pygame.K_RETURN:
            # Submit draft
            p, t = self.player_target
            new_neg = {
                "p_name": p["name"],
                "t_short": t["short"],
                "p_obj": p,
                "state": "pending",
                "wait": 2, # wait 2 weeks
                "estimated_value": self.draft_val,
                "bid": self.draft_bid,
                "cooldown": 0
            }
            career_manager.negotiations.append(new_neg)
            self._show_msg("✉️ ¡Oferta enviada al club!")
            self.state = "RESULTS" if self.filter_results else "ROSTER"
        elif key == pygame.K_ESCAPE:
            self.state = "PLAYER"


    # --- DRAW ROUTINES ---
    def draw(self, surface):
        surface.fill((15, 18, 25))
        
        # Header
        title = self.font_title.render("RED GLOBAL DE OJEADORES", True, UI_ACCENT)
        surface.blit(title, (50, 20))
        
        b_lbl = self.font_text.render(f"Presupuesto: ${career_manager.player_team.get('budget', 0)}M", True, (100, 255, 150))
        surface.blit(b_lbl, (WIDTH - 250, 35))
        
        if self.state == "MENU":
            self._draw_menu(surface)
        elif self.state == "LEAGUES":
            self._draw_leagues(surface)
        elif self.state == "TEAMS":
            self._draw_teams(surface)
        elif self.state == "ROSTER":
            self._draw_roster(surface)
        elif self.state == "FILTER":
            self._draw_filter(surface)
        elif self.state == "RESULTS":
            self._draw_results(surface)
        elif self.state == "PLAYER":
            self._draw_player(surface)
        elif self.state == "BID":
            self._draw_player(surface) # Base
            self._draw_bid_modal(surface)
            
        if self.sub_msg_timer > 0:
            ms = self.font_btn.render(self.sub_msg, True, (255, 255, 100))
            surface.blit(ms, (WIDTH//2 - ms.get_width()//2, HEIGHT - 80))

    def _draw_menu(self, surface):
        opts = [("BUSCAR POR LIGAS Y CLUBES", "Navega manualmente por las diferentes divisiones."),
                ("FILTRO MUNDIAL AVANZADO", "Busca perfiles de jugadores específicos en todo el mundo.")]
        
        for i, (name, desc) in enumerate(opts):
            rect = pygame.Rect(100, 150 + i * 100, WIDTH - 200, 80)
            is_sel = (self.selected_league == i)
            
            c = UI_CARD_HOVER if is_sel else UI_CARD_BG
            pygame.draw.rect(surface, c, rect, border_radius=8)
            if is_sel:
                pygame.draw.rect(surface, UI_ACCENT, rect, 2, border_radius=8)
                
            ns = self.font_btn.render(name, True, WHITE)
            surface.blit(ns, (rect.left + 30, rect.top + 15))
            ds = self.font_text.render(desc, True, UI_TEXT_DIM)
            surface.blit(ds, (rect.left + 30, rect.top + 45))

    def _draw_leagues(self, surface):
        y = 100
        for i, lg in enumerate(self.leagues):
            rect = pygame.Rect(50, y + i * 45, 250, 40)
            is_sel = (self.selected_league == i)
            c = UI_CARD_HOVER if is_sel else (30,35,45)
            pygame.draw.rect(surface, c, rect, border_radius=4)
            
            league_names_map = {"EN": "Premier League", "ES": "La Liga", "IT": "Serie A", "DE": "Bundesliga", 
                                "FR": "Ligue 1", "PT": "Primeira Liga", "BR": "Brasileirão", "AR": "Liga Profesional", 
                                "CO": "Liga BetPlay", "US": "MLS", "JP": "J-League", "LIB": "AGENTES LIBRES"}
            lg_name = league_names_map.get(lg, lg)
            
            ls = self.font_btn.render(f"{lg_name}", True, WHITE if is_sel else UI_TEXT_DIM)
            surface.blit(ls, (rect.left + 20, rect.top + 10))
            
        # Draw standings of selected league
        lg = self.leagues[self.selected_league]
        st = list(career_manager.standings.get(lg, {}).items())
        st.sort(key=lambda x: (x[1]["pts"], x[1]["gf"] - x[1]["ga"]), reverse=True)
        
        tl = self.font_title.render(f"TABLA: {lg}", True, WHITE)
        surface.blit(tl, (350, 100))
        
        sy = 150
        for i, (short, data) in enumerate(st[:15]): # top 15
            ss = self.font_text.render(f"{i+1}. {short}", True, WHITE)
            surface.blit(ss, (350, sy))
            ps = self.font_bold.render(f"{data['pts']} Pts", True, (100, 255, 100))
            surface.blit(ps, (600, sy))
            sy += 25

    def _draw_teams(self, surface):
        y = 100
        vis = self.teams_list[self.scroll_y : self.scroll_y + 12]
        lg = self.leagues[self.selected_league]
        tl = self.font_title.render(f"EQUIPOS - {lg}", True, WHITE)
        surface.blit(tl, (50, 60))
        
        for i, t in enumerate(vis):
            idx = self.scroll_y + i
            rect = pygame.Rect(50, y + i * 50, 400, 45)
            is_sel = (self.selected_team == idx)
            c = UI_CARD_HOVER if is_sel else (30,35,45)
            pygame.draw.rect(surface, c, rect, border_radius=4)
            ts = self.font_btn.render(t["name"], True, WHITE if is_sel else UI_TEXT_DIM)
            surface.blit(ts, (rect.left + 20, rect.top + 10))

    def _draw_roster(self, surface):
        t = self.teams_list[self.selected_team]
        self._draw_list_core(surface, self.roster_list, f"PLANTILLA: {t['name']}", self.selected_player, self.scroll_y, t["short"])

    def _draw_filter(self, surface):
        tl = self.font_title.render("FILTRO DE BÚSQUEDA GLOBAL", True, WHITE)
        surface.blit(tl, (50, 100))
        
        ps = self.font_btn.render(f"Posición Principal: < {self.filter_pos_list[self.filter_pos_idx]} >", True, WHITE)
        surface.blit(ps, (100, 180))
        
        ags = self.font_btn.render(f"Edad Máxima: < {self.filter_age_max} >", True, WHITE)
        surface.blit(ags, (100, 240))
        
        hs = self.font_text.render("ENTER: Empezar Búsqueda", True, UI_ACCENT)
        surface.blit(hs, (100, 320))

    def _draw_results(self, surface):
        self._draw_list_core(surface, [r[0] for r in self.filter_results], f"RESULTADOS ({len(self.filter_results)})", self.filter_sel, self.filter_scroll, None, show_club=True)

    def _draw_list_core(self, surface, lst, title, sel_idx, scroll_val, forced_short=None, show_club=False):
        tl = self.font_title.render(title, True, WHITE)
        surface.blit(tl, (50, 60))
        
        vis = lst[scroll_val : scroll_val + 12]
        y = 110
        
        cols = [("POS", 40), ("NOMBRE", 200), ("EDAD", 50), ("OVR", 50), ("POT", 50)]
        if show_club: cols.insert(2, ("CLUB", 80))
        
        cx = 50
        for label, w in cols:
            ls = self.font_bold.render(label, True, UI_ACCENT)
            surface.blit(ls, (cx, y))
            cx += w
            
        y += 30
        
        for i, p in enumerate(vis):
            idx = scroll_val + i
            is_sel = (sel_idx == idx)
            rect = pygame.Rect(45, y - 3, 700, 30)
            
            c_bg = UI_CARD_HOVER if is_sel else (30,35,45)
            pygame.draw.rect(surface, c_bg, rect, border_radius=4)
            if is_sel:
                pygame.draw.rect(surface, UI_ACCENT, rect, 1, border_radius=4)
                
            c_text = WHITE if is_sel else UI_TEXT_DIM
            
            t_short = forced_short
            if show_club:
                t_short = self.filter_results[idx][1]["short"]
                
            scouted = self._is_scouted(p, t_short)
            
            cx = 50
            # POS
            pos_c = (220, 200, 50) if p["pos"] == "GK" else (50, 150, 250) if p["pos"] in ["CB", "LB", "RB"] else (50, 200, 100) if p["pos"] in ["CM", "CDM", "CAM"] else (250, 80, 80)
            pygame.draw.rect(surface, pos_c, (cx, y - 2, 32, 20), border_radius=4)
            ps = self.font_hint.render(p["pos"], True, BLACK)
            surface.blit(ps, (cx + 16 - ps.get_width()//2, y + 1))
            cx += 40
            
            # NOMBRE
            nms = self.font_bold.render(p["name"], True, c_text)
            surface.blit(nms, (cx, y))
            cx += 200
            
            # CLUB
            if show_club:
                cs = self.font_text.render(t_short, True, c_text)
                surface.blit(cs, (cx, y))
                cx += 80
                
            # EDAD
            as_ = self.font_text.render(str(p.get("age", 25)), True, c_text)
            surface.blit(as_, (cx, y))
            cx += 50
            
            # OVR & POT
            ovr_val = str(p.get("ovr", 75)) if scouted else "?"
            pot_val = str(p.get("pot", p.get("ovr", 75))) if scouted else "?"
            
            ovs = self.font_bold.render(ovr_val, True, (255, 215, 0) if scouted else c_text)
            surface.blit(ovs, (cx, y))
            cx += 50
            
            pts = self.font_bold.render(pot_val, True, c_text)
            surface.blit(pts, (cx, y))
            
            y += 35

    def _draw_player(self, surface):
        p, t = self.player_target
        scouted = self._is_scouted(p, t['short'])
        
        rect = pygame.Rect(100, 100, WIDTH - 200, 400)
        pygame.draw.rect(surface, UI_CARD_BG, rect, border_radius=12)
        pygame.draw.rect(surface, UI_ACCENT, rect, 2, border_radius=12)
        
        ns = self.font_title.render(p["name"], True, WHITE)
        surface.blit(ns, (130, 130))
        
        ds = self.font_text.render(f"🛡️ Club: {t['name']} ({t['short']})  |  ⚽ POS: {p['pos']}  |  🎂 EDAD: {p.get('age', 25)}", True, UI_TEXT_DIM)
        surface.blit(ds, (130, 170))
        
        if scouted:
            vs = self.font_title.render(f"OVR: {p.get('ovr', 70)}", True, (100, 255, 100))
            surface.blit(vs, (130, 220))
            ps = self.font_btn.render(f"POT: {p.get('pot', 70)}", True, (0, 200, 255))
            surface.blit(ps, (280, 230))
            
            sy = 280
            for k, v in p.get("s", {}).items():
                ss = self.font_text.render(f"📊 {k.upper()}: {v}", True, WHITE)
                surface.blit(ss, (130, sy))
                sy += 25
                
            msg = "🤝 SPACE: Enviar Oferta Inicial (Automática)  |  ESC: Volver"
        else:
            vs = self.font_title.render("OVR: ?", True, UI_TEXT_DIM)
            surface.blit(vs, (130, 220))
            ps = self.font_btn.render("POT: ?", True, UI_TEXT_DIM)
            surface.blit(ps, (280, 230))
            
            ws = self.font_text.render(f"Estadísticas bloqueadas. Fog of War activo.", True, (255, 100, 100))
            surface.blit(ws, (130, 280))
            
            msg = "🔍 ENTER: Pagar $1M para Investigar  |  SPACE: Negociar a Ciegas  |  ESC: Volver"
        
        if t["short"] == "LIB":
            if career_manager.mode == "manager":
                msg = "🤝 SPACE: Negociar Fichaje (Agente Libre)  |  ESC: Volver"
            else:
                msg = "🛡️ CLUB LIBRE: Solo lectura (No negociable)  |  ESC: Volver"
            
        ms = self.font_hint.render(msg, True, WHITE)
        surface.blit(ms, (130, 450))

    def _draw_bid_modal(self, surface):
        m_w, m_h = 400, 250
        rect = pygame.Rect(WIDTH//2 - m_w//2, HEIGHT//2 - m_h//2, m_w, m_h)
        pygame.draw.rect(surface, (30, 35, 45), rect, border_radius=12)
        pygame.draw.rect(surface, UI_ACCENT, rect, 3, border_radius=12)
        
        ns = self.font_btn.render("Redactar Oferta Final", True, WHITE)
        surface.blit(ns, (rect.left + 20, rect.top + 20))
        
        vs = self.font_text.render("Al enviar, deberás esperar 2 semanas por respuesta", True, UI_TEXT_DIM)
        surface.blit(vs, (rect.left + 20, rect.top + 60))
        
        # Bid input
        bs = self.font_title.render(f"${self.draft_bid}M", True, (100, 255, 100))
        surface.blit(bs, (rect.centerx - bs.get_width()//2, rect.top + 100))
        
        hs = self.font_hint.render("↑/↓: +/- 1M  |  ←/→: +/- 10M", True, UI_TEXT_DIM)
        surface.blit(hs, (rect.centerx - hs.get_width()//2, rect.top + 160))
        
        hs2 = self.font_btn.render("ENTER: Enviar Fax  |  ESC: Cancelar", True, WHITE)
        surface.blit(hs2, (rect.centerx - hs2.get_width()//2, rect.top + 200))
