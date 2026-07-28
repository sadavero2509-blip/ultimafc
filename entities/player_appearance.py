import pygame
import math

# --- PALETAS EXPANDIDAS DE APARIENCIA ---

SKIN_PALETTE = [
    (255, 224, 196),  # 0: Clara / Teint Clair
    (245, 205, 172),  # 1: Melocotón / Piel Clara Cálida
    (225, 172, 132),  # 2: Trigueña Clara / Tan Soft
    (200, 140, 95),   # 3: Morena / Olivo
    (160, 102, 65),   # 4: Castaña / Canela
    (122, 78, 50),    # 5: Oscura Cálida
    (88, 52, 34),     # 6: Café Profundo / Espresso
    (58, 32, 20),     # 7: Ébano / Noche
]

HAIR_COLOR_PALETTE = [
    (20, 20, 20),     # 0: Negro Azabache
    (45, 32, 24),     # 1: Chocolate Oscuro
    (85, 52, 34),     # 2: Castaño Medio
    (145, 90, 50),    # 3: Castaño Claro / Avellana
    (225, 190, 105),  # 4: Rubio Dorado
    (240, 230, 190),  # 5: Rubio Platino
    (160, 55, 35),    # 6: Pelirrojo Cobrizo
    (200, 95, 40),    # 7: Pelirrojo / Ginger
    (110, 95, 80),    # 8: Rubio Ceniza / Grisáceo
    (185, 190, 195),  # 9: Plateado / Canoso
    (30, 140, 240),   # 10: Azul Neón (Teñido)
    (220, 50, 160),   # 11: Rosa Neón / Magenta (Teñido)
]

BOOT_PALETTE = [
    (50, 255, 50),    # 0: Verde Volt / Neón
    (255, 100, 0),    # 1: Naranja Hiper
    (0, 220, 255),    # 2: Cian Eléctrico
    (255, 220, 0),    # 3: Amarillo Solar
    (240, 240, 240),  # 4: Blanco Metalizado
    (230, 30, 90),    # 5: Rosa Fucsia / Neón
    (218, 165, 32),   # 6: Oro Puro / Dorado
    (200, 20, 20),    # 7: Rojo Carmesí
    (160, 30, 240),   # 8: Púrpura Neón
    (30, 30, 35),     # 9: Negro Mate / Clásico
    (190, 200, 210),  # 10: Plata Cromo
    (255, 120, 140),  # 11: Rojo Coral / Neón
]

# Mapeos demográficos por país/región
# SKIN_PALETTE: 0: Clara, 1: Melocotón, 2: Trigueña Clara, 3: Morena/Olivo, 4: Castaña/Canela, 5: Oscura Cálida, 6: Café Profundo, 7: Ébano
# HAIR_COLOR_PALETTE: 0: Negro, 1: Chocolate Oscuro, 2: Castaño Medio, 3: Castaño Claro, 4: Rubio Dorado, 5: Rubio Platino, 6: Pelirrojo Cobrizo, 7: Pelirrojo, 8: Rubio Ceniza, 9: Plateado, 10: Azul, 11: Rosa

