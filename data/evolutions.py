EVOLUTIONS_DB = [
    {
        "id": "founder_speed",
        "name": "Velocista Fundador",
        "desc": "La historia comienza con un paso al frente. Esta evolución está diseñada para aquellos pioneros que buscan romper líneas con una zancada eléctrica. Perfecta para convertir a un talento bruto en un relámpago imparable.",
        "icon": "⚡",
        "cost": 10000,
        "req": {
            "max_ovr": 85,
            "max_speed": 82
        },
        "levels": [
            {
                "obj_type": "matches",
                "obj_desc": "Forja el carácter: Juega 2 partidos en Ultimate Team.",
                "target": 2,
                "reward_stats": {"speed": 1},
                "reward_design": "EVO_PROGRESS"
            },
            {
                "obj_type": "goals",
                "obj_desc": "Instinto asesino: Anota 3 goles con este jugador.",
                "target": 3,
                "reward_stats": {"speed": 2},
                "reward_design": "EVO_SPEED"
            }
        ]
    },
    {
        "id": "midfield_general",
        "name": "General del Medio",
        "desc": "El campo de batalla se domina desde el círculo central. Mejora la visión periférica y la precisión quirúrgica de tus arquitectos del juego. Un general no corre, hace que el balón corra por él.",
        "icon": "🧭",
        "cost": 0,
        "req": {
            "max_ovr": 88,
            "pos": ["CM", "CDM", "CAM"]
        },
        "levels": [
            {
                "obj_type": "assists",
                "obj_desc": "Visión de águila: Asiste 1 gol con este jugador.",
                "target": 1,
                "reward_stats": {"passing": 1},
                "reward_design": "EVO_PROGRESS"
            },
            {
                "obj_type": "matches",
                "obj_desc": "Liderazgo silencioso: Juega 4 partidos con él en el once.",
                "target": 4,
                "reward_stats": {"passing": 1, "defense": 1},
                "reward_design": "EVO_MIDFIELD"
            }
        ]
    },
    {
        "id": "legendary_striker",
        "name": "Artillero Letal",
        "desc": "El gol es un arte, y esta evolución es el pincel. Convierte a un delantero ordinario en un verdugo despiadado frente a la portería. Cada disparo será una sentencia de muerte para el rival.",
        "icon": "🎯",
        "cost": 25000,
        "req": {
            "max_ovr": 90,
            "pos": ["ST", "CF", "LW", "RW"]
        },
        "levels": [
            {
                "obj_type": "goals",
                "obj_desc": "Sangre fría: Anota 4 goles con este jugador.",
                "target": 4,
                "reward_stats": {"shot": 1},
                "reward_design": "EVO_PROGRESS"
            },
            {
                "obj_type": "goals",
                "obj_desc": "Dominación total: Anota 6 goles más con este jugador.",
                "target": 6,
                "reward_stats": {"shot": 2, "speed": 1},
                "reward_design": "EVO_STRIKER"
            }
        ]
    },
    {
        "id": "classic_heritage",
        "name": "Herencia Clásica",
        "desc": "Regresa a las raíces del fútbol elegante. Esta evolución imbuye a los jóvenes talentos con la clase y el temple de los viejos maestros del balón. El estilo nunca pasa de moda.",
        "icon": "📜",
        "cost": 0,
        "req": {
            "max_ovr": 78,
            "max_speed": 75
        },
        "levels": [
            {
                "obj_type": "matches",
                "obj_desc": "Respeto a la historia: Juega 3 partidos (Evento Clásico).",
                "target": 3,
                "reward_stats": {"passing": 2, "shot": 1},
                "reward_design": "EVO_RETRO_1"
            },
            {
                "obj_type": "assists",
                "obj_desc": "Magia pura: Asiste 2 goles con elegancia suprema.",
                "target": 2,
                "reward_stats": {"passing": 3, "dribbling": 2},
                "reward_design": "EVO_RETRO_FINAL"
            }
        ]
    }
]

def check_evolution_eligibility(player, evo_id):
    import datetime
    # --- LÍMITE TEMPORAL PARA EVOLUCIONES DE LANZAMIENTO ---
    limited_evos = ["founder_speed", "midfield_general", "legendary_striker"]
    if evo_id in limited_evos:
        deadline = datetime.datetime(2026, 9, 26, 0, 0)
        if datetime.datetime.now() >= deadline:
            return False # Estas evoluciones específicas han expirado
            
    # --- LÍMITE TEMPORAL PARA NUEVOS EVENTOS (Bloqueados hasta 15:00 ET) ---
    if evo_id == "classic_heritage":
        start_time = datetime.datetime(2026, 9, 26, 15, 0)
        if datetime.datetime.now() < start_time:
            return False # Aún no disponible
    
    evo = next((e for e in EVOLUTIONS_DB if e["id"] == evo_id), None)
    if not evo: return False
    
    # Restricciones globales
    if player.get("ovr", 0) > 90: return False
    if "evolution" in player: return False # Ya está o estuvo en evolución
    
    req = evo["req"]
    if "max_ovr" in req and player.get("ovr", 0) > req["max_ovr"]: return False
    if "max_speed" in req and player.get("s", {}).get("speed", 0) > req["max_speed"]: return False
    if "pos" in req and player.get("pos", "") not in req["pos"]: return False
    
    return True
