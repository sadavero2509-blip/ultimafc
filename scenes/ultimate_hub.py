import pygame
import random
import copy
import math
from systems.ultimate_manager import ultimate_manager
from systems.card_renderer import card_renderer
from data.teams import TEAMS
from settings import FORMATIONS, WIDTH, HEIGHT, WHITE, UI_ACCENT, UI_TEXT_DIM, GOLD, RED
from data.evolutions import EVOLUTIONS_DB, check_evolution_eligibility

TEAL = (0, 200, 200)

COIN_BUNDLES = [
    {"id": "bundle_500fp", "name": "500 FC POINTS", "price_usd": 0.99, "fc_points": 500, "details": {"players": "500 FC Points", "guaranteed": "+500 FP"}, "color_tier": "BRONCE", "type": "FC_POINTS_BUNDLE"},
    {"id": "bundle_1050fp", "name": "1,050 FC POINTS", "price_usd": 1.99, "fc_points": 1050, "details": {"players": "1050 FC Points", "guaranteed": "+1050 FP"}, "color_tier": "PLATA", "type": "FC_POINTS_BUNDLE"},
    {"id": "bundle_2800fp", "name": "2,800 FC POINTS", "price_usd": 4.99, "fc_points": 2800, "details": {"players": "2,800 FC Points", "guaranteed": "+2800 FP"}, "color_tier": "ORO", "type": "FC_POINTS_BUNDLE"},
    {"id": "bundle_5800fp", "name": "5,800 FC POINTS", "price_usd": 9.99, "fc_points": 5800, "details": {"players": "5,800 FC Points", "guaranteed": "+5800 FP"}, "color_tier": "ELITE", "type": "FC_POINTS_BUNDLE"},
    {"id": "bundle_12000fp", "name": "12,000 FC POINTS", "price_usd": 19.99, "fc_points": 12000, "details": {"players": "12,000 FC Points", "guaranteed": "+12000 FP"}, "color_tier": "ELITE", "type": "FC_POINTS_BUNDLE"}
]

