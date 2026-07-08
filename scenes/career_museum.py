import pygame
from settings import *
from data.career_manager import career_manager

class CareerMuseumScene:
    def __init__(self, manager, context=None):
        self.manager = manager
        
        try:
            self.font_title = pygame.font.SysFont("Impact", 36)
            self.font_sub = pygame.font.SysFont("Impact", 24)
            self.font_text = pygame.font.SysFont("Arial", 18, bold=True)
            self.font_hint = pygame.font.SysFont("Arial", 12)
        except:
            self.font_title = pygame.font.Font(None, 36)
            self.font_sub = pygame.font.Font(None, 24)
            self.font_text = pygame.font.Font(None, 18)
            self.font_hint = pygame.font.Font(None, 12)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_BACKSPACE):
                    self.manager.pop_scene()

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill(UI_BG)
        
        team = career_manager.player_team
        if not team: return
        
        # Header
        pygame.draw.rect(surface, (20, 25, 45), (0, 0, WIDTH, 100))
        from data.teams import draw_badge
        draw_badge(surface, team, 50, 50, size=60)
        
        title = self.font_title.render(f"MUSEO DEL CLUB - {team['name'].upper()}", True, WHITE)
        surface.blit(title, (130, 30))
        
        # Content
        records = career_manager._get_historic_records(team)
        if not records:
            txt = self.font_text.render("No hay registros históricos disponibles.", True, UI_TEXT_DIM)
            surface.blit(txt, (50, 150))
            return
            
        y = 130
        x1 = 50
        x2 = 460
        
        # Récords
        def draw_record(x, y, title, name, value_str):
            pygame.draw.rect(surface, (25, 30, 50), (x, y, 390, 80), border_radius=8)
            ts = self.font_sub.render(title, True, UI_ACCENT)
            surface.blit(ts, (x + 15, y + 10))
            ns = self.font_text.render(name, True, WHITE)
            surface.blit(ns, (x + 15, y + 45))
            vs = self.font_title.render(str(value_str), True, UI_ACCENT)
            surface.blit(vs, (x + 390 - vs.get_width() - 15, y + 25))
            return y + 100
            
        ry1 = draw_record(x1, y, "MÁS PARTIDOS", records.get("most_matches", {}).get("name", "---"), records.get("most_matches", {}).get("val", 0))
        ry1 = draw_record(x1, ry1, "MÁXIMO GOLEADOR", records.get("most_goals", {}).get("name", "---"), records.get("most_goals", {}).get("val", 0))
        ry1 = draw_record(x1, ry1, "MÁXIMO ASISTENTE", records.get("most_assists", {}).get("name", "---"), records.get("most_assists", {}).get("val", 0))
        
        ry2 = draw_record(x2, y, "MÁS JOVEN EN 10 GOLES", records.get("youngest_10_goals", {}).get("name", "---"), f"{records.get('youngest_10_goals', {}).get('age', '--')} años")
        ry2 = draw_record(x2, ry2, "MÁS JOVEN EN 50 GOLES", records.get("youngest_50_goals", {}).get("name", "---"), f"{records.get('youngest_50_goals', {}).get('age', '--')} años")
        ry2 = draw_record(x2, ry2, "MÁS JOVEN EN 100 PARTIDOS", records.get("youngest_100_matches", {}).get("name", "---"), f"{records.get('youngest_100_matches', {}).get('age', '--')} años")
        
        # My Stats panel if Player Career
        if career_manager.mode == "player":
            my_stats = None
            roster = career_manager.rosters.get(team["short"], [])
            for p in roster:
                if p.get("name") == career_manager.career_player["name"]:
                    my_stats = p
                    break
                    
            if my_stats:
                my_y = ry1 + 20
                pygame.draw.rect(surface, (40, 30, 20), (x1, my_y, 800, 100), border_radius=8)
                pygame.draw.rect(surface, UI_ACCENT, (x1, my_y, 800, 100), 2, border_radius=8)
                
                ms = self.font_sub.render("TUS REGISTROS EN EL CLUB", True, WHITE)
                surface.blit(ms, (x1 + 15, my_y + 10))
                
                txt = f"Partidos: {my_stats.get('club_matches', 0)}   |   Goles: {my_stats.get('club_goals', 0)}   |   Asistencias: {my_stats.get('club_assists', 0)}"
                ts = self.font_text.render(txt, True, (200, 255, 200))
                surface.blit(ts, (x1 + 15, my_y + 50))
                
        # Hint
        hint = self.font_hint.render("ESC o ENTER para volver", True, UI_TEXT_DIM)
        surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 30))
