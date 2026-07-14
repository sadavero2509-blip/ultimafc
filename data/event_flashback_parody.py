import datetime

# --- CONFIGURACIÓN DEL EVENTO ---
EVENT_NAME = "FLASHBACK: CRÓNICAS DEL TIEMPO"
START_DATE = datetime.datetime(2026, 12, 1, 0, 0)
END_DATE = datetime.datetime(2026, 12, 31, 23, 59)

def is_flashback_active():
    now = datetime.datetime.now()
    return START_DATE <= now <= END_DATE

# --- JUGADORES DEL EVENTO ---
FLASHBACK_PLAYERS = [
    {
        "name": "Lio Messy", "pos": "RW", "ovr": 91, "nat": "ARG", "team": "ROS",
        "card_type": "FLASHBACK", "event": "CRÓNICAS DEL TIEMPO",
        "s": {"speed": 96, "shot": 90, "passing": 94, "dribbling": 98, "defense": 38, "physical": 68, "gk": 10}
    },
    {
        "name": "Kylian Mbappeh", "pos": "ST", "ovr": 88, "nat": "FRA", "team": "MON",
        "card_type": "FLASHBACK", "event": "CRÓNICAS DEL TIEMPO",
        "s": {"speed": 97, "shot": 85, "passing": 78, "dribbling": 89, "defense": 36, "physical": 72, "gk": 10}
    },
    {
        "name": "Lamine Yammal", "pos": "RW", "ovr": 90, "nat": "ESP", "team": "STE",
        "card_type": "FLASHBACK", "event": "CRÓNICAS DEL TIEMPO",
        "s": {"speed": 94, "shot": 86, "passing": 88, "dribbling": 93, "defense": 45, "physical": 70, "gk": 10}
    },
    {
        "name": "Wayne Rooneyah", "pos": "ST", "ovr": 89, "nat": "ENG", "team": "UDV", "is_legend": True,
        "card_type": "FLASHBACK", "event": "CRÓNICAS DEL TIEMPO",
        "s": {"speed": 91, "shot": 88, "passing": 78, "dribbling": 84, "defense": 50, "physical": 86, "gk": 10}
    },
    {
        "name": "Ronaldoo", "pos": "ST", "ovr": 91, "nat": "BRA", "team": "BRA", "is_legend": True,
        "card_type": "FLASHBACK", "event": "CRÓNICAS DEL TIEMPO",
        "s": {"speed": 99, "shot": 87, "passing": 75, "dribbling": 94, "defense": 30, "physical": 75, "gk": 10}
    },
    {
        "name": "Diego Maradonae", "pos": "CAM", "ovr": 91, "nat": "ARG", "team": "ARG", "is_legend": True,
        "card_type": "FLASHBACK", "event": "CRÓNICAS DEL TIEMPO",
        "s": {"speed": 97, "shot": 88, "passing": 90, "dribbling": 98, "defense": 40, "physical": 74, "gk": 10}
    },
    {
        "name": "Neymar Jr", "pos": "LW", "ovr": 90, "nat": "BRA", "team": "BRA",
        "card_type": "FLASHBACK", "event": "CRÓNICAS DEL TIEMPO",
        "s": {"speed": 96, "shot": 88, "passing": 84, "dribbling": 96, "defense": 35, "physical": 80, "gk": 10}
    },
    {
        "name": "Cristian Ronaldoo", "pos": "LM", "ovr": 91, "nat": "POR", "team": "POR",
        "card_type": "FLASHBACK", "event": "CRÓNICAS DEL TIEMPO",
        "s": {"speed": 97, "shot": 94, "passing": 80, "dribbling": 90, "defense": 38, "physical": 86, "gk": 10}
    }
]

def get_flashback_cards():
    return FLASHBACK_PLAYERS
