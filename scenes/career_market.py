import pygame
from settings import *
from data.career_manager import career_manager

class CareerMarketScene:
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        
        self.team = career_manager.player_team
        self.roster = career_manager.rosters.get(self.team["short"], [])
        
        self.neg_list = career_manager.negotiations
        
        self.scroll_y = 0
        self.selected_idx = 0
        
        self.msg = ""
        self.msg_timer = 0
        
        try:
            self.font_title = pygame.font.SysFont("Impact", 36)
            self.font_btn = pygame.font.SysFont("Arial", 22, bold=True)
            self.font_text = pygame.font.SysFont("Arial", 16)
            self.font_bold = pygame.font.SysFont("Arial", 16, bold=True)
            self.font_hint = pygame.font.SysFont("Arial", 14)
        except:
            self.font_title = pygame.font.Font(None, 36)
            self.font_btn = pygame.font.Font(None, 22)
            self.font_text = pygame.font.Font(None, 16)
            self.font_bold = pygame.font.Font(None, 16)
            self.font_hint = pygame.font.Font(None, 14)

    def handle_events(self, events):
        max_idx = len(self.neg_list) - 1
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_w):
                    self.selected_idx = max(0, self.selected_idx - 1)
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    self.selected_idx = min(max_idx, self.selected_idx + 1)
                elif event.key == pygame.K_RETURN:
                    self._resolve_negotiation()
                elif event.key == pygame.K_DELETE or event.key == pygame.K_BACKSPACE:
                    self._cancel_negotiation()
                elif event.key == pygame.K_SPACE:
                    from scenes.career_search import CareerSearchScene
                    self.manager.set_scene(CareerSearchScene)
                elif event.key == pygame.K_ESCAPE:
                    from scenes.career_hub import CareerHubScene
                    self.manager.set_scene(CareerHubScene)

    def _resolve_negotiation(self):
        if not self.neg_list: return
        neg = self.neg_list[self.selected_idx]
        
        if neg["state"] == "accepted":
            if self.team["budget"] >= neg["bid"]:
                self.team["budget"] -= neg["bid"]
                # Move
                t_short = neg["t_short"]
                orig_rost = career_manager.rosters.get(t_short, [])
                for i, op in enumerate(orig_rost):
                    if op["name"] == neg["p_name"]:
                        popped = orig_rost.pop(i)
                        self.roster.append(popped)
                        seller = career_manager.get_team_by_short(t_short)
                        if seller and "budget" in seller:
                            seller["budget"] += neg["bid"]
                        break
                
                self.neg_list.pop(self.selected_idx)
                
                # Presentar al nuevo fichaje
                from scenes.presentation import PresentationScene
                from scenes.career_market import CareerMarketScene
                self.manager.set_scene(PresentationScene, context={
                    "team": self.team,
                    "player_name": popped["name"],
                    "is_manager": False,
                    "number": popped.get("num", 99),
                    "next_scene": CareerMarketScene
                })
            else:
                self.msg = "Presupuesto insuficiente para firmar."
                self.msg_timer = 2.0
                
        elif neg["state"] == "counter":
            # Match counter offer
            if self.team["budget"] >= neg["counter_val"]:
                neg["bid"] = neg["counter_val"]
                neg["state"] = "pending"
                neg["wait"] = 1
                self.msg = "Contraoferta igualada. Esperando papeleo (1 Sem)."
                self.msg_timer = 2.0
            else:
                self.msg = "No tienes presupuesto para igualar."
                self.msg_timer = 2.0
                
        else:
            self.msg = "Trato inactivo o en espera. Usa SUprimir para cancelar."
            self.msg_timer = 2.0

    def _cancel_negotiation(self):
        if not self.neg_list: return
        self.neg_list.pop(self.selected_idx)
        if self.selected_idx > 0: self.selected_idx -= 1
        self.msg = "Negociación cancelada."
        self.msg_timer = 2.0

    def update(self, dt):
        if self.msg_timer > 0:
            self.msg_timer -= dt

    def draw(self, surface):
        surface.fill((15, 18, 25))
        
        title = self.font_title.render("NEGOCIACIONES ACTIVAS (MERCADO)", True, UI_ACCENT)
        surface.blit(title, (50, 20))
        
        b_lbl = self.font_text.render(f"Presupuesto: ${self.team.get('budget', 0)}M", True, (100, 255, 150))
        surface.blit(b_lbl, (WIDTH - 250, 35))
        
        if not self.neg_list:
            ns = self.font_text.render("No tienes pujas ni tratos activos.", True, UI_TEXT_DIM)
            surface.blit(ns, (50, 100))
        else:
            y = 100
            for i, neg in enumerate(self.neg_list):
                is_sel = (self.selected_idx == i)
                rect = pygame.Rect(50, y + i * 85, WIDTH - 100, 75)
                c_bg = UI_CARD_HOVER if is_sel else UI_CARD_BG
                
                pygame.draw.rect(surface, c_bg, rect, border_radius=8)
                if is_sel:
                    pygame.draw.rect(surface, UI_ACCENT, rect, 2, border_radius=8)
                    
                ns = self.font_btn.render(f"📌 Objetivo: {neg['p_name']} ({neg['t_short']})", True, WHITE)
                surface.blit(ns, (rect.left + 20, rect.top + 10))
                
                v_lbl = f"💰 Tu Oferta: ${neg['bid']}M"
                vs = self.font_text.render(v_lbl, True, (200, 200, 200))
                surface.blit(vs, (rect.left + 20, rect.top + 40))
                
                # Check status
                status = neg["state"]
                sc = WHITE
                st_txt = ""
                if status == "pending":
                    st_txt = f"⏳ Esperando ({neg['wait']} sem)..."
                    sc = (255, 215, 0)
                elif status == "accepted":
                    st_txt = "✅ ¡OFERTA ACEPTADA! (ENTER: Firmar)"
                    sc = (100, 255, 100)
                elif status == "counter":
                    st_txt = f"🔄 Contraoferta: ${neg['counter_val']}M (ENTER: Igualar)"
                    sc = (0, 200, 255)
                elif status == "rejected":
                    st_txt = f"❌ Rechazado. (Espera: {neg['cooldown']} sem)"
                    sc = (255, 100, 100)
                    
                sts = self.font_btn.render(st_txt, True, sc)
                surface.blit(sts, (rect.right - sts.get_width() - 20, rect.centery - sts.get_height()//2))

        if self.msg_timer > 0:
            ms = self.font_btn.render(self.msg, True, (255, 255, 100))
            surface.blit(ms, (WIDTH//2 - ms.get_width()//2, 80))
            
        hint = self.font_hint.render("SPACE: Red Glogal de Ojeadores (Nuevo Fichaje)  ·  ENTER: Interactuar  ·  DEL: Cancelar  ·  ESC: Volver", True, UI_TEXT_DIM)
        surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 30))
