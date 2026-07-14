import pygame
import random
from settings import *
from scene_manager import BaseScene
from systems.pitch import Pitch
from systems.hud import HUD
from entities.ball import Ball
from entities.field_player import FieldPlayer
from entities.goalkeeper import Goalkeeper


class MatchScene(BaseScene):
    """Escena principal del partido de fútbol."""

    @property
    def left_team(self):
        return self.user_team if self.user_side == "left" else self.rival_team
        
    @property
    def right_team(self):
        return self.user_team if self.user_side == "right" else self.rival_team

    @property
    def user_side(self):
        return getattr(self, "_user_side", "left")

    @user_side.setter
    def user_side(self, value):
        self._user_side = value

    @property
    def cpu_side(self):
        return "right" if self.user_side == "left" else "left"

    def __init__(self, manager, resume=False, **kwargs):
        super().__init__(manager)

        self.user_team = manager.shared_data.get("player_team")
        self.rival_team = manager.shared_data.get("rival_team")
        game_mode = manager.shared_data.get("game_mode", "quick")
        is_free = game_mode == "free"
        
        self.last_switch_time = 0
        self.user_is_sub = manager.shared_data.get("user_is_sub", False)
        self.sub_performed = False
        self.difficulty = manager.shared_data.get("difficulty", 5) # 1-10 scale
        
        # Side assignment
        self.user_side = "left"
        if self.manager.shared_data.get("career_match_state", {}).get("swapped"):
            self.user_side = "right"

        if resume and "match_state" in manager.shared_data:
            state = manager.shared_data["match_state"]
            self.pitch = Pitch(None)
            self.hud = state["hud"]
            if "user_side" in state:
                self.user_side = state["user_side"]
            elif "left_team" in state:
                # Fallback for old saves
                if state["left_team"] == self.user_team: self.user_side = "left"
                else: self.user_side = "right"

            self.ball = Ball(WIDTH // 2, HEIGHT // 2)
            
            from systems.audio_manager import audio_manager
            audio_manager.stop_menu_music()
            audio_manager.start_crowd_bg()
            audio_manager.play_whistle()
            
            # Restaurar estado exacto (no borrar los goles y mantener suplentes)
            self.match_goal_events = state.get("match_goal_events", [])
            self.sub_performed = state.get("sub_performed", False)
            self.halftime_pause = state.get("halftime_pause", False)
            self.user_is_sub = state.get("user_is_sub", self.user_is_sub)
            self.out_of_bounds_msg = state.get("out_of_bounds_msg", "")
            self.out_of_bounds_timer = state.get("out_of_bounds_timer", 0)
            self.goal_freeze = 0
            
            if "left_field" in state:
                self.left_field = state["left_field"]
                self.right_field = state["right_field"]
                self.left_gk = state["left_gk"]
                self.right_gk = state["right_gk"]
                # Reconstruir las listas combinadas de todos los jugadores que antes se hacían en _setup_players()
                self.left_all = self.left_field + [self.left_gk]
                self.right_all = self.right_field + [self.right_gk]
                self.all_players = self.left_all + self.right_all
                # Restaurar bancas y contador de cambios
                self.left_bench = state.get("left_bench", [])
                self.right_bench = state.get("right_bench", [])
                self.left_subs_count = state.get("left_subs_count", 0)
                self.right_subs_count = state.get("right_subs_count", 0)
            else:
                self.left_bench = []
                self.right_bench = []
                self.left_subs_count = 0
                self.right_subs_count = 0
                self._setup_players()
                
            self._kickoff()
        else:
            self.pitch = Pitch(None)
            self.hud = HUD(self.left_team, self.right_team, is_free_mode=is_free)
            self.ball = Ball(WIDTH // 2, HEIGHT // 2)
            self.goal_freeze = 0
            self.match_goal_events = [] # Store {"scorer": name, "assistant": name}
            
            # El saque inicial del partido siempre corresponde al local (equipo izquierdo)
            # a menos que se implemente un factor extra en torneos cruzados.
            self.manager.shared_data["kickoff_team"] = "left"
            self.manager.shared_data["first_half_kickoff"] = "left"
            
            self.left_bench = []
            self.right_bench = []
            self.left_subs_count = 0
            self.right_subs_count = 0
            
            self._setup_players()
            self._kickoff()
            
        self.halftime_pause = False
        self.out_of_bounds_msg = ""
        self.out_of_bounds_timer = 0
        
        self.pending_subs = [] # List of (side, out_player_obj, in_player_dict)
        self.goal_scored = False # Flag to prevent double goals
        self._goal_handled_frame = -1
        self.intro_timer = 0
        self.intro_type = None
        if not resume:
            mode = self.manager.shared_data.get("game_mode", "")
            important = self.manager.shared_data.get("is_important_match", False)
            
            if important:
                self.intro_type = "ELIMINATORIA" if mode == "tournament" else "PARTIDO CRUCIAL"
            elif self.left_team.get("ovr", 0) > 82 and self.right_team.get("ovr", 0) > 82:
                self.intro_type = "DUELO DE TITANES"
            elif self.left_team.get("country") == self.right_team.get("country") and self.left_team.get("ovr", 0) > 75:
                self.intro_type = "DERBI"
                
            if self.intro_type:
                self.intro_timer = 4.5

    def _setup_players(self):
        pitch_rect = self.pitch.rect
        from settings import FORMATIONS
        from data.rosters import get_base_rosters, calculate_ovr
        from data.career_manager import career_manager
        self.left_gk = None
        self.right_gk = None

        all_r = get_base_rosters()

        # ── Left Team Roster Setup ──
        left_roster = self.left_team.get("roster", [])
        if not left_roster:
            left_roster = all_r.get(self.left_team.get("short"), [])
            if not left_roster:
                from data.procedural import generate_roster
                team_stats = self.left_team.get("stats", {"speed": 75, "shot": 75, "defense": 75, "passing": 75})
                team_ovr = int((team_stats["speed"] + team_stats["shot"] + team_stats["defense"] + team_stats["passing"]) / 4)
                left_roster = generate_roster(self.left_team.get("league", "EN"), team_ovr)
                self.left_team["roster"] = left_roster
                
        # ── Right Team Roster Setup ──
        right_roster = self.right_team.get("roster", [])
        if not right_roster:
            right_roster = all_r.get(self.right_team.get("short"), [])
            if not right_roster:
                from data.procedural import generate_roster
                team_stats = self.right_team.get("stats", {"speed": 75, "shot": 75, "defense": 75, "passing": 75})
                team_ovr = int((team_stats["speed"] + team_stats["shot"] + team_stats["defense"] + team_stats["passing"]) / 4)
                right_roster = generate_roster(self.right_team.get("league", "EN"), team_ovr)
                self.right_team["roster"] = right_roster
        
        left_starters_slice = left_roster[:11]
        right_starters_slice = right_roster[:11]
        
        # Reset stamina for non-career modes
        game_mode = self.manager.shared_data.get("game_mode", "quick")
        is_career = game_mode == "career"
        self._is_career_mode = is_career
        if not is_career:
            for p in left_starters_slice: p["energy"] = 100.0
            for p in right_starters_slice: p["energy"] = 100.0

        if not left_starters_slice or not right_starters_slice:
            print("ERROR CRITICO: No hay jugadores iniciales.")
            self.manager.transition_to(None)
            return

        human_formation = self.manager.shared_data.get("formation", "4-3-3")
        # Ultimate Team support
        from systems.ultimate_manager import ultimate_manager
        if self.manager.shared_data.get("game_mode", "").startswith("ultimate"):
            human_formation = ultimate_manager.formation
            cap_name = ultimate_manager.captain_name
            if cap_name:
                user_starters = left_starters_slice if self.user_side == "left" else right_starters_slice
                for p in user_starters: p["is_captain"] = (p.get("name") == cap_name)

        # 1. Selección de Portero
        left_gk_data = next((p for p in left_starters_slice if p.get("pos") == "GK"), None)
        if not left_gk_data:
            left_gk_data = next((p for p in left_roster if p.get("pos") == "GK"), left_starters_slice[0] if left_starters_slice else None)

        right_gk_data = next((p for p in right_starters_slice if p.get("pos") == "GK"), None)
        if not right_gk_data:
            right_gk_data = next((p for p in right_roster if p.get("pos") == "GK"), right_starters_slice[0] if right_starters_slice else None)
            
        # 2. Asegurar que el usuario esté en los titulares si no es suplente
        user_name_clean = career_manager.career_player["name"].lower().strip() if (career_manager.active and career_manager.mode == "player") else ""
        if not self.user_is_sub and user_name_clean:
            user_starters = left_starters_slice if self.user_side == "left" else right_starters_slice
            user_roster = left_roster if self.user_side == "left" else right_roster
            user_gk = left_gk_data if self.user_side == "left" else right_gk_data
            
            user_in_slice = any(p.get("name", "").lower().strip() == user_name_clean for p in user_starters)
            if not user_in_slice:
                user_p = next((p for p in user_roster if p.get("name", "").lower().strip() == user_name_clean), None)
                if user_p:
                    # Reemplazar al jugador de campo con menor OVR por el usuario
                    idx_to_replace = 10 if user_starters[10] != user_gk else 9
                    user_starters[idx_to_replace] = user_p

        left_field_data = [p for p in left_starters_slice if p != left_gk_data]
        right_field_data = [p for p in right_starters_slice if p != right_gk_data]
        
        # Ordenar por categoría de posición para que coincidan con las coordenadas (DEF, MID, ATT)
        def pos_order(p):
            pos = p.get("pos", "ST")
            if pos in ["CB", "LB", "RB", "LWB", "RWB"]: return 0
            if pos in ["CM", "CDM", "CAM", "LM", "RM"]: return 1
            return 2
            
        left_field_data.sort(key=pos_order)
        right_field_data.sort(key=pos_order)

        # Primero, separamos al usuario del resto para ponerlo donde corresponde
        user_p_data = None
        user_field_data = left_field_data if self.user_side == "left" else right_field_data
        if not self.user_is_sub and user_name_clean:
            for p in user_field_data:
                if p.get("name", "").lower().strip() == user_name_clean:
                    user_p_data = p
                    break

        # Re-ordenar para asegurar que el usuario tenga prioridad en su categoría
        def get_final_order_fn(team_side):
            def final_order(p):
                order = pos_order(p)
                is_u = (team_side == self.user_side and user_name_clean and p.get("name", "").lower().strip() == user_name_clean)
                return (order, 1 if is_u else 0)
            return final_order
        
        left_field_data.sort(key=get_final_order_fn("left"))
        right_field_data.sort(key=get_final_order_fn("right"))

        # ── Left Team Setup ──
        self.left_field = []
        for player_data, (fx, fy) in zip(left_field_data, FORMATIONS.get(human_formation, FORMATIONS["4-3-3"])):
            player = FieldPlayer(pitch_rect.left + pitch_rect.width * fx, pitch_rect.top + pitch_rect.height * fy,
                                self.left_team, player_data=player_data, side="left", formation_pos=(fx, fy))
            player.apply_difficulty(self.difficulty)
            
            # Forzar control si es el usuario
            if self.user_side == "left" and user_p_data and player_data == user_p_data:
                player.is_controlled = True
                player.is_user_player = True
                
            self.left_field.append(player)

        # Si nadie es controlado y el usuario no es sub, controlar al último
        if self.user_side == "left" and not any(p.is_controlled for p in self.left_field) and not self.user_is_sub:
            self.left_field[-1].is_controlled = True

        if left_gk_data:
            self.left_gk = Goalkeeper(pitch_rect.left + 30, pitch_rect.centery, self.left_team, player_data=left_gk_data, side="left")
            self.left_gk.apply_difficulty(self.difficulty)

        # ── Right Team Setup ──
        self.right_field = []
        ai_formation = "4-3-3"
        right_formation = human_formation if self.user_side == "right" else ai_formation
        right_coords = FORMATIONS.get(right_formation, FORMATIONS["4-3-3"])
        
        for player_data, (fx, fy) in zip(right_field_data, right_coords):
            inverted_fx = 1.0 - fx
            player = FieldPlayer(pitch_rect.right - pitch_rect.width * fx, pitch_rect.top + pitch_rect.height * fy,
                                self.right_team, player_data=player_data, side="right", formation_pos=(inverted_fx, fy))
            player.apply_difficulty(self.difficulty)
            
            # Forzar control si es el usuario
            if self.user_side == "right" and user_p_data and player_data == user_p_data:
                player.is_controlled = True
                player.is_user_player = True
                
            self.right_field.append(player)

        # Si nadie es controlado y el usuario no es sub, controlar al último
        if self.user_side == "right" and not any(p.is_controlled for p in self.right_field) and not self.user_is_sub:
            self.right_field[-1].is_controlled = True

        if right_gk_data:
            self.right_gk = Goalkeeper(pitch_rect.right - 30, pitch_rect.centery, self.right_team, player_data=right_gk_data, side="right")
            self.right_gk.apply_difficulty(self.difficulty)
            
        # Bench setup
        self.left_bench = [p for p in self.left_team.get("roster", []) if p not in left_starters_slice]
        self.right_bench = [p for p in self.right_team.get("roster", []) if p not in right_starters_slice]
        
        # Procedural Bench Generation (In case roster is empty or small)
        def generate_procedural_bench(team_data, current_field_data, existing_bench):
            if len(existing_bench) >= 8: return existing_bench
            needed = 8 - len(existing_bench)
            from data.rosters import calculate_ovr
            import random
            
            team_stats = team_data.get("stats", {"speed": 75, "shot": 75, "defense": 75, "passing": 75})
            new_bench = existing_bench[:]
            positions = ["GK", "CB", "LB", "RB", "CM", "CDM", "CAM", "ST", "LW", "RW"]
            
            for _ in range(needed):
                pos = random.choice(positions)
                p_ovr = int((team_stats["speed"] + team_stats["shot"] + team_stats["defense"] + team_stats["passing"]) / 4) + random.randint(-5, 5)
                p_ovr = max(60, min(95, p_ovr))
                
                gen_p = {
                    "name": f"{team_data.get('short', 'T')} Sub {len(new_bench)+1}",
                    "pos": pos,
                    "num": random.randint(12, 99),
                    "nat": team_data.get("league", "??"),
                    "age": random.randint(18, 32),
                    "ovr": p_ovr,
                    "s": {
                        "speed": team_stats["speed"] + random.randint(-10, 10),
                        "shot": team_stats["shot"] + random.randint(-10, 10),
                        "passing": team_stats["passing"] + random.randint(-10, 10),
                        "defense": team_stats["defense"] + random.randint(-10, 10),
                        "gk": 10 if pos != "GK" else p_ovr,
                        "dribbling": 70,
                        "physical": 70
                    }
                }
                new_bench.append(gen_p)
            return new_bench

        self.left_bench = generate_procedural_bench(self.left_team, left_starters_slice, self.left_bench)
        self.right_bench = generate_procedural_bench(self.right_team, right_starters_slice, self.right_bench)

        for p in self.left_bench + self.right_bench:
            if "ovr" not in p: p["ovr"] = calculate_ovr(p)

        self.left_all = self.left_field + ([self.left_gk] if self.left_gk else [])
        self.right_all = self.right_field + ([self.right_gk] if self.right_gk else [])
        self.all_players = self.left_all + self.right_all

        # Capitanes
        def assign_captain(players, force_player_name=None):
            if not players: return
            cap = None
            if force_player_name:
                cap = next((p for p in players if p.player_data.get("name") and p.player_data["name"].lower().strip() == force_player_name.lower().strip()), None)
            if not cap:
                cap = next((p for p in players if p.player_data.get("is_captain")), None)
            if not cap:
                cap = max(players, key=lambda p: p.player_data.get("ovr", 70))
            if cap:
                for p in players: p.player_data["is_captain"] = False
                cap.player_data["is_captain"] = True

        force_left_cap = career_manager.career_player["name"] if (self.user_side == "left" and career_manager.active and career_manager.mode == "player" and career_manager.career_stats.get("coach_confidence", 0) > 85) else None
        force_right_cap = career_manager.career_player["name"] if (self.user_side == "right" and career_manager.active and career_manager.mode == "player" and career_manager.career_stats.get("coach_confidence", 0) > 85) else None
        
        assign_captain(self.left_all, force_left_cap)
        assign_captain(self.right_all, force_right_cap)

        if career_manager.active and career_manager.mode == "player" and not self.user_is_sub:
            cp = career_manager.career_player
            user_all = self.left_all if self.user_side == "left" else self.right_all
            for p in user_all:
                if p.player_data.get("is_user_player") or (p.player_data.get("name") and cp.get("name") and p.player_data["name"].lower().strip() == cp["name"].lower().strip()):
                    self.switch_controlled_player(p)
                    break

    def _kickoff(self):
        pitch_rect = self.pitch.rect
        self.ball.reset(WIDTH // 2, HEIGHT // 2)
        self.goal_scored = False
        self._goal_handled_frame = -1
        self.is_kickoff = True
        self.kickoff_team = self.manager.shared_data.get("kickoff_team", "left")

        left_active = [p for p in self.left_field if not p.red_card]
        right_active = [p for p in self.right_field if not p.red_card]

        # Primero mandar a todos los expulsados fuera del campo
        for p in self.left_field + self.right_field:
            if p.red_card:
                p.pos = pygame.math.Vector2(-1000, -1000)
                p.has_ball = False

        if left_active:
            for i, player in enumerate(left_active):
                fx, fy = player.formation_pos
                if self.kickoff_team == "left" and i == len(left_active) - 1:
                    player.pos.x = pitch_rect.centerx - 12
                    player.pos.y = pitch_rect.centery
                    player.has_ball = True
                    self.ball.last_touch = "left"
                else:
                    px = pitch_rect.left + pitch_rect.width * fx
                    player.pos.x = min(px, pitch_rect.centerx - 30)
                    player.pos.y = pitch_rect.top + pitch_rect.height * fy

        if self.left_gk:
            self.left_gk.pos.x = pitch_rect.left + 30
            self.left_gk.pos.y = pitch_rect.centery
            if self.left_gk.red_card:
                self.left_gk.pos = pygame.math.Vector2(-1000, -1000)

        if right_active:
            for i, player in enumerate(right_active):
                fx, fy = player.formation_pos
                if self.kickoff_team == "right" and i == len(right_active) - 1:
                    player.pos.x = pitch_rect.centerx + 12
                    player.pos.y = pitch_rect.centery
                    player.has_ball = True
                    self.ball.last_touch = "right"
                else:
                    px = pitch_rect.left + pitch_rect.width * fx
                    player.pos.x = max(px, pitch_rect.centerx + 30)
                    player.pos.y = pitch_rect.top + pitch_rect.height * fy

        if self.right_gk:
            self.right_gk.pos.x = pitch_rect.right - 30
            self.right_gk.pos.y = pitch_rect.centery
            if self.right_gk.red_card:
                self.right_gk.pos = pygame.math.Vector2(-1000, -1000)

        for p in self.all_players: p.is_controlled = False
        our_field = [p for p in (self.left_field if self.left_team == self.user_team else self.right_field) if not p.red_card]
        is_user_kicking_off = (self.kickoff_team == "left" and self.left_team == self.user_team) or \
                              (self.kickoff_team == "right" and self.right_team == self.user_team)
        
        from data.career_manager import career_manager
        assigned = False
        if career_manager.active and career_manager.mode == "player":
            for p in our_field:
                if p.player_data.get("is_user_player") or (p.player_data.get("name") and career_manager.career_player.get("name") and p.player_data["name"].lower().strip() == career_manager.career_player["name"].lower().strip()):
                    self.switch_controlled_player(p)
                    assigned = True
                    break
        
        if not assigned and not self.user_is_sub:
            if is_user_kicking_off and our_field: self.switch_controlled_player(our_field[-1])
            elif our_field: self.switch_controlled_player(min(our_field, key=lambda p: p.pos.distance_to(self.ball.pos)))

    def switch_controlled_player(self, new_player):
        for p in self.all_players: p.is_controlled = False
        new_player.is_controlled = True
        new_player.pass_charge = 0
        new_player.kick_charge = 0
        new_player.receive_cooldown = 0.4
        self.last_switch_time = pygame.time.get_ticks()
        self.switch_cooldown = 0.6

    def _update_team_logic(self):
        if getattr(self, 'is_kickoff', False) or getattr(self, 'is_set_piece', False):
            for p in self.all_players: p.is_active_ai = False
            our_all = self.left_all if self.left_team == self.user_team else self.right_all
            holder = next((p for p in our_all if p.has_ball), None)
            if holder and not holder.is_controlled and not self.user_is_sub: self.switch_controlled_player(holder)
            return

        ball_pos = self.ball.pos
        current_time = pygame.time.get_ticks()
        our_all = self.left_all if self.left_team == self.user_team else self.right_all
        rival_all = self.right_all if self.left_team == self.user_team else self.left_all
        our_field = self.left_field if self.left_team == self.user_team else self.right_field
        rival_field = self.right_field if self.left_team == self.user_team else self.left_field

        for p in rival_field: p.is_active_ai = False
        sorted_rival = sorted(rival_field, key=lambda p: p.pos.distance_to(ball_pos))
        
        # Cantidad de presionantes activos según dificultad
        pressers_limit = 1
        if self.difficulty >= 4: pressers_limit = 2
        if self.difficulty >= 8: pressers_limit = 3

        for i in range(min(len(sorted_rival), pressers_limit)):
            # Solo presionan si están a una distancia razonable (que aumenta con la dificultad)
            if i == 0 or sorted_rival[i].pos.distance_to(ball_pos) < 200 + (self.difficulty * 25):
                sorted_rival[i].is_active_ai = True
                
        our_player_with_ball = next((p for p in our_all if p.has_ball), None)
        controlled = next((p for p in our_all if p.is_controlled), None)
        closest_left = min(our_field, key=lambda p: p.pos.distance_to(ball_pos))
        
        for p in our_field: p.is_active_ai = False
        allies = [p for p in our_field if not p.is_controlled and not p.has_ball]
        if allies:
            sorted_allies = sorted(allies, key=lambda p: p.pos.distance_to(ball_pos))
            for i in range(min(len(sorted_allies), pressers_limit)):
                if i == 0 or sorted_allies[i].pos.distance_to(ball_pos) < 200 + (self.difficulty * 25):
                    sorted_allies[i].is_active_ai = True
        
        from data.career_manager import career_manager
        if career_manager.active and career_manager.mode == "player":
            if self.user_is_sub:
                for p in self.all_players: p.is_controlled = False
                closest_left.is_active_ai = True
                return
            cp = career_manager.career_player
            if cp and (not controlled or not controlled.player_data.get("name") or controlled.player_data["name"].lower().strip() != cp["name"].lower().strip()):
                for p in our_all:
                    if p.player_data.get("name") and p.player_data["name"].lower().strip() == cp["name"].lower().strip():
                        self.switch_controlled_player(p)
            return

        if our_player_with_ball and controlled != our_player_with_ball:
            self.switch_controlled_player(our_player_with_ball)
            controlled = our_player_with_ball

        keys = pygame.key.get_pressed()
        user_is_active = any([keys[pygame.K_UP], keys[pygame.K_DOWN], keys[pygame.K_LEFT], keys[pygame.K_RIGHT], keys[pygame.K_w], keys[pygame.K_a], keys[pygame.K_s], keys[pygame.K_d], keys[pygame.K_e], keys[pygame.K_SPACE]])
        if user_is_active and not our_player_with_ball:
            if current_time - getattr(self, 'last_switch_time', 0) > 200:
                if getattr(self, 'switch_cooldown', 0) <= 0:
                    if controlled != closest_left: self.switch_controlled_player(closest_left)
                        
    def _manual_switch(self):
        from data.career_manager import career_manager
        if career_manager.active and career_manager.mode == "player": return
        our_all = self.left_all if self.left_team == self.user_team else self.right_all
        our_field = [p for p in (self.left_field if self.left_team == self.user_team else self.right_field) if not p.red_card]
        controlled = next((p for p in our_all if p.is_controlled), None)
        closest = None
        min_dist = float('inf')
        for p in our_field:
            if p != controlled:
                dist = p.pos.distance_to(self.ball.pos)
                if dist < min_dist:
                    min_dist = dist
                    closest = p
        if closest: self.switch_controlled_player(closest)

    def _force_switch_away_from_red_card(self):
        our_field = [p for p in (self.left_field if self.left_team == self.user_team else self.right_field) if not p.red_card]
        if our_field:
            closest = min(our_field, key=lambda p: p.pos.distance_to(self.ball.pos))
            self.switch_controlled_player(closest)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if getattr(self, 'in_pause_menu', False):
                    if event.key == pygame.K_ESCAPE: self.in_pause_menu = False
                    elif event.key == pygame.K_UP: self.pause_sel = max(0, getattr(self, 'pause_sel', 0) - 1)
                    elif event.key == pygame.K_DOWN: self.pause_sel = min(2, getattr(self, 'pause_sel', 0) + 1)
                    elif event.key == pygame.K_RETURN:
                        sel = getattr(self, 'pause_sel', 0)
                        if sel == 0: self.in_pause_menu = False
                        elif sel == 1:
                            from scenes.tactics import TacticsScene
                            self.manager.push_scene(TacticsScene, in_match=True, match_scene=self)
                        elif sel == 2:
                            mode = self.manager.shared_data.get("game_mode", "")
                            if mode.startswith("ultimate"): from scenes.ultimate_hub import UltimateHubScene; self.manager.transition_to(UltimateHubScene)
                            elif mode == "online": from scenes.online_hub import OnlineHubScene; self.manager.transition_to(OnlineHubScene)
                            elif mode == "career": from scenes.career_hub import CareerHubScene; self.manager.transition_to(CareerHubScene)
                            elif mode == "tournament": from scenes.tournament_hub import TournamentHubScene; self.manager.transition_to(TournamentHubScene)
                            else: from scenes.main_menu import MainMenuScene; self.manager.transition_to(MainMenuScene)
                    return
                else:
                    if event.key == pygame.K_ESCAPE: self.in_pause_menu = True; self.pause_sel = 0; return
                    elif event.key == pygame.K_q: self._manual_switch()
                    elif event.key == pygame.K_p: # FORZAR ENTRADA (Sustitución Manual)
                        if self.user_is_sub:
                            print("DEBUG: Forzando entrada del usuario...")
                            self._force_user_substitution()
                        else:
                            print("DEBUG: El usuario ya está en el campo o no es modo carrera.")
                    elif event.key == pygame.K_RETURN and self.halftime_pause:
                        self.halftime_pause = False
                        self.hud.paused = False
                        self.hud.half = 2
                        self.out_of_bounds_msg = ""
                        self._setup_new_half()
                        self.manager.shared_data["kickoff_team"] = "right" if self.manager.shared_data.get("first_half_kickoff", "left") == "left" else "left"
                        self._kickoff()

    def _setup_new_half(self):
        self.ball.reset(WIDTH // 2, HEIGHT // 2)
        self._swap_sides()

    def on_exit(self):
        from systems.audio_manager import audio_manager
        audio_manager.stop_crowd_bg()

    def update(self, dt):
        if dt > 0.05: dt = 0.05  # Failsafe para evitar saltos enormes tras menús
        
        if getattr(self, "intro_timer", 0) > 0:
            self.intro_timer -= dt
            return
        if getattr(self, "in_pause_menu", False): return
        
        # Aceleración de tiempo para suplentes
        sim_steps = 1
        keys = pygame.key.get_pressed()
        if self.user_is_sub and keys[pygame.K_s]:
            sim_steps = 3 # x3 velocidad
            
        for _ in range(sim_steps):
            if getattr(self, "sub_freeze", 0) > 0:
                self.sub_freeze -= dt
                if self.sub_freeze <= 0 and getattr(self, "out_of_bounds_timer", 0) <= 0:
                    self.out_of_bounds_msg = ""
                continue
            if self.goal_freeze > 0: self.goal_freeze -= dt; continue
            if self.hud.is_match_over(): self._end_match(); return
            if self.hud.is_half_over() and self.hud.half == 1 and not getattr(self, 'halftime_pause', False): self._trigger_halftime(); return
            
            if getattr(self, "out_of_bounds_timer", 0) > 0:
                self.out_of_bounds_timer -= dt
                if self.out_of_bounds_timer <= 0:
                    if getattr(self, "pending_subs", []):
                        self._process_pending_subs()
                        self.out_of_bounds_timer = 2.0
                    else:
                        self._reset_from_out()
                continue
            is_k = getattr(self, 'is_kickoff', False)
            is_sp = getattr(self, 'is_set_piece', False)
            if is_k or is_sp:
                if is_k and self.ball.vel.length() > 50:
                    self.is_kickoff = False
            else:
                self.hud.update(dt)
            
            # Tension music in the last 5 minutes of match
            game_min = int(self.hud.match_time * (90 / self.hud.match_duration))
            if game_min >= 85 and not getattr(self, "_tension_music_playing", False) and not self.hud.is_match_over():
                self._tension_music_playing = True
                from systems.audio_manager import audio_manager
                audio_manager.play_match_tension()
                
            if getattr(self, 'switch_cooldown', 0) > 0: self.switch_cooldown -= dt
            if is_sp:
                our_all = self.left_all if self.left_team == self.user_team else self.right_all
                if not any(p.has_ball for p in our_all):
                    self.is_set_piece = False
                    self.out_of_bounds_msg = ""

            if hasattr(self, "_user_sub_timer"):
                self._user_sub_timer -= dt
                if self._user_sub_timer <= 0 and not getattr(self, "out_of_bounds_timer", 0) > 0:
                    # Forzar salida del balón para el cambio del usuario
                    self.out_of_bounds_timer = 1.5
                    self.ball.out_of_bounds = "manual" # Trigger whistle
                    if hasattr(self, "_user_sub_timer"): delattr(self, "_user_sub_timer")

            # Cambiar control si el jugador activo tiene tarjeta roja
            controlled = next((p for p in (self.left_all + self.right_all) if p.is_controlled), None)
            if controlled and controlled.red_card:
                self._force_switch_away_from_red_card()

            self._update_team_logic()
            # Lógica del coach: chequeo constante regulado internamente
            self._update_coach_logic(dt)
            for p in self.left_field: p.update(dt, self.ball, self.pitch.rect, teammates=self.left_field, opponents=self.right_all, match_scene=self)
            for p in self.right_field: p.update(dt, self.ball, self.pitch.rect, teammates=self.right_field, opponents=self.left_all, match_scene=self)
            self.left_gk.update(dt, self.ball, self.pitch.rect, teammates=self.left_field, opponents=self.right_field, match_scene=self)
            self.right_gk.update(dt, self.ball, self.pitch.rect, teammates=self.right_field, opponents=self.left_field, match_scene=self)
            goal = self.ball.update(dt, self.pitch.rect, self.pitch.left_goal_rect, self.pitch.right_goal_rect)
            if goal:
                self._handle_goal(goal)
                break
            else:
                self._check_out_of_bounds()

    def _handle_foul(self, player, victim):
        """Procesa una falta cometida por 'player' sobre 'victim'."""
        if getattr(self, "out_of_bounds_timer", 0) > 0: return # Evitar spam
        
        # Probabilidades basadas en agresividad y dificultad
        foul_roll = random.random()
        
        # Siempre silbar falta si es colisión de tackle
        self.ball.vel *= 0.1 # Frenar el balón
        self.out_of_bounds_timer = 2.5
        self.out_of_bounds_msg = f"¡FALTA DE {player.player_data['name'].upper()}!"
        from systems.audio_manager import audio_manager
        audio_manager.play_foul_whistle()
        
        # 1. Determinar tarjeta (probabilidades realistas)
        card = None
        if foul_roll < 0.003:
            card = "RED"      # 0.3% roja directa
        elif foul_roll < 0.08:
            card = "YELLOW"   # ~7.7% amarilla
            
        if card == "YELLOW":
            player.yellow_cards += 1
            player.match_stats["yellow_cards"] += 1
            self.out_of_bounds_msg += " [AMARILLA]"
            from systems.audio_manager import audio_manager
            audio_manager.play_card("yellow")
            if player.yellow_cards >= 2:
                card = "RED" # Doble amarilla
                
        if card == "RED":
            player.red_card = True
            player.match_stats["red_card"] = 1
            self.out_of_bounds_msg += " [ROJA] EXPULSADO"
            from systems.audio_manager import audio_manager
            audio_manager.play_card("red")
            
        # 2. Determinar lesión del receptor (3% de probabilidad)
        if random.random() < 0.03:
            self._handle_injury(victim, intensity=foul_roll)
            
        # 3. Penalización en rating
        player.match_stats["rating"] -= 0.3
        if card == "YELLOW": player.match_stats["rating"] -= 0.5
        if card == "RED": player.match_stats["rating"] -= 1.5
        
        # 4. Configurar tiro libre para el equipo de la víctima
        victim_side = victim.side if hasattr(victim, 'side') else ("left" if player.side == "right" else "right")
        # Guardar posición de la falta para el tiro libre
        self._foul_pos = pygame.math.Vector2(victim.pos.x, victim.pos.y)
        self.next_set_piece = ("free_kick", victim_side, None)

    def _handle_injury(self, player, intensity):
        """Aplica un estado de lesión al jugador."""
        player.is_injured = True
        player.injury_severity = int(intensity * 100)
        from systems.audio_manager import audio_manager
        audio_manager.play_crowd_reaction("boo")
        
        msg = f"¡{player.player_data['name'].upper()} SE HA LESIONADO!"
        if player.injury_severity > 70:
            msg += " (GRAVE)"
            # Forzar cambio si es grave
            if player.side == "left":
                self._check_team_subs("left", self.left_field, self.left_bench)
            else:
                self._check_team_subs("right", self.right_field, self.right_bench)
        
        self.out_of_bounds_msg = msg
        self.out_of_bounds_timer = 3.0

    def _handle_goal(self, scoring_side):
        if self.goal_scored: return
        self.goal_scored = True
        
        if getattr(self, "_goal_handled_frame", -1) == self.hud.match_time: return # Evitar doble conteo frame
        
        scorer_name = self.ball.last_touch_name
        game_min = int(self.hud.match_time * (90 / self.hud.match_duration))
        self.goal_freeze = GOAL_FREEZE_TIME
        
        from systems.audio_manager import audio_manager
        audio_manager.play_goal_cheer()
        audio_manager.play_whistle()
        
        self.manager.shared_data["kickoff_team"] = "right" if scoring_side == "left" else "left"
        self.manager.shared_data["match_state"] = {
            "hud": self.hud, "left_field": self.left_field, "right_field": self.right_field,
            "left_gk": self.left_gk, "right_gk": self.right_gk, "sub_performed": self.sub_performed,
            "match_goal_events": self.match_goal_events, "user_side": self.user_side,
            "user_is_sub": self.user_is_sub, "halftime_pause": getattr(self, 'halftime_pause', False),
            "out_of_bounds_msg": getattr(self, 'out_of_bounds_msg', ""), "out_of_bounds_timer": getattr(self, 'out_of_bounds_timer', 0)
        }
        scoring_team = self.left_team if scoring_side == "left" else self.right_team
        team_side_for_hud = "left" if scoring_team["short"] == self.hud.left_team["short"] else "right"
        self.hud.add_goal(team_side_for_hud, scorer_name=scorer_name, minute=game_min)
        assistant_name = self.ball.assistant_name if self.ball.assistant_name != self.ball.last_touch_name else None
        is_decisive = (game_min > 85)
        for p in (self.left_all + self.right_all):
            p_name_clean = p.player_data.get("name", "").lower().strip()
            if p_name_clean and scorer_name and p_name_clean == scorer_name.lower().strip():
                p.match_stats["goals"] += 1
                if is_decisive: p.match_stats["rating"] += 0.5
            if assistant_name and p_name_clean and p_name_clean == assistant_name.lower().strip():
                p.match_stats["assists"] += 1
        self.match_goal_events.append({"scorer": scorer_name, "assistant": assistant_name, "min": game_min, "team": scoring_team["short"]})
        from scenes.goal_celebration import GoalCelebrationScene
        self.manager.transition_to(GoalCelebrationScene, scoring_team=scoring_team, left_score=self.hud.left_score, right_score=self.hud.right_score, left_team=self.left_team, right_team=self.right_team, scorer_name=scorer_name, goal_min=game_min)

    def _end_match(self):
        self._calculate_all_ratings()
        from systems.audio_manager import audio_manager
        audio_manager.play_whistle()
        from scenes.goal_celebration import MatchEndScene
        user_team_short = self.user_team.get("short", "") if self.user_team else ""
        left_team_short = self.hud.left_team.get("short", "") if self.hud.left_team else ""
        user_side_initial = "left" if (user_team_short and left_team_short == user_team_short) else "right"
        p_stats = []
        for p in self.left_all + self.right_all:
            p_stats.append({
                "name": p.player_data["name"],
                "team": p.team_data["short"],
                "rating": p.match_stats["rating"],
                "goals": p.match_stats["goals"],
                "assists": p.match_stats["assists"],
                "yellow_cards": p.match_stats["yellow_cards"],
                "red_card": p.match_stats["red_card"],
                "is_injured": p.is_injured,
                "injury_severity": p.injury_severity
            })
        self.manager.transition_to(MatchEndScene, left_score=self.hud.left_score, right_score=self.hud.right_score, 
                                 left_team=self.hud.left_team, right_team=self.hud.right_team, 
                                 player_side=user_side_initial, goal_events=self.match_goal_events, 
                                 player_stats=p_stats)
        
    def _calculate_all_ratings(self):
        importance = 1.0
        if self.manager.shared_data.get("game_mode") == "tournament": importance = 1.2
        for p in (self.left_all + self.right_all):
            stats = p.match_stats
            pos = p.player_data.get("pos", "CM")
            rating = 5.5
            rating += stats["goals"] * 1.6
            rating += stats["assists"] * 1.2
            rating += (stats["passes_completed"] / 15.0)
            if pos == "GK":
                rating += stats["saves"] * 0.35
                if (p.side == "left" and self.hud.right_score == 0) or (p.side == "right" and self.hud.left_score == 0): rating += 0.8
            elif pos in ["CB", "LB", "RB", "CDM"]: rating += stats["steals"] * 0.28
            else: rating += stats["steals"] * 0.15
            rating *= (0.95 + importance * 0.05)
            my_score = self.hud.left_score if p.side == "left" else self.hud.right_score
            opp_score = self.hud.right_score if p.side == "left" else self.hud.left_score
            if my_score > opp_score: rating += 0.5
            elif my_score < opp_score: rating -= 0.3
            import random
            rating += random.uniform(-0.2, 0.2)
            p.match_stats["rating"] = round(max(1.0, min(10.0, rating)), 1)

    def _swap_sides(self):
        pitch_rect = self.pitch.rect
        for player in self.left_field + self.right_field:
            player.side = "right" if player.side == "left" else "left"
            fx, fy = player.formation_pos
            player.formation_pos = (1.0 - fx, fy)
        self.left_gk.side = "right" if self.left_gk.side == "left" else "left"
        self.left_gk.home_x = pitch_rect.right - 30 if self.left_gk.side == "right" else pitch_rect.left + 30
        self.right_gk.side = "right" if self.right_gk.side == "left" else "left"
        self.right_gk.home_x = pitch_rect.right - 30 if self.right_gk.side == "right" else pitch_rect.left + 30
        self.left_field, self.right_field = self.right_field, self.left_field
        self.left_gk, self.right_gk = self.right_gk, self.left_gk
        self.user_side = "right" if self.user_side == "left" else "left"
        self.left_all = self.left_field + [self.left_gk]
        self.right_all = self.right_field + [self.right_gk]
        
        from systems.audio_manager import audio_manager
        audio_manager.stop_menu_music()
        audio_manager.start_crowd_bg()
        audio_manager.play_whistle()
        
        self.all_players = self.left_all + self.right_all
        self.hud.left_score, self.hud.right_score = self.hud.right_score, self.hud.left_score
        self.hud.left_team, self.hud.right_team = self.hud.right_team, self.hud.left_team
        self.left_bench, self.right_bench = self.right_bench, self.left_bench
        self.left_subs_count, self.right_subs_count = self.right_subs_count, self.left_subs_count
        
    def _trigger_halftime(self):
        self.halftime_pause = True
        self.hud.paused = True
        self.out_of_bounds_msg = "ENTRETIEMPO - PRESIONA ENTER PARA 2T"
            
    def _perform_user_substitution(self):
        from data.career_manager import career_manager
        cp_data = career_manager.career_player
        side = self.user_side
        our_field = self.left_field if side == "left" else self.right_field
        candidates = sorted(our_field, key=lambda x: x.player_data.get("ovr", 70))
        if not candidates: return
        self._perform_manual_sub(side, candidates[0], cp_data)

    def _update_coach_logic(self, dt):
        game_min = int(self.hud.match_time * (90 / self.hud.match_duration))
        # Coach starts thinking about subs after min 25
        if game_min < 25: return 
        
        # Check more frequently but not every frame (every ~1 second of game time)
        if not hasattr(self, "_last_coach_check"): self._last_coach_check = 0
        if self.hud.match_time - self._last_coach_check < 1.0: return
        self._last_coach_check = self.hud.match_time

        # Allow queuing multiple subs up to the limit (5)
        left_queued = len([s for s in self.pending_subs if s[0] == "left"])
        right_queued = len([s for s in self.pending_subs if s[0] == "right"])

        if left_queued + self.left_subs_count < 5:
            self._check_team_subs("left", self.left_field, self.left_bench)
        if right_queued + self.right_subs_count < 5:
            self._check_team_subs("right", self.right_field, self.right_bench)

    def _check_team_subs(self, side, field_players, bench):
        if not bench: return
        current_subs = self.left_subs_count if side == "left" else self.right_subs_count
        if current_subs >= 5: return # FIFA/IFAB rules: 5 subs
        
        game_min = int(self.hud.match_time * (90 / self.hud.match_duration))
        
        from data.career_manager import career_manager
        user_name = career_manager.career_player["name"].lower().strip() if (career_manager.active and career_manager.mode == "player") else None
        
        def pos_cat(pos):
            if pos in ["GK"]: return "GK"
            if pos in ["CB", "LB", "RB", "LWB", "RWB"]: return "DEF"
            if pos in ["CM", "CDM", "CAM", "LM", "RM"]: return "MID"
            return "ATT"
            
        # 1. ¿El usuario está en la banca y debe entrar?
        user_in_bench = next((p for p in bench if p.get("name", "").lower().strip() == user_name), None)
        user_cat = pos_cat(career_manager.career_player.get("pos", "ST") if career_manager.active else "ST")
        
        # Determine team strategy based on score
        # (Simplified: if losing, sub in attackers; if winning, sub in defenders)
        # But mostly we sub by fatigue.
        
        # Sort field players by energy (worst first) to find candidates
        candidates = sorted(field_players, key=lambda p: (p.energy, p.match_stats["rating"]))
        
        current_queued = len([s for s in self.pending_subs if s[0] == side])
        total_used = current_subs + current_queued
        
        for p in candidates:
            if total_used >= 5: break
            
            p_name_clean = p.player_data.get("name", "").lower().strip()
            is_user_player = (user_name and p_name_clean == user_name)
            # User is rarely subbed out unless dead (energy < 15) or very late
            energy_threshold = 15.0 if is_user_player else 75.0 
            if game_min > 60 and not is_user_player: energy_threshold = 82.0
            if game_min > 80 and not is_user_player: energy_threshold = 88.0
            
            should_sub = p.energy < energy_threshold or p.match_stats["rating"] < 5.2
            
            # Special case: Force user entry if they are on the bench
            if not is_user_player and user_in_bench and game_min > 65:
                # If coach is happy/unhappy or just time to play
                if pos_cat(p.player_data.get("pos")) == user_cat:
                    should_sub = True # Force this player out for the user
            
            if should_sub:
                # Find best sub in bench
                best_sub = None
                
                # If user is candidate, they enter
                if user_in_bench and not is_user_player and pos_cat(p.player_data.get("pos")) == user_cat:
                    best_sub = user_in_bench
                
                if not best_sub:
                    # Match position category
                    target_cat = pos_cat(p.player_data.get("pos"))
                    compatibles = [b for b in bench if pos_cat(b.get("pos")) == target_cat]
                    if compatibles:
                        # Pick best OVR
                        best_sub = max(compatibles, key=lambda x: x.get("ovr", 0))
                
                if not best_sub and game_min > 70:
                    # Last resort: just pick the best player remaining
                    best_sub = max(bench, key=lambda x: x.get("ovr", 0))
                
                if best_sub:
                    self.pending_subs.append((side, p, best_sub))
                    if best_sub in bench:
                        bench.remove(best_sub)
                    total_used += 1
                    
                    if best_sub == user_in_bench:
                        self.out_of_bounds_msg = "EL DT TE HA LLAMADO: ENTRAS EN LA PRÓXIMA PAUSA"
                        self._user_sub_timer = 8.0 
                        user_in_bench = None
                    else:
                        team_name = "TU EQUIPO" if side == self.user_side else "RIVAL"
                        self.out_of_bounds_msg = f"CAMBIOS PREPARADOS ({team_name})"


    def _perform_manual_sub(self, side, out_player, in_player_data):
        from entities.field_player import FieldPlayer
        new_p = FieldPlayer(out_player.pos.x, out_player.pos.y, out_player.team_data, player_data=in_player_data, side=side)
        new_p.formation_pos = out_player.formation_pos
        from data.career_manager import career_manager
        is_user = False
        if career_manager.active and career_manager.mode == "player" and in_player_data.get("name") and career_manager.career_player.get("name") and in_player_data["name"].lower().strip() == career_manager.career_player["name"].lower().strip():
            is_user = True; new_p.is_user_player = True
        
        if side == "left":
            if out_player not in self.left_field:
                print(f"DEBUG: Fallo sub left, {out_player.player_data['name']} no está en campo")
                return
            idx = self.left_field.index(out_player); self.left_field[idx] = new_p
            self.left_all = [p if p != out_player else new_p for p in self.left_all]
            if out_player == self.left_gk: self.left_gk = new_p
        else:
            if out_player not in self.right_field:
                print(f"DEBUG: Fallo sub right, {out_player.player_data['name']} no está en campo")
                return
            idx = self.right_field.index(out_player); self.right_field[idx] = new_p
            self.right_all = [p if p != out_player else new_p for p in self.right_all]
            if out_player == self.right_gk: self.right_gk = new_p
        self.all_players = self.left_all + self.right_all
        if is_user:
            self.user_is_sub = False; self.sub_performed = True; self.switch_controlled_player(new_p)
            self.out_of_bounds_msg = "¡ESTÁS DENTRO! DEMUESTRA LO QUE VALES"; self.out_of_bounds_timer = 4.0
        elif out_player.is_controlled: self.switch_controlled_player(new_p)

    def _force_user_substitution(self):
        """Fuerza la entrada del usuario al campo inmediatamente."""
        from data.career_manager import career_manager
        if not career_manager.active or career_manager.mode != "player": return
        
        user_name = career_manager.career_player["name"]
        user_in_bench = next((p for p in self.left_bench + self.right_bench if p.get("name") and user_name and p["name"].lower().strip() == user_name.lower().strip()), None)
        
        if user_in_bench:
            side = "left" if user_in_bench in self.left_bench else "right"
            field = self.left_field if side == "left" else self.right_field
            # Buscar a alguien de la misma zona
            def pos_cat(pos):
                if pos in ["GK"]: return "GK"
                if pos in ["CB", "LB", "RB", "LWB", "RWB"]: return "DEF"
                if pos in ["CM", "CDM", "CAM", "LM", "RM"]: return "MID"
                return "ATT"
            
            user_cat = pos_cat(career_manager.career_player.get("pos", "ST"))
            out_p = next((p for p in field if pos_cat(p.player_data.get("pos")) == user_cat), field[-1])
            
            # Encolar para la siguiente pausa
            if not any(s[2].get("name") and user_name and s[2]["name"].lower().strip() == user_name.lower().strip() for s in self.pending_subs):
                self.pending_subs.append((side, out_p, user_in_bench))
                if user_in_bench in self.left_bench: self.left_bench.remove(user_in_bench)
                else: self.right_bench.remove(user_in_bench)
                self.out_of_bounds_msg = "CALENTANDO... ENTRARÁS EN LA PRÓXIMA PAUSA"
                self.out_of_bounds_timer = 2.0

    def _check_out_of_bounds(self):
        out = self.ball.out_of_bounds
        if out and self.out_of_bounds_timer <= 0:
            self.out_of_bounds_timer = 2.0
            last_side = self.ball.last_touch or "left"
            favored_side = "right" if last_side == "left" else "left"
            if out == "top" or out == "bottom": self.out_of_bounds_msg = "SAQUE DE BANDA"; self.next_set_piece = ("throw_in", favored_side, out)
            else:
                if last_side == out: self.out_of_bounds_msg = "TIRO DE ESQUINA"; self.next_set_piece = ("corner", favored_side, out)
                else: self.out_of_bounds_msg = "SAQUE DE PUERTA"; self.next_set_piece = ("goal_kick", favored_side, out)
            
            for p in self.all_players: p.vel = pygame.math.Vector2(0, 0)
            self.ball.vel = pygame.math.Vector2(0, 0)

    def _process_pending_subs(self):
        """Ejecuta todos los cambios que están en cola al mismo tiempo."""
        if not self.pending_subs: return
        
        to_process = self.pending_subs[:]
        self.pending_subs = []
        
        msg_parts = []
        for side, out_p, in_data in to_process:
            self._perform_manual_sub(side, out_p, in_data)
            if side == "left": self.left_subs_count += 1
            else: self.right_subs_count += 1
            msg_parts.append(f"In: {in_data['name']}")
            
        if msg_parts:
            self.out_of_bounds_msg = "CAMBIOS: " + " | ".join(msg_parts[:3]) + ("..." if len(msg_parts) > 3 else "")

    def _reset_from_out(self):
        self.out_of_bounds_msg = ""; self.ball.out_of_bounds = None
        sp_data = getattr(self, "next_set_piece", None)
        if sp_data is None: sp_data = ("kickoff", "left", None)
        sp_type, favored_side, out_edge = sp_data
        if sp_type == "throw_in": self._start_throw_in(favored_side, out_edge)
        elif sp_type == "goal_kick": self._start_goal_kick(favored_side, out_edge)
        elif sp_type == "corner": self._start_corner(favored_side, out_edge)
        elif sp_type == "free_kick": self._start_free_kick(favored_side)
        else: self._kickoff()
        self.next_set_piece = None

    def _start_throw_in(self, favored_side, edge):
        pitch_rect = self.pitch.rect
        team_players = [p for p in (self.left_field if favored_side == "left" else self.right_field) if not p.red_card]
        is_user_team = (favored_side == self.user_side)
        bx = max(pitch_rect.left + 20, min(pitch_rect.right - 20, self.ball.pos.x))
        by = pitch_rect.top + 2 if edge == "top" else pitch_rect.bottom - 2
        self.ball.reset(bx, by)
        
        if not team_players: 
            self._kickoff(); return
            
        thrower = min(team_players, key=lambda p: p.pos.distance_to(self.ball.pos))
        thrower.pos.x = bx; thrower.pos.y = by; thrower.has_ball = True
        self.ball.last_touch = favored_side
        from data.career_manager import career_manager
        is_user_taking_it = True
        if career_manager.active and career_manager.mode == "player" and thrower.player_data.get("name") and career_manager.career_player.get("name") and thrower.player_data["name"].lower().strip() != career_manager.career_player["name"].lower().strip(): is_user_taking_it = False
        if is_user_team and not self.user_is_sub and is_user_taking_it: self.is_set_piece = True; self.switch_controlled_player(thrower); self.out_of_bounds_msg = "TU SAQUE (Pasa con S)"
        else:
            teammates = [p for p in team_players if p != thrower]
            target = min(teammates, key=lambda p: p.pos.distance_to(thrower.pos))
            kick_dir = (target.pos - thrower.pos)
            pass_dist = kick_dir.length()
            if pass_dist > 0: kick_dir = kick_dir.normalize()
            self.ball.vel = kick_dir * min(450, max(250, pass_dist * 1.8))
            self.ball.target_player = target; thrower.kick_cooldown = 1.0; thrower.has_ball = False
        
    def _start_goal_kick(self, favored_side, edge):
        pitch_rect = self.pitch.rect
        gk = self.left_gk if favored_side == "left" else self.right_gk
        if not gk:
            # Fallback si no hay portero (raro pero posible en bugs de subs)
            team_players = [p for p in (self.left_field if favored_side == "left" else self.right_field) if not p.red_card]
            if not team_players: self._kickoff(); return
            gk = min(team_players, key=lambda p: p.pos.distance_to(pygame.math.Vector2(pitch_rect.left if favored_side=="left" else pitch_rect.right, pitch_rect.centery)))

        bx = pitch_rect.left + 80 if favored_side == "left" else pitch_rect.right - 80
        by = pitch_rect.centery; self.ball.reset(bx, by)
        gk.pos.x = bx - 10 if favored_side == "left" else bx + 10; gk.pos.y = by; gk.has_ball = True; self.ball.last_touch = favored_side
        from data.career_manager import career_manager
        is_user_taking_it = True
        if career_manager.active and career_manager.mode == "player" and gk.player_data.get("name") and career_manager.career_player.get("name") and gk.player_data["name"].lower().strip() != career_manager.career_player["name"].lower().strip(): is_user_taking_it = False
        if favored_side == self.user_side and not self.user_is_sub and is_user_taking_it: self.is_set_piece = True; self.switch_controlled_player(gk); self.out_of_bounds_msg = "SAQUE DE PUERTA (Pasa con S)"
        else:
            team_players = [p for p in (self.left_field if favored_side == "left" else self.right_field) if not p.red_card]
            target = min(team_players, key=lambda p: p.pos.distance_to(gk.pos))
            kick_dir = (target.pos - gk.pos)
            pass_dist = kick_dir.length()
            if pass_dist > 0: kick_dir = kick_dir.normalize()
            self.ball.vel = kick_dir * min(500, max(300, pass_dist * 1.5))
            self.ball.target_player = target; gk.kick_cooldown = 1.0; gk.has_ball = False
        
    def _start_corner(self, favored_side, edge):
        from systems.audio_manager import audio_manager
        audio_manager.play_crowd_reaction("chant")
        pitch_rect = self.pitch.rect
        team_players = [p for p in (self.left_field if favored_side == "left" else self.right_field) if not p.red_card]
        bx = pitch_rect.right - 20 if favored_side == "left" else pitch_rect.left + 20
        by = pitch_rect.top + 20 if self.ball.pos.y < pitch_rect.centery else pitch_rect.bottom - 20
        self.ball.reset(bx, by)
        thrower = min(team_players, key=lambda p: p.pos.distance_to(self.ball.pos))
        thrower.pos.x = bx; thrower.pos.y = by; thrower.has_ball = True; self.ball.last_touch = favored_side
        from data.career_manager import career_manager
        is_user_taking_it = True
        if career_manager.active and career_manager.mode == "player" and thrower.player_data.get("name") and career_manager.career_player.get("name") and thrower.player_data["name"].lower().strip() != career_manager.career_player["name"].lower().strip(): is_user_taking_it = False
        if favored_side == self.user_side and not self.user_is_sub and is_user_taking_it: self.is_set_piece = True; self.switch_controlled_player(thrower); self.out_of_bounds_msg = "CÓRNER (Pasa con S)"
        else:
            teammates = [p for p in team_players if p != thrower]
            target = min(teammates, key=lambda p: p.pos.distance_to(thrower.pos))
            kick_dir = (target.pos - thrower.pos)
            pass_dist = kick_dir.length()
            if pass_dist > 0: kick_dir = kick_dir.normalize()
            self.ball.vel = kick_dir * min(450, max(250, pass_dist * 1.8))
            self.ball.target_player = target; thrower.kick_cooldown = 1.0; thrower.has_ball = False

    def _start_free_kick(self, favored_side):
        """Ejecuta un tiro libre para el equipo indicado desde la posición de la falta."""
        pitch_rect = self.pitch.rect
        team_players = [p for p in (self.left_field if favored_side == "left" else self.right_field) if not p.red_card]
        is_user_team = (favored_side == self.user_side)
        
        # Usar la posición guardada de la falta, o la posición actual del balón como fallback
        foul_pos = getattr(self, '_foul_pos', None)
        if foul_pos:
            bx = max(pitch_rect.left + 30, min(pitch_rect.right - 30, foul_pos.x))
            by = max(pitch_rect.top + 20, min(pitch_rect.bottom - 20, foul_pos.y))
        else:
            bx = max(pitch_rect.left + 30, min(pitch_rect.right - 30, self.ball.pos.x))
            by = max(pitch_rect.top + 20, min(pitch_rect.bottom - 20, self.ball.pos.y))
        
        self.ball.reset(bx, by)
        self._foul_pos = None  # Limpiar posición de falta
        
        if not team_players:
            self._kickoff(); return
        
        kicker = min(team_players, key=lambda p: p.pos.distance_to(self.ball.pos))
        kicker.pos.x = bx; kicker.pos.y = by; kicker.has_ball = True
        self.ball.last_touch = favored_side
        
        from data.career_manager import career_manager
        is_user_taking_it = True
        if career_manager.active and career_manager.mode == "player" and kicker.player_data.get("name") and career_manager.career_player.get("name") and kicker.player_data["name"].lower().strip() != career_manager.career_player["name"].lower().strip():
            is_user_taking_it = False
        
        if is_user_team and not self.user_is_sub and is_user_taking_it:
            self.is_set_piece = True
            self.switch_controlled_player(kicker)
            self.out_of_bounds_msg = "TIRO LIBRE (Pasa con S)"
        else:
            # IA ejecuta el tiro libre automáticamente
            teammates = [p for p in team_players if p != kicker]
            if not teammates:
                # Si no hay compañeros, disparar hacia portería
                goal_x = pitch_rect.right if favored_side == "left" else pitch_rect.left
                kick_dir = pygame.math.Vector2(goal_x - kicker.pos.x, pitch_rect.centery - kicker.pos.y)
                if kick_dir.length() > 0: kick_dir = kick_dir.normalize()
                self.ball.vel = kick_dir * 400
                kicker.kick_cooldown = 1.0; kicker.has_ball = False
            else:
                target = min(teammates, key=lambda p: p.pos.distance_to(kicker.pos))
                kick_dir = (target.pos - kicker.pos)
                pass_dist = kick_dir.length()
                if pass_dist > 0: kick_dir = kick_dir.normalize()
                self.ball.vel = kick_dir * min(450, max(250, pass_dist * 1.8))
                self.ball.target_player = target; kicker.kick_cooldown = 1.0; kicker.has_ball = False

    def draw(self, surface):
        self.pitch.surface = surface; surface.fill(BLACK); self.pitch.draw()
        all_entities = self.all_players + [self.ball]; all_entities.sort(key=lambda e: e.pos.y)
        for entity in all_entities: entity.draw(surface)
        if getattr(self, "intro_timer", 0) > 0: self._draw_intro(surface)
        self.hud.shared_match_state = {"left_field": self.left_field, "right_field": self.right_field, "left_gk": self.left_gk, "right_gk": self.right_gk}
        self.hud.draw(surface)
        if self.out_of_bounds_msg:
            try: f_big = pygame.font.SysFont("Impact", 60)
            except: f_big = pygame.font.Font(None, 60)
            m_surf = f_big.render(self.out_of_bounds_msg, True, GOLD)
            m_rect = m_surf.get_rect(center=(WIDTH//2, HEIGHT//2))
            bg_r = m_rect.inflate(40, 20); pygame.draw.rect(surface, (0, 0, 0, 180), bg_r); pygame.draw.rect(surface, GOLD, bg_r, 3); surface.blit(m_surf, m_rect)
        if getattr(self, 'in_pause_menu', False):
            overlay = pygame.Surface((WIDTH, HEIGHT)); overlay.fill(BLACK); overlay.set_alpha(200); surface.blit(overlay, (0, 0))
            try: f_title = pygame.font.SysFont("Impact", 60)
            except: f_title = pygame.font.Font(None, 60)
            t_surf = f_title.render("PARTIDO PAUSADO", True, WHITE); surface.blit(t_surf, t_surf.get_rect(center=(WIDTH//2, 200)))
            options = ["REANUDAR PARTIDO", "TÁCTICAS Y SUSTITUCIONES", "ABANDONAR PARTIDO"]
            try: f_opt = pygame.font.SysFont("Arial", 30, bold=True)
            except: f_opt = pygame.font.Font(None, 30)
            for i, opt in enumerate(options):
                color = GOLD if getattr(self, 'pause_sel', 0) == i else (150, 150, 150)
                opt_s = f_opt.render(opt, True, color); rect = opt_s.get_rect(center=(WIDTH//2, 350 + i * 80)); surface.blit(opt_s, rect)
                if getattr(self, 'pause_sel', 0) == i: pygame.draw.rect(surface, GOLD, rect.inflate(40, 20), 3, border_radius=10)
            our_field = self.left_field if self.left_team == self.user_team else self.right_field
            sx_start, sy_start = WIDTH - 250, 250
            p_font = pygame.font.SysFont("Arial", 14, bold=True)
            surface.blit(p_font.render("ESTADO FÍSICO:", True, GOLD), (sx_start, sy_start - 30))
            for idx, p in enumerate(our_field[:11]):
                name, energy = p.player_data["name"][:12], p.energy
                py = sy_start + idx * 25
                surface.blit(p_font.render(name, True, WHITE), (sx_start, py))
                bw, bh, bx = 80, 6, sx_start + 110
                pygame.draw.rect(surface, (40, 40, 40), (bx, py + 5, bw, bh))
                ratio = energy / 100.0; col = (0, 255, 100) if ratio > 0.6 else (255, 200, 0) if ratio > 0.3 else (255, 50, 50)
                pygame.draw.rect(surface, col, (bx, py + 5, int(bw * ratio), bh))
        from systems.touch_manager import touch_manager
        touch_manager.draw(surface)
        import os
        if 'ANDROID_ARGUMENT' not in os.environ and not hasattr(pygame, 'android') and not getattr(self, 'in_pause_menu', False):
            try: f_small = pygame.font.SysFont("Arial", 14)
            except: f_small = pygame.font.Font(None, 14)
            q_surf = f_small.render("Q: Cambiar | A: Chutar/Entrada | S: Pasar/Presión | W: Al Hueco | D: Centro | E: Sprint | Flechas: Mover", True, (150, 150, 180))
            surface.blit(q_surf, (WIDTH // 2 - q_surf.get_width() // 2, HEIGHT - 30))

    def apply_formation(self, new_formation_name):
        from settings import FORMATIONS
        human_coords = FORMATIONS.get(new_formation_name, FORMATIONS["4-3-3"])
        field = self.left_field if self.user_side == "left" else self.right_field
        for player, (fx, fy) in zip(field, human_coords):
            if self.user_side == "right":
                player.formation_pos = (1.0 - fx, fy)
            else:
                player.formation_pos = (fx, fy)

    def apply_substitution(self, old_player_data, new_player_data):
        from entities.field_player import FieldPlayer
        from entities.goalkeeper import Goalkeeper
        sub_done = False
        side = self.user_side
        
        if side == "left":
            for i, p in enumerate(self.left_field):
                if p.player_data == old_player_data:
                    new_p = FieldPlayer(p.pos.x, p.pos.y, self.left_team, player_data=new_player_data, side="left", formation_pos=p.formation_pos)
                    if p.is_controlled: new_p.is_controlled = True
                    self.left_field[i] = new_p; self.left_all = self.left_field + ([self.left_gk] if self.left_gk else []); self.all_players = self.left_all + self.right_all
                    sub_done = True
                    break
            if not sub_done and self.left_gk and self.left_gk.player_data == old_player_data:
                self.left_gk = Goalkeeper(self.left_gk.pos.x, self.left_gk.pos.y, self.left_team, player_data=new_player_data, side="left")
                self.left_all = self.left_field + [self.left_gk]; self.all_players = self.left_all + self.right_all
                sub_done = True
        else:
            for i, p in enumerate(self.right_field):
                if p.player_data == old_player_data:
                    new_p = FieldPlayer(p.pos.x, p.pos.y, self.right_team, player_data=new_player_data, side="right", formation_pos=p.formation_pos)
                    if p.is_controlled: new_p.is_controlled = True
                    self.right_field[i] = new_p; self.right_all = self.right_field + ([self.right_gk] if self.right_gk else []); self.all_players = self.left_all + self.right_all
                    sub_done = True
                    break
            if not sub_done and self.right_gk and self.right_gk.player_data == old_player_data:
                self.right_gk = Goalkeeper(self.right_gk.pos.x, self.right_gk.pos.y, self.right_team, player_data=new_player_data, side="right")
                self.right_all = self.right_field + [self.right_gk]; self.all_players = self.left_all + self.right_all
                sub_done = True
            
        if sub_done:
            self.out_of_bounds_msg = f"[CAMBIO] Sale {old_player_data['name']} / Entra {new_player_data['name']}"
            self.sub_freeze = 3.0

    def queue_manual_substitution(self, old_player_data, new_player_data):
        out_p = None
        side = self.user_side
        field = self.left_field if side == "left" else self.right_field
        gk = self.left_gk if side == "left" else self.right_gk
        bench = self.left_bench if side == "left" else self.right_bench
        
        for p in field:
            if p.player_data == old_player_data:
                out_p = p
                break
        if not out_p and gk and gk.player_data == old_player_data:
            out_p = gk
            
        if out_p:
            if not any(s[2]["name"] == new_player_data["name"] for s in self.pending_subs):
                self.pending_subs.append((side, out_p, new_player_data))
                # Update bench immediately so they can't be queued again
                for i, bp in enumerate(bench):
                    if bp["name"] == new_player_data["name"]:
                        bench[i] = old_player_data
                        break

    def _draw_intro(self, surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        alpha = 220
        if self.intro_timer > 3.5: alpha = int(220 * (1.0 - (self.intro_timer - 3.5)))
        elif self.intro_timer < 1.0: alpha = int(220 * self.intro_timer)
        overlay.fill((10, 10, 15, alpha)); surface.blit(overlay, (0, 0))
        progress = min(1.0, (4.5 - self.intro_timer) * 1.5)
        if self.intro_timer < 1.0: progress = self.intro_timer
        import math
        ease = 1.0 - math.pow(1.0 - progress, 3)
        left_x, right_x, cy = int(-200 + ease * (WIDTH // 2 - 180)), int(WIDTH + 200 - ease * (WIDTH // 2 + 180)), HEIGHT // 2 - 40
        from data.teams import draw_badge
        draw_badge(surface, self.left_team, left_x, cy, size=160); draw_badge(surface, self.right_team, right_x, cy, size=160)
        if progress > 0.5:
            vs_alpha = int(min(255, (progress - 0.5) * 510))
            if self.intro_timer < 1.0: vs_alpha = int(255 * self.intro_timer)
            vs_font = pygame.font.SysFont("Impact", 80) if pygame.font.get_init() else pygame.font.Font(None, 80)
            vs_surf = vs_font.render("VS", True, YELLOW); vs_surf.set_alpha(vs_alpha); surface.blit(vs_surf, vs_surf.get_rect(center=(WIDTH // 2, cy)))
            type_font = pygame.font.SysFont("Arial", 42, bold=True) if pygame.font.get_init() else pygame.font.Font(None, 42)
            type_surf = type_font.render(self.intro_type, True, WHITE); type_surf.set_alpha(vs_alpha); bg_rect = type_surf.get_rect(center=(WIDTH // 2, HEIGHT - 140))
            pygame.draw.rect(surface, (200, 30, 30, vs_alpha), (bg_rect.left - 40, bg_rect.y, bg_rect.width + 80, bg_rect.height)); surface.blit(type_surf, bg_rect)
            if self.intro_timer > 1.0:
                hint_font = pygame.font.SysFont("Arial", 16) if pygame.font.get_init() else pygame.font.Font(None, 16)
                hint_surf = hint_font.render("Presiona SPACE para omitir", True, (150, 150, 150)); hint_surf.set_alpha(vs_alpha); surface.blit(hint_surf, hint_surf.get_rect(center=(WIDTH // 2, HEIGHT - 50)))
