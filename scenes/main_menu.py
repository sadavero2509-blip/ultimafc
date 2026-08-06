import pygame
import math
import random
from settings import *
from scene_manager import BaseScene


class MenuScene(BaseScene):
    """Clase base para menús con utilidades de renderizado."""
    def __init__(self, manager):
        super().__init__(manager)
        
    def handle_events(self, events):
        for event in events:
            self.handle_event(event)

    def handle_event(self, event):
        """Sobrescribir en subclases."""
        pass

    def draw_text(self, surface, text, x, y, size=24, color=(255, 255, 255), bold=False, alpha=255, center=False):
        try:
            font = pygame.font.SysFont("Arial", size, bold=bold)
        except:
            font = pygame.font.Font(None, size)
        
        img = font.render(str(text), True, color)
        if alpha < 255:
            img.set_alpha(alpha)
            
        render_x = x
        if center:
            render_x = x - img.get_width() // 2
            
        surface.blit(img, (render_x, y))


class Particle:
    """Partícula decorativa para el fondo del menú estilo EA SPORTS FC."""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.uniform(1.5, 4.0)
        self.speed = random.uniform(20, 50)
        self.alpha = random.randint(50, 150)
        self.angle = random.uniform(0, math.pi * 2)

    def update(self, dt):
        self.y -= self.speed * dt
        self.x += math.sin(self.angle) * 12 * dt
        self.angle += dt * 0.6
        if self.y < -10:
            self.y = HEIGHT + 10
            self.x = random.randint(0, WIDTH)

    def draw(self, surface):
        s = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        color = UI_ACCENT if random.random() > 0.3 else (0, 180, 255)
        pygame.draw.circle(s, (*color, self.alpha), (int(self.size), int(self.size)), int(self.size))
        surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))


