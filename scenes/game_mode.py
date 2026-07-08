import pygame
import math
from settings import *
from scene_manager import BaseScene


class GameModeScene(BaseScene):
    def __init__(self, manager):
        super().__init__(manager)
        self.time = 0
        self.selected = 0
        self.modes = [
            {
                "name": "PARTIDO RÁPIDO",
                "icon": "[FAST]",
                "desc": "Un partido completo con tiempo y marcador.",
                "color": (0, 200, 150),
                "available": True,
            },
            {
                "name": "TORNEO",
                "icon": "[COPA]",
                "desc": "Eliminatorias hacia la gloria. (Próximamente)",
                "color": (255, 215, 0),
                "available": False,
            },
            {
                "name": "JUEGO LIBRE",
                "icon": "[LIBRE]",
                "desc": "Practica sin límites de tiempo. Sin marcador.",
                "color": (100, 150, 255),
                "available": True,
            },
        ]

        try:
            self.font_title = pygame.font.SysFont("Arial", 40, bold=True)
            self.font_mode = pygame.font.SysFont("Arial", 30, bold=True)
            self.font_desc = pygame.font.SysFont("Arial", 18)
            self.font_hint = pygame.font.SysFont("Arial", 16)
            self.font_icon = pygame.font.SysFont("Segoe UI Emoji", 42)
        except:
            self.font_title = pygame.font.Font(None, 40)
            self.font_mode = pygame.font.Font(None, 30)
            self.font_desc = pygame.font.Font(None, 18)
            self.font_hint = pygame.font.Font(None, 16)
            self.font_icon = pygame.font.Font(None, 42)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.selected = (self.selected - 1) % len(self.modes)
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.selected = (self.selected + 1) % len(self.modes)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    self._select_mode()
                elif event.key == pygame.K_ESCAPE:
                    from scenes.main_menu import MainMenuScene
                    self.manager.transition_to(MainMenuScene)

    def _select_mode(self):
        mode = self.modes[self.selected]
        if not mode["available"]:
            return  # Modo no disponible

        game_mode = "quick" if self.selected == 0 else "free"
        self.manager.shared_data["game_mode"] = game_mode

        from scenes.team_select import TeamSelectScene
        self.manager.transition_to(TeamSelectScene)

    def update(self, dt):
        self.time += dt

    def draw(self, surface):
        # Fondo
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(15 + ratio * 8)
            g = int(15 + ratio * 5)
            b = int(30 + ratio * 15)
            pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

        # Título
        title_surf = self.font_title.render("SELECCIONA MODO DE JUEGO", True, UI_TEXT)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, 80))
        surface.blit(title_surf, title_rect)

        # Línea decorativa
        pygame.draw.line(surface, UI_ACCENT, (WIDTH // 2 - 200, 115),
                         (WIDTH // 2 + 200, 115), 2)

        # Tarjetas de modo
        card_w = 320
        card_h = 380
        total_w = card_w * len(self.modes) + 40 * (len(self.modes) - 1)
        start_x = (WIDTH - total_w) // 2

        for i, mode in enumerate(self.modes):
            x = start_x + i * (card_w + 40)
            y = 160
            is_selected = i == self.selected
            is_available = mode["available"]

            self._draw_card(surface, mode, x, y, card_w, card_h, is_selected, is_available)

        # Hint
        hint_text = "← → Navegar   ·   ENTER Seleccionar   ·   ESC Volver"
        hint_surf = self.font_hint.render(hint_text, True, UI_TEXT_DIM)
        hint_rect = hint_surf.get_rect(center=(WIDTH // 2, HEIGHT - 35))
        surface.blit(hint_surf, hint_rect)

    def _draw_card(self, surface, mode, x, y, w, h, selected, available):
        color = mode["color"]

        # Fondo de tarjeta
        card_rect = pygame.Rect(x, y, w, h)
        bg_color = UI_CARD_HOVER if selected else UI_CARD_BG
        if not available:
            bg_color = (30, 30, 35)

        pygame.draw.rect(surface, bg_color, card_rect, border_radius=16)

        # Borde
        if selected:
            # Borde animado brillante
            pulse = (math.sin(self.time * 4) + 1) / 2
            border_color = (
                int(color[0] * (0.6 + 0.4 * pulse)),
                int(color[1] * (0.6 + 0.4 * pulse)),
                int(color[2] * (0.6 + 0.4 * pulse)),
            )
            pygame.draw.rect(surface, border_color, card_rect, 3, border_radius=16)
            # Glow sutil
            glow_rect = card_rect.inflate(6, 6)
            glow_surf = pygame.Surface((glow_rect.w, glow_rect.h), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*color, 20), (0, 0, glow_rect.w, glow_rect.h), border_radius=18)
            surface.blit(glow_surf, glow_rect.topleft)
        else:
            pygame.draw.rect(surface, (60, 60, 80), card_rect, 1, border_radius=16)

        # Ícono (usamos texto como ícono ya que no hay sprites)
        cx = x + w // 2
        # Círculo decorativo para el ícono
        icon_y = y + 80
        circle_r = 50
        icon_circle_color = (*color, 30) if available else (60, 60, 60, 30)
        icon_surf = pygame.Surface((circle_r * 2, circle_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(icon_surf, icon_circle_color, (circle_r, circle_r), circle_r)
        surface.blit(icon_surf, (cx - circle_r, icon_y - circle_r))
        pygame.draw.circle(surface, color if available else GRAY, (cx, icon_y), circle_r, 2)

        # Texto del ícono
        try:
            sz = 18 if len(mode["icon"]) > 1 else 42
            font = pygame.font.SysFont("Arial", sz, bold=True) if len(mode["icon"]) > 1 else self.font_icon
            icon_text = font.render(mode["icon"], True, color if available else GRAY)
            icon_text_rect = icon_text.get_rect(center=(cx, icon_y))
            surface.blit(icon_text, icon_text_rect)
        except:
            pass

        # Nombre del modo
        name_color = WHITE if available else GRAY
        name_surf = self.font_mode.render(mode["name"], True, name_color)
        name_rect = name_surf.get_rect(center=(cx, y + 170))
        surface.blit(name_surf, name_rect)

        # Línea separadora
        pygame.draw.line(surface, (*color, 60) if available else (60, 60, 60),
                         (x + 30, y + 200), (x + w - 30, y + 200), 1)

        # Descripción (multi-línea simple)
        desc_text = mode["desc"]
        words = desc_text.split()
        lines = []
        current_line = ""
        for word in words:
            test = current_line + " " + word if current_line else word
            if self.font_desc.size(test)[0] < w - 40:
                current_line = test
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)

        desc_color = UI_TEXT_DIM if available else (80, 80, 80)
        for j, line in enumerate(lines):
            line_surf = self.font_desc.render(line, True, desc_color)
            line_rect = line_surf.get_rect(center=(cx, y + 230 + j * 24))
            surface.blit(line_surf, line_rect)

        # Tag de no disponible
        if not available:
            tag_surf = self.font_desc.render("PRÓXIMAMENTE", True, YELLOW)
            tag_rect = tag_surf.get_rect(center=(cx, y + h - 40))
            surface.blit(tag_surf, tag_rect)
