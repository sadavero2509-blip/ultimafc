import pygame
import math
import random
from settings import *
from scene_manager import BaseScene


class GoalCelebrationScene(BaseScene):
    """Escena de celebración de gol con animaciones."""

    def __init__(self, manager, scoring_team=None, left_score=0, right_score=0,
                 left_team=None, right_team=None, scorer_name=None, goal_min=0):
        super().__init__(manager)
        self.time = 0
        self.scoring_team = scoring_team  # dict del equipo que anotó
        self.left_score = left_score
        self.right_score = right_score
        self.left_team = left_team
        self.right_team = right_team
        self.scorer_name = scorer_name
        self.goal_min = goal_min
        self.duration = CELEBRATION_DURATION


        # Confetti
        self.confetti = []
        if scoring_team:
            colors = [scoring_team["primary"], scoring_team["secondary"],
                      scoring_team.get("accent", YELLOW), YELLOW, WHITE]
            for _ in range(120):
                self.confetti.append({
                    "x": random.randint(0, WIDTH),
                    "y": random.randint(-HEIGHT, 0),
                    "vx": random.uniform(-80, 80),
                    "vy": random.uniform(100, 350),
                    "size": random.randint(3, 8),
                    "color": random.choice(colors),
                    "rot": random.uniform(0, 360),
                    "rot_speed": random.uniform(-300, 300),
                })

        try:
            self.font_goal = pygame.font.SysFont("Impact", 100)
            self.font_score = pygame.font.SysFont("Impact", 60)
            self.font_team = pygame.font.SysFont("Arial", 28, bold=True)
            self.font_hint = pygame.font.SysFont("Arial", 18)
        except:
            self.font_goal = pygame.font.Font(None, 100)
            self.font_score = pygame.font.Font(None, 60)
            self.font_team = pygame.font.Font(None, 28)
            self.font_hint = pygame.font.Font(None, 18)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if self.time > 0.5:  # Evitar skip accidental
                        self._return_to_match()

    def _return_to_match(self):
        from scenes.match import MatchScene
        self.manager.transition_to(MatchScene, resume=True)

    def update(self, dt):
        self.time += dt

        # Actualizar confetti
        for c in self.confetti:
            c["x"] += c["vx"] * dt
            c["y"] += c["vy"] * dt
            c["rot"] += c["rot_speed"] * dt
            # Gravedad
            c["vy"] += 80 * dt
            # Resistencia del aire
            c["vx"] *= 0.998

        # Auto-volver al partido después de la duración
        if self.time >= self.duration:
            self._return_to_match()

    def draw(self, surface):
        # ── Flash blanco inicial ──
        if self.time < 0.3:
            flash_alpha = int(255 * (1 - self.time / 0.3))
            surface.fill(WHITE)
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.fill(UI_BG)
            overlay.set_alpha(255 - flash_alpha)
            surface.blit(overlay, (0, 0))
        else:
            # Fondo oscuro
            surface.fill(UI_BG)

        # ── Confetti ──
        for c in self.confetti:
            if 0 <= c["y"] <= HEIGHT:
                conf_surf = pygame.Surface((c["size"], c["size"] // 2 + 1), pygame.SRCALPHA)
                pygame.draw.rect(conf_surf, c["color"],
                                 (0, 0, c["size"], c["size"] // 2 + 1))
                rotated = pygame.transform.rotate(conf_surf, c["rot"])
                surface.blit(rotated, (int(c["x"]), int(c["y"])))

        # ── Texto "¡¡GOOOL!!" con efecto de escala ──
        if self.time < 0.8:
            scale = min(1.0, self.time / 0.4) * 1.2
            if self.time > 0.4:
                scale = 1.2 - (self.time - 0.4) / 0.4 * 0.2
        else:
            scale = 1.0 + math.sin(self.time * 6) * 0.05

        goal_text = "¡¡ G O O O L !!"
        # Renderizar a tamaño normal y escalar
        base_surf = self.font_goal.render(goal_text, True, YELLOW)

        scaled_w = int(base_surf.get_width() * scale)
        scaled_h = int(base_surf.get_height() * scale)
        if scaled_w > 0 and scaled_h > 0:
            scaled_surf = pygame.transform.scale(base_surf, (scaled_w, scaled_h))
            scaled_rect = scaled_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60))

            # Sombra
            shadow_surf = self.font_goal.render(goal_text, True, (50, 50, 0))
            shadow_scaled = pygame.transform.scale(shadow_surf, (scaled_w, scaled_h))
            shadow_rect = shadow_scaled.get_rect(center=(WIDTH // 2 + 4, HEIGHT // 2 - 56))
            surface.blit(shadow_scaled, shadow_rect)

            surface.blit(scaled_surf, scaled_rect)

        # ── Nombre del equipo que anotó ──
        if self.scoring_team and self.time > 0.5:
            alpha = min(255, int((self.time - 0.5) * 500))
            team_surf = self.font_team.render(self.scoring_team["name"], True,
                                               self.scoring_team["primary"])
            team_surf.set_alpha(alpha)
            team_rect = team_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30))
            surface.blit(team_surf, team_rect)

            # Nombre del goleador y minuto
            if self.scorer_name:
                info_text = f"{self.scorer_name} ({self.goal_min}')"
                info_surf = self.font_hint.render(info_text, True, WHITE)
                info_surf.set_alpha(alpha)
                info_rect = info_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 65))
                surface.blit(info_surf, info_rect)


        # ── Marcador actual ──
        if self.time > 0.8:
            alpha = min(255, int((self.time - 0.8) * 500))
            score_str = f"{self.left_score}  -  {self.right_score}"
            score_surf = self.font_score.render(score_str, True, WHITE)
            score_surf.set_alpha(alpha)
            score_rect = score_surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
            surface.blit(score_surf, score_rect)

            # Nombres de equipos bajo el marcador
            if self.left_team:
                ln = self.font_hint.render(self.left_team["short"], True, UI_TEXT_DIM)
                ln.set_alpha(alpha)
                surface.blit(ln, (score_rect.left - 20, score_rect.bottom + 5))
            if self.right_team:
                rn = self.font_hint.render(self.right_team["short"], True, UI_TEXT_DIM)
                rn.set_alpha(alpha)
                surface.blit(rn, (score_rect.right - 20, score_rect.bottom + 5))

        # ── Hint ──
        if self.time > 1.5:
            pulse = (math.sin(self.time * 4) + 1) / 2
            hint_alpha = int(100 + pulse * 100)
            hint_surf = self.font_hint.render("Presiona ENTER para continuar", True, UI_TEXT_DIM)
            hint_surf.set_alpha(hint_alpha)
            hint_rect = hint_surf.get_rect(center=(WIDTH // 2, HEIGHT - 50))
            surface.blit(hint_surf, hint_rect)


class MatchEndScene(BaseScene):
    """Pantalla de fin de partido con resultado."""

    def __init__(self, manager, left_score=0, right_score=0,
                 left_team=None, right_team=None, goal_events=None, player_stats=None, player_side="left"):
        super().__init__(manager)
        self.time = 0
        self.left_score = left_score
        self.right_score = right_score
        self.left_team = left_team
        self.right_team = right_team
        self.goal_events = goal_events or []
        self.player_stats = player_stats or []
        self.player_side = player_side

        # Determinar ganador desde la perspectiva del usuario (usando IDs de equipo)
        from data.career_manager import career_manager
        user_team = self.manager.shared_data.get("player_team")
        user_team_short = user_team["short"] if user_team else ""
        if not user_team_short and career_manager.active:
            user_team_short = career_manager.player_team["short"]
        
        # Determinar si el usuario está del lado izquierdo basándose en el short code del equipo
        is_left = False
        if user_team_short:
            is_left = (self.left_team and self.left_team.get("short") == user_team_short)
        else:
            is_left = (self.player_side == "left")
        
        if is_left:
            user_score = self.left_score
            opp_score = self.right_score
        else:
            user_score = self.right_score
            opp_score = self.left_score
            
        if user_score > opp_score:
            self.result_text = "¡VICTORIA!"
        elif opp_score > user_score:
            self.result_text = "DERROTA"
        else:
            self.result_text = "EMPATE"

        try:
            self.font_result = pygame.font.SysFont("Impact", 72)
            self.font_score = pygame.font.SysFont("Impact", 90)
            self.font_team = pygame.font.SysFont("Arial", 26, bold=True)
            self.font_hint = pygame.font.SysFont("Arial", 20)
            self.font_label = pygame.font.SysFont("Arial", 18)
        except:
            self.font_result = pygame.font.Font(None, 72)
            self.font_score = pygame.font.Font(None, 90)
            self.font_team = pygame.font.Font(None, 26)
            self.font_hint = pygame.font.Font(None, 20)
            self.font_label = pygame.font.Font(None, 18)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE or event.key == pygame.K_ESCAPE:
                    # Check if we're in ultimate mode
                    if self.manager.shared_data.get("game_mode", "").startswith("ultimate"):
                        self._finish_ultimate_match()
                        return
                    
                    # Check if we're in online mode
                    if self.manager.shared_data.get("game_mode") == "online":
                        self._finish_online_match()
                        return
                    
                    # Check if we're in career mode
                    career_state = self.manager.shared_data.get("career_match_state")
                    if career_state:
                        self._finish_career_match(career_state)
                        return
                    # Check if we're in tournament mode
                    tournament_state = self.manager.shared_data.get("tournament_hub_state")
                    if tournament_state:
                        from scenes.tournament_hub import TournamentHubScene
                        ctx = tournament_state["context"]
                        hub = TournamentHubScene(self.manager, context=ctx)
                        hub._restore_state(tournament_state)
                        hub.advance_round((self.left_score, self.right_score))
                        del self.manager.shared_data["tournament_hub_state"]
                        if "tournament_context" in self.manager.shared_data:
                            del self.manager.shared_data["tournament_context"]
                        self.manager.current_scene = hub
                    else:
                        from scenes.main_menu import MainMenuScene
                        self.manager.transition_to(MainMenuScene)

    def _finish_ultimate_match(self):
        from systems.ultimate_manager import ultimate_manager
        
        user_team = self.manager.shared_data.get("player_team")
        user_team_short = user_team["short"] if user_team else ""
        
        is_left = False
        if user_team_short:
            is_left = (self.left_team and self.left_team.get("short") == user_team_short)
        else:
            is_left = (self.player_side == "left")
            
        gf = self.left_score if is_left else self.right_score
        ga = self.right_score if is_left else self.left_score
        
        res = {
            "gf": gf,
            "ga": ga,
            "goal_events": self.goal_events,
            "player_stats": self.player_stats,
            "reward": self.manager.shared_data.get("match_reward", 500)
        }
        
        # Actualizar estadísticas en el manager
        ultimate_manager.advance_match_stats(res)
        
        # Actualizar objetivos diarios y pase de batalla
        ultimate_manager.advance_objectives(gf, ga)
        
        # Modo Liga: Actualizar puntos y división
        if self.manager.shared_data.get("game_mode") == "ultimate_league":
            ultimate_manager.advance_league_match(gf, ga)
        elif self.manager.shared_data.get("game_mode") == "ultimate_online_league":
            ultimate_manager.advance_online_league_match(gf, ga)
            
        ultimate_manager.save_ultimate()
        
        # Limpiar datos
        if "match_state" in self.manager.shared_data:
            del self.manager.shared_data["match_state"]
        from scenes.ultimate_hub import UltimateHubScene
        self.manager.transition_to(UltimateHubScene)

    def _finish_online_match(self):
        from systems.network import NetworkManager
        nm = NetworkManager()
        if nm.connected:
            user_team = self.manager.shared_data.get("player_team")
            user_team_short = user_team["short"] if user_team else ""
            
            is_left = False
            if user_team_short:
                is_left = (self.left_team and self.left_team.get("short") == user_team_short)
            else:
                is_left = (self.player_side == "left")
                
            gf = self.left_score if is_left else self.right_score
            ga = self.right_score if is_left else self.left_score
            user_t = self.left_team if is_left else self.right_team
            
            # Calcular puntos ganados para subir a la tabla
            pts = 0
            if gf > ga:
                pts = 3 # Victoria
            elif gf == ga:
                pts = 1 # Empate
            pts += gf # +1 por gol anotado
            
            # Intentar subir al Ranking Mundial
            team_name = user_t.get("name", "Mi Equipo") if user_t else "Mi Equipo"
            nm.post_score(pts, team_name)
            
        if "match_state" in self.manager.shared_data:
            del self.manager.shared_data["match_state"]
            
        from scenes.online_hub import OnlineHubScene
        self.manager.transition_to(OnlineHubScene)

    def _finish_career_match(self, career_state):
        """Process real match result back into the career engine."""
        from data.career_manager import career_manager
        
        user_team_short = career_manager.player_team["short"]
        if self.left_team and self.left_team["short"] == user_team_short:
            gf = self.left_score
            ga = self.right_score
        else:
            gf = self.right_score
            ga = self.left_score
        
        res = {
            "gf": gf,
            "ga": ga,
            "scorers": [e["scorer"] for e in self.goal_events if e["scorer"]],
            "assists": [e["assistant"] for e in self.goal_events if e["assistant"]],
            "player_stats": self.player_stats
        }
        
        career_manager.advance_time(res)
        
        # Player Mode: Reward Skill Points
        if career_manager.mode == "player":
            cp_name = career_manager.career_player["name"].lower().strip()
            played = False
            for ps in self.player_stats:
                if ps.get("name") and ps["name"].lower().strip() == cp_name:
                    played = True
                    break
            
            if played:
                reward = 1 # Participation
                if gf > ga: reward += 2 # Win
                elif gf == ga: reward += 1 # Draw
                
                career_manager.skill_points += reward
                self.manager.shared_data["last_reward"] = reward
            else:
                self.manager.shared_data["last_reward"] = 0
        
        # Clean up shared_data
        if "career_match_state" in self.manager.shared_data:
            del self.manager.shared_data["career_match_state"]
        if "match_state" in self.manager.shared_data:
            del self.manager.shared_data["match_state"]
        
        # Chance of Press Conference
        result_str = "win" if gf > ga else ("loss" if gf < ga else "draw")
        import random
        # 40% chance or if it's an important match (final, etc)
        if random.random() < 0.4 or self.manager.shared_data.get("is_important_match"):
            from scenes.press_conference import PressConferenceScene
            self.manager.set_scene(PressConferenceScene, context={"result": result_str})
        else:
            from scenes.career_hub import CareerHubScene
            self.manager.set_scene(CareerHubScene)

    def update(self, dt):
        self.time += dt

    def draw(self, surface):
        # Fondo
        surface.fill(UI_BG)

        # Resultado
        if self.result_text == "¡VICTORIA!":
            result_color = (0, 220, 100)
        elif self.result_text == "DERROTA":
            result_color = (220, 50, 50)
        else:
            result_color = YELLOW

        # Label "FINAL DEL PARTIDO"
        label_surf = self.font_label.render("FINAL DEL PARTIDO", True, UI_TEXT_DIM)
        label_rect = label_surf.get_rect(center=(WIDTH // 2, 120))
        surface.blit(label_surf, label_rect)

        # Resultado
        result_surf = self.font_result.render(self.result_text, True, result_color)
        result_rect = result_surf.get_rect(center=(WIDTH // 2, 180))
        surface.blit(result_surf, result_rect)

        # Marcador grande
        score_str = f"{self.left_score}  -  {self.right_score}"
        score_surf = self.font_score.render(score_str, True, WHITE)
        score_rect = score_surf.get_rect(center=(WIDTH // 2, 320))
        surface.blit(score_surf, score_rect)

        # Nombres de equipos
        if self.left_team:
            from data.teams import draw_badge
            draw_badge(surface, self.left_team, WIDTH // 2 - 160, 320, size=60)
            ln = self.font_team.render(self.left_team["name"], True, UI_TEXT)
            lr = ln.get_rect(center=(WIDTH // 2 - 160, 370))
            surface.blit(ln, lr)

        if self.right_team:
            from data.teams import draw_badge
            draw_badge(surface, self.right_team, WIDTH // 2 + 160, 320, size=60)
            rn = self.font_team.render(self.right_team["name"], True, UI_TEXT)
            rr = rn.get_rect(center=(WIDTH // 2 + 160, 370))
            surface.blit(rn, rr)

        # Hint
        if self.time > 1.0:
            pulse = (math.sin(self.time * 3) + 1) / 2
            hint_surf = self.font_hint.render("Presiona ENTER para volver al menú", True,
                                               (int(100 + pulse * 80),) * 3)
            hint_rect = hint_surf.get_rect(center=(WIDTH // 2, HEIGHT - 60))
            surface.blit(hint_surf, hint_rect)
            
        # ── Listado de Goleadores ──
        left_goals = []
        right_goals = []
        if self.left_team and self.right_team:
            left_goals = [e for e in self.goal_events if e.get("team") == self.left_team["short"]]
            right_goals = [e for e in self.goal_events if e.get("team") == self.right_team["short"]]
        
        goal_y_start = 400
        for i, g in enumerate(left_goals[:4]): # Max 4 per side to avoid clutter
            txt = f"Gol: {g['scorer']} {g['min']}'"
            gs = self.font_label.render(txt, True, UI_TEXT_DIM)
            surface.blit(gs, (WIDTH // 2 - 160 - gs.get_width() // 2, goal_y_start + i * 22))
            
        for i, g in enumerate(right_goals[:4]):
            txt = f"Gol: {g['scorer']} {g['min']}'"
            gs = self.font_label.render(txt, True, UI_TEXT_DIM)
            surface.blit(gs, (WIDTH // 2 + 160 - gs.get_width() // 2, goal_y_start + i * 22))

        # ── Ratings display (Movido hacia abajo) ──
        if self.player_stats:
            # Sort by rating
            top_players = sorted(self.player_stats, key=lambda x: x["rating"], reverse=True)[:5]
            
            start_y = 520
            title = self.font_label.render("RENDIMIENTOS DESTACADOS", True, UI_ACCENT)
            surface.blit(title, (WIDTH//2 - title.get_width()//2, start_y))
            
            for i, ps in enumerate(top_players):
                name = ps.get("name", "Jugador")
                team = ps.get("team", "")
                rating = ps.get("rating", 6.0)
                if len(name) > 13: name = name[:11] + ".."
                
                # Color based on rating
                rc = (0, 200, 100) if rating >= 8.0 else (200, 200, 0) if rating >= 6.5 else (200, 100, 50)
                
                rs = self.font_label.render(f"{name} ({team})", True, WHITE)
                rv = self.font_label.render(f"{rating}", True, rc)
                
                surface.blit(rs, (WIDTH//2 - 140, start_y + 35 + i * 25))
                surface.blit(rv, (WIDTH//2 + 100, start_y + 35 + i * 25))