class UltimateHubScene:
    def __init__(self, manager):
        self.manager = manager
        self.fonts = {} # Caché de fuentes
        self.market_menu_data = [
            {"title": "MERCADO GLOBAL", "desc": ["Busca y compra jugadores", "de todo el mundo."], "col": (0, 100, 200)},
            {"title": "MIS SUBASTAS", "desc": ["Gestiona los jugadores", "que tienes a la venta."], "col": (255, 215, 0)}
        ]
        self.tab = "PLAY"
        self.selected_idx = 0
        self.msg = ""
        self.msg_timer = 0
        self.detail_mode = False
        self.confirm_exit = False
        
        self.evo_state = "EVO_SELECT" # PLAYER_SELECT, EVO_SELECT
        self.evo_player = None
        self.evo_player_idx = 0
        self.club_tab = "MENU"
        self.club_mode = "LINEUP"
        self.club_menu_idx = 0
        self.search_mode = False
        self.evo_idx = 0
        self.tactic_section = "FORMATION"
        self.tactic_sel = 0
        self.swap_idx = None
        self.search_query = ""
        self.filter_row = 0
        self.f_pos_idx = 0
        self.f_class_idx = 0
        self.f_evt_idx = 0
        self.f_show_all = False # Nueva opción para ver todo el club
        
        self.market_tab = "MENU"      # MENU, GLOBAL, MY_AUCTIONS
        self.market_menu_idx = 0
        self.market_state = "FILTERS" # FILTERS, RESULTS
        self.market_filter_row = 0
        self.m_pos_idx = 0
        self.m_class_idx = 0
        self.market_results = []
        
        self.management_state = "MAIN"      # MAIN, RENAME, RESET
        self.input_text = ""
        self.listing_mode = False           # Si estamos poniendo un jugador a la venta
        self.list_bid = 0
        self.list_buy = 0
        self.list_ranges = {"min": 0, "max": 0}
        self.list_step = 100
        self.list_sel = 0                   # 0: Bid, 1: Buy Now
        self.sell_confirm_idx = None        # Para evitar ventas accidentales
        self.reveal_timer = 0               # Para efectos visuales en sobres
        
        self.colors = {
            "bg": (10, 12, 22),
            "panel": (22, 28, 45),
            "panel_light": (35, 42, 65),
            "accent": (0, 220, 255),
            "gold": (255, 215, 0),
            "red": (255, 60, 60),
            "text_dim": (160, 175, 200)
        }
        self.tab_timer = 0
        self.pack_reveal_items = None
        self.reveal_idx = 0
        self.dup_scroll = 0
        self.reveal_scroll = 0
        self.mgmt_scroll = 0
        self.store_cat = "NORMAL"
        self.market_tick_timer = 0          # Temporizador para la actividad del bot
        
        # Superficies pre-renderizadas para optimización
        self.header_gradient = pygame.Surface((WIDTH, 150), pygame.SRCALPHA)
        for y in range(0, 150):
            alpha = max(0, 255 - y * 1.7)
            pygame.draw.line(self.header_gradient, (15, 25, 50, alpha), (0, y), (WIDTH, y))
            
        self.selection_glow = pygame.Surface((200, 290), pygame.SRCALPHA)
        pygame.draw.rect(self.selection_glow, (255, 255, 255, 60), (0, 0, 200, 290), border_radius=15)
        
        # Forzar refresco de medias al entrar para asegurar sincronía entre Club y Alineación
        ultimate_manager.refresh_all_ovrs()

    def update(self, dt):
        self.tab_timer += dt
        if self.msg_timer > 0:
            self.msg_timer -= dt
            
        if self.pack_reveal_items:
            self.reveal_timer += 1
            
        # Simulación del mercado (cada 10 segundos el bot revisa algo)
        self.market_tick_timer += dt
        if self.market_tick_timer >= 10.0:
            import threading
            threading.Thread(target=ultimate_manager.simulate_market_tick, daemon=True).start()
            self.market_tick_timer = 0
            self._cached_my_auctions = None

    def draw(self, screen):
        # Bloqueo si no hay conexión al servidor
        if ultimate_manager.online_status == "OFFLINE_ERROR":
            screen.fill((10, 10, 25))
            # Dibujar un icono de "No Señal"
            cx, cy = WIDTH//2, HEIGHT//2 - 50
            pygame.draw.circle(screen, (150, 50, 50), (cx, cy), 60, 4)
            pygame.draw.line(screen, (150, 50, 50), (cx-40, cy-40), (cx+40, cy+40), 6)
            
            self.draw_text(screen, "MODO ULTIMATE TEAM - SIN CONEXIÓN", WIDTH//2, cy + 100, size=32, bold=True, color=WHITE, center=True)
            self.draw_text(screen, ultimate_manager.connection_error_msg, WIDTH//2, cy + 150, size=20, color=(200, 100, 100), center=True)
            self.draw_text(screen, "Este modo requiere una conexión activa con el servidor central.", WIDTH//2, cy + 200, size=16, color=UI_TEXT_DIM, center=True)
            self.draw_text(screen, "Verifica tu server_config.json y asegúrate de que el servidor esté corriendo.", WIDTH//2, cy + 230, size=14, color=UI_TEXT_DIM, center=True)
            self.draw_text(screen, "PULSA [R] PARA REINTENTAR CONEXIÓN", WIDTH//2, HEIGHT - 150, size=18, bold=True, color=self.colors["accent"], center=True)
            self.draw_text(screen, "PULSA [ESC] PARA VOLVER AL MENÚ", WIDTH//2, HEIGHT - 100, size=18, bold=True, color=WHITE, center=True)
            return

        screen.fill(self.colors["bg"])
        
        # Fondo con degradado pre-renderizado
        screen.blit(self.header_gradient, (0,0))

        # Header / Tabs
        self._draw_tabs(screen)
        

        
        # Contenido por pestaña
        if self.tab == "PLAY":
            self._draw_play(screen)
        elif self.tab == "CLUB":
            self._draw_club(screen)
        elif self.tab == "MARKET":
            self._draw_market(screen)
        elif self.tab == "STORE":
            self._draw_store(screen)

        elif self.tab == "EVOLUTIONS":
            self._draw_evolutions(screen)
        elif self.tab == "SBC":
            self._draw_sbc_preview(screen)
        elif self.tab == "OBJECTIVES":
            self._draw_objectives(screen)

        # Stats rápidas (Dibuja sobre el contenido para evitar que se tape)
        # Stats rápidas (Dibuja sobre el contenido para evitar que se tape)
        # Monedas (Pill Derecha)
        coin_rect = pygame.Rect(WIDTH - 160, 95, 140, 35)
        pygame.draw.rect(screen, (20, 25, 45), coin_rect, border_radius=10)
        pygame.draw.rect(screen, self.colors["gold"], coin_rect, 1, border_radius=10)
        
        # Dibujar MONEDA VECTORIAL (Círculo oro con C)
        cx, cy = coin_rect.left + 20, coin_rect.centery
        pygame.draw.circle(screen, self.colors["gold"], (cx, cy), 12)
        pygame.draw.circle(screen, (150, 120, 0), (cx, cy), 12, 1)
        self.draw_text(screen, "C", cx, cy - 7, size=14, color=(80, 60, 0), bold=True, center=True)
        self.draw_text(screen, f"{ultimate_manager.coins:,}", cx + 20, cy - 10, size=18, color=self.colors["gold"], bold=True)
        
        # Cronómetro para nuevos eventos
        if self.tab in ["STORE", "EVOLUTIONS"]:
            self._draw_countdown(screen)
            
        # OVERLAY DE SELECCIÓN DE PICK (NUEVO)
        if hasattr(self, "active_pick") and self.active_pick:
            self._draw_pick_selection(screen)
            
        # OVERLAY DE DETALLES DE JUGADOR
        if self.detail_mode:
            self._draw_player_details(screen)

        # Mensajes temporales
        if self.msg_timer > 0:
            self._draw_toast(screen)

        # Overlay de apertura de sobre
        if self.pack_reveal_items:
            self._draw_pack_reveal(screen)

        # Overlay de listado en mercado
        if self.listing_mode:
            self._draw_listing_overlay(screen)

        # Overlay de fundador si es necesario
        if ultimate_manager.check_founder_reward():
            self._draw_founder_overlay(screen)

    def _draw_toast(self, screen):
        msg_surf = pygame.Surface((400, 50), pygame.SRCALPHA)
        pygame.draw.rect(msg_surf, (0, 0, 0, 200), (0, 0, 400, 50), border_radius=10)
        screen.blit(msg_surf, (WIDTH//2 - 200, HEIGHT - 80))
        self.draw_text(screen, self.msg, WIDTH//2, HEIGHT - 55, size=18, color=WHITE, center=True)

    def _draw_countdown(self, screen):
        """Dibuja un cronómetro si hay contenido próximo a lanzarse."""
        import datetime
        promo_start = datetime.datetime(2026, 8, 26, 15, 0)
        launch_time = datetime.datetime(2026, 9, 26, 15, 0)
        now = datetime.datetime.now()
        
        if promo_start <= now < launch_time:
            diff = launch_time - now
            hours, remainder = divmod(int(diff.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            time_str = f"{hours:02}:{minutes:02}:{seconds:02}"
            
            # Banner de cuenta atrás
            banner_rect = pygame.Rect(WIDTH - 320, 95, 280, 40)
            pygame.draw.rect(screen, (255, 50, 50), banner_rect, border_radius=10)
            self.draw_text(screen, f"EVENTO EN: {time_str}", banner_rect.centerx, banner_rect.centery - 8, size=16, color=WHITE, center=True, bold=True)

    def _draw_founder_overlay(self, screen):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 230))
        screen.blit(overlay, (0, 0))
        
        self.draw_text(screen, "¡RECOMPENSA DE FUNDADOR!", WIDTH//2, 100, size=40, color=self.colors["gold"], bold=True, center=True)
        self.draw_text(screen, "Elige una LEYENDA para liderar tu club este año.", WIDTH//2, 160, size=20, color=WHITE, center=True)
        
        options = ultimate_manager.legend_pick_options
        for i, p in enumerate(options):
            x = WIDTH//2 - 300 + i * 220
            y = 250
            scale = 1.0
            is_sel = (self.selected_idx == i)
            if is_sel:
                pygame.draw.rect(screen, (255, 215, 0), (x-10, y-10, 180, 260), 4, border_radius=15)
                self.draw_text(screen, "SELECCIONAR", x + 30, y + 270, size=18, color=(255, 215, 0), bold=True)
            
            card_renderer.render_card(screen, p, x, y, scale=scale)
        
        self.draw_text(screen, "Usa ← → y ENTER para reclamar tu recompensa", WIDTH//2 - 180, HEIGHT - 100, size=18, color=UI_TEXT_DIM)

    def _draw_tabs(self, screen):
        # Header Moderno estilo EA FC / FIFA
        pygame.draw.rect(screen, (10, 15, 30), (0, 0, WIDTH, 85))
        pygame.draw.line(screen, (50, 60, 100), (0, 85), (WIDTH, 85), 2)
        
        tabs = [
            ("PLAY", "INICIO"),
            ("CLUB", "PLANTILLA"),
            ("MARKET", "MERCADO"),
            ("STORE", "TIENDA"),
            ("EVOLUTIONS", "EVOS"),
            ("SBC", "INTERCAMBIOS"),
            ("OBJECTIVES", "OBJETIVOS")
        ]
        
        tab_w = WIDTH // len(tabs)
        for i, (tab_id, t_name) in enumerate(tabs):
            x = i * tab_w
            is_active = (self.tab == tab_id)
            
            if is_active:
                # Fondo de pestaña activa con gradiente
                active_rect = pygame.Rect(x, 0, tab_w, 85)
                pygame.draw.rect(screen, (30, 45, 80), active_rect)
                pygame.draw.rect(screen, self.colors["accent"], (x, 81, tab_w, 4))
                
            color = WHITE if is_active else self.colors["text_dim"]
            # Ícono central dibujado manualmente
            self._draw_tab_icon(screen, tab_id, x + tab_w//2, 32, color)
            # Texto inferior
            self.draw_text(screen, t_name, x + tab_w//2, 60, size=14, color=color, bold=is_active, center=True)
            
            # Separador vertical sutil
            if i < len(tabs) - 1:
                pygame.draw.line(screen, (40, 50, 80), (x + tab_w, 20), (x + tab_w, 65), 1)

        # Teclas rápidas L1/R1
        self.draw_text(screen, "[Q] L1", 20, 35, size=12, color=UI_TEXT_DIM)
        self.draw_text(screen, "R1 [E]", WIDTH - 60, 35, size=12, color=UI_TEXT_DIM)

    def _draw_tab_icon(self, screen, tab_id, x, y, color):
        """Dibuja iconos geométricos para las pestañas (evita problemas de emojis)."""
        if tab_id == "PLAY":
            # Triángulo de Play
            pts = [(x-10, y-10), (x+12, y), (x-10, y+10)]
            pygame.draw.polygon(screen, color, pts)
        elif tab_id == "CLUB":
            # Escudo
            pts = [(x-10, y-12), (x+10, y-12), (x+10, y+2), (x, y+12), (x-10, y+2)]
            pygame.draw.polygon(screen, color, pts, 2)
        elif tab_id == "MARKET":
            # Símbolo de intercambio/mercado
            pygame.draw.circle(screen, color, (x, y), 10, 2)
            pygame.draw.line(screen, color, (x-12, y), (x+12, y), 2)
        elif tab_id == "STORE":
            # Bolsa/Sobre
            pygame.draw.rect(screen, color, (x-10, y-8, 20, 16), 2, border_radius=2)
            pygame.draw.line(screen, color, (x-10, y-8), (x, y), 2)
            pygame.draw.line(screen, color, (x+10, y-8), (x, y), 2)
        elif tab_id == "EVOLUTIONS":
            # Rayo
            pts = [(x+2, y-12), (x-8, y+2), (x-2, y+2), (x-2, y+12), (x+8, y-2), (x+2, y-2)]
            pygame.draw.polygon(screen, color, pts)
        elif tab_id == "MANAGEMENT":
            # Engranaje simplificado
            pygame.draw.circle(screen, color, (x, y), 8, 2)
            for i in range(4):
                ang = i * (math.pi / 2)
                px, py = math.cos(ang)*11, math.sin(ang)*11
                pygame.draw.line(screen, color, (x, y), (x+px, y+py), 3)

    def _draw_play(self, screen):
        self.draw_text(screen, "MODOS DE JUEGO", 50, 110, size=28, color=self.colors["accent"], bold=True)
        
        # Panel Principal Ampliado
        play_panel = pygame.Rect(50, 160, 750, 530)
        pygame.draw.rect(screen, self.colors["panel"], play_panel, border_radius=20)
        pygame.draw.rect(screen, (50, 60, 100), play_panel, 1, border_radius=20)
        
        # --- SELECCIÓN DE MODO DE JUEGO ---
        modes = [
            ("AMISTOSO RÁPIDO", "Juega contra un rival al azar", 1200),
            ("LIGA DE CLUBES", "Liga offline contra la IA", 2500),
            ("DIVISION RIVALS", "Liga ONLINE contra jugadores reales", 3500),
            ("TORNEO ELIMINATORIO", "Gana o vete a casa", 5000)
        ]
        
        for i, (name, desc, reward) in enumerate(modes):
            is_sel = (self.selected_idx == i)
            y = 180 + i * 115 # Espaciado ajustado para 4 elementos
            m_rect = pygame.Rect(80, y, 690, 95)
            
            bg_col = (40, 50, 90) if is_sel else (30, 32, 55)
            pygame.draw.rect(screen, bg_col, m_rect, border_radius=18)
            if is_sel:
                pygame.draw.rect(screen, self.colors["accent"], m_rect, 2, border_radius=18)

            self.draw_text(screen, name, 110, y + 20, size=22, bold=True, color=WHITE if is_sel else UI_TEXT_DIM)
            self.draw_text(screen, desc, 110, y + 55, size=15, color=UI_TEXT_DIM)
            
            # Recompensa a la derecha
            self.draw_text(screen, f"$ {reward}", 640, y + 30, size=22, color=GOLD, bold=True)
            if is_sel:
                self.draw_text(screen, "[ENTER] JUGAR", 640, y + 65, size=12, color=self.colors["accent"], bold=True)

        # ── PANEL DE STATUS DEL CLUB (DERECHA) ──
        status_rect = pygame.Rect(820, 160, 410, 400)
        pygame.draw.rect(screen, self.colors["panel"], status_rect, border_radius=20)
        pygame.draw.rect(screen, (50, 60, 100), status_rect, 1, border_radius=20)
        
        self.draw_text(screen, "ESTADO DEL CLUB", 840, 185, size=18, bold=True, color=GOLD)
        
        # Bloques de información
        info_blocks = [
            ("Monedas Actuales", f"{ultimate_manager.coins:,}", "$"),
            ("Jugadores en Club", str(len(ultimate_manager.club_items["players"])), "[Club]"),
            ("Formación Activa", ultimate_manager.formation, "[Form]"),
            ("Victorias Totales", str(ultimate_manager.stats["wins"]), "[Wins]"),
            ("Goles Marcados", str(ultimate_manager.stats["gf"]), "[Goles]")
        ]
        
        for i, (label, val, icon) in enumerate(info_blocks):
            y = 230 + i * 60
            pygame.draw.line(screen, (40, 50, 80), (840, y + 45), (1190, y + 45), 1)
            self.draw_text(screen, icon, 840, y + 8, size=14, color=GOLD)
            self.draw_text(screen, label, 900, y + 5, size=16, color=WHITE)
            self.draw_text(screen, val, 1180, y + 5, size=18, bold=True, color=self.colors["accent"], center=True)

        # Ticker de noticias/consejos inferior
        pygame.draw.rect(screen, (20, 25, 45), (50, 580, 1180, 50), border_radius=10)
        tips = ["CONSEJO: Usa el Mercado para mejorar tus posiciones débiles.", "TIP: Las Evoluciones mejoran stats permanentemente.", "INFO: El Capitán recibe un ligero boost de moral."]
        active_tip = tips[int(pygame.time.get_ticks()/3000) % len(tips)]
        self.draw_text(screen, f"[TIP] {active_tip}", 70, 595, size=15, color=TEAL)

    def _get_squad_positions(self):
        """Calcula las coordenadas de pantalla para los 11 titulares y 7 suplentes."""
        from settings import FORMATIONS
        pitch_rect = pygame.Rect(50, 160, 720, 450)
        p_w, p_h = 720, 450
        form_coords = FORMATIONS.get(ultimate_manager.formation, FORMATIONS["4-3-3"])
        
        # Titulares (11)
        positions = [(pitch_rect.left + 45, pitch_rect.top + 225 - 20)] # GK
        for fx, fy in form_coords:
            px = int(fx * (p_w * 1.6))
            py = int(fy * p_h)
            px = max(150, min(650, px))
            py = max(40, min(410, py))
            positions.append((pitch_rect.left + px, pitch_rect.top + py - 20))
            
        # Banca (7) - Ajustado para evitar salirse de pantalla
        for i in range(7):
            positions.append((70 + i * 105, 615))
            
        return positions

    def _get_duplicate_list(self):
        """Devuelve una lista de jugadores con copias extra en el club (agrupado por tipo específico de carta)."""
        from collections import Counter
        all_p = ultimate_manager.club_items.get("players", [])
        
        # Agrupamos por los campos que definen inequívocamente la versión/tipo de la carta
        card_count = Counter((p["name"], p.get("card_type", "NORMAL"), p.get("ovr", 0), p.get("is_legend", False)) for p in all_p)
        
        seen = set()
        duplicates = []
        for (name, card_type, ovr, is_legend), count in card_count.items():
            if count >= 2 and (name, card_type, ovr, is_legend) not in seen:
                seen.add((name, card_type, ovr, is_legend))
                indices = [
                    i for i, p in enumerate(all_p) 
                    if p["name"] == name 
                    and p.get("card_type", "NORMAL") == card_type 
                    and p.get("ovr", 0) == ovr 
                    and p.get("is_legend", False) == is_legend
                ]
                ref = all_p[indices[0]]
                duplicates.append({
                    "name": name,
                    "pos": ref.get("pos", "?"),
                    "ovr": ovr,
                    "card_type": card_type,
                    "nat": ref.get("nat", "?"),
                    "copies": count - 1,
                    "total": count,
                    "indices": indices,
                    "last_uid": all_p[indices[-1]].get("uid"),
                    "is_legend": is_legend,
                })
        duplicates.sort(key=lambda x: x["ovr"], reverse=True)
        return duplicates

    def _draw_duplicates_panel(self, screen):
        """Panel lateral que muestra los jugadores repetidos del club."""
        self.draw_text(screen, "JUGADORES REPETIDOS", 800, 130, size=22, bold=True, color=self.colors["red"])
        
        dups = self._get_duplicate_list()
        total_copies = sum(d["copies"] for d in dups)
        
        # Header con resumen
        header_rect = pygame.Rect(800, 170, 435, 50)
        pygame.draw.rect(screen, (50, 30, 30), header_rect, border_radius=10)
        self.draw_text(screen, f"Total Repetidos: {len(dups)} jugadores ({total_copies} copias)", 815, 185, size=14, color=WHITE)
        
        if not dups:
            self.draw_text(screen, "¡No tienes jugadores repetidos!", 1017, 400, size=18, color=UI_TEXT_DIM, center=True)
            self.draw_text(screen, "[ESC/D] Volver", 1017, 650, size=14, color=UI_TEXT_DIM, center=True)
            return
        
        # Lista scrolleable
        visible = 10
        start = self.dup_scroll
        end = min(start + visible, len(dups))
        
        for i, d in enumerate(dups[start:end]):
            y = 235 + i * 40
            is_sel = (self.selected_idx == start + i)
            
            row_rect = pygame.Rect(800, y, 435, 36)
            if is_sel:
                pygame.draw.rect(screen, (60, 40, 40), row_rect, border_radius=8)
                pygame.draw.rect(screen, self.colors["red"], row_rect, 2, border_radius=8)
            else:
                pygame.draw.rect(screen, (30, 25, 35), row_rect, border_radius=8)
            
            # OVR
            ovr_col = GOLD if d["ovr"] >= 85 else WHITE
            self.draw_text(screen, str(d["ovr"]), 820, y + 8, size=16, color=ovr_col, bold=True)
            
            # Posición
            self.draw_text(screen, d["pos"], 860, y + 8, size=13, color=UI_TEXT_DIM)
            
            # Nombre
            name_col = GOLD if d["is_legend"] else WHITE
            self.draw_text(screen, d["name"][:18], 900, y + 8, size=14, color=name_col)
            
            # Nacionalidad
            self.draw_text(screen, d["nat"], 1110, y + 8, size=13, color=UI_TEXT_DIM)
            
            # Badge de copias
            badge_col = (200, 50, 50) if d["copies"] >= 3 else (180, 120, 30)
            badge_rect = pygame.Rect(1160, y + 4, 60, 28)
            pygame.draw.rect(screen, badge_col, badge_rect, border_radius=8)
            self.draw_text(screen, f"x{d['copies']}", 1190, y + 8, size=14, color=WHITE, center=True, bold=True)
        
        # Scroll indicator
        if len(dups) > visible:
            self.draw_text(screen, f"{start+1}-{end} de {len(dups)}", 1017, 645, size=12, color=UI_TEXT_DIM, center=True)
        
        # Controles
        self.draw_text(screen, "[↑↓] Navegar   [X] Vender Copia   [D/ESC] Volver", 1017, 670, size=12, color=UI_TEXT_DIM, center=True)

    def _draw_club(self, screen):
        if self.club_tab == "MENU":
            self._draw_club_main_menu(screen)
        elif self.club_tab == "EQUIPO":
            if not hasattr(self, "_cached_subs") or self._cached_subs is None:
                all_players = ultimate_manager.club_items["players"]
                starters = [p for p in ultimate_manager.squad if p]
                starter_names = {p["name"] for p in starters}
                starter_uids = {p.get("uid") for p in starters}
                # Excluir si la carta específica ya es titular O si ya hay alguien con ese nombre en el XI
                self._cached_subs = [p for p in all_players if p.get("uid") not in starter_uids and p["name"] not in starter_names][:7]
            self._draw_club_lineup(screen)
        elif self.club_tab == "MI_CLUB":
            if not hasattr(self, "_cached_inv") or self._cached_inv is None:
                from data.rosters import calculate_ovr
                all_p = ultimate_manager.club_items.get("players", [])[:]
                for p in all_p: p["ovr"] = calculate_ovr(p)
                all_p.sort(key=lambda x: (x.get("ovr", 0), x.get("name", "")), reverse=True)
                self._cached_inv = all_p
            self._draw_club_inventory(screen)
        elif self.club_tab == "DUPLICADOS":
            if not hasattr(self, "_cached_dups") or self._cached_dups is None:
                self._cached_dups = self._get_duplicate_list()
            self._draw_duplicates_panel_full(screen)
        elif self.club_tab == "GESTIÓN":
            self._draw_management(screen)

    def _draw_club_main_menu(self, screen):
        """Menú principal del Club con tarjetas grandes."""
        self.draw_text(screen, "CENTRO DE MANDO DEL CLUB", WIDTH//2, 120, size=32, bold=True, color=GOLD, center=True)
        
        menus = [
            ("MI EQUIPO", "Gestiona tu alineación, formación y capitán.", (50, 80, 150)),
            ("MI CLUB", "Examina toda tu colección de jugadores e ítems.", (40, 120, 80)),
            ("REPETIDOS", "Vende o gestiona tus jugadores duplicados.", (150, 50, 50)),
            ("GESTIÓN", "Ajustes, cambio de nombre y guardado de datos.", (100, 100, 100))
        ]
        
        card_w, card_h = 280, 400
        total_w = len(menus) * (card_w + 20) - 20
        start_x = (WIDTH - total_w) // 2
        
        for i, (title, desc, col) in enumerate(menus):
            is_sel = (self.club_menu_idx == i)
            x = start_x + i * (card_w + 20)
            y = 200
            
            rect = pygame.Rect(x, y, card_w, card_h)
            # Sombra y fondo
            bg_col = tuple(min(255, c + 30) for c in col) if is_sel else col
            pygame.draw.rect(screen, bg_col, rect, border_radius=15)
            
            if is_sel:
                pygame.draw.rect(screen, WHITE, rect, 3, border_radius=15)
                # Brillo animado
                glow = math.sin(pygame.time.get_ticks() * 0.01) * 5 + 5
                pygame.draw.rect(screen, WHITE, (x-glow, y-glow, card_w+glow*2, card_h+glow*2), 1, border_radius=18)
            
            # Título e Info
            self.draw_text(screen, title, x + card_w//2, y + 50, size=24, bold=True, color=WHITE, center=True)
            
            # Separador
            pygame.draw.line(screen, (255,255,255,100), (x + 40, y + 90), (x + card_w - 40, y + 90), 2)
            
            # Descripción (wrap manual simple)
            words = desc.split()
            line1 = " ".join(words[:len(words)//2])
            line2 = " ".join(words[len(words)//2:])
            self.draw_text(screen, line1, x + card_w//2, y + 130, size=14, color=WHITE, center=True)
            self.draw_text(screen, line2, x + card_w//2, y + 155, size=14, color=WHITE, center=True)
            
            # Indicador de selección
            if is_sel:
                self.draw_text(screen, "PULSA ENTER PARA ENTRAR", x + card_w//2, y + card_h - 40, size=14, bold=True, color=WHITE, center=True)

        self.draw_text(screen, "[← →] Seleccionar categoría  [ENTER] Confirmar  [ESC] Volver", WIDTH//2, HEIGHT - 50, size=16, color=UI_TEXT_DIM, center=True)

    def _draw_club_inventory(self, screen):
        """Muestra todos los jugadores del club en una cuadrícula amplia."""
        self.draw_text(screen, "MI COLECCIÓN", 50, 160, size=24, bold=True, color=self.colors["accent"])
        
        all_p = self._cached_inv if hasattr(self, "_cached_inv") else []
        
        # Grid de 6x2 o 6x3 dependiendo del espacio
        cols, rows = 6, 2
        cell_w, cell_h = 160, 220
        start_y = 200
        
        visible_count = cols * rows
        # Navegación por la cuadrícula
        start_idx = (self.selected_idx // cols) * cols
        
        for i in range(visible_count):
            idx = start_idx + i
            if idx >= len(all_p): break
            
            p = all_p[idx]
            col = i % cols
            row = i // cols
            x = 80 + col * (cell_w + 30)
            y = start_y + row * (cell_h + 30)
            
            is_sel = (self.selected_idx == idx)
            if is_sel:
                pygame.draw.rect(screen, self.colors["accent"], (x-5, y-5, cell_w+10, cell_h+10), 3, border_radius=15)
            
            card_renderer.render_card(screen, p, x, y, scale=0.48)

        # Info de scroll y controles
        self.draw_text(screen, f"Mostrando {start_idx + 1}-{min(start_idx + visible_count, len(all_p))} de {len(all_p)} jugadores", 50, HEIGHT - 50, size=14, color=UI_TEXT_DIM)
        self.draw_text(screen, "[FLECHAS] Navegar  [I] Detalles  [V] Venta Rápida", WIDTH - 450, HEIGHT - 50, size=14, color=UI_TEXT_DIM)

    def _draw_duplicates_panel_full(self, screen):
        """Versión ampliada de la gestión de repetidos."""
        self.draw_text(screen, "DEPÓSITO DE DUPLICADOS", 50, 160, size=24, bold=True, color=self.colors["red"])
        
        dups = self._cached_dups if hasattr(self, "_cached_dups") and self._cached_dups is not None else self._get_duplicate_list()
        total_copies = sum(d["copies"] for d in dups)
        
        # Panel central grande
        list_rect = pygame.Rect(50, 200, WIDTH - 100, 420)
        pygame.draw.rect(screen, self.colors["panel"], list_rect, border_radius=15)
        pygame.draw.rect(screen, (50, 30, 30), list_rect, 2, border_radius=15)
        
        if not dups:
            self.draw_text(screen, "¡No tienes jugadores repetidos actualmente!", WIDTH//2, 400, size=20, color=UI_TEXT_DIM, center=True)
            return

        self.draw_text(screen, f"Tienes {total_copies} copias extra de {len(dups)} jugadores.", 70, 220, size=16, color=WHITE)

        visible_count = 12
        start_idx = self.dup_scroll
        end_idx = min(start_idx + visible_count, len(dups))

        for i in range(start_idx, end_idx):
            d = dups[i]
            y = 260 + (i - start_idx) * 35
            is_sel = (self.selected_idx == i)
            if is_sel: 
                pygame.draw.rect(screen, (60, 40, 40), (60, y-5, WIDTH-120, 30), border_radius=5)
                pygame.draw.rect(screen, self.colors["red"], (60, y-5, WIDTH-120, 30), 1, border_radius=5)
            
            ovr_col = GOLD if d["ovr"] >= 85 else WHITE
            self.draw_text(screen, f"{d['ovr']}", 80, y, size=16, color=ovr_col, bold=True)
            self.draw_text(screen, f"{d['pos']} {d['name']}", 130, y, size=16, color=WHITE)
            
            # Badge de copias
            badge_rect = pygame.Rect(WIDTH - 180, y-2, 60, 24)
            pygame.draw.rect(screen, (200, 50, 50), badge_rect, border_radius=6)
            self.draw_text(screen, f"x{d['copies']}", WIDTH - 150, y, size=14, color=WHITE, center=True, bold=True)

        self.draw_text(screen, f"Mostrando {start_idx+1}-{end_idx} de {len(dups)} | [↑↓] Seleccionar  [X] Venta Rápida", 70, 640, size=14, color=UI_TEXT_DIM)

    def _draw_club_management(self, screen):
        """Ajustes de club, cambio de nombre y guardado."""
        self.draw_text(screen, "ADMINISTRACIÓN DEL CLUB", 50, 160, size=24, bold=True, color=GOLD)
        
        # Info del club actual
        info_rect = pygame.Rect(50, 200, WIDTH - 100, 80)
        pygame.draw.rect(screen, self.colors["panel"], info_rect, border_radius=12)
        self.draw_text(screen, f"CLUB: {ultimate_manager.team_name} ({ultimate_manager.abbreviation})", 80, 215, size=22, bold=True, color=WHITE)
        self.draw_text(screen, f"Monedas en caja: $ {ultimate_manager.coins:,}", 80, 245, size=14, color=GOLD)

        actions = [
            ("S", "GUARDAR PROGRESO", "Sincroniza tu equipo y monedas con el servidor."),
            ("R", "CAMBIAR NOMBRE", "Modifica el nombre y abreviatura de tu equipo."),
            ("B", "BORRAR CLUB", "Elimina permanentemente tu club para empezar de cero."),
            ("ESC", "VOLVER AL MENÚ", "Guarda y sal al menú principal.")
        ]
        
        for i, (key, title, desc) in enumerate(actions):
            y = 300 + i * 90
            rect = pygame.Rect(50, y, WIDTH - 100, 75)
            pygame.draw.rect(screen, self.colors["panel_light"], rect, border_radius=12)
            pygame.draw.rect(screen, (70, 70, 100), rect, 1, border_radius=12)
            
            self.draw_text(screen, f"[{key}] {title}", 80, y + 15, size=18, bold=True, color=WHITE)
            self.draw_text(screen, desc, 80, y + 42, size=14, color=UI_TEXT_DIM)

    def _draw_listing_overlay(self, screen):
        """Overlay para configurar el precio de venta de un jugador."""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))
        
        all_p = ultimate_manager.club_items.get("players", [])
        if self.selected_idx >= len(all_p): return
        p = all_p[self.selected_idx]
        
        # Panel Central
        rect = pygame.Rect(WIDTH//2 - 300, HEIGHT//2 - 250, 600, 500)
        pygame.draw.rect(screen, self.colors["panel"], rect, border_radius=20)
        pygame.draw.rect(screen, GOLD, rect, 2, border_radius=20)
        
        self.draw_text(screen, "LISTAR JUGADOR EN EL MERCADO", WIDTH//2, rect.top + 30, size=24, bold=True, color=GOLD, center=True)
        
        # Previsualización de carta
        card_renderer.render_card(screen, p, rect.left + 50, rect.top + 100, scale=0.6)
        
        # Configuración de precios
        lx = rect.left + 300
        ly = rect.top + 120
        
        # Rangos
        self.draw_text(screen, f"Rango Permitido: {self.list_ranges['min']:,} - {self.list_ranges['max']:,}", lx, ly, size=14, color=UI_TEXT_DIM)
        
        # Inputs
        options = [
            ("PRECIO DE SALIDA (Subasta)", self.list_bid),
            ("PRECIO COMPRAR YA", self.list_buy)
        ]
        
        for i, (label, val) in enumerate(options):
            is_sel = (self.list_sel == i)
            iy = ly + 60 + i * 100
            
            self.draw_text(screen, label, lx, iy, size=16, color=WHITE, bold=True)
            box_rect = pygame.Rect(lx, iy + 25, 250, 45)
            pygame.draw.rect(screen, (30, 40, 60), box_rect, border_radius=8)
            if is_sel: pygame.draw.rect(screen, self.colors["accent"], box_rect, 2, border_radius=8)
            
            self.draw_text(screen, f"$ {val:,}", lx + 125, iy + 35, size=20, color=GOLD, bold=True, center=True)

        # Regla de los 50
        valid = self.list_buy >= self.list_bid + 50
        if not valid:
            self.draw_text(screen, "Error: El 'Comprar Ya' debe ser +50 que la subasta", lx, ly + 280, size=12, color=self.colors["red"])

        self.draw_text(screen, "[↑↓] Cambiar Opción  [← →] Ajustar Precio", WIDTH//2, rect.bottom - 80, size=14, color=WHITE, center=True)
        self.draw_text(screen, "[ENTER] PUBLICAR SUBASTA  [ESC] CANCELAR", WIDTH//2, rect.bottom - 40, size=18, bold=True, color=self.colors["accent"] if valid else (100,100,100), center=True)

    def _get_inventory_positions(self, count):
        """Calcula las posiciones visuales (x, y) de la cuadrícula del club."""
        positions = []
        cols = 6
        cell_w, cell_h = 160, 220
        margin = 10
        for i in range(count):
            row = i // cols
            col = i % cols
            x = 50 + col * (cell_w + margin)
            y = 210 + row * (cell_h + margin)
            positions.append((x + cell_w//2, y + cell_h//2))
        return positions

    def _get_duplicate_positions(self, count):
        """Calcula las posiciones visuales de la lista de repetidos."""
        positions = []
        start_y = 260
        for i in range(count):
            y = start_y + i * 35
            positions.append((WIDTH//2, y + 15)) # Centro del item
        return positions

    def _draw_club_lineup(self, screen):
        # Sidebar con info de plantilla
        starters = [p for p in ultimate_manager.squad[:11] if p]
        avg_ovr = sum(p["ovr"] for p in starters) / 11 if starters else 0
        chem = ultimate_manager.calculate_chemistry()
        
        self.draw_text(screen, "MI CLUB", 50, 110, size=28, color=self.colors["accent"], bold=True)
        
        # Indicadores Rápidos
        header_rect = pygame.Rect(400, 105, 220, 40)
        pygame.draw.rect(screen, (30, 35, 60), header_rect, border_radius=8)
        self.draw_text(screen, f"VAL: {int(avg_ovr)}", 415, 115, size=16, color=GOLD, bold=True)
        chem_col = TEAL if chem >= 80 else (GOLD if chem >= 50 else RED)
        self.draw_text(screen, f"QUIM: {chem}", 510, 115, size=16, color=chem_col, bold=True)

        # 1. CANCHA (VISTA ESTRATÉGICA)
        pitch_rect = pygame.Rect(50, 160, 720, 450)
        pygame.draw.rect(screen, (25, 60, 30), pitch_rect, border_radius=15)
        pygame.draw.rect(screen, (60, 120, 60), pitch_rect, 2, border_radius=15)
        
        pygame.draw.line(screen, (255, 255, 255, 40), (pitch_rect.centerx, pitch_rect.top), (pitch_rect.centerx, pitch_rect.bottom), 2)
        pygame.draw.circle(screen, (255, 255, 255, 40), pitch_rect.center, 60, 2)
        pygame.draw.rect(screen, (255, 255, 255, 40), (50, 160 + 100, 80, 250), 2)

        all_positions = self._get_squad_positions()
        squad = ultimate_manager.squad
        
        # Renderizar Titulares
        for i, p in enumerate(squad[:11]):
            x, y = all_positions[i]
            self._draw_player_card(screen, p, i, x, y, 0.32)

        # 2. BANCA
        self.draw_text(screen, "SUPLENTES (BANCA)", 50, 625, size=18, color=self.colors["gold"])
        subs = squad[11:18] # No filtrar por 'if p' para mostrar slots vacíos

        for i, p in enumerate(subs):
            idx = 11 + i
            x, y = all_positions[idx]
            self._draw_player_card(screen, p, idx, x, y, 0.32)

        # Panel Lateral de Opciones (Rediseñado como Dashboard)
        opt_rect = pygame.Rect(785, 110, 465, 590)
        pygame.draw.rect(screen, self.colors["panel"], opt_rect, border_radius=15)
        pygame.draw.rect(screen, (50, 60, 100), opt_rect, 1, border_radius=15)
        
        if self.search_mode:
            # PANTALLA DE BÚSQUEDA INTERNA (Vista Integrada)
            self.draw_text(screen, "BÚSQUEDA EN CLUB", 800, 130, size=22, bold=True, color=self.colors["accent"])
            
            # Filtros con estilo moderno
            pos_list = ["TODOS", "POR", "DEF", "MED", "DEL"]
            rar_list = ["TODOS", "LEYENDA", "ORO", "PLATA", "BRONCE"]
            evt_list = ["TODOS", "MUNDIAL", "FLASHBACK"]
            
            for i, label in enumerate(["Posición", "Rareza", "Evento", "Resultados"]):
                is_sel = (self.filter_row == i)
                y = 175 + i * 50
                box_rect = pygame.Rect(800, y, 435, 40)
                pygame.draw.rect(screen, self.colors["panel_light"] if is_sel else (30, 35, 60), box_rect, border_radius=8)
                if is_sel: pygame.draw.rect(screen, self.colors["accent"], box_rect, 1, border_radius=8)
                
                if i == 0: val = pos_list[self.f_pos_idx]
                elif i == 1: val = rar_list[self.f_class_idx]
                elif i == 2: val = evt_list[self.f_evt_idx] if hasattr(self, "f_evt_idx") else "TODOS"
                elif i == 3: val = "SÍ" if self.f_show_all else "SQUAD OCULTO"
                else: val = ""
                
                if val: self.draw_text(screen, val, 1050, y + 10, size=16, color=WHITE, bold=is_sel)

            # Lista de resultados
            list_y_start = 380 # Bajamos un poco la lista para el nuevo filtro
            # --- ÚNICA FUENTE DE VERDAD ---
            filtered = self._get_filtered_club_list()

            start_idx = max(0, self.selected_idx - 100 - 4)
            for i, p in enumerate(filtered[start_idx:start_idx+8]):
                idx = 100 + start_idx + i
                is_sel = (self.selected_idx == idx and self.filter_row == 4)
                y = list_y_start + i * 38
                if is_sel: 
                    pygame.draw.rect(screen, (50, 70, 120), (800, y-2, 435, 34), border_radius=5)
                
                self.draw_text(screen, f"{p['ovr']}", 815, y + 5, size=16, color=GOLD, bold=True)
                self.draw_text(screen, f"{p['pos']}", 855, y + 5, size=14, color=WHITE)
                self.draw_text(screen, p["name"][:20], 900, y + 5, size=16, color=WHITE)
                
            self.draw_text(screen, "[ESC] CANCELAR  ·  [ENTER] INTERCAMBIAR", 1015, 675, size=12, color=UI_TEXT_DIM, center=True)
            
        elif self.club_mode == "DUPLICATES":
            self._draw_duplicates_panel(screen)

        elif self.club_mode == "LINEUP":
            self.draw_text(screen, "GESTIÓN DE PLANTILLA", 800, 130, size=22, bold=True, color=self.colors["accent"])
            
            # Bloque de Identidad (Nuevo)
            ident_rect = pygame.Rect(800, 170, 435, 80)
            pygame.draw.rect(screen, (30, 35, 65), ident_rect, border_radius=12)
            self.draw_text(screen, ultimate_manager.team_name.upper(), 815, 185, size=20, bold=True, color=GOLD)
            self.draw_text(screen, f"Abreviatura: {ultimate_manager.abbreviation}", 815, 215, size=14, color=UI_TEXT_DIM)
            # Preview del Escudo (Círculo de color primario)
            pygame.draw.circle(screen, ultimate_manager.primary, (1190, 210), 25)
            pygame.draw.circle(screen, ultimate_manager.accent, (1190, 210), 25, 2)

            # Acciones como Tarjetas
            actions = [
                ("ENTER", "Intercambiar", "SWAP"), ("F", "Buscar Club", "SEARCH"),
                ("I", "Detalles", "INFO"), ("V", "Venta Rápida", "COIN"),
                ("T", "Tácticas", "TACTIC"), ("D", "Repetidos", "DUP"),
            ]
            
            for i, (key, label, icon_type) in enumerate(actions):
                ax = 800 + (i % 2) * 225
                ay = 270 + (i // 2) * 85
                a_rect = pygame.Rect(ax, ay, 210, 75)
                pygame.draw.rect(screen, self.colors["panel_light"], a_rect, border_radius=12)
                pygame.draw.rect(screen, (70, 80, 120), a_rect, 1, border_radius=12)
                
                # --- DIBUJO DE ICONOS VECTORIALES PARA ACCIONES ---
                ix, iy = ax + 30, ay + 35
                icol = GOLD if label == "Intercambiar" else WHITE
                if icon_type == "SWAP":
                    pygame.draw.line(screen, icol, (ix-10, iy-5), (ix+10, iy-5), 2)
                    pygame.draw.line(screen, icol, (ix+10, iy+5), (ix-10, iy+5), 2)
                    pygame.draw.polygon(screen, icol, [(ix+10, iy-10), (ix+15, iy-5), (ix+10, iy)])
                elif icon_type == "SEARCH":
                    pygame.draw.circle(screen, icol, (ix, iy-3), 8, 2)
                    pygame.draw.line(screen, icol, (ix+5, iy+2), (ix+12, iy+9), 3)
                elif icon_type == "INFO":
                    pygame.draw.rect(screen, icol, (ix-10, iy-10, 5, 20))
                    pygame.draw.rect(screen, icol, (ix, iy, 5, 10))
                    pygame.draw.rect(screen, icol, (ix+10, iy-5, 5, 15))
                elif icon_type == "COIN":
                    pygame.draw.circle(screen, GOLD, (ix, iy), 10)
                    self.draw_text(screen, "C", ix, iy-7, size=14, color=(80,60,0), bold=True, center=True)
                elif icon_type == "TACTIC":
                    pygame.draw.rect(screen, icol, (ix-10, iy-12, 20, 24), 2)
                    pygame.draw.circle(screen, icol, (ix, iy), 4)
                elif icon_type == "DUP":
                    pygame.draw.rect(screen, icol, (ix-12, iy-12, 10, 24), 2)
                    pygame.draw.rect(screen, icol, (ix+2, iy-12, 10, 24), 2)

                self.draw_text(screen, label, ax + 60, ay + 15, size=16, bold=True)
                self.draw_text(screen, f"Tecla [{key}]", ax + 60, ay + 45, size=12, color=UI_TEXT_DIM)
            
            # Resumen de Estadísticas (Mini-block)
            pygame.draw.rect(screen, (25, 28, 50), (800, 540, 435, 130), border_radius=12)
            self.draw_text(screen, "RESUMEN DEL CLUB", 815, 555, size=14, bold=True, color=GOLD)
            self.draw_text(screen, f"Partidos: {ultimate_manager.stats['matches']}", 815, 585, size=16)
            self.draw_text(screen, f"Victorias: {ultimate_manager.stats['wins']}", 815, 620, size=16)
            self.draw_text(screen, f"GF: {ultimate_manager.stats['gf']} | GC: {ultimate_manager.stats['ga']}", 1020, 585, size=16)

        else:
            # MODO TÁCTICAS (Vista de Dashboard)
            formations_list = list(FORMATIONS.keys())
            squad_players = [p for p in ultimate_manager.squad[:11] if p]

            self.draw_text(screen, "PANEL TÁCTICO", 785, 120, size=22, bold=True, color=GOLD)
            
            # --- Formaciones con Scroll ---
            self.draw_text(screen, "SELECCIONAR FORMACIÓN", 785, 160, size=16, bold=True, color=self.colors["accent"])
            
            max_form_vis = 8 # Mostrar máximo 8 formaciones
            form_start_idx = 0
            if self.tactic_section == "FORMATION" and self.tactic_sel >= max_form_vis:
                form_start_idx = self.tactic_sel - max_form_vis + 1
            
            for i_offset, fname in enumerate(formations_list[form_start_idx:form_start_idx+max_form_vis]):
                i = form_start_idx + i_offset
                is_active = (fname == ultimate_manager.formation)
                is_sel = (self.tactic_section == "FORMATION" and i == self.tactic_sel)
                y = 195 + i_offset * 38
                
                b_rect = pygame.Rect(785, y, 450, 34)
                bg_col = self.colors["panel_light"] if is_sel else (30, 35, 60)
                pygame.draw.rect(screen, bg_col, b_rect, border_radius=5)
                if is_active: pygame.draw.rect(screen, GOLD, b_rect, 1, border_radius=5)
                
                col = GOLD if is_active else (WHITE if is_sel else UI_TEXT_DIM)
                prefix = "▸ " if is_sel else ("✓ " if is_active else "  ")
                self.draw_text(screen, f"{prefix}{fname}", 800, y + 8, size=17, color=col, bold=is_sel)

            # --- Capitán (Fijado abajo del bloque de formaciones) ---
            cap_y_start = 195 + (max_form_vis * 38) + 15
            self.draw_text(screen, "DESIGNAR CAPITÁN", 785, cap_y_start, size=16, bold=True, color=self.colors["accent"])
            
            start_y = cap_y_start + 30
            max_cap_vis = 4
            cap_start_idx = 0
            if self.tactic_section == "CAPTAIN" and self.tactic_sel >= max_cap_vis:
                cap_start_idx = self.tactic_sel - max_cap_vis + 1
                
            for i_offset, p in enumerate(squad_players[cap_start_idx:cap_start_idx+max_cap_vis]):
                i = cap_start_idx + i_offset
                is_cap = (p.get("name") == ultimate_manager.captain_name)
                is_sel = (self.tactic_section == "CAPTAIN" and i == self.tactic_sel)
                y = start_y + i_offset * 32
                
                b_rect = pygame.Rect(785, y, 450, 28)
                bg_col = self.colors["panel_light"] if is_sel else (30, 35, 60)
                pygame.draw.rect(screen, bg_col, b_rect, border_radius=5)
                
                col = GOLD if is_cap else (WHITE if is_sel else UI_TEXT_DIM)
                prefix = "▸ " if is_sel else ("© " if is_cap else "  ")
                self.draw_text(screen, f"{prefix}{p['ovr']} {p['pos']} {p['name']}", 800, y + 5, size=16, color=col, bold=is_sel)
        
        self.draw_text(screen, "[T] VOLVER A LA PLANTILLA", 1000, 670, size=12, color=UI_TEXT_DIM, center=True)

    def _draw_market(self, screen):
        if self.market_tab == "MENU":
            self._draw_market_hub(screen)
        elif self.market_tab == "GLOBAL":
            self._draw_market_global(screen)
        elif self.market_tab == "MY_AUCTIONS":
            self._draw_market_my_auctions(screen)

    def _draw_market_hub(self, screen):
        """Menú principal del mercado con tarjetas grandes optimizado."""
        card_w, card_h = 350, 450
        total_w = 2 * (card_w + 40) - 40
        start_x = (WIDTH - total_w) // 2
        
        for i, mdata in enumerate(self.market_menu_data):
            is_sel = (self.market_menu_idx == i)
            x = start_x + i * (card_w + 40)
            y = 180
            
            rect = pygame.Rect(x, y, card_w, card_h)
            col = mdata["col"]
            bg_col = tuple(min(255, c + 30) for c in col) if is_sel else col
            pygame.draw.rect(screen, bg_col, rect, border_radius=20)
            
            if is_sel:
                pygame.draw.rect(screen, WHITE, rect, 4, border_radius=20)
                glow = math.sin(pygame.time.get_ticks() * 0.01) * 8 + 8
                pygame.draw.rect(screen, WHITE, (x-glow, y-glow, card_w+glow*2, card_h+glow*2), 1, border_radius=24)
            
            # Icono decorativo
            ic_x, ic_y = x + card_w//2, y + 120
            pygame.draw.circle(screen, (255,255,255,40), (ic_x, ic_y), 60)
            self.draw_text(screen, "M" if i == 0 else "S", ic_x, ic_y - 25, size=40, bold=True, color=WHITE, center=True)
            
            self.draw_text(screen, mdata["title"], x + card_w//2, y + 220, size=28, bold=True, color=WHITE, center=True)
            
            # Descripción pre-split
            self.draw_text(screen, mdata["desc"][0], x + card_w//2, y + 270, size=16, color=WHITE, center=True)
            self.draw_text(screen, mdata["desc"][1], x + card_w//2, y + 295, size=16, color=WHITE, center=True)
            
            if is_sel:
                self.draw_text(screen, "PULSA ENTER", x + card_w//2, y + card_h - 60, size=18, bold=True, color=WHITE, center=True)

        self.draw_text(screen, "[← →] Seleccionar  [ENTER] Confirmar  [ESC] Volver", WIDTH//2, HEIGHT - 50, size=16, color=self.colors.get("text_dim", WHITE), center=True)

    def _draw_market_global(self, screen):
        # Aquí va la lógica antigua de filtros y resultados
        if self.market_state == "FILTERS":
            self._draw_market_filters(screen)
        else:
            self._draw_market_results(screen)

    def _draw_market_my_auctions(self, screen):
        """Vista de los jugadores que el usuario está vendiendo."""
        self.draw_text(screen, "MIS SUBASTAS ACTIVAS", 50, 160, size=24, bold=True, color=self.colors["gold"])
        
        if not hasattr(self, "_cached_my_auctions") or self._cached_my_auctions is None:
            self._cached_my_auctions = ultimate_manager.get_my_auctions()
        
        my_auctions = self._cached_my_auctions
        
        if not my_auctions:
            pygame.draw.rect(screen, self.colors["panel"], (50, 200, WIDTH-100, 400), border_radius=15)
            self.draw_text(screen, "No tienes subastas activas.", WIDTH//2, 400, size=20, color=self.colors["text_dim"], center=True)
            return

        for i, auc in enumerate(my_auctions):
            y = 220 + i * 80
            rect = pygame.Rect(50, y, WIDTH - 100, 70)
            pygame.draw.rect(screen, self.colors["panel"], rect, border_radius=10)
            
            p = auc.get("player_data", auc.get("player"))
            if not p: continue
            
            bid = auc.get("current_bid", auc.get("bid", 0))
            buy_now = auc.get("buy_now", 0)
            
            self.draw_text(screen, f"{p['name']} ({p['ovr']})", 70, y + 15, size=18, bold=True, color=WHITE)
            self.draw_text(screen, f"Puja Actual: {bid:,} | Compra ya: {buy_now:,}", 70, y + 40, size=14, color=self.colors["text_dim"])
            
            # Estado (tiempo restante placeholder)
            self.draw_text(screen, "EN VENTA", WIDTH - 200, y + 25, size=16, color=TEAL, bold=True)

    def _draw_market_filters(self, screen):
        pos_list = ["TODOS", "POR", "DEF", "MED", "DEL"]
        rar_list = ["TODOS", "LEYENDA", "ORO", "PLATA", "BRONCE"]

        panel_rect = pygame.Rect(WIDTH//2 - 300, 180, 600, 300)
        pygame.draw.rect(screen, self.colors["panel"], panel_rect, border_radius=15)
        pygame.draw.rect(screen, WHITE, panel_rect, 1, border_radius=15)
        
        self.draw_text(screen, "FILTROS DE BÚSQUEDA", WIDTH//2, 210, size=24, bold=True, center=True)
        
        rows = [
            (f"Posición: {pos_list[self.m_pos_idx]}", 260),
            (f"Calidad: {rar_list[self.m_class_idx]}", 310),
            ("BUSCAR", 380)
        ]
        for i, (text, y) in enumerate(rows):
            is_sel = (self.market_filter_row == i)
            col = self.colors["accent"] if is_sel else WHITE
            self.draw_text(screen, text, WIDTH//2, y, size=20, color=col, bold=is_sel, center=True)
        
        self.draw_text(screen, "Usa ← → para cambiar filtros, ENTER para buscar.", WIDTH//2, 450, size=16, color=UI_TEXT_DIM, center=True)

    def _draw_market_results(self, screen):
        """Muestra los jugadores encontrados en el mercado global con soporte de scroll infinito y subastas completas."""
        self.draw_text(screen, "MERCADO GLOBAL - RESULTADOS", 50, 160, size=24, bold=True, color=self.colors["accent"])
        
        if not self.market_results:
            self.draw_text(screen, "No se encontraron jugadores.", WIDTH//2, HEIGHT//2, size=20, color=WHITE, center=True)
            self.draw_text(screen, "[BACKSPACE] Volver", WIDTH//2, HEIGHT//2 + 40, size=16, color=UI_TEXT_DIM, center=True)
            return

        # Calcular ventana de scroll (8 jugadores a la vez en cuadrícula 4x2)
        scroll = getattr(self, "market_scroll_idx", 0)
        visible_results = self.market_results[scroll:scroll+8]
        
        import time
        for i, auc in enumerate(visible_results):
            p = auc.get("player_data", auc.get("player"))
            if not p: continue

            # Spacing premium amplio (4x2)
            x = 50 + (i % 4) * 295
            y = 200 + (i // 4) * 235
            
            # El índice global para la selección es scroll + i
            is_sel = (self.selected_idx == 20 + scroll + i)
            scale = 0.62
            
            # Dibujar contenedor con estilo premium glassmorphism/dark panel
            rect = pygame.Rect(x, y, 280, 215)
            bg_color = (25, 30, 50)
            pygame.draw.rect(screen, bg_color, rect, border_radius=15)
            
            if is_sel:
                # Brillo de selección neon dorado/acento
                pygame.draw.rect(screen, self.colors["accent"], rect, 3, border_radius=15)
                glow = pygame.Surface((280, 215), pygame.SRCALPHA)
                pygame.draw.rect(glow, (*self.colors["accent"], 25), (0, 0, 280, 215), border_radius=15)
                screen.blit(glow, (x, y))
            else:
                # Borde elegante
                pygame.draw.rect(screen, (50, 60, 90), rect, 1, border_radius=15)
            
            # Dibujar carta del jugador (izquierda)
            card_renderer.render_card(screen, p, x + 10, y + 15, scale=scale)
            
            # ---- DETALLES DE LA SUBASTA (derecha) ----
            right_x = x + 130
            
            # 1. Tiempo Restante
            expires = auc.get("expires", 0)
            diff_ms = expires - int(time.time() * 1000)
            if diff_ms <= 0:
                time_str = "EXPIRADO"
                time_col = (255, 80, 80)
            else:
                diff_sec = diff_ms // 1000
                if diff_sec < 60:
                    time_str = f"⏱ {diff_sec}s"
                    time_col = (255, 80, 80)
                elif diff_sec < 3600:
                    time_str = f"⏱ {diff_sec // 60}m"
                    time_col = (255, 165, 0)
                else:
                    hours = diff_sec // 3600
                    mins = (diff_sec % 3600) // 60
                    time_str = f"⏱ {hours}h {mins}m"
                    time_col = (0, 255, 150)
            self.draw_text(screen, time_str, right_x, y + 20, size=14, color=time_col, bold=True)
            
            # 2. Precio de Puja Actual / Inicial
            self.draw_text(screen, "PUJA ACTUAL", right_x, y + 50, size=10, color=UI_TEXT_DIM, bold=True)
            current_bid = auc.get("current_bid", auc.get("bid", 0))
            last_bidder = auc.get("last_bidder")
            is_leading = (last_bidder == ultimate_manager.username)
            
            # Si eres el líder de la puja, se ve verde neón!
            bid_col = (0, 255, 150) if is_leading else self.colors["gold"]
            self.draw_text(screen, f"$ {current_bid:,}", right_x, y + 63, size=15, color=bid_col, bold=True)
            
            if is_leading:
                self.draw_text(screen, "¡LÍDER!", right_x, y + 80, size=9, color=(0, 255, 150), bold=True)
            elif last_bidder:
                self.draw_text(screen, f"Por {last_bidder[:8]}", right_x, y + 80, size=9, color=UI_TEXT_DIM)
            else:
                self.draw_text(screen, "Sin ofertas", right_x, y + 80, size=9, color=UI_TEXT_DIM)
            
            # 3. Precio de Compra Ya
            self.draw_text(screen, "COMPRAR YA", right_x, y + 105, size=10, color=UI_TEXT_DIM, bold=True)
            price = auc.get("buy_now", 0)
            self.draw_text(screen, f"$ {price:,}", right_x, y + 118, size=17, color=self.colors["gold"], bold=True)
            
            # 4. Vendedor
            seller = auc.get("seller_id", "System")
            if seller == "SERVER_SYSTEM": seller = "BOT SISTEMA"
            self.draw_text(screen, f"Vendedor: {seller[:10]}", right_x, y + 155, size=11, color=UI_TEXT_DIM)
            
            # 5. Prompts específicos al estar seleccionado
            if is_sel:
                pygame.draw.rect(screen, (30, 40, 70), (x + 10, y + 185, 260, 20), border_radius=5)
                self.draw_text(screen, "[ENTER] Compra Ya   [P] Puja   [I] Info", x + 140, y + 188, size=11, color=WHITE, bold=True, center=True)

        # Indicador de Scroll / Páginas
        total = len(self.market_results)
        cur_row = (scroll // 4) + 1
        total_rows = (total + 3) // 4
        
        self.draw_text(screen, f"RESULTADOS: {total} | FILA {cur_row} de {total_rows}", WIDTH-300, 165, size=14, color=UI_TEXT_DIM)
        self.draw_text(screen, "↑↓←→ Navegar   ·   [ENTER] Comprar Ya   ·   [P] Ofertar Puja   ·   [I] Detalles   ·   ESC Volver", WIDTH//2, HEIGHT - 30, size=14, color=UI_TEXT_DIM, center=True, bold=True)

    def _draw_pack_card(self, screen, pack, x, y, is_sel):
        """Método unificado para dibujar un sobre con diseño premium en cualquier sección."""
        rect = pygame.Rect(x, y, 260, 420)
        
        # 1. Definición de colores según Tier
        tier = pack.get("color_tier", "ORO")
        main_col = (40, 40, 60)
        accent_col = self.colors["accent"]
        
        if tier == "BRONCE":
            main_col = (80, 50, 40); accent_col = (180, 120, 80)
        elif tier == "PLATA":
            main_col = (60, 70, 90); accent_col = (192, 192, 192)
        elif tier == "ORO":
            main_col = (80, 70, 20); accent_col = (255, 215, 0)
        elif tier == "ELITE":
            main_col = (10, 30, 80); accent_col = (0, 255, 255)

        # 2. Sombra y Cuerpo
        shadow_rect = rect.copy()
        shadow_rect.x += 8; shadow_rect.y += 8
        pygame.draw.rect(screen, (10, 10, 20, 150), shadow_rect, border_radius=20)
        pygame.draw.rect(screen, main_col, rect, border_radius=20)
        
        # 3. Patrones de Fondo Dinámicos
        cat = pack.get("cat", "NORMAL")
        cx, cy = rect.width//2, rect.height//2
        
        if cat == "PROMO":
            # Efecto Sutil PROMO (Sin líneas)
            diag_surf = pygame.Surface((rect.width, 140), pygame.SRCALPHA)
            p_col = (255, 100, 255, 30) if tier != "ELITE" else (0, 255, 255, 30)
            pygame.draw.polygon(diag_surf, p_col, [(0, 100), (100, 0), (260, 40), (160, 140)])
            screen.blit(diag_surf, (x, y + cy + 40))
        else:
            # --- DISEÑOS ÚNICOS POR TIER (Fondo) ---
            if tier == "BRONCE":
                # Patrón de líneas verticales (Textura metal mate)
                for i in range(15, rect.width, 30):
                    pygame.draw.line(screen, (*main_col, 150), (x + i, y + 10), (x + i, y + rect.height - 10), 2)
            elif tier == "PLATA":
                # Reflejo metálico diagonal
                refl_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                pygame.draw.polygon(refl_surf, (255, 255, 255, 20), [(0, 0), (100, 0), (260, 160), (160, 260)])
                screen.blit(refl_surf, (x, y))
            elif tier == "ORO":
                # Doble franja elegante y motas doradas
                refl_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                pygame.draw.polygon(refl_surf, (255, 215, 0, 25), [(0, 150), (150, 0), (260, 110), (110, 260)])
                pygame.draw.polygon(refl_surf, (255, 215, 0, 15), [(0, 250), (250, 0), (260, 10), (10, 260)])
                screen.blit(refl_surf, (x, y))
                for _ in range(20):
                    px, py = random.randint(15, rect.width-15), random.randint(15, rect.height-15)
                    pygame.draw.circle(screen, (255, 255, 200, 120), (x + px, y + py), 1)

            # Franja Estándar de Acento (Aumentar alpha para legibilidad)
            diag_surf = pygame.Surface((rect.width, 120), pygame.SRCALPHA)
            pygame.draw.polygon(diag_surf, (*accent_col, 100), [(0, 80), (100, 0), (260, 40), (160, 120)])
            screen.blit(diag_surf, (x, y + cy + 60))

        # 4. Overlays de Identidad de Evento (Mundial, etc)
        event = pack.get("event", "NORMAL")
        if event == "WC":
            bar_h = 16
            bar_y = y + rect.height - 35
            bw = (rect.width - 10) // 3
            bx = x + 5
            pygame.draw.rect(screen, (0, 104, 71), (bx, bar_y, bw, bar_h)) # Verde
            pygame.draw.rect(screen, (191, 10, 48), (bx + bw, bar_y, bw, bar_h)) # Rojo
            pygame.draw.rect(screen, (0, 40, 104), (bx + bw*2, bar_y, rect.width - 10 - bw*2, bar_h)) # Azul
            pygame.draw.rect(screen, GOLD, (x + 20, y + cy - 2, rect.width - 40, 4))
        
        # 5. Iconos de Tier / Clase
        glow_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        if tier == "ELITE":
            pygame.draw.line(glow_surf, (200, 255, 255, 100), (cx, 50), (cx, 370), 3)
            pygame.draw.line(glow_surf, (200, 255, 255, 100), (20, cy), (240, cy), 3)
            self.draw_text(screen, "✦", x + cx, y + 210, size=80, color=(0, 255, 255), center=True)
        elif cat == "PROMO":
            self.draw_text(screen, "✦", x + cx, y + 210, size=60, color=(255, 255, 200), center=True)
        
        # 6. Icono Central del Tipo de Artículo
        p_type = pack.get("type", "PACK")
        if p_type == "PLAYER":
            p_data = pack.get("data", {})
            self.draw_text(screen, f"{p_data.get('ovr', '??')}", x + cx, y + 210, size=50, color=GOLD, bold=True, center=True)
        else:
            icon = "PICK" if p_type == "PICK" else "SOBRE"
            self.draw_text(screen, icon, x + cx, y + 210, size=32, bold=True, center=True)
        screen.blit(glow_surf, (x, y))

        # 7. Borde de Selección y Textos
        pygame.draw.rect(screen, accent_col, rect, 5 if is_sel else 2, border_radius=20)
        self.draw_text(screen, pack["name"].upper(), x + cx, y + 40, size=20, bold=True, center=True)
        
        det = pack.get("details", {})
        if det:
            p_txt = det.get('players', '??')
            self.draw_text(screen, f"• {p_txt} Jugadores", x + 45, y + 85, size=14, color=WHITE)
            self.draw_text(screen, f"• Garantizado: {det.get('guaranteed', 'VARIOS')}", x + 45, y + 110, size=14, color=accent_col, bold=True)
            if "prob" in det:
                self.draw_text(screen, f"• Prob: {det['prob']}", x + 45, y + 135, size=12, color=(200, 255, 200))
        
        # 8. Precio (Si corresponde)
        # 8. Precio (Si corresponde)
        if "price" in pack and self.store_cat != "MIS SOBRES":
            # Dibujar ambos precios apilados con fondo
            price_rect = pygame.Rect(x + 20, y + 335, 220, 50)
            pygame.draw.rect(screen, (20, 20, 40), price_rect, border_radius=10)
            
            # Línea de monedas
            self.draw_text(screen, f"$ {pack['price']:,} | [ENTER]", x + cx, y + 345, size=12, color=GOLD, bold=True, center=True)
            
            # Línea de FC Points
            price_fp = pack.get("price_points", 0)
            self.draw_text(screen, f"{price_fp:,} FP | [F]", x + cx, y + 365, size=12, color=(0, 255, 180), bold=True, center=True)
        elif "price_usd" in pack:
            price_rect = pygame.Rect(x + 40, y + 340, 180, 45)
            pygame.draw.rect(screen, (20, 20, 40), price_rect, border_radius=10)
            self.draw_text(screen, f"${pack['price_usd']:.2f} USD", x + cx, y + 355, size=18, color=(100, 255, 150), bold=True, center=True)

    def _draw_store(self, screen):
        """Renderiza la tienda y el inventario de sobres."""
        self.draw_text(screen, "TIENDA DEL CLUB", 50, 110, size=28, color=self.colors["accent"], bold=True)
        
        # --- CATEGORÍAS DE TIENDA (Soporte para 100 Items) ---
        cats = ["NORMAL", "PROMO", "MIS SOBRES"]
        for i, c in enumerate(cats):
            is_sel = (self.store_cat == c)
            x = 240 + i * 185
            color = WHITE if is_sel else UI_TEXT_DIM
            label = f"[{i+1}] {c}"
            self.draw_text(screen, label, x, 115, size=14, bold=is_sel, color=color)
            if is_sel:
                pygame.draw.rect(screen, self.colors["accent"], (x - 10, 140, 160, 3))

        # Filtrar packs
        if self.store_cat == "MIS SOBRES":
            visible_packs = ultimate_manager.pending_packs
        else:
            visible_packs = [p for p in ultimate_manager.store_packs if p.get("cat", "NORMAL") == self.store_cat]


        if not visible_packs:
            msg = "No tienes sobres guardados." if self.store_cat == "MIS SOBRES" else "No hay artículos disponibles en esta categoría."
            self.draw_text(screen, msg, WIDTH//2, HEIGHT//2, center=True, color=UI_TEXT_DIM)
            return

        self.selected_idx = min(self.selected_idx, len(visible_packs) - 1)
        if self.selected_idx < 0 and visible_packs: self.selected_idx = 0

        # --- SCROLL HORIZONTAL DINÁMICO ---
        target_scroll = self.selected_idx * 290
        if not hasattr(self, "store_x_scroll"): self.store_x_scroll = 0
        self.store_x_scroll += (target_scroll - self.store_x_scroll) * 0.1
        
        max_scroll = max(0, (len(visible_packs) * 290) - (WIDTH - 160))
        scroll_val = min(max_scroll, max(0, self.store_x_scroll - 200))

        # --- AVISO DE ARTÍCULOS PENDIENTES ---
        pending_count = len(ultimate_manager.pending_items) + len(ultimate_manager.pending_picks)
        if pending_count > 0:
            warn_rect = pygame.Rect(50, 620, WIDTH-100, 60)
            pygame.draw.rect(screen, (80, 20, 20), warn_rect, border_radius=10)
            pygame.draw.rect(screen, self.colors["red"], warn_rect, 2, border_radius=10)
            txt = f"[!] TIENES {pending_count} ARTÍCULOS O PICKS PENDIENTES"
            self.draw_text(screen, txt, WIDTH//2, 635, size=18, color=WHITE, bold=True, center=True)
            self.draw_text(screen, "PULSA [P] PARA GESTIONAR TUS ARTÍCULOS O PICKS", WIDTH//2, 655, size=14, color=UI_TEXT_DIM, center=True)
        
        for i, pack in enumerate(visible_packs):
            x = 80 + i * 290 - scroll_val
            y = 180
            is_sel = (self.selected_idx == i)
            
            if x + 260 < 0 or x > WIDTH: continue
            
            # Usar el nuevo método unificado
            self._draw_pack_card(screen, pack, x, y, is_sel)
            
            if is_sel:
                prompt_txt = "PULSA [ENTER] PARA PAGAR" if self.store_cat == "COMPRAR FC POINTS" else "PULSA [ENTER] PARA ABRIR"
                self.draw_text(screen, prompt_txt, x + 130, y + 405, size=12, color=self.colors["accent"], bold=True, center=True)

    def _draw_pick_selection(self, screen):
        """Overlay para elegir un jugador de un Player Pick."""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 230))
        screen.blit(overlay, (0, 0))
        
        pick = self.active_pick
        options = pick["options"]
        
        self.draw_text(screen, f"SELECCIÓN DE JUGADOR: {pick['name']}", WIDTH//2, 100, size=32, color=GOLD, bold=True, center=True)
        self.draw_text(screen, "Escoge 1 jugador para que se una a tu club", WIDTH//2, 145, size=18, color=WHITE, center=True)
        
        total_w = len(options) * 220 - 20
        start_x = (WIDTH - total_w) // 2
        
        for i, p in enumerate(options):
            x = start_x + i * 220
            y = 250
            is_sel = (self.selected_idx == i)
            
            if is_sel:
                # Resplandor de selección
                glow = pygame.Surface((220, 310), pygame.SRCALPHA)
                pygame.draw.rect(glow, (*self.colors["accent"], 60), (0, 0, 220, 310), border_radius=15)
                screen.blit(glow, (x-10, y-10))
                pygame.draw.rect(screen, self.colors["accent"], (x-10, y-10, 220, 310), 3, border_radius=15)
            
            card_renderer.render_card(screen, p, x, y, scale=1.1)
            
        self.draw_text(screen, "[← →] Seleccionar   [ENTER] Confirmar Elección", WIDTH//2, HEIGHT - 100, size=18, color=WHITE, center=True, bold=True)

    def _draw_pack_reveal(self, screen):
        """Pantalla interactiva para gestionar hasta 100 artículos de un sobre."""
        # --- CINEMÁTICA WALKOUT ---
        if hasattr(self, "walkout_state") and self.walkout_state > 0:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((5, 5, 10, 255))
            screen.blit(overlay, (0, 0))
            p = self.walkout_player
            self.walkout_timer += 1

            # Reproducir sonido walkout al inicio (caminante 86+ tiene sonido de walkout, panel 83-85 tiene select)
            if self.walkout_timer == 1:
                try:
                    from systems.audio_manager import audio_manager
                    if p and p.get("ovr", 0) >= 86:
                        audio_manager.play_sfx("walkout", 0.9)
                    else:
                        audio_manager.play_sfx("select", 0.9)
                except: pass

            if self.walkout_timer > 60 and self.walkout_state == 1: self.walkout_state = 2
            if self.walkout_timer > 120 and self.walkout_state == 2: self.walkout_state = 3
            if self.walkout_timer > 180 and self.walkout_state == 3: self.walkout_state = 4
            cx, cy = WIDTH//2, HEIGHT//2

            # --- PARTÍCULAS DORADAS WALKOUT (Solo para caminantes 86+) ---
            if p and p.get("ovr", 0) >= 86:
                if not hasattr(self, "_walkout_particles") or self.walkout_timer <= 2:
                    self._walkout_particles = []
                    for _ in range(80):
                        self._walkout_particles.append({
                            "x": random.randint(0, WIDTH),
                            "y": random.randint(0, HEIGHT),
                            "r": random.uniform(1.5, 4),
                            "vy": random.uniform(-60, -20),
                            "vx": random.uniform(-15, 15),
                            "alpha": random.randint(100, 255),
                            "color": random.choice([
                                (255, 215, 0), (255, 200, 50), (255, 180, 30),
                                (255, 255, 150), (200, 170, 0)
                            ])
                        })

                for wp in self._walkout_particles:
                    wp["y"] += wp["vy"] * 0.016
                    wp["x"] += wp["vx"] * 0.016
                    if wp["y"] < -10:
                        wp["y"] = HEIGHT + 10
                        wp["x"] = random.randint(0, WIDTH)
                    ps = pygame.Surface((int(wp["r"]*2), int(wp["r"]*2)), pygame.SRCALPHA)
                    r = int(wp["r"])
                    col = wp["color"]
                    pygame.draw.circle(ps, (*col, wp["alpha"]), (r, r), r)
                    screen.blit(ps, (int(wp["x"]), int(wp["y"])))

            if self.walkout_state < 4:
                glow = pygame.Surface((400, 400), pygame.SRCALPHA)
                pygame.draw.circle(glow, (255, 215, 0, 40), (200, 200), 200)
                screen.blit(glow, (cx-200, cy-200))
            if self.walkout_state == 1:
                self.draw_text(screen, "NACIÓN", cx, cy-60, size=24, color=UI_TEXT_DIM, center=True, bold=True)
                self.draw_text(screen, p.get("nat", "???"), cx, cy+10, size=60, color=WHITE, bold=True, center=True)
            elif self.walkout_state == 2:
                self.draw_text(screen, "POSICIÓN", cx, cy-60, size=24, color=UI_TEXT_DIM, center=True, bold=True)
                self.draw_text(screen, p.get("pos", "UNK"), cx, cy+10, size=70, color=WHITE, bold=True, center=True)
            elif self.walkout_state == 3:
                self.draw_text(screen, "MEDIA", cx, cy-60, size=24, color=UI_TEXT_DIM, center=True, bold=True)
                self.draw_text(screen, str(p.get("ovr", 0)), cx, cy+10, size=90, color=GOLD, bold=True, center=True)
            elif self.walkout_state >= 4:
                # Resplandor dorado detrás de la carta
                pulse = abs(math.sin(self.walkout_timer * 0.04))
                glow_big = pygame.Surface((500, 500), pygame.SRCALPHA)
                pygame.draw.circle(glow_big, (255, 215, 0, int(30 + 25 * pulse)), (250, 250), 250)
                screen.blit(glow_big, (cx-250, cy-250))
                card_renderer.render_card(screen, p, cx-135, cy-200, scale=1.5)
                if int(self.walkout_timer * 0.1) % 2 == 0:
                    self.draw_text(screen, "PULSA [ENTER] PARA VER TODO EL SOBRE", cx, HEIGHT - 60, size=18, color=WHITE, center=True)
            return

        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 15, 30, 250))
        screen.blit(overlay, (0, 0))
        
        self.draw_text(screen, "ARTÍCULOS DEL SOBRE", WIDTH//2, 40, size=32, color=GOLD, bold=True, center=True)
        
        # --- LÓGICA DE ORDENACIÓN DINÁMICA ---
        club_names = [p["name"] for p in ultimate_manager.club_items.get("players", [])]
        def _is_dup(item):
            if item["type"] != "player": return False
            return club_names.count(item["data"]["name"]) >= 1
            
        non_dups = sorted([it for it in self.pack_reveal_items if not _is_dup(it)], key=lambda it: it["data"].get("ovr", 0) if it["type"] == "player" else 10, reverse=True)
        dups = sorted([it for it in self.pack_reveal_items if _is_dup(it)], key=lambda it: it["data"].get("ovr", 0) if it["type"] == "player" else 10, reverse=True)
        
        sorted_items = non_dups + dups
        real_indices = [self.pack_reveal_items.index(it) for it in sorted_items]
        
        # Grid Configuration
        COLS = 6
        CARD_W, CARD_H = 160, 220
        GAP_X, GAP_Y = 30, 40
        START_X = (WIDTH - (COLS * CARD_W + (COLS-1) * GAP_X)) // 2
        START_Y = 120 - self.reveal_scroll
        
        # Renderizado de Secciones y Cartas
        for vi, item in enumerate(sorted_items):
            row = vi // COLS
            col = vi % COLS
            
            # Ajuste de Y para el separador de duplicados
            extra_y = 0
            if vi >= len(non_dups) and dups:
                extra_y = 60
                if vi == len(non_dups):
                    title_y = START_Y + row * (CARD_H + GAP_Y) + 20
                    pygame.draw.line(screen, (100, 100, 120), (100, title_y), (WIDTH-100, title_y), 1)
                    self.draw_text(screen, f"DUPLICADOS ({len(dups)})", 100, title_y + 10, size=16, color=self.colors["red"], bold=True)
            
            # Título de sección "Nuevos"
            if vi == 0 and non_dups:
                self.draw_text(screen, f"ARTÍCULOS NUEVOS ({len(non_dups)})", 100, START_Y - 30, size=16, color=TEAL, bold=True)

            x = START_X + col * (CARD_W + GAP_X)
            y = START_Y + row * (CARD_H + GAP_Y) + extra_y
            
            # Solo dibujar si es visible para rendimiento
            if y + CARD_H < 0 or y > HEIGHT - 80: continue
            
            real_i = real_indices[vi]
            is_sel = (self.reveal_idx == real_i)
            is_dup = _is_dup(item)
            
            # Efecto de aparición gradual (Movimiento/Fade visual)
            item_timer = self.reveal_timer - (vi * 5) # 5 frames de desfase entre cartas
            if item_timer < 0: continue
            
            alpha = min(255, item_timer * 15)
            # Nota: Para un fade real necesitaríamos superficies con alpha, 
            # pero aquí simularemos 'aparición' por tiempo.
            
            if is_sel:
                # Resplandor animado de selección
                sel_col = self.colors["red"] if vi >= len(non_dups) else self.colors["accent"]
                pygame.draw.rect(screen, sel_col, (x-5, y-5, CARD_W+10, CARD_H+10), 3, border_radius=15)
            
            if item["type"] == "player":
                card_renderer.render_card(screen, item["data"], x, y, scale=0.88)
                if vi >= len(non_dups): # Es duplicado
                    badge_rect = pygame.Rect(x + 2, y + 2, 70, 22)
                    pygame.draw.rect(screen, (200, 50, 50), badge_rect, border_radius=6)
                    self.draw_text(screen, "REPETIDO", x + 35, y + 5, size=10, color=WHITE, center=True, bold=True)
            else:
                # Otros ítems (Badge/Kit/Consumible)
                rect = pygame.Rect(x, y, CARD_W, CARD_H)
                pygame.draw.rect(screen, (40, 45, 70), rect, border_radius=15)
                pygame.draw.rect(screen, (80, 80, 100), rect, 2, border_radius=15)
                
                ic_map = {"badge": "ESCUDO", "kit": "UNIFORME", "consumable": "MEJORA"}
                self.draw_text(screen, ic_map.get(item["type"], "SOBRE"), x + CARD_W//2, y + CARD_H//2 - 20, size=22, bold=True, color=GOLD, center=True)
                self.draw_text(screen, item["data"].get("name", "ITEM")[:15], x + CARD_W//2, y + CARD_H//2 + 40, size=14, color=WHITE, center=True, bold=True)
                self.draw_text(screen, item["type"].upper(), x + CARD_W//2, y + CARD_H//2 + 65, size=12, color=UI_TEXT_DIM, center=True)

        # Panel de Acciones Inferior persistente
        pygame.draw.rect(screen, (20, 25, 45), (0, HEIGHT - 80, WIDTH, 80))
        pygame.draw.line(screen, self.colors["accent"], (0, HEIGHT - 80), (WIDTH, HEIGHT - 80), 2)
        
        controls = [
            ("[S] GUARDAR", 100),
            ("[L] MERCADO", 300),
            ("[X] DESCARTAR", 500),
            ("[A] GUARDAR TODO", 750),
            ("[ESC] SALIR", 1050)
        ]
        for txt, cx in controls:
            self.draw_text(screen, txt, cx, HEIGHT - 45, size=18, color=WHITE, bold=True, center=True)

    def _get_evolved_preview(self, player, evo):
        import copy
        from data.rosters import calculate_ovr
        p_copy = copy.deepcopy(player)
        for lvl in evo["levels"]:
            if "reward_stats" in lvl:
                for s_k, s_v in lvl["reward_stats"].items():
                    if s_k in p_copy["s"]:
                        p_copy["s"][s_k] += s_v
            if "reward_design" in lvl:
                p_copy["card_type"] = lvl["reward_design"]
        p_copy["ovr"] = calculate_ovr(p_copy)
        return p_copy

    def _draw_evolutions(self, screen):
        TEAL = (0, 255, 150)
        GOLD = self.colors["gold"]
        WHITE = (255, 255, 255)
        UI_TEXT_DIM = (140, 140, 160)

        self.draw_text(screen, "CENTRO DE EVOLUCIONES", 50, 115, size=26, bold=True, color=TEAL)

        import datetime
        promo_start = datetime.datetime(2026, 8, 26, 15, 0)
        now = datetime.datetime.now()
        
        # Filtrar catálogo para ocultar contenido no anunciado
        visible_evos = [e for e in EVOLUTIONS_DB if e["id"] != "classic_heritage" or now >= promo_start]
        if not visible_evos:
            self.draw_text(screen, "No hay evoluciones disponibles en este momento.", WIDTH//2, HEIGHT//2, size=20, color=WHITE, center=True)
            return

        self.evo_idx = min(self.evo_idx, len(visible_evos) - 1)
        evo = visible_evos[self.evo_idx]

        # Obtener los jugadores compatibles
        compatible_players = [p for p in ultimate_manager.club_items["players"] if check_evolution_eligibility(p, evo["id"])]
        compatible_players.sort(key=lambda x: x.get("ovr", 0), reverse=True)

        if self.evo_state == "EVO_SELECT":
            # --- MODO EVO_SELECT ---
            # 1. Catálogo de Evoluciones (Izquierda)
            cat_panel = pygame.Rect(30, 160, 480, 480)
            pygame.draw.rect(screen, self.colors["panel"], cat_panel, border_radius=15)
            pygame.draw.rect(screen, TEAL, cat_panel, 2, border_radius=15)
            self.draw_text(screen, "CATÁLOGO DE EVOLUCIONES", 45, 175, size=18, bold=True, color=TEAL)

            for i, item_evo in enumerate(visible_evos):
                is_sel = (i == self.evo_idx)
                y = 210 + i * 102
                rect = pygame.Rect(45, y, 450, 92)
                bg = (40, 45, 75) if is_sel else (30, 32, 55)
                pygame.draw.rect(screen, bg, rect, border_radius=10)
                if is_sel:
                    pygame.draw.rect(screen, GOLD, rect, 2, border_radius=10)

                # Icono y Nombre
                self.draw_text(screen, item_evo.get("icon", "*"), 60, y + 15, size=24)
                self.draw_text(screen, item_evo["name"].upper(), 100, y + 18, size=16, bold=True, color=GOLD if is_sel else WHITE)
                
                # Requisitos resumidos
                req_txt = f"Máx {item_evo['req'].get('max_ovr',99)} OVR"
                if "pos" in item_evo["req"]:
                    req_txt += f" | Pos: {','.join(item_evo['req']['pos'])}"
                self.draw_text(screen, req_txt, 100, y + 42, size=12, color=UI_TEXT_DIM)
                
                # Costo
                cost_txt = "GRATIS" if item_evo["cost"] == 0 else f"$ {item_evo['cost']:,}"
                self.draw_text(screen, cost_txt, 100, y + 62, size=13, bold=True, color=GOLD)

                # Cantidad de jugadores compatibles en tu club
                comp_count = len([p for p in ultimate_manager.club_items["players"] if check_evolution_eligibility(p, item_evo["id"])])
                self.draw_text(screen, f"Compatibles: {comp_count}", 340, y + 62, size=12, color=TEAL if comp_count > 0 else UI_TEXT_DIM)

            # 2. Detalles de Evolución Seleccionada + Sugerencia (Derecha)
            details_panel = pygame.Rect(530, 160, 720, 480)
            pygame.draw.rect(screen, self.colors["panel"], details_panel, border_radius=15)
            pygame.draw.rect(screen, GOLD, details_panel, 2, border_radius=15)
            
            self.draw_text(screen, f"DETALLES: {evo['name'].upper()}", 550, 175, size=20, bold=True, color=GOLD)

            cost_txt = "GRATIS" if evo["cost"] == 0 else f"$ {evo['cost']:,} MONEDAS"
            self.draw_text(screen, cost_txt, 1030, 175, size=16, bold=True, color=GOLD)

            # Descripción narrativa
            desc = evo["desc"]
            words = desc.split()
            lines = []
            current_line = []
            for w in words:
                current_line.append(w)
                if len(" ".join(current_line)) > 75:
                    current_line.pop()
                    lines.append(" ".join(current_line))
                    current_line = [w]
            if current_line:
                lines.append(" ".join(current_line))
            
            for j, line in enumerate(lines[:3]):
                self.draw_text(screen, line, 550, 210 + j * 18, size=13, color=WHITE)

            # Requisitos y Niveles
            self.draw_text(screen, "REQUISITOS DE ELEGIBILIDAD:", 550, 280, size=14, bold=True, color=TEAL)
            
            req_txt = f"• Valoración Máxima (OVR): {evo['req'].get('max_ovr', 99)}"
            if "max_speed" in evo["req"]:
                req_txt += f"\n• Ritmo Máximo (PAC): {evo['req']['max_speed']}"
            if "pos" in evo["req"]:
                req_txt += f"\n• Posiciones válidas: {', '.join(evo['req']['pos'])}"
            
            for j, line in enumerate(req_txt.split('\n')):
                self.draw_text(screen, line, 550, 302 + j * 18, size=13, color=WHITE)

            # Niveles y mejoras finales
            self.draw_text(screen, "MEJORA FINAL ESTIMADA:", 550, 370, size=14, bold=True, color=TEAL)
            lvl_txt = f"• Niveles totales: {len(evo['levels'])}"
            total_stats_up = {}
            final_design = None
            for lvl in evo["levels"]:
                if "reward_stats" in lvl:
                    for sk, sv in lvl["reward_stats"].items():
                        total_stats_up[sk] = total_stats_up.get(sk, 0) + sv
                if "reward_design" in lvl:
                    final_design = lvl["reward_design"]

            upgrade_parts = []
            for sk, sv in total_stats_up.items():
                stat_names_es = {"speed": "RIT", "shot": "TIR", "passing": "PAS", "dribbling": "REG", "defense": "DEF", "physical": "FIS", "gk": "POR"}
                upgrade_parts.append(f"{stat_names_es.get(sk, sk.upper())} +{sv}")
            
            lvl_txt += f"\n• Atributos: {', '.join(upgrade_parts)}"
            if final_design:
                lvl_txt += f"\n• Diseño de carta especial: {final_design}"
                
            for j, line in enumerate(lvl_txt.split('\n')):
                self.draw_text(screen, line, 550, 392 + j * 18, size=13, color=WHITE)

            # --- SUGERENCIA DE JUGADOR DESTACADO (Elemento Visual) ---
            pygame.draw.line(screen, (50, 55, 75), (540, 470), (1240, 470), 1)
            self.draw_text(screen, "RECOMENDACIÓN DE TU CLUB (Sugerencia Visual)", 550, 480, size=14, bold=True, color=GOLD)
            
            if compatible_players:
                best_p = compatible_players[0]
                p_evo_prev = self._get_evolved_preview(best_p, evo)
                
                # Renderizar las dos cartas side-by-side
                card_renderer.render_card(screen, best_p, 570, 510, scale=0.55)
                self.draw_text(screen, "Original", 610, 642, size=11, color=UI_TEXT_DIM, center=True)
                
                self.draw_text(screen, "->", 700, 560, size=32, color=GOLD, bold=True, center=True)
                self.draw_text(screen, "EVO", 700, 595, size=12, color=GOLD, bold=True, center=True)
                
                card_renderer.render_card(screen, p_evo_prev, 760, 510, scale=0.55)
                self.draw_text(screen, "Mejorado", 800, 642, size=11, color=TEAL, center=True)
                
                self.draw_text(screen, f"¡{best_p['name']} mejorará a {p_evo_prev['ovr']}!", 890, 510, size=14, bold=True, color=WHITE)
                
                stat_y = 535
                for sk, sv in total_stats_up.items():
                    stat_names_es = {"speed": "Ritmo (PAC)", "shot": "Tiro (SHO)", "passing": "Pase (PAS)", "dribbling": "Regate (DRI)", "defense": "Defensa (DEF)", "physical": "Físico (PHY)"}
                    base_val = best_p["s"].get(sk, 70)
                    new_val = base_val + sv
                    self.draw_text(screen, f"• {stat_names_es.get(sk, sk.upper())}: {base_val} -> {new_val} (+{sv})", 890, stat_y, size=12, color=TEAL)
                    stat_y += 18
                
                self.draw_text(screen, "[ENTER] para comenzar la selección de jugador", 890, 615, size=12, color=WHITE, bold=True)
            else:
                self.draw_text(screen, "No tienes ningún jugador compatible en tu club para esta evolución.", 550, 540, size=14, color=UI_TEXT_DIM)

        elif self.evo_state == "PLAYER_SELECT":
            # --- MODO PLAYER_SELECT ---
            # 1. Lista de Jugadores Compatibles (Izquierda)
            player_panel = pygame.Rect(30, 160, 480, 480)
            pygame.draw.rect(screen, self.colors["panel"], player_panel, border_radius=15)
            pygame.draw.rect(screen, TEAL, player_panel, 2, border_radius=15)
            self.draw_text(screen, f"CLUB: COMPATIBLES CON {evo['name'].upper()}", 45, 175, size=18, bold=True, color=TEAL)

            if not compatible_players:
                self.draw_text(screen, "No hay jugadores compatibles.", 50, 220, size=14, color=UI_TEXT_DIM)
            else:
                self.evo_player_idx = min(self.evo_player_idx, len(compatible_players) - 1)
                start_idx = max(0, self.evo_player_idx - 3)
                
                for i, p in enumerate(compatible_players[start_idx:start_idx+8]):
                    actual_i = start_idx + i
                    is_sel = (actual_i == self.evo_player_idx)
                    y = 210 + i * 52
                    bg_col = (40, 50, 90) if is_sel else (30, 35, 60)
                    pygame.draw.rect(screen, bg_col, (45, y, 450, 45), border_radius=8)
                    if is_sel:
                        pygame.draw.rect(screen, GOLD, (45, y, 450, 45), 1, border_radius=8)

                    self.draw_text(screen, p["name"], 60, y + 8, size=15, bold=is_sel, color=WHITE)
                    self.draw_text(screen, f"{p['ovr']} {p['pos']} | PAC: {p['s'].get('speed',70)}  TIR: {p['s'].get('shot',70)}  PAS: {p['s'].get('passing',70)}  DEF: {p['s'].get('defense',70)}", 60, y + 26, size=11, color=UI_TEXT_DIM)
                    
                    if is_sel:
                        self.draw_text(screen, "► SELECCIONA", 350, y + 14, size=11, color=GOLD, bold=True)

            # 2. Vista Previa de Mejora Detallada (Derecha)
            details_panel = pygame.Rect(530, 160, 720, 480)
            pygame.draw.rect(screen, self.colors["panel"], details_panel, border_radius=15)
            pygame.draw.rect(screen, GOLD, details_panel, 2, border_radius=15)
            self.draw_text(screen, "VISTA PREVIA DE LA EVOLUCIÓN", 550, 175, size=20, bold=True, color=GOLD)

            if compatible_players:
                selected_p = compatible_players[self.evo_player_idx]
                p_evo_prev = self._get_evolved_preview(selected_p, evo)

                # Dibujar cartas grandes side-by-side
                card_renderer.render_card(screen, selected_p, 570, 220, scale=1.1)
                self.draw_text(screen, "CARTA ORIGINAL", 655, 475, size=12, color=UI_TEXT_DIM, bold=True, center=True)

                # Flecha intermedia
                self.draw_text(screen, "->", 790, 310, size=48, color=GOLD, bold=True, center=True)
                self.draw_text(screen, "MEJORA", 790, 360, size=14, color=GOLD, bold=True, center=True)

                # Carta evolucionada
                card_renderer.render_card(screen, p_evo_prev, 860, 220, scale=1.1)
                self.draw_text(screen, "VISTA PREVIA MEJORADA", 945, 475, size=12, color=TEAL, bold=True, center=True)

                # Atributos sumados detallados
                self.draw_text(screen, f"CAMBIOS EN ATRIBUTOS PARA {selected_p['name'].upper()}:", 550, 505, size=14, bold=True, color=WHITE)
                
                # Sumar mejoras
                total_stats_up = {}
                for lvl in evo["levels"]:
                    if "reward_stats" in lvl:
                        for sk, sv in lvl["reward_stats"].items():
                            total_stats_up[sk] = total_stats_up.get(sk, 0) + sv

                stat_y = 530
                col_x = 550
                col_i = 0
                for sk, sv in total_stats_up.items():
                    stat_names_es = {"speed": "Ritmo (PAC)", "shot": "Tiro (SHO)", "passing": "Pase (PAS)", "dribbling": "Regate (DRI)", "defense": "Defensa (DEF)", "physical": "Físico (PHY)", "gk": "Portero (GK)"}
                    base_val = selected_p["s"].get(sk, 70)
                    new_val = base_val + sv
                    self.draw_text(screen, f"• {stat_names_es.get(sk, sk.upper())}: {base_val} -> {new_val} (+{sv})", col_x, stat_y, size=12, color=TEAL)
                    col_i += 1
                    if col_i % 3 == 0:
                        stat_y += 20
                        col_x = 550
                    else:
                        col_x += 230

                # Instrucciones de confirmación
                pygame.draw.line(screen, (50, 55, 75), (540, 595), (1240, 595), 1)
                cost_text = "GRATIS" if evo["cost"] == 0 else f"Costo: $ {evo['cost']:,} Monedas"
                self.draw_text(screen, f"[ENTER] Iniciar Evolución ({cost_text})   ·   [ESC] Volver al Catálogo", 890, 610, size=14, bold=True, color=GOLD, center=True)
            else:
                self.draw_text(screen, "Selecciona un jugador compatible de la lista.", 550, 220, size=14, color=UI_TEXT_DIM)

    def _draw_sbc_preview(self, screen):
        """Dibuja una previsualización atractiva del modo Intercambios (SBC) con dos categorías."""
        GOLD = self.colors["gold"]
        PURPLE = (120, 40, 180)
        
        self.draw_text(screen, "INTERCAMBIOS DE PLANTILLA (SBC)", 50, 115, size=26, bold=True, color=GOLD)
        
        main_panel = pygame.Rect(30, 160, WIDTH - 60, 480)
        pygame.draw.rect(screen, self.colors["panel"], main_panel, border_radius=20)
        pygame.draw.rect(screen, PURPLE, main_panel, 2, border_radius=20)
        
        center_x = WIDTH // 2
        center_y = 350
        
        # Opciones de SBC (Botones visuales)
        categories = [
            ("PREMIUM", "Leyendas y Eventos", (50, 40, 80), GOLD),
            ("FUNDAMENTOS", "Diarios y Países", (40, 70, 50), (100, 255, 100))
        ]
        
        if not hasattr(self, "sbc_preview_idx"): self.sbc_preview_idx = 0
        
        for i, (title, desc, bg, acc) in enumerate(categories):
            is_sel = (self.sbc_preview_idx == i)
            x = center_x - 300 + i * 320
            rect = pygame.Rect(x, center_y - 120, 280, 240)
            
            # Dibujar caja
            pygame.draw.rect(screen, bg if is_sel else (30, 30, 45), rect, border_radius=15)
            if is_sel:
                pygame.draw.rect(screen, acc, rect, 3, border_radius=15)
                # Brillo animado
                glow = math.sin(pygame.time.get_ticks() * 0.01) * 5 + 5
                pygame.draw.rect(screen, acc, (x-glow, center_y-120-glow, 280+glow*2, 240+glow*2), 1, border_radius=18)
            
            self.draw_text(screen, title, x + 140, center_y - 30, size=24, bold=True, color=acc, center=True)
            self.draw_text(screen, desc, x + 140, center_y + 10, size=14, color=WHITE, center=True)
            
            icon = "[CAT]" if i == 0 else "[EVO]"
            self.draw_text(screen, icon, x + 140, center_y - 80, size=24, color=GOLD, bold=True, center=True)

        self.draw_text(screen, "[← →] Seleccionar Categoría   [ENTER] Entrar   [BACKSPACE] Volver", WIDTH//2, 660, size=14, color=UI_TEXT_DIM, center=True)

    def _draw_management(self, screen):
        self.draw_text(screen, "GESTIÓN DEL CLUB", 50, 115, size=28, color=self.colors["accent"], bold=True)
        
        # Panel central
        panel = pygame.Rect(50, 160, 1180, 500)
        pygame.draw.rect(screen, self.colors["panel"], panel, border_radius=20)
        
        mgmt_options = [
            ("EDITAR NOMBRE DEL CLUB", "Cambia la identidad de tu equipo", "EDIT"),
            ("PERSONALIZAR ESCUDO", "Diseña los colores de tu emblema", "BADGE"),
            ("GESTIÓN DE EQUIPACIONES", "Cambia el diseño de tus kits", "KIT"),
            ("REINICIAR CLUB (BORRAR TODO)", "Cuidado: Esta acción es irreversible", "WARN")
        ]
        
        # Inyectar repetidos si existen
        if ultimate_manager.pending_items:
            mgmt_options.insert(0, ("ARTÍCULOS PENDIENTES", f"Tienes {len(ultimate_manager.pending_items)} artículos por gestionar", "PENDING"))

        # Desplazamiento de lista de gestión
        visible_count = 5
        start_i = getattr(self, "mgmt_scroll", 0)
        end_i = min(start_i + visible_count, len(mgmt_options))

        for i, (txt, desc, icon_type) in enumerate(mgmt_options[start_i:end_i]):
            actual_idx = start_i + i
            is_sel = (self.selected_idx == actual_idx)
            y = 190 + i * 90
            o_rect = pygame.Rect(80, y, 1120, 80)
            
            bg = (40, 50, 90) if is_sel else (30, 32, 55)
            pygame.draw.rect(screen, bg, o_rect, border_radius=15)
            if is_sel: pygame.draw.rect(screen, self.colors["accent"], o_rect, 2, border_radius=15)
            
            # Iconos
            ix, iy = 130, y + 40
            if icon_type == "PENDING":
                pygame.draw.circle(screen, self.colors["red"], (ix, iy), 15, 2)
                self.draw_text(screen, "!", ix, iy-8, size=18, bold=True, color=self.colors["red"], center=True)
            elif icon_type == "EDIT":
                pygame.draw.rect(screen, WHITE, (ix-12, iy-12, 24, 24), 2)
            elif icon_type == "BADGE":
                pygame.draw.polygon(screen, GOLD, [(ix-12, iy-12), (ix+12, iy-12), (ix, iy+15)], 2)
            elif icon_type == "KIT":
                pygame.draw.rect(screen, WHITE, (ix-12, iy-10, 24, 20), 2)
            elif icon_type == "WARN":
                pygame.draw.polygon(screen, self.colors["red"], [(ix, iy-15), (ix-15, iy+12), (ix+15, iy+12)], 2)
            
            self.draw_text(screen, txt, 180, y + 15, size=20, bold=True, color=WHITE if is_sel else UI_TEXT_DIM)
            self.draw_text(screen, desc, 180, y + 45, size=14, color=UI_TEXT_DIM)
            
            if is_sel:
                self.draw_text(screen, "PULSA ENTER", 1000, y + 30, size=14, color=self.colors["accent"], bold=True)

        # Inputs overlays
        if self.management_state == "RENAME":
            title = "NUEVO NOMBRE" if self.active_input == "NAME" else "NUEVA ABREVIATURA (3 letras)"
            self._draw_input_overlay(screen, title, self.input_text)
        elif self.management_state == "RESET":
            self._draw_input_overlay(screen, "¿ELIMINAR CLUB? ESCRIBE 'BORRAR' PARA CONFIRMAR", self.input_text, color=self.colors["red"])
        elif self.management_state in ("SELECT_BADGE", "SELECT_KIT"):
            self._draw_item_selector(screen)

    def _draw_item_selector(self, screen):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 230))
        screen.blit(overlay, (0, 0))
        
        COLS = 5
        CELL_W, CELL_H = 220, 250
        GRID_X0 = 100
        GRID_Y0 = 160
        
        is_badge = (self.management_state == "SELECT_BADGE")
        items = ultimate_manager.club_items["badges"] if is_badge else ultimate_manager.club_items["kits"]
        title = "ELIGE TU ESCUDO" if is_badge else "ELIGE TU UNIFORME"
        total_rows = (len(items) + COLS - 1) // COLS
        
        self.draw_text(screen, title, WIDTH//2, 60, size=32, color=GOLD, bold=True, center=True)
        
        cur_row = self.selected_idx // COLS
        cur_col = self.selected_idx % COLS
        self.draw_text(screen, f"Fila {cur_row+1}/{total_rows}  ·  {self.selected_idx + 1}/{len(items)}", WIDTH//2, 105, size=16, color=WHITE, center=True)
        
        scroll = getattr(self, "item_scroll", 0)
        from data.teams import TEAMS, draw_badge, draw_uniform_preview
        
        for i, item in enumerate(items):
            col = i % COLS
            row = i // COLS
            x = GRID_X0 + col * CELL_W
            y = GRID_Y0 + row * CELL_H - scroll
            is_sel = (self.selected_idx == i)
            
            if y < -50 or y > HEIGHT: continue
            
            rect = pygame.Rect(x, y, 200, 220)
            bg = (40, 50, 90) if is_sel else (30, 32, 55)
            pygame.draw.rect(screen, bg, rect, border_radius=15)
            if is_sel: pygame.draw.rect(screen, self.colors["accent"], rect, 3, border_radius=15)
            
            full_team = next((t for t in TEAMS if t.get("short") == item.get("short")), None)
            if not full_team:
                full_team = next((t for t in TEAMS if t.get("name") == item.get("name")), item)

            if is_badge:
                draw_badge(screen, full_team, x + 100, y + 100, size=100)
            else:
                draw_uniform_preview(screen, full_team, x + 100, y + 60, scale=1.5)
            
            self.draw_text(screen, item.get("name", "?")[:15], x + 100, y + 185, size=14, center=True, bold=True)

        self.draw_text(screen, "[←→↑↓] Navegar   [ENTER] Equipar   [ESC] Volver", WIDTH//2, HEIGHT - 50, size=16, color=UI_TEXT_DIM, center=True)

    def _nav_item_grid(self, key, total):
        """Navegación de cuadrícula para selectores de ítems. Devuelve el nuevo índice."""
        COLS = 5
        row = self.selected_idx // COLS
        col = self.selected_idx % COLS
        total_rows = (total + COLS - 1) // COLS
        
        if key == pygame.K_LEFT:
            if col > 0: self.selected_idx -= 1
        elif key == pygame.K_RIGHT:
            if col < COLS - 1 and self.selected_idx + 1 < total:
                self.selected_idx += 1
        elif key == pygame.K_UP:
            if row > 0: self.selected_idx -= COLS
        elif key == pygame.K_DOWN:
            new_idx = self.selected_idx + COLS
            if new_idx < total: self.selected_idx = new_idx
        
        # Scroll para que la fila seleccionada sea visible
        CELL_H = 250
        VISIBLE_H = HEIGHT - 220  # Espacio visible del grid
        if not hasattr(self, "item_scroll"): self.item_scroll = 0
        sel_row = self.selected_idx // COLS
        row_top = sel_row * CELL_H
        row_bot = row_top + CELL_H
        if row_top < self.item_scroll:
            self.item_scroll = row_top
        elif row_bot > self.item_scroll + VISIBLE_H:
            self.item_scroll = row_bot - VISIBLE_H

    def _draw_input_overlay(self, screen, title, val, color=None):
        if not color: color = self.colors["accent"]
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        screen.blit(overlay, (0, 0))
        
        pygame.draw.rect(screen, self.colors["panel"], (WIDTH//2-250, HEIGHT//2-100, 500, 200), border_radius=20)
        self.draw_text(screen, title, WIDTH//2, HEIGHT//2 - 60, size=20, bold=True, center=True, color=color)
        
        input_rect = pygame.Rect(WIDTH//2-200, HEIGHT//2-10, 400, 50)
        pygame.draw.rect(screen, (10, 10, 30), input_rect, border_radius=10)
        pygame.draw.rect(screen, color, input_rect, 2, border_radius=10)
        self.draw_text(screen, val + "|", WIDTH//2, HEIGHT//2 + 5, size=24, center=True)
        self.draw_text(screen, "[ENTER] Confirmar   [ESC] Cancelar", WIDTH//2, HEIGHT//2 + 60, size=14, color=UI_TEXT_DIM, center=True)

    def _draw_player_card(self, screen, p, idx, x, y, scale):
        is_sel = (self.selected_idx == idx and self.club_mode == "LINEUP")
        if is_sel:
            # Cálculo de alineación perfecta del brillo
            card_w, card_h = int(180 * scale), int(270 * scale)
            s_w, s_h = int(card_w * 1.25), int(card_h * 1.15)
            scaled_glow = pygame.transform.smoothscale(self.selection_glow, (s_w, s_h))
            # Centrado: x_glow = x_card - (w_glow - w_card)/2
            gx = x - (s_w - card_w) // 2
            gy = y - (s_h - card_h) // 2
            screen.blit(scaled_glow, (gx, gy))
            
        if p:
            card_renderer.render_card(screen, p, x, y, scale=scale)
            # --- BRAZALETE DE CAPITÁN ---
            if p.get("name") == ultimate_manager.captain_name:
                card_w = int(180 * scale)
                badge_size = max(14, int(22 * scale))
                bx = x + card_w - badge_size - int(3 * scale)
                by = y + int(3 * scale)
                # Fondo circular dorado con borde
                pygame.draw.circle(screen, (30, 30, 30), (bx + badge_size // 2, by + badge_size // 2), badge_size // 2 + 2)
                pygame.draw.circle(screen, (255, 200, 0), (bx + badge_size // 2, by + badge_size // 2), badge_size // 2)
                # Letra C centrada
                c_font = pygame.font.SysFont("Arial", max(10, int(16 * scale)), bold=True)
                c_surf = c_font.render("C", True, (20, 20, 20))
                c_rect = c_surf.get_rect(center=(bx + badge_size // 2, by + badge_size // 2))
                screen.blit(c_surf, c_rect)
        else:
            # Slot vacío
            rect = pygame.Rect(x, y, int(180 * scale), int(270 * scale))
            pygame.draw.rect(screen, (30, 40, 60), rect, border_radius=int(10*scale))
            pygame.draw.rect(screen, (60, 80, 100), rect, 1, border_radius=int(10*scale))
            self.draw_text(screen, "+", x + int(90*scale), y + int(135*scale), size=int(40*scale), color=(60, 80, 100), center=True)

    def _get_filtered_club_list(self):
        """Devuelve la lista de jugadores filtrada según los criterios actuales (ÚNICA FUENTE DE VERDAD)."""
        all_p = ultimate_manager.club_items.get("players", [])
        
        # Filtros
        pos_list = ["TODOS", "POR", "DEF", "MED", "DEL"]
        rar_list = ["TODOS", "LEYENDA", "ORO", "PLATA", "BRONCE"]
        evt_list = ["TODOS", "MUNDIAL", "FLASHBACK"]
        
        # Jugadores ya en el campo (Titulares + Banca)
        active_uids = {p.get("uid") for p in ultimate_manager.squad if p}
        
        filtered = []
        for p in all_p:
            # Filtro de "Mostrar todos" vs "Solo disponibles"
            if not getattr(self, "f_show_all", False) and p.get("uid") in active_uids:
                continue
                
            # Filtro de posición
            m_pos = pos_list[getattr(self, "f_pos_idx", 0)]
            if m_pos != "TODOS":
                p_pos = p.get("pos", "")
                if m_pos == "POR" and p_pos != "GK": continue
                elif m_pos == "DEF" and p_pos not in ["LB", "CB", "RB", "LWB", "RWB"]: continue
                elif m_pos == "MED" and p_pos not in ["CM", "CDM", "CAM", "LM", "RM"]: continue
                elif m_pos == "DEL" and p_pos not in ["ST", "CF", "LW", "RW"]: continue
                
            # Filtro de rareza
            m_rar = rar_list[getattr(self, "f_class_idx", 0)]
            if m_rar != "TODOS" and p.get("rarity") != m_rar:
                continue
                
            # Filtro de evento
            m_evt = evt_list[getattr(self, "f_evt_idx", 0)]
            if m_evt != "TODOS":
                target_evt = "WC" if m_evt == "MUNDIAL" else m_evt
                if p.get("event") != target_evt:
                    continue
                
            filtered.append(p)
            
        # Ordenación Unificada e Inquebrantable: (Media desc, Nombre asc)
        filtered.sort(key=lambda x: (-x.get("ovr", 0), x.get("name", "")))
        return filtered

    def _draw_player_details(self, screen):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 220))
        screen.blit(overlay, (0, 0))
        
        p = None
        # --- DETERMINAR QUÉ JUGADOR MOSTRAR SEGÚN EL CONTEXTO ---
        if self.tab == "CLUB":
            if self.club_tab == "EQUIPO":
                if self.selected_idx >= 100: # Búsqueda de reemplazo
                    all_p = ultimate_manager.club_items.get("players", [])
                    starters_and_subs = [sp for sp in ultimate_manager.squad if sp]
                    current_uids = {sp.get("uid") for sp in starters_and_subs}
                    
                    filtered = [ap for ap in all_p if ap.get("uid") not in current_uids]
                    pos_list = ["TODOS", "POR", "DEF", "MED", "DEL"]
                    rar_list = ["TODOS", "LEYENDA", "ORO", "PLATA", "BRONCE"]
                    
                    if pos_list[self.f_pos_idx] != "TODOS":
                        m_pos = pos_list[self.f_pos_idx]
                        if m_pos == "POR": filtered = [f for f in filtered if f["pos"] == "GK"]
                        elif m_pos == "DEF": filtered = [f for f in filtered if f["pos"] in ["LB", "CB", "RB", "LWB", "RWB"]]
                        elif m_pos == "MED": filtered = [f for f in filtered if f["pos"] in ["CM", "CDM", "CAM", "LM", "RM"]]
                        elif m_pos == "DEL": filtered = [f for f in filtered if f["pos"] in ["ST", "CF", "LW", "RW"]]
                    
                    if rar_list[self.f_class_idx] != "TODOS":
                        filtered = [f for f in filtered if f.get("rarity") == rar_list[self.f_class_idx]]
                    
                    # Ordenación Unificada en búsqueda
                    filtered.sort(key=lambda x: (-x.get("ovr", 0), x.get("name", "")))
                    target = self.selected_idx - 100
                    if target < len(filtered): p = filtered[target]
                else: # Jugador de la alineación activa
                    if self.selected_idx < len(ultimate_manager.squad):
                        p = ultimate_manager.squad[self.selected_idx]
            elif self.club_tab == "MI_CLUB":
                if hasattr(self, "_cached_inv") and self._cached_inv:
                    if self.selected_idx < len(self._cached_inv):
                        p = self._cached_inv[self.selected_idx]
        
        elif self.tab == "MARKET":
            if self.market_tab == "GLOBAL" and self.market_results:
                res_idx = self.selected_idx - 20
                if 0 <= res_idx < len(self.market_results):
                    p = self.market_results[res_idx].get("player_data", self.market_results[res_idx].get("player"))
            elif self.market_tab == "MY_AUCTIONS":
                my_auctions = ultimate_manager.get_my_auctions()
                if self.selected_idx < len(my_auctions):
                    p = my_auctions[self.selected_idx]["player_data"]

        if p:
            # Carta Grande
            card_renderer.render_card(screen, p, 100, 150, scale=1.5)
            
            # Panel de Stats
            stats_panel = pygame.Rect(450, 150, 700, 450)
            pygame.draw.rect(screen, self.colors["panel"], stats_panel, border_radius=20)
            self.draw_text(screen, f"{p.get('name', 'N/A').upper()}", 480, 180, size=32, bold=True, color=self.colors["accent"])
            self.draw_text(screen, f"{p.get('pos', '???')} | {str(p.get('rarity', 'COMÚN')).upper()}", 480, 220, size=18, color=UI_TEXT_DIM)
            
            # Stats detalladas
            s = p.get("s", {})
            stat_items = [("RIT", s.get("speed", 75)), ("TIR", s.get("shot", 75)), ("PAS", s.get("passing", 75)), 
                          ("REG", s.get("dribbling", 75)), ("DEF", s.get("defense", 75)), ("FIS", s.get("physical", 75))]
            
            for i, (label, val) in enumerate(stat_items):
                x = 480 + (i % 2) * 300
                y = 280 + (i // 2) * 60
                self.draw_text(screen, f"{label}:", x, y, size=20, color=WHITE)
                # Barra de stat
                pygame.draw.rect(screen, (40, 40, 60), (x + 60, y + 5, 200, 15), border_radius=5)
                bar_col = (0, 255, 100) if val >= 80 else (255, 200, 0) if val >= 60 else (220, 50, 50)
                pygame.draw.rect(screen, bar_col, (x + 60, y + 5, int(val * 2), 15), border_radius=5)
                self.draw_text(screen, str(val), x + 270, y, size=20, color=WHITE, bold=True)
                
            # --- HISTORIAL EN EL CLUB ---
            stats = p.get("stats", {"matches": 0, "goals": 0, "assists": 0})
            hist_y = 460
            pygame.draw.line(screen, (80, 80, 100), (480, hist_y), (1100, hist_y), 2)
            self.draw_text(screen, "RENDIMIENTO HISTÓRICO EN TU CLUB", 480, hist_y + 15, size=18, color=GOLD, bold=True)
            
            h_data = [
                ("PARTIDOS JUGADOS", stats.get("matches", 0)),
                ("GOLES ANOTADOS", stats.get("goals", 0)),
                ("ASISTENCIAS", stats.get("assists", 0))
            ]
            
            for i, (lbl, val) in enumerate(h_data):
                hx = 480 + i * 210
                self.draw_text(screen, lbl, hx, hist_y + 50, size=12, color=UI_TEXT_DIM, bold=True)
                self.draw_text(screen, str(val), hx, hist_y + 70, size=32, color=WHITE, bold=True)

        self.draw_text(screen, "[ESC/I] Cerrar Detalles", WIDTH//2, HEIGHT - 80, size=16, color=UI_TEXT_DIM, center=True)

    def _execute_swap(self, idx1, idx2):
        if idx1 == idx2 or idx1 is None or idx2 is None: return
        squad = ultimate_manager.squad
        
        def get_player(idx):
            if idx < 18: return squad[idx]
            if idx >= 100:
                filtered = self._get_filtered_club_list()
                target = idx - 100
                if target < len(filtered): return filtered[target]
            return None

        p1 = get_player(idx1)
        p2 = get_player(idx2)
        if (not p1 and not p2) or p1 == p2: return
        
        # Aplicar el cambio a los 18 slots
        if idx1 < 18: squad[idx1] = p2
        if idx2 < 18: squad[idx2] = p1

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Bloqueo total si hay error de conexión (solo permitir ESC para salir o R para reintentar)
                if ultimate_manager.online_status == "OFFLINE_ERROR":
                    if event.key == pygame.K_ESCAPE:
                        self.manager.pop_scene()
                    elif event.key == pygame.K_r:
                        print("Reintentando conexión con el servidor...")
                        ultimate_manager.online_status = "CONNECTING"
                        import threading
                        threading.Thread(target=ultimate_manager.load_ultimate, daemon=True).start()
                    continue

                # --- ESTADO DE ELECCIÓN DE PICK (MODAL GLOBAL) ---
                if hasattr(self, "active_pick") and self.active_pick:
                    pick = self.active_pick
                    if event.key == pygame.K_LEFT: 
                        self.selected_idx = max(0, self.selected_idx - 1)
                    elif event.key == pygame.K_RIGHT: 
                        self.selected_idx = min(len(pick["options"]) - 1, self.selected_idx + 1)
                    elif event.key == pygame.K_RETURN:
                        # Confirmar selección
                        p_idx = self.pending_pick_idx if hasattr(self, "pending_pick_idx") else 0
                        chosen = ultimate_manager.select_pick_player(p_idx, self.selected_idx)
                        if chosen:
                            self.msg = f"¡{chosen['name']} seleccionado!"
                            self.msg_timer = 3.0
                            self.active_pick = None
                            self.pack_reveal_items = ultimate_manager.pending_items
                            self.reveal_idx = 0
                            self.reveal_timer = 0
                        self.selected_idx = 0
                    continue

                # --- TECLA P PARA ABRIR PICKS O ARTÍCULOS PENDIENTES ---
                if event.key == pygame.K_p:
                    in_market_results = (self.tab == "MARKET" and hasattr(self, "market_tab") and self.market_tab == "RESULTS" and hasattr(self, "market_results") and self.market_results)
                    if not in_market_results:
                        if ultimate_manager.pending_picks:
                            self.active_pick = ultimate_manager.pending_picks[0]
                            self.pending_pick_idx = 0
                            self.selected_idx = 0
                            continue
                        elif ultimate_manager.pending_items:
                            self.pack_reveal_items = ultimate_manager.pending_items
                            self.reveal_idx = 0
                            self.reveal_timer = 0
                            self.walkout_state = 0
                            continue

                if event.key == pygame.K_q or event.key == pygame.K_e:
                    # Cerrar modos secundarios al cambiar de pestaña
                    self.listing_mode = False
                    self.detail_mode = False
                    self.management_state = "MAIN"
                    tabs_order = ["PLAY", "CLUB", "MARKET", "STORE", "EVOLUTIONS", "SBC", "OBJECTIVES"]
                    curr_idx = tabs_order.index(self.tab)
                    step = -1 if event.key == pygame.K_q else 1
                    self.tab = tabs_order[(curr_idx + step) % len(tabs_order)]
                    if self.tab == "CLUB":
                        self.club_tab = "MENU"
                        self.club_mode = "LINEUP"
                        self.search_mode = False
                    self.selected_idx = 0
                    self._cached_inv = None
                    self._cached_subs = None
                    self._cached_dups = None
                    self._cached_my_auctions = None
                    continue

                if event.key == pygame.K_ESCAPE:
                    # 1. Prioridad: Salir de modos visuales
                    if self.detail_mode:
                        self.detail_mode = False
                        continue
                    if self.listing_mode:
                        self.listing_mode = False
                        continue
                    if self.search_mode:
                        self.search_mode = False
                        self.selected_idx = self.search_pos if hasattr(self, "search_pos") else 0
                        continue
                    
                    # 2. Prioridad: Salir de sub-pestañas de Club
                    if self.tab == "CLUB" and self.club_tab != "MENU":
                        self.club_tab = "MENU"
                        self.selected_idx = 0
                        self._cached_inv = None 
                        self._cached_subs = None
                        self._cached_dups = None
                        continue
                        
                    # 3. Prioridad: Salir del Mercado
                    if self.tab == "MARKET" and self.market_tab != "MENU":
                        self.market_tab = "MENU"
                        self.market_state = "FILTERS"
                        continue
                        
                    # 3b. Prioridad: Salir de la selección de jugador de Evoluciones
                    if self.tab == "EVOLUTIONS" and self.evo_state == "PLAYER_SELECT":
                        self.evo_state = "EVO_SELECT"
                        continue
                    
                    # 4. Salir del juego (confirmación)
                    if hasattr(self, "confirm_exit") and self.confirm_exit:
                        ultimate_manager.save_ultimate()
                        self.manager.pop_scene()
                    else:
                        self.confirm_exit = True
                        self.msg = "¿Salir? Pulsa ESC de nuevo para confirmar"
                        self.msg_timer = 2.0
                    continue

                if self.listing_mode:
                    if event.key == pygame.K_ESCAPE: 
                        self.listing_mode = False
                        self.listing_source = None
                    elif event.key == pygame.K_UP: self.list_sel = 0
                    elif event.key == pygame.K_DOWN: self.list_sel = 1
                    elif event.key == pygame.K_LEFT:
                        if self.list_sel == 0: self.list_bid = max(self.list_ranges["min"], self.list_bid - self.list_step)
                        else: self.list_buy = max(self.list_ranges["min"] + 50, self.list_buy - self.list_step)
                    elif event.key == pygame.K_RIGHT:
                        if self.list_sel == 0: self.list_bid = min(self.list_ranges["max"] - 50, self.list_bid + self.list_step)
                        else: self.list_buy = min(self.list_ranges["max"], self.list_buy + self.list_step)
                    elif event.key == pygame.K_RETURN:
                        if self.list_buy >= self.list_bid + 50:
                            if getattr(self, "listing_source", None) == "PACK":
                                item = self.pack_reveal_items[self.reveal_idx]
                                if ultimate_manager.list_direct_item_on_market(item["data"], self.list_bid, self.list_buy):
                                    # Calcular v_idx para mantener la posición visual
                                    club_names = [p["name"] for p in ultimate_manager.club_items.get("players", [])]
                                    def _is_dup(it):
                                        if it["type"] != "player": return False
                                        return club_names.count(it["data"]["name"]) >= 1
                                    non_dups = sorted([it for it in self.pack_reveal_items if not _is_dup(it)], key=lambda it: it["data"].get("ovr", 0) if it["type"] == "player" else 10, reverse=True)
                                    dups = sorted([it for it in self.pack_reveal_items if _is_dup(it)], key=lambda it: it["data"].get("ovr", 0) if it["type"] == "player" else 10, reverse=True)
                                    temp_sorted = non_dups + dups
                                    temp_order = [self.pack_reveal_items.index(it) for it in temp_sorted]
                                    try:
                                        v_idx = temp_order.index(self.reveal_idx)
                                    except:
                                        v_idx = 0

                                    self.pack_reveal_items.pop(self.reveal_idx)
                                    self.listing_mode = False
                                    self.listing_source = None
                                    self.msg = "¡Jugador del sobre subastado!"
                                    self.msg_timer = 3.0
                                    
                                    if not self.pack_reveal_items: 
                                        self.pack_reveal_items = None
                                        ultimate_manager.pending_items = []
                                    else: 
                                        non_dups = sorted([it for it in self.pack_reveal_items if not _is_dup(it)], key=lambda it: it["data"].get("ovr", 0) if it["type"] == "player" else 10, reverse=True)
                                        dups = sorted([it for it in self.pack_reveal_items if _is_dup(it)], key=lambda it: it["data"].get("ovr", 0) if it["type"] == "player" else 10, reverse=True)
                                        temp_sorted = non_dups + dups
                                        temp_order = [self.pack_reveal_items.index(it) for it in temp_sorted]
                                        next_v_idx = min(v_idx, len(temp_order) - 1)
                                        self.reveal_idx = temp_order[next_v_idx]
                                        ultimate_manager.pending_items = self.pack_reveal_items
                                    ultimate_manager.save_ultimate()
                                else:
                                    self.msg = "Error al listar jugador"
                                    self.msg_timer = 2.0
                            else:
                                if ultimate_manager.list_player_on_market(self.selected_idx, self.list_bid, self.list_buy):
                                    self.listing_mode = False
                                    self.msg = "¡Jugador puesto en subasta!"
                                    self.msg_timer = 3.0
                                else:
                                    self.msg = "Error al listar jugador"
                                    self.msg_timer = 2.0
                    continue

                # El manejo de CLUB se ha movido al bloque unificado más abajo para evitar bloqueos


                if event.key == pygame.K_F9:
                    ultimate_manager.request_admin_coins()
                    self.msg = "Petición de Administrador enviada..."
                    self.msg_timer = 2.0
                    continue

                # Resetear confirmación de salida si pulsa otra tecla
                if event.key != pygame.K_ESCAPE:
                    self.confirm_exit = False

                if self.detail_mode:
                    if event.key in (pygame.K_ESCAPE, pygame.K_i): self.detail_mode = False
                    continue # Use continue instead of return to process other events if needed

                if self.tab == "CLUB":
                    if self.club_tab == "MENU":
                        # Founder reward check solo en el menú principal del club
                        if ultimate_manager.check_founder_reward():
                            if event.key == pygame.K_LEFT: self.selected_idx = (self.selected_idx - 1) % 3
                            elif event.key == pygame.K_RIGHT: self.selected_idx = (self.selected_idx + 1) % 3
                            elif event.key == pygame.K_RETURN:
                                chosen = ultimate_manager.claim_legend_pick(self.selected_idx)
                                self.msg = f"¡{chosen['name']} se ha unido a tu club!"
                                self.msg_timer = 4.0
                                self.selected_idx = 0
                            elif event.key == pygame.K_ESCAPE:
                                self.club_tab = "MENU"
                            continue
                        
                        if event.key == pygame.K_LEFT: self.club_menu_idx = (self.club_menu_idx - 1) % 4
                        elif event.key == pygame.K_RIGHT: self.club_menu_idx = (self.club_menu_idx + 1) % 4
                        elif event.key == pygame.K_RETURN:
                            targets = ["EQUIPO", "MI_CLUB", "DUPLICADOS", "GESTIÓN"]
                            self.club_tab = targets[self.club_menu_idx]
                            self.selected_idx = 0
                            if self.club_tab == "EQUIPO":
                                self.club_mode = "LINEUP"
                                self.search_mode = False
                        continue

                    elif self.club_tab == "EQUIPO":
                        if self.search_mode:
                            # Lógica de búsqueda interna
                            pos_list = ["TODOS", "POR", "DEF", "MED", "DEL"]
                            rar_list = ["TODOS", "LEYENDA", "ORO", "PLATA", "BRONCE"]
                            evt_list = ["TODOS", "MUNDIAL", "FLASHBACK"]
                            
                            # --- ÚNICA FUENTE DE VERDAD ---
                            filtered = self._get_filtered_club_list()
                            if event.key == pygame.K_UP: 
                                if self.filter_row == 4:
                                    if self.selected_idx > 100: self.selected_idx -= 1
                                    else: self.filter_row = 3
                                elif self.filter_row > 0: self.filter_row -= 1
                            elif event.key == pygame.K_DOWN:
                                if self.filter_row < 4:
                                    self.filter_row += 1
                                    if self.filter_row == 4: self.selected_idx = 100
                                elif self.selected_idx - 100 < len(filtered) - 1: self.selected_idx += 1
                            elif event.key == pygame.K_LEFT:
                                if self.filter_row == 0: self.f_pos_idx = (self.f_pos_idx - 1) % 5
                                elif self.filter_row == 1: self.f_class_idx = (self.f_class_idx - 1) % 5
                                elif self.filter_row == 2: self.f_evt_idx = (self.f_evt_idx - 1) % 3
                                elif self.filter_row == 3: self.f_show_all = not self.f_show_all
                            elif event.key == pygame.K_RIGHT:
                                if self.filter_row == 0: self.f_pos_idx = (self.f_pos_idx + 1) % 5
                                elif self.filter_row == 1: self.f_class_idx = (self.f_class_idx + 1) % 5
                                elif self.filter_row == 2: self.f_evt_idx = (self.f_evt_idx + 1) % 3
                                elif self.filter_row == 3: self.f_show_all = not self.f_show_all
                            elif event.key == pygame.K_RETURN:
                                if self.filter_row == 4:
                                    res_idx = self.selected_idx - 100
                                    if 0 <= res_idx < len(filtered):
                                        target_p = filtered[res_idx]
                                        
                                        # VALIDACIÓN DE DUPLICADOS (MISMO NOMBRE O UID)
                                        can_add, reason = ultimate_manager.can_add_to_squad(target_p, ignore_idx=self.search_pos)
                                        if not can_add:
                                            self.msg = reason
                                            self.msg_timer = 2.0
                                        else:
                                            if self.search_pos < 18:
                                                ultimate_manager.squad[self.search_pos] = target_p
                                            self.search_mode = False
                                            self.msg = "¡Jugador añadido!"
                                            self.msg_timer = 2.0
                                            ultimate_manager.save_ultimate()
                            elif event.key == pygame.K_ESCAPE:
                                self.search_mode = False
                                self.selected_idx = self.search_pos
                            continue

                        if self.club_mode == "TACTICS":
                            formations_list = list(FORMATIONS.keys())
                            squad_players = [p for p in ultimate_manager.squad[:11] if p]
                            if event.key == pygame.K_t or event.key == pygame.K_ESCAPE: 
                                self.club_mode = "LINEUP"
                                continue
                            elif event.key == pygame.K_UP:
                                if self.tactic_section == "FORMATION":
                                    if self.tactic_sel > 0: self.tactic_sel -= 1
                                else:
                                    if self.tactic_sel > 0: self.tactic_sel -= 1
                                    else:
                                        self.tactic_section = "FORMATION"
                                        self.tactic_sel = len(formations_list) - 1
                            elif event.key == pygame.K_DOWN:
                                if self.tactic_section == "FORMATION":
                                    if self.tactic_sel < len(formations_list) - 1: self.tactic_sel += 1
                                    else:
                                        self.tactic_section = "CAPTAIN"
                                        self.tactic_sel = 0
                                else:
                                    if self.tactic_sel < len(squad_players) - 1: self.tactic_sel += 1
                            elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                                self.tactic_section = "CAPTAIN" if self.tactic_section == "FORMATION" else "FORMATION"
                                self.tactic_sel = 0
                            elif event.key == pygame.K_RETURN:
                                if self.tactic_section == "FORMATION":
                                    ultimate_manager.formation = formations_list[self.tactic_sel]
                                    ultimate_manager.calculate_chemistry()
                                    self.msg = f"Formación {ultimate_manager.formation}!"
                                else:
                                    if self.tactic_sel < len(squad_players):
                                        ultimate_manager.set_captain(squad_players[self.tactic_sel])
                                        self.msg = "¡Capitán asignado!"
                                self.msg_timer = 2.0
                                ultimate_manager.save_ultimate()
                            continue

                        if self.club_mode == "DUPLICATES":
                            if event.key in (pygame.K_ESCAPE, pygame.K_d):
                                self.club_mode = "LINEUP"
                                self.selected_idx = 0
                            elif event.key == pygame.K_UP:
                                if self.selected_idx > 0: 
                                    self.selected_idx -= 1
                                    if self.selected_idx < self.dup_scroll:
                                        self.dup_scroll = self.selected_idx
                            elif event.key == pygame.K_DOWN:
                                dups = self._get_duplicate_list()
                                if self.selected_idx < len(dups) - 1: 
                                    self.selected_idx += 1
                                    if self.selected_idx >= self.dup_scroll + 10:
                                        self.dup_scroll = self.selected_idx - 9
                            continue

                        if self.club_mode == "LINEUP":
                            if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                                all_positions = self._get_squad_positions()
                                if self.selected_idx >= len(all_positions):
                                    self.selected_idx = 0
                                cx, cy = all_positions[self.selected_idx]
                                
                                best_score = float('inf')
                                target_idx = self.selected_idx
                                
                                for i in range(18):
                                    if i == self.selected_idx: continue
                                    ix, iy = all_positions[i]
                                    dx = ix - cx
                                    dy = iy - cy
                                    
                                    # Filtrar por dirección pura
                                    # Puntuación: Distancia en el eje + 4x Distancia perpendicular
                                    # 4x evita saltos largos a mediocentros desde el portero
                                    score = float('inf')
                                    if event.key == pygame.K_LEFT and dx < 0:
                                        score = abs(dx) + abs(dy) * 4
                                    elif event.key == pygame.K_RIGHT and dx > 0:
                                        score = abs(dx) + abs(dy) * 4
                                    elif event.key == pygame.K_UP and dy < 0:
                                        score = abs(dy) + abs(dx) * 4
                                    elif event.key == pygame.K_DOWN and dy > 0:
                                        score = abs(dy) + abs(dx) * 4
                                    
                                    if score < best_score:
                                        best_score = score
                                        target_idx = i
                                
                                self.selected_idx = target_idx
                            elif event.key == pygame.K_RETURN:
                                if self.swap_idx is None:
                                    self.swap_idx = self.selected_idx
                                    self.msg = "Selecciona destino"
                                else:
                                    p1 = ultimate_manager.squad[self.swap_idx]
                                    p2 = ultimate_manager.squad[self.selected_idx]
                                    ultimate_manager.squad[self.swap_idx] = p2
                                    ultimate_manager.squad[self.selected_idx] = p1
                                    self.swap_idx = None
                                    self.msg = "¡Intercambio realizado!"
                                    ultimate_manager.save_ultimate()
                                self.msg_timer = 1.0
                            elif event.key in (pygame.K_s, pygame.K_f):
                                self.search_mode = True
                                self.search_pos = self.selected_idx
                                self.selected_idx = 100
                                self.filter_row = 0
                            elif event.key == pygame.K_t:
                                self.club_mode = "TACTICS"
                            elif event.key == pygame.K_d:
                                self.club_mode = "DUPLICATES"
                                self.selected_idx = 0
                            elif event.key == pygame.K_i: self.detail_mode = True
                            elif event.key == pygame.K_v:
                                p = ultimate_manager.squad[self.selected_idx]
                                if p:
                                    ultimate_manager.coins += int(p["ovr"] * 10)
                                    if p in ultimate_manager.club_items["players"]:
                                        ultimate_manager.club_items["players"].remove(p)
                                    ultimate_manager.squad[self.selected_idx] = None
                                    self.msg = f"¡{p['name']} vendido!"
                                    self.msg_timer = 2.0
                                    ultimate_manager.save_ultimate()
                            continue

                    elif self.club_tab == "MI_CLUB":
                        # Navegación en cuadrícula de Inventario (6 columnas)
                        if not hasattr(self, "_cached_inv") or self._cached_inv is None:
                            self._cached_inv = ultimate_manager.club_items.get("players", [])[:]
                            self._cached_inv.sort(key=lambda x: x["ovr"], reverse=True)
                        
                        all_p = self._cached_inv
                        cols = 6
                        if event.key == pygame.K_UP: 
                            if self.selected_idx >= cols: self.selected_idx -= cols
                        elif event.key == pygame.K_DOWN:
                            if self.selected_idx + cols < len(all_p): self.selected_idx += cols
                        elif event.key == pygame.K_LEFT:
                            if self.selected_idx > 0: self.selected_idx -= 1
                        elif event.key == pygame.K_RIGHT:
                            if self.selected_idx < len(all_p) - 1: self.selected_idx += 1
                        elif event.key == pygame.K_i:
                            self.detail_mode = True
                        elif event.key == pygame.K_l:
                            if self.selected_idx < len(all_p):
                                self.listing_mode = True
                                p = all_p[self.selected_idx]
                                self.list_ranges = ultimate_manager.get_price_ranges(p)
                                self.list_bid = self.list_ranges["min"]
                                self.list_buy = self.list_bid + 100
                                self.list_sel = 0
                        continue

                    elif self.club_tab == "DUPLICADOS":
                        if not hasattr(self, "_cached_dups") or self._cached_dups is None:
                            self._cached_dups = self._get_duplicate_list()
                        
                        dups = self._cached_dups
                        if not dups: continue
                        
                        if event.key == pygame.K_UP: 
                            if self.selected_idx > 0:
                                self.selected_idx -= 1
                                if self.selected_idx < self.dup_scroll:
                                    self.dup_scroll = self.selected_idx
                        elif event.key == pygame.K_DOWN:
                            if self.selected_idx < len(dups) - 1:
                                self.selected_idx += 1
                                if self.selected_idx >= self.dup_scroll + 12:
                                    self.dup_scroll = self.selected_idx - 11
                        elif event.key == pygame.K_x:
                            d = dups[self.selected_idx]
                            # Venta rápida optimizada
                            target_uid = d.get("last_uid")
                            all_p_global = ultimate_manager.club_items["players"]
                            for idx, p in enumerate(all_p_global):
                                if p.get("uid") == target_uid:
                                    sold = all_p_global.pop(idx)
                                    val = ultimate_manager.get_quick_sell_value(sold)
                                    ultimate_manager.coins += val
                                    self.msg = f"Vendido: {sold['name']} (+{val}C)"
                                    self.msg_timer = 2.0
                                    self._cached_dups = None
                                    self._cached_inv = None
                                    ultimate_manager.save_ultimate()
                                    break
                        continue

                    elif self.club_tab == "GESTIÓN":
                        mgmt_ids = ["EDIT", "BADGE", "KIT", "WARN"]
                        if ultimate_manager.pending_items: mgmt_ids.insert(0, "PENDING")
                        
                        if self.management_state == "RENAME":
                            if event.key == pygame.K_RETURN:
                                if self.active_input == "NAME":
                                    ultimate_manager.team_name = self.input_text
                                    self.active_input = "SHORT"
                                    self.input_text = ultimate_manager.abbreviation
                                else:
                                    ultimate_manager.abbreviation = self.input_text[:3].upper()
                                    ultimate_manager.save_ultimate()
                                    self.management_state = "MAIN"
                                    self.msg = "¡Identidad actualizada!"
                                    self.msg_timer = 2.0
                            elif event.key == pygame.K_BACKSPACE: self.input_text = self.input_text[:-1]
                            elif event.key == pygame.K_ESCAPE: self.management_state = "MAIN"
                            else:
                                limit = 20 if self.active_input == "NAME" else 3
                                if len(self.input_text) < limit and event.unicode.isprintable():
                                    self.input_text += event.unicode if self.active_input == "NAME" else event.unicode.upper()
                            continue

                        elif self.management_state == "SELECT_BADGE":
                            badges = ultimate_manager.club_items["badges"]
                            if event.key == pygame.K_ESCAPE:
                                self.management_state = "MAIN"
                                self.selected_idx = mgmt_ids.index("BADGE")
                                self.item_scroll = 0
                            elif event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                                self._nav_item_grid(event.key, len(badges))
                            elif event.key == pygame.K_RETURN:
                                ultimate_manager.badge = badges[self.selected_idx]
                                ultimate_manager.save_ultimate()
                                self.msg = "Escudo equipado"
                                self.msg_timer = 2.0
                                self.management_state = "MAIN"
                                self.selected_idx = mgmt_ids.index("BADGE")
                                self.item_scroll = 0
                            continue

                        elif self.management_state == "SELECT_KIT":
                            kits = ultimate_manager.club_items["kits"]
                            if event.key == pygame.K_ESCAPE:
                                self.management_state = "MAIN"
                                self.selected_idx = mgmt_ids.index("KIT")
                                self.item_scroll = 0
                            elif event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                                self._nav_item_grid(event.key, len(kits))
                            elif event.key == pygame.K_RETURN:
                                from data.teams import TEAMS
                                kit = kits[self.selected_idx]
                                full_team = next((t for t in TEAMS if t.get("short") == kit.get("short")), None)
                                if not full_team:
                                    full_team = next((t for t in TEAMS if t.get("name") == kit.get("name")), kit)
                                ultimate_manager.kit = kit
                                ultimate_manager.primary = full_team.get("primary", (0, 100, 200))
                                ultimate_manager.secondary = full_team.get("secondary", (255, 255, 255))
                                ultimate_manager.save_ultimate()
                                self.msg = "Uniforme equipado"
                                self.msg_timer = 2.0
                                self.management_state = "MAIN"
                                self.selected_idx = mgmt_ids.index("KIT")
                                self.item_scroll = 0
                            continue

                        elif self.management_state == "RESET":
                            if event.key == pygame.K_ESCAPE:
                                self.management_state = "MAIN"
                                self.selected_idx = mgmt_ids.index("WARN")
                            elif event.key == pygame.K_BACKSPACE: self.input_text = self.input_text[:-1]
                            elif event.key == pygame.K_RETURN:
                                if self.input_text.upper() == "BORRAR":
                                    ultimate_manager.reset_club()
                                    from scenes.ultimate_setup import UltimateSetupScene
                                    self.manager.transition_to(UltimateSetupScene)
                                    return
                                else:
                                    self.msg = "Escribe BORRAR correctamente"
                                    self.msg_timer = 2.0
                            else:
                                if len(self.input_text) < 10 and event.unicode.isprintable():
                                    self.input_text += event.unicode.upper()
                            continue

                        if event.key == pygame.K_UP: 
                            self.selected_idx = max(0, self.selected_idx - 1)
                            if self.selected_idx < getattr(self, "mgmt_scroll", 0):
                                self.mgmt_scroll = self.selected_idx
                        elif event.key == pygame.K_DOWN: 
                            self.selected_idx = min(len(mgmt_ids) - 1, self.selected_idx + 1)
                            if self.selected_idx >= getattr(self, "mgmt_scroll", 0) + 5:
                                self.mgmt_scroll = self.selected_idx - 4
                        elif event.key == pygame.K_RETURN:
                            current_opt = mgmt_ids[self.selected_idx]
                            if current_opt == "PENDING":
                                self.pack_reveal_items = ultimate_manager.pending_items
                                self.reveal_idx = 0
                                self.reveal_timer = 0
                                self.reveal_scroll = 0
                            elif current_opt == "EDIT":
                                self.management_state = "RENAME"
                                self.input_text = ultimate_manager.team_name
                                self.active_input = "NAME"
                            elif current_opt == "BADGE":
                                if ultimate_manager.club_items["badges"]:
                                    self.management_state = "SELECT_BADGE"
                                    self.selected_idx = 0
                                else:
                                    self.msg = "No tienes escudos extra"
                                    self.msg_timer = 2.0
                            elif current_opt == "KIT":
                                if ultimate_manager.club_items["kits"]:
                                    self.management_state = "SELECT_KIT"
                                    self.selected_idx = 0
                                else:
                                    self.msg = "No tienes kits extra"
                                    self.msg_timer = 2.0
                            elif current_opt == "WARN":
                                self.management_state = "RESET"
                                self.input_text = ""
                        elif event.key == pygame.K_ESCAPE:
                            self.club_tab = "MENU"
                            self.selected_idx = 3
                            self.msg = "Menú de Club"
                            self.msg_timer = 1.0
                        continue

                    elif event.key == pygame.K_ESCAPE:
                        if self.club_tab != "MENU":
                            self.club_tab = "MENU"
                            self.selected_idx = 0
                            self.msg = "Menú de Club"
                            self.msg_timer = 1.0
                        continue

                elif self.tab == "PLAY":
                    # Movimiento entre modos
                    if event.key == pygame.K_UP: self.selected_idx = (self.selected_idx - 1) % 4
                    elif event.key == pygame.K_DOWN: self.selected_idx = (self.selected_idx + 1) % 4
                    elif event.key == pygame.K_RETURN:
                        if self.selected_idx == 1: # LIGA DE CLUBES (Offline)
                            from scenes.ultimate_league import UltimateLeagueScene
                            self.manager.push_scene(UltimateLeagueScene)
                            continue
                        elif self.selected_idx == 3: # TORNEO ELIMINATORIO
                            # Por ahora no implementado, mostramos mensaje
                            self.msg = "Torneo Eliminatorio próximamente..."
                            self.msg_timer = 2.0
                            continue
                            
                        starters = [p for p in ultimate_manager.squad[:11] if p]
                        if len(starters) < 11:
                            self.msg = "¡Necesitas 11 titulares para jugar!"
                            self.msg_timer = 2.0
                            continue
                            
                        p_team = {
                            "primary": ultimate_manager.primary,
                            "secondary": ultimate_manager.secondary,
                            "accent": ultimate_manager.accent,
                            "roster": [p for p in ultimate_manager.squad if p]
                        }
                        if ultimate_manager.badge:
                            for k in ["badge_shape", "primary", "secondary", "accent"]:
                                if k in ultimate_manager.badge:
                                    p_team[k] = ultimate_manager.badge[k]
                        if ultimate_manager.kit:
                            for k in ["primary", "secondary", "accent"]:
                                if k in ultimate_manager.kit:
                                    p_team[k] = ultimate_manager.kit[k]
                        
                        # --- FORZAR IDENTIDAD PERSONALIZADA ---
                        p_team["name"] = ultimate_manager.team_name
                        p_team["short"] = ultimate_manager.abbreviation
                        p_team["roster"] = [p for p in ultimate_manager.squad if p]
                        
                        if self.selected_idx == 2: # DIVISION RIVALS (Online)
                            from scenes.ultimate_league import UltimateLeagueScene
                            self.manager.push_scene(UltimateLeagueScene, is_online=True)
                            continue

                        # Si es 0 (AMISTOSO RÁPIDO Offline)
                        # Seleccionar rival aleatorio (Solo de ligas reales o evento)
                        from data.rosters import get_base_rosters
                        from data.teams import TEAMS
                        all_rosters = get_base_rosters()
                        
                        # Whitelist estricta de ligas reales/evento
                        REAL_LEAGUES = ["ES", "EN", "IT", "FR", "DE", "CO", "FB"]
                        real_teams = [t for t in TEAMS if t.get("league") in REAL_LEAGUES]
                        
                        if not real_teams: real_teams = [t for t in TEAMS if not t.get("is_national")]
                        
                        rival_info = random.choice(real_teams)
                        rival_roster = all_rosters.get(rival_info["short"], [])
                        
                        # Preparar objeto de equipo rival
                        opponent = {
                            "name": rival_info["name"], "short": rival_info["short"],
                            "primary": rival_info["primary"], "secondary": rival_info["secondary"],
                            "accent": rival_info.get("accent", WHITE), "roster": rival_roster[:11] 
                        }
                        
                        self.manager.shared_data.update({
                            "player_team": p_team, "rival_team": opponent, "game_mode": "ultimate",
                            "match_reward": 1200, "starters": starters, "formation": ultimate_manager.formation
                        })
                        from scenes.match import MatchScene
                        self.manager.push_scene(MatchScene)

                elif self.tab == "OBJECTIVES":
                    if event.key == pygame.K_SPACE:
                        bp = ultimate_manager.battle_pass
                        unclaimed = [lv for lv in range(1, bp["level"]) if lv not in bp.get("claimed_levels", [])]
                        if unclaimed:
                            if "claimed_levels" not in bp: bp["claimed_levels"] = []
                            # Claim everything
                            for lv in unclaimed:
                                bp["claimed_levels"].append(lv)
                                # Reward logic: give a Gold Pack for every level for simplicity
                                pack_cfg = {
                                    "id": f"bp_reward_{lv}", "name": f"SOBRE ORO (BP LVL {lv})",
                                    "total_items": 10, "event": "NORMAL", "type": "PACK", "cat": "MIS SOBRES",
                                    "details": {"min_players": 10, "max_players": 10, "rarity": "ORO"}
                                }
                                ultimate_manager.add_reward_pack(pack_cfg)
                            
                            ultimate_manager.save_ultimate()
                            self.msg = f"¡Reclamados {len(unclaimed)} sobres!"
                            self.msg_timer = 3.0



                if self.tab == "MARKET":
                    if self.market_tab == "MENU":
                        if event.key == pygame.K_LEFT: self.market_menu_idx = (self.market_menu_idx - 1) % 2
                        elif event.key == pygame.K_RIGHT: self.market_menu_idx = (self.market_menu_idx + 1) % 2
                        elif event.key == pygame.K_RETURN:
                            targets = ["GLOBAL", "MY_AUCTIONS"]
                            self.market_tab = targets[self.market_menu_idx]
                            self.selected_idx = 0
                            continue
                    
                    elif event.key == pygame.K_ESCAPE:
                        if self.market_tab == "GLOBAL" and self.market_state == "RESULTS":
                            self.market_state = "FILTERS"
                        else:
                            self.market_tab = "MENU"
                            self.market_state = "FILTERS"
                        continue

                    if self.market_tab == "GLOBAL":
                        if self.market_state == "FILTERS":
                            if event.key == pygame.K_UP: self.market_filter_row = max(0, self.market_filter_row - 1)
                            elif event.key == pygame.K_DOWN: self.market_filter_row = min(2, self.market_filter_row + 1)
                            elif event.key == pygame.K_LEFT:
                                if self.market_filter_row == 0: self.m_pos_idx = (self.m_pos_idx - 1) % 5
                                elif self.market_filter_row == 1: self.m_class_idx = (self.m_class_idx - 1) % 5
                            elif event.key == pygame.K_RIGHT:
                                if self.market_filter_row == 0: self.m_pos_idx = (self.m_pos_idx + 1) % 5
                                elif self.market_filter_row == 1: self.m_class_idx = (self.m_class_idx + 1) % 5
                            elif event.key == pygame.K_RETURN and self.market_filter_row == 2:
                                self._search_market()
                        else:
                            if event.key in (pygame.K_BACKSPACE, pygame.K_ESCAPE): 
                                self.market_state = "FILTERS"
                            elif event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT):
                                # Navegación visual para resultados
                                count = len(self.market_results)
                                if count > 0:
                                    # Posiciones visuales para resultados (grid infinito vertical con spacing premium)
                                    positions = []
                                    for i in range(count):
                                        x = 50 + (i % 4) * 295
                                        y = 200 + (i // 4) * 235
                                        positions.append((x + 140, y + 100))
                                    
                                    cur_idx = self.selected_idx - 20
                                    if cur_idx < 0 or cur_idx >= count: cur_idx = 0
                                    
                                    cx, cy = positions[cur_idx]
                                    best_dist = float('inf')
                                    target_idx = cur_idx
                                    for i, (ix, iy) in enumerate(positions):
                                        if i == cur_idx: continue
                                        dist = float('inf')
                                        # Pesamos más el movimiento en el eje deseado
                                        if event.key == pygame.K_LEFT and ix < cx: dist = abs(iy - cy) * 10 + (cx - ix)
                                        elif event.key == pygame.K_RIGHT and ix > cx: dist = abs(iy - cy) * 10 + (ix - cx)
                                        elif event.key == pygame.K_UP and iy < cy: dist = abs(ix - cx) * 10 + (cy - iy)
                                        elif event.key == pygame.K_DOWN and iy > cy: dist = abs(ix - cx) * 10 + (iy - cy)
                                        
                                        if dist < best_dist:
                                            best_dist = dist
                                            target_idx = i
                                    
                                    self.selected_idx = 20 + target_idx
                                    
                                    # AJUSTE AUTOMÁTICO DE SCROLL
                                    # Mantener el índice seleccionado dentro de la ventana de 8 cartas (2 filas)
                                    row_selected = target_idx // 4
                                    current_scroll_row = self.market_scroll_idx // 4
                                    
                                    if row_selected < current_scroll_row:
                                        self.market_scroll_idx = row_selected * 4
                                    elif row_selected >= current_scroll_row + 2:
                                        self.market_scroll_idx = (row_selected - 1) * 4
                                    
                            elif event.key == pygame.K_RETURN:
                                res_idx = self.selected_idx - 20
                                if 0 <= res_idx < len(self.market_results):
                                    auc = self.market_results[res_idx]
                                    success, msg = ultimate_manager.buy_from_market(auc)
                                    self.msg = msg
                                    if success:
                                        self.market_results.pop(res_idx)
                                    self.msg_timer = 2.5
                            
                            elif event.key == pygame.K_p:
                                res_idx = self.selected_idx - 20
                                if 0 <= res_idx < len(self.market_results):
                                    auc = self.market_results[res_idx]
                                    current_bid = auc.get("current_bid", 0)
                                    next_bid = max(current_bid + 50, int(current_bid * 1.05))
                                    # Alinear a múltiplos de 50 para realismo
                                    next_bid = ((next_bid + 49) // 50) * 50
                                    
                                    success, msg = ultimate_manager.bid_on_market(auc, next_bid)
                                    self.msg = msg
                                    self.msg_timer = 2.5
                                    
                            elif event.key == pygame.K_i:
                                res_idx = self.selected_idx - 20
                                if 0 <= res_idx < len(self.market_results):
                                    self.detail_mode = True

                    elif self.market_tab == "MY_AUCTIONS":
                        # Navegación en mis subastas (lista vertical)
                        my_auctions = ultimate_manager.get_my_auctions()
                        if event.key == pygame.K_UP: self.selected_idx = max(0, self.selected_idx - 1)
                        elif event.key == pygame.K_DOWN: self.selected_idx = min(len(my_auctions)-1, self.selected_idx + 1)
                
                elif self.tab == "SBC":
                    if not hasattr(self, "sbc_preview_idx"): self.sbc_preview_idx = 0
                    if event.key == pygame.K_LEFT: self.sbc_preview_idx = (self.sbc_preview_idx - 1) % 2
                    elif event.key == pygame.K_RIGHT: self.sbc_preview_idx = (self.sbc_preview_idx + 1) % 2
                    elif event.key == pygame.K_RETURN:
                        from .ultimate_sbc import SBCScene
                        group = "PREMIUM" if self.sbc_preview_idx == 0 else "FUNDAMENTOS"
                        self.manager.transition_to(SBCScene, group=group)

                elif self.tab == "STORE":
                    if self.pack_reveal_items:
                        # ... (Mantenemos la lógica de revelación existente)
                        if hasattr(self, "walkout_state") and self.walkout_state > 0:
                            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                                if self.walkout_state >= 4: self.walkout_state = 0
                                else: self.walkout_state = 4
                            continue

                        # GESTIÓN DE REVELACIÓN DE SOBRE (Navegación Visual 2D)
                        club_names = [p["name"] for p in ultimate_manager.club_items.get("players", [])]
                        def _is_dup(item):
                            if item["type"] != "player": return False
                            return club_names.count(item["data"]["name"]) >= 1
                            
                        non_dups = sorted([it for it in self.pack_reveal_items if not _is_dup(it)], 
                                       key=lambda it: it["data"].get("ovr", 0) if it["type"] == "player" else 10, reverse=True)
                        dups = sorted([it for it in self.pack_reveal_items if _is_dup(it)], 
                                    key=lambda it: it["data"].get("ovr", 0) if it["type"] == "player" else 10, reverse=True)
                        
                        sorted_items = non_dups + dups
                        visual_order = [self.pack_reveal_items.index(it) for it in sorted_items]
                        
                        try:
                            v_idx = visual_order.index(self.reveal_idx)
                        except:
                            v_idx = 0
                            self.reveal_idx = visual_order[0]
                            
                        if event.key == pygame.K_LEFT: 
                            if v_idx > 0:
                                v_idx -= 1
                                self.reveal_idx = visual_order[v_idx]
                        elif event.key == pygame.K_RIGHT: 
                            if v_idx < len(visual_order) - 1:
                                v_idx += 1
                                self.reveal_idx = visual_order[v_idx]
                        elif event.key == pygame.K_UP: 
                            row = v_idx // 6
                            col = v_idx % 6
                            if row > 0:
                                next_v_idx = (row - 1) * 6 + col
                                self.reveal_idx = visual_order[next_v_idx]
                                if (row - 1) * 260 < self.reveal_scroll:
                                    self.reveal_scroll = (row - 1) * 260
                        elif event.key == pygame.K_DOWN: 
                            row = v_idx // 6
                            col = v_idx % 6
                            max_row = (len(visual_order) - 1) // 6
                            if row < max_row:
                                next_v_idx = min(len(visual_order) - 1, (row + 1) * 6 + col)
                                self.reveal_idx = visual_order[next_v_idx]
                                next_row = next_v_idx // 6
                                if (next_row + 1) * 260 > self.reveal_scroll + 500:
                                    self.reveal_scroll = (next_row + 1) * 260 - 500
                        
                        elif event.key == pygame.K_s: # Guardar individual
                            v_idx = visual_order.index(self.reveal_idx)
                            item = self.pack_reveal_items.pop(self.reveal_idx)
                            if item["type"] == "player": ultimate_manager.club_items["players"].append(item["data"])
                            elif item["type"] == "badge": ultimate_manager.club_items["badges"].append(item["data"])
                            elif item["type"] == "kit": ultimate_manager.club_items["kits"].append(item["data"])
                            elif item["type"] == "consumable": ultimate_manager.club_items["consumables"].append(item["data"])
                            self.msg = "Guardado en Club"
                            self.msg_timer = 1.0
                            from systems.audio_manager import audio_manager
                            audio_manager.play_ui("success")
                            ultimate_manager.pending_items = self.pack_reveal_items
                            if not self.pack_reveal_items: 
                                self.pack_reveal_items = None
                                ultimate_manager.pending_items = []
                            else: 
                                non_dups = sorted([it for it in self.pack_reveal_items if not _is_dup(it)], key=lambda it: it["data"].get("ovr", 0) if it["type"] == "player" else 10, reverse=True)
                                dups = sorted([it for it in self.pack_reveal_items if _is_dup(it)], key=lambda it: it["data"].get("ovr", 0) if it["type"] == "player" else 10, reverse=True)
                                temp_sorted = non_dups + dups
                                temp_order = [self.pack_reveal_items.index(it) for it in temp_sorted]
                                next_v_idx = min(v_idx, len(temp_order) - 1)
                                self.reveal_idx = temp_order[next_v_idx]
                            ultimate_manager.save_ultimate()
                            
                        elif event.key == pygame.K_l: # Listar directo en mercado
                            item = self.pack_reveal_items[self.reveal_idx]
                            if item["type"] == "player":
                                self.listing_mode = True
                                self.listing_source = "PACK"
                                self.list_ranges = ultimate_manager.get_price_ranges(item["data"])
                                self.list_bid = self.list_ranges["min"]
                                self.list_buy = self.list_bid + 100
                                self.list_sel = 0
                            else:
                                self.msg = "Solo jugadores subastables"
                                self.msg_timer = 2.0
                                
                        elif event.key == pygame.K_x: # Venta rápida individual
                            v_idx = visual_order.index(self.reveal_idx)
                            item = self.pack_reveal_items.pop(self.reveal_idx)
                            value = 20 if item["type"] != "player" else ultimate_manager.get_quick_sell_value(item["data"])
                            ultimate_manager.coins += value
                            from systems.audio_manager import audio_manager
                            audio_manager.play_ui("coin_spend")
                            self.msg = f"Vendido por $ {value}"
                            self.msg_timer = 1.0
                            if not self.pack_reveal_items: 
                                self.pack_reveal_items = None
                                ultimate_manager.pending_items = []
                            else: 
                                non_dups = sorted([it for it in self.pack_reveal_items if not _is_dup(it)], key=lambda it: it["data"].get("ovr", 0) if it["type"] == "player" else 10, reverse=True)
                                dups = sorted([it for it in self.pack_reveal_items if _is_dup(it)], key=lambda it: it["data"].get("ovr", 0) if it["type"] == "player" else 10, reverse=True)
                                temp_sorted = non_dups + dups
                                temp_order = [self.pack_reveal_items.index(it) for it in temp_sorted]
                                next_v_idx = min(v_idx, len(temp_order) - 1)
                                self.reveal_idx = temp_order[next_v_idx]
                                ultimate_manager.pending_items = self.pack_reveal_items
                            ultimate_manager.save_ultimate()
                            
                        elif event.key == pygame.K_a: # Guardar todo
                            for item in self.pack_reveal_items:
                                if item["type"] == "player": ultimate_manager.club_items["players"].append(item["data"])
                                elif item["type"] == "badge": ultimate_manager.club_items["badges"].append(item["data"])
                                elif item["type"] == "kit": ultimate_manager.club_items["kits"].append(item["data"])
                                elif item["type"] == "consumable": ultimate_manager.club_items["consumables"].append(item["data"])
                            self.pack_reveal_items = None
                            ultimate_manager.pending_items = []
                            self.msg = "Todo guardado en Club"
                            self.msg_timer = 2.0
                            ultimate_manager.save_ultimate()
                        
                        elif event.key == pygame.K_ESCAPE:
                            self.pack_reveal_items = None
                        continue

                    if self.store_cat == "MIS SOBRES":
                        visible_packs = ultimate_manager.pending_packs
                    else:
                        visible_packs = [p for p in ultimate_manager.store_packs if p.get("cat", "NORMAL") == self.store_cat]
                    
                    if event.key == pygame.K_LEFT: 
                        self.selected_idx = max(0, self.selected_idx - 1)
                    elif event.key == pygame.K_RIGHT: 
                        if visible_packs:
                            self.selected_idx = min(len(visible_packs)-1, self.selected_idx + 1)
                        else:
                            self.selected_idx = 0
                    elif event.key == pygame.K_1: self.store_cat = "NORMAL"; self.selected_idx = 0
                    elif event.key == pygame.K_2: self.store_cat = "PROMO"; self.selected_idx = 0
                    elif event.key == pygame.K_3: self.store_cat = "MIS SOBRES"; self.selected_idx = 0
                    
                    elif event.key == pygame.K_RETURN:
                        if self.selected_idx < len(visible_packs):
                            pack = visible_packs[self.selected_idx]

                            # Lógica para abrir sobres ya poseídos
                            if self.store_cat == "MIS SOBRES":
                                res_items = ultimate_manager.open_pending_pack(self.selected_idx)
                                if res_items:
                                    from systems.audio_manager import audio_manager
                                    audio_manager.play_ui("pack_open")
                                    self.pack_reveal_items = res_items
                                    self.reveal_idx = 0; self.reveal_timer = 0
                                    # Walkout check: animacion solo si es panel o caminante (83+ OVR)
                                    players = [i["data"] for i in res_items if i["type"] == "player"]
                                    best = max(players, key=lambda x: x["ovr"]) if players else None
                                    if best and best.get("ovr", 0) >= 83:
                                        self.walkout_player = best
                                        self.walkout_state = 1
                                    else:
                                        self.walkout_player = None
                                        self.walkout_state = 0
                                    self.walkout_timer = 0
                                    ultimate_manager.save_ultimate()
                                continue

                            # Lógica de compra normal
                            if ultimate_manager.coins >= pack["price"]:
                                from systems.audio_manager import audio_manager
                                audio_manager.play_ui("coin_spend")
                                res = ultimate_manager.buy_item(pack["id"], currency="COINS")
                                
                                if res["status"] == "pack":
                                    from systems.audio_manager import audio_manager
                                    audio_manager.play_ui("pack_open")
                                    self.pack_reveal_items = res["items"]
                                    self.reveal_idx = 0; self.reveal_timer = 0
                                    # Walkout check: animacion solo si es panel o caminante (83+ OVR)
                                    players = [i["data"] for i in res["items"] if i["type"] == "player"]
                                    best = max(players, key=lambda x: x["ovr"]) if players else None
                                    if best and best.get("ovr", 0) >= 83:
                                        self.walkout_player = best
                                        self.walkout_state = 1
                                    else:
                                        self.walkout_player = None
                                        self.walkout_state = 0
                                    self.walkout_timer = 0
                                elif res["status"] == "pick":
                                    self.active_pick = res["pick"]
                                    self.pending_pick_idx = len(ultimate_manager.pending_picks) - 1
                                    self.selected_idx = 0
                                elif res["status"] == "direct":
                                    self.msg = res["msg"]
                                    self.msg_timer = 3.0
                                elif res["status"] == "error":
                                    self.msg = res["msg"]
                                    self.msg_timer = 2.0
                            else:
                                from systems.audio_manager import audio_manager
                                audio_manager.play_ui("error")
                                self.msg = "Monedas insuficientes"
                                self.msg_timer = 2.0

                elif self.tab == "EVOLUTIONS":
                    # Filtrar catálogo para ocultar contenido no anunciado
                    import datetime
                    promo_start = datetime.datetime(2026, 8, 26, 15, 0)
                    now = datetime.datetime.now()
                    visible_evos = [e for e in EVOLUTIONS_DB if e["id"] != "classic_heritage" or now >= promo_start]
                    
                    if not visible_evos:
                        continue
                        
                    self.evo_idx = min(self.evo_idx, len(visible_evos) - 1)
                    evo = visible_evos[self.evo_idx]
                    
                    # Jugadores compatibles para la evo actual
                    compatible_players = [p for p in ultimate_manager.club_items["players"] if check_evolution_eligibility(p, evo["id"])]
                    compatible_players.sort(key=lambda x: x.get("ovr", 0), reverse=True)
                    
                    if self.evo_state == "EVO_SELECT":
                        if event.key == pygame.K_UP:
                            self.evo_idx = max(0, self.evo_idx - 1)
                        elif event.key == pygame.K_DOWN:
                            self.evo_idx = min(len(visible_evos) - 1, self.evo_idx + 1)
                        elif event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_RIGHT):
                            if compatible_players:
                                self.evo_state = "PLAYER_SELECT"
                                self.evo_player_idx = 0
                            else:
                                self.msg = "No tienes jugadores compatibles."
                                self.msg_timer = 2.0
                                
                    elif self.evo_state == "PLAYER_SELECT":
                        if event.key == pygame.K_UP:
                            self.evo_player_idx = max(0, self.evo_player_idx - 1)
                        elif event.key == pygame.K_DOWN:
                            self.evo_player_idx = min(len(compatible_players) - 1, self.evo_player_idx + 1)
                        elif event.key in (pygame.K_LEFT, pygame.K_BACKSPACE, pygame.K_ESCAPE):
                            self.evo_state = "EVO_SELECT"
                        elif event.key == pygame.K_RETURN:
                            if not compatible_players:
                                continue
                            self.evo_player_idx = min(self.evo_player_idx, len(compatible_players) - 1)
                            p = compatible_players[self.evo_player_idx]
                            
                            if "evolution" in p:
                                self.msg = "Ya en evolución"
                            elif not check_evolution_eligibility(p, evo["id"]):
                                self.msg = "No elegible"
                            elif ultimate_manager.coins < evo["cost"]:
                                self.msg = "Monedas insuficientes"
                            else:
                                ultimate_manager.coins -= evo["cost"]
                                p["evolution"] = {"id": evo["id"], "level": 0, "progress": 0}
                                ultimate_manager.save_ultimate()
                                self.msg = f"¡Evolución de {p['name']} iniciada!"
                                self.evo_state = "EVO_SELECT"
                            self.msg_timer = 2.0

    def _search_market(self):
        """Busca en las subastas reales sincronizadas del servidor."""
        # Forzar refresco antes de buscar
        ultimate_manager.refresh_market()
        
        all_auctions = ultimate_manager.market_auctions
        pos_list = ["TODOS", "POR", "DEF", "MED", "DEL"]
        rar_list = ["TODOS", "LEYENDA", "ORO", "PLATA", "BRONCE"]
        
        filtered = []
        for auc in all_auctions:
            p = auc.get("player_data", {})
            if not p: continue
            
            # Filtro de Posición
            p_pos = p.get("pos", "")
            m_pos = pos_list[self.m_pos_idx]
            match_pos = True
            if m_pos == "POR" and p_pos != "GK": match_pos = False
            elif m_pos == "DEF" and p_pos not in ["LB", "CB", "RB", "LWB", "RWB"]: match_pos = False
            elif m_pos == "MED" and p_pos not in ["CM", "CDM", "CAM", "LM", "RM"]: match_pos = False
            elif m_pos == "DEL" and p_pos not in ["ST", "CF", "LW", "RW"]: match_pos = False
            
            if not match_pos: continue
            
            # Filtro de Rareza/Clase
            m_rar = rar_list[self.m_class_idx]
            p_rar = p.get("rarity", "ORO")
            is_l = p.get("is_legend", False)
            match_rar = True
            if m_rar == "LEYENDA" and not is_l: match_rar = False
            elif m_rar == "ORO" and (p_rar != "ORO" or is_l): match_rar = False
            elif m_rar == "PLATA" and (p_rar != "PLATA" or is_l): match_rar = False
            elif m_rar == "BRONCE" and (p_rar != "BRONCE" or is_l): match_rar = False
            
            if match_rar:
                filtered.append(auc)
        
        # Ordenar por OVR de mayor a menor
        filtered.sort(key=lambda a: a.get("player_data", {}).get("ovr", 0), reverse=True)
        
        self.market_results = filtered
        self.market_state = "RESULTS"
        self.selected_idx = 20
        self.market_scroll_idx = 0
        self.selected_idx = 20

    def draw_text(self, screen, text, x, y, size=20, color=WHITE, bold=False, center=False, alpha=255):
        font_key = f"{size}_{bold}"
        if font_key not in self.fonts:
            self.fonts[font_key] = pygame.font.SysFont("Arial", size, bold=bold)
        
        font = self.fonts[font_key]
        surf = font.render(str(text), True, color)
        if alpha < 255:
            surf.set_alpha(alpha)
        rect = surf.get_rect()
        if center: rect.center = (x, y)
        else: rect.topleft = (x, y)
        screen.blit(surf, rect)

    def _draw_objectives(self, screen):
        self.draw_text(screen, "OBJETIVOS Y PASE DE BATALLA", 50, 110, size=28, color=self.colors["accent"], bold=True)
        
        bp = ultimate_manager.battle_pass
        objs = ultimate_manager.daily_objectives
        
        # --- PASE DE BATALLA (Arriba) ---
        bp_rect = pygame.Rect(50, 160, 1180, 120)
        pygame.draw.rect(screen, (30, 35, 55), bp_rect, border_radius=15)
        pygame.draw.rect(screen, self.colors["accent"], bp_rect, 2, border_radius=15)
        
        self.draw_text(screen, f"NIVEL DE TEMPORADA: {bp['level']}", 80, 180, size=24, color=WHITE, bold=True)
        self.draw_text(screen, f"XP: {bp['xp']} / {bp['level'] * 1000}", 80, 220, size=18, color=UI_TEXT_DIM)
        
        # Barra de XP
        bar_w = 800
        bar_h = 20
        pygame.draw.rect(screen, (15, 20, 35), (80, 245, bar_w, bar_h), border_radius=5)
        progress = min(1.0, bp['xp'] / (bp['level'] * 1000))
        if progress > 0:
            pygame.draw.rect(screen, (0, 255, 120), (80, 245, int(bar_w * progress), bar_h), border_radius=5)
            
        # Recompensa próximo nivel
        self.draw_text(screen, "PRÓXIMA RECOMPENSA:", 920, 180, size=14, color=UI_TEXT_DIM)
        self.draw_text(screen, f"SOBRE ORO (Nivel {bp['level'] + 1})", 920, 205, size=18, color=GOLD, bold=True)
        
        unclaimed = [lv for lv in range(1, bp["level"]) if lv not in bp.get("claimed_levels", [])]
        if unclaimed:
            claim_rect = pygame.Rect(920, 235, 200, 30)
            pygame.draw.rect(screen, (0, 200, 100), claim_rect, border_radius=5)
            self.draw_text(screen, "PULSA [ESPACIO] PARA RECLAMAR", 1020, 250, size=14, color=WHITE, bold=True, center=True)
        
        # --- OBJETIVOS DIARIOS (Abajo) ---
        self.draw_text(screen, "OBJETIVOS DIARIOS (Se reinician 18:00 UTC)", 50, 310, size=20, color=WHITE, bold=True)
        
        for i, obj in enumerate(objs):
            y = 350 + i * 90
            obj_rect = pygame.Rect(50, y, 1180, 75)
            pygame.draw.rect(screen, (25, 30, 50), obj_rect, border_radius=10)
            
            # Estado
            if obj["completed"]:
                pygame.draw.rect(screen, (0, 200, 80), obj_rect, 2, border_radius=10)
                status_color = (0, 255, 120)
                status_text = "COMPLETADO"
            else:
                pygame.draw.rect(screen, (50, 60, 90), obj_rect, 1, border_radius=10)
                status_color = UI_TEXT_DIM
                status_text = f"{obj['progress']} / {obj['target']}"
                
            self.draw_text(screen, obj["desc"], 70, y + 25, size=20, color=WHITE)
            self.draw_text(screen, f"+{obj['xp']} XP", 70, y + 50, size=14, color=self.colors["accent"])
            self.draw_text(screen, status_text, 1150, y + 27, size=20, color=status_color, bold=True, center=True)
