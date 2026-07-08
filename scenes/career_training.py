import pygame
from settings import *
from data.career_manager import career_manager

class CareerTrainingScene:
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        
        self.player = career_manager.career_player
        self.stats = self.player["s"]
        
        self.options = [
            {"id": "speed", "name": "VELOCIDAD"},
            {"id": "shot", "name": "TIRO"},
            {"id": "passing", "name": "PASE"},
            {"id": "dribbling", "name": "REGATE"},
            {"id": "defense", "name": "DEFENSA"},
            {"id": "physical", "name": "FÍSICO"},
        ]
        if self.player.get("pos") == "GK":
            self.options.append({"id": "gk", "name": "PORTERÍA"})
        self.sel_idx = 0
        self.msg = ""
        self.msg_timer = 0

        try:
            self.font_title = pygame.font.SysFont("Impact", 44)
            self.font_stat = pygame.font.SysFont("Arial", 26, bold=True)
            self.font_curr = pygame.font.SysFont("Consolas", 32, bold=True)
            self.font_text = pygame.font.SysFont("Arial", 18)
            self.font_hint = pygame.font.SysFont("Arial", 14)
        except:
            self.font_title = pygame.font.Font(None, 44)
            self.font_stat = pygame.font.Font(None, 26)
            self.font_curr = pygame.font.Font(None, 32)
            self.font_text = pygame.font.Font(None, 18)
            self.font_hint = pygame.font.Font(None, 14)

    def _get_cost(self, val):
        """Calcula el costo dinámico: a mayor nivel, mayor costo."""
        # Coste base reducido para permitir progresión inicial más fluida
        cost = 2 + max(0, (val - 62) // 3)
        return int(cost)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.sel_idx = (self.sel_idx - 1) % len(self.options)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.sel_idx = (self.sel_idx + 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    self._upgrade_stat()
                elif event.key == pygame.K_ESCAPE:
                    from scenes.career_hub import CareerHubScene
                    self.manager.set_scene(CareerHubScene)

    def _upgrade_stat(self):
        opt = self.options[self.sel_idx]
        stat_id = opt["id"]
        val = self.stats[stat_id]
        cost = self._get_cost(val)
        
        if career_manager.skill_points >= cost:
            if self.stats[stat_id] < 99:
                career_manager.skill_points -= cost
                self.stats[stat_id] += 1
                # Recalculate OVR
                from data.rosters import calculate_ovr
                self.player["ovr"] = calculate_ovr(self.player)
                self.msg = f"¡{opt['name']} mejorada!"
                self.msg_timer = 2.0
            else:
                self.msg = "Atributo al máximo (99)."
                self.msg_timer = 2.0
        else:
            self.msg = f"Necesitas {cost} puntos de habilidad."
            self.msg_timer = 2.0

    def update(self, dt):
        if self.msg_timer > 0:
            self.msg_timer -= dt

    def draw(self, surface):
        surface.fill((15, 20, 35))
        
        # Header
        title = self.font_title.render("ENTRENAMIENTO Y MEJORA", True, (255, 215, 0))
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 40))
        
        points = self.font_stat.render(f"Puntos Disponibles: {career_manager.skill_points}", True, WHITE)
        surface.blit(points, (WIDTH//2 - points.get_width()//2, 100))
        
        # Player Info
        ovr_lbl = self.font_curr.render(f"MEDIA: {self.player['ovr']}", True, UI_ACCENT)
        surface.blit(ovr_lbl, (WIDTH//2 - ovr_lbl.get_width()//2, 150))
        
        # Stats List
        start_y = 220
        for i, opt in enumerate(self.options):
            is_sel = (i == self.sel_idx)
            val = self.stats[opt["id"]]
            cost = self._get_cost(val)
            
            rect = pygame.Rect(WIDTH//2 - 200, start_y + i * 70, 400, 60)
            bg = (40, 50, 80) if is_sel else (30, 35, 50)
            pygame.draw.rect(surface, bg, rect, border_radius=10)
            if is_sel:
                pygame.draw.rect(surface, UI_ACCENT_ALT, rect, 2, border_radius=10)
                
            name_t = self.font_stat.render(opt["name"], True, WHITE)
            surface.blit(name_t, (rect.left + 20, rect.centery - name_t.get_height()//2))
            
            val_t = self.font_curr.render(str(val), True, (100, 255, 150))
            surface.blit(val_t, (rect.right - 60, rect.centery - val_t.get_height()//2))

            # Cost label
            cost_t = self.font_text.render(f"Coste: {cost}", True, YELLOW if is_sel else UI_TEXT_DIM)
            surface.blit(cost_t, (rect.right + 15, rect.centery - cost_t.get_height()//2))
            
            # Progress bar for stat
            bar_w = 150
            bar_rect = pygame.Rect(rect.left + 150, rect.centery - 5, bar_w, 10)
            pygame.draw.rect(surface, (20, 20, 20), bar_rect, border_radius=5)
            pygame.draw.rect(surface, (100, 255, 100), (bar_rect.x, bar_rect.y, int(bar_w * (val/99)), 10), border_radius=5)

        if self.msg_timer > 0:
            ms = self.font_text.render(self.msg, True, UI_ACCENT)
            surface.blit(ms, (WIDTH//2 - ms.get_width()//2, HEIGHT - 100))
            
        hint = self.font_hint.render("ENTER Mejorar Atributo  ·  ESC Volver", True, UI_TEXT_DIM)
        surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 40))
