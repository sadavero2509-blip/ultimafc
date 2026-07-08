import pygame
import math

# ─────────────────────────────────────────────────────────────
# Base de datos de equipos ficticios (inspirados en clubes reales)
# Cada equipo tiene: nombre, abreviatura, colores, stats
# ─────────────────────────────────────────────────────────────

TEAMS = [
    # --- ESPAÑA (ES) ---
    { "name": "FC Stellaris", "short": "STE", "primary": (163, 26, 81), "secondary": (36, 72, 155), "accent": (255, 205, 0), "league": "ES", "stats": {"speed": 85, "shot": 90, "defense": 70, "passing": 92}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Real Coronas", "short": "COR", "primary": (255, 255, 255), "secondary": (218, 165, 32), "accent": (0, 50, 120), "league": "ES", "stats": {"speed": 82, "shot": 88, "defense": 80, "passing": 85}, "badge_shape": "crown", "is_real_parody": True },
    { "name": "Athletic Osos", "short": "ATM", "primary": (200, 30, 30), "secondary": (255, 255, 255), "accent": (0, 50, 150), "league": "ES", "stats": {"speed": 80, "shot": 84, "defense": 88, "passing": 82}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Sevilla Giralda", "short": "SEV", "primary": (255, 255, 255), "secondary": (200, 30, 30), "accent": (200, 30, 30), "league": "ES", "stats": {"speed": 78, "shot": 80, "defense": 78, "passing": 78}, "badge_shape": "shield" },
    { "name": "Valencia Murcielagos", "short": "VLC", "primary": (255, 255, 255), "secondary": (20, 20, 20), "accent": (230, 100, 30), "league": "ES", "stats": {"speed": 78, "shot": 76, "defense": 76, "passing": 78}, "badge_shape": "shield" },
    { "name": "Amarillo Submarino", "short": "VLR", "primary": (255, 215, 0), "secondary": (0, 70, 150), "accent": (0, 70, 150), "league": "ES", "stats": {"speed": 76, "shot": 78, "defense": 74, "passing": 80}, "badge_shape": "shield" },
    { "name": "Sociedad San Seb", "short": "RSO", "primary": (255, 255, 255), "secondary": (0, 100, 200), "accent": (0, 100, 200), "league": "ES", "stats": {"speed": 75, "shot": 76, "defense": 78, "passing": 82}, "badge_shape": "shield" },
    { "name": "Real Béticos", "short": "BET", "primary": (0, 150, 70), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "ES", "stats": {"speed": 78, "shot": 79, "defense": 76, "passing": 80}, "badge_shape": "shield" },
    { "name": "Bilbao Leones", "short": "BIL", "primary": (200, 30, 30), "secondary": (255, 255, 255), "accent": (20, 20, 20), "league": "ES", "stats": {"speed": 82, "shot": 78, "defense": 80, "passing": 76}, "badge_shape": "shield" },
    { "name": "RC Periquitos", "short": "PERI", "primary": (36, 72, 155), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "ES", "stats": {"speed": 75, "shot": 74, "defense": 76, "passing": 75}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Vigo Celestes", "short": "CEL", "primary": (135, 206, 250), "secondary": (255, 255, 255), "accent": (0, 0, 100), "league": "ES", "stats": {"speed": 78, "shot": 78, "defense": 72, "passing": 80}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Rayo Valle", "short": "RAY", "primary": (255, 255, 255), "secondary": (200, 30, 30), "accent": (200, 30, 30), "league": "ES", "stats": {"speed": 76, "shot": 75, "defense": 72, "passing": 74}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Getafe Azules", "short": "GET", "primary": (0, 70, 150), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "ES", "stats": {"speed": 72, "shot": 72, "defense": 78, "passing": 74}, "badge_shape": "circle", "is_real_parody": True },
    { "name": "Girona Blancirrojos", "short": "GIR", "primary": (200, 30, 30), "secondary": (255, 255, 255), "accent": (200, 30, 30), "league": "ES", "stats": {"speed": 78, "shot": 80, "defense": 75, "passing": 80}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Pamplona Rojos", "short": "OSA", "primary": (200, 30, 30), "secondary": (20, 20, 20), "accent": (20, 20, 20), "league": "ES", "stats": {"speed": 75, "shot": 76, "defense": 78, "passing": 75}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Vitoria Albiazules", "short": "ALA", "primary": (0, 70, 150), "secondary": (255, 255, 255), "accent": (0, 70, 150), "league": "ES", "stats": {"speed": 74, "shot": 72, "defense": 76, "passing": 74}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Palma Bermellones", "short": "MAL", "primary": (200, 30, 30), "secondary": (20, 20, 20), "accent": (200, 30, 30), "league": "ES", "stats": {"speed": 74, "shot": 74, "defense": 78, "passing": 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Canarias Amarillos", "short": "LPA", "primary": (255, 215, 0), "secondary": (0, 70, 150), "accent": (0, 70, 150), "league": "ES", "stats": {"speed": 76, "shot": 72, "defense": 74, "passing": 78}, "badge_shape": "circle", "is_real_parody": True },
    { "name": "Pepinero FC", "short": "LEG", "primary": (255, 255, 255), "secondary": (0, 70, 150), "accent": (0, 70, 150), "league": "ES", "stats": {"speed": 72, "shot": 70, "defense": 74, "passing": 70}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Pucela Blanquivioletas", "short": "VLL", "primary": (138, 43, 226), "secondary": (255, 255, 255), "accent": (138, 43, 226), "league": "ES", "stats": {"speed": 74, "shot": 72, "defense": 72, "passing": 74}, "badge_shape": "shield", "is_real_parody": True },

    # --- INGLATERRA (EN) ---
    { "name": "United Devils", "short": "UDV", "primary": (210, 30, 30), "secondary": (255, 255, 255), "accent": (255, 215, 0), "league": "EN", "stats": {"speed": 80, "shot": 84, "defense": 78, "passing": 82}, "badge_shape": "diamond" },
    { "name": "Sky City FC", "short": "ALB", "primary": (108, 171, 221), "secondary": (255, 255, 255), "accent": (28, 45, 80), "league": "EN", "stats": {"speed": 84, "shot": 86, "defense": 74, "passing": 90}, "badge_shape": "circle", "is_elite": True },
    { "name": "London Gunners", "short": "ARS", "primary": (230, 30, 30), "secondary": (255, 255, 255), "accent": (218, 165, 32), "league": "EN", "stats": {"speed": 85, "shot": 85, "defense": 86, "passing": 88}, "badge_shape": "shield", "is_elite": True },
    { "name": "Merseyside Reds", "short": "LIV", "primary": (200, 20, 20), "secondary": (200, 20, 20), "accent": (255, 255, 255), "league": "EN", "stats": {"speed": 86, "shot": 88, "defense": 84, "passing": 84}, "badge_shape": "shield", "is_elite": True },
    { "name": "Blue Lions London", "short": "CHE", "primary": (0, 30, 150), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "EN", "stats": {"speed": 82, "shot": 80, "defense": 82, "passing": 80}, "badge_shape": "circle" },
    { "name": "Tottenham Spurs", "short": "TOT", "primary": (255, 255, 255), "secondary": (10, 20, 50), "accent": (10, 20, 50), "league": "EN", "stats": {"speed": 84, "shot": 82, "defense": 78, "passing": 82}, "badge_shape": "shield" },
    { "name": "West Ham Hammers", "short": "WHU", "primary": (120, 30, 60), "secondary": (0, 150, 200), "accent": (0, 150, 200), "league": "EN", "stats": {"speed": 78, "shot": 78, "defense": 76, "passing": 76}, "badge_shape": "shield" },
    { "name": "Aston Villanos", "short": "AVL", "primary": (100, 20, 50), "secondary": (150, 200, 255), "accent": (218, 165, 32), "league": "EN", "stats": {"speed": 82, "shot": 82, "defense": 78, "passing": 82}, "badge_shape": "shield" },
    { "name": "Newcastle Magpies", "short": "NEW", "primary": (20, 20, 20), "secondary": (255, 255, 255), "accent": (108, 171, 221), "league": "EN", "stats": {"speed": 84, "shot": 80, "defense": 80, "passing": 78}, "badge_shape": "shield" },
    { "name": "Foxes City", "short": "LEI", "primary": (0, 83, 160), "secondary": (255, 255, 255), "accent": (255, 215, 0), "league": "EN", "stats": {"speed": 82, "shot": 78, "defense": 75, "passing": 76}, "badge_shape": "circle", "is_real_parody": True },
    { "name": "Blue Mersey", "short": "EVE", "primary": (0, 51, 153), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "EN", "stats": {"speed": 76, "shot": 75, "defense": 82, "passing": 74}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Wolves FC", "short": "WOL", "primary": (255, 165, 0), "secondary": (20, 20, 20), "accent": (20, 20, 20), "league": "EN", "stats": {"speed": 80, "shot": 76, "defense": 78, "passing": 75}, "badge_shape": "circle", "is_real_parody": True },
    { "name": "Brighton Seagulls", "short": "BHA", "primary": (0, 87, 184), "secondary": (255, 255, 255), "accent": (255, 215, 0), "league": "EN", "stats": {"speed": 80, "shot": 78, "defense": 78, "passing": 82}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Brentford Bees", "short": "BRE", "primary": (200, 30, 30), "secondary": (255, 255, 255), "accent": (20, 20, 20), "league": "EN", "stats": {"speed": 78, "shot": 76, "defense": 76, "passing": 76}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Fulham Whites", "short": "FUL", "primary": (255, 255, 255), "secondary": (20, 20, 20), "accent": (200, 30, 30), "league": "EN", "stats": {"speed": 78, "shot": 76, "defense": 75, "passing": 78}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Crystal Eagles", "short": "CRY", "primary": (0, 35, 125), "secondary": (200, 30, 30), "accent": (255, 255, 255), "league": "EN", "stats": {"speed": 82, "shot": 74, "defense": 76, "passing": 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Bournemouth Cherries", "short": "BOU", "primary": (200, 30, 30), "secondary": (20, 20, 20), "accent": (255, 255, 255), "league": "EN", "stats": {"speed": 78, "shot": 76, "defense": 74, "passing": 76}, "badge_shape": "circle", "is_real_parody": True },
    { "name": "Forest Reds", "short": "NFO", "primary": (200, 30, 30), "secondary": (255, 255, 255), "accent": (255, 215, 0), "league": "EN", "stats": {"speed": 76, "shot": 74, "defense": 76, "passing": 74}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Southampton Saints", "short": "SOU", "primary": (200, 30, 30), "secondary": (255, 255, 255), "accent": (20, 20, 20), "league": "EN", "stats": {"speed": 74, "shot": 72, "defense": 72, "passing": 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Ipswich Tractors", "short": "IPS", "primary": (0, 65, 145), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "EN", "stats": {"speed": 74, "shot": 70, "defense": 72, "passing": 70}, "badge_shape": "shield", "is_real_parody": True },

    # --- ITALIA (IT) ---
    { "name": "AC Rossonero", "short": "ROS", "primary": (200, 30, 30), "secondary": (20, 20, 20), "accent": (255, 255, 255), "league": "IT", "stats": {"speed": 78, "shot": 82, "defense": 85, "passing": 80}, "badge_shape": "circle" },
    { "name": "Inter Nerazurro", "short": "AZZ", "primary": (0, 50, 140), "secondary": (20, 20, 20), "accent": (218, 165, 32), "league": "IT", "stats": {"speed": 79, "shot": 82, "defense": 86, "passing": 80}, "badge_shape": "circle" },
    { "name": "Zebra Torino", "short": "JUV", "primary": (255, 255, 255), "secondary": (20, 20, 20), "accent": (218, 165, 32), "league": "IT", "stats": {"speed": 82, "shot": 85, "defense": 85, "passing": 80}, "badge_shape": "shield" },
    { "name": "Napoli Vesubio", "short": "NAP", "primary": (0, 150, 255), "secondary": (255, 255, 255), "accent": (0, 50, 150), "league": "IT", "stats": {"speed": 85, "shot": 84, "defense": 78, "passing": 82}, "badge_shape": "circle" },
    { "name": "Roma Lobos", "short": "ROM", "primary": (130, 20, 40), "secondary": (255, 200, 0), "accent": (255, 200, 0), "league": "IT", "stats": {"speed": 80, "shot": 82, "defense": 80, "passing": 82}, "badge_shape": "circle" },
    { "name": "Lazio Eagles", "short": "LAZ", "primary": (150, 200, 255), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "IT", "stats": {"speed": 82, "shot": 80, "defense": 78, "passing": 80}, "badge_shape": "circle" },
    { "name": "Fiorentina Viola", "short": "FIO", "primary": (100, 0, 180), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "IT", "stats": {"speed": 76, "shot": 78, "defense": 74, "passing": 80}, "badge_shape": "circle" },
    { "name": "Atalanta Diosa", "short": "ATA", "primary": (0, 50, 120), "secondary": (20, 20, 20), "accent": (255, 255, 255), "league": "IT", "stats": {"speed": 80, "shot": 80, "defense": 82, "passing": 82}, "badge_shape": "circle" },
    { "name": "Bolonia Galgos", "short": "BOL_IT", "primary": (160, 30, 50), "secondary": (0, 40, 90), "accent": (255, 255, 255), "league": "IT", "stats": {"speed": 78, "shot": 76, "defense": 80, "passing": 78}, "badge_shape": "circle" },
    { "name": "Bulls Torino", "short": "TOR", "primary": (100, 0, 0), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "IT", "stats": {"speed": 75, "shot": 74, "defense": 82, "passing": 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Genoa Grifos", "short": "GEN", "primary": (150, 0, 0), "secondary": (0, 0, 100), "accent": (255, 215, 0), "league": "IT", "stats": {"speed": 76, "shot": 75, "defense": 78, "passing": 74}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Empoli Azules", "short": "EMP", "primary": (0, 50, 150), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "IT", "stats": {"speed": 74, "shot": 72, "defense": 75, "passing": 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Verona Giallo", "short": "VER", "primary": (255, 215, 0), "secondary": (0, 50, 120), "accent": (0, 50, 120), "league": "IT", "stats": {"speed": 75, "shot": 74, "defense": 74, "passing": 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Monza Corona", "short": "MONZ", "primary": (180, 20, 40), "secondary": (255, 255, 255), "accent": (218, 165, 32), "league": "IT", "stats": {"speed": 76, "shot": 74, "defense": 75, "passing": 76}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Udinese Cebras", "short": "UDI", "primary": (20, 20, 20), "secondary": (255, 255, 255), "accent": (218, 165, 32), "league": "IT", "stats": {"speed": 76, "shot": 75, "defense": 76, "passing": 74}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Lecce Lobos", "short": "LEC", "primary": (255, 215, 0), "secondary": (200, 20, 20), "accent": (0, 50, 120), "league": "IT", "stats": {"speed": 78, "shot": 74, "defense": 72, "passing": 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Cagliari Castillos", "short": "CAG", "primary": (150, 0, 20), "secondary": (0, 20, 70), "accent": (255, 255, 255), "league": "IT", "stats": {"speed": 74, "shot": 74, "defense": 75, "passing": 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Parma Cruzados", "short": "PARM", "primary": (255, 255, 255), "secondary": (20, 20, 20), "accent": (255, 215, 0), "league": "IT", "stats": {"speed": 76, "shot": 74, "defense": 75, "passing": 76}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Venezia Leones", "short": "VEN_IT", "primary": (0, 100, 60), "secondary": (255, 100, 0), "accent": (20, 20, 20), "league": "IT", "stats": {"speed": 75, "shot": 74, "defense": 72, "passing": 74}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Como Lagos", "short": "COM", "primary": (0, 80, 180), "secondary": (255, 255, 255), "accent": (218, 165, 32), "league": "IT", "stats": {"speed": 76, "shot": 74, "defense": 74, "passing": 76}, "badge_shape": "shield", "is_real_parody": True },

    # --- ALEMANIA (DE) ---
    { "name": "Bayern Stern", "short": "AJT", "primary": (220, 20, 60), "secondary": (255, 255, 255), "accent": (0, 50, 120), "league": "DE", "stats": {"speed": 86, "shot": 78, "defense": 70, "passing": 92}, "badge_shape": "circle" },
    { "name": "BV Schwarz-Gelb", "short": "BSG", "primary": (255, 215, 0), "secondary": (20, 20, 20), "accent": (255, 255, 255), "league": "DE", "stats": {"speed": 88, "shot": 80, "defense": 72, "passing": 85}, "badge_shape": "shield" },
    { "name": "Leverkusen Pillen", "short": "LEV", "primary": (200, 20, 20), "secondary": (20, 20, 20), "accent": (255, 255, 255), "league": "DE", "stats": {"speed": 86, "shot": 82, "defense": 80, "passing": 85}, "badge_shape": "shield" },
    { "name": "Leipzig Toros", "short": "RBL", "primary": (255, 255, 255), "secondary": (200, 20, 20), "accent": (0, 50, 150), "league": "DE", "stats": {"speed": 88, "shot": 80, "defense": 78, "passing": 80}, "badge_shape": "shield" },
    { "name": "Frankfurt Aguilas", "short": "SGE", "primary": (220, 20, 20), "secondary": (255, 255, 255), "accent": (20, 20, 20), "league": "DE", "stats": {"speed": 84, "shot": 78, "defense": 78, "passing": 80}, "badge_shape": "shield" },
    { "name": "Gladbach Foals", "short": "BMG", "primary": (255, 255, 255), "secondary": (20, 20, 20), "accent": (0, 150, 60), "league": "DE", "stats": {"speed": 78, "shot": 76, "defense": 75, "passing": 78}, "badge_shape": "shield" },
    { "name": "Wolfsburg Wolves", "short": "WOB", "primary": (0, 200, 50), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "DE", "stats": {"speed": 82, "shot": 75, "defense": 76, "passing": 74}, "badge_shape": "circle" },
    { "name": "Hoffenheim Aldea", "short": "HOF", "primary": (0, 100, 200), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "DE", "stats": {"speed": 80, "shot": 82, "defense": 74, "passing": 80}, "badge_shape": "circle" },
    { "name": "Union Ferreos", "short": "UNI", "primary": (200, 30, 30), "secondary": (255, 255, 255), "accent": (218, 165, 32), "league": "DE", "stats": {"speed": 78, "shot": 74, "defense": 82, "passing": 72}, "badge_shape": "shield" },
    { "name": "Stuttgart Suabos", "short": "STU", "primary": (255, 255, 255), "secondary": (200, 30, 30), "accent": (200, 30, 30), "league": "DE", "stats": {"speed": 82, "shot": 78, "defense": 78, "passing": 80}, "badge_shape": "shield" },
    { "name": "Bremen Verdes", "short": "SVW", "primary": (0, 150, 80), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "DE", "stats": {"speed": 78, "shot": 75, "defense": 72, "passing": 78}, "badge_shape": "diamond", "is_real_parody": True },
    { "name": "Gelsenkirchen 04", "short": "S04", "primary": (0, 80, 200), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "DE", "stats": {"speed": 74, "shot": 72, "defense": 75, "passing": 74}, "badge_shape": "circle", "is_real_parody": True },

    { "name": "Friburgo Selva Negra", "short": "FRE", "primary": (200, 30, 30), "secondary": (20, 20, 20), "accent": (255, 255, 255), "league": "DE", "stats": {"speed": 78, "shot": 76, "defense": 78, "passing": 76}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Augsburgo Fugger", "short": "AUG", "primary": (255, 255, 255), "secondary": (200, 30, 30), "accent": (0, 150, 50), "league": "DE", "stats": {"speed": 76, "shot": 75, "defense": 76, "passing": 74}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Maguncia Carnaval", "short": "MAI", "primary": (200, 30, 30), "secondary": (255, 255, 255), "accent": (200, 30, 30), "league": "DE", "stats": {"speed": 75, "shot": 74, "defense": 75, "passing": 76}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Bochum Azul", "short": "BOC", "primary": (0, 50, 150), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "DE", "stats": {"speed": 74, "shot": 72, "defense": 76, "passing": 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Heidenheim Castillos", "short": "HEI", "primary": (0, 50, 150), "secondary": (200, 30, 30), "accent": (255, 255, 255), "league": "DE", "stats": {"speed": 76, "shot": 74, "defense": 74, "passing": 75}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Piratas de Pauli", "short": "PAU", "primary": (139, 69, 19), "secondary": (255, 255, 255), "accent": (200, 30, 30), "league": "DE", "stats": {"speed": 74, "shot": 72, "defense": 72, "passing": 74}, "badge_shape": "circle", "is_real_parody": True },

    # --- FRANCIA (FR) ---
    { "name": "Olympique Lumière", "short": "OLY", "primary": (15, 30, 80), "secondary": (230, 100, 160), "accent": (255, 255, 255), "league": "FR", "stats": {"speed": 90, "shot": 92, "defense": 65, "passing": 88}, "badge_shape": "circle" },
    { "name": "Marseille Phocéen", "short": "OM", "primary": (255, 255, 255), "secondary": (0, 150, 255), "accent": (218, 165, 32), "league": "FR", "stats": {"speed": 82, "shot": 80, "defense": 76, "passing": 78}, "badge_shape": "circle" },
    { "name": "Lyon Leones", "short": "LYO", "primary": (255, 255, 255), "secondary": (200, 30, 30), "accent": (0, 50, 150), "league": "FR", "stats": {"speed": 80, "shot": 82, "defense": 75, "passing": 80}, "badge_shape": "shield" },
    # --- TURQUÍA (TR) ---
    { "name": "Lion Gold Istanbul", "short": "GAL", "primary": (200, 20, 20), "secondary": (255, 215, 0), "accent": (255, 255, 255), "league": "TR", "stats": {'speed': 82, 'shot': 83, 'defense': 78, 'passing': 80}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Canary Blue Istanbul", "short": "FEN", "primary": (0, 35, 125), "secondary": (255, 215, 0), "accent": (255, 255, 255), "league": "TR", "stats": {'speed': 80, 'shot': 80, 'defense': 79, 'passing': 81}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Eagle Black Istanbul", "short": "BES", "primary": (20, 20, 20), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "TR", "stats": {'speed': 79, 'shot': 79, 'defense': 77, 'passing': 78}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Burgundy Storm Trabzon", "short": "TRA", "primary": (128, 0, 32), "secondary": (135, 206, 235), "accent": (255, 255, 255), "league": "TR", "stats": {'speed': 77, 'shot': 76, 'defense': 75, 'passing': 76}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Owl City Istanbul", "short": "IBF", "primary": (255, 100, 0), "secondary": (0, 35, 125), "accent": (255, 255, 255), "league": "TR", "stats": {'speed': 75, 'shot': 74, 'defense': 74, 'passing': 73}, "badge_shape": "circle", "is_real_parody": True },
    { "name": "Green Eagles Konya", "short": "KON", "primary": (0, 100, 50), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "TR", "stats": {'speed': 72, 'shot': 71, 'defense': 72, 'passing': 71}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Scorpions Antalya", "short": "ANT", "primary": (200, 20, 20), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "TR", "stats": {'speed': 73, 'shot': 72, 'defense': 71, 'passing': 71}, "badge_shape": "circle", "is_real_parody": True },
    { "name": "Red Braves Sivas", "short": "SIV", "primary": (200, 20, 20), "secondary": (255, 255, 255), "accent": (20, 20, 20), "league": "TR", "stats": {'speed': 72, 'shot': 73, 'defense': 70, 'passing': 70}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Blue Lightning Adana", "short": "ADS", "primary": (135, 206, 235), "secondary": (0, 35, 125), "accent": (255, 255, 255), "league": "TR", "stats": {'speed': 74, 'shot': 73, 'defense': 69, 'passing': 71}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Navy Anchors Kasimpasa", "short": "KAS_TR", "primary": (0, 35, 125), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "TR", "stats": {'speed': 73, 'shot': 73, 'defense': 70, 'passing': 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Yellow Stars Göztepe", "short": "GOZ", "primary": (255, 215, 0), "secondary": (200, 20, 20), "accent": (255, 255, 255), "league": "TR", "stats": {'speed': 72, 'shot': 71, 'defense': 71, 'passing': 69}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Red Giants Samsun", "short": "SAM", "primary": (200, 20, 20), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "TR", "stats": {'speed': 73, 'shot': 72, 'defense': 71, 'passing': 72}, "badge_shape": "circle", "is_real_parody": True },
    { "name": "Lavender Giants Istanbul", "short": "EYU", "primary": (138, 43, 226), "secondary": (255, 255, 0), "accent": (255, 255, 255), "league": "TR", "stats": {'speed': 72, 'shot': 72, 'defense': 73, 'passing': 73}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Tea Storm Rize", "short": "RIZ", "primary": (30, 144, 255), "secondary": (0, 128, 0), "accent": (255, 255, 255), "league": "TR", "stats": {'speed': 71, 'shot': 71, 'defense': 71, 'passing': 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Falcons Gaziantep", "short": "GAZ", "primary": (200, 20, 20), "secondary": (20, 20, 20), "accent": (255, 255, 255), "league": "TR", "stats": {'speed': 71, 'shot': 71, 'defense': 70, 'passing': 71}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Orange Alanya", "short": "ALN", "primary": (255, 140, 0), "secondary": (30, 144, 255), "accent": (255, 255, 255), "league": "TR", "stats": {'speed': 72, 'shot': 71, 'defense': 71, 'passing': 71}, "badge_shape": "circle", "is_real_parody": True },
    { "name": "Bodrum Castle", "short": "BOD", "primary": (0, 128, 0), "secondary": (255, 255, 255), "accent": (30, 144, 255), "league": "TR", "stats": {'speed': 70, 'shot': 70, 'defense': 70, 'passing': 69}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Star Hatay", "short": "HAT", "primary": (178, 34, 34), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "TR", "stats": {'speed': 70, 'shot': 70, 'defense': 70, 'passing': 70}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Red Stars Kayseri", "short": "KAY", "primary": (200, 20, 20), "secondary": (255, 215, 0), "accent": (255, 255, 255), "league": "TR", "stats": {'speed': 71, 'shot': 71, 'defense': 71, 'passing': 71}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Monaco Princes", "short": "MON", "primary": (200, 20, 20), "secondary": (255, 255, 255), "accent": (218, 165, 32), "league": "FR", "stats": {"speed": 84, "shot": 82, "defense": 76, "passing": 82}, "badge_shape": "shield" },
    { "name": "Lille Dogos", "short": "LIL", "primary": (200, 20, 20), "secondary": (0, 30, 80), "accent": (255, 255, 255), "league": "FR", "stats": {"speed": 85, "shot": 78, "defense": 80, "passing": 78}, "badge_shape": "shield" },
    { "name": "Nice Riviers", "short": "NIC", "primary": (200, 20, 20), "secondary": (20, 20, 20), "accent": (20, 20, 20), "league": "FR", "stats": {"speed": 78, "shot": 75, "defense": 76, "passing": 76}, "badge_shape": "shield" },
    { "name": "Rennais Bretons", "short": "REN", "primary": (200, 20, 20), "secondary": (20, 20, 20), "accent": (255, 255, 255), "league": "FR", "stats": {"speed": 80, "shot": 76, "defense": 74, "passing": 78}, "badge_shape": "circle" },
    { "name": "Lens Sangre-Oro", "short": "LEN", "primary": (200, 20, 20), "secondary": (255, 215, 0), "accent": (20, 20, 20), "league": "FR", "stats": {"speed": 82, "shot": 78, "defense": 78, "passing": 76}, "badge_shape": "shield" },
    { "name": "Rois de Reims", "short": "RRE", "primary": (200, 20, 20), "secondary": (255, 255, 255), "accent": (218, 165, 32), "league": "FR", "stats": {"speed": 78, "shot": 76, "defense": 76, "passing": 75}, "badge_shape": "crown" },
    { "name": "Sainte Verts", "short": "STE_FR", "primary": (0, 150, 50), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "FR", "stats": {"speed": 74, "shot": 72, "defense": 78, "passing": 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Canaris de Nantes", "short": "NAN", "primary": (255, 215, 0), "secondary": (0, 150, 50), "accent": (0, 150, 50), "league": "FR", "stats": {"speed": 78, "shot": 74, "defense": 72, "passing": 76}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Pirates de Brest", "short": "BRE_FR", "primary": (200, 20, 20), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "FR", "stats": {"speed": 78, "shot": 76, "defense": 78, "passing": 76}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Toulouse Violettes", "short": "TOU", "primary": (100, 0, 100), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "FR", "stats": {"speed": 76, "shot": 74, "defense": 74, "passing": 75}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Montpellier Paillade", "short": "MON_FR", "primary": (0, 30, 100), "secondary": (255, 100, 0), "accent": (255, 100, 0), "league": "FR", "stats": {"speed": 75, "shot": 75, "defense": 72, "passing": 74}, "badge_shape": "circle", "is_real_parody": True },
    { "name": "Cigognes de Strasbourg", "short": "STR", "primary": (0, 100, 200), "secondary": (255, 255, 255), "accent": (0, 30, 100), "league": "FR", "stats": {"speed": 75, "shot": 72, "defense": 74, "passing": 74}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Ciel et Marine Le Havre", "short": "HAC", "primary": (135, 206, 250), "secondary": (0, 30, 100), "accent": (0, 30, 100), "league": "FR", "stats": {"speed": 74, "shot": 70, "defense": 75, "passing": 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Jeunesse d'Auxerre", "short": "AUX", "primary": (255, 255, 255), "secondary": (0, 100, 200), "accent": (0, 100, 200), "league": "FR", "stats": {"speed": 74, "shot": 72, "defense": 72, "passing": 74}, "badge_shape": "circle", "is_real_parody": True },
    { "name": "Noirs et Blancs d'Angers", "short": "ANG", "primary": (20, 20, 20), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "FR", "stats": {"speed": 72, "shot": 70, "defense": 72, "passing": 70}, "badge_shape": "shield", "is_real_parody": True },

    # --- PORTUGAL (PT) ---
    { "name": "Dragões Porto", "short": "DRP", "primary": (0, 70, 170), "secondary": (255, 255, 255), "accent": (218, 165, 32), "league": "PT", "stats": {"speed": 80, "shot": 80, "defense": 84, "passing": 78}, "badge_shape": "shield" },
    { "name": "Benfica Águilas", "short": "BEN", "primary": (200, 30, 30), "secondary": (255, 255, 255), "accent": (218, 165, 32), "league": "PT", "stats": {"speed": 82, "shot": 80, "defense": 78, "passing": 82}, "badge_shape": "shield" },
    { "name": "Sporting Leones", "short": "SPO", "primary": (0, 150, 50), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "PT", "stats": {"speed": 84, "shot": 82, "defense": 80, "passing": 80}, "badge_shape": "shield" },
    { "name": "Braga Guerreros", "short": "BRA_PT", "primary": (200, 30, 30), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "PT", "stats": {"speed": 78, "shot": 76, "defense": 78, "passing": 78}, "badge_shape": "shield" },
    { "name": "Vitoria Minho", "short": "VIT", "primary": (255, 255, 255), "secondary": (20, 20, 20), "accent": (20, 20, 20), "league": "PT", "stats": {"speed": 75, "shot": 74, "defense": 76, "passing": 75}, "badge_shape": "shield" },
    { "name": "Boavista Panteras", "short": "BOA", "primary": (255, 255, 255), "secondary": (20, 20, 20), "accent": (20, 20, 20), "league": "PT", "stats": {"speed": 74, "shot": 72, "defense": 74, "passing": 72}, "badge_shape": "shield" },
    { "name": "Rio Ave Boat", "short": "RAV", "primary": (0, 150, 60), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "PT", "stats": {"speed": 76, "shot": 70, "defense": 72, "passing": 74}, "badge_shape": "shield" },
    { "name": "Famalicao Azules", "short": "FAM", "primary": (255, 255, 255), "secondary": (0, 50, 120), "accent": (0, 50, 120), "league": "PT", "stats": {"speed": 76, "shot": 72, "defense": 72, "passing": 75}, "badge_shape": "shield" },
    { "name": "Gil Vicente Gallos", "short": "GVI", "primary": (200, 30, 30), "secondary": (0, 40, 100), "accent": (255, 255, 255), "league": "PT", "stats": {"speed": 75, "shot": 74, "defense": 70, "passing": 72}, "badge_shape": "shield" },
    { "name": "Vitoria Conquist", "short": "GUI", "primary": (255, 255, 255), "secondary": (20, 20, 20), "accent": (218, 165, 32), "league": "PT", "stats": {"speed": 78, "shot": 76, "defense": 78, "passing": 78}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Estoril Canarios", "short": "EST_PT", "primary": (255, 215, 0), "secondary": (0, 50, 150), "accent": (0, 50, 150), "league": "PT", "stats": {"speed": 80, "shot": 74, "defense": 70, "passing": 75}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Moreirense Verdes", "short": "MOR_PT", "primary": (0, 150, 50), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "PT", "stats": {"speed": 74, "shot": 72, "defense": 74, "passing": 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Arouca Lobos", "short": "ARO", "primary": (255, 215, 0), "secondary": (0, 50, 150), "accent": (0, 50, 150), "league": "PT", "stats": {"speed": 75, "shot": 74, "defense": 72, "passing": 74}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Casa Pia Gansos", "short": "CAS", "primary": (20, 20, 20), "secondary": (255, 255, 255), "accent": (200, 20, 20), "league": "PT", "stats": {"speed": 72, "shot": 70, "defense": 75, "passing": 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Farense Leones", "short": "FAR_PT", "primary": (20, 20, 20), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "PT", "stats": {"speed": 74, "shot": 72, "defense": 70, "passing": 70}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Estrela Tricolor", "short": "ESTR", "primary": (200, 30, 30), "secondary": (0, 100, 50), "accent": (255, 255, 255), "league": "PT", "stats": {"speed": 75, "shot": 72, "defense": 72, "passing": 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Santa Clara Açores", "short": "SCL", "primary": (200, 20, 20), "secondary": (255, 255, 255), "accent": (218, 165, 32), "league": "PT", "stats": {"speed": 76, "shot": 74, "defense": 72, "passing": 74}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Nacional Alvinegros", "short": "NAC_PT", "primary": (20, 20, 20), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "PT", "stats": {"speed": 74, "shot": 72, "defense": 70, "passing": 72}, "badge_shape": "shield", "is_real_parody": True },

    # --- ARGENTINA (AR) ---
    { "name": "Boca Tempest", "short": "CON", "primary": (0, 40, 104), "secondary": (255, 215, 0), "accent": (255, 255, 255), "league": "AR", "stats": {"speed": 76, "shot": 78, "defense": 88, "passing": 75}, "badge_shape": "shield" },
    { "name": "Rio Plate", "short": "RIV", "primary": (255, 255, 255), "secondary": (200, 30, 30), "accent": (200, 30, 30), "league": "AR", "stats": {"speed": 78, "shot": 80, "defense": 76, "passing": 82}, "badge_shape": "shield" },
    { "name": "Racing Academia", "short": "RAC", "primary": (108, 171, 221), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "AR", "stats": {"speed": 76, "shot": 75, "defense": 78, "passing": 76}, "badge_shape": "shield" },
    { "name": "Independiente Diablos", "short": "IND", "primary": (200, 20, 20), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "AR", "stats": {"speed": 75, "shot": 76, "defense": 74, "passing": 76}, "badge_shape": "shield" },
    { "name": "San Lorenzo Santos", "short": "SLO", "primary": (0, 30, 100), "secondary": (200, 20, 20), "accent": (255, 255, 255), "league": "AR", "stats": {"speed": 74, "shot": 74, "defense": 78, "passing": 74}, "badge_shape": "circle" },
    { "name": "Velez El Fortin", "short": "VEL", "primary": (255, 255, 255), "secondary": (0, 40, 120), "accent": (0, 40, 120), "league": "AR", "stats": {"speed": 72, "shot": 70, "defense": 74, "passing": 74}, "badge_shape": "shield" },
    { "name": "Pincha La Plata", "short": "EST", "primary": (200, 20, 20), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "AR", "stats": {"speed": 70, "shot": 74, "defense": 76, "passing": 72}, "badge_shape": "shield" },
    { "name": "Talleres Matadores", "short": "TAL", "primary": (255, 255, 255), "secondary": (0, 40, 100), "accent": (0, 40, 100), "league": "AR", "stats": {"speed": 80, "shot": 76, "defense": 75, "passing": 78}, "badge_shape": "shield" },
    { "name": "Huracán Globos", "short": "HUR", "primary": (255, 255, 255), "secondary": (200, 30, 30), "accent": (200, 30, 30), "league": "AR", "stats": {"speed": 76, "shot": 75, "defense": 74, "passing": 74}, "badge_shape": "circle" },
    { "name": "Nacional Tricolor", "short": "NAC", "primary": (255, 255, 255), "secondary": (0, 30, 100), "accent": (200, 30, 30), "league": "AR", "stats": {"speed": 78, "shot": 76, "defense": 76, "passing": 74}, "badge_shape": "shield" },
    { "name": "Rosario Canallas", "short": "ROS_AR", "primary": (0, 50, 150), "secondary": (255, 215, 0), "accent": (255, 215, 0), "league": "AR", "stats": {"speed": 75, "shot": 78, "defense": 74, "passing": 76}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Lepra Rosario", "short": "NEW_AR", "primary": (200, 20, 20), "secondary": (20, 20, 20), "accent": (255, 255, 255), "league": "AR", "stats": {"speed": 76, "shot": 76, "defense": 72, "passing": 78}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Halcón Varela", "short": "DEF", "primary": (255, 215, 0), "secondary": (0, 100, 45), "accent": (0, 100, 45), "league": "AR", "stats": {"speed": 75, "shot": 74, "defense": 72, "passing": 76}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Semillero Juniors", "short": "ARG_JR", "primary": (200, 20, 20), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "AR", "stats": {"speed": 76, "shot": 75, "defense": 74, "passing": 78}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Granate Lanús", "short": "LAN", "primary": (120, 30, 60), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "AR", "stats": {"speed": 75, "shot": 76, "defense": 74, "passing": 76}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Taladro Banfield", "short": "BAN", "primary": (0, 100, 50), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "AR", "stats": {"speed": 74, "shot": 72, "defense": 75, "passing": 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Lobo La Plata", "short": "GELP", "primary": (255, 255, 255), "secondary": (0, 30, 100), "accent": (0, 30, 100), "league": "AR", "stats": {"speed": 74, "shot": 72, "defense": 74, "passing": 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Piratas Alberdi", "short": "BEL_AR", "primary": (135, 206, 250), "secondary": (255, 255, 255), "accent": (0, 35, 125), "league": "AR", "stats": {"speed": 75, "shot": 74, "defense": 75, "passing": 74}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Tomba Mendoza", "short": "GOD", "primary": (0, 50, 150), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "AR", "stats": {"speed": 76, "shot": 75, "defense": 76, "passing": 75}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Tatengue Unión", "short": "USF", "primary": (200, 20, 20), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "AR", "stats": {"speed": 74, "shot": 72, "defense": 72, "passing": 74}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Calamar Vicente López", "short": "PLA", "primary": (139, 69, 19), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "AR", "stats": {"speed": 72, "shot": 72, "defense": 76, "passing": 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "La Gloria Cordobesa", "short": "INS", "primary": (200, 20, 20), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "AR", "stats": {"speed": 75, "shot": 72, "defense": 72, "passing": 74}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Decano Tucumán", "short": "ATU", "primary": (135, 206, 250), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "AR", "stats": {"speed": 74, "shot": 75, "defense": 72, "passing": 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Matador Victoria", "short": "TIG", "primary": (0, 50, 150), "secondary": (200, 20, 20), "accent": (255, 255, 255), "league": "AR", "stats": {"speed": 75, "shot": 74, "defense": 72, "passing": 74}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Guapo Barracas", "short": "BAR", "primary": (200, 20, 20), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "AR", "stats": {"speed": 72, "shot": 72, "defense": 74, "passing": 70}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Speed Riestra", "short": "RIE", "primary": (20, 20, 20), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "AR", "stats": {"speed": 72, "shot": 70, "defense": 75, "passing": 68}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Verde Junín", "short": "SAR", "primary": (0, 100, 50), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "AR", "stats": {"speed": 72, "shot": 72, "defense": 74, "passing": 70}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Ferroviario Santiago", "short": "CCV", "primary": (20, 20, 20), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "AR", "stats": {"speed": 74, "shot": 72, "defense": 72, "passing": 72}, "badge_shape": "shield", "is_real_parody": True },

    # --- BRASIL (BR) ---
    { "name": "Palmeiros Verdão", "short": "SVR", "primary": (0, 100, 45), "secondary": (255, 255, 255), "accent": (218, 165, 32), "league": "BR", "stats": {"speed": 82, "shot": 76, "defense": 82, "passing": 80}, "badge_shape": "shield" },
    { "name": "Flamengo Rubro", "short": "FLA", "primary": (200, 20, 20), "secondary": (20, 20, 20), "accent": (255, 255, 255), "league": "BR", "stats": {"speed": 82, "shot": 84, "defense": 75, "passing": 80}, "badge_shape": "shield" },
    { "name": "Sao Paulo Tricolor", "short": "SAO", "primary": (255, 255, 255), "secondary": (200, 20, 20), "accent": (20, 20, 20), "league": "BR", "stats": {"speed": 78, "shot": 76, "defense": 78, "passing": 80}, "badge_shape": "shield" },
    { "name": "Gremio Imortal", "short": "GRE_BR", "primary": (0, 150, 255), "secondary": (20, 20, 20), "accent": (255, 255, 255), "league": "BR", "stats": {"speed": 79, "shot": 76, "defense": 80, "passing": 78}, "badge_shape": "circle" },
    { "name": "Corinthians Timao", "short": "COR_BR", "primary": (255, 255, 255), "secondary": (20, 20, 20), "accent": (20, 20, 20), "league": "BR", "stats": {"speed": 78, "shot": 75, "defense": 82, "passing": 76}, "badge_shape": "circle" },
    { "name": "Cruzeiro Raposa", "short": "CRU", "primary": (0, 80, 180), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "BR", "stats": {"speed": 74, "shot": 72, "defense": 76, "passing": 74}, "badge_shape": "shield" },
    { "name": "Internacional Colorado", "short": "INT", "primary": (200, 20, 20), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "BR", "stats": {"speed": 75, "shot": 74, "defense": 78, "passing": 72}, "badge_shape": "circle" },
    { "name": "Botafogo Estrella", "short": "BOT", "primary": (20, 20, 20), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "BR", "stats": {"speed": 82, "shot": 80, "defense": 78, "passing": 78}, "badge_shape": "shield" },
    { "name": "Fortaleza Leones", "short": "FOR", "primary": (200, 30, 30), "secondary": (0, 50, 150), "accent": (255, 255, 255), "league": "BR", "stats": {"speed": 78, "shot": 76, "defense": 76, "passing": 74}, "badge_shape": "shield" },
    { "name": "Vasco Cruzados", "short": "VAS", "primary": (20, 20, 20), "secondary": (255, 255, 255), "accent": (200, 20, 20), "league": "BR", "stats": {"speed": 74, "shot": 72, "defense": 78, "passing": 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Flu Tricolor", "short": "FLU", "primary": (120, 30, 50), "secondary": (0, 100, 45), "accent": (255, 255, 255), "league": "BR", "stats": {"speed": 78, "shot": 78, "defense": 74, "passing": 82}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Furacão", "short": "CAP", "primary": (200, 20, 20), "secondary": (20, 20, 20), "accent": (20, 20, 20), "league": "BR", "stats": {"speed": 78, "shot": 76, "defense": 78, "passing": 74}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Tricolor Bahía", "short": "BAH", "primary": (0, 30, 120), "secondary": (255, 255, 255), "accent": (200, 20, 20), "league": "BR", "stats": {"speed": 76, "shot": 75, "defense": 74, "passing": 78}, "badge_shape": "circle", "is_real_parody": True },

    # --- COLOMBIA (CO) ---
    { "name": "Atletico Verdolaga", "short": "NAL", "primary": (0, 130, 60), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "CO", "stats": {"speed": 76, "shot": 74, "defense": 75, "passing": 78}, "badge_shape": "shield" },
    { "name": "Blue Millionaires", "short": "MIL", "primary": (0, 70, 150), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "CO", "stats": {"speed": 74, "shot": 75, "defense": 76, "passing": 79}, "badge_shape": "shield" },
    { "name": "Junior Tiburones", "short": "JUN", "primary": (200, 30, 30), "secondary": (255, 255, 255), "accent": (0, 50, 120), "league": "CO", "stats": {"speed": 82, "shot": 78, "defense": 70, "passing": 75}, "badge_shape": "shield" },
    { "name": "Red Devils Cali", "short": "AME", "primary": (210, 20, 20), "secondary": (210, 20, 20), "accent": (255, 255, 255), "league": "CO", "stats": {"speed": 78, "shot": 76, "defense": 72, "passing": 74}, "badge_shape": "shield" },
    { "name": "Leopardos Bucaram", "short": "BUC", "primary": (255, 215, 0), "secondary": (0, 100, 45), "accent": (0, 100, 45), "league": "CO", "stats": {"speed": 74, "shot": 72, "defense": 76, "passing": 70}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Matecañas Pereira", "short": "PER_CO", "primary": (255, 215, 0), "secondary": (200, 20, 20), "accent": (200, 20, 20), "league": "CO", "stats": {"speed": 75, "shot": 74, "defense": 72, "passing": 72}, "badge_shape": "circle", "is_real_parody": True },
    { "name": "Tolima Vinotinto", "short": "TOL", "primary": (120, 30, 60), "secondary": (255, 215, 0), "accent": (255, 215, 0), "league": "CO", "stats": {"speed": 76, "shot": 76, "defense": 75, "passing": 74}, "badge_shape": "shield" },
    { "name": "Once Blancos", "short": "ONC", "primary": (255, 255, 255), "secondary": (20, 20, 20), "accent": (0, 150, 60), "league": "CO", "stats": {"speed": 74, "shot": 72, "defense": 76, "passing": 72}, "badge_shape": "shield" },
    { "name": "Santa Fe Cardenales", "short": "SFE", "primary": (220, 20, 20), "secondary": (255, 255, 255), "accent": (255, 215, 0), "league": "CO", "stats": {"speed": 74, "shot": 74, "defense": 76, "passing": 74}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Azucareros Cali", "short": "CAL", "primary": (0, 100, 50), "secondary": (255, 255, 255), "accent": (0, 100, 50), "league": "CO", "stats": {"speed": 74, "shot": 74, "defense": 74, "passing": 75}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Poderoso Medellin", "short": "DIM", "primary": (200, 20, 20), "secondary": (0, 50, 150), "accent": (0, 50, 150), "league": "CO", "stats": {"speed": 76, "shot": 74, "defense": 75, "passing": 74}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Aseguradores Equidad", "short": "EQU", "primary": (50, 205, 50), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "CO", "stats": {"speed": 74, "shot": 72, "defense": 75, "passing": 73}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Dorados Rionegro", "short": "AGU", "primary": (212, 175, 55), "secondary": (20, 20, 20), "accent": (212, 175, 55), "league": "CO", "stats": {"speed": 76, "shot": 74, "defense": 74, "passing": 75}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Envigado Naranjas", "short": "ENV", "primary": (255, 100, 0), "secondary": (0, 150, 60), "accent": (255, 255, 255), "league": "CO", "stats": {"speed": 78, "shot": 72, "defense": 70, "passing": 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Volcánicos Pasto", "short": "PAS", "primary": (0, 50, 150), "secondary": (200, 20, 20), "accent": (255, 215, 0), "league": "CO", "stats": {"speed": 74, "shot": 74, "defense": 72, "passing": 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Ajedrezados Boyaca", "short": "CHI_CO", "primary": (20, 20, 20), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "CO", "stats": {"speed": 72, "shot": 70, "defense": 72, "passing": 70}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Alianza Caciques", "short": "ALI", "primary": (255, 215, 0), "secondary": (20, 20, 20), "accent": (255, 215, 0), "league": "CO", "stats": {"speed": 74, "shot": 72, "defense": 72, "passing": 72}, "badge_shape": "circle", "is_real_parody": True },
    { "name": "Felinos Cordoba", "short": "JAG", "primary": (0, 150, 200), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "CO", "stats": {"speed": 76, "shot": 72, "defense": 70, "passing": 70}, "badge_shape": "circle", "is_real_parody": True },
    { "name": "Lanceros Patriotas", "short": "PAT", "primary": (200, 20, 20), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "CO", "stats": {"speed": 72, "shot": 70, "defense": 72, "passing": 70}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Fortaleza Bogota", "short": "FOR_CO", "primary": (0, 70, 150), "secondary": (200, 20, 20), "accent": (255, 255, 255), "league": "CO", "stats": {"speed": 76, "shot": 72, "defense": 72, "passing": 74}, "badge_shape": "shield", "is_real_parody": True },

    # --- ESTADOS UNIDOS (US) ---
    { "name": "Miami Pink", "short": "MIA", "primary": (255, 100, 200), "secondary": (20, 20, 20), "accent": (255, 255, 255), "league": "US", "stats": {"speed": 82, "shot": 88, "defense": 70, "passing": 85}, "badge_shape": "circle", "is_real_parody": True },
    { "name": "Columbus Gold", "short": "CLB", "primary": (255, 215, 0), "secondary": (20, 20, 20), "accent": (20, 20, 20), "league": "US", "stats": {"speed": 78, "shot": 80, "defense": 78, "passing": 82}, "badge_shape": "shield" },
    { "name": "LA Golden Wings", "short": "LAF", "primary": (20, 20, 20), "secondary": (218, 165, 32), "accent": (218, 165, 32), "league": "US", "stats": {"speed": 85, "shot": 82, "defense": 78, "passing": 80}, "badge_shape": "shield" },
    { "name": "LA Galaxy Stars", "short": "LAG", "primary": (255, 255, 255), "secondary": (0, 35, 125), "accent": (255, 215, 0), "league": "US", "stats": {"speed": 80, "shot": 82, "defense": 75, "passing": 82}, "badge_shape": "shield" },
    { "name": "Seattle Green", "short": "SEA", "primary": (100, 200, 0), "secondary": (0, 50, 150), "accent": (255, 255, 255), "league": "US", "stats": {"speed": 76, "shot": 76, "defense": 82, "passing": 78}, "badge_shape": "shield" },
    { "name": "NY Bulls", "short": "NYR", "primary": (200, 20, 20), "secondary": (255, 255, 255), "accent": (218, 165, 32), "league": "US", "stats": {"speed": 84, "shot": 74, "defense": 76, "passing": 75}, "badge_shape": "circle" },
    { "name": "NY Sky Blue", "short": "NYC", "primary": (135, 206, 250), "secondary": (255, 255, 255), "accent": (0, 35, 125), "league": "US", "stats": {"speed": 78, "shot": 75, "defense": 74, "passing": 82}, "badge_shape": "circle" },
    { "name": "Atlanta Red", "short": "ATL", "primary": (130, 20, 40), "secondary": (20, 20, 20), "accent": (218, 165, 32), "league": "US", "stats": {"speed": 82, "shot": 80, "defense": 72, "passing": 78}, "badge_shape": "circle" },
    { "name": "Cincinnati Orange", "short": "CIN", "primary": (255, 100, 0), "secondary": (0, 35, 125), "accent": (255, 255, 255), "league": "US", "stats": {"speed": 78, "shot": 82, "defense": 76, "passing": 80}, "badge_shape": "shield" },
    { "name": "Philadelphia Snakes", "short": "PHI", "primary": (10, 30, 60), "secondary": (218, 165, 32), "accent": (255, 255, 255), "league": "US", "stats": {"speed": 75, "shot": 76, "defense": 82, "passing": 78}, "badge_shape": "circle" },
    { "name": "Orlando Purple", "short": "ORL", "primary": (100, 0, 180), "secondary": (255, 215, 0), "accent": (255, 215, 0), "league": "US", "stats": {"speed": 80, "shot": 78, "defense": 74, "passing": 78}, "badge_shape": "shield" },
    { "name": "Portland Lumber", "short": "PDX", "primary": (0, 100, 50), "secondary": (255, 215, 0), "accent": (255, 215, 0), "league": "US", "stats": {"speed": 78, "shot": 80, "defense": 72, "passing": 76}, "badge_shape": "shield" },
    { "name": "Houston Orange", "short": "HOU", "primary": (255, 100, 0), "secondary": (20, 20, 20), "accent": (255, 255, 255), "league": "US", "stats": {"speed": 76, "shot": 74, "defense": 78, "passing": 78}, "badge_shape": "shield" },
    { "name": "Dallas Red", "short": "DAL", "primary": (200, 20, 20), "secondary": (0, 35, 125), "accent": (255, 255, 255), "league": "US", "stats": {"speed": 80, "shot": 72, "defense": 74, "passing": 75}, "badge_shape": "shield" },
    { "name": "St. Louis Arch", "short": "STL", "primary": (200, 20, 80), "secondary": (10, 30, 60), "accent": (255, 255, 255), "league": "US", "stats": {"speed": 78, "shot": 76, "defense": 74, "passing": 74}, "badge_shape": "shield" },
    { "name": "Nashville Yellow", "short": "NSH", "primary": (255, 215, 0), "secondary": (10, 30, 60), "accent": (10, 30, 60), "league": "US", "stats": {"speed": 74, "shot": 78, "defense": 82, "passing": 74}, "badge_shape": "circle" },
    { "name": "New England Blue", "short": "NE", "primary": (10, 30, 60), "secondary": (200, 20, 20), "accent": (255, 255, 255), "league": "US", "stats": {"speed": 75, "shot": 74, "defense": 76, "passing": 78}, "badge_shape": "shield" },
    { "name": "Toronto Reds", "short": "TOR_US", "primary": (200, 20, 20), "secondary": (120, 120, 120), "accent": (255, 255, 255), "league": "US", "stats": {"speed": 72, "shot": 75, "defense": 70, "passing": 76}, "badge_shape": "shield" },
    { "name": "Montreal Blue", "short": "MTL", "primary": (20, 20, 20), "secondary": (0, 100, 200), "accent": (255, 255, 255), "league": "US", "stats": {"speed": 72, "shot": 72, "defense": 74, "passing": 74}, "badge_shape": "circle" },
    { "name": "Vancouver Snow", "short": "VAN", "primary": (255, 255, 255), "secondary": (10, 30, 60), "accent": (150, 200, 255), "league": "US", "stats": {"speed": 74, "shot": 74, "defense": 76, "passing": 72}, "badge_shape": "shield" },

    # --- JAPÓN (JP) ---
    { "name": "Kobe Harbor", "short": "KOB", "primary": (130, 20, 40), "secondary": (255, 255, 255), "accent": (20, 20, 20), "league": "JP", "stats": {"speed": 78, "shot": 82, "defense": 78, "passing": 80}, "badge_shape": "shield" },
    { "name": "Yokohama Anchors", "short": "YOK", "primary": (0, 35, 125), "secondary": (255, 255, 255), "accent": (200, 20, 20), "league": "JP", "stats": {"speed": 82, "shot": 78, "defense": 74, "passing": 82}, "badge_shape": "circle" },
    { "name": "Kawasaki Blue", "short": "KAW", "primary": (0, 150, 255), "secondary": (20, 20, 20), "accent": (255, 255, 255), "league": "JP", "stats": {"speed": 80, "shot": 76, "defense": 78, "passing": 85}, "badge_shape": "shield" },
    { "name": "Urawa Jewels", "short": "URA", "primary": (200, 20, 20), "secondary": (20, 20, 20), "accent": (255, 255, 255), "league": "JP", "stats": {"speed": 76, "shot": 78, "defense": 82, "passing": 76}, "badge_shape": "diamond" },
    { "name": "Hiroshima Purple", "short": "HIR", "primary": (100, 0, 150), "secondary": (255, 255, 255), "accent": (255, 215, 0), "league": "JP", "stats": {"speed": 75, "shot": 76, "defense": 80, "passing": 78}, "badge_shape": "shield" },
    { "name": "Tokyo Tech", "short": "TOK", "primary": (0, 50, 150), "secondary": (200, 20, 20), "accent": (255, 255, 255), "league": "JP", "stats": {"speed": 80, "shot": 74, "defense": 76, "passing": 78}, "badge_shape": "shield" },
    { "name": "Nagoya Orcas", "short": "NAG", "primary": (200, 20, 20), "secondary": (255, 215, 0), "accent": (20, 20, 20), "league": "JP", "stats": {"speed": 82, "shot": 78, "defense": 78, "passing": 74}, "badge_shape": "circle" },
    { "name": "Osaka Blue", "short": "GAM", "primary": (0, 50, 150), "secondary": (20, 20, 20), "accent": (255, 255, 255), "league": "JP", "stats": {"speed": 78, "shot": 74, "defense": 78, "passing": 80}, "badge_shape": "shield" },
    { "name": "Osaka Pink", "short": "CER", "primary": (255, 100, 180), "secondary": (0, 0, 80), "accent": (255, 255, 255), "league": "JP", "stats": {"speed": 80, "shot": 76, "defense": 75, "passing": 78}, "badge_shape": "shield" },
    { "name": "Kashima Horns", "short": "KAS", "primary": (150, 0, 0), "secondary": (20, 20, 20), "accent": (255, 215, 0), "league": "JP", "stats": {"speed": 76, "shot": 78, "defense": 80, "passing": 76}, "badge_shape": "shield" },
    { "name": "Fukuoka Bees", "short": "FUK", "primary": (0, 50, 100), "secondary": (200, 255, 0), "accent": (255, 255, 255), "league": "JP", "stats": {"speed": 75, "shot": 72, "defense": 78, "passing": 74}, "badge_shape": "shield" },
    { "name": "Sapporo Snow", "short": "SAP", "primary": (200, 20, 20), "secondary": (20, 20, 20), "accent": (255, 255, 255), "league": "JP", "stats": {"speed": 78, "shot": 75, "defense": 72, "passing": 74}, "badge_shape": "shield" },
    { "name": "Shonan Sea", "short": "SHO", "primary": (100, 255, 0), "secondary": (0, 100, 200), "accent": (255, 255, 255), "league": "JP", "stats": {"speed": 82, "shot": 72, "defense": 70, "passing": 72}, "badge_shape": "shield" },
    { "name": "Kyoto Purple", "short": "KYO", "primary": (100, 0, 100), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "JP", "stats": {"speed": 74, "shot": 72, "defense": 76, "passing": 75}, "badge_shape": "shield" },
    { "name": "Tosu Blue", "short": "TOS", "primary": (100, 200, 255), "secondary": (255, 100, 200), "accent": (255, 255, 255), "league": "JP", "stats": {"speed": 78, "shot": 72, "defense": 74, "passing": 72}, "badge_shape": "shield" },
    { "name": "Albirex Orange", "short": "ALB_JP", "primary": (255, 120, 0), "secondary": (0, 50, 150), "accent": (255, 255, 255), "league": "JP", "stats": {"speed": 76, "shot": 74, "defense": 74, "passing": 76}, "badge_shape": "shield" },
    { "name": "Kashiwa Sun", "short": "KSW", "primary": (255, 255, 0), "secondary": (20, 20, 20), "accent": (20, 20, 20), "league": "JP", "stats": {"speed": 78, "shot": 75, "defense": 75, "passing": 76}, "badge_shape": "shield" },
    { "name": "Machida Sky", "short": "MAC", "primary": (0, 100, 200), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "JP", "stats": {"speed": 82, "shot": 76, "defense": 80, "passing": 74}, "badge_shape": "shield" },
    { "name": "Tokyo Green", "short": "TGV", "primary": (0, 120, 60), "secondary": (255, 255, 255), "accent": (218, 165, 32), "league": "JP", "stats": {"speed": 76, "shot": 74, "defense": 74, "passing": 76}, "badge_shape": "shield" },
    { "name": "Iwata Blue", "short": "JWI", "primary": (135, 206, 250), "secondary": (255, 255, 255), "accent": (20, 20, 20), "league": "JP", "stats": {"speed": 75, "shot": 72, "defense": 74, "passing": 78}, "badge_shape": "shield" },
    
    # --- ÁFRICA (AF) ---
    { "name": "Pharaohs Cairo", "short": "AHL", "primary": (200, 20, 20), "secondary": (255, 215, 0), "accent": (255, 255, 255), "league": "AF", "stats": {"speed": 78, "shot": 80, "defense": 76, "passing": 78}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Casablanca Red", "short": "WYD", "primary": (200, 20, 20), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "AF", "stats": {"speed": 76, "shot": 75, "defense": 78, "passing": 74}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Pretoria Sun", "short": "MSD", "primary": (255, 215, 0), "secondary": (0, 35, 125), "accent": (0, 100, 50), "league": "AF", "stats": {"speed": 82, "shot": 76, "defense": 74, "passing": 80}, "badge_shape": "circle", "is_real_parody": True },
    { "name": "Tunis Gold", "short": "EST_AF", "primary": (200, 20, 20), "secondary": (255, 215, 0), "accent": (20, 20, 20), "league": "AF", "stats": {"speed": 75, "shot": 74, "defense": 76, "passing": 75}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Lubumbashi Ravens", "short": "TPM", "primary": (20, 20, 20), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "AF", "stats": {"speed": 74, "shot": 76, "defense": 72, "passing": 74}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Casablanca Green", "short": "RAJ", "primary": (0, 100, 50), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "AF", "stats": {"speed": 76, "shot": 74, "defense": 75, "passing": 76}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Cairo White", "short": "ZAM", "primary": (255, 255, 255), "secondary": (200, 20, 20), "accent": (200, 20, 20), "league": "AF", "stats": {"speed": 77, "shot": 75, "defense": 74, "passing": 78}, "badge_shape": "circle", "is_real_parody": True },
    { "name": "Soweto Pirates", "short": "ORL_AF", "primary": (20, 20, 20), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "AF", "stats": {"speed": 80, "shot": 74, "defense": 72, "passing": 72}, "badge_shape": "shield", "is_real_parody": True },

    # --- BÉLGICA (BE) ---
    { "name": "Blue Crown Brugge", "short": "BRU", "primary": (0, 50, 150), "secondary": (20, 20, 20), "accent": (255, 255, 255), "league": "BE", "stats": {"speed": 77, "shot": 76, "defense": 76, "passing": 78}, "badge_shape": "crown", "is_real_parody": True },
    { "name": "Purple Royals Anderlecht", "short": "AND", "primary": (100, 0, 150), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "BE", "stats": {"speed": 76, "shot": 77, "defense": 75, "passing": 77}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Blue Miners Genk", "short": "GNK", "primary": (0, 100, 200), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "BE", "stats": {"speed": 78, "shot": 75, "defense": 74, "passing": 76}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Indian Buffaloes Gent", "short": "GNT", "primary": (0, 70, 150), "secondary": (255, 255, 255), "accent": (218, 165, 32), "league": "BE", "stats": {"speed": 75, "shot": 75, "defense": 74, "passing": 75}, "badge_shape": "circle", "is_real_parody": True },
    { "name": "Great Old Antwerp", "short": "ANW", "primary": (200, 20, 20), "secondary": (255, 255, 255), "accent": (218, 165, 32), "league": "BE", "stats": {"speed": 76, "shot": 74, "defense": 75, "passing": 74}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Union Gold Saint-Gilloise", "short": "USG", "primary": (255, 215, 0), "secondary": (0, 50, 120), "accent": (255, 255, 255), "league": "BE", "stats": {"speed": 76, "shot": 75, "defense": 76, "passing": 76}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Green Circle Brugge", "short": "CRB", "primary": (0, 120, 60), "secondary": (20, 20, 20), "accent": (20, 20, 20), "league": "BE", "stats": {"speed": 75, "shot": 73, "defense": 72, "passing": 73}, "badge_shape": "circle", "is_real_parody": True },
    { "name": "Yellow-Red Mechelen", "short": "MEC", "primary": (255, 215, 0), "secondary": (200, 20, 20), "accent": (20, 20, 20), "league": "BE", "stats": {"speed": 73, "shot": 72, "defense": 72, "passing": 73}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Red Lions Liege", "short": "STD", "primary": (200, 20, 20), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "BE", "stats": {"speed": 74, "shot": 73, "defense": 74, "passing": 73}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Yellow-Blue Westerlo", "short": "WES", "primary": (255, 215, 0), "secondary": (0, 50, 120), "accent": (255, 255, 255), "league": "BE", "stats": {"speed": 74, "shot": 72, "defense": 71, "passing": 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Red Guys Kortrijk", "short": "KRT", "primary": (200, 20, 20), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "BE", "stats": {"speed": 72, "shot": 70, "defense": 71, "passing": 71}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Canaries Sint-Truiden", "short": "STV", "primary": (255, 215, 0), "secondary": (0, 50, 120), "accent": (0, 50, 120), "league": "BE", "stats": {"speed": 73, "shot": 71, "defense": 71, "passing": 71}, "badge_shape": "circle", "is_real_parody": True },
    { "name": "Zebras Charleroi", "short": "CRL", "primary": (20, 20, 20), "secondary": (255, 255, 255), "accent": (20, 20, 20), "league": "BE", "stats": {"speed": 73, "shot": 71, "defense": 71, "passing": 71}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Dender Giants", "short": "DND", "primary": (0, 50, 120), "secondary": (20, 20, 20), "accent": (255, 255, 255), "league": "BE", "stats": {"speed": 70, "shot": 70, "defense": 70, "passing": 69}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Leuven Students", "short": "LEU", "primary": (255, 255, 255), "secondary": (0, 120, 60), "accent": (0, 120, 60), "league": "BE", "stats": {"speed": 72, "shot": 71, "defense": 71, "passing": 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Beerschot Bears", "short": "BEE", "primary": (100, 0, 120), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "BE", "stats": {"speed": 70, "shot": 69, "defense": 69, "passing": 69}, "badge_shape": "shield", "is_real_parody": True },

    # --- RUSIA (RU) ---
    { "name": "Zar San Petersburgo", "short": "ZEN", "primary": (0, 180, 240), "secondary": (255, 255, 255), "accent": (218, 165, 32), "league": "RU", "stats": {"speed": 80, "shot": 82, "defense": 78, "passing": 82}, "badge_shape": "crown", "is_real_parody": True },
    { "name": "Espartano Moscú", "short": "SPA", "primary": (200, 20, 20), "secondary": (255, 255, 255), "accent": (218, 165, 32), "league": "RU", "stats": {"speed": 78, "shot": 78, "defense": 76, "passing": 78}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Ejército Moscú", "short": "CSK", "primary": (200, 20, 20), "secondary": (0, 50, 150), "accent": (218, 165, 32), "league": "RU", "stats": {"speed": 78, "shot": 76, "defense": 78, "passing": 76}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Locomotora Moscú", "short": "LOK", "primary": (0, 120, 60), "secondary": (200, 20, 20), "accent": (255, 255, 255), "league": "RU", "stats": {"speed": 78, "shot": 75, "defense": 76, "passing": 77}, "badge_shape": "circle", "is_real_parody": True },
    { "name": "Dinamo Moscú", "short": "DYN", "primary": (0, 50, 150), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "RU", "stats": {"speed": 77, "shot": 76, "defense": 78, "passing": 78}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Toros Krasnodar", "short": "KRA", "primary": (0, 100, 50), "secondary": (20, 20, 20), "accent": (218, 165, 32), "league": "RU", "stats": {"speed": 79, "shot": 78, "defense": 76, "passing": 77}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Cosecha Rostov", "short": "ROS_RU", "primary": (255, 215, 0), "secondary": (0, 50, 150), "accent": (255, 255, 255), "league": "RU", "stats": {"speed": 75, "shot": 74, "defense": 75, "passing": 73}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Rubí Kazán", "short": "RUB", "primary": (128, 0, 32), "secondary": (0, 100, 50), "accent": (218, 165, 32), "league": "RU", "stats": {"speed": 74, "shot": 74, "defense": 75, "passing": 74}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Alas Samara", "short": "KRY", "primary": (135, 206, 250), "secondary": (0, 50, 150), "accent": (255, 255, 255), "league": "RU", "stats": {"speed": 75, "shot": 72, "defense": 74, "passing": 74}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Lobo Grozny", "short": "AKH", "primary": (0, 100, 50), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "RU", "stats": {"speed": 73, "shot": 71, "defense": 74, "passing": 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Nizhny Azules", "short": "NIZ", "primary": (0, 100, 200), "secondary": (135, 206, 250), "accent": (255, 255, 255), "league": "RU", "stats": {"speed": 72, "shot": 70, "defense": 74, "passing": 71}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Antorcha Voronezh", "short": "FAK", "primary": (0, 50, 150), "secondary": (255, 255, 255), "accent": (200, 20, 20), "league": "RU", "stats": {"speed": 71, "shot": 70, "defense": 74, "passing": 70}, "badge_shape": "circle", "is_real_parody": True },
    { "name": "Orenburg Girasoles", "short": "ORE", "primary": (0, 70, 150), "secondary": (255, 255, 255), "accent": (0, 70, 150), "league": "RU", "stats": {"speed": 73, "shot": 72, "defense": 71, "passing": 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Khimki Rojos", "short": "KHI", "primary": (200, 20, 20), "secondary": (20, 20, 20), "accent": (255, 255, 255), "league": "RU", "stats": {"speed": 72, "shot": 71, "defense": 72, "passing": 71}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Caspio Makhachkala", "short": "MAK", "primary": (255, 215, 0), "secondary": (0, 50, 150), "accent": (255, 255, 255), "league": "RU", "stats": {"speed": 70, "shot": 69, "defense": 72, "passing": 70}, "badge_shape": "circle", "is_real_parody": True },
    { "name": "Akron Metal", "short": "AKR", "primary": (200, 20, 20), "secondary": (20, 20, 20), "accent": (200, 20, 20), "league": "RU", "stats": {"speed": 71, "shot": 70, "defense": 70, "passing": 71}, "badge_shape": "shield", "is_real_parody": True },

    # --- ESCUELA / EXTRAS (RO, SC, AT) ---
    # --- ESCOCIA (SC) ---
    { "name": "Trébol Glasgow", "short": "CEL_SC", "primary": (0, 150, 60), "secondary": (255, 255, 255), "accent": (212, 175, 55), "league": "SC", "stats": {'speed': 77, 'shot': 75, 'defense': 73, 'passing': 76}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Vigilantes Glasgow", "short": "RAN", "primary": (0, 50, 160), "secondary": (255, 255, 255), "accent": (220, 20, 20), "league": "SC", "stats": {'speed': 76, 'shot': 74, 'defense': 74, 'passing': 75}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Corazones Edimburgo", "short": "HEA", "primary": (120, 0, 40), "secondary": (255, 255, 255), "accent": (212, 175, 55), "league": "SC", "stats": {'speed': 71, 'shot': 68, 'defense': 70, 'passing': 69}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Granito Aberdeen", "short": "ABE", "primary": (220, 20, 20), "secondary": (255, 255, 255), "accent": (220, 20, 20), "league": "SC", "stats": {'speed': 70, 'shot': 67, 'defense': 69, 'passing': 68}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Kilmarnock Azules", "short": "KIL", "primary": (0, 70, 150), "secondary": (255, 255, 255), "accent": (212, 175, 55), "league": "SC", "stats": {'speed': 69, 'shot': 66, 'defense': 68, 'passing': 67}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Santos de Paisley", "short": "STM", "primary": (30, 30, 30), "secondary": (255, 255, 255), "accent": (30, 30, 30), "league": "SC", "stats": {'speed': 68, 'shot': 65, 'defense': 67, 'passing': 66}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Dundee Azules", "short": "DUN", "primary": (10, 30, 70), "secondary": (255, 255, 255), "accent": (212, 175, 55), "league": "SC", "stats": {'speed': 67, 'shot': 64, 'defense': 66, 'passing': 65}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Madre del Pozo", "short": "MOT", "primary": (230, 160, 10), "secondary": (100, 0, 30), "accent": (230, 160, 10), "league": "SC", "stats": {'speed': 67, 'shot': 64, 'defense': 66, 'passing': 65}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Hiberia Edimburgo", "short": "HIB", "primary": (0, 120, 50), "secondary": (255, 255, 255), "accent": (0, 180, 80), "league": "SC", "stats": {'speed': 69, 'shot': 66, 'defense': 67, 'passing': 68}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Condado de Ross", "short": "ROC", "primary": (15, 30, 60), "secondary": (255, 255, 255), "accent": (220, 20, 20), "league": "SC", "stats": {'speed': 66, 'shot': 63, 'defense': 65, 'passing': 64}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Santos de Perth", "short": "STJ", "primary": (0, 70, 150), "secondary": (240, 200, 0), "accent": (255, 255, 255), "league": "SC", "stats": {'speed': 65, 'shot': 62, 'defense': 64, 'passing': 63}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Dundee Naranjas", "short": "DUT", "primary": (255, 100, 0), "secondary": (20, 20, 20), "accent": (255, 100, 0), "league": "SC", "stats": {'speed': 68, 'shot': 65, 'defense': 66, 'passing': 67}, "badge_shape": "shield", "is_real_parody": True },

    # --- AUSTRIA (AT) ---
    { "name": "Toro Rojo Salzburgo", "short": "SAL", "primary": (220, 20, 20), "secondary": (255, 255, 255), "accent": (180, 180, 180), "league": "AT", "stats": {'speed': 78, 'shot': 76, 'defense': 74, 'passing': 76}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Tormenta Graz", "short": "STU_AT", "primary": (20, 20, 20), "secondary": (255, 255, 255), "accent": (20, 20, 20), "league": "AT", "stats": {'speed': 76, 'shot': 74, 'defense': 75, 'passing': 74}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Rápido Viena", "short": "RAP", "primary": (0, 120, 50), "secondary": (255, 255, 255), "accent": (0, 120, 50), "league": "AT", "stats": {'speed': 72, 'shot': 69, 'defense': 71, 'passing': 70}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Austria de Viena", "short": "AUS_AT", "primary": (80, 0, 120), "secondary": (255, 255, 255), "accent": (80, 0, 120), "league": "AT", "stats": {'speed': 71, 'shot': 68, 'defense': 70, 'passing': 69}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Linz Blancos", "short": "LAS", "primary": (20, 20, 20), "secondary": (255, 255, 255), "accent": (212, 175, 55), "league": "AT", "stats": {'speed': 72, 'shot': 69, 'defense': 71, 'passing': 70}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Hartberg Azules", "short": "HAR", "primary": (0, 100, 200), "secondary": (255, 255, 255), "accent": (0, 100, 200), "league": "AT", "stats": {'speed': 68, 'shot': 65, 'defense': 67, 'passing': 66}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Lobos de Wolfsberger", "short": "WAC", "primary": (30, 30, 30), "secondary": (255, 255, 255), "accent": (150, 150, 150), "league": "AT", "stats": {'speed': 68, 'shot': 65, 'defense': 67, 'passing': 66}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Klagenfurt Violetas", "short": "KLA", "primary": (90, 0, 130), "secondary": (255, 255, 255), "accent": (150, 150, 150), "league": "AT", "stats": {'speed': 67, 'shot': 64, 'defense': 66, 'passing': 65}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Tirol Verdes", "short": "TIR", "primary": (0, 130, 60), "secondary": (255, 255, 255), "accent": (150, 150, 150), "league": "AT", "stats": {'speed': 66, 'shot': 63, 'defense': 65, 'passing': 64}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Altach Negros", "short": "ALT", "primary": (20, 20, 20), "secondary": (255, 255, 255), "accent": (0, 80, 150), "league": "AT", "stats": {'speed': 66, 'shot': 63, 'defense': 65, 'passing': 64}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Linz Azules", "short": "BWL", "primary": (0, 100, 220), "secondary": (255, 255, 255), "accent": (0, 100, 220), "league": "AT", "stats": {'speed': 67, 'shot': 64, 'defense': 65, 'passing': 66}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Lustenau Verdes", "short": "LUS", "primary": (0, 120, 50), "secondary": (20, 20, 20), "accent": (0, 120, 50), "league": "AT", "stats": {'speed': 65, 'shot': 62, 'defense': 64, 'passing': 63}, "badge_shape": "shield", "is_real_parody": True },

    # --- RUMANÍA (RO) ---
    { "name": "Estrella Bucarest", "short": "FCSB", "primary": (220, 20, 20), "secondary": (0, 50, 150), "accent": (212, 175, 55), "league": "RO", "stats": {'speed': 73, 'shot': 70, 'defense': 71, 'passing': 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Ferroviarios Cluj", "short": "CLU", "primary": (100, 0, 30), "secondary": (255, 255, 255), "accent": (212, 175, 55), "league": "RO", "stats": {'speed': 72, 'shot': 69, 'defense': 71, 'passing': 71}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Estudiantes Craiova", "short": "UCV", "primary": (0, 80, 180), "secondary": (255, 255, 255), "accent": (0, 80, 180), "league": "RO", "stats": {'speed': 71, 'shot': 68, 'defense': 70, 'passing': 69}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Rápido Bucarest", "short": "RAP_RO", "primary": (130, 0, 40), "secondary": (255, 255, 255), "accent": (130, 0, 40), "league": "RO", "stats": {'speed': 71, 'shot': 68, 'defense': 69, 'passing': 70}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Faro Constanza", "short": "FAR", "primary": (0, 70, 150), "secondary": (255, 255, 255), "accent": (0, 70, 150), "league": "RO", "stats": {'speed': 70, 'shot': 67, 'defense': 69, 'passing': 68}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Sepsi OSK", "short": "SEP", "primary": (220, 20, 20), "secondary": (255, 255, 255), "accent": (220, 20, 20), "league": "RO", "stats": {'speed': 69, 'shot': 66, 'defense': 68, 'passing': 67}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Hermannstadt Negros", "short": "HER", "primary": (20, 20, 20), "secondary": (255, 255, 255), "accent": (212, 175, 55), "league": "RO", "stats": {'speed': 68, 'shot': 65, 'defense': 67, 'passing': 66}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "UTA Arad Rojos", "short": "UTA", "primary": (220, 20, 20), "secondary": (255, 255, 255), "accent": (220, 20, 20), "league": "RO", "stats": {'speed': 67, 'shot': 64, 'defense': 66, 'passing': 65}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Petroleros Ploiesti", "short": "PET", "primary": (255, 220, 0), "secondary": (0, 50, 150), "accent": (255, 220, 0), "league": "RO", "stats": {'speed': 68, 'shot': 65, 'defense': 66, 'passing': 67}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Aceros Galati", "short": "OTE", "primary": (220, 20, 20), "secondary": (255, 255, 255), "accent": (0, 50, 150), "league": "RO", "stats": {'speed': 67, 'shot': 64, 'defense': 66, 'passing': 65}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Leones Craiova", "short": "FCU", "primary": (0, 50, 150), "secondary": (255, 255, 255), "accent": (212, 175, 55), "league": "RO", "stats": {'speed': 67, 'shot': 64, 'defense': 66, 'passing': 65}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Dínamo Bucarest", "short": "DIN_RO", "primary": (220, 20, 20), "secondary": (255, 255, 255), "accent": (220, 20, 20), "league": "RO", "stats": {'speed': 69, 'shot': 66, 'defense': 67, 'passing': 68}, "badge_shape": "shield", "is_real_parody": True },



    # --- EXTRA RUMANÍA (COMPLETAR 16 EQUIPOS) ---
    { "name": "U Cluj Blancos", "short": "UCL", "primary": (255, 255, 255), "secondary": (20, 20, 20), "accent": (255, 255, 255), "league": "RO", "stats": {'speed': 68, 'shot': 65, 'defense': 67, 'passing': 66}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Botoșani Rojos", "short": "BOT_RO", "primary": (220, 20, 20), "secondary": (255, 255, 255), "accent": (220, 20, 20), "league": "RO", "stats": {'speed': 66, 'shot': 63, 'defense': 65, 'passing': 64}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Voluntari Celestes", "short": "VOL", "primary": (135, 206, 235), "secondary": (255, 255, 255), "accent": (135, 206, 235), "league": "RO", "stats": {'speed': 67, 'shot': 64, 'defense': 66, 'passing': 65}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Politehnica Azules", "short": "POL_RO", "primary": (0, 70, 150), "secondary": (255, 255, 255), "accent": (0, 70, 150), "league": "RO", "stats": {'speed': 67, 'shot': 64, 'defense': 66, 'passing': 65}, "badge_shape": "shield", "is_real_parody": True },


    # --- LIGA CHILENA ---
    { "name": "Cacique Albo", "short": "COL_CL", "primary": (255, 255, 255), "secondary": (0, 0, 0), "accent": (255, 255, 255), "league": "CL", "stats": {'speed': 78, 'shot': 77, 'defense': 76, 'passing': 77}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Azules Universidad", "short": "UCH", "primary": (0, 0, 180), "secondary": (255, 255, 255), "accent": (0, 0, 180), "league": "CL", "stats": {'speed': 77, 'shot': 76, 'defense': 75, 'passing': 76}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Cruzados Católica", "short": "UCA", "primary": (255, 255, 255), "secondary": (0, 50, 160), "accent": (255, 255, 255), "league": "CL", "stats": {'speed': 76, 'shot': 75, 'defense': 74, 'passing': 75}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Hispanos Unidos", "short": "UES", "primary": (255, 0, 0), "secondary": (255, 200, 0), "accent": (255, 0, 0), "league": "CL", "stats": {'speed': 73, 'shot': 72, 'defense': 72, 'passing': 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Mineros Naranja", "short": "CBL", "primary": (255, 100, 0), "secondary": (0, 0, 0), "accent": (255, 100, 0), "league": "CL", "stats": {'speed': 72, 'shot': 71, 'defense': 71, 'passing': 71}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Mineros del Cobre", "short": "CBS", "primary": (0, 100, 0), "secondary": (255, 255, 255), "accent": (0, 100, 0), "league": "CL", "stats": {'speed': 70, 'shot': 69, 'defense': 70, 'passing': 69}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Celestes del Sur", "short": "OHI", "primary": (135, 206, 250), "secondary": (255, 255, 255), "accent": (135, 206, 250), "league": "CL", "stats": {'speed': 72, 'shot': 71, 'defense': 71, 'passing': 71}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Palestinos Santiago", "short": "PAL", "primary": (255, 255, 255), "secondary": (0, 100, 0), "accent": (255, 0, 0), "league": "CL", "stats": {'speed': 72, 'shot': 71, 'defense': 71, 'passing': 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Itálicos Audaces", "short": "AUD", "primary": (0, 120, 0), "secondary": (255, 255, 255), "accent": (0, 120, 0), "league": "CL", "stats": {'speed': 73, 'shot': 72, 'defense': 72, 'passing': 73}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Acereros del Pacífico", "short": "HUA", "primary": (0, 0, 120), "secondary": (255, 200, 0), "accent": (0, 0, 120), "league": "CL", "stats": {'speed': 71, 'shot': 70, 'defense': 71, 'passing': 70}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Ruleteros de Viña", "short": "EVE_CL", "primary": (0, 0, 150), "secondary": (255, 200, 0), "accent": (0, 0, 150), "league": "CL", "stats": {'speed': 72, 'shot': 71, 'defense': 71, 'passing': 71}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Diablos Rojos Chillán", "short": "NUB", "primary": (200, 0, 0), "secondary": (0, 0, 0), "accent": (200, 0, 0), "league": "CL", "stats": {'speed': 71, 'shot': 70, 'defense': 70, 'passing': 70}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Cementeros Calera", "short": "ULC", "primary": (255, 0, 0), "secondary": (255, 255, 255), "accent": (255, 0, 0), "league": "CL", "stats": {'speed': 70, 'shot': 69, 'defense': 70, 'passing': 69}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Piratas del Norte", "short": "COQ", "primary": (255, 200, 0), "secondary": (0, 0, 0), "accent": (255, 200, 0), "league": "CL", "stats": {'speed': 71, 'shot': 70, 'defense': 70, 'passing': 70}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Dragones del Desierto", "short": "DIQ", "primary": (0, 0, 150), "secondary": (255, 255, 255), "accent": (0, 0, 150), "league": "CL", "stats": {'speed': 70, 'shot': 69, 'defense': 69, 'passing': 69}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Atacameños Dorados", "short": "DCO", "primary": (255, 200, 0), "secondary": (0, 100, 0), "accent": (255, 200, 0), "league": "CL", "stats": {'speed': 69, 'shot': 68, 'defense': 69, 'passing': 68}, "badge_shape": "shield", "is_real_parody": True },


    # --- LIGA PERUANA ---
    { "name": "Íntimos Alianza", "short": "ALI_PE", "primary": (0, 0, 102), "secondary": (255, 255, 255), "accent": (0, 0, 102), "league": "PE", "stats": {'speed': 75, 'shot': 74, 'defense': 73, 'passing': 74}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Cremas Universitario", "short": "UNI_PE", "primary": (245, 245, 220), "secondary": (128, 0, 0), "accent": (245, 245, 220), "league": "PE", "stats": {'speed': 76, 'shot': 75, 'defense': 74, 'passing': 75}, "badge_shape": "circle", "is_real_parody": True },
    { "name": "Celestes Cristal", "short": "CRI", "primary": (135, 206, 250), "secondary": (255, 255, 255), "accent": (135, 206, 250), "league": "PE", "stats": {'speed': 75, 'shot': 74, 'defense': 73, 'passing': 75}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Rojinegros Melgar", "short": "MEL", "primary": (255, 0, 0), "secondary": (0, 0, 0), "accent": (255, 0, 0), "league": "PE", "stats": {'speed': 73, 'shot': 72, 'defense': 72, 'passing': 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Cusqueños Cienciano", "short": "CIE", "primary": (255, 0, 0), "secondary": (255, 255, 255), "accent": (255, 0, 0), "league": "PE", "stats": {'speed': 71, 'shot': 70, 'defense': 70, 'passing': 70}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Poetas Vallejo", "short": "UCV_PE", "primary": (255, 165, 0), "secondary": (0, 0, 102), "accent": (255, 165, 0), "league": "PE", "stats": {'speed': 72, 'shot': 71, 'defense': 70, 'passing': 71}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Imperiales Cusco", "short": "CUS", "primary": (255, 215, 0), "secondary": (0, 0, 0), "accent": (255, 215, 0), "league": "PE", "stats": {'speed': 70, 'shot': 69, 'defense': 69, 'passing': 69}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Celestes ADT", "short": "ADT", "primary": (255, 255, 255), "secondary": (135, 206, 250), "accent": (255, 255, 255), "league": "PE", "stats": {'speed': 70, 'shot': 69, 'defense': 69, 'passing': 69}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Rosados Callao", "short": "SBA", "primary": (255, 192, 203), "secondary": (0, 0, 0), "accent": (255, 192, 203), "league": "PE", "stats": {'speed': 71, 'shot': 70, 'defense': 70, 'passing': 70}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Gavilanes UTC", "short": "UTC", "primary": (255, 255, 255), "secondary": (0, 102, 204), "accent": (255, 255, 255), "league": "PE", "stats": {'speed': 69, 'shot': 68, 'defense': 69, 'passing': 68}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Carlistas Trujillo", "short": "CAM_PE", "primary": (0, 0, 153), "secondary": (255, 255, 255), "accent": (0, 0, 153), "league": "PE", "stats": {'speed': 69, 'shot': 68, 'defense': 69, 'passing': 68}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Albos Piura", "short": "GRA", "primary": (255, 255, 255), "secondary": (255, 0, 0), "accent": (255, 255, 255), "league": "PE", "stats": {'speed': 70, 'shot': 69, 'defense': 69, 'passing': 69}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Pedacito Garcilaso", "short": "GAR", "primary": (135, 206, 235), "secondary": (0, 0, 0), "accent": (135, 206, 235), "league": "PE", "stats": {'speed': 70, 'shot': 69, 'defense': 69, 'passing': 69}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Cutervinos Unidos", "short": "COM_PE", "primary": (255, 255, 0), "secondary": (0, 0, 153), "accent": (255, 255, 0), "league": "PE", "stats": {'speed': 68, 'shot': 67, 'defense': 68, 'passing': 67}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Guerreros Chankas", "short": "CHA", "primary": (255, 0, 0), "secondary": (255, 255, 0), "accent": (255, 0, 0), "league": "PE", "stats": {'speed': 69, 'shot': 68, 'defense': 68, 'passing': 68}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Rojo Matador", "short": "HUAN", "primary": (255, 0, 0), "secondary": (255, 255, 255), "accent": (255, 0, 0), "league": "PE", "stats": {'speed': 71, 'shot': 70, 'defense': 70, 'passing': 70}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Churres Sullana", "short": "AAS", "primary": (0, 0, 153), "secondary": (255, 255, 255), "accent": (0, 0, 153), "league": "PE", "stats": {'speed': 69, 'shot': 68, 'defense': 68, 'passing': 68}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Poderoso San Martín", "short": "UCO", "primary": (255, 255, 0), "secondary": (255, 255, 255), "accent": (255, 255, 0), "league": "PE", "stats": {'speed': 68, 'shot': 67, 'defense': 67, 'passing': 67}, "badge_shape": "shield", "is_real_parody": True },

    # --- SELECCIONES NACIONALES ---
    { "name": "Rusia", "short": "RUS", "primary": (255, 255, 255), "secondary": (0, 50, 150), "accent": (200, 20, 20), "league": "NT", "stats": {"speed": 78, "shot": 76, "defense": 78, "passing": 76}, "badge_shape": "shield", "is_national": True },
    { "name": "Argentina", "short": "ARG", "primary": (117, 170, 219), "secondary": (255, 255, 255), "accent": (255, 215, 0), "league": "NT", "stats": {"speed": 85, "shot": 88, "defense": 84, "passing": 90}, "badge_shape": "shield", "is_national": True },
    { "name": "España", "short": "ESP", "primary": (200, 30, 30), "secondary": (255, 215, 0), "accent": (255, 215, 0), "league": "NT", "stats": {"speed": 84, "shot": 82, "defense": 85, "passing": 92}, "badge_shape": "shield", "is_national": True },
    { "name": "Francia", "short": "FRA", "primary": (0, 35, 125), "secondary": (255, 255, 255), "accent": (210, 15, 45), "league": "NT", "stats": {"speed": 92, "shot": 88, "defense": 86, "passing": 85}, "badge_shape": "shield", "is_national": True },
    { "name": "Brasil", "short": "BRA", "primary": (255, 220, 0), "secondary": (0, 150, 60), "accent": (0, 40, 120), "league": "NT", "stats": {"speed": 88, "shot": 86, "defense": 80, "passing": 88}, "badge_shape": "shield", "is_national": True },
    { "name": "Inglaterra", "short": "ENG", "primary": (255, 255, 255), "secondary": (0, 35, 125), "accent": (200, 30, 30), "league": "NT", "stats": {"speed": 85, "shot": 84, "defense": 88, "passing": 86}, "badge_shape": "shield", "is_national": True },
    { "name": "Alemania", "short": "GER", "primary": (255, 255, 255), "secondary": (20, 20, 20), "accent": (255, 215, 0), "league": "NT", "stats": {"speed": 82, "shot": 82, "defense": 85, "passing": 88}, "badge_shape": "shield", "is_national": True },
    { "name": "Italia", "short": "ITA", "primary": (0, 100, 200), "secondary": (255, 255, 255), "accent": (255, 215, 0), "league": "NT", "stats": {"speed": 80, "shot": 82, "defense": 92, "passing": 82}, "badge_shape": "shield" },
    { "name": "Portugal", "short": "POR", "primary": (200, 30, 30), "secondary": (0, 150, 50), "accent": (255, 215, 0), "league": "NT", "stats": {"speed": 88, "shot": 85, "defense": 82, "passing": 85}, "badge_shape": "shield", "is_national": True },
    { "name": "Colombia", "short": "COL", "primary": (255, 215, 0), "secondary": (0, 35, 125), "accent": (200, 30, 30), "league": "NT", "stats": {"speed": 84, "shot": 82, "defense": 78, "passing": 80}, "badge_shape": "shield", "is_national": True },
    { "name": "Japón", "short": "JPN", "primary": (0, 30, 100), "secondary": (255, 255, 255), "accent": (200, 30, 30), "league": "NT", "stats": {"speed": 86, "shot": 78, "defense": 76, "passing": 84}, "badge_shape": "circle", "is_national": True },
    { "name": "Uruguay", "short": "URU", "primary": (117, 170, 219), "secondary": (255, 255, 255), "accent": (255, 215, 0), "league": "NT", "stats": {"speed": 82, "shot": 84, "defense": 86, "passing": 82}, "badge_shape": "shield", "is_national": True },
    { "name": "Países Bajos", "short": "NED", "primary": (255, 100, 0), "secondary": (255, 255, 255), "accent": (0, 30, 100), "league": "NT", "stats": {"speed": 84, "shot": 82, "defense": 86, "passing": 88}, "badge_shape": "shield", "is_national": True },
    { "name": "Bélgica", "short": "BEL", "primary": (200, 30, 30), "secondary": (20, 20, 20), "accent": (255, 215, 0), "league": "NT", "stats": {"speed": 82, "shot": 82, "defense": 80, "passing": 86}, "badge_shape": "shield", "is_national": True },
    { "name": "Croacia", "short": "CRO", "primary": (255, 255, 255), "secondary": (200, 30, 30), "accent": (0, 50, 150), "league": "NT", "stats": {"speed": 78, "shot": 80, "defense": 82, "passing": 90}, "badge_shape": "shield", "is_national": True },
    { "name": "Marruecos", "short": "MAR", "primary": (200, 30, 30), "secondary": (0, 100, 50), "accent": (255, 215, 0), "league": "NT", "stats": {"speed": 86, "shot": 78, "defense": 84, "passing": 82}, "badge_shape": "shield", "is_national": True },
    { "name": "México", "short": "MEX", "primary": (0, 100, 50), "secondary": (255, 255, 255), "accent": (200, 30, 30), "league": "NT", "stats": {"speed": 82, "shot": 78, "defense": 78, "passing": 78}, "badge_shape": "shield", "is_national": True },
    { "name": "Estados Unidos", "short": "USA", "primary": (255, 255, 255), "secondary": (0, 35, 125), "accent": (200, 30, 30), "league": "NT", "stats": {"speed": 84, "shot": 78, "defense": 78, "passing": 80}, "badge_shape": "shield", "is_national": True },
    { "name": "Chile", "short": "CHI", "primary": (200, 30, 30), "secondary": (255, 255, 255), "accent": (0, 35, 125), "league": "NT", "stats": {"speed": 82, "shot": 78, "defense": 76, "passing": 78}, "badge_shape": "shield", "is_national": True },
    { "name": "Ecuador", "short": "ECU", "primary": (255, 215, 0), "secondary": (0, 35, 125), "accent": (200, 30, 30), "league": "NT", "stats": {"speed": 86, "shot": 76, "defense": 80, "passing": 75}, "badge_shape": "shield", "is_national": True },
    { "name": "Paraguay", "short": "PAR", "primary": (255, 255, 255), "secondary": (200, 30, 30), "accent": (0, 35, 125), "league": "NT", "stats": {"speed": 78, "shot": 76, "defense": 82, "passing": 74}, "badge_shape": "shield", "is_national": True },
    { "name": "Suiza", "short": "SUI", "primary": (200, 30, 30), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "NT", "stats": {"speed": 80, "shot": 78, "defense": 84, "passing": 82}, "badge_shape": "shield", "is_national": True },
    { "name": "Dinamarca", "short": "DEN", "primary": (200, 30, 30), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "NT", "stats": {"speed": 78, "shot": 80, "defense": 82, "passing": 84}, "badge_shape": "shield", "is_national": True },
    { "name": "Noruega", "short": "NOR", "primary": (200, 30, 30), "secondary": (0, 35, 125), "accent": (255, 255, 255), "league": "NT", "stats": {"speed": 85, "shot": 85, "defense": 78, "passing": 82}, "badge_shape": "shield", "is_national": True },
    { "name": "Suecia", "short": "SWE", "primary": (255, 215, 0), "secondary": (0, 70, 150), "accent": (0, 70, 150), "league": "NT", "stats": {"speed": 82, "shot": 82, "defense": 76, "passing": 78}, "badge_shape": "shield", "is_national": True },
    { "name": "Polonia", "short": "POL_NT", "primary": (255, 255, 255), "secondary": (200, 30, 30), "accent": (200, 30, 30), "league": "NT", "stats": {"speed": 78, "shot": 86, "defense": 76, "passing": 74}, "badge_shape": "shield", "is_national": True },
    { "name": "Ucrania", "short": "UKR", "primary": (255, 215, 0), "secondary": (0, 80, 200), "accent": (0, 80, 200), "league": "NT", "stats": {"speed": 84, "shot": 80, "defense": 78, "passing": 82}, "badge_shape": "shield", "is_national": True },
    { "name": "Grecia", "short": "GRE", "primary": (0, 50, 150), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "NT", "stats": {"speed": 75, "shot": 74, "defense": 86, "passing": 72}, "badge_shape": "shield", "is_national": True },
    { "name": "Turquía", "short": "TUR", "primary": (200, 20, 20), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "NT", "stats": {"speed": 82, "shot": 80, "defense": 78, "passing": 84}, "badge_shape": "shield", "is_national": True },
    { "name": "Escocia", "short": "SCO", "primary": (0, 35, 100), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "NT", "stats": {"speed": 78, "shot": 76, "defense": 80, "passing": 78}, "badge_shape": "shield", "is_national": True },
    { "name": "Gales", "short": "WAL", "primary": (200, 30, 30), "secondary": (255, 255, 255), "accent": (0, 150, 60), "league": "NT", "stats": {"speed": 84, "shot": 78, "defense": 75, "passing": 76}, "badge_shape": "shield", "is_national": True },
    { "name": "Perú", "short": "PER", "primary": (255, 255, 255), "secondary": (200, 30, 30), "accent": (200, 30, 30), "league": "NT", "stats": {"speed": 78, "shot": 76, "defense": 75, "passing": 78}, "badge_shape": "shield", "is_national": True },
    { "name": "Venezuela", "short": "VEN", "primary": (120, 20, 50), "secondary": (255, 255, 255), "accent": (218, 165, 32), "league": "NT", "stats": {"speed": 80, "shot": 78, "defense": 76, "passing": 75}, "badge_shape": "shield", "is_national": True },
    { "name": "Bolivia", "short": "BOL", "primary": (0, 100, 50), "secondary": (255, 255, 255), "accent": (255, 215, 0), "league": "NT", "stats": {"speed": 72, "shot": 74, "defense": 70, "passing": 72}, "badge_shape": "shield", "is_national": True },
    { "name": "Corea del Sur", "short": "KOR", "primary": (200, 30, 30), "secondary": (255, 255, 255), "accent": (0, 35, 125), "league": "NT", "stats": {"speed": 88, "shot": 82, "defense": 74, "passing": 80}, "badge_shape": "shield", "is_national": True },
    { "name": "Australia", "short": "AUS", "primary": (255, 215, 0), "secondary": (0, 100, 45), "accent": (0, 100, 45), "league": "NT", "stats": {"speed": 78, "shot": 75, "defense": 78, "passing": 76}, "badge_shape": "shield", "is_national": True },
    { "name": "Senegal", "short": "SEN", "primary": (255, 255, 255), "secondary": (0, 100, 50), "accent": (200, 30, 30), "league": "NT", "stats": {"speed": 88, "shot": 80, "defense": 82, "passing": 78}, "badge_shape": "shield", "is_national": True },
    { "name": "Egipto", "short": "EGY", "primary": (200, 30, 30), "secondary": (255, 255, 255), "accent": (20, 20, 20), "league": "NT", "stats": {"speed": 84, "shot": 88, "defense": 75, "passing": 82}, "badge_shape": "shield", "is_national": True },
    { "name": "Nigeria", "short": "NGA", "primary": (0, 100, 50), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "NT", "stats": {"speed": 88, "shot": 82, "defense": 72, "passing": 75}, "badge_shape": "shield", "is_national": True },
    { "name": "Camerún", "short": "CMR", "primary": (0, 100, 50), "secondary": (200, 30, 30), "accent": (255, 215, 0), "league": "NT", "stats": {"speed": 82, "shot": 80, "defense": 78, "passing": 74}, "badge_shape": "shield", "is_national": True },
    { "name": "Canadá", "short": "CAN", "primary": (200, 30, 30), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "NT", "stats": {"speed": 86, "shot": 78, "defense": 76, "passing": 78}, "badge_shape": "shield", "is_national": True },
    { "name": "Serbia", "short": "SRB", "primary": (200, 20, 20), "secondary": (255, 255, 255), "accent": (0, 35, 149), "league": "NT", "stats": {"speed": 80, "shot": 82, "defense": 78, "passing": 80}, "badge_shape": "shield", "is_national": True },
    { "name": "Austria", "short": "AUT", "primary": (200, 20, 20), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "NT", "stats": {"speed": 78, "shot": 76, "defense": 80, "passing": 80}, "badge_shape": "shield", "is_national": True },
    { "name": "República Checa", "short": "CZE", "primary": (200, 20, 20), "secondary": (0, 35, 149), "accent": (255, 255, 255), "league": "NT", "stats": {"speed": 76, "shot": 78, "defense": 78, "passing": 78}, "badge_shape": "shield", "is_national": True },
    { "name": "Rumanía", "short": "ROU", "primary": (255, 215, 0), "secondary": (0, 45, 140), "accent": (200, 30, 30), "league": "NT", "stats": {"speed": 78, "shot": 74, "defense": 76, "passing": 76}, "badge_shape": "shield", "is_national": True },
    { "name": "Hungría", "short": "HUN", "primary": (200, 20, 20), "secondary": (255, 255, 255), "accent": (0, 100, 50), "league": "NT", "stats": {"speed": 76, "shot": 78, "defense": 76, "passing": 76}, "badge_shape": "shield", "is_national": True },
    { "name": "Ghana", "short": "GHA", "primary": (255, 255, 255), "secondary": (0, 0, 0), "accent": (255, 215, 0), "league": "NT", "stats": {"speed": 86, "shot": 78, "defense": 74, "passing": 76}, "badge_shape": "circle", "is_national": True },
    { "name": "Costa de Marfil", "short": "CIV", "primary": (255, 100, 0), "secondary": (255, 255, 255), "accent": (0, 100, 50), "league": "NT", "stats": {"speed": 84, "shot": 80, "defense": 78, "passing": 78}, "badge_shape": "shield", "is_national": True },
    { "name": "Irán", "short": "IRN", "primary": (255, 255, 255), "secondary": (200, 20, 20), "accent": (0, 100, 50), "league": "NT", "stats": {"speed": 76, "shot": 76, "defense": 78, "passing": 74}, "badge_shape": "shield", "is_national": True },
    { "name": "Arabia Saudita", "short": "KSA", "primary": (0, 100, 50), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "NT", "stats": {"speed": 76, "shot": 72, "defense": 74, "passing": 74}, "badge_shape": "shield", "is_national": True },
    { "name": "Jamaica", "short": "JAM", "primary": (255, 215, 0), "secondary": (0, 0, 0), "accent": (0, 100, 50), "league": "NT", "stats": {"speed": 84, "shot": 76, "defense": 72, "passing": 72}, "badge_shape": "shield", "is_national": True },
    { "name": "Georgia", "short": "GEO", "primary": (200, 20, 20), "secondary": (255, 255, 255), "accent": (200, 20, 20), "league": "NT", "stats": {"speed": 78, "shot": 76, "defense": 74, "passing": 75}, "badge_shape": "shield", "is_national": True },
    { "name": "Irlanda", "short": "IRL", "primary": (0, 150, 50), "secondary": (255, 255, 255), "accent": (255, 100, 0), "league": "NT", "stats": {"speed": 76, "shot": 74, "defense": 76, "passing": 74}, "badge_shape": "shield", "is_national": True },
    { "name": "Sudáfrica", "short": "RSA", "primary": (255, 215, 0), "secondary": (0, 100, 45), "accent": (255, 255, 255), "league": "NT", "stats": {"speed": 76, "shot": 72, "defense": 73, "passing": 72}, "badge_shape": "shield", "is_national": True },
    { "name": "Irak", "short": "IRQ", "primary": (255, 255, 255), "secondary": (0, 100, 45), "accent": (200, 20, 20), "league": "NT", "stats": {"speed": 74, "shot": 72, "defense": 71, "passing": 71}, "badge_shape": "shield", "is_national": True },
    { "name": "Uzbekistán", "short": "UZB", "primary": (255, 255, 255), "secondary": (0, 100, 200), "accent": (200, 20, 20), "league": "NT", "stats": {"speed": 75, "shot": 73, "defense": 72, "passing": 73}, "badge_shape": "shield", "is_national": True },
    { "name": "China", "short": "CHN", "primary": (200, 20, 20), "secondary": (255, 215, 0), "accent": (255, 215, 0), "league": "NT", "stats": {"speed": 73, "shot": 70, "defense": 70, "passing": 70}, "badge_shape": "shield", "is_national": True },
    { "name": "Malí", "short": "MLI", "primary": (0, 100, 50), "secondary": (255, 215, 0), "accent": (200, 20, 20), "league": "NT", "stats": {"speed": 78, "shot": 74, "defense": 76, "passing": 76}, "badge_shape": "shield", "is_national": True },
    { "name": "Burkina Faso", "short": "BFA", "primary": (200, 20, 20), "secondary": (0, 100, 50), "accent": (255, 215, 0), "league": "NT", "stats": {"speed": 78, "shot": 73, "defense": 74, "passing": 72}, "badge_shape": "shield", "is_national": True },
    { "name": "Haití", "short": "HAI", "primary": (0, 35, 149), "secondary": (200, 20, 20), "accent": (255, 255, 255), "league": "NT", "stats": {"speed": 75, "shot": 70, "defense": 70, "passing": 69}, "badge_shape": "shield", "is_national": True },
    { "name": "El Salvador", "short": "SLV", "primary": (0, 35, 149), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "NT", "stats": {"speed": 74, "shot": 68, "defense": 68, "passing": 68}, "badge_shape": "shield", "is_national": True },
    { "name": "Eslovenia", "short": "SVN", "primary": (255, 255, 255), "secondary": (0, 100, 200), "accent": (200, 20, 20), "league": "NT", "stats": {"speed": 76, "shot": 75, "defense": 76, "passing": 75}, "badge_shape": "shield", "is_national": True },
    { "name": "Montenegro", "short": "MNE", "primary": (200, 20, 20), "secondary": (255, 215, 0), "accent": (255, 215, 0), "league": "NT", "stats": {"speed": 75, "shot": 72, "defense": 73, "passing": 72}, "badge_shape": "shield", "is_national": True },
    { "name": "Israel", "short": "ISR", "primary": (0, 100, 200), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "NT", "stats": {"speed": 76, "shot": 73, "defense": 72, "passing": 74}, "badge_shape": "shield", "is_national": True },
    { "name": "R.D. Congo", "short": "COD", "primary": (0, 100, 200), "secondary": (255, 215, 0), "accent": (200, 20, 20), "league": "NT", "stats": {"speed": 78, "shot": 74, "defense": 73, "passing": 73}, "badge_shape": "shield", "is_national": True },
    { "name": "Guinea", "short": "GUI_NT", "primary": (200, 20, 20), "secondary": (255, 215, 0), "accent": (0, 100, 50), "league": "NT", "stats": {"speed": 78, "shot": 75, "defense": 73, "passing": 72}, "badge_shape": "shield", "is_national": True },
    { "name": "Cabo Verde", "short": "CPV", "primary": (0, 35, 149), "secondary": (255, 255, 255), "accent": (200, 20, 20), "league": "NT", "stats": {"speed": 76, "shot": 72, "defense": 72, "passing": 72}, "badge_shape": "shield", "is_national": True },
    { "name": "Emiratos Árabes Unidos", "short": "UAE", "primary": (255, 255, 255), "secondary": (0, 100, 50), "accent": (200, 20, 20), "league": "NT", "stats": {"speed": 74, "shot": 71, "defense": 70, "passing": 70}, "badge_shape": "shield", "is_national": True },
    { "name": "Jordania", "short": "JOR", "primary": (255, 255, 255), "secondary": (200, 20, 20), "accent": (0, 100, 50), "league": "NT", "stats": {"speed": 76, "shot": 71, "defense": 70, "passing": 70}, "badge_shape": "shield", "is_national": True },
    { "name": "Nueva Zelanda", "short": "NZL", "primary": (20, 20, 20), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "NT", "stats": {"speed": 73, "shot": 70, "defense": 70, "passing": 70}, "badge_shape": "shield", "is_national": True },
    { "name": "Guatemala", "short": "GUA", "primary": (0, 100, 200), "secondary": (255, 255, 255), "accent": (0, 100, 200), "league": "NT", "stats": {"speed": 74, "shot": 68, "defense": 68, "passing": 68}, "badge_shape": "shield", "is_national": True },
    { "name": "Costa Rica", "short": "CRC", "primary": (200, 20, 20), "secondary": (255, 255, 255), "accent": (0, 35, 149), "league": "NT", "stats": {"speed": 78, "shot": 74, "defense": 76, "passing": 76}, "badge_shape": "shield", "is_national": True },
    { "name": "Panamá", "short": "PAN", "primary": (200, 20, 20), "secondary": (255, 255, 255), "accent": (0, 35, 149), "league": "NT", "stats": {"speed": 76, "shot": 72, "defense": 74, "passing": 72}, "badge_shape": "shield", "is_national": True },
    { "name": "Túnez", "short": "TUN", "primary": (200, 20, 20), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "NT", "stats": {"speed": 78, "shot": 76, "defense": 78, "passing": 78}, "badge_shape": "shield", "is_national": True },
    { "name": "Argelia", "short": "ALG", "primary": (0, 100, 50), "secondary": (255, 255, 255), "accent": (200, 20, 20), "league": "NT", "stats": {"speed": 82, "shot": 80, "defense": 76, "passing": 80}, "badge_shape": "shield", "is_national": True },
    { "name": "Catar", "short": "QAT", "primary": (120, 20, 50), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "NT", "stats": {"speed": 74, "shot": 72, "defense": 72, "passing": 72}, "badge_shape": "shield", "is_national": True },
    { "name": "Eslovaquia", "short": "SVK", "primary": (0, 35, 149), "secondary": (255, 255, 255), "accent": (200, 20, 20), "league": "NT", "stats": {"speed": 78, "shot": 78, "defense": 80, "passing": 80}, "badge_shape": "shield", "is_national": True },
    { "name": "Finlandia", "short": "FIN", "primary": (255, 255, 255), "secondary": (0, 35, 149), "accent": (0, 35, 149), "league": "NT", "stats": {"speed": 76, "shot": 74, "defense": 76, "passing": 74}, "badge_shape": "shield", "is_national": True },
    { "name": "Islandia", "short": "ISL", "primary": (0, 35, 149), "secondary": (255, 255, 255), "accent": (200, 20, 20), "league": "NT", "stats": {"speed": 76, "shot": 72, "defense": 78, "passing": 72}, "badge_shape": "shield", "is_national": True },
    { "name": "Honduras", "short": "HON", "primary": (0, 35, 149), "secondary": (255, 255, 255), "accent": (255, 255, 255), "league": "NT", "stats": {"speed": 78, "shot": 72, "defense": 72, "passing": 72}, "badge_shape": "shield", "is_national": True },
    { "name": "Albania", "short": "ALB_NT", "primary": (200, 20, 20), "secondary": (20, 20, 20), "accent": (20, 20, 20), "league": "NT", "stats": {"speed": 78, "shot": 74, "defense": 78, "passing": 76}, "badge_shape": "shield", "is_national": True },

    { "name": "Águilas del Capital", "short": "AMX", "primary": (255, 230, 0), "secondary": (0, 30, 90), "accent": (255, 230, 0), "league": "MX", "stats": {'speed': 82, 'shot': 80, 'defense': 78, 'passing': 81}, "badge_shape": "circle", "is_real_parody": True },
    { "name": "Chivitas de Jalisco", "short": "GDL", "primary": (220, 0, 0), "secondary": (255, 255, 255), "accent": (0, 0, 150), "league": "MX", "stats": {'speed': 80, 'shot': 78, 'defense': 76, 'passing': 79}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Máquina Cementera", "short": "CAZ", "primary": (0, 50, 180), "secondary": (255, 255, 255), "accent": (220, 0, 0), "league": "MX", "stats": {'speed': 81, 'shot': 79, 'defense': 79, 'passing': 80}, "badge_shape": "circle", "is_real_parody": True },
    { "name": "Felinos del Pedregal", "short": "UNM", "primary": (20, 35, 60), "secondary": (195, 155, 45), "accent": (195, 155, 45), "league": "MX", "stats": {'speed': 78, 'shot': 76, 'defense': 75, 'passing': 76}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Tigres del Norte", "short": "TGX", "primary": (255, 215, 0), "secondary": (0, 80, 180), "accent": (255, 215, 0), "league": "MX", "stats": {'speed': 81, 'shot': 82, 'defense': 78, 'passing': 81}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Rayados de la Silla", "short": "MTY", "primary": (0, 30, 80), "secondary": (255, 255, 255), "accent": (0, 30, 80), "league": "MX", "stats": {'speed': 82, 'shot': 81, 'defense': 79, 'passing': 82}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Diablos del Infierno", "short": "TLC", "primary": (210, 0, 0), "secondary": (255, 255, 255), "accent": (210, 0, 0), "league": "MX", "stats": {'speed': 79, 'shot': 78, 'defense': 75, 'passing': 78}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Tuzos del Reloj", "short": "PAC", "primary": (0, 50, 140), "secondary": (255, 255, 255), "accent": (0, 50, 140), "league": "MX", "stats": {'speed': 80, 'shot': 78, 'defense': 76, 'passing': 79}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Esmeraldas del Bajío", "short": "LEO", "primary": (0, 110, 60), "secondary": (255, 255, 255), "accent": (255, 215, 0), "league": "MX", "stats": {'speed': 77, 'shot': 76, 'defense': 73, 'passing': 76}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Guerreros del Desierto", "short": "SLG", "primary": (0, 128, 60), "secondary": (255, 255, 255), "accent": (0, 128, 60), "league": "MX", "stats": {'speed': 76, 'shot': 75, 'defense': 74, 'passing': 75}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Zorros del Coloso", "short": "ATS", "primary": (200, 0, 0), "secondary": (0, 0, 0), "accent": (200, 0, 0), "league": "MX", "stats": {'speed': 76, 'shot': 74, 'defense': 74, 'passing': 75}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Xolos de la Frontera", "short": "TIJ", "primary": (180, 0, 0), "secondary": (0, 0, 0), "accent": (180, 0, 0), "league": "MX", "stats": {'speed': 75, 'shot': 74, 'defense': 72, 'passing': 74}, "badge_shape": "circle", "is_real_parody": True },
    { "name": "Rayos del Rayo", "short": "NEC", "primary": (220, 0, 0), "secondary": (255, 255, 255), "accent": (220, 0, 0), "league": "MX", "stats": {'speed': 74, 'shot': 73, 'defense': 72, 'passing': 73}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Camoteros del Rincón", "short": "PUE", "primary": (0, 80, 160), "secondary": (255, 255, 255), "accent": (0, 80, 160), "league": "MX", "stats": {'speed': 73, 'shot': 72, 'defense': 71, 'passing': 72}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Gallos del Corregidor", "short": "QRO", "primary": (0, 90, 190), "secondary": (0, 0, 0), "accent": (255, 255, 255), "league": "MX", "stats": {'speed': 72, 'shot': 71, 'defense': 70, 'passing': 71}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Cañoneros del Faro", "short": "MAZ", "primary": (90, 0, 120), "secondary": (0, 0, 0), "accent": (255, 255, 255), "league": "MX", "stats": {'speed': 72, 'shot': 71, 'defense': 70, 'passing': 71}, "badge_shape": "circle", "is_real_parody": True },
    { "name": "Potosinos del Túnel", "short": "ASL", "primary": (220, 0, 0), "secondary": (0, 0, 150), "accent": (255, 255, 255), "league": "MX", "stats": {'speed': 75, 'shot': 73, 'defense': 73, 'passing': 74}, "badge_shape": "shield", "is_real_parody": True },
    { "name": "Bravos del Desierto", "short": "JUA", "primary": (0, 150, 0), "secondary": (220, 0, 0), "accent": (0, 150, 0), "league": "MX", "stats": {'speed': 73, 'shot': 72, 'defense': 71, 'passing': 72}, "badge_shape": "shield", "is_real_parody": True },
]

# Inyectar Rosters
from data.rosters import get_base_rosters, calculate_ovr
from data.procedural import generate_filler_teams

all_rosters = get_base_rosters()
gen_teams, gen_rosters = generate_filler_teams(len(TEAMS), TEAMS)

TEAMS.extend(gen_teams)
all_rosters.update(gen_rosters)

for t in TEAMS:
    r = all_rosters.get(t["short"], [])
    # Calcular OVR individual para todos y asignar nacionalidad por defecto
    for player in r:
        player["team"] = t["short"]
        player["ovr"] = calculate_ovr(player)
        # Si no tiene nacionalidad explícita (como parodias extranjeras), usar la de la liga
        if "nat" not in player:
            player["nat"] = t.get("league", "??")
    
    # Recalcular métricas del equipo basándose en el once titular real
    if len(r) >= 11:
        starters = r[:11]
        spd = sum(p["s"]["speed"] for p in starters) // 11
        sht = sum(p["s"]["shot"] for p in starters) // 11
        pas = sum(p["s"]["passing"] for p in starters) // 11
        dfn = sum(p["s"]["defense"] for p in starters) // 11
        t["stats"] = {"speed": spd, "shot": sht, "defense": dfn, "passing": pas}
        
    t["roster"] = r



def draw_badge(surface, team, x, y, size=60):
    """Dibuja un escudo procedural para el equipo dado."""
    if not team: return
    shape = team.get("badge_shape", "shield")
    p = team.get("primary", (200, 200, 200))
    s = team.get("secondary", (255, 255, 255))
    a = team.get("accent", (100, 100, 100))
    half = size // 2

    if shape == "shield":
        # Escudo tipo blasón
        points = [
            (x - half, y - half),
            (x + half, y - half),
            (x + half, y + half // 2),
            (x, y + half),
            (x - half, y + half // 2),
        ]
        pygame.draw.polygon(surface, p, points)
        pygame.draw.polygon(surface, a, points, 2)
        # Línea vertical interior
        pygame.draw.line(surface, s, (x, y - half + 6), (x, y + half - 6), 3)
        # Línea horizontal
        pygame.draw.line(surface, s, (x - half + 6, y - 4), (x + half - 6, y - 4), 3)

    elif shape == "circle":
        pygame.draw.circle(surface, p, (x, y), half)
        pygame.draw.circle(surface, a, (x, y), half, 2)
        # Patrón interno: franjas verticales
        stripe_w = size // 5
        for i in range(-2, 3, 2):
            sx = x + i * stripe_w // 2
            top = y - int(math.sqrt(max(0, half**2 - (sx - x)**2)))
            bot = y + int(math.sqrt(max(0, half**2 - (sx - x)**2)))
            if top < bot:
                pygame.draw.line(surface, s, (sx, top + 3), (sx, bot - 3), stripe_w // 2)

    elif shape == "diamond":
        points = [
            (x, y - half),
            (x + half, y),
            (x, y + half),
            (x - half, y),
        ]
        pygame.draw.polygon(surface, p, points)
        pygame.draw.polygon(surface, a, points, 2)
        # Rombo interior pequeño
        inner = half // 3
        inner_pts = [
            (x, y - inner),
            (x + inner, y),
            (x, y + inner),
            (x - inner, y),
        ]
        pygame.draw.polygon(surface, s, inner_pts)

    elif shape == "crown":
        # Base rectangular
        base = pygame.Rect(x - half, y - half // 2, size, half + half // 2)
        pygame.draw.rect(surface, p, base)
        pygame.draw.rect(surface, a, base, 2)
        # Puntas de corona
        crown_pts = [
            (x - half, y - half // 2),
            (x - half // 2, y - half),
            (x, y - half // 2),
            (x + half // 2, y - half),
            (x + half, y - half // 2),
        ]
        pygame.draw.polygon(surface, a, crown_pts)
        pygame.draw.polygon(surface, p, crown_pts, 0)
        pygame.draw.polygon(surface, a, crown_pts, 2)
        # Franja central
        pygame.draw.line(surface, s, (x - half + 4, y + 4), (x + half - 4, y + 4), 4)

    # Iniciales del equipo
    try:
        font = pygame.font.SysFont("Arial", max(10, size // 4), bold=True)
    except:
        font = pygame.font.Font(None, max(12, size // 4))
    text_surf = font.render(team["short"], True, a)
    text_rect = text_surf.get_rect(center=(x, y + 2))
    surface.blit(text_surf, text_rect)


def draw_uniform_preview(surface, team, x, y, scale=1.0):
    """Dibuja una vista previa del uniforme (camiseta + short simplificados)."""
    p = team.get("primary", (200, 200, 200)) if team else (200, 200, 200)
    s = team.get("secondary", (255, 255, 255)) if team else (255, 255, 255)

    w = int(60 * scale)
    h_shirt = int(70 * scale)
    h_short = int(30 * scale)

    # Camiseta
    shirt_rect = pygame.Rect(x - w // 2, y, w, h_shirt)
    pygame.draw.rect(surface, p, shirt_rect, border_radius=6)
    # Franjas en camiseta
    stripe_w = w // 3
    stripe_rect = pygame.Rect(x - stripe_w // 2, y, stripe_w, h_shirt)
    pygame.draw.rect(surface, s, stripe_rect, border_radius=3)
    # Cuello
    pygame.draw.arc(surface, s, pygame.Rect(x - 10, y - 5, 20, 14), 0, math.pi, 3)
    # Mangas (triángulos a los lados)
    sleeve_h = int(25 * scale)
    # manga izquierda
    pygame.draw.polygon(surface, p, [
        (x - w // 2, y + 4),
        (x - w // 2 - int(15 * scale), y + sleeve_h // 2),
        (x - w // 2, y + sleeve_h),
    ])
    # manga derecha
    pygame.draw.polygon(surface, p, [
        (x + w // 2, y + 4),
        (x + w // 2 + int(15 * scale), y + sleeve_h // 2),
        (x + w // 2, y + sleeve_h),
    ])

    # Short
    short_rect = pygame.Rect(x - w // 2, y + h_shirt + 2, w, h_short)
    pygame.draw.rect(surface, s, short_rect, border_radius=4)
    # Línea media
    pygame.draw.line(surface, p, (x, y + h_shirt + 2), (x, y + h_shirt + 2 + h_short), 2)

    # Bordes
    pygame.draw.rect(surface, (0, 0, 0), shirt_rect, 2, border_radius=6)
    pygame.draw.rect(surface, (0, 0, 0), short_rect, 2, border_radius=4)
