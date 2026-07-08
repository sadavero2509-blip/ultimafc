import pygame
from settings import *


class Pitch:
    def __init__(self, surface):
        self.surface = surface

        # Dimensiones de campo relativas a la ventana (dejando margen)
        self.margin = 35  # Reducido (50→35) para campo más grande
        self.width = WIDTH - self.margin * 2
        self.height = HEIGHT - self.margin * 2
        self.rect = pygame.Rect(self.margin, self.margin, self.width, self.height)

        self.center = (WIDTH // 2, HEIGHT // 2)

        # ── Rectángulos de portería (para detección de gol) ──
        goal_width = 14
        goal_height = 110
        self.left_goal_rect = pygame.Rect(
            self.margin - goal_width,
            self.center[1] - goal_height // 2,
            goal_width,
            goal_height
        )
        self.right_goal_rect = pygame.Rect(
            WIDTH - self.margin,
            self.center[1] - goal_height // 2,
            goal_width,
            goal_height
        )

        # Áreas grandes y pequeñas proporcionadas al nuevo zoom
        self.left_area = pygame.Rect(self.margin, self.center[1] - 100, 100, 200)
        self.left_small_area = pygame.Rect(self.margin, self.center[1] - 40, 40, 80)
        self.right_area = pygame.Rect(WIDTH - self.margin - 100, self.center[1] - 100, 100, 200)
        self.right_small_area = pygame.Rect(WIDTH - self.margin - 40, self.center[1] - 40, 40, 80)

        # ── Generar Público ──
        import random
        self.crowd_particles = []
        colors = [(200, 50, 50), (50, 100, 200), (200, 200, 200), (250, 200, 50), (50, 200, 100), (100, 50, 150)]
        for _ in range(1200):
            margin_choice = random.choice(["top", "bottom", "left", "right"])
            if margin_choice == "top":
                x = random.randint(0, WIDTH)
                y = random.randint(0, self.margin - 5)
            elif margin_choice == "bottom":
                x = random.randint(0, WIDTH)
                y = random.randint(HEIGHT - self.margin + 5, HEIGHT)
            elif margin_choice == "left":
                x = random.randint(0, self.margin - 5)
                y = random.randint(0, HEIGHT)
            else:
                x = random.randint(WIDTH - self.margin + 5, WIDTH)
                y = random.randint(0, HEIGHT)
                
            # Evitar dibujar público justo detrás de las porterías
            if margin_choice in ["left", "right"]:
                if self.center[1] - 70 < y < self.center[1] + 70:
                    continue
                    
            self.crowd_particles.append({
                "x": x,
                "y": y,
                "color": random.choice(colors),
                "phase": random.uniform(0, 6.28),
                "speed": random.uniform(0.003, 0.008)
            })

    def check_goal(self, ball):
        """Verifica si el balón entró en una portería.
        Retorna 'left' si gol en portería izquierda (punto para equipo derecho),
        'right' si gol en portería derecha (punto para equipo izquierdo),
        o None si no hay gol."""
        if self.left_goal_rect.collidepoint(ball.pos.x, ball.pos.y):
            return "right"  # Equipo derecho anotó
        if self.right_goal_rect.collidepoint(ball.pos.x, ball.pos.y):
            return "left"   # Equipo izquierdo anotó
        return None

    def draw(self):
        # ── Franjas de césped alternas ──
        stripe_width = self.width // 10
        for i in range(12):
            x = self.margin + i * stripe_width - stripe_width
            color = GREEN_PITCH if i % 2 == 0 else GREEN_PITCH_ALT
            pygame.draw.rect(self.surface, color,
                             (x, self.margin, stripe_width, self.height))

        # ── Gradas y Público ──
        # Fondo de gradas oscuras
        pygame.draw.rect(self.surface, (20, 20, 25), (0, 0, WIDTH, self.margin))
        pygame.draw.rect(self.surface, (20, 20, 25), (0, HEIGHT - self.margin, WIDTH, self.margin))
        pygame.draw.rect(self.surface, (20, 20, 25), (0, 0, self.margin, HEIGHT))
        pygame.draw.rect(self.surface, (20, 20, 25), (WIDTH - self.margin, 0, self.margin, HEIGHT))

        # Dibujar público animado
        import math
        t = pygame.time.get_ticks()
        for p in getattr(self, 'crowd_particles', []):
            offset_y = math.sin(t * p["speed"] + p["phase"]) * 2
            pygame.draw.circle(self.surface, p["color"], (p["x"], int(p["y"] + offset_y)), 2)

        # ── Líneas de la cancha ──
        # Líneas exteriores
        pygame.draw.rect(self.surface, WHITE, self.rect, 3)

        # Línea central
        pygame.draw.line(self.surface, WHITE,
                         (self.center[0], self.margin),
                         (self.center[0], HEIGHT - self.margin), 3)

        # Círculo central proporcionado
        pygame.draw.circle(self.surface, WHITE, self.center, 52, 3)
        pygame.draw.circle(self.surface, WHITE, self.center, 4)  # Punto de saque

        # Áreas - Lado izquierdo
        pygame.draw.rect(self.surface, WHITE, self.left_area, 3)
        pygame.draw.rect(self.surface, WHITE, self.left_small_area, 3)
        # Punto penal izquierdo
        pygame.draw.circle(self.surface, WHITE,
                           (self.margin + 70, self.center[1]), 3)

        # Áreas - Lado derecho
        pygame.draw.rect(self.surface, WHITE, self.right_area, 3)
        pygame.draw.rect(self.surface, WHITE, self.right_small_area, 3)
        # Punto penal derecho
        pygame.draw.circle(self.surface, WHITE,
                           (WIDTH - self.margin - 70, self.center[1]), 3)

        # ── Porterías ──
        # Red de portería (fondo de la portería)
        # Izquierda
        net_rect_l = self.left_goal_rect.copy()
        pygame.draw.rect(self.surface, (180, 180, 180), net_rect_l)
        # Dibujar rejilla de red
        for ny in range(net_rect_l.top, net_rect_l.bottom, 8):
            pygame.draw.line(self.surface, (140, 140, 140),
                             (net_rect_l.left, ny), (net_rect_l.right, ny), 1)
        for nx in range(net_rect_l.left, net_rect_l.right, 8):
            pygame.draw.line(self.surface, (140, 140, 140),
                             (nx, net_rect_l.top), (nx, net_rect_l.bottom), 1)
        pygame.draw.rect(self.surface, WHITE, net_rect_l, 3)

        # Derecha
        net_rect_r = self.right_goal_rect.copy()
        pygame.draw.rect(self.surface, (180, 180, 180), net_rect_r)
        for ny in range(net_rect_r.top, net_rect_r.bottom, 8):
            pygame.draw.line(self.surface, (140, 140, 140),
                             (net_rect_r.left, ny), (net_rect_r.right, ny), 1)
        for nx in range(net_rect_r.left, net_rect_r.right, 8):
            pygame.draw.line(self.surface, (140, 140, 140),
                             (nx, net_rect_r.top), (nx, net_rect_r.bottom), 1)
        pygame.draw.rect(self.surface, WHITE, net_rect_r, 3)

        # Esquinas (arcos de esquina)
        corner_radius = 15
        # Esquina superior izquierda
        pygame.draw.arc(self.surface, WHITE,
                        (self.margin - corner_radius, self.margin - corner_radius,
                         corner_radius * 2, corner_radius * 2),
                        -1.5708, 0, 2)
        # Esquina inferior izquierda
        pygame.draw.arc(self.surface, WHITE,
                        (self.margin - corner_radius, HEIGHT - self.margin - corner_radius,
                         corner_radius * 2, corner_radius * 2),
                        0, 1.5708, 2)
        # Esquina superior derecha
        pygame.draw.arc(self.surface, WHITE,
                        (WIDTH - self.margin - corner_radius, self.margin - corner_radius,
                         corner_radius * 2, corner_radius * 2),
                        3.1416, 4.7124, 2)
        # Esquina inferior derecha
        pygame.draw.arc(self.surface, WHITE,
                        (WIDTH - self.margin - corner_radius, HEIGHT - self.margin - corner_radius,
                         corner_radius * 2, corner_radius * 2),
                        1.5708, 3.1416, 2)
