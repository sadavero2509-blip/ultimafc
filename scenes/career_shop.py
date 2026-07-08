import pygame
from settings import *
from data.career_manager import career_manager, ITEM_SHOP

class CareerShopScene:
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        self.selected_idx = 0
        self.msg = ""
        self.msg_timer = 0
        
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
                    self.selected_idx = max(0, self.selected_idx - 1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected_idx = min(len(ITEM_SHOP) - 1, self.selected_idx + 1)
                elif event.key == pygame.K_RETURN:
                    self._buy_selected()
                elif event.key == pygame.K_SPACE:
                    self._equip_selected()
                elif event.key == pygame.K_ESCAPE:
                    from scenes.career_hub import CareerHubScene
                    self.manager.set_scene(CareerHubScene)

    def _buy_selected(self):
        item = ITEM_SHOP[self.selected_idx]
        success, msg = career_manager.buy_item(item["id"])
        self.msg = msg
        self.msg_timer = 2.0

    def _equip_selected(self):
        item = ITEM_SHOP[self.selected_idx]
        if item["id"] in career_manager.inventory:
            if career_manager.equip_item(item["id"]):
                self.msg = f"Cambio aplicado."
            else:
                self.msg = "Máximo 2 items equipados."
            self.msg_timer = 1.5

    def update(self, dt):
        if self.msg_timer > 0: self.msg_timer -= dt

    def draw(self, surface):
        surface.fill((10, 15, 25))
        
        # Header
        pygame.draw.rect(surface, (20, 30, 50), (0, 0, WIDTH, 80))
        title = self.font_title.render("TIENDA DE ARTÍCULOS", True, UI_ACCENT)
        surface.blit(title, (50, 20))
        
        # Balance
        money = career_manager.career_stats["money"]
        mb = self.font_text.render(f"CUENTA: ${money:.2f}M", True, (100, 255, 150))
        surface.blit(mb, (WIDTH - 250, 30))
        
        # Items List (With Auto-Scroll)
        scroll_shop = 0
        if self.selected_idx >= 4:
            scroll_shop = (self.selected_idx - 3) * 85
            
        start_y = 120 - scroll_shop
        for i, item in enumerate(ITEM_SHOP):
            is_sel = (self.selected_idx == i)
            rect = pygame.Rect(50, start_y, 450, 70)
            
            # Draw only if roughly visible
            if rect.bottom > 100 and rect.top < HEIGHT - 80:
                bg = (40, 50, 80) if is_sel else (25, 30, 45)
                pygame.draw.rect(surface, bg, rect, border_radius=10)
                if is_sel: pygame.draw.rect(surface, WHITE, rect, 2, border_radius=10)
                
                # Info
                name_c = WHITE
                owned = item["id"] in career_manager.inventory
                equipped = item["id"] in career_manager.equipped_items
                
                name_str = item["name"]
                if owned: name_str += " (Comprado)"
                if equipped: name_str += " [EQUIPADO]"
                
                ns = self.font_text.render(name_str, True, (255, 215, 0) if equipped else name_c)
                surface.blit(ns, (rect.left + 15, rect.top + 12))
                
                ds = self.font_sub.render(item["desc"], True, UI_TEXT_DIM)
                surface.blit(ds, (rect.left + 15, rect.top + 40))
                
                price_s = self.font_text.render(f"${item['price']}M", True, (100, 255, 100))
                surface.blit(price_s, (rect.right - 80, rect.top + 25))
            
            start_y += 85
            
        # Message
        if self.msg_timer > 0:
            ms = self.font_text.render(self.msg, True, (255, 255, 255))
            surface.blit(ms, (WIDTH//2 - ms.get_width()//2, HEIGHT - 80))
            
        # Footer
        hint = self.font_hint.render("↑↓ Seleccionar  ·  ENTER Comprar  ·  ESPACIO Equipar  ·  ESC Volver", True, UI_TEXT_DIM)
        surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 30))
        
        # Details Panel
        p_rect = pygame.Rect(550, 120, 200, 350)
        pygame.draw.rect(surface, (20, 25, 40), p_rect, border_radius=15)
        dt = self.font_text.render("MIS STATS", True, UI_ACCENT)
        surface.blit(dt, (p_rect.centerx - dt.get_width()//2, p_rect.top + 15))
        
        stats = career_manager.career_player["s"]
        sy = p_rect.top + 60
        for s_name, val in stats.items():
            if s_name == "gk": continue
            label = self.font_sub.render(f"{s_name.upper()}: {val}", True, WHITE)
            surface.blit(label, (p_rect.left + 20, sy))
            sy += 25
            
        ovr = self.font_title.render(str(career_manager.career_player["ovr"]), True, (100, 255, 150))
        surface.blit(ovr, (p_rect.centerx - ovr.get_width()//2, p_rect.bottom - 60))
        ol = self.font_hint.render("OVR", True, UI_TEXT_DIM)
        surface.blit(ol, (p_rect.centerx - ol.get_width()//2, p_rect.bottom - 25))
