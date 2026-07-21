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

def get_player_appearance(player_data):
    """Calcula de forma determinista (hash de datos) la apariencia del jugador."""
    name = str(player_data.get("name", ""))
    num = int(player_data.get("num", 1))
    pos = str(player_data.get("pos", ""))
    
    # Hash determinista para que la apariencia no cambie entre frames
    h_str = f"{name}_{num}_{pos}"
    h_val = 0
    for char in h_str:
        h_val = (h_val * 31 + ord(char)) & 0xFFFFFFFF
        
    skin_idx = h_val % len(SKIN_PALETTE)
    hair_col_idx = (h_val // 7) % len(HAIR_COLOR_PALETTE)
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
