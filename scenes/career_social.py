import pygame
import math
import random
from settings import *
from data.career_manager import career_manager

class CareerSocialScene:
    """Scene for the Social Media platform in Player Career Mode."""
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        
        # Tabs inside Social Media
        self.sub_tabs = [
            {"id": "feed", "name": "FEED GLOBAL", "icon": "Feed"},
            {"id": "dms", "name": "MENSAJES PRIVADOS", "icon": "DMs"},
            {"id": "relations", "name": "RELACIONES", "icon": "Rel"},
            {"id": "cm", "name": "GESTIÓN DE CM", "icon": "CM"}
        ]
        self.tab_idx = 0
        
        # Selection states
        self.post_scroll = 0
        self.dm_scroll = 0
        self.dm_focus = "list"  # "list" (lista de chats) o "chat" (responder en chat activo)
        self.selected_dm_idx = 0
        self.selected_cm_idx = 0
        self.selected_choice_idx = 0 # Active option for DM reply
        self.selected_relation_idx = 0
        self.relation_scroll = 0
        
        # Action states
        self.show_post_popup = False
        self.post_popup_idx = 0 # 0: Profesional, 1: Picante
        
        # Message/Status banner
        self.msg = ""
        self.msg_timer = 0.0
        self.time = 0.0
        
        # CM specifications
        self.cm_options = [
            {"tier": 0, "name": "Autogestión (Tú mismo)", "cost": 0.0, "desc": "Publica manualmente. Sin bonificaciones de relaciones ni patrocinio automático."},
            {"tier": 1, "name": "CM Junior", "cost": 0.001, "desc": "Sube un post positivo tras partidos. +10% fama ganada. Coste: $1k/semana."},
            {"tier": 2, "name": "Agencia Profesional", "cost": 0.004, "desc": "Posts post-partido y relaciones. +20% fama, +5% confianza de DT. Coste: $4k/semana."},
            {"tier": 3, "name": "Gabinete RRPP Élite", "cost": 0.015, "desc": "Gestión total. Acepta patrocinios menores automáticos (+dinero). +30% fama, +10% DT. Coste: $15k/semana."}
        ]
        
        # Font initialization
        try:
            self.font_title = pygame.font.SysFont("Impact", 36)
            self.font_sub = pygame.font.SysFont("Arial", 22, bold=True)
            self.font_bold = pygame.font.SysFont("Arial", 16, bold=True)
            self.font_text = pygame.font.SysFont("Arial", 16)
            self.font_small = pygame.font.SysFont("Arial", 14)
            self.font_hint = pygame.font.SysFont("Arial", 12)
            self.font_icon = pygame.font.SysFont("Segoe UI Emoji", 26)
            self.font_big_emoji = pygame.font.SysFont("Segoe UI Emoji", 50)
        except:
            self.font_title = pygame.font.Font(None, 36)
            self.font_sub = pygame.font.Font(None, 22)
            self.font_bold = pygame.font.Font(None, 16)
            self.font_text = pygame.font.Font(None, 16)
            self.font_small = pygame.font.Font(None, 14)
            self.font_hint = pygame.font.Font(None, 12)
            self.font_icon = pygame.font.Font(None, 26)
            self.font_big_emoji = pygame.font.Font(None, 50)

        # Make sure social media is initialized
        career_manager._ensure_social_media_exists()

        # Check if nickname setup is needed
        sm = career_manager.career_stats["social_media"]
        self.setting_up_nickname = False
        self.nickname_input = ""
        if not sm.get("player_handle"):
            self.setting_up_nickname = True
            p_name = career_manager.career_player["name"] if career_manager.career_player else "jugador"
            # Normalize suggestion
            import unicodedata
            normalized = unicodedata.normalize('NFKD', p_name).encode('ASCII', 'ignore').decode('utf-8')
            suggested = ""
            for char in normalized.lower():
                if char.isalnum() or char == "_":
                    suggested += char
            self.nickname_input = suggested[:15]

    def handle_events(self, events):
        sm = career_manager.career_stats["social_media"]
        posts = sm["posts"]
        dms = sm["dms"]

        # Intercept events if setting up nickname
        if self.setting_up_nickname:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        from scenes.career_hub import CareerHubScene
                        self.manager.set_scene(CareerHubScene)
                    elif event.key == pygame.K_BACKSPACE:
                        self.nickname_input = self.nickname_input[:-1]
                    elif event.key == pygame.K_RETURN:
                        if len(self.nickname_input) >= 3:
                            sm["player_handle"] = f"@{self.nickname_input.lower()}"
                            self.setting_up_nickname = False
                            self._set_msg("¡Nickname guardado! Bienvenido a Fútbol Social.")
                        else:
                            self._set_msg("El nickname debe tener al menos 3 caracteres.")
                    else:
                        ch = event.unicode.lower()
                        if len(ch) == 1 and (ch.isalnum() or ch == "_") and len(self.nickname_input) < 15:
                            self.nickname_input += ch
            return
        
        # Handle Popups
        if self.show_post_popup:
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE):
                        self.show_post_popup = False
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        self.post_popup_idx = 0
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.post_popup_idx = 1
                    elif event.key == pygame.K_RETURN:
                        tone = "professional" if self.post_popup_idx == 0 else "spicy"
                        if career_manager.post_custom_message(tone):
                            self._set_msg("¡Publicación enviada con éxito!")
                        self.show_post_popup = False
            return

        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_TAB, pygame.K_e):
                    self.tab_idx = (self.tab_idx + 1) % len(self.sub_tabs)
                    self.selected_dm_idx = 0
                    self.selected_choice_idx = 0
                    self.selected_relation_idx = 0
                    self.relation_scroll = 0
                    self.dm_scroll = 0
                elif event.key == pygame.K_q:
                    self.tab_idx = (self.tab_idx - 1) % len(self.sub_tabs)
                    self.selected_dm_idx = 0
                    self.selected_choice_idx = 0
                    self.selected_relation_idx = 0
                    self.relation_scroll = 0
                    self.dm_scroll = 0
                elif event.key == pygame.K_ESCAPE:
                    from scenes.career_hub import CareerHubScene
                    self.manager.set_scene(CareerHubScene)
                
                # Tab 1: Feed
                elif self.sub_tabs[self.tab_idx]["id"] == "feed":
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.post_scroll = max(0, self.post_scroll - 1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        if len(posts) > 3:
                            self.post_scroll = min(len(posts) - 3, self.post_scroll + 1)
                    elif event.key == pygame.K_c:
                        self.show_post_popup = True
                        self.post_popup_idx = 0
                
                # Tab 2: DMs
                elif self.sub_tabs[self.tab_idx]["id"] == "dms":
                    if self.dm_focus == "list":
                        if event.key in (pygame.K_UP, pygame.K_w):
                            if dms:
                                self.selected_dm_idx = (self.selected_dm_idx - 1) % len(dms)
                                self.selected_choice_idx = 0
                                # Auto-scroll view
                                visible_count = 6
                                if self.selected_dm_idx < self.dm_scroll:
                                    self.dm_scroll = self.selected_dm_idx
                                elif self.selected_dm_idx >= self.dm_scroll + visible_count:
                                    self.dm_scroll = self.selected_dm_idx - visible_count + 1
                                self.dm_scroll = max(0, min(self.dm_scroll, len(dms) - visible_count))
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            if dms:
                                self.selected_dm_idx = (self.selected_dm_idx + 1) % len(dms)
                                self.selected_choice_idx = 0
                                # Auto-scroll view
                                visible_count = 6
                                if self.selected_dm_idx < self.dm_scroll:
                                    self.dm_scroll = self.selected_dm_idx
                                elif self.selected_dm_idx >= self.dm_scroll + visible_count:
                                    self.dm_scroll = self.selected_dm_idx - visible_count + 1
                                self.dm_scroll = max(0, min(self.dm_scroll, len(dms) - visible_count))
                        elif event.key in (pygame.K_RIGHT, pygame.K_d, pygame.K_RETURN):
                            if dms:
                                active_dm = dms[self.selected_dm_idx]
                                # Mark as read when opening the conversation
                                if active_dm["status"] == "unread":
                                    active_dm["status"] = "read"
                                self.dm_focus = "chat"
                                self.selected_choice_idx = 0
                    else:  # self.dm_focus == "chat"
                        if event.key in (pygame.K_UP, pygame.K_w):
                            if dms:
                                active_dm = dms[self.selected_dm_idx]
                                if active_dm["status"] in ("unread", "read") and active_dm.get("choices"):
                                    self.selected_choice_idx = (self.selected_choice_idx - 1) % len(active_dm["choices"])
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            if dms:
                                active_dm = dms[self.selected_dm_idx]
                                if active_dm["status"] in ("unread", "read") and active_dm.get("choices"):
                                    self.selected_choice_idx = (self.selected_choice_idx + 1) % len(active_dm["choices"])
                        elif event.key in (pygame.K_LEFT, pygame.K_a, pygame.K_ESCAPE):
                            self.dm_focus = "list"
                        elif event.key == pygame.K_RETURN:
                            if dms:
                                active_dm = dms[self.selected_dm_idx]
                                if active_dm["status"] in ("unread", "read") and active_dm.get("choices"):
                                    success = career_manager.reply_to_dm(active_dm["id"], self.selected_choice_idx)
                                    if success:
                                        self._set_msg("Respuesta enviada y consecuencias aplicadas.")
                                        self.selected_choice_idx = 0
                                        self.dm_focus = "list"
                
                # Tab: Relations
                elif self.sub_tabs[self.tab_idx]["id"] == "relations":
                    relationships_list = sorted(list(career_manager.career_stats.get("relationships", {}).items()), key=lambda x: x[1].get("name", ""))
                    if relationships_list:
                        if event.key in (pygame.K_UP, pygame.K_w):
                            self.selected_relation_idx = (self.selected_relation_idx - 1) % len(relationships_list)
                            visible_count = 6
                            if self.selected_relation_idx < self.relation_scroll:
                                self.relation_scroll = self.selected_relation_idx
                            elif self.selected_relation_idx >= self.relation_scroll + visible_count:
                                self.relation_scroll = self.selected_relation_idx - visible_count + 1
                            self.relation_scroll = max(0, min(self.relation_scroll, len(relationships_list) - visible_count))
                        elif event.key in (pygame.K_DOWN, pygame.K_s):
                            self.selected_relation_idx = (self.selected_relation_idx + 1) % len(relationships_list)
                            visible_count = 6
                            if self.selected_relation_idx < self.relation_scroll:
                                self.relation_scroll = self.selected_relation_idx
                            elif self.selected_relation_idx >= self.relation_scroll + visible_count:
                                self.relation_scroll = self.selected_relation_idx - visible_count + 1
                            self.relation_scroll = max(0, min(self.relation_scroll, len(relationships_list) - visible_count))

                # Tab 3: CM Manager
                elif self.sub_tabs[self.tab_idx]["id"] == "cm":
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.selected_cm_idx = (self.selected_cm_idx - 1) % len(self.cm_options)
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.selected_cm_idx = (self.selected_cm_idx + 1) % len(self.cm_options)
                    elif event.key == pygame.K_RETURN:
                        # Hire CM
                        selected_cm = self.cm_options[self.selected_cm_idx]
                        if sm["cm_tier"] == selected_cm["tier"]:
                            self._set_msg("Ya tienes contratado este nivel de CM.")
                        else:
                            sm["cm_tier"] = selected_cm["tier"]
                            self._set_msg(f"¡Has contratado a: {selected_cm['name']}!")
                    elif event.key == pygame.K_1:
                        sm["strategy"] = "professional"
                        self._set_msg("Estrategia cambiada a Profesional / Corporativa.")
                    elif event.key == pygame.K_2:
                        sm["strategy"] = "spicy"
                        self._set_msg("Estrategia cambiada a Picante / Hype.")

    def _set_msg(self, text):
        self.msg = text
        self.msg_timer = 2.0

    def update(self, dt):
        self.time += dt
        if self.msg_timer > 0:
            self.msg_timer -= dt

    def draw(self, surface):
        if self.setting_up_nickname:
            self._draw_nickname_setup(surface)
            return

        sm = career_manager.career_stats["social_media"]
        if self.sub_tabs[self.tab_idx]["id"] == "feed":
            for post in sm.get("posts", []):
                post["read"] = True

        surface.fill((10, 12, 20))
        
        # Draw background pattern/grid
        for x in range(0, WIDTH, 80):
            pygame.draw.line(surface, (15, 20, 35), (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, 80):
            pygame.draw.line(surface, (15, 20, 35), (0, y), (WIDTH, y), 1)
            
        # Draw top banner
        pygame.draw.rect(surface, (18, 22, 38), (0, 0, WIDTH, 100))
        pygame.draw.rect(surface, UI_ACCENT, (0, 97, WIDTH, 3))
        
        # Header Info
        title = self.font_title.render("FÚTBOL SOCIAL", True, WHITE)
        surface.blit(title, (50, 20))
        
        # Followers count
        sm = career_manager.career_stats["social_media"]
        f_count = f"Seguidores: {sm.get('followers', 1200):,}"
        f_surf = self.font_sub.render(f_count, True, (100, 255, 180))
        surface.blit(f_surf, (WIDTH - f_surf.get_width() - 50, 25))
        
        # Render Sub-Tabs
        tab_x = 50
        for i, t in enumerate(self.sub_tabs):
            is_sel = (self.tab_idx == i)
            t_rect = pygame.Rect(tab_x, 115, 200, 38)
            bg = (28, 38, 62) if is_sel else (15, 18, 30)
            pygame.draw.rect(surface, bg, t_rect, border_radius=8)
            if is_sel:
                pygame.draw.rect(surface, UI_ACCENT, t_rect, 1, border_radius=8)
                tc = WHITE
            else:
                tc = UI_TEXT_DIM
            
            lbl = self.font_bold.render(f"{t['icon']} {t['name']}", True, tc)
            surface.blit(lbl, (t_rect.centerx - lbl.get_width()//2, t_rect.centery - lbl.get_height()//2))

            # Notificaciones en la cabecera
            if t["id"] == "feed":
                unread_posts = sum(1 for post in sm.get("posts", []) if not post.get("read", True))
                if unread_posts > 0:
                    badge_w = self.font_hint.size(str(unread_posts))[0] + 10
                    badge_rect = pygame.Rect(t_rect.right - badge_w - 5, t_rect.top + 5, badge_w, 16)
                    pygame.draw.rect(surface, (255, 50, 50), badge_rect, border_radius=8)
                    btxt = self.font_hint.render(str(unread_posts), True, WHITE)
                    surface.blit(btxt, (badge_rect.centerx - btxt.get_width()//2, badge_rect.centery - btxt.get_height()//2))
            elif t["id"] == "dms":
                unread_dms = sum(1 for dm in sm.get("dms", []) if dm.get("status") == "unread")
                if unread_dms > 0:
                    badge_w = self.font_hint.size(str(unread_dms))[0] + 10
                    badge_rect = pygame.Rect(t_rect.right - badge_w - 5, t_rect.top + 5, badge_w, 16)
                    pygame.draw.rect(surface, (255, 50, 50), badge_rect, border_radius=8)
                    btxt = self.font_hint.render(str(unread_dms), True, WHITE)
                    surface.blit(btxt, (badge_rect.centerx - btxt.get_width()//2, badge_rect.centery - btxt.get_height()//2))

            tab_x += 220
            
        # Draw Banner Message
        if self.msg_timer > 0:
            msg_surf = self.font_bold.render(self.msg, True, (80, 255, 120))
            surface.blit(msg_surf, (WIDTH//2 - msg_surf.get_width()//2, 122))

        # Render Active Tab Content
        active_id = self.sub_tabs[self.tab_idx]["id"]
        if active_id == "feed":
            self._draw_feed_tab(surface)
        elif active_id == "dms":
            self._draw_dms_tab(surface)
        elif active_id == "relations":
            self._draw_relations_tab(surface)
        elif active_id == "cm":
            self._draw_cm_tab(surface)
            
        # Render Popups
        if self.show_post_popup:
            self._draw_post_popup(surface)

        # Bottom Hint Bar
        pygame.draw.rect(surface, (15, 18, 30), (0, HEIGHT - 45, WIDTH, 45))
        hint_text = "Q/E o TAB Cambiar Pestaña  ·  ↑↓ Navegar  ·  ENTER Seleccionar  ·  ESC Volver"
        if active_id == "feed":
            hint_text += "  ·  [C] Crear Publicación"
        elif active_id == "cm":
            hint_text += "  ·  [1] Estrategia PR  ·  [2] Estrategia Picante"
        elif active_id == "dms":
            if self.dm_focus == "list":
                hint_text = "↑↓ Seleccionar Chat  ·  ENTER/▶ Abrir Chat  ·  Q/E Cambiar Pestaña  ·  ESC Volver"
            else:
                hint_text = "↑↓ Seleccionar Respuesta  ·  ENTER Enviar  ·  ESC/◀ Lista de Chats"
            
        hint = self.font_hint.render(hint_text, True, UI_TEXT_DIM)
        surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 30))

    def _draw_feed_tab(self, surface):
        sm = career_manager.career_stats["social_media"]
        posts = sm["posts"]
        
        # Panel Left: Feed lists
        feed_rect = pygame.Rect(50, 170, WIDTH - 100, HEIGHT - 230)
        pygame.draw.rect(surface, (16, 20, 32), feed_rect, border_radius=12)
        pygame.draw.rect(surface, (45, 50, 70), feed_rect, 1, border_radius=12)
        
        if not posts:
            empty = self.font_sub.render("No hay publicaciones en tu feed aún.", True, UI_TEXT_DIM)
            surface.blit(empty, (feed_rect.centerx - empty.get_width()//2, feed_rect.centery - 10))
            return
            
        py = 185
        visible_posts = posts[self.post_scroll : self.post_scroll + 3]
        for i, post in enumerate(visible_posts):
            p_rect = pygame.Rect(70, py, feed_rect.width - 40, 120)
            
            # Post background based on type
            colors = {
                "user": (30, 42, 60),
                "media": (20, 24, 40),
                "fan": (26, 28, 42),
                "club": (32, 22, 45)
            }
            bg_c = colors.get(post.get("type", "fan"), (20, 24, 40))
            pygame.draw.rect(surface, bg_c, p_rect, border_radius=8)
            pygame.draw.rect(surface, (55, 62, 85), p_rect, 1, border_radius=8)
            
            # Icon Profile
            pygame.draw.circle(surface, UI_ACCENT, (p_rect.left + 35, p_rect.top + 35), 20)
            try:
                # First letter of name as icon
                letter = post["author"][0].upper()
                let_s = self.font_bold.render(letter, True, BLACK)
                surface.blit(let_s, (p_rect.left + 35 - let_s.get_width()//2, p_rect.top + 35 - let_s.get_height()//2))
            except: pass
            
            # Author, handle & Date
            auth_str = f"{post['author']} "
            auth_s = self.font_bold.render(auth_str, True, WHITE)
            surface.blit(auth_s, (p_rect.left + 65, p_rect.top + 12))
            
            handle_s = self.font_small.render(post["handle"], True, (130, 145, 175))
            surface.blit(handle_s, (p_rect.left + 65 + auth_s.get_width(), p_rect.top + 13))
            
            date_s = self.font_hint.render(post["date"], True, UI_TEXT_DIM)
            surface.blit(date_s, (p_rect.right - date_s.get_width() - 15, p_rect.top + 12))
            
            # Content (Word Wrap)
            words = post["content"].split(' ')
            line = ""
            cy = p_rect.top + 40
            for w in words:
                test_line = line + w + " "
                if self.font_text.size(test_line)[0] < p_rect.width - 90:
                    line = test_line
                else:
                    surface.blit(self.font_text.render(line, True, UI_TEXT), (p_rect.left + 65, cy))
                    line = w + " "
                    cy += 20
            surface.blit(self.font_text.render(line, True, UI_TEXT), (p_rect.left + 65, cy))
            
            # Likes & Retweets
            stat_txt = f"Likes: {post['likes']:,}   RTs: {post['retweets']:,}"
            stat_s = self.font_small.render(stat_txt, True, (130, 160, 200))
            surface.blit(stat_s, (p_rect.left + 65, p_rect.bottom - 22))
            
            py += 135
            
        # Draw scrollbars if needed
        if len(posts) > 3:
            s_bar_h = feed_rect.height - 40
            s_btn_h = max(20, int(s_bar_h * (3.0 / len(posts))))
            s_btn_y = feed_rect.top + 20 + int((s_bar_h - s_btn_h) * (self.post_scroll / (len(posts) - 3.0)))
            pygame.draw.rect(surface, (30, 35, 50), (feed_rect.right - 15, feed_rect.top + 20, 6, s_bar_h), border_radius=3)
            pygame.draw.rect(surface, UI_ACCENT, (feed_rect.right - 15, s_btn_y, 6, s_btn_h), border_radius=3)

    def _draw_dms_tab(self, surface):
        sm = career_manager.career_stats["social_media"]
        dms = sm["dms"]
        
        # Left Panel: DM List (40% width)
        list_w = int((WIDTH - 100) * 0.4)
        list_rect = pygame.Rect(50, 170, list_w, HEIGHT - 230)
        pygame.draw.rect(surface, (16, 20, 32), list_rect, border_radius=12)
        list_bc = UI_ACCENT if self.dm_focus == "list" else (45, 50, 70)
        pygame.draw.rect(surface, list_bc, list_rect, 2 if self.dm_focus == "list" else 1, border_radius=12)
        
        # Right Panel: Chat Thread (60% width)
        chat_rect = pygame.Rect(list_rect.right + 15, 170, (WIDTH - 100) - list_w - 15, HEIGHT - 230)
        pygame.draw.rect(surface, (20, 25, 42), chat_rect, border_radius=12)
        chat_bc = UI_ACCENT if self.dm_focus == "chat" else (60, 68, 92)
        pygame.draw.rect(surface, chat_bc, chat_rect, 2 if self.dm_focus == "chat" else 1, border_radius=12)
        
        if not dms:
            empty = self.font_sub.render("No tienes mensajes privados.", True, UI_TEXT_DIM)
            surface.blit(empty, (WIDTH//2 - empty.get_width()//2, HEIGHT//2))
            return

        # Render Left DM List
        dy = 180
        for i, dm in enumerate(dms):
            if i >= self.dm_scroll and i < self.dm_scroll + 6:
                rect = pygame.Rect(60, dy, list_rect.width - 20, 62)
                is_sel = (self.selected_dm_idx == i)
                
                # Active highlight
                if is_sel:
                    pygame.draw.rect(surface, (38, 48, 76), rect, border_radius=8)
                    pygame.draw.rect(surface, UI_ACCENT, rect, 1, border_radius=8)
                else:
                    pygame.draw.rect(surface, (25, 30, 48), rect, border_radius=8)
                
                # Status indicators (unread dot)
                if dm["status"] == "unread":
                    pygame.draw.circle(surface, (255, 100, 100), (rect.left + 15, rect.top + 31), 5)
                
                # Profile initials icon
                pygame.draw.circle(surface, (100, 180, 255), (rect.left + 42, rect.top + 31), 18)
                p_initial = dm["sender"][0].upper()
                pi_s = self.font_bold.render(p_initial, True, BLACK)
                surface.blit(pi_s, (rect.left + 42 - pi_s.get_width()//2, rect.top + 31 - pi_s.get_height()//2))
                
                # Sender text
                s_name = dm["sender"]
                if len(s_name) > 16: s_name = s_name[:14] + "..."
                s_s = self.font_bold.render(s_name, True, WHITE)
                surface.blit(s_s, (rect.left + 70, rect.top + 12))
                
                s_handle = dm["handle"]
                if len(s_handle) > 18: s_handle = s_handle[:16] + "..."
                h_s = self.font_hint.render(s_handle, True, UI_TEXT_DIM)
                surface.blit(h_s, (rect.left + 70, rect.top + 33))
                
                dy += 68
                
        # Render Selected DM Chat on Right
        active_dm = dms[self.selected_dm_idx]
        
        # Sender Info Header inside chat
        pygame.draw.rect(surface, (28, 35, 58), (chat_rect.left + 1, chat_rect.top + 1, chat_rect.width - 2, 60), border_top_left_radius=12, border_top_right_radius=12)
        pygame.draw.line(surface, (60, 68, 92), (chat_rect.left, chat_rect.top + 60), (chat_rect.right, chat_rect.top + 60), 1)
        
        sender_disp = active_dm['sender']
        if len(sender_disp) > 12:
            sender_disp = sender_disp[:10] + "..."
        chat_hdr_txt = f" Chat con {sender_disp} ({active_dm['handle']})"
        chat_hdr = self.font_sub.render(chat_hdr_txt, True, WHITE)
        surface.blit(chat_hdr, (chat_rect.left + 20, chat_rect.top + 18))
        
        # Look up relationship
        rel = career_manager.career_stats.get("relationships", {}).get(active_dm["handle"])
        if rel:
            status_text = rel.get("status", "Conocido")
            if rel.get("on_maternity_leave"):
                status_text = "MATERNIDAD"
            pill_color, text_color = self._get_status_pill_colors(status_text)
            
            badge_w, badge_h = self.font_hint.size(status_text)
            badge_w += 12
            badge_h += 6
            badge_rect = pygame.Rect(chat_rect.left + 20 + chat_hdr.get_width() + 15, chat_rect.top + 20, badge_w, badge_h)
            pygame.draw.rect(surface, pill_color, badge_rect, border_radius=8)
            
            badge_s = self.font_hint.render(status_text, True, text_color)
            surface.blit(badge_s, (badge_rect.centerx - badge_s.get_width()//2, badge_rect.centery - badge_s.get_height()//2))
            
            # Draw small affinity icon next to the chat header
            affinity = rel.get("affinity", 0)
            if affinity >= 70:
                icon_char = "♥"
            elif affinity >= 40:
                icon_char = "+"
            elif affinity >= 0:
                icon_char = "."
            else:
                icon_char = "x"
                
            affinity_txt = f"Aff: {icon_char} ({affinity})"
            aff_s = self.font_small.render(affinity_txt, True, UI_ACCENT)
            surface.blit(aff_s, (badge_rect.right + 10, chat_rect.top + 20))
        
        # Message bubble (received)
        msg_bubble_rect = pygame.Rect(chat_rect.left + 25, chat_rect.top + 80, chat_rect.width - 50, 110)
        pygame.draw.rect(surface, (35, 42, 66), msg_bubble_rect, border_radius=10)
        
        # Message bubble text
        words = active_dm["message"].split(' ')
        line = ""
        m_y = msg_bubble_rect.top + 15
        for w in words:
            test_line = line + w + " "
            if self.font_text.size(test_line)[0] < msg_bubble_rect.width - 40:
                line = test_line
            else:
                surface.blit(self.font_text.render(line, True, WHITE), (msg_bubble_rect.left + 20, m_y))
                line = w + " "
                m_y += 22
        surface.blit(self.font_text.render(line, True, WHITE), (msg_bubble_rect.left + 20, m_y))
        
        # Choices panel (Bottom of chat) — vertical scrollable list
        if active_dm["status"] in ("unread", "read"):
            choices = active_dm["choices"]
            n_choices = len(choices)
            
            # Dynamic panel height: show up to 3.5 choices at a time, each ~38px
            choice_item_h = 38
            visible_items = min(n_choices, 4)
            panel_h = 30 + visible_items * choice_item_h + 10
            panel_rect = pygame.Rect(chat_rect.left + 20, chat_rect.bottom - panel_h - 10, chat_rect.width - 40, panel_h)
            pygame.draw.rect(surface, (25, 30, 48), panel_rect, border_radius=10)
            
            # Prompt
            prompt_text = "► SELECCIONA TU RESPUESTA (W/S o Flechas + ENTER):" if self.dm_focus == "chat" else "► ENTER / D / Flecha Derecha PARA RESPONDER MENSAJE:"
            prompt_s = self.font_small.render(prompt_text, True, UI_ACCENT)
            surface.blit(prompt_s, (panel_rect.left + 15, panel_rect.top + 8))
            
            # Scrollable vertical choice list
            choice_start_y = panel_rect.top + 28
            # Auto-scroll so selected choice is always visible
            max_scroll = max(0, n_choices - visible_items)
            ch_scroll = min(max(0, self.selected_choice_idx - visible_items + 2), max_scroll)
            
            # Clip area
            clip_rect = pygame.Rect(panel_rect.left + 8, choice_start_y, panel_rect.width - 16, visible_items * choice_item_h)
            
            for j in range(ch_scroll, min(ch_scroll + visible_items, n_choices)):
                c = choices[j]
                is_ch_sel = (self.selected_choice_idx == j) and (self.dm_focus == "chat")
                row_y = choice_start_y + (j - ch_scroll) * choice_item_h
                ch_rect = pygame.Rect(panel_rect.left + 12, row_y, panel_rect.width - 24, choice_item_h - 4)
                
                bg_ch = (45, 55, 90) if is_ch_sel else (30, 35, 55)
                pygame.draw.rect(surface, bg_ch, ch_rect, border_radius=6)
                if is_ch_sel:
                    pygame.draw.rect(surface, UI_ACCENT, ch_rect, 2, border_radius=6)
                    # Selection indicator arrow
                    arrow = self.font_small.render("▶", True, UI_ACCENT)
                    surface.blit(arrow, (ch_rect.left + 6, ch_rect.top + 10))
                
                # Choice number + text (truncate if too long)
                ch_prefix = f"{j + 1}. "
                ch_text = ch_prefix + c["text"]
                max_text_w = ch_rect.width - 30
                # Truncate to fit
                while self.font_small.size(ch_text)[0] > max_text_w and len(ch_text) > 10:
                    ch_text = ch_text[:len(ch_text) - 4] + "..."
                
                text_x = ch_rect.left + (22 if is_ch_sel else 10)
                ct_color = WHITE if is_ch_sel else (180, 180, 200)
                ct_s = self.font_small.render(ch_text, True, ct_color)
                surface.blit(ct_s, (text_x, ch_rect.top + 11))
            
            # Scroll indicators
            if ch_scroll > 0:
                up_arrow = self.font_small.render("▲ más opciones", True, UI_TEXT_DIM)
                surface.blit(up_arrow, (panel_rect.right - 120, choice_start_y - 2))
            if ch_scroll + visible_items < n_choices:
                dn_arrow = self.font_small.render("▼ más opciones", True, UI_TEXT_DIM)
                surface.blit(dn_arrow, (panel_rect.right - 120, panel_rect.bottom - 14))
        else:
            # Replied view
            rep_rect = pygame.Rect(chat_rect.left + 25, chat_rect.bottom - 120, chat_rect.width - 50, 90)
            pygame.draw.rect(surface, (20, 40, 30), rep_rect, border_radius=10)
            pygame.draw.rect(surface, (50, 150, 80), rep_rect, 1, border_radius=10)
            
            done_icon = self.font_title.render("[OK]", True, (100, 255, 120))
            surface.blit(done_icon, (rep_rect.left + 25, rep_rect.centery - done_icon.get_height()//2))
            
            reply_idx = active_dm.get("reply_selected")
            if reply_idx is not None and reply_idx < len(active_dm.get("choices", [])):
                sel_choice = active_dm["choices"][reply_idx]
                replied_txt = f"Respondido: \"{sel_choice['text']}\""
                if len(replied_txt) > 42: replied_txt = replied_txt[:39] + "..."
            else:
                replied_txt = "Conversación finalizada."
            
            r_s1 = self.font_bold.render("MENSAJE RESPONDIDO", True, (100, 255, 120))
            surface.blit(r_s1, (rep_rect.left + 90, rep_rect.top + 20))
            r_s2 = self.font_text.render(replied_txt, True, WHITE)
            surface.blit(r_s2, (rep_rect.left + 90, rep_rect.top + 45))

    def _draw_cm_tab(self, surface):
        sm = career_manager.career_stats["social_media"]
        cm_tier = sm.get("cm_tier", 0)
        strategy = sm.get("strategy", "professional")
        
        # Left Panel: Strategies and status (40% width)
        l_w = int((WIDTH - 100) * 0.4)
        l_rect = pygame.Rect(50, 170, l_w, HEIGHT - 230)
        pygame.draw.rect(surface, (16, 20, 32), l_rect, border_radius=12)
        pygame.draw.rect(surface, (45, 50, 70), l_rect, 1, border_radius=12)
        
        # Right Panel: CM Hire options (60% width)
        r_rect = pygame.Rect(l_rect.right + 15, 170, (WIDTH - 100) - l_w - 15, HEIGHT - 230)
        pygame.draw.rect(surface, (20, 25, 42), r_rect, border_radius=12)
        pygame.draw.rect(surface, (60, 68, 92), r_rect, 1, border_radius=12)
        
        # 1. Left Content: Current Status
        curr_cm = self.cm_options[cm_tier]["name"]
        lbl_cm = self.font_bold.render("COMMUNITY MANAGER ACTUAL:", True, UI_ACCENT)
        val_cm = self.font_sub.render(curr_cm, True, WHITE)
        surface.blit(lbl_cm, (l_rect.left + 25, l_rect.top + 25))
        surface.blit(val_cm, (l_rect.left + 25, l_rect.top + 50))
        
        # Active strategy
        lbl_strat = self.font_bold.render("ESTRATEGIA ACTIVA:", True, UI_ACCENT)
        strat_str = "Humilde / Profesional" if strategy == "professional" else "Picante / Hype"
        val_strat = self.font_sub.render(strat_str, True, WHITE)
        surface.blit(lbl_strat, (l_rect.left + 25, l_rect.top + 110))
        surface.blit(val_strat, (l_rect.left + 25, l_rect.top + 135))
        
        # Strategy selection helper
        help_strat = self.font_text.render("Pulsa [1] o [2] para cambiar estrategia.", True, UI_TEXT_DIM)
        surface.blit(help_strat, (l_rect.left + 25, l_rect.top + 175))
        
        # Strategy effects
        pygame.draw.rect(surface, (30, 35, 55), (l_rect.left + 20, l_rect.top + 220, l_rect.width - 40, 80), border_radius=8)
        if strategy == "professional":
            eff_t = "Aumenta la relación con el DT y Club.\nProporciona subidas estables de Prestigio."
        else:
            eff_t = "Grandes picos de Fama y Seguidores.\nDisminuye la confianza del DT por distracciones."
            
        for idx, line in enumerate(eff_t.split('\n')):
            surface.blit(self.font_small.render(line, True, (160, 200, 255)), (l_rect.left + 35, l_rect.top + 235 + idx*22))

        # 2. Right Content: Hire Options
        h_title = self.font_bold.render("MEJORAR / CONTRATAR EQUIPO DE REDES:", True, UI_ACCENT)
        surface.blit(h_title, (r_rect.left + 25, r_rect.top + 20))
        
        oy = r_rect.top + 50
        for i, opt in enumerate(self.cm_options):
            is_sel = (self.selected_cm_idx == i)
            is_hired = (cm_tier == opt["tier"])
            
            box = pygame.Rect(r_rect.left + 20, oy, r_rect.width - 40, 68)
            
            bg = (40, 48, 70) if is_sel else (25, 30, 48)
            pygame.draw.rect(surface, bg, box, border_radius=8)
            if is_sel:
                pygame.draw.rect(surface, UI_ACCENT, box, 1, border_radius=8)
            
            # CM details
            name_s = self.font_bold.render(opt["name"], True, (255, 215, 0) if is_hired else WHITE)
            surface.blit(name_s, (box.left + 15, box.top + 10))
            
            desc_s = self.font_small.render(opt["desc"], True, UI_TEXT_DIM if not is_sel else WHITE)
            surface.blit(desc_s, (box.left + 15, box.top + 33))
            
            # Cost or Active Badge
            if is_hired:
                active_s = self.font_bold.render("CONTRATADO", True, (80, 255, 120))
                surface.blit(active_s, (box.right - active_s.get_width() - 20, box.top + 22))
            else:
                price_txt = f"${opt['cost'] * 1000:.0f}k/sem" if opt["cost"] > 0 else "Gratis"
                cost_s = self.font_bold.render(price_txt, True, (255, 100, 100) if not is_sel else WHITE)
                surface.blit(cost_s, (box.right - cost_s.get_width() - 20, box.top + 22))
                
            oy += 74

    def _draw_post_popup(self, surface):
        # Draw translucent grey overlay
        ov = pygame.Surface((WIDTH, HEIGHT))
        ov.fill(BLACK)
        ov.set_alpha(150)
        surface.blit(ov, (0, 0))
        
        # Popup box
        box_w, box_h = 560, 300
        box = pygame.Rect(WIDTH//2 - box_w//2, HEIGHT//2 - box_h//2, box_w, box_h)
        pygame.draw.rect(surface, (20, 25, 45), box, border_radius=15)
        pygame.draw.rect(surface, UI_ACCENT, box, 2, border_radius=15)
        
        # Header
        hdr = self.font_sub.render("REDACTAR PUBLICACIÓN NUEVA", True, UI_ACCENT)
        surface.blit(hdr, (box.left + 30, box.top + 25))
        
        # Prompt
        pr = self.font_text.render("Elige el tono de tu publicación en tus redes:", True, WHITE)
        surface.blit(pr, (box.left + 30, box.top + 70))
        
        # Two options: Professional vs Spicy
        opts = [
            {"name": "[PRO] Profesional & Humilde", "desc": "Enfocado en el equipo, entrenamiento y respeto.\nEfectos: +DT Confianza, +Prestigio estable."},
            {"name": "[HOT] Picante & Hype", "desc": "Presume de tu nivel, busca provocar o agrandarte.\nEfectos: +++Prestigio/Fama, -DT Confianza, +Afición."}
        ]
        
        bx = box.left + 30
        opt_w = (box_w - 80) // 2
        for i, opt in enumerate(opts):
            is_sel = (self.post_popup_idx == i)
            o_rect = pygame.Rect(bx, box.top + 115, opt_w, 110)
            
            bg_c = (42, 50, 80) if is_sel else (28, 32, 52)
            pygame.draw.rect(surface, bg_c, o_rect, border_radius=8)
            if is_sel:
                pygame.draw.rect(surface, UI_ACCENT, o_rect, 2, border_radius=8)
                
            # Render Option Name
            name_s = self.font_bold.render(opt["name"], True, WHITE)
            surface.blit(name_s, (o_rect.left + 15, o_rect.top + 15))
            
            # Wrap description lines
            for idx, line in enumerate(opt["desc"].split('\n')):
                line_s = self.font_hint.render(line, True, UI_TEXT_DIM if not is_sel else (180, 210, 255))
                surface.blit(line_s, (o_rect.left + 15, o_rect.top + 45 + idx * 18))
                
            bx += opt_w + 20
            
        # Hint inside popup
        hint_s = self.font_hint.render("←/→ Seleccionar  ·  ENTER Publicar  ·  ESC Cancelar", True, UI_TEXT_DIM)
        surface.blit(hint_s, (box.centerx - hint_s.get_width()//2, box.bottom - 30))

    def _draw_nickname_setup(self, surface):
        surface.fill((10, 12, 20))
        
        # Grid lines in background
        for x in range(0, WIDTH, 80):
            pygame.draw.line(surface, (15, 20, 35), (x, 0), (x, HEIGHT), 1)
        for y in range(0, HEIGHT, 80):
            pygame.draw.line(surface, (15, 20, 35), (0, y), (WIDTH, y), 1)
            
        # Accent glows
        glow_surf = pygame.Surface((400, 400), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (0, 200, 150, 20), (200, 200), 200)
        surface.blit(glow_surf, (WIDTH//2 - 200, HEIGHT//2 - 250))
        
        # Center card
        card_w, card_h = 600, 380
        card = pygame.Rect(WIDTH//2 - card_w//2, HEIGHT//2 - card_h//2 - 30, card_w, card_h)
        
        # Glassmorphic card back
        pygame.draw.rect(surface, (18, 22, 38), card, border_radius=16)
        pygame.draw.rect(surface, UI_ACCENT, card, 2, border_radius=16)
        
        # Title
        title_text = "CREA TU IDENTIDAD DIGITAL"
        title_s = self.font_title.render(title_text, True, WHITE)
        surface.blit(title_s, (card.centerx - title_s.get_width()//2, card.top + 40))
        
        # Subtitle
        sub_text = "Elige tu @nickname personalizado para las redes sociales"
        sub_s = self.font_sub.render(sub_text, True, UI_ACCENT)
        surface.blit(sub_s, (card.centerx - sub_s.get_width()//2, card.top + 95))
        
        # Explanation paragraph
        desc_lines = [
            "Este alias se utilizará en tus publicaciones, menciones de prensa y",
            "mensajes directos con aficionados, clubes y otras celebridades.",
            "Usa letras, números y guiones bajos (máximo 15 caracteres)."
        ]
        curr_y = card.top + 140
        for line in desc_lines:
            line_s = self.font_text.render(line, True, UI_TEXT_DIM)
            surface.blit(line_s, (card.centerx - line_s.get_width()//2, curr_y))
            curr_y += 24
            
        # Input Box
        input_w, input_h = 420, 60
        input_rect = pygame.Rect(card.centerx - input_w//2, card.top + 230, input_w, input_h)
        pygame.draw.rect(surface, (12, 14, 24), input_rect, border_radius=8)
        pygame.draw.rect(surface, (60, 68, 92), input_rect, 1, border_radius=8)
        
        # Prepend '@' prefix and draw it in accent color, then input text
        prefix_s = self.font_bold.render("@", True, UI_ACCENT)
        surface.blit(prefix_s, (input_rect.left + 20, input_rect.centery - prefix_s.get_height()//2))
        
        cursor = "_" if int(self.time * 2.5) % 2 == 0 else ""
        typed_text = self.nickname_input + cursor
        text_s = self.font_bold.render(typed_text, True, WHITE)
        surface.blit(text_s, (input_rect.left + 20 + prefix_s.get_width() + 5, input_rect.centery - text_s.get_height()//2))
        
        # Validation feedback
        feedback_text = ""
        feedback_color = UI_TEXT_DIM
        if len(self.nickname_input) == 0:
            feedback_text = "Escribe un nickname para continuar..."
        elif len(self.nickname_input) < 3:
            feedback_text = "Demasiado corto (mínimo 3 caracteres)"
            feedback_color = (255, 100, 100)
        else:
            feedback_text = f"Tu dirección será: @{self.nickname_input}"
            feedback_color = (100, 255, 150)
            
        feed_s = self.font_small.render(feedback_text, True, feedback_color)
        surface.blit(feed_s, (card.centerx - feed_s.get_width()//2, input_rect.bottom + 8))
        
        # Bottom hint bar
        pygame.draw.rect(surface, (15, 18, 30), (0, HEIGHT - 45, WIDTH, 45))
        hint_text = "ENTER para confirmar nickname  ·  ESC para volver"
        hint = self.font_hint.render(hint_text, True, UI_TEXT_DIM)
        surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 30))
        
        # Message/Status banner
        if self.msg_timer > 0:
            msg_surf = self.font_bold.render(self.msg, True, (255, 100, 100))
            surface.blit(msg_surf, (WIDTH//2 - msg_surf.get_width()//2, card.bottom + 35))

    def _draw_relations_tab(self, surface):
        # Left Panel: Relations List (40% width)
        list_w = int((WIDTH - 100) * 0.4)
        list_rect = pygame.Rect(50, 170, list_w, HEIGHT - 230)
        pygame.draw.rect(surface, (16, 20, 32), list_rect, border_radius=12)
        pygame.draw.rect(surface, (45, 50, 70), list_rect, 1, border_radius=12)
        
        # Right Panel: Relation Details (60% width)
        details_rect = pygame.Rect(list_rect.right + 15, 170, (WIDTH - 100) - list_w - 15, HEIGHT - 230)
        pygame.draw.rect(surface, (20, 25, 42), details_rect, border_radius=12)
        pygame.draw.rect(surface, (60, 68, 92), details_rect, 1, border_radius=12)
        
        relationships_list = sorted(list(career_manager.career_stats.get("relationships", {}).items()), key=lambda x: x[1].get("name", ""))
        
        # Check bounds for safety
        if self.selected_relation_idx >= len(relationships_list):
            self.selected_relation_idx = max(0, len(relationships_list) - 1)
        
        if not relationships_list:
            empty = self.font_sub.render("No tienes relaciones registradas.", True, UI_TEXT_DIM)
            surface.blit(empty, (list_rect.centerx - empty.get_width()//2, list_rect.centery - empty.get_height()//2))
            
            r_empty = self.font_text.render("Aquí aparecerán tus contactos, compañeros y pareja.", True, UI_TEXT_DIM)
            surface.blit(r_empty, (details_rect.centerx - r_empty.get_width()//2, details_rect.centery - r_empty.get_height()//2))
            return
            
        # Draw Left List
        dy = 180
        visible_count = 6
        for i in range(self.relation_scroll, min(self.relation_scroll + visible_count, len(relationships_list))):
            handle, data = relationships_list[i]
            rect = pygame.Rect(60, dy, list_rect.width - 20, 62)
            is_sel = (self.selected_relation_idx == i)
            
            if is_sel:
                pygame.draw.rect(surface, (38, 48, 76), rect, border_radius=8)
                pygame.draw.rect(surface, UI_ACCENT, rect, 1, border_radius=8)
            else:
                pygame.draw.rect(surface, (25, 30, 48), rect, border_radius=8)
                
            # Avatar Circle
            rel_type = data.get("type", "other")
            if rel_type == "agent":
                avatar_color = (255, 200, 100)
            elif rel_type == "teammate":
                avatar_color = (100, 255, 180)
            else:
                avatar_color = (255, 100, 180)
                
            pygame.draw.circle(surface, avatar_color, (rect.left + 35, rect.top + 31), 18)
            
            # Initial
            initial = data.get("name", "?")[0].upper()
            init_s = self.font_bold.render(initial, True, BLACK)
            surface.blit(init_s, (rect.left + 35 - init_s.get_width()//2, rect.top + 31 - init_s.get_height()//2))
            
            # Name and Handle
            name_text = data.get("name", "Desconocido")
            if len(name_text) > 14: name_text = name_text[:12] + "..."
            name_s = self.font_bold.render(name_text, True, WHITE)
            surface.blit(name_s, (rect.left + 65, rect.top + 12))
            
            handle_text = handle
            if len(handle_text) > 16: handle_text = handle_text[:14] + "..."
            h_s = self.font_hint.render(handle_text, True, UI_TEXT_DIM)
            surface.blit(h_s, (rect.left + 65, rect.top + 33))
            
            # Status Badge Pill
            status_text = data.get("status", "Conocido")
            if data.get("on_maternity_leave"):
                status_text = "MATERNIDAD"
            pill_color, text_color = self._get_status_pill_colors(status_text)
            
            badge_w, badge_h = self.font_hint.size(status_text)
            badge_w += 12
            badge_h += 6
            badge_rect = pygame.Rect(rect.right - badge_w - 12, rect.centery - badge_h//2, badge_w, badge_h)
            pygame.draw.rect(surface, pill_color, badge_rect, border_radius=10)
            
            badge_s = self.font_hint.render(status_text, True, text_color)
            surface.blit(badge_s, (badge_rect.centerx - badge_s.get_width()//2, badge_rect.centery - badge_s.get_height()//2))
            
            dy += 68
            
        # Draw Selected Relation Details on Right
        handle, data = relationships_list[self.selected_relation_idx]
        
        # Details Header
        pygame.draw.rect(surface, (28, 35, 58), (details_rect.left + 1, details_rect.top + 1, details_rect.width - 2, 60), border_top_left_radius=12, border_top_right_radius=12)
        pygame.draw.line(surface, (60, 68, 92), (details_rect.left, details_rect.top + 60), (details_rect.right, details_rect.top + 60), 1)
        
        det_hdr_txt = f"Detalle de Relación: {data.get('name')}"
        det_hdr = self.font_sub.render(det_hdr_txt, True, WHITE)
        surface.blit(det_hdr, (details_rect.left + 20, details_rect.top + 18))
        
        # Details Body
        body_y = details_rect.top + 80
        
        # Big avatar / status icon
        avatar_r = 40
        avatar_cx = details_rect.left + 60
        avatar_cy = body_y + 45
        
        rel_type = data.get("type", "other")
        if rel_type == "agent":
            avatar_color = (255, 200, 100)
            type_label = "Representante / Agente"
        elif rel_type == "teammate":
            avatar_color = (100, 255, 180)
            type_label = "Compañero de Equipo"
        else:
            avatar_color = (255, 100, 180)
            type_label = "Contacto / Relación Personal"
            
        pygame.draw.circle(surface, avatar_color, (avatar_cx, avatar_cy), avatar_r)
        
        # Giant Initial
        giant_initial = data.get("name", "?")[0].upper()
        g_init_s = self.font_big_emoji.render(giant_initial, True, BLACK)
        surface.blit(g_init_s, (avatar_cx - g_init_s.get_width()//2, avatar_cy - g_init_s.get_height()//2))
        
        # Name next to avatar
        name_s = self.font_sub.render(data.get("name", ""), True, WHITE)
        surface.blit(name_s, (details_rect.left + 120, body_y + 10))
        
        handle_s = self.font_bold.render(handle, True, UI_ACCENT)
        surface.blit(handle_s, (details_rect.left + 120, body_y + 35))
        
        type_s = self.font_small.render(type_label, True, UI_TEXT_DIM)
        surface.blit(type_s, (details_rect.left + 120, body_y + 55))
        
        # Status Pill Badge next to details or below details
        status_text = data.get("status", "Conocido")
        if data.get("on_maternity_leave"):
            status_text = "MATERNIDAD"
        pill_color, text_color = self._get_status_pill_colors(status_text)
        badge_w, badge_h = self.font_bold.size(status_text)
        badge_w += 20
        badge_h += 10
        badge_rect = pygame.Rect(details_rect.left + 120, body_y + 75, badge_w, badge_h)
        pygame.draw.rect(surface, pill_color, badge_rect, border_radius=12)
        badge_s = self.font_bold.render(status_text, True, text_color)
        surface.blit(badge_s, (badge_rect.centerx - badge_s.get_width()//2, badge_rect.centery - badge_s.get_height()//2))
        
        # Affinity Section
        aff_y = body_y + 140
        aff_val = data.get("affinity", 0)
        
        lbl_aff = self.font_bold.render("AFINIDAD Y CONFIANZA:", True, UI_ACCENT)
        surface.blit(lbl_aff, (details_rect.left + 30, aff_y))
        
        # Slider Track
        slider_w = details_rect.width - 60
        slider_h = 10
        slider_x = details_rect.left + 30
        slider_y = aff_y + 25
        
        # Draw track background
        pygame.draw.rect(surface, (30, 35, 55), (slider_x, slider_y, slider_w, slider_h), border_radius=5)
        
        # Draw central line for 0 point
        center_x = slider_x + slider_w // 2
        pygame.draw.line(surface, UI_TEXT_DIM, (center_x, slider_y - 4), (center_x, slider_y + slider_h + 4), 2)
        
        # Draw progress color
        percent = aff_val / 100.0
        val_x = center_x + int((slider_w // 2) * percent)
        
        if percent > 0:
            fill_rect = pygame.Rect(center_x, slider_y, val_x - center_x, slider_h)
            pygame.draw.rect(surface, (80, 220, 100), fill_rect, border_radius=5)
        elif percent < 0:
            fill_rect = pygame.Rect(val_x, slider_y, center_x - val_x, slider_h)
            pygame.draw.rect(surface, (220, 80, 80), fill_rect, border_radius=5)
            
        # Draw Slider Handle
        pygame.draw.circle(surface, WHITE, (val_x, slider_y + slider_h // 2), 8)
        pygame.draw.circle(surface, UI_ACCENT, (val_x, slider_y + slider_h // 2), 5)
        
        # Text values below slider: -100, 0, +100, and current value
        lbl_n100 = self.font_hint.render("-100 (Hostil)", True, (220, 100, 100))
        lbl_0 = self.font_hint.render("0 (Neutral)", True, UI_TEXT_DIM)
        lbl_p100 = self.font_hint.render("+100 (Aliado)", True, (100, 220, 100))
        
        surface.blit(lbl_n100, (slider_x, slider_y + 15))
        surface.blit(lbl_0, (center_x - lbl_0.get_width()//2, slider_y + 15))
        surface.blit(lbl_p100, (slider_x + slider_w - lbl_p100.get_width(), slider_y + 15))
        
        # Current Affinity Value
        aff_txt = f"{'+' if aff_val > 0 else ''}{aff_val}"
        aff_s = self.font_bold.render(aff_txt, True, WHITE)
        surface.blit(aff_s, (details_rect.right - aff_s.get_width() - 30, aff_y))
        
        # Descriptive Text Block
        desc_y = slider_y + 48
        children = [c for c in career_manager.career_stats.get("children", []) if c.get("mother_handle") == handle]
        has_family_info = data.get("is_pregnant") or len(children) > 0
        desc_h = 62 if has_family_info else 105
        desc_rect = pygame.Rect(details_rect.left + 30, desc_y, details_rect.width - 60, desc_h)
        pygame.draw.rect(surface, (25, 30, 48), desc_rect, border_radius=8)
        pygame.draw.rect(surface, (45, 50, 70), desc_rect, 1, border_radius=8)
        
        desc_text = self._get_relation_description(data)
        
        words = desc_text.split(' ')
        line = ""
        txt_y = desc_rect.top + 12
        for w in words:
            test_line = line + w + " "
            if self.font_text.size(test_line)[0] < desc_rect.width - 30:
                line = test_line
            else:
                if txt_y + 16 < desc_rect.bottom:
                    surface.blit(self.font_text.render(line, True, UI_TEXT), (desc_rect.left + 15, txt_y))
                line = w + " "
                txt_y += 18
        if txt_y + 16 < desc_rect.bottom:
            surface.blit(self.font_text.render(line, True, UI_TEXT), (desc_rect.left + 15, txt_y))
            
        # Draw Pregnancy and Children Info
        if has_family_info:
            family_y = desc_rect.bottom + 8
            if data.get("is_pregnant"):
                preg_weeks = data.get("pregnancy_weeks", 0)
                preg_lbl = self.font_bold.render(f"EMBARAZO (Semana {preg_weeks}/38):", True, (255, 105, 180))
                surface.blit(preg_lbl, (details_rect.left + 35, family_y))
                
                # Progress Bar
                bar_w = details_rect.width - 70
                bar_h = 10
                pygame.draw.rect(surface, (30, 35, 55), (details_rect.left + 35, family_y + 18, bar_w, bar_h), border_radius=5)
                fill_w = int(bar_w * (min(preg_weeks, 38) / 38.0))
                if fill_w > 0:
                    pygame.draw.rect(surface, (255, 105, 180), (details_rect.left + 35, family_y + 18, fill_w, bar_h), border_radius=5)
                family_y += 34
                
            if children:
                child_lbl = self.font_bold.render("HIJOS REGISTRADOS:", True, UI_ACCENT)
                surface.blit(child_lbl, (details_rect.left + 35, family_y))
                
                cy = family_y + 16
                for child in children[:2]: # Show up to 2 children due to space
                    gender_icon = "[H]" if child.get("gender") == "male" else "[M]"
                    age_val = child.get("age", 0)
                    age_txt = f"{age_val} años" if age_val > 0 else "Bebé recién nacido"
                    txt = f"{gender_icon} {child.get('name')} ({age_txt})"
                    child_s = self.font_text.render(txt, True, WHITE)
                    surface.blit(child_s, (details_rect.left + 50, cy))
                    cy += 18

    def _get_status_pill_colors(self, status_text):
        st = status_text.lower()
        if "maternidad" in st:
            return (235, 104, 160), WHITE  # Bright pink for maternity leave
        elif "novia" in st or "esposa" in st or "pareja" in st:
            return (255, 105, 180), WHITE  # Pink (Hot Pink)
        elif "íntimo" in st or "íntima" in st:
            return (255, 215, 0), BLACK    # Gold
        elif "amigo" in st or "amiga" in st:
            return (50, 205, 50), WHITE    # Lime Green
        elif "colega" in st or "conocido" in st or "conocida" in st:
            return (0, 191, 255), WHITE   # Deep Sky Blue (cyan)
        elif "enemistad" in st or "rival" in st or "tensa" in st:
            return (255, 69, 0), WHITE     # OrangeRed
        else:
            return (128, 128, 128), WHITE  # Grey

    def _get_relation_description(self, data):
        rel_type = data.get("type", "other")
        status = data.get("status", "Conocido")
        affinity = data.get("affinity", 0)
        name = data.get("name", "Esta persona")
        
        if rel_type == "agent":
            if affinity >= 70:
                return f"{name} es tu representante de confianza. Negocia los mejores contratos de patrocinio y salario con entusiasmo porque cree firmemente en tu potencial de clase mundial."
            elif affinity >= 40:
                return f"{name} gestiona tus asuntos profesionales de manera eficiente. Mantenéis una buena relación comercial y responde adecuadamente a tus peticiones."
            elif affinity >= 0:
                return f"{name} cumple con su deber básico como representante. La relación es meramente profesional y fría, por lo que su disposición para negociar mejores condiciones es limitada."
            else:
                return f"La tensión con tu representante {name} es evidente. Su actitud hacia tus intereses está comprometida debido a vuestra baja afinidad. Considera mejorar la relación."
        elif rel_type == "teammate":
            if affinity >= 70:
                return f"{name} es un gran aliado dentro y fuera del vestuario. Vuestra conexión se nota en el campo, facilitando jugadas colectivas y apoyo mutuo ante cualquier dificultad."
            elif affinity >= 40:
                return f"{name} es un buen compañero de equipo. Hay respeto mutuo y trabajáis bien juntos por el objetivo común del club."
            elif affinity >= 0:
                return f"La relación con {name} es neutral. Sois compañeros de trabajo que comparten vestuario sin una afinidad o rivalidad particular."
            elif affinity >= -30:
                return f"Hay cierta distancia con {name}. Pequeños roces o diferencias tácticas han enfriado la relación del vestuario."
            else:
                return f"Vuestra relación con {name} es hostil. La rivalidad o desprecio mutuo es evidente en el vestuario, lo que podría perjudicar la química de equipo si no se controla."
        else:
            if status in ("Novia", "Esposa"):
                if affinity >= 75:
                    return f"{name} es tu pareja y tu mayor apoyo. Su amor y compañía te dan una gran estabilidad emocional, lo que potencia tu rendimiento profesional en el campo."
                else:
                    return f"{name} es tu pareja. Aunque tenéis altibajos debido a las exigencias de tu carrera profesional, se esfuerza por apoyarte en tu camino al éxito."
            else:
                if affinity >= 70:
                    return f"{name} es una amistad íntima que te brinda apoyo incondicional en el ámbito personal, sirviendo como un gran pilar en tus momentos difíciles."
                elif affinity >= 40:
                    return f"{name} es una amistad agradable en tu círculo personal. Os apoyáis mutuamente cuando la ocasión lo requiere."
                elif affinity >= 0:
                    return f"{name} es un contacto casual en tus redes sociales. Compartís interacciones esporádicas sin mayor compromiso personal."
                else:
                    return f"Mantenéis una relación distante o tensa con {name}. Vuestras interacciones suelen estar cargadas de malentendidos o discrepancias públicas."