NATIONALITY_APPEARANCE_WEIGHTS = {
    # Nórdicos / Europa del Norte
    "NO": {"skin": [0, 0, 0, 1, 1, 2], "hair": [2, 3, 4, 4, 5, 5, 6, 7, 8]},
    "SE": {"skin": [0, 0, 0, 1, 1, 2], "hair": [2, 3, 4, 4, 5, 5, 8]},
    "DK": {"skin": [0, 0, 0, 1, 1, 2], "hair": [2, 3, 4, 4, 5, 5, 8]},
    "FI": {"skin": [0, 0, 0, 1, 1], "hair": [3, 4, 4, 5, 5, 8]},
    "IS": {"skin": [0, 0, 0, 1, 1], "hair": [3, 4, 4, 5, 6, 7, 8]},

    # Europa Este / Centro
    "PL": {"skin": [0, 0, 1, 1, 2], "hair": [1, 2, 3, 4, 4, 8]},
    "UA": {"skin": [0, 0, 1, 1, 2], "hair": [1, 2, 3, 4, 8]},
    "HR": {"skin": [0, 1, 1, 2, 3], "hair": [0, 1, 2, 2, 3]},
    "CZ": {"skin": [0, 0, 1, 1, 2], "hair": [1, 2, 3, 4, 8]},
    "HU": {"skin": [0, 1, 1, 2], "hair": [1, 2, 3, 4]},
    "SK": {"skin": [0, 0, 1, 1, 2], "hair": [1, 2, 3, 4]},
    "RO": {"skin": [0, 1, 2, 3], "hair": [0, 1, 2, 3]},
    "RS": {"skin": [0, 1, 2, 3], "hair": [0, 1, 2, 3]},
    "GR": {"skin": [1, 2, 3, 3, 4], "hair": [0, 0, 1, 2]},
    "TR": {"skin": [1, 2, 3, 4], "hair": [0, 0, 1, 2]},

    # Europa Occidental
    "DE": {"skin": [0, 0, 1, 1, 2, 3, 5], "hair": [1, 2, 3, 4, 4, 5, 8]},
    "NL": {"skin": [0, 0, 1, 1, 2, 4, 6], "hair": [2, 3, 4, 4, 5, 8]},
    "BE": {"skin": [0, 0, 1, 1, 2, 3, 5], "hair": [1, 2, 3, 4, 5]},
    "CH": {"skin": [0, 0, 1, 1, 2, 3], "hair": [1, 2, 3, 4]},
    "AT": {"skin": [0, 0, 1, 1, 2], "hair": [1, 2, 3, 4, 5]},
    "EN": {"skin": [0, 0, 1, 1, 2, 4, 5, 6], "hair": [1, 2, 3, 4, 4, 6, 7]},
    "SC": {"skin": [0, 0, 0, 1], "hair": [2, 3, 4, 6, 6, 7, 7]},
    "WA": {"skin": [0, 0, 1, 1], "hair": [1, 2, 3, 4, 6, 7]},
    "IE": {"skin": [0, 0, 0, 1], "hair": [2, 3, 4, 6, 6, 7, 7]},

    # Sur de Europa / Mediterráneo
    "ES": {"skin": [1, 2, 2, 3, 3, 4], "hair": [0, 1, 1, 2, 3]},
    "IT": {"skin": [1, 2, 2, 3, 3, 4], "hair": [0, 1, 1, 2, 3]},
    "PT": {"skin": [1, 2, 2, 3, 3, 4, 5], "hair": [0, 0, 1, 2, 3]},

    # Francia (diversidad amplia histórica en fútbol)
    "FR": {"skin": [0, 1, 2, 3, 4, 5, 6, 7], "hair": [0, 0, 1, 1, 2, 3, 4]},

    # África Sub-Sahariana
    "SN": {"skin": [5, 6, 6, 7, 7, 7], "hair": [0, 0, 0, 0, 10, 11]},
    "NG": {"skin": [5, 6, 6, 7, 7, 7], "hair": [0, 0, 0, 0, 10, 11]},
    "CM": {"skin": [5, 6, 6, 7, 7, 7], "hair": [0, 0, 0, 0]},
    "GH": {"skin": [5, 6, 6, 7, 7, 7], "hair": [0, 0, 0, 0]},
    "CI": {"skin": [5, 6, 6, 7, 7, 7], "hair": [0, 0, 0, 0]},
    "CD": {"skin": [5, 6, 6, 7, 7, 7], "hair": [0, 0, 0, 0]},
    "GN": {"skin": [5, 6, 6, 7, 7, 7], "hair": [0, 0, 0, 0]},
    "CV": {"skin": [4, 5, 5, 6, 6, 7], "hair": [0, 0, 1]},
    "ZA": {"skin": [4, 5, 6, 6, 7], "hair": [0, 0, 1]},
    "AO": {"skin": [5, 6, 6, 7, 7], "hair": [0, 0, 0]},
    "ML": {"skin": [5, 6, 6, 7, 7], "hair": [0, 0, 0]},
    "BF": {"skin": [5, 6, 6, 7, 7], "hair": [0, 0, 0]},

    # Norte de África / Medio Oriente
    "MA": {"skin": [2, 3, 3, 4, 4, 5], "hair": [0, 0, 1, 2]},
    "EG": {"skin": [2, 3, 3, 4, 4, 5], "hair": [0, 0, 1, 2]},
    "DZ": {"skin": [2, 3, 3, 4, 4, 5], "hair": [0, 0, 1, 2]},
    "TN": {"skin": [2, 3, 3, 4, 4, 5], "hair": [0, 0, 1, 2]},
    "SA": {"skin": [2, 3, 3, 4, 5], "hair": [0, 0, 1]},
    "QA": {"skin": [2, 3, 4, 5], "hair": [0, 0, 1]},
    "IR": {"skin": [1, 2, 3, 3, 4], "hair": [0, 0, 1, 2]},
    "IQ": {"skin": [2, 3, 4], "hair": [0, 0, 1]},
    "AE": {"skin": [2, 3, 4, 5], "hair": [0, 0, 1]},

    # Asia Oriental / Sudeste
    "JP": {"skin": [0, 1, 1, 2], "hair": [0, 0, 0, 1, 10, 11]},
    "KR": {"skin": [0, 1, 1, 2], "hair": [0, 0, 0, 1]},
    "CN": {"skin": [0, 1, 1, 2], "hair": [0, 0, 0, 1]},
    "VN": {"skin": [1, 2, 3], "hair": [0, 0, 1]},
    "TH": {"skin": [1, 2, 3], "hair": [0, 0, 1]},

    # Sudamérica
    "AR": {"skin": [0, 1, 1, 2, 2, 3, 4], "hair": [0, 1, 1, 2, 3, 4]},
    "BR": {"skin": [1, 2, 3, 4, 5, 6, 7], "hair": [0, 0, 1, 1, 2, 3]},
    "CO": {"skin": [2, 3, 3, 4, 5, 6], "hair": [0, 0, 1, 1, 2]},
    "UY": {"skin": [0, 1, 1, 2, 3, 4], "hair": [0, 1, 1, 2, 3]},
    "CL": {"skin": [1, 2, 2, 3, 4], "hair": [0, 0, 1, 2]},
    "EC": {"skin": [2, 3, 4, 5, 6], "hair": [0, 0, 1, 2]},
    "PE": {"skin": [2, 3, 3, 4], "hair": [0, 0, 1]},
    "VE": {"skin": [1, 2, 3, 4, 5], "hair": [0, 0, 1, 2]},
    "BO": {"skin": [2, 3, 3, 4], "hair": [0, 0, 1]},
    "PY": {"skin": [1, 2, 2, 3, 4], "hair": [0, 0, 1, 2]},

    # Centroamérica / Caribe
    "MX": {"skin": [1, 2, 3, 3, 4], "hair": [0, 0, 1, 2]},
    "CR": {"skin": [1, 2, 3, 4, 5], "hair": [0, 0, 1, 2]},
    "PA": {"skin": [3, 4, 5, 6], "hair": [0, 0, 1]},
    "JM": {"skin": [5, 6, 6, 7, 7], "hair": [0, 0, 1]},
    "HT": {"skin": [5, 6, 7, 7], "hair": [0, 0, 1]},
    "CU": {"skin": [2, 3, 4, 5, 6], "hair": [0, 0, 1]},
    "DO": {"skin": [3, 4, 5, 6], "hair": [0, 0, 1]},

    # Norteamérica / Oceanía
    "US": {"skin": [0, 1, 1, 2, 3, 5, 6], "hair": [1, 2, 3, 4, 4, 5]},
    "CA": {"skin": [0, 1, 1, 2, 3, 5, 6], "hair": [1, 2, 3, 4, 5]},
    "AU": {"skin": [0, 1, 1, 2, 3], "hair": [1, 2, 3, 4, 5]},
    "NZ": {"skin": [1, 2, 3, 4, 5], "hair": [0, 1, 2, 3, 4]},
}

