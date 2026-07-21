import pygame

# Versión del Juego
GAME_VERSION = "1.1.0"
UPDATE_TYPE = "minor"  # "minor" para parches/actualización en vivo, "major" para instalación obligatoria

# Dimensiones de la ventana (Escala base)
WIDTH = 1280
HEIGHT = 720
FPS = 60

# ── Sistema de Dificultad ──
# 1=Aficionado, 3=Semi-Pro, 5=Profesional, 7=Clase Mundial, 9=Leyenda
DIFFICULTY_PRESETS = {
    "AFICIONADO":    {"level": 1, "desc": "Para aprender los controles"},
    "SEMI-PRO":      {"level": 3, "desc": "Rivales moderados"},
    "PROFESIONAL":   {"level": 5, "desc": "Experiencia equilibrada"},
    "CLASE MUNDIAL": {"level": 7, "desc": "Rivales inteligentes y rápidos"},
    "LEYENDA":       {"level": 9, "desc": "Sin piedad"},
}
DIFFICULTY_NAMES = list(DIFFICULTY_PRESETS.keys())
DEFAULT_DIFFICULTY = 5  # Profesional

# Colores comunes
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN_PITCH = (34, 139, 34)
GREEN_PITCH_ALT = (28, 120, 28)  # Franja alterna de césped
RED = (200, 50, 50)
BLUE = (50, 100, 200)
YELLOW = (255, 215, 0)
GOLD = (218, 165, 32)
GRAY = (120, 120, 120)
DARK_GRAY = (40, 40, 40)
LIGHT_GRAY = (180, 180, 180)

# Colores de UI
UI_BG = (15, 15, 30)
UI_ACCENT = (0, 200, 150)
UI_ACCENT_ALT = (255, 100, 60)
UI_CARD_BG = (25, 25, 50)
UI_CARD_HOVER = (40, 40, 70)
UI_TEXT = (230, 230, 240)
UI_TEXT_DIM = (140, 140, 160)

# Física base (Rebalanceado v1.2 – Ritmo más dinámico y rápido)
FRICTION = 0.987         # Menos fricción → el balón ruede más fluido y rápido
BALL_RADIUS = 7          
PLAYER_RADIUS = 13       

PLAYER_SPEED = 86        # Velocidad base de jugador aumentada (75→86)
DASH_MULTIPLIER = 1.70   # Sprint más explosivo (1.60→1.70)
KICK_FORCE = 1000        # Tiros más potentes (900→1000)
PASS_FORCE = 680         # Pases más rápidos (600→680)
PASS_COOLDOWN = 0.35     
MAGNET_DIST = 20         # Rango de posesión ampliado para igualar tamaños (16→20)

# Cooldowns y Robos
TACKLE_BOOST = 250       # Velocidad de tackle aumentada (220→250)
TACKLE_DURATION = 0.5    

# IA
AI_SPEED = 82            # IA ajustada a mayor ritmo (72→82)
AI_CHASE_RADIUS = 320    # Rango de persecución ampliado (300→320)
AI_POSITION_JITTER = 12  
GK_SPEED = 98            # Portero ajustado a la mayor velocidad (90→98)
GK_DIVE_SPEED = 265      # Portero se lanza más rápido (240→265)
GK_REACT_DIST = 100      # Portero reacciona desde más lejos (75→100)

# Partido
MATCH_DURATION = 180     # Duración en segundos (3 minutos)
GOAL_FREEZE_TIME = 0.5   
CELEBRATION_DURATION = 3.0  

