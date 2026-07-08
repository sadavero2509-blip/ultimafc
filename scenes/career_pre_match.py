import pygame
import copy
from settings import *
from data.career_manager import career_manager

class CareerPreMatchScene:
    """Pre-match screen: shows matchup info and lets player choose PLAY or SIMULATE."""
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        
        self.pm, self.evt = career_manager.get_player_match_today()
        if not self.pm:
            from scenes.career_hub import CareerHubScene
            self.manager.set_scene(CareerHubScene)
            return
        
        self.t1_short, self.t2_short = self.pm
        self.tour_name = self.evt.get("type", "PARTIDO") if self.evt else "AMISTOSO"
        
        self.team1 = career_manager.get_team_by_short(self.t1_short)
        self.team2 = career_manager.get_team_by_short(self.t2_short)
        
        self.r1 = career_manager.rosters.get(self.t1_short, [])
        self.r2 = career_manager.rosters.get(self.t2_short, [])
        
        # Which side is the player?
        pshort = career_manager.player_team["short"]
        self.player_is_left = (self.t1_short == pshort)
        
        # Pre-calculate starter status
        r = self.r1 if self.t1_short == pshort else self.r2
        t_check = self._build_team_dict(career_manager.player_team, r)
        self.is_starter = any(p.get("is_user_player") for p in t_check.get("roster", [])[:11])
        
        self.sel = 0  # 0 = JUGAR, 1 = SIMULAR
        self.time = 0
        
        try:
            self.font_title = pygame.font.SysFont("Impact", 44)
            self.font_team = pygame.font.SysFont("Arial", 30, bold=True)
            self.font_vs = pygame.font.SysFont("Impact", 60)
            self.font_btn = pygame.font.SysFont("Arial", 24, bold=True)
            self.font_text = pygame.font.SysFont("Arial", 18)
            self.font_hint = pygame.font.SysFont("Arial", 14)
        except:
            self.font_title = pygame.font.Font(None, 44)
            self.font_team = pygame.font.Font(None, 30)
            self.font_vs = pygame.font.Font(None, 60)
            self.font_btn = pygame.font.Font(None, 24)
            self.font_text = pygame.font.Font(None, 18)
            self.font_hint = pygame.font.Font(None, 14)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a) or event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.sel = 1 - self.sel
                elif event.key == pygame.K_RETURN:
                    # Default state
                    is_avail = True
                    conf = career_manager.career_stats.get("coach_confidence", 40)
                    
                    pshort = career_manager.player_team["short"]
                    r = self.r1 if self.t1_short == pshort else self.r2
                    
                    if career_manager.mode == "player" and self.sel == 0:
                        cp = career_manager.career_player
                        real_p = next((p for p in r if p.get("is_user_player") or p["name"] == cp["name"]), cp)
                        # Check availability
                        if real_p and (real_p.get("injured_until") or real_p.get("suspension", 0) > 0):
                            is_avail = False
                        elif conf < 30:
                            is_avail = False
                        self.manager.shared_data["user_is_sub"] = not self.is_starter
                            
                    if self.sel == 0:
                        if is_avail:
                            self._start_playable_match()
                    else:
                        self._start_simulation()
                elif event.key == pygame.K_ESCAPE:
                    from scenes.career_hub import CareerHubScene
                    self.manager.set_scene(CareerHubScene)

    def _build_team_dict(self, team_obj, roster):
        """Build a team dict compatible with MatchScene expectations."""
        t = copy.deepcopy(team_obj)
        pshort = career_manager.player_team["short"]
        
        # Sort roster by OVR initially
        sorted_roster = sorted(roster, key=lambda x: x.get("ovr", 70), reverse=True)
        
        if career_manager.mode == "player" and team_obj["short"] == pshort:
            conf = career_manager.career_stats.get("coach_confidence", 40)
            cp = career_manager.career_player
            real_cp = next((p for p in roster if p.get("is_user_player") or p["name"] == cp["name"]), None)
            
            if real_cp:
                is_avail = not (real_cp.get("injured_until") or real_cp.get("suspension", 0) > 0)
                if conf >= 50 and is_avail:
                    sorted_roster = [p for p in sorted_roster if p["name"] != cp["name"]]
                    sorted_roster.insert(0, real_cp)
                elif conf >= 30 and is_avail:
                    sorted_roster = [p for p in sorted_roster if p["name"] != cp["name"]]
                    sorted_roster.insert(11, real_cp)
                else:
                    # NOT CONVOCADO / INJURED: remove from match squad entirely
                    sorted_roster = [p for p in sorted_roster if p["name"] != cp["name"]]
            
        t["roster"] = sorted_roster
        return t
    
    def _start_playable_match(self):
        """Launch the real playable match."""
        left_team = self._build_team_dict(self.team1, self.r1)
        right_team = self._build_team_dict(self.team2, self.r2)
        
        self.manager.shared_data["career_match_state"] = {
            "match": self.pm,
            "event": self.evt,
            "player_is_left": self.player_is_left
        }
        
        if self.player_is_left:
            self.manager.shared_data["player_team"] = left_team
            self.manager.shared_data["rival_team"] = right_team
        else:
            self.manager.shared_data["player_team"] = right_team
            self.manager.shared_data["rival_team"] = left_team
            self.manager.shared_data["career_match_state"]["swapped"] = True
        
        self.manager.shared_data["game_mode"] = "career"
        self.manager.shared_data["starters"] = self.manager.shared_data["player_team"]["roster"]
        self.manager.shared_data["formation"] = "4-3-3"
        self.manager.shared_data["kickoff_team"] = "left"
        self.manager.shared_data["difficulty"] = getattr(career_manager, "difficulty", 5)
        
        from scenes.pre_match_presentation import PreMatchPresentationScene
        self.manager.transition_to(PreMatchPresentationScene)

    def _start_simulation(self):
        from scenes.career_match_sim import CareerMatchSimScene
        self.manager.set_scene(CareerMatchSimScene)

    def update(self, dt):
        self.time += dt

    def draw(self, surface):
        surface.fill((12, 16, 24))
        
        colors = {
            "CHAMPIONS": (255, 215, 0),
            "EUROPA_LEAGUE": (255, 140, 0),
            "CONFERENCE": (50, 205, 50),
            "LIBERTADORES": (173, 255, 47),
            "SUDAMERICANA": (0, 191, 255)
        }
        tc = (0, 200, 150)
        for comp_name, color in colors.items():
            if comp_name in self.tour_name:
                tc = color
                break
        title = self.font_title.render(f"🏆 {self.tour_name}", True, tc)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 30))
        
        d = career_manager.current_date
        if d:
            months = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
            ds = self.font_text.render(f"{d.day} de {months[d.month-1]} {d.year}", True, UI_TEXT_DIM)
            surface.blit(ds, (WIDTH//2 - ds.get_width()//2, 75))
        
        cx = WIDTH // 2
        from data.teams import draw_badge
        draw_badge(surface, self.team1, cx - 200, 200, size=80)
        n1 = self.font_team.render(self.team1["name"], True, WHITE)
        surface.blit(n1, (cx - 200 - n1.get_width()//2, 300))
        
        vs = self.font_vs.render("VS", True, UI_ACCENT_ALT)
        surface.blit(vs, (cx - vs.get_width()//2, 190))
        
        draw_badge(surface, self.team2, cx + 200, 200, size=80)
        n2 = self.font_team.render(self.team2["name"], True, WHITE)
        surface.blit(n2, (cx + 200 - n2.get_width()//2, 300))
        
        y = 450
        is_p_avail = True
        p_status_msg = ""
        pshort = career_manager.player_team["short"]
        r = career_manager.rosters.get(pshort, [])
        cp = career_manager.career_player
        real_p = next((p for p in r if p["name"] == cp["name"]), cp)
        conf = career_manager.career_stats.get("coach_confidence", 40)
        
        if real_p.get("injured_until"):
            is_p_avail = False
            p_status_msg = "No disponible: Lesión"
        elif real_p.get("suspension", 0) > 0:
            is_p_avail = False
            p_status_msg = "No disponible: Sanción"
        elif conf < 30:
            is_p_avail = False
            p_status_msg = "No convocado: Falta confianza"
        elif conf < 50:
            p_status_msg = "¡ESTÁS EN LA BANCA!"

        opts = [("🎮 JUGAR PARTIDO", (0, 180, 120)), ("⏩ SIMULAR", (100, 100, 140))]
        for i, (label, base_c) in enumerate(opts):
            rect = pygame.Rect(cx - 270 + i * 280, y, 260, 60)
            is_sel = (self.sel == i)
            
            can_select = True
            if i == 0:
                if not is_p_avail:
                    can_select = False
                    base_c = (60, 60, 60)
                
                final_label = label
                if is_p_avail:
                    final_label += " [TITULAR]" if self.is_starter else " [SUPLENTE]"
                else:
                    final_label = p_status_msg if len(p_status_msg) < 18 else "NO DISPONIBLE"
            else:
                final_label = label

            if is_sel:
                c = tuple(min(255, v + 40) for v in base_c)
                pygame.draw.rect(surface, c, rect, border_radius=10)
                pygame.draw.rect(surface, WHITE if can_select else (150, 150, 150), rect, 3, border_radius=10)
            else:
                pygame.draw.rect(surface, base_c, rect, border_radius=10)
            
            ls = self.font_btn.render(final_label, True, WHITE if can_select else (180, 180, 180))
            surface.blit(ls, (rect.centerx - ls.get_width()//2, rect.centery - ls.get_height()//2))
        
        hint = self.font_hint.render("◀ ▶ Seleccionar  ·  ENTER Confirmar  ·  ESC Cancelar", True, UI_TEXT_DIM)
        surface.blit(hint, (cx - hint.get_width()//2, HEIGHT - 30))
