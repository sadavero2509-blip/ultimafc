import random

# Pool de sílabas/nombres base globales para parodias
PATTERNS = {
    "EN": {"first": ["J.", "T.", "H.", "B.", "C.", "M."], "last": ["Smith", "Jones", "Brown", "Taylor", "White", "Cole", "Kanne", "Grealishh", "Fodden"]},
    "ES": {"first": ["A.", "P.", "J.", "D.", "F.", "L."], "last": ["García", "Pérez", "López", "Gómez", "Torres", "Martínez", "Ramos", "Iskoh"]},
    "IT": {"first": ["M.", "L.", "F.", "G.", "A.", "C."], "last": ["Rossi", "Russo", "Ferrari", "Esposito", "Bianchi", "Ricci", "Chiesah", "Barellah"]},
    "DE": {"first": ["T.", "L.", "M.", "H.", "F.", "J."], "last": ["Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Kimmichh", "Saneh"]},
    "FR": {"first": ["H.", "K.", "N.", "P.", "L.", "E."], "last": ["Martin", "Bernard", "Thomas", "Petit", "Robert", "Durand", "Mbapppe", "Dembeleh"]},
    "PT": {"first": ["J.", "R.", "B.", "D.", "C.", "N."], "last": ["Silva", "Santos", "Ferreira", "Pereira", "Oliveira", "Costa", "Felixe", "Diass"]},
    "BR": {"first": ["R.", "G.", "L.", "V.", "M.", "E."], "last": ["da Silva", "dos Santos", "Pereira", "Alves", "Ribeiro", "Gomes", "Gabriel", "Vinny"]},
    "AR": {"first": ["F.", "L.", "J.", "M.", "E.", "G."], "last": ["Fernández", "González", "Rodríguez", "Álvarez", "López", "García", "Martinez", "Paredes"]},
    "CO": {"first": ["D.", "J.", "C.", "S.", "A.", "Y."], "last": ["Rodríguez", "Gómez", "Martínez", "Pérez", "Muñoz", "Díaz", "Quintero", "Ruiz"]},
    "UY": {"first": ["F.", "D.", "L.", "R.", "M.", "N."], "last": ["Balverde", "Nunnez", "Suarezz", "Araujoh", "Giménez", "Bentancurr", "De la Cruz", "Olivera"]},
    "NL": {"first": ["V.", "C.", "M.", "N.", "X.", "J."], "last": ["van Dyk", "Gakpoh", "Simonnz", "Akeh", "Dumfries", "Depay", "de Ligt", "Reijnders"]},
    "BE": {"first": ["K.", "J.", "L.", "R.", "A.", "Y."], "last": ["De Bruyneh", "Dokuh", "Lukakuh", "Trossard", "Onana", "Tielemans", "Casteels", "Faes"]},
    "HR": {"first": ["L.", "J.", "M.", "A.", "B.", "D."], "last": ["Modrich", "Gvardiolla", "Kovacich", "Kramaric", "Brozovic", "Livakovic", "Sutalo", "Perisic"]},
    "MA": {"first": ["A.", "Y.", "H.", "B.", "S.", "N."], "last": ["Hakimih", "Bounouh", "Ziyechh", "En-Nesyri", "Amrabat", "Ounahi", "Mazraoui", "Abde"]},
    "MX": {"first": ["S.", "E.", "L.", "H.", "C.", "G."], "last": ["Giménez", "Álvarez", "Lozano", "Martín", "Montes", "Ochoa", "Vásquez", "Chávez"]},
    "US": {"first": ["C.", "W.", "G.", "T.", "F.", "A."], "last": ["Pulisic", "McKennie", "Reyna", "Weah", "Balogun", "Adams", "Robinson", "Dest"]},
    "CL": {"first": ["A.", "E.", "V.", "B.", "D.", "M."], "last": ["Sánchez", "Vargas", "Dávila", "Brereton", "Pulgar", "Diaz", "Suazo", "Isla"]},
    "EC": {"first": ["E.", "P.", "M.", "K.", "G.", "W."], "last": ["Valencia", "Estupiñán", "Caicedo", "Páez", "Plata", "Pacho", "Hincapié", "Preciado"]},
    "PY": {"first": ["J.", "R.", "A.", "G.", "O.", "M."], "last": ["Enciso", "Sosa", "Sanabria", "Almirón", "Gómez", "Alderete", "Alonso", "Villasanti"]},
}

