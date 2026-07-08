import pygame
import math
from settings import *
from data.career_manager import career_manager

class CareerSlotsScene:
    """Scene for selecting a save/load slot."""
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        self.mode = self.context.get("slot_mode", "load") # "load" or "save"
        self.career_type = self.context.get("career_type", "manager") # "manager" or "player"
        self.time = 0
        self.sel_idx = 0
        
        from data.career_manager import career_manager
        
        # When saving mid-game, career_type must match current mode
        if self.mode == "save":
            self.career_type = "player" if career_manager.mode == "player" else "manager"
            
        self.slot_offset = 0 if self.career_type == "manager" else 10
        self.slots = career_manager.get_slots_metadata()
        self.confirm_overwrite = False
        self.confirm_delete = False
        
        try:
            self.font_title = pygame.font.SysFont("Impact", 44)
            self.font_sub = pygame.font.SysFont("Arial", 26, bold=True)
            self.font_name = pygame.font.SysFont("Arial", 22, bold=True)
            self.font_text = pygame.font.SysFont("Arial", 16)
            self.font_hint = pygame.font.SysFont("Arial", 14)
        except:
            self.font_title = pygame.font.Font(None, 44)
            self.font_sub = pygame.font.Font(None, 26)
            self.font_name = pygame.font.Font(None, 22)
            self.font_text = pygame.font.Font(None, 16)
            self.font_hint = pygame.font.Font(None, 14)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.confirm_overwrite:
                    if event.key == pygame.K_RETURN:
                        self._execute_action(self._get_real_slot())
                    elif event.key == pygame.K_ESCAPE or event.key == pygame.K_n:
                        self.confirm_overwrite = False
                elif self.confirm_delete:
                    if event.key == pygame.K_RETURN:
                        from data.career_manager import career_manager
                        career_manager.delete_career(self._get_real_slot())
                        self.slots = career_manager.get_slots_metadata()
                        self.confirm_delete = False
                    elif event.key == pygame.K_ESCAPE or event.key == pygame.K_n:
                        self.confirm_delete = False
                else:
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        self.sel_idx = max(0, self.sel_idx - 1)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.sel_idx = min(9, self.sel_idx + 1)
                    elif event.key in (pygame.K_UP, pygame.K_w):
                        self.sel_idx = max(0, self.sel_idx - 5)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.sel_idx = min(9, self.sel_idx + 5)
                    elif event.key == pygame.K_RETURN:
                        self._on_slot_click(self._get_real_slot())
                    elif event.key in (pygame.K_DELETE, pygame.K_BACKSPACE):
                        slot_id = self._get_real_slot()
                        if self.slots.get(slot_id):
                            self.confirm_delete = True
                    elif event.key == pygame.K_ESCAPE:
                        self._go_back()

    def _get_real_slot(self):
        return self.sel_idx + 1 + self.slot_offset

    def _go_back(self):
        if self.mode == "save":
            from scenes.career_hub import CareerHubScene
            self.manager.set_scene(CareerHubScene)
        else:
            from scenes.career_setup import CareerSetupScene
            self.manager.set_scene(CareerSetupScene)

    def _on_slot_click(self, slot_id):
        meta = self.slots.get(slot_id)
        if self.mode == "save":
            if meta:
                self.confirm_overwrite = True
            else:
                self._execute_action(slot_id)
        else:
            if meta:
                self._execute_action(slot_id)

    def _execute_action(self, slot_id):
        from data.career_manager import career_manager
        if self.mode == "save":
            career_manager.save_career(slot_id)
            from scenes.career_hub import CareerHubScene
            self.manager.set_scene(CareerHubScene)
        else:
            if career_manager.load_career(slot_id):
                from scenes.career_hub import CareerHubScene
                self.manager.set_scene(CareerHubScene)

    def update(self, dt):
        self.time += dt

    def draw(self, surface):
        surface.fill((15, 20, 30))
        
        # Header
        base_title = "GUARDAR PARTIDA" if self.mode == "save" else "CARGAR PARTIDA"
        mode_str = "DE MÁNAGER" if self.career_type == "manager" else "DE JUGADOR"
        title = self.font_title.render(f"{base_title} {mode_str}", True, UI_ACCENT)
        surface.blit(title, (WIDTH//2 - title.get_width()//2, 50))
        
        # Slots Grid (2 rows of 5)
        slot_w = 220
        slot_h = 240
        gap_x = 20
        gap_y = 20
        total_w = slot_w * 5 + gap_x * 4
        start_x = (WIDTH - total_w) // 2
        start_y = 150
        
        from data.career_manager import career_manager
        
        for i in range(10):
            slot_id = i + 1 + self.slot_offset
            meta = self.slots.get(slot_id)
            is_sel = (self.sel_idx == i)
            
            col = i % 5
            row = i // 5
            
            x = start_x + col * (slot_w + gap_x)
            y = start_y + row * (slot_h + gap_y)
            rect = pygame.Rect(x, y, slot_w, slot_h)
            
            bg = UI_CARD_HOVER if is_sel else UI_CARD_BG
            pygame.draw.rect(surface, bg, rect, border_radius=10)
            
            if is_sel:
                pulse = (math.sin(self.time * 5) + 1) / 2
                bc = (int(0 + pulse * 100), int(200 + pulse * 55), int(150 + pulse * 105))
                pygame.draw.rect(surface, bc, rect, 3, border_radius=10)
            else:
                pygame.draw.rect(surface, (50, 55, 70), rect, 1, border_radius=10)
            
            # Slot Number Label
            lbl = self.font_hint.render(f"SLOT {slot_id}", True, UI_TEXT_DIM)
            surface.blit(lbl, (rect.left + 10, rect.top + 10))
            
            if meta:
                # Name
                name_t = self.font_name.render(meta["name"].upper(), True, WHITE)
                # scale if too long
                if name_t.get_width() > slot_w - 20:
                    name_t = pygame.transform.scale(name_t, (slot_w - 20, name_t.get_height()))
                surface.blit(name_t, (rect.centerx - name_t.get_width()//2, rect.top + 40))
                
                # Team Badge
                from data.teams import draw_badge
                t_obj = career_manager.get_team_by_short(meta["team_short"])
                if t_obj:
                    draw_badge(surface, t_obj, rect.centerx, rect.top + 110, size=50)
                
                team_t = self.font_text.render(meta["team"], True, UI_ACCENT_ALT)
                surface.blit(team_t, (rect.centerx - team_t.get_width()//2, rect.top + 160))
                
                # Date
                date_t = self.font_hint.render(f"Año {meta['year']} | {meta['date']}", True, UI_TEXT_DIM)
                surface.blit(date_t, (rect.centerx - date_t.get_width()//2, rect.top + 190))
                
                # Autosave indicator if it's the current slot
                if meta.get("autosave"):
                    ai = self.font_hint.render("AUTOSAVE", True, (255, 200, 100))
                    surface.blit(ai, (rect.centerx - ai.get_width()//2, rect.top + 215))
            else:
                empty_t = self.font_sub.render("VACÍO", True, (60, 65, 80))
                surface.blit(empty_t, (rect.centerx - empty_t.get_width()//2, rect.centery - empty_t.get_height()//2))

        # Confirmation Overlay
        if self.confirm_overwrite or self.confirm_delete:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            surface.blit(overlay, (0,0))
            
            box = pygame.Rect(WIDTH//2 - 250, HEIGHT//2 - 80, 500, 160)
            pygame.draw.rect(surface, (35, 40, 60), box, border_radius=12)
            pygame.draw.rect(surface, (255, 100, 80) if self.confirm_overwrite else (220, 50, 50), box, 2, border_radius=12)
            
            msg_text = "¿SOBREESCRIBIR PARTIDA?" if self.confirm_overwrite else "¿BORRAR PARTIDA DEFINITIVAMENTE?"
            msg = self.font_sub.render(msg_text, True, WHITE)
            surface.blit(msg, (box.centerx - msg.get_width()//2, box.top + 30))
            
            hint = self.font_text.render("ENTER: Sí  ·  ESC: Cancelar", True, UI_TEXT_DIM)
            surface.blit(hint, (box.centerx - hint.get_width()//2, box.top + 90))

        # Footer Hint
        fh = self.font_hint.render("FLECHAS: Navegar  ·  ENTER: Seleccionar  ·  SUPR/DEL: Borrar  ·  ESC: Volver", True, UI_TEXT_DIM)
        surface.blit(fh, (WIDTH//2 - fh.get_width()//2, HEIGHT - 30))
