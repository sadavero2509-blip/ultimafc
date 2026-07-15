import pygame
import time
import math
import random
from settings import *
from .main_menu import BaseScene

class EventTeaserScene(BaseScene):
    def __init__(self, manager):
        super().__init__(manager)
        from data.event_worldcup import is_event_active
        active = is_event_active()
        
        self.banners = [
            {
                "title": "¡EVENTO ACTIVO: COPA DEL MUNDO 2026!" if active else "PRÓXIMAMENTE: COPA DEL MUNDO 2026",
                "subtitle": "¡Los mejores jugadores del Mundial con estadísticas mejoradas!" if active else "¡El evento más grande del fútbol está por comenzar!",
                "hints": [
                    {"ovr": 95, "nat": "BRA", "pos": "LW", "type": "EVENTO", "name": "Vinni Jr."},
                    {"ovr": 94, "nat": "ARG", "pos": "RW", "type": "EVENTO", "name": "Lio Messy"},
                    {"ovr": 94, "nat": "FRA", "pos": "LW", "type": "EVENTO", "name": "Kylian Mbappeh"}
                ],
                "color": (0, 104, 71) # Verde México
            },
            {
                "title": "LEYENDAS MUNDIALISTAS DISPONIBLES" if active else "LEYENDAS MUNDIALISTAS",
                "subtitle": "¡Consigue a los héroes que hicieron historia en los Mundiales!" if active else "Inmortaliza a los héroes de la historia.",
                "hints": [
                    {"ovr": 99, "nat": "BRA", "pos": "ST", "type": "LEYENDA", "name": "Pellé"},
                    {"ovr": 98, "nat": "ARG", "pos": "CAM", "type": "LEYENDA", "name": "Diego Maradonae"}
                ],
                "color": (191, 10, 48) # Rojo
            }
        ]
        self.current_banner = 0
        self.fade_alpha = 255
        self.timer = 0
        self.auto_timer = 0
        self.transitioning = False
        
        # Sincronización y estado de carga del modo Ultimate
        self.waiting_for_load = False
        self.skip_teaser = not active  # Si el evento ya terminó, saltar teaser
        try:
            from systems.ultimate_manager import ultimate_manager
            # Si no se ha cargado ningún dato del club y no está intentando conectar actualmente, forzar carga de seguridad
            if ultimate_manager.team_name == "Mi Club" and ultimate_manager.online_status not in ("ONLINE", "CONNECTING"):
                ultimate_manager.online_status = "CONNECTING"
                import threading
                threading.Thread(target=ultimate_manager.load_ultimate, daemon=True).start()
            # Si debemos saltar el teaser, activar transición inmediata
            if self.skip_teaser:
                self.waiting_for_load = True
        except Exception as e:
            print(f"Error en sincronización de teaser: {e}")
        
        # Partículas decorativas (Confeti/Estrellas)
        self.particles = [{"x": random.randint(0, WIDTH), "y": random.randint(0, HEIGHT), "s": random.uniform(1, 3)} for _ in range(50)]

    def update(self, dt):
        self.timer += dt
        self.auto_timer += dt
        
        # Si se activó la pantalla de carga, evaluar transiciones una vez completada la sincronización
        if self.waiting_for_load:
            try:
                from systems.ultimate_manager import ultimate_manager
                if ultimate_manager.online_status != "CONNECTING":
                    self.waiting_for_load = False
                    if not ultimate_manager.badge or not ultimate_manager.kit or ultimate_manager.team_name == "Mi Club":
                        from .ultimate_setup import UltimateSetupScene
                        self.manager.transition_to(UltimateSetupScene)
                    else:
                        from .ultimate_hub import UltimateHubScene
                        self.manager.transition_to(UltimateHubScene)
                    return
            except Exception as e:
                print(f"Error al evaluar transición tras carga: {e}")
                self.waiting_for_load = False
        
        # Movimiento automático de banners cada 4 segundos
        if self.auto_timer > 4.0:
            self._next_banner()
            self.auto_timer = 0
            
        # Animación de partículas
        for p in self.particles:
            p["y"] += p["s"]
            if p["y"] > HEIGHT: p["y"] = -10; p["x"] = random.randint(0, WIDTH)

    def _next_banner(self):
        self.current_banner = (self.current_banner + 1) % len(self.banners)
        self.fade_alpha = 0 # Efecto de flash al cambiar

    def draw(self, screen):
        banner = self.banners[self.current_banner]
        
        # Fondo Degradado
        for i in range(HEIGHT):
            col = [max(0, banner["color"][c] - i//5) for c in range(3)]
            pygame.draw.line(screen, col, (0, i), (WIDTH, i))
            
        # Dibujar partículas
        for p in self.particles:
            pygame.draw.circle(screen, (255, 255, 255, 100), (int(p["x"]), int(p["y"])), int(p["s"]))

        # Brillo animado
        glow = (math.sin(time.time() * 2) + 1) / 2
        
        # Título Principal
        self.draw_text(screen, banner["title"], WIDTH//2, 150, size=50, bold=True, center=True, color=WHITE)
        self.draw_text(screen, banner["subtitle"], WIDTH//2, 210, size=24, center=True, color=(200, 255, 200))
        
        from systems.card_renderer import card_renderer
        
        # Dibujar Pistas (Cartas del Evento)
        card_w, card_h = 180, 270
        scale = 1.0
        spacing = 40
        total_w = len(banner["hints"]) * card_w + (len(banner["hints"])-1) * spacing
        start_x = (WIDTH - total_w) // 2
        
        for i, hint in enumerate(banner["hints"]):
            x = start_x + i * (card_w + spacing)
            y = 280
            
            # Crear objeto de jugador temporal para el renderizador
            from data.event_worldcup import is_event_active
            active = is_event_active()
            temp_p = {
                "name": hint["name"] if active else "???",
                "ovr": hint["ovr"],
                "pos": hint["pos"],
                "nat": hint["nat"],
                "is_legend": (hint["type"] == "LEYENDA"),
                "card_type": "WORLDCUP" if hint["type"] == "EVENTO" else "WORLDCUP_LEGEND",
                "s": {
                    "speed": hint["ovr"] - 2,
                    "shot": hint["ovr"] - 3,
                    "passing": hint["ovr"] - 5,
                    "dribbling": hint["ovr"] - 1,
                    "defense": 40,
                    "physical": 75
                }
            }
            
            # Renderizar la carta real
            card_renderer.render_card(screen, temp_p, x, y, scale=scale)

        # Indicadores de Banner (Puntos abajo)
        for i in range(len(self.banners)):
            col = WHITE if i == self.current_banner else (100, 100, 100)
            pygame.draw.circle(screen, col, (WIDTH//2 - 20 + i*40, 620), 6)

        # Botón de acción
        pulse = (math.sin(time.time() * 5) + 1) / 2
        alpha = int(150 + 105 * pulse)
        self.draw_text(screen, "PRESIONA [ENTER] PARA CONTINUAR", WIDTH//2, 700, size=26, bold=True, center=True, color=WHITE, alpha=alpha)
        self.draw_text(screen, "[← / →] Cambiar Banner", WIDTH//2, 740, size=16, center=True, color=(180, 180, 180))

        # Efecto de transicion inicial
        if self.fade_alpha > 0:
            s = pygame.Surface((WIDTH, HEIGHT))
            s.fill((255, 255, 255))
            s.set_alpha(self.fade_alpha)
            screen.blit(s, (0,0))
            self.fade_alpha = max(0, self.fade_alpha - 15)

        # Dibujar pantalla de carga si estamos esperando la sincronización
        if self.waiting_for_load:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.fill((10, 15, 25))
            overlay.set_alpha(230)
            screen.blit(overlay, (0, 0))
            
            # Texto animado
            dots = "." * (int(time.time() * 3) % 4)
            self.draw_text(screen, "Sincronizando club con el servidor" + dots, WIDTH//2, HEIGHT//2 - 25, size=24, bold=True, center=True, color=UI_ACCENT)
            self.draw_text(screen, "Por favor, espera unos segundos...", WIDTH//2, HEIGHT//2 + 15, size=16, center=True, color=UI_TEXT_DIM)

    def handle_events(self, events):
        if self.waiting_for_load:
            return  # Ignorar eventos mientras carga
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    from systems.ultimate_manager import ultimate_manager
                    
                    # Si todavía está intentando conectar o cargar de fondo, bloquear y esperar
                    if ultimate_manager.online_status == "CONNECTING":
                        self.waiting_for_load = True
                    else:
                        # Si ya terminó de cargar, transicionamos basándonos en si tiene club guardado
                        if not ultimate_manager.badge or not ultimate_manager.kit or ultimate_manager.team_name == "Mi Club":
                            from .ultimate_setup import UltimateSetupScene
                            self.manager.transition_to(UltimateSetupScene)
                        else:
                            from .ultimate_hub import UltimateHubScene
                            self.manager.transition_to(UltimateHubScene)
                if event.key == pygame.K_RIGHT:
                    self._next_banner()
                    self.auto_timer = 0
                if event.key == pygame.K_LEFT:
                    self.current_banner = (self.current_banner - 1) % len(self.banners)
                    self.fade_alpha = 0
                    self.auto_timer = 0

    def draw_text(self, screen, text, x, y, size=20, color=(255, 255, 255), bold=False, center=False, alpha=255):
        # Implementación local de draw_text para evitar dependencias
        font = pygame.font.SysFont("Arial", size, bold=bold)
        surf = font.render(str(text), True, color)
        if alpha < 255: surf.set_alpha(alpha)
        rect = surf.get_rect()
        if center: rect.center = (x, y)
        else: rect.topleft = (x, y)
        screen.blit(surf, rect)