# Mapa de liga -> código de país (para asignar nacionalidad)
LEAGUE_TO_COUNTRY = {
    "EN": "EN", "ES": "ES", "IT": "IT", "DE": "DE", "FR": "FR",
    "PT": "PT", "BR": "BR", "AR": "AR", "CO": "CO", "JP": "JP",
    "UY": "UY", "NL": "NL", "BE": "BE", "HR": "HR", "MA": "MA",
    "MX": "MX", "US": "US", "CL": "CL", "EC": "EC", "PY": "PY"
}
ALL_COUNTRIES = list(LEAGUE_TO_COUNTRY.values())

# Países con sus pools de nombres (para jugadores japoneses que no tienen liga propia)
PATTERNS["JP"] = {"first": ["T.", "K.", "S.", "H.", "Y.", "R."], "last": ["Tanaka", "Suzuki", "Yamada", "Takahashi", "Watanabe", "Nakamura", "Honda", "Kagawa"]}

# Prefijos/Sufijos de clubes procedimentales para rellenar ligas
TEAM_NAMES = {
    "EN": ["FC", "United", "City", "Rovers", "Wanderers", "Athletic"],
    "ES": ["Real", "Deportivo", "Athletic", "Club", "UD", "SD"],
    "IT": ["AC", "Inter", "SS", "Calcio", "US", "FC"],
    "DE": ["FC", "BV", "SC", "SV", "TSV", "VfL"],
    "FR": ["Olympique", "AS", "FC", "Racing", "Stade"],
    "PT": ["FC", "Sporting", "Clube", "Vitória", "SC"],
    "BR": ["Série", "Clube", "Atlético", "EC", "FR"],
    "AR": ["Atlético", "Club", "CA", "Independiente", "Deportivo"],
    "CO": ["Deportivo", "Atlético", "Santa", "Real", "CD"],
    "US": ["FC", "United", "City", "SC", "Athletic"],
    "JP": ["FC", "SC", "Reysol", "Antlers", "Grampus"],
}

CITIES = {
    "EN": ["London", "Manch", "Liver", "Birming", "Leeds", "South", "New", "Aston", "Wolves", "Brighton", "Palace", "Brentford", "Ever", "Fulham"],
    "ES": ["Madrid", "Cataluña", "Valenc", "Sevill", "Bilbao", "Celt", "Vill", "Betis", "Sociedad", "Girona", "Getafe", "Mallorc", "Alaves"],
    "IT": ["Milano", "Roma", "Turin", "Napoli", "Fioren", "Bolo", "Genoa", "Bologna", "Lazio", "Atalanta", "Sassuolo", "Lecce", "Empoli", "Verona"],
    "DE": ["Berlin", "Baviera", "Dort", "Hamburg", "Stutt", "Frank", "Koln", "Leipzig", "Bayer", "Wolfsburg", "Bremen", "Mainz", "Freiburg"],

    "FR": ["Paris", "Lyon", "Marsei", "Lille", "Bord", "Rennes", "Nantes", "Monaco", "Lens", "Nice", "Reims", "Stras", "Montp", "Toulouse"],
    "PT": ["Lisboa", "Porto", "Braga", "Coimbr", "Faro", "Aveir", "Madeir", "Guimara", "Setubal", "Funchal", "Barcelos"],
    "BR": ["Paulo", "Rio", "Belo", "Porto", "Salva", "Forta", "Recif", "Curitiba", "Goiania", "Natal", "Manaus", "Belem"],
    "AR": ["Aires", "Rosar", "Cordo", "Mendo", "Plata", "Tucum", "Santa", "Mar", "Salta", "San", "Corri", "Neuquen"],
    "CO": ["Bogota", "Medell", "Cali", "Barranq", "Bucara", "Cartage", "Pasto", "Pereira", "Maniz", "Armenia", "Cucuta", "Huila"],
    "US": ["Miami", "Dallas", "Denver", "Atlanta", "Kansas", "Chicago", "Salt Lake", "San Jose", "Austin", "Charlotte", "DC", "Minnesota"],
    "JP": ["Tokyo", "Osaka", "Nagoya", "Kobe", "Sendai", "Niigata", "Chiba", "Sapporo", "Shizuoka", "Oita", "Mito", "Tokushi"],
}

