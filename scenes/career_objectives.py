import pygame
from settings import *
from data.career_manager import career_manager

class CareerObjectivesScene:
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        self.scroll_y = 0
        
        try:
            self.font_title = pygame.font.SysFont("Impact", 36)
            self.font_text = pygame.font.SysFont("Arial", 18, bold=True)
            self.font_sub = pygame.font.SysFont("Arial", 14)
            self.font_hint = pygame.font.SysFont("Arial", 12)
        except:
            self.font_title = pygame.font.Font(None, 36)
            self.font_text = pygame.font.Font(None, 18)
            self.font_sub = pygame.font.Font(None, 14)
            self.font_hint = pygame.font.Font(None, 12)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.scroll_y = max(0, self.scroll_y - 30)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.scroll_y += 30
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                    from scenes.career_hub import CareerHubScene
                    self.manager.set_scene(CareerHubScene)

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((10, 15, 30))
        
        # Header
        pygame.draw.rect(surface, (20, 30, 50), (0, 0, WIDTH, 80))
        title = self.font_title.render("OBJETIVOS DE LA TEMPORADA", True, UI_ACCENT)
        surface.blit(title, (50, 20))
        
        # Draw Objectives List
        objs = career_manager.objectives
        if not objs:
            msg = self.font_text.render("No hay objetivos asignados en este momento.", True, UI_TEXT_DIM)
            surface.blit(msg, (WIDTH//2 - msg.get_width()//2, HEIGHT//2))
        else:
            start_y = 100 - self.scroll_y
            for i, obj in enumerate(objs):
                if start_y + 80 < 80: # Above header
                    start_y += 100
                    continue
                if start_y > HEIGHT - 50: break # Below footer
                
                rect = pygame.Rect(50, start_y, WIDTH - 100, 80)
                pygame.draw.rect(surface, (25, 35, 55), rect, border_radius=10)
                
                # Info
                name = self.font_text.render(obj["desc"].upper(), True, WHITE)
                surface.blit(name, (rect.left + 20, rect.top + 15))
                
                # Progress Bar
                bar_w = rect.width - 300
                bar_h = 12
                bar_x = rect.left + 20
                bar_y = rect.top + 50
                pygame.draw.rect(surface, (15, 20, 35), (bar_x, bar_y, bar_w, bar_h), border_radius=6)
                
                # Calculate percent
                target = obj["target"]
                current = obj["current"]
                
                # Handle team pos (lower is better)
                if obj["type"] == "team_pos":
                    percent = 1.0 if current <= target else max(0, 1.0 - (current - target) / 10)
                    progress_text = f"Puesto actual: {current} (Meta: Top {target})"
                elif obj["type"] == "avg_rating":
                    percent = min(1.0, current / target)
                    progress_text = f"Promedio: {current:.2f} / {target:.2f}"
                else:
                    percent = min(1.0, current / target)
                    progress_text = f"{int(current)} / {int(target)}"
                
                fill_w = int(bar_w * percent)
                color = (100, 255, 100) if percent >= 1.0 else UI_ACCENT
                pygame.draw.rect(surface, color, (bar_x, bar_y, fill_w, bar_h), border_radius=6)
                
                # Value text
                ps = self.font_sub.render(progress_text, True, UI_TEXT_DIM)
                surface.blit(ps, (bar_x + bar_w + 20, bar_y - 2))
                
                # Status Icon
                if percent >= 1.0:
                    status = self.font_text.render("✓ COMPLETADO", True, (100, 255, 100))
                    surface.blit(status, (rect.right - 150, rect.centery - 10))
                
                start_y += 100

        hint = self.font_hint.render("↑↓ Desplazar  ·  ESC / ENTER Volver", True, UI_TEXT_DIM)
        surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 30))
