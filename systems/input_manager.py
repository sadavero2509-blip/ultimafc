import pygame

class InputManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(InputManager, cls).__new__(cls)
            cls._instance.init_joysticks()
        return cls._instance

    def init_joysticks(self):
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(i) for i in range(pygame.joystick.get_count())]
        for j in self.joysticks:
            j.init()
            print(f"Mando detectado: {j.get_name()}")

    def get_movement(self):
        """Devuelve un Vector2 con la dirección de movimiento (Solo Flechas y Mando)."""
        from systems.touch_manager import touch_manager
        keys = pygame.key.get_pressed()
        move = pygame.math.Vector2(0, 0)
        
        # Teclado (SOLO FLECHAS)
        if keys[pygame.K_LEFT]: move.x -= 1
        if keys[pygame.K_RIGHT]: move.x += 1
        if keys[pygame.K_UP]: move.y -= 1
        if keys[pygame.K_DOWN]: move.y += 1
        
        # Mando
        for j in self.joysticks:
            try:
                if j.get_numaxes() > 1:
                    jx = j.get_axis(0)
                    jy = j.get_axis(1)
                    if abs(jx) > 0.2: move.x += jx
                    if abs(jy) > 0.2: move.y += jy
                if j.get_numhats() > 0:
                    hat = j.get_hat(0)
                    move.x += hat[0]
                    move.y -= hat[1]
            except:
                pass
            
        # Touch (Joystick Virtual)
        if touch_manager.enabled:
            move += touch_manager.get_movement()
            
        if move.length() > 0:
            return move.normalize()
        return move

    def is_action_pressed(self, action):
        """Comprueba si se ha pulsado una acción (Tiro, Pase, etc.)."""
        from systems.touch_manager import touch_manager
        keys = pygame.key.get_pressed()
        
        # Touch check
        if touch_manager.enabled and action in touch_manager.pressed_actions:
            return True
            
        if action == "PASS": # S
            if keys[pygame.K_s]: return True
            for j in self.joysticks:
                try:
                    if j.get_numbuttons() > 0 and j.get_button(0): return True # A
                except: pass
        
        if action == "KICK": # A
            if keys[pygame.K_a]: return True
            for j in self.joysticks:
                try:
                    if j.get_numbuttons() > 2 and j.get_button(2): return True # X
                except: pass
                
        if action == "THROUGH": # W
            if keys[pygame.K_w]: return True
            for j in self.joysticks:
                try:
                    if j.get_numbuttons() > 3 and j.get_button(3): return True # Y
                except: pass
        
        if action == "CROSS": # D
            if keys[pygame.K_d]: return True
            for j in self.joysticks:
                try:
                    if j.get_numbuttons() > 1 and j.get_button(1): return True # B
                except: pass
                
        if action == "PRESS": # S (Cuando no tienes balón)
            if keys[pygame.K_s]: return True

        if action == "SPRINT": # E
            if keys[pygame.K_e]: return True
            for j in self.joysticks:
                try:
                    if (j.get_numbuttons() > 5 and j.get_button(5)) or (j.get_numaxes() > 5 and j.get_axis(5) > 0.5): return True # R1 o R2
                except: pass
                
        if action == "TACKLE": # A
            if keys[pygame.K_a]: return True
            for j in self.joysticks:
                try:
                    if j.get_numbuttons() > 2 and j.get_button(2): return True # X
                except: pass
                
        return False

input_manager = InputManager()
