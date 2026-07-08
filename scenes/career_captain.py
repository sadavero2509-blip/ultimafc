import pygame
from settings import *
from data.career_manager import career_manager

class CareerCaptainScene:
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        self.sel_idx = 0
        
        is_cap = career_manager.career_stats.get("is_captain")
        is_nt_cap = career_manager.career_stats.get("is_nt_captain")
        
        self.options = [
            {"id": "talk", "name": "CHARLA MOTIVACIONAL", "desc": "Sube el ánimo del equipo para el próximo partido.", "icon": "🗣️"},
            {"id": "formation", "name": "SUGERIR TÁCTICA", "desc": "Pide al mánager un cambio de formación.", "icon": "📋"}
        ]
        
        if is_cap:
            self.options.append({"id": "transfer", "name": "SUGERIR FICHAJE", "desc": "Recomienda un jugador a la directiva.", "icon": "🤝"})
            
        self.msg = ""
        self.msg_timer = 0
        
        try:
            self.font_title = pygame.font.SysFont("Impact", 36)
            self.font_text = pygame.font.SysFont("Arial", 20, bold=True)
            self.font_sub = pygame.font.SysFont("Arial", 14)
            self.font_hint = pygame.font.SysFont("Arial", 12)
        except:
            self.font_title = pygame.font.Font(None, 36)
            self.font_text = pygame.font.Font(None, 20)
            self.font_sub = pygame.font.Font(None, 14)
            self.font_hint = pygame.font.Font(None, 12)

    def handle_events(self, events):
        if self.msg_timer > 0: return
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.sel_idx = (self.sel_idx - 1) % len(self.options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.sel_idx = (self.sel_idx + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    self._execute_action()
                elif event.key == pygame.K_ESCAPE:
                    from scenes.career_hub import CareerHubScene
                    self.manager.set_scene(CareerHubScene)

    def _execute_action(self):
        opt = self.options[self.sel_idx]["id"]
        
        if opt == "talk":
            # Motivational Talk logic
            if career_manager.career_stats.get("talk_used_today"):
                self.msg = "Ya has hablado con el equipo hoy."
            else:
                career_manager.career_stats["talk_used_today"] = True
                # Boost team morale/stats for next match (simplified)
                career_manager.add_news("CLUB", "LIDERAZGO", "El capitán ha dado una charla inspiradora. El equipo está motivado.")
                self.msg = "¡Charla realizada! El equipo saldrá con más energía."
            self.msg_timer = 2.5
            
        elif opt == "formation":
            # Suggest formation
            self.msg = "Petición enviada. El mánager la estudiará para el próximo partido."
            career_manager.add_email("board", "Sugerencia Táctica", "He recibido tu sugerencia. Como capitán, tu opinión cuenta; lo tendremos en cuenta.")
            self.msg_timer = 3.0
            
        elif opt == "transfer":
            # Suggest transfer
            self.msg = "Has sugerido un refuerzo a la directiva."
            career_manager.add_email("board", "Mercado de Fichajes", "Gracias por la recomendación. Buscaremos perfiles similares en el mercado.")
            self.msg_timer = 3.0

    def update(self, dt):
        if self.msg_timer > 0:
            self.msg_timer -= dt
            if self.msg_timer <= 0:
                from scenes.career_hub import CareerHubScene
                self.manager.set_scene(CareerHubScene)

    def draw(self, surface):
        surface.fill((10, 15, 25))
        
        # Header
        pygame.draw.rect(surface, (20, 30, 50), (0, 0, WIDTH, 80))
        title = self.font_title.render("DESPACHO DEL CAPITÁN", True, UI_ACCENT)
        surface.blit(title, (50, 20))
        
        # Options List
        for i, opt in enumerate(self.options):
            is_sel = (i == self.sel_idx)
            rect = pygame.Rect(100, 150 + i*110, WIDTH-200, 90)
            
            bg = (30, 45, 70) if is_sel else (20, 25, 40)
            pygame.draw.rect(surface, bg, rect, border_radius=10)
            if is_sel:
                pygame.draw.rect(surface, WHITE, rect, 2, border_radius=10)
            
            # Icon
            ts = self.font_text.render(opt["icon"], True, WHITE)
            surface.blit(ts, (rect.left + 30, rect.centery - 15))
            
            # Label
            ls = self.font_text.render(opt["name"], True, WHITE)
            surface.blit(ls, (rect.left + 80, rect.top + 20))
            
            # Desc
            ds = self.font_sub.render(opt["desc"], True, UI_TEXT_DIM)
            surface.blit(ds, (rect.left + 80, rect.top + 50))

        # Status Msg
        if self.msg_timer > 0:
            ms = self.font_text.render(self.msg, True, (100, 255, 150))
            surface.blit(ms, (WIDTH//2 - ms.get_width()//2, HEIGHT//2))

        # Hint
        hint = self.font_hint.render("↑↓ Seleccionar  ·  ENTER Confirmar  ·  ESC Volver", True, UI_TEXT_DIM)
        surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 30))
