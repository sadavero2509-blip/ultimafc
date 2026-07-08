import pygame
from settings import *
from data.career_manager import career_manager

class CareerRetireScene:
    """Manager retirement confirmation and career summary."""
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        self.confirmed = False
        self.become_manager_prompt = False
        self.sel = 0  # 0 = No, 1 = Sí
        
        try:
            self.font_title = pygame.font.SysFont("Impact", 44)
            self.font_sub = pygame.font.SysFont("Arial", 24, bold=True)
            self.font_text = pygame.font.SysFont("Arial", 18)
            self.font_bold = pygame.font.SysFont("Arial", 20, bold=True)
            self.font_hint = pygame.font.SysFont("Arial", 14)
        except:
            self.font_title = pygame.font.Font(None, 44)
            self.font_sub = pygame.font.Font(None, 24)
            self.font_text = pygame.font.Font(None, 18)
            self.font_bold = pygame.font.Font(None, 20)
            self.font_hint = pygame.font.Font(None, 14)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.become_manager_prompt:
                    if event.key in (pygame.K_LEFT, pygame.K_a) or event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.sel = 1 - self.sel
                    elif event.key == pygame.K_RETURN:
                        if self.sel == 1:
                            self._convert_to_manager()
                        else:
                            career_manager.active = False
                            career_manager.retired = True
                            from scenes.main_menu import MainMenuScene
                            self.manager.set_scene(MainMenuScene)
                elif self.confirmed:
                    if event.key == pygame.K_RETURN:
                        if career_manager.mode == "player":
                            self.become_manager_prompt = True
                            self.sel = 0 # Default to NO
                        else:
                            career_manager.active = False
                            career_manager.retired = True
                            from scenes.main_menu import MainMenuScene
                            self.manager.set_scene(MainMenuScene)
                else:
                    if event.key in (pygame.K_LEFT, pygame.K_a) or event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.sel = 1 - self.sel
                    elif event.key == pygame.K_RETURN:
                        if self.sel == 1:
                            self.confirmed = True
                        else:
                            from scenes.career_hub import CareerHubScene
                            self.manager.set_scene(CareerHubScene)
                    elif event.key == pygame.K_ESCAPE:
                        from scenes.career_hub import CareerHubScene
                        self.manager.set_scene(CareerHubScene)

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((15, 20, 30))
        
        cs = career_manager.career_stats
        
        if self.become_manager_prompt:
            self._draw_become_manager(surface)
        elif not self.confirmed:
            self._draw_confirmation(surface, cs)
        else:
            self._draw_farewell(surface, cs)

    def _draw_confirmation(self, surface, cs):
        is_player = (career_manager.mode == "player")
        title_txt = "🌅 RETIRO DEL JUGADOR" if is_player else "🌅 RETIRO DEL ENTRENADOR"
        title = self.font_title.render(title_txt, True, (255, 100, 80))
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 60))
        
        warn = self.font_text.render("¿Estás seguro de que deseas retirarte? Esta acción terminará tu carrera.", True, WHITE)
        surface.blit(warn, (WIDTH//2 - warn.get_width()//2, 130))
        
        # Quick summary
        y = 200
        name_lbl = "Jugador" if is_player else "Mánager"
        matches_lbl = "Partidos Jugados" if is_player else "Partidos Dirigidos"
        
        lines = [
            f"{name_lbl}: {career_manager.manager_name}",
            f"Temporadas: {cs['seasons_completed']}",
            f"{matches_lbl}: {cs['matches']}"
        ]
        
        if is_player:
            lines.append(f"Tus Goles: {cs.get('player_goals', 0)}  |  Tus Asistencias: {cs.get('player_assists', 0)}")
        else:
            lines.append(f"Goles A Favor: {cs.get('goals_scored', 0)}  |  Goles En Contra: {cs.get('goals_conceded', 0)}")
            
        lines.append(f"Victorias: {cs['wins']}  |  Empates: {cs['draws']}  |  Derrotas: {cs['losses']}")
        lines.append(f"Títulos: {len(cs.get('titles', []))}")
        for line in lines:
            ls = self.font_text.render(line, True, UI_TEXT_DIM)
            surface.blit(ls, (WIDTH//2 - ls.get_width()//2, y))
            y += 30
        
        # Buttons
        y += 40
        opts = ["❌ CANCELAR", "✅ CONFIRMAR RETIRO"]
        for i, opt in enumerate(opts):
            rect = pygame.Rect(WIDTH//2 - 250 + i * 260, y, 240, 50)
            is_sel = (self.sel == i)
            c = (80, 30, 30) if i == 1 and is_sel else UI_CARD_HOVER if is_sel else UI_CARD_BG
            pygame.draw.rect(surface, c, rect, border_radius=8)
            if is_sel:
                bc = (255, 100, 100) if i == 1 else UI_ACCENT
                pygame.draw.rect(surface, bc, rect, 2, border_radius=8)
            
            os_txt = self.font_bold.render(opt, True, WHITE)
            surface.blit(os_txt, (rect.centerx - os_txt.get_width()//2, rect.centery - os_txt.get_height()//2))
        
        hint = self.font_hint.render("◀ ▶ Seleccionar  ·  ENTER Confirmar  ·  ESC Cancelar", True, UI_TEXT_DIM)
        surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 30))

    def _draw_farewell(self, surface, cs):
        is_player = (career_manager.mode == "player")
        title_txt = "👏 LEYENDA DEL FÚTBOL" if is_player else "👏 GRACIAS POR TODO, MISTER"
        title = self.font_title.render(title_txt, True, (255, 215, 0))
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 40))
        
        sub_txt = f"{career_manager.manager_name} cuelga las botas..." if is_player else f"{career_manager.manager_name} se retira del fútbol profesional."
        sub = self.font_sub.render(sub_txt, True, WHITE)
        surface.blit(sub, (WIDTH//2 - sub.get_width()//2, 100))
        
        y = 170
        
        # Grand summary
        box = pygame.Rect(WIDTH//2 - 300, y, 600, 350)
        pygame.draw.rect(surface, UI_CARD_BG, box, border_radius=12)
        pygame.draw.rect(surface, (255, 215, 0), box, 2, border_radius=12)
        
        seasons_lbl = "Temporadas en Activo" if is_player else "Temporadas en el Banquillo"
        matches_lbl = "Partidos Jugados" if is_player else "Partidos Dirigidos"
        goals_lbl = "Goles Marcados" if is_player else "Goles del Equipo"
        goals_val = str(cs["player_goals"] if is_player else cs["goals_scored"])
        market_lbl = "Valor de Mercado Final" if is_player else "Fichajes Realizados"
        market_val = "$25.0M" if is_player else str(cs["transfers_in"])
        
        summary_lines = [
            (seasons_lbl, str(cs["seasons_completed"])),
            (matches_lbl, str(cs["matches"])),
            ("Victorias", str(cs["wins"])),
            ("Empates", str(cs["draws"])),
            ("Derrotas", str(cs["losses"])),
            ("Porcentaje de Victoria", f"{(cs['wins']/max(1,cs['matches']))*100:.1f}%"),
            (goals_lbl, goals_val),
        ]
        if is_player:
            summary_lines.append(("Asistencias Reales", str(cs["player_assists"])))
            
        summary_lines += [
            ("Goles Recibidos / En Contra", str(cs["goals_conceded"])),
            (market_lbl, market_val),
            ("Títulos Conquistados", str(len(cs.get("titles", [])))),
        ]
        
        sy = y + 20
        for label, value in summary_lines:
            ls = self.font_text.render(label, True, UI_TEXT_DIM)
            vs = self.font_bold.render(value, True, WHITE)
            surface.blit(ls, (box.left + 30, sy))
            surface.blit(vs, (box.right - 80, sy))
            sy += 30
        
        # Titles list
        titles = cs.get("titles", [])
        if titles:
            sy += 10
            tlbl = self.font_sub.render("🏆 Palmarés:", True, (255, 215, 0))
            surface.blit(tlbl, (box.left + 30, sy))
            sy += 25
            for t_name in titles[:3]:
                ts = self.font_text.render(f"🏆 {t_name}", True, (255, 215, 0))
                surface.blit(ts, (box.left + 50, sy))
                sy += 22
        
        # Teams
        teams_str = ", ".join(cs.get("teams_managed", []))
        tms = self.font_text.render(f"Equipos: {teams_str}", True, UI_TEXT_DIM)
        surface.blit(tms, (WIDTH//2 - tms.get_width()//2, y + 360))
        
        h = self.font_bold.render("Presiona ENTER para continuar", True, WHITE)
        surface.blit(h, (WIDTH//2 - h.get_width()//2, HEIGHT - 60))

    def _draw_become_manager(self, surface):
        title = self.font_title.render("👔 UNA NUEVA ETAPA", True, UI_ACCENT)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 60))
        
        warn = self.font_bold.render(f"¿Te gustaría continuar en {career_manager.player_team['name']} como Entrenador Profesional?", True, WHITE)
        surface.blit(warn, (WIDTH//2 - warn.get_width()//2, 130))
        
        desc1 = self.font_text.render("Tu increíble carrera como jugador te otorga prestigio inicial para tomar las riendas.", True, UI_TEXT_DIM)
        surface.blit(desc1, (WIDTH//2 - desc1.get_width()//2, 170))
        
        # Calculate expected prestige based on position
        cs = career_manager.career_stats
        titles = len(cs.get("titles", []))
        goals = cs.get("player_goals", 0)
        assists = cs.get("player_assists", 0)
        matches = cs.get("matches", 0)
        
        pos = career_manager.career_player.get("pos", "CM") if career_manager.career_player else "CM"
        if pos == "GK":
            perf_bonus = int(matches / 15)
        elif pos in ["CB", "LB", "RB", "LWB", "RWB"]:
            perf_bonus = int(matches / 20) + int(goals / 3) + int(assists / 5)
        elif pos in ["CM", "CAM", "CDM", "LM", "RM"]:
            perf_bonus = int(assists / 5) + int(goals / 5) + int(matches / 25)
        else: # ST, CF, LW, RW
            perf_bonus = int(goals / 10) + int(assists / 10) + int(matches / 30)
            
        expected_prestige = min(990, 500 + (titles * 50) + perf_bonus * 10)
        
        desc2 = self.font_text.render(f"Prestigio Inicial Esperado: {expected_prestige}/1000", True, (255, 215, 0))
        surface.blit(desc2, (WIDTH//2 - desc2.get_width()//2, 210))
        
        # Buttons
        y = 300
        opts = ["❌ NO, RETIRARME DEL FÚTBOL", "✅ SÍ, SER ENTRENADOR"]
        for i, opt in enumerate(opts):
            rect = pygame.Rect(WIDTH//2 - 270 + i * 280, y, 260, 50)
            is_sel = (self.sel == i)
            c = (40, 80, 40) if i == 1 and is_sel else UI_CARD_HOVER if is_sel else UI_CARD_BG
            pygame.draw.rect(surface, c, rect, border_radius=8)
            if is_sel:
                bc = (100, 255, 100) if i == 1 else UI_ACCENT
                pygame.draw.rect(surface, bc, rect, 2, border_radius=8)
            
            os_txt = self.font_bold.render(opt, True, WHITE)
            surface.blit(os_txt, (rect.centerx - os_txt.get_width()//2, rect.centery - os_txt.get_height()//2))
        
        hint = self.font_hint.render("◀ ▶ Seleccionar  ·  ENTER Confirmar", True, UI_TEXT_DIM)
        surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 30))

    def _convert_to_manager(self):
        # We need to change the mode
        career_manager.mode = "manager"
        
        # We also need to give them a prestige boost based on their player career.
        cs = career_manager.career_stats
        titles = len(cs.get("titles", []))
        goals = cs.get("player_goals", 0)
        assists = cs.get("player_assists", 0)
        matches = cs.get("matches", 0)
        
        pos = career_manager.career_player.get("pos", "CM") if career_manager.career_player else "CM"
        if pos == "GK":
            perf_bonus = int(matches / 15)
        elif pos in ["CB", "LB", "RB", "LWB", "RWB"]:
            perf_bonus = int(matches / 20) + int(goals / 3) + int(assists / 5)
        elif pos in ["CM", "CAM", "CDM", "LM", "RM"]:
            perf_bonus = int(assists / 5) + int(goals / 5) + int(matches / 25)
        else: # ST, CF, LW, RW
            perf_bonus = int(goals / 10) + int(assists / 10) + int(matches / 30)
            
        bonus_prestige = min(990, 500 + (titles * 50) + perf_bonus * 10)
        
        career_manager.manager_prestige = bonus_prestige
        career_manager.career_stats["prestige"] = bonus_prestige
        
        # Save the player's legacy before clearing career_player
        legacy = {
            "name": career_manager.career_player["name"],
            "pos": career_manager.career_player.get("pos", "CM"),
            "goals": cs.get("player_goals", 0),
            "assists": cs.get("player_assists", 0),
            "matches": matches,
            "titles": cs.get("titles", [])[:],
            "idol": career_manager.career_player.get("idol"),
            "teams": cs.get("teams_managed", [])[:],
            "individual_awards": cs.get("individual_awards", [])[:],
        }
        
        # Find best partner from playing career
        partnerships = cs.get("partnerships", {})
        best_partner = None
        best_score = 0
        for name, data in partnerships.items():
            score = data.get("assists_to_you", 0) * 3 + data.get("assists_from_you", 0) * 3 + data.get("goals_together", 0) * 2 + data.get("matches", 0) * 0.1
            if score > best_score:
                best_score = score
                best_partner = name
        legacy["best_partner"] = best_partner
        
        # Find top rival from playing career
        rivalries = cs.get("rivalries", {})
        top_rival = None
        top_rival_score = 0
        for name, data in rivalries.items():
            score = data.get("matches_against", 0) + data.get("their_goals", 0) * 2
            if score > top_rival_score:
                top_rival_score = score
                top_rival = name
        legacy["top_rival"] = top_rival
        
        career_manager.career_stats["player_legacy"] = legacy
        
        career_manager.career_player = None
        
        # Presentar al nuevo DT
        from scenes.presentation import PresentationScene
        from scenes.career_hub import CareerHubScene
        self.manager.set_scene(PresentationScene, context={
            "team": career_manager.player_team,
            "player_name": career_manager.manager_name,
            "is_manager": True,
            "next_scene": CareerHubScene
        })
