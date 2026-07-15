import pygame
import math
from settings import *


class Ball:
    def __init__(self, x, y):
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.radius = BALL_RADIUS
        self.owner = None       # Referencia al jugador que la posee
        self.last_touch = None  # Último equipo que tocó el balón ("left" o "right")
        self.last_touch_name = None # Nombre del último jugador
        self.assistant_name = None  # Nombre del jugador previo (asistente potencial)
        self.target_player = None   # Jugador al que va dirigido el pase exacto
        self.out_of_bounds = None   # "top", "bottom", "left", "right" o None
        self.z = 0                  # Altura (z-axis)
        self.vz = 0                 # Velocidad vertical
        self.is_through_pass = False
        self.rotation_angle = 0.0

    def reset(self, x, y):
        """Reposiciona el balón para saque central."""
        self.pos = pygame.math.Vector2(x, y)
        self.vel = pygame.math.Vector2(0, 0)
        self.owner = None
        self.last_touch_name = None
        self.assistant_name = None
        self.target_player = None
        self.out_of_bounds = None
        self.z = 0
        self.vz = 0
        self.is_through_pass = False
        self.rotation_angle = 0.0


    def update(self, dt, pitch_rect, left_goal_rect, right_goal_rect):
        # Resetear flag de fuera de banda cada frame (se re-detecta si aplica)
        self.out_of_bounds = None
        
        # Si es un pase exacto guiado
        if self.target_player:
            dir_vec = (self.target_player.pos - self.pos)
            dist = dir_vec.length()
            if dist > 10:
                # Velocidad proporcional: rápido al inicio, desacelerar al acercarse
                current_speed = self.vel.length()
                desired_speed = max(200, min(current_speed, dist * 3))  # Se frena conforme llega
                self.vel = dir_vec.normalize() * desired_speed
            else:
                self.target_player = None  # Llegó
                self.vel *= 0.3  # Frenazo suave al recibir
                
        # Mover por inercia
        self.pos += self.vel * dt
        
        # Actualizar rotación del balón en base a la velocidad
        speed = self.vel.length()
        if speed > 0:
            self.rotation_angle = (self.rotation_angle + (speed * dt) / max(1.0, self.radius)) % (2 * math.pi)
        
        # ── Física Z (Altura) ──
        if self.z > 0 or self.vz > 0:
            self.z += self.vz * dt
            self.vz -= 1200 * dt # Gravedad
            if self.z <= 0:
                self.z = 0
                self.vz *= -0.4 # Rebote amortiguado
                if abs(self.vz) < 50: self.vz = 0
                self.vel *= 0.7 # Pierde inercia al rebotar
 

        # Aplicar fricción solo si no es un pase magnético y está en el suelo
        if not self.target_player:
            fric = FRICTION if self.z <= 0 else 0.995 # Menos fricción en el aire
            self.vel *= fric

        # Si la velocidad es ínfima, detener
        if self.vel.length() < 3 and self.z <= 0:
            self.vel = pygame.math.Vector2(0, 0)

        # ── Detección de colisión con los postes ──
        left_post1 = pygame.math.Vector2(pitch_rect.left, left_goal_rect.top)
        left_post2 = pygame.math.Vector2(pitch_rect.left, left_goal_rect.bottom)
        right_post1 = pygame.math.Vector2(pitch_rect.right, right_goal_rect.top)
        right_post2 = pygame.math.Vector2(pitch_rect.right, right_goal_rect.bottom)
        
        for post in [left_post1, left_post2, right_post1, right_post2]:
            if self.pos.distance_to(post) < self.radius + 3:
                # Calcular vector de rebote
                normal = (self.pos - post).normalize() if self.pos.distance_to(post) > 0 else pygame.math.Vector2(1, 0)
                self.vel = self.vel.reflect(normal) * 0.6
                self.pos = post + normal * (self.radius + 4)
                from systems.audio_manager import audio_manager
                audio_manager.play_post_hit()
                break

        # ── Detección de gol (anti-tunneling) ──
        if self.pos.x < pitch_rect.left and left_goal_rect.top <= self.pos.y <= left_goal_rect.bottom:
            return "right"
        if self.pos.x > pitch_rect.right and right_goal_rect.top <= self.pos.y <= right_goal_rect.bottom:
            return "left"

        # ── Mantener balón dentro del campo si está en pase guiado ──
        # Si hay target_player, clampar la posición para que no se salga
        if self.target_player:
            self.pos.x = max(pitch_rect.left + self.radius, min(pitch_rect.right - self.radius, self.pos.x))
            self.pos.y = max(pitch_rect.top + self.radius, min(pitch_rect.bottom - self.radius, self.pos.y))
            return None

        # ── Detección de fuera de banda (solo balón libre) ──
        if self.pos.x - self.radius < pitch_rect.left:
            self.out_of_bounds = "left"
        elif self.pos.x + self.radius > pitch_rect.right:
            self.out_of_bounds = "right"
        elif self.pos.y - self.radius < pitch_rect.top:
            self.out_of_bounds = "top"
        elif self.pos.y + self.radius > pitch_rect.bottom:
            self.out_of_bounds = "bottom"

        return None

    def draw(self, surface):
        px, py = int(self.pos.x), int(self.pos.y)
        # Sombra (se aleja y se hace más pequeña según la altura)
        shadow_dist = self.z * 0.5
        shadow_scale = max(0.5, 1.0 - (self.z / 300))
        shadow_w = int(self.radius * 3 * shadow_scale)
        shadow_h = int(self.radius * shadow_scale)
        
        shadow_surf = pygame.Surface((shadow_w, shadow_h), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 40), (0, 0, shadow_w, shadow_h))
        surface.blit(shadow_surf, (px - shadow_w // 2, py + self.radius - 2 + shadow_dist))

        # Balón (se ve más grande según la altura)
        visual_radius = int(self.radius * (1.0 + self.z / 400))
        draw_y = py - int(self.z)
        
        # Color base blanco
        pygame.draw.circle(surface, WHITE, (px, draw_y), visual_radius)
        
        # Patrón detallado de pentágono de balón de fútbol giratorio
        pent_r = max(1.5, visual_radius * 0.35)
        pent_pts = []
        for i in range(5):
            a = self.rotation_angle + i * (2 * math.pi / 5)
            pt_x = px + int(math.cos(a) * pent_r)
            pt_y = draw_y + int(math.sin(a) * pent_r)
            pent_pts.append((pt_x, pt_y))
            
        # Pentagono central
        pygame.draw.polygon(surface, (30, 30, 30), pent_pts)
        pygame.draw.polygon(surface, BLACK, pent_pts, 1)
        
        # Paneles y líneas radiales
        for i in range(5):
            a = self.rotation_angle + i * (2 * math.pi / 5)
            start_x = px + int(math.cos(a) * pent_r)
            start_y = draw_y + int(math.sin(a) * pent_r)
            
            # Línea de unión del panel
            end_x = px + int(math.cos(a) * visual_radius)
            end_y = draw_y + int(math.sin(a) * visual_radius)
            pygame.draw.line(surface, (80, 80, 80), (start_x, start_y), (end_x, end_y), 1)
            
            # Paneles externos secundarios (pequeños triángulos/pentágonos en los bordes)
            sub_a1 = a - 0.22
            sub_a2 = a + 0.22
            mid_r = pent_r + (visual_radius - pent_r) * 0.6
            out_pts = [
                (start_x, start_y),
                (px + int(math.cos(sub_a1) * mid_r), draw_y + int(math.sin(sub_a1) * mid_r)),
                (px + int(math.cos(sub_a2) * mid_r), draw_y + int(math.sin(sub_a2) * mid_r))
            ]
            pygame.draw.polygon(surface, (40, 40, 40), out_pts)
            pygame.draw.polygon(surface, BLACK, out_pts, 1)

        # Borde exterior del balón
        pygame.draw.circle(surface, BLACK, (px, draw_y), visual_radius, 1)

