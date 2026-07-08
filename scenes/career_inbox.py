import pygame
from settings import *
from data.career_manager import career_manager

class CareerInboxScene:
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        self.selected_idx = 0
        self.time = 0
        
        try:
            self.font_title = pygame.font.SysFont("Impact", 36)
            self.font_list = pygame.font.SysFont("Arial", 18, bold=True)
            self.font_msg = pygame.font.SysFont("Arial", 16)
            self.font_hint = pygame.font.SysFont("Arial", 14)
            self.font_icon = pygame.font.SysFont("Segoe UI Emoji", 24)
        except:
            self.font_title = pygame.font.Font(None, 36)
            self.font_list = pygame.font.Font(None, 18)
            self.font_msg = pygame.font.Font(None, 16)
            self.font_hint = pygame.font.Font(None, 14)
            self.font_icon = pygame.font.Font(None, 24)

    def handle_events(self, events):
        inbox = career_manager.inbox
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    if inbox: self.selected_idx = (self.selected_idx - 1) % len(inbox)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    if inbox: self.selected_idx = (self.selected_idx + 1) % len(inbox)
                elif event.key == pygame.K_RETURN:
                    if inbox:
                        inbox[self.selected_idx]["read"] = True
                elif event.key == pygame.K_ESCAPE:
                    from scenes.career_hub import CareerHubScene
                    self.manager.set_scene(CareerHubScene)

    def update(self, dt):
        self.time += dt

    def draw(self, surface):
        surface.fill((10, 15, 25))
        # Gradient
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(10 + ratio * 15)
            g = int(12 + ratio * 8)
            b = int(25 + ratio * 20)
            pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))
            
        # Header
        title = self.font_title.render("BANDEJA DE ENTRADA", True, UI_ACCENT)
        surface.blit(title, (50, 20))
        
        inbox = career_manager.inbox
        
        # List Area (Left)
        list_rect = pygame.Rect(50, 80, WIDTH//2 - 50, HEIGHT - 150)
        pygame.draw.rect(surface, (20, 25, 40), list_rect, border_radius=12)
        pygame.draw.rect(surface, (50, 55, 75), list_rect, 1, border_radius=12)
        
        if not inbox:
            empty = self.font_list.render("No hay mensajes.", True, UI_TEXT_DIM)
            surface.blit(empty, (list_rect.centerx - empty.get_width()//2, list_rect.centery))
        else:
            ny = 90
            for i, mail in enumerate(inbox):
                # Scroll simulation
                if i >= self.selected_idx - 4 and i < self.selected_idx + 5:
                    rect = pygame.Rect(60, ny, list_rect.width - 20, 60)
                    is_sel = (self.selected_idx == i)
                    
                    if is_sel:
                        pygame.draw.rect(surface, (45, 55, 90), rect, border_radius=8)
                        pygame.draw.rect(surface, UI_ACCENT, rect, 1, border_radius=8)
                    
                    # Unread indicator
                    if not mail["read"]:
                        pygame.draw.circle(surface, UI_ACCENT, (rect.left + 15, rect.top + 15), 4)
                    
                    # Icon
                    icons = {"offer": "🤝", "info": "ℹ️", "alert": "⚠️", "contract": "📜"}
                    its = self.font_icon.render(icons.get(mail["type"], "✉️"), True, WHITE)
                    surface.blit(its, (rect.left + 25, rect.centery - its.get_height()//2))
                    
                    # Subject
                    sub = mail["subject"]
                    if len(sub) > 30: sub = sub[:27] + "..."
                    sts = self.font_list.render(sub, True, WHITE if not mail["read"] else UI_TEXT_DIM)
                    surface.blit(sts, (rect.left + 65, rect.top + 10))
                    
                    # Date
                    dts = self.font_hint.render(mail["date"], True, UI_TEXT_DIM)
                    surface.blit(dts, (rect.left + 65, rect.top + 35))
                    
                    ny += 65
                    
        # Detail Area (Right)
        detail_rect = pygame.Rect(WIDTH//2 + 25, 80, WIDTH//2 - 75, HEIGHT - 150)
        pygame.draw.rect(surface, (15, 20, 30), detail_rect, border_radius=12)
        pygame.draw.rect(surface, (60, 65, 85), detail_rect, 1, border_radius=12)
        
        if inbox and self.selected_idx < len(inbox):
            mail = inbox[self.selected_idx]
            # Label
            cat_surf = self.font_hint.render(mail["type"].upper() + " | " + mail["date"], True, UI_ACCENT)
            surface.blit(cat_surf, (detail_rect.left + 30, detail_rect.top + 30))
            
            # Subject
            sts = self.font_title.render(mail["subject"], True, WHITE)
            # Truncate title if too long for detail pane
            surface.blit(sts, (detail_rect.left + 30, detail_rect.top + 55))
            
            # Content
            words = mail["content"].split(' ')
            line = ""
            dy = detail_rect.top + 110
            for word in words:
                test_line = line + word + " "
                if self.font_msg.size(test_line)[0] < detail_rect.width - 60:
                    line = test_line
                else:
                    surface.blit(self.font_msg.render(line, True, UI_TEXT), (detail_rect.left + 30, dy))
                    line = word + " "
                    dy += 25
            surface.blit(self.font_msg.render(line, True, UI_TEXT), (detail_rect.left + 30, dy))
            
            # Data table
            if mail.get("data"):
                dy += 40
                pygame.draw.line(surface, (50, 55, 75), (detail_rect.left + 30, dy), (detail_rect.right - 30, dy))
                dy += 20
                for k, v in mail["data"].items():
                    ks = self.font_hint.render(str(k).upper(), True, UI_TEXT_DIM)
                    vs = self.font_msg.render(str(v), True, WHITE)
                    surface.blit(ks, (detail_rect.left + 30, dy))
                    surface.blit(vs, (detail_rect.left + 160, dy))
                    dy += 30
        
        # Hint
        hint = self.font_hint.render("↑↓/WS Navegar Mensajes  ·  ENTER Marcar como leído  ·  ESC Volver", True, UI_TEXT_DIM)
        surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 40))
