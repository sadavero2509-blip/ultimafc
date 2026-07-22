import pygame
import math
import random
from settings import *

class PresentationScene:
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        
        self.team = self.context.get("team")
        self.player_name = self.context.get("player_name", "Jugador")
        self.is_manager = self.context.get("is_manager", False)
        self.number = self.context.get("number", 10)
        self.next_scene = self.context.get("next_scene")
        
        if not self.team:
            from data.teams import TEAMS
            self.team = TEAMS[0]
            
        self.award_name = self.context.get("award_name")
        self.timer = 0
        self.state = "award_photo" if self.award_name else "photo"
        
        # Interactive press state
        self.current_q = 0
        self.text_revealed = 0
        self.selected_ans_idx = 0
        self.ans_selected = False
        self.flash_timer = 0
        
        # Obtener ídolo del jugador si existe
        self.idol = None
        if not self.is_manager:
            from data.career_manager import career_manager
            if career_manager.active and career_manager.career_player and career_manager.career_player.get("idol") and career_manager.career_player["idol"] != "Nadie":
                self.idol = career_manager.career_player["idol"]
        
        self.questions = self._generate_questions()
        
        try:
            self.font_title = pygame.font.SysFont("Impact", 60)
            self.font_subtitle = pygame.font.SysFont("Arial", 30, bold=True)
            self.font_q = pygame.font.SysFont("Arial", 22, italic=True)
            self.font_a = pygame.font.SysFont("Arial", 26, bold=True)
            self.font_hint = pygame.font.SysFont("Arial", 16)
        except:
            self.font_title = pygame.font.Font(None, 60)
            self.font_subtitle = pygame.font.Font(None, 30)
            self.font_q = pygame.font.Font(None, 22)
            self.font_a = pygame.font.Font(None, 26)
            self.font_hint = pygame.font.Font(None, 16)

    def _generate_questions(self):
        pool = []
        from data.career_manager import career_manager
        is_first_debut = career_manager.career_stats["matches"] == 0
        
        region_name = "el continente"
        if career_manager.league_id in ["ES", "EN", "IT", "DE", "FR", "PT"]: region_name = "Europa"
        elif career_manager.league_id in ["AR", "BR", "CO"]: region_name = "Sudamérica"

        if self.award_name:
            # (Keep award logic similar)
            if "Oro" in self.award_name:
                pool = [
                    {"q": f"¡Felicidades por el {self.award_name}! ¿Es el mejor día de tu vida?", "ans": [{"t": "Sin duda.", "res": "Es el mayor honor que un futbolista puede recibir. Un sueño total."}, {"t": "Muy especial.", "res": "Es un momento único, pero mañana toca seguir trabajando duro."}, {"t": "Para mi familia.", "res": "Más que por mí, me alegro por los que estuvieron en las malas."}]},
                    {"q": "¿Crees que con esto ya tocaste el techo de tu carrera?", "ans": [{"t": "Para nada.", "res": "Este premio solo me da más hambre para seguir mejorando cada día."}, {"t": "He cumplido un ciclo.", "res": "Siento que he llegado a la cima, pero quiero mantenerme ahí."}, {"t": "Hay más metas.", "res": "Falta la Champions y el Mundial. Esto es solo el principio."}]},
                    {"q": "¿A quién agradeces este reconocimiento?", "ans": [{"t": "A mis compañeros.", "res": "Sin ellos no hubiera metido ni la mitad de los goles."}, {"t": "A la afición.", "res": "Su apoyo me motiva a dejarme la piel en el campo cada domingo."}, {"t": "A mi esfuerzo.", "res": "He trabajado más que nadie para estar hoy en este estrado."}]}
                ]
            elif "Joven" in self.award_name or "Golden Boy" in self.award_name:
                pool = [
                    {"q": "Ganador del Golden Boy... El futuro es el presente. ¿Cómo te sientes?", "ans": [{"t": "Pies en la tierra.", "res": "Es emocionante, pero queda muchísimo camino por recorrer. El trabajo duro apenas empieza."}, {"t": "Soy el mejor.", "res": "Trabajo para ser el número uno y este premio lo confirma. Vengo a marcar una época."}, {"t": "Gracias al club.", "res": "Sin la confianza de este equipo no estaría hoy aquí. Este premio es de mis compañeros."}]},
                    {"q": "¿Sientes presión por ser considerado la gran promesa del fútbol mundial?", "ans": [{"t": "Es un privilegio.", "res": "La presión es un privilegio. Me motiva a demostrar por qué estoy en este lugar."}, {"t": "No leo la prensa.", "res": "Solo me enfoco en el balón y en lo que me pide el míster. Los elogios son pasajeros."}, {"t": "Poco a poco.", "res": "Aún soy joven, no hay que cargarme de demasiadas expectativas. Quiero disfrutar del fútbol."}]},
                    {"q": "¿Cuál es tu próximo objetivo?", "ans": [{"t": "Ganar la Liga.", "res": "Los premios individuales están bien, pero quiero levantar trofeos con el equipo."}, {"t": "Seguir creciendo.", "res": "Mi meta es mejorar mis números de la temporada pasada y ser más decisivo."}, {"t": "Llegar a la selección.", "res": "Representar a mi país es lo máximo. Trabajaré para que el seleccionador me llame."}]}
                ]
            else:
                pool = [
                    {"q": f"¡Ganador del {self.award_name}! ¿Cuál es el secreto de tu éxito?", "ans": [{"t": "Disciplina.", "res": "No hay magia, solo sudor y constancia cada entrenamiento. La disciplina vence al talento."}, {"t": "Mentalidad.", "res": "Nunca dar un balón por perdido es lo que marca la diferencia en la élite."}, {"t": "Talento puro.", "res": "Nací con este don y trato de perfeccionarlo día tras día. Amo este deporte."}]},
                    {"q": "¿Es este el punto más alto de tu carrera profesional?", "ans": [{"t": "Solo el inicio.", "res": "Tengo hambre de más. Quiero que este sea el primero de muchos éxitos."}, {"t": "Un sueño hecho realidad.", "res": "Mirando atrás, todo el sacrificio ha valido la pena por este momento."}, {"t": "Lo colectivo importa.", "res": "Cambiaría este trofeo individual por un título con mi equipo sin dudarlo."}]}
                ]
        elif self.is_manager:
            pool = [
                {"q": f"¿Qué significa para usted dirigir a una institución como el {self.team['name']}?", "ans": [{"t": "Un honor.", "res": "Es una de las instituciones más grandes del mundo. Vengo a ganar títulos y hacer historia."}, {"t": "Un reto.", "res": "Sé que las expectativas son altas, pero estamos listos para el desafío táctico."}, {"t": "Un sueño.", "res": "Siempre quise estar en este banquillo desde que era jugador. Hoy se hace realidad."}]},
                {"q": "¿Qué estilo de juego piensa implementar en sus primeras semanas?", "ans": [{"t": "Fútbol Total.", "res": "Quiero un equipo que asfixie al rival, tenga la posesión y busque siempre el arco."}, {"t": "Solidez defensiva.", "res": "Lo importante es el equilibrio. Si mantenemos el arco a cero, las victorias llegarán."}, {"t": "Contragolpe letal.", "res": "Presión alta y transiciones rápidas. Quiero que seamos un rayo en el campo."}]},
                {"q": "¿Qué mensaje le envía a la afición que duda de su proyecto?", "ans": [{"t": "Paciencia y fe.", "res": "Los grandes cambios llevan tiempo. Los resultados hablarán por sí solos en el césped."}, {"t": "Compromiso total.", "res": "Trabajaré 24 horas al día para devolver a este club al lugar que se merece."}, {"t": "Fútbol vistoso.", "res": "Vengan al estadio, se van a divertir con lo que este equipo va a proponer."}]},
                {"q": "¿Habrá fichajes pronto?", "ans": [{"t": "Estamos mirando.", "res": "El mercado es largo. Si hay una oportunidad que mejore lo que tenemos, la aprovecharemos."}, {"t": "Confío en el grupo.", "res": "Tenemos una plantilla excelente. Mi trabajo es sacar el máximo rendimiento de ellos."}, {"t": "Buscamos perfiles.", "res": "Falta un par de piezas para que el engranaje sea perfecto. La directiva está en ello."}]}
            ]
        elif is_first_debut:
            pool = [
                {"q": f"Hoy es un día histórico. Tu primer contrato profesional con el {self.team['name']}. ¿Qué sientes?", "ans": [{"t": "Es increíble.", "res": "He trabajado desde niño para este momento. Ver mi nombre en esta camiseta es un sueño."}, {"t": "Responsabilidad.", "res": "Soy joven, pero sé lo que representa este club. Vengo a aprender y a darlo todo."}, {"t": "Hambre de gloria.", "res": "Esto es solo el inicio. Quiero devolverle al club la confianza con goles y títulos."}]},
                {"q": "¿Cuál es tu meta para esta primera temporada como profesional?", "ans": [{"t": "Aprender.", "res": "Quiero absorber todo de los veteranos y ganarme un puesto en el equipo."}, {"t": "Debutar pronto.", "res": "Mi único objetivo es pisar el césped y demostrarle al míster que puede contar conmigo."}, {"t": "Ser decisivo.", "res": "A pesar de mi edad, quiero ser una pieza clave y ayudar al equipo a ganar."}]},
                {"q": "La afición está expectante con tu llegada. ¿Qué pueden esperar de ti?", "ans": [{"t": "Sacrificio.", "res": "No daré un balón por perdido. Sudaré la camiseta en cada entrenamiento y partido."}, {"t": "Alegría.", "res": "Quiero que la gente se divierta viéndome jugar. Vengo a disfrutar del fútbol."}, {"t": "Goles.", "res": "Como delantero, mi trabajo es mandarla a guardar, y eso es lo que haré."}]}
            ]
        else: # Fichaje Jugador (Cambio de club)
            pool = [
                {"q": f"¿Cómo te sientes al vestir por fin la mítica camiseta del {self.team['name']}?", "ans": [{"t": "Cumplí un sueño.", "res": "Llevo esperando esta oportunidad desde que pateaba el balón en el barrio."}, {"t": "Paso adelante.", "res": "Es el salto de calidad que mi carrera necesitaba. Estoy en el mejor lugar posible."}, {"t": "Con hambre.", "res": "Vengo a aportar goles, sacrificio y ayudar al club a levantar trofeos pronto."}]},
                {"q": f"Llevarás el dorsal {self.number}. ¿Eres consciente de la responsabilidad?", "ans": [{"t": "Es historia.", "res": "Sé quiénes lo usaron antes y es un orgullo portar este legado en mi espalda."}, {"t": "Solo un número.", "res": "Lo importante es lo que rinda dentro del campo, el dorsal no juega solo."}, {"t": "Motivación extra.", "res": "Me hace sentir una pieza clave del proyecto y voy a demostrar que doy la talla."}]},
                {"q": "¿Por qué elegiste este destino entre tantas ofertas?", "ans": [{"t": "El proyecto.", "res": f"Había ofertas, pero el proyecto deportivo de este club es inigualable en {region_name}."}, {"t": "Por sentimiento.", "res": "Mi corazón siempre fue de este color. No podía decir que no a esta llamada."}, {"t": "Por el DT.", "res": "Hablé con el míster y su visión del fútbol me convenció de que este es mi sitio."}]},
                {"q": "¿Cuándo estarás listo para debutar?", "ans": [{"t": "Mañana mismo.", "res": "He estado entrenando duro por mi cuenta. Si el míster quiere, juego mañana."}, {"t": "Poco a poco.", "res": "Necesito unos días para conocer a mis compañeros, pero estoy físicamente al 100%."}, {"t": "Ansioso.", "res": "Espero que en el próximo partido ya pueda pisar el césped y sentir a la afición."}]}
            ]

        if self.idol:
            pool.append({"q": f"Muchos te comparan con {self.idol}. ¿Te consideras su heredero?", "ans": [{"t": "Es mi referente.", "res": f"Crecí viéndolo jugar. Es un honor la comparación, pero quiero hacer mi propio nombre."}, {"t": "Incomparable.", "res": f"Lo que hizo {self.idol} es único. Yo vengo a aportar mi propio estilo al equipo."}, {"t": "Aprendo de él.", "res": f"Trato de imitar sus movimientos, pero en el fútbol moderno hay que ser versátil."}]})

        if career_manager.career_stats.get("player_legacy") and self.is_manager:
            leg = career_manager.career_stats["player_legacy"]
            pool.append({"q": f"Muchos lo recuerdan como un gran {leg['pos']}. ¿Veremos eso en su equipo?", "ans": [{"t": "Totalmente.", "res": "Mi equipo jugará con el mismo ADN con el que yo jugaba."}, {"t": "Es distinto.", "res": "Como técnico veo cosas que como jugador no percibía."}, {"t": "Evolución.", "res": "He aprendido mucho y quiero mezclar mi garra con orden táctico."}]})

        random.shuffle(pool)
        final_q = pool[:3]
        final_q.append({"q": "Jefe de Prensa: Muchas gracias. Con esto cerramos la presentación.", "ans": [{"t": "¡Gracias!", "res": "¡Gracias a todos! ¡Nos vemos en el estadio!"}]})
        return final_q

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.state == "photo" and not self.is_manager:
                    if event.key in (pygame.K_UP, pygame.K_w):
                        self.number = min(99, self.number + 1)
                        from data.career_manager import career_manager
                        if career_manager.active and career_manager.career_player:
                            career_manager.career_player["num"] = self.number
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        self.number = max(1, self.number - 1)
                        from data.career_manager import career_manager
                        if career_manager.active and career_manager.career_player:
                            career_manager.career_player["num"] = self.number
                            
                if self.state in ("photo", "award_photo"):
                    if event.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_ESCAPE):
                        self.state = "press"; self.timer = 0
                elif self.state == "press":
                    if not self.ans_selected:
                        q_data = self.questions[self.current_q]
                        if event.key == pygame.K_UP: self.selected_ans_idx = (self.selected_ans_idx - 1) % len(q_data["ans"])
                        elif event.key == pygame.K_DOWN: self.selected_ans_idx = (self.selected_ans_idx + 1) % len(q_data["ans"])
                        elif event.key == pygame.K_RETURN: self.ans_selected = True; self.text_revealed = 0; self.timer = 0
                    else:
                        if event.key == pygame.K_RETURN:
                            if self.current_q < len(self.questions) - 1:
                                self.current_q += 1; self.text_revealed = 0; self.timer = 0; self.ans_selected = False; self.selected_ans_idx = 0
                            else: self._finish()

    def update(self, dt):
        self.timer += dt
        if self.state in ("photo", "award_photo"):
            if getattr(self, "flash_timer", 0) > 0: self.flash_timer -= dt
            elif random.random() < 0.1: self.flash_timer = 0.1
            if self.timer > 5.0: self.state = "press"; self.timer = 0; self.flash_timer = 0
        elif self.state == "press":
            self.text_revealed += dt * 40
            if getattr(self, "flash_timer", 0) > 0: self.flash_timer -= dt
            elif random.random() < 0.03: self.flash_timer = 0.05

    def _finish(self):
        if self.next_scene: self.manager.set_scene(self.next_scene)
        else:
            from scenes.career_hub import CareerHubScene
            self.manager.set_scene(CareerHubScene)

    def draw(self, surface):
        surface.fill((15, 15, 20))
        from data.teams import draw_badge, draw_uniform_preview
        bg_logo_surf = pygame.Surface((200, 200), pygame.SRCALPHA); draw_badge(bg_logo_surf, self.team, 100, 100, size=80); bg_logo_surf.set_alpha(30)
        for x in range(0, WIDTH, 200):
            for y in range(0, HEIGHT, 200): surface.blit(bg_logo_surf, (x, y))
                
        if self.state == "award_photo":
            title = self.font_title.render("GALA DE PREMIOS", True, (255, 215, 0)); surface.blit(title, (WIDTH//2 - title.get_width()//2, 50))
            sub = self.font_subtitle.render(f"¡GANADOR: {self.award_name.upper()}!", True, WHITE); surface.blit(sub, (WIDTH//2 - sub.get_width()//2, 120))
            cy = HEIGHT // 2 + 50; draw_badge(surface, self.team, WIDTH//2 - 150, cy, size=150)
            trophy = pygame.font.SysFont("Arial", 48, bold=True) if pygame.font.get_init() else pygame.font.Font(None, 48)
            ts = trophy.render("[COPA]", True, (255, 215, 0)); surface.blit(ts, (WIDTH//2 + 150 - ts.get_width()//2, cy - ts.get_height()//2))
            name_lbl = self.font_title.render(self.player_name, True, WHITE); surface.blit(name_lbl, (WIDTH//2 - name_lbl.get_width()//2, HEIGHT - 120))
        elif self.state == "photo":
            title = self.font_title.render("PRESENTACIÓN OFICIAL", True, UI_ACCENT); surface.blit(title, (WIDTH//2 - title.get_width()//2, 50))
            sub = self.font_subtitle.render(f"¡BIENVENIDO AL {self.team['name'].upper()}!", True, WHITE); surface.blit(sub, (WIDTH//2 - sub.get_width()//2, 120))
            cy = HEIGHT // 2 + 50; draw_badge(surface, self.team, WIDTH//2 - 150, cy, size=150)
            if not self.is_manager:
                shirt_rect = pygame.Rect(0, 0, 180, 240); shirt_rect.center = (WIDTH//2 + 150, cy); pygame.draw.rect(surface, (30, 30, 35), shirt_rect, border_radius=15); pygame.draw.rect(surface, UI_ACCENT, shirt_rect, 3, border_radius=15)
                from entities.player_appearance import draw_player_avatar, get_player_appearance
                p_app = None
                from data.career_manager import career_manager
                if career_manager.active and career_manager.career_player:
                    p_app = career_manager.career_player.get("custom_appearance") or get_player_appearance(career_manager.career_player)
                else:
                    p_app = get_player_appearance({"name": self.player_name, "num": self.number, "pos": "ST"})
                draw_player_avatar(surface, shirt_rect.centerx, shirt_rect.centery - 10, p_app, scale=2.8, team_color=self.team.get("primary", (0, 200, 150)), secondary_color=self.team.get("secondary", (255, 255, 255)), number=self.number)
                hint_lbl = self.font_hint.render("▲/▼ o W/S: Pedir cambio de Dorsal", True, GOLD)
                surface.blit(hint_lbl, (shirt_rect.centerx - hint_lbl.get_width()//2, shirt_rect.bottom + 15))
            name_lbl = self.font_title.render(self.player_name, True, YELLOW); surface.blit(name_lbl, (WIDTH//2 - name_lbl.get_width()//2, HEIGHT - 120))
        elif self.state == "press":
            title = self.font_subtitle.render("RUEDA DE PRENSA", True, UI_ACCENT); surface.blit(title, (WIDTH//2 - title.get_width()//2, 40)); draw_badge(surface, self.team, WIDTH//2, 160, size=100)
            q_data = self.questions[self.current_q]; q_panel = pygame.Rect(WIDTH//2 - 400, 240, 800, 80); pygame.draw.rect(surface, (30, 35, 50), q_panel, border_radius=10); pygame.draw.rect(surface, UI_ACCENT, q_panel, 2, border_radius=10)
            q_text = self.font_q.render(f"P: {q_data['q']}", True, WHITE); surface.blit(q_text, (q_panel.left + 25, q_panel.centery - q_text.get_height()//2))
            if not self.ans_selected:
                for i, ans in enumerate(q_data["ans"]):
                    y = 350 + i * 65; rect = pygame.Rect(WIDTH//2 - 350, y, 700, 55); is_sel = (self.selected_ans_idx == i); bg_col = (45, 55, 80) if is_sel else (35, 40, 55); border_col = GOLD if is_sel else (70, 75, 90); pygame.draw.rect(surface, bg_col, rect, border_radius=8); pygame.draw.rect(surface, border_col, rect, 2 if is_sel else 1, border_radius=8)
                    txt = self.font_subtitle.render(ans["t"], True, WHITE if is_sel else (180, 180, 200)); surface.blit(txt, (rect.centerx - txt.get_width()//2, rect.centery - txt.get_height()//2))
            else:
                ans_data = q_data["ans"][self.selected_ans_idx]
                ans_text = f"{self.player_name}: {ans_data['res']}"
                res_panel = pygame.Rect(WIDTH//2 - 400, 350, 800, 150)
                pygame.draw.rect(surface, (20, 20, 25, 220), res_panel, border_radius=15)
                pygame.draw.rect(surface, GOLD, res_panel, 2, border_radius=15)
                
                chars_to_show = int(self.text_revealed)
                if chars_to_show > len(ans_text):
                    chars_to_show = len(ans_text)
                
                words = ans_text[:chars_to_show].split(' ')
                lines = []
                curr_line = ""
                for w in words:
                    test_line = curr_line + w + " "
                    if self.font_a.size(test_line)[0] < 750:
                        curr_line = test_line
                    else:
                        lines.append(curr_line)
                        curr_line = w + " "
                lines.append(curr_line)
                
                for idx, line in enumerate(lines):
                    a_surf = self.font_a.render(line, True, WHITE)
                    surface.blit(a_surf, (res_panel.left + 25, res_panel.top + 30 + idx * 35))
                
                if chars_to_show >= len(ans_text):
                    h_font = pygame.font.SysFont("Arial", 14, bold=True) if pygame.font.get_init() else pygame.font.Font(None, 14)
                    h_surf = h_font.render("PRESIONA ENTER PARA CONTINUAR", True, GOLD)
                    surface.blit(h_surf, (res_panel.right - h_surf.get_width() - 20, res_panel.bottom - 25))
        if getattr(self, "flash_timer", 0) > 0:
            flash_surf = pygame.Surface((WIDTH, HEIGHT)); flash_surf.fill(WHITE); flash_surf.set_alpha(150); surface.blit(flash_surf, (0,0))
        hint = self.font_hint.render("Presiona SPACE para continuar", True, (150, 150, 150)); surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 30))
