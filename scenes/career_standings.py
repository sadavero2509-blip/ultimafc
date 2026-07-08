import pygame
from settings import *
from data.career_manager import career_manager

class CareerStandingsScene:
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        
        self.tabs = ["TABLA DE POSICIONES", "GOLEADORES", "ASISTIDORES"]
        self.tab_idx = 0
        self.scroll_y = 0
        
        self.lg_idx = career_manager.leagues.index(career_manager.league_id)
        
        self._refresh_data()
        
    def _refresh_data(self):
        lg = career_manager.leagues[self.lg_idx]
        
        st = list(career_manager.standings.get(lg, {}).items())
        st.sort(key=lambda x: (x[1]["pts"], x[1]["gf"] - x[1]["ga"], x[1]["gf"]), reverse=True)
        self.table_data = st
        
        sc = list(career_manager.scorers.get(f"LIGA_{lg}", {}).items())
        sc.sort(key=lambda x: x[1], reverse=True)
        self.scorers_data = sc
        
        a = list(career_manager.assists.get(f"LIGA_{lg}", {}).items())
        a.sort(key=lambda x: x[1], reverse=True)
        self.assists_data = a
        
        try:
            self.font_title = pygame.font.SysFont("Impact", 36)
            self.font_tab = pygame.font.SysFont("Arial", 22, bold=True)
            self.font_text = pygame.font.SysFont("Arial", 16)
            self.font_bold = pygame.font.SysFont("Arial", 16, bold=True)
            self.font_hint = pygame.font.SysFont("Arial", 14)
        except:
            self.font_title = pygame.font.Font(None, 36)
            self.font_tab = pygame.font.Font(None, 22)
            self.font_text = pygame.font.Font(None, 16)
            self.font_bold = pygame.font.Font(None, 16)
            self.font_hint = pygame.font.Font(None, 14)

    def handle_events(self, events):
        max_scroll = 0
        if self.tab_idx == 0: max_scroll = max(0, len(self.table_data) - 15)
        else: max_scroll = max(0, len(self.scorers_data) - 15)
        
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_a):
                    self.tab_idx = (self.tab_idx - 1) % len(self.tabs)
                    self.scroll_y = 0
                elif event.key in (pygame.K_RIGHT, pygame.K_d):
                    self.tab_idx = (self.tab_idx + 1) % len(self.tabs)
                    self.scroll_y = 0
                elif event.key in (pygame.K_UP, pygame.K_w):
                    self.scroll_y = max(0, self.scroll_y - 1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.scroll_y = min(max_scroll, self.scroll_y + 1)
                elif event.key == pygame.K_q:
                    self.lg_idx = (self.lg_idx - 1) % len(career_manager.leagues)
                    self.scroll_y = 0
                    self._refresh_data()
                elif event.key == pygame.K_w:
                    self.lg_idx = (self.lg_idx + 1) % len(career_manager.leagues)
                    self.scroll_y = 0
                    self._refresh_data()
                elif event.key == pygame.K_ESCAPE:
                    from scenes.career_hub import CareerHubScene
                    self.manager.set_scene(CareerHubScene)

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((15, 20, 30))
        
        lg = career_manager.leagues[self.lg_idx]
        title = self.font_title.render(f"ESTADÍSTICAS LIGA: {lg}", True, UI_ACCENT)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 20))
        
        # Tabs
        tab_w = WIDTH // len(self.tabs)
        for i, t in enumerate(self.tabs):
            is_sel = (self.tab_idx == i)
            c = WHITE if is_sel else UI_TEXT_DIM
            ts = self.font_tab.render(t, True, c)
            tx = i * tab_w + (tab_w//2 - ts.get_width()//2)
            surface.blit(ts, (tx, 80))
            if is_sel:
                pygame.draw.line(surface, UI_ACCENT, (tx - 10, 110), (tx + ts.get_width() + 10, 110), 3)
                
        # Content
        col_y = 140
        if self.tab_idx == 0:
            self._draw_standings(surface, col_y)
        elif self.tab_idx == 1:
            self._draw_stats(surface, col_y, self.scorers_data, "GOLES")
        elif self.tab_idx == 2:
            self._draw_stats(surface, col_y, self.assists_data, "ASISTENCIAS")
            
        hint = self.font_hint.render("Q/W: Cambiar Liga  ·  ◀ ▶ Cambiar Pestaña  ·  ↑ ↓ Bajar/Subir  ·  ESC Volver", True, UI_TEXT_DIM)
        surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 30))

    def _draw_standings(self, surface, start_y):
        cols = [("#", 50), ("EQUIPO", 250), ("PTS", 80), ("PJ", 50), ("PG", 50), ("PE", 50), ("PP", 50), ("GF", 50), ("GC", 50), ("DIF", 50)]
        
        cx = 50
        for label, w in cols:
            ls = self.font_bold.render(label, True, UI_ACCENT)
            surface.blit(ls, (cx, start_y))
            cx += w
            
        pygame.draw.line(surface, (50, 55, 70), (40, start_y + 25), (WIDTH - 40, start_y + 25), 1)
        
        row_y = start_y + 40
        visible = self.table_data[self.scroll_y : self.scroll_y + 15]
        
        for i, (short, s) in enumerate(visible):
            real_idx = self.scroll_y + i + 1
            
            c_text = WHITE
            if career_manager.player_team["short"] == short:
                c_text = (255, 215, 0) # Gold for player team
                
            cx = 50
            # #
            ns = self.font_text.render(str(real_idx), True, c_text)
            surface.blit(ns, (cx, row_y))
            cx += 50
            # EQUIPO
            ts = self.font_text.render(short, True, c_text)
            surface.blit(ts, (cx, row_y))
            cx += 250
            # PTS
            ps = self.font_bold.render(str(s["pts"]), True, c_text)
            surface.blit(ps, (cx, row_y))
            cx += 80
            # PJ
            pjs = self.font_text.render(str(s["ph"]), True, c_text)
            surface.blit(pjs, (cx, row_y))
            cx += 50
            # PG, PE, PP, GF, GC
            for k in ["w", "d", "l", "gf", "ga"]:
                vs = self.font_text.render(str(s[k]), True, c_text)
                surface.blit(vs, (cx, row_y))
                cx += 50
            
            # DIF
            dif = s["gf"] - s["ga"]
            dc = (100, 255, 100) if dif > 0 else (255, 100, 100) if dif < 0 else WHITE
            ds = self.font_text.render(str(dif), True, dc)
            surface.blit(ds, (cx, row_y))
            
            row_y += 30

    def _draw_stats(self, surface, start_y, data, val_label):
        cols = [("#", 80), ("JUGADOR", 400), (val_label, 100)]
        
        cx = 200
        for label, w in cols:
            ls = self.font_bold.render(label, True, UI_ACCENT)
            surface.blit(ls, (cx, start_y))
            cx += w
            
        pygame.draw.line(surface, (50, 55, 70), (190, start_y + 25), (800, start_y + 25), 1)
        
        row_y = start_y + 40
        visible = data[self.scroll_y : self.scroll_y + 15]
        
        if not visible:
            ns = self.font_text.render("No hay datos disponibles.", True, UI_TEXT_DIM)
            surface.blit(ns, (200, row_y))
            
        for i, (name, val) in enumerate(visible):
            real_idx = self.scroll_y + i + 1
            
            cx = 200
            ns = self.font_text.render(str(real_idx), True, WHITE)
            surface.blit(ns, (cx, row_y))
            cx += 80
            
            nms = self.font_text.render(name, True, WHITE)
            surface.blit(nms, (cx, row_y))
            cx += 400
            
            vs = self.font_bold.render(str(val), True, (255, 215, 0))
            surface.blit(vs, (cx, row_y))
            
            row_y += 30
