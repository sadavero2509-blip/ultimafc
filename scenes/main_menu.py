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
    """Partícula decorativa para el fondo del menú."""
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.uniform(1, 3)
        self.speed = random.uniform(15, 40)
        self.alpha = random.randint(40, 120)
        self.angle = random.uniform(0, math.pi * 2)

    def update(self, dt):
        self.y -= self.speed * dt
        self.x += math.sin(self.angle) * 10 * dt
        self.angle += dt * 0.5
        if self.y < -5:
            self.y = HEIGHT + 5
            self.x = random.randint(0, WIDTH)

    def draw(self, surface):
        s = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
        pygame.draw.circle(s, (*UI_ACCENT, self.alpha), (int(self.size), int(self.size)), int(self.size))
        surface.blit(s, (int(self.x - self.size), int(self.y - self.size)))


class MainMenuScene(BaseScene):
    def __init__(self, manager):
        super().__init__(manager)
        self.time = 0
        self.selected = 0
        from systems.network import NetworkManager
        self.net = NetworkManager()
        self.options = ["JUGAR", "ULTIMATE CLUB", "ONLINE", "INICIAR SESIÓN" if not self.net.connected else "CAMBIAR CUENTA", "SALIR"]
        self.particles = [Particle() for _ in range(60)]
        
        # Toast notification para mensajes de error
        self.toast_message = ""
        self.toast_timer = 0
        
        from systems.audio_manager import audio_manager
        audio_manager.play_menu_music()

        # Fuentes
        try:
            self.font_title = pygame.font.SysFont("Impact", 72)
            self.font_subtitle = pygame.font.SysFont("Arial", 22)
            self.font_option = pygame.font.SysFont("Arial", 36, bold=True)
            self.font_hint = pygame.font.SysFont("Arial", 16)
            self.font_toast = pygame.font.SysFont("Arial", 20, bold=True)
        except:
            self.font_title = pygame.font.Font(None, 72)
            self.font_subtitle = pygame.font.Font(None, 22)
            self.font_option = pygame.font.Font(None, 36)
            self.font_hint = pygame.font.Font(None, 16)
            self.font_toast = pygame.font.Font(None, 20)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected = (self.selected - 1) % len(self.options)
                elif event.key == pygame.K_DOWN:
                    self.selected = (self.selected + 1) % len(self.options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self._select_option()
                elif event.key == pygame.K_ESCAPE:
                    pygame.event.post(pygame.event.Event(pygame.QUIT))

    def _select_option(self):
        if self.options[self.selected] == "JUGAR":
            from scenes.mode_select import ModeSelectScene
            self.manager.transition_to(ModeSelectScene)
        elif self.options[self.selected] == "ULTIMATE CLUB":
            from systems.network import NetworkManager
            net = NetworkManager()
            if net.is_remote_server:
                from .event_teaser import EventTeaserScene
                self.manager.transition_to(EventTeaserScene)
            else:
                self.toast_message = "[!] ULTIMATE CLUB requiere conexión al servidor central"
                self.toast_timer = 3.0
        elif self.options[self.selected] == "ONLINE":
            from systems.network import NetworkManager
            net = NetworkManager()
            if net.is_remote_server:
                from scenes.online_hub import OnlineHubScene
                self.manager.transition_to(OnlineHubScene)
            else:
                self.toast_message = "[!] Modo ONLINE requiere conexión al servidor central"
                self.toast_timer = 3.0
        elif "SESIÓN" in self.options[self.selected] or "CUENTA" in self.options[self.selected]:
            from scenes.login import LoginScene
            self.manager.transition_to(LoginScene)
        elif self.options[self.selected] == "SALIR":
            pygame.event.post(pygame.event.Event(pygame.QUIT))

    def update(self, dt):
        self.time += dt
        for p in self.particles:
            p.update(dt)

    def draw(self, surface):
        # Fondo degradado oscuro
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(15 + ratio * 10)
            g = int(15 + ratio * 5)
            b = int(30 + ratio * 20)
            pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

        # Partículas
        for p in self.particles:
            p.draw(surface)

        # Dibujar cancha difuminada al fondo (mini pitch)
        self._draw_bg_pitch(surface)

        # ── TÍTULO ──
        # Efecto de brillo pulsante
        pulse = (math.sin(self.time * 2.5) + 1) / 2  # 0 a 1
        glow_color = (
            int(UI_ACCENT[0] * 0.6 + pulse * 100),
            int(UI_ACCENT[1] * 0.6 + pulse * 60),
            int(UI_ACCENT[2] * 0.3 + pulse * 40),
        )

        title_text = "ULTIMA  FC"
        # Sombra
        shadow = self.font_title.render(title_text, True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(WIDTH // 2 + 3, 180 + 3))
        surface.blit(shadow, shadow_rect)
        # Texto principal
        title_surf = self.font_title.render(title_text, True, glow_color)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, 180))
        surface.blit(title_surf, title_rect)

        # Línea decorativa bajo el título
        line_w = 300 + int(pulse * 40)
        line_y = 220
        pygame.draw.line(surface, UI_ACCENT, (WIDTH // 2 - line_w // 2, line_y),
                         (WIDTH // 2 + line_w // 2, line_y), 2)

        # Subtítulo
        sub_text = "---  ULTIMATE  FOOTBALL  EXPERIENCE  ---"
        sub_surf = self.font_subtitle.render(sub_text, True, UI_TEXT_DIM)
        sub_rect = sub_surf.get_rect(center=(WIDTH // 2, 248))
        surface.blit(sub_surf, sub_rect)

        # ── OPCIONES ──
        start_y = 340
        for i, option in enumerate(self.options):
            y = start_y + i * 80
            is_selected = i == self.selected

            if is_selected:
                # Fondo de opción seleccionada
                box_w = 320
                box_h = 56
                box_rect = pygame.Rect(WIDTH // 2 - box_w // 2, y - box_h // 2, box_w, box_h)

                # Borde animado
                border_surf = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
                pygame.draw.rect(border_surf, (*UI_ACCENT, 40), (0, 0, box_w, box_h), border_radius=10)
                pygame.draw.rect(border_surf, UI_ACCENT, (0, 0, box_w, box_h), 2, border_radius=10)
                surface.blit(border_surf, box_rect.topleft)

                # Indicadores
                arrow_x_offset = int(math.sin(self.time * 5) * 6)
                arrow_surf = self.font_option.render("▸", True, UI_ACCENT)
                surface.blit(arrow_surf, (WIDTH // 2 - box_w // 2 + 10 + arrow_x_offset, y - 18))

                color = UI_ACCENT
            else:
                color = UI_TEXT_DIM

            opt_surf = self.font_option.render(option, True, color)
            opt_rect = opt_surf.get_rect(center=(WIDTH // 2, y))
            surface.blit(opt_surf, opt_rect)

        # ── HINT ──
        hint_alpha = int(128 + 60 * math.sin(self.time * 3))
        hint_text = "↑↓ Navegar   ·   ENTER Seleccionar"
        hint_surf = self.font_hint.render(hint_text, True, (*UI_TEXT_DIM[:3],))
        hint_surf.set_alpha(hint_alpha)
        hint_rect = hint_surf.get_rect(center=(WIDTH // 2, HEIGHT - 40))
        surface.blit(hint_surf, hint_rect)

        # ── SERVER STATUS ──
        from systems.network import NetworkManager
        net = NetworkManager()
        status_color = (0, 255, 120) if net.connected else (255, 60, 60)
        status_text = "SERVER: ONLINE" if net.connected else "SERVER: OFFLINE"
        try:
            status_surf = self.font_hint.render(status_text, True, status_color)
            surface.blit(status_surf, (WIDTH - status_surf.get_width() - 20, 20))
            if not net.connected:
                reconnect_surf = self.font_hint.render("(Iniciando...)", True, (150, 150, 150))
                surface.blit(reconnect_surf, (WIDTH - reconnect_surf.get_width() - 20, 40))
        except: pass

    def _draw_bg_pitch(self, surface):
        """Dibuja una cancha muy tenue al fondo del menú."""
        alpha_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pitch_color = (34, 139, 34, 15)  # Muy transparente
        line_color = (255, 255, 255, 10)

        # Rectángulo de cancha
        rect = pygame.Rect(140, 280, WIDTH - 280, HEIGHT - 320)
        pygame.draw.rect(alpha_surf, pitch_color, rect)
        pygame.draw.rect(alpha_surf, line_color, rect, 2)
        # Línea central
        mid_x = WIDTH // 2
        pygame.draw.line(alpha_surf, line_color, (mid_x, rect.top), (mid_x, rect.bottom), 1)
        # Círculo central
        pygame.draw.circle(alpha_surf, line_color, (mid_x, rect.centery), 60, 1)

        surface.blit(alpha_surf, (0, 0))
