import pygame
import math
from settings import *
from data.career_manager import career_manager

class CareerAgentScene:
    """Scene to manage the player's representative and view club opportunities."""
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        self.tab = "agents" # "agents" or "opportunities"
        self.sel_idx = 0
        self.time = 0
        self.msg = ""
        self.msg_timer = 0
        
        self.agents = [
            {"level": 0, "name": "Ninguno", "commission": 0, "price": 0, "desc": "Tú mismo negocias. Sin bonus de sueldo."},
            {"level": 1, "name": "Básico (Familiar)", "commission": 3, "price": 0.1, "desc": "Tu familia te ayuda. +15% sueldo base."},
            {"level": 2, "name": "Profesional", "commission": 5, "price": 0.5, "desc": "Agente con contactos. +30% sueldo base."},
            {"level": 3, "name": "Top (Agente FIFA)", "commission": 7, "price": 2.0, "desc": "Agente de renombre. +45% sueldo base."},
            {"level": 4, "name": "Leyenda (Agente Top)", "commission": 10, "price": 5.0, "desc": "El mejor del mundo. +60% sueldo base y mejores clubes."}
        ]
        
        try:
            self.font_title = pygame.font.SysFont("Impact", 40)
            self.font_sub = pygame.font.SysFont("Arial", 24, bold=True)
            self.font_text = pygame.font.SysFont("Arial", 18)
            self.font_bold = pygame.font.SysFont("Arial", 18, bold=True)
            self.font_hint = pygame.font.SysFont("Arial", 14)
            self.font_small = pygame.font.SysFont("Arial", 14)
        except:
            self.font_title = pygame.font.Font(None, 40)
            self.font_sub = pygame.font.Font(None, 24)
            self.font_text = pygame.font.Font(None, 18)
            self.font_bold = pygame.font.Font(None, 18)
            self.font_hint = pygame.font.Font(None, 14)
            self.font_small = pygame.font.Font(None, 14)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    self.tab = "opportunities" if self.tab == "agents" else "agents"
                    self.sel_idx = 0
                elif event.key in (pygame.K_UP, pygame.K_w):
                    limit = len(self.agents) if self.tab == "agents" else len(career_manager.agent_recommendations)
                    if limit > 0: self.sel_idx = (self.sel_idx - 1) % limit
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    limit = len(self.agents) if self.tab == "agents" else len(career_manager.agent_recommendations)
                    if limit > 0: self.sel_idx = (self.sel_idx + 1) % limit
                elif event.key == pygame.K_RETURN:
                    if self.tab == "agents":
                        self._hire_selected()
                    else:
                        self._request_formal_offer()
                elif event.key == pygame.K_ESCAPE:
                    from scenes.career_hub import CareerHubScene
                    self.manager.set_scene(CareerHubScene)

    def _hire_selected(self):
        agent = self.agents[self.sel_idx]
        curr_lvl = career_manager.agent.get("level", 0)
        
        if agent["level"] <= curr_lvl and agent["level"] != 0:
            self._set_msg("Ya tienes un agente igual o mejor.")
            return
        
        if agent["level"] > curr_lvl + 1:
            self._set_msg("Debes mejorar tus agentes paso a paso.")
            return

        if agent["level"] == 0:
            self._set_msg("Ya tienes lo básico.")
            return
            
        success, msg = career_manager.upgrade_agent()
        self._set_msg(msg)

    def _request_formal_offer(self):
        recs = career_manager.agent_recommendations
        if not recs: return
        rec = recs[self.sel_idx]
        if any(o["team_short"] == rec["team_short"] for o in career_manager.manager_offers):
            self._set_msg("Ya tienes una oferta formal de este club.")
            return
            
        career_manager.manager_offers.append({
            "team_short": rec["team_short"],
            "team_name": rec["team_name"],
            "salary": rec["salary"],
            "state": "pending",
            "expires_in": 7
        })
        career_manager.agent_recommendations.remove(rec)
        self.sel_idx = 0
        self._set_msg(f"Has pedido al agente que formalice con {rec['team_name']}.")

    def _set_msg(self, text):
        self.msg = text
        self.msg_timer = 120

    def update(self, dt):
        self.time += dt
        if self.msg_timer > 0:
            self.msg_timer -= 1

    def draw(self, surface):
        surface.fill((15, 20, 30))
        
        # Header
        header_rect = pygame.Rect(0, 0, WIDTH, 100)
        pygame.draw.rect(surface, (25, 30, 45), header_rect)
        title_txt = " MI REPRESENTANTE" if self.tab == "agents" else " OPORTUNIDADES / PROYECTOS"
        title = self.font_title.render(title_txt, True, (200, 200, 255))
        surface.blit(title, (40, 25))
        
        # Tabs
        tab_y = 110
        for i, tname in enumerate(["REPRESENTANTES", "OPORTUNIDADES"]):
            tid = "agents" if i == 0 else "opportunities"
            is_sel = (self.tab == tid)
            t_rect = pygame.Rect(40 + i*220, tab_y, 200, 35)
            bg = (50, 60, 90) if is_sel else (30, 35, 50)
            pygame.draw.rect(surface, bg, t_rect, border_radius=5)
            txt = self.font_bold.render(tname, True, WHITE if is_sel else UI_TEXT_DIM)
            surface.blit(txt, (t_rect.centerx - txt.get_width()//2, t_rect.centery - txt.get_height()//2))

        if self.tab == "agents":
            self._draw_agents(surface)
        else:
            self._draw_opportunities(surface)
        
        # Msg
        if self.msg_timer > 0:
            m_surf = self.font_bold.render(self.msg, True, UI_ACCENT)
            surface.blit(m_surf, (WIDTH//2 - m_surf.get_width()//2, HEIGHT - 80))
            
        hint_txt = "↑↓ Seleccionar  ·  ENTER Acción  ·  TAB Cambiar Pestaña  ·  ESC Volver"
        hint = self.font_hint.render(hint_txt, True, UI_TEXT_DIM)
        surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 30))

    def _draw_agents(self, surface):
        start_y = 170
        for i, a in enumerate(self.agents):
            is_sel = (self.sel_idx == i)
            is_owned = (career_manager.agent.get("level", 0) == a["level"])
            
            rect = pygame.Rect(40, start_y + i * 105, WIDTH - 80, 95)
            bg = (40, 50, 70) if is_sel else (30, 35, 50)
            pygame.draw.rect(surface, bg, rect, border_radius=10)
            
            if is_sel:
                pygame.draw.rect(surface, UI_ACCENT, rect, 2, border_radius=10)
            
            # Name & Price
            display_name = a["name"]
            if is_owned and a["level"] > 0:
                agent_prof = career_manager.career_stats.get("agent_profile", {})
                display_name = f"{agent_prof.get('name', a['name'])} ({a['name']})"
            name_surf = self.font_bold.render(display_name, True, (255, 215, 0) if is_owned else WHITE)
            surface.blit(name_surf, (rect.left + 20, rect.top + 12))
            
            price_txt = f"Coste: ${a['price']}M | Comisión: {a['commission']}%"
            p_surf = self.font_text.render(price_txt, True, UI_TEXT_DIM)
            surface.blit(p_surf, (rect.left + 20, rect.top + 40))
            
            desc_surf = self.font_text.render(a["desc"], True, (150, 200, 255))
            surface.blit(desc_surf, (rect.left + 20, rect.top + 65))
            
            if is_owned:
                owned_txt = self.font_bold.render("CONTRATADO", True, (100, 255, 100))
                surface.blit(owned_txt, (rect.right - 150, rect.top + 35))

    def _draw_opportunities(self, surface):
        recs = career_manager.agent_recommendations
        if not recs:
            empty = self.font_sub.render("No hay clubes contactando a tu agente por ahora.", True, UI_TEXT_DIM)
            surface.blit(empty, (WIDTH//2 - empty.get_width()//2, HEIGHT//2))
            return
            
        start_y = 170
        for i, r in enumerate(recs):
            is_sel = (self.sel_idx == i)
            rect = pygame.Rect(40, start_y + i * 160, WIDTH - 80, 150)
            bg = (40, 50, 70) if is_sel else (25, 30, 45)
            pygame.draw.rect(surface, bg, rect, border_radius=12)
            if is_sel: pygame.draw.rect(surface, UI_ACCENT, rect, 2, border_radius=12)
            
            # Team
            team_txt = self.font_sub.render(f"🛡️ {r['team_name']}", True, (255, 215, 0))
            surface.blit(team_txt, (rect.left + 20, rect.top + 15))
            
            # Sporting Project
            proj_title = self.font_bold.render(f"PROYECTO: {r['project_name']}", True, (100, 255, 100))
            surface.blit(proj_title, (rect.left + 20, rect.top + 55))
            proj_desc = self.font_text.render(r['project_desc'], True, WHITE)
            surface.blit(proj_desc, (rect.left + 20, rect.top + 80))
            
            # Economic Project
            econ_title = self.font_bold.render("PROYECTO ECONÓMICO", True, (80, 200, 255))
            surface.blit(econ_title, (rect.left + 450, rect.top + 55))
            econ_sal = self.font_text.render(f"Sueldo propuesto: ${r['salary']}M", True, WHITE)
            surface.blit(econ_sal, (rect.left + 450, rect.top + 80))
            econ_desc = self.font_small.render(r['economic_desc'], True, UI_TEXT_DIM)
            surface.blit(econ_desc, (rect.left + 450, rect.top + 105))
            
            if is_sel:
                hint = self.font_small.render("ENTER para solicitar oferta formal", True, UI_ACCENT)
                surface.blit(hint, (rect.right - 230, rect.top + 20))
