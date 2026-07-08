import pygame
import math
import random
from settings import *

class TournamentHubScene:
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        
        self.player_team = self.context.get("player_team")
        self.league_id = self.context.get("league")
        self.t_type = self.context.get("tournament_type", "champions")
        
        from data.teams import TEAMS
        
        # Recolectar 32 equipos para el torneo (filtrando por región)
        pool = []
        target_region = "EU" if self.t_type == "champions" else "SA"
        eu_leagues = ["EN", "ES", "IT", "DE", "FR", "PT"]
        sa_leagues = ["BR", "AR", "CO"]
        
        for t in TEAMS:
            if t == self.player_team: continue
            lg = t.get("league", "EN")
            if target_region == "EU" and lg in eu_leagues:
                pool.append(t)
            elif target_region == "SA" and lg in sa_leagues:
                pool.append(t)
                
        random.shuffle(pool)
        while len(pool) < 31:
            pool.append(random.choice(pool))
            
        self.tournament_teams = [self.player_team] + pool[:31]
        random.shuffle(self.tournament_teams)
        self.bracket = []
        for i in range(0, 32, 2):
            self.bracket.append((self.tournament_teams[i], self.tournament_teams[i+1]))
            
        self.scorers = {}  # "Player Name": goals
        self.assisters = {}  # "Player Name": assists
        
        self.round_phase = "ro32"
        self.bracket_next_phase = []
        self.winner = None
        self.player_eliminated = False
        self.time = 0
        
        self.generate_fixtures()
        
        # UI
        try:
            self.font_title = pygame.font.SysFont("Impact", 42, bold=True)
            self.font_btn = pygame.font.SysFont("Arial", 22, bold=True)
            self.font_text = pygame.font.SysFont("Arial", 16)
            self.font_small = pygame.font.SysFont("Arial", 14)
            self.font_hint = pygame.font.SysFont("Arial", 14)
            self.font_section = pygame.font.SysFont("Arial", 18, bold=True)
        except:
            self.font_title = pygame.font.Font(None, 42)
            self.font_btn = pygame.font.Font(None, 22)
            self.font_text = pygame.font.Font(None, 16)
            self.font_small = pygame.font.Font(None, 14)
            self.font_hint = pygame.font.Font(None, 14)
            self.font_section = pygame.font.Font(None, 18)

    def generate_fixtures(self):
        self.matches = self.bracket

    def get_player_match(self):
        if self.player_eliminated:
            return None
        for m in self.matches:
            if self.player_team in m:
                return m
        return None

    def simulate_match(self, t1, t2):
        s1 = sum(t1["stats"].values()) / 4
        s2 = sum(t2["stats"].values()) / 4
        
        base_goals_1 = random.randint(0, 2)
        base_goals_2 = random.randint(0, 2)
        
        diff = s1 - s2
        if diff > 5: base_goals_1 += random.randint(0, 2)
        elif diff < -5: base_goals_2 += random.randint(0, 2)
        
        return base_goals_1, base_goals_2

    def _register_goals(self, team, goals):
        """Register random scorers and assisters for a team."""
        roster = team.get("roster", [{"name": "Jugador"}])
        attackers = [p for p in roster[:11] if p.get("pos") in ["ST", "LW", "RW", "CM", "CAM"]]
        if not attackers:
            attackers = roster[:11]
        
        for _ in range(goals):
            scorer = random.choice(attackers)["name"]
            self.scorers[scorer] = self.scorers.get(scorer, 0) + 1
            
            # 60% chance of an assist
            if random.random() < 0.6:
                possible = [p for p in roster[:11] if p["name"] != scorer]
                if possible:
                    assister = random.choice(possible)["name"]
                    self.assisters[assister] = self.assisters.get(assister, 0) + 1

    def advance_round(self, simulated_player_match_result=None):
        player_match = self.get_player_match()
        
        for m in self.matches:
            if m == player_match and simulated_player_match_result:
                g1, g2 = simulated_player_match_result
            elif m == player_match and not simulated_player_match_result:
                continue
            else:
                g1, g2 = self.simulate_match(m[0], m[1])
            
            self._register_goals(m[0], g1)
            self._register_goals(m[1], g2)
            
            # KO - must have a winner
            if g1 == g2:
                if random.random() < 0.5: g1 += 1
                else: g2 += 1
            
            winner = m[0] if g1 > g2 else m[1]
            loser = m[1] if winner == m[0] else m[0]
            
            if loser == self.player_team:
                self.player_eliminated = True
            
            self.bracket_next_phase.append(winner)

        # Transition Phase
        phases = ["ro32", "ro16", "qf", "sf", "final"]
        next_phases = ["ro16", "qf", "sf", "final", "finished"]
        idx = phases.index(self.round_phase) if self.round_phase in phases else -1
        
        if idx >= 0 and idx < len(next_phases):
            self.round_phase = next_phases[idx]
            if self.round_phase == "finished":
                self.winner = self.bracket_next_phase[0] if self.bracket_next_phase else None
            else:
                self._build_next_bracket()
            
        self.generate_fixtures()

    def _build_next_bracket(self):
        self.bracket = []
        for i in range(0, len(self.bracket_next_phase), 2):
            if i + 1 < len(self.bracket_next_phase):
                self.bracket.append((self.bracket_next_phase[i], self.bracket_next_phase[i+1]))
        self.bracket_next_phase = []

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.round_phase == "finished":
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        from scenes.main_menu import MainMenuScene
                        self.manager.set_scene(MainMenuScene)
                    return
                    
                if event.key == pygame.K_s:
                    pm = self.get_player_match()
                    if pm:
                        res = self.simulate_match(pm[0], pm[1])
                        self.advance_round(res)
                    else:
                        self.advance_round((0,0))
                elif event.key == pygame.K_RETURN:
                    pm = self.get_player_match()
                    if pm:
                        from scenes.tactics import TacticsScene
                        self.manager.shared_data["player_team"] = pm[0] if pm[0] == self.player_team else pm[1]
                        self.manager.shared_data["rival_team"] = pm[1] if pm[0] == self.player_team else pm[0]
                        self.manager.shared_data["tournament_context"] = self.context
                        self.manager.shared_data["tournament_hub_state"] = self._save_state()
                        self.manager.set_scene(TacticsScene)
                    else:
                        self.advance_round((0,0))
                elif event.key == pygame.K_ESCAPE:
                    from scenes.main_menu import MainMenuScene
                    self.manager.set_scene(MainMenuScene)

    def _save_state(self):
        """Save tournament state so MatchEndScene can restore it."""
        return {
            "context": self.context,
            "bracket": self.bracket,
            "bracket_next_phase": self.bracket_next_phase,
            "scorers": self.scorers,
            "assisters": self.assisters,
            "round_phase": self.round_phase,
            "tournament_teams": self.tournament_teams,
            "player_eliminated": self.player_eliminated,
            "winner": self.winner,
        }

    def _restore_state(self, state):
        """Restore tournament state from saved dict."""
        self.bracket = state["bracket"]
        self.bracket_next_phase = state["bracket_next_phase"]
        self.scorers = state["scorers"]
        self.assisters = state["assisters"]
        self.round_phase = state["round_phase"]
        self.tournament_teams = state["tournament_teams"]
        self.player_eliminated = state["player_eliminated"]
        self.winner = state["winner"]
        self.generate_fixtures()

    def update(self, dt):
        self.time += dt

    def draw(self, surface):
        # Background
        for y in range(HEIGHT):
            ratio = y / HEIGHT
            r = int(12 + ratio * 8)
            g = int(14 + ratio * 5)
            b = int(28 + ratio * 14)
            pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))
        
        round_names = {"ro32": "16vos de Final", "ro16": "Octavos de Final",
                       "qf": "Cuartos de Final", "sf": "Semifinales", "final": "GRAN FINAL"}
        
        if self.round_phase == "finished":
            self._draw_finished(surface)
            return
        
        # Title
        t_name = "Copa Champions" if self.t_type == "champions" else "Copa Libertadores"
        title = f"{t_name} — {round_names.get(self.round_phase, '')}"
        tsurf = self.font_title.render(title, True, UI_ACCENT)
        surface.blit(tsurf, (WIDTH//2 - tsurf.get_width()//2, 18))
        pygame.draw.line(surface, UI_ACCENT, (WIDTH//2 - 220, 58), (WIDTH//2 + 220, 58), 2)
        
        # ═══ LEFT PANEL: Matches ═══
        panel_left = pygame.Rect(30, 70, 440, HEIGHT - 130)
        pygame.draw.rect(surface, UI_CARD_BG, panel_left, border_radius=12)
        pygame.draw.rect(surface, (50, 55, 70), panel_left, 1, border_radius=12)
        
        header = self.font_section.render("PARTIDOS DE RONDA", True, UI_ACCENT)
        surface.blit(header, (45, 82))
        
        pm = self.get_player_match()
        my = 110
        for i, m in enumerate(self.matches):
            is_player_match = (m == pm)
            row_rect = pygame.Rect(40, my, 420, 28)
            
            if is_player_match:
                pygame.draw.rect(surface, (40, 80, 60), row_rect, border_radius=6)
                pygame.draw.rect(surface, UI_ACCENT, row_rect, 1, border_radius=6)
            elif i % 2 == 0:
                pygame.draw.rect(surface, (30, 33, 45), row_rect, border_radius=4)
            
            c1 = UI_ACCENT_ALT if m[0] == self.player_team else WHITE
            c2 = UI_ACCENT_ALT if m[1] == self.player_team else WHITE
            
            t1s = self.font_text.render(m[0]['name'], True, c1)
            vs = self.font_small.render(" vs ", True, UI_TEXT_DIM)
            t2s = self.font_text.render(m[1]['name'], True, c2)
            
            surface.blit(t1s, (48, my + 4))
            mid_x = 48 + t1s.get_width()
            surface.blit(vs, (mid_x, my + 5))
            surface.blit(t2s, (mid_x + vs.get_width(), my + 4))
            my += 32
        
        # ═══ RIGHT PANEL: Top Scorers & Assisters ═══
        panel_right = pygame.Rect(490, 70, WIDTH - 520, HEIGHT - 130)
        pygame.draw.rect(surface, UI_CARD_BG, panel_right, border_radius=12)
        pygame.draw.rect(surface, (50, 55, 70), panel_right, 1, border_radius=12)
        
        # Scorers
        sc_header = self.font_section.render("GOLEADORES", True, (255, 215, 0))
        surface.blit(sc_header, (505, 82))
        
        sorted_scorers = sorted(self.scorers.items(), key=lambda x: -x[1])[:8]
        sy = 108
        for rank, (name, goals) in enumerate(sorted_scorers, 1):
            color = (255, 215, 0) if rank == 1 else WHITE if rank <= 3 else UI_TEXT_DIM
            ns = self.font_text.render(f"{rank}. {name}", True, color)
            gs = self.font_text.render(f"{goals} gol{'es' if goals > 1 else ''}", True, color)
            surface.blit(ns, (510, sy))
            surface.blit(gs, (panel_right.right - gs.get_width() - 15, sy))
            sy += 24
        
        if not sorted_scorers:
            ns = self.font_small.render("Sin goles aún", True, UI_TEXT_DIM)
            surface.blit(ns, (510, sy))
        
        # Assisters
        sy += 20
        pygame.draw.line(surface, (50, 55, 70), (505, sy), (panel_right.right - 10, sy), 1)
        sy += 8
        as_header = self.font_section.render("🅰️ ASISTENTES", True, (100, 200, 255))
        surface.blit(as_header, (505, sy))
        sy += 26
        
        sorted_assisters = sorted(self.assisters.items(), key=lambda x: -x[1])[:6]
        for rank, (name, assists) in enumerate(sorted_assisters, 1):
            color = (100, 200, 255) if rank == 1 else WHITE if rank <= 3 else UI_TEXT_DIM
            ns = self.font_text.render(f"{rank}. {name}", True, color)
            asst = self.font_text.render(f"{assists} asist.", True, color)
            surface.blit(ns, (510, sy))
            surface.blit(asst, (panel_right.right - asst.get_width() - 15, sy))
            sy += 24
        
        if not sorted_assisters:
            ns = self.font_small.render("Sin asistencias aún", True, UI_TEXT_DIM)
            surface.blit(ns, (510, sy))
        
        # ═══ BOTTOM BAR ═══
        if self.player_eliminated:
            elim_msg = self.font_btn.render("Tu equipo fue eliminado. Puedes simular el resto del torneo.", True, (200, 80, 60))
            surface.blit(elim_msg, (WIDTH//2 - elim_msg.get_width()//2, HEIGHT - 100))
        
        btn_y = HEIGHT - 50
        btn_sim = self.font_btn.render("[S] SIMULAR RONDA", True, (180, 180, 200))
        surface.blit(btn_sim, (50, btn_y))
        
        if pm:
            btn_play = self.font_btn.render("[ENTER] JUGAR TU PARTIDO", True, UI_ACCENT)
            surface.blit(btn_play, (WIDTH - btn_play.get_width() - 50, btn_y))
        
        hint = self.font_hint.render("ESC: Salir del Torneo", True, UI_TEXT_DIM)
        surface.blit(hint, (WIDTH//2 - hint.get_width()//2, btn_y + 4))

    def _draw_finished(self, surface):
        """Draw the championship finished screen."""
        is_player_champion = (self.winner == self.player_team)
        
        # Trophy animation
        pulse = (math.sin(self.time * 3) + 1) / 2
        
        if is_player_champion:
            # ═══ PLAYER WON ═══
            # Golden background glow
            glow_r = int(100 + pulse * 50)
            for y in range(HEIGHT):
                ratio = y / HEIGHT
                r = int(25 + ratio * glow_r * 0.3)
                g = int(20 + ratio * glow_r * 0.25)
                b = int(5 + ratio * 8)
                pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))
            
            # Big trophy
            tx, ty = WIDTH // 2, 200
            gold = (int(200 + 55 * pulse), int(175 + 50 * pulse), 0)
            
            # Cup body
            cup_w = 80 + int(10 * pulse)
            pygame.draw.polygon(surface, gold, [
                (tx - cup_w//2, ty - 40), (tx + cup_w//2, ty - 40),
                (tx + cup_w//3, ty + 30), (tx - cup_w//3, ty + 30)])
            # Handles
            pygame.draw.arc(surface, gold, (tx - cup_w//2 - 20, ty - 40, 30, 40), -1.5, 1.5, 4)
            pygame.draw.arc(surface, gold, (tx + cup_w//2 - 10, ty - 40, 30, 40), 1.5, 4.5, 4)
            # Stem
            pygame.draw.rect(surface, (160, 130, 0), (tx - 8, ty + 30, 16, 30))
            # Base
            pygame.draw.rect(surface, gold, (tx - 40, ty + 60, 80, 14), border_radius=4)
            
            # Confetti particles
            for i in range(30):
                cx = (i * 97 + int(self.time * 40 * (i % 3 + 1))) % WIDTH
                cy = (i * 53 + int(self.time * 60 * (i % 2 + 1))) % HEIGHT
                colors = [(255, 215, 0), (255, 50, 50), (50, 200, 255), (255, 255, 255), (0, 255, 100)]
                cc = colors[i % len(colors)]
                pygame.draw.rect(surface, cc, (cx, cy, 6, 4))
            
            title = self.font_title.render("¡CAMPEONES!", True, gold)
            surface.blit(title, (WIDTH//2 - title.get_width()//2, ty + 100))
            
            sub = self.font_btn.render(f"¡{self.winner['name']} ha conquistado la copa!", True, WHITE)
            surface.blit(sub, (WIDTH//2 - sub.get_width()//2, ty + 150))
            
        else:
            # ═══ AI WON - News bulletin ═══
            for y in range(HEIGHT):
                ratio = y / HEIGHT
                r = int(15 + ratio * 8)
                g = int(15 + ratio * 5)
                b = int(30 + ratio * 15)
                pygame.draw.line(surface, (r, g, b), (0, y), (WIDTH, y))
            
            # News card
            card_w = 700
            card_h = 350
            card_rect = pygame.Rect(WIDTH//2 - card_w//2, 100, card_w, card_h)
            pygame.draw.rect(surface, UI_CARD_BG, card_rect, border_radius=16)
            pygame.draw.rect(surface, UI_ACCENT, card_rect, 2, border_radius=16)
            
            # Breaking news banner
            banner_rect = pygame.Rect(card_rect.left, card_rect.top, card_w, 50)
            pygame.draw.rect(surface, (180, 30, 30), banner_rect, border_radius=16)
            pygame.draw.rect(surface, (180, 30, 30), pygame.Rect(card_rect.left, card_rect.top + 25, card_w, 25))
            
            breaking = self.font_title.render("NOTICIAS DE ÚLTIMA HORA", True, WHITE)
            surface.blit(breaking, (WIDTH//2 - breaking.get_width()//2, card_rect.top + 6))
            
            # Trophy icon
            gold = (255, 215, 0)
            tx = WIDTH//2
            ty = card_rect.top + 130
            pygame.draw.polygon(surface, gold, [
                (tx - 25, ty - 20), (tx + 25, ty - 20),
                (tx + 15, ty + 10), (tx - 15, ty + 10)])
            pygame.draw.rect(surface, (160, 130, 0), (tx - 5, ty + 10, 10, 15))
            pygame.draw.rect(surface, gold, (tx - 20, ty + 25, 40, 8), border_radius=3)
            
            # Champion name
            t_name = "Copa Champions" if self.t_type == "champions" else "Copa Libertadores"
            champ = self.font_title.render(f"{self.winner['name']}", True, UI_ACCENT)
            surface.blit(champ, (WIDTH//2 - champ.get_width()//2, ty + 50))
            
            wins_text = self.font_btn.render(f"se consagra campeón de la {t_name}", True, UI_TEXT)
            surface.blit(wins_text, (WIDTH//2 - wins_text.get_width()//2, ty + 95))
            
            detail = self.font_text.render("Tu equipo no logró avanzar en esta edición.", True, UI_TEXT_DIM)
            surface.blit(detail, (WIDTH//2 - detail.get_width()//2, ty + 130))
        
        # ═══ CENTERED SCORERS TABLE (below) ═══
        table_y = HEIGHT - 200
        pygame.draw.line(surface, UI_ACCENT, (100, table_y - 10), (WIDTH - 100, table_y - 10), 1)
        
        # Top Scorer
        sorted_scorers = sorted(self.scorers.items(), key=lambda x: -x[1])[:5]
        sc_title = self.font_section.render("Máx. Goleador", True, (255, 215, 0))
        surface.blit(sc_title, (120, table_y))
        for i, (name, goals) in enumerate(sorted_scorers):
            color = (255, 215, 0) if i == 0 else WHITE
            s = self.font_text.render(f"{i+1}. {name} — {goals} gol{'es' if goals>1 else ''}", True, color)
            surface.blit(s, (130, table_y + 24 + i * 22))
        
        # Top Assister
        sorted_assisters = sorted(self.assisters.items(), key=lambda x: -x[1])[:5]
        as_title = self.font_section.render("Máx. Asistente", True, (100, 200, 255))
        surface.blit(as_title, (WIDTH//2 + 60, table_y))
        for i, (name, assists) in enumerate(sorted_assisters):
            color = (100, 200, 255) if i == 0 else WHITE
            s = self.font_text.render(f"{i+1}. {name} — {assists} asist.", True, color)
            surface.blit(s, (WIDTH//2 + 70, table_y + 24 + i * 22))
        
        # Exit hint
        if self.time > 1.0:
            pulse_h = (math.sin(self.time * 3) + 1) / 2
            hint = self.font_btn.render("ENTER para volver al menú", True,
                                         (int(120 + pulse_h * 80),) * 3)
            surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 35))
