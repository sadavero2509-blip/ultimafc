import pygame
from settings import *


class SceneManager:
    """Controla el flujo entre escenas del juego con transiciones suaves."""

    def __init__(self, screen):
        self.screen = screen
        self.current_scene = None
        self.transition_alpha = 0
        self.transitioning = False
        self.next_scene = None
        self.next_kwargs = {}
        self.fade_speed = 600  # Alpha por segundo
        self.fading_out = False
        self.shared_data = {}  # Datos compartidos entre escenas (equipo elegido, etc.)
        self.scene_stack = []

    def set_scene(self, scene_class, **kwargs):
        """Cambia de escena inmediatamente (sin transición)."""
        if self.current_scene and hasattr(self.current_scene, 'on_exit'):
            self.current_scene.on_exit()
        self.current_scene = scene_class(self, **kwargs)

    def push_scene(self, scene_class, **kwargs):
        """Guarda la escena actual en la pila y cambia a una nueva."""
        if self.current_scene:
            self.scene_stack.append(self.current_scene)
        self.current_scene = scene_class(self, **kwargs)

    def pop_scene(self):
        """Vuelve a la escena anterior en la pila."""
        if self.scene_stack:
            if self.current_scene and hasattr(self.current_scene, 'on_exit'):
                self.current_scene.on_exit()
            self.current_scene = self.scene_stack.pop()
        else:
            # Fallback a menú principal si no hay nada en la pila
            from scenes.main_menu import MainMenuScene
            self.set_scene(MainMenuScene)

    def transition_to(self, scene_class, **kwargs):
        """Inicia una transición con fade a otra escena."""
        if self.transitioning:
            return
        self.transitioning = True
        self.fading_out = True
        self.transition_alpha = 0
        self.next_scene = scene_class
        self.next_kwargs = kwargs

    def handle_events(self, events):
        if self.current_scene and not self.transitioning:
            from systems.audio_manager import audio_manager
            for event in events:
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT, pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d):
                        audio_manager.play_sfx("move", 0.5)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        audio_manager.play_sfx("select", 0.8)
                    elif event.key == pygame.K_ESCAPE:
                        audio_manager.play_sfx("move", 0.7)
            self.current_scene.handle_events(events)

    def update(self, dt):
        if self.transitioning:
            if self.fading_out:
                self.transition_alpha += self.fade_speed * dt
                if self.transition_alpha >= 255:
                    self.transition_alpha = 255
                    # Cambio de escena en el punto de máxima opacidad
                    if self.current_scene and hasattr(self.current_scene, 'on_exit'):
                        self.current_scene.on_exit()
                    self.current_scene = self.next_scene(self, **self.next_kwargs)
                    self.fading_out = False
            else:
                self.transition_alpha -= self.fade_speed * dt
                if self.transition_alpha <= 0:
                    self.transition_alpha = 0
                    self.transitioning = False
                    self.next_scene = None
                    self.next_kwargs = {}

        if self.current_scene:
            self.current_scene.update(dt)

    def draw(self):
        if self.current_scene:
            self.current_scene.draw(self.screen)

        # Dibujar overlay de transición
        if self.transitioning and self.transition_alpha > 0:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.fill(BLACK)
            overlay.set_alpha(int(self.transition_alpha))
            self.screen.blit(overlay, (0, 0))


class BaseScene:
    """Clase base para todas las escenas."""

    def __init__(self, manager):
        self.manager = manager

    def handle_events(self, events):
        pass

    def update(self, dt):
        pass

    def draw(self, surface):
        pass

    def on_exit(self):
        pass
