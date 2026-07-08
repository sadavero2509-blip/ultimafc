import pygame
import math
from settings import *
from data.career_manager import career_manager

class CareerHubScene:
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        self.time = 0
        
        # Tabs system (EA FC Style)
        self.tabs = [
            {"id": "central", "name": "CENTRAL", "icon": "🏠"},
            {"id": "squad", "name": "PLANTILLA", "icon": "📋"},
            {"id": "market", "name": "TRASPASOS", "icon": "🤝"},
            {"id": "office", "name": "OFICINA", "icon": "💼"}
        ]
        self._update_menu_items()
        
        self.tab_idx = 0
        self.sel_idx = 0 # Use index-based selection for the flat list of items per tab
        self.auto_advancing = False
        self.sim_timer = 0
        self.msg = ""
        self.msg_timer = 0
        self.months = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
        
        try:
            self.font_tab = pygame.font.SysFont("Impact", 24)
            self.font_tile = pygame.font.SysFont("Arial", 18, bold=True)
            self.font_tile_sub = pygame.font.SysFont("Arial", 14)
            self.font_name = pygame.font.SysFont("Impact", 32)
            self.font_text = pygame.font.SysFont("Arial", 16)
            self.font_icon = pygame.font.SysFont("Segoe UI Emoji", 36)
            self.font_hint = pygame.font.SysFont("Arial", 12)
        except:
            self.font_tab = pygame.font.Font(None, 24)
            self.font_tile = pygame.font.Font(None, 18)
            self.font_tile_sub = pygame.font.Font(None, 14)
            self.font_name = pygame.font.Font(None, 32)
            self.font_text = pygame.font.Font(None, 16)
            self.font_icon = pygame.font.Font(None, 36)
            self.font_hint = pygame.font.Font(None, 12)
            
        # Check pending awards
        if career_manager.active and career_manager.mode == "player":
            if career_manager.career_stats.get("pending_award_presentations"):
                award_name = career_manager.career_stats["pending_award_presentations"].pop(0)
                from scenes.presentation import PresentationScene
                self.manager.set_scene(PresentationScene, context={
                    "team": career_manager.player_team,
                    "player_name": career_manager.career_player["name"],
                    "is_manager": False,
                    "number": career_manager.career_player.get("num", 10),
                    "award_name": award_name,
                    "next_scene": CareerHubScene
                })

    def _update_menu_items(self):
        """Organizes all options into a categorical grid per tab."""
        match_today, _ = career_manager.get_player_match_today()
        adv_name = "JUGAR PARTIDO" if match_today else "AVANZAR DÍA"
        adv_icon = "⚽" if match_today else "📅"
        is_player = (career_manager.mode == "player")
        
        # Categorized items for each tab
        # Each item: {id, name, icon, pos(col, row), size(w, h), category, desc}
        self.menu_items = {
            "central": [
                {"id": "advance_day", "name": adv_name, "icon": adv_icon, "pos": (0, 0), "size": (2, 2), "cat": "PRÓXIMO PASO", "desc": "Avanzar al siguiente evento."},
                {"id": "play", "name": "SIMULAR", "icon": "🎯", "pos": (2, 0), "size": (1, 1), "cat": "PARTIDO", "desc": "Simulación rápida."},
                {"id": "objectives", "name": "OBJETIVOS", "icon": "📈", "pos": (3, 0), "size": (1, 1), "cat": "PARTIDO", "desc": "Metas del club."},
                {"id": "inbox", "name": "BUZÓN", "icon": "📧", "pos": (2, 1), "size": (1, 1), "cat": "CENTRO", "desc": "Mensajes y ofertas."},
                {"id": "news", "name": "NOTICIAS", "icon": "📰", "pos": (3, 1), "size": (1, 1), "cat": "CENTRO", "desc": "Actualidad mundial."},
                {"id": "shop", "name": "TIENDA", "icon": "🛒", "pos": (4, 0), "size": (1, 1), "cat": "ESTILO", "desc": "Gastar salario."},
                {"id": "contract", "name": "CONTRATO", "icon": "📄", "pos": (4, 1), "size": (1, 1), "cat": "ESTILO", "desc": "Renovación."},
                {"id": "social", "name": "REDES SOCIALES", "icon": "📱", "pos": (0, 2), "size": (2, 1), "cat": "COMUNIDAD", "desc": "Ver menciones, posts y gestionar tu red.", "visible": is_player}
            ],
            "squad": [
                {"id": "player_profile", "name": "MI PERFIL", "icon": "👤", "pos": (0, 0), "size": (2, 1), "cat": "PERSONAL", "visible": is_player},
                {"id": "squad", "name": "PLANTILLA", "icon": "📋", "pos": (0, 1) if is_player else (0, 0), "size": (2, 1) if is_player else (2, 2), "cat": "EQUIPO"},
                {"id": "training", "name": "ENTRENAR", "icon": "🏋️", "pos": (2, 0), "size": (1, 1), "cat": "RENDIMIENTO", "visible": is_player},
                {"id": "standings", "name": "TABLA LIGA", "icon": "🏆", "pos": (2, 1) if is_player else (2, 0), "size": (1, 1), "cat": "COMPETICIÓN"},
                {"id": "stats", "name": "ESTADÍSTICAS", "icon": "📈", "pos": (3, 0), "size": (1, 1), "cat": "RENDIMIENTO"},
                {"id": "change_number", "name": "DORSAL", "icon": "🔟", "pos": (3, 1), "size": (1, 1), "cat": "PERSONAL", "visible": (is_player and career_manager.can_change_number)},
                {"id": "museum", "name": "MUSEO", "icon": "🏛️", "pos": (4, 0), "size": (1, 2), "cat": "HISTORIA", "desc": "Récords del Club"},
                {"id": "nt_squad", "name": "SELECCIÓN", "icon": "🌍", "pos": (0, 2), "size": (2, 1), "cat": "INTERNACIONAL", "visible": (career_manager.is_called_up or career_manager.managing_nt)}
            ],
            "market": [
                {"id": "market" if not is_player else "market_player", "name": "MERCADO" if not is_player else "TRASPASO", "icon": "🤝", "pos": (0, 0), "size": (2, 2), "cat": "NEGOCIACIÓN"},
                {"id": "search" if not is_player else "loan_request", "name": "BUSCAR" if not is_player else "CESIÓN", "icon": "🔍" if not is_player else "📋", "pos": (2, 0), "size": (2, 1), "cat": "EXPLORACIÓN" if not is_player else "PEDIDOS"},
                {"id": "stay_request", "name": "QUEDARSE", "icon": "🏠", "pos": (2, 1), "size": (1, 1), "cat": "PEDIDOS", "visible": is_player},
                {"id": "destinations", "name": "DESTINOS", "icon": "🌍", "pos": (3, 1), "size": (1, 1), "cat": "EXPLORACIÓN", "visible": is_player, "desc": "Buscar clubes y sugerir al agente."},
                {"id": "offers", "name": "OFERTAS DT", "icon": "💼", "pos": (0, 2), "size": (2, 1), "cat": "MÁNAGER", "visible": not is_player}
            ],
            "office": [
                {"id": "agent", "name": "AGENTE", "icon": "🕶️", "pos": (0, 0), "size": (1, 1), "cat": "GESTIÓN", "desc": "Tu representante."},
                {"id": "save", "name": "GUARDAR", "icon": "💾", "pos": (1, 0), "size": (1, 1), "cat": "SISTEMA"},
                {"id": "settings", "name": "AJUSTES", "icon": "⚙️", "pos": (2, 0), "size": (1, 1), "cat": "SISTEMA", "desc": "Toggle Autosave."},
                {"id": "cloud_save", "name": "NUBE", "icon": "☁️", "pos": (3, 0), "size": (1, 1), "cat": "SISTEMA", "desc": "Sincronizar con servidor."},
                {"id": "retire", "name": "RETIRARSE", "icon": "🌅", "pos": (0, 1), "size": (1, 1), "cat": "SISTEMA"},
                {"id": "exit", "name": "SALIR", "icon": "🚪", "pos": (1, 1), "size": (1, 1), "cat": "SISTEMA"},
                {"id": "captain_actions", "name": "CAPITÁN", "icon": "👑", "pos": (0, 2), "size": (2, 1), "cat": "GESTIÓN", "visible": (career_manager.career_stats.get("is_captain") or career_manager.career_stats.get("is_nt_captain")), "desc": "Liderazgo del equipo."}
            ]
        }
        
        # Filter visible items
        for tid in self.menu_items:
            self.menu_items[tid] = [item for item in self.menu_items[tid] if item.get("visible", True)]

        
    def handle_events(self, events):
        if self.auto_advancing:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    self.auto_advancing = False
                    self.msg = "Simulación detenida."
                    self.msg_timer = 1.5
            return
        
        tab_id = self.tabs[self.tab_idx]["id"]
        items = self.menu_items[tab_id]
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q: # L1
                    self.tab_idx = (self.tab_idx - 1) % len(self.tabs)
                    self.sel_idx = 0
                elif event.key == pygame.K_e: # R1
                    self.tab_idx = (self.tab_idx + 1) % len(self.tabs)
                    self.sel_idx = 0
                
                # Intelligent navigation based on grid positions
                current = items[self.sel_idx]
                cx, cy = current["pos"]
                target_idx = self.sel_idx
                
                if event.key == pygame.K_LEFT:
                    best_dist = float('inf')
                    for i, item in enumerate(items):
                        ix, iy = item["pos"]
                        if ix < cx:
                            dist = abs(iy - cy) * 10 + (cx - ix)
                            if dist < best_dist:
                                best_dist = dist; target_idx = i
                elif event.key == pygame.K_RIGHT:
                    best_dist = float('inf')
                    for i, item in enumerate(items):
                        ix, iy = item["pos"]
                        if ix > cx:
                            dist = abs(iy - cy) * 10 + (ix - cx)
                            if dist < best_dist:
                                best_dist = dist; target_idx = i
                elif event.key == pygame.K_UP:
                    best_dist = float('inf')
                    for i, item in enumerate(items):
                        ix, iy = item["pos"]
                        if iy < cy:
                            dist = abs(ix - cx) * 10 + (cy - iy)
                            if dist < best_dist:
                                best_dist = dist; target_idx = i
                elif event.key == pygame.K_DOWN:
                    best_dist = float('inf')
                    for i, item in enumerate(items):
                        ix, iy = item["pos"]
                        if iy > cy:
                            dist = abs(ix - cx) * 10 + (iy - cy)
                            if dist < best_dist:
                                best_dist = dist; target_idx = i
                elif event.key == pygame.K_RETURN:
                    self._select_option()
                
                self.sel_idx = target_idx

    def _select_option(self):
        tab_id = self.tabs[self.tab_idx]["id"]
        items = self.menu_items[tab_id]
        if self.sel_idx >= len(items): return
        sel_item = items[self.sel_idx]
        sel = sel_item["id"]
        
        if sel == "advance_day":
            match_today, _ = career_manager.get_player_match_today()
            if match_today:
                from scenes.career_pre_match import CareerPreMatchScene
                self.manager.set_scene(CareerPreMatchScene)
            else:
                career_manager.advance_time()
                self.msg = "Día procesado."
                self.msg_timer = 1.5
                self._update_menu_items()
        elif sel == "play":
            match_today, _ = career_manager.get_player_match_today()
            if match_today:
                from scenes.career_pre_match import CareerPreMatchScene
                self.manager.set_scene(CareerPreMatchScene)
            else:
                self.auto_advancing = True
        elif sel == "squad":
            from scenes.career_squad import CareerSquadScene
            self.manager.set_scene(CareerSquadScene)
        elif sel == "player_profile":
            from scenes.career_profile import CareerProfileScene
            self.manager.set_scene(CareerProfileScene)
        elif sel == "training":
            from scenes.career_training import CareerTrainingScene
            self.manager.set_scene(CareerTrainingScene)
        elif sel == "standings":
            from scenes.career_standings import CareerStandingsScene
            self.manager.set_scene(CareerStandingsScene)
        elif sel == "stats":
            from scenes.career_stats import CareerStatsScene
            self.manager.set_scene(CareerStatsScene)
        elif sel == "news":
            from scenes.career_news import CareerNewsScene
            self.manager.set_scene(CareerNewsScene)
        elif sel == "inbox":
            from scenes.career_inbox import CareerInboxScene
            self.manager.set_scene(CareerInboxScene)
        elif sel == "social":
            from scenes.career_social import CareerSocialScene
            self.manager.set_scene(CareerSocialScene)
        elif sel == "objectives":
            from scenes.career_objectives import CareerObjectivesScene
            self.manager.set_scene(CareerObjectivesScene)
        elif sel == "shop":
            from scenes.career_shop import CareerShopScene
            self.manager.set_scene(CareerShopScene)
        elif sel == "contract":
            if career_manager.mode != "player":
                self.msg = "Solo disponible en modo Jugador."
                self.msg_timer = 2.0
            elif career_manager.career_player.get("contract_years", 3) > 2:
                # Consultar contrato sin permitir negociación
                from scenes.career_stats import CareerStatsScene
                self.manager.set_scene(CareerStatsScene, context={"tab_id": "contract", "contract_consult_only": True})
            else:
                from scenes.career_negotiation import CareerNegotiationScene
                self.manager.set_scene(CareerNegotiationScene)
        elif sel == "change_number":
            from scenes.career_change_number import CareerChangeNumberScene
            t_ovr = career_manager.get_team_ovr(career_manager.player_team["short"])
            is_star = (career_manager.career_player.get("ovr", 70) >= 80 or t_ovr >= 78)
            self.manager.set_scene(CareerChangeNumberScene, context={"is_star": is_star})
        elif sel == "market":
            from scenes.career_market import CareerMarketScene
            self.manager.set_scene(CareerMarketScene)
        elif sel == "market_player":
            if career_manager.request_transfer_status("transfer"):
                self.msg = "Petición de TRASPASO enviada al mánager."
            else:
                self.msg = "Ya tienes una petición pendiente."
            self.msg_timer = 3.0
        elif sel == "loan_request":
            if career_manager.request_transfer_status("loan"):
                self.msg = "Petición de CESIÓN enviada al mánager."
            else:
                self.msg = "Ya tienes una petición pendiente."
            self.msg_timer = 3.0
        elif sel == "stay_request":
            if career_manager.request_transfer_status("stay"):
                self.msg = "Petición de PERMANENCIA enviada al mánager."
            else:
                self.msg = "Ya tienes una petición pendiente."
            self.msg_timer = 3.0
        elif sel == "destinations":
            if not career_manager.transfer_window_open:
                self.msg = "La ventana de fichajes está cerrada."
                self.msg_timer = 3.0
            elif career_manager.agent.get("level", 0) < 1:
                self.msg = "Necesitas un agente para explorar destinos."
                self.msg_timer = 3.0
            else:
                from scenes.career_destinations import CareerDestinationsScene
                self.manager.set_scene(CareerDestinationsScene)
        elif sel == "museum":
            from scenes.career_museum import CareerMuseumScene
            self.manager.push_scene(CareerMuseumScene)


        elif sel == "offers":
            from scenes.career_manager_offers import CareerManagerOffersScene
            self.manager.set_scene(CareerManagerOffersScene)
        elif sel == "nt_squad":
            from scenes.career_squad import CareerSquadScene
            nt_short = career_manager.nationality
            self.manager.set_scene(CareerSquadScene, context={"nt_mode": True, "team_short": nt_short})
        elif sel == "save":
            from scenes.career_slots import CareerSlotsScene
            self.manager.set_scene(CareerSlotsScene, context={"slot_mode": "save"})
        elif sel == "settings":
            career_manager.autosave_enabled = not getattr(career_manager, 'autosave_enabled', True)
            career_manager.save_config()
            state_str = "ACTIVADO" if career_manager.autosave_enabled else "DESACTIVADO"
            self.msg = f"Autoguardado {state_str}"
            self.msg_timer = 3.0
        elif sel == "cloud_save":
            from systems.network import NetworkManager
            net = NetworkManager()
            if not net.connected:
                self.msg = "Error: No conectado al servidor."
            else:
                # Subir partida actual
                data = career_manager.get_save_data()
                if net.save_cloud(data):
                    self.msg = "Partida sincronizada en la NUBE."
                else:
                    self.msg = "Error al sincronizar partida."
            self.msg_timer = 3.0
        elif sel == "agent":
            from scenes.career_agent import CareerAgentScene
            self.manager.set_scene(CareerAgentScene)
        elif sel == "captain_actions":
            from scenes.career_captain import CareerCaptainScene
            self.manager.set_scene(CareerCaptainScene)
        elif sel == "retire":
            from scenes.career_retire import CareerRetireScene
            self.manager.set_scene(CareerRetireScene)
        elif sel == "exit":
            from scenes.main_menu import MainMenuScene
            career_manager.active = False
            self.manager.set_scene(MainMenuScene)

    def update(self, dt):
        self.time += dt
        if self.msg_timer > 0: self.msg_timer -= dt
        
        # NT Events
        if hasattr(career_manager, 'pending_nt_event') and career_manager.pending_nt_event:
            evt = career_manager.pending_nt_event
            career_manager.pending_nt_event = None
            from scenes.career_international import CareerInternationalScene
            self.manager.set_scene(CareerInternationalScene, context=evt)
            return
            
        if self.auto_advancing:
            self.sim_timer += dt
            if self.sim_timer >= 0.7:
                self.sim_timer = 0
                result = career_manager.advance_time()
                if result["status"] == "END_OF_SEASON":
                    self.auto_advancing = False
                    from scenes.career_season_end import CareerSeasonEndScene
                    self.manager.set_scene(CareerSeasonEndScene, context={"top_players": result["top_players"]})
                else:
                    m, _ = career_manager.get_player_match_today()
                    if m: self.auto_advancing = False

    def draw(self, surface):
        surface.fill((10, 12, 20))
        
        # --- TOP HEADER (EA FC Style Tabs) ---
        pygame.draw.rect(surface, (20, 25, 45), (0, 0, WIDTH, 120))
        
        # Tabs
        tab_x = 50
        for i, tab in enumerate(self.tabs):
            is_sel = (self.tab_idx == i)
            # Underline for selected tab
            if is_sel:
                pygame.draw.rect(surface, UI_ACCENT, (tab_x, 115, 120, 5))
                tc = WHITE
            else:
                tc = UI_TEXT_DIM
            
            ts = self.font_tab.render(tab["name"], True, tc)
            surface.blit(ts, (tab_x + 60 - ts.get_width()//2, 85))
            tab_x += 160
            
        # L1/R1 Hints
        l1 = self.font_hint.render("[Q] L1", True, UI_TEXT_DIM)
        r1 = self.font_hint.render("[E] R1", True, UI_TEXT_DIM)
        surface.blit(l1, (30, 88))
        surface.blit(r1, (tab_x - 40, 88))

        # --- USER INFO ---
        t = career_manager.player_team
        if t:
            from data.teams import draw_badge
            draw_badge(surface, t, WIDTH - 100, 60, size=50)
            
            # Manager/Player Name + Age
            user_label = career_manager.manager_name.upper()
            if career_manager.mode == "player" and career_manager.career_player:
                age = career_manager.career_player.get('age', 17)
                cap_icon = " (C)" if career_manager.career_stats.get("is_captain") else ""
                user_label += f"{cap_icon} ({age} AÑOS)"
                
            name = self.font_name.render(user_label, True, WHITE)
            surface.blit(name, (WIDTH - 450, 20))
            
            # Cabecera pending social notification badge
            sm_data = career_manager.career_stats.get("social_media", {})
            unread_dms = sum(1 for dm in sm_data.get("dms", []) if dm.get("status") == "unread")
            unread_posts = sum(1 for post in sm_data.get("posts", []) if not post.get("read", True))
            tot_pending = unread_dms + unread_posts
            if tot_pending > 0:
                badge_lbl = f"● {tot_pending} SOCIAL"
                badge_w = self.font_hint.size(badge_lbl)[0] + 12
                # Pulsing red color
                pulse_color = (255, int(50 + 30 * math.sin(self.time * 5)), int(50 + 30 * math.sin(self.time * 5)))
                badge_rect = pygame.Rect(WIDTH - 450 + name.get_width() + 15, 20, badge_w, 20)
                pygame.draw.rect(surface, pulse_color, badge_rect, border_radius=10)
                badge_txt = self.font_hint.render(badge_lbl, True, WHITE)
                surface.blit(badge_txt, (badge_rect.centerx - badge_txt.get_width() // 2, badge_rect.centery - badge_txt.get_height() // 2 - 1))

            d = career_manager.current_date
            ds = f"{d.day} {self.months[d.month-1]} {d.year}"
            d_surf = self.font_text.render(ds, True, UI_ACCENT)
            surface.blit(d_surf, (WIDTH - 450, 55))
            
            # Money and Prestige info
            if career_manager.mode == "player":
                money_str = f"Cuenta: ${career_manager.career_stats['money']:.1f}M"
                ms = self.font_hint.render(money_str, True, (100, 255, 150))
                surface.blit(ms, (WIDTH - 450, 75))
                
                pres_str = f"Prestigio: {career_manager.career_stats['prestige']}/1000"
                ps = self.font_hint.render(pres_str, True, (255, 200, 50))
                surface.blit(ps, (WIDTH - 450, 90))
                
                # Coach Confidence Bar
                conf = career_manager.career_stats.get("coach_confidence", 40)
                conf_str = f"Confianza DT: {conf}/100"
                cs = self.font_hint.render(conf_str, True, WHITE)
                surface.blit(cs, (WIDTH - 450, 105))
                
                # Draw small progress bar
                bar_x = WIDTH - 330
                bar_y = 108
                pygame.draw.rect(surface, (40, 40, 40), (bar_x, bar_y, 100, 10))
                color = (255, 50, 50) if conf < 30 else (255, 200, 0) if conf < 50 else (50, 255, 100)
                pygame.draw.rect(surface, color, (bar_x, bar_y, conf, 10))
                
                # Status hint
                status_txt = "CONVOCADO" if conf >= 30 else "NO CONVOCADO"
                if conf >= 50: status_txt = "TITULAR"
                if conf >= 85: status_txt = "ESTRELLA"
                ss = self.font_hint.render(status_txt, True, color)
                surface.blit(ss, (bar_x + 110, bar_y - 2))
                
                # --- ACTIVE OBJECTIVES SUMMARY ---
                objs = career_manager.objectives
                if objs:
                    oy = 130
                    surface.blit(self.font_hint.render("OBJETIVOS ACTIVOS:", True, UI_ACCENT), (WIDTH - 450, oy))
                    oy += 20
                    for obj in objs[:3]: # Show top 3
                        # Calculate percent for the dot color
                        target = obj["target"]
                        current = obj["current"]
                        if obj["type"] == "team_pos":
                            percent = 1.0 if current <= target else 0.0
                        else:
                            percent = min(1.0, current / target) if target > 0 else 0
                        
                        dot_c = (100, 255, 100) if percent >= 1.0 else (255, 200, 50)
                        pygame.draw.circle(surface, dot_c, (WIDTH - 440, oy + 8), 4)
                        
                        o_txt = f"{obj['desc']}"
                        osurf = self.font_hint.render(o_txt, True, UI_TEXT_DIM)
                        surface.blit(osurf, (WIDTH - 430, oy))
                        oy += 18

        # --- CATEGORIZED GRID TILES (No Scroll) ---
        start_y = 150 # Slightly higher since labels are inside
        start_x = 50
        tile_margin = 15
        tile_base_w = 180
        tile_base_h = 130
            
        tab_id = self.tabs[self.tab_idx]["id"]
        items = self.menu_items[tab_id]
        
        # Draw items
        for i, item in enumerate(items):
            is_sel = (self.sel_idx == i)
            col, row = item["pos"]
            tw, th = item["size"]
            
            rect_w = tw * tile_base_w + (tw-1) * tile_margin
            rect_h = th * tile_base_h + (th-1) * tile_margin
            
            draw_x = start_x + col * (tile_base_w + tile_margin)
            draw_y = start_y + row * (tile_base_h + tile_margin)
            
            tile_rect = pygame.Rect(draw_x, draw_y, rect_w, rect_h)
            
            # Draw Tile Background
            bg_color = (30, 35, 60) if is_sel else (20, 25, 45)
            pygame.draw.rect(surface, bg_color, tile_rect, border_radius=10)
            
            if is_sel:
                # Top accent bar for selection
                pygame.draw.rect(surface, UI_ACCENT, (tile_rect.left, tile_rect.top, tile_rect.width, 4), border_top_left_radius=10, border_top_right_radius=10)
                # Outer border
                pygame.draw.rect(surface, WHITE, tile_rect, 2, border_radius=10)
                # Description at bottom
                if "desc" in item:
                    ds = self.font_text.render(item["desc"], True, WHITE)
                    surface.blit(ds, (WIDTH - ds.get_width() - 50, HEIGHT - 75))
            else:
                pygame.draw.rect(surface, (40, 45, 70), tile_rect, 1, border_radius=10)
            
            # Category Label (Inside)
            cat = item.get("cat", "")
            if cat:
                cat_c = UI_ACCENT if is_sel else UI_TEXT_DIM
                cs = self.font_hint.render(cat, True, cat_c)
                surface.blit(cs, (tile_rect.left + 12, tile_rect.top + 10))
            
            # Icon
            try:
                ic = self.font_icon.render(item["icon"], True, WHITE)
                # Offset icon down if it has a category label
                y_off = 10 if cat else 0
                surface.blit(ic, (tile_rect.centerx - ic.get_width()//2, tile_rect.centery - 15 + y_off))
            except: pass
            
            # Label
            ls = self.font_tile.render(item["name"], True, WHITE)
            surface.blit(ls, (tile_rect.left + 12, tile_rect.bottom - 30))

            if item["id"] == "social":
                sm_data = career_manager.career_stats.get("social_media", {})
                unread_dms = sum(1 for dm in sm_data.get("dms", []) if dm.get("status") == "unread")
                unread_posts = sum(1 for post in sm_data.get("posts", []) if not post.get("read", True))
                tot = unread_dms + unread_posts
                if tot > 0:
                    badge_size = 20
                    badge_rect = pygame.Rect(tile_rect.right - 28, tile_rect.top + 8, badge_size, badge_size)
                    pygame.draw.circle(surface, (255, 50, 50), badge_rect.center, badge_size // 2)
                    badge_txt = self.font_hint.render(str(tot), True, WHITE)
                    surface.blit(badge_txt, (badge_rect.centerx - badge_txt.get_width() // 2, badge_rect.centery - badge_txt.get_height() // 2))
            elif item["id"] == "inbox":
                unread_emails = sum(1 for mail in career_manager.inbox if not mail.get("read", False))
                if unread_emails > 0:
                    badge_size = 20
                    badge_rect = pygame.Rect(tile_rect.right - 28, tile_rect.top + 8, badge_size, badge_size)
                    pygame.draw.circle(surface, (255, 50, 50), badge_rect.center, badge_size // 2)
                    badge_txt = self.font_hint.render(str(unread_emails), True, WHITE)
                    surface.blit(badge_txt, (badge_rect.centerx - badge_txt.get_width() // 2, badge_rect.centery - badge_txt.get_height() // 2))


        # Status Message
        if self.msg_timer > 0:
            ms = self.font_text.render(self.msg, True, (100, 255, 100))
            surface.blit(ms, (WIDTH//2 - ms.get_width()//2, 130))

        # Simulation Banner (non-blocking, stays on main menu)
        if self.auto_advancing:
            # Pulsing accent bar at the top
            pulse = int(180 + 75 * math.sin(self.time * 4))
            bar_h = 38
            bar_surf = pygame.Surface((WIDTH, bar_h), pygame.SRCALPHA)
            bar_surf.fill((0, 200, 150, 40))
            surface.blit(bar_surf, (0, 120))
            pygame.draw.line(surface, (0, min(255, pulse), 150), (0, 120 + bar_h), (WIDTH, 120 + bar_h), 2)
            txt = self.font_tile.render("⏩ SIMULANDO DÍAS...", True, (0, 255, 180))
            surface.blit(txt, (WIDTH//2 - txt.get_width()//2, 126))
            sub_txt = self.font_hint.render("Presiona cualquier tecla para detener", True, UI_TEXT_DIM)
            surface.blit(sub_txt, (WIDTH//2 - sub_txt.get_width()//2, 143))

        # Bottom Hint
        hint = self.font_hint.render("↑↓←→ Navegar  ·  Q/E Cambiar Pestaña  ·  ENTER Seleccionar", True, UI_TEXT_DIM)
        surface.blit(hint, (50, HEIGHT - 30))
