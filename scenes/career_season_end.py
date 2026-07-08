import pygame
from settings import *
from data.career_manager import career_manager

class CareerSeasonEndScene:
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        self.top_players = self.context.get("top_players") or []
        
        try:
            self.font_title = pygame.font.SysFont("Impact", 50)
            self.font_text = pygame.font.SysFont("Arial", 22)
            self.font_bold = pygame.font.SysFont("Arial", 24, bold=True)
            self.font_btn = pygame.font.SysFont("Arial", 20, bold=True)
        except:
            self.font_title = pygame.font.Font(None, 50)
            self.font_text = pygame.font.Font(None, 22)
            self.font_bold = pygame.font.Font(None, 24)
            self.font_btn = pygame.font.Font(None, 20)
            
    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    from scenes.career_hub import CareerHubScene
                    self.manager.set_scene(CareerHubScene)
                    
    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((15, 20, 30))
        
        t = self.font_title.render(f"RESUMEN DE TEMPORADA {career_manager.year - 1}", True, (255, 215, 0))
        surface.blit(t, (WIDTH//2 - t.get_width()//2, 40))
        
        sub = self.font_text.render("El fútbol mundial toma un breve descanso. Así quedó el Olimpo de Goleadores:", True, WHITE)
        surface.blit(sub, (WIDTH//2 - sub.get_width()//2, 100))
        
        y = 180
        for i, (name, gls, lg) in enumerate(self.top_players):
            rect = pygame.Rect(WIDTH//2 - 250, y, 500, 60)
            c = (40, 45, 60) if i > 0 else (200, 180, 50)
            pygame.draw.rect(surface, c, rect, border_radius=8)
            
            ns = self.font_bold.render(f"#{i+1} {name}", True, WHITE if i > 0 else BLACK)
            gs = self.font_bold.render(f"{gls} Goles", True, (100, 255, 100) if i > 0 else BLACK)
            lgs = self.font_text.render(lg, True, UI_TEXT_DIM if i > 0 else (50, 50, 50))
            
            surface.blit(ns, (rect.left + 20, rect.centery - ns.get_height()//2))
            surface.blit(gs, (rect.right - 120, rect.centery - gs.get_height()//2))
            surface.blit(lgs, (rect.centerx, rect.centery - lgs.get_height()//2))
            
            y += 75
            
        pygame.draw.rect(surface, UI_CARD_BG, (WIDTH//2 - 300, 560, 600, 60), border_radius=8)
        ms = self.font_text.render("Todos los equipos han recibido presupuesto nuevo y modificado plantillas.", True, UI_TEXT_DIM)
        surface.blit(ms, (WIDTH//2 - ms.get_width()//2, 570))
        
        h = self.font_btn.render("Presiona ENTER para comenzar el nuevo año", True, WHITE)
        surface.blit(h, (WIDTH//2 - h.get_width()//2, 650))
