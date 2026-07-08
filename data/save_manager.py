"""Sistema de persistencia para datos editados por el usuario."""
import json
import os

SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "saves")
SAVE_FILE = os.path.join(SAVE_DIR, "user_data.json")

# Posiciones válidas expandidas
ALL_POSITIONS = [
    "GK",
    "LB", "CB", "RB", "LWB", "RWB",
    "CDM", "CM", "CAM", "LM", "RM",
    "LW", "RW", "SS", "CF", "ST",
]

POS_LABELS = {
    "GK": "Portero", "LB": "Lateral Izq.", "CB": "Central", "RB": "Lateral Der.",
    "LWB": "Carrilero Izq.", "RWB": "Carrilero Der.",
    "CDM": "Pivote", "CM": "Mediocentro", "CAM": "Med. Ofensivo",
    "LM": "Medio Izq.", "RM": "Medio Der.",
    "LW": "Extremo Izq.", "RW": "Extremo Der.",
    "SS": "Med. Punta", "CF": "Delantero Centro", "ST": "Delantero",
}

POS_CATEGORIES = {
    "Portero": ["GK"],
    "Defensa": ["LB", "CB", "RB", "LWB", "RWB"],
    "Mediocampo": ["CDM", "CM", "CAM", "LM", "RM"],
    "Delantera": ["LW", "RW", "SS", "CF", "ST"],
}

def _ensure_dir():
    os.makedirs(SAVE_DIR, exist_ok=True)

def load_user_data():
    """Load saved user data or return defaults."""
    _ensure_dir()
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return {"team_configs": {}, "created_players": []}

def save_user_data(data):
    """Persist user data to disk."""
    _ensure_dir()
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def get_team_config(team_short):
    """Get saved config for a specific team (formation, lineup order)."""
    data = load_user_data()
    return data.get("team_configs", {}).get(team_short, None)

def save_team_config(team_short, config):
    """Save config for a team. config = {formation, starter_indices, reserve_indices}"""
    data = load_user_data()
    if "team_configs" not in data:
        data["team_configs"] = {}
    data["team_configs"][team_short] = config
    save_user_data(data)

def get_created_players():
    """Get list of user-created players."""
    data = load_user_data()
    return data.get("created_players", [])

def add_created_player(player):
    """Add a new user-created player and save."""
    data = load_user_data()
    if "created_players" not in data:
        data["created_players"] = []
    data["created_players"].append(player)
    save_user_data(data)
    return len(data["created_players"]) - 1  # Return index

def add_player_to_team(team_short, player_data):
    """Add a created player to a team's reserve pool."""
    data = load_user_data()
    configs = data.get("team_configs", {})
    tc = configs.get(team_short, {})
    if "extra_players" not in tc:
        tc["extra_players"] = []
    tc["extra_players"].append(player_data)
    configs[team_short] = tc
    data["team_configs"] = configs
    save_user_data(data)
