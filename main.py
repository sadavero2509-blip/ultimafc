import sys
import traceback
import os

# --- HOT-PATCHING EN VIVO (Priorizar código en disco sobre el congelado del .exe) ---
if getattr(sys, 'frozen', False):
    exe_dir = os.path.dirname(sys.executable)
    if exe_dir not in sys.path:
        sys.path.insert(0, exe_dir)
else:
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)


def run_game(screen):
    from settings import WIDTH, HEIGHT, FPS
    from scene_manager import SceneManager
    from scenes.loading import LoadingScene
    from scenes.login import LoginScene
    from scenes.main_menu import MainMenuScene
    import pygame
    
    IS_ANDROID = 'ANDROID_ARGUMENT' in os.environ or (hasattr(pygame, 'android'))
    
    if IS_ANDROID:
        from systems.touch_manager import touch_manager
        touch_manager.enabled = True
        
    pygame.display.set_caption("Futbol Game Ultimate")
    clock = pygame.time.Clock()
    
    from systems.audio_manager import audio_manager

    # --- INTEGRACIÓN DE SERVIDOR ---
    try:
        from systems.network import NetworkManager
        import time, json
        network = NetworkManager()
        
        # Intentar Auto-Login si existen credenciales
        creds_path = "saves/creds.json"
        logged_in = False
        if os.path.exists(creds_path):
            try:
                with open(creds_path, "r") as f:
                    c = json.load(f)
                    success, _ = network.login(c["user"], c["pass"])
                    logged_in = success
                    if logged_in:
                        try:
                            from systems.ultimate_manager import ultimate_manager
                            import threading
                            threading.Thread(target=ultimate_manager.load_ultimate, daemon=True).start()
                        except Exception as e:
                            print(f"Error cargando club tras auto-login: {e}")
            except: pass
            
        initial_scene = MainMenuScene if logged_in else LoginScene
        if not logged_in:
            # Si no hay login, igual conectamos un usuario temporal por si acaso,
            # pero la escena de Login sobreescribirá esto.
            network.connect(f"Guest_{int(time.time()) % 1000}")
    except Exception as e:
        print(f"Modo Offline/Remoto: {e}")
        from scenes.main_menu import MainMenuScene
        initial_scene = MainMenuScene

    scene_manager = SceneManager(screen)
    scene_manager.set_scene(initial_scene)

    mouse_timer = 2.0
    mouse_visible = True
    
    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        events = pygame.event.get()
        
        # Mouse visibility logic
        mouse_activity = False
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            if event.type in (pygame.MOUSEMOTION, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP):
                mouse_activity = True
                
            from systems.audio_manager import MUSIC_END_EVENT, audio_manager
            if event.type == MUSIC_END_EVENT:
                audio_manager.play_next_song()
            
            from systems.touch_manager import touch_manager
            touch_manager.handle_event(event)

        if mouse_activity:
            mouse_timer = 2.0
            if not mouse_visible:
                pygame.mouse.set_visible(True)
                mouse_visible = True
        else:
            if mouse_timer > 0:
                mouse_timer -= dt
                if mouse_timer <= 0 and mouse_visible:
                    pygame.mouse.set_visible(False)
                    mouse_visible = False

        if not running: break
        scene_manager.handle_events(events)
        scene_manager.update(dt)
        scene_manager.draw()
        pygame.display.flip()

    # Servidor local removido (se requiere servidor real externo)
    pygame.quit()
    sys.exit()

def main():
    import pygame
    pygame.init()
    IS_ANDROID = 'ANDROID_ARGUMENT' in os.environ or (hasattr(pygame, 'android'))
    try:
        if IS_ANDROID:
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            from settings import WIDTH, HEIGHT
            screen = pygame.display.set_mode((WIDTH, HEIGHT))
            
        run_game(screen)
    except Exception as e:
        error_msg = traceback.format_exc()
        print("\n" + "="*50)
        print("CRASH DETECTADO:")
        print(error_msg)
        print("="*50 + "\n")
        
        font = pygame.font.Font(None, 24)
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or event.type == pygame.FINGERDOWN:
                    running = False
            screen.fill((150, 0, 0))
            y = 20
            for line in error_msg.split('\n'):
                while len(line) > 60:
                    screen.blit(font.render(line[:60], True, (255,255,255)), (20, y))
                    y += 30
                    line = line[60:]
                screen.blit(font.render(line, True, (255,255,255)), (20, y))
                y += 30
            pygame.display.flip()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