# Formaciones (11v11, excluyen portero que siempre está en su área)
FORMATIONS = {
    "4-3-3": [
        (0.12, 0.20), (0.10, 0.40), (0.10, 0.60), (0.12, 0.80), # DEF
        (0.28, 0.30), (0.25, 0.50), (0.28, 0.70),             # MID
        (0.42, 0.25), (0.42, 0.75), (0.50, 0.50),             # ATT
    ],
    "4-3-3 OFENSIVA": [
        (0.12, 0.20), (0.10, 0.40), (0.10, 0.60), (0.12, 0.80), # DEF
        (0.22, 0.35), (0.22, 0.65), (0.32, 0.50),             # 2 CM + 1 CAM
        (0.42, 0.20), (0.42, 0.80), (0.50, 0.50),             # ATT
    ],
    "4-3-3 DEFENSIVA": [
        (0.12, 0.20), (0.10, 0.40), (0.10, 0.60), (0.12, 0.80), # DEF
        (0.18, 0.50), (0.28, 0.35), (0.28, 0.65),             # 1 CDM + 2 CM
        (0.42, 0.20), (0.42, 0.80), (0.50, 0.50),             # ATT
    ],
    "4-3-3 FALSO 9": [
        (0.12, 0.20), (0.10, 0.40), (0.10, 0.60), (0.12, 0.80), # DEF
        (0.25, 0.30), (0.22, 0.50), (0.25, 0.70),             # MID
        (0.42, 0.20), (0.42, 0.80), (0.38, 0.50),             # CF (Retrasado)
    ],
    "4-4-2": [
        (0.12, 0.20), (0.10, 0.40), (0.10, 0.60), (0.12, 0.80), # DEF
        (0.25, 0.20), (0.22, 0.40), (0.22, 0.60), (0.25, 0.80), # MID
        (0.45, 0.35), (0.50, 0.50), # ATT
    ],
    "4-4-2 CONTENCIÓN": [
        (0.12, 0.20), (0.10, 0.40), (0.10, 0.60), (0.12, 0.80), # DEF
        (0.18, 0.40), (0.18, 0.60), (0.28, 0.15), (0.28, 0.85), # 2 CDM + LM/RM
        (0.45, 0.35), (0.50, 0.50), # ATT
    ],
    "4-2-3-1 CERRADA": [
        (0.12, 0.20), (0.10, 0.40), (0.10, 0.60), (0.12, 0.80), # DEF
        (0.18, 0.40), (0.18, 0.60),                            # 2 CDM
        (0.32, 0.30), (0.32, 0.50), (0.32, 0.70),              # 3 CAM
        (0.50, 0.50),                                          # ST
    ],
    "4-2-3-1 ANCHA": [
        (0.12, 0.20), (0.10, 0.40), (0.10, 0.60), (0.12, 0.80), # DEF
        (0.18, 0.40), (0.18, 0.60),                            # 2 CDM
        (0.28, 0.15), (0.32, 0.50), (0.28, 0.85),              # LM, CAM, RM
        (0.50, 0.50),                                          # ST
    ],
    "4-1-2-1-2 CERRADA": [
        (0.12, 0.20), (0.10, 0.40), (0.10, 0.60), (0.12, 0.80), # DEF
        (0.18, 0.50), (0.25, 0.35), (0.25, 0.65), (0.32, 0.50), # CDM, 2 CM, CAM
        (0.45, 0.35), (0.50, 0.50),                             # 2 ST
    ],
    "4-1-2-1-2 ANCHA": [
        (0.12, 0.20), (0.10, 0.40), (0.10, 0.60), (0.12, 0.80), # DEF
        (0.18, 0.50), (0.28, 0.15), (0.28, 0.85), (0.35, 0.50), # CDM, LM, RM, CAM
        (0.45, 0.35), (0.50, 0.50),                             # 2 ST
    ],
    "4-3-2-1 ÁRBOL": [ 
        (0.12, 0.20), (0.10, 0.40), (0.10, 0.60), (0.12, 0.80), # DEF
        (0.25, 0.25), (0.22, 0.50), (0.25, 0.75),               # 3 CM
        (0.35, 0.35), (0.35, 0.65),                             # 2 CF/CAM
        (0.50, 0.50),                                           # ST
    ],
    "3-4-3": [
        (0.10, 0.30), (0.08, 0.50), (0.10, 0.70),               # 3 CB
        (0.25, 0.15), (0.22, 0.40), (0.22, 0.60), (0.25, 0.85), # LM, 2 CM, RM
        (0.42, 0.25), (0.42, 0.75), (0.50, 0.50),               # LW, RW, ST
    ],
    "3-5-2": [
        (0.10, 0.30), (0.08, 0.50), (0.10, 0.70),               # 3 CB
        (0.22, 0.15), (0.25, 0.35), (0.18, 0.50), (0.25, 0.65), (0.22, 0.85), # MID
        (0.45, 0.35), (0.50, 0.50),                             # 2 ST
    ],
    "5-2-1-2": [
        (0.12, 0.15), (0.10, 0.35), (0.08, 0.50), (0.10, 0.65), (0.12, 0.85), # 5 DEF
        (0.25, 0.40), (0.25, 0.60),                             # 2 CM
        (0.35, 0.50),                                           # CAM
        (0.45, 0.35), (0.50, 0.50),                             # 2 ST
    ],
    "5-4-1": [
        (0.12, 0.15), (0.10, 0.35), (0.08, 0.50), (0.10, 0.65), (0.12, 0.85), # 5 DEF
        (0.28, 0.20), (0.25, 0.40), (0.25, 0.60), (0.28, 0.80), # 4 MID
        (0.50, 0.50),                                           # ST
    ]
}

# Fix para Kickoff (Asegurar que el último jugador siempre esté en el centro 0.5, 0.5)
for f_name in FORMATIONS:
    if "FALSO 9" not in f_name: # En F9 el delantero está retrasado, mejor no forzarlo
        FORMATIONS[f_name][-1] = (0.50, 0.50)

