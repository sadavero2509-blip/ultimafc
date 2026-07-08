import pygame
from settings import *
from data.career_manager import career_manager

class CareerNegotiationScene:
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        
        self.roles = ["Estrella", "Fijo", "Rotación", "Promesa", "Ocasional"]
        player_role = career_manager.career_player.get("role", "Rotación")
        if player_role not in self.roles: player_role = "Rotación"
        self.sel_role_idx = self.roles.index(player_role)
        self.proposed_salary = career_manager.career_player.get("salary", 0.5)
        
        self.step = "select" # "select", "result"
        self.result_msg = ""
        self.result_state = "" # "accepted", "counter", "rejected"
        self.counter_val = 0
        
        try:
            self.font_title = pygame.font.SysFont("Impact", 36)
            self.font_text = pygame.font.SysFont("Arial", 22, bold=True)
            self.font_sub = pygame.font.SysFont("Arial", 16)
            self.font_hint = pygame.font.SysFont("Arial", 14)
        except:
            self.font_title = pygame.font.Font(None, 36)
            self.font_text = pygame.font.Font(None, 22)
            self.font_sub = pygame.font.Font(None, 16)
            self.font_hint = pygame.font.Font(None, 14)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.step == "select":
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.sel_role_idx = (self.sel_role_idx - 1) % len(self.roles)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.sel_role_idx = (self.sel_role_idx + 1) % len(self.roles)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        self.proposed_salary = round(max(0.1, self.proposed_salary - 0.05), 2)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.proposed_salary = round(min(50.0, self.proposed_salary + 0.05), 2)
                    elif event.key == pygame.K_RETURN:
                        self._propose()
                    elif event.key == pygame.K_ESCAPE:
                        from scenes.career_hub import CareerHubScene
                        self.manager.set_scene(CareerHubScene)
                else:
                    if event.key == pygame.K_RETURN:
                        if self.result_state == "accepted":
                            self._apply(self.roles[self.sel_role_idx], self.proposed_salary)
                        elif self.result_state == "counter":
                            self._apply(self.roles[self.sel_role_idx], self.counter_val)
                        else:
                            from scenes.career_hub import CareerHubScene
                            self.manager.set_scene(CareerHubScene)
                    elif event.key == pygame.K_ESCAPE:
                        from scenes.career_hub import CareerHubScene
                        self.manager.set_scene(CareerHubScene)

    def _propose(self):
        role = self.roles[self.sel_role_idx]
        state, val, msg = career_manager.evaluate_contract_proposal(role, self.proposed_salary)
        self.result_state = state
        self.counter_val = val
        self.result_msg = msg
        self.step = "result"

    def _apply(self, role, salary):
        career_manager.career_player["contract_years"] = 3
        career_manager.career_player["role"] = role
        career_manager.career_player["salary"] = salary
        career_manager._update_prestige(5)
        
        # News: Renewal
        p_name = career_manager.career_player["name"]
        team_name = career_manager.player_team["name"]
        
        if role == "Estrella":
            comment = f"Seguirá siendo el líder indiscutible del {team_name} tras firmar un contrato estelar."
        elif role == "Promesa":
            comment = f"El club blinda a su joven perla, asegurando su futuro en la institución."
        else:
            comment = f"Ha decidido extender su estancia, confirmando su compromiso con el proyecto del club."
            
        career_manager.add_news("MERCADO", "RENOVACIÓN CONFIRMADA", 
                               f"¡{p_name} se queda! {comment}", 
                               importance=2, expiry_days=7)
        
        from scenes.career_hub import CareerHubScene
        self.manager.set_scene(CareerHubScene)

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((15, 20, 30))
        
        title = self.font_title.render("NEGOCIACIÓN DE CONTRATO", True, UI_ACCENT)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 40))
        
        contract_years = career_manager.career_player.get("contract_years", 0)
        sub_title = self.font_sub.render(f"Contrato actual: {contract_years} año(s) restante(s)", True, WHITE)
        surface.blit(sub_title, (WIDTH//2 - sub_title.get_width()//2, 90))
        
        if self.step == "select":
            # Role selection
            ry = 150
            for i, role in enumerate(self.roles):
                is_sel = (self.sel_role_idx == i)
                color = WHITE if is_sel else UI_TEXT_DIM
                if is_sel:
                    pygame.draw.rect(surface, (40, 50, 80), (WIDTH//2 - 150, ry - 5, 300, 35), border_radius=5)
                rs = self.font_text.render(role, True, color)
                surface.blit(rs, (WIDTH//2 - rs.get_width()//2, ry))
                ry += 45
                
            # Salary selection
            sy = ry + 40
            label = self.font_sub.render("SALARIO PROPUESTO (Millones/Año):", True, UI_ACCENT)
            surface.blit(label, (WIDTH//2 - label.get_width()//2, sy))
            
            sal_str = f"${self.proposed_salary:.2f}M"
            ss = self.font_title.render(sal_str, True, WHITE)
            surface.blit(ss, (WIDTH//2 - ss.get_width()//2, sy + 30))
            
            hint = self.font_hint.render("↑↓ Rol  ·  ← → Salario  ·  ENTER Proponer  ·  ESC Volver", True, UI_TEXT_DIM)
            surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 50))
        else:
            # Result display
            color = (100, 255, 100) if self.result_state == "accepted" else (255, 200, 50) if self.result_state == "counter" else (255, 100, 100)
            status_t = self.font_title.render(self.result_state.upper(), True, color)
            surface.blit(status_t, (WIDTH//2 - status_t.get_width()//2, HEIGHT//2 - 100))
            
            words = self.result_msg.split(' ')
            line = ""
            dy = HEIGHT//2 - 30
            for word in words:
                test_line = line + word + " "
                if self.font_sub.size(test_line)[0] < 500:
                    line = test_line
                else:
                    surface.blit(self.font_sub.render(line, True, WHITE), (WIDTH//2 - self.font_sub.size(line)[0]//2, dy))
                    line = word + " "
                    dy += 25
            surface.blit(self.font_sub.render(line, True, WHITE), (WIDTH//2 - self.font_sub.size(line)[0]//2, dy))
            
            hint = self.font_hint.render("ENTER Continuar / Aceptar  ·  ESC Cancelar", True, UI_TEXT_DIM)
            surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 50))
