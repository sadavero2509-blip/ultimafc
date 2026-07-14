import datetime
import copy
from data.rosters import calculate_ovr

# Configuración del Evento
EVENT_START_DATE = datetime.datetime(2026, 6, 11, 12, 0) # 11 de Junio, 12:00 ET
EVENT_END_DATE = datetime.datetime(2026, 7, 12, 23, 59)

def is_event_active():
    """Verifica si el evento del Mundial está activo según la fecha actual."""
    now = datetime.datetime.now()
    return EVENT_START_DATE <= now <= EVENT_END_DATE

# Jugadores del Evento (Boosted Stats)
WORLDCUP_PLAYERS = [
    # ARG
    {'name': 'Lio Messy', 'team': 'ARG', 'ovr_boost': 2, 'pos': 'RW', 's': {'speed': 78, 'shot': 92, 'passing': 95, 'defense': 35, 'gk': 10, 'dribbling': 94, 'physical': 72}},
    {'name': 'Julián Álvares', 'team': 'ARG', 'ovr_boost': 1, 'pos': 'ST', 's': {'speed': 86, 'shot': 88, 'passing': 82, 'defense': 55, 'gk': 10, 'dribbling': 84, 'physical': 82}},
    
    # BRA
    {'name': 'Vinni Jr.', 'team': 'BRA', 'ovr_boost': 2, 'pos': 'LW', 's': {'speed': 98, 'shot': 88, 'passing': 85, 'defense': 35, 'gk': 10, 'dribbling': 95, 'physical': 74}},
    {'name': 'Endrickko', 'team': 'BRA', 'ovr_boost': 2, 'pos': 'ST', 's': {'speed': 92, 'shot': 86, 'passing': 75, 'defense': 35, 'gk': 10, 'dribbling': 85, 'physical': 86}},
    
    # FRA
    {'name': 'Kylian Mbappeh', 'team': 'FRA', 'ovr_boost': 1, 'pos': 'LW', 's': {'speed': 99, 'shot': 93, 'passing': 84, 'defense': 35, 'gk': 10, 'dribbling': 94, 'physical': 78}},
    {'name': 'Antoine Griezmannn', 'team': 'FRA', 'ovr_boost': 1, 'pos': 'CM', 's': {'speed': 80, 'shot': 86, 'passing': 91, 'defense': 65, 'gk': 10, 'dribbling': 86, 'physical': 72}},
    
    # ESP
    {'name': 'Lamine Yammal', 'team': 'ESP', 'ovr_boost': 2, 'pos': 'RW', 's': {'speed': 94, 'shot': 85, 'passing': 88, 'defense': 40, 'gk': 10, 'dribbling': 92, 'physical': 64}},
    {'name': 'Rodrii', 'team': 'ESP', 'ovr_boost': 1, 'pos': 'CM', 's': {'speed': 68, 'shot': 80, 'passing': 90, 'defense': 90, 'gk': 10, 'dribbling': 78, 'physical': 86}},
    
    # ENG
    {'name': 'Jude Belingham', 'team': 'ENG', 'ovr_boost': 1, 'pos': 'CM', 's': {'speed': 84, 'shot': 86, 'passing': 88, 'defense': 84, 'gk': 10, 'dribbling': 87, 'physical': 82}},
    {'name': 'Harry Kanne', 'team': 'ENG', 'ovr_boost': 1, 'pos': 'ST', 's': {'speed': 74, 'shot': 94, 'passing': 90, 'defense': 45, 'gk': 10, 'dribbling': 82, 'physical': 84}},
    
    # GER
    {'name': 'Jammal Mussiala', 'team': 'GER', 'ovr_boost': 2, 'pos': 'CM', 's': {'speed': 88, 'shot': 85, 'passing': 88, 'defense': 55, 'gk': 10, 'dribbling': 91, 'physical': 72}},
    {'name': 'Florian Wirtzza', 'team': 'GER', 'ovr_boost': 2, 'pos': 'LW', 's': {'speed': 86, 'shot': 85, 'passing': 91, 'defense': 55, 'gk': 10, 'dribbling': 90, 'physical': 70}},
    
    # POR
    {'name': 'Cristian Ronaldoo', 'team': 'POR', 'ovr_boost': 2, 'pos': 'ST', 's': {'speed': 80, 'shot': 92, 'passing': 80, 'defense': 35, 'gk': 10, 'dribbling': 84, 'physical': 82}},
    {'name': 'Rafael Leãih', 'team': 'POR', 'ovr_boost': 1, 'pos': 'LW', 's': {'speed': 96, 'shot': 84, 'passing': 80, 'defense': 35, 'gk': 10, 'dribbling': 90, 'physical': 74}},
    
    # COL
    {'name': 'Luis Díazzo', 'team': 'COL', 'ovr_boost': 2, 'pos': 'LW', 's': {'speed': 95, 'shot': 85, 'passing': 80, 'defense': 45, 'gk': 10, 'dribbling': 91, 'physical': 76}},
    {'name': 'Jammes Redríguoz', 'team': 'COL', 'ovr_boost': 2, 'pos': 'CM', 's': {'speed': 65, 'shot': 88, 'passing': 94, 'defense': 45, 'gk': 10, 'dribbling': 88, 'physical': 72}},

    # URU
    {'name': 'Federrico Valverddi', 'team': 'URU', 'ovr_boost': 1, 'pos': 'CM', 's': {'speed': 92, 'shot': 86, 'passing': 90, 'defense': 84, 'gk': 10, 'dribbling': 80, 'physical': 80}},
    {'name': 'Darwin Núñezi', 'team': 'URU', 'ovr_boost': 2, 'pos': 'ST', 's': {'speed': 94, 'shot': 88, 'passing': 78, 'defense': 50, 'gk': 10, 'dribbling': 78, 'physical': 82}},

    # NED
    {'name': 'Virgil van Dijkih', 'team': 'NED', 'ovr_boost': 1, 'pos': 'CB', 's': {'speed': 80, 'shot': 62, 'passing': 82, 'defense': 94, 'gk': 10, 'dribbling': 56, 'physical': 86}},
    {'name': 'Codye Gakpeh', 'team': 'NED', 'ovr_boost': 2, 'pos': 'LW', 's': {'speed': 88, 'shot': 86, 'passing': 84, 'defense': 50, 'gk': 10, 'dribbling': 82, 'physical': 62}},

    # BEL
    {'name': 'Kevin De Bruyneh', 'team': 'BEL', 'ovr_boost': 1, 'pos': 'CM', 's': {'speed': 78, 'shot': 92, 'passing': 97, 'defense': 74, 'gk': 10, 'dribbling': 74, 'physical': 74}},
    {'name': 'Jérémy Dokeh', 'team': 'BEL', 'ovr_boost': 2, 'pos': 'LW', 's': {'speed': 96, 'shot': 82, 'passing': 82, 'defense': 40, 'gk': 10, 'dribbling': 86, 'physical': 66}},

    # CRO
    {'name': 'Luka Modrich', 'team': 'CRO', 'ovr_boost': 2, 'pos': 'CM', 's': {'speed': 74, 'shot': 82, 'passing': 93, 'defense': 72, 'gk': 10, 'dribbling': 74, 'physical': 76}},
    {'name': 'Josko Gvirdaol', 'team': 'CRO', 'ovr_boost': 2, 'pos': 'LB', 's': {'speed': 84, 'shot': 68, 'passing': 84, 'defense': 88, 'gk': 10, 'dribbling': 74, 'physical': 80}},

    # MAR
    {'name': 'Achrafo Hacimi', 'team': 'MAR', 'ovr_boost': 1, 'pos': 'RB', 's': {'speed': 96, 'shot': 80, 'passing': 85, 'defense': 78, 'gk': 10, 'dribbling': 72, 'physical': 75}},
    {'name': 'Brahim Díazah', 'team': 'MAR', 'ovr_boost': 2, 'pos': 'CM', 's': {'speed': 88, 'shot': 82, 'passing': 84, 'defense': 40, 'gk': 10, 'dribbling': 85, 'physical': 66}},

    # MEX
    {'name': 'Santiago Giménes', 'team': 'MEX', 'ovr_boost': 2, 'pos': 'ST', 's': {'speed': 86, 'shot': 88, 'passing': 72, 'defense': 40, 'gk': 10, 'dribbling': 80, 'physical': 82}},
    {'name': 'Edson Álbarez', 'team': 'MEX', 'ovr_boost': 1, 'pos': 'CM', 's': {'speed': 76, 'shot': 68, 'passing': 78, 'defense': 88, 'gk': 10, 'dribbling': 72, 'physical': 86}},

    # USA
    {'name': 'Christtian Pilisuc', 'team': 'USA', 'ovr_boost': 2, 'pos': 'LW', 's': {'speed': 91, 'shot': 86, 'passing': 84, 'defense': 45, 'gk': 10, 'dribbling': 88, 'physical': 66}},
    {'name': 'Weston McKenniih', 'team': 'USA', 'ovr_boost': 1, 'pos': 'CM', 's': {'speed': 82, 'shot': 78, 'passing': 80, 'defense': 82, 'gk': 10, 'dribbling': 78, 'physical': 86}},

    # --- LEYENDAS MUNDIALISTAS (Boost +1) ---
    {'name': 'Pellé', 'team': 'BRA', 'ovr_boost': 1, 'is_legend': True, 'pos': 'ST', 's': {'speed': 96, 'shot': 97, 'passing': 91, 'defense': 55, 'gk': 10, 'dribbling': 99, 'physical': 88}},
    {'name': 'Ronaldoo', 'team': 'BRA', 'ovr_boost': 1, 'is_legend': True, 'pos': 'ST', 's': {'speed': 98, 'shot': 96, 'passing': 82, 'defense': 45, 'gk': 10, 'dribbling': 98, 'physical': 85}},
    {'name': 'Caffú', 'team': 'BRA', 'ovr_boost': 1, 'is_legend': True, 'pos': 'RB', 's': {'speed': 92, 'shot': 66, 'passing': 83, 'defense': 89, 'gk': 10, 'dribbling': 82, 'physical': 90}},
    {'name': 'Diego Maradonae', 'team': 'AR', 'ovr_boost': 1, 'is_legend': True, 'pos': 'CAM', 's': {'speed': 93, 'shot': 95, 'passing': 96, 'defense': 45, 'gk': 10, 'dribbling': 98, 'physical': 78}},
    {'name': 'Andrés Iniezta', 'team': 'ESP', 'ovr_boost': 1, 'is_legend': True, 'pos': 'CM', 's': {'speed': 81, 'shot': 79, 'passing': 93, 'defense': 65, 'gk': 10, 'dribbling': 94, 'physical': 70}},
    {'name': 'Zinedine Zadine', 'team': 'FRA', 'ovr_boost': 1, 'is_legend': True, 'pos': 'CAM', 's': {'speed': 85, 'shot': 92, 'passing': 97, 'defense': 65, 'gk': 10, 'dribbling': 92, 'physical': 82}},
    {'name': 'Miroslav Klosse', 'team': 'GER', 'ovr_boost': 1, 'is_legend': True, 'pos': 'ST', 's': {'speed': 83, 'shot': 91, 'passing': 71, 'defense': 45, 'gk': 10, 'dribbling': 80, 'physical': 88}},
    {'name': 'Diego Forlánn', 'team': 'URU', 'ovr_boost': 1, 'is_legend': True, 'pos': 'ST', 's': {'speed': 86, 'shot': 92, 'passing': 85, 'defense': 42, 'gk': 10, 'dribbling': 88, 'physical': 82}},
]

