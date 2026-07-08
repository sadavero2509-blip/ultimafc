import pygame
from settings import WIDTH, HEIGHT

class TouchManager:
    def __init__(self):
        self.enabled = False # Solo se activa en Android o modo test
        self.joystick_pos = pygame.math.Vector2(150, HEIGHT - 150)
        self.joystick_radius = 70
        self.knob_pos = pygame.math.Vector2(self.joystick_pos)
        self.knob_radius = 35
        
        self.is_dragging = False
        self.active_finger_id = -1
        
        # Botones (Posiciones relativas a la derecha)
        self.buttons = {
            "PASS": {"rect": pygame.Rect(WIDTH - 180, HEIGHT - 100, 80, 80), "color": (50, 200, 50), "label": "A"},
            "KICK": {"rect": pygame.Rect(WIDTH - 100, HEIGHT - 180, 80, 80), "color": (200, 50, 50), "label": "X"},
            "THROUGH": {"rect": pygame.Rect(WIDTH - 180, HEIGHT - 180, 80, 80), "color": (200, 200, 50), "label": "Y"},
            "CROSS": {"rect": pygame.Rect(WIDTH - 100, HEIGHT - 100, 80, 80), "color": (50, 50, 200), "label": "B"}
        }
        
        self.pressed_actions = set()

    def handle_event(self, event):
        if not self.enabled: return
        
        if event.type == pygame.FINGERDOWN:
            fx, fy = event.x * WIDTH, event.y * HEIGHT
            # Check Joystick
            dist = pygame.math.Vector2(fx, fy).distance_to(self.joystick_pos)
            if dist < self.joystick_radius * 2:
                self.is_dragging = True
                self.active_finger_id = event.finger_id
                self._update_knob(fx, fy)
            
            # Check Buttons
            for action, btn in self.buttons.items():
                if btn["rect"].collidepoint(fx, fy):
                    self.pressed_actions.add(action)

        elif event.type == pygame.FINGERMOVE:
            if self.is_dragging and event.finger_id == self.active_finger_id:
                fx, fy = event.x * WIDTH, event.y * HEIGHT
                self._update_knob(fx, fy)

        elif event.type == pygame.FINGERUP:
            if event.finger_id == self.active_finger_id:
                self.is_dragging = False
                self.active_finger_id = -1
                self.knob_pos = pygame.math.Vector2(self.joystick_pos)
            
            # Limpiar botones (esto es simplificado, idealmente rastrear por finger_id)
            self.pressed_actions.clear()

    def _update_knob(self, x, y):
        dir = pygame.math.Vector2(x, y) - self.joystick_pos
        if dir.length() > self.joystick_radius:
            dir = dir.normalize() * self.joystick_radius
        self.knob_pos = self.joystick_pos + dir

    def get_movement(self):
        if not self.is_dragging: return pygame.math.Vector2(0,0)
        dir = (self.knob_pos - self.joystick_pos)
        if dir.length() > 10:
            return dir.normalize()
        return pygame.math.Vector2(0,0)

    def draw(self, screen):
        if not self.enabled: return
        
        # Dibujar Joystick (Base)
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.circle(overlay, (255, 255, 255, 50), self.joystick_pos, self.joystick_radius)
        pygame.draw.circle(overlay, (255, 255, 255, 120), self.knob_pos, self.knob_radius)
        
        # Dibujar Botones
        for action, btn in self.buttons.items():
            alpha = 180 if action in self.pressed_actions else 80
            col = (*btn["color"], alpha)
            pygame.draw.ellipse(overlay, col, btn["rect"])
            # Etiqueta
            try:
                font = pygame.font.SysFont("Arial", 24, bold=True)
            except:
                font = pygame.font.Font(None, 24)
            txt = font.render(btn["label"], True, (255, 255, 255))
            overlay.blit(txt, (btn["rect"].centerx - 10, btn["rect"].centery - 12))
            
        screen.blit(overlay, (0, 0))

touch_manager = TouchManager()
