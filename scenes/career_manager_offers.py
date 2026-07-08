import pygame
from settings import *
from data.career_manager import career_manager

class CareerManagerOffersScene:
    """View incoming offers and outgoing applications for manager team changes."""
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        
        self.tab_idx = 0  # 0=Incoming offers, 1=My applications, 2=Apply to team
        self.sel = 0
        self.scroll_y = 0
        
        # For "Apply to team" tab
        self.league_browse_idx = 0
        self.team_browse_idx = 0
        self.browse_teams = []
        self.browse_state = "LEAGUE"  # LEAGUE, TEAM
        
        self.msg = ""
        self.msg_timer = 0
        
        try:
            self.font_title = pygame.font.SysFont("Impact", 36)
            self.font_sub = pygame.font.SysFont("Arial", 22, bold=True)
            self.font_text = pygame.font.SysFont("Arial", 16)
            self.font_bold = pygame.font.SysFont("Arial", 16, bold=True)
            self.font_hint = pygame.font.SysFont("Arial", 14)
        except:
            self.font_title = pygame.font.Font(None, 36)
            self.font_sub = pygame.font.Font(None, 22)
            self.font_text = pygame.font.Font(None, 16)
            self.font_bold = pygame.font.Font(None, 16)
            self.font_hint = pygame.font.Font(None, 14)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    self.tab_idx = (self.tab_idx - 1) % 3
                    self.sel = 0; self.scroll_y = 0
                    if self.tab_idx == 2: self.browse_state = "LEAGUE"
                elif event.key == pygame.K_w:
                    self.tab_idx = (self.tab_idx + 1) % 3
                    self.sel = 0; self.scroll_y = 0
                    if self.tab_idx == 2: self.browse_state = "LEAGUE"
                elif event.key == pygame.K_ESCAPE:
                    if self.tab_idx == 2 and self.browse_state == "TEAM":
                        self.browse_state = "LEAGUE"
                    else:
                        from scenes.career_hub import CareerHubScene
                        self.manager.set_scene(CareerHubScene)
                else:
                    if self.tab_idx == 0:
                        self._handle_offers(event.key)
                    elif self.tab_idx == 1:
                        self._handle_applications(event.key)
                    elif self.tab_idx == 2:
                        self._handle_apply(event.key)

    def _handle_offers(self, key):
        offers = career_manager.manager_offers
        if key == pygame.K_UP:
            self.sel = max(0, self.sel - 1)
        elif key == pygame.K_DOWN:
            self.sel = min(len(offers) - 1, self.sel + 1)
        elif key == pygame.K_RETURN:
            if offers and self.sel < len(offers):
                o = offers[self.sel]
                if o["state"] == "pending":
                    result = career_manager.accept_offer(self.sel)
                    self.msg = result
                    self.msg_timer = 3.0
                    if "Bienvenido" in result:
                        from scenes.career_hub import CareerHubScene
                        is_star = False
                        if career_manager.mode == "player" and career_manager.career_player:
                            t_ovr = career_manager.get_team_ovr(career_manager.player_team["short"])
                            is_star = (career_manager.career_player.get("ovr", 70) >= 80 or t_ovr >= 78)
                        
                        if is_star:
                            from scenes.stadium_presentation import StadiumPresentationScene
                            target_scene = StadiumPresentationScene
                            target_context = {
                                "team": career_manager.player_team,
                                "player_name": career_manager.career_player["name"],
                                "number": career_manager.career_player.get("num", 10),
                                "next_scene": CareerHubScene
                            }
                        else:
                            from scenes.presentation import PresentationScene
                            target_scene = PresentationScene
                            target_context = {
                                "team": career_manager.player_team,
                                "player_name": career_manager.career_player["name"] if career_manager.career_player else "Entrenador",
                                "is_manager": (career_manager.mode == "manager"),
                                "number": career_manager.career_player.get("num", 10) if career_manager.career_player else 10,
                                "next_scene": CareerHubScene
                            }
                        
                        if career_manager.mode == "player":
                            from scenes.career_change_number import CareerChangeNumberScene
                            self.manager.set_scene(CareerChangeNumberScene, context={
                                "next_scene": target_scene,
                                "next_context": target_context,
                                "is_star": is_star
                            })
                        else:
                            self.manager.set_scene(target_scene, context=target_context)
        elif key == pygame.K_DELETE or key == pygame.K_BACKSPACE:
            if offers and self.sel < len(offers):
                offers.pop(self.sel)
                if self.sel > 0: self.sel -= 1
                self.msg = "Oferta rechazada."
                self.msg_timer = 2.0

    def _handle_applications(self, key):
        apps = career_manager.manager_applications
        if key == pygame.K_UP:
            self.sel = max(0, self.sel - 1)
        elif key == pygame.K_DOWN:
            self.sel = min(len(apps) - 1, self.sel + 1)
        elif key == pygame.K_RETURN:
            if apps and self.sel < len(apps):
                a = apps[self.sel]
                if a["state"] == "accepted":
                    result = career_manager.accept_application(self.sel)
                    self.msg = result
                    self.msg_timer = 3.0
                    if "Bienvenido" in result:
                        from scenes.career_hub import CareerHubScene
                        is_star = False
                        if career_manager.mode == "player" and career_manager.career_player:
                            t_ovr = career_manager.get_team_ovr(career_manager.player_team["short"])
                            is_star = (career_manager.career_player.get("ovr", 70) >= 80 or t_ovr >= 78)
                        
                        if is_star:
                            from scenes.stadium_presentation import StadiumPresentationScene
                            target_scene = StadiumPresentationScene
                            target_context = {
                                "team": career_manager.player_team,
                                "player_name": career_manager.career_player["name"],
                                "number": career_manager.career_player.get("num", 10),
                                "next_scene": CareerHubScene
                            }
                        else:
                            from scenes.presentation import PresentationScene
                            target_scene = PresentationScene
                            target_context = {
                                "team": career_manager.player_team,
                                "player_name": career_manager.career_player["name"] if career_manager.career_player else "Entrenador",
                                "is_manager": (career_manager.mode == "manager"),
                                "number": career_manager.career_player.get("num", 10) if career_manager.career_player else 10,
                                "next_scene": CareerHubScene
                            }
                        
                        if career_manager.mode == "player":
                            from scenes.career_change_number import CareerChangeNumberScene
                            self.manager.set_scene(CareerChangeNumberScene, context={
                                "next_scene": target_scene,
                                "next_context": target_context,
                                "is_star": is_star
                            })
                        else:
                            self.manager.set_scene(target_scene, context=target_context)

    def _handle_apply(self, key):
        if self.browse_state == "LEAGUE":
            if key == pygame.K_UP:
                self.league_browse_idx = max(0, self.league_browse_idx - 1)
            elif key == pygame.K_DOWN:
                self.league_browse_idx = min(len(career_manager.leagues) - 1, self.league_browse_idx + 1)
            elif key == pygame.K_RETURN:
                lg = career_manager.leagues[self.league_browse_idx]
                self.browse_teams = [t for t in career_manager.teams 
                                    if t.get("league", "EN") == lg 
                                    and t["short"] != career_manager.player_team["short"]]
                self.team_browse_idx = 0
                self.browse_state = "TEAM"
        elif self.browse_state == "TEAM":
            if key == pygame.K_UP:
                self.team_browse_idx = max(0, self.team_browse_idx - 1)
            elif key == pygame.K_DOWN:
                self.team_browse_idx = min(len(self.browse_teams) - 1, self.team_browse_idx + 1)
            elif key == pygame.K_RETURN:
                if self.browse_teams:
                    t = self.browse_teams[self.team_browse_idx]
                    result = career_manager.apply_to_team(t["short"])
                    self.msg = result
                    self.msg_timer = 3.0

    def update(self, dt):
        if self.msg_timer > 0:
            self.msg_timer -= dt

    def draw(self, surface):
        surface.fill((15, 20, 30))
        
        title = self.font_title.render("GESTIÓN DEL ENTRENADOR", True, UI_ACCENT)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 20))
        
        # Transfer window status
        if career_manager.transfer_window_open:
            wn = career_manager._get_transfer_window_name()
            ws = self.font_bold.render(f"🟢 VENTANA {wn} ABIERTA", True, (100, 255, 100))
        else:
            ws = self.font_bold.render("🔴 VENTANA DE TRASPASOS CERRADA", True, (255, 100, 100))
        surface.blit(ws, (WIDTH - ws.get_width() - 30, 30))
        
        # Tabs
        tabs = ["📥 OFERTAS RECIBIDAS", "📤 MIS SOLICITUDES", "🔍 BUSCAR CLUB"]
        tab_w = WIDTH // len(tabs)
        for i, t in enumerate(tabs):
            is_sel = (self.tab_idx == i)
            c = WHITE if is_sel else UI_TEXT_DIM
            ts = self.font_sub.render(t, True, c)
            tx = i * tab_w + (tab_w//2 - ts.get_width()//2)
            surface.blit(ts, (tx, 70))
            if is_sel:
                pygame.draw.line(surface, UI_ACCENT, (tx - 10, 98), (tx + ts.get_width() + 10, 98), 3)
        
        if self.tab_idx == 0:
            self._draw_offers(surface)
        elif self.tab_idx == 1:
            self._draw_applications(surface)
        elif self.tab_idx == 2:
            self._draw_apply(surface)
        
        if self.msg_timer > 0:
            ms = self.font_sub.render(self.msg, True, (255, 255, 100))
            surface.blit(ms, (WIDTH//2 - ms.get_width()//2, HEIGHT - 70))
        
        hint = self.font_hint.render("Q/W: Cambiar Pestaña  ·  ENTER: Acción  ·  DEL: Rechazar  ·  ESC: Volver", True, UI_TEXT_DIM)
        surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 30))

    def _draw_offers(self, surface):
        offers = career_manager.manager_offers
        y = 120
        
        if not offers:
            ns = self.font_text.render("No has recibido ofertas de otros clubes.", True, UI_TEXT_DIM)
            surface.blit(ns, (100, y))
            ns2 = self.font_text.render("Las ofertas llegan durante las ventanas de traspasos.", True, UI_TEXT_DIM)
            surface.blit(ns2, (100, y + 25))
            return
        
        for i, o in enumerate(offers):
            is_sel = (self.sel == i)
            rect = pygame.Rect(60, y, WIDTH - 120, 65)
            c = UI_CARD_HOVER if is_sel else UI_CARD_BG
            pygame.draw.rect(surface, c, rect, border_radius=8)
            if is_sel:
                pygame.draw.rect(surface, UI_ACCENT, rect, 2, border_radius=8)
            
            ns = self.font_bold.render(f"{o['team_name']} ({o['team_short']})", True, WHITE)
            surface.blit(ns, (rect.left + 20, rect.top + 10))
            
            ds = self.font_text.render(f"💰 Salario: ${o['salary']}M/año  |  ⏳ Expira en {o.get('expires_in', '?')} días", True, UI_TEXT_DIM)
            surface.blit(ds, (rect.left + 20, rect.top + 38))
            
            st = self.font_bold.render(o["state"].upper(), True, 
                (100, 255, 100) if o["state"] == "pending" else UI_TEXT_DIM)
            surface.blit(st, (rect.right - 120, rect.centery - st.get_height()//2))
            
            y += 75

    def _draw_applications(self, surface):
        apps = career_manager.manager_applications
        y = 120
        
        if not apps:
            ns = self.font_text.render("No has enviado solicitudes a ningún club.", True, UI_TEXT_DIM)
            surface.blit(ns, (100, y))
            return
        
        for i, a in enumerate(apps):
            is_sel = (self.sel == i)
            rect = pygame.Rect(60, y, WIDTH - 120, 65)
            c = UI_CARD_HOVER if is_sel else UI_CARD_BG
            pygame.draw.rect(surface, c, rect, border_radius=8)
            if is_sel:
                pygame.draw.rect(surface, UI_ACCENT, rect, 2, border_radius=8)
            
            ns = self.font_bold.render(f"{a['team_name']} ({a['team_short']})", True, WHITE)
            surface.blit(ns, (rect.left + 20, rect.top + 10))
            
            state = a["state"]
            if state == "pending":
                st_txt = f"⏳ En espera... ({a.get('wait', '?')} días)"
                sc = (255, 215, 0)
            elif state == "accepted":
                st_txt = "✅ ¡ACEPTADA! ENTER para fichar."
                sc = (100, 255, 100)
            elif state == "rejected":
                st_txt = "❌ Rechazada."
                sc = (255, 100, 100)
            else:
                st_txt = state
                sc = UI_TEXT_DIM
            
            ds = self.font_bold.render(st_txt, True, sc)
            surface.blit(ds, (rect.left + 20, rect.top + 38))
            
            y += 75

    def _draw_apply(self, surface):
        y = 120
        
        if not career_manager.transfer_window_open:
            ws = self.font_text.render("La ventana de traspasos está cerrada. No puedes enviar solicitudes ahora.", True, (255, 100, 100))
            surface.blit(ws, (100, y))
            return
        
        if self.browse_state == "LEAGUE":
            ls = self.font_sub.render("🌍 Selecciona una liga:", True, WHITE)
            surface.blit(ls, (100, y))
            y += 35
            
            for i, lg in enumerate(career_manager.leagues):
                is_sel = (self.league_browse_idx == i)
                rect = pygame.Rect(100, y, 300, 35)
                c = UI_CARD_HOVER if is_sel else (30, 35, 45)
                pygame.draw.rect(surface, c, rect, border_radius=4)
                ts = self.font_bold.render(f"Liga {lg}", True, WHITE if is_sel else UI_TEXT_DIM)
                surface.blit(ts, (rect.left + 15, rect.centery - ts.get_height()//2))
                y += 40
        
        elif self.browse_state == "TEAM":
            lg = career_manager.leagues[self.league_browse_idx]
            ls = self.font_sub.render(f"🛡️ Equipos en Liga {lg}:", True, WHITE)
            surface.blit(ls, (100, y))
            y += 35
            
            for i, t in enumerate(self.browse_teams):
                if i > 12: break
                is_sel = (self.team_browse_idx == i)
                rect = pygame.Rect(100, y, 500, 35)
                c = UI_CARD_HOVER if is_sel else (30, 35, 45)
                pygame.draw.rect(surface, c, rect, border_radius=4)
                
                ts = self.font_bold.render(t["name"], True, WHITE if is_sel else UI_TEXT_DIM)
                surface.blit(ts, (rect.left + 15, rect.centery - ts.get_height()//2))
                
                bs = self.font_text.render(f"${t.get('budget', 0)}M", True, (100, 255, 150))
                surface.blit(bs, (rect.right - 80, rect.centery - bs.get_height()//2))
                
                y += 40