# RECOMPENSA SBC PELÉ (Exclusivo, no sale en sobres)
PELE_SBC_REWARD = {
    'name': 'Peléi',
    'team': 'BRA',
    'is_legend': True,
    'pos': 'ST',
    'card_type': 'WORLDCUP_LEGEND',
    'event': 'COPA DEL MUNDO',
    'ovr': 99,
    's': {'speed': 97, 'shot': 98, 'passing': 92, 'defense': 55, 'gk': 10, 'dribbling': 99, 'physical': 90}
}

def get_event_cards():
    cards = []
    for p_base in WORLDCUP_PLAYERS:
        p = copy.deepcopy(p_base)
        ovr = calculate_ovr(p) + p.get("ovr_boost", 0)
        p["ovr"] = ovr
        
        # Rareza base según OVR o si es leyenda
        if p.get("is_legend"):
            p["rarity"] = "LEYENDA"
            p["card_type"] = "WORLDCUP_LEGEND"
        else:
            if ovr >= 75: p["rarity"] = "ORO"
            elif ovr >= 65: p["rarity"] = "PLATA"
            else: p["rarity"] = "BRONCE"
            p["card_type"] = "WORLDCUP"
            
        p["event"] = "WC" # Usamos WC para que coincida con el filtro interno
        cards.append(p)
    return cards

# Diseño Visual del Evento
EVENT_COLORS = {
    "primary": (0, 104, 71), # Verde México (Esmeralda)
    "accent_1": (191, 10, 48), # Rojo Canadá/USA
    "accent_2": (0, 40, 104), # Azul USA
    "text": (255, 255, 255)
}
