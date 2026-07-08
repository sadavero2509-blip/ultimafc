import pygame
from settings import *
from data.career_manager import career_manager

class CareerProfileScene:
    def __init__(self, manager, context=None):
        self.manager = manager
        self.context = context or {}
        
        self.player = self.context.get("player", career_manager.career_player)
        self.team = self.context.get("team", career_manager.player_team)
        self.is_main_player = (self.player == career_manager.career_player)
        self.stats = career_manager.career_stats if self.is_main_player else {}
        
        try:
            self.font_huge = pygame.font.SysFont("Impact", 60)
            self.font_title = pygame.font.SysFont("Impact", 40)
            self.font_sub = pygame.font.SysFont("Arial", 24, bold=True)
            self.font_text = pygame.font.SysFont("Arial", 20)
            self.font_bold = pygame.font.SysFont("Arial", 20, bold=True)
            self.font_small = pygame.font.SysFont("Arial", 16)
        except:
            self.font_huge = pygame.font.Font(None, 60)
            self.font_title = pygame.font.Font(None, 40)
            self.font_sub = pygame.font.Font(None, 24)
            self.font_text = pygame.font.Font(None, 20)
            self.font_bold = pygame.font.Font(None, 20)
            self.font_small = pygame.font.Font(None, 16)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_SPACE):
                    if self.context.get("from_scene"):
                        self.manager.set_scene(self.context["from_scene"])
                    else:
                        from scenes.career_hub import CareerHubScene
                        self.manager.set_scene(CareerHubScene)

    def update(self, dt):
        pass

    def draw(self, surface):
        surface.fill((10, 15, 25))
        
        # --- HEADER BACKGROUND ---
        header_h = 180
        pygame.draw.rect(surface, (20, 30, 45), (0, 0, WIDTH, header_h))
        pygame.draw.rect(surface, UI_ACCENT, (0, header_h - 2, WIDTH, 2))
        
        # --- PLAYER IDENTITY (Left Side) ---
        name = self.player.get('name', 'Jugador')
        name_surf = self.font_huge.render(name.upper(), True, WHITE)
        surface.blit(name_surf, (40, 30))
        
        ovr = self.player.get('ovr', 50)
        color_ovr = (100, 255, 100) if ovr >= 85 else ((255, 215, 0) if ovr >= 75 else WHITE)
        ovr_txt = f"OVR {ovr} | {self.player.get('pos', 'CM')}"
        ovr_surf = self.font_title.render(ovr_txt, True, color_ovr)
        surface.blit(ovr_surf, (40, 100))
        
        # --- TEAM INFO (Right Side of Header) ---
        team_name = self.team.get('name', 'Club')
        age = self.player.get('age', 18)
        nat = self.player.get('nat', '??')
        
        t_surf = self.font_sub.render(team_name.upper(), True, (200, 220, 255))
        surface.blit(t_surf, (WIDTH - t_surf.get_width() - 40, 40))
        
        inf_txt = f"{age} Años | Nac: {nat}"
        i_surf = self.font_text.render(inf_txt, True, UI_TEXT_DIM)
        surface.blit(i_surf, (WIDTH - i_surf.get_width() - 40, 80))
        
        val_txt = f"Valor: ${career_manager.calculate_player_value(self.player)}M"
        v_surf = self.font_bold.render(val_txt, True, (150, 255, 150))
        surface.blit(v_surf, (WIDTH - v_surf.get_width() - 40, 110))
        
        
        # --- CONTENT AREA ---
        content_y = header_h + 30
        
        # Left Column: MORAL E INFORME
        col_w = (WIDTH - 120) // 2
        
        pygame.draw.rect(surface, (20, 25, 40), (40, content_y, col_w, 250), border_radius=10)
        lbl1 = self.font_bold.render("ESTADO PSICOLÓGICO", True, UI_ACCENT)
        surface.blit(lbl1, (60, content_y + 20))
        
        # Calculate Morale
        if self.is_main_player:
            trust = self.stats.get('manager_trust', 50)
            pres = self.stats.get('prestige', 0) / 10.0
        else:
            # Fake morale for NPCs based on OVR vs Team Avg
            avg_ovr = self.team.get("stats", {}).get("speed", 75) # rough proxy
            diff = ovr - avg_ovr
            trust = 60 + diff
            pres = ovr - 10
            
        if trust >= 85 and pres >= 70:
            moral = "Excelente"
            m_col = (100, 255, 100)
            m_desc = "El jugador está en un estado de forma anímico increíble. Total sintonía con el DT."
        elif trust >= 60:
            moral = "Buena"
            m_col = (200, 255, 100)
            m_desc = "Muestra una actitud positiva en el vestuario."
        elif trust >= 40:
            moral = "Normal"
            m_col = WHITE
            m_desc = "Su moral es estable, aunque podría involucrarse más en el grupo."
        else:
            moral = "Baja / Descontento"
            m_col = (255, 100, 100)
            m_desc = "Está frustrado por su situación. La relación con el cuerpo técnico es tensa."
            
        ms1 = self.font_title.render(moral, True, m_col)
        surface.blit(ms1, (60, content_y + 60))
        
        md_surf = self.font_text.render(m_desc, True, UI_TEXT_DIM)
        surface.blit(md_surf, (60, content_y + 110))
        
        # Right Column: COMENTARIOS Y POTENCIAL
        rx = 40 + col_w + 40
        pygame.draw.rect(surface, (20, 25, 40), (rx, content_y, col_w, 250), border_radius=10)
        lbl2 = self.font_bold.render("INFORME DE EXPLORACIÓN", True, UI_ACCENT)
        surface.blit(lbl2, (rx + 20, content_y + 20))
        
        # Comments logic
        comments = []
        is_cap = self.stats.get("is_captain", False) if self.is_main_player else False
        pot = self.player.get('pot', ovr)
        
        is_wonderkid = (age <= 21 and pot >= 86 and pot - ovr >= 5)
        is_high_potential = (age <= 22 and pot >= 82 and pot - ovr >= 4)
        
        if self.is_main_player and self.stats.get('is_global_goat'):
            comments.append("El Dios del Fútbol. Literalmente el mejor de la historia.")
        elif self.is_main_player and self.stats.get(f"is_goat_{self.team.get('short', '')}"):
            comments.append("Leyenda viviente y máximo ídolo de la afición local.")
        elif ovr >= 88:
            if age >= 32:
                comments.append("Leyenda absoluta del fútbol mundial y referente veterano.")
            else:
                comments.append("Uno de los jugadores de clase mundial más respetados.")
        elif ovr >= 84:
            if age <= 23:
                comments.append("Una superestrella joven con un talento generacional.")
            elif age >= 33:
                comments.append("Veterano ilustre que sigue rindiendo al máximo nivel.")
            else:
                comments.append("Jugador fundamental y figura destacada en el panorama internacional.")
        elif ovr >= 80:
            if is_wonderkid or age <= 21:
                comments.append("Una de las promesas más brillantes, ya es una realidad en el campo.")
            elif age >= 32:
                comments.append("Veterano experimentado que aporta calidad y jerarquía.")
            else:
                comments.append("Un jugador clave y titular indiscutible en su posición.")
        elif is_wonderkid:
            comments.append("Una auténtica 'joya'. Los ojeadores predicen que será una estrella mundial.")
        elif is_high_potential:
            comments.append("Joven con muchísimo potencial. Si se desarrolla bien, llegará a la élite.")
        elif ovr >= 75:
            if age <= 20:
                comments.append("Joven en progresión constante, ganando peso en el primer equipo.")
            else:
                comments.append("Jugador sólido y pieza de confianza en la rotación del equipo.")
        elif ovr >= 70:
            if age <= 19:
                comments.append("Tiene talento y margen de mejora para llegar al primer nivel.")
            else:
                comments.append("Jugador de rol, siempre cumple cuando el míster se lo pide.")
        else:
            if age <= 19:
                if pot >= 78:
                    comments.append("Canterano muy prometedor, necesita minutos para explotar su talento.")
                else:
                    comments.append("Joven del filial buscando su oportunidad en el fútbol profesional.")
            else:
                comments.append("Jugador de banquillo, trabajando duro para demostrar su valía.")
                
        if is_cap:
            comments.append("El gran capitán y líder indiscutible del vestuario.")
            
        # Transfer status and Market rumors
        import random
        top_clubs = ["Real Coronas", "FC Stellaris", "Bayern AJT", "Zebra Torino", "United Devils", "AC Rossonero", "Merseyside Reds"]
        # Filtrar el club actual para que no haya rumores consigo mismo
        top_clubs = [c for c in top_clubs if c.lower() not in self.team.get("name", "").lower()]
        
        if self.is_main_player:
            offers_pending = self.stats.get('transfer_status')
            if offers_pending == 'transfer':
                comments.append("Ha solicitado salir. Su agente busca opciones en el mercado.")
            elif offers_pending == 'loan':
                comments.append("Busca salir cedido para ganar más protagonismo.")
        
        if self.player.get('transfer_listed'):
            comments.append("El club lo ha declarado transferible y le busca salida inmediata.")
        elif self.player.get('loan_listed'):
            comments.append("El club planea cederlo para que coja experiencia competitiva.")
        elif trust < 40 and ovr >= 80:
            random_club = random.choice(top_clubs) if top_clubs else "un gran club"
            comments.append(f"El {random_club} y otros equipos monitorean su tensa relación con el club.")
        elif is_wonderkid or (ovr >= 82 and age <= 21):
            random_club = random.choice(top_clubs) if top_clubs else "la élite europea"
            comments.append(f"Los ojeadores del {random_club} le siguen muy de cerca para un futuro fichaje.")
        elif ovr >= 86 and age <= 29:
            random_clubs = random.sample(top_clubs, 2) if len(top_clubs) >= 2 else ["clubes top", "la élite"]
            comments.append(f"{random_clubs[0]} y {random_clubs[1]} estarían preparando ofertas millonarias por él.")
            
        cy = content_y + 70
        for c in comments:
            # Wrap text manually if too long (simplified wrapping by splitting on '.' or hardcoding lengths)
            words = c.split(" ")
            line = ""
            for w in words:
                if self.font_text.size(line + w + " ")[0] < col_w - 40:
                    line += w + " "
                else:
                    cs = self.font_text.render(line, True, WHITE)
                    surface.blit(cs, (rx + 20, cy))
                    cy += 25
                    line = w + " "
            if line:
                cs = self.font_text.render(line, True, WHITE)
                surface.blit(cs, (rx + 20, cy))
                cy += 35

        # Footer
        hint = self.font_small.render("Presiona ESC, ENTER o ESPACIO para volver", True, UI_TEXT_DIM)
        surface.blit(hint, (WIDTH//2 - hint.get_width()//2, HEIGHT - 40))
