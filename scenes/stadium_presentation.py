import pygame
import math
import random
from settings import *
from data.career_manager import career_manager
from data.teams import draw_badge, draw_uniform_preview

class StadiumPresentationScene:
    """A premium, high-impact stadium presentation for star player transfers."""
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        
        self.team = self.context.get("team")
        self.player_name = self.context.get("player_name", "Estrella")
        self.number = self.context.get("number", 10)
        self.next_scene = self.context.get("next_scene")
        
        if not self.team:
            from data.teams import TEAMS
            self.team = TEAMS[0]
            
        self.time = 0
        self.state = "intro" # "intro", "juggling", "kick", "outro"
        
        # Juggling Game State
        self.ball_x = WIDTH // 2 + 180
        self.ball_y = 100
        self.ball_vx = 0
        self.ball_vy = 0
        self.gravity = 750 # Pixels/sec^2
        self.juggles = 0
        self.max_juggles = 0
        self.excitement = 30.0 # Percentage (0-100)
        self.zone_y_start = HEIGHT // 2 + 90
        self.zone_y_end = HEIGHT // 2 + 150
        self.grass_y = HEIGHT // 2 + 160
        self.respawn_timer = 0.0
        
        # Ball Kicked state
        self.kicked_ball = None # dict with physical state for outro shot
        
        # Text popup effects ("¡OLÉ!", "¡UUUUH!")
        self.popups = [] # list of {"txt": str, "x": int, "y": int, "scale": float, "color": tuple, "timer": float}
        
        # Crowd Camera Flashes
        self.flashes = [] # list of {"x": int, "y": int, "timer": float}
        
        # Confetti Particle System
        self.confetti = [] # list of dicts
        self._spawn_confetti(80) # Initial floating atmosphere
        
        # Neon green zone alpha
        self.zone_pulse = 0
        
        try:
            self.font_big = pygame.font.SysFont("Impact", 54)
            self.font_title = pygame.font.SysFont("Impact", 38)
            self.font_sub = pygame.font.SysFont("Arial", 22, bold=True)
            self.font_text = pygame.font.SysFont("Arial", 16)
            self.font_hint = pygame.font.SysFont("Arial", 14)
        except:
            self.font_big = pygame.font.Font(None, 54)
            self.font_title = pygame.font.Font(None, 38)
            self.font_sub = pygame.font.Font(None, 22)
            self.font_text = pygame.font.Font(None, 16)
            self.font_hint = pygame.font.Font(None, 14)
            
    def _spawn_confetti(self, count, target_x=None, target_y=None):
        cols = [
            (255, 215, 0), # Gold
            (255, 255, 255), # White
            self.team.get("color_1", UI_ACCENT),
            self.team.get("color_2", WHITE)
        ]
        for _ in range(count):
            x = target_x if target_x is not None else random.randint(0, WIDTH)
            y = target_y if target_y is not None else random.randint(-150, HEIGHT - 100)
            self.confetti.append({
                "x": x,
                "y": y,
                "vx": random.uniform(-80, 80),
                "vy": random.uniform(80, 220),
                "size": random.randint(4, 9),
                "color": random.choice(cols),
                "sway_offset": random.uniform(0, 100),
                "sway_speed": random.uniform(2, 5),
                "angle": random.uniform(0, 360),
                "rot_speed": random.uniform(90, 270)
            })
            
    def _add_popup(self, text, x, y, color):
        self.popups.append({
            "txt": text,
            "x": x,
            "y": y,
            "scale": 1.0,
            "color": color,
            "timer": 0.8 # Seconds lifespan
        })

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                # Key number changing allowed in both intro/juggling/kick states
                if self.state in ("intro", "juggling", "kick"):
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.number = min(99, self.number + 1)
                        if career_manager.active and career_manager.career_player:
                            career_manager.career_player["num"] = self.number
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.number = max(1, self.number - 1)
                        if career_manager.active and career_manager.career_player:
                            career_manager.career_player["num"] = self.number
                
                # Flow transitions
                if self.state == "intro":
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        self.state = "juggling"
                        self.ball_y = 50
                        self.ball_vy = 100
                        self.juggles = 0
                
                elif self.state == "juggling":
                    if event.key == pygame.K_SPACE:
                        # JUGGLE TOUCH CHECK!
                        if self.zone_y_start <= self.ball_y <= self.zone_y_end:
                            # PERFECT KICK!
                            dist_from_center = abs(self.ball_y - (self.zone_y_start + self.zone_y_end)//2)
                            timing_bonus = max(0, 1.0 - (dist_from_center / 30.0)) # 0 to 1
                            
                            self.ball_vy = -random.randint(380, 440)
                            self.ball_vx = random.uniform(-90, 90)
                            
                            self.juggles += 1
                            self.max_juggles = max(self.max_juggles, self.juggles)
                            
                            # Add popups & particles
                            cols = [GOLD, (100, 255, 100), (150, 255, 255)]
                            txt = "¡OLÉ!" if self.juggles % 3 != 0 else f"¡MAGIA! ({self.juggles})"
                            if self.juggles >= 10: txt = "¡CRACK MUNDIAL!"
                            self._add_popup(txt, self.ball_x, self.ball_y - 20, random.choice(cols))
                            
                            self._spawn_confetti(15, self.ball_x, self.ball_y)
                            
                            # Boost crowd excitement
                            self.excitement = min(100.0, self.excitement + 10.0 + (timing_bonus * 5.0))
                        else:
                            # Whiff!
                            self.juggles = 0
                            self._add_popup("¡CASI!", self.ball_x, self.ball_y - 10, (255, 100, 100))
                            self.excitement = max(10.0, self.excitement - 8.0)
                    
                    elif event.key == pygame.K_RETURN:
                        # Proceed to Kick State
                        self.state = "kick"
                        # Set ball to player's foot ready to shoot
                        self.ball_x = WIDTH // 2 + 100
                        self.ball_y = self.zone_y_start + 10
                        self.ball_vx = 0
                        self.ball_vy = 0
                        
                elif self.state == "kick":
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                        # CHUTAR AL ESTADIO!
                        self.kicked_ball = {
                            "x": self.ball_x,
                            "y": self.ball_y,
                            "vx": -450, # Shoot left-upwards deep into stands
                            "vy": -650,
                            "rot": 0,
                            "trail": []
                        }
                        self.state = "outro"
                        self.excitement = 100.0
                        self._spawn_confetti(120, WIDTH // 2 - 150, HEIGHT // 3)
                        self._add_popup("¡GOOOOL A LA GRADA!", WIDTH // 2 - 100, HEIGHT // 2 - 100, GOLD)
                        
                elif self.state == "outro":
                    if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
                        self._finish()

    def _finish(self):
        if self.next_scene:
            self.manager.set_scene(self.next_scene)
        else:
            from scenes.career_hub import CareerHubScene
            self.manager.set_scene(CareerHubScene)

    def update(self, dt):
        self.time += dt
        
        # Zone pulsing
        self.zone_pulse = (math.sin(self.time * 6) + 1) / 2
        
        # Physics for Juggling Ball
        if self.state == "juggling":
            if self.respawn_timer > 0:
                self.respawn_timer -= dt
                if self.respawn_timer <= 0:
                    self.ball_x = WIDTH // 2 + 180
                    self.ball_y = 50
                    self.ball_vx = 0
                    self.ball_vy = 100
            else:
                self.ball_y += self.ball_vy * dt
                self.ball_x += self.ball_vx * dt
                self.ball_vy += self.gravity * dt
                
                # Screen edge bounce
                if self.ball_x < WIDTH // 2 + 30:
                    self.ball_x = WIDTH // 2 + 30
                    self.ball_vx = -self.ball_vx * 0.7
                elif self.ball_x > WIDTH - 50:
                    self.ball_x = WIDTH - 50
                    self.ball_vx = -self.ball_vx * 0.7
                    
                # Floor hit
                if self.ball_y >= self.grass_y:
                    self.ball_y = self.grass_y
                    self.ball_vy = -self.ball_vy * 0.35 # Soft grass bounce
                    self.ball_vx = self.ball_vx * 0.5
                    
                    if abs(self.ball_vy) < 60:
                        self.ball_vy = 0
                        self.ball_vx = 0
                        # Trigger respawn timer
                        self.juggles = 0
                        self._add_popup("¡AL SUELO!", self.ball_x, self.ball_y - 20, (255, 100, 100))
                        self.respawn_timer = 1.2
                        
        # Physics for Outro Kicked Ball
        if self.state == "outro" and self.kicked_ball:
            kb = self.kicked_ball
            kb["trail"].append((int(kb["x"]), int(kb["y"])))
            if len(kb["trail"]) > 18: kb["trail"].pop(0)
            
            kb["x"] += kb["vx"] * dt
            kb["y"] += kb["vy"] * dt
            kb["vy"] += 500 * dt # Gravity pulling ball down in arc
            kb["rot"] += 360 * dt
            
        # Update popups
        for pop in self.popups[:]:
            pop["timer"] -= dt
            pop["scale"] += 0.8 * dt
            pop["y"] -= 30 * dt
            if pop["timer"] <= 0:
                self.popups.remove(pop)
                
        # Generate crowd camera flashes
        if random.random() < 0.12:
            self.flashes.append({
                "x": random.randint(30, WIDTH - 30),
                "y": random.randint(80, HEIGHT // 2 - 40),
                "timer": random.uniform(0.05, 0.15)
            })
            
        # Update flashes
        for fl in self.flashes[:]:
            fl["timer"] -= dt
            if fl["timer"] <= 0:
                self.flashes.remove(fl)
                
        # Update particles (Confetti)
        for p in self.confetti[:]:
            p["y"] += p["vy"] * dt
            p["x"] += (p["vx"] + math.sin(self.time * p["sway_speed"] + p["sway_offset"]) * 50) * dt
            p["angle"] += p["rot_speed"] * dt
            
            # Wrap around top if initial drop, or remove if bottom
            if p["y"] > HEIGHT + 10:
                if self.state == "outro" or self.excitement >= 90.0:
                    # Keep spawning at top
                    p["y"] = -10
                    p["x"] = random.randint(0, WIDTH)
                else:
                    self.confetti.remove(p)

    def draw(self, surface):
        surface.fill((10, 12, 20)) # Dark night sky
        
        # --- 1. Draw Stadium Stands Background ---
        # Stands silhouettes
        pygame.draw.ellipse(surface, (20, 25, 40), (50, 100, WIDTH - 100, HEIGHT // 2), 0)
        pygame.draw.ellipse(surface, (15, 18, 30), (-100, 150, WIDTH + 200, HEIGHT // 2 + 100), 0)
        
        # Draw Thousands of Crowd Lights (Spectators)
        for i in range(150):
            # Seed based coordinate to prevent jumping stars
            random.seed(i * 999)
            cx = random.randint(40, WIDTH - 40)
            cy = random.randint(90, HEIGHT // 2 - 20)
            color = random.choice([(80, 90, 130), (120, 130, 170), (40, 50, 80)])
            size = random.choice([1, 2])
            pygame.draw.circle(surface, color, (cx, cy), size)
            
        # Draw Floodlight Beams
        beams = [
            ((80, 50), (WIDTH // 3, HEIGHT)),
            ((WIDTH - 80, 50), (2 * WIDTH // 3, HEIGHT))
        ]
        for src, dest in beams:
            beam_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            # Drawing a transparent polygon representing the light cone
            pygame.draw.polygon(beam_surf, (255, 255, 220, 15), [src, (dest[0] - 150, dest[1]), (dest[0] + 150, dest[1])])
            pygame.draw.circle(beam_surf, (255, 255, 255, 50), src, 30)
            pygame.draw.circle(beam_surf, (255, 255, 255, 120), src, 12)
            surface.blit(beam_surf, (0, 0))
            
        # Draw active camera flashes
        for fl in self.flashes:
            # Concentric glowing circles
            pygame.draw.circle(surface, (255, 255, 255), (fl["x"], fl["y"]), 8)
            pygame.draw.circle(surface, (200, 240, 255), (fl["x"], fl["y"]), 18, 2)
            
        # --- 2. Draw Pitch / Grass Floor ---
        pitch_rect = pygame.Rect(0, HEIGHT // 2 + 20, WIDTH, HEIGHT // 2)
        # Deep green grass gradient
        for y in range(pitch_rect.top, HEIGHT, 4):
            val = (y - pitch_rect.top) / (HEIGHT - pitch_rect.top)
            g_col = (int(10 + val * 20), int(60 + val * 90), int(15 + val * 25))
            pygame.draw.rect(surface, g_col, (0, y, WIDTH, 4))
            
        # Draw field white lines (perspective effect)
        pygame.draw.line(surface, (255, 255, 255, 60), (0, HEIGHT // 2 + 100), (WIDTH, HEIGHT // 2 + 100), 2)
        pygame.draw.line(surface, (255, 255, 255, 80), (WIDTH // 2 - 180, HEIGHT // 2 + 20), (WIDTH // 2 - 380, HEIGHT), 3)
        pygame.draw.line(surface, (255, 255, 255, 80), (WIDTH // 2 + 180, HEIGHT // 2 + 20), (WIDTH // 2 + 380, HEIGHT), 3)
        
        # --- 3. Draw Presentation Jersey & Badge ---
        # Giant badge glowing in the center background
        badge_surf = pygame.Surface((300, 300), pygame.SRCALPHA)
        draw_badge(badge_surf, self.team, 150, 150, size=120)
        badge_surf.set_alpha(int(40 + math.sin(self.time * 3) * 15))
        surface.blit(badge_surf, (WIDTH // 2 - 350, HEIGHT // 2 - 170))
        
        # Player model (jersey representation)
        px, py = WIDTH // 2 - 100, HEIGHT // 2 - 30
        shirt_rect = pygame.Rect(px - 90, py - 120, 180, 240)
        pygame.draw.rect(surface, (25, 30, 45), shirt_rect, border_radius=20)
        pygame.draw.rect(surface, GOLD if self.excitement >= 100.0 else UI_ACCENT, shirt_rect, 3 + int(self.zone_pulse*2), border_radius=20)
        
        # Uniform
        draw_uniform_preview(surface, self.team, shirt_rect.centerx, shirt_rect.centery - 25, scale=2.0)
        
        # Big number
        num_font = pygame.font.SysFont("Impact", 68) if pygame.font.get_init() else pygame.font.Font(None, 68)
        ns = num_font.render(str(self.number), True, WHITE)
        surface.blit(ns, (shirt_rect.centerx - ns.get_width()//2, shirt_rect.centery + 45))
        
        # Shirt number change hint under shirt
        if self.state in ("intro", "juggling", "kick"):
            dh = self.font_hint.render("▲/▼ o W/S: Cambiar Dorsal", True, GOLD)
            surface.blit(dh, (shirt_rect.centerx - dh.get_width()//2, shirt_rect.bottom + 15))
            
        # --- 4. Draw Juggling Mechanics ---
        if self.state == "juggling":
            # Target Touch Zone (Neon glowing green box)
            zone_color = (0, int(200 + self.zone_pulse * 55), 100)
            zone_rect = pygame.Rect(WIDTH // 2 + 100, self.zone_y_start, 160, self.zone_y_end - self.zone_y_start)
            
            # Pulse highlight
            zone_surf = pygame.Surface((zone_rect.width, zone_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(zone_surf, (0, 255, 120, int(35 + self.zone_pulse * 40)), (0, 0, zone_rect.width, zone_rect.height), border_radius=5)
            surface.blit(zone_surf, zone_rect.topleft)
            pygame.draw.rect(surface, zone_color, zone_rect, 2 + int(self.zone_pulse * 2), border_radius=5)
            
            # Target zone text label
            zt = self.font_hint.render("ZONA DE TOQUE", True, zone_color)
            surface.blit(zt, (zone_rect.right + 12, zone_rect.centery - zt.get_height()//2))
            
            # Draw Ball Juggling Shadow
            shadow_size = max(5, int(22 - (self.grass_y - self.ball_y) * 0.12))
            shadow_surf = pygame.Surface((40, 15), pygame.SRCALPHA)
            pygame.draw.ellipse(shadow_surf, (0, 0, 0, 90), (20 - shadow_size, 7 - shadow_size//3, shadow_size*2, shadow_size*2//3))
            surface.blit(shadow_surf, (self.ball_x - 20, self.grass_y + 10))
            
            # Draw Soccer Ball
            if self.respawn_timer <= 0:
                ball_color = (245, 245, 245)
                # Drawing details
                pygame.draw.circle(surface, (0, 0, 0), (int(self.ball_x), int(self.ball_y)), 15)
                pygame.draw.circle(surface, ball_color, (int(self.ball_x), int(self.ball_y)), 14)
                # Pentagon accents
                for angle in range(0, 360, 72):
                    ax = int(self.ball_x + math.cos(math.radians(angle + self.time*180)) * 7)
                    ay = int(self.ball_y + math.sin(math.radians(angle + self.time*180)) * 7)
                    pygame.draw.circle(surface, (20, 20, 20), (ax, ay), 3)
            else:
                # Announce respawn
                rt = self.font_hint.render("¡LISTO!...", True, WHITE)
                surface.blit(rt, (WIDTH // 2 + 150, HEIGHT // 2 + 40))
                
        elif self.state == "kick":
            # Draw indicator line for kick
            pygame.draw.ellipse(surface, (255, 215, 0), (self.ball_x - 30, self.ball_y - 30, 60, 60), 2)
            k_hint = self.font_sub.render("¡CHUTA A LA GRADA!", True, GOLD)
            surface.blit(k_hint, (self.ball_x - k_hint.get_width()//2, self.ball_y - 65))
            
            # Draw Ball
            pygame.draw.circle(surface, WHITE, (int(self.ball_x), int(self.ball_y)), 15)
            pygame.draw.circle(surface, (20, 20, 20), (int(self.ball_x), int(self.ball_y)), 15, 2)
            
        elif self.state == "outro" and self.kicked_ball:
            kb = self.kicked_ball
            # Draw trail
            for idx, pt in enumerate(kb["trail"]):
                alpha = int(255 * (idx / len(kb["trail"])))
                t_col = (255, 230, 150, alpha)
                t_surf = pygame.Surface((30, 30), pygame.SRCALPHA)
                pygame.draw.circle(t_surf, t_col, (15, 15), int(4 + idx*0.5))
                surface.blit(t_surf, (pt[0] - 15, pt[1] - 15))
                
            # Draw flying ball
            bx, by = int(kb["x"]), int(kb["y"])
            if 0 <= bx <= WIDTH and 0 <= by <= HEIGHT:
                pygame.draw.circle(surface, WHITE, (bx, by), 12)
                pygame.draw.circle(surface, (0, 0, 0), (bx, by), 12, 1)
                # Rotation line
                rx = int(bx + math.cos(math.radians(kb["rot"])) * 9)
                ry = int(by + math.sin(math.radians(kb["rot"])) * 9)
                pygame.draw.line(surface, (0, 0, 0), (bx, by), (rx, ry), 2)

        # --- 5. Draw Particles (Confetti) ---
        for p in self.confetti:
            # Draw rotated rectangle confetti particle
            c_surf = pygame.Surface((p["size"]*2, p["size"]*2), pygame.SRCALPHA)
            # Create rect in center and rotate
            rect_col = p["color"] + (210,) # Adding opacity
            pygame.draw.rect(c_surf, rect_col, (p["size"]//2, p["size"]//2, p["size"], p["size"]))
            rot_surf = pygame.transform.rotate(c_surf, int(p["angle"]))
            surface.blit(rot_surf, (int(p["x"] - rot_surf.get_width()//2), int(p["y"] - rot_surf.get_height()//2)))

        # --- 6. Draw Text Popups ---
        for pop in self.popups:
            p_surf = self.font_big.render(pop["txt"], True, pop["color"])
            # Scale effect
            w = int(p_surf.get_width() * pop["scale"])
            h = int(p_surf.get_height() * pop["scale"])
            if w > 0 and h > 0:
                scaled = pygame.transform.scale(p_surf, (w, h))
                surface.blit(scaled, (int(pop["x"] - w//2), int(pop["y"] - h//2)))

        # --- 7. Draw HUD Overlay (Chants, Announcer and Info) ---
        # Top banner with name
        banner_rect = pygame.Rect(50, 25, WIDTH - 100, 65)
        pygame.draw.rect(surface, (15, 20, 35, 220), banner_rect, border_radius=10)
        pygame.draw.rect(surface, GOLD, banner_rect, 2, border_radius=10)
        
        name_t = self.font_title.render(f"BIENVENIDO: {self.player_name.upper()}", True, GOLD)
        surface.blit(name_t, (banner_rect.centerx - name_t.get_width()//2, banner_rect.centery - name_t.get_height()//2))
        
        # Draw excitement bar
        bar_x = 50
        bar_y = HEIGHT - 85
        bar_w = 300
        bar_h = 24
        
        # Label
        el = self.font_text.render("EMOCIÓN DE LA AFICIÓN:", True, UI_TEXT_DIM)
        surface.blit(el, (bar_x, bar_y - 22))
        
        # Fill
        pygame.draw.rect(surface, (30, 35, 50), (bar_x, bar_y, bar_w, bar_h), border_radius=5)
        fill_w = int(bar_w * (self.excitement / 100.0))
        # Excitement color shift (green to orange to gold)
        e_color = (0, 255, 100) if self.excitement < 60 else (255, 180, 0) if self.excitement < 90 else (255, 215, 0)
        if fill_w > 0:
            pygame.draw.rect(surface, e_color, (bar_x, bar_y, fill_w, bar_h), border_radius=5)
        pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_w, bar_h), 1, border_radius=5)
        
        # Streak counters on the right
        sx = WIDTH - 350
        sy = HEIGHT - 95
        
        st_lbl = self.font_sub.render(f"TOQUES SEGUIDOS:  {self.juggles}", True, WHITE)
        surface.blit(st_lbl, (sx, sy))
        
        max_lbl = self.font_text.render(f"Record del día:  {self.max_juggles} toques", True, UI_TEXT_DIM)
        surface.blit(max_lbl, (sx, sy + 25))

        # Bottom state-dependent instructions card
        card_rect = pygame.Rect(WIDTH // 2 - 280, HEIGHT - 145, 560, 45)
        
        if self.state == "intro":
            msg = "¡Saltas al césped ante 80,000 hinchas! [ENTER/SPACE] Presentarse"
            pygame.draw.rect(surface, (20, 25, 40, 230), card_rect, border_radius=8)
            pygame.draw.rect(surface, UI_ACCENT, card_rect, 1, border_radius=8)
            ms = self.font_sub.render(msg, True, WHITE)
            surface.blit(ms, (card_rect.centerx - ms.get_width()//2, card_rect.centery - ms.get_height()//2))
            
        elif self.state == "juggling":
            msg = "PRESIONA [ESPACIO] al caer el balón para hacer toques"
            pygame.draw.rect(surface, (20, 25, 40, 230), card_rect, border_radius=8)
            pygame.draw.rect(surface, (0, 255, 120), card_rect, 1, border_radius=8)
            ms = self.font_sub.render(msg, True, WHITE)
            surface.blit(ms, (card_rect.centerx - ms.get_width()//2, card_rect.centery - ms.get_height()//2))
            
            # Advise how to complete keepy-ups
            hint_t = self.font_hint.render("Presiona ENTER para chutar a la afición cuando quieras terminar.", True, UI_TEXT_DIM)
            surface.blit(hint_t, (WIDTH//2 - hint_t.get_width()//2, HEIGHT - 180))
            
        elif self.state == "kick":
            msg = "¡Presiona [ESPACIO / ENTER] para chutar de volea a la grada!"
            pygame.draw.rect(surface, (20, 25, 40, 230), card_rect, border_radius=8)
            pygame.draw.rect(surface, GOLD, card_rect, 2, border_radius=8)
            ms = self.font_sub.render(msg, True, GOLD)
            surface.blit(ms, (card_rect.centerx - ms.get_width()//2, card_rect.centery - ms.get_height()//2))
            
        elif self.state == "outro":
            # Display giant chanting banner
            chant_rect = pygame.Rect(WIDTH//2 - 350, HEIGHT//2 - 210, 700, 70)
            pygame.draw.rect(surface, (10, 10, 15, 235), chant_rect, border_radius=12)
            pygame.draw.rect(surface, GOLD, chant_rect, 3, border_radius=12)
            
            chant_font = pygame.font.SysFont("Impact", 44) if pygame.font.get_init() else pygame.font.Font(None, 44)
            # Pulse the chant text color
            pulse_gold = (int(200 + self.zone_pulse*55), int(170 + self.zone_pulse*45), int(30 - self.zone_pulse*30))
            chant_surf = chant_font.render(f"¡{self.player_name.upper()}! ¡{self.player_name.upper()}!", True, pulse_gold)
            surface.blit(chant_surf, (chant_rect.centerx - chant_surf.get_width()//2, chant_rect.centery - chant_surf.get_height()//2))
            
            msg = "¡La grada corea tu nombre! [ENTER / ESPACIO] Entrar al Club"
            pygame.draw.rect(surface, (20, 25, 40, 230), card_rect, border_radius=8)
            pygame.draw.rect(surface, GOLD, card_rect, 1, border_radius=8)
            ms = self.font_sub.render(msg, True, WHITE)
            surface.blit(ms, (card_rect.centerx - ms.get_width()//2, card_rect.centery - ms.get_height()//2))
