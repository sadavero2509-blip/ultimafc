import pygame
import time
import math
from settings import *
from .main_menu import MenuScene
from systems.network import NetworkManager

class OnlineMatchmakingScene(MenuScene):
    def __init__(self, manager, team_data=None):
        super().__init__(manager)
        self.team_data = team_data # {name, roster}
        self.start_time = time.time()
        self.status = "Buscando oponente..."
        self.nm = NetworkManager()
        self.nm.on_match_found = self._on_match_found
        self.nm.start_matchmaking()
        self.opponent_data = None
        self.is_host = False
        self.match_ready = False
        self.ready_time = 0

    def _on_match_found(self, data):
        self.opponent_data = data["opponent"]
        self.is_host = data["is_host"]
        self.status = f"¡Oponente encontrado: {self.opponent_data}!"
        self.match_ready = True
        self.ready_time = time.time()

    def update(self, dt):
        if self.match_ready and time.time() - self.ready_time > 2.0:
            from .match import MatchScene
            from data.teams import TEAMS
            import random
            
            # Simulamos un equipo para el oponente (en una versión final esto vendría del server)
            elite_teams = [t for t in TEAMS if t.get("is_elite", False)]
            opp_team = random.choice(elite_teams)
            opp_team["name"] = self.opponent_data # Usamos el nombre real del usuario
            
            # Si venimos de Ultimate Team, usar el roster real o simulado fuerte
            if self.manager.shared_data.get("game_mode") == "ultimate_online_league":
                from data.rosters import get_base_rosters
                rosters = get_base_rosters()
                if opp_team["short"] in rosters:
                    opp_team["roster"] = rosters[opp_team["short"]][:11]
                self.manager.shared_data["rival_team"] = opp_team
                self.manager.shared_data["player_team"] = self.team_data
                self.manager.transition_to(MatchScene)
            else:
                self.manager.shared_data["game_mode"] = "online"
                self.manager.shared_data["player_team"] = self.team_data
                self.manager.shared_data["rival_team"] = opp_team
                self.manager.transition_to(MatchScene)

    def draw(self, screen):
        screen.fill((15, 20, 35))
        
        # Título
        self.draw_text(screen, "PARTIDO AMISTOSO ONLINE", WIDTH//2, 100, size=40, color=UI_ACCENT, center=True, bold=True)
        
        # Radar de búsqueda
        center = (WIDTH//2, HEIGHT//2)
        radius = 150
        pygame.draw.circle(screen, (30, 40, 60), center, radius, 2)
        pygame.draw.circle(screen, (30, 40, 60), center, radius - 50, 1)
        pygame.draw.circle(screen, (30, 40, 60), center, radius - 100, 1)
        
        # Línea de radar
        if not self.match_ready:
            angle = time.time() * 3
            end_x = center[0] + math.cos(angle) * radius
            end_y = center[1] + math.sin(angle) * radius
            pygame.draw.line(screen, UI_ACCENT, center, (end_x, end_y), 3)
            
            # Efecto de pulso
            pulse = (math.sin(time.time() * 5) + 1) / 2
            pygame.draw.circle(screen, (*UI_ACCENT, int(pulse * 100)), center, int(radius * pulse), 1)
        else:
            pygame.draw.circle(screen, (50, 200, 100), center, radius, 4)

        self.draw_text(screen, self.status, WIDTH//2, HEIGHT//2 + 180, size=24, color=WHITE, center=True)
        
        # Info del equipo seleccionado
        if self.team_data:
            self.draw_text(screen, f"Tu equipo: {self.team_data['name']}", 50, HEIGHT - 50, size=18, color=UI_TEXT_DIM)

        self.draw_text(screen, "[ESC] Cancelar búsqueda", WIDTH//2, HEIGHT - 50, size=16, color=UI_TEXT_DIM, center=True)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.nm.cancel_matchmaking()
                self.manager.pop_scene()
