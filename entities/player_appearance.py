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
    """Dibuja los 8 estilos de cabello detallados."""
    if hair_style == 0:
        # Style 0: Corte Corto / Rapado clásico
        pygame.draw.circle(surface, hair_color, (hx, hy - head_r + 2), int(head_r * 0.75))
        
    elif hair_style == 1:
        # Style 1: Afro / Rizo denso
        for dx, dy in [(-3, -head_r+1), (0, -head_r-1), (3, -head_r+1), (-4, -head_r+3), (4, -head_r+3), (0, -head_r+1)]:
            pygame.draw.circle(surface, hair_color, (hx + dx, hy + dy), int(head_r * 0.5))
            
    elif hair_style == 2:
        # Style 2: Cresta / Spiky / Mohawk
        pygame.draw.circle(surface, hair_color, (hx, hy - head_r + 2), int(head_r * 0.65))
        for dx in [-4, -1, 2, 5]:
            pygame.draw.polygon(surface, hair_color, [
                (hx + dx - 1, hy - head_r + 1),
                (hx + dx, hy - head_r - 3),
                (hx + dx + 1, hy - head_r + 1)
            ])
            
    elif hair_style == 3:
        # Style 3: Coleta / Moño / Man Bun
        pygame.draw.circle(surface, hair_color, (hx, hy - head_r + 2), int(head_r * 0.75))
        py_x = hx - int(aim_dir.x * head_r * 0.85)
        py_y = hy - int(aim_dir.y * head_r * 0.2) + 2
        pygame.draw.circle(surface, hair_color, (py_x, py_y), int(head_r * 0.45))
        pygame.draw.circle(surface, (210, 210, 210), (py_x, py_y), max(1, int(head_r * 0.25)), 1)
        
    elif hair_style == 4:
        # Style 4: Melena Larga / Caída a los lados
        pygame.draw.circle(surface, hair_color, (hx, hy - head_r + 2), int(head_r * 0.8))
        pygame.draw.line(surface, hair_color, (hx - head_r + 1, hy - head_r + 3), (hx - head_r - 1, hy + 2), 2)
        pygame.draw.line(surface, hair_color, (hx + head_r - 1, hy - head_r + 3), (hx + head_r + 1, hy + 2), 2)
        
    elif hair_style == 5:
        # Style 5: Rastas / Dreads con cuentas doradas
        pygame.draw.circle(surface, hair_color, (hx, hy - head_r + 2), int(head_r * 0.75))
        for dx in [-4, -2, 0, 2, 4]:
            end_x = int(hx + dx * 1.2)
            end_y = hy + 2
            pygame.draw.line(surface, hair_color, (hx + dx, hy - head_r + 2), (end_x, end_y), 2)
            pygame.draw.circle(surface, (230, 190, 50), (end_x, end_y), 1)  # Cuentas de rasta
            
    elif hair_style == 6:
        # Style 6: Undercut / Tupe peinado de lado
        pygame.draw.circle(surface, hair_color, (hx + 1, hy - head_r + 1), int(head_r * 0.8))
        pygame.draw.polygon(surface, hair_color, [
            (hx - head_r + 2, hy - head_r + 2),
            (hx + head_r, hy - head_r - 2),
            (hx + head_r - 1, hy)
        ])
        
    else:
        # Style 7: Calvo / Rapado al cero (con sombra de cuero cabelludo)
        highlight = (min(255, hair_color[0]+80), min(255, hair_color[1]+80), min(255, hair_color[2]+80))
        pygame.draw.arc(surface, highlight, (hx - head_r + 2, hy - head_r + 1, head_r, head_r), 0.5, 2.2, 1)