class MainMenuScene(BaseScene):
    """Menú Principal estilo EA SPORTS FC / FIFA:
    - Pantalla de Presentación Inicial (Title Splash Screen 'Press Any Key')
    - Hub Principal de Modos con tarjetas heroicas (Partido Rápido, Carrera, Ultimate Club, Torneos, Planteles, Opciones)
    - Widget de Login/Cuenta en la esquina superior derecha con atajo [L]
    - Salir en esquina inferior con Modal de Confirmación [ESC]
    """

    STATE_SPLASH = "splash"
    STATE_HUB = "hub"

    def __init__(self, manager):
        super().__init__(manager)
        self.time = 0
        self.state = self.STATE_SPLASH
        
        # Tarjetas de Modos (Estilo EA SPORTS FC Carousel)
        self.selected_card = 0
        self.cards = [
            {
                "id": "quick_match",
                "title": "PARTIDO RÁPIDO",
                "badge": "AMISTOSO DIRECTO",
                "desc": "Sal al campo al instante en una exhibición personalizada con cualquier equipo.",
                "icon": "⚽",
                "color": (0, 200, 150),
            },
            {
                "id": "career",
                "title": "MODO CARRERA",
                "badge": "JUGADOR & DT",
                "desc": "Dirige un club como DT o construye la carrera de tu estrella con ofertas y mensajes.",
                "icon": "👑",
                "color": (255, 180, 0),
            },
            {
                "id": "ultimate",
                "title": "ULTIMATE CLUB",
                "badge": "CARTAS & SBC",
                "desc": "Construye la plantilla de tus sueños, abre sobres de cartas y compite online.",
                "icon": "🃏",
                "color": (180, 80, 255),
            },
            {
                "id": "tournaments",
                "title": "TORNEOS Y LIGAS",
                "badge": "COPAS NACIONALES",
                "desc": "Compite en ligas de primera división, copas eliminatorias y torneos personalizados.",
                "icon": "🏆",
                "color": (50, 150, 250),
            },
            {
                "id": "rosters",
                "title": "PLANTELES",
                "badge": "11 INICIAL & TÁCTICAS",
                "desc": "Edita la formación predeterminada y el 11 inicial de cualquier equipo con confirmación.",
                "icon": "📋",
                "color": (255, 90, 90),
            },
            {
                "id": "settings",
                "title": "CONFIGURACIÓN",
                "badge": "DIFICULTAD & OPCIONES",
                "desc": "Ajusta el nivel de la IA (Aficionado a Leyenda), sonido y controles de juego.",
                "icon": "⚙️",
                "color": (160, 170, 190),
            },
        ]

        self.particles = [Particle() for _ in range(70)]
        self.quit_modal_active = False
        self.settings_modal_active = False
        
        # Toast notifications
        self.toast_msg = ""
        self.toast_timer = 0.0

        from systems.network import NetworkManager
        self.net = NetworkManager()
        
        from systems.audio_manager import audio_manager
        audio_manager.play_menu_music()

        # Fuentes estilo EA FC
        try:
            self.font_logo = pygame.font.SysFont("Impact", 80)
            self.font_card_title = pygame.font.SysFont("Impact", 30)
            self.font_badge = pygame.font.SysFont("Arial", 12, bold=True)
            self.font_desc = pygame.font.SysFont("Arial", 14)
            self.font_text = pygame.font.SysFont("Arial", 16)
            self.font_bold = pygame.font.SysFont("Arial", 16, bold=True)
            self.font_hint = pygame.font.SysFont("Arial", 15)
            self.font_press = pygame.font.SysFont("Arial", 22, bold=True)
            self.font_user = pygame.font.SysFont("Arial", 15, bold=True)
            self.font_icon = pygame.font.SysFont("Segoe UI Emoji", 40)
        except:
            self.font_logo = pygame.font.Font(None, 80)
            self.font_card_title = pygame.font.Font(None, 30)
            self.font_badge = pygame.font.Font(None, 12)
            self.font_desc = pygame.font.Font(None, 14)
            self.font_text = pygame.font.Font(None, 16)
            self.font_bold = pygame.font.Font(None, 16)
            self.font_hint = pygame.font.Font(None, 15)
            self.font_press = pygame.font.Font(None, 22)
            self.font_user = pygame.font.Font(None, 15)
            self.font_icon = pygame.font.Font(None, 40)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                self.quit_modal_active = True
                return

            if event.type == pygame.KEYDOWN:
                # 1. MODAL DE CONFIRMACIÓN DE SALIDA
                if self.quit_modal_active:
                    if event.key == pygame.K_RETURN:
                        pygame.event.post(pygame.event.Event(pygame.QUIT))
                    elif event.key == pygame.K_ESCAPE:
                        self.quit_modal_active = False
                    return

                # 2. MODAL DE CONFIGURACIÓN DE DIFICULTAD
                if self.settings_modal_active:
                    if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                        self.settings_modal_active = False
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        self._adjust_difficulty(-1)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self._adjust_difficulty(1)
                    return

                # 3. PANTALLA DE PRESENTACIÓN INICIAL (SPLASH)
                if self.state == self.STATE_SPLASH:
                    from systems.audio_manager import audio_manager
                    audio_manager.play_pass()
                    self.state = self.STATE_HUB
                    return

                # 4. HUB PRINCIPAL (CAROUSEL DE MODOS EA FC)
                if self.state == self.STATE_HUB:
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        self.selected_card = (self.selected_card - 1) % len(self.cards)
                        from systems.audio_manager import audio_manager
                        audio_manager.play_whistle() if False else None
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.selected_card = (self.selected_card + 1) % len(self.cards)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self._launch_selected_card()
                    elif event.key == pygame.K_l:
                        # Atajo directo a Iniciar Sesión / Gestionar Cuenta
                        from scenes.login import LoginScene
                        self.manager.transition_to(LoginScene)
                    elif event.key == pygame.K_ESCAPE:
                        self.quit_modal_active = True

    def _launch_selected_card(self):
        card_id = self.cards[self.selected_card]["id"]
        from systems.audio_manager import audio_manager
        audio_manager.play_pass()

        if card_id == "quick_match":
            from scenes.team_select import TeamSelectScene
            self.manager.transition_to(TeamSelectScene, context={"mode": "friendly"})

        elif card_id == "career":
            from data.career_manager import career_manager
            if career_manager.active:
                from scenes.career_hub import CareerHubScene
                self.manager.transition_to(CareerHubScene)
            else:
                from scenes.career_setup import CareerSetupScene
                self.manager.transition_to(CareerSetupScene)

        elif card_id == "ultimate":
            from systems.network import NetworkManager
            net = NetworkManager()
            if net.is_remote_server or True:
                from scenes.ultimate_hub import UltimateHubScene
                self.manager.transition_to(UltimateHubScene)
            else:
                self._show_toast("[!] Ultimate Club requiere conexión al servidor central")

        elif card_id == "tournaments":
            from scenes.tournament_type_select import TournamentTypeSelectScene
            self.manager.transition_to(TournamentTypeSelectScene)

        elif card_id == "rosters":
            from scenes.team_viewer import TeamViewerScene
            self.manager.transition_to(TeamViewerScene)

        elif card_id == "settings":
            self.settings_modal_active = True

    def _adjust_difficulty(self, step):
        from data.career_manager import career_manager
        cur_diff = self.manager.shared_data.get("difficulty", 5)
        new_diff = max(1, min(10, cur_diff + step))
        self.manager.shared_data["difficulty"] = new_diff
        self._show_toast(f"Dificultad ajustada: Nivel {new_diff}/10")

    def _show_toast(self, msg):
        self.toast_msg = msg
        self.toast_timer = 3.0

    def update(self, dt):
        self.time += dt
        for p in self.particles:
            p.update(dt)
        if self.toast_timer > 0:
            self.toast_timer -= dt
            if self.toast_timer <= 0:
                self.toast_msg = ""

    def draw(self, surface):
        # Fondo degradado de estadio (Estilo EA SPORTS FC Dark Theme)
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(10 + ratio * 12)
            g = int(14 + ratio * 10)
            b = int(28 + ratio * 22)
            pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

        # Cancha difuminada al fondo
        self._draw_bg_pitch(surface)

        # Partículas flotantes
        for p in self.particles:
            p.draw(surface)

        # Renderizar vista según estado
        if self.state == self.STATE_SPLASH:
            self._draw_splash_screen(surface)
        else:
            self._draw_hub_screen(surface)

        # Overlays superiores e inferiores
        self._draw_toast(surface)

        if self.settings_modal_active:
            self._draw_settings_modal(surface)

        if self.quit_modal_active:
            self._draw_quit_modal(surface)

    # ═══════════════════════════════════════════
    # 1. PANTALLA DE PRESENTACIÓN INICIAL (SPLASH)
    # ═══════════════════════════════════════════
    def _draw_splash_screen(self, surface):
        pulse = (math.sin(self.time * 2.5) + 1) / 2
        
        # Resplandor central del estadio
        center_glow = pygame.Surface((600, 300), pygame.SRCALPHA)
        glow_alpha = int(40 + pulse * 40)
        pygame.draw.ellipse(center_glow, (0, 200, 150, glow_alpha), (0, 0, 600, 300))
        surface.blit(center_glow, (WIDTH//2 - 300, HEIGHT//2 - 180))

        # Logo Grande ULTIMA FC 27
        title_str = "ULTIMA  FC  27"
        glow_color = (
            int(UI_ACCENT[0] * 0.7 + pulse * 80),
            int(UI_ACCENT[1] * 0.7 + pulse * 55),
            int(UI_ACCENT[2] * 0.4 + pulse * 40),
        )

        shadow = self.font_logo.render(title_str, True, (0, 0, 0))
        surface.blit(shadow, (WIDTH//2 - shadow.get_width()//2 + 4, HEIGHT//2 - 110 + 4))

        logo = self.font_logo.render(title_str, True, glow_color)
        surface.blit(logo, (WIDTH//2 - logo.get_width()//2, HEIGHT//2 - 110))

        # Líneas decorativas doradas/cyan
        line_w = 400 + int(pulse * 60)
        pygame.draw.line(surface, UI_ACCENT, (WIDTH//2 - line_w//2, HEIGHT//2 - 25), (WIDTH//2 + line_w//2, HEIGHT//2 - 25), 3)

        sub_str = "---  EA SPORTS STYLE FOOTBALL EXPERIENCE  ---"
        sub_s = self.font_bold.render(sub_str, True, UI_TEXT_DIM)
        surface.blit(sub_s, (WIDTH//2 - sub_s.get_width()//2, HEIGHT//2 + 5))

        # Prompt Pulsante "PULSA CUALQUIER TECLA"
        press_alpha = int(120 + 135 * math.sin(self.time * 4))
        press_s = self.font_press.render("▶  PULSA CUALQUIER TECLA PARA CONTINUAR  ◀", True, UI_ACCENT)
        press_s.set_alpha(press_alpha)
        surface.blit(press_s, (WIDTH//2 - press_s.get_width()//2, HEIGHT - 120))

        # Pie de versión
        ver_s = self.font_hint.render(f"v{GAME_VERSION}  ·  ULTIMA FOOTBALL CLUB 2027", True, (80, 90, 110))
        surface.blit(ver_s, (WIDTH//2 - ver_s.get_width()//2, HEIGHT - 40))

    # ═══════════════════════════════════════════
    # 2. HUB PRINCIPAL DE MODOS (CAROUSEL EA FC)
    # ═══════════════════════════════════════════
    def _draw_hub_screen(self, surface):
        # ── WIDGET ESQUINA SUPERIOR DERECHA: CUENTA / LOGIN ──
        self._draw_account_corner_widget(surface)

        # ── ENCABEZADO ARRIBA A LA IZQUIERDA ──
        badge_title = self.font_card_title.render("ULTIMA FC 27", True, UI_ACCENT)
        surface.blit(badge_title, (40, 20))
        hub_lbl = self.font_hint.render("MENÚ PRINCIPAL DE MODOS", True, UI_TEXT_DIM)
        surface.blit(hub_lbl, (40, 52))

        # ── CAROUSEL HORIZONTAL DE TARJETAS (CARDS) ──
        card_w = 260
        card_h = 360
        spacing = 25
        start_x = 50
        card_y = 110

        # Scroll suave hacia la tarjeta seleccionada
        target_scroll_x = (WIDTH // 2) - (self.selected_card * (card_w + spacing) + card_w // 2)
        if not hasattr(self, 'scroll_x'): self.scroll_x = float(target_scroll_x)
        self.scroll_x += (target_scroll_x - self.scroll_x) * 0.2

        for i, card in enumerate(self.cards):
            cx = int(self.scroll_x + i * (card_w + spacing))
            # Omitir renderizado si está fuera de pantalla
            if cx + card_w < -100 or cx > WIDTH + 100:
                continue

            is_sel = (i == self.selected_card)
            c_rect = pygame.Rect(cx, card_y, card_w, card_h)

            # Efecto de elevación al estar seleccionada
            if is_sel:
                c_rect.y -= 12
                c_rect.height += 10

            # Fondo de la tarjeta
            bg_color = (25, 32, 50) if is_sel else (18, 22, 34)
            pygame.draw.rect(surface, bg_color, c_rect, border_radius=16)

            # Borde brillante animado
            if is_sel:
                pulse = (math.sin(self.time * 5) + 1) / 2
                borderColor = card["color"]
                pygame.draw.rect(surface, borderColor, c_rect, 3, border_radius=16)
                
                # Glow resplandor inferior
                glow_s = pygame.Surface((card_w, 15), pygame.SRCALPHA)
                glow_s.fill((*borderColor, int(80 + pulse * 60)))
                surface.blit(glow_s, (cx, c_rect.bottom - 15))
            else:
                pygame.draw.rect(surface, (45, 55, 75), c_rect, 1, border_radius=16)

            # Insignia superior
            badge_bg = pygame.Rect(c_rect.left + 15, c_rect.top + 15, 150, 22)
            pygame.draw.rect(surface, card["color"] if is_sel else (50, 60, 80), badge_bg, border_radius=6)
            bs = self.font_badge.render(card["badge"], True, (0, 0, 0) if is_sel else WHITE)
            surface.blit(bs, (badge_bg.centerx - bs.get_width()//2, badge_bg.top + 4))

            # Icono principal
            try:
                ic_s = self.font_icon.render(card["icon"], True, WHITE)
                surface.blit(ic_s, (c_rect.centerx - ic_s.get_width()//2, c_rect.top + 55))
            except: pass

            # Título de la tarjeta
            ts = self.font_card_title.render(card["title"], True, WHITE if is_sel else UI_TEXT_DIM)
            surface.blit(ts, (c_rect.centerx - ts.get_width()//2, c_rect.top + 115))

            # Separador
            pygame.draw.line(surface, card["color"] if is_sel else (50, 60, 80), (c_rect.left + 20, c_rect.top + 155), (c_rect.right - 20, c_rect.top + 155), 1)

            # Descripción multitexto
            words = card["desc"].split()
            lines = []
            cur_line = ""
            for w in words:
                test = cur_line + " " + w if cur_line else w
                if self.font_desc.size(test)[0] < card_w - 30:
                    cur_line = test
                else:
                    lines.append(cur_line)
                    cur_line = w
            if cur_line: lines.append(cur_line)

            for dy, lstr in enumerate(lines[:4]):
                ds = self.font_desc.render(lstr, True, WHITE if is_sel else UI_TEXT_DIM)
                surface.blit(ds, (c_rect.left + 15, c_rect.top + 175 + dy * 20))

            # Botón de acción en la tarjeta activa
            if is_sel:
                action_rect = pygame.Rect(c_rect.left + 15, c_rect.bottom - 45, card_w - 30, 32)
                pygame.draw.rect(surface, card["color"], action_rect, border_radius=8)
                act_str = "ENTRAR [ ENTER ]"
                as_ = self.font_bold.render(act_str, True, (0, 0, 0))
                surface.blit(as_, (action_rect.centerx - as_.get_width()//2, action_rect.top + 7))

        # ── ESQUINA INFERIOR IZQUIERDA: BOTÓN SALIR SUTIL ──
        quit_hint = self.font_hint.render("[ ESC ] Salir del juego", True, (180, 100, 100))
        surface.blit(quit_hint, (40, HEIGHT - 35))

        # ── ESQUINA INFERIOR DERECHA: ATAYOS DE NAVEGACIÓN ──
        nav_hint = self.font_hint.render("◀ ▶ Seleccionar Modo  ·  ENTER Confirmar  ·  L Gestionar Cuenta", True, UI_TEXT_DIM)
        surface.blit(nav_hint, (WIDTH - nav_hint.get_width() - 40, HEIGHT - 35))

    # ═══════════════════════════════════════════
    # 3. WIDGET DE CUENTA Y LOGIN (ESQUINA SUPERIOR DERECHA)
    # ═══════════════════════════════════════════
    def _draw_account_corner_widget(self, surface):
        """Muestra el estado de la cuenta en la esquina superior derecha."""
        from systems.network import NetworkManager
        net = NetworkManager()

        user_name = "Invitar/Offline"
        creds_path = "saves/creds.json"
        if os.path.exists(creds_path):
            try:
                import json
                with open(creds_path, "r", encoding="utf-8") as f:
                    cdata = json.load(f)
                    user_name = cdata.get("username", "Jugador")
            except: pass
        elif net.connected:
            user_name = "Usuario Conectado"

        widget_w, widget_h = 240, 44
        rect = pygame.Rect(WIDTH - widget_w - 30, 15, widget_w, widget_h)
        pygame.draw.rect(surface, (20, 26, 42), rect, border_radius=10)
        pygame.draw.rect(surface, UI_ACCENT if net.connected else (100, 110, 130), rect, 1, border_radius=10)

        # Avatar
        pygame.draw.circle(surface, UI_ACCENT if net.connected else (120, 120, 120), (rect.left + 22, rect.centery), 12)
        u_icon = self.font_hint.render("👤", True, (0, 0, 0))
        surface.blit(u_icon, (rect.left + 15, rect.centery - u_icon.get_height()//2))

        # Username & Status
        un = self.font_user.render(user_name[:14], True, WHITE)
        surface.blit(un, (rect.left + 42, rect.top + 4))

        status_str = "ONLINE" if net.connected else "OFFLINE"
        status_c = (0, 220, 120) if net.connected else (220, 100, 100)
        ss = self.font_badge.render(f"● {status_str}  ·  [L] Cuenta", True, status_c)
        surface.blit(ss, (rect.left + 42, rect.top + 23))

    # ═══════════════════════════════════════════
    # 4. MODAL DE CONFIRMACIÓN DE SALIDA (QUIT MODAL)
    # ═══════════════════════════════════════════
    def _draw_quit_modal(self, surface):
        """Ventana modal interactiva pidiendo confirmación antes de salir del juego."""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 10, 18, 220))
        surface.blit(overlay, (0, 0))

        box_w, box_h = 500, 220
        box = pygame.Rect(WIDTH//2 - box_w//2, HEIGHT//2 - box_h//2, box_w, box_h)
        pygame.draw.rect(surface, (22, 26, 40), box, border_radius=16)
        pygame.draw.rect(surface, (255, 90, 90), box, 2, border_radius=16)

        title = self.font_card_title.render("SALIR DE ULTIMA FC 27", True, (255, 90, 90))
        surface.blit(title, (box.centerx - title.get_width()//2, box.top + 25))

        msg = self.font_text.render("¿Estás seguro de que deseas salir del juego?", True, WHITE)
        surface.blit(msg, (box.centerx - msg.get_width()//2, box.top + 80))

        btn_y = box.bottom - 55
        pygame.draw.line(surface, (50, 55, 75), (box.left + 20, btn_y - 12), (box.right - 20, btn_y - 12), 1)

        btn_yes = self.font_bold.render("[ ENTER ]  Sí, Salir", True, (255, 90, 90))
        btn_no = self.font_bold.render("[ ESC ]  Cancelar / Volver", True, UI_ACCENT)

        surface.blit(btn_yes, (box.left + 40, btn_y))
        surface.blit(btn_no, (box.right - 40 - btn_no.get_width(), btn_y))

    # ═══════════════════════════════════════════
    # 5. MODAL DE CONFIGURACIÓN Y DIFICULTAD
    # ═══════════════════════════════════════════
    def _draw_settings_modal(self, surface):
        """Modal de configuración de dificultad y opciones de juego."""
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((8, 10, 18, 220))
        surface.blit(overlay, (0, 0))

        box_w, box_h = 560, 320
        box = pygame.Rect(WIDTH//2 - box_w//2, HEIGHT//2 - box_h//2, box_w, box_h)
        pygame.draw.rect(surface, (22, 28, 44), box, border_radius=16)
        pygame.draw.rect(surface, UI_ACCENT, box, 2, border_radius=16)

        title = self.font_card_title.render("CONFIGURACIÓN DE JUEGO", True, UI_ACCENT)
        surface.blit(title, (box.centerx - title.get_width()//2, box.top + 20))
        pygame.draw.line(surface, UI_ACCENT, (box.left + 30, box.top + 55), (box.right - 30, box.top + 55), 1)

        # Dificultad
        cur_diff = self.manager.shared_data.get("difficulty", 5)
        diff_names = {1: "AFICIONADO", 3: "SEMI-PRO", 5: "PROFESIONAL", 7: "CLASE MUNDIAL", 9: "LEYENDA", 10: "LEYENDA TOTAL"}
        dname = diff_names.get(cur_diff, f"NIVEL {cur_diff}")

        dlbl = self.font_bold.render("NIVEL DE DIFICULTAD DE LA IA:", True, WHITE)
        surface.blit(dlbl, (box.left + 40, box.top + 80))

        # Selector de dificultad
        sel_box = pygame.Rect(box.left + 40, box.top + 110, box_w - 80, 50)
        pygame.draw.rect(surface, (32, 40, 62), sel_box, border_radius=10)
        pygame.draw.rect(surface, UI_ACCENT, sel_box, 1, border_radius=10)

        arr_l = self.font_bold.render("◀", True, UI_ACCENT)
        arr_r = self.font_bold.render("▶", True, UI_ACCENT)
        surface.blit(arr_l, (sel_box.left + 15, sel_box.centery - arr_l.get_height()//2))
        surface.blit(arr_r, (sel_box.right - 25, sel_box.centery - arr_r.get_height()//2))

        dval = self.font_bold.render(f"Nivel {cur_diff}/10 — {dname}", True, GOLD)
        surface.blit(dval, (sel_box.centerx - dval.get_width()//2, sel_box.centery - dval.get_height()//2))

        # Descripción
        desc_str = "IA con respuestas dinámicas, cobertura de líneas de pase y achique de portero 1v1."
        desc_s = self.font_desc.render(desc_str, True, UI_TEXT_DIM)
        surface.blit(desc_s, (box.centerx - desc_s.get_width()//2, box.top + 175))

        btn_y = box.bottom - 45
        pygame.draw.line(surface, (50, 55, 75), (box.left + 20, btn_y - 10), (box.right - 20, btn_y - 10), 1)

        hint = self.font_hint.render("← → Cambiar Dificultad  ·  ENTER / ESC Cerrar", True, UI_ACCENT)
        surface.blit(hint, (box.centerx - hint.get_width()//2, btn_y))

    def _draw_toast(self, surface):
        if self.toast_timer <= 0 or not self.toast_msg: return

        alpha = min(255, int(self.toast_timer * 200))
        toast_w, toast_h = 500, 40
        rect = pygame.Rect(WIDTH//2 - toast_w//2, 15, toast_w, toast_h)

        tsurf = pygame.Surface((toast_w, toast_h), pygame.SRCALPHA)
        tsurf.fill((20, 35, 50, min(230, alpha)))
        pygame.draw.rect(tsurf, (0, 200, 150, alpha), (0, 0, toast_w, toast_h), 2, border_radius=10)

        msg_s = self.font_bold.render(self.toast_msg, True, (255, 255, 255))
        tsurf.blit(msg_s, (toast_w//2 - msg_s.get_width()//2, toast_h//2 - msg_s.get_height()//2))
        surface.blit(tsurf, rect)

    def _draw_bg_pitch(self, surface):
        """Dibuja una cancha tenue de fondo."""
        alpha_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pitch_color = (34, 139, 34, 12)
        line_color = (255, 255, 255, 8)

        rect = pygame.Rect(100, 220, WIDTH - 200, HEIGHT - 260)
        pygame.draw.rect(alpha_surf, pitch_color, rect)
        pygame.draw.rect(alpha_surf, line_color, rect, 2)
        mid_x = WIDTH // 2
        pygame.draw.line(alpha_surf, line_color, (mid_x, rect.top), (mid_x, rect.bottom), 1)
        pygame.draw.circle(alpha_surf, line_color, (mid_x, rect.centery), 70, 1)

        surface.blit(alpha_surf, (0, 0))
