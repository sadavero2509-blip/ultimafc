import pygame
import math
from settings import *
from data.career_manager import career_manager

class CareerStatsScene:
    """Full career statistics dashboard with a fixed tab-based layout."""
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        self.tab_idx = 0
        self.time = 0
        
        self.tabs = [
            {"id": "matches", "name": "PARTIDOS", "icon": "📊"},
            {"id": "contract", "name": "CONTRATO", "icon": "📄"},
            {"id": "clubs", "name": "CLUBES", "icon": "🛡️"},
            {"id": "titles", "name": "PALMARÉS", "icon": "🏆"}
        ]

        # Allow opening a specific tab from another scene (e.g. from CareerHub)
        tab_id = self.context.get("tab_id")
        if tab_id:
            for i, tab in enumerate(self.tabs):
                if tab["id"] == tab_id:
                    self.tab_idx = i
                    break
        
        try:
            self.font_title = pygame.font.SysFont("Impact", 40)
            self.font_sub = pygame.font.SysFont("Arial", 24, bold=True)
            self.font_text = pygame.font.SysFont("Arial", 18)
            self.font_bold = pygame.font.SysFont("Arial", 18, bold=True)
            self.font_hint = pygame.font.SysFont("Arial", 14)
            self.font_icon = pygame.font.SysFont("Segoe UI Emoji", 26)
        except:
            self.font_title = pygame.font.Font(None, 40)
            self.font_sub = pygame.font.Font(None, 24)
            self.font_text = pygame.font.Font(None, 18)
            self.font_bold = pygame.font.Font(None, 18)
            self.font_hint = pygame.font.Font(None, 14)
            self.font_icon = pygame.font.Font(None, 26)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.tab_idx = (self.tab_idx - 1) % len(self.tabs)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.tab_idx = (self.tab_idx + 1) % len(self.tabs)
                elif event.key == pygame.K_ESCAPE:
                    from scenes.career_hub import CareerHubScene
                    self.manager.set_scene(CareerHubScene)

    def update(self, dt):
        self.time += dt

    def draw(self, surface):
        surface.fill((15, 20, 30))
        
        cs = career_manager.career_stats
        t = career_manager.player_team
        
        # ── HEADER (Fixed) ──
        header_rect = pygame.Rect(0, 0, WIDTH, 100)
        pygame.draw.rect(surface, (25, 30, 45), header_rect)
        pygame.draw.line(surface, UI_ACCENT, (0, 100), (WIDTH, 100), 3)
        
        mode_title = "ESTADÍSTICAS DEL JUGADOR" if career_manager.mode == "player" else "REPORTE DEL MÁNAGER"
        title = self.font_title.render(f"{mode_title}: {career_manager.manager_name.upper()}", True, (255, 215, 0))
        surface.blit(title, (40, 25))
        
        if t:
            team_txt = self.font_text.render(f"Club: {t['name']} | Temp. {career_manager.year}", True, WHITE)
            surface.blit(team_txt, (40, 65))

        # ── LEFT MENU (Static) ──
        menu_x = 40
        menu_y = 140
        menu_w = 300
        for i, tab in enumerate(self.tabs):
            is_sel = (self.tab_idx == i)
            rect = pygame.Rect(menu_x, menu_y + i * 50, menu_w, 42)
            
            bg = UI_CARD_HOVER if is_sel else UI_CARD_BG
            pygame.draw.rect(surface, bg, rect, border_radius=8)
            
            if is_sel:
                pulse = (math.sin(self.time * 4) + 1) / 2
                bc = (int(pulse * 100), int(150 + pulse * 100), int(200 + pulse * 50))
                pygame.draw.rect(surface, bc, rect, 2, border_radius=8)
            else:
                pygame.draw.rect(surface, (50, 55, 70), rect, 1, border_radius=8)

            # Icon
            try:
                ic = self.font_icon.render(tab["icon"], True, WHITE)
                surface.blit(ic, (rect.left + 10, rect.centery - ic.get_height()//2))
            except: pass
            
            txt = self.font_bold.render(tab["name"], True, WHITE if is_sel else UI_TEXT_DIM)
            surface.blit(txt, (rect.left + 50, rect.centery - txt.get_height()//2))

        # ── RIGHT DETAIL PANE (Fixed Perspective) ──
        pane_rect = pygame.Rect(menu_x + menu_w + 40, 140, WIDTH - (menu_x + menu_w + 80), HEIGHT - 200)
        pygame.draw.rect(surface, (20, 25, 40), pane_rect, border_radius=12)
        pygame.draw.rect(surface, (40, 45, 60), pane_rect, 2, border_radius=12)
        
        sel_id = self.tabs[self.tab_idx]["id"]
        self._draw_detail(surface, pane_rect, sel_id, cs)

        # Hint
        hint = self.font_hint.render("↑↓/WS Navegar  ·  ESC Volver", True, UI_TEXT_DIM)
        surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 30))

    def _draw_detail(self, surface, rect, tab_id, cs):
        px, py = rect.left + 30, rect.top + 30
        
        if tab_id == "matches":
            lbl = self.font_sub.render("📊 RENDIMIENTO HISTÓRICO", True, UI_ACCENT)
            surface.blit(lbl, (px, py))
            py += 60
            
            matches = cs["matches"]
            wins = cs["wins"]
            draws = cs["draws"]
            losses = cs["losses"]
            
            if career_manager.mode == "player":
                played = cs.get("matches_played", 0)
                stats = [
                    ("Partidos Jugados", str(played)),
                    ("Victorias", str(wins)),
                    ("Empates", str(draws)),
                    ("Derrotas", str(losses)),
                    ("Calificación Media", f"{cs.get('avg_rating', 0.0):.1f}"),
                ]
            else:
                stats = [
                    ("Partidos Dirigidos", str(matches)),
                    ("Victorias", str(wins)),
                    ("Empates", str(draws)),
                    ("Derrotas", str(losses)),
                    ("Efectividad", f"{(wins/max(1,matches))*100:.1f}%")
                ]
            
            for label, val in stats:
                l_surf = self.font_text.render(label, True, UI_TEXT_DIM)
                v_surf = self.font_bold.render(val, True, WHITE)
                surface.blit(l_surf, (px, py))
                surface.blit(v_surf, (px + 280, py))
                py += 35
                
            py += 20
            if career_manager.mode == "player":
                goals_txt = f"Tus Goles: {cs['player_goals']}  |  Tus Asistencias: {cs['player_assists']}"
            else:
                goals_txt = f"Goles del Equipo: {cs['goals_scored']}  |  Goles Recibidos: {cs['goals_conceded']}"
            g_surf = self.font_text.render(goals_txt, True, (100, 255, 150))
            surface.blit(g_surf, (px, py))

        elif tab_id == "contract":
            lbl = self.font_sub.render("📄 SITUACIÓN CONTRACTUAL", True, (0, 200, 255))
            surface.blit(lbl, (px, py))
            py += 60
            
            if career_manager.mode == "player":
                p = career_manager.career_player
                contract_years = int(p.get("contract_years", 3) or 0)
                role = p.get("role") or career_manager._get_player_role(p)

                # Prefer contract-stored salary; fallback to dynamic calculation
                sal_m_yr = p.get("salary", None)
                if sal_m_yr is None:
                    sal_m_yr = career_manager._calculate_salary(p)
                sal_k_wk = round((float(sal_m_yr) * 1000.0) / 52.0, 1)

                # Keep consult-only: negotiation rules live in CareerHub
                can_renew = contract_years <= 2
                renew_str = "Renovación disponible" if can_renew else f"Renovación en {max(0, contract_years-2)} año(s)"

                # Market value is still useful as extra context
                val = career_manager.calculate_player_value(p)
                
                info = [
                    ("Club", career_manager.player_team["name"]),
                    ("Rol (contrato)", role),
                    ("Contrato restante", f"{contract_years} año(s)"),
                    ("Salario anual", f"${float(sal_m_yr):.2f}M"),
                    ("Sueldo Semanal", f"${sal_k_wk}k"),
                    ("Renovación", renew_str),
                    ("Valor de Mercado", f"${val}M"),
                ]
            else:
                info = [
                    ("Club", career_manager.player_team["name"]),
                    ("Fichajes", str(cs["transfers_in"])),
                    ("Ventas", str(cs["transfers_out"])),
                    ("Inversión Total", f"${cs['total_spent']}M"),
                    ("Beneficio Total", f"${cs['total_earned']}M")
                ]
            
            for label, val in info:
                l_surf = self.font_text.render(label, True, UI_TEXT_DIM)
                v_surf = self.font_bold.render(str(val), True, WHITE)
                surface.blit(l_surf, (px, py))
                surface.blit(v_surf, (px + 250, py))
                py += 35

        elif tab_id == "clubs":
            lbl = self.font_sub.render("🛡️ CLUBES EN LA CARRERA", True, (255, 150, 50))
            surface.blit(lbl, (px, py))
            py += 60
            
            clubs = cs.get("teams_managed", [])
            if not clubs:
                surface.blit(self.font_text.render("Sin historial aún.", True, UI_TEXT_DIM), (px, py))
            else:
                for i, club in enumerate(clubs):
                    c_surf = self.font_text.render(f"{i+1}. {club}", True, WHITE)
                    surface.blit(c_surf, (px, py))
                    py += 35

        elif tab_id == "titles":
            lbl = self.font_sub.render("🏆 PALMARÉS Y GLORIA", True, (255, 215, 0))
            surface.blit(lbl, (px, py))
            py += 60
            
            titles = cs.get("titles", [])
            awards = cs.get("individual_awards", [])
            
            if not titles and not awards:
                surface.blit(self.font_text.render("Sin títulos ni premios aún. ¡Es hora de ganar!", True, UI_TEXT_DIM), (px, py))
            else:
                for title_name in titles:
                    t_surf = self.font_bold.render(f"🏆 {title_name}", True, (255, 215, 0))
                    surface.blit(t_surf, (px, py))
                    py += 40
                
                if awards:
                    py += 20
                    lbl2 = self.font_sub.render("✨ PREMIOS INDIVIDUALES", True, UI_ACCENT)
                    surface.blit(lbl2, (px, py))
                    py += 50
                    for award in awards:
                        a_surf = self.font_bold.render(f"🏅 {award}", True, WHITE)
                        surface.blit(a_surf, (px, py))
                        py += 35


