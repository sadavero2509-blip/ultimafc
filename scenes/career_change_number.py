import pygame
import math
from settings import *
from data.career_manager import career_manager

class CareerChangeNumberScene:
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        self.new_number = career_manager.career_player.get("num", 10)
        self.time = 0
        
        # Check taken status of the jersey
        self.taken_by = None
        self._update_taken_status()
        
        try:
            self.font_title = pygame.font.SysFont("Impact", 44)
            self.font_subtitle = pygame.font.SysFont("Arial", 22, bold=True)
            self.font_num = pygame.font.SysFont("Impact", 74)
            self.font_bold = pygame.font.SysFont("Arial", 18, bold=True)
            self.font_text = pygame.font.SysFont("Arial", 16)
            self.font_hint = pygame.font.SysFont("Arial", 15)
        except:
            self.font_title = pygame.font.Font(None, 44)
            self.font_subtitle = pygame.font.Font(None, 22)
            self.font_num = pygame.font.Font(None, 74)
            self.font_bold = pygame.font.Font(None, 18)
            self.font_text = pygame.font.Font(None, 16)
            self.font_hint = pygame.font.Font(None, 15)

    def _update_taken_status(self):
        self.taken_by = None
        team_short = career_manager.player_team["short"]
        if team_short in career_manager.rosters:
            for p in career_manager.rosters[team_short]:
                if not p.get("is_user_player") and p.get("num") == self.new_number:
                    self.taken_by = p
                    break

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.new_number = min(99, self.new_number + 1)
                    self._update_taken_status()
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.new_number = max(1, self.new_number - 1)
                    self._update_taken_status()
                elif event.key == pygame.K_RETURN:
                    self._confirm()
                elif event.key == pygame.K_ESCAPE:
                    self._skip()

    def _confirm(self):
        team_short = career_manager.player_team["short"]
        is_star = self.context.get("is_star", False)
        
        if self.taken_by:
            if is_star:
                # Steal the number! Assign a random free number to the other player
                taken_nums = {p["num"] for p in career_manager.rosters[team_short] if "num" in p}
                new_free = 99
                for candidate in range(1, 100):
                    if candidate not in taken_nums and candidate != self.new_number:
                        new_free = candidate
                        break
                
                old_owner_name = self.taken_by["name"]
                self.taken_by["num"] = new_free
                career_manager.career_player["num"] = self.new_number
                
                # Log dressroom narrative hook
                career_manager.add_news(
                    "VESTUARIO", 
                    "DORSAL CEDIDO", 
                    f"¡Poder de estrella! {old_owner_name} ha cedido amablemente el dorsal {self.new_number} al recién llegado {career_manager.career_player['name']}.", 
                    importance=2, 
                    expiry_days=7
                )
            else:
                # Regular players cannot steal the number
                return
        else:
            # Free number
            career_manager.career_player["num"] = self.new_number
            
        # Update user player in team roster database
        if team_short in career_manager.rosters:
            for p in career_manager.rosters[team_short]:
                if p.get("is_user_player"):
                    p["num"] = career_manager.career_player["num"]
                    break
        
        self._transition_next()

    def _skip(self):
        self._transition_next()

    def _transition_next(self):
        next_scene = self.context.get("next_scene")
        next_context = self.context.get("next_context") or {}
        
        # Keep presentation scene sync'd with player number
        if "number" in next_context:
            next_context["number"] = career_manager.career_player.get("num", 10)
            
        if next_scene:
            self.manager.set_scene(next_scene, context=next_context)
        else:
            from scenes.career_hub import CareerHubScene
            self.manager.set_scene(CareerHubScene)

    def update(self, dt):
        self.time += dt

    def draw(self, surface):
        # Premium dark slate glass background
        surface.fill((12, 16, 24))
        
        # 3D Grid Overlay for futuristic UI look
        for i in range(0, WIDTH, 40):
            pygame.draw.line(surface, (20, 26, 42), (i, 0), (i, HEIGHT))
        for j in range(0, HEIGHT, 40):
            pygame.draw.line(surface, (20, 26, 42), (0, j), (WIDTH, j))
            
        # Outer Card shadow & body
        card_w = 460
        card_h = 440
        card_rect = pygame.Rect(WIDTH//2 - card_w//2, HEIGHT//2 - card_h//2 - 20, card_w, card_h)
        
        pygame.draw.rect(surface, (0, 0, 0, 100), card_rect.move(5, 5), border_radius=15)
        pygame.draw.rect(surface, (20, 25, 40), card_rect, border_radius=15)
        
        # Glow border pulsing using team's primary color
        team = career_manager.player_team
        team_primary = team.get("primary", (0, 102, 204))
        team_secondary = team.get("secondary", (255, 255, 255))
        
        pulse = (math.sin(self.time * 3) + 1) / 2
        bc = (
            int(team_primary[0] * 0.7 + pulse * (team_primary[0] * 0.3)),
            int(team_primary[1] * 0.7 + pulse * (team_primary[1] * 0.3)),
            int(team_primary[2] * 0.7 + pulse * (team_primary[2] * 0.3))
        )
        pygame.draw.rect(surface, bc, card_rect, 3, border_radius=15)
        
        # Title
        title_surf = self.font_title.render("NEGOCIACIÓN DE DORSAL", True, UI_ACCENT)
        surface.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, card_rect.top + 25))
        
        team_lbl = self.font_text.render(f"Petición oficial al {team['name']}", True, UI_TEXT_DIM)
        surface.blit(team_lbl, (WIDTH//2 - team_lbl.get_width()//2, card_rect.top + 70))
        
        # Render Vector Jersey
        self._draw_jersey(surface, WIDTH//2, card_rect.centery + 15, str(self.new_number), team_primary, team_secondary)
        
        # Status box below jersey
        status_y = card_rect.bottom - 80
        is_star = self.context.get("is_star", False)
        
        if self.taken_by:
            if is_star:
                status_txt = f"⚠️ OCUPADO POR {self.taken_by['name'].upper()}"
                status_sub = "Tu estatus de estrella forzará al club a cedértelo."
                color = (255, 200, 50)
            else:
                status_txt = f"❌ OCUPADO POR {self.taken_by['name'].upper()}"
                status_sub = "Dado tu rol modesto, no puedes exigir este dorsal."
                color = (255, 100, 100)
        else:
            status_txt = "🟢 DORSAL TOTALMENTE DISPONIBLE"
            status_sub = "¡Está libre! Te será asignado oficialmente al instante."
            color = (100, 255, 100)
            
        st_surf = self.font_subtitle.render(status_txt, True, color)
        surface.blit(st_surf, (WIDTH//2 - st_surf.get_width()//2, status_y))
        
        sub_surf = self.font_text.render(status_sub, True, UI_TEXT_DIM)
        surface.blit(sub_surf, (WIDTH//2 - sub_surf.get_width()//2, status_y + 25))
        
        # Hints
        hint_str = "▲▼ / W S: Cambiar Número  ·  ENTER: Confirmar Dorsal  ·  ESC: Omitir / Mantener"
        hint_surf = self.font_hint.render(hint_str, True, WHITE)
        surface.blit(hint_surf, (WIDTH//2 - hint_surf.get_width()//2, HEIGHT - 80))

    def _draw_jersey(self, surface, cx, cy, num_str, primary, secondary):
        w = 120
        h = 135
        
        # Draw shadow
        shadow_pts = [
            (cx - w//2 + 4, cy - h//2 + 4),
            (cx - w//3 + 4, cy - h//2 - 8 + 4),
            (cx + w//3 + 4, cy - h//2 - 8 + 4),
            (cx + w//2 + 4, cy - h//2 + 4),
            (cx + w//2 + 20 + 4, cy - h//3 + 4),
            (cx + w//3 + 8 + 4, cy - h//4 + 4),
            (cx + w//3 + 4 + 4, cy + h//2 + 4),
            (cx - w//3 - 4 + 4, cy + h//2 + 4),
            (cx - w//3 - 8 + 4, cy - h//4 + 4),
            (cx - w//2 - 20 + 4, cy - h//3 + 4)
        ]
        pygame.draw.polygon(surface, (0, 0, 0, 100), shadow_pts)
        
        # Primary body
        pts = [
            (cx - w//2, cy - h//2),
            (cx - w//3, cy - h//2 - 8),
            (cx + w//3, cy - h//2 - 8),
            (cx + w//2, cy - h//2),
            (cx + w//2 + 20, cy - h//3),
            (cx + w//3 + 8, cy - h//4),
            (cx + w//3 + 4, cy + h//2),
            (cx - w//3 - 4, cy + h//2),
            (cx - w//3 - 8, cy - h//4),
            (cx - w//2 - 20, cy - h//3)
        ]
        pygame.draw.polygon(surface, primary, pts)
        pygame.draw.polygon(surface, secondary, pts, 2)
        
        # Collar (secondary)
        neck_pts = [
            (cx - w//6, cy - h//2 - 4),
            (cx + w//6, cy - h//2 - 4),
            (cx, cy - h//2 + 8)
        ]
        pygame.draw.polygon(surface, secondary, neck_pts)
        
        # Sleeves stripe (secondary)
        left_s = [
            (cx - w//2, cy - h//2),
            (cx - w//2 - 20, cy - h//3),
            (cx - w//2 - 14, cy - h//3 + 4),
            (cx - w//2 + 4, cy - h//2 + 4)
        ]
        pygame.draw.polygon(surface, secondary, left_s)
        
        right_s = [
            (cx + w//2, cy - h//2),
            (cx + w//2 + 20, cy - h//3),
            (cx + w//2 + 14, cy - h//3 + 4),
            (cx + w//2 - 4, cy - h//2 + 4)
        ]
        pygame.draw.polygon(surface, secondary, right_s)
        
        # Jersey stripes details (sleek central striping)
        pygame.draw.rect(surface, secondary, (cx - 4, cy - h//3, 8, h*0.7))
        
        # Render number inside jersey (contrast secondary or white)
        num_surf = self.font_num.render(num_str, True, secondary)
        num_rect = num_surf.get_rect(center=(cx, cy + 10))
        surface.blit(num_surf, num_rect)
