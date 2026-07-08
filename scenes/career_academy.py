import pygame
from settings import *
from data.career_manager import career_manager

class CareerAcademyScene:
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        
        self.team = career_manager.player_team
        self.roster = career_manager.rosters.setdefault(self.team["short"], [])
        self.academy = self.team.setdefault("youth_academy", [])
        
        self.selected_idx = 0
        
        try:
            self.font_title = pygame.font.SysFont("Impact", 36)
            self.font_btn = pygame.font.SysFont("Arial", 22, bold=True)
            self.font_text = pygame.font.SysFont("Arial", 16)
            self.font_hint = pygame.font.SysFont("Arial", 14)
        except:
            self.font_title = pygame.font.Font(None, 36)
            self.font_btn = pygame.font.Font(None, 22)
            self.font_text = pygame.font.Font(None, 16)
            self.font_hint = pygame.font.Font(None, 14)

    def handle_events(self, events):
        max_idx = len(self.academy) - 1
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.selected_idx = max(0, self.selected_idx - 1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected_idx = min(max_idx, self.selected_idx + 1)
                elif event.key == pygame.K_RETURN:
                    self._promote_player()
                elif event.key == pygame.K_ESCAPE:
                    from scenes.career_hub import CareerHubScene
                    self.manager.set_scene(CareerHubScene)

    def _promote_player(self):
        if not self.academy or self.selected_idx >= len(self.academy): return
        p = self.academy[self.selected_idx]
        
        if p.get("age", 15) >= 16:
            # Promote
            self.roster.append(p)
            self.academy.pop(self.selected_idx)
            if self.selected_idx > 0: self.selected_idx -= 1

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((10, 15, 20))
        
        title = self.font_title.render("CANTERA Y FUERZAS BÁSICAS", True, UI_ACCENT)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 40))
        
        if not self.academy:
            lbl = self.font_text.render("No hay prospectos en la cantera en este momento.", True, UI_TEXT_DIM)
            surface.blit(lbl, (WIDTH//2 - lbl.get_width()//2, 200))
        else:
            for i, p in enumerate(self.academy):
                rect = pygame.Rect(100, 120 + i * 80, WIDTH - 200, 70)
                is_sel = (self.selected_idx == i)
                bg = UI_CARD_HOVER if is_sel else UI_CARD_BG
                
                pygame.draw.rect(surface, bg, rect, border_radius=8)
                if is_sel:
                    pygame.draw.rect(surface, UI_ACCENT, rect, 2, border_radius=8)
                    
                # Details
                ns = self.font_btn.render(p["name"], True, WHITE)
                surface.blit(ns, (rect.left + 20, rect.top + 10))
                
                ps = self.font_text.render(f"POS: {p['pos']}  |  EDAD: {p['age']}  |  OVR: {p['ovr']}", True, (200, 200, 200))
                surface.blit(ps, (rect.left + 20, rect.bottom - 25))
                
                # Pot range (fuzzy)
                pot = p["pot"]
                p_text = f"POTENCIAL: {pot-3} - {min(99, pot+3)}"
                pots = self.font_btn.render(p_text, True, (100, 255, 100))
                surface.blit(pots, (rect.right - pots.get_width() - 20, rect.centery - pots.get_height()//2))
                
                # Promotion rule
                if p["age"] < 16:
                    rs = self.font_hint.render("Demasiado joven para promover.", True, (255, 100, 100))
                    surface.blit(rs, (rect.left + 350, rect.bottom - 25))
                elif is_sel:
                    rs = self.font_hint.render("ENTER: Promover al Primer Equipo", True, UI_ACCENT)
                    surface.blit(rs, (rect.left + 350, rect.bottom - 25))
                    
        hint = self.font_hint.render("ESC Volver", True, UI_TEXT_DIM)
        surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 30))
