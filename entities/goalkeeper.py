import pygame
import math
import random
from settings import *


class Goalkeeper:
    """Portero controlado por IA."""

    def __init__(self, x, y, team_data, player_data, side="left"):
        self.pos = pygame.math.Vector2(x, y)
        self.radius = PLAYER_RADIUS + 2  # Portero ligeramente más grande
        self.team_data = team_data
        self.player_data = player_data
        # Portero usa colores invertidos (secundario como principal)
        self.color = team_data["secondary"]
        self.secondary = team_data["primary"]
        self.side = side
        
        self.speed = GK_SPEED * (player_data["s"]["speed"] / 50.0)  # GK speed es usualmente baja (40-50)
        self.dive_speed = GK_DIVE_SPEED * (player_data["s"]["gk"] / 80.0)
        
        self.has_ball = False
        self.is_controlled = False
        self.kick_cooldown = 0
        self.pass_charge = 0
        self.kick_charge = 0
        self.holding_timer = 0
        self.home_x = x
        self.home_y = y
        self.direction = pygame.math.Vector2(1 if side == "left" else -1, 0)
        
        # Reaction delay: the GK only recalculates its ideal position every ~0.15s
        self._react_timer = 0.0
        self._react_interval = 0.15  # seconds between position recalculations
        self._current_target = pygame.math.Vector2(x, y)
        
        # Stamina / Energy
        self.energy = player_data.get("energy", 100.0)
        self.max_energy = 100.0
        
        self.difficulty = 5
        
        self.match_stats = {
            "name": self.player_data["name"],
            "goals": 0, "assists": 0, "passes_completed": 0, "steals": 0, "saves": 0,
            "yellow_cards": 0, "red_card": 0, "rating": 6.0
        }
        self.red_card = False
        self.yellow_cards = 0
        self.is_injured = False
        self.injury_severity = 0 # 0-100

        # --- Animación visual simplificada (no afecta físicas) ---
        self._anim_phase = random.random() * 6.28318530718
        self._match_scene_ref = None  # Referencia efímera para efectos visuales (goal_freeze)
        
    def apply_difficulty(self, difficulty):
        self.difficulty = difficulty
        # Scale dive speed and reaction time — GKs are now much stronger
        diff_mult = 0.82 + (difficulty * 0.05) # 0.87 to 1.32 (was 0.84 to 1.2)
        self.dive_speed *= diff_mult
        self._react_interval = max(0.02, 0.22 - (difficulty * 0.022)) # 0.198s to 0.02s (faster)
        
        # Catch bonus: higher difficulty = GK catches more shots instead of parrying
        self.catch_bonus = difficulty * 3  # 3 to 30 extra speed threshold
        
        # Initialize stats if needed (already done in __init__, but keep for safety if reset)
        self.match_stats = {
            "name": self.player_data["name"],
            "goals": 0, "assists": 0, "passes_completed": 0, "steals": 0, "saves": 0,
            "yellow_cards": 0, "red_card": 0, "rating": 6.0
        }

    def update(self, dt, ball, pitch_rect, teammates=None, opponents=None, match_scene=None):
        if match_scene is not None:
            self._match_scene_ref = match_scene

        if self.red_card:
            self.has_ball = False
            self.pos = pygame.math.Vector2(-1000, -1000) # Fuera del campo
            return
            
        if self.kick_cooldown > 0:
            self.kick_cooldown -= dt

        dist_to_ball = self.pos.distance_to(ball.pos)
        
        if getattr(match_scene, 'is_kickoff', False) or getattr(match_scene, 'is_set_piece', False):
            return
            
        # ── Interacción con el balón (Trapping) ──
        # No re-atrapar si acabamos de patear
        if self.kick_cooldown > 0:
            self.has_ball = False
        else:
            # Lógica de Captura vs Despeje (Evitar absorción mágica)
            catch_radius = self.radius + ball.radius + 4 # Radio reducido
            ball_speed = ball.vel.length()
            
            if not self.has_ball and dist_to_ball < catch_radius + 20:
                # Detectar peligro para estadísticas (Debe ir hacia el arco y tener cierta velocidad)
                is_on_target = 245 < ball.pos.y < 355
                is_danger = (self.side == "left" and ball.vel.x < -150) or (self.side == "right" and ball.vel.x > 150)
                
                if is_danger and is_on_target and dist_to_ball < catch_radius + 10:
                    catch_bonus = getattr(self, 'catch_bonus', 0)
                    
                    # SI EL TIRO ES MUY FUERTE: Despejar en lugar de atrapar
                    if ball_speed > 380 + catch_bonus:
                        self.match_stats["saves"] += 1
                        # Rebotar balón (Parry)
                        ball.vel.x *= -0.4
                        ball.vel.y += random.uniform(-100, 100)
                        self.kick_cooldown = 0.5 # No re-atrapar de inmediato
                        return
                    
                    # SI EL TIRO ES MEDIO: Probabilidad de atrapar
                    elif ball_speed > 220:
                        if dist_to_ball < catch_radius:
                            self.match_stats["saves"] += 1
                            self.has_ball = True
                    # TIRO FLOJO: Atrape fácil
                    else:
                        if dist_to_ball < catch_radius + 5:
                            self.has_ball = True

        if self.has_ball:
            if ball.last_touch_name != self.player_data["name"]:
                ball.assistant_name = ball.last_touch_name
                ball.last_touch_name = self.player_data["name"]
            ball.last_touch = self.side
            
            # Atracción magnética (trap)
            target_ball_pos = self.pos + self.direction * (self.radius + 4)
            ball.pos = ball.pos.lerp(target_ball_pos, 0.4)
            ball.vel = pygame.math.Vector2(0, 0)
                
            if self.is_controlled:
                # ── Control Humano del Portero ──
                keys = pygame.key.get_pressed()
                
                # Cargar Pase (S)
                if keys[pygame.K_s]:
                    self.pass_charge = min(self.pass_charge + 800 * dt, PASS_FORCE)
                elif self.pass_charge > 0:
                    self._execute_pass(ball, PASS_FORCE * 0.4 + self.pass_charge * 0.6, teammates, pitch_rect)
                    self.pass_charge = 0
                    return
                # Cargar Despeje/Tiro Largo (A)
                elif keys[pygame.K_a]:
                    self.kick_charge = min(self.kick_charge + 1200 * dt, KICK_FORCE)
                elif self.kick_charge > 0:
                    # Direccionar largo adelante
                    kick_dir = pygame.math.Vector2(1 if self.side == "left" else -1, (ball.pos.y - pitch_rect.centery) / 500)
                    if kick_dir.length() > 0:
                        kick_dir = kick_dir.normalize()
                    ball.vel = kick_dir * (self.kick_charge)
                    self.kick_cooldown = 1.0
                    self.kick_charge = 0
                    self.has_ball = False
                    return
            else:
                # ── Control IA del Portero ──
                if self.holding_timer <= 0:
                    self.holding_timer = 1.5 # retener por segundo y medio
                
                self.holding_timer -= dt
                if self.holding_timer <= 0 and self.kick_cooldown <= 0:
                    self._execute_pass(ball, PASS_FORCE * 0.8, teammates, pitch_rect)
                    return
        else:
            self.holding_timer = 0
            self.pass_charge = 0
            self.kick_charge = 0

            # ── Movimiento del portero cuando no tiene balón ──
            ball_approaching = False
            if self.side == "left":
                ball_approaching = ball.vel.x < -50 and ball.pos.x < pitch_rect.left + 250
            else:
                ball_approaching = ball.vel.x > 50 and ball.pos.x > pitch_rect.right - 250

            if ball_approaching and dist_to_ball < GK_REACT_DIST:
                # Lanzarse hacia el balón
                to_ball = ball.pos - self.pos
                if to_ball.length() > 0:
                    direction = to_ball.normalize()
                    self.pos += direction * self.dive_speed * dt
            else:
                # ── Lógica de Achique con RETARDO DE REACCIÓN ──
                # El portero solo recalcula su posición ideal cada ~0.4s
                # Esto crea ventanas donde el palo lejano queda libre
                self._react_timer += dt
                
                if self._react_timer >= self._react_interval:
                    self._react_timer = 0.0
                    goal_center = pygame.math.Vector2(self.home_x, pitch_rect.centery)
                    
                    if dist_to_ball > 400:
                        self._current_target = goal_center + pygame.math.Vector2(5 if self.side == "left" else -5, 0)
                    else:
                        to_ball_dir = (ball.pos - goal_center)
                        if to_ball_dir.length() > 0:
                            to_ball_dir = to_ball_dir.normalize()
                        rush_dist = min(20, max(0, 300 - dist_to_ball) * 0.08)
                        self._current_target = goal_center + to_ball_dir * rush_dist

                # Moverse hacia el target guardado (puede estar desactualizado)
                adaptive_speed = self.speed * (0.7 if dist_to_ball > 300 else 1.0)
                
                diff_y = self._current_target.y - self.pos.y
                if abs(diff_y) > 5:
                    self.pos.y += min(abs(diff_y), adaptive_speed * dt) * (1 if diff_y > 0 else -1)

                diff_x = self._current_target.x - self.pos.x
                if abs(diff_x) > 5:
                    self.pos.x += min(abs(diff_x), adaptive_speed * 0.65 * dt) * (1 if diff_x > 0 else -1)

        # ── Límites estrictos del portero ──
        # La portería mide 110px de alto. Limitamos su Y para que no abandone los 3 palos (+/- 55px).
        # Ampliamos el X para permitirle achicar hasta 100px.
        area_x_start = pitch_rect.left if self.side == "left" else pitch_rect.right - 100
        area_x_end = pitch_rect.left + 100 if self.side == "left" else pitch_rect.right
        area_y_start = pitch_rect.centery - 55
        area_y_end = pitch_rect.centery + 55

        self.pos.x = max(area_x_start + self.radius, min(self.pos.x, area_x_end - self.radius))
        self.pos.y = max(area_y_start + self.radius, min(self.pos.y, area_y_end - self.radius))

    def _execute_pass(self, ball, force, teammates, pitch_rect):
        """Asistente de pase para portero."""
        if teammates:
            # Buscar el compañero más desmarcado/cercano adelante
            target = None
            min_dist = float('inf')
            
            for t in teammates:
                # Solo pasar a gente que esté en nuestra mitad por seguridad
                if self.side == "left" and t.pos.x < pitch_rect.centerx:
                    dist = self.pos.distance_to(t.pos)
                    if dist < min_dist and dist > 50:
                        min_dist = dist
                        target = t
                elif self.side == "right" and t.pos.x > pitch_rect.centerx:
                    dist = self.pos.distance_to(t.pos)
                    if dist < min_dist and dist > 50:
                        min_dist = dist
                        target = t
            
            if not target:
                if len(teammates) > 0: target = teammates[0]
                
            if target:
                kick_dir = (target.pos - self.pos)
                if kick_dir.length() > 0:
                    kick_dir = kick_dir.normalize()
                ball.vel = kick_dir * force
                self.kick_cooldown = 1.0
                self.has_ball = False
                return
                
        # Si no hay teammates o fallback
        default_dir = pygame.math.Vector2(1 if self.side == "left" else -1, 0)
        ball.vel = default_dir * force
        self.kick_cooldown = 1.0
        self.has_ball = False

    def _get_goal_center(self, pitch_rect):
        return pygame.math.Vector2(self.home_x, pitch_rect.centery)

    def draw(self, surface):
        px, py = int(self.pos.x), int(self.pos.y)
        now = pygame.time.get_ticks() / 1000.0
        phase = getattr(self, "_anim_phase", 0.0)

        # Respiración/bob sutil para que "no sea una bolita muerta"
        breathe = math.sin(now * 7.5 + phase)
        y_offset = int(breathe * 1.2)
        cy = py + y_offset

        # Radio elástico muy pequeño
        radius = self.radius + int(math.sin(now * 10.0 + phase) * 0.6)
        radius = max(3, radius)

        # Gestos de carga: subimos guantes y "tamaño" un poco
        charge = max(self.pass_charge, self.kick_charge)
        max_charge = PASS_FORCE if self.pass_charge > 0 else (KICK_FORCE if self.kick_charge > 0 else 1)
        charge_ratio = 0.0
        if max_charge > 0:
            charge_ratio = max(0.0, min(1.0, charge / max_charge))
        glove_raise = int(radius * 0.22 * charge_ratio)

        # Sombra
        shadow_surf = pygame.Surface((radius * 3, radius), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 50),
                            (0, 0, radius * 3, radius))
        surface.blit(shadow_surf, (px - radius * 3 // 2, cy + radius - 3))

        # Cuerpo (uniforme de portero - color diferente)
        pygame.draw.circle(surface, self.color, (px, cy), radius)

        # Guantes (pequeños rectángulos a los lados)
        glove_color = (255, 165, 0)  # Naranja para guantes
        glove_w = 5
        glove_h = 8
        pygame.draw.rect(surface, glove_color,
                         (px - radius - glove_w + 2, cy - glove_h // 2 - glove_raise, glove_w, glove_h))
        pygame.draw.rect(surface, glove_color,
                         (px + radius - 2, cy - glove_h // 2 - glove_raise, glove_w, glove_h))

        # Borde
        pygame.draw.circle(surface, BLACK, (px, cy), radius, 2)

        # Ojos (blink) para gesto facial mínimo
        blink = (math.sin(now * 4.0 + phase) + 1.0) / 2.0
        eye_open = 1.0 if blink > 0.15 else 0.15
        eye_r = max(1, int(radius * 0.08))
        ex_off = max(2, int(radius * 0.25))
        ey = cy - int(radius * 0.05)
        pygame.draw.circle(surface, BLACK, (px - ex_off, ey), max(1, int(eye_r * eye_open)))
        pygame.draw.circle(surface, BLACK, (px + ex_off, ey), max(1, int(eye_r * eye_open)))

        # Indicador de jugador controlado
        if self.is_controlled:
            tri_y = cy - radius - 12
            pulse = (math.sin(pygame.time.get_ticks() / 150) + 1) / 2
            tri_color = (int(pulse * 80), int(220 + pulse * 35), int(160 + pulse * 40))
            points = [(px, tri_y - 6), (px - 6, tri_y + 2), (px + 6, tri_y + 2)]
            pygame.draw.polygon(surface, tri_color, points)
            
            # Dibujar nombre
            try: font_n = pygame.font.SysFont("Arial", 12, bold=True)
            except: font_n = pygame.font.Font(None, 12)
            name_str = self.player_data["name"]
            if self.player_data.get("is_captain"):
                name_str = "(C) " + name_str
            name_surf = font_n.render(name_str, True, WHITE)
            surface.blit(name_surf, (px - name_surf.get_width()//2, cy + radius + 15))
        else:
            # Número en la espalda
            try: font_num = pygame.font.SysFont("Arial", 10, bold=True)
            except: font_num = pygame.font.Font(None, 10)
            num_str = str(self.player_data.get("num", "1"))
            if self.player_data.get("is_captain"):
                num_str = "C"
            num_surf = font_num.render(num_str, True, self.team_data["accent"])
            surface.blit(num_surf, (px - num_surf.get_width()//2, cy - num_surf.get_height()//2))

        # Barras de carga de pase y tiro si están activas
        if self.pass_charge > 0 or self.kick_charge > 0:
            charge = max(self.pass_charge, self.kick_charge)
            max_c = PASS_FORCE if self.pass_charge > 0 else KICK_FORCE
            c_color = (100, 200, 255) if self.pass_charge > 0 else (255, 100, 100)
            bar_w = 26
            bar_h = 4
            pygame.draw.rect(surface, (40, 40, 40), (px - bar_w // 2, cy - radius - 10, bar_w, bar_h))
            fill_w = int((charge / max_c) * bar_w)
            pygame.draw.rect(surface, c_color, (px - bar_w // 2, cy - radius - 10, fill_w, bar_h))
