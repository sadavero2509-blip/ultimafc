import pygame
from settings import *
from data.career_manager import career_manager

class CareerContinentalScene:
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        
        self.comps = ["CHAMPIONS", "EUROPA_LEAGUE", "CONFERENCE", "LIBERTADORES", "SUDAMERICANA", "CAF_CHAMPIONS", "CAF_CONFEDERATION", "CONCACAF_CUP"]
        self.comp_idx = 0
        self.tab_idx = 0  # 0=GRUPOS, 1=LLAVES, 2=GOLEADORES
        self.scroll_y = 0
        self.group_idx = 0
        
        try:
            self.font_title = pygame.font.SysFont("Impact", 36)
            self.font_sub = pygame.font.SysFont("Arial", 24, bold=True)
            self.font_text = pygame.font.SysFont("Arial", 16)
            self.font_bold = pygame.font.SysFont("Arial", 16, bold=True)
            self.font_hint = pygame.font.SysFont("Arial", 14)
        except:
            self.font_title = pygame.font.Font(None, 36)
            self.font_sub = pygame.font.Font(None, 24)
            self.font_text = pygame.font.Font(None, 16)
            self.font_bold = pygame.font.Font(None, 16)
            self.font_hint = pygame.font.Font(None, 14)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.tab_idx = (self.tab_idx - 1) % 3
                    self.scroll_y = 0
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.tab_idx = (self.tab_idx + 1) % 3
                    self.scroll_y = 0
                elif event.key == pygame.K_q:
                    self.comp_idx = (self.comp_idx - 1) % len(self.comps)
                    self.group_idx = 0
                    self.scroll_y = 0
                elif event.key == pygame.K_w:
                    self.comp_idx = (self.comp_idx + 1) % len(self.comps)
                    self.group_idx = 0
                    self.scroll_y = 0
                elif event.key in (pygame.K_UP, pygame.K_w):
                    if self.tab_idx == 0:
                        comp = career_manager.continental.get(self.comps[self.comp_idx])
                        if comp:
                            groups = sorted(comp["groups"].keys())
                            self.group_idx = (self.group_idx - 1) % len(groups)
                    else:
                        self.scroll_y = max(0, self.scroll_y - 1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    if self.tab_idx == 0:
                        comp = career_manager.continental.get(self.comps[self.comp_idx])
                        if comp:
                            groups = sorted(comp["groups"].keys())
                            self.group_idx = (self.group_idx + 1) % len(groups)
                    else:
                        self.scroll_y += 1
                elif event.key == pygame.K_ESCAPE:
                    from scenes.career_hub import CareerHubScene
                    self.manager.set_scene(CareerHubScene)

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((15, 20, 30))
        
        comp_name = self.comps[self.comp_idx]
        comp = career_manager.continental.get(comp_name)
        
        # Title
        colors = {
            "CHAMPIONS": (255, 215, 0),
            "EUROPA_LEAGUE": (255, 140, 0),
            "CONFERENCE": (50, 205, 50),
            "LIBERTADORES": (173, 255, 47),
            "SUDAMERICANA": (0, 191, 255),
            "CAF_CHAMPIONS": (230, 180, 40),
            "CAF_CONFEDERATION": (40, 200, 150),
            "CONCACAF_CUP": (210, 100, 250)
        }
        title_color = colors.get(comp_name, WHITE)
        title = self.font_title.render(comp_name, True, title_color)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 20))
        
        if not comp:
            ns = self.font_text.render("No hay datos de esta competencia aún.", True, UI_TEXT_DIM)
            surface.blit(ns, (100, 100))
            hint = self.font_hint.render("Q/W: Cambiar Competencia  ·  ESC: Volver", True, UI_TEXT_DIM)
            surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 30))
            return
        
        phase_lbl = self.font_sub.render(f"Fase: {comp['phase']}", True, UI_TEXT_DIM)
        surface.blit(phase_lbl, (WIDTH - 250, 30))
        
        # Tabs
        tabs = ["GRUPOS", "LLAVES", "GOLEADORES"]
        tab_w = WIDTH // len(tabs)
        for i, t in enumerate(tabs):
            is_sel = (self.tab_idx == i)
            c = WHITE if is_sel else UI_TEXT_DIM
            ts = self.font_sub.render(t, True, c)
            tx = i * tab_w + (tab_w//2 - ts.get_width()//2)
            surface.blit(ts, (tx, 70))
            if is_sel:
                pygame.draw.line(surface, title_color, (tx - 10, 100), (tx + ts.get_width() + 10, 100), 3)
        
        if self.tab_idx == 0:
            self._draw_groups(surface, comp, title_color)
        elif self.tab_idx == 1:
            self._draw_knockout(surface, comp, title_color)
        elif self.tab_idx == 2:
            self._draw_scorers(surface, comp_name)
        
        hint = self.font_hint.render("Q/W: Cambiar Comp  ·  ◀ ▶ Cambiar Pestaña  ·  ↑ ↓ Cambiar Grupo  ·  ESC: Volver", True, UI_TEXT_DIM)
        surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 30))

    def _draw_groups(self, surface, comp, accent):
        groups = sorted(comp["groups"].keys())
        if not groups:
            return
            
        # Group selector
        g_name = groups[self.group_idx % len(groups)]
        g_data = comp["groups"][g_name]
        
        gs = self.font_sub.render(f"GRUPO {g_name}", True, accent)
        surface.blit(gs, (50, 120))
        
        # Standings table
        st = sorted(g_data["standings"].items(), 
                    key=lambda x: (x[1]["pts"], x[1]["gf"]-x[1]["ga"]), reverse=True)
        
        cols = [("#", 40), ("EQUIPO", 180), ("PTS", 50), ("PJ", 40), ("PG", 40), ("PE", 40), ("PP", 40), ("GF", 40), ("GC", 40), ("DIF", 50)]
        
        cx = 50
        y = 160
        for label, w in cols:
            ls = self.font_bold.render(label, True, accent)
            surface.blit(ls, (cx, y))
            cx += w
        
        pygame.draw.line(surface, (50, 55, 70), (40, y + 22), (WIDTH - 300, y + 22), 1)
        
        row_y = y + 35
        for i, (short, s) in enumerate(st):
            c_text = WHITE
            if career_manager.player_team and career_manager.player_team["short"] == short:
                c_text = (255, 215, 0)
                
            cx = 50
            ns = self.font_text.render(str(i+1), True, c_text)
            surface.blit(ns, (cx, row_y)); cx += 40
            
            ts = self.font_bold.render(short, True, c_text)
            surface.blit(ts, (cx, row_y)); cx += 180
            
            pts = self.font_bold.render(str(s["pts"]), True, c_text)
            surface.blit(pts, (cx, row_y)); cx += 50
            
            for k in ["ph", "w", "d", "l", "gf", "ga"]:
                vs = self.font_text.render(str(s[k]), True, c_text)
                surface.blit(vs, (cx, row_y)); cx += 40
            
            dif = s["gf"] - s["ga"]
            dc = (100, 255, 100) if dif > 0 else (255, 100, 100) if dif < 0 else WHITE
            ds = self.font_text.render(str(dif), True, dc)
            surface.blit(ds, (cx, row_y))
            
            row_y += 30
        
        # Results list
        ry = row_y + 30
        rs = self.font_sub.render("RESULTADOS:", True, accent)
        surface.blit(rs, (50, ry))
        ry += 30
        
        results = g_data.get("results", [])
        if not results:
            ns = self.font_text.render("Aún no se han jugado partidos.", True, UI_TEXT_DIM)
            surface.blit(ns, (50, ry))
        else:
            for r in results[-6:]:  # Last 6 results
                txt = f"{r['home']} {r['g1']} - {r['g2']} {r['away']}"
                rs_txt = self.font_text.render(txt, True, WHITE)
                surface.blit(rs_txt, (70, ry))
                ry += 25

    def _draw_knockout(self, surface, comp, accent):
        y = 130
        
        for stage_name, stage_label in [("R16", "OCTAVOS DE FINAL"), ("QF", "CUARTOS DE FINAL"), ("SF", "SEMIFINALES"), ("FINAL", "FINAL")]:
            matches = comp["knockout"].get(stage_name, [])
            
            ls = self.font_sub.render(stage_label, True, accent)
            surface.blit(ls, (50, y))
            y += 30
            
            if not matches:
                ns = self.font_text.render("Por definir...", True, UI_TEXT_DIM)
                surface.blit(ns, (70, y))
                y += 30
            else:
                for m in matches:
                    home = m["home"]
                    away = m["away"]
                    result = m.get("result")
                    
                    if result:
                        txt = f"{home} {result[0]} - {result[1]} {away}"
                        c = (100, 255, 100)
                    else:
                        txt = f"{home} vs {away}"
                        c = WHITE
                    
                    rect = pygame.Rect(60, y - 3, 400, 28)
                    pygame.draw.rect(surface, UI_CARD_BG, rect, border_radius=4)
                    
                    ms = self.font_bold.render(txt, True, c)
                    surface.blit(ms, (70, y))
                    y += 35
            
            y += 15

    def _draw_scorers(self, surface, comp_name):
        sc = list(career_manager.scorers.get(comp_name, {}).items())
        sc.sort(key=lambda x: x[1], reverse=True)
        
        as_ = list(career_manager.assists.get(comp_name, {}).items())
        as_.sort(key=lambda x: x[1], reverse=True)
        
        y = 130
        
        # Scorers
        ls = self.font_sub.render("GOLEADORES", True, (255, 215, 0))
        surface.blit(ls, (50, y))
        y += 30
        
        if not sc:
            ns = self.font_text.render("Sin goles registrados aún.", True, UI_TEXT_DIM)
            surface.blit(ns, (70, y))
        else:
            for i, (name, gls) in enumerate(sc[:10]):
                ns = self.font_text.render(f"{i+1}. {name}", True, WHITE)
                gs = self.font_bold.render(str(gls), True, (255, 215, 0))
                surface.blit(ns, (70, y))
                surface.blit(gs, (450, y))
                y += 25
        
        y += 30
        
        # Assisters
        ls2 = self.font_sub.render("ASISTIDORES", True, (0, 200, 255))
        surface.blit(ls2, (50, y))
        y += 30
        
        if not as_:
            ns = self.font_text.render("Sin asistencias registradas aún.", True, UI_TEXT_DIM)
            surface.blit(ns, (70, y))
        else:
            for i, (name, ast) in enumerate(as_[:10]):
                ns = self.font_text.render(f"{i+1}. {name}", True, WHITE)
                gs = self.font_bold.render(str(ast), True, (0, 200, 255))
                surface.blit(ns, (70, y))
                surface.blit(gs, (450, y))
                y += 25
