import pygame
import random
from settings import *
from scene_manager import BaseScene
from data.career_manager import career_manager

class PressConferenceScene(BaseScene):
    """A narrative scene where the player/manager answers questions from journalists."""
    
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {} # result, match_data, is_final, etc.
        
        # Determine the topic based on context
        self.mode = career_manager.mode
        self.result = self.context.get("result", "draw")
        self.is_final = self.context.get("is_final", False)
        
        self.questions = self._generate_questions()
        self.current_q_idx = 0
        self.selected_ans_idx = 0
        self.finished = (len(self.questions) == 0)
        
        self.time = 0
        self.alpha = 0
        
        try:
            self.font_q = pygame.font.SysFont("Arial", 28, bold=True)
            self.font_a = pygame.font.SysFont("Arial", 22)
            self.font_title = pygame.font.SysFont("Impact", 40)
            self.font_label = pygame.font.SysFont("Arial", 16, bold=True)
        except:
            self.font_q = pygame.font.Font(None, 28)
            self.font_a = pygame.font.Font(None, 22)
            self.font_title = pygame.font.Font(None, 40)
            self.font_label = pygame.font.Font(None, 16)

        self.flash_timer = 0
        self.journalist_name = random.choice(["G. Rossi", "M. Taylor", "L. García", "F. Müller", "J. Smith"])
        
        self.player_name = "TÚ"
        if career_manager.active and career_manager.career_player:
            self.player_name = career_manager.career_player.get("name", "TÚ")

    def _generate_questions(self):
        pool = []
        
        if self.mode == "player":
            if self.result == "win":
                pool.append({
                    "q": "¿Cómo te sientes tras esta victoria decisiva?",
                    "ans": [
                        {"t": "Ha sido un trabajo de todo el equipo.", "dt": 5, "team": 8, "fan": 3},
                        {"t": "Sabía que podía marcar la diferencia hoy.", "dt": 2, "team": -5, "fan": 10},
                        {"t": "El entrenador planteó el partido perfecto.", "dt": 10, "team": 2, "fan": 2}
                    ]
                })
                pool.append({
                    "q": "Tus compañeros parecen buscarte mucho en el campo...",
                    "ans": [
                        {"t": "Confían en mí y yo confío en ellos.", "dt": 0, "team": 10, "fan": 5},
                        {"t": "Es normal, soy el que crea más peligro.", "dt": 3, "team": -8, "fan": 8},
                        {"t": "Estamos conectando muy bien últimamente.", "dt": 2, "team": 5, "fan": 2}
                    ]
                })
                pool.append({
                    "q": "La afición coreó tu nombre hoy. ¿Qué sentiste?",
                    "ans": [
                        {"t": "Se me puso la piel de gallina. Son increíbles.", "dt": 0, "team": 0, "fan": 12},
                        {"t": "Agradezco el apoyo, pero mantengo la calma.", "dt": 5, "team": 0, "fan": -2},
                        {"t": "Es genial, trabajo cada día para ellos.", "dt": 2, "team": 2, "fan": 8}
                    ]
                })
                pool.append({
                    "q": "¿Crees que el equipo puede mantener esta racha ganadora?",
                    "ans": [
                        {"t": "Si seguimos unidos, nadie nos parará.", "dt": 5, "team": 10, "fan": 5},
                        {"t": "Vamos partido a partido, con humildad.", "dt": 8, "team": 2, "fan": 2},
                        {"t": "Con mi nivel actual, seguro que sí.", "dt": -5, "team": -5, "fan": 10}
                    ]
                })
            elif self.result == "loss":
                pool.append({
                    "q": "Una derrota dura hoy. ¿Qué ha faltado?",
                    "ans": [
                        {"t": "Faltó concentración en momentos clave.", "dt": -5, "team": -2, "fan": -5},
                        {"t": "Asumo la responsabilidad, no estuve fino.", "dt": 5, "team": 5, "fan": 8},
                        {"t": "El rival fue superior, hay que aprender.", "dt": 2, "team": 2, "fan": 3}
                    ]
                })
                pool.append({
                    "q": "El vestuario parecía muy tocado tras el pitido final...",
                    "ans": [
                        {"t": "A nadie le gusta perder, pero nos levantaremos.", "dt": 5, "team": 8, "fan": 5},
                        {"t": "Faltó actitud por parte de algunos compañeros.", "dt": -5, "team": -15, "fan": -2},
                        {"t": "El Míster sabrá cómo animarnos para el próximo.", "dt": 8, "team": 0, "fan": 2}
                    ]
                })
                pool.append({
                    "q": "¿Preocupa el nivel físico del equipo tras este partido?",
                    "ans": [
                        {"t": "Estamos bien, ha sido solo un mal día.", "dt": 2, "team": 5, "fan": 0},
                        {"t": "Debemos entrenar más duro, eso es seguro.", "dt": 5, "team": -2, "fan": 5},
                        {"t": "Yo estoy perfecto, pregúntale a los demás.", "dt": -5, "team": -10, "fan": 2}
                    ]
                })
            else: # Empate o resultado no definido
                pool.append({
                    "q": "Un empate hoy. ¿Saben a poco este punto?",
                    "ans": [
                        {"t": "Queríamos ganar, pero sumar siempre es bueno.", "dt": 2, "team": 2, "fan": 0},
                        {"t": "Merecíamos más, tuvimos las ocasiones.", "dt": -2, "team": 5, "fan": 5},
                        {"t": "Ha sido un partido muy parejo y disputado.", "dt": 0, "team": 2, "fan": 2}
                    ]
                })
                pool.append({
                    "q": "¿Qué crees que faltó para llevarse los 3 puntos?",
                    "ans": [
                        {"t": "Más contundencia en las dos áreas.", "dt": 2, "team": -2, "fan": 2},
                        {"t": "Quizá un poco de suerte al final.", "dt": -2, "team": 2, "fan": -2},
                        {"t": "Mejorar el planteamiento táctico.", "dt": -10, "team": 0, "fan": -5}
                    ]
                })
                pool.append({
                    "q": "La afición exige más victorias en casa...",
                    "ans": [
                        {"t": "Tienen razón, debemos hacernos fuertes aquí.", "dt": 5, "team": 2, "fan": 10},
                        {"t": "Que tengan paciencia, los resultados llegarán.", "dt": -2, "team": 0, "fan": -5},
                        {"t": "Hacemos lo que podemos, el rival también juega.", "dt": 0, "team": 5, "fan": -2}
                    ]
                })
        else: # Manager mode
            if self.result == "win":
                pool.append({
                    "q": "Gran planteamiento hoy. ¿Es este el camino a seguir?",
                    "ans": [
                        {"t": "Los jugadores ejecutaron el plan a la perfección.", "dt": 2, "team": 8, "fan": 5, "board": 5},
                        {"t": "Estamos construyendo algo especial aquí.", "dt": 0, "team": 5, "fan": 10, "board": 2},
                        {"t": "Aún hay cosas que mejorar pese al resultado.", "dt": 5, "team": -2, "fan": 2, "board": 3}
                    ]
                })
                pool.append({
                    "q": "¿Siente que la afición por fin conecta con su estilo de juego?",
                    "ans": [
                        {"t": "Es fundamental que disfruten viéndonos jugar.", "dt": 0, "team": 0, "fan": 12, "board": 2},
                        {"t": "A mí me importan los puntos, no el espectáculo.", "dt": 5, "team": 2, "fan": -10, "board": 5},
                        {"t": "Poco a poco estamos logrando esa sinergia.", "dt": 2, "team": 2, "fan": 5, "board": 0}
                    ]
                })
                pool.append({
                    "q": "¿Qué fue lo más destacable del equipo en este partido?",
                    "ans": [
                        {"t": "La solidez defensiva, estuvimos impenetrables.", "dt": 2, "team": 5, "fan": 2, "board": 2},
                        {"t": "La efectividad arriba, no perdonamos ninguna.", "dt": 2, "team": 5, "fan": 5, "board": 0},
                        {"t": "El esfuerzo y desgaste físico de todos.", "dt": 5, "team": 8, "fan": 0, "board": 2}
                    ]
                })
            else:
                pool.append({
                    "q": "¿Teme por su puesto tras los últimos resultados?",
                    "ans": [
                        {"t": "Sigo confiando plenamente en este grupo.", "dt": -2, "team": 10, "fan": 2, "board": -5},
                        {"t": "Necesitamos refuerzos si queremos competir.", "dt": 0, "team": -5, "fan": 5, "board": -10},
                        {"t": "Trabajaremos el doble para revertir esto.", "dt": 5, "team": 2, "fan": 8, "board": 5}
                    ]
                })
                pool.append({
                    "q": "¿Faltó actitud o fue un error táctico suyo?",
                    "ans": [
                        {"t": "Soy el principal responsable de esta derrota.", "dt": 8, "team": 5, "fan": 2, "board": -2},
                        {"t": "Faltó intensidad en el campo, eso es innegable.", "dt": -5, "team": -8, "fan": 0, "board": 0},
                        {"t": "El rival nos sorprendió, hay que darles mérito.", "dt": 2, "team": 0, "fan": -2, "board": -2}
                    ]
                })
                pool.append({
                    "q": "La afición está perdiendo la paciencia. ¿Qué mensaje les da?",
                    "ans": [
                        {"t": "Les pido que confíen en el proceso.", "dt": 0, "team": 2, "fan": 5, "board": 0},
                        {"t": "Comprendo sus críticas, deben exigirnos más.", "dt": 5, "team": 0, "fan": 8, "board": 2},
                        {"t": "Que apoyen al equipo, los pitos no ayudan.", "dt": -5, "team": 5, "fan": -12, "board": -5}
                    ]
                })
        
        # Dynamic questions based on historic partnerships and rivalries
        if self.mode == "player":
            partnerships = career_manager.career_stats.get("partnerships", {})
            rivalries = career_manager.career_stats.get("rivalries", {})
            
            # Best partner question
            best_partner = None
            best_score = 0
            for name, data in partnerships.items():
                score = data.get("assists_to_you", 0) * 3 + data.get("assists_from_you", 0) * 3 + data.get("goals_together", 0) * 2
                if score > best_score:
                    best_score = score
                    best_partner = name
            
            if best_partner and best_score >= 3:
                pool.append({
                    "q": f"Tu conexión con {best_partner} es espectacular. ¿Cuál es el secreto?",
                    "ans": [
                        {"t": f"Con {best_partner} nos entendemos con la mirada.", "dt": 0, "team": 10, "fan": 5},
                        {"t": "Entrenamos mucho juntos fuera de las horas normales.", "dt": 5, "team": 5, "fan": 2},
                        {"t": "Es pura química natural, no se puede explicar.", "dt": 0, "team": 8, "fan": 8}
                    ]
                })
            
            # Top rival question
            top_rival = None
            top_rival_score = 0
            for name, data in rivalries.items():
                score = data.get("matches_against", 0) + data.get("their_goals", 0) * 2
                if score > top_rival_score:
                    top_rival_score = score
                    top_rival = (name, data)
            
            if top_rival and top_rival_score >= 3:
                rn, rd = top_rival
                pool.append({
                    "q": f"Tu rivalidad con {rn} da mucho de qué hablar. ¿Cómo la vives?",
                    "ans": [
                        {"t": f"{rn} es un gran jugador. Me motiva competir contra él.", "dt": 5, "team": 0, "fan": 5},
                        {"t": "No pierdo el tiempo pensando en rivales individuales.", "dt": 2, "team": 2, "fan": -2},
                        {"t": f"Que hablen las estadísticas. Yo solo quiero ganar.", "dt": 0, "team": 5, "fan": 8}
                    ]
                })
        
        # Pick 3 random questions from pool
        random.shuffle(pool)
        return pool[:3]

    def handle_events(self, events):
        if self.finished:
            for event in events:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    from scenes.career_hub import CareerHubScene
                    self.manager.set_scene(CareerHubScene)
            return

        for event in events:
            if self.finished: break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_ans_idx = (self.selected_ans_idx - 1) % len(self.questions[self.current_q_idx]["ans"])
                elif event.key == pygame.K_DOWN:
                    self.selected_ans_idx = (self.selected_ans_idx + 1) % len(self.questions[self.current_q_idx]["ans"])
                elif event.key == pygame.K_RETURN:
                    self._submit_answer()
                    return

    def _submit_answer(self):
        q_data = self.questions[self.current_q_idx]
        ans = q_data["ans"][self.selected_ans_idx]
        
        # Apply effects
        career_manager.career_stats["coach_confidence"] += ans.get("dt", 0)
        career_manager.career_stats["teammate_rel"] += ans.get("team", 0)
        career_manager.career_stats["fan_rel"] += ans.get("fan", 0)
        career_manager.career_stats["board_rel"] += ans.get("board", 0)
        
        # Clamp stats
        for k in ["coach_confidence", "teammate_rel", "fan_rel", "board_rel"]:
            career_manager.career_stats[k] = max(0, min(100, career_manager.career_stats[k]))
            
        self.current_q_idx += 1
        self.selected_ans_idx = 0
        self.flash_timer = 0.3 # Camera flash effect
        
        if self.current_q_idx >= len(self.questions):
            self.finished = True

    def update(self, dt):
        self.time += dt
        if self.alpha < 255:
            self.alpha = min(255, self.alpha + dt * 500)
            
        if self.flash_timer > 0:
            self.flash_timer -= dt

    def draw(self, surface):
        # Background gradient
        for i in range(HEIGHT):
            c = (15 - i//60, 20 - i//60, 35 - i//60)
            pygame.draw.line(surface, c, (0, i), (WIDTH, i))
        
        # Title "RUEDA DE PRENSA"
        title_surf = self.font_title.render("RUEDA DE PRENSA", True, GOLD)
        surface.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 40))
        
        # Journalist panel
        panel_rect = pygame.Rect(50, 120, WIDTH - 100, 150)
        pygame.draw.rect(surface, (30, 35, 50), panel_rect, border_radius=15)
        pygame.draw.rect(surface, UI_ACCENT, panel_rect, 2, border_radius=15)
        
        if not self.finished:
            q_data = self.questions[self.current_q_idx]
            
            # Label
            label = self.font_label.render(f"PREGUNTA DE {self.journalist_name.upper()}:", True, UI_ACCENT)
            surface.blit(label, (70, 140))
            
            # Question text
            q_text = q_data["q"]
            qs = self.font_q.render(q_text, True, WHITE)
            surface.blit(qs, (70, 175))
            
            # Answers
            for i, ans in enumerate(q_data["ans"]):
                y = 300 + i * 70
                rect = pygame.Rect(70, y, WIDTH - 140, 60)
                
                is_sel = (self.selected_ans_idx == i)
                bg_col = (45, 50, 70) if is_sel else (35, 40, 55)
                border_col = WHITE if is_sel else (60, 65, 80)
                
                pygame.draw.rect(surface, bg_col, rect, border_radius=10)
                pygame.draw.rect(surface, border_col, rect, 2 if is_sel else 1, border_radius=10)
                
                txt_surf = self.font_a.render(ans["t"], True, WHITE if is_sel else UI_TEXT_DIM)
                surface.blit(txt_surf, (rect.centerx - txt_surf.get_width()//2, rect.centery - txt_surf.get_height()//2))
        else:
            # Finished screen
            # Cinematic goodbye from the press officer
            msg_q = self.font_label.render("JEFE DE PRENSA:", True, UI_ACCENT)
            surface.blit(msg_q, (WIDTH//2 - 300, 150))
            
            msg = self.font_q.render("Muchas gracias a todos por su tiempo. Con esto finalizamos la rueda de prensa.", True, WHITE)
            surface.blit(msg, (WIDTH//2 - 300, 180))
            
            p_label = self.font_label.render(f"{self.player_name.upper()}:", True, YELLOW)
            surface.blit(p_label, (WIDTH//2 - 300, 250))
            
            msg_a = self.font_q.render("Gracias a todos. ¡Hasta luego!", True, WHITE)
            surface.blit(msg_a, (WIDTH//2 - 300, 280))
            
            hint = self.font_a.render("Presiona ENTER para salir de la sala", True, UI_ACCENT)
            surface.blit(hint, (WIDTH//2 - hint.get_width()//2, 420))

        # Flash effect
        if self.flash_timer > 0:
            flash_surf = pygame.Surface((WIDTH, HEIGHT))
            flash_surf.fill(WHITE)
            flash_surf.set_alpha(int(self.flash_timer * 600))
            surface.blit(flash_surf, (0,0))
            
        # UI overlay alpha
        if self.alpha < 255:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.fill((0,0,0))
            overlay.set_alpha(255 - int(self.alpha))
            surface.blit(overlay, (0,0))
