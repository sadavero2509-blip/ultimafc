import pygame
from settings import *
from data.career_manager import career_manager

class CareerSquadScene:
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        
        if self.context.get("nt_mode"):
            t_short = self.context.get("team_short", "AR")
            self.team = career_manager.get_team_by_short(t_short)
            self.roster = career_manager.rosters.get(t_short, [])
            self.title_text = "PLANTILLA NACIONAL"
        else:
            self.team = career_manager.player_team
            self.roster = career_manager.rosters.get(self.team["short"], [])
            self.title_text = "MI PLANTILLA"
        
        self.scroll_y = 0
        self.selected_idx = 0
        self.swap_selected = None
        
        try:
            self.font_title = pygame.font.SysFont("Impact", 36)
            self.font_btn = pygame.font.SysFont("Arial", 22, bold=True)
            self.font_text = pygame.font.SysFont("Arial", 16)
            self.font_bold = pygame.font.SysFont("Arial", 16, bold=True)
            self.font_hint = pygame.font.SysFont("Arial", 14)
        except:
            self.font_title = pygame.font.Font(None, 36)
            self.font_btn = pygame.font.Font(None, 22)
            self.font_text = pygame.font.Font(None, 16)
            self.font_bold = pygame.font.Font(None, 16)
            self.font_hint = pygame.font.Font(None, 14)

    def handle_events(self, events):
        max_idx = len(self.roster) - 1
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.selected_idx = max(0, self.selected_idx - 1)
                    if self.selected_idx < self.scroll_y:
                        self.scroll_y = self.selected_idx
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected_idx = min(max_idx, self.selected_idx + 1)
                    if self.selected_idx >= self.scroll_y + 15:
                        self.scroll_y = self.selected_idx - 14
                elif event.key == pygame.K_t:
                    # Toggle Transfer List
                    p = self.roster[self.selected_idx]
                    p["transfer_listed"] = not p.get("transfer_listed", False)
                    if p["transfer_listed"]: p["loan_listed"] = False
                elif event.key == pygame.K_l:
                    # Toggle Loan List
                    p = self.roster[self.selected_idx]
                    p["loan_listed"] = not p.get("loan_listed", False)
                    if p["loan_listed"]: p["transfer_listed"] = False

                elif event.key == pygame.K_SPACE:
                    # Modo intercambio: seleccionar/intercambiar jugadores
                    if self.swap_selected is None:
                        self.swap_selected = self.selected_idx
                    elif self.swap_selected == self.selected_idx:
                        self.swap_selected = None
                    else:
                        a, b = self.swap_selected, self.selected_idx
                        self.roster[a], self.roster[b] = self.roster[b], self.roster[a]
                        self.swap_selected = None
                elif event.key == pygame.K_RETURN:
                    from scenes.career_profile import CareerProfileScene
                    p = self.roster[self.selected_idx]
                    self.manager.set_scene(CareerProfileScene, context={"player": p, "team": self.team, "from_scene": CareerSquadScene})
                elif event.key == pygame.K_ESCAPE:
                    from scenes.career_hub import CareerHubScene
                    self.manager.set_scene(CareerHubScene)

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((15, 20, 30))
        
        title = self.font_title.render(self.title_text, True, UI_ACCENT)
        surface.blit(title, (50, 30))
        
        b_lbl = self.font_text.render(f"Presupuesto: ${self.team.get('budget', 0)}M", True, (100, 255, 150))
        surface.blit(b_lbl, (WIDTH - 250, 45))
        
        cols = [("#", 30), ("POS", 40), ("NOMBRE", 220), ("EDAD", 50), ("OVR", 50), ("POT", 50), ("ESTADO", 150)]
        start_y = 100
        cx = 50
        for label, w in cols:
            ls = self.font_bold.render(label, True, UI_ACCENT)
            surface.blit(ls, (cx, start_y))
            cx += w
            
        pygame.draw.line(surface, (50, 55, 70), (40, start_y + 25), (WIDTH - 40, start_y + 25), 1)
        
        row_y = start_y + 40
        visible = self.roster[self.scroll_y : self.scroll_y + 15]
        
        for i, p in enumerate(visible):
            real_idx = self.scroll_y + i
            is_sel = (self.selected_idx == real_idx)
            
            is_swap = (self.swap_selected == real_idx)
            if is_swap:
                pygame.draw.rect(surface, (50, 45, 20), (45, row_y - 3, 700, 28), border_radius=4)
                pygame.draw.rect(surface, (218, 165, 32), (45, row_y - 3, 700, 28), 2, border_radius=4)
            elif is_sel:
                pygame.draw.rect(surface, UI_CARD_HOVER, (45, row_y - 3, 700, 28), border_radius=4)
                pygame.draw.rect(surface, UI_ACCENT, (45, row_y - 3, 700, 28), 1, border_radius=4)
                
            c_text = WHITE if is_sel else UI_TEXT_DIM
            if real_idx < 11: c_text = WHITE # Starters always white
            
            cx = 50
            # #
            ns = self.font_text.render(str(p.get("num", "?")), True, c_text)
            surface.blit(ns, (cx, row_y))
            cx += 30
            # POS
            pos_c = (220, 200, 50) if p["pos"] == "GK" else (50, 150, 250) if p["pos"] in ["CB", "LB", "RB"] else (50, 200, 100) if p["pos"] in ["CM", "CDM", "CAM"] else (250, 80, 80)
            pygame.draw.rect(surface, pos_c, (cx, row_y - 2, 32, 20), border_radius=4)
            ps = self.font_hint.render(p["pos"], True, BLACK)
            surface.blit(ps, (cx + 16 - ps.get_width()//2, row_y + 1))
            cx += 40
            # NOMBRE
            nms = self.font_bold.render(p["name"], True, c_text) if real_idx < 11 else self.font_text.render(p["name"], True, c_text)
            surface.blit(nms, (cx, row_y))
            cx += 220
            # EDAD
            try:
                age = int(p.get("age", 25))
            except (ValueError, TypeError):
                age = 25
            as_ = self.font_text.render(str(age), True, c_text)
            surface.blit(as_, (cx, row_y))
            cx += 50
            # OVR
            try:
                ovr = int(p.get("ovr", 75))
            except (ValueError, TypeError):
                ovr = 75
            ovr_c = (0, 220, 100) if ovr >= 85 else (255, 215, 0) if ovr >= 80 else UI_TEXT_DIM
            oss = self.font_bold.render(str(ovr), True, ovr_c)
            surface.blit(oss, (cx, row_y))
            cx += 50
            # POT
            try:
                pot = int(p.get("pot", ovr))
            except (ValueError, TypeError):
                pot = ovr
            pot_c = (0, 220, 255) if pot >= 88 else (0, 200, 100) if pot >= 82 else UI_TEXT_DIM
            pots = self.font_bold.render(str(pot), True, pot_c)
            surface.blit(pots, (cx, row_y))
            cx += 50
            # ESTADO
            # Cápsula de estado visual
            if p.get("injury_weeks", 0) > 0:
                status = f"LESIÓN ({p['injury_weeks']}s)"
                cap_bg = (180, 40, 40)
                cap_fg = WHITE
            elif p.get("transfer_listed"):
                status = "TRANSFERIBLE"
                cap_bg = (180, 60, 60)
                cap_fg = WHITE
            elif p.get("loan_listed"):
                status = "CEDIBLE"
                cap_bg = (60, 120, 200)
                cap_fg = WHITE
            elif real_idx < 11:
                status = "TITULAR"
                cap_bg = (0, 140, 70)
                cap_fg = WHITE
            else:
                status = "SUPLENTE"
                cap_bg = (55, 60, 75)
                cap_fg = (180, 180, 190)
            
            cap_w = max(80, self.font_hint.size(status)[0] + 14)
            cap_rect = pygame.Rect(cx, row_y - 1, cap_w, 20)
            pygame.draw.rect(surface, cap_bg, cap_rect, border_radius=10)
            st_s = self.font_hint.render(status, True, cap_fg)
            surface.blit(st_s, (cap_rect.centerx - st_s.get_width() // 2, cap_rect.centery - st_s.get_height() // 2))
            
            row_y += 30
            # Línea separadora entre titulares y suplentes
            if real_idx == 10 and real_idx < len(self.roster) - 1:
                pygame.draw.line(surface, (0, 200, 150), (50, row_y - 5), (740, row_y - 5), 2)
                sep_lbl = self.font_hint.render("── SUPLENTES ──", True, (0, 200, 150))
                surface.blit(sep_lbl, (350 - sep_lbl.get_width() // 2, row_y - 12))
                row_y += 8
            
        swap_hint = "  ·  [INTERCAMBIANDO...]" if self.swap_selected is not None else ""
        hint = self.font_hint.render(f"↑↓ Navegar  ·  ESPACIO Intercambiar  ·  ENTER Perfil  ·  T Transferible  ·  L Cedible  ·  ESC Volver{swap_hint}", True, UI_TEXT_DIM if self.swap_selected is None else GOLD)
        surface.blit(hint, (50, HEIGHT - 30))
