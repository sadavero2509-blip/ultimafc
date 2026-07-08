import pygame
from settings import *
from data.career_manager import career_manager

class CareerNewsScene:
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        self.time = 0
        
        self.tabs = [
            {"id": "global", "name": "Global", "color": (100, 150, 255)},
            {"id": "local", "name": "Local", "color": (100, 255, 100)},
            {"id": "market", "name": "Fichajes", "color": (255, 200, 50)},
            {"id": "intl", "name": "Internacional", "color": (255, 100, 100)}
        ]
        self.selected_tab = 0
        self.selected_news_idx = 0
        self.viewing_detail = False
        
        try:
            self.font_title = pygame.font.SysFont("Impact", 36)
            self.font_tab = pygame.font.SysFont("Arial", 20, bold=True)
            self.font_news_title = pygame.font.SysFont("Arial", 18, bold=True)
            self.font_news_desc = pygame.font.SysFont("Arial", 16)
            self.font_date = pygame.font.SysFont("Consolas", 14)
            self.font_hint = pygame.font.SysFont("Arial", 14)
        except:
            self.font_title = pygame.font.Font(None, 36)
            self.font_tab = pygame.font.Font(None, 20)
            self.font_news_title = pygame.font.Font(None, 18)
            self.font_news_desc = pygame.font.Font(None, 16)
            self.font_date = pygame.font.Font(None, 14)
            self.font_hint = pygame.font.Font(None, 14)

    def handle_events(self, events):
        filtered = self._get_filtered_news()
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.viewing_detail:
                    if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                        self.viewing_detail = False
                else:
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        self.selected_tab = (self.selected_tab - 1) % len(self.tabs)
                        self.selected_news_idx = 0
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.selected_tab = (self.selected_tab + 1) % len(self.tabs)
                        self.selected_news_idx = 0
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        if filtered: self.selected_news_idx = (self.selected_news_idx - 1) % len(filtered)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        if filtered: self.selected_news_idx = (self.selected_news_idx + 1) % len(filtered)
                    elif event.key == pygame.K_RETURN:
                        if filtered: self.viewing_detail = True
                    elif event.key == pygame.K_ESCAPE:
                        from scenes.career_hub import CareerHubScene
                        self.manager.set_scene(CareerHubScene)

    def update(self, dt):
        self.time += dt

    def _get_filtered_news(self):
        tab_id = self.tabs[self.selected_tab]["id"]
        
        # Mapping of all used categories to the 4 UI tabs
        category_map = {
            "local": ["local", "liga", "club", "cantera", "objetivos", "historia", "reportaje", "estadio", "deportes", "previa"],
            "market": ["market", "mercado"],
            "intl": ["intl", "seleccion", "internacional"],
            "global": ["global", "gloria", "especial", "narrativa", "historia", "reportaje"] # Some history can be global
        }
        
        def matches(news_cat, tab_cats):
            if not news_cat: return False
            return news_cat.lower() in tab_cats
            
        return [n for n in career_manager.news if matches(n["category"], category_map.get(tab_id, []))]

    def draw(self, surface):
        surface.fill((10, 15, 25))
        # Header
        title = self.font_title.render("DIARIO DEPORTIVO", True, UI_ACCENT)
        surface.blit(title, (50, 20))
        
        # Tabs
        tw = 180
        tx = 50
        for i, tab in enumerate(self.tabs):
            is_sel = (self.selected_tab == i)
            rect = pygame.Rect(tx, 80, tw, 40)
            bg = (40, 45, 60) if is_sel else (20, 25, 35)
            pygame.draw.rect(surface, bg, rect, border_radius=8)
            ts = self.font_tab.render(tab["name"], True, WHITE if is_sel else UI_TEXT_DIM)
            surface.blit(ts, (rect.centerx - ts.get_width()//2, rect.centery - ts.get_height()//2))
            tx += tw + 10
            
        # News list area
        list_rect = pygame.Rect(50, 140, WIDTH//2 - 25, HEIGHT - 200)
        pygame.draw.rect(surface, (15, 18, 28), list_rect, border_radius=12)
        
        filtered = self._get_filtered_news()
        ny = 150
        for i, item in enumerate(filtered):
            # Only draw visible in list (simple paging logic if needed, but let's do top 10)
            if i >= self.selected_news_idx - 4 and i < self.selected_news_idx + 5:
                rect = pygame.Rect(60, ny, list_rect.width - 20, 40)
                is_sel = (self.selected_news_idx == i)
                if is_sel:
                    pygame.draw.rect(surface, (45, 50, 70), rect, border_radius=5)
                
                # Truncate title
                txt = item["title"]
                if len(txt) > 35: txt = txt[:32] + "..."
                ts = self.font_news_title.render(txt, True, WHITE if is_sel else UI_TEXT_DIM)
                surface.blit(ts, (rect.left + 10, rect.centery - ts.get_height()//2))
                ny += 45
        
        # Detail Area
        detail_rect = pygame.Rect(WIDTH//2 + 25, 140, WIDTH//2 - 75, HEIGHT - 200)
        pygame.draw.rect(surface, (20, 25, 35), detail_rect, border_radius=12)
        pygame.draw.rect(surface, (50, 55, 70), detail_rect, 1, border_radius=12)
        
        if filtered and self.selected_news_idx < len(filtered):
            item = filtered[self.selected_news_idx]
            # Content
            ds = self.font_date.render(item["date"] + " | " + item["category"].upper(), True, UI_ACCENT)
            surface.blit(ds, (detail_rect.left + 20, detail_rect.top + 20))
            
            ts = self.font_news_title.render(item["title"], True, WHITE)
            # Wrap title if long
            surface.blit(ts, (detail_rect.left + 20, detail_rect.top + 50))
            
            # Desc (multiline wrap)
            words = item["desc"].split(' ')
            line = ""
            dy = detail_rect.top + 90
            for word in words:
                test_line = line + word + " "
                if self.font_news_desc.size(test_line)[0] < detail_rect.width - 40:
                    line = test_line
                else:
                    surface.blit(self.font_news_desc.render(line, True, UI_TEXT), (detail_rect.left + 20, dy))
                    line = word + " "
                    dy += 25
            surface.blit(self.font_news_desc.render(line, True, UI_TEXT), (detail_rect.left + 20, dy))
            
        else:
            empty = self.font_tab.render("No hay noticias.", True, UI_TEXT_DIM)
            surface.blit(empty, (detail_rect.centerx - empty.get_width()//2, detail_rect.centery))
            
        # Hint
        hint = self.font_hint.render("↑↓ Seleccionar  ·  ENTER Ver Detalle  ·  ESC Volver", True, UI_TEXT_DIM)
        surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 30))
