import pygame
import math
import random
from settings import *
from data.career_manager import career_manager
from data.teams import TEAMS

class CareerDestinationsScene:
    """Scene to browse leagues/teams and suggest transfer destinations to agent."""
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        self.time = 0
        self.msg = ""
        self.msg_timer = 0
        
        # View mode: "leagues" or "teams"
        self.view = "leagues"
        
        # League browsing
        self.leagues = ["EN", "ES", "IT", "DE", "FR", "PT", "TR", "BR", "AR", "CO", "US", "JP", "AF"]
        self.league_names = {
            "EN": "Premier League", "ES": "La Liga", "IT": "Serie A", "DE": "Bundesliga",
            "FR": "Ligue 1", "PT": "Primeira Liga", "BR": "Brasileirão", "AR": "Liga Profesional",
            "CO": "Liga BetPlay", "US": "MLS", "JP": "J-League", "AF": "African League"
        }
        self.lg_idx = 0
        
        # Team browsing (populated when entering a league)
        self.teams_in_league = []
        self.team_idx = 0
        self.scroll_offset = 0
        
        # Current suggestions stored in career_manager
        self.suggestions = getattr(career_manager, 'agent_suggestions', [])
        
        # Player info
        self.player_ovr = career_manager.career_player["ovr"] if career_manager.career_player else 60
        self.player_team = career_manager.player_team["short"] if career_manager.player_team else ""
        self.agent_level = career_manager.agent.get("level", 0)
        
        try:
            self.font_title = pygame.font.SysFont("Impact", 40)
            self.font_sub = pygame.font.SysFont("Arial", 24, bold=True)
            self.font_text = pygame.font.SysFont("Arial", 18)
            self.font_bold = pygame.font.SysFont("Arial", 18, bold=True)
            self.font_hint = pygame.font.SysFont("Arial", 14)
            self.font_small = pygame.font.SysFont("Arial", 13)
        except:
            self.font_title = pygame.font.Font(None, 40)
            self.font_sub = pygame.font.Font(None, 24)
            self.font_text = pygame.font.Font(None, 18)
            self.font_bold = pygame.font.Font(None, 18)
            self.font_hint = pygame.font.Font(None, 14)
            self.font_small = pygame.font.Font(None, 13)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.view == "leagues":
                    self._handle_leagues(event)
                elif self.view == "teams":
                    self._handle_teams(event)

    def _handle_leagues(self, event):
        if event.key in (pygame.K_UP, pygame.K_w):
            self.lg_idx = (self.lg_idx - 1) % len(self.leagues)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.lg_idx = (self.lg_idx + 1) % len(self.leagues)
        elif event.key == pygame.K_RETURN:
            self._enter_league()
        elif event.key == pygame.K_TAB:
            # Suggest entire league to agent
            self._suggest_league()
        elif event.key == pygame.K_ESCAPE:
            from scenes.career_hub import CareerHubScene
            self.manager.set_scene(CareerHubScene)

    def _handle_teams(self, event):
        if event.key in (pygame.K_UP, pygame.K_w):
            self.team_idx = max(0, self.team_idx - 1)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.team_idx = min(len(self.teams_in_league) - 1, self.team_idx + 1)
        elif event.key == pygame.K_RETURN:
            # Suggest specific team to agent
            self._suggest_team()
        elif event.key == pygame.K_ESCAPE:
            self.view = "leagues"
            self.team_idx = 0

    def _enter_league(self):
        lg = self.leagues[self.lg_idx]
        self.teams_in_league = [t for t in TEAMS if t.get("league") == lg]
        # Sort by OVR descending
        for t in self.teams_in_league:
            t["_ovr"] = career_manager.get_team_ovr(t["short"])
        self.teams_in_league.sort(key=lambda t: t["_ovr"], reverse=True)
        self.team_idx = 0
        self.view = "teams"

    def _suggest_league(self):
        if self.agent_level < 1:
            self._set_msg("Necesitas un agente para sugerir destinos.")
            return
        lg = self.leagues[self.lg_idx]
        lg_name = self.league_names.get(lg, lg)
        
        # Check if already suggested
        if not hasattr(career_manager, 'agent_suggestions'):
            career_manager.agent_suggestions = []
        
        if any(s.get("league") == lg and not s.get("team") for s in career_manager.agent_suggestions):
            self._set_msg(f"Ya sugeriste la {lg_name} a tu agente.")
            return
        
        if len(career_manager.agent_suggestions) >= 3:
            self._set_msg("Tu agente solo puede gestionar 3 sugerencias a la vez.")
            return
            
        career_manager.agent_suggestions.append({
            "league": lg,
            "league_name": lg_name,
            "team": None,
            "date": career_manager.current_date.isoformat()
        })
        self.suggestions = career_manager.agent_suggestions
        career_manager.add_email("agent", f"Destino: {lg_name}",
            f"Recibido, jefe. Voy a mover hilos en la {lg_name}. "
            f"Si hay un club que se ajuste a tu perfil, te lo haré saber.")
        
        # Add rumor chance
        if random.random() < 0.4:
            career_manager.add_rumor(lg_name, importance=1)
            
        self._set_msg(f"Sugerencia enviada: {lg_name}")

    def _suggest_team(self):
        if self.agent_level < 1:
            self._set_msg("Necesitas un agente para sugerir destinos.")
            return
        if not self.teams_in_league:
            return
        
        team = self.teams_in_league[self.team_idx]
        
        if team["short"] == self.player_team:
            self._set_msg("¡Ese es tu club actual!")
            return
            
        if not hasattr(career_manager, 'agent_suggestions'):
            career_manager.agent_suggestions = []
        
        if any(s.get("team") == team["short"] for s in career_manager.agent_suggestions):
            self._set_msg(f"Ya sugeriste {team['name']} a tu agente.")
            return

        if len(career_manager.agent_suggestions) >= 3:
            self._set_msg("Tu agente solo puede gestionar 3 sugerencias a la vez.")
            return
        
        team_ovr = team.get("_ovr", career_manager.get_team_ovr(team["short"]))
        
        # Feasibility check
        diff = team_ovr - self.player_ovr
        if diff > 15 and self.agent_level < 3:
            feasibility = "Muy difícil"
        elif diff > 8:
            feasibility = "Complicado"
        elif diff > 0:
            feasibility = "Posible"
        else:
            feasibility = "Muy probable"
        
        career_manager.agent_suggestions.append({
            "league": team.get("league"),
            "league_name": self.league_names.get(team.get("league", ""), ""),
            "team": team["short"],
            "team_name": team["name"],
            "feasibility": feasibility,
            "date": career_manager.current_date.isoformat()
        })
        self.suggestions = career_manager.agent_suggestions
        career_manager.add_email("agent", f"Destino: {team['name']}",
            f"Interesante elección. Voy a contactar al {team['name']}. "
            f"Mi valoración: {feasibility}. Te mantendré informado.")
        
        # High rumor chance for specific team suggestion
        if random.random() < 0.7:
            career_manager.add_rumor(team["name"], importance=2)
            
        self._set_msg(f"Sugerencia enviada: {team['name']} ({feasibility})")

    def _set_msg(self, text):
        self.msg = text
        self.msg_timer = 3.0

    def update(self, dt):
        self.time += dt
        if self.msg_timer > 0:
            self.msg_timer -= dt

    def draw(self, surface):
        surface.fill((15, 20, 30))
        
        # Header
        header_rect = pygame.Rect(0, 0, WIDTH, 100)
        pygame.draw.rect(surface, (25, 30, 45), header_rect)
        pygame.draw.line(surface, UI_ACCENT, (0, 100), (WIDTH, 100), 3)
        
        title = self.font_title.render("🌍 EXPLORAR DESTINOS", True, UI_ACCENT)
        surface.blit(title, (40, 20))
        
        # Agent info
        agent_name = career_manager.agent.get("name", "Ninguno")
        sugg_count = len(getattr(career_manager, 'agent_suggestions', []))
        agent_txt = self.font_text.render(f"Agente: {agent_name}  |  Sugerencias activas: {sugg_count}/3", True, UI_TEXT_DIM)
        surface.blit(agent_txt, (40, 65))
        
        if self.view == "leagues":
            self._draw_leagues(surface)
        elif self.view == "teams":
            self._draw_teams(surface)
        
        # Active Suggestions Panel (right side)
        self._draw_suggestions_panel(surface)
        
        # Message
        if self.msg_timer > 0:
            m_surf = self.font_bold.render(self.msg, True, UI_ACCENT)
            surface.blit(m_surf, (WIDTH//2 - m_surf.get_width()//2, HEIGHT - 70))
        
        # Hint
        if self.view == "leagues":
            hint = "↑↓ Navegar  ·  ENTER Ver equipos  ·  TAB Sugerir liga  ·  ESC Volver"
        else:
            hint = "↑↓ Navegar  ·  ENTER Sugerir equipo  ·  ESC Volver a ligas"
        h_surf = self.font_hint.render(hint, True, UI_TEXT_DIM)
        surface.blit(h_surf, (WIDTH//2 - h_surf.get_width()//2, HEIGHT - 30))

    def _draw_leagues(self, surface):
        lbl = self.font_sub.render("SELECCIONA UNA LIGA", True, WHITE)
        surface.blit(lbl, (40, 120))
        
        start_y = 170
        max_visible = 8
        
        for i, lg in enumerate(self.leagues):
            if i >= max_visible:
                break
            is_sel = (self.lg_idx == i)
            rect = pygame.Rect(40, start_y + i * 55, WIDTH // 2 - 80, 48)
            
            bg = UI_CARD_HOVER if is_sel else UI_CARD_BG
            pygame.draw.rect(surface, bg, rect, border_radius=8)
            if is_sel:
                pulse = (math.sin(self.time * 4) + 1) / 2
                bc = (int(pulse * 80), int(180 + pulse * 75), int(200 + pulse * 55))
                pygame.draw.rect(surface, bc, rect, 2, border_radius=8)
            else:
                pygame.draw.rect(surface, (50, 55, 70), rect, 1, border_radius=8)
            
            name = self.league_names.get(lg, lg)
            n_surf = self.font_bold.render(name, True, WHITE if is_sel else UI_TEXT_DIM)
            surface.blit(n_surf, (rect.left + 20, rect.centery - n_surf.get_height()//2))
            
            # Team count
            t_count = len([t for t in TEAMS if t.get("league") == lg])
            tc_surf = self.font_small.render(f"{t_count} equipos", True, (120, 120, 140))
            surface.blit(tc_surf, (rect.right - tc_surf.get_width() - 20, rect.centery - tc_surf.get_height()//2))

    def _draw_teams(self, surface):
        lg = self.leagues[self.lg_idx]
        lg_name = self.league_names.get(lg, lg)
        lbl = self.font_sub.render(f"EQUIPOS: {lg_name}", True, WHITE)
        surface.blit(lbl, (40, 120))
        
        start_y = 170
        max_visible = 9
        
        # Scroll
        if self.team_idx >= self.scroll_offset + max_visible:
            self.scroll_offset = self.team_idx - max_visible + 1
        elif self.team_idx < self.scroll_offset:
            self.scroll_offset = self.team_idx
        
        for draw_i in range(max_visible):
            i = draw_i + self.scroll_offset
            if i >= len(self.teams_in_league):
                break
            
            t = self.teams_in_league[i]
            is_sel = (self.team_idx == i)
            is_current = (t["short"] == self.player_team)
            rect = pygame.Rect(40, start_y + draw_i * 52, WIDTH // 2 - 80, 46)
            
            if is_current:
                bg = (40, 50, 35)
            elif is_sel:
                bg = UI_CARD_HOVER
            else:
                bg = UI_CARD_BG
            pygame.draw.rect(surface, bg, rect, border_radius=8)
            
            if is_sel:
                pygame.draw.rect(surface, UI_ACCENT, rect, 2, border_radius=8)
            elif is_current:
                pygame.draw.rect(surface, (100, 200, 100), rect, 1, border_radius=8)
            else:
                pygame.draw.rect(surface, (50, 55, 70), rect, 1, border_radius=8)
            
            # Badge
            from data.teams import draw_badge
            draw_badge(surface, t, rect.left + 30, rect.centery, size=18)
            
            # Name
            name_col = (100, 255, 100) if is_current else (WHITE if is_sel else UI_TEXT_DIM)
            n_surf = self.font_bold.render(t["name"], True, name_col)
            surface.blit(n_surf, (rect.left + 55, rect.centery - n_surf.get_height()//2))
            
            # OVR
            ovr = t.get("_ovr", career_manager.get_team_ovr(t["short"]))
            ovr_col = (100, 255, 100) if ovr >= 80 else (255, 200, 80) if ovr >= 70 else UI_TEXT_DIM
            o_surf = self.font_bold.render(f"OVR {ovr}", True, ovr_col)
            surface.blit(o_surf, (rect.right - o_surf.get_width() - 20, rect.centery - o_surf.get_height()//2))
            
            if is_current:
                tag = self.font_small.render("TU CLUB", True, (100, 255, 100))
                surface.blit(tag, (rect.right - 130, rect.centery - tag.get_height()//2))
        
        # Team detail card for selected team
        if self.teams_in_league:
            self._draw_team_detail(surface, self.teams_in_league[self.team_idx])

    def _draw_team_detail(self, surface, team):
        """Draw a detail card for the selected team."""
        card_x = WIDTH // 2 - 20
        card_y = 120
        card_w = WIDTH // 2 - 20
        card_h = 280
        
        card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
        pygame.draw.rect(surface, (25, 30, 50), card_rect, border_radius=12)
        pygame.draw.rect(surface, (60, 70, 100), card_rect, 2, border_radius=12)
        
        cx = card_rect.centerx
        py = card_rect.top + 20
        
        # Badge
        from data.teams import draw_badge
        draw_badge(surface, team, cx, py + 30, size=50)
        py += 80
        
        # Name
        n = self.font_sub.render(team["name"], True, WHITE)
        surface.blit(n, (cx - n.get_width()//2, py))
        py += 35
        
        # OVR
        ovr = team.get("_ovr", career_manager.get_team_ovr(team["short"]))
        o = self.font_bold.render(f"Media: {ovr}", True, UI_ACCENT_ALT)
        surface.blit(o, (cx - o.get_width()//2, py))
        py += 30
        
        # Feasibility analysis
        diff = ovr - self.player_ovr
        if diff > 15:
            feas_text = "INALCANZABLE"
            feas_col = (255, 60, 60)
        elif diff > 8:
            feas_text = "MUY DIFÍCIL"
            feas_col = (255, 150, 80)
        elif diff > 3:
            feas_text = "COMPLICADO"
            feas_col = (255, 200, 80)
        elif diff > -5:
            feas_text = "POSIBLE"
            feas_col = (100, 255, 100)
        else:
            feas_text = "MUY PROBABLE"
            feas_col = (80, 200, 255)
        
        f = self.font_bold.render(f"Viabilidad: {feas_text}", True, feas_col)
        surface.blit(f, (cx - f.get_width()//2, py))
        py += 30
        
        # Player OVR comparison
        cmp = self.font_text.render(f"Tu OVR: {self.player_ovr} vs Equipo: {ovr}", True, UI_TEXT_DIM)
        surface.blit(cmp, (cx - cmp.get_width()//2, py))

    def _draw_suggestions_panel(self, surface):
        """Draw panel showing current active suggestions."""
        panel_x = WIDTH // 2 - 20
        panel_y = 420
        panel_w = WIDTH // 2 - 20
        panel_h = HEIGHT - 420 - 80
        
        if self.view == "leagues":
            panel_x = WIDTH // 2
            panel_y = 120
            panel_h = HEIGHT - 120 - 80
        
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        pygame.draw.rect(surface, (20, 25, 40), panel_rect, border_radius=10)
        pygame.draw.rect(surface, (50, 60, 80), panel_rect, 1, border_radius=10)
        
        px = panel_rect.left + 15
        py = panel_rect.top + 15
        
        lbl = self.font_bold.render("📋 DESTINOS SUGERIDOS AL AGENTE", True, (200, 200, 255))
        surface.blit(lbl, (px, py))
        py += 35
        
        suggestions = getattr(career_manager, 'agent_suggestions', [])
        
        if not suggestions:
            empty = self.font_text.render("Sin sugerencias activas.", True, UI_TEXT_DIM)
            surface.blit(empty, (px, py))
            py += 25
            tip = self.font_small.render("Usa TAB en ligas o ENTER en equipos", True, (100, 100, 120))
            surface.blit(tip, (px, py))
        else:
            for i, s in enumerate(suggestions):
                sy = py + i * 60
                s_rect = pygame.Rect(px, sy, panel_w - 30, 50)
                pygame.draw.rect(surface, (30, 35, 55), s_rect, border_radius=6)
                
                if s.get("team"):
                    icon = "🏟️"
                    name = s.get("team_name", s["team"])
                    feas = s.get("feasibility", "")
                    detail = f"{s.get('league_name', '')} | {feas}"
                else:
                    icon = "🌍"
                    name = s.get("league_name", s.get("league", ""))
                    detail = "Liga completa"
                
                n_surf = self.font_bold.render(f"{icon} {name}", True, WHITE)
                surface.blit(n_surf, (s_rect.left + 10, s_rect.top + 8))
                
                d_surf = self.font_small.render(detail, True, UI_TEXT_DIM)
                surface.blit(d_surf, (s_rect.left + 10, s_rect.top + 30))
