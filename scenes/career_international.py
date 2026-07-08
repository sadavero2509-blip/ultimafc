import pygame
from settings import *
from data.career_manager import career_manager

class CareerInternationalScene:
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        
        self.type = self.context.get("type", "CALL") # CALL (player) or OFFER (manager)
        self.country_code = self.context.get("country_code", "AR")
        self.nt_data = self.context.get("nt_data", {})
        
        try:
            self.font_title = pygame.font.SysFont("Impact", 42)
            self.font_btn = pygame.font.SysFont("Arial", 28, bold=True)
            self.font_text = pygame.font.SysFont("Arial", 18)
        except:
            self.font_title = pygame.font.Font(None, 42)
            self.font_btn = pygame.font.Font(None, 28)
            self.font_text = pygame.font.Font(None, 18)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    # Accept
                    if self.type == "OFFER":
                        career_manager.managing_nt = self.country_code
                        # Schedule matches
                        career_manager.schedule_international_break()
                    else:
                        career_manager.is_called_up = True
                        # Schedule matches
                        career_manager.schedule_international_break()
                    
                    from scenes.career_hub import CareerHubScene
                    self.manager.set_scene(CareerHubScene)
                elif event.key == pygame.K_ESCAPE:
                    # Decline
                    from scenes.career_hub import CareerHubScene
                    self.manager.set_scene(CareerHubScene)

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((10, 20, 40))
        
        # Gradient background
        for y in range(HEIGHT):
            r, g, b = 10 + y//30, 20 + y//40, 40 + y//20
            pygame.draw.line(surface, (min(255, r), min(255, g), min(255, b)), (0, y), (WIDTH, y))
            
        title_text = "¡CONVOCATORIA NACIONAL!" if self.type == "CALL" else "¡OFERTA INTERNACIONAL!"
        title = self.font_title.render(title_text, True, (255, 215, 0))
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 80))
        
        # Country Badge / Info
        from data.teams import draw_badge
        draw_badge(surface, self.nt_data, WIDTH//2, 220, size=80)
        
        nt_name = self.nt_data.get("name", "Selección Nacional")
        ns = self.font_btn.render(nt_name, True, WHITE)
        surface.blit(ns, (WIDTH//2 - ns.get_width()//2, 320))
        
        if self.type == "CALL":
            msg = f"El seleccionador de {nt_name} ha seguido de cerca tu progreso."
            msg2 = "Te han convocado para los próximos partidos internacionales."
        else:
            msg = f"Tras tus excelentes resultados, la federación de {nt_name}"
            msg2 = "te ofrece el cargo de seleccionador nacional."
            
        ms1 = self.font_text.render(msg, True, UI_TEXT)
        surface.blit(ms1, (WIDTH//2 - ms1.get_width()//2, 380))
        ms2 = self.font_text.render(msg2, True, UI_TEXT)
        surface.blit(ms2, (WIDTH//2 - ms2.get_width()//2, 410))
        
        # Prompt
        p_txt = "PRESIONA [ENTER] PARA ACEPTAR  |  [ESC] PARA RECHAZAR"
        ps = self.font_btn.render(p_txt, True, (100, 255, 100))
        surface.blit(ps, (WIDTH//2 - ps.get_width()//2, 550))
