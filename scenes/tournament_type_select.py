import pygame
import math
from settings import *

class TournamentTypeSelectScene:
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        self.time = 0
        self.selected = 0
        self.modes = [
            {
                "id": "champions",
                "name": "COPA CHAMPIONS",
                "icon": "[EU]",
                "desc": "El torneo europeo definitivo. 32 clubes compiten por el honor del viejo continente.",
                "color": (200, 200, 220), # Platinado
            },
            {
                "id": "libertadores",
                "name": "COPA LIBERTADORES",
                "icon": "[SA]",
                "desc": "La gloria eterna sudamericana. Pasión, garra y 32 equipos históricos.",
                "color": (50, 180, 100), # Verde
            }
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
                    self._proceed()
                elif event.key == pygame.K_ESCAPE:
                    from scenes.mode_select import ModeSelectScene
                    self.manager.set_scene(ModeSelectScene)

    def _proceed(self):
        opt = self.modes[self.selected]["id"]
        
        self.context["tournament_type"] = opt
        from scenes.league_select import LeagueSelectScene
        self.manager.set_scene(LeagueSelectScene, context=self.context)

    def update(self, dt):
        self.time += dt

    def draw(self, surface):
        surface.fill((10, 15, 25))
        
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(15 + ratio * 8)
            g = int(15 + ratio * 5)
            b = int(30 + ratio * 15)
            pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))

        title_surf = self.font_title.render("SELECCIONA TIPO DE TORNEO", True, UI_TEXT)
        title_rect = title_surf.get_rect(center=(WIDTH // 2, 80))
        surface.blit(title_surf, title_rect)

        pygame.draw.line(surface, UI_ACCENT, (WIDTH // 2 - 200, 115),
                         (WIDTH // 2 + 200, 115), 2)

        card_w = 320
        card_h = 380
        total_w = card_w * len(self.modes) + 60 * (len(self.modes) - 1)
        start_x = (WIDTH - total_w) // 2

        for i, mode in enumerate(self.modes):
            x = start_x + i * (card_w + 60)
            y = 160
            is_selected = i == self.selected
            self._draw_card(surface, mode, x, y, card_w, card_h, is_selected)

        hint_text = "← → Navegar   ·   ENTER Seleccionar   ·   ESC Volver"
        hint_surf = self.font_hint.render(hint_text, True, UI_TEXT_DIM)
        hint_rect = hint_surf.get_rect(center=(WIDTH // 2, HEIGHT - 35))
        surface.blit(hint_surf, hint_rect)

    def _draw_card(self, surface, mode, x, y, w, h, selected):
        color = mode["color"]
        card_rect = pygame.Rect(x, y, w, h)
        bg_color = UI_CARD_HOVER if selected else UI_CARD_BG

        pygame.draw.rect(surface, bg_color, card_rect, border_radius=16)

        if selected:
            pulse = (math.sin(self.time * 4) + 1) / 2
            border_color = (
                int(color[0] * (0.6 + 0.4 * pulse)),
                int(color[1] * (0.6 + 0.4 * pulse)),
                int(color[2] * (0.6 + 0.4 * pulse)),
            )
            pygame.draw.rect(surface, border_color, card_rect, 3, border_radius=16)
            glow_rect = card_rect.inflate(6, 6)
            glow_surf = pygame.Surface((glow_rect.w, glow_rect.h), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*color, 20), (0, 0, glow_rect.w, glow_rect.h), border_radius=18)
            surface.blit(glow_surf, glow_rect.topleft)
        else:
            pygame.draw.rect(surface, (60, 60, 80), card_rect, 1, border_radius=16)

        # Ícono
        cx = x + w // 2
        icon_y = y + 80
        circle_r = 50
        icon_circle_color = (*color, 30)
        icon_surf = pygame.Surface((circle_r * 2, circle_r * 2), pygame.SRCALPHA)
        pygame.draw.circle(icon_surf, icon_circle_color, (circle_r, circle_r), circle_r)
        surface.blit(icon_surf, (cx - circle_r, icon_y - circle_r))
        pygame.draw.circle(surface, color, (cx, icon_y), circle_r, 2)

        try:
            sz = 18 if len(mode["icon"]) > 1 else 42
            font = pygame.font.SysFont("Arial", sz, bold=True) if len(mode["icon"]) > 1 else self.font_icon
            icon_text = font.render(mode["icon"], True, color)
            icon_text_rect = icon_text.get_rect(center=(cx, icon_y))
            surface.blit(icon_text, icon_text_rect)
        except:
            pass

        name_surf = self.font_mode.render(mode["name"], True, WHITE)
        name_rect = name_surf.get_rect(center=(cx, y + 170))
        surface.blit(name_surf, name_rect)

        pygame.draw.line(surface, (*color, 60), (x + 30, y + 200), (x + w - 30, y + 200), 1)

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

        for j, line in enumerate(lines):
            line_surf = self.font_desc.render(line, True, UI_TEXT_DIM)
            line_rect = line_surf.get_rect(center=(cx, y + 230 + j * 24))
            surface.blit(line_surf, line_rect)
