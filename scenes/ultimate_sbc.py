import pygame
from settings import *
from .main_menu import MenuScene, BaseScene
import copy
from systems.ultimate_manager import ultimate_manager
from systems.card_renderer import card_renderer

class SBCScene(MenuScene):
    def __init__(self, manager, group="PREMIUM"):
        super().__init__(manager)
        self.um = ultimate_manager
        self.group = group
        # Forzar refresco para asegurar que los requisitos de SBC (Media) se basen en datos actualizados
        ultimate_manager.refresh_all_ovrs()
        if group == "PREMIUM":
            self.categories = ["FUNDADOR", "EVENTOS"]
        else:
            self.categories = ["PAÍSES", "MEJORAS", "DIARIOS"]
            
        self.cat_idx = 0
        self.selected_idx = 0
        self.view_mode = "LIST" # "LIST", "DETAILS", "PICKING"
        
        # Selección de jugadores
        self.sbc_slots = [None] * 11
        self.picking_slot_idx = -1
        self.inv_scroll = 0
        self.inv_selected = 0
        self._cached_inv = None
        
        self.msg = ""
        self.msg_timer = 0
        
        self._init_sbcs()

    def _init_sbcs(self):
        # 1. PREMIUM - FUNDADOR
        self.sbcs_founder = [
            {
                "id": "founder_claim", "name": "RECOMPENSA DE FUNDADOR", "cat": "FUNDADOR",
                "desc": "¡Gracias por ser parte de los inicios! Reclama tu carta exclusiva.",
                "reqs": [], "reward_type": "founder", "completed": self.um.has_claimed_founder_reward
            }
        ]
        
        # 2. PREMIUM - EVENTOS
        from data.event_worldcup import is_event_active
        self.sbcs_events = []
        if is_event_active():
            self.sbcs_events.append({
                "id": "pele_wc", "name": "SBC: PELÉ MUNDIALISTA", "cat": "EVENTOS",
                "desc": "Intercambia a O Rei (90+) y una plantilla galáctica por su versión WC.",
                "reqs": [
                    {"type": "min_ovr", "value": 90, "count": 3},
                    {"type": "min_nat", "value": "BRA", "count": 2},
                    {"type": "total", "value": "Jugadores", "count": 11}
                ],
                "reward_type": "player", "reward_data": "pele_wc", "completed": False,
                "locked": False
            })

        # 3. FUNDAMENTOS - PAÍSES
        self.sbcs_countries = [
            {
                "id": "nations_esp", "name": "ORGULLO ESPAÑOL", "cat": "PAÍSES",
                "desc": "Entrega 11 jugadores (mín. 1 español) por 10 Oros (3 Españoles).",
                "reqs": [{"type": "min_nat", "value": "ESP", "count": 1}, {"type": "total", "value": "Cualquiera", "count": 11}],
                "reward_type": "pack_themed_mixed", "reward_data": "ESP", "completed": False
            }
        ]

        # 4. FUNDAMENTOS - MEJORAS
        self.sbcs_upgrades = [
            {
                "id": "upgrade_gold", "name": "MEJORA DE ORO (+80 OVR)", "cat": "MEJORAS",
                "desc": "Entrega 11 jugadores de Oro para obtener un sobre de 10 jugadores Oro (+80).",
                "reqs": [{"type": "rarity", "value": "ORO", "count": 11}],
                "reward_type": "pack_80", "count": 10, "completed": False
            }
        ]

        # 5. FUNDAMENTOS - DIARIOS
        self.sbcs_daily = []
        for rarity in ["ORO", "PLATA", "BRONCE"]:
            self.sbcs_daily.append({
                "id": f"daily_{rarity.lower()}", "name": f"DESAFÍO DIARIO: {rarity}", "cat": "DIARIOS",
                "desc": f"Entrega 1 jugador {rarity} por un sobre de 5 jugadores {rarity}.",
                "reqs": [{"type": "rarity", "value": rarity, "count": 1}],
                "reward_type": "pack_5", "reward_rarity": rarity, "completed": False
            })

        # Sync from state
        for group in [self.sbcs_founder, self.sbcs_events, self.sbcs_countries, self.sbcs_upgrades, self.sbcs_daily]:
            for sbc in group:
                if sbc["id"] in self.um.sbc_state:
                    sbc["completed"] = self.um.sbc_state[sbc["id"]]
                    
        self._refresh_current_list()

    def _refresh_current_list(self):
        cat = self.categories[self.cat_idx]
        if cat == "FUNDADOR": self.current_sbcs = self.sbcs_founder
        elif cat == "EVENTOS": self.current_sbcs = self.sbcs_events
        elif cat == "PAÍSES": self.current_sbcs = self.sbcs_countries
        elif cat == "MEJORAS": self.current_sbcs = self.sbcs_upgrades
        else: self.current_sbcs = self.sbcs_daily
        if len(self.current_sbcs) > 0:
            self.selected_idx = max(0, min(self.selected_idx, len(self.current_sbcs)-1))
        else:
            self.selected_idx = 0

    def draw(self, screen):
        screen.fill((10, 15, 30))
        
        if self.view_mode == "PICKING":
            self._draw_inventory_picker(screen)
        elif self.view_mode == "DETAILS":
            self._draw_details(screen)
        else:
            self._draw_list(screen)
            
        if self.msg_timer > 0:
            self.draw_text(screen, self.msg, WIDTH//2, 50, color=GOLD, bold=True, center=True)

    def _draw_list(self, screen):
        # Cabecera
        pygame.draw.rect(screen, (20, 25, 45), (0, 0, WIDTH, 120))
        self.draw_text(screen, "INTERCAMBIOS DE PLANTILLA (SBC)", 50, 25, size=32, bold=True, color=UI_ACCENT)
        
        for i, cat in enumerate(self.categories):
            is_sel = (self.cat_idx == i)
            color = WHITE if is_sel else UI_TEXT_DIM
            x = 50 + i * 180
            self.draw_text(screen, cat, x, 80, size=20, bold=is_sel, color=color)
            if is_sel: pygame.draw.rect(screen, UI_ACCENT, (x, 105, 120, 3))
            
        import datetime
        now = datetime.datetime.utcnow()
        reset_time = now.replace(hour=18, minute=0, second=0, microsecond=0)
        if now >= reset_time:
            reset_time += datetime.timedelta(days=1)
        diff = reset_time - now
        hours, remainder = divmod(int(diff.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        
        self.draw_text(screen, f"Nuevos Desafíos en: {hours:02}:{minutes:02}:{seconds:02}", WIDTH - 350, 80, size=20, color=(255, 100, 100), bold=True)

        # Lista de desafíos
        for i, sbc in enumerate(self.current_sbcs):
            rect = pygame.Rect(50, 140 + i*130, WIDTH-100, 110)
            color = (35, 45, 75) if i == self.selected_idx else (25, 30, 50)
            pygame.draw.rect(screen, color, rect, border_radius=15)
            if i == self.selected_idx: pygame.draw.rect(screen, UI_ACCENT, rect, 2, border_radius=15)
            
            icon = "[PREM]" if sbc["cat"] == "PREMIUM" else "[DIARIO]"
            if sbc.get("locked"): icon = "[LOCK]"
            
            self.draw_text(screen, icon, 70, 175 + i*130, size=14, color=GOLD, bold=True)
            
            name_color = UI_TEXT_DIM if sbc.get("locked") else WHITE
            self.draw_text(screen, sbc["name"], 140, 160 + i*130, size=22, bold=True, color=name_color)
            self.draw_text(screen, sbc["desc"], 140, 195 + i*130, size=16, color=UI_TEXT_DIM)
            
            if sbc.get("locked"):
                self.draw_text(screen, "PRÓXIMAMENTE", WIDTH - 200, 175 + i*130, color=UI_TEXT_DIM, bold=True)
            elif sbc.get("completed"):
                self.draw_text(screen, "[OK] COMPLETADO", WIDTH - 220, 175 + i*130, color=(100, 255, 100), bold=True)

    def _draw_details(self, screen):
        sbc = self.current_sbcs[self.selected_idx]
        pygame.draw.rect(screen, (30, 35, 60), (50, 50, WIDTH-100, 620), border_radius=20)
        
        self.draw_text(screen, sbc["name"], WIDTH//2, 90, size=28, center=True, bold=True, color=UI_ACCENT)
        self.draw_text(screen, sbc["desc"], WIDTH//2, 130, size=16, center=True, color=UI_TEXT_DIM)

        # Requisitos
        start_y = 170
        self.draw_text(screen, "REQUISITOS:", 100, start_y, size=18, bold=True, color=WHITE)
        for i, req in enumerate(sbc["reqs"]):
            txt = self._format_requirement(req)
            met = self._check_individual_req(req)
            col = (100, 255, 100) if met else (255, 100, 100)
            self.draw_text(screen, txt, 120, start_y + 35 + i*30, size=16, color=col)

        # Slots de jugadores
        needed = self._get_sbc_slots_count(sbc)

        self.draw_text(screen, "TU PLANTILLA SBC:", 100, 380, size=18, bold=True)
        
        slot_w, slot_h = 100, 140
        for i in range(needed):
            x = 100 + i * 110
            y = 420
            rect = pygame.Rect(x, y, slot_w, slot_h)
            is_sel = (self.picking_slot_idx == i)
            
            pygame.draw.rect(screen, (20, 25, 45), rect, border_radius=10)
            if is_sel: pygame.draw.rect(screen, UI_ACCENT, rect, 2, border_radius=10)
            
            p = self.sbc_slots[i]
            if p:
                card_renderer.render_card(screen, p, x, y, scale=0.55)
            else:
                self.draw_text(screen, "+", x + slot_w//2, y + slot_h//2, center=True, size=30, color=(50, 60, 90))

        can_complete = self._check_all_requirements()
        btn_col = UI_ACCENT if can_complete else (80, 80, 80)
        pygame.draw.rect(screen, btn_col, (WIDTH//2 - 150, 600, 300, 50), border_radius=10)
        self.draw_text(screen, "COMPLETAR DESAFÍO", WIDTH//2, 625, center=True, bold=True, color=WHITE)
        
        self.draw_text(screen, "[ENTER] Seleccionar Slot   [X] Quitar Jugador   [SPACE] Enviar", WIDTH//2, 680, center=True, size=14, color=UI_TEXT_DIM)

    def _draw_inventory_picker(self, screen):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 230))
        screen.blit(overlay, (0, 0))
        
        self.draw_text(screen, "SELECCIONA UN JUGADOR PARA EL SBC", WIDTH//2, 50, size=24, bold=True, center=True, color=GOLD)
        
        if self._cached_inv is None:
            all_p = self.um.club_items["players"]
            used_uids = {p["uid"] for p in self.sbc_slots if p}
            active_uids = {p["uid"] for p in self.um.squad if p}
            self._cached_inv = [p for p in all_p if p["uid"] not in used_uids and p["uid"] not in active_uids]
            from data.rosters import calculate_ovr
            for p in self._cached_inv: p["ovr"] = calculate_ovr(p)
            # Ordenación Unificada: (Media desc, Nombre asc)
            self._cached_inv.sort(key=lambda x: (-x.get("ovr", 0), x.get("name", "")))

        inv = self._cached_inv
        COLS = 6
        ROWS = 3
        start_idx = self.inv_scroll * COLS
        
        for i in range(COLS * ROWS):
            idx = start_idx + i
            if idx >= len(inv): break
            
            col = i % COLS
            row = i // COLS
            x = 100 + col * 180
            y = 120 + row * 180
            
            p = inv[idx]
            is_sel = (self.inv_selected == idx)
            
            if is_sel:
                pygame.draw.rect(screen, UI_ACCENT, (x-5, y-5, 140, 160), 3, border_radius=10)
            
            card_renderer.render_card(screen, p, x, y, scale=0.7)

        self.draw_text(screen, f"Jugadores disponibles: {len(inv)}", 100, HEIGHT - 50, color=UI_TEXT_DIM)
        self.draw_text(screen, "[ENTER] Confirmar   [ESC] Volver", WIDTH - 300, HEIGHT - 50, color=WHITE)

    def _format_requirement(self, req):
        r_type = req["type"]
        val = req["value"]
        count = req["count"]
        
        # Diccionario para nacionalidades en adjetivos en español
        nat_map = {
            "BRA": "brasileña",
            "ESP": "española",
            "ARG": "argentina",
            "FRA": "francesa",
            "GER": "alemana",
            "ITA": "italiana",
            "ENG": "inglesa",
            "POR": "portuguesa",
            "URU": "uruguaya",
            "MEX": "mexicana",
            "COL": "colombiana",
            "NED": "neerlandesa",
            "BEL": "belga",
            "CRO": "croata",
            "TUR": "turca",
            "SEN": "senegalesa",
            "USA": "estadounidense",
            "MAR": "marroquí",
            "CHI": "chilena",
            "PAR": "paraguaya",
            "ECU": "ecuatoriana",
            "VEN": "venezolana",
            "SWE": "sueca",
            "NOR": "noruega",
            "RUS": "rusa",
            "SUI": "suiza",
            "DEN": "danesa",
            "POL_NT": "polaca",
            "UKR": "ucraniana",
            "GRE": "griega",
            "SCO": "escocesa",
            "WAL": "galesa",
            "PER": "peruana",
            "BOL": "boliviana",
            "KOR": "surcoreana",
            "AUS": "australiana",
            "EGY": "egipcia",
            "NGA": "nigeriana",
            "CMR": "camerunesa",
            "CAN": "canadiense",
            "SRB": "serbia",
            "AUT": "austriaca",
            "CZE": "checa",
            "ROU": "rumana",
            "HUN": "húngara",
            "GHA": "ghanesa",
            "CIV": "marfileña",
            "IRN": "iraní",
            "KSA": "saudí",
            "JAM": "jamaicana",
            "GEO": "georgiana",
            "IRL": "irlandesa",
            "RSA": "sudafricana",
            "IRQ": "iraquí",
            "UZB": "uzbeka",
            "CHN": "china",
            "MLI": "maliense",
            "BFA": "burkinesa",
            "HAI": "haitiana",
            "SLV": "salvadoreña",
            "SVN": "eslovena",
            "MNE": "montenegrina",
            "ISR": "israelí",
            "COD": "congoleña",
            "GUI_NT": "guineana",
            "CPV": "caboverdiana",
            "UAE": "emiratí",
            "JOR": "jordana",
            "NZL": "neozelandesa",
            "GUA": "guatemalteca",
            "CRC": "costarricense",
            "PAN": "panameña",
            "TUN": "tunecina",
            "ALG": "argelina",
            "QAT": "catarí",
            "SVK": "eslovaca",
            "FIN": "finlandesa",
            "ISL": "islandesa",
            "HON": "hondureña",
            "ALB_NT": "albanesa",
            "JPN": "japonesa",
        }
        
        if r_type == "min_ovr":
            if count == 1:
                return f"• 1 jugador con valoración (OVR) mínima de {val}"
            return f"• {count} jugadores con valoración (OVR) mínima de {val}"
            
        elif r_type == "min_nat":
            nat_adj = nat_map.get(str(val).upper(), f"de {val}")
            if nat_adj.startswith("de "):
                nat_phrase = nat_adj
            else:
                nat_phrase = f"{nat_adj}"
                
            if count == 1:
                return f"• 1 jugador de nacionalidad {nat_phrase}"
            return f"• {count} jugadores de nacionalidad {nat_phrase}"
            
        elif r_type == "rarity":
            rarity_str = str(val).capitalize()
            if count == 1:
                return f"• 1 jugador de calidad {rarity_str}"
            return f"• {count} jugadores de calidad {rarity_str}"
            
        elif r_type == "player_name":
            if count == 1:
                return f"• 1 jugador llamado {val}"
            return f"• {count} jugadores llamados {val}"
            
        elif r_type == "total":
            if count == 11:
                return "• Completar la plantilla con 11 jugadores"
            return f"• {count} jugadores en total en la plantilla"
            
        else:
            return f"• {count} de {r_type.upper()}: {val}"

    def _check_individual_req(self, req):
        players = [p for p in self.sbc_slots if p]
        if req["type"] == "total":
            return len(players) >= req["count"]
        
        count = 0
        for p in players:
            if req["type"] == "min_ovr" and p["ovr"] >= req["value"]: count += 1
            elif req["type"] == "min_nat" and p["nat"] == req["value"]: count += 1
            elif req["type"] == "rarity" and p["rarity"] == req["value"]: count += 1
            elif req["type"] == "player_name" and req["value"] in p["name"]: count += 1
            
        return count >= req["count"]

    def _check_all_requirements(self):
        sbc = self.current_sbcs[self.selected_idx]
        if not sbc["reqs"]: return True
        return all(self._check_individual_req(r) for r in sbc["reqs"])

    def _get_sbc_slots_count(self, sbc):
        if not sbc or not sbc.get("reqs"):
            return 0
        if sbc.get("reward_type") == "founder":
            return 0
        total_req = next((r for r in sbc["reqs"] if r["type"] == "total"), None)
        if total_req:
            val = total_req["count"]
        else:
            val = sum(r["count"] for r in sbc["reqs"])
        return min(11, val)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if self.view_mode == "LIST":
                if event.key == pygame.K_ESCAPE:
                    from .ultimate_hub import UltimateHubScene
                    self.manager.transition_to(UltimateHubScene)
                elif event.key == pygame.K_UP and len(self.current_sbcs) > 0: self.selected_idx = max(0, self.selected_idx - 1)
                elif event.key == pygame.K_DOWN and len(self.current_sbcs) > 0: self.selected_idx = min(len(self.current_sbcs)-1, self.selected_idx + 1)
                elif event.key == pygame.K_q: self.cat_idx = (self.cat_idx - 1) % len(self.categories); self._refresh_current_list()
                elif event.key == pygame.K_e: self.cat_idx = (self.cat_idx + 1) % len(self.categories); self._refresh_current_list()
                elif event.key == pygame.K_RETURN and len(self.current_sbcs) > 0:
                    sbc = self.current_sbcs[self.selected_idx]
                    if sbc.get("locked"):
                        self.msg = "ESTE DESAFÍO AÚN NO ESTÁ DISPONIBLE"
                        self.msg_timer = 2.0
                        return
                    if sbc["id"] == "founder_claim":
                        self._claim_founder()
                    else:
                        self.view_mode = "DETAILS"
                        self.sbc_slots = [None] * 11
                        self.picking_slot_idx = 0
                        
            elif self.view_mode == "DETAILS":
                if event.key == pygame.K_ESCAPE: self.view_mode = "LIST"
                elif event.key == pygame.K_LEFT: self.picking_slot_idx = max(0, self.picking_slot_idx - 1)
                elif event.key == pygame.K_RIGHT: 
                    sbc = self.current_sbcs[self.selected_idx]
                    needed = self._get_sbc_slots_count(sbc)
                    self.picking_slot_idx = min(needed - 1, self.picking_slot_idx + 1)
                elif event.key == pygame.K_RETURN:
                    self.view_mode = "PICKING"
                    self._cached_inv = None
                    self.inv_selected = 0
                    self.inv_scroll = 0
                elif event.key == pygame.K_x:
                    self.sbc_slots[self.picking_slot_idx] = None
                elif event.key == pygame.K_SPACE:
                    self._complete_sbc()

            elif self.view_mode == "PICKING":
                if event.key == pygame.K_ESCAPE: self.view_mode = "DETAILS"
                elif event.key == pygame.K_LEFT: self.inv_selected = max(0, self.inv_selected - 1)
                elif event.key == pygame.K_RIGHT: self.inv_selected = min(len(self._cached_inv)-1, self.inv_selected + 1)
                elif event.key == pygame.K_UP: self.inv_selected = max(0, self.inv_selected - 6)
                elif event.key == pygame.K_DOWN: self.inv_selected = min(len(self._cached_inv)-1, self.inv_selected + 6)
                elif event.key == pygame.K_RETURN:
                    if self._cached_inv:
                        p = self._cached_inv[self.inv_selected]
                        self.sbc_slots[self.picking_slot_idx] = p
                        self.view_mode = "DETAILS"
                
                # Ajustar scroll dinámicamente
                COLS = 6
                ROWS = 3
                row_selected = self.inv_selected // COLS
                if row_selected < self.inv_scroll:
                    self.inv_scroll = row_selected
                elif row_selected >= self.inv_scroll + ROWS:
                    self.inv_scroll = row_selected - ROWS + 1

    def _complete_sbc(self):
        if not self._check_all_requirements():
            self.msg = "¡No cumples los requisitos!"; self.msg_timer = 2.0; return
            
        sbc = self.current_sbcs[self.selected_idx]
        # Consumir jugadores
        used_uids = {p["uid"] for p in self.sbc_slots if p}
        self.um.club_items["players"] = [p for p in self.um.club_items["players"] if p["uid"] not in used_uids]
        
        # Recompensa
        reward = sbc.get("reward_type")
        if reward == "player":
            from data.event_worldcup import PELE_SBC_REWARD
            p = copy.deepcopy(PELE_SBC_REWARD)
            p["uid"] = self.um._generate_uid()
            self.um.club_items["players"].append(p)
        elif reward == "pack":
            self.um.add_pack(sbc["reward_data"])
        elif reward == "pack_5":
            # REQUISITO: Que sea un SOBRE en "MIS SOBRES"
            pack_cfg = {
                "id": f"sbc_reward_{sbc['id']}", "name": f"SOBRE {sbc['reward_rarity']} SBC",
                "total_items": 5, "event": "NORMAL", "type": "PACK", "cat": "MIS SOBRES",
                "details": {"min_players": 5, "max_players": 5, "rarity": sbc["reward_rarity"]}
            }
            # En _generate_pack_items de ultimate_manager, si hay details['rarity'], se usará.
            self.um.add_reward_pack(pack_cfg)
            self.msg = "¡Sobre añadido a Mis Sobres!"; self.msg_timer = 3.0
        
        sbc["completed"] = True
        self.um.sbc_state[sbc["id"]] = True
        self.um.save_ultimate()
        self.view_mode = "LIST"
        self.msg = "¡SBC Completado!"; self.msg_timer = 3.0

    def _claim_founder(self):
        # Mismo código que antes...
        pass

    def update(self, dt):
        if self.msg_timer > 0: self.msg_timer -= dt

    def draw_text(self, screen, text, x, y, size=20, color=WHITE, bold=False, center=False):
        font = pygame.font.SysFont("Arial", size, bold=bold)
        surf = font.render(str(text), True, color)
        rect = surf.get_rect()
        if center: rect.center = (x, y)
        else: rect.topleft = (x, y)
        screen.blit(surf, rect)
