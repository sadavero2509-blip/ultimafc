import pygame
import math
import random

class CardRenderer:
    def __init__(self):
        self.card_w = 180
        self.card_h = 270
        self.colors = {
            "gold_bg": (218, 165, 32),
            "gold_border": (255, 215, 0),
            "silver_bg": (150, 150, 160),
            "silver_border": (200, 200, 210),
            "bronze_bg": (120, 80, 60),
            "bronze_border": (160, 120, 100),
            "legend_bg": (240, 240, 240),
            "legend_border": (180, 180, 180),
            "text": (20, 20, 20),
            "sub_text": (60, 60, 60)
        }
        self.team_to_nat = {
            "STE": "ES", "COR": "ES", "ATM": "ES", "SEV": "ES", "VLC": "ES", "VLR": "ES", "RSO": "ES", "BET": "ES", "BIL": "ES",
            "UDV": "EN", "ALB": "EN", "ARS": "EN", "LIV": "EN", "CHE": "EN", "TOT": "EN", "WHU": "EN", "AVL": "EN", "NEW": "EN",
            "ROS": "IT", "AZZ": "IT", "JUV": "IT", "NAP": "IT", "ROM": "IT", "LAZ": "IT", "FIO": "IT", "ATA": "IT", "BOL": "IT", "BOL_IT": "IT", "TOR": "IT", "GEN": "IT", "EMP": "IT", "VER": "IT", "MONZ": "IT", "UDI": "IT", "LEC": "IT", "CAG": "IT", "PARM": "IT", "VEN_IT": "IT", "COM": "IT",
            "AJT": "DE", "BSG": "DE", "LEV": "DE", "RBL": "DE", "SGE": "DE", "BMG": "DE", "WOB": "DE", "HOF": "DE", "UNI": "DE", "STU": "DE",
            "OLY": "FR", "MAR": "FR", "LYO": "FR", "MON": "FR", "LIL": "FR", "NIC": "FR", "REN": "FR", "LEN": "FR", "RRE": "FR",
            "ARG": "AR", "ESP": "ES", "FRA": "FR", "BRA": "BR", "ENG": "EN", "GER": "DE", "ITA": "IT", "POR": "PT", "COL": "CO", "JPN": "JP"
        }

    def render_card(self, surface, player, x, y, scale=1.0):
        is_legend = player.get("is_legend", False)
        card_type = player.get("card_type", "NORMAL")
        
        # Determinar rareza si no está explícita
        rarity = player.get("rarity")
        if not rarity and not is_legend:
            ovr = player.get("ovr", 75)
            if ovr >= 75: rarity = "ORO"
            elif ovr >= 65: rarity = "PLATA"
            else: rarity = "BRONCE"

        if is_legend or rarity == "LEYENDA":
            bg_color = self.colors["legend_bg"]
            border_color = self.colors["legend_border"]
            text_color = self.colors["text"]
        elif rarity == "PLATA":
            bg_color = self.colors["silver_bg"]
            border_color = self.colors["silver_border"]
            text_color = self.colors["text"]
        elif rarity == "BRONCE":
            bg_color = self.colors["bronze_bg"]
            border_color = self.colors["bronze_border"]
            text_color = (245, 245, 245) # Blanco para contraste en Bronce
        else: # ORO
            bg_color = self.colors["gold_bg"]
            border_color = self.colors["gold_border"]
            text_color = self.colors["text"]

        # Especial: Carta Mundial 2026
        if card_type == "WORLDCUP":
            # Diseño Esmeralda Premium (Substituyendo los 3 bloques)
            bg_color = (0, 60, 40)   # Esmeralda profundo
            border_color = (200, 180, 100) # Oro suave
            text_color = (255, 255, 255)
        elif card_type == "WORLDCUP_LEGEND":
            bg_color = (240, 245, 255) # Mármol Ártico
            border_color = (255, 215, 0) # Oro Premium
            text_color = (20, 20, 50)
        elif card_type == "FOUNDER":
            bg_color = (15, 15, 25)      # Negro Mate / Oscuro
            border_color = (255, 215, 0) # Oro
            text_color = (255, 255, 255)
        elif card_type == "EVO_PROGRESS":
            bg_color = (20, 80, 60)       # Teal oscuro
            border_color = (0, 255, 150)  # Verde neón
            text_color = (255, 255, 255)
        # --- Diseños únicos por evolución completada ---
        elif card_type == "EVO_SPEED":
            bg_color = (10, 20, 60)        # Azul marino profundo
            border_color = (80, 180, 255)  # Azul eléctrico
            text_color = (200, 235, 255)
        elif card_type == "EVO_MIDFIELD":
            bg_color = (20, 25, 45)        # Pizarra oscura
            border_color = (160, 130, 255) # Violeta suave
            text_color = (225, 215, 255)
        elif card_type == "EVO_STRIKER":
            bg_color = (55, 10, 15)        # Rojo sangre oscuro
            border_color = (255, 80, 60)   # Rojo fuego
            text_color = (255, 220, 200)
        elif card_type == "RETRO_HERITAGE":
            bg_color = (30, 10, 50)        # Púrpura retro profundo
            border_color = (255, 215, 0)   # Oro brillante
            text_color = (255, 255, 255)
        elif card_type == "FLASHBACK":
            bg_color = (20, 20, 45)        # Índigo crepuscular (Vibras al pasado)
            border_color = (200, 160, 50)  # Oro envejecido
            text_color = (245, 245, 220)   # Crema/Hueso para contraste vintage

        # Escalar dimensiones
        w = int(self.card_w * scale)
        h = int(self.card_h * scale)
        
        # Rectángulo base
        card_rect = pygame.Rect(x, y, w, h)
        
        # Dibujar Sombra
        shadow_rect = card_rect.move(4, 4)
        pygame.draw.rect(surface, (0, 0, 0, 100), shadow_rect, border_radius=int(12 * scale))
        
        # Dibujar Fondo
        pygame.draw.rect(surface, bg_color, card_rect, border_radius=int(12 * scale))

        # --- ACENTOS ESPECIALES DE DISEÑO ---
        if card_type == "WORLDCUP":
            # Dibujar degradado diagonal (Verde Esmeralda a Azul Profundo)
            for i in range(w):
                ratio = i / w
                col = (
                    0,
                    int(80 * (1-ratio) + 20 * ratio),
                    int(50 * (1-ratio) + 120 * ratio)
                )
                # Margen de 4px para no salirse de los bordes redondeados
                pygame.draw.line(surface, col, (x+i, y+4), (x+i, y+h-6))
            
            # BORDE ROJO GRUESO (CAN)
            pygame.draw.rect(surface, (220, 20, 40), card_rect, max(1, int(6*scale)), border_radius=int(12*scale))

        elif card_type == "WORLDCUP_LEGEND":
            # Franja Tricolor Igualitaria (MEX-CAN-USA) - Sin mezclas de color
            bar_h = int(12*scale)
            bar_y = y + h - int(15*scale)
            bw = (w - int(6*scale)) // 3
            bx = x + int(3*scale)
            pygame.draw.rect(surface, (0, 104, 71), (bx, bar_y, bw, bar_h)) # Verde
            pygame.draw.rect(surface, (191, 10, 48), (bx + bw, bar_y, bw, bar_h)) # Rojo
            pygame.draw.rect(surface, (0, 40, 104), (bx + bw*2, bar_y, w - int(6*scale) - bw*2, bar_h)) # Azul
            
            # Línea dorada de separación
            pygame.draw.line(surface, (255, 215, 0), (bx, bar_y), (bx + w - int(6*scale), bar_y), 1)

            # Estrella dorada de leyenda (arriba a la derecha)
            self._draw_star(surface, x + w - int(25*scale), y + int(25*scale), int(8*scale))

        
        elif card_type == "FOUNDER":
             # Diseño elegante: Borde dorado y franja vertical
             pygame.draw.rect(surface, (255, 215, 0), card_rect, max(1, int(3*scale)), border_radius=int(12*scale))
             pygame.draw.rect(surface, (255, 215, 0), (x+w-int(10*scale), y+int(40*scale), max(1, int(4*scale)), h-int(100*scale)))
             # Texto "FOUNDER" vertical sutil
             f_font = pygame.font.SysFont("Arial", int(14*scale), bold=True)
             f_surf = f_font.render("FOUNDER EDITION", True, (255, 215, 0))
             f_surf = pygame.transform.rotate(f_surf, 90)
             surface.blit(f_surf, (x+w-int(12*scale), y+int(50*scale)))
        
        elif card_type == "EVO_PROGRESS":
             # Borde interior neón pulsante
             inner_rect = card_rect.inflate(-int(16*scale), -int(16*scale))
             pygame.draw.rect(surface, (0, 255, 150), inner_rect, max(1, int(1*scale)), border_radius=int(6*scale))
        elif card_type == "EVO_SPEED":
             # Franja diagonal azul eléctrica en la parte superior
             pts = [(x, y + int(40*scale)), (x + w, y + int(20*scale)), (x + w, y), (x, y)]
             pygame.draw.polygon(surface, (80, 180, 255, 80), pts)
             # Línea fina en la base
             pygame.draw.rect(surface, (80, 180, 255), (x, y + h - int(6*scale), w, int(6*scale)), border_bottom_left_radius=int(12*scale), border_bottom_right_radius=int(12*scale))
        elif card_type == "EVO_MIDFIELD":
             # Dos franjas horizontales violeta a ambos extremos
             pygame.draw.rect(surface, (160, 130, 255), (x, y, w, int(8*scale)), border_top_left_radius=int(12*scale), border_top_right_radius=int(12*scale))
             pygame.draw.rect(surface, (160, 130, 255), (x, y + h - int(8*scale), w, int(8*scale)), border_bottom_left_radius=int(12*scale), border_bottom_right_radius=int(12*scale))
             # Doble borde interior sutil
             inner = card_rect.inflate(-int(18*scale), -int(18*scale))
             pygame.draw.rect(surface, (120, 90, 220), inner, max(1, int(1*scale)), border_radius=int(5*scale))
        elif card_type == "EVO_STRIKER":
             # Banda diagonal roja en esquina superior derecha
             pts = [(x + w - int(60*scale), y), (x + w, y), (x + w, int(60*scale) + y)]
             pygame.draw.polygon(surface, (255, 80, 60), pts)
             # Acento en la base
             pygame.draw.rect(surface, (200, 40, 20), (x, y + h - int(10*scale), w, int(10*scale)), border_bottom_left_radius=int(12*scale), border_bottom_right_radius=int(12*scale))
        elif card_type == "RETRO_HERITAGE":
             # Doble borde interior
             inner = card_rect.inflate(-int(10*scale), -int(10*scale))
             pygame.draw.rect(surface, (255, 255, 255, 50), inner, max(1, int(1*scale)), border_radius=int(8*scale))
             # Acento neón cian/rosa en la base
             pygame.draw.rect(surface, (0, 255, 255), (x, y + h - int(12*scale), w, int(4*scale)))
             pygame.draw.rect(surface, (255, 0, 255), (x, y + h - int(8*scale), w, int(8*scale)), border_bottom_left_radius=int(12*scale), border_bottom_right_radius=int(12*scale))
        
        elif card_type == "FLASHBACK":
            # --- SIMBOLOGÍA DEL TIEMPO ---
            # Reloj central sutil
            clock_center = (x + w//2, y + h//2 - int(20*scale))
            pygame.draw.circle(surface, (255, 215, 0, 40), clock_center, int(40*scale), 2)
            # Manecillas (Líneas finas)
            pygame.draw.line(surface, (255, 215, 0, 60), clock_center, (clock_center[0], clock_center[1] - int(35*scale)), 2)
            pygame.draw.line(surface, (255, 215, 0, 60), clock_center, (clock_center[0] + int(25*scale), clock_center[1]), 2)
            
            # Flecha curva de retorno al pasado (esquina superior izquierda)
            pts_arrow = [(x+int(15*scale), y+int(40*scale)), (x+int(35*scale), y+int(25*scale)), (x+int(35*scale), y+int(55*scale))]
            pygame.draw.polygon(surface, (200, 160, 50, 100), pts_arrow)
            
            # Borde interior doble
            inner_f = card_rect.inflate(-int(12*scale), -int(12*scale))
            pygame.draw.rect(surface, (200, 160, 50, 80), inner_f, 1, border_radius=int(10*scale))
        
        # --- EFECTOS COMUNES ---
        # Solo aplicar brillo si NO es carta del mundial (para no lavar el degradado)
        if card_type != "WORLDCUP":
            for i in range(3):
                alpha = 25 - i * 8
                grad_rect = pygame.Rect(x + i, y + i, w - i*2, h // 3) # Solo un tercio superior
                grad_surf = pygame.Surface((grad_rect.width, grad_rect.height), pygame.SRCALPHA)
                pygame.draw.rect(grad_surf, (255, 255, 255, alpha), (0, 0, grad_rect.width, grad_rect.height), 
                                 border_top_left_radius=int(12*scale), border_top_right_radius=int(12*scale))
                surface.blit(grad_surf, grad_rect.topleft)

        # Borde Premium (Desactivado para Mundial ya que usa borde rojo grueso propio)
        if card_type != "WORLDCUP":
            b_width = max(1, int(5 * scale)) if card_type == "WORLDCUP_LEGEND" else max(1, int(3 * scale))
            pygame.draw.rect(surface, border_color, card_rect, b_width, border_radius=int(12 * scale))
        
        # --- DETALLES (Media, Posición, Nacionalidad) ---
        margin = int(12 * scale)
        detail_y = y + int(25 * scale)
        detail_x = x + int(18 * scale)
        
        # Fuentes (EXTREMO) - Aumentadas para claridad
        font_ovr = pygame.font.SysFont("Impact", int(60 * scale))
        font_pos = pygame.font.SysFont("Arial", int(32 * scale), bold=True)
        font_nat = pygame.font.SysFont("Arial", int(28 * scale), bold=True)
        
        # OVR
        ovr_val = player.get("ovr", 75)
        ovr_surf = font_ovr.render(str(ovr_val), True, text_color)
        surface.blit(ovr_surf, (detail_x, detail_y))
        
        # Posición
        pos_surf = font_pos.render(player.get("pos", "ST"), True, text_color)
        surface.blit(pos_surf, (detail_x, detail_y + int(65 * scale)))
        
        # Nacionalidad (Abreviatura)
        nat = player.get("nat")
        if not nat:
            team_id = player.get("team")
            nat = self.team_to_nat.get(team_id, "??")
            
        nat_surf = font_nat.render(str(nat).upper(), True, text_color)
        # Dibujar una pequeña sombra bajo el texto de nacionalidad para que resalte
        surface.blit(font_nat.render(str(nat).upper(), True, (0,0,0,100)), (detail_x + 1, detail_y + int(105 * scale) + 1))
        surface.blit(nat_surf, (detail_x, detail_y + int(105 * scale)))
        
        # --- NOMBRE ---
        # Tamaño máximo y contraste absoluto
        font_name = pygame.font.SysFont("Arial", int(26 * scale), bold=True)
        name_text = self._format_player_name(player).upper()
        
        # Placa para el nombre (más alta y opaca)
        plate_w = int(w * 0.95)
        plate_h = int(42 * scale)
        plate_rect = pygame.Rect(x + (w - plate_w)//2, y + h - int(60 * scale), plate_w, plate_h)
        
        # Fondo oscuro casi opaco
        plate_surf = pygame.Surface((plate_w, plate_h), pygame.SRCALPHA)
        pygame.draw.rect(plate_surf, (0, 0, 0, 230), (0, 0, plate_w, plate_h), border_radius=int(8*scale))
        surface.blit(plate_surf, plate_rect.topleft)
        
        # Borde blanco fino para la placa del nombre
        pygame.draw.rect(surface, (255, 255, 255, 100), plate_rect, 1, border_radius=int(8*scale))

        name_surf = font_name.render(name_text, True, (255, 255, 255))
        name_rect = name_surf.get_rect(center=plate_rect.center)
        surface.blit(name_surf, name_rect)

        # --- ESTADÍSTICAS (6 Columnas) ---
        # Solo mostrar stats si no es modo miniatura extremo
        if scale > 0.5:
            font_stats = pygame.font.SysFont("Arial", int(20 * scale), bold=True)
            stats_y = y + h - int(120 * scale)
            stats_x_left = x + int(25 * scale)
            stats_x_right = x + w - int(65 * scale)
            
            s = player.get("s", {})
            stat_list = [
                ("RIT", s.get("speed", 75), stats_x_left, stats_y),
                ("TIR", s.get("shot", 75), stats_x_left, stats_y + int(25 * scale)),
                ("PAS", s.get("passing", 75), stats_x_left, stats_y + int(50 * scale)),
                ("REG", s.get("dribbling", 75), stats_x_right, stats_y),
                ("DEF", s.get("defense", 75), stats_x_right, stats_y + int(25 * scale)),
                ("FIS", s.get("physical", 75), stats_x_right, stats_y + int(50 * scale))
            ]
            
            for label, val, sx, sy in stat_list:
                # Sombra sutil para legibilidad
                surface.blit(font_stats.render(f"{val} {label}", True, (0,0,0,80)), (sx+1, sy+1))
                surface.blit(font_stats.render(f"{val} {label}", True, text_color), (sx, sy))
            
            # Línea divisoria vertical entre stats
            pygame.draw.line(surface, text_color, (x + w//2, stats_y + int(5*scale)), (x + w//2, stats_y + int(60*scale)), 1)

        # --- INDICADORES: SBC Y UNTRADEABLE ---
        if player.get("is_sbc"):
            sbc_font = pygame.font.SysFont("Arial", int(14 * scale), bold=True)
            sbc_rect = pygame.Rect(x + w - int(45 * scale), y + int(115 * scale), int(35 * scale), int(18 * scale))
            pygame.draw.rect(surface, (0, 0, 0, 180), sbc_rect, border_radius=int(4*scale))
            sbc_surf = sbc_font.render("SBC", True, (255, 215, 0))
            surface.blit(sbc_surf, sbc_surf.get_rect(center=sbc_rect.center))

        if player.get("untradeable"):
            lock_size = int(12 * scale)
            lx, ly = x + int(15 * scale), y + h - int(80 * scale)
            # Dibujar un pequeño candado simbólico (Círculo + Rect)
            pygame.draw.circle(surface, text_color, (lx + lock_size//2, ly), lock_size//2, 1)
            pygame.draw.rect(surface, text_color, (lx, ly, lock_size, lock_size), border_radius=1)

        # --- IMAGEN/RETRATO GENÉRICO HUMANO ---
        is_legend = player.get("is_legend", False)
        
        # Colores de anatomía genérica
        skin_color = (240, 190, 150) # Tono de piel natural
        skin_shadow = (200, 150, 110)
        hair_color = (40, 30, 20)    # Cabello oscuro
        
        # Determinar rareza si no está explícita
        rarity = player.get("rarity")
        if not rarity and not is_legend:
            ovr = player.get("ovr", 75)
            if ovr >= 75: rarity = "ORO"
            elif ovr >= 65: rarity = "PLATA"
            else: rarity = "BRONCE"
            
        # Color de la camiseta basado en la rareza
        if is_legend: jersey_color = (255, 245, 210) # Blanco perlado
        elif rarity == "ORO": jersey_color = (210, 170, 40)
        elif rarity == "PLATA": jersey_color = (160, 160, 160)
        elif rarity == "BRONCE": jersey_color = (130, 90, 60)
        else: jersey_color = (200, 200, 220) # Blanco/Gris genérico
        
        jersey_shadow = (max(0, jersey_color[0]-40), max(0, jersey_color[1]-40), max(0, jersey_color[2]-40))

        cx = x + w // 2
        
        # 1. CUELLO Y HOMBROS
        head_y = y + int(45 * scale)
        shoulder_y = head_y + int(40 * scale)
        neck_w, neck_h = int(16 * scale), int(24 * scale)
        
        # Sombra profunda del cuello
        neck_rect = pygame.Rect(cx - neck_w//2, head_y + int(24*scale), neck_w, neck_h)
        pygame.draw.rect(surface, skin_shadow, neck_rect) 
        
        # 2. TORSO Y CAMISETA
        torso_base_y = y + h - int(55 * scale)
        torso_w_top = int(72 * scale)
        torso_w_bottom = int(94 * scale)
        
        torso_pts = [
            (cx - neck_w//2 - int(6*scale), shoulder_y),  # Cuello izq
            (cx - torso_w_top//2, shoulder_y + int(14*scale)), # Hombro izq
            (cx - torso_w_bottom//2, torso_base_y), # Base izq
            (cx + torso_w_bottom//2, torso_base_y), # Base der
            (cx + torso_w_top//2, shoulder_y + int(14*scale)), # Hombro der
            (cx + neck_w//2 + int(6*scale), shoulder_y) # Cuello der
        ]
        pygame.draw.polygon(surface, jersey_color, torso_pts)
        
        # Sombreado lateral de la camiseta para volumen
        jersey_side_pts = [
            (cx + torso_w_top//2 - int(6*scale), shoulder_y + int(14*scale)),
            (cx + torso_w_bottom//2 - int(10*scale), torso_base_y),
            (cx + torso_w_bottom//2, torso_base_y),
            (cx + torso_w_top//2, shoulder_y + int(14*scale))
        ]
        pygame.draw.polygon(surface, jersey_shadow, jersey_side_pts)

        # Detalle de la camiseta (Cuello en V profundo)
        v_neck_pts = [
            (cx - neck_w//2 - int(4*scale), shoulder_y),
            (cx + neck_w//2 + int(4*scale), shoulder_y),
            (cx, shoulder_y + int(18*scale))
        ]
        pygame.draw.polygon(surface, jersey_shadow, v_neck_pts)

        # 3. CABEZA Y ROSTRO
        head_w, head_h = int(34 * scale), int(46 * scale)
        
        # Orejas
        ear_w, ear_h = int(10 * scale), int(16 * scale)
        ear_y = head_y + int(18 * scale)
        pygame.draw.ellipse(surface, skin_shadow, (cx - head_w//2 - int(4*scale), ear_y, ear_w, ear_h)) # Izquierda
        pygame.draw.ellipse(surface, skin_shadow, (cx + head_w//2 - int(6*scale), ear_y, ear_w, ear_h)) # Derecha

        # Silueta base de la cabeza (sombra general)
        pygame.draw.ellipse(surface, skin_shadow, (cx - head_w//2, head_y, head_w, head_h))
        
        # Cara iluminada (dejando un margen izquierdo para sombra 3D)
        inner_head = pygame.Rect(cx - head_w//2 + int(2*scale), head_y + int(2*scale), head_w - int(6*scale), head_h - int(4*scale))
        pygame.draw.ellipse(surface, skin_color, inner_head)
        
        # Detalles faciales minimalistas (Cejas, Ojos, Nariz, Boca)
        # Cejas
        pygame.draw.line(surface, hair_color, (cx - int(10*scale), head_y + int(18*scale)), (cx - int(3*scale), head_y + int(18*scale)), max(1, int(2*scale)))
        pygame.draw.line(surface, hair_color, (cx + int(3*scale), head_y + int(18*scale)), (cx + int(10*scale), head_y + int(18*scale)), max(1, int(2*scale)))
        
        # Ojos (Sutiles sombras)
        pygame.draw.line(surface, skin_shadow, (cx - int(9*scale), head_y + int(21*scale)), (cx - int(4*scale), head_y + int(21*scale)), max(1, int(2*scale)))
        pygame.draw.line(surface, skin_shadow, (cx + int(4*scale), head_y + int(21*scale)), (cx + int(9*scale), head_y + int(21*scale)), max(1, int(2*scale)))

        # Nariz (Sombra lateral)
        pygame.draw.polygon(surface, skin_shadow, [
            (cx, head_y + int(20*scale)),
            (cx - int(3*scale), head_y + int(30*scale)),
            (cx + int(2*scale), head_y + int(31*scale))
        ])

        # Boca
        pygame.draw.line(surface, skin_shadow, (cx - int(6*scale), head_y + int(38*scale)), (cx + int(6*scale), head_y + int(38*scale)), max(1, int(2*scale)))

        # 4. CABELLO (Texturizado y amplio)
        # Base oscura (Volumen principal)
        hair_base = pygame.Rect(cx - head_w//2 - int(3*scale), head_y - int(6*scale), head_w + int(6*scale), int(22*scale))
        pygame.draw.ellipse(surface, hair_color, hair_base)
        
        # Brillo del cabello (Textura superior)
        hair_hl_color = (min(255, hair_color[0]+30), min(255, hair_color[1]+30), min(255, hair_color[2]+30))
        pygame.draw.ellipse(surface, hair_hl_color, (cx - head_w//2 + int(4*scale), head_y - int(4*scale), head_w - int(10*scale), int(10*scale)))

        # Patillas
        pygame.draw.rect(surface, hair_color, (cx - head_w//2 - int(2*scale), head_y + int(12*scale), int(6*scale), int(14*scale)))
        pygame.draw.rect(surface, hair_color, (cx + head_w//2 - int(4*scale), head_y + int(12*scale), int(6*scale), int(14*scale)))


    def _draw_star(self, surface, x, y, size, color=(255, 215, 0)):
        """Dibuja una estrella de 5 puntas decorativa."""
        points = []
        for i in range(10):
            angle = math.radians(i * 36 - 90)
            radius = size if i % 2 == 0 else size // 2
            points.append((x + radius * math.cos(angle), y + radius * math.sin(angle)))
        pygame.draw.polygon(surface, color, points)

    def _format_player_name(self, player):
        """Formatea el nombre para mostrarlo en la carta (Apellido único o apodo)."""
        name = player.get("name", "Jugador")
        parts = name.split()
        if len(parts) == 1:
            return name
            
        # Si el último término es un sufijo (Jr, Jr.oh, etc.), devolvemos el término anterior más el sufijo
        last_word = parts[-1].lower().rstrip('.')
        is_suffix = last_word in ('jr', 'jr.oh', 'jr.ih', 'jr.eh', 'jr.ah', 'ii', 'iii', 'iv')
        
        if is_suffix and len(parts) > 1:
            return f"{parts[-2]} {parts[-1]}"
            
        # Retorna solo el apellido/último nombre para estilo premium de carta única
        return parts[-1]

card_renderer = CardRenderer()
