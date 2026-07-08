import pygame
import random
from settings import *
from data.career_manager import career_manager

class CareerMatchSimScene:
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        
        self.pm, self.evt = career_manager.get_player_match_today()
        if not self.pm:
            # Error fallback
            from scenes.career_hub import CareerHubScene
            self.manager.set_scene(CareerHubScene)
            return
            
        self.t1_short, self.t2_short = self.pm
        self.tour_name = f"🏆 {self.evt.get('type')}" if self.evt else "PARTIDO AMISTOSO"
        
        self.team1 = career_manager.get_team_by_short(self.t1_short)
        self.team2 = career_manager.get_team_by_short(self.t2_short)
        
        self.r1 = career_manager.rosters.get(self.t1_short, [])
        self.r2 = career_manager.rosters.get(self.t2_short, [])
        
        # Sort rosters by OVR
        self.r1 = sorted(self.r1, key=lambda x: x.get("ovr", 70), reverse=True)
        self.r2 = sorted(self.r2, key=lambda x: x.get("ovr", 70), reverse=True)
        
        # Position user player in roster according to coach confidence
        pshort = career_manager.player_team["short"] if career_manager.player_team else ""
        if career_manager.mode == "player":
            for team_short, roster in [(self.t1_short, self.r1), (self.t2_short, self.r2)]:
                if team_short == pshort:
                    cp = career_manager.career_player
                    real_cp = next((p for p in roster if p.get("is_user_player") or p["name"] == cp["name"]), None)
                    if real_cp:
                        conf = career_manager.career_stats.get("coach_confidence", 40)
                        is_avail = not (real_cp.get("injured_until") or real_cp.get("suspension", 0) > 0)
                        if conf >= 50 and is_avail:
                            # Starter: force at index 0
                            roster.remove(real_cp)
                            roster.insert(0, real_cp)
                        elif conf >= 30 and is_avail:
                            # Bench/Reserve: force at index 11 (first sub)
                            roster.remove(real_cp)
                            roster.insert(11, real_cp)
                        else:
                            # NOT CONVOCADO / INJURED: remove from simulation roster completely
                            roster.remove(real_cp)
        
        # Calculate strengths
        s1 = career_manager.get_team_ovr(self.t1_short)
        s2 = career_manager.get_team_ovr(self.t2_short)
        
        # Determine total goals
        g1, g2 = random.randint(0, 2), random.randint(0, 2)
        if s1 - s2 > 4: g1 += random.randint(0, 2)
        elif s2 - s1 > 4: g2 += random.randint(0, 2)
        if random.random() < 0.3: g1 += 1 # Home advantage
        
        self.final_g1 = g1
        self.final_g2 = g2
        
        self.events = self._generate_events(g1, g2)
        
        self.current_g1 = 0
        self.current_g2 = 0
        
        self.time = 0
        self.event_idx = 0
        self.event_timer = 0
        
        self.finished = False
        self.logs_display = []
        
        try:
            self.font_title = pygame.font.SysFont("Impact", 48)
            self.font_score = pygame.font.SysFont("Impact", 72)
            self.font_team = pygame.font.SysFont("Arial", 32, bold=True)
            self.font_log = pygame.font.SysFont("Segoe UI Emoji", 20)
            self.font_btn = pygame.font.SysFont("Arial", 22, bold=True)
        except:
            self.font_title = pygame.font.Font(None, 48)
            self.font_score = pygame.font.Font(None, 72)
            self.font_team = pygame.font.Font(None, 32)
            self.font_log = pygame.font.Font(None, 20)
            self.font_btn = pygame.font.Font(None, 22)

    def _generate_events(self, g1, g2):
        evs = []
        
        # Determine times for all events first
        times_g1 = sorted([random.randint(5, 90) for _ in range(g1)])
        times_g2 = sorted([random.randint(5, 90) for _ in range(g2)])
        
        total_rnd_events = random.randint(2, 5)
        rnd_times = sorted([random.randint(10, 85) for _ in range(total_rnd_events)])
        
        # Sub times (up to 2-4 subs per team)
        subs_t1_count = random.randint(2, 4)
        subs_t2_count = random.randint(2, 4)
        sub_times_t1 = sorted([random.randint(45, 85) for _ in range(subs_t1_count)])
        sub_times_t2 = sorted([random.randint(45, 85) for _ in range(subs_t2_count)])
        
        # Combine all to a single timeline to process sequentially
        timeline = []
        for t in times_g1: timeline.append({"min": t, "type": "goal", "team": 1})
        for t in times_g2: timeline.append({"min": t, "type": "goal", "team": 2})
        for t in rnd_times:
            team_rnd = random.randint(1, 2)
            evt_type = random.choices(["yellow", "red", "injury"], weights=[70, 5, 25])[0]
            timeline.append({"min": t, "type": evt_type, "team": team_rnd})
        for t in sub_times_t1: timeline.append({"min": t, "type": "sub", "team": 1})
        for t in sub_times_t2: timeline.append({"min": t, "type": "sub", "team": 2})
        
        timeline.sort(key=lambda x: x["min"])
        
        # Keep track of state (excluding injured/suspended players from match day squads)
        avail_t1 = [p for p in self.r1 if not (p.get("injured_until") or p.get("suspension", 0) > 0)] if self.r1 else []
        avail_t2 = [p for p in self.r2 if not (p.get("injured_until") or p.get("suspension", 0) > 0)] if self.r2 else []
        
        on_field_t1 = avail_t1[:11]
        on_field_t2 = avail_t2[:11]
        bench_t1 = avail_t1[11:]
        bench_t2 = avail_t2[11:]
        
        def get_team_state(t):
            if t == 1: return on_field_t1, bench_t1
            return on_field_t2, bench_t2
            
        def pick_scorer(on_field):
            if not on_field: return "D. Desconocido", None
            att = [p for p in on_field if p.get("pos") in ["ST", "LW", "RW", "CM", "CAM"]]
            if not att: att = on_field
            if not att: return "D. Desconocido", None
            sc = random.choice(att)["name"]
            ast = None
            if random.random() < 0.6:
                others = [p for p in on_field if p["name"] != sc]
                if others: ast = random.choice(others)["name"]
            return sc, ast
            
        def pick_player(on_field):
            if not on_field: return "D. Desconocido"
            return random.choice(on_field)["name"]

        for evt in timeline:
            on_f, bench = get_team_state(evt["team"])
            
            if evt["type"] == "goal":
                sc, ast = pick_scorer(on_f)
                evt["sc"] = sc
                evt["ast"] = ast
                evs.append(evt)
                
            elif evt["type"] in ["yellow", "red", "injury"]:
                p_name = pick_player(on_f)
                evt["player"] = p_name
                evs.append(evt)
                
                if evt["type"] == "injury":
                    # Apply injury to database
                    rost = self.r1 if evt["team"] == 1 else self.r2
                    player_obj = next((p for p in rost if p["name"] == p_name), None)
                    if player_obj:
                        player_obj["injury_weeks"] = random.randint(1, 8)
                        
                # Handle red card / injury removals
                if evt["type"] in ["red", "injury"]:
                    p_obj = next((p for p in on_f if p["name"] == p_name), None)
                    if p_obj:
                        on_f.remove(p_obj)
                        
                    # Force a substitution if it's an injury and we have bench players
                    if evt["type"] == "injury" and bench:
                        p_in = random.choice(bench)
                        bench.remove(p_in)
                        on_f.append(p_in)
                        evs.append({"min": evt["min"], "type": "sub", "team": evt["team"], "out": p_name, "in": p_in["name"]})
                        
            elif evt["type"] == "sub":
                if on_f and bench:
                    # Pick someone to sub out (avoid GK if possible)
                    out_cands = [p for p in on_f if p.get("pos") != "GK"]
                    if not out_cands: out_cands = on_f
                    p_out = random.choice(out_cands)
                    p_in = random.choice(bench)
                    
                    on_f.remove(p_out)
                    bench.remove(p_in)
                    on_f.append(p_in)
                    
                    evt["out"] = p_out["name"]
                    evt["in"] = p_in["name"]
                    evs.append(evt)

        return evs

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if self.finished:
                        self._finish()
                    else:
                        # Skip sim
                        self._skip_sim()
                elif event.key == pygame.K_SPACE:
                    if not self.finished:
                        self._skip_sim()

    def _skip_sim(self):
        while self.event_idx < len(self.events):
            self._process_event(self.events[self.event_idx])
            self.event_idx += 1
        self.finished = True

    def _process_event(self, ev):
        m = f"{ev['min']}'"
        
        if ev["type"] == "goal":
            if ev["team"] == 1: self.current_g1 += 1
            else: self.current_g2 += 1
            
            t_name = self.team1["short"] if ev["team"] == 1 else self.team2["short"]
            txt = f"{m} ⚽ GOAL {t_name}! {ev['sc']}"
            if ev["ast"]: txt += f" (Ast: {ev['ast']})"
            self.logs_display.append((txt, (100, 255, 100)))
            
        elif ev["type"] == "yellow":
            self.logs_display.append((f"{m} 🟨 Tarjeta Amarilla: {ev['player']}", (255, 255, 100)))
        elif ev["type"] == "red":
            self.logs_display.append((f"{m} 🟥 Tarjeta Roja: {ev['player']}", (255, 100, 100)))
        elif ev["type"] == "injury":
            self.logs_display.append((f"{m} 🏥 Lesión: {ev['player']} tiene que salir.", (255, 150, 80)))
        elif ev["type"] == "sub":
            self.logs_display.append((f"{m} 🔄 Cambio: Sale {ev['out']}, Entra {ev['in']}", (150, 200, 255)))
            
        while len(self.logs_display) > 10:
            self.logs_display.pop(0)

    def _finish(self):
        sc_list = []
        ast_list = []
        p_stats_map = {} # {name: stats}
        
        # Inicializar stats para todos los titulares que empezaron
        for p in (self.r1[:11] + self.r2[:11]):
            p_stats_map[p["name"]] = {
                "name": p["name"], "team": self.t1_short if p in self.r1 else self.t2_short,
                "rating": round(random.uniform(6.0, 7.5), 1), "goals": 0, "assists": 0,
                "yellow_cards": 0, "red_card": 0, "is_injured": False, "injury_severity": 0
            }

        for e in self.events:
            if e["type"] == "goal":
                sc_list.append(e["sc"])
                if e["sc"] in p_stats_map:
                    p_stats_map[e["sc"]]["goals"] += 1
                    p_stats_map[e["sc"]]["rating"] += 1.0
                if e["ast"]: 
                    ast_list.append(e["ast"])
                    if e["ast"] in p_stats_map:
                        p_stats_map[e["ast"]]["assists"] += 1
                        p_stats_map[e["ast"]]["rating"] += 0.6
            elif e["type"] == "yellow":
                if e["player"] in p_stats_map:
                    p_stats_map[e["player"]]["yellow_cards"] += 1
                    p_stats_map[e["player"]]["rating"] -= 0.5
            elif e["type"] == "red":
                if e["player"] in p_stats_map:
                    p_stats_map[e["player"]]["red_card"] = 1
                    p_stats_map[e["player"]]["rating"] -= 2.0
            elif e["type"] == "injury":
                if e["player"] in p_stats_map:
                    p_stats_map[e["player"]]["is_injured"] = True
                    p_stats_map[e["player"]]["injury_severity"] = random.randint(20, 90)
                    p_stats_map[e["player"]]["rating"] -= 0.3
            elif e["type"] == "sub":
                # Si entra alguien de la banca, añadirlo a las stats
                if e["in"] not in p_stats_map:
                    p_stats_map[e["in"]] = {
                        "name": e["in"], "team": self.t1_short if e["team"] == 1 else self.t2_short,
                        "rating": round(random.uniform(6.0, 7.0), 1), "goals": 0, "assists": 0,
                        "yellow_cards": 0, "red_card": 0, "is_injured": False, "injury_severity": 0
                    }
                
        res = {
            "gf": self.final_g1,
            "ga": self.final_g2,
            "scorers": sc_list,
            "assists": ast_list,
            "player_stats": list(p_stats_map.values())
        }
        career_manager.advance_time(res)
        
        # Player Mode: Reward Skill Points
        if career_manager.mode == "player":
            cp_name = career_manager.career_player["name"].lower().strip()
            played = False
            for name in p_stats_map:
                if name.lower().strip() == cp_name:
                    played = True
                    break
            
            if played:
                pshort = career_manager.player_team["short"] if career_manager.player_team else ""
                if self.t1_short == pshort:
                    gf = self.final_g1
                    ga = self.final_g2
                else:
                    gf = self.final_g2
                    ga = self.final_g1
                    
                reward = 1 # Participation
                if gf > ga: reward += 2 # Win
                elif gf == ga: reward += 1 # Draw
                
                career_manager.skill_points += reward
                self.manager.shared_data["last_reward"] = reward
            else:
                self.manager.shared_data["last_reward"] = 0
            
        from scenes.career_hub import CareerHubScene
        self.manager.set_scene(CareerHubScene)

    def update(self, dt):
        if not self.finished:
            self.time += dt
            self.event_timer -= dt
            
            if self.event_timer <= 0:
                if self.event_idx < len(self.events):
                    self._process_event(self.events[self.event_idx])
                    self.event_idx += 1
                    self.event_timer = random.uniform(0.3, 0.8) # Fast pacing
                else:
                    self.finished = True

    def draw(self, surface):
        surface.fill((10, 15, 20))
        
        # Header
        t1, t2 = self.team1, self.team2
        title = self.font_title.render(f"SIMULACIÓN: {self.tour_name}", True, UI_ACCENT)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 30))
        
        # Scoreboard
        from data.teams import draw_badge
        draw_badge(surface, t1, WIDTH//2 - 200, 150, size=70)
        draw_badge(surface, t2, WIDTH//2 + 200, 150, size=70)
        
        n1 = self.font_team.render(t1["name"], True, WHITE)
        surface.blit(n1, (WIDTH//2 - 200 - n1.get_width()//2, 240))
        
        n2 = self.font_team.render(t2["name"], True, WHITE)
        surface.blit(n2, (WIDTH//2 + 200 - n2.get_width()//2, 240))
        
        score_txt = f"{self.current_g1} - {self.current_g2}"
        ss = self.font_score.render(score_txt, True, UI_ACCENT_ALT)
        surface.blit(ss, (WIDTH//2 - ss.get_width()//2, 130))
        
        # Event Logs
        log_y = 320
        pygame.draw.line(surface, UI_TEXT_DIM, (100, log_y - 15), (WIDTH - 100, log_y - 15))
        
        for txt, color in self.logs_display:
            try:
                ls = self.font_log.render(txt, True, color)
            except:
                ls = self.font_btn.render(txt, True, color) # Fallback if emoji fails
            surface.blit(ls, (150, log_y))
            log_y += 30
            
        if self.finished:
            end_btn = pygame.Rect(WIDTH//2 - 150, HEIGHT - 80, 300, 50)
            pygame.draw.rect(surface, UI_ACCENT, end_btn, border_radius=8)
            bs = self.font_btn.render("CONTINUAR", True, BLACK)
            surface.blit(bs, (end_btn.centerx - bs.get_width()//2, end_btn.centery - bs.get_height()//2))
        else:
            hint = self.font_btn.render("SPACE / ENTER para saltar simulación recta final", True, UI_TEXT_DIM)
            surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 50))