def generate_player(league, pos, ovr_target):
    base_target = max(30, ovr_target - 3)
    
    s = {}
    if pos == "GK":
        s['gk'] = min(97, base_target * 1.1)
        s['passing'] = base_target * 0.5
        s['speed'] = 45
        s['shot'] = 15
        s['defense'] = 30
    elif pos in ["CB", "LB", "RB"]:
        s['defense'] = min(97, base_target * 1.1)
        s['speed'] = min(97, base_target * 0.9)
        s['passing'] = min(97, base_target * 0.8)
        s['shot'] = min(97, base_target * 0.6)
        s['gk'] = 10
    elif pos in ["CM", "CDM", "CAM"]:
        s['passing'] = min(97, base_target * 1.05)
        s['defense'] = min(97, base_target * 0.9)
        s['shot'] = min(97, base_target * 0.85)
        s['speed'] = min(97, base_target * 0.85)
        s['gk'] = 10
    else: # ST, LW, RW
        s['shot'] = min(97, base_target * 1.1)
        s['speed'] = min(97, base_target * 1.0)
        s['passing'] = min(97, base_target * 0.8)
        s['defense'] = min(97, base_target * 0.4)
        s['gk'] = 10
        
    s = {k: int(v) for k, v in s.items()}
    
    from data.rosters import calculate_ovr
    ovr = calculate_ovr({"pos": pos, "s": s})
    age = random.randint(17, 36)
    
    if age <= 18:
        pot = ovr + min(12, 94 - ovr) + random.randint(-2, 3)
    elif age <= 22:
        pot = ovr + min(8, 94 - ovr) + random.randint(-1, 3)
    elif age <= 25:
        pot = ovr + min(4, 94 - ovr) + random.randint(0, 2)
    elif age <= 28:
        pot = ovr + min(1, 94 - ovr)
    else:
        pot = ovr
        
    pot = min(94, max(ovr, pot))
    
    pats = PATTERNS.get(league, PATTERNS["EN"])
    name = f"{random.choice(pats['first'])} {random.choice(pats['last'])}"
    
    return {
        "name": name,
        "age": age,
        "ovr": ovr,
        "pot": pot,
        "pos": pos,
        "nat": _assign_nationality(league),
        "s": s
    }

def _assign_nationality(league):
    """Asigna nacionalidad: 70% local, 30% extranjero."""
    local_country = LEAGUE_TO_COUNTRY.get(league, "EN")
    if random.random() < 0.70:
        return local_country
    else:
        return random.choice(ALL_COUNTRIES)

def generate_roster(league, team_ovr):
    positions = ["GK", "LB", "CB", "CB", "RB", "CM", "CM", "CM", "LW", "ST", "RW"]
    subs = ["GK", "CB", "CB", "CM", "CM", "RW", "LW", "ST"] # 8 subs
    roster = []
    
    num_pool = list(range(1, 99))
    random.shuffle(num_pool)
    
    for p in positions:
        pl = generate_player(league, p, team_ovr + random.randint(-2, 2))
        pl["num"] = num_pool.pop()
        roster.append(pl)
        
    for p in subs:
        pl = generate_player(league, p, team_ovr - random.randint(4, 7))
        pl["num"] = num_pool.pop()
        roster.append(pl)
    
    return roster

def generate_filler_teams(existing_teams_count, current_teams_data):
    TARGETS = {"EN": 20, "ES": 20, "IT": 20, "DE": 18, "FR": 18, "PT": 18, "BR": 20, "AR": 28, "CO": 20, "US": 29, "JP": 20}
    
    COLORS = [
        (200, 30, 30), (30, 30, 200), (30, 200, 30), (255, 255, 255), (0, 0, 0),
        (255, 215, 0), (163, 26, 81), (0, 130, 50), (130, 190, 240), (255, 100, 0),
        (128, 0, 128), (0, 128, 128), (128, 128, 0)
    ]
    
    generated_teams = []
    generated_rosters_db = {}
    
    counts = {k: 0 for k in TARGETS}
    for t in current_teams_data:
        lg = t.get("league", "EN")  # Default to EN if not specified
        if lg in counts:
            counts[lg] += 1
            
    # Track used identifiers to avoid collisions
    used_shorts = set(t.get("short") for t in current_teams_data)
    
    for lg, target in TARGETS.items():
        needed = target - counts.get(lg, 0)
        for i in range(needed):
            city = random.choice(CITIES[lg])
            prefix = random.choice(TEAM_NAMES[lg])
            name = f"{prefix} {city}" if random.random() < 0.5 else f"{city} {prefix}"
            
            # Create a unique short
            short = f"{city[:3].upper()}{random.randint(0,99)}"
            while short in used_shorts:
                short = f"{city[:3].upper()}{random.randint(0,99)}"
            used_shorts.add(short)
            
            p1 = random.choice(COLORS)
            p2 = random.choice(COLORS)
            while p1 == p2: p2 = random.choice(COLORS)
            
            ovr = random.randint(70, 78) # Mid table stats
            
            generated_teams.append({
                "name": name,
                "short": short,
                "primary": p1,
                "secondary": p2,
                "accent": (255, 255, 255),
                "badge_shape": random.choice(["shield", "circle", "diamond", "crown"]),
                "league": lg,
                "stats": {"speed": ovr, "shot": ovr, "defense": ovr, "passing": ovr},
                "is_filler": True
            })
            
            generated_rosters_db[short] = generate_roster(lg, ovr)
            
    return generated_teams, generated_rosters_db

