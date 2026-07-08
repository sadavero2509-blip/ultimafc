import datetime

# --- CONFIGURACIÓN DEL EVENTO: HERENCIA RETRO ---

# Fecha de revelación (Promo/Banner): 26 de Agosto de 2026, 15:00 ET
PROMO_DATE = datetime.datetime(2026, 8, 26, 15, 0)

# Fecha de disponibilidad (Sobres/Evoluciones): 26 de Septiembre de 2026, 15:00 ET
RELEASE_DATE = datetime.datetime(2026, 9, 26, 15, 0)

def is_promo_active():
    return datetime.datetime.now() >= PROMO_DATE

def is_release_active():
    return datetime.datetime.now() >= RELEASE_DATE

# Estadísticas mejoradas para las versiones de evento (+1 o +2 sobre su base)
EVENT_LEGENDS = {
    "Erick Kantonah": {
        "name": "Erick Kantonah (HERENCIA)", "short": "KAN", "age": 28, "pot": 92, "pos": "CF", "num": 7, "nat": "FRA", 
        "card_type": "RETRO_HERITAGE", "is_legend": True,
        "s": {"speed": 84, "shot": 91, "passing": 90, "defense": 48, "gk": 10}
    },
    "Lev Yashinn": {
        "name": "Lev Yashinn (HERENCIA)", "short": "YAS", "age": 31, "pot": 96, "pos": "GK", "num": 1, "nat": "RUS", 
        "card_type": "RETRO_HERITAGE", "is_legend": True,
        "s": {"speed": 65, "shot": 10, "passing": 78, "defense": 30, "gk": 98}
    },
    "Alestandro Nestah": {
        "name": "Alestandro Nestah (HERENCIA)", "short": "NES", "age": 28, "pot": 94, "pos": "CB", "num": 13, "nat": "ITA", 
        "card_type": "RETRO_HERITAGE", "is_legend": True,
        "s": {"speed": 86, "shot": 42, "passing": 70, "defense": 96, "gk": 10}
    },
    "Bekenbauer": {
        "name": "Bekenbauer (HERENCIA)", "short": "BEC", "age": 32, "pot": 96, "pos": "CB", "num": 5, "nat": "GER", 
        "card_type": "RETRO_HERITAGE", "is_legend": True,
        "s": {"speed": 84, "shot": 78, "passing": 90, "defense": 97, "gk": 10}
    },
    "Peléi": {
        "name": "Peléi (HERENCIA)", "short": "PEL", "age": 25, "pot": 99, "pos": "ST", "num": 10, "nat": "BRA", 
        "card_type": "RETRO_HERITAGE", "is_legend": True,
        "s": {"speed": 97, "shot": 98, "passing": 92, "defense": 55, "gk": 10}
    }
}