# Pool default para países no especificados
DEFAULT_APPEARANCE_WEIGHTS = {
    "skin": [0, 1, 2, 3, 4, 5, 6, 7],
    "hair": list(range(len(HAIR_COLOR_PALETTE)))
}

def get_player_appearance(player_data):
    """Calcula de forma determinista (hash de datos + nacionalidad) la apariencia del jugador."""
    name = str(player_data.get("name", ""))
    num = int(player_data.get("num", 1))
    pos = str(player_data.get("pos", ""))
    nat = str(player_data.get("nat", player_data.get("country_code", ""))).upper()

    # Hash determinista para que la apariencia no cambie entre frames
    h_str = f"{name}_{num}_{pos}_{nat}"
    h_val = 0
    for char in h_str:
        h_val = (h_val * 31 + ord(char)) & 0xFFFFFFFF

    weights = NATIONALITY_APPEARANCE_WEIGHTS.get(nat, DEFAULT_APPEARANCE_WEIGHTS)
    skin_pool = weights["skin"]
    hair_pool = weights["hair"]

    skin_idx = skin_pool[h_val % len(skin_pool)]
    hair_col_idx = hair_pool[(h_val // 7) % len(hair_pool)]
    hair_style_idx = (h_val // 13) % 8  # 8 estilos de cabello
    boot_l_idx = (h_val // 19) % len(BOOT_PALETTE)
    boot_r_idx = (h_val // 23) % len(BOOT_PALETTE)
    has_beard = ((h_val // 29) % 3 == 0)
    has_headband = ((h_val // 31) % 6 == 0)

    skin_color = SKIN_PALETTE[skin_idx]
    skin_shadow = (max(0, skin_color[0]-40), max(0, skin_color[1]-35), max(0, skin_color[2]-30))
    hair_color = HAIR_COLOR_PALETTE[hair_col_idx]
    boot_color_l = BOOT_PALETTE[boot_l_idx]
    boot_color_r = BOOT_PALETTE[boot_r_idx]

    return {
        "skin_color": skin_color,
        "skin_shadow": skin_shadow,
        "hair_color": hair_color,
        "hair_style": hair_style_idx,
        "boot_color_l": boot_color_l,
        "boot_color_r": boot_color_r,
        "has_beard": has_beard,
        "has_headband": has_headband
    }

def draw_procedural_hair(surface, hx, hy, head_r, hair_style, hair_color, aim_dir):
    """Dibuja los 8 estilos de cabello mejorados y realistas."""
    # Color de sombra para dar volumen
    shadow = (max(0, hair_color[0]-35), max(0, hair_color[1]-35), max(0, hair_color[2]-30))
    highlight = (min(255, hair_color[0]+40), min(255, hair_color[1]+40), min(255, hair_color[2]+35))
    r = head_r

    if hair_style == 0:
        # Style 0: Corte Clásico Corto (tipo futbolista europeo)
        # Capa base que cubre la parte superior de la cabeza
        pygame.draw.ellipse(surface, hair_color, (hx - r, hy - r - int(r*0.3), r*2, int(r*1.3)))
        # Sombra lateral para dar profundidad
        pygame.draw.ellipse(surface, shadow, (hx - r + 2, hy - r - int(r*0.2), r*2 - 4, int(r*0.9)))
        # Brillo sutil en la parte superior
        pygame.draw.arc(surface, highlight, (hx - int(r*0.5), hy - r - int(r*0.25), r, int(r*0.6)), 0.3, 2.8, 1)

    elif hair_style == 1:
        # Style 1: Afro Voluminoso (tipo Marcelo, Fellaini)
        afro_r = int(r * 1.45)
        # Capa exterior del afro - voluminosa
        pygame.draw.circle(surface, shadow, (hx, hy - int(r*0.3)), afro_r)
        pygame.draw.circle(surface, hair_color, (hx, hy - int(r*0.35)), afro_r - 1)
        # Textura rizada: pequeños arcos distribuidos
        for angle_step in range(0, 360, 30):
            import math
            rad = math.radians(angle_step)
            tx = hx + int(math.cos(rad) * (afro_r - 3))
            ty = hy - int(r*0.35) + int(math.sin(rad) * (afro_r - 3))
            pygame.draw.circle(surface, shadow, (tx, ty), max(1, int(r * 0.18)))
        # Brillo central superior
        pygame.draw.circle(surface, highlight, (hx - int(r*0.15), hy - r - int(r*0.2)), max(1, int(r*0.25)))

    elif hair_style == 2:
        # Style 2: Fade con Copete / Quiff (tipo Cristiano, Griezmann)
        # Lados rapados - tono más oscuro y pegado a la cabeza
        pygame.draw.arc(surface, shadow, (hx - r + 1, hy - r, r*2 - 2, r*2), 3.5, 5.9, max(1, int(r*0.15)))
        # Copete voluminoso arriba, peinado hacia un lado
        pts_top = [
            (hx - int(r*0.7), hy - int(r*0.6)),
            (hx - int(r*0.3), hy - r - int(r*0.5)),
            (hx + int(r*0.2), hy - r - int(r*0.55)),
            (hx + int(r*0.7), hy - r - int(r*0.3)),
            (hx + int(r*0.85), hy - int(r*0.5)),
            (hx + int(r*0.6), hy - int(r*0.4)),
        ]
        pygame.draw.polygon(surface, hair_color, pts_top)
        pygame.draw.polygon(surface, shadow, pts_top, 1)
        # Textura de mechones en el copete
        pygame.draw.line(surface, shadow, (hx - int(r*0.1), hy - r - int(r*0.35)), (hx + int(r*0.5), hy - r - int(r*0.15)), 1)
        pygame.draw.line(surface, shadow, (hx - int(r*0.3), hy - r - int(r*0.2)), (hx + int(r*0.3), hy - r - int(r*0.1)), 1)

    elif hair_style == 3:
        # Style 3: Man Bun / Moño alto (tipo Gareth Bale, Ibrahimovic)
        # Base del cabello peinado hacia atrás
        pygame.draw.ellipse(surface, hair_color, (hx - r, hy - r - int(r*0.2), r*2, int(r*1.1)))
        # Lados más pegados
        pygame.draw.ellipse(surface, shadow, (hx - r + 2, hy - int(r*0.6), r*2 - 4, int(r*0.7)))
        # El moño: esfera en la parte trasera-superior
        bun_x = hx - int(aim_dir.x * r * 0.6)
        bun_y = hy - r - int(r * 0.15)
        pygame.draw.circle(surface, shadow, (bun_x + 1, bun_y + 1), max(2, int(r * 0.4)))
        pygame.draw.circle(surface, hair_color, (bun_x, bun_y), max(2, int(r * 0.38)))
        # Elástico del moño
        pygame.draw.circle(surface, (min(255, hair_color[0]+60), min(255, hair_color[1]+60), min(255, hair_color[2]+60)), (bun_x, bun_y), max(2, int(r * 0.38)), 1)

    elif hair_style == 4:
        # Style 4: Melena Larga Ondulada (tipo Cavani, Puyol)
        # Masa principal del cabello en la parte superior
        pygame.draw.ellipse(surface, hair_color, (hx - int(r*1.1), hy - r - int(r*0.35), int(r*2.2), int(r*1.4)))
        # Mechones cayendo a los lados de la cara
        for side in [-1, 1]:
            sx = hx + side * int(r * 0.85)
            # Mechón lateral que cae
            pts_strand = [
                (sx, hy - int(r*0.5)),
                (sx + side * int(r*0.25), hy - int(r*0.1)),
                (sx + side * int(r*0.2), hy + int(r*0.5)),
                (sx + side * int(r*0.05), hy + int(r*0.7)),
                (sx - side * int(r*0.1), hy + int(r*0.4)),
                (sx - side * int(r*0.15), hy - int(r*0.2)),
            ]
            pygame.draw.polygon(surface, hair_color, pts_strand)
            pygame.draw.polygon(surface, shadow, pts_strand, 1)
        # Textura de ondas en la parte superior
        pygame.draw.arc(surface, shadow, (hx - int(r*0.6), hy - r - int(r*0.2), int(r*1.2), int(r*0.6)), 0.3, 2.9, 1)

    elif hair_style == 5:
        # Style 5: Rastas / Dreads (tipo Gullit, Renato Sanches)
        # Base del cabello
        pygame.draw.ellipse(surface, hair_color, (hx - r, hy - r - int(r*0.25), r*2, int(r*1.2)))
        # Rastas individuales cayendo
        import math
        num_dreads = 9
        for i in range(num_dreads):
            angle = math.pi * 0.15 + (math.pi * 0.7 / (num_dreads - 1)) * i
            start_x = hx + int(math.cos(angle) * r * 0.7) - int(r*0.1)
            start_y = hy - int(math.sin(angle) * r * 0.5)
            # Cada rasta se curva ligeramente
            sway = int(math.sin(i * 1.7) * r * 0.15)
            mid_x = start_x + sway
            mid_y = start_y + int(r * 0.4)
            end_x = start_x + sway + int(math.sin(i * 0.8) * r * 0.1)
            end_y = start_y + int(r * 0.8)
            dread_w = max(1, int(r * 0.12))
            pygame.draw.line(surface, hair_color, (start_x, start_y), (mid_x, mid_y), dread_w + 1)
            pygame.draw.line(surface, shadow, (mid_x, mid_y), (end_x, end_y), dread_w)
            # Cuenta dorada en la punta de algunas rastas
            if i % 3 == 0:
                pygame.draw.circle(surface, (218, 185, 50), (end_x, end_y), max(1, int(r * 0.07)))

    elif hair_style == 6:
        # Style 6: Undercut Peinado de Lado / Side Part (tipo Kroos, De Bruyne)
        # Lados rapados (sombra pegada a la cabeza)
        pygame.draw.arc(surface, shadow, (hx - r + 1, hy - r + 2, r*2 - 2, r*2 - 4), 3.6, 5.8, max(1, int(r*0.12)))
        # Parte superior voluminosa peinada hacia la derecha
        pts_side = [
            (hx - int(r*0.8), hy - int(r*0.55)),
            (hx - int(r*0.6), hy - r - int(r*0.3)),
            (hx, hy - r - int(r*0.35)),
            (hx + int(r*0.5), hy - r - int(r*0.25)),
            (hx + int(r*0.9), hy - int(r*0.6)),
            (hx + int(r*0.75), hy - int(r*0.35)),
            (hx + int(r*0.3), hy - int(r*0.4)),
            (hx - int(r*0.2), hy - int(r*0.45)),
        ]
        pygame.draw.polygon(surface, hair_color, pts_side)
        # Línea del raya (part line)
        pygame.draw.line(surface, shadow, (hx - int(r*0.5), hy - r - int(r*0.1)), (hx - int(r*0.6), hy - int(r*0.5)), 1)
        # Brillo en el lado peinado
        pygame.draw.line(surface, highlight, (hx + int(r*0.1), hy - r - int(r*0.15)), (hx + int(r*0.6), hy - int(r*0.5)), 1)

    else:
        # Style 7: Calvo / Rapado al cero (tipo Zidane, Henry)
        # Sutil sombra de cuero cabelludo en la coronilla
        pygame.draw.arc(surface, highlight, (hx - int(r*0.6), hy - r, int(r*1.2), int(r*0.8)), 0.4, 2.7, 1)
        # Reflejo de luz en la calva
        pygame.draw.arc(surface, (min(255, highlight[0]+30), min(255, highlight[1]+30), min(255, highlight[2]+30)),
                        (hx - int(r*0.3), hy - r + int(r*0.1), int(r*0.6), int(r*0.4)), 0.6, 2.5, 1)

def draw_player_avatar(surface, center_x, center_y, appearance_dict, scale=2.5, team_color=(0, 200, 150), secondary_color=(255, 255, 255), number="10"):
    """Dibuja un avatar completo y detallado del jugador para vistas de menú y vista previa."""
    skin_color = appearance_dict.get("skin_color", (245, 205, 172))
    skin_shadow = appearance_dict.get("skin_shadow", (200, 160, 130))
    hair_color = appearance_dict.get("hair_color", (20, 20, 20))
    hair_style = appearance_dict.get("hair_style", 0)
    boot_l = appearance_dict.get("boot_color_l", (50, 255, 50))
    boot_r = appearance_dict.get("boot_color_r", (255, 100, 0))
    has_beard = appearance_dict.get("has_beard", False)
    has_headband = appearance_dict.get("has_headband", False)

    r = int(12 * scale)
    cx, cy = int(center_x), int(center_y)

    # Sombra del jugador en el suelo
    shadow_surf = pygame.Surface((r * 4, r * 1.5), pygame.SRCALPHA)
    pygame.draw.ellipse(shadow_surf, (0, 0, 0, 80), (0, 0, r * 4, r * 1.5))
    surface.blit(shadow_surf, (cx - r * 2, cy + int(r * 2.8)))

    # Piernas y Botas
    leg_w = max(2, int(3 * scale / 2))
    leg_len = int(14 * scale)
    lx = cx - int(r * 0.4)
    rx = cx + int(r * 0.4)
    hip_y = cy + int(r * 0.8)

    # Pierna Izquierda
    pygame.draw.line(surface, skin_color, (lx, hip_y), (lx, hip_y + leg_len // 2), leg_w)
    pygame.draw.line(surface, team_color, (lx, hip_y + leg_len // 2), (lx, hip_y + leg_len), leg_w)
    pygame.draw.ellipse(surface, boot_l, (lx - max(2, int(2 * scale)), hip_y + leg_len - max(1, int(2 * scale)), max(5, int(6 * scale)), max(4, int(4 * scale))))

    # Pierna Derecha
    pygame.draw.line(surface, skin_color, (rx, hip_y), (rx, hip_y + leg_len // 2), leg_w)
    pygame.draw.line(surface, team_color, (rx, hip_y + leg_len // 2), (rx, hip_y + leg_len), leg_w)
    pygame.draw.ellipse(surface, boot_r, (rx - max(2, int(2 * scale)), hip_y + leg_len - max(1, int(2 * scale)), max(5, int(6 * scale)), max(4, int(4 * scale))))

    # Torso (Camiseta)
    torso_w = int(r * 1.5)
    torso_h = int(r * 1.4)
    torso_rect = pygame.Rect(cx - torso_w // 2, cy - torso_h // 3, torso_w, torso_h)
    pygame.draw.rect(surface, team_color, torso_rect, border_radius=max(3, int(4 * scale)))
    pygame.draw.rect(surface, secondary_color, torso_rect, max(1, int(scale)), border_radius=max(3, int(4 * scale)))

    # Número en camiseta
    try:
        font_num = pygame.font.SysFont("Impact", max(10, int(11 * scale)))
        num_s = font_num.render(str(number), True, secondary_color)
        surface.blit(num_s, (cx - num_s.get_width() // 2, cy + int(r * 0.1)))
    except:
        pass

    # Brazos
    arm_w = max(2, int(2.5 * scale))
    arm_len = int(10 * scale)
    lax = cx - torso_w // 2 - 2
    rax = cx + torso_w // 2 + 2
    arm_y = cy - torso_h // 4
    pygame.draw.line(surface, skin_color, (lax, arm_y), (lax - int(3 * scale), arm_y + arm_len), arm_w)
    pygame.draw.line(surface, skin_color, (rax, arm_y), (rax + int(3 * scale), arm_y + arm_len), arm_w)

    # Cabeza
    head_r = int(r * 0.65)
    hx = cx
    hy = cy - torso_h // 2 - head_r // 2
    pygame.draw.circle(surface, skin_shadow, (hx + 1, hy + 1), head_r)
    pygame.draw.circle(surface, skin_color, (hx, hy), head_r)
    pygame.draw.circle(surface, (10, 10, 10), (hx, hy), head_r, max(1, int(1 * scale)))

    # Cabello
    aim_dummy = pygame.math.Vector2(0, 1)
    draw_procedural_hair(surface, hx, hy, head_r, hair_style, hair_color, aim_dummy)

    # Barba y Cinta
    if has_beard:
        beard_col = (max(0, skin_color[0]-60), max(0, skin_color[1]-55), max(0, skin_color[2]-50))
        pygame.draw.arc(surface, beard_col, (hx - head_r + 1, hy - 1, (head_r - 1) * 2, head_r), 3.14, 6.28, max(1, int(1.5 * scale)))

    if has_headband:
        pygame.draw.line(surface, secondary_color, (hx - head_r + 1, hy - head_r + 4), (hx + head_r - 1, hy - head_r + 4), max(1, int(2 * scale)))