# --- WOMEN FOOTBALLERS & SOCIAL PERSONALITIES NAME GENERATION ---

FEMALE_FIRST_NAMES = {
    "EN": ["Lucy", "Chloe", "Lauren", "Mary", "Keira", "Georgia", "Alessia", "Millie", "Leah", "Ella", "Sophie", "Beth", "Rachel", "Alex", "Steph"],
    "ES": ["Aitana", "Alexia", "Salma", "Mapi", "Olga", "Athenea", "Cata", "Maria", "Irene", "Jenni", "Laia", "Ona", "Esther", "Lucia", "Sandra"],
    "FR": ["Kadidiatou", "Grace", "Marie", "Sakina", "Sandie", "Eugénie", "Selma", "Wendie", "Delphine", "Amandine", "Kenza", "Vicki", "Elisa"],
    "DE": ["Alexandra", "Lea", "Lena", "Giulia", "Sara", "Klara", "Jule", "Laura", "Svenja", "Kathrin", "Melanie", "Marina", "Felicitas"],
    "PT": ["Jessica", "Diana", "Ana", "Carolina", "Tatiana", "Dolores", "Vanessa", "Ines", "Fatima", "Joana"],
    "BR": ["Marta", "Debinha", "Rafaelle", "Tamires", "Gabi", "Ary", "Bia", "Kerolin", "Lorena", "Tainara", "Cristiane", "Formiga", "Andressa"],
    "IT": ["Manuela", "Valentina", "Cristiana", "Barbara", "Elena", "Aurora", "Sofia", "Giulia", "Martina", "Chiara", "Lisa", "Laura", "Alia"],
    "NL": ["Lieke", "Vivianne", "Jill", "Sherida", "Daniëlle", "Jackie", "Esmee", "Lineth", "Tessa", "Janice", "Aniek", "Victoria", "Merel"],
    "BE": ["Tessa", "Janice", "Sari", "Davina", "Laura", "Julie", "Justine", "Amber", "Fara", "Elena"],
    "HR": ["Ana", "Marija", "Ivana", "Petra", "Kristina", "Leonarda", "Karla", "Antonia", "Helena", "Tea"],
    "MA": ["Ghizlane", "Anissa", "Elodie", "Fatima", "Salma", "Hanane", "Yasmin", "Sofia", "Rania", "Kenza"],
    "MX": ["Stephany", "Kenti", "Charlyn", "Katty", "Jacqueline", "Greta", "Rebeca", "Lizbeth", "Alicia", "Carolina"],
    "US": ["Sophia", "Trinity", "Mallory", "Rose", "Crystal", "Lindsey", "Emily", "Naomi", "Jenna", "Tierna", "Alex", "Megan", "Alyssa", "Carli"],
    "CL": ["Christiane", "Francisca", "Yanara", "Karen", "Camila", "Carla", "Maria", "Rosario", "Yessenia", "Javiera"],
    "EC": ["Ligia", "Kerly", "Madelin", "Emily", "Ambar", "Gianina", "Nayely", "Analiz", "Danna", "Joselyn"],
    "PY": ["Lice", "Jessica", "Fanny", "Limpia", "Dulce", "Camila", "Ramona", "Fabiola", "Gloria", "Maria"]
}

def generate_female_player_name(nat):
    """Generates a realistic female name based on the country code."""
    es_group = ["AR", "CO", "UY", "MX", "CL", "EC", "PY"]
    lookup_nat = nat
    if nat in es_group and nat not in FEMALE_FIRST_NAMES:
        lookup_nat = "ES"
    
    first_names = FEMALE_FIRST_NAMES.get(lookup_nat, FEMALE_FIRST_NAMES["EN"])
    pats = PATTERNS.get(nat, PATTERNS["EN"])
    
    first_name = random.choice(first_names)
    last_name = random.choice(pats["last"])
    return f"{first_name} {last_name}"

