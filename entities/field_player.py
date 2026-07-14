import pygame
import math
import random
from settings import *

class FieldPlayer:
    """Jugador universal de campo, puede ser controlado por humano o IA."""

    # Estados de la IA
    STATE_POSITION = "position"     # Mantener formación fluida
    STATE_CHASE = "chase"           # Perseguir el balón (IA Activa)
    STATE_DEFEND = "defend"         # Retroceder agresivamente
    STATE_ATTACK = "attack"         # Desmarcarse hacia adelante

    def __init__(self, x, y, team_data, player_data, side="left", formation_pos=(0.5, 0.5)):
        self.pos = pygame.math.Vector2(x, y)
        self.radius = PLAYER_RADIUS
        self.team_data = team_data
        self.player_data = player_data
        self.color = team_data["primary"]
        self.secondary = team_data["secondary"]
        self.side = side
        
        self.formation_pos = formation_pos
        self.human_speed = PLAYER_SPEED * (player_data["s"]["speed"] / 80.0)
        self.difficulty = 5 # Default
        self.ai_speed = AI_SPEED * (player_data["s"]["speed"] / 80.0)
        
        self.direction = pygame.math.Vector2(1 if side == "left" else -1, 0)
        self.has_ball = False
        
        # Flags de control
        self.is_controlled = False
        self.is_active_ai = False  # Si es True, es el presionante principal
        
        # Cooldowns y Timers
        self.kick_cooldown = 0
        self.pass_cooldown = 0
        self.tackle_timer = 0
        self.kick_charge = 0.0
        self.pass_charge = 0.0
        self.receive_cooldown = 0  # Prevents accidental pass after receiving ball
        
        # Estado AI
        self.state = self.STATE_POSITION
        self.state_timer = 0
        self.jitter = pygame.math.Vector2(
            random.uniform(-AI_POSITION_JITTER, AI_POSITION_JITTER),
            random.uniform(-AI_POSITION_JITTER, AI_POSITION_JITTER)
        )
        
        # --- Animación visual simplificada (no afecta físicas) ---
        self._anim_phase = random.random() * 6.28318530718
        self._match_scene_ref = None  # Referencia efímera para efectos (goal_freeze)
        self._last_move_speed = 0.0   # Aproximación (ya se actualiza durante update)
        
        # Stamina / Energy System
        # Start from player_data if exists (Career Mode persistence), else 100
        self.energy = player_data.get("energy", 100.0)
        self.max_energy = 100.0
        
        self.match_stats = {
            "name": self.player_data["name"],
            "goals": 0, "assists": 0, "passes_completed": 0, "steals": 0, "saves": 0, 
            "yellow_cards": 0, "red_card": 0, "rating": 6.0
        }
        self.red_card = False
        self.yellow_cards = 0
        self.is_injured = False
        self.injury_severity = 0 # 0-100

    def apply_difficulty(self, difficulty):
        """Escala la IA de forma realista basándose en el nivel (1-10)."""
        self.difficulty = difficulty
        
        # Curva de velocidad: Niveles bajos son lentos, niveles altos son muy atléticos
        # 1-3: Amateur, 4-6: Profesional, 7-9: Clase Mundial, 10: Leyenda
        diff_mult = 0.72 + (self.difficulty * 0.06) # 0.78 a 1.32
        self.ai_speed *= diff_mult
        
        # Tiempo de reacción: cuánto tarda en 'ver' que el balón cambió de dueño o dirección
        self.reaction_delay = max(0.03, 0.50 - (self.difficulty * 0.05)) 
        
        # Probabilidad de robo: reforzada para defensas más fuertes
        self.tackle_prob = 0.02 + (self.difficulty * 0.016) # 3.6% a 18% (era 2.2% a 13%)
        
        # Error de IA: Probabilidad de fallar la dirección de un pase o tiro
        self.ai_error_rate = max(0.02, 0.40 - (self.difficulty * 0.04))
        
        # Agresividad defensiva: qué tan rápido retroceden los defensas
        self.def_aggression = 0.6 + (self.difficulty * 0.06) # 0.66 a 1.20

    def get_formation_world_pos(self, pitch_rect, ball_pos, my_team_has_ball, match_scene=None):
        """Calcula la posición táctica basándose en el rol del jugador (Defensa, Medio, Ataque)."""
        pos_type = self.player_data.get("pos", "CM")
        is_defender = pos_type in ["CB", "LB", "RB", "LWB", "RWB"]
        is_attacker = pos_type in ["ST", "CF", "LW", "RW"]
        
        # 1. Base X y Y según formación
        base_x = pitch_rect.left + self.formation_pos[0] * pitch_rect.width
        base_y = pitch_rect.top + self.formation_pos[1] * pitch_rect.height
        
        # 2. Influencia de la posición del balón
        ball_rel_x = ball_pos.x - pitch_rect.centerx
        ball_shift_x = ball_rel_x * 0.35  
        
        ball_rel_y = ball_pos.y - pitch_rect.centery
        ball_shift_y = ball_rel_y * 0.20
        
        # 3. Cambio Táctico (Roles Dinámicos IA Real)
        tactical_shift_x = 0
        gk_has_ball = match_scene and (match_scene.left_gk.has_ball or match_scene.right_gk.has_ball)
        
        if gk_has_ball:
            retreat_dist = 220
            tactical_shift_x = -retreat_dist if self.side == "left" else retreat_dist
        elif my_team_has_ball:
            # Ofensiva AGRESIVA (EA FC Style)
            if is_defender:
                tactical_shift_x = 160 if self.side == "left" else -160 # Suben al medio campo
            elif is_attacker:
                tactical_shift_x = 450 if self.side == "left" else -450 # Presión total en área rival
            else:
                tactical_shift_x = 320 if self.side == "left" else -320 # Apoyo ofensivo total
        else:
            # Defensiva AGRESIVA (Bloque Bajo Compacto)
            if is_attacker:
                tactical_shift_x = -150 if self.side == "left" else 150 # Bajan a presionar la salida
            else:
                tactical_shift_x = -280 if self.side == "left" else 280 # Todos defienden su arco
            
        x = base_x + ball_shift_x + tactical_shift_x + self.jitter.x
        y = base_y + ball_shift_y + self.jitter.y
        
        y = min(max(y, pitch_rect.top + 30), pitch_rect.bottom - 30)
        
        # No hundir la defensa dentro del arco
        if is_defender and not my_team_has_ball:
            safe_x = pitch_rect.left + 150 if self.side == "left" else pitch_rect.right - 150
            if self.side == "left": x = max(x, safe_x)
            else: x = min(x, safe_x)
        
        # 4. Evitar estorbar al jugador con balón (Box Awareness)
        if my_team_has_ball and not self.has_ball and match_scene:
            player_with_ball = next((p for p in match_scene.left_all + match_scene.right_all if p.has_ball), None)
            if player_with_ball and player_with_ball.side == self.side:
                # Si estoy cerca del arco rival y mi compañero tiene el balón, abrirme
                dist_to_goal = x - pitch_rect.right if self.side == "left" else x - pitch_rect.left
                if abs(dist_to_goal) < 300:
                    # Crear espacio: moverse lateralmente si estoy en su trayectoria
                    to_mate = player_with_ball.pos - pygame.math.Vector2(x, y)
                    if to_mate.length() < 100:
                        y += 80 if y < pitch_rect.centery else -80
        
        return pygame.math.Vector2(x, y)

    def _check_foul_collision(self, opponents, ball, match_scene):
        """Detecta si el tackle impacta a un rival en lugar del balón."""
        if not opponents or not match_scene: return
        
        for opp in opponents:
            if opp.pos.distance_to(self.pos) < (self.radius + opp.radius + 5):
                # Colisión detectada durante el tackle
                # Si el oponente tiene el balón o está muy cerca de él, hay riesgo de falta
                dist_to_ball = self.pos.distance_to(ball.pos)
                opp_to_ball = opp.pos.distance_to(ball.pos)
                
                # Si el rival está más cerca del balón que yo, es falta probable
                if opp_to_ball < dist_to_ball - 5:
                    # Probabilidad base 12%, modulada por velocidad del tackleador
                    speed_factor = min(self.vel.length() / 400, 1.0) if self.vel.length() > 0 else 0.5
                    foul_chance = 0.08 + 0.06 * speed_factor  # 8%-14% según velocidad
                    if random.random() < foul_chance:
                        match_scene._handle_foul(self, opp)
                        self.tackle_timer = 0 # Detener tackle tras falta
                        break

    def update(self, dt, ball, pitch_rect, teammates=None, opponents=None, match_scene=None):
        # Guardamos la referencia de match para que draw() pueda saber si está en "goal_freeze".
        # Nota: cuando goal_freeze>0, el MatchScene no llama a update(), pero draw seguirá ocurriendo.
        if match_scene is not None:
            self._match_scene_ref = match_scene

        if self.kick_cooldown > 0: self.kick_cooldown -= dt
        if self.pass_cooldown > 0: self.pass_cooldown -= dt
        if self.tackle_timer > 0: 
            self.tackle_timer -= dt
            self._check_foul_collision(opponents, ball, match_scene)
        if self.receive_cooldown > 0: self.receive_cooldown -= dt

        # Rango efectivo: aumenta durante una entrada (tackle)
        effective_radius = self.radius * 1.6 if self.tackle_timer > 0 else self.radius

        dist_to_ball = self.pos.distance_to(ball.pos)
        
        # Lógica Condicional de Captura Magnética y Posesión
        collision_dist = effective_radius + ball.radius
        catch_threshold = collision_dist + MAGNET_DIST if ball.vel.length() < 250 else collision_dist
        
        # No capturar si estamos en cooldown de tiro o pase (liberación del balón)
        can_capture = (self.kick_cooldown <= 0) and (self.pass_cooldown <= 0)
        # Si es un pase al hueco, impedir captura si tenemos receive_cooldown activo
        if getattr(ball, 'is_through_pass', False) and self.receive_cooldown > 0:
            can_capture = False
        
        # Si el rival la está conduciendo, no robar mágicamente solo con el roce, a menos que el bot 'tacklee'
        is_enemy_ball = (ball.last_touch and ball.last_touch != self.side)
        if is_enemy_ball and self.tackle_timer <= 0 and ball.vel.length() < 250:
            catch_threshold = collision_dist - 8
            
        was_holding = getattr(self, '_had_ball_prev', False)
        # Solo capturar si el balón está cerca del suelo (z < 20)
        self.has_ball = (dist_to_ball < catch_threshold) and can_capture and (ball.z < 20)
        
        # Detect first frame of ball possession → apply receive cooldown
        if self.has_ball and not was_holding:
            self.receive_cooldown = max(self.receive_cooldown, 0.35)
            self.pass_charge = 0
            self.kick_charge = 0
            if hasattr(ball, 'is_through_pass'):
                ball.is_through_pass = False
        self._had_ball_prev = self.has_ball
        
        # Impedir movimiento si está expulsado
        if self.red_card:
            self.has_ball = False
            self.pos = pygame.math.Vector2(-1000, -1000) # Fuera del campo
            return

        if self.is_controlled:
            self._human_update(dt, ball, pitch_rect, dist_to_ball, effective_radius, teammates, opponents, match_scene)
        else:
            self._ai_update(dt, ball, pitch_rect, dist_to_ball, effective_radius, teammates, opponents, match_scene)
        
        # Efecto de lesión: reducción de velocidad
        if self.is_injured:
            self._last_move_speed *= 0.6
            self.energy -= 2.0 * dt # Drena más energía estar lesionado

        # ── Stamina Depletion ──
        is_kickoff = getattr(match_scene, 'is_kickoff', False) if match_scene else False
        if not is_kickoff:
            self.energy -= 0.22 * dt # Further reduced passive drain (0.32 -> 0.22)
            
        move_speed = getattr(self, '_last_move_speed', 0)
        if move_speed > 5:
            # Draining depends on speed relative to base human speed
            drain_mult = 1.4 # Further reduced base drain (1.8 -> 1.4)
            if move_speed > self.human_speed * 1.05: # Sprinting
                drain_mult = 3.6 # Further reduced sprint drain (4.8 -> 3.6)
            
            # Age-based drain factor (ONLY in Career Mode)
            age_factor = 1.0
            game_mode = ""
            if match_scene and hasattr(match_scene, "manager"):
                game_mode = match_scene.manager.shared_data.get("game_mode", "")
            
            if game_mode == "career":
                age = self.player_data.get("age", 25)
                if age < 22:
                    age_factor = 0.85 # Youngsters are even more efficient
                elif age > 30:
                    # Veterans tire faster: reduced penalty (0.04 -> 0.025)
                    age_factor = 1.0 + (age - 30) * 0.025
            
            # Deplete energy based on speed, time and age factor
            self.energy -= (move_speed / 3000.0) * drain_mult * age_factor * dt
            
        self.energy = max(0, self.energy)
        # Sync back to player_data for persistence
        self.player_data["energy"] = self.energy

        # Limitar al jugador dentro de las bandas rebotando ligeramente
        if self.pos.x - self.radius < pitch_rect.left: self.pos.x = pitch_rect.left + self.radius
        if self.pos.x + self.radius > pitch_rect.right: self.pos.x = pitch_rect.right - self.radius
        if self.pos.y - self.radius < pitch_rect.top: self.pos.y = pitch_rect.top + self.radius
        if self.pos.y + self.radius > pitch_rect.bottom: self.pos.y = pitch_rect.bottom - self.radius

    def _interact_with_ball(self, ball, dist_to_ball, effective_radius, current_speed, push_dir, match_scene=None):

        """Lógica universal (IA o Humano) para anclar el balón a los pies (Efecto Imán Verdadero)."""
        is_enemy_ball = (ball.last_touch and ball.last_touch != self.side)
        if ball.last_touch_name != self.player_data["name"]:
            # Check if it was a successful pass completion
            if ball.target_player == self and ball.last_touch == self.side:
                # Find the player who sent the pass
                for p in (match_scene.all_players if match_scene else []):
                    if p.player_data["name"] == ball.last_touch_name:
                        p.match_stats["passes_completed"] += 1
                        break
            
            ball.assistant_name = ball.last_touch_name
            ball.last_touch_name = self.player_data["name"]
        ball.last_touch = self.side
        ball.owner = self
        ball.target_player = None
        
        if self.tackle_timer > 0:
            # Robo de balón efectivo (Solo contar una vez por tackle)
            if is_enemy_ball and self.kick_cooldown <= 0:
                self.match_stats["steals"] += 1
                self.kick_cooldown = 0.8 # Bloqueo para no contar robos infinitos en colisión
            
            ball.last_touch_name = self.player_data["name"]
            target_ball_pos = self.pos + self.direction * (self.radius + ball.radius * 1.5)
            ball.pos = ball.pos.lerp(target_ball_pos, 0.95)
            ball.vel = self.direction * current_speed
            self.tackle_timer = 0
        elif current_speed > 0:
            # Conducción magnética perfecta
            target_ball_pos = self.pos + self.direction * (self.radius + ball.radius * 1.5)
            # Lerp ultra alto (0.95) para el efecto imán definitivo pedido por el jugador
            ball.pos = ball.pos.lerp(target_ball_pos, 0.95)
            ball.vel = self.direction * current_speed
        else:
            # Si el jugador está quieto, jala el balón a sus pies firmemente
            target_ball_pos = self.pos + self.direction * (effective_radius + ball.radius)
            ball.pos = ball.pos.lerp(target_ball_pos, 0.6)

    def _human_update(self, dt, ball, pitch_rect, dist_to_ball, effective_radius, teammates, opponents, match_scene):
        from systems.input_manager import input_manager
        input_dir = input_manager.get_movement()

        is_kickoff_state = getattr(match_scene, 'is_kickoff', False)
        is_set_piece_state = getattr(match_scene, 'is_set_piece', False)

        speed = self.human_speed
        
        # Stamina penalty: reduce speed if energy is low
        # Speed starts dropping linearly below 40% energy
        energy_factor = 1.0
        if self.energy < 30: # Threshold lowered (40 -> 30)
            energy_factor = 0.75 + (self.energy / 30.0) * 0.25 # min 0.75 speed (softened)
        
        speed *= energy_factor

        # SPRINT
        is_sprinting = input_manager.is_action_pressed("SPRINT") and self.energy > 5
        if is_sprinting: 
            speed *= DASH_MULTIPLIER
        
        self._last_move_speed = speed if input_dir.length() > 0 else 0

        # --- ACCIONES DEFENSIVAS (Sin balón) ---
        if not self.has_ball and not is_kickoff_state and not is_set_piece_state:
            # PRESIÓN / SEGUIMIENTO (S Button)
            if input_manager.is_action_pressed("PRESS"):
                # Moverse automáticamente hacia el balón
                target_dir = (ball.pos - self.pos)
                if target_dir.length() > 5:
                    input_dir = target_dir.normalize()
            
            # ENTRADA / TACKLE (A Button)
            if input_manager.is_action_pressed("TACKLE") and self.kick_cooldown <= 0:
                self.tackle_timer = TACKLE_DURATION
                self.kick_cooldown = 1.0
                from systems.audio_manager import audio_manager
                audio_manager.play_tackle()
            
            # PRESIÓN / JOCKEY (PASS Button)
            if input_manager.is_action_pressed("PASS"):
                # Moverse automáticamente hacia el balón (Jockeying)
                to_ball = (ball.pos - self.pos)
                if to_ball.length() > 20:
                    input_dir = to_ball.normalize()
                    speed *= 0.8 # Aplicar reducción sobre la velocidad actual (con o sin sprint)
        if self.tackle_timer > 0: speed = TACKLE_BOOST

        if self.tackle_timer <= 0:
            if input_dir.length() > 0:
                input_dir = input_dir.normalize()
                self.direction = input_dir
        else:
            t_dir = (ball.pos - self.pos)
            if t_dir.length() > 0:
                self.direction = t_dir.normalize()
            input_dir = self.direction

        if is_kickoff_state or is_set_piece_state:
            speed = 0

        self.pos += input_dir * speed * dt

        if self.has_ball:
            push_dir = (ball.pos - self.pos).normalize() if dist_to_ball > 0 else self.direction

            # --- ACCIONES (Solo con balón) ---
            # PASE NORMAL
            if input_manager.is_action_pressed("PASS") and self.pass_cooldown <= 0 and self.receive_cooldown <= 0:
                self.pass_charge += dt * 2.0
                self.pass_charge = min(self.pass_charge, 1.0)
            elif self.pass_charge > 0 and self.pass_cooldown <= 0:
                # 1. Calcular distancia deseada basada en carga (40 a 900 píxeles)
                d_dist = 60 + (self.pass_charge * 840)
                target = self._find_pass_target(teammates, desired_dist=d_dist)
                
                pass_dir = (target.pos - self.pos).normalize() if target else self.direction
                # Velocidad del pase escalada por la carga (mínimo 300, máximo 750)
                pass_speed = PASS_FORCE * (0.6 + self.pass_charge * 0.7)
                ball.vel = pass_dir * pass_speed
                from systems.audio_manager import audio_manager
                audio_manager.play_pass()
                
                ball.target_player = target
                ball.owner = None
                self.pass_cooldown = PASS_COOLDOWN
                self.pass_charge = 0
                if match_scene and target and not (getattr(match_scene, 'user_is_sub', False)):
                    match_scene.switch_controlled_player(target)
                return

            # PASE AL HUECO (Al espacio libre y velocidad adaptativa)
            if input_manager.is_action_pressed("THROUGH") and self.pass_cooldown <= 0:
                # Pases al hueco siempre buscan una distancia media-larga
                target = self._find_pass_target(teammates, desired_dist=500, is_through=True)
                if target:
                    to_target = (target.pos - self.pos)
                    dist = to_target.length()
                    
                    # Dirección en la que corre el receptor
                    run_dir = target.direction
                    if run_dir.length() < 0.1:
                        # Si está parado, corre hacia el arco rival
                        run_dir = pygame.math.Vector2(1, 0) if self.side == "left" else pygame.math.Vector2(-1, 0)
                    else:
                        run_dir = run_dir.normalize()
                    
                    # Espacio libre adelantado (al hueco)
                    lead_dist = max(130, min(250, dist * 0.5))
                    lead_pos = target.pos + run_dir * lead_dist
                    
                    # Dirección final desde el pasador hacia el hueco
                    to_space = (lead_pos - self.pos)
                    if to_space.length() > 0:
                        final_dir = to_space.normalize()
                    else:
                        final_dir = self.direction
                    
                    # Mezclar con la dirección de apuntado actual del usuario para permitir control manual (35%)
                    aim_dir = self.direction
                    if aim_dir.length() > 0:
                        final_dir = (final_dir * 0.65 + aim_dir.normalize() * 0.35).normalize()
                    
                    # Velocidad adaptativa basada en la distancia al hueco
                    dist_to_space = to_space.length()
                    adapted_speed = min(850, 420 + dist_to_space * 0.8)
                    
                    ball.vel = final_dir * adapted_speed
                    from systems.audio_manager import audio_manager
                    audio_manager.play_kick()
                    ball.target_player = None  # Al espacio
                    ball.is_through_pass = True  # Marcar que es pase al hueco
                    ball.owner = None
                    self.pass_cooldown = PASS_COOLDOWN
                    
                    if match_scene:
                        match_scene.switch_controlled_player(target)
                        # Forzar un receive_cooldown ligeramente mayor para pases al hueco
                        target.receive_cooldown = 0.45
                    return
                else:
                    # Si no hay target claro, mandar al espacio en la dirección que apunta
                    pass_dir = self.direction
                    ball.vel = pass_dir * (PASS_FORCE * 1.1)
                    from systems.audio_manager import audio_manager
                    audio_manager.play_kick()
                    ball.target_player = None
                    ball.is_through_pass = True
                    ball.owner = None
                    self.pass_cooldown = PASS_COOLDOWN
                    return

            # TIRO AL ARCO
            if not is_kickoff_state:
                if input_manager.is_action_pressed("KICK") and self.kick_cooldown <= 0:
                    self.kick_charge += dt * 1.5
                    self.kick_charge = min(self.kick_charge, 1.0)
                elif self.kick_charge > 0:
                    goal_center = self._get_rival_goal(pitch_rect)
                    rival_gk = match_scene.right_gk if self.side == "left" else match_scene.left_gk
                    
                    # Definir límites del arco (postes)
                    top_post_y = goal_center.y - 48
                    bot_post_y = goal_center.y + 48
                    
                    # --- NUEVA LÓGICA DE APUNTADO INTELIGENTE + USUARIO ---
                    input_dir = input_manager.get_movement()
                    
                    if abs(input_dir.y) > 0.3:
                        # Si el usuario apunta arriba/abajo, tirar hacia ese poste
                        if input_dir.y < 0: # Arriba
                            target_y = top_post_y + random.uniform(5, 15)
                        else: # Abajo
                            target_y = bot_post_y - random.uniform(5, 15)
                    elif rival_gk:
                        # Si no hay input claro, buscar el hueco vacío inteligentemente
                        # Si el portero está centrado, buscar las esquinas (postes)
                        gk_rel_y = rival_gk.pos.y - goal_center.y
                        if abs(gk_rel_y) < 15:
                            # Portero centrado: tirar a una esquina aleatoria pero lejos del centro
                            target_y = random.choice([top_post_y + 10, bot_post_y - 10])
                        elif gk_rel_y < 0:
                            # Portero arriba: tirar abajo
                            target_y = bot_post_y - random.uniform(5, 15)
                        else:
                            # Portero abajo: tirar arriba
                            target_y = top_post_y + random.uniform(5, 15)
                    else:
                        target_y = goal_center.y + random.uniform(-20, 20)
                    
                    # Asegurar que el tiro no se salga del arco por el random
                    target_y = max(top_post_y + 2, min(bot_post_y - 2, target_y))
                    
                    best_target = pygame.math.Vector2(goal_center.x, target_y)
                    kick_dir = (best_target - self.pos).normalize()
                    
                    # Potencia de tiro (escalada por carga y stat de tiro)
                    shot_stat_mult = 0.8 + (self.player_data["s"]["shot"] / 100.0) * 0.4 # 0.8 a 1.2
                    ball.vel = kick_dir * (KICK_FORCE * (0.8 + self.kick_charge * 0.9) * shot_stat_mult)
                    from systems.audio_manager import audio_manager
                    audio_manager.play_kick()
                    
                    ball.target_player = None
                    ball.owner = None
                    self.kick_cooldown = 0.5
                    self.kick_charge = 0
                    return

            # CENTRO (Mejorado: Lofted ball al área)
            if input_manager.is_action_pressed("CROSS") and self.pass_cooldown <= 0:
                goal_center = self._get_rival_goal(pitch_rect)
                box_target = None
                best_score = float('inf')
                
                # Buscar el mejor receptor en el área rival
                for m in teammates:
                    if m == self: continue
                    dist_to_goal = m.pos.distance_to(goal_center)
                    # Solo centrar si el compañero está relativamente cerca del área
                    if dist_to_goal < 450:
                        # Priorizar jugadores que estén en el eje del arco
                        y_dist = abs(m.pos.y - goal_center.y)
                        score = dist_to_goal + y_dist * 0.5
                        if score < best_score:
                            best_score = score
                            box_target = m
                
                # Punto de caída: jugador o punto penal
                penalty_spot = pygame.math.Vector2(goal_center.x - (220 if self.side == "left" else -220), goal_center.y)
                target_pos = box_target.pos if box_target else penalty_spot
                
                to_target = (target_pos - self.pos)
                dist = to_target.length()
                pass_dir = to_target.normalize() if dist > 0 else self.direction
                
                # Velocidad y ARCO (vz)
                # Un centro debe ser lento pero alto para permitir el cabezazo
                ball.vel = pass_dir * min(650, 350 + dist * 0.5)
                from systems.audio_manager import audio_manager
                audio_manager.play_kick()
                # El impulso vertical (vz) depende de la distancia para que caiga en el sitio
                ball.vz = 450 + (dist * 0.25) 
                
                ball.target_player = box_target # Permitir imán ligero al caer
                ball.owner = None
                self.pass_cooldown = PASS_COOLDOWN + 0.5
                if match_scene and box_target: 
                    match_scene.switch_controlled_player(box_target)
                return

                
            self._interact_with_ball(ball, dist_to_ball, effective_radius, speed if input_dir.length()>0 else 0, push_dir, match_scene)



    def _ai_update(self, dt, ball, pitch_rect, dist_to_ball, effective_radius, teammates, opponents, match_scene):
        is_kickoff_state = getattr(match_scene, 'is_kickoff', False)
        is_set_piece_state = getattr(match_scene, 'is_set_piece', False)

        if is_kickoff_state or is_set_piece_state:
            # Nadie de la IA se mueve durante el kickoff o jugadas preparadas
            if is_kickoff_state and self.has_ball and self.side == getattr(match_scene, 'kickoff_team', 'left'):
                # Solo el delantero que posee el balón saca
                if self.kick_cooldown <= 0:
                    pass_target = self._find_ai_pass_target(teammates, opponents)
                    if pass_target:
                        pass_dir = (pass_target.pos - self.pos)
                        pass_dist = pass_dir.length()
                        if pass_dist > 0: pass_dir = pass_dir.normalize()
                        adapted_force = min(PASS_FORCE, max(250, pass_dist * 1.8))
                    else:
                        pass_dir = pygame.math.Vector2(-1 if self.side == 'right' else 1, 0)
                        adapted_force = 350
                    ball.vel = pass_dir * adapted_force
                    ball.target_player = pass_target
                    ball.owner = None
                    self.kick_cooldown = 1.0
            # Si es kickoff, DEVOLVEMOS INMEDIATAMENTE PARA TODOS LOS JUGADORES, congelando la cancha
            return

        self.state_timer += dt
        if self.state_timer < getattr(self, "reaction_delay", 0.15):
            # No recalcular target aún, solo moverse hacia el anterior o mantener formación
            if not hasattr(self, "_ai_target"): self._ai_target = self.pos
        else:
            self.state_timer = 0
            self._ai_target = None # Forzar recalcular
            
        target = getattr(self, "_ai_target", None)
        
        # Stamina penalty for AI
        energy_factor = 1.0
        if self.energy < 40:
            energy_factor = 0.6 + (self.energy / 40.0) * 0.4
            
        speed = self.ai_speed * energy_factor
        self._last_move_speed = speed # Approximate for drain calculation

        if target is None:
            self._decide_state(ball, pitch_rect, match_scene)

            target = None
            if self.state == self.STATE_CHASE:
                # Agresividad de persecución escalada por dificultad
                chase_boost = 1.05 + (self.difficulty * 0.02) # 1.07 a 1.25
                speed = self.ai_speed * chase_boost

                if not self.has_ball:
                    if self.is_active_ai:
                        # IA Principal: Persecución Directa (Agresividad total) al balón
                        target = ball.pos
                    else:
                        # IA Secundaria/Apoyo: Contención (Defense Jockeying)
                        # Niveles altos contienen más cerca y con más presión
                        jockey_dist = max(25, 60 - (self.difficulty * 3))
                        my_goal_pos = pygame.math.Vector2(pitch_rect.left, pitch_rect.centery) if self.side == "left" else pygame.math.Vector2(pitch_rect.right, pitch_rect.centery)
                        jockey_vector = (my_goal_pos - ball.pos)
                        if jockey_vector.length() > 0:
                            jockey_vector = jockey_vector.normalize() * jockey_dist 
                        target = ball.pos + jockey_vector
                    
                    # Si está lo suficentemente cerca, intentar robar con más decisión
                    if dist_to_ball < 60:
                        speed = self.ai_speed * 0.9 
                        prob = getattr(self, "tackle_prob", 0.05)
                        if self.kick_cooldown <= 0 and random.random() < prob: 
                            self.tackle_timer = TACKLE_DURATION
                            self.kick_cooldown = 0.8 # Menos cooldown para IA difícil para que presione más
                else:
                    target = ball.pos

            elif self.state == self.STATE_POSITION:
                my_team_has_ball = ball.last_touch == self.side
                target = self.get_formation_world_pos(pitch_rect, ball.pos, my_team_has_ball, match_scene)

            self._ai_target = target
            
        if target is None: return

        # Aplicar el tackle extra vel
        if self.tackle_timer > 0:
            speed = TACKLE_BOOST

        # ── IA REAL: Toma de Decisiones con Balón ──
        if self.has_ball:
            goal_pos = self._get_rival_goal(pitch_rect)
            dist_to_goal = self.pos.distance_to(goal_pos)
            
            # Análisis del entorno
            near_top_edge = self.pos.y < pitch_rect.top + 70
            near_bot_edge = self.pos.y > pitch_rect.bottom - 70
            near_edge = near_top_edge or near_bot_edge
            
            closest_opp_dist = float('inf')
            if opponents:
                closest_opp = min(opponents, key=lambda o: self.pos.distance_to(o.pos))
                closest_opp_dist = self.pos.distance_to(closest_opp.pos)
            
            under_pressure = closest_opp_dist < 80
            
            # 1. Dirección de conducción inteligente
            ideal_push = (goal_pos - self.pos).normalize() if (goal_pos - self.pos).length() > 0 else self.direction
            
            # Si estoy en la banda, conducir hacia el centro del campo
            if near_top_edge:
                ideal_push = pygame.math.Vector2(ideal_push.x, 0.6).normalize()
            elif near_bot_edge:
                ideal_push = pygame.math.Vector2(ideal_push.x, -0.6).normalize()
            
            # Si un defensa está encima, esquivarlo ligeramente
            if under_pressure and opponents:
                evasion = (self.pos - closest_opp.pos).normalize()
                ideal_push = (ideal_push * 0.5 + evasion * 0.5)
                if ideal_push.length() > 0: ideal_push = ideal_push.normalize()
            
            push_dir = ideal_push
            step = speed * dt
            if self.tackle_timer <= 0:
                self.direction = push_dir
            self.pos += self.direction * step
            
            # 2. Decisiones de acción (solo si no estamos en cooldown ni acabamos de recibir)
            if self.kick_cooldown <= 0 and self.receive_cooldown <= 0:
                # PRIORIDAD 1: Tiro al arco (IA Agresiva)
                can_shoot = dist_to_goal < 350 and not near_edge
                if can_shoot:
                    # Si está muy cerca o está libre, tira con mucha frecuencia
                    shoot_chance = 0.65 if dist_to_goal < 200 else 0.35
                    if random.random() < shoot_chance:
                        kick_dir = (goal_pos - self.pos)
                        if kick_dir.length() > 0: kick_dir = kick_dir.normalize()
                        
                        # Jitter basado en error_rate de la dificultad
                        err = getattr(self, "ai_error_rate", 0.1)
                        kick_dir.x += random.uniform(-err, err)
                        kick_dir.y += random.uniform(-err, err)
                        
                        ball.vel = kick_dir.normalize() * (KICK_FORCE * (1.05 + (1.0 - err) * 0.1))
                        ball.target_player = None
                        ball.owner = None
                        self.kick_cooldown = 1.0 # Cooldown post-tiro
                        return
                elif teammates:
                    target_mate = self._find_ai_pass_target(teammates, opponents)
                    if target_mate:
                        # IA favorece más el toque (passing) que la conducción solitaria
                        pass_chance = 0.65 if under_pressure else 0.45
                        if random.random() < pass_chance:
                            pass_dir = (target_mate.pos - self.pos)
                            pass_dist = pass_dir.length()
                            if pass_dir.length() > 0: pass_dir = pass_dir.normalize()
                            
                            # Jitter en pases (pueden ser imprecisos en niveles bajos)
                            err = getattr(self, "ai_error_rate", 0.1) * 0.5
                            pass_dir.x += random.uniform(-err, err)
                            pass_dir.y += random.uniform(-err, err)
                            
                            adapted_force = min(PASS_FORCE * 1.1, max(300, pass_dist * 1.85))
                            ball.vel = pass_dir.normalize() * adapted_force
                            ball.target_player = target_mate
                            ball.owner = None
                            self.kick_cooldown = 0.7 # Cooldown para evitar pases infinitos instantáneos
                            return
                        else:
                            self._interact_with_ball(ball, dist_to_ball, effective_radius, speed, push_dir, match_scene)
                    else:
                        self._interact_with_ball(ball, dist_to_ball, effective_radius, speed, push_dir, match_scene)
                # PRIORIDAD 3: Conducir hacia el arco
                else:
                    self._interact_with_ball(ball, dist_to_ball, effective_radius, speed, push_dir, match_scene)
            else:
                self._interact_with_ball(ball, dist_to_ball, effective_radius, speed, push_dir, match_scene)

                
        elif target:
            dist = self.pos.distance_to(target)
            if dist > 3:
                # Evita acelerar en la milímetra final para evitar temblores
                step = speed * dt if dist > speed * dt else dist
                dir_vec = (target - self.pos).normalize()
                
                # Rastreo perfecto (sin bloqueo mágico) asegura que el tackle siempre conecte
                self.direction = dir_vec
                self.pos += dir_vec * step


    def _decide_state(self, ball, pitch_rect, match_scene=None):
        """Asigna roles posicionales verdaderos, dictando quién presiona activamente."""
        gk_has_ball = match_scene and (match_scene.left_gk.has_ball or match_scene.right_gk.has_ball)
        if gk_has_ball:
            self.state = self.STATE_POSITION
            return
            
        my_team_has_ball = ball.last_touch == self.side
        dist_to_ball = self.pos.distance_to(ball.pos)

        # Si el pase viene exactamente hacia mí, TENGO que ir a buscarlo de inmediato
        if getattr(ball, 'target_player', None) is self:
            self.state = self.STATE_CHASE
            return

        can_chase = self.is_active_ai

        if can_chase:
            # Si el balón está suelto y soy el encargado, siempre voy a por él
            if ball.owner is None:
                self.state = self.STATE_CHASE
            elif not my_team_has_ball:
                self.state = self.STATE_CHASE
            else:
                self.state = self.STATE_POSITION
        else:
            # Nadie presiona salvajemente, el equipo mantiene táctica defensiva u ofensiva posicional
            self.state = self.STATE_POSITION


    def _find_pass_target(self, teammates, desired_dist=200, is_through=False):
        """Busca el mejor receptor basándose primordialmente en la dirección y el peso de la potencia (distancia deseada)."""
        best = None
        best_score = float('inf')
        
        goal_x = WIDTH if self.side == "left" else 0

        for mate in teammates:
            if mate is self: continue
            to_mate = mate.pos - self.pos
            dist = to_mate.length()
            
            # Filtro de distancia mínima y máxima
            if dist < 40 or dist > 1100: continue
            
            # Normalizar vector hacia el compañero
            to_mate_dir = to_mate.normalize()
            dot = self.direction.dot(to_mate_dir)
            
            # Ampliamos el cono de visión
            if dot < -0.3: continue 

            # Cálculo de score:
            # 1. Penalización de ángulo
            angle_penalty = (1.0 - dot) * 1200
            
            # 2. Penalización de distancia
            dist_penalty = abs(dist - desired_dist) * 1.2
            
            # 3. Bonus por profundidad (si es pase al hueco)
            depth_bonus = 0
            if is_through:
                # Premiar a quien esté más adelantado que yo hacia el arco rival
                is_ahead = (mate.pos.x - self.pos.x) * (1 if self.side == "left" else -1) > 20
                if is_ahead: depth_bonus = -400
                else: depth_bonus = 500 # Penalizar pases al hueco hacia atrás

            score = angle_penalty + dist_penalty + depth_bonus
            
            if score < best_score:
                best_score = score
                best = mate
        return best

    def _find_ai_pass_target(self, teammates, opponents):
        best = None
        best_score = float('inf')
        goal = self._get_rival_goal(pygame.Rect(0, 0, WIDTH, HEIGHT))
        my_dist_to_goal = self.pos.distance_to(goal)
        pitch_top = 0
        pitch_bottom = HEIGHT
        
        for mate in teammates:
            if mate is self: continue
            dist = self.pos.distance_to(mate.pos)
            if dist < 60 or dist > 500: continue  # Rango más realista
            
            dist_to_goal = mate.pos.distance_to(goal)
            
            # Puntuación base: premia a quienes estén más cerca del arco y cerca nuestro
            score = dist_to_goal + (dist * 0.5)
            
            # --- PENALIZAR PASES HACIA LOS BORDES ---
            margin = 80
            if mate.pos.y < pitch_top + margin or mate.pos.y > pitch_bottom - margin:
                score += 600  # No elegir a quien está pegado a la banda
            
            # --- EVALUACIÓN DE SEGURIDAD DEL PASE (Intercepción) ---
            pass_dir = (mate.pos - self.pos)
            if pass_dir.length() > 0:
                pass_dir_norm = pass_dir.normalize()
                is_safe = True
                for opp in opponents:
                    opp_dist = self.pos.distance_to(opp.pos)
                    if opp_dist < dist: 
                        to_opp = (opp.pos - self.pos).normalize() if opp_dist > 0 else pygame.math.Vector2(0,0)
                        dot = pass_dir_norm.dot(to_opp)
                        if dot > 0.90: 
                            is_safe = False
                            break
                        elif dot > 0.80 and opp_dist < 120:
                            is_safe = False
                            break
                            
                if not is_safe:
                    score += 1500  # Penalizar pases interceptables
            
            # --- PREFERENCIA HACIA ADELANTE Y ROMPER LÍNEAS ---
            if dist_to_goal < my_dist_to_goal - 20:
                score -= 400 # Gran incentivo a pases que ganan metros
                
                # Bonus por 'Romper Líneas': Si el pase cruza el eje X de rivales
                opps_passed = 0
                for opp in opponents:
                    if self.side == "left":
                        if self.pos.x < opp.pos.x < mate.pos.x: opps_passed += 1
                    else:
                        if self.pos.x > opp.pos.x > mate.pos.x: opps_passed += 1
                score -= opps_passed * 150 # Romper líneas es muy valioso
            
            # --- JUEGO POR EL CENTRO ---
            center_y = HEIGHT // 2
            if abs(mate.pos.y - center_y) < 150:
                score -= 200 # Incentivo a jugar por el carril central
                
            if score < best_score:
                best_score = score
                best = mate
                
        # Si la única opción es un pase malísimo, mejor driblear
        if best_score > 1000 and random.random() < 0.6:
            return None
            
        return best

    def _get_rival_goal(self, pitch_rect):
        return pygame.math.Vector2(pitch_rect.right if self.side == "left" else pitch_rect.left, pitch_rect.centery)

    def draw(self, surface):
        # Posición base
        px, py = int(self.pos.x), int(self.pos.y)

        # Estado para animación visual (no afecta físicas)
        now = pygame.time.get_ticks() / 1000.0
        phase = getattr(self, "_anim_phase", 0.0)
        ms = getattr(self, "_match_scene_ref", None)

        goal_freeze = getattr(ms, "goal_freeze", 0) if ms else 0
        goal_scored = getattr(ms, "goal_scored", False) if ms else False
        scorer_name = None
        if ms and getattr(ms, "ball", None):
            scorer_name = getattr(ms.ball, "last_touch_name", None)

        my_name = (self.player_data.get("name") or "").lower().strip()
        celebrate = bool(
            goal_freeze > 0
            and goal_scored
            and scorer_name
            and (str(scorer_name).lower().strip() == my_name)
        )

        # Movimiento: usa la velocidad aproximada guardada en update()
        move_speed = float(getattr(self, "_last_move_speed", 0.0) or 0.0)
        denom = max(1.0, float(self.human_speed) if hasattr(self, "human_speed") else 1.0)
        move_ratio = max(0.0, min(1.0, move_speed / denom))

        # Tackle/slide visual
        tackle_active = self.tackle_timer > 0
        tackle_frac = 0.0
        if tackle_active:
            tackle_frac = min(1.0, self.tackle_timer / max(1e-5, TACKLE_DURATION))

        # Respiración / bob (idle y también durante movimiento)
        breathe = math.sin(now * (7.5 + move_ratio * 6.0) + phase)
        breathe2 = math.sin(now * 15.0 + phase * 2.0)

        y_slide = 0 if not tackle_active else 5
        y_bob = int(breathe * (1.0 + move_ratio * 1.2))

        # Celebration: salto sutil en goal_freeze
        y_celebrate = 0
        if celebrate:
            jump = 0.5 + 0.5 * math.sin(now * 18.0 + phase)
            y_celebrate = -int(self.radius * 0.18 * jump)

        y_offset = y_slide + y_bob + y_celebrate
        cx, cy = px, py + y_offset

        # Radio (squash en tackle; elasticidad en movimiento)
        if tackle_active:
            radius = max(3, int(self.radius * (1.0 - 0.12 * tackle_frac)))
        else:
            radius = max(3, int(self.radius * (1.0 + 0.03 * breathe + 0.06 * move_ratio)))

        # Sombra: se estira un poco si hay movimiento (y se "aplana" en tackle)
        shadow_h = radius // 2 if tackle_active else radius
        shadow_w = radius * 3 + int(move_ratio * 6)
        shadow_dx = int(self.direction.x * move_ratio * radius * 0.45) if hasattr(self, "direction") else 0
        shadow_surf = pygame.Surface((shadow_w, max(1, shadow_h)), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow_surf, (0, 0, 0, 50), (0, 0, shadow_w, shadow_h))
        shadow_y = cy + radius - (3 if not tackle_active else 0)
        surface.blit(shadow_surf, (cx - shadow_w // 2 + shadow_dx, shadow_y))

        # Rastros simples de movimiento (trail) para que la bolita se sienta viva
        if (move_ratio > 0.22 and not tackle_active) or self.has_ball:
            aim = pygame.math.Vector2(self.direction)
            if aim.length() > 0:
                aim = aim.normalize()
            else:
                aim = pygame.math.Vector2(1 if self.side == "left" else -1, 0)

            trail_n = 2 if move_ratio > 0.35 else 1
            base_col = self.color
            trail_col = (max(0, base_col[0] - 40), max(0, base_col[1] - 40), max(0, base_col[2] - 40))
            for i in range(trail_n):
                t = (i + 1) / (trail_n + 1)
                tx = cx - int(aim.x * radius * 0.55 * (1.0 + t))
                ty = cy - int(aim.y * radius * 0.55 * (1.0 + t))
                pygame.draw.circle(surface, trail_col, (tx, ty), max(1, int(radius * 0.55 * (1.0 - t * 0.6))))

        # --- Procedural Humanoid Player Model ---
        num_val = self.player_data.get("num", 0)
        skin_color = (253, 213, 185) if num_val % 4 != 0 else (120, 80, 55)  # Diverse skins
        hair_color = [(45, 35, 30), (95, 65, 45), (210, 180, 100), (145, 90, 50), (25, 25, 25)][num_val % 5]

        # Base proportions
        torso_w = int(radius * 1.3)
        torso_h = int(radius * 1.0)
        head_r = int(radius * 0.55)
        
        # Slide/tackle adjustments
        if tackle_active:
            slide_dir = self.direction if self.direction.length() > 0.1 else pygame.math.Vector2(1 if self.side == "left" else -1, 0)
            slide_dir = slide_dir.normalize()
            
            hx = cx + int(slide_dir.x * radius * 0.5)
            hy = cy + y_offset + int(slide_dir.y * radius * 0.5) - 2
            
            # Legs extended backward
            leg_x1 = cx - int(slide_dir.x * radius * 0.5) - int(slide_dir.y * radius * 0.2)
            leg_y1 = cy + y_offset - int(slide_dir.y * radius * 0.5) + int(slide_dir.x * radius * 0.2) + 2
            leg_x2 = cx - int(slide_dir.x * radius * 0.5) + int(slide_dir.y * radius * 0.2)
            leg_y2 = cy + y_offset - int(slide_dir.y * radius * 0.5) - int(slide_dir.x * radius * 0.2) + 2
            
            pygame.draw.line(surface, skin_color, (cx, cy + y_offset), (leg_x1, leg_y1), 3)
            pygame.draw.line(surface, skin_color, (cx, cy + y_offset), (leg_x2, leg_y2), 3)
            pygame.draw.circle(surface, (30, 30, 30), (leg_x1, leg_y1), 3)
            pygame.draw.circle(surface, (30, 30, 30), (leg_x2, leg_y2), 3)
            
            # Torso
            pygame.draw.circle(surface, self.color, (cx, cy + y_offset), radius)
            pygame.draw.circle(surface, BLACK, (cx, cy + y_offset), radius, 1)
            
            # Head
            pygame.draw.circle(surface, skin_color, (hx, hy), head_r)
            pygame.draw.circle(surface, BLACK, (hx, hy), head_r, 1)
            pygame.draw.circle(surface, hair_color, (hx, hy - head_r + 1), int(head_r * 0.6))
        else:
            # Stand/Run/Celebrate details
            hx = cx
            hy = cy - int(radius * 0.85)
            
            # 1. Legs and Feet
            leg_swing = math.sin(now * 16.0 + phase) * move_ratio * radius * 0.35
            lx = cx - int(radius * 0.3)
            rx = cx + int(radius * 0.3)
            ly = cy + int(radius * 0.4)
            
            # Left leg
            pygame.draw.line(surface, skin_color, (lx, ly), (lx, ly + int(radius * 0.4) + int(leg_swing)), 3)
            pygame.draw.circle(surface, (30, 30, 30), (lx, ly + int(radius * 0.4) + int(leg_swing)), 3)
            # Right leg
            pygame.draw.line(surface, skin_color, (rx, ly), (rx, ly + int(radius * 0.4) - int(leg_swing)), 3)
            pygame.draw.circle(surface, (30, 30, 30), (rx, ly + int(radius * 0.4) - int(leg_swing)), 3)
            
            # 2. Torso (Shirt)
            ty = cy - int(radius * 0.1)
            pygame.draw.rect(surface, self.color, (cx - torso_w//2, ty - torso_h//2, torso_w, torso_h), border_radius=3)
            pygame.draw.rect(surface, BLACK, (cx - torso_w//2, ty - torso_h//2, torso_w, torso_h), 1, border_radius=3)
            
            # 3. Uniform stripe/accent
            stripe_w = max(2, torso_w // 4)
            pygame.draw.rect(surface, self.secondary, (cx - stripe_w//2, ty - torso_h//2, stripe_w, torso_h))
            
            # 4. Shorts
            shorts_y = ty + torso_h//2 - 1
            shorts_h = int(radius * 0.4)
            pygame.draw.rect(surface, self.secondary, (cx - torso_w//2, shorts_y, torso_w, shorts_h), border_radius=1)
            pygame.draw.rect(surface, BLACK, (cx - torso_w//2, shorts_y, torso_w, shorts_h), 1, border_radius=1)
            
            # 5. Head & Hair
            pygame.draw.circle(surface, skin_color, (hx, hy), head_r)
            pygame.draw.circle(surface, BLACK, (hx, hy), head_r, 1)
            # Hair crown
            pygame.draw.circle(surface, hair_color, (hx, hy - head_r + 2), int(head_r * 0.75))
            
            # 6. Arms
            lax = cx - torso_w//2 - 1
            lay = ty - torso_h//3
            rax = cx + torso_w//2 + 1
            ray = ty - torso_h//3
            
            # Arm swing/action
            if celebrate:
                # Both arms raised high
                pygame.draw.line(surface, self.color, (lax, lay), (lax - 3, lay - int(radius * 0.7)), 2)
                pygame.draw.line(surface, self.color, (rax, ray), (rax + 3, ray - int(radius * 0.7)), 2)
                pygame.draw.circle(surface, skin_color, (lax - 3, lay - int(radius * 0.7)), 2)
                pygame.draw.circle(surface, skin_color, (rax + 3, ray - int(radius * 0.7)), 2)
            elif (self.pass_charge > 0 or self.kick_charge > 0) and self.has_ball:
                # Pointing arm
                aim = self.direction.normalize() if self.direction.length() > 0.1 else pygame.math.Vector2(1 if self.side == "left" else -1, 0)
                px_arm = cx + int(aim.x * radius * 0.8)
                py_arm = cy + int(aim.y * radius * 0.8)
                pygame.draw.line(surface, self.secondary, (cx, cy), (px_arm, py_arm), 3)
                pygame.draw.circle(surface, skin_color, (px_arm, py_arm), 2)
            else:
                # Running swing arms
                arm_swing = math.sin(now * 16.0 + phase) * move_ratio * radius * 0.35
                pygame.draw.line(surface, self.color, (lax, lay), (lax - 2, lay + int(radius * 0.4) + int(arm_swing)), 2)
                pygame.draw.line(surface, self.color, (rax, ray), (rax + 2, ray + int(radius * 0.4) - int(arm_swing)), 2)
                pygame.draw.circle(surface, skin_color, (lax - 2, lay + int(radius * 0.4) + int(arm_swing)), 2)
                pygame.draw.circle(surface, skin_color, (rax + 2, ray + int(radius * 0.4) - int(arm_swing)), 2)

            # 7. Eyes
            blink = (math.sin(now * 3.0 + phase) + 1.0) / 2.0
            eye_open = 1.0 if blink > 0.12 else 0.15
            eye_r = max(1, int(head_r * 0.18))
            
            # Eye offset based on facing/action direction
            aim_dir = self.direction.normalize() if self.direction.length() > 0.1 else pygame.math.Vector2(1 if self.side == "left" else -1, 0)
            ex = hx + int(aim_dir.x * head_r * 0.3)
            ey = hy + int(aim_dir.y * head_r * 0.3)
            
            # Draw eyes perpendicular to looking direction
            perp = pygame.math.Vector2(-aim_dir.y, aim_dir.x)
            e1x = ex - int(perp.x * head_r * 0.3)
            e1y = ey - int(perp.y * head_r * 0.3)
            e2x = ex + int(perp.x * head_r * 0.3)
            e2y = ey + int(perp.y * head_r * 0.3)
            
            pygame.draw.circle(surface, BLACK, (int(e1x), int(e1y)), max(1, int(eye_r * eye_open)))
            pygame.draw.circle(surface, BLACK, (int(e2x), int(e2y)), max(1, int(eye_r * eye_open)))

        # Celebración: anillo + chispas simples
        if celebrate:
            pulse = 0.5 + 0.5 * math.sin(now * 12.0 + phase)
            ring_r = radius + int(2 + pulse * 3)
            pygame.draw.circle(surface, YELLOW, (cx, cy), ring_r, 2)
            s = int(radius * 0.6)
            pygame.draw.line(surface, YELLOW, (cx - s, cy), (cx + s, cy), 2)
            pygame.draw.line(surface, YELLOW, (cx, cy - s), (cx, cy + s), 2)

        # Indicador de jugador controlado
        if self.is_controlled:
            tri_y = cy - radius - 12
            pulse = (math.sin(pygame.time.get_ticks() / 150) + 1) / 2
            tri_color = (int(pulse * 80), int(220 + pulse * 35), int(160 + pulse * 40))
            points = [(cx, tri_y - 6), (cx - 6, tri_y + 2), (cx + 6, tri_y + 2)]
            pygame.draw.polygon(surface, tri_color, points)
            
            # Dibujar nombre de jugador controlado abajo
            try: font_n = pygame.font.SysFont("Arial", 12, bold=True)
            except: font_n = pygame.font.Font(None, 12)
            name_str = self.player_data["name"]
            if self.player_data.get("is_captain"):
                name_str = "(C) " + name_str
            name_surf = font_n.render(name_str, True, WHITE)
            surface.blit(name_surf, (cx - name_surf.get_width() // 2, cy + radius + 15))

            # --- BARRA DE STAMINA (Solo para el controlado) ---
            stamina_w = 40
            stamina_h = 4
            sx = cx - stamina_w // 2
            sy = cy + radius + 30
            # Fondo
            pygame.draw.rect(surface, (20, 20, 20), (sx, sy, stamina_w, stamina_h))
            # Barra de color (Verde -> Amarillo -> Rojo)
            energy_ratio = self.energy / 100.0
            if energy_ratio > 0.6:
                bar_col = (50, 255, 50)
            elif energy_ratio > 0.3:
                bar_col = (255, 255, 50)
            else:
                bar_col = (255, 50, 50)
            pygame.draw.rect(surface, bar_col, (sx, sy, int(stamina_w * energy_ratio), stamina_h))
            # Borde
            pygame.draw.rect(surface, (0, 0, 0), (sx, sy, stamina_w, stamina_h), 1)
        else:
            # Dibujar número en la espalda (ilusión visual superior)
            try: font_num = pygame.font.SysFont("Arial", 10, bold=True)
            except: font_num = pygame.font.Font(None, 10)
            num_str = str(self.player_data.get("num", ""))
            if self.player_data.get("is_captain"):
                num_str = "C"
            num_surf = font_num.render(num_str, True, self.team_data["accent"])
            surface.blit(num_surf, (cx - num_surf.get_width() // 2, cy - num_surf.get_height() // 2))
            
        # UI: Barras de Carga para Pase/Tiro si están activas
        if self.pass_charge > 0 or self.kick_charge > 0:
            charge = max(self.pass_charge, self.kick_charge)
            is_kick = self.kick_charge > 0
            bar_w = 40
            bar_h = 6
            bar_x = cx - bar_w // 2
            bar_y = cy - radius - 20
            
            pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_w, bar_h))
            
            fill_color = RED if is_kick else BLUE
            if charge == 1.0:
                fill_color = GOLD
            
            pygame.draw.rect(surface, fill_color, (bar_x, bar_y, int(bar_w * charge), bar_h))
