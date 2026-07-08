import random
import copy
import datetime
from settings import *
from data.teams import TEAMS
from data.rosters import get_base_rosters, calculate_ovr
from data.procedural import generate_filler_teams
from settings import *

ITEM_SHOP = [
    {"id": "boots_speed", "name": "Botas AeroVeloce", "desc": "+5 Velocidad, -2 Tiro", "price": 0.5, "stats": {"speed": 5, "shot": -2}},
    {"id": "energy_drink", "name": "Bebida Energética", "desc": "+3 Velocidad, -1 Defensa", "price": 0.2, "stats": {"speed": 3, "defense": -1}},
    {"id": "precision_ball", "name": "Balón Elite", "desc": "+5 Tiro, -2 Velocidad", "price": 0.6, "stats": {"shot": 5, "speed": -2}},
    {"id": "tactical_watch", "name": "Reloj Táctico", "desc": "+5 Pase, -1 Velocidad", "price": 0.4, "stats": {"passing": 5, "speed": -1}},
    {"id": "shin_guards", "name": "Canilleras Pro", "desc": "+5 Defensa, -2 Pase", "price": 0.5, "stats": {"defense": 5, "passing": -2}},
]

class CareerManager:
    """Core logic for Career Mode."""
    
    def __init__(self):
        import os
        self.active = False
        self.manager_name = ""
        self.start_year_offset = 0 # Added to track generational legacy skips
        self.difficulty = 5  # 1-10 scale, persisted with saves
        
        # Save config paths
        self.save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "saves")
        self.manifest_file = os.path.join(self.save_dir, "career_slots.json")
        self.current_slot = 1
        
        self.load_config()
        
        # State
        self.year = 1
        self.current_date = None
        self.season_start = None
        self.season_end = None
        self.player_team = None
        self.league_id = "EN"
        self.leagues = ["EN", "ES", "IT", "DE", "FR", "PT", "TR", "BE", "RU", "RO", "SC", "AT", "BR", "AR", "CO", "CL", "PE", "MX", "US", "JP", "AF"]
        
        # Datasets (divorced from base database)
        self.teams = []
        self.rosters = {}
        
        # Calendar variables
        self.calendar = {} # {"YYYY-MM-DD": [{"type": "LIGA", "lg": "EN", "matches": [(t1, t2)...]}]}
        self.standings = {} # {league_id: {short: {"pts":0, ...}}}
        
        self.scorers = {} # {"LIGA_EN": {name: goals}, "CHAMPIONS": {name: goals}}
        self.assists = {} # {"LIGA_EN": {name: assists}, "CHAMPIONS": {name: assists}}
        
        # Continental tournaments (Clubs)
        self.continental = {}
        
        # International Tournaments (National Teams)
        self.intl_tournaments = {} # {"WORLD_CUP": {...}, "EURO": {...}, "COPA_AMERICA": {...}}
        
        # National Cups (Clubs)
        self.national_cups = {} # {league_id: {"name": "Copa...", "round": "R16", "bracket": {}, "matchday": 0}}
        
        # Scouting & Market
        self.scouted_players = []
        self.negotiations = []
        
        # Transfer windows & Manager offers
        self.transfer_window_open = False
        self.manager_offers = []      # offers FROM other teams to the player
        self.manager_applications = [] # offers the player SENT to other teams
        self.retired = False
        self.free_agents = []         # Jugadores paródicos en el club 'Libre'
        self.international_matches = [] # Partidos de selección programados
        self.cup_performers = {}      # {"COPA_ES": [perf...]}
        self.managing_nt = None       # "AR", "EN", etc.
        self.is_called_up = False     # True si el jugador está convocado
        self.nt_stats = {"matches": 0, "goals": 0}
        
        # Performance tracking for TOTW/POTM
        self.weekly_performers = [] # List of {name, team, rating, pos}
        self.monthly_performers = [] # List of {name, team, rating, pos}
        
        # News & Inbox
        self.news = [] # List of {date, category, title, desc, seen}
        self.inbox = [] # List of {date, type, subject, content, data, read}
        self.pending_requests = [] # List of {type, days_left, target_state}
        
        # Career statistics (cumulative across all seasons)
        self.career_stats = {
            "matches": 0, "wins": 0, "draws": 0, "losses": 0,
            "goals_scored": 0, "goals_conceded": 0,
            "player_goals": 0, "player_assists": 0,
            "matches_played": 0, # Solo partidos jugados en cancha (modo jugador)
            "titles": [], "teams_managed": [],
            "seasons_completed": 0,
            "coach_confidence": 40,
            "teammate_rel": 50,  # Relación con compañeros (0-100)
            "fan_rel": 50,       # Relación con la afición (0-100)
            "board_rel": 50,     # Relación con la directiva (0-100)
            "transfers_in": 0, "transfers_out": 0,
            "total_spent": 0, "total_earned": 0,
            "rating_history": [], "avg_rating": 0.0,
            "prestige": 100, # 0 to 1000
            "money": 0.0,   # Millions
            "individual_awards": [], # New: Balón de Oro, etc.
            "relationships": {},  # {handle: {"name": str, "gender": str, "affinity": int, "status": str, "type": str}}
            "partnerships": {},  # {player_name: {"team": str, "matches": int, "goals_together": int, "assists_to_you": int, "assists_from_you": int}}
            "rivalries": {},     # {player_name: {"team": str, "pos": str, "matches_against": int, "your_wins": int, "their_wins": int, "their_goals": int, "their_awards": []}}
        }

        
        # Final standings snapshot (saved before reset for continental qualification)
        self._final_standings = {}
        
        # Player Career Mode attributes
        self.mode = "manager" # "manager" or "player"
        self.career_player = None # Store player dict if mode == "player"
        self.skill_points = 0
        self.nationality = None  # Código de país del entrenador/jugador ("AR", "EN", etc.)
        self.inventory = []      # List of item IDs
        self.equipped_items = [] # List of item IDs (max 2)
        
        # Agent & Status
        self.agent = {"name": "Ninguno", "level": 0, "commission": 0.0}
        self.agent_suggestions = [] # New: suggestions to the agent
        self.agent_recommendations = [] # New: clubs that contacted the agent
        self.player_status = "Suplente" # "Titular", "Suplente", "No Convocado"
        
        # Objectives & Transfers history
        self.objectives = [] # List of {desc, type, target, current, status}
        self.joined_date = None # Date when player joined current club
        self.joined_transfer_window = None # Window name when joined
        
        # Narrative & History
        self.team_history = []  # List of {short, ovr, goals, matches, titles}
        self.milestones = []    # List of {date, type, desc, team}
        self.current_team_stats = {"goals": 0, "matches": 0}

    @property
    def can_change_number(self):
        if self.mode != "player": return False
        if not self.joined_date or not self.joined_transfer_window: return False
        
        # Must be in the SAME transfer window as joined
        if not self.transfer_window_open: return False
        if self._get_transfer_window_name() != self.joined_transfer_window: return False
        
        # Only for first 30 days of that window (safety)
        delta = (self.current_date - self.joined_date).days
        return delta <= 31

    def _get_player_role(self, p):
        """Calcula el rol jerárquico de un jugador en la plantilla basándose en el equipo."""
        age = p.get("age", 19)
        ovr = p.get("ovr", 75)
        
        # Comparar con la media del equipo
        team_short = p.get("team_short")
        if not team_short and self.player_team: team_short = self.player_team["short"]
        
        team_ovr = self.get_team_ovr(team_short) if team_short else 75
        diff = ovr - team_ovr
        
        if diff >= 7: return "Estrella"
        if diff >= 2: return "Fijo"
        if diff >= -3: return "Rotación"
        if age <= 21: return "Promesa"
        return "Ocasional"

    def calculate_player_value(self, p):
        """Calcula valor de mercado realista en millones (basado en OVR y edad)."""
        import math
        ovr = p.get("ovr", 75)
        age = p.get("age", 19)
        
        # Escala exponencial: 60->0.1M, 75->5M, 85->45M, 93->150M
        base = 0.12 * math.exp((ovr - 60) * 0.22)
        
        # Ajuste por edad (Los jóvenes valen más)
        if age <= 21: mult = 1.5
        elif age <= 25: mult = 1.2
        elif age >= 32: mult = 0.4
        else: mult = 1.0
        
        # Performance/Milestone modifier
        mult *= p.get("market_modifier", 1.0)
        
        # Awards modifier: Each award adds +10% value, capped at 100% (2.0x)
        awards = self.career_stats.get("individual_awards", [])
        award_bonus = min(1.0, len(awards) * 0.1)
        mult *= (1.0 + award_bonus)
        
        return round(base * mult, 1)

    def _boost_roster_value(self, team_short, boost=0.1):
        """Increases the market modifier for all players in a roster."""
        roster = self.rosters.get(team_short, [])
        for p in roster:
            mod = p.get("market_modifier", 1.0)
            p["market_modifier"] = round(mod + boost, 2)

    def _calculate_salary(self, p):
        """Calcula un salario anual realista en millones."""
        import math
        ovr = p.get("ovr", 75)
        role = self._get_player_role(p)
        
        # Base por calidad
        base = 0.05 * math.exp((ovr - 60) * 0.15)
        role_mult = {"Estrella": 2.5, "Fijo": 1.4, "Rotación": 0.8, "Promesa": 0.5, "Ocasional": 0.3}
        
        # Un mejor agente negocia un mejor sueldo base (+15% por nivel)
        agent_bonus = 1.0 + (self.agent.get("level", 0) * 0.15)
        
        salary = base * role_mult.get(role, 1.0) * agent_bonus
        return round(max(0.05, salary), 2)

    def _update_prestige(self, change):
        """Actualiza el medidor de prestigio del jugador."""
        scaled_change = change * 10
        self.career_stats["prestige"] = min(1000, max(0, self.career_stats["prestige"] + scaled_change))

    def buy_item(self, item_id):
        item = next((i for i in ITEM_SHOP if i["id"] == item_id), None)
        if not item: return False, "Item no encontrado."
        if item_id in self.inventory: return False, "Ya tienes este item."
        if self.career_stats["money"] < item["price"]: return False, "Dinero insuficiente."
        
        self.career_stats["money"] -= item["price"]
        self.inventory.append(item_id)
        return True, f"Compraste {item['name']}."

    def equip_item(self, item_id):
        if item_id not in self.inventory: return False
        if item_id in self.equipped_items:
            self.equipped_items.remove(item_id)
            self._apply_item_stats(item_id, remove=True)
            return True
        if len(self.equipped_items) >= 2: return False
        
        self.equipped_items.append(item_id)
        self._apply_item_stats(item_id)
        return True

    def _apply_item_stats(self, item_id, remove=False):
        item = next((i for i in ITEM_SHOP if i["id"] == item_id), None)
        if not item: return
        mult = -1 if remove else 1
        for stat, val in item["stats"].items():
            self.career_player["s"][stat] += val * mult
        from data.rosters import calculate_ovr
        self.career_player["ovr"] = calculate_ovr(self.career_player["s"])

    def evaluate_contract_proposal(self, role, salary):
        """El club CPU evalúa la propuesta del usuario en modo Jugador."""
        prestige = self.career_stats.get("prestige", 100)
        ovr = self.career_player["ovr"]
        
        # Fair salary calculation
        fair_salary = self._calculate_salary(self.career_player)
        
        # Tolerance based on prestige
        tolerance = 1.0 + (prestige / 1000.0) * 0.5 # Up to 50% more if top prestige
        max_salary = fair_salary * tolerance
        
        if salary > max_salary * 1.5:
            return "rejected", 0, "Tu propuesta salarial es ridícula para el presupuesto del club."
        
        if salary > max_salary:
            counter = round(max_salary, 2)
            return "counter", counter, f"No llegamos a tanto. Te ofrecemos ${counter}M como {role}."
            
        # Check role consistency
        fair_role = self._get_player_role(self.career_player)
        role_priority = ["Estrella", "Fijo", "Rotación", "Promesa", "Ocasional"]
        try:
            if role_priority.index(role) < role_priority.index(fair_role):
                # User wants a higher role than deserved
                if prestige < 600:
                    return "counter", salary, f"Aceptamos el sueldo, pero tu rol será {fair_role}."
        except ValueError:
            pass
                
        # Accept
        return "accepted", salary, "¡Trato hecho! Nos alegra contar contigo."
        
    def add_news(self, category, title, desc, importance=1, expiry_days=7):
        date_str = self.current_date.strftime("%d %b %Y") if self.current_date else "N/A"
        self.news.insert(0, {
            "date": date_str,
            "category": category.upper(),
            "title": title,
            "desc": desc,
            "importance": importance,
            "seen": False,
            "expiry_date": (self.current_date + datetime.timedelta(days=expiry_days)).isoformat() if self.current_date else None
        })

    def add_rumor(self, team_name, importance=1):
        """Generates a media rumor about the player and a specific team."""
        if self.mode != "player" or not self.career_player: return
        
        p_name = self.career_player["name"]
        headlines = [
            f"¿{p_name} al {team_name}?",
            f"Interés del {team_name}",
            f"Rumores en {team_name}",
            f"Contactos por {p_name}"
        ]
        bodies = [
            f"Fuentes cercanas al club aseguran que el {team_name} está siguiendo muy de cerca la situación de {p_name}.",
            f"Se ha visto al agente de {p_name} en las oficinas del {team_name}. ¿Habrá fichaje pronto?",
            f"El {team_name} busca reforzar su plantilla y el nombre de {p_name} suena con mucha fuerza en los pasillos.",
            f"Aunque no hay oferta oficial, el interés del {team_name} por {p_name} es el secreto a voces del mercado."
        ]
        
        # Add prestige prefix if player has major awards
        awards = self.career_stats.get("individual_awards", [])
        if awards and random.random() < 0.5:
            award = random.choice(awards)
            if "Balón de Oro" in award: prefix = "¡BOMBA! El ganador del Balón de Oro, "
            elif "Bota de Oro" in award: prefix = "El goleador de moda, "
            else: prefix = "La estrella premiada, "
            
            headlines = [prefix + h for h in headlines]
            bodies = [f"El {team_name} sabe que fichar a un {award} como {p_name} no será barato, pero están dispuestos a negociar." for _ in range(4)]

        
        self.add_news("MERCADO", random.choice(headlines), random.choice(bodies), importance=importance, expiry_days=5)
        if len(self.news) > 50: self.news.pop() # Cap history

    def add_email(self, type, subject, content, data=None):
        """Añade un correo al buzón del usuario."""
        date_str = self.current_date.strftime("%d %b %Y") if self.current_date else "N/A"
        self.inbox.insert(0, {
            "date": date_str,
            "type": type, # 'offer', 'info', 'alert', 'contract'
            "subject": subject,
            "content": content,
            "data": data or {},
            "read": False
        })
        if len(self.inbox) > 50: self.inbox.pop()

    def _ensure_social_media_exists(self):
        """Initializes the social_media data structure in career_stats if not present."""
        if "social_media" not in self.career_stats:
            self.career_stats["social_media"] = {
                "cm_tier": 0,
                "strategy": "professional",
                "followers": 1200,
                "posts": [],
                "dms": [],
                "player_handle": ""
            }
        else:
            sm = self.career_stats["social_media"]
            if "cm_tier" not in sm: sm["cm_tier"] = 0
            if "strategy" not in sm: sm["strategy"] = "professional"
            if "followers" not in sm: sm["followers"] = 1200
            if "posts" not in sm: sm["posts"] = []
            if "dms" not in sm: sm["dms"] = []
            if "player_handle" not in sm: sm["player_handle"] = ""
            
        if "relationships" not in self.career_stats:
            self.career_stats["relationships"] = {}
        if "children" not in self.career_stats:
            self.career_stats["children"] = []
        self._ensure_agent_profile()

    def _ensure_agent_profile(self):
        if not self.agent or self.agent.get("level", 0) == 0:
            return
        
        if "agent_profile" not in self.career_stats:
            level = self.agent.get("level", 1)
            p_name = self.career_player["name"] if self.career_player else "Jugador"
            surname = p_name.strip().split()[-1] if len(p_name.strip().split()) > 1 else "García"
            
            is_female = random.random() < 0.5
            
            if level == 1:
                # Familiar
                if is_female:
                    names = ["Laura", "Sofía", "María", "Lucía", "Gabriela", "Marta", "Elena", "Ana"]
                    name = f"{random.choice(names)} {surname} (Familiar)"
                    gender = "female"
                    handle = f"@{name.split()[0].lower()}_{surname.lower()}_agt"
                else:
                    names = ["Carlos", "Daniel", "Diego", "Alejandro", "Andrés", "Javier", "Luis", "Pedro"]
                    name = f"{random.choice(names)} {surname} (Familiar)"
                    gender = "male"
                    handle = f"@{name.split()[0].lower()}_{surname.lower()}_agt"
            else:
                # Profesional / Leyenda
                if is_female:
                    names = ["Silvia Mendes", "Wanda Nara Style", "Marta Agent", "Carla Pinho", "Verónica Romero", "Helena Costa"]
                    n = random.choice(names)
                    name = n
                    gender = "female"
                    handle = f"@{name.lower().replace(' ', '').replace('.', '')}_agt"
                else:
                    names = ["Jorge Mendes Style", "Mino Raiola Jr", "Pini Zahavi Jr", "Federico Pastorello", "Jonathan Barnett"]
                    n = random.choice(names)
                    name = n
                    gender = "male"
                    handle = f"@{name.lower().replace(' ', '').replace('.', '')}_agt"
            
            self.career_stats["agent_profile"] = {
                "name": name,
                "gender": gender,
                "handle": handle,
                "affinity": 50,
                "status": "Colega"
            }
            self.update_relationship(handle, name, gender, "agent", 0)

    def update_relationship(self, handle, name, gender, rel_type, affinity_change):
        if "relationships" not in self.career_stats:
            self.career_stats["relationships"] = {}
            
        if handle not in self.career_stats["relationships"]:
            if rel_type in ("agent", "teammate"):
                status = "Colega"
                affinity = 50
            else:
                status = "Conocida"
                affinity = 20
                
            self.career_stats["relationships"][handle] = {
                "name": name,
                "gender": gender,
                "type": rel_type,
                "affinity": affinity,
                "status": status
            }
            
        r = self.career_stats["relationships"][handle]
        old_status = r.get("status", "Conocida")
        old_aff = r.get("affinity", 50)
        
        new_aff = min(100, max(-100, old_aff + affinity_change))
        r["affinity"] = new_aff
        
        new_status = old_status
        
        if r["type"] == "teammate":
            if new_aff <= -60:
                new_status = "Enemistad Extrema"
            elif new_aff <= -30:
                new_status = "Rival"
            elif new_aff < 0:
                new_status = "Relación Tensa"
            elif new_aff < 40:
                new_status = "Colega"
            elif new_aff < 70:
                new_status = "Amigo"
            else:
                new_status = "Amigo Íntimo"
        elif r["type"] == "agent":
            if new_aff <= -60:
                new_status = "Enemistad Extrema"
            elif new_aff <= -30:
                new_status = "Rival"
            elif new_aff < 0:
                new_status = "Relación Tensa"
            elif new_aff < 40:
                new_status = "Colega"
            elif new_aff < 70:
                new_status = "Amiga" if gender == "female" else "Amigo"
            else:
                if gender == "female":
                    if old_status in ("Novia", "Esposa"):
                        new_status = old_status
                    else:
                        new_status = "Amiga Íntima"
                else:
                    new_status = "Amigo Íntimo"
        else:
            is_fem = (gender == "female")
            if new_aff <= -60:
                new_status = "Enemistad Extrema"
            elif new_aff <= -30:
                new_status = "Rival"
            elif new_aff < 0:
                new_status = "Relación Tensa"
            elif new_aff < 40:
                new_status = "Conocida" if is_fem else "Conocido"
            elif new_aff < 70:
                new_status = "Amiga" if is_fem else "Amigo"
            else:
                if is_fem and old_status in ("Novia", "Esposa"):
                    new_status = old_status
                else:
                    new_status = "Amiga Íntima" if is_fem else "Amigo Íntimo"
                        
        r["status"] = new_status
        return old_status != new_status

    def _generate_achievement_reactions(self, stats_user, match_result):
        if not stats_user or self.mode != "player" or not self.career_player: return
        sm = self.career_stats["social_media"]
        p_name = self.career_player["name"]
        p_handle = sm.get("player_handle") or f"@{p_name.lower().replace(' ', '')}"
        goals = stats_user.get("goals", 0)
        rating = stats_user.get("rating", 6.0)
        date_str = self.current_date.strftime("%d %b %Y") if self.current_date else "Hoy"
        
        partner_handle = None
        partner_name = None
        partner_status = None
        for h, rel in self.career_stats.get("relationships", {}).items():
            if rel.get("status") in ("Novia", "Esposa"):
                partner_handle = h
                partner_name = rel["name"]
                partner_status = rel["status"]
                break
                
        if partner_handle:
            if goals > 0 or rating >= 7.5:
                if random.random() < 0.5:
                    if partner_status == "Esposa":
                        msg = f"¡Felicidades mi amor! ⚽ Qué orgullo verte jugar hoy, ¡ese gol/rendimiento fue espectacular! 🌟 Te amo, ¡disfruta de la victoria! Hoy celebramos en casa."
                    else:
                        msg = f"¡Cariño! Qué partidazo te mandaste hoy, ¡vi tu gol/jugadas por la tele y estuve gritando de la emoción! 😍 Eres el mejor novio del mundo."
                    choices = [
                        {"text": "¡Te amo hermosa! Todo el esfuerzo es por ti y la familia. ❤️", "effects": {"affinity_change": 8}},
                        {"text": "¡Gracias amor! Nos vemos pronto para celebrar.", "effects": {"affinity_change": 5}}
                    ]
                    self._add_dm(partner_name, partner_handle, "female_player", msg, choices)
                    dm_added = sm["dms"][0]
                    dm_added["relationship_handle"] = partner_handle
                    dm_added["gender"] = "female"
                    
                if random.random() < 0.3:
                    if partner_status == "Esposa":
                        content = f"¡Orgullosa de mi maravilloso esposo {p_handle} por su partidazo hoy! ¡Ese gol fue de otra galaxia! ⚽✨ Te amo. ❤️"
                    else:
                        content = f"¡Felicidades a mi novio {p_handle}! Qué orgullo verte brillar hoy en la cancha. ¡Te amo mucho! 😍🏆"
                    sm["posts"].insert(0, {
                        "id": f"post_part_{random.randint(10000,99999)}",
                        "date": date_str,
                        "author": partner_name,
                        "handle": partner_handle,
                        "content": content,
                        "likes": random.randint(300, 2000),
                        "retweets": random.randint(50, 500),
                        "type": "fan",
                        "read": False
                    })
                    
        agent_prof = self.career_stats.get("agent_profile")
        if agent_prof and (goals > 0 or rating >= 7.5) and random.random() < 0.3:
            content = f"Gran rendimiento de mi representado {p_handle} hoy en la cancha ({rating:.1f}). Clave para la victoria. Sigan atentos a su evolución."
            sm["posts"].insert(0, {
                "id": f"post_agt_{random.randint(10000,99999)}",
                "date": date_str,
                "author": agent_prof["name"],
                "handle": agent_prof["handle"],
                "content": content,
                "likes": random.randint(100, 800),
                "retweets": random.randint(20, 200),
                "type": "media",
                "read": False
            })

        roster = self.rosters.get(self.player_team["short"], []) if self.player_team else []
        teammates = [p for p in roster if not p.get("is_user_player")]
        if teammates:
            if goals > 0 or rating >= 7.5:
                tm = random.choice(teammates)
                tm_handle = f"@{tm['name'].lower().replace(' ', '')}"
                tm_rel = self.career_stats.get("relationships", {}).get(tm_handle, {})
                tm_aff = tm_rel.get("affinity", 50)
                
                if tm_aff >= 50 and random.random() < 0.3:
                    content = f"¡Qué partidazo jugamos hoy, hermano! Qué gran asistencia/gol de {p_handle}. ¡A seguir sumando! 👊🔥"
                    sm["posts"].insert(0, {
                        "id": f"post_tm_{random.randint(10000,99999)}",
                        "date": date_str,
                        "author": tm["name"],
                        "handle": tm_handle,
                        "content": content,
                        "likes": random.randint(100, 600),
                        "retweets": random.randint(20, 150),
                        "type": "fan",
                        "read": False
                    })
                elif tm_aff < 50 and random.random() < 0.15:
                    content = f"Suerte con el resultado hoy. Algunos se creen que ganan el partido solos en el vestuario."
                    sm["posts"].insert(0, {
                        "id": f"post_tm_riv_{random.randint(10000,99999)}",
                        "date": date_str,
                        "author": tm["name"],
                        "handle": tm_handle,
                        "content": content,
                        "likes": random.randint(50, 300),
                        "retweets": random.randint(10, 80),
                        "type": "fan",
                        "read": False
                    })

    def _generate_transfer_reactions(self, old_short, new_short):
        if self.mode != "player" or not self.career_player: return
        self._ensure_social_media_exists()
        sm = self.career_stats["social_media"]
        p_name = self.career_player["name"]
        p_handle = sm.get("player_handle") or f"@{p_name.lower().replace(' ', '')}"
        
        old_team = self.get_team_by_short(old_short)
        new_team = self.get_team_by_short(new_short)
        old_name = old_team["name"] if old_team else "Club anterior"
        new_name = new_team["name"] if new_team else "Club nuevo"
        
        date_str = self.current_date.strftime("%d %b %Y") if self.current_date else "Hoy"
        
        player_content = f"Muy emocionado de iniciar esta nueva etapa en mi carrera con las filas del {new_name}. Gracias al {old_name} por los momentos vividos y a la afición por su apoyo. ¡A darlo todo! 👊⚽ #Fichaje"
        sm["posts"].insert(0, {
            "id": f"post_trans_user_{random.randint(1000,9999)}",
            "date": date_str,
            "author": p_name,
            "handle": p_handle,
            "content": player_content,
            "likes": int(sm["followers"] * random.uniform(0.12, 0.30)) + 10,
            "retweets": int(sm["followers"] * random.uniform(0.02, 0.08)) + 3,
            "type": "user",
            "read": True
        })
        
        agent_prof = self.career_stats.get("agent_profile")
        if agent_prof:
            agent_content = f"Orgulloso de guiar el futuro de mi representado {p_handle} al {new_name}. Un gran acuerdo deportivo y económico. ¡El cielo es el límite! 🚀🤝"
            sm["posts"].insert(0, {
                "id": f"post_trans_agt_{random.randint(1000,9999)}",
                "date": date_str,
                "author": agent_prof["name"],
                "handle": agent_prof["handle"],
                "content": agent_content,
                "likes": random.randint(150, 1000),
                "retweets": random.randint(30, 250),
                "type": "media",
                "read": False
            })
            
        partner_handle = None
        partner_name = None
        partner_status = None
        partner_rel = None
        for h, rel in self.career_stats.get("relationships", {}).items():
            if rel.get("status") in ("Novia", "Esposa"):
                partner_handle = h
                partner_name = rel["name"]
                partner_status = rel["status"]
                partner_rel = rel
                break
                
        if partner_handle:
            partner_type = partner_rel.get("type", "fan")
            
            # Si tiene una profesion atada a su club/ubicacion, no se muda automaticamente
            if partner_type in ("player", "female_player", "journalist"):
                p_work = partner_rel.get("team") or "mi club/trabajo"
                msg = f"¡Qué emoción, mi amor! 💕 Un nuevo desafío en el {new_name}. Estoy tan orgullosa de ti y de este gran paso profesional. Aunque me entristece pensar que ahora estaremos separados por la distancia debido a mi trabajo en {p_work}. ¡Te apoyaré siempre! Te amo."
                choices = [
                    {"text": "Es difícil la distancia, mi amor, pero nuestro amor puede con todo. Te llamaré a diario. ❤️", "effects": {"affinity_change": 10}},
                    {"text": "El fútbol exige sacrificios, amor. Estemos en contacto constante.", "effects": {"affinity_change": 6}}
                ]
            else:
                # Si es hincha o influencer, se muda con el jugador y se actualiza su ubicacion
                partner_rel["league"] = self.player_team.get("league", "ES")
                partner_rel["team_short"] = self.player_team.get("short")
                msg = f"¡Qué emoción, mi amor! 💕 Un nuevo desafío en el {new_name}. Estoy tan orgullosa de ti y de este gran paso profesional. ¡Ya quiero empacar y mudarnos juntos a esta nueva ciudad! Te amo."
                choices = [
                    {"text": "¡Gracias mi vida! Eres mi compañera de viaje y mi mayor tesoro. ¡Empecemos esta aventura juntos! ❤️", "effects": {"affinity_change": 10}},
                    {"text": "Muchas gracias, mi amor. Tu apoyo lo es todo para mí.", "effects": {"affinity_change": 5}}
                ]
                
            self._add_dm(partner_name, partner_handle, "female_player", msg, choices)
            dm_added = sm["dms"][0]
            dm_added["relationship_handle"] = partner_handle
            dm_added["gender"] = "female"
            
            partner_content = f"¡Nueva etapa! Muy feliz por acompañar y apoyar a {p_handle} en su nuevo desafío con el {new_name}. ¡Te amo cariño! 💑⚽ #NuevaAventura"
            sm["posts"].insert(0, {
                "id": f"post_trans_part_{random.randint(1000,9999)}",
                "date": date_str,
                "author": partner_name,
                "handle": partner_handle,
                "content": partner_content,
                "likes": random.randint(400, 2500),
                "retweets": random.randint(60, 600),
                "type": "fan",
                "read": False
            })

    def _update_social_media(self, match_result=None):
        """Processes daily social media changes (CM pay, followers, posts, and DMs)."""
        self._ensure_social_media_exists()
        sm = self.career_stats["social_media"]
        cm_tier = sm["cm_tier"]
        
        # CM weekly payroll on Mondays
        if self.current_date.weekday() == 0 and cm_tier > 0:
            costs = {1: 0.001, 2: 0.004, 3: 0.015}
            cost = costs.get(cm_tier, 0.0)
            if self.career_stats.get("money", 0.0) >= cost:
                self.career_stats["money"] = round(self.career_stats["money"] - cost, 4)
                if random.random() < 0.25:
                    self.add_email("info", "Pago de CM Realizado",
                                   f"Se han debitado de tu cuenta ${cost}M por los servicios semanales del Community Manager (Nivel {cm_tier}).")
            else:
                sm["cm_tier"] = 0
                self.add_email("alert", "CM Despedido por Impago",
                               "No tienes saldo suficiente para pagar a tu Community Manager. Los servicios automatizados han sido cancelados.")

        # Followers grow dynamically based on prestige
        prestige = self.career_stats.get("prestige", 100)
        target_followers = prestige * 180 + random.randint(-100, 100)
        diff = target_followers - sm["followers"]
        if diff != 0:
            sm["followers"] = max(100, int(sm["followers"] + diff * 0.08))

        # Handle matchday vs regular day content
        if match_result is not None and self.mode == "player" and self.career_player:
            p_name = self.career_player["name"]
            stats_user = next((ps for ps in match_result.get("player_stats", []) if ps.get("name", "").lower().strip() == p_name.lower().strip()), None)
            
            if cm_tier > 0:
                self._cm_auto_post(stats_user, match_result)
                
            self._generate_match_feed(stats_user, match_result)
            self._generate_match_dms(stats_user, match_result)
            self._generate_achievement_reactions(stats_user, match_result)
        else:
            if random.random() < 0.15:
                self._generate_random_feed()
            if random.random() < 0.35:
                self._generate_random_dms()

        # Cap histories to avoid huge files
        if len(sm["posts"]) > 50:
            sm["posts"] = sm["posts"][:50]
        if len(sm["dms"]) > 30:
            sm["dms"] = sm["dms"][:30]

    def _process_weekly_pregnancy(self):
        """Advances pregnancy week-by-week and triggers key milestones/DMs on Mondays."""
        if self.mode != "player" or not self.career_player:
            return
            
        self._ensure_social_media_exists()
        sm = self.career_stats["social_media"]
        relationships = self.career_stats.get("relationships", {})
        
        for h, rel in list(relationships.items()):
            # Solo aplica a la esposa
            if rel.get("status") != "Esposa":
                continue
                
            # 1. Si está embarazada
            if rel.get("is_pregnant"):
                # Incrementar semanas
                rel["pregnancy_weeks"] = rel.get("pregnancy_weeks", 0) + 1
                weeks = rel["pregnancy_weeks"]
                
                # Hit 1: Semana 12 (Ecografía y Anuncio)
                if weeks == 12:
                    msg = f"¡Hola mi amor! Hoy me hicieron la ecografía de las 12 semanas y ¡mira! Ya se le ve forma al bebé. 🥹 Es el momento más hermoso de mi vida. ¿Qué opinas si publicamos la noticia para compartirla con nuestros seguidores o preferimos mantenerlo en privado por ahora? 📸❤️"
                    choices = [
                        {"text": "¡Publiquémoslo ya! Quiero que todo el mundo comparta nuestra alegría. 📸👶", "effects": {"prestige": 15, "fan_rel": 10, "affinity_change": 10, "news_trigger": "embarazo_anunciado"}, "next_dm": {
                            "message": "¡Sii! Subí la foto de la ecografía y las redes están estallando de felicitaciones. ¡Te amo papá! 😍✨",
                            "choices": []
                        }},
                        {"text": "Prefiero que lo mantengamos en la intimidad familiar por un tiempo, mi amor. Es más seguro.", "effects": {"affinity_change": 5, "coach_confidence": 3}, "next_dm": {
                            "message": "Tienes mucha razón, cariño. Es un momento sagrado para nosotros dos. Gracias por ser tan protector. ❤️",
                            "choices": []
                        }}
                    ]
                    self._add_dm(rel["name"], h, "female_player", msg, choices)
                    dm_added = sm["dms"][0]
                    dm_added["relationship_handle"] = h
                    dm_added["gender"] = "female"
                    
                # Hit 2: Semana 20 (Revelación de Sexo y Nombre)
                elif weeks == 20:
                    gender = random.choice(["male", "female"])
                    if gender == "male":
                        boy_names = ["Mateo", "Lucas", "Santiago", "Thiago", "Matías", "Benjamín", "Joaquín", "Felipe", "Bautista", "Valentín"]
                        baby_name = random.choice(boy_names)
                    else:
                        girl_names = ["Emma", "Sofía", "Martina", "Valentina", "Isabella", "Catalina", "Camila", "Lucía", "Victoria", "Julieta"]
                        baby_name = random.choice(girl_names)
                    
                    rel["baby_gender"] = gender
                    rel["baby_name"] = f"{baby_name} {self.career_player['name'].strip().split()[-1]}"
                    
                    msg = f"¡Amor! Hoy en la ecografía de las 20 semanas por fin se dejó ver el bebé. ¡Vamos a tener un{'a niña' if gender == 'female' else ' niño'}! 👶💖 He pensado que podríamos llamarl{'a' if gender == 'female' else 'o'} {baby_name}. ¿Qué te parece el nombre o prefieres elegir tú?"
                    choices = [
                        {"text": f"¡Me encanta el nombre {baby_name}! Es perfecto para nuestr{'a' if gender == 'female' else 'o'} hij{'a' if gender == 'female' else 'o'}. ❤️", "effects": {"affinity_change": 12}, "next_dm": {
                            "message": f"¡Ay qué emoción! Ya es oficial entonces: se llamará {rel['baby_name']}. ¡Te amo muchísimo, papá! 💕",
                            "choices": []
                        }},
                        {"text": "Es un nombre hermoso, pero ¿qué tal si lo decidimos con calma en casa?", "effects": {"affinity_change": 5}, "next_dm": {
                            "message": "Claro, mi vida. Lo charlamos tranquilos en la cena y buscamos opciones que nos gusten a ambos. 😘",
                            "choices": []
                        }}
                    ]
                    self._add_dm(rel["name"], h, "female_player", msg, choices)
                    dm_added = sm["dms"][0]
                    dm_added["relationship_handle"] = h
                    dm_added["gender"] = "female"
                    
                # Hit 3: Semana 24 (Baja de Maternidad)
                elif weeks == 24:
                    if rel.get("type") in ("player", "female_player"):
                        rel["on_maternity_leave"] = True
                        msg = f"Hola cariño. Ya en la semana 24 el médico del club me ha recomendado dejar los entrenamientos de alta intensidad y tomar la baja por maternidad. 🤰⚽ Me da nostalgia alejarme de las canchas por unos meses, pero es lo mejor para el bebé. ¡A partir de ahora veré todos tus partidos desde la grada!"
                        choices = [
                            {"text": "Haces bien, mi amor. Tu salud y la del bebé son lo primero. Estaré en la tribuna contigo.", "effects": {"affinity_change": 10}},
                            {"text": "Te extrañaremos en el césped, pero es por una hermosa causa. ¡Te amo!", "effects": {"affinity_change": 6}}
                        ]
                        self._add_dm(rel["name"], h, "female_player", msg, choices)
                        dm_added = sm["dms"][0]
                        dm_added["relationship_handle"] = h
                        dm_added["gender"] = "female"
                        
                # Hit 4: Semana 32 (Hospital y Presupuesto)
                elif weeks == 32:
                    msg = f"¡Hola mi vida! Ya en la semana 32 hay que reservar la clínica de maternidad y comprar los últimos muebles del cuarto del bebé. Me pasaron dos presupuestos: la clínica privada premium ($0.03M) o el hospital de la mutualidad ($0.005M). ¿Cuál elegimos? 🏥🍼"
                    choices = [
                        {"text": "Elijamos la clínica premium. Quiero lo mejor y más seguro para ti y el bebé. (-$0.03M)", "effects": {"money": -0.03, "affinity_change": 15}, "next_dm": {
                            "message": "¡Oh, eres tan lindo! De verdad me da mucha tranquilidad saber que contaremos con la mejor atención. Ya hice la reserva. ¡Te amo! ❤️🏥",
                            "choices": []
                        }},
                        {"text": "El hospital de la mutualidad tiene excelentes profesionales y es más que suficiente. (-$0.005M)", "effects": {"money": -0.005, "affinity_change": 3}, "next_dm": {
                            "message": "Entiendo, es una opción muy razonable y práctica. Haré el trámite de admisión esta tarde. ¡Mucho éxito en el entrenamiento! 👍",
                            "choices": []
                        }}
                    ]
                    self._add_dm(rel["name"], h, "female_player", msg, choices)
                    dm_added = sm["dms"][0]
                    dm_added["relationship_handle"] = h
                    dm_added["gender"] = "female"
                    
                # Hit 5: Semana 38 (Nacimiento del bebé)
                elif weeks >= 38:
                    baby_name = rel.get("baby_name")
                    gender = rel.get("baby_gender", "male")
                    if not baby_name:
                        surn = self.career_player["name"].strip().split()[-1]
                        baby_name = f"Mateo {surn}" if gender == "male" else f"Emma {surn}"
                        
                    # Registrar el hijo
                    child = {
                        "name": baby_name,
                        "gender": gender,
                        "birth_date": self.current_date.isoformat(),
                        "mother_handle": h,
                        "mother_name": rel["name"],
                        "age": 0
                    }
                    if "children" not in self.career_stats:
                        self.career_stats["children"] = []
                    self.career_stats["children"].append(child)
                    
                    # Limpiar variables de embarazo
                    rel["is_pregnant"] = False
                    rel["pregnancy_weeks"] = 0
                    if "baby_name" in rel: del rel["baby_name"]
                    if "baby_gender" in rel: del rel["baby_gender"]
                    
                    # Licencia de maternidad post-parto
                    rel["on_maternity_leave"] = True
                    if rel.get("type") in ("player", "female_player"):
                        rel["maternity_weeks_left"] = 12
                    else:
                        rel["maternity_weeks_left"] = 8
                        
                    # Noticia de nacimiento
                    self.add_news("local", "👶 ¡BIENVENIDO AL MUNDO!", f"¡Ha nacido el bebé de @{self.career_player['name'].lower().replace(' ', '')} y {rel['name']}! Se llama {baby_name}. ¡Toda la familia del club les desea lo mejor!")
                    
                    self.add_email("info", "¡Felicidades por tu bebé!", f"Hola {self.career_player['name']}, de parte de toda la plantilla y la directiva te enviamos nuestras más sinceras felicitaciones por el nacimiento de {baby_name}. ¡Disfruta esta hermosa etapa!")
                    
                    msg = f"¡Cariño! Ya nació nuestro precioso bebé, ¡es perfecto/a! 😭❤️ {baby_name} ya está aquí con nosotros y no puedo dejar de mirarl{'o' if gender == 'male' else 'a'}. Gracias por estar a mi lado. ¡Somos una familia completa! 👨‍👩‍👧‍👦✨"
                    choices = [
                        {"text": "¡Es el día más feliz de mi vida! Los amo con toda mi alma. 👨‍👩‍👧‍👦❤️", "effects": {"affinity_change": 25, "prestige": 15}}
                    ]
                    self._add_dm(rel["name"], h, "female_player", msg, choices)
                    dm_added = sm["dms"][0]
                    dm_added["relationship_handle"] = h
                    dm_added["gender"] = "female"
            
            # 2. Si está de baja de maternidad posparto
            elif rel.get("on_maternity_leave") and rel.get("maternity_weeks_left", 0) > 0:
                rel["maternity_weeks_left"] -= 1
                if rel["maternity_weeks_left"] == 0:
                    rel["on_maternity_leave"] = False
                    
                    if rel.get("type") in ("player", "female_player"):
                        msg = f"¡Hola mi amor! Hoy se cumple mi última semana de baja por maternidad y me reincorporo a los entrenamientos completos con mi equipo. 🏃‍♀️⚽ Ha sido un tiempo maravilloso cuidando al bebé, pero ¡ya extrañaba el césped! A ver si vienes a ver mi próximo partido."
                    else:
                        msg = f"¡Hola cariño! Hoy por fin termino mi reposo posparto y me siento al 100% de energía de nuevo. El bebé está durmiendo genial y ya puedo retomar mis actividades normales. ¡Gracias por apoyarme tanto estos meses! ❤️"
                    choices = [
                        {"text": "¡Qué gran noticia mi vida! Sé lo mucho que extrañabas tu rutina. ¡A por todas! 😘", "effects": {"affinity_change": 10}}
                    ]
                    self._add_dm(rel["name"], h, "female_player", msg, choices)
                    dm_added = sm["dms"][0]
                    dm_added["relationship_handle"] = h
                    dm_added["gender"] = "female"

    def _cm_auto_post(self, stats_user, match_result):
        sm = self.career_stats["social_media"]
        strategy = sm["strategy"]
        p_name = self.career_player["name"]
        t_name = self.player_team["name"]
        
        gf = match_result.get("gf", 0)
        ga = match_result.get("ga", 0)
        is_win = gf > ga
        is_draw = gf == ga
        
        content = ""
        if strategy == "professional":
            if is_win:
                content = f"¡Gran victoria hoy del equipo! Orgulloso de todos los muchachos. 👊 #Vamos{t_name.replace(' ', '')}"
            elif is_draw:
                content = f"Un partido duro hoy. Sumamos un punto y ya pensamos en trabajar para el siguiente. #Enfoque"
            else:
                content = f"Resultado difícil. No fue nuestro mejor día, pero nos levantaremos juntos. Gracias a la afición por su apoyo."
            
            if stats_user and stats_user.get("goals", 0) > 0:
                content = f"Feliz por el gol y por ayudar al equipo a sumar hoy. ¡A seguir por este camino! ⚽💪"
        elif strategy == "spicy":
            if is_win:
                content = f"Victoria fácil. El equipo estuvo a otro nivel hoy. ¿Quién es el siguiente? 😉🔥"
            elif is_draw:
                content = f"Punto insípido hoy. Merecimos ganar de sobra, pero algunos errores nos costaron los 3 puntos."
            else:
                content = f"Dura derrota, pero a nivel individual me sentí bien. Volveré más fuerte."
            
            if stats_user and stats_user.get("goals", 0) > 0:
                content = f"¿Dudaban de mí? Otro gol para la colección. Sigan hablando, yo sigo sumando. 😎📈 #Clase"
        
        if content:
            date_str = self.current_date.strftime("%d %b %Y") if self.current_date else "Hoy"
            post = {
                "id": f"post_{self.current_date}_{random.randint(1000,9999)}",
                "date": date_str,
                "author": p_name,
                "handle": sm.get("player_handle") or f"@{p_name.lower().replace(' ', '')}",
                "content": content,
                "likes": int(sm["followers"] * random.uniform(0.05, 0.25)) + 5,
                "retweets": int(sm["followers"] * random.uniform(0.01, 0.05)) + 1,
                "type": "user",
                "user_replied": True
            }
            sm["posts"].insert(0, post)
            bonus = 5 if strategy == "spicy" else 2
            self._update_prestige(bonus / 10.0)

    def _generate_match_feed(self, stats_user, match_result):
        sm = self.career_stats["social_media"]
        p_name = self.career_player["name"]
        t_name = self.player_team["name"]
        gf = match_result.get("gf", 0)
        ga = match_result.get("ga", 0)
        is_win = gf > ga
        is_draw = gf == ga
        
        journalists = [
            {"author": "Diario Sportivo", "handle": "@diariosport"},
            {"author": "Fútbol Al Día", "handle": "@futbolaldia"},
            {"author": "Mario Periodista", "handle": "@mario_cronista"},
            {"author": "Ana G. (Prensa)", "handle": "@anag_prensa"}
        ]
        
        fans = [
            {"author": "Hincha Fiel", "handle": "@hinchafiel_fc"},
            {"author": "Socio 392", "handle": "@socio392"},
            {"author": "Fútbol Fanático", "handle": "@fanatico_futbol"},
            {"author": "Crítico del Balón", "handle": "@criticobalon"}
        ]
        
        date_str = self.current_date.strftime("%d %b %Y") if self.current_date else "Hoy"
        
        # 1. Media tweet
        j = random.choice(journalists)
        if stats_user:
            rating = stats_user.get("rating", 6.0)
            goals = stats_user.get("goals", 0)
            if rating >= 7.5:
                j_content = f"Partidazo de {p_name} ({rating:.1f}) hoy en el encuentro del {t_name}. Clave en el rendimiento del equipo."
                if goals > 0: j_content += f" ¡Y coronado con {goals} gol(es)!"
            elif rating < 5.5:
                j_content = f"Noche para el olvido de {p_name} ({rating:.1f}). Se le vio muy desconectado del juego hoy."
            else:
                j_content = f"Actuación correcta de {p_name} hoy. Cumplió con lo táctico sin llegar a brillar."
        else:
            j_content = f"El {t_name} disputó un partido intenso que finalizó {gf}-{ga}. ¿Qué opinan del planteamiento táctico?"

        sm["posts"].insert(0, {
            "id": f"post_j_{random.randint(10000,99999)}",
            "date": date_str,
            "author": j["author"],
            "handle": j["handle"],
            "content": j_content,
            "likes": random.randint(100, 500),
            "retweets": random.randint(20, 100),
            "type": "media",
            "user_replied": False
        })
        
        # 2. Fan tweet
        f = random.choice(fans)
        if is_win:
            f_content = f"¡Vamooos! Victoria espectacular del {t_name}. "
            if stats_user and stats_user.get("rating", 6.0) >= 7.5:
                f_content += f"¡{p_name} es un jugador de otra galaxia! 🌟"
            else:
                f_content += "Gran esfuerzo colectivo hoy."
        elif is_draw:
            f_content = f"Un empate de local/visitante del {t_name} ({gf}-{ga}). Pudimos haber dado más."
        else:
            f_content = f"Qué desastre del {t_name} hoy. Falta actitud en la cancha. "
            if stats_user and stats_user.get("rating", 6.0) < 5.5:
                f_content += f"¿Por qué sigue jugando {p_name} de titular?"

        sm["posts"].insert(0, {
            "id": f"post_f_{random.randint(10000,99999)}",
            "date": date_str,
            "author": f["author"],
            "handle": f["handle"],
            "content": f_content,
            "likes": random.randint(10, 100),
            "retweets": random.randint(2, 20),
            "type": "fan",
            "user_replied": False
        })

    def _generate_random_feed(self):
        sm = self.career_stats["social_media"]
        p_name = self.career_player["name"] if self.career_player else "Jugador"
        t_name = self.player_team["name"] if self.player_team else "Club"
        date_str = self.current_date.strftime("%d %b %Y") if self.current_date else "Hoy"
        
        opinions = [
            ("Mundial Fútbol", "@mundialfutbol", f"Se rumorea que varios clubes grandes están siguiendo la progresión de los jóvenes de la liga. ¿Estará {p_name} en la lista?"),
            ("Chiringuito Parodia", "@chiringuitop", f"¡EXCLUSIVA! La afición del {t_name} debate si {p_name} merece ser el líder indiscutible del proyecto. ¿Qué opinan?"),
            ("Fútbol Estadísticas", "@optapedia", f"{p_name} registra estadísticas interesantes esta temporada. Su porcentaje de acierto en pases sigue creciendo."),
            ("Memes del Deporte", "@deportememes", f"Cuando {p_name} empieza a encarar a la defensa rival... ¡Sálvese quien pueda! ⚡💨")
        ]
        
        op = random.choice(opinions)
        sm["posts"].insert(0, {
            "id": f"post_r_{random.randint(10000,99999)}",
            "date": date_str,
            "author": op[0],
            "handle": op[1],
            "content": op[2],
            "likes": random.randint(200, 1500),
            "retweets": random.randint(50, 400),
            "type": "media",
            "user_replied": False
        })

    def _generate_match_dms(self, stats_user, match_result):
        if self.mode != "player" or not self.career_player: return
        sm = self.career_stats["social_media"]
        p_name = self.career_player["name"]
        rating = stats_user.get("rating", 6.0) if stats_user else 6.0
        
        if rating >= 7.5:
            msg = f"¡Hola {p_name}! Qué partidazo te mandaste hoy. De verdad eres mi jugador favorito. ¿Habría alguna forma de conseguir tu camiseta firmada? ¡Sería un sueño!"
            choices = [
                {
                    "text": "¡Hola! Por supuesto, dile a mi CM tu dirección y te la envío. 👍",
                    "effects": {"fan_rel": 8, "prestige": 2}
                },
                {
                    "text": "Gracias por el apoyo. Sigue alentando en el estadio.",
                    "effects": {"fan_rel": 4}
                },
                {
                    "text": "Ignorar (No responder)",
                    "effects": {}
                }
            ]
            self._add_dm("Hincha Agradecido", "@hincha_top1", "fan", msg, choices)
            
        elif rating < 5.5:
            msg = f"Hola... Te escribo con respeto, pero hoy no estuviste a la altura en la cancha. La camiseta del {self.player_team['name']} se suda más. ¿Qué pasó?"
            choices = [
                {
                    "text": "Tienes razón, fue un mal día. Trabajaré el doble para compensarlo.",
                    "effects": {"coach_confidence": 6, "fan_rel": 5, "prestige": -2}
                },
                {
                    "text": "Es fácil criticar desde el sillón. Yo doy todo en la cancha.",
                    "effects": {"coach_confidence": -6, "fan_rel": -5, "prestige": 10}
                },
                {
                    "text": "Ignorar (No responder)",
                    "effects": {}
                }
            ]
            self._add_dm("Hincha Decepcionado", "@hincha_critico", "fan", msg, choices)

    def _generate_random_dms(self):
        if self.mode != "player" or not self.career_player: return
        sm = self.career_stats["social_media"]
        p_name = self.career_player["name"]
        p_handle = sm.get("player_handle") or f"@{p_name.lower().replace(' ', '')}"
        
        r_val = random.random()
        
        # 1. Family Legacy DM
        is_legacy_career = self.career_stats.get("is_legacy_career", False)
        legacy = self.career_stats.get("player_legacy") if is_legacy_career else None
        has_legacy_dm = any("padre" in d["message"].lower() or "legado" in d["message"].lower() for d in sm["dms"])
        
        if legacy and not has_legacy_dm:
            msg = f"¡Hola {p_name}! Qué coincidencia tan linda verte jugar. Mi padre jugaba y siempre me hablaba del legado de los {p_name.strip().split()[-1]}. ¿Es verdad que eres el hijo de {legacy['name']}? ¡Felicidades por seguir sus pasos!"
            choices = [
                {"text": "¡Sí! Es mi orgullo e intento honrar su legado cada día.", "effects": {"prestige": 15, "fan_rel": 8, "coach_confidence": 3, "affinity_change": 15}, "tone": "professional", "next_dm": {
                    "message": "¡Qué gran actitud! Se nota que heredaste su clase. A ver si nos vemos pronto en el estadio. ¡Mucha suerte en tu carrera!",
                    "choices": []
                }},
                {"text": "¡Hola! Qué lindo que lo recuerdes, fue un honor para mi padre. Gracias por escribirme. 😊", "effects": {"prestige": 12, "fan_rel": 5, "affinity_change": 10}, "tone": "friendly", "next_dm": {
                    "message": "De nada, de verdad. Me pareció muy tierno recordar esa época. ¿Cómo va tu temporada? ¿Es duro jugar con tanta presión?",
                    "choices": [
                        {"text": "Es duro, pero los profesionales estamos acostumbrados a la presión.", "effects": {"coach_confidence": 4}, "next_dm": {
                            "message": "¡Admiro tu profesionalidad! Ojalá logres todos tus objetivos. ¡Te sigo de cerca!",
                            "choices": []
                        }},
                        {"text": "Un poco, pero con personas como tú apoyándome es más fácil. 😊", "effects": {"affinity_change": 10}, "next_dm": {
                            "message": "Ay, qué dulce. Me alegra poder animarte un poco. ¡Te sigo de cerca!",
                            "choices": []
                        }}
                    ]
                }},
                {"text": f"Sí, soy su hijo, y espero estar a la altura. Por cierto, yo también sigo tus publicaciones, eres preciosa. ¿Me invitas a un café para contarte más? 😉☕", "effects": {"prestige": 22, "coach_confidence": -4, "fan_rel": 4, "affinity_change": 25}, "tone": "romantic", "next_dm": {
                    "message": "Jajaja, ¡qué directo! 😉 Me halaga tu interés... Pero dime, ¿siempre eres así de atrevido en todo o solo con las cámaras de por medio?",
                    "choices": [
                        {"text": "Solo cuando sé muy bien lo que quiero. Y ahora mismo quiero conocerte. 😉", "effects": {"affinity_change": 15, "prestige": 5}, "next_dm": {
                            "message": "Vaya... Me has dejado sin palabras. Está bien, acepto ese café. Escríbeme cuando tengas un día libre.",
                            "choices": []
                        }},
                        {"text": "Jaja, un poco de ambos. Pero de verdad me gustaría charlar tranquilos.", "effects": {"affinity_change": 8}, "next_dm": {
                            "message": "Bueno, está bien. Vamos a ver si el café está a la altura de tu confianza.",
                            "choices": []
                        }}
                    ]
                }},
                {"text": "Sí, soy su hijo, pero escribiré mi propia historia por mí mismo.", "effects": {"prestige": 25, "coach_confidence": -3, "fan_rel": 5, "affinity_change": -5}, "tone": "professional", "next_dm": {
                    "message": "¡Esa es la mentalidad de un campeón! Tienes toda la razón, harás tu propio nombre. ¡Mucho éxito!",
                    "choices": []
                }},
                {"text": "Prefiero no hablar de temas familiares en redes.", "effects": {"coach_confidence": 5, "affinity_change": -10}, "tone": "ignore", "next_dm": {
                    "message": "Entiendo perfectamente, disculpa el atrevimiento. ¡Mucho éxito en la temporada!",
                    "choices": []
                }}
            ]
            self._add_dm("Elena Rossi", "@elena_rossi", "female_celeb", msg, choices)
            dm_added = sm["dms"][0]
            dm_added["relationship_handle"] = "@elena_rossi"
            dm_added["gender"] = "female"
            return

        # Cooldown and anti-spam check: Collect handles that currently have unread DMs or were recent
        unread_handles = {d["handle"] for d in sm["dms"] if d["status"] in ("unread", "read")}
        recent_handles = [d["handle"] for d in sm["dms"][:3]]

        # Pre-calculate context for weighted category selection
        partner_handle = None
        partner_name = None
        partner_status = None
        partner_rel = None
        for h, rel in self.career_stats.get("relationships", {}).items():
            if rel.get("status") in ("Novia", "Esposa"):
                partner_handle = h
                partner_name = rel["name"]
                partner_status = rel["status"]
                partner_rel = rel
                break

        agent_prof = self.career_stats.get("agent_profile")
        roster = self.rosters.get(self.player_team["short"], []) if self.player_team else []
        teammates = [p for p in roster if not p.get("is_user_player")]

        # Determine if partner is long distance
        is_long_distance = False
        if partner_rel and self.player_team:
            partner_team_short = partner_rel.get("team_short")
            partner_league = partner_rel.get("league")
            
            if not partner_league:
                partner_rel["league"] = self.player_team.get("league", "ES")
                partner_league = partner_rel["league"]
            if not partner_team_short:
                partner_rel["team_short"] = self.player_team.get("short")
                partner_team_short = partner_rel["team_short"]
                
            if partner_league != self.player_team.get("league", "ES"):
                is_long_distance = True

        # Weighted category selection for more balanced DM distribution
        categories = []
        if partner_handle and partner_handle not in unread_handles and partner_handle not in recent_handles:
            categories.append(("partner", 25))
        if agent_prof and agent_prof["handle"] not in unread_handles and agent_prof["handle"] not in recent_handles:
            categories.append(("agent", 15))
        if teammates:
            categories.append(("teammate", 15))
        categories.append(("brand", 15))
        categories.append(("female_celeb", 22))
        categories.append(("fan", 8))
        
        if not categories:
            categories = [("brand", 50), ("fan", 50)]
            
        cat_names = [c[0] for c in categories]
        cat_weights = [c[1] for c in categories]
        chosen_cat = random.choices(cat_names, weights=cat_weights, k=1)[0]

        # 2. Partner interactions
        if chosen_cat == "partner":
            if is_long_distance:
                templates = [
                    f"Hola mi amor. Se hace tan difícil la distancia desde que fichaste por el {self.player_team['name']}. Te extraño mucho aquí. ¿Cuándo vienes a visitarme? ❤️✈️",
                    f"¡Hola cariño! Vi tu partido de hoy por televisión. Me da rabia estar tan lejos y no poder abrazarte. Te extraño un montón. 😘",
                    f"Amor, estaba pensando en cuándo nos vemos. La distancia en la liga de {self.player_team.get('league', 'extranjero')} no es fácil, pero te apoyo siempre."
                ]
                msg = random.choice(templates)
                choices = [
                    {"text": "Yo también te extraño mi amor. Vuelo a verte este fin de semana. ✈️❤️ (-$5k)", "effects": {"affinity_change": 12, "money": -0.005}, "next_dm": {
                        "message": "¡Sii! Me hace muy feliz leer eso. Ya estoy contando los días para que llegues. ¡Te amo! 😍",
                        "choices": []
                    }},
                    {"text": "Es difícil estar lejos, pero este esfuerzo valdrá la pena por nuestro futuro. ¡Te amo!", "effects": {"affinity_change": 6}, "next_dm": {
                        "message": "Lo sé, mi vida. Tienes razón, hay que ser fuertes. ¡Mucho éxito en el entrenamiento! 😘",
                        "choices": []
                    }},
                    {"text": "Ahora mismo estoy muy concentrado en adaptarme a mi nuevo club. Hablamos luego.", "effects": {"affinity_change": -10}, "next_dm": {
                        "message": "Entiendo... El fútbol siempre es lo primero. Que te vaya bien en tu equipo.",
                        "choices": []
                    }}
                ]
            elif partner_status == "Novia":
                aff = self.career_stats["relationships"][partner_handle]["affinity"]
                if aff >= 90 and random.random() < 0.4:
                    msg = f"¡Hola mi amor! 💕 Llevamos un tiempo maravilloso de novios y siento que eres el indicado para mí. He visto unos anillos de compromiso preciosos... ¿Qué opinas si damos el gran paso y nos casamos? 💍✨"
                    choices = [
                        {"text": "¡Sí, acepto casarme contigo! Eres el amor de mi vida. 💍✨", "effects": {"prestige": 20, "fan_rel": 10, "affinity_change": 20, "set_relationship_status": "Esposa", "news_trigger": "boda_real"}, "next_dm": {
                            "message": "¡Dios mío, sí! Jaja, ¡me haces la mujer más feliz del mundo! Le contaré a mi familia de inmediato. ¡Te amo! ❤️💍",
                            "choices": []
                        }},
                        {"text": "Aún es pronto, mi amor. Concentrémonos en el fútbol y nuestras carreras.", "effects": {"affinity_change": -15}, "next_dm": {
                            "message": "Entiendo... Quizás tienes razón y nos precipitamos. Seguiremos como estamos.",
                            "choices": []
                        }}
                    ]
                else:
                    templates = [
                        "Hola mi vida, quería desearte un buen día en el entrenamiento. Te extraño mucho, a ver si cenamos juntos hoy. ❤️",
                        "¡Hola guapo! He visto fotos tuyas en redes de la última marca publicitaria... ¡sales guapísimo! Pero no te distraigas de mí, ¿eh? 😉💕",
                        "¡Hola cariño! Acabo de ver el pronóstico de tu próximo partido. ¡Estoy segura de que vas a romperla! Te amo."
                    ]
                    msg = random.choice(templates)
                    choices = [
                        {"text": "¡Muchas gracias mi amor! Eres mi mayor apoyo. Cenemos hoy sin falta. 😘", "effects": {"affinity_change": 8, "coach_confidence": -1}, "next_dm": {
                            "message": "¡Trato hecho! Reservo un lugar agradable para la cena. ¡Nos vemos más tarde! ❤️",
                            "choices": []
                        }},
                        {"text": "¡Hola cariño! Muchas gracias por el apoyo, te amo mucho. Nos vemos en casa.", "effects": {"affinity_change": 5}, "next_dm": {
                            "message": "¡Te amo más! Conduce con cuidado de vuelta.",
                            "choices": []
                        }}
                    ]
            elif partner_status == "Esposa":
                is_pregnant = partner_rel.get("is_pregnant", False)
                pregnancy_weeks = partner_rel.get("pregnancy_weeks", 0)
                on_maternity_leave = partner_rel.get("on_maternity_leave", False)
                aff = partner_rel.get("affinity", 50)
                
                if is_pregnant:
                    # Diálogos sobre el embarazo según la semana
                    if pregnancy_weeks < 15:
                        templates = [
                            "Hola mi amor, últimamente me siento un poco cansada y con náuseas, pero pensar en nuestro futuro bebé me da todas las fuerzas del mundo. ¡Te amo! 🤰❤️",
                            "Cariño, ¿has pensado en si será niño o niña? Yo presiento que va a ser muy activo/a como su padre. ¡Buen entrenamiento hoy!"
                        ]
                        msg = random.choice(templates)
                        choices = [
                            {"text": "Cuídate mucho mi vida, descansa. Volveré temprano para consentirte. 😘", "effects": {"affinity_change": 8}},
                            {"text": "Yo también estoy muy emocionado de empezar esta etapa contigo. ¡Te amo!", "effects": {"affinity_change": 5}}
                        ]
                    elif pregnancy_weeks < 28:
                        templates = [
                            "¡Amor! Hoy sentí la primera patadita del bebé. ¡Fue increíble! Ojalá hubieras estado aquí para sentirlo. ¿Cómo va el club? 👶💕",
                            "Hola esposo hermoso. Llevo días buscando cunas y ropita por internet. ¡Hay tantas opciones! Me hace mucha ilusión todo esto."
                        ]
                        msg = random.choice(templates)
                        choices = [
                            {"text": "¡Qué emoción! La próxima vez pon mi mano en tu barriga. Te amo mucho. ❤️", "effects": {"affinity_change": 10}},
                            {"text": "Qué lindo, amor. Elige lo que más te guste, yo me encargo de los gastos.", "effects": {"affinity_change": 5, "money": -0.002}}
                        ]
                    else:
                        templates = [
                            "Hola cariño. Ya falta muy poco para tener a nuestro bebé en brazos. Me canso muy rápido al caminar, pero estoy tan feliz. ¡Mucha suerte en tu partido! 🤰🍼",
                            "Amor, mi maleta para el hospital ya está casi lista. Solo falta que el bebé decida salir. ¡Espero que no nazca en medio de tu partido! Jaja."
                        ]
                        msg = random.choice(templates)
                        choices = [
                            {"text": "¡Estaré listo para correr al hospital cuando sea! Te amo, hermosa.", "effects": {"affinity_change": 10}},
                            {"text": "Todo saldrá perfecto, mi vida. Estoy muy orgulloso de ti.", "effects": {"affinity_change": 5}}
                        ]
                elif on_maternity_leave:
                    # Diálogos durante la baja por maternidad (bebón ya nació)
                    templates = [
                        "Hola amor, el bebé se durmió por fin. Es agotador pero ver su carita lo vale todo. Te extrañamos mucho aquí, ¡vuelve pronto! 👶❤️",
                        "¡Esposo! Hoy el bebé no ha parado de sonreír. Me alegra haber tomado esta pausa en mi carrera deportiva para cuidarlo. ¿Cómo va el entrenamiento?",
                        "Hola cariño. Estaba pensando en lo afortunados que somos. El bebé está creciendo sano y fuerte. Te amamos muchísimo."
                    ]
                    msg = random.choice(templates)
                    choices = [
                        {"text": "¡Son mi mayor motivación! Volveré volando a casa en cuanto termine. 😘", "effects": {"affinity_change": 10, "prestige": 5}},
                        {"text": "Me alegra que estés disfrutando de esta pausa. Te amo mucho.", "effects": {"affinity_change": 6}}
                    ]
                # Petición de tener un hijo (cuando no está embarazada, tiene afinidad >= 85 y menos de 3 hijos)
                elif aff >= 85 and len(self.career_stats.get("children", [])) < 3 and random.random() < 0.35:
                    msg = f"Hola esposo hermoso... 💕 Llevamos un tiempo casados y soy sumamente feliz a tu lado. He estado pensando mucho en nuestro futuro y en el hogar que hemos construido... ¿Qué opinas si damos el paso y tratamos de tener un bebé? 👶🍼✨"
                    choices = [
                        {"text": "¡Me hace muchísima ilusión, mi amor! Hagamos crecer nuestra familia. ❤️🍼", "effects": {"affinity_change": 20, "set_pregnancy": True}, "next_dm": {
                            "message": "¡Sii! ¡Me haces tan feliz! No puedo esperar para empezar esta nueva aventura contigo. ¡Te amo con todo mi corazón! 😍🤰",
                            "choices": []
                        }},
                        {"text": "Aún me gustaría enfocarme un poco más en mi carrera esta temporada, amor. Esperemos un poco más.", "effects": {"affinity_change": -5}, "next_dm": {
                            "message": "Entiendo... El fútbol requiere mucha concentración ahora. No te preocupes, esperaremos al momento adecuado. ¡Mucho éxito en el entrenamiento! 😘",
                            "choices": []
                        }}
                    ]
                else:
                    templates = [
                        "Hola esposo hermoso, espero que el entrenamiento haya ido genial. He preparado tu cena favorita para cuando vuelvas. Te amo. 💕",
                        "Hola amor. Estaba pensando en lo rápido que pasa el tiempo y lo feliz que estoy de estar casada contigo. ¡Mucha fuerza para el partido de esta semana!",
                        "¡Amor! Un periodista me preguntó hoy en un evento sobre ti y le dije que eres el mejor esposo y jugador del mundo. ¡Orgullosa de ti siempre! 👑"
                    ]
                    msg = random.choice(templates)
                    choices = [
                        {"text": "¡Te amo hermosa! Eres mi mayor pilar, gracias por ser tan especial.", "effects": {"affinity_change": 8, "prestige": 5}, "next_dm": {
                            "message": "Siempre estaré a tu lado, cariño. ¡Que tengas un excelente día!",
                            "choices": []
                        }},
                        {"text": "Muchas gracias cariño, yo también tengo la suerte de tenerte. Cenamos juntos.", "effects": {"affinity_change": 5}, "next_dm": {
                            "message": "¡Claro que sí! Nos vemos en casa. ❤️",
                            "choices": []
                        }}
                    ]
            
            self._add_dm(partner_name, partner_handle, "female_player", msg, choices)
            dm_added = sm["dms"][0]
            dm_added["relationship_handle"] = partner_handle
            dm_added["gender"] = "female"
            return

        # 3. Agent DMs
        elif chosen_cat == "agent":
            agent_handle = agent_prof["handle"]
            agent_name = agent_prof["name"]
            agent_gender = agent_prof["gender"]
            agent_aff = agent_prof.get("affinity", 50)
            
            if agent_gender == "female" and agent_aff >= 70 and not partner_handle and random.random() < 0.4:
                msg = f"Hola {p_name}. He estado revisando tus contratos de patrocinio, pero honestamente... también he estado pensando mucho en nosotros fuera de la oficina. ¿Qué te parece si salimos a cenar esta noche a solas y celebramos tus éxitos? 😉🍷"
                choices = [
                    {"text": "Me encantaría. Creo que entre nosotros hay una chispa especial. Seamos novios. ❤️", "effects": {"affinity_change": 15, "coach_confidence": -3, "set_relationship_status": "Novia", "news_trigger": "novia_confirmado"}, "next_dm": {
                        "message": "¡Oh! Me hace muy feliz oír eso. A partir de ahora seré tu manager oficial... y tu novia. Cenemos hoy para celebrar nuestra nueva etapa. 😘",
                        "choices": []
                    }},
                    {"text": "Me parece genial, pasemos un buen rato juntos a solas. 😉", "effects": {"affinity_change": 10, "coach_confidence": -2}, "next_dm": {
                        "message": "¡Trato hecho! Será una cena interesante. Te paso el lugar y la hora por privado.",
                        "choices": []
                    }},
                    {"text": "Prefiero que mantengamos las cosas estrictamente profesionales, gracias por la oferta.", "effects": {"affinity_change": -10, "coach_confidence": 3}, "next_dm": {
                        "message": "Entiendo perfectamente y lamento el atrevimiento. Seguiremos trabajando duro por tu carrera.",
                        "choices": []
                    }}
                ]
            elif agent_gender == "female" and agent_aff >= 70 and partner_handle:
                msg = f"¡Hola {p_name}! Quería decirte que estoy muy orgullosa de cómo estamos gestionando tu carrera. Eres un gran cliente y una excelente persona. ¡A seguir trabajando duro! 💪😊"
                choices = [
                    {"text": "¡Muchas gracias! Es genial tenerte como representante y amiga. ¡A por más!", "effects": {"affinity_change": 8, "prestige": 3}, "next_dm": {
                        "message": "¡Totalmente de acuerdo! Eres una estrella en potencia y el mercado lo sabe. ¡Sigamos así!",
                        "choices": []
                    }},
                    {"text": "Igualmente, gracias por todo tu esfuerzo profesional.", "effects": {"affinity_change": 3}, "next_dm": {
                        "message": "Es mi trabajo. Cuenta conmigo siempre.",
                        "choices": []
                    }}
                ]
            else:
                templates = [
                    f"¡Hola {p_name}! He recibido una propuesta menor de prensa para una entrevista exclusiva de tu patrocinador. Nos ofrecen un pago menor por unas declaraciones sencillas. ¿La hacemos?",
                    f"Ey, {p_name}. Varios clubes han preguntado de manera informal a mi agencia por tu situación contractual. ¿Quieres que preparemos el terreno para presionar por una renovación?"
                ]
                msg = random.choice(templates)
                if "entrevista" in msg:
                    choices = [
                        {"text": "Hagamos la entrevista. Más visibilidad y dinero. (+0.01M, -2 Confianza DT)", "effects": {"money": 0.01, "prestige": 8, "coach_confidence": -2, "affinity_change": 5}, "next_dm": {
                            "message": "¡Perfecto! Ya agendé la entrevista. Te pasaré las preguntas preparadas de antemano.",
                            "choices": []
                        }},
                        {"text": "Rechaza. Mejor concentrarse en los entrenamientos hoy.", "effects": {"coach_confidence": 4, "affinity_change": -2}, "next_dm": {
                            "message": "Entendido. Les notificaré que tu agenda deportiva está llena por ahora. ¡Buen enfoque!",
                            "choices": []
                        }}
                    ]
                else:
                    choices = [
                        {"text": "Sí, presiona por una renovación. Quiero un aumento de sueldo.", "effects": {"prestige": 10, "affinity_change": 5, "teammate_rel": -2}, "next_dm": {
                            "message": "Excelente. Empezaré a deslizar a la prensa rumores de ofertas para acelerar la propuesta del club. Mantente concentrado en el campo.",
                            "choices": []
                        }},
                        {"text": "No, estoy cómodo con mi contrato y quiero evitar especulaciones.", "effects": {"coach_confidence": 5, "affinity_change": -3}, "next_dm": {
                            "message": "Muy sensato. Apaciguaré los rumores y les diré que estás comprometido al 100% aquí.",
                            "choices": []
                        }}
                    ]
            
            self._add_dm(agent_name, agent_handle, "agent", msg, choices)
            dm_added = sm["dms"][0]
            dm_added["relationship_handle"] = agent_handle
            dm_added["gender"] = agent_gender
            return

        # 4. Teammate DMs
        elif chosen_cat == "teammate":
            eligible_tms = [t for t in teammates if f"@{t['name'].lower().replace(' ', '')}" not in unread_handles]
            if not eligible_tms: eligible_tms = teammates
            if not eligible_tms:
                chosen_cat = "brand"
            else:
                tm = random.choice(eligible_tms)
                tm_name = tm["name"]
                tm_handle = f"@{tm_name.lower().replace(' ', '')}"
                tm_rel = self.career_stats.get("relationships", {}).get(tm_handle, {})
                tm_aff = tm_rel.get("affinity", 50)
                
                if tm_aff >= 50:
                    msg = f"¡Qué onda, hermano! 👊 Varios de la plantilla vamos a salir a cenar y a jugar bolos después del entrenamiento de hoy para unir al grupo. ¿Te vienes con nosotros?"
                    choices = [
                        {"text": "¡Claro que sí! Contad conmigo, es vital hacer piña en el vestuario.", "effects": {"teammate_rel": 8, "affinity_change": 10, "coach_confidence": -2}, "next_dm": {
                            "message": "¡Esa es! Te guardamos plaza. Nos vemos después de la ducha. ¡Trae calzado cómodo!",
                            "choices": []
                        }},
                        {"text": "Gracias hermano, pero hoy me toca descansar y entrenar por mi cuenta.", "effects": {"coach_confidence": 5, "affinity_change": -3, "teammate_rel": -2}, "next_dm": {
                            "message": "No pasa nada crack. Otra vez será. ¡Buen entreno!",
                            "choices": []
                        }}
                    ]
                else:
                    msg = f"Oye, veo que el míster te está dando muchísima bola en los partidos, pero algunos en el vestuario sentimos que hay favoritismos. ¿Te crees intocable en este equipo?"
                    choices = [
                        {"text": "El DT pone al que mejor rinde. Esfuérzate más en los entrenamientos y calla.", "effects": {"affinity_change": -15, "coach_confidence": 4, "teammate_rel": -5, "news_trigger": "enemistad_teammate"}, "next_dm": {
                            "message": "Jaja... Menuda soberbia. A ver si eres tan valiente cuando el equipo entre en mala racha. Nos vemos en la cancha.",
                            "choices": []
                        }},
                        {"text": "Todos sumamos aquí, amigo. Mi intención no es pisar a nadie. Suerte.", "effects": {"affinity_change": 5, "teammate_rel": 4}, "next_dm": {
                            "message": "Está bien, puede que me haya calentado rápido. Espero que tengas razón. Seguimos sumando.",
                            "choices": []
                        }}
                    ]
                
                self._add_dm(f"{tm_name} (Compañero)", tm_handle, "teammate", msg, choices)
                dm_added = sm["dms"][0]
                dm_added["relationship_handle"] = tm_handle
                dm_added["gender"] = "male"
                return

        # 5. Brand Sponsorships
        if chosen_cat == "brand":
            brands = ["AeroMax", "Gatorade Parodia", "Puma Parodia", "FitLife Pro"]
            brand = random.choice(brands)
            brand_handle = f"@{brand.lower().replace(' ', '')}"
            if brand_handle in unread_handles: return
            
            pay = round(random.uniform(0.01, 0.05) * (1 + self.career_stats["prestige"] / 300.0), 3)
            
            msg = f"¡Hola! Nos encanta tu perfil y tu proyección en el {self.player_team['name'] if self.player_team else 'Club'}. Queremos ofrecerte un patrocinio menor de ${pay:.3f}M por publicar un post promocional de nuestra nueva marca en tus redes."
            choices = [
                {"text": f"¡Acepto la campaña! (+${pay:.3f}M, -3 Relación DT por distracción)", "effects": {"money": pay, "prestige": 5, "coach_confidence": -3}, "next_dm": {
                    "message": "¡Perfecto! Hemos verificado el post y transferido el pago. ¡Un placer hacer negocios!",
                    "choices": []
                }},
                {"text": "Rechazar oferta. Prefiero concentrarme en el fútbol.", "effects": {"coach_confidence": 6, "prestige": 2}, "next_dm": {
                    "message": "Entendemos tu postura. Te deseamos mucho éxito deportivo y seguiremos en contacto.",
                    "choices": []
                }}
            ]
            
            if sm.get("cm_tier", 0) == 3:
                self.career_stats["money"] = round(self.career_stats.get("money", 0.0) + pay, 4)
                self.add_email("info", "Contrato publicitario completado (CM Élite)", f"Tu CM Élite ha gestionado y aceptado automáticamente el patrocinio de {brand}, ingresando ${pay:.3f}M a tu cuenta.")
                self._add_dm(brand, brand_handle, "sponsor", msg, choices, auto_replied_idx=0)
            else:
                self._add_dm(brand, brand_handle, "sponsor", msg, choices)
            return

        # 6. Female Celebrity DMs
        elif chosen_cat == "female_celeb":
            from data.procedural import generate_female_player_name
            
            REAL_FEMALE_CELEBS = [
                {"name": "Aitana Bonmatí", "handle": "@aitanabonmati", "team": "FC Stellaris Femení", "nat": "ES", "type": "player"},
                {"name": "Alexia Putellas", "handle": "@alexiaputellas", "team": "FC Stellaris Femení", "nat": "ES", "type": "player"},
                {"name": "Salma Paralluelo", "handle": "@salmaparalluelo", "team": "FC Stellaris Femení", "nat": "ES", "type": "player"},
                {"name": "Jenni Hermoso", "handle": "@jennihermoso", "team": "Tigres Femenil", "nat": "ES", "type": "player"},
                {"name": "Sam Kerr", "handle": "@samkerr20", "team": "Blue Lions Femenino", "nat": "US", "type": "player"},
                {"name": "Carla Vieri", "handle": "@carlavieri_tv", "team": "Periodista Deportiva (Sky)", "nat": "IT", "type": "journalist"},
                {"name": "Diletta Leotta", "handle": "@dilettaleotta", "team": "Presentadora (DAZN)", "nat": "IT", "type": "journalist"},
                {"name": "Morena Beltrán", "handle": "@morenabeltran", "team": "Analista de ESPN", "nat": "AR", "type": "journalist"},
                {"name": "Sofia Martinez", "handle": "@sofimartinez_ok", "team": "Reportera de TV", "nat": "AR", "type": "influencer"},
                {"name": "Alisha Lehmann", "handle": "@alishalehmann7", "team": "Influencer Deportiva", "nat": "CH", "type": "influencer"},
                {"name": "Camila Romero", "handle": "@cami_romero_fit", "team": "Creadora Fitness & Sport", "nat": "ES", "type": "influencer"},
                {"name": "Martina Silva", "handle": "@martina_hincha", "team": "Socia VIP del Club", "nat": "ES", "type": "fan"},
                {"name": "Giulia Bianchi", "handle": "@giulia_bianchi", "team": "Aficionada Histórica", "nat": "IT", "type": "fan"}
            ]
            
            candidates = [c for c in REAL_FEMALE_CELEBS if c["handle"] not in unread_handles and c["handle"] not in recent_handles]
            
            if candidates and random.random() < 0.6:
                fc = random.choice(candidates)
                sender_name = fc["name"]
                sender_handle = fc["handle"]
                sender_team = fc["team"]
                sender_type = fc["type"]
            else:
                sender_type = random.choice(["player", "journalist", "influencer", "fan"])
                nat = self.nationality or "ES"
                sender_name = generate_female_player_name(nat)
                sender_handle = f"@{sender_name.lower().replace(' ', '')}_{sender_type[:3]}"
                
                if sender_handle in unread_handles: return
                
                if sender_type == "player":
                    t = random.choice(self.teams)
                    sender_team = f"{t['name']} Femenil"
                elif sender_type == "journalist":
                    sender_team = random.choice(["Presentadora Fox", "Periodista de Marca", "Analista Deportiva"])
                elif sender_type == "influencer":
                    sender_team = random.choice(["Streamer Deportiva", "Fitness Blogger", "Creadora de Contenido"])
                else:
                    sender_team = random.choice(["Socia del Club", "Aficionada VIP", "Seguidora del Equipo"])
            
            f_rel = self.career_stats.get("relationships", {}).get(sender_handle, {})
            f_aff = f_rel.get("affinity", 20)
            f_status = f_rel.get("status", "Conocida")
            
            if partner_handle and sender_handle == partner_handle: return

            if f_aff >= 70 and not partner_handle and f_status in ("Amiga", "Amiga Íntima", "Conocida"):
                msg = f"¡Hola {p_name}! 💕 Llevamos hablando un tiempo y la verdad es que... me gustas muchísimo. Siento que conectamos genial y no puedo parar de pensar en ti. ¿Te gustaría que formalicemos y seamos novios? 😊❤️"
                choices = [
                    {"text": "¡Me encantaría! Yo también siento lo mismo por ti, hermosa. Seamos novios. ❤️", "effects": {"affinity_change": 15, "prestige": 10, "set_relationship_status": "Novia", "news_trigger": "novia_confirmado"}, "next_dm": {
                        "message": "¡Sii! ¡Me haces inmensamente feliz! Jaja, ya quiero que salgamos de nuevo. ¡Te amo! 😍❤️",
                        "choices": []
                    }},
                    {"text": "Eres una chica increíble, de verdad. Pero ahora mismo necesito concentrarme en el fútbol. Seamos amigos.", "effects": {"affinity_change": -5}, "next_dm": {
                        "message": "Entiendo... El fútbol exige mucho. Está bien, mantengamos nuestra amistad. Mucho éxito.",
                        "choices": []
                    }}
                ]
            elif f_status == "Rival" or f_aff <= -30:
                msg = f"Vi tus últimas declaraciones y me parecieron súper arrogantes. Te crees la gran cosa pero aún tienes mucho que demostrar."
                choices = [
                    {"text": "Tú preocúpate por tu liga, que yo sigo sumando. 😎", "effects": {"affinity_change": -12, "prestige": 10, "coach_confidence": -2}, "next_dm": {
                        "message": "Típico de ti, incapaz de aceptar críticas. Ya nos veremos en el ranking de rendimiento.",
                        "choices": []
                    }},
                    {"text": "No busco agradar a todos. Suerte con tu temporada.", "effects": {"affinity_change": -3, "coach_confidence": 2}, "next_dm": {
                        "message": "Vaya actitud. Igualmente, suerte.",
                        "choices": []
                    }}
                ]
            else:
                if sender_type == "player":
                    templates = [
                        f"¡Hola {p_name}! Te escribo para felicitarte por tu progresión en el {self.player_team['name'] if self.player_team else 'Club'}. ¡Juegas con mucho estilo! Ojalá coincidamos en algún evento.",
                        f"¡Ey {p_name}! Vi tu último partido y me gustó mucho tu forma de jugar. ¡Mucho éxito!"
                    ]
                    msg = random.choice(templates)
                    choices = [
                        {"text": "¡Muchas gracias! Es un verdadero honor viniendo de ti. Suerte en tu liga.", "effects": {"prestige": 10, "affinity_change": 8}, "tone": "friendly", "next_dm": {
                            "message": "¡De nada! Me alegra que te sirva. ¡Seguiré atenta a tus partidos! 😉",
                            "choices": []
                        }},
                        {"text": "Gracias hermosa. Qué lindo saber que me sigues. ¿Cenamos algún día? 😉🌹", "effects": {"prestige": 15, "coach_confidence": -3, "affinity_change": 15}, "tone": "romantic", "next_dm": {
                            "message": "¡Vaya! No te andas con rodeos, ¿eh? 😉 Me encantaría cenar contigo, pero cuéntame: ¿dónde me llevarías en nuestra primera cita?",
                            "choices": [
                                {"text": "A un restaurante de lujo. Te mereces lo mejor.", "effects": {"affinity_change": 10, "money": -0.01}, "next_dm": {
                                    "message": "¡Suena increíble! Me encantan los detalles especiales. Cuenta con esa cena. Escríbeme el fin de semana.",
                                    "choices": []
                                }},
                                {"text": "A un lugar tranquilo a charlar de fútbol y de la vida.", "effects": {"affinity_change": 15}, "next_dm": {
                                    "message": "Me parece el plan perfecto. Menos pose y más conversación. ¡Trato hecho!",
                                    "choices": []
                                }},
                                {"text": "A comer hamburguesas. Algo informal y divertido.", "effects": {"affinity_change": 8}, "next_dm": {
                                    "message": "Jaja, ¡me encanta la idea! Nada de formalismos. ¡Nos vemos pronto!",
                                    "choices": []
                                }}
                            ]
                        }},
                        {"text": "Ignorar mensaje.", "effects": {}, "tone": "ignore", "next_dm": {
                            "message": "Bueno, veo que estás muy ocupado. Éxito de todas formas.",
                            "choices": []
                        }}
                    ]
                elif sender_type == "journalist":
                    msg = f"¡Hola {p_name}! Hago un reportaje sobre las jóvenes promesas de la liga para mi programa y me encantaría saber si estarías disponible para una entrevista exclusiva esta semana. ¿Qué me dices?"
                    choices = [
                        {"text": "¡Claro! Me encantaría conversar y analizar la temporada.", "effects": {"prestige": 12, "affinity_change": 8}, "next_dm": {
                            "message": "¡Excelente! Coordinaré con tu representante. Por cierto, sigo tus partidos y me parece que tienes un talento increíble. ¡Mucha suerte!",
                            "choices": []
                        }},
                        {"text": "Lo siento, ahora mismo prefiero enfocarme solo en los entrenamientos.", "effects": {"coach_confidence": 5, "affinity_change": -2}, "next_dm": {
                            "message": "Entiendo perfectamente, la concentración es clave. Si cambias de opinión, avísame. ¡Éxito!",
                            "choices": []
                        }}
                    ]
                elif sender_type == "influencer":
                    msg = f"¡Hola! Vi tus jugadas en redes y se hicieron súper virales. Hago contenido de retos de fútbol y me encantaría grabar un video contigo desafiándote en tiros de falta. ¿Te sumas?"
                    choices = [
                        {"text": "¡Suena divertidísimo! Organicemos ese reto de tiros libres. 🎯", "effects": {"prestige": 15, "affinity_change": 10}, "next_dm": {
                            "message": "¡Genial! Será un video épico. Te paso los detalles por privado para la producción. ¡La gente se va a volver loca!",
                            "choices": []
                        }},
                        {"text": "Gracias por la propuesta, pero mi agenda deportiva está muy ajustada.", "effects": {"coach_confidence": 3, "affinity_change": -1}, "next_dm": {
                            "message": "No te preocupes, ¡otra vez será! Sigue brillando en la cancha.",
                            "choices": []
                        }}
                    ]
                else: # fan
                    msg = f"¡Hola {p_name}! Vi tu partido desde el palco de abonados y me encantó tu entrega. ¿Sería posible pedirte una foto o firma después del entrenamiento de mañana? ¡Significaría el mundo para mí!"
                    choices = [
                        {"text": "¡Hola! Claro, búscame al salir del complejo y nos tomamos la foto sin problemas. 😊", "effects": {"fan_rel": 8, "affinity_change": 12}, "next_dm": {
                            "message": "¡No me lo puedo creer! Eres súper humilde y un crack de verdad. ¡Allí estaré apoyándote con todo!",
                            "choices": []
                        }},
                        {"text": "Hola, muchas gracias por el apoyo. A ver si nos vemos en los eventos oficiales del club.", "effects": {"fan_rel": 4, "affinity_change": 3}, "next_dm": {
                            "message": "¡Gracias de todas formas! Seguiré alentando con la misma pasión desde la tribuna.",
                            "choices": []
                        }}
                    ]
                    
            self._add_dm(f"{sender_name} ({sender_team})", sender_handle, sender_type, msg, choices)
            dm_added = sm["dms"][0]
            dm_added["relationship_handle"] = sender_handle
            dm_added["gender"] = "female"
            return

        # 7. Fan DMs
        else:
            if "@fanatico_balon" in unread_handles: return
            fan_templates = [
                f"Eres mi jugador favorito, {p_name}! Siempre te pongo en mi equipo de fantasia. Podrias darme un consejo para mejorar como jugador?",
                f"Hola {p_name}! Soy un gran fan tuyo. Me encanta como juegas y tu actitud dentro del campo. Sigue asi crack!",
            ]
            msg = random.choice(fan_templates)
            choices = [
                {
                    "effects": {}
                }
            ]
            self._add_dm("Fanatico del Futbol", "@fanatico_balon", "fan", msg, choices)

    def _add_dm(self, sender, handle, sender_type, message, choices, auto_replied_idx=None):
        sm = self.career_stats["social_media"]
        
        # Evitar duplicar mensajes no leidos del mismo remitente
        if auto_replied_idx is None:
            if any(d.get("handle") == handle and d.get("status") in ("unread", "read") for d in sm.get("dms", [])):
                return
                
        # Evitar repetir exactamente el mismo mensaje en la bandeja de entrada reciente
        if any(d.get("message") == message for d in sm.get("dms", [])[:6]):
            return
            
        date_str = self.current_date.strftime("%d %b %Y") if self.current_date else "Hoy"
        
        dm = {
            "id": f"dm_{self.current_date}_{random.randint(1000,9999)}",
            "date": date_str,
            "sender": sender,
            "handle": handle,
            "sender_type": sender_type,
            "message": message,
            "status": "unread" if auto_replied_idx is None else "replied",
            "choices": choices,
            "reply_selected": auto_replied_idx
        }
        sm["dms"].insert(0, dm)

    def reply_to_dm(self, dm_id, choice_idx):
        self._ensure_social_media_exists()
        sm = self.career_stats["social_media"]
        dm = next((d for d in sm["dms"] if d["id"] == dm_id), None)
        if not dm or dm["status"] == "replied": return False
        
        if choice_idx >= len(dm["choices"]): return False
        
        choice = dm["choices"][choice_idx]
        
        # Apply consequences
        effects = choice.get("effects", {})
        if "money" in effects:
            self.career_stats["money"] = round(self.career_stats.get("money", 0.0) + effects["money"], 4)
        if "prestige" in effects:
            self._update_prestige(effects["prestige"] / 10.0)
        if "coach_confidence" in effects:
            self.career_stats["coach_confidence"] = min(100, max(0, self.career_stats.get("coach_confidence", 50) + effects["coach_confidence"]))
        if "fan_rel" in effects:
            self.career_stats["fan_rel"] = min(100, max(0, self.career_stats.get("fan_rel", 50) + effects["fan_rel"]))
        if "teammate_rel" in effects:
            self.career_stats["teammate_rel"] = min(100, max(0, self.career_stats.get("teammate_rel", 50) + effects["teammate_rel"]))
            
        # Process relationship effects
        rel_handle = dm.get("relationship_handle")
        if rel_handle:
            rel_name = dm.get("sender", "Conocida").split(" (")[0]
            rel_type = dm.get("sender_type", "celeb")
            gender = dm.get("gender", "female")
            
            affinity_change = effects.get("affinity_change", 0)
            self.update_relationship(rel_handle, rel_name, gender, rel_type, affinity_change)
            
            # Explicit status if specified
            set_status = effects.get("set_relationship_status")
            if set_status:
                if rel_handle in self.career_stats["relationships"]:
                    self.career_stats["relationships"][rel_handle]["status"] = set_status
                    # Save team details for long distance checks
                    if set_status in ("Novia", "Esposa") and self.player_team:
                        self.career_stats["relationships"][rel_handle]["league"] = self.player_team.get("league", "ES")
                        self.career_stats["relationships"][rel_handle]["team_short"] = self.player_team.get("short")
            
            if effects.get("set_pregnancy"):
                if rel_handle in self.career_stats["relationships"]:
                    self.career_stats["relationships"][rel_handle]["is_pregnant"] = True
                    self.career_stats["relationships"][rel_handle]["pregnancy_weeks"] = 0
            
            # Check news triggers
            news_trigger = effects.get("news_trigger")
            if news_trigger == "novia_confirmado":
                self.add_news("local", "💥 Romance Confirmado", f"La prensa rosa vincula a la estrella @{self.career_player['name'].lower().replace(' ', '')} con {rel_name} en una intensa relación de noviazgo.")
            elif news_trigger == "boda_real":
                self.add_news("local", "💍 ¡BODA DEL AÑO!", f"¡Se casaron! @{self.career_player['name'].lower().replace(' ', '')} y {rel_name} contraen matrimonio en una gran ceremonia privada.")
            elif news_trigger == "embarazo_anunciado":
                self.add_news("local", "🤰 ESTRELLA EN CAMINO", f"El jugador @{self.career_player['name'].lower().replace(' ', '')} y su esposa {rel_name} han anunciado en redes que esperan su primer hijo. ¡Felicidades a la pareja!")
            elif news_trigger == "enemistad_teammate":
                self.add_news("local", "🔥 CRISIS EN EL VESTUARIO", f"Rumores de vestuario reportan que la relación entre @{self.career_player['name'].lower().replace(' ', '')} y su compañero {rel_name} está rota por completo.")

        # Multi-turn conversational flow check
        next_dm = choice.get("next_dm")
        if next_dm and next_dm.get("message"):
            dm["message"] = next_dm["message"]
            dm["choices"] = next_dm.get("choices", [])
            dm["status"] = "unread"
            dm["reply_selected"] = None
        else:
            # End of conversation
            dm["status"] = "replied"
            dm["reply_selected"] = choice_idx
            
        return True

    def post_custom_message(self, tone):
        self._ensure_social_media_exists()
        sm = self.career_stats["social_media"]
        p_name = self.career_player["name"] if self.career_player else "Jugador"
        
        content = ""
        if tone == "professional":
            content = f"Día de entrenamiento superado. Mentalizados al 100% en los objetivos del grupo. 👊 #Fútbol #Trabajo"
            self._update_prestige(0.3)
            self.career_stats["coach_confidence"] = min(100, self.career_stats.get("coach_confidence", 50) + 2)
        elif tone == "spicy":
            content = f"Trabajando duro porque el talento sin esfuerzo no vale nada... y de talento me sobra. 😎⚽ #ModoBestia"
            self._update_prestige(1.0)
            self.career_stats["coach_confidence"] = max(0, self.career_stats.get("coach_confidence", 50) - 4)
            self.career_stats["fan_rel"] = min(100, self.career_stats.get("fan_rel", 50) + 4)
            
        if content:
            date_str = self.current_date.strftime("%d %b %Y") if self.current_date else "Hoy"
            post = {
                "id": f"post_user_{self.current_date}_{random.randint(1000,9999)}",
                "date": date_str,
                "author": p_name,
                "handle": sm.get("player_handle") or f"@{p_name.lower().replace(' ', '')}",
                "content": content,
                "likes": int(sm["followers"] * random.uniform(0.08, 0.20)) + 5,
                "retweets": int(sm["followers"] * random.uniform(0.01, 0.04)) + 1,
                "type": "user",
                "user_replied": True
            }
            sm["posts"].insert(0, post)
            return True
        return False

    def _find_first_empty_slot(self, mode):
        """Finds the first empty save slot for the given mode.
        Manager slots: 1-10, Player slots: 11-20."""
        slots = self.get_slots_metadata()
        start = 1 if mode == "manager" else 11
        end = 11 if mode == "manager" else 21
        for i in range(start, end):
            if slots.get(i) is None:
                return i
        # All slots full — default to first slot in range (will overwrite)
        return start

    def start_new_career(self, manager_name, team_short):
        self.active = True
        self.manager_name = manager_name
        self.year = 1
        
        # Assign to the correct slot range for manager mode
        self.current_slot = self._find_first_empty_slot("manager")
        
        # 1. Expand universe (clone all teams)
        base_teams = copy.deepcopy(TEAMS)
        gen_teams, gen_rosters = generate_filler_teams(len(base_teams), base_teams)
        
        self.teams = base_teams + gen_teams
        
        # 2. Get rosters
        db_rosters = get_base_rosters()
        self.rosters = {}
        for t in self.teams:
            short = t["short"]
            if short in db_rosters:
                self.rosters[short] = copy.deepcopy(db_rosters[short])
            elif short in gen_rosters:
                self.rosters[short] = copy.deepcopy(gen_rosters[short])
            else:
                from data.procedural import generate_roster
                self.rosters[short] = generate_roster(t.get("league", "EN"), 74)
            
            # Initialize transfer/loan status
            for p in self.rosters[short]:
                p["transfer_listed"] = False
                p["loan_listed"] = False
                p["energy"] = 100.0
                
        # Check for legacy generation skip!
        if getattr(self, "start_year_offset", 0) > 0:
            self._apply_legacy_roster_regeneration()
            
        # Identify
        self.player_team = next((t for t in self.teams if t["short"] == team_short), self.teams[0])
        self.team_history = [] # Reset for new career
        self.milestones = []
        self._log_milestone("START", f"Inició carrera en {self.player_team['name']}")
        self.league_id = self.player_team["league"]
        
        self._init_player_energy() # Ensure everyone has energy attribute
        
        # Start intro news & Emails iniciales
        self.add_news("global", "¡NUEVA ERA!", f"{self.manager_name} toma el mando del {self.player_team['name']}.")
        
        # Expectativas del club
        lg = self.player_team.get("league", "EN")
        self._initialize_objectives() # New: sets up tracking
        
        # Initial Emails
        self.add_email("info", "Bienvenida a la Directiva", 
                       f"Estimado {self.manager_name}, es un placer tenerle en el {self.player_team['name']}. " +
                       "Nuestras expectativas para esta temporada han sido enviadas a tu panel de objetivos. ¡Buena suerte!")
        
        if self.mode == "manager":
            self.add_email("info", "Presupuesto de Fichajes", 
                           f"Contamos con un presupuesto de ${self.player_team.get('budget', 0)}M para reforzar el plantel. " +
                           "Úsalo con sabiduría en el mercado de traspasos.")
        else:
            status = "Titular" if self.career_player["ovr"] > 75 else "Suplente"
            self.add_email("alert", "Estado en el Plantel", 
                           f"Hola {self.manager_name}. Tras ver tu nivel en pretemporada, el cuerpo técnico ha decidido que comiences como {status}. " +
                           "Sigue entrenando duro para mantener o mejorar tu puesto.")
            self.add_news("local", f"Debut de {self.manager_name}", f"La afición del {self.player_team['name']} está ansiosa por ver a su nueva incorporación.")
                
        # Incorporate player creations from save_manager if needed
        # (For simplicity in this complex mode, we'll import base ones. Let's do it).
        from data.save_manager import load_user_data
        ud = load_user_data()
        tc = ud.get("team_configs", {})
        for short, team_cfg in tc.items():
            if short in self.rosters:
                extras = team_cfg.get("extra_players", [])
                for e in extras:
                    self.rosters[short].append(copy.deepcopy(e))
        
        
        # Establish Time boundaries
        eu_leagues = ["EN", "ES", "IT", "DE", "FR", "PT", "TR", "BE", "RU", "RO", "SC", "AT", "AF"]
        jp_league = ["JP"]
        is_eu = self.league_id in eu_leagues
        is_jp = self.league_id in jp_league
        if is_eu:
            base_date = datetime.date(2024, 7, 1)
            end_date = datetime.date(2025, 6, 30)
        elif is_jp:
            base_date = datetime.date(2024, 2, 1)
            end_date = datetime.date(2024, 12, 10)
        else:
            base_date = datetime.date(2024, 1, 1)
            end_date = datetime.date(2024, 12, 31)

        # Apply year skip offset
        offset = getattr(self, "start_year_offset", 0)
        if offset > 0:
            base_date = base_date.replace(year=base_date.year + offset)
            end_date = end_date.replace(year=end_date.year + offset)

        self.current_date = base_date
        self.season_start = base_date
        self.season_end = end_date
        self.calendar.clear()
        self.news = []
        
        # Initial Welcome News
        self.add_news("global", "¡Comienza una Nueva Era!", f"El mundo del fútbol pone sus ojos en {self.manager_name}, quien inicia hoy su carrera en {team_short}.")
        if self.mode == "player":
             self.add_news("local", "Promesa Local debuta", f"{self.manager_name} ha firmado su primer contrato profesional con {team_short}.")
        
        # Setup Standings & Budgets
        self._init_budgets()
        
        self.leagues = ["EN", "ES", "IT", "DE", "FR", "PT", "TR", "BE", "RU", "RO", "SC", "AT", "BR", "AR", "CO", "CL", "PE", "MX", "US", "JP", "AF"]
        for lg in self.leagues:
            self.standings[lg] = {}
            self.scorers[f"LIGA_{lg}"] = {}
            self.assists[f"LIGA_{lg}"] = {}
            lg_teams = [t for t in self.teams if t.get("league", "EN") == lg]
            for t in lg_teams:
                self.standings[lg][t["short"]] = {"pts":0, "ph":0, "w":0, "d":0, "l":0, "gf":0, "ga":0}
        
        # Full reset of career_stats for a fresh career
        self.career_stats = {
            "matches": 0, "wins": 0, "draws": 0, "losses": 0,
            "goals_scored": 0, "goals_conceded": 0,
            "player_goals": 0, "player_assists": 0,
            "matches_played": 0,
            "titles": [], "teams_managed": [self.player_team["short"]],
            "seasons_completed": 0,
            "coach_confidence": 50,
            "teammate_rel": 50,
            "fan_rel": 50,
            "board_rel": 50,
            "transfers_in": 0, "transfers_out": 0,
            "total_spent": 0, "total_earned": 0,
            "rating_history": [], "avg_rating": 0.0,
            "prestige": 100,
            "money": 0.0,
            "individual_awards": [],
            "partnerships": {},
            "rivalries": {},
            "is_captain": False,
            "is_nt_captain": False,
            "children": []
        }
        
        # Guardar metadata de legado generacional si corresponde
        is_legacy = getattr(self, "start_year_offset", 0) > 0
        self.career_stats["is_legacy_career"] = is_legacy
        if is_legacy:
            legacy_info = self.check_legacy_match(manager_name)
            if legacy_info:
                self.career_stats["player_legacy"] = legacy_info
                
        self.retired = False
        self.manager_offers = []
        self.manager_applications = []
        
        # 3. Inicializar Club Libre
        self._init_free_agents_club()
                
        self._ensure_social_media_exists()
        self._generate_schedules()
        self._generate_national_cups() # New
        if self.year > 1:
            self._generate_continental()

    def _init_budgets(self):
        """Assign starting budget based on overall strength and macro region."""
        for t in self.teams:
            short = t["short"]
            avg_ovr = self.get_team_ovr(short)
                
            region = t.get("league", "EN")
            eu_big = ["EN", "ES", "IT", "DE"]
            
            # Base logic
            if region in eu_big and avg_ovr >= 85:
                budget = random.randint(150, 400) # Millions
            elif region in eu_big and avg_ovr >= 78:
                budget = random.randint(60, 150)
            elif region in ["BR", "AR"] and avg_ovr >= 80:
                budget = random.randint(30, 80)
            else:
                budget = random.randint(5, 25)
                
            t["budget"] = budget
            
            # Initial academy seed
            ya = []
            for _ in range(random.randint(2, 4)):
                gen_pot = random.randint(70, 94)
                ya.append({
                    "name": f"J. Promesa {random.randint(100,999)}",
                    "pos": random.choice(["CB", "LB", "RB", "CM", "CDM", "CAM", "LW", "RW", "ST", "GK"]),
                    "age": random.randint(14, 16),
                    "pot": gen_pot,
                    "ovr": gen_pot - random.randint(15, 25),
                    "num": random.randint(50, 99),
                    "s": {"speed": 60, "shot": 60, "passing": 60, "defense": 60, "gk": 10},
                    "energy": 100.0
                })
            t["youth_academy"] = ya


    def _process_league_split(self, lg, current_date):
        import datetime
        st = list(self.standings.get(lg, {}).items())
        st.sort(key=lambda x: (-x[1].get("split_group", 1), x[1]["pts"], x[1]["gf"] - x[1]["ga"]), reverse=True)
        
        # Halve points for Austria and Romania
        if lg in ["AT", "RO", "BE"]:
            for team, data in st:
                data["pts"] = data["pts"] // 2
        
        # Split groups
        if lg == "RO":
            top_group = [s[0] for s in st[:6]]
            bottom_group = [s[0] for s in st[6:]]
            double_top, double_bottom = True, False
        elif lg == "BE":
            top_group = [s[0] for s in st[:6]]
            bottom_group = [s[0] for s in st[6:]]
            double_top, double_bottom = True, False
        elif lg == "CO":
            top_group = [s[0] for s in st[:8]]
            bottom_group = [] # Bottom teams are eliminated!
            double_top, double_bottom = False, False
            # Reset points for the Top 8 (Octogonal Final format)
            for t in top_group:
                self.standings[lg][t]["pts"] = 0
        else: # SC and AT
            top_group = [s[0] for s in st[:6]]
            bottom_group = [s[0] for s in st[6:]]
            double_top, double_bottom = True, True
            
        for t in top_group:
            self.standings[lg][t]["split_group"] = 1
        for t in bottom_group:
            self.standings[lg][t]["split_group"] = 2
            
        top_fixtures = self._generate_round_robin(top_group, double=double_top)
        bottom_fixtures = self._generate_round_robin(bottom_group, double=double_bottom) if bottom_group else []
            
        current_dt = current_date
        while current_dt.weekday() != 5:
            current_dt += datetime.timedelta(days=1)
            
        max_len = max(len(top_fixtures), len(bottom_fixtures))
        for i in range(max_len):
            combined_fixture = []
            if i < len(top_fixtures):
                combined_fixture.extend(top_fixtures[i])
            if i < len(bottom_fixtures):
                combined_fixture.extend(bottom_fixtures[i])
                
            if combined_fixture:
                d_str = current_dt.isoformat()
                if d_str not in self.calendar:
                    self.calendar[d_str] = []
                self.calendar[d_str].append({"type": "LIGA", "lg": lg, "matches": combined_fixture})
            current_dt += datetime.timedelta(days=7)
            
        self.add_news("LIGA", f"¡ARRANCAN LOS PLAY-OFFS DE LA LIGA {lg}!", "La temporada regular ha terminado y la liga se divide. Los puntos de Austria y Rumanía se dividen a la mitad.", importance=3)

    def _generate_round_robin(self, teams_list, double=True):
        lg_teams = list(teams_list)
        if len(lg_teams) % 2 != 0:
            lg_teams.append("BYE")
        n = len(lg_teams)
        matchs = []
        fixtures = []
        for fixture in range(1, n):
            for i in range(n // 2):
                matchs.append((lg_teams[i], lg_teams[n - 1 - i]))
            lg_teams.insert(1, lg_teams.pop())
            fixtures.insert(len(fixtures) // 2, matchs)
            matchs = []
            
        if double:
            sec_leg = []
            for i, fixture in enumerate(fixtures):
                clean_matches = [(m[1], m[0]) for m in fixture if "BYE" not in m]
                sec_leg.append(clean_matches)
            all_fixtures = []
            for i, fixture in enumerate(fixtures):
                clean_matches = [m for m in fixture if "BYE" not in m]
                all_fixtures.append(clean_matches)
            all_fixtures.extend(sec_leg)
            return all_fixtures
        else:
            all_fixtures = []
            for i, fixture in enumerate(fixtures):
                clean_matches = [m for m in fixture if "BYE" not in m]
                all_fixtures.append(clean_matches)
            return all_fixtures

    def _generate_schedules(self):
        """Round-robin tournament attached to actual dates."""
        for lg in self.leagues:
            lg_teams = [t["short"] for t in self.teams if t.get("league", "EN") == lg]
            random.shuffle(lg_teams)
            if len(lg_teams) % 2 != 0:
                lg_teams.append("BYE")
                
            n = len(lg_teams)
            matchs = []
            fixtures = []
            for fixture in range(1, n):
                for i in range(n // 2):
                    matchs.append((lg_teams[i], lg_teams[n - 1 - i]))
                lg_teams.insert(1, lg_teams.pop())
                fixtures.insert(len(fixtures) // 2, matchs)
                matchs = []
                
            all_fixtures = []
            for i, fixture in enumerate(fixtures):
                clean_matches = [m for m in fixture if "BYE" not in m]
                all_fixtures.append(clean_matches)
                
            # Solo si no es Argentina agregamos la segunda vuelta (ida y vuelta)
            if lg != "AR":
                sec_leg = []
                for i, fixture in enumerate(fixtures):
                    clean_matches = [(m[1], m[0]) for m in fixture if "BYE" not in m]
                    sec_leg.append(clean_matches)
                all_fixtures.extend(sec_leg)
            
            # Map fixtures to dates (Saturdays & Sundays)
            current_dt = self.season_start
            while current_dt.weekday() != 5: # Find first saturday
                current_dt += datetime.timedelta(days=1)
                
            current_dt += datetime.timedelta(days=14) # Start mid august / mod january usually
            
            for fixture in all_fixtures:
                d_str = current_dt.isoformat()
                if d_str not in self.calendar:
                    self.calendar[d_str] = []
                self.calendar[d_str].append({"type": "LIGA", "lg": lg, "matches": fixture})
                
                # Small leagues get wider spacing to spread the season evenly
                if len(lg_teams) <= 8:
                    spacing = 21
                elif len(lg_teams) <= 10:
                    spacing = 14
                else:
                    spacing = 7
                current_dt += datetime.timedelta(days=spacing)
            
            # SPLIT LOGIC
            if lg in ["SC", "AT", "RO", "CO", "BE"]:
                split_dt = current_dt - datetime.timedelta(days=4)
                d_str = split_dt.isoformat()
                if d_str not in self.calendar:
                    self.calendar[d_str] = []
                self.calendar[d_str].append({"type": "LEAGUE_SPLIT", "lg": lg, "matches": []})


    def _get_sorted_teams_for_league(self, lg):
        """Returns the list of team short-names in a league sorted by standings or OVR."""
        if self.year <= 2 and not self._final_standings:
            # First season or no standings: sort by team OVR
            lg_teams = [t for t in self.teams if t.get("league", "EN") == lg]
            lg_teams.sort(key=lambda t: self.get_team_ovr(t["short"]), reverse=True)
            return [t["short"] for t in lg_teams]
        else:
            # Subsequent seasons: use saved standings
            st = list(self._final_standings.get(lg, {}).items())
            st.sort(key=lambda x: (-x[1].get("split_group", 1), x[1]["pts"], x[1]["gf"] - x[1]["ga"]), reverse=True)
            return [s[0] for s in st]

    def _get_cup_winner(self, lg):
        """Identifies the winner of the national cup for a league."""
        cup = self.national_cups.get(lg)
        if not cup: return None
        final_matches = cup["bracket"].get("FINAL", [])
        if not final_matches: return None
        m = final_matches[0]
        if m.get("res1") is None: return None
        g1, g2 = m["res1"]
        return m["h"] if g1 > g2 else m["a"]

    def _generate_continental(self):
        """Generate Champions, Europa League, Conference, Libertadores, Sudamericana,
        CAF Champions League, CAF Confederation Cup, and CONCACAF Champions Cup."""
        eu_leagues = ["EN", "ES", "IT", "DE", "FR", "PT", "TR", "BE", "RU", "RO", "SC", "AT"]
        sa_leagues = ["BR", "AR", "CO", "CL", "PE"]
        af_leagues = ["AF"]
        na_leagues = ["MX", "US"]
        
        ucl_qualified = []
        uel_qualified = []
        uecl_qualified = []
        
        lib_qualified = []
        sud_qualified = []
        
        caf_cl_qualified = []
        caf_conf_qualified = []
        
        concacaf_qualified = []
        
        # 1. European Leagues Qualification
        eu_coefs = {
            "EN": (4, 2, 1), "ES": (4, 2, 1), "IT": (4, 2, 1), "DE": (4, 2, 1),
            "FR": (3, 2, 1), "PT": (2, 1, 1), "BE": (1, 1, 2), "TR": (1, 1, 2),
            "SC": (1, 1, 2), "AT": (1, 1, 2), "RU": (1, 1, 2), "RO": (1, 0, 3)
        }
        for lg in eu_leagues:
            teams = self._get_sorted_teams_for_league(lg)
            cup_winner = self._get_cup_winner(lg)
            
            c_ucl, c_uel, c_uecl = eu_coefs.get(lg, (1, 1, 1))
            
            ucl = teams[:c_ucl]
            uel = teams[c_ucl : c_ucl + c_uel]
            uecl = teams[c_ucl + c_uel : c_ucl + c_uel + c_uecl]
            
            ucl_qualified.extend(ucl)
            uel_qualified.extend(uel)
            uecl_qualified.extend(uecl)
            
            total_spots = c_ucl + c_uel + c_uecl
            # Cup Winner goes to Europa League if not already qualified for UCL/UEL
            if cup_winner and cup_winner not in (ucl + uel):
                if cup_winner in uecl:
                    uecl.remove(cup_winner)
                    uecl_qualified.remove(cup_winner)
                uel_qualified.append(cup_winner)
            
        # 2. South American Leagues Qualification
        sa_coefs = {
            "BR": (6, 6), "AR": (6, 6), "CO": (3, 4), "CL": (3, 3), "PE": (2, 2)
        }
        for lg in sa_leagues:
            teams = self._get_sorted_teams_for_league(lg)
            cup_winner = self._get_cup_winner(lg)
            
            c_lib, c_sud = sa_coefs.get(lg, (4, 4))
            
            lib = teams[:c_lib]
            sud = teams[c_lib : c_lib + c_sud]
            
            lib_qualified.extend(lib)
            sud_qualified.extend(sud)
            
            # Cup Winner rule: Only if not already qualified via league (outside top 6)
            if cup_winner and cup_winner not in teams[:6]:
                sud_qualified.append(cup_winner)
        
        # 3. African Leagues Qualification (CAF Champions League & Confederation Cup)
        for lg in af_leagues:
            teams = self._get_sorted_teams_for_league(lg)
            cup_winner = self._get_cup_winner(lg)
            # Top 8 go to CAF Champions League, next 8 to CAF Confederation Cup
            caf_cl_qualified.extend(teams[:8])
            caf_conf_qualified.extend(teams[8:16])
            if cup_winner and cup_winner not in teams[:8]:
                caf_cl_qualified.append(cup_winner)
        
        # 4. CONCACAF Qualification (MX and US leagues)
        na_coefs = {"MX": (8, 4), "US": (4, 4)}
        for lg in na_leagues:
            teams = self._get_sorted_teams_for_league(lg)
            cup_winner = self._get_cup_winner(lg)
            c_ccl, _ = na_coefs.get(lg, (4, 4))
            concacaf_qualified.extend(teams[:c_ccl])
            if cup_winner and cup_winner not in teams[:c_ccl]:
                concacaf_qualified.append(cup_winner)
            
        # 5. Initialize all tournaments
        self._initialize_continental_comp("CHAMPIONS", ucl_qualified, eu_leagues)
        self._initialize_continental_comp("EUROPA_LEAGUE", uel_qualified, eu_leagues)
        self._initialize_continental_comp("CONFERENCE", uecl_qualified, eu_leagues)
        self._initialize_continental_comp("LIBERTADORES", lib_qualified, sa_leagues)
        self._initialize_continental_comp("SUDAMERICANA", sud_qualified, sa_leagues)
        self._initialize_continental_comp("CAF_CHAMPIONS", caf_cl_qualified, af_leagues)
        self._initialize_continental_comp("CAF_CONFEDERATION", caf_conf_qualified, af_leagues)
        self._initialize_continental_comp("CONCACAF_CUP", concacaf_qualified, na_leagues)

    def _initialize_continental_comp(self, comp_name, qualified_list, comp_leagues):
        """Helper to initialize a single continental competition."""
        # UCL uses 36-team Swiss league phase (new format 2024+)
        if comp_name == "CHAMPIONS":
            target = 36
        else:
            target = 32
        qualified = qualified_list[:target]
        while len(qualified) < target:
            pool = [t["short"] for t in self.teams 
                    if t.get("league") in comp_leagues and t["short"] not in qualified]
            if pool:
                pool.sort(key=lambda s: self.get_team_ovr(s), reverse=True)
                qualified.append(pool[0])
            else:
                break
        random.shuffle(qualified)
        
        if comp_name == "CHAMPIONS":
            # Swiss league phase: each team plays 8 matches (no groups)
            league_standings = {s: {"pts":0,"ph":0,"w":0,"d":0,"l":0,"gf":0,"ga":0} for s in qualified}
            # Generate 8 opponents per team (Swiss draw)
            swiss_fixtures = self._generate_swiss_draw(qualified, 8)
            self.continental[comp_name] = {
                "format": "SWISS",
                "league_standings": league_standings,
                "swiss_fixtures": swiss_fixtures,
                "knockout": {"R16": [], "QF": [], "SF": [], "FINAL": []},
                "bracket": {"R16": [], "QF": [], "SF": [], "FINAL": []},
                "phase": "LEAGUE",
                "matchday": 0,
                "groups": {}  # empty for compatibility
            }
        else:
            # Traditional 8 groups of 4
            groups = {}
            for g_idx in range(8):
                g_name = chr(65 + g_idx)
                g_teams = qualified[g_idx*4 : g_idx*4+4]
                groups[g_name] = {
                    "teams": g_teams,
                    "standings": {s: {"pts":0,"ph":0,"w":0,"d":0,"l":0,"gf":0,"ga":0} for s in g_teams},
                    "results": []
                }
            self.continental[comp_name] = {
                "format": "GROUPS",
                "groups": groups,
                "knockout": {"R16": [], "QF": [], "SF": [], "FINAL": []},
                "bracket": {"R16": [], "QF": [], "SF": [], "FINAL": []},
                "phase": "GROUPS",
                "matchday": 0
            }
        
        self.scorers[comp_name] = {}
        self.assists[comp_name] = {}
        
        if comp_name == "CHAMPIONS":
            self._schedule_swiss_league(comp_name)
        else:
            self._schedule_continental_groups(comp_name)

    def _generate_swiss_draw(self, teams, matches_per_team):
        """Generates a Swiss-system draw: each team gets unique opponents."""
        fixtures_by_matchday = []
        assigned = {t: [] for t in teams}
        for md in range(matches_per_team):
            available = list(teams)
            random.shuffle(available)
            md_matches = []
            used = set()
            for t in available:
                if t in used:
                    continue
                opponents = [o for o in available if o != t and o not in used and o not in assigned[t]]
                if opponents:
                    opp = opponents[0]
                    md_matches.append((t, opp))
                    used.add(t)
                    used.add(opp)
                    assigned[t].append(opp)
                    assigned[opp].append(t)
            fixtures_by_matchday.append(md_matches)
        return fixtures_by_matchday

    def _schedule_swiss_league(self, comp_name):
        """Schedule Swiss league phase matches on Wednesdays."""
        comp = self.continental[comp_name]
        current_dt = self.season_start + datetime.timedelta(days=60)
        while current_dt.weekday() != 2:
            current_dt += datetime.timedelta(days=1)
        for md_matches in comp["swiss_fixtures"]:
            d_str = current_dt.isoformat()
            if d_str not in self.calendar:
                self.calendar[d_str] = []
            self.calendar[d_str].append({"type": comp_name, "lg": comp_name, "matches": md_matches})
            current_dt += datetime.timedelta(days=14)

    def _advance_swiss_to_knockout(self, comp_name):
        """After Swiss league phase, top 8 direct to R16, 9-24 play playoff."""
        comp = self.continental[comp_name]
        st = sorted(comp["league_standings"].items(), key=lambda x: (x[1]["pts"], x[1]["gf"]-x[1]["ga"]), reverse=True)
        top8 = [s[0] for s in st[:8]]
        playoff_teams = [s[0] for s in st[8:24]]
        playoff_winners = []
        for i in range(min(8, len(playoff_teams) // 2)):
            high = playoff_teams[i]
            low = playoff_teams[len(playoff_teams) - 1 - i]
            g1 = random.randint(0, 3)
            g2 = random.randint(0, 3)
            winner = high if g1 >= g2 else low
            playoff_winners.append(winner)
        r16 = []
        for i in range(min(8, len(playoff_winners))):
            r16.append({"h": top8[i], "a": playoff_winners[7 - i] if 7 - i < len(playoff_winners) else playoff_winners[i], "res1": None, "res2": None})
        comp["bracket"]["R16"] = r16
        comp["phase"] = "R16"
        self._schedule_continental_round(comp_name, "R16")

    def _schedule_continental_groups(self, comp_name):
        """Schedule group stage matches on Wednesdays."""
        comp = self.continental[comp_name]
        
        # Generate all group matchdays (each team plays 6 matches: home+away vs 3 opponents)
        all_matchdays = []
        for g_name, g_data in comp["groups"].items():
            teams = g_data["teams"]
            if len(teams) < 4:
                continue
            # Round-robin: 6 matchdays
            matchups = [
                [(teams[0], teams[1]), (teams[2], teams[3])],
                [(teams[0], teams[2]), (teams[1], teams[3])],
                [(teams[0], teams[3]), (teams[1], teams[2])],
                [(teams[1], teams[0]), (teams[3], teams[2])],
                [(teams[2], teams[0]), (teams[3], teams[1])],
                [(teams[3], teams[0]), (teams[2], teams[1])],
            ]
            for md_idx, md_matches in enumerate(matchups):
                while len(all_matchdays) <= md_idx:
                    all_matchdays.append([])
                all_matchdays[md_idx].extend(md_matches)
        
        # Spread matchdays on Wednesdays, starting ~2 months after season start
        current_dt = self.season_start + datetime.timedelta(days=60)
        while current_dt.weekday() != 2:  # Wednesday
            current_dt += datetime.timedelta(days=1)
        
        for md_matches in all_matchdays:
            d_str = current_dt.isoformat()
            if d_str not in self.calendar:
                self.calendar[d_str] = []
            self.calendar[d_str].append({
                "type": comp_name,
                "lg": comp_name,
                "matches": md_matches
            })
            current_dt += datetime.timedelta(days=14)  # Every 2 weeks

    def _advance_continental_knockout(self, comp_name):
        """After group stage ends, generate knockout bracket."""
        comp = self.continental.get(comp_name)
        if not comp or comp["phase"] != "GROUPS":
            return
        
        # Get top 2 from each group
        qualifiers = []
        for g_name in sorted(comp["groups"].keys()):
            g = comp["groups"][g_name]
            st = sorted(g["standings"].items(), 
                       key=lambda x: (x[1]["pts"], x[1]["gf"]-x[1]["ga"]), reverse=True)
            qualifiers.extend([s[0] for s in st[:2]])
        
        # Determine starting phase dynamically based on the number of qualifiers
        if len(qualifiers) >= 16:
            r16 = [
                (qualifiers[0], qualifiers[3]),
                (qualifiers[4], qualifiers[7]),
                (qualifiers[8], qualifiers[11]),
                (qualifiers[12], qualifiers[15]),
                (qualifiers[2], qualifiers[1]),
                (qualifiers[6], qualifiers[5]),
                (qualifiers[10], qualifiers[9]),
                (qualifiers[14], qualifiers[13]),
            ]
            comp["bracket"]["R16"] = [{"h": m[0], "a": m[1], "res1": None, "res2": None} for m in r16]
            comp["knockout"]["R16"] = [{"home": m[0], "away": m[1], "result": None} for m in r16]
            comp["phase"] = "R16"
            self._schedule_continental_round(comp_name, "R16")
        elif len(qualifiers) == 8:
            qf = [(qualifiers[i], qualifiers[i+1]) for i in range(0, len(qualifiers)-1, 2)]
            comp["bracket"]["QF"] = [{"h": m[0], "a": m[1], "res1": None, "res2": None} for m in qf]
            comp["knockout"]["QF"] = [{"home": m[0], "away": m[1], "result": None} for m in qf]
            comp["phase"] = "QF"
            self._schedule_continental_round(comp_name, "QF")
        elif len(qualifiers) == 4:
            sf = [(qualifiers[i], qualifiers[i+1]) for i in range(0, len(qualifiers)-1, 2)]
            comp["bracket"]["SF"] = [{"h": m[0], "a": m[1], "res1": None, "res2": None} for m in sf]
            comp["knockout"]["SF"] = [{"home": m[0], "away": m[1], "result": None} for m in sf]
            comp["phase"] = "SF"
            self._schedule_continental_round(comp_name, "SF")
        else:
            final = [(qualifiers[i], qualifiers[i+1]) for i in range(0, len(qualifiers)-1, 2)]
            comp["bracket"]["FINAL"] = [{"h": m[0], "a": m[1], "res1": None, "res2": None} for m in final]
            comp["knockout"]["FINAL"] = [{"home": m[0], "away": m[1], "result": None} for m in final]
            comp["phase"] = "FINAL"
            self._schedule_continental_round(comp_name, "FINAL")

    def get_player_match_today(self):
        if not self.current_date:
            return None, None
        d_str = self.current_date.isoformat()
        if d_str in self.calendar:
            pshort = self.player_team["short"]
            nt_short = self.nationality # e.g. "AR"
            for evt in self.calendar[d_str]:
                is_int = evt.get("type") == "INTERNACIONAL"
                for m in evt["matches"]:
                    if is_int:
                        if nt_short in m and (self.is_called_up or self.managing_nt):
                            return m, evt
                    else:
                        if pshort in m:
                            return m, evt
        return None, None
        
    def get_next_player_match_date(self):
        if not self.current_date:
            return None
        temp = self.current_date + datetime.timedelta(days=1)
        pshort = self.player_team["short"]
        nt_short = self.nationality
        while temp <= self.season_end:
            d_str = temp.isoformat()
            if d_str in self.calendar:
                for evt in self.calendar[d_str]:
                    is_int = evt.get("type") == "INTERNACIONAL"
                    for m in evt["matches"]:
                        if is_int:
                            if nt_short in m and (self.is_called_up or self.managing_nt):
                                return temp
                        else:
                            if pshort in m:
                                return temp
            temp += datetime.timedelta(days=1)
        return None
        
    def get_team_by_short(self, short):
        for t in self.teams:
            if t["short"] == short:
                return t
        return None

    def get_team_ovr(self, short):
        """Calculates the official general average based on top 11 players or base stats."""
        r = self.rosters.get(short, [])
        if r:
            # Sort by OVR descending to get the best 11
            sorted_r = sorted(r, key=lambda x: x.get("ovr", 70), reverse=True)
            return sum(p.get("ovr", 70) for p in sorted_r[:11]) / max(1, min(11, len(r)))
        
        t = self.get_team_by_short(short)
        if t and "stats" in t:
            return sum(t["stats"].values()) / max(1, len(t["stats"]))
        
        return 70 # Absolute fallback if data is missing

    def _is_transfer_window(self, d=None):
        """Check if a date falls within a transfer window."""
        if d is None: d = self.current_date
        if not d: return False
        m, day = d.month, d.day
        eu_leagues = ["EN", "ES", "IT", "DE", "FR", "PT", "TR", "BE", "RU", "RO", "SC", "AT", "AF"]
        if self.league_id in eu_leagues:
            # EU Summer: Jul 1 - Aug 31 | EU Winter: Jan 1 - Feb 2
            return (m == 7) or (m == 8) or (m == 1) or (m == 2 and day <= 2)
        else:
            # SA Window 1: Jan 1 - Mar 31 | SA Window 2: Jul 1 - Aug 31
            return (m in [1, 2, 3]) or (m == 7) or (m == 8)

    def _get_transfer_window_name(self):
        if not self.current_date: return ""
        m = self.current_date.month
        eu = self.league_id in ["EN", "ES", "IT", "DE", "FR", "PT", "TR", "BE", "AF"]
        if eu:
            if m in [7, 8]: return "VERANO"
            if m in [1, 2]: return "INVIERNO"
        else:
            if m in [1, 2, 3]: return "APERTURA"
            if m in [7, 8]: return "MITAD DE AÑO"
        return ""

    def advance_time(self, match_result=None):
        """Advances 1 day. Returns dict with status info."""
        if self.current_date >= self.season_end:
            top_players = self._end_season()
            return {"status": "END_OF_SEASON", "top_players": top_players}
            
        d_str = self.current_date.isoformat()
        
        # Update transfer window state
        self.transfer_window_open = self._is_transfer_window()
        
        # Simulate local events exactly TODAY
        if d_str in self.calendar:
            events_today = self.calendar[d_str]
            pshort = self.player_team["short"]
            
            for evt in events_today:
                ev_type = evt["type"]
                lg = evt.get("lg", "GLOBAL")
                stat_key = f"LIGA_{lg}" if ev_type == "LIGA" else ev_type
                
                if ev_type == "LEAGUE_SPLIT":
                    self._process_league_split(lg, self.current_date)
                    continue
                
                for m in evt["matches"]:
                    t1, t2 = m
                    if pshort in (t1, t2) and match_result is not None:
                        g1, g2 = match_result["gf"], match_result["ga"]
                        if pshort == t2: g1, g2 = g2, g1
                        if ev_type == "LIGA":
                            self._apply_match_stats(lg, t1, t2, g1, g2)
                        elif ev_type in ("CHAMPIONS", "EUROPA_LEAGUE", "CONFERENCE", "LIBERTADORES", "SUDAMERICANA", "CAF_CHAMPIONS", "CAF_CONFEDERATION", "CONCACAF_CUP"):
                            self._apply_continental_match(ev_type, t1, t2, g1, g2)
                        elif "COPA_" in ev_type:
                            self._apply_cup_match(lg, t1, t2, g1, g2)
                        elif "INTL_" in ev_type:
                            self._apply_intl_match(lg, t1, t2, g1, g2)
                            
                        # Detect if player actually played on the field
                        actually_played = False
                        if "player_stats" in match_result and self.mode == "player":
                            p_name = self.career_player["name"]
                            actually_played = any(ps.get("name", "").lower().strip() == p_name.lower().strip() for ps in match_result["player_stats"])
                        
                        # Update rating history if it's the career player
                        if "player_stats" in match_result:
                            self.weekly_performers.extend(match_result["player_stats"])
                            self._check_narrative_hooks(match_result, t1, t2, ev_type)
                            self.monthly_performers.extend(match_result["player_stats"])
                            if "COPA_" in ev_type or "INTL_" in ev_type:
                                if ev_type not in self.cup_performers: self.cup_performers[ev_type] = []
                                self.cup_performers[ev_type].extend(match_result["player_stats"])
                            
                            if self.mode == "player":
                                for ps in match_result["player_stats"]:
                                    if ps.get("name", "").lower().strip() == p_name.lower().strip():
                                         rating = ps.get("rating", 6.0)
                                         self.career_stats["rating_history"].append(rating)
                                         # Recalculate avg
                                         hist = self.career_stats["rating_history"]
                                         self.career_stats["avg_rating"] = round(sum(hist) / len(hist), 2)
                                         break
                                
                            for p_stat in match_result.get("player_stats", []):
                                t_short = p_stat.get("team", "")
                                if t_short.endswith("_NT"):
                                    self._update_nt_player_stats(t_short, p_stat["name"], matches=1, 
                                                                   goals=p_stat.get("goals", 0), 
                                                                   assists=p_stat.get("assists", 0))
                                    # Aplicar también al club para lesiones/sanciones
                                    club_short = self._find_player_club(p_stat["name"])
                                    if club_short:
                                        self._update_club_player_stats(club_short, p_stat["name"], matches=1, 
                                                                       goals=p_stat.get("goals", 0), 
                                                                       assists=p_stat.get("assists", 0),
                                                                       yellow_cards=p_stat.get("yellow_cards", 0),
                                                                       red_card=p_stat.get("red_card", 0),
                                                                       is_injured=p_stat.get("is_injured", False),
                                                                       injury_severity=p_stat.get("injury_severity", 0))
                                else:
                                    self._update_club_player_stats(t_short, p_stat["name"], matches=1, 
                                                                   goals=p_stat.get("goals", 0), 
                                                                   assists=p_stat.get("assists", 0),
                                                                   yellow_cards=p_stat.get("yellow_cards", 0),
                                                                   red_card=p_stat.get("red_card", 0),
                                                                   is_injured=p_stat.get("is_injured", False),
                                                                   injury_severity=p_stat.get("injury_severity", 0))
                                    
                        # Reducir sanciones para ambos equipos tras el partido
                        for short in [t1, t2]:
                            for p in self.rosters.get(short, []):
                                if p.get("suspension", 0) > 0:
                                    p["suspension"] -= 1
 
                        for sc in match_result.get("scorers", []):
                            self._add_goal(stat_key, sc)
                            if self.mode == "player" and sc and sc.lower().strip() == self.career_player["name"].lower().strip():
                                self.career_stats["player_goals"] += 1
                        for a in match_result.get("assists", []):
                            self._add_assist(stat_key, a)
                            if self.mode == "player" and a and a.lower().strip() == self.career_player["name"].lower().strip():
                                self.career_stats["player_assists"] += 1
                                
                        # Update career stats for team match
                        self.career_stats["matches"] += 1
                        pf = match_result["gf"]
                        pa = match_result["ga"]
                        self.career_stats["goals_scored"] += pf
                        self.career_stats["goals_conceded"] += pa
                        if pf > pa: self.career_stats["wins"] += 1
                        elif pf < pa: self.career_stats["losses"] += 1
                        else: self.career_stats["draws"] += 1
                        
                        # Track matches actually played on the field by the player
                        if self.mode == "player" and actually_played:
                            self.career_stats["matches_played"] = self.career_stats.get("matches_played", 0) + 1
                            self.current_team_stats["matches"] = self.current_team_stats.get("matches", 0) + 1
                        
                        # Update Coach Confidence based on match
                        self._update_coach_confidence(match_result)
                        
                        # Track historic partnerships and rivalries
                        if self.mode == "player":
                            self._track_relationships(match_result, t1, t2)
                    else:
                        g1, g2 = self._simulate_score(stat_key, t1, t2, ev_type)
                        if ev_type == "LIGA":
                            self._apply_match_stats(lg, t1, t2, g1, g2)
                            # Noticia dinámica: Solo si involucra al jugador directamente
                            is_player_match = (t1 == self.player_team["short"] or t2 == self.player_team["short"])
                            
                            if is_player_match:
                                self.add_news("LIGA", f"LIGA {lg}: {t1} {g1}-{g2} {t2}", f"Resultado de tu equipo en la competición.", expiry_days=3)
                        elif ev_type in ("CHAMPIONS", "EUROPA_LEAGUE", "CONFERENCE", "LIBERTADORES", "SUDAMERICANA", "CAF_CHAMPIONS", "CAF_CONFEDERATION", "CONCACAF_CUP"):
                            self._apply_continental_match(ev_type, t1, t2, g1, g2)
                        elif "COPA_" in ev_type:
                            self._apply_cup_match(lg, t1, t2, g1, g2)
                        elif "INTL_" in ev_type:
                            self._apply_intl_match(lg, t1, t2, g1, g2)
                            
                # Progressive check
                if ev_type == "LIGA": self._check_league_progression(lg)
                elif ev_type in ("CHAMPIONS", "EUROPA_LEAGUE", "CONFERENCE", "LIBERTADORES", "SUDAMERICANA", "CAF_CHAMPIONS", "CAF_CONFEDERATION", "CONCACAF_CUP"): self._check_continental_progression(ev_type)
                elif "COPA_" in ev_type: self._check_cup_progression(lg)
                elif "INTL_" in ev_type: self._check_intl_progression(lg)
                            
            del self.calendar[d_str]
        
        # Update progress for seasonal objectives and leadership
        self._update_objectives_progress()
        self._check_captaincy()
        
        # Periodic Tasks (every Monday)
        if self.current_date.weekday() == 0:
            if self.transfer_window_open:
                self._process_cpu_transfers()
            self._process_negotiations()
            self._process_manager_applications()
            self._generate_manager_offers()
            self._process_weekly_pregnancy()
            if self.mode == "player":
                self._generate_agent_recommendations()
                if self.career_player:
                    ann_salary = self.career_player.get("salary")
                    if ann_salary is None:
                        ann_salary = self._calculate_salary(self.career_player)
                        self.career_player["salary"] = ann_salary
                    weekly_pay = round(ann_salary / 52.0, 4)
                    self.career_stats["money"] = round(self.career_stats.get("money", 0.0) + weekly_pay, 4)
                    if random.random() < 0.15:
                        self.add_email("info", "Nómina de Salario Semanal", 
                                       f"Hola {self.career_player['name']}, se ha depositado tu salario semanal de ${weekly_pay:.3f}M correspondientes a tu contrato con el {self.player_team['name']}.")
            
            # Check for manager legacy news (youth referencing old career)
            self._check_manager_legacy_narrative()
            
            # Check if group stage just finished for continental
            for comp_name in ["CHAMPIONS", "EUROPA_LEAGUE", "CONFERENCE", "LIBERTADORES", "SUDAMERICANA", "CAF_CHAMPIONS", "CAF_CONFEDERATION", "CONCACAF_CUP"]:
                comp = self.continental.get(comp_name)
                if comp and comp["phase"] == "GROUPS":
                    all_done = True
                    for g in comp["groups"].values():
                        for s in g["standings"].values():
                            if s["ph"] < 6:
                                all_done = False
                                break
                    if all_done:
                        self._advance_continental_knockout(comp_name)
            
            # Check for National Cup progression
            for lg_id, cup in self.national_cups.items():
                self._check_cup_progression(lg_id)
            
            # Generate Weekly News (Team of the Week)
            self._generate_weekly_news()
            self._generate_cultural_impact_news()
            
            # Generate Monthly News (Player of the Month)
            if self.current_date.day <= 7: # First Monday of the month
                self._generate_monthly_news()
        
        # Eliminated _handle_awards_ceremony to avoid duplicate awards. 
        # All global awards are now processed together correctly in _end_season() vía _generate_yearly_awards()
                
        self.current_date += datetime.timedelta(days=1)
        self._update_social_media(match_result)

        # Limpiar noticias caducadas
        current_iso = self.current_date.isoformat()
        self.news = [n for n in self.news if not n.get("expiry_date") or n["expiry_date"] > current_iso]
        
        # Procesar recuperación diaria de lesiones
        for rost in self.rosters.values():
            for p in rost:
                if p.get("injured_until") and datetime.date.fromisoformat(p["injured_until"]) <= self.current_date:
                    p["injured_until"] = None
                
        # Expiración de recomendaciones del agente
        if self.mode == "player":
            to_remove = []
            for rec in self.agent_recommendations:
                rec["expires_in"] -= 1
                if rec["expires_in"] <= 0:
                    to_remove.append(rec)
            for r in to_remove:
                self.agent_recommendations.remove(r)
        
        self._recover_stamina(match_result)
        
        self._check_international_eligibility()
        self._process_pending_requests()
        self._update_objectives_progress() # New: sync goals
        
        # Check for non-match milestones (e.g. time milestones)
        self._check_calendar_milestones()
        
        # Ejecutar Autosave si hubo partido
        if match_result and getattr(self, 'autosave_enabled', True):
            if hasattr(self, 'current_slot') and self.current_slot:
                self.save_career(self.current_slot)
        
        return {"status": "OK"}

    def _check_narrative_hooks(self, res, t1, t2, comp_type):
        """Generates dynamic news based on match events and player/manager history."""
        # Detect current entity name
        entity_name = self.career_player["name"] if self.mode == "player" else self.manager_name
        p_team = self.player_team["short"]
        rival = t2 if p_team == t1 else t1
        
        # 1. UPDATE NARRATIVE STATS (no match counting here, already done in advance_time)
        old_played = self.career_stats.get("matches_played", 0)
        old_team_matches = self.current_team_stats.get("matches", 0)
        
        # Noticias de Debut Profesional
        if self.mode == "player" and old_played <= 1:
            if old_played == 1:  # Just incremented to 1 by advance_time
                self.add_news("GLOBAL", "¡DEBUT PROFESIONAL!", f"El joven talento {entity_name} ha debutado hoy profesionalmente con el {self.player_team['name']}. Una carrera que promete mucho.", importance=3, expiry_days=15)
        # Debut con nuevo club
        if self.mode == "player" and old_team_matches == 1 and old_played > 1:
            self.add_news("LOCAL", "PRESENTACIÓN", f"Primeros minutos de {entity_name} con la camiseta del {self.player_team['name']}. La afición lo ha recibido con una ovación.", importance=2, expiry_days=7)
        
        scorers = res.get("scorers", [])
        p_goals_today = scorers.count(entity_name) if self.mode == "player" else 0
        if self.mode == "player":
            self.current_team_stats["goals"] += p_goals_today
        
        # 2. FIND HISTORY
        hist = next((h for h in self.team_history if h["short"] == rival), None)
        
        if hist:
            hist_matches = hist.get("matches", 0)
            hist_titles = hist.get("titles", 0)
            
            if self.mode == "player":
                # --- Player Logic (Scoring vs Ex-club, Star Return, etc.) ---
                current_ovr = self.career_player["ovr"]
                p_pos = self.career_player.get("pos", "FW")
                hist_goals = hist.get("goals", 0)
                
                is_legend = (hist_titles > 0) or \
                            (p_pos in ("ST", "FW") and hist_goals >= 60) or \
                            (p_pos in ("CM", "CAM", "LM", "RM") and hist_goals >= 25) or \
                            (p_pos in ("CB", "LB", "RB", "GK") and hist_matches >= 100) or \
                            (hist_matches >= 150)
                
                if p_goals_today > 0:
                    self.add_news("ESPECIAL", f"LA LEY DEL EX: {entity_name.upper()}", 
                                 f"No hubo piedad. {entity_name} anotó ante su antiguo club, el {rival}, demostrando que el pasado quedó atrás.")
                
                if is_legend:
                    self.add_news("ESTADIO", f"EL REGRESO DEL ÍDOLO", 
                                 f"Clima de nostalgia: {entity_name} vuelve al {rival}. Sus {hist_matches} partidos " +
                                 "y legado en este club lo convierten en un eterno favorito de la grada.")
                elif current_ovr >= 82 and (current_ovr - hist.get("ovr", 70) >= 8) and hist_matches < 25:
                    self.add_news("REPORTAJE", f"EL REENCUENTRO DEL CRACK", 
                                 f"El {rival} dejó ir a {entity_name} cuando era un desconocido. Hoy regresa como una estrella mundial.")
            
            else:
                # --- Manager Logic (Reunions, Revenge, Legacy) ---
                if hist_titles > 0:
                    self.add_news("PREVIA", f"EL MAESTRO VUELVE A CASA", 
                                 f"El estadio del {rival} recibe a {entity_name}, el técnico que los llevó a la gloria con {hist_titles} títulos. " +
                                 "Día de homenajes y tensión táctica.")
                elif hist_matches > 100:
                    self.add_news("DEPORTES", f"REENCUENTRO TÁCTICO", 
                                 f"{entity_name} se enfrenta a su pasado. Dirigió al {rival} durante {hist_matches} jornadas. " +
                                 "Conoce cada rincón de ese vestuario.")
                else:
                    self.add_news("PREVIA", f"DUELO DE BANQUILLOS", f"{entity_name} busca vencer a su antiguo equipo, el {rival}.")

                        # 3. MILESTONES (Common)
        m_count = self.career_stats["matches"]
        if m_count in [1, 50, 100, 250, 500]:
            title = "DEBUT PROFESIONAL" if m_count == 1 else f"HITO: {m_count} PARTIDOS"
            role = "jugador" if self.mode == "player" else "entrenador"
            desc = f"{entity_name} alcanza los {m_count} encuentros como {role}. Un camino de perseverancia."
            self.add_news("HISTORIA", title, desc, importance=2)

    def _log_milestone(self, mtype, desc):
        """Logs a player milestone and adds news."""
        self.career_stats.setdefault("milestones", []).append({"date": self.current_date.isoformat(), "type": mtype, "desc": desc})
        self.add_news("HISTORY", "HITO ALCANZADO", desc, importance=2)

    def _check_club_historical_milestone(self, team_short, comp_name, current_phase):
        """Checks if a club reaching a certain phase is a historical first or best."""
        self.career_stats.setdefault("club_records", {})
        recs = self.career_stats["club_records"].setdefault(team_short, {})
        
        # Rank phases for comparison
        phase_rank = {"GROUPS": 1, "R16": 2, "QF": 3, "SF": 4, "FINAL": 5, "FINISHED": 6}
        current_val = phase_rank.get(current_phase, 0)
        best_val = phase_rank.get(recs.get(comp_name), 0)
        
        if current_val > best_val:
            recs[comp_name] = current_phase
            team = self.get_team_by_short(team_short)
            team_name = team["name"]
            
            # Significant milestone for a "small" team (OVR < 78)
            ovr = self.get_team_ovr(team_short)
            if ovr < 78 and current_val >= 3: # QF or better
                self.add_news("GLOBAL", "HISTORIA VIVA", 
                              f"¡Increíble! El {team_name} alcanza las {current_phase} de {comp_name} por primera vez en su historia moderna. ¡Matagigantes!",
                              importance=2)
            elif current_val >= 5: # Final or Winner
                self.add_news("GLOBAL", "HITO HISTÓRICO", 
                              f"El {team_name} escribe una página de oro al llegar a la gran final de {comp_name}. Un logro sin precedentes para la institución.",
                              importance=3)

    def _check_manager_legacy_narrative(self):
        """Generates news about young players referencing the manager's past player career."""
        if self.mode != "manager": return
        legacy = self.career_stats.get("player_legacy")
        if not legacy: return

        # Probabilidad aumentada para que sea más visible (15% cada lunes)
        if random.random() > 0.15: return

        p_name = legacy["name"]
        p_pos = legacy["pos"]
        
        pool = [
            {
                "title": "Inspiración en la Cantera",
                "desc": f"El efecto {p_name} es real. En la academia, los juveniles intentan imitar los regates que el ahora técnico hacía en su etapa dorada."
            },
            {
                "title": "El Legado del 'Míster'",
                "desc": f"Un canterano de 16 años ha declarado: 'Tener a una leyenda como {p_name} dándonos órdenes es lo que me motiva a ser profesional'."
            },
            {
                "title": "ADN Ganador",
                "desc": f"La prensa local destaca que los juveniles del {self.player_team['name']} están adoptando la mentalidad competitiva que {p_name} mostró como {p_pos}."
            },
            {
                "title": "Camisetas con Historia",
                "desc": f"Se ha visto a varios niños de la cantera con la antigua camiseta de {p_name}. Su impacto como jugador aún perdura en el club."
            }
        ]
        
        # Menciones específicas basadas en estadísticas de legado
        if legacy.get("goals", 0) > 50:
            pool.append({
                "title": "Cátedra de Definición",
                "desc": f"Los delanteros juveniles han tenido una sesión de video analizando los {legacy['goals']} goles de {p_name}. 'Es el espejo donde mirarse', afirma el coordinador."
            })
        
        if legacy.get("titles"):
            pool.append({
                "title": "Hambre de Gloria",
                "desc": f"La vitrina de trofeos de {p_name} es la mayor motivación para los chicos. 'Queremos ganar lo que el jefe ganó', comentan en el vestuario juvenil."
            })
            
        # Mention Individual Awards in legacy news
        p_awards = legacy.get("individual_awards", [])
        if p_awards:
            award = random.choice(p_awards)
            pool.append({
                "title": "Un Maestro Premiado",
                "desc": f"En el entrenamiento se comenta: 'Ayer el míster trajo su {award} para enseñárnoslo. No pudimos evitar quedarnos boquiabiertos'."
            })
            pool.append({
                "title": "Tras los Pasos del Oro",
                "desc": f"La prensa deportiva ha publicado un reportaje comparando a la nueva joya de la cantera con el {p_name} que ganó el {award}."
            })

        news = random.choice(pool)
        self.add_news("CANTERA", news["title"], news["desc"], importance=1)

    def _check_calendar_milestones(self):
        """Checks for date-based milestones (birthday, anniversary, etc.)"""
        pass

    def _log_milestone(self, mtype, desc):
        """Records a career milestone for posterity."""
        date_str = self.current_date.isoformat() if self.current_date else "N/A"
        self.milestones.append({
            "date": date_str,
            "type": mtype,
            "desc": desc,
            "team": self.player_team["short"] if self.player_team else "None"
        })

    def _recover_stamina(self, match_result=None):
        """Recover stamina with a realistic formula based on participation, age and facilities."""
        played_names = []
        if match_result and "player_stats" in match_result:
            played_names = [p["name"] for p in match_result["player_stats"]]
            
        prestige = self.career_stats.get("prestige", 100)
        facility_bonus = prestige / 250.0 # Max +4% recovery
        
        for short, rost in self.rosters.items():
            is_player_team = (self.player_team and short == self.player_team["short"])
            
            for p in rost:
                curr = p.get("energy", 100.0)
                if curr >= 100.0: continue
                
                # Base Recovery
                recovery = 18.0 
                
                # Participation Penalty/Bonus
                if is_player_team and p["name"] in played_names:
                    recovery = 12.0 # Significantly improved (6.0 -> 12.0)
                else:
                    recovery += 5.0 # Improved bonus for rest day (4.0 -> 5.0)
                
                # Age Factor
                age = p.get("age", 25)
                if age > 30:
                    recovery -= (age - 30) * 0.75 # Seniors recover slower
                elif age < 22:
                    recovery += 2.5 # Youngsters recover faster
                
                # Facilities (Prestige)
                recovery += facility_bonus
                
                # Cap recovery to be between 4% and 30%
                recovery = max(4.0, min(30.0, recovery))
                
                p["energy"] = min(100.0, curr + recovery)

    def _init_player_energy(self):
        """Ensure every player in every team has the energy attribute."""
        for rost in self.rosters.values():
            for p in rost:
                if "energy" not in p:
                    p["energy"] = 100.0
        if self.career_player and "energy" not in self.career_player:
            self.career_player["energy"] = 100.0

    def _process_pending_requests(self):
        """Procesa las peticiones del jugador al DT tras unos días."""
        to_remove = []
        for req in self.pending_requests:
            req["days_left"] -= 1
            if req["days_left"] <= 0:
                self._handle_request_result(req)
                to_remove.append(req)
        for r in to_remove: self.pending_requests.remove(r)

    def _handle_request_result(self, req):
        """Genera la respuesta del DT a una petición."""
        import random
        success = random.random() < 0.7 # 70% de éxito por defecto
        
        # Factores que afectan
        conf = self.career_stats.get("coach_confidence", 40)
        if conf > 70: success = True # El DT te quiere complacer
        if conf < 30 and req["type"] == "stay": success = False # El DT te quiere fuera
        
        t = req["type"]
        if t == "transfer":
            if success:
                self.career_player["transfer_listed"] = True
                self.career_player["loan_listed"] = False
                self.add_email("info", "Respuesta: Solicitud de Traspaso", "Tras hablar con la directiva, hemos aceptado tu petición. Estás oficialmente en el mercado.")
            else:
                self.add_email("info", "Respuesta: Solicitud de Traspaso", "No podemos permitirnos perderte en este momento. La petición ha sido denegada.")
        elif t == "loan":
            if success:
                self.career_player["loan_listed"] = True
                self.career_player["transfer_listed"] = False
                self.add_email("info", "Respuesta: Solicitud de Cesión", "Creemos que una cesión te vendría bien para ganar minutos. Petición aceptada.")
            else:
                self.add_email("info", "Respuesta: Solicitud de Cesión", "Contamos contigo para la rotación del primer equipo. No saldrás cedido de momento.")
        elif t == "stay":
            self.career_player["transfer_listed"] = False
            self.career_player["loan_listed"] = False
            self.add_email("info", "Respuesta: Permanencia", "Me alegra que quieras quedarte. Te hemos retirado de la lista de transferencias.")

    def request_transfer_status(self, req_type):
        """Inicia una petición al DT."""
        # Evitar duplicados
        if any(r["type"] == req_type for r in self.pending_requests): return False
        
        import random
        self.pending_requests.append({
            "type": req_type,
            "days_left": random.randint(2, 4)
        })
        return True

    def _check_captaincy(self):
        """Checks if the player qualifies to be the team captain."""
        if self.mode != "player" or not self.career_player: return
        if self.career_stats.get("is_captain"): return
        
        conf = self.career_stats.get("coach_confidence", 0)
        prestige = self.career_stats.get("prestige", 0)
        seasons = self.career_stats.get("seasons_completed", 0)
        ovr = self.career_player.get("ovr", 0)
        # Requirements:
        # High confidence (85+), High prestige (800+), and either 2 seasons OR being the best player (OVR 86+)
        if conf >= 85 and prestige >= 800:
            if seasons >= 2 or ovr >= 86:
                self.career_stats["is_captain"] = True
                self.add_news("CLUB", "NUEVO CAPITÁN", f"{self.career_player['name']} ha sido nombrado capitán del equipo. Un líder nato.")
                self.add_email("board", "Brazalete de Capitán", 
                               f"Hola {self.career_player['name']}, el cuerpo técnico y la directiva han decidido que eres el hombre ideal para portar el brazalete. "
                               "Tu liderazgo y rendimiento son un ejemplo para todos. ¡Felicidades, Capitán!")
                self._update_prestige(20)
                
        # --- National Team Captaincy ---
        if self.is_called_up and not self.career_stats.get("is_nt_captain"):
            nt_stats = self.nt_stats.get(self.nationality, {"matches": 0})
            
            # Dynamic requirement: Must be one of the top 3 players of the country
            from data.national_teams import build_national_squad
            nt_data, nt_roster, _ = build_national_squad(self.nationality, self.rosters, self.teams)
            top_ovr = max([p["ovr"] for p in nt_roster]) if nt_roster else 0
            
            # Requirements: Best player of the country (or close to it), high prestige, and 8+ matches
            if ovr >= top_ovr - 2 and prestige >= 850 and nt_stats.get("matches", 0) >= 8:
                self.career_stats["is_nt_captain"] = True
                self.add_news("INTL", "LÍDER NACIONAL", f"{self.career_player['name']} es el nuevo capitán de la selección. El brazalete está en buenas manos.")
                self.add_email("info", "Capitán de la Patria", 
                               f"Representar a tu país es un honor, pero liderarlo como capitán es la gloria máxima. "
                               "Has sido nombrado capitán de la selección nacional. ¡Haz historia!")
                self._update_prestige(30)

    def _check_national_goat_status(self):
        """Determines if the player is now the GOAT of their country with flexible criteria."""
        if self.mode != "player" or not self.career_player: return
        if self.career_stats.get("is_national_goat"): return # Already achieved
        
        nat = self.career_player.get("nat")
        if not nat: return
        
        # 1. Base requirements (Quality and Reputation)
        prestige = self.career_stats.get("prestige", 0)
        ovr = self.career_player.get("ovr", 0)
        if prestige < 850 or ovr < 85: return # Minimum threshold for any country
        
        # 2. Performance markers
        records = self._get_nt_historic_records(nat)
        p_name = self.career_player["name"]
        records_owned = 0
        if records.get("goals", {}).get("owner") == p_name: records_owned += 1
        if records.get("assists", {}).get("owner") == p_name: records_owned += 1
        if records.get("matches", {}).get("owner") == p_name: records_owned += 1
        
        # 3. Achievements
        titles = self.career_stats.get("titles", [])
        has_major_title = any(t in ["Copa del Mundo", "Eurocopa", "Copa América", "Copa Africana de Naciones", "Copa Asiática", "Copa de Oro CONCACAF"] for t in titles)
        has_ballon_dor = any("Balón de Oro" in award for award in self.career_stats.get("individual_awards", []))
        
        # 4. Contextual "Weight"
        # For small nations, reaching a Final is basically being a god
        made_wc_final = any("Finalista de la Copa del Mundo" in t for t in titles) or "Copa del Mundo" in titles
        
        # --- THE FLEXIBLE GOAT LOGIC ---
        is_goat = False
        
        # Path A: The Record Breaker (Owned almost all records + decent success)
        if records_owned >= 2 and (has_major_title or has_ballon_dor):
            is_goat = True
            
        # Path B: The Pioneer (Won the first major title or Ballon d'Or for a nation that had none)
        # (Assuming nations like Japan/African ones have no Ballon d'Or in our database history)
        if has_ballon_dor and (records_owned >= 1 or prestige >= 950):
            is_goat = True
            
        # Path C: The Hero (Won a World Cup or reached Final with a mid-tier nation)
        if made_wc_final and (records_owned >= 1 or ovr >= 90):
            is_goat = True
 
        if is_goat:
            self.career_stats["is_national_goat"] = True
            from data.national_teams import COUNTRY_MAP
            country_name = COUNTRY_MAP.get(nat, nat)
            
            # Massive News
            self.add_news("global", f"¡EL REY DE {country_name.upper()}!", 
                          f"{p_name} es ahora indiscutiblemente el MEJOR de su historia. Su impacto trasciende los números.")
            
            # Special Email
            self.add_email("info", "Leyenda Inmortal", 
                           f"Hiciste lo que nadie creía posible para {country_name}. Ya seas el primer Balón de Oro de tu tierra "
                           "o el hombre que rompió todos los récords, hoy eres eterno.")
            
            self._update_prestige(100)
            self.add_news("history", f"Leyenda: {p_name}", "Hito nacional desbloqueado.")
 
    def _check_global_goat_status(self):
        """The ultimate check: Is the player the greatest of all time in football history?"""
        if self.mode != "player" or not self.career_player: return
        if self.career_stats.get("is_global_goat"): return
        
        # Criteria for GLOBAL GOAT (The Messi/Pelé Level):
        p_name = self.career_player["name"]
        titles = self.career_stats.get("titles", [])
        awards = self.career_stats.get("individual_awards", [])
        
        # 1. Individual Dominance
        ballon_dors = len([a for a in awards if "Balón de Oro" in a])
        
        # 2. Collective Glory
        has_wc = any("Copa del Mundo" in t for t in titles)
        has_ucl = any(
            "Champions" in t or "CHAMPIONS" in t or 
            "Libertadores" in t or "LIBERTADORES" in t or 
            "Europa" in t or "EUROPA" in t or 
            "Conference" in t or "CONFERENCE" in t or 
            "Sudamericana" in t or "SUDAMERICANA" in t or
            "CAF_CONFEDERATION" in t or "CONCACAF_CUP" in t
            for t in titles
        )
        
        # 3. Attributes and Legacy
        ovr = self.career_player.get("ovr", 0)
        prestige = self.career_stats.get("prestige", 0)
        is_nat_goat = self.career_stats.get("is_national_goat", False)
        
        # THE GOD CONDITION (The "Madness" Requirements)
        # 3+ Ballon d'Ors, World Cup, Continental Title, National GOAT, 92+ OVR, 990+ Prestige
        if ballon_dors >= 3 and has_wc and has_ucl and is_nat_goat and ovr >= 92 and prestige >= 990:
            self.career_stats["is_global_goat"] = True
            
            # --- GLOBAL MADNESS EVENTS ---
            self.add_news("global", "¡EL MEJOR DE SIEMPRE!", 
                          f"Se acabó el debate. {p_name} es oficialmente el MEJOR JUGADOR DE LA HISTORIA DEL FÚTBOL.", importance=5)
            
            self.add_email("info", "De una Leyenda a otra", 
                           f"Hola {p_name}. El mundo del fútbol se inclina ante ti. Has superado todos los récords y la magia de los que estuvimos antes. "
                           "Ya no eres solo un jugador, eres el estándar eterno. Bienvenido al Olimpo.")
            
            # Bonus: Perfect Stats (Small boost)
            for s in self.career_player["s"]:
                if self.career_player["s"][s] > 80:
                    self.career_player["s"][s] = min(99, self.career_player["s"][s] + 3)
            
            self._update_prestige(100)
            self.add_news("history", "EL TRONO DE ORO", f"{p_name} ha sido coronado como el GOAT GLOBAL.")

    def _get_club_historic_records(self, team_short):
        """Returns the historic records for a specific club using database legend names."""
        # Parody legends matching the database
        LEGENDS = {
            "STE": {"goals": {"val": 672, "owner": "Lionel Messi"}, "matches": {"val": 778, "owner": "Xavi"}},
            "COR": {"goals": {"val": 450, "owner": "Cristiano Ronaldo"}, "matches": {"val": 741, "owner": "Raul"}},
            "UDV": {"goals": {"val": 253, "owner": "Wayner Runi"}, "matches": {"val": 718, "owner": "P. Scholles"}},
            "LIV": {"goals": {"val": 158, "owner": "M. Owenn"}, "matches": {"val": 710, "owner": "S. Gerrarde"}},
            "ROS": {"goals": {"val": 175, "owner": "Andri Shevchen"}, "matches": {"val": 902, "owner": "Maldinni"}},
            "AJT": {"goals": {"val": 563, "owner": "G. Mullere"}, "matches": {"val": 582, "owner": "Bekenbauer"}},
            "MIA": {"goals": {"val": 29, "owner": "Lionel Messi"}, "matches": {"val": 40, "owner": "Lionel Messi"}},
        }
        
        # Default for other clubs
        default = {"goals": {"val": 150, "owner": "Leyenda Local"}, "matches": {"val": 300, "owner": "Capitán Eterno"}}
        return LEGENDS.get(team_short, default)

    def _check_club_goat_status(self):
        """Determines if the player is now the GOAT of their current club."""
        if self.mode != "player" or not self.career_player: return
        t_short = self.player_team["short"]
        goat_key = f"is_goat_{t_short}"
        if self.career_stats.get(goat_key): return
        
        records = self._get_club_historic_records(t_short)
        p_name = self.career_player["name"]
        
        # Current career stats for THIS club
        # (For simplicity, we use total career stats if they haven't changed clubs, 
        # but in a real system we'd track club-specific stats. Let's assume total for now if club matches)
        p_goals = self.career_stats.get("player_goals", 0)
        p_assists = self.career_stats.get("player_assists", 0)
        p_matches = self.career_stats.get("matches", 0)
        titles = len(self.career_stats.get("titles", []))
        awards = len(self.career_stats.get("individual_awards", []))
        
        goal_record = records["goals"]["val"]
        match_record = records["matches"]["val"]
        
        # Position-based GOAT criteria
        pos = self.career_player.get("pos", "ST")
        pos_cat = self._get_pos_cat(p_name) # Reuse the helper
        
        can_be_goat = False
        reason = ""
        
        if pos_cat == "FW":
            # Goleadores: Superar récord o acercarse mucho con muchos títulos/premios
            if p_goals > goal_record: 
                can_be_goat = True
                reason = "máximo goleador histórico"
            elif p_goals > goal_record * 0.8 and (titles + awards) >= 10:
                can_be_goat = True
                reason = "su impacto ofensivo y vitrina de trofeos"
        
        elif pos_cat == "DF" or pos_cat == "GK":
            # Defensas/Porteros: Superar partidos o acercarse con muchos títulos y capitanía
            if p_matches > match_record:
                can_be_goat = True
                reason = "el jugador con más batallas en sus botas"
            elif p_matches > match_record * 0.8 and titles >= 4:
                can_be_goat = True
                reason = "ser el muro defensivo más laureado de nuestra historia"
        
        else: # Centrocampistas
            # Mix de asistencias, partidos y visión
            if (p_matches > match_record * 0.9 or p_assists > 100) and titles >= 3:
                can_be_goat = True
                reason = "ser el cerebro y arquitecto de nuestra era dorada"

        if can_be_goat and titles >= 2:
            self.career_stats[goat_key] = True
            team_name = self.player_team["name"]
            
            # Massive News with Cultural Impact
            pool = [
                f"{p_name} es ahora considerado el MEJOR DE LA HISTORIA del {team_name}. No es solo por sus números, sino por cómo cambió la identidad del club para siempre. Se ha anunciado la construcción de una estatua de bronce en la entrada principal.",
                f"Leyenda total: {p_name} alcanza el estatus de GOAT en {team_name}. En la ciudad no se habla de otra cosa; las tiendas han agotado existencias de su camiseta y una generación entera de niños ha empezado a jugar al fútbol gracias a él.",
                f"El fenómeno {p_name} llega a su punto máximo: declarado el más grande de la historia de los '{team_name}'. El club ha decidido renombrar una de las puertas del estadio en su honor. Su impacto cultural trasciende el campo de juego.",
                f"Hay un antes y un después de {p_name} en el {team_name}. Tras superar los registros de los antiguos mitos, el jugador se convierte en el estándar de oro de la institución. La devoción de la grada es total."
            ]
            self.add_news("CLUB", "MÁS QUE UN JUGADOR: UN ICONO", random.choice(pool), importance=3)
            
            # Email
            self.add_email("board", "Gracias por Todo", 
                           f"Como presidente del {team_name}, es un honor decir que eres el más grande que ha pasado por aquí. "
                           "No solo has ganado trofeos, has cambiado el alma de este club. Gracias por elegirnos para hacer historia.")
            
            self._update_prestige(45)

    def _generate_cultural_impact_news(self):
        """Random news reflecting the player's influence on fans and culture (if star)."""
        if self.mode != "player" or not self.career_player: return
        ovr = self.career_player.get("ovr", 70)
        if ovr < 82 and len(self.career_stats.get("titles", [])) < 2: return
        
        if random.random() > 0.05: return # Rare event
        
        p_name = self.career_player["name"]
        tm = self.player_team["name"]
        
        impacts = [
            {"t": "FIEBRE POR LA CAMISETA", "d": f"La demanda de la camiseta de {p_name} ha superado todas las expectativas. El club reporta ingresos récord por merchandising."},
            {"t": "TATUAJES CON HISTORIA", "d": f"Se ha hecho viral la imagen de varios aficionados tatuándose la firma de {p_name}. 'Es el héroe de mi vida', declara un seguidor."},
            {"t": "EL PLATO DEL CRACK", "d": f"Un famoso restaurante de la ciudad ha nombrado a su plato estrella como '{p_name}'. La devoción por el jugador llega hasta la gastronomía local."},
            {"t": "EFECTO EN LA CANTERA", "d": f"Las inscripciones en las escuelas de fútbol de la zona han subido un 40% desde la llegada de {p_name}. Todos quieren ser como el ídolo del {tm}."},
            {"t": "MURAL EN EL BARRIO", "d": f"Artistas locales han terminado un mural gigante con el rostro de {p_name} cerca del estadio. Se ha convertido en un lugar de peregrinación para los fans."}
        ]
        ev = random.choice(impacts)
        self.add_news("CULTURA", ev["t"], ev["d"], importance=1)


    def _check_international_eligibility(self):

        """Verifica si el jugador o mánager califica para la selección (A partir de Temp 2)."""
        if self.year < 2: return
        if self.managing_nt or self.is_called_up: return
        if not self.nationality: return
        
        # Evaluar cada 2 meses (aprox)
        if self.current_date.day == 1 and self.current_date.month % 2 == 0:
            eligible = False
            if self.mode == "player":
                # Check for national team call
                if self.career_stats.get("avg_rating", 0) >= 7.0 and self.career_stats["matches"] >= 3:
                    eligible = True
            else:
                # Manager logic: High win rate or top table
                if self.career_stats["matches"] >= 10 and self.career_stats["coach_confidence"] > 70:
                    eligible = True
            
            if eligible and random.random() < 0.3:
                from data.national_teams import get_national_team
                nt_data = get_national_team(self.nationality)
                if nt_data:
                    self.pending_nt_event = {
                        "type": "CALL" if self.mode == "player" else "OFFER",
                        "country_code": self.nationality,
                        "nt_data": nt_data
                    }

    def _generate_weekly_news(self):
        """Crea la noticia del Equipo de la Semana basado en las mejores calificaciones."""
        if not self.weekly_performers: return
        
        # Filtrar por mi liga para que sea relevante
        local_perf = [p for p in self.weekly_performers if (self.get_team_by_short(p["team"]).get("league") if self.get_team_by_short(p["team"]) else None) == self.league_id]
        if not local_perf: local_perf = self.weekly_performers
        
        local_perf.sort(key=lambda x: x["rating"], reverse=True)
        
        # Elegir 11 (idealmente por posicion, pero simplificado: top 11)
        totw = local_perf[:11]
        names = ", ".join([p["name"] for p in totw[:3]]) + "..."
        
        self.add_news("local", "Equipo de la Semana", f"La liga ha anunciado el XI ideal. Destacan: {names}. ¡Pura calidad en el campo!")
        self.weekly_performers = [] # Clear for next week

    def _generate_monthly_news(self):
        """Crea la noticia del Jugador del Mes."""
        if not self.monthly_performers: return
        
        # Promediar por nombre
        stats = {} # {name: [ratings, team]}
        for p in self.monthly_performers:
            if p["name"] not in stats: stats[p["name"]] = [[], p["team"]]
            stats[p["name"]][0].append(p["rating"])
            
        # Calcular promedios
        averages = []
        for name, data in stats.items():
            avg = sum(data[0]) / len(data[0])
            averages.append({"name": name, "team": data[1], "avg": avg, "matches": len(data[0])})
            
        # Filtrar los que jugaron al menos 2 partidos
        averages = [a for a in averages if a["matches"] >= 2]
        if not averages: return
        
        averages.sort(key=lambda x: x["avg"], reverse=True)
        potm = averages[0]
        
        title = f"POTM: {potm['name']} ({potm['team']})"
        desc = f"Con un promedio de {potm['avg']:.2f}, el jugador del {potm['team']} se corona como el mejor del mes."
        
        self.add_news("local", title, desc, importance=2)
        # Breve presencia en Global
        self.add_news("global", f"Estrella del Mes: {potm['name']}", f"El mundo habla del gran nivel mostrado por {potm['name']} este mes.", importance=2)
        
        self.monthly_performers = [] # Clear

    def schedule_international_break(self):

        """Programa 2 partidos amistosos internacionales."""
        if not self.nationality: return
        
        from data.national_teams import build_national_squad, NATIONAL_TEAMS
        
        # 1. Armar mi selección
        my_nt_data, my_roster, used_fa = build_national_squad(self.nationality, self.rosters, self.teams)
        self.add_news("intl", f"Convocatoria de {my_nt_data['name']}", f"El seleccionador ha anunciado la lista para los próximos amistosos. {self.manager_name} estará al mando.")
        if self.mode == "player" and self.is_called_up:
             self.add_news("local", "¡ESTÁS CONVOCADO!", f"Gran noticia para {self.manager_name}: ha sido citado para representar a su país.")
        for fa in used_fa:
            self.add_to_free_agents(fa)
            
        # 2. Elegir rival aleatorio
        rival_code = random.choice([nt["country_code"] for nt in NATIONAL_TEAMS if nt["country_code"] != self.nationality])
        rival_nt_data, rival_roster, used_fa_rival = build_national_squad(rival_code, self.rosters, self.teams)
        for fa in used_fa_rival:
            self.add_to_free_agents(fa)
            
        # Guardar rosters temporales para el partido
        self.rosters[my_nt_data["short"]] = my_roster
        self.rosters[rival_nt_data["short"]] = rival_roster
        if not any(t["short"] == my_nt_data["short"] for t in self.teams):
            self.teams.append(my_nt_data)
        if not any(t["short"] == rival_nt_data["short"] for t in self.teams):
            self.teams.append(rival_nt_data)
            
        # 3. Programar en el calendario (próximos 7 y 14 días)
        for days in [7, 14]:
            match_dt = self.current_date + datetime.timedelta(days=days)
            d_str = match_dt.isoformat()
            if d_str not in self.calendar:
                self.calendar[d_str] = []
            self.calendar[d_str].append({
                "type": "INTERNACIONAL",
                "lg": "INT",
                "matches": [(my_nt_data["short"], rival_nt_data["short"])]
            })

            
    def _simulate_score(self, stat_key, short1, short2, ev_type):
        t1, t2 = self.get_team_by_short(short1), self.get_team_by_short(short2)
        if not t1 or not t2: return 0, 0
        
        # Consistent OVR calculation
        s1 = self.get_team_ovr(short1)
        s2 = self.get_team_ovr(short2)
        
        g1, g2 = random.randint(0, 2), random.randint(0, 2)
        if s1 - s2 > 4: g1 += random.randint(0, 2)
        elif s2 - s1 > 4: g2 += random.randint(0, 2)
        
        # Home advantage in league
        if ev_type == "LIGA" and random.random() < 0.3: g1 += 1
        
        self._register_sim_goals(stat_key, short1, g1)
        self._register_sim_goals(stat_key, short2, g2)
        
        # Simular incidentes (tarjetas y lesiones)
        self._simulate_match_incidents(stat_key, short1)
        self._simulate_match_incidents(stat_key, short2)
        
        # Add random performers to buffers for TOTW/POTM
        for t_short in [short1, short2]:
            t_obj = self.get_team_by_short(t_short)
            roster = self.rosters.get(t_short, [])
            if roster and t_obj:
                # Pick 2-3 players from each team and give them a rating
                best = sorted(roster, key=lambda x: x.get("ovr",70), reverse=True)[:3]
                for p in best:
                    rating = round(random.uniform(6.0, 8.5), 1)
                    if (t_short == short1 and g1 > g2) or (t_short == short2 and g2 > g1):
                        rating += 0.5 # Winner boost
                    perf = {"name": p["name"], "team": t_short, "rating": rating, "pos": p.get("pos", "CM")}
                    self.weekly_performers.append(perf)
                    self.monthly_performers.append(perf)
                    if "COPA_" in ev_type or "INTL_" in ev_type:
                        if ev_type not in self.cup_performers: self.cup_performers[ev_type] = []
                        self.cup_performers[ev_type].append(perf)

        return g1, g2

    def _get_sim_starters(self, team_short):
        """Get best 11 available (non-injured, non-suspended) players for simulation."""
        r = self.rosters.get(team_short, [])
        if not r: return []
        
        available = []
        for p in r:
            if p.get("injured_until") or p.get("suspended_matches", 0) > 0:
                continue
            available.append(p)
            
        # Ordenar por OVR y tomar top 11
        available.sort(key=lambda x: x.get("ovr", 70), reverse=True)
        
        # Integrar jugador de carrera según confianza si está en este equipo
        if self.mode == "player" and team_short == self.player_team["short"]:
            conf = self.career_stats.get("coach_confidence", 40)
            cp = self.career_player
            real_cp = next((p for p in available if p["name"] == cp["name"]), None)
            if real_cp:
                if conf >= 50:
                    available = [p for p in available if p["name"] != cp["name"]]
                    available.insert(0, real_cp)
                else:
                    # Benched/Substitute/No Convocado: exclude from starting 11
                    available = [p for p in available if p["name"] != cp["name"]]
                    available.append(real_cp)
        
        return available[:11]

    def _update_coach_confidence(self, res):
        """Logic to evolve the coach's trust in the player progressively."""
        if self.mode != "player": return
        
        old_conf = self.career_stats.get("coach_confidence", 40)
        delta = 0
        pf, pa = res["gf"], res["ga"]
        
        if pf > pa: delta += 1.5
        elif pf < pa: delta -= 1.0
        
        # Performance impact (Very progressive as requested)
        if "player_stats" in res:
            pname = self.career_player["name"]
            for ps in res["player_stats"]:
                if ps.get("name") == pname:
                    rat = ps.get("rating", 6.0)
                    if rat >= 9.0: delta += 2.0 # 5 goals won't give 50 confidence anymore
                    elif rat >= 8.0: delta += 1.2
                    elif rat >= 7.0: delta += 0.5
                    elif rat >= 6.0: delta += 0.1
                    elif rat < 5.0: delta -= 2.5
                    break
        
        self.career_stats["coach_confidence"] = max(0, min(100, old_conf + delta))
        conf = self.career_stats["coach_confidence"]
        
        # Update Starter Status based on thresholds
        if conf >= 50: self.player_status = "Titular"
        elif conf >= 30: self.player_status = "Suplente"
        else: self.player_status = "No Convocado"
        
        # Emails for status change
        if old_conf < 50 and conf >= 50:
            self.add_email("alert", "¡HAS GANADO LA TITULARIDAD!", "Tus esfuerzos han dado frutos. El mánager confía en ti para el XI inicial.")
        elif old_conf >= 50 and conf < 50:
            self.add_email("alert", "Pérdida de Titularidad", "El mánager no está satisfecho con tus últimos rendimientos. Partirás desde el banquillo.")

    def _simulate_match_incidents(self, stat_key, team_short):
        import random
        players = self._get_sim_starters(team_short)
        if not players: return
        
        for p in players:
            self._update_club_player_stats(team_short, p["name"], matches=1)
            # 1. Lesiones (Baja probabilidad: 0.8% por partido)
            if random.random() < 0.008:
                days = random.randint(3, 21)
                recovery_date = self.current_date + datetime.timedelta(days=days)
                p["injured_until"] = recovery_date.isoformat()
                if self.mode == "player" and p["name"] == self.career_player["name"]:
                    self.add_email("alert", "PARTE MÉDICO: LESIÓN", f"Durante el último encuentro has sufrido una lesión. Los médicos estiman una recuperación de {days} días. Volverás el {recovery_date.strftime('%d/%m/%y')}.")

            # 2. Tarjetas (Probabilidad: 12% por partido)
            if random.random() < 0.12:
                # 90% Amarilla, 10% Roja directa
                if random.random() < 0.90:
                    p["yellow_cards"] = p.get("yellow_cards", 0) + 1
                    if p["yellow_cards"] >= 5: # Ciclo de 5 amarillas
                        p["suspended_matches"] = 1
                        p["yellow_cards"] = 0
                else:
                    p["suspended_matches"] = 1
        
    def _add_goal(self, stat_key, name):
        if stat_key not in self.scorers: self.scorers[stat_key] = {}
        self.scorers[stat_key][name] = self.scorers[stat_key].get(name, 0) + 1
        
    def _add_assist(self, stat_key, name):
        if stat_key not in self.assists: self.assists[stat_key] = {}
        self.assists[stat_key][name] = self.assists[stat_key].get(name, 0) + 1
        
    def _register_sim_goals(self, stat_key, short, goals):
        starters = self._get_sim_starters(short)
        if not starters: return
        
        attackers = [p for p in starters if p.get("pos") in ["ST", "LW", "RW", "CM", "CAM"]]
        if not attackers: attackers = starters
        
        for _ in range(goals):
            sc_player = random.choice(attackers)
            sc = sc_player["name"]
            self._add_goal(stat_key, sc)
            self._update_club_player_stats(short, sc, goals=1)
            
            # Si es el jugador de carrera, sumar a su estadística global
            if self.mode == "player" and sc == self.career_player["name"]:
                self.career_stats["player_goals"] += 1
                
            if random.random() < 0.6:
                assisters = [p for p in starters if p["name"] != sc]
                if assisters:
                    a_player = random.choice(assisters)
                    a = a_player["name"]
                    self._add_assist(stat_key, a)
                    self._update_club_player_stats(short, a, assists=1)
                    if self.mode == "player" and a == self.career_player["name"]:
                        self.career_stats["player_assists"] += 1
                    
    def _track_relationships(self, match_result, t1, t2):
        """Track historic partnerships (teammates) and rivalries (opponents) for narrative depth."""
        if not self.career_player: return
        p_name = self.career_player["name"]
        p_team = self.player_team["short"]
        p_pos = self.career_player.get("pos", "CM")
        
        partnerships = self.career_stats.setdefault("partnerships", {})
        rivalries = self.career_stats.setdefault("rivalries", {})
        
        scorers = match_result.get("scorers", [])
        assists = match_result.get("assists", [])
        gf = match_result.get("gf", 0)
        ga = match_result.get("ga", 0)
        player_scored = p_name in scorers
        player_assisted = p_name in assists
        
        # --- PARTNERSHIPS (teammates) ---
        # Get teammates from the roster
        teammates = self.rosters.get(p_team, [])
        for tm in teammates:
            tm_name = tm.get("name", "")
            if tm_name == p_name: continue
            
            entry = partnerships.setdefault(tm_name, {
                "team": p_team, "matches": 0, "goals_together": 0,
                "assists_to_you": 0, "assists_from_you": 0
            })
            entry["team"] = p_team
            entry["matches"] += 1
            
            # Did they score together this match?
            if tm_name in scorers and player_scored:
                entry["goals_together"] += 1
            # Did they assist the player?
            if player_scored and tm_name in assists:
                entry["assists_to_you"] += 1
            # Did the player assist them?
            if player_assisted and tm_name in scorers:
                entry["assists_from_you"] += 1
                
        # --- RIVALRIES (opponents) ---
        opp_short = t2 if p_team == t1 else t1
        opp_roster = self.rosters.get(opp_short, [])
        
        # Determine similar positions for rivalry focus
        attacking = ["ST", "CF", "LW", "RW"]
        midfield = ["CM", "CAM", "CDM", "LM", "RM"]
        defense = ["CB", "LB", "RB", "LWB", "RWB"]
        
        if p_pos in attacking: rival_pos_group = attacking
        elif p_pos in midfield: rival_pos_group = midfield
        elif p_pos in defense: rival_pos_group = defense
        else: rival_pos_group = ["GK"]
        
        player_won = gf > ga
        player_lost = ga > gf
        
        for opp in opp_roster:
            opp_name = opp.get("name", "")
            opp_pos = opp.get("pos", "CM")
            
            # Only track as "rival" if they share a position group or they scored against us
            is_pos_rival = opp_pos in rival_pos_group
            opp_scored = opp_name in scorers
            
            if not is_pos_rival and not opp_scored:
                continue
            
            entry = rivalries.setdefault(opp_name, {
                "team": opp_short, "pos": opp_pos,
                "matches_against": 0, "your_wins": 0, "their_wins": 0,
                "their_goals": 0, "their_awards": []
            })
            entry["team"] = opp_short
            entry["matches_against"] += 1
            if player_won: entry["your_wins"] += 1
            if player_lost: entry["their_wins"] += 1
            if opp_scored: entry["their_goals"] += 1

    def _generate_relationship_news(self):
        """Called at season end to generate news stories about notable partnerships and rivalries."""
        if self.mode != "player" or not self.career_player: return
        
        p_name = self.career_player["name"]
        partnerships = self.career_stats.get("partnerships", {})
        rivalries = self.career_stats.get("rivalries", {})
        
        # --- Best Partner ---
        best_partner = None
        best_score = 0
        for name, data in partnerships.items():
            score = data["assists_to_you"] * 3 + data["assists_from_you"] * 3 + data["goals_together"] * 2 + data["matches"] * 0.1
            if score > best_score:
                best_score = score
                best_partner = (name, data)
                
        if best_partner and best_score >= 5:
            pn, pd = best_partner
            total_connections = pd["assists_to_you"] + pd["assists_from_you"] + pd["goals_together"]
            self.add_news("narrativa", f"🤝 Dupla Histórica: {p_name} y {pn}",
                f"La conexión entre {p_name} y {pn} sigue siendo imparable. "
                f"Han compartido {pd['matches']} partidos juntos con {total_connections} conexiones de gol directas. "
                f"¿Estamos ante la mejor dupla del fútbol actual?", importance=2)
        
        # --- Main Rival ---
        top_rival = None
        top_rival_score = 0
        for name, data in rivalries.items():
            score = data["matches_against"] + data["their_goals"] * 2 + abs(data["your_wins"] - data["their_wins"])
            if score > top_rival_score:
                top_rival_score = score
                top_rival = (name, data)
                
        if top_rival and top_rival_score >= 4:
            rn, rd = top_rival
            opp_team = self.get_team_by_short(rd["team"])
            opp_name = opp_team["name"] if opp_team else rd["team"]
            
            if rd["your_wins"] > rd["their_wins"]:
                verdict = f"{p_name} lleva ventaja con {rd['your_wins']} victorias contra {rd['their_wins']}."
            elif rd["their_wins"] > rd["your_wins"]:
                verdict = f"{rn} domina la rivalidad con {rd['their_wins']} victorias contra {rd['your_wins']}."
            else:
                verdict = "La rivalidad está igualadísima en victorias directas."
            
            self.add_news("narrativa", f"⚔️ Rivalidad Histórica: {p_name} vs {rn}",
                f"La batalla entre {p_name} y {rn} ({opp_name}) se ha convertido en una de las grandes narrativas del fútbol. "
                f"Se han enfrentado {rd['matches_against']} veces. {verdict}", importance=2)
        
        # --- Loyalty Partner (many matches together regardless of goals) ---
        loyal_partner = None
        loyal_matches = 0
        for name, data in partnerships.items():
            if data["matches"] > loyal_matches:
                loyal_matches = data["matches"]
                loyal_partner = (name, data)
                
        if loyal_partner and loyal_matches >= 20 and (not best_partner or loyal_partner[0] != best_partner[0]):
            ln, ld = loyal_partner
            self.add_news("narrativa", f"🫂 Hermanos de Vestuario: {p_name} y {ln}",
                f"{p_name} y {ln} llevan ya {ld['matches']} partidos compartiendo vestuario. "
                f"Una amistad forjada en el campo que trasciende las estadísticas.", importance=1)

    def _apply_match_stats(self, lg, short1, short2, g1, g2):
        st1 = self.standings.get(lg, {}).get(short1)
        st2 = self.standings.get(lg, {}).get(short2)
        if not st1 or not st2: return
        
        st1["ph"] += 1; st2["ph"] += 1
        st1["gf"] += g1; st1["ga"] += g2
        st2["gf"] += g2; st2["ga"] += g1
        
        if g1 > g2:
            st1["pts"] += 3; st1["w"] += 1
            st2["l"] += 1
        elif g2 > g1:
            st2["pts"] += 3; st2["w"] += 1
            st1["l"] += 1
        else:
            st1["pts"] += 1; st1["d"] += 1
            st2["pts"] += 1; st2["d"] += 1
            
        self._decrement_suspensions(short1)
        self._decrement_suspensions(short2)

    def _get_historic_records(self, team):
        if "records" in team: return team["records"]
        
        import random
        from data.procedural import PATTERNS
        
        ovr = self.get_team_ovr(team["short"])
        if ovr >= 85: max_m, max_g, max_a = random.randint(500, 750), random.randint(250, 450), random.randint(100, 200)
        elif ovr >= 78: max_m, max_g, max_a = random.randint(350, 500), random.randint(120, 250), random.randint(60, 120)
        else: max_m, max_g, max_a = random.randint(200, 400), random.randint(60, 130), random.randint(40, 80)
            
        lg = team.get("league", "EN")
        pats = PATTERNS.get(lg, PATTERNS["EN"])
        def _n(): return f"{random.choice(pats['first'])} {random.choice(pats['last'])}"
        
        records = {
            "most_matches": {"name": _n(), "val": max_m},
            "most_goals": {"name": _n(), "val": max_g},
            "most_assists": {"name": _n(), "val": max_a},
            "youngest_10_goals": {"name": _n(), "age": random.randint(17, 19)},
            "youngest_50_goals": {"name": _n(), "age": random.randint(20, 22)},
            "youngest_100_matches": {"name": _n(), "age": random.randint(20, 23)}
        }
        team["records"] = records
        return records

    def _get_nt_historic_records(self, country_code):
        """Generates historical records using the Master Legends database (Ultimate Mode)."""
        from data.national_teams import get_national_team
        nt = get_national_team(country_code)
        if not nt: return None
        if "records" in nt: return nt["records"]
        
        # 1. Load Base Legends from Server database
        try:
            from server.legends_database import LEGENDS_BASE
            all_legends = LEGENDS_BASE
        except ImportError:
            all_legends = []
            
        # 2. Map 2-letter code to 3-letter database codes
        mapping_3 = {
            "AR": "ARG", "BR": "BRA", "DE": "GER", "IT": "ITA", "EN": "ENG", "ES": "ESP", "TR": "TUR", "TR": "TUR",
            "FR": "FRA", "PT": "POR", "NL": "NED", "UY": "URU", "CO": "COL", "JP": "JPN",
            "MX": "MEX", "US": "USA", "BE": "BEL", "HR": "CRO", "UA": "UKR", "CL": "CHI"
        }
        target_3 = mapping_3.get(country_code, country_code)
        
        # 3. Filter legends for this nation
        nat_legends = [p for p in all_legends if p.get("nat") == target_3]
        def _safe_pot(x):
            try:
                return int(x.get("pot", 70))
            except (ValueError, TypeError):
                return 70
        nat_legends.sort(key=_safe_pot, reverse=True)
        
        # Base values for records
        ovr = nt.get("target_ovr", 78)
        if ovr >= 85: max_m, max_g, max_a = random.randint(130, 180), random.randint(50, 110), random.randint(30, 60)
        elif ovr >= 80: max_m, max_g, max_a = random.randint(110, 150), random.randint(35, 70), random.randint(20, 45)
        else: max_m, max_g, max_a = random.randint(90, 130), random.randint(20, 50), random.randint(15, 30)
        
        from data.procedural import PATTERNS
        lg_pool = nt.get("league_pool", "EN")
        pats = PATTERNS.get(lg_pool, PATTERNS["EN"])
        def _n(): return f"{random.choice(pats['first'])} {random.choice(pats['last'])}"
        
        records = {
            "most_matches": {"name": _n(), "val": max_m},
            "most_goals": {"name": _n(), "val": max_g},
            "most_assists": {"name": _n(), "val": max_a},
            "youngest_debut_goal": {"name": _n(), "age": random.randint(17, 19)},
            "youngest_10_goals": {"name": _n(), "age": random.randint(19, 21)},
            "youngest_50_matches": {"name": _n(), "age": random.randint(20, 22)}
        }
        
        # 4. Use Legends from Database (Position-Aware)
        if nat_legends:
            # Most Goals: Best Forward (ST, CF, LW, RW)
            forwards = [p for p in nat_legends if p.get("pos") in ["ST", "CF", "LW", "RW", "CAM"]]
            if forwards:
                records["most_goals"] = {"name": forwards[0]["name"], "val": max_g}
            else:
                records["most_goals"] = {"name": nat_legends[0]["name"], "val": max_g}
            
            # Most Matches: Absolute top legend (often the one with highest pot)
            records["most_matches"] = {"name": nat_legends[0]["name"], "val": max_m}
            
            # Most Assists: Best Midfielder (CAM, CM, LM, RM)
            mids = [p for p in nat_legends if p.get("pos") in ["CAM", "CM", "LM", "RM", "LW", "RW"]]
            if mids:
                records["most_assists"] = {"name": mids[0]["name"], "val": max_a}
                
            # Youngest debut goal: Second best forward or a young legend if available
            if len(forwards) > 1:
                records["youngest_debut_goal"] = {"name": forwards[1]["name"], "age": random.randint(17, 19)}
        else:
            # Fallback to free_agents if no ultimate legends
            fa_pool = nt.get("free_agents", [])
            if fa_pool:
                fa_pool_sorted = sorted(fa_pool, key=lambda x: x.get("ovr", 70), reverse=True)
                # Apply same position logic for free agents
                fa_fw = [p for p in fa_pool_sorted if p["pos"] in ["ST", "CF", "LW", "RW", "CAM"]]
                if fa_fw:
                    records["most_goals"] = {"name": fa_fw[0]["name"], "val": max_g}
                else:
                    records["most_goals"] = {"name": fa_pool_sorted[0]["name"], "val": max_g}
                    
                records["most_matches"] = {"name": fa_pool_sorted[0]["name"], "val": max_m}
                
                fa_mids = [p for p in fa_pool_sorted if p["pos"] in ["CAM", "CM", "LW", "RW"]]
                if fa_mids:
                    records["most_assists"] = {"name": fa_mids[0]["name"], "val": max_a}

        nt["records"] = records
        return records

    def _update_nt_player_stats(self, nt_short, p_name, matches=0, goals=0, assists=0):
        """Updates international stats and checks for historical milestones."""
        country_code = nt_short.replace("_NT", "")
        records = self._get_nt_historic_records(country_code)
        if not records: return
        
        # We need to find the player in the career universe to update their nt_stats
        # For simplicity, we track it in a separate dict if they are not the main player
        if not hasattr(self, "global_nt_stats"): self.global_nt_stats = {} # {name: {matches, goals, assists}}
        
        if p_name not in self.global_nt_stats:
            self.global_nt_stats[p_name] = {"matches": 0, "goals": 0, "assists": 0, "age": 22} # Default age
            
        st = self.global_nt_stats[p_name]
        st["matches"] += matches
        st["goals"] += goals
        st["assists"] += assists
        
        # If it's the main player, we use the formal stats
        if self.mode == "player" and p_name and p_name.lower().strip() == self.career_player["name"].lower().strip():
            self.nt_stats["matches"] += matches
            self.nt_stats["goals"] += goals
            st["matches"] = self.nt_stats["matches"]
            st["goals"] = self.nt_stats["goals"]
            st["age"] = self.career_player.get("age", 20)

        # Check records
        m, g, a = st["matches"], st["goals"], st["assists"]
        age = st["age"]
        
        new_records = []
        if m > records["most_matches"]["val"]:
            records["most_matches"] = {"name": p_name, "val": m}
            if m >= 50: new_records.append(f"Jugador con más internacionalidades ({m})")
        if g > records["most_goals"]["val"] and g > 0:
            records["most_goals"] = {"name": p_name, "val": g}
            if g >= 10: new_records.append(f"Máximo goleador histórico de la selección ({g} goles)")
        if a > records["most_assists"]["val"] and a > 0:
            records["most_assists"] = {"name": p_name, "val": a}
            
        if g >= 1 and age < records["youngest_debut_goal"]["age"]:
            records["youngest_debut_goal"] = {"name": p_name, "age": age}
            new_records.append(f"Goleador más joven de la historia nacional ({age} años)")

        # News if milestone reached
        for msg in new_records:
            from data.national_teams import COUNTRY_MAP
            c_name = COUNTRY_MAP.get(country_code, country_code)
            self.add_news("INTL", f"HITO: {p_name} ({c_name})", msg, importance=2)
            if self.mode == "player" and p_name and p_name.lower().strip() == self.career_player["name"].lower().strip():
                self.add_email("info", "¡Hito Nacional!", f"Has alcanzado un récord con tu selección: {msg}. ¡Todo el país celebra tu logro!")
                self._update_prestige(15)

    def _find_player_club(self, p_name):
        """Busca el club actual de un jugador en todo el universo de la carrera."""
        for short, rost in self.rosters.items():
            for p in rost:
                if p.get("name") and p_name and p["name"].lower().strip() == p_name.lower().strip():
                    return short
        return None

    def _update_club_player_stats(self, team_short, p_name, matches=0, goals=0, assists=0, yellow_cards=0, red_card=0, is_injured=False, injury_severity=0):
        if not team_short: return
        team = self.get_team_by_short(team_short)
        if not team: return
        team_name = team["name"]
        
        records = self._get_historic_records(team)
        
        roster = self.rosters.get(team_short, [])
        for p in roster:
            if p.get("name") and p_name and p["name"].lower().strip() == p_name.lower().strip():
                p["club_matches"] = p.get("club_matches", 0) + matches
                p["club_goals"] = p.get("club_goals", 0) + goals
                p["club_assists"] = p.get("club_assists", 0) + assists
                
                # Sanciones (Carrera)
                if yellow_cards > 0:
                    p["yellow_cards_season"] = p.get("yellow_cards_season", 0) + yellow_cards
                    if p["yellow_cards_season"] >= 3:
                        p["suspension"] = p.get("suspension", 0) + 1
                        p["yellow_cards_season"] = 0
                if red_card > 0:
                    p["suspension"] = p.get("suspension", 0) + 1
                
                # Lesiones
                if is_injured:
                    days = 3 + int(injury_severity * 0.5) # De 3 a 53 días
                    if injury_severity > 80: days += 30 # Grave: +1 mes
                    p["injured_until"] = (self.current_date + datetime.timedelta(days=days)).isoformat()
                    
                    # News for important injuries
                    is_star = p.get("ovr", 70) > 82 or p.get("role") == "Estrella"
                    is_prospect = p.get("ovr", 70) > 75 and p.get("age", 25) < 22
                    is_my_team = team_short == self.player_team["short"]
                    
                    if days > 14 and (is_star or is_my_team or is_prospect):
                        severity_txt = "GRAVE" if days > 40 else "PREOCUPANTE"
                        if is_my_team:
                            news_msg = f"MALAS NOTICIAS: El {team_name} pierde a {p_name} por una lesión {severity_txt.lower()}. Se estima una baja de {days} días."
                        elif is_prospect:
                            news_msg = f"LA JOVEN PROMESA {p_name.upper()} SE LESIONA: El talentoso jugador del {team_name} estará fuera {days} días. ¿Afectará a su progresión?"
                        else:
                            news_msg = f"¡ALERTA MUNDIAL! La estrella {p_name} se ha lesionado en un partido {'internacional' if team_short.endswith('_NT') else 'clave'}. Estará fuera {days} días."
                        
                        self.add_news("INFO", f"PARTE MÉDICO: {p_name}", news_msg, importance=2 if days < 30 else 3)

                    if self.mode == "player" and p_name and p_name.lower().strip() == self.career_player["name"].lower().strip():
                        self.add_email("info", "Parte Médico", f"Malas noticias. Los doctores confirman una lesión. Estarás fuera aproximadamente {days} días.")

                # News for important red cards
                if red_card > 0:
                    is_star = p.get("ovr", 70) > 83
                    is_my_team = team_short == self.player_team["short"]
                    if is_star or is_my_team:
                        self.add_news("MERCADO", f"SANCIÓN: {p_name}", 
                                      f"Polémica en el último encuentro: {p_name} fue expulsado con roja directa y se perderá los próximos compromisos del {team_name}.", 
                                      importance=2)
                
                c_matches = p["club_matches"]
                c_goals = p["club_goals"]
                c_assists = p["club_assists"]
                age = p.get("age", 25)
                
                new_records = []
                if c_matches > records["most_matches"]["val"]:
                    records["most_matches"] = {"name": p_name, "val": c_matches}
                    if c_matches >= 30: new_records.append(f"Jugador con más partidos en la historia del club ({c_matches})")
                    
                if c_goals > records["most_goals"]["val"] and c_goals > 0:
                    records["most_goals"] = {"name": p_name, "val": c_goals}
                    if c_goals >= 10: new_records.append(f"Máximo goleador histórico del club ({c_goals} goles)")
                    
                if c_assists > records["most_assists"]["val"] and c_assists > 0:
                    records["most_assists"] = {"name": p_name, "val": c_assists}
                    if c_assists >= 10: new_records.append(f"Máximo asistente histórico del club ({c_assists} asistencias)")
                    
                if c_goals >= 10 and age < records["youngest_10_goals"]["age"]:
                    records["youngest_10_goals"] = {"name": p_name, "age": age}
                    new_records.append(f"Jugador más joven en marcar 10 goles ({age} años)")
                    
                if c_goals >= 50 and age < records["youngest_50_goals"]["age"]:
                    records["youngest_50_goals"] = {"name": p_name, "age": age}
                    new_records.append(f"Jugador más joven en llegar a 50 goles ({age} años)")
                    
                if c_matches >= 100 and age < records["youngest_100_matches"]["age"]:
                    records["youngest_100_matches"] = {"name": p_name, "age": age}
                    new_records.append(f"Jugador más joven en llegar a 100 partidos ({age} años)")
                    
                for rec in new_records:
                    self.add_news("club", f"🏆 ¡Nuevo Récord en {team['name']}!",
                        f"Historia viva: {p_name} ha establecido un nuevo récord en el club: {rec}.", importance=2)
                break
    def _decrement_suspensions(self, team_short):
        r = self.rosters.get(team_short, [])
        for p in r:
            if p.get("suspended_matches", 0) > 0:
                p["suspended_matches"] -= 1

    def _apply_continental_match(self, comp_name, short1, short2, g1, g2):
        # Handle Swiss league phase for UCL
        comp = self.continental.get(comp_name, {})
        if comp.get("format") == "SWISS" and comp.get("phase") == "LEAGUE":
            ls = comp["league_standings"]
            for team, goals_for, goals_against in [(short1, g1, g2), (short2, g2, g1)]:
                if team in ls:
                    ls[team]["ph"] += 1
                    ls[team]["gf"] += goals_for
                    ls[team]["ga"] += goals_against
                    if goals_for > goals_against:
                        ls[team]["pts"] += 3; ls[team]["w"] += 1
                    elif goals_for == goals_against:
                        ls[team]["pts"] += 1; ls[team]["d"] += 1
                    else:
                        ls[team]["l"] += 1
            # Check if league phase is done (8 matchdays)
            all_done = all(s["ph"] >= 8 for s in ls.values())
            if not all_done:
                all_done = all(s["ph"] >= len(comp.get("swiss_fixtures", [])) for s in ls.values())
            if all_done:
                self._advance_swiss_to_knockout(comp_name)
            return
        self._decrement_suspensions(short1)
        self._decrement_suspensions(short2)
        
        comp = self.continental.get(comp_name)
        if not comp: return
        
        if comp["phase"] == "GROUPS":
            for g_name, g_data in comp["groups"].items():
                st = g_data["standings"]
                if short1 in st and short2 in st:
                    t1 = self.get_team_by_short(short1)
                    t2 = self.get_team_by_short(short2)
                    lg1 = t1.get("league", "EN")
                    
                    g_data["results"].append({"home": short1, "away": short2, "g1": g1, "g2": g2})
                    st[short1]["ph"] += 1; st[short2]["ph"] += 1
                    st[short1]["gf"] += g1; st[short1]["ga"] += g2
                    st[short2]["gf"] += g2; st[short2]["ga"] += g1
                    if g1 > g2:
                        st[short1]["pts"] += 3; st[short1]["w"] += 1; st[short2]["l"] += 1
                        if g1 >= 5:
                            self.add_news("global", f"Goleada del {t1['name']}", f"Victoria contundente por {g1}-{g2} ante el {t2['name']} en competición continental.")
                    elif g2 > g1:
                        st[short2]["pts"] += 3; st[short2]["w"] += 1; st[short1]["l"] += 1
                        if g2 >= 5:
                            self.add_news("global", f"Paliza del {t2['name']}", f"El {t2['name']} humilló al {t1['name']} con un marcador de {g2}-{g1}.")
                    else:
                        st[short1]["pts"] += 1; st[short1]["d"] += 1
                        st[short2]["pts"] += 1; st[short2]["d"] += 1
                    break
        elif comp["phase"] in ("KNOCKOUT", "R16", "QF", "SF", "FINAL"):
            # 1. Update bracket (with double legs)
            for stage in ["R16", "QF", "SF", "FINAL"]:
                matches = comp["bracket"].get(stage, [])
                for m in matches:
                    if m["h"] == short1 and m["a"] == short2 and m["res1"] is None:
                        m["res1"] = (g1, g2)
                        break
                    elif m["h"] == short2 and m["a"] == short1 and m["res2"] is None:
                        m["res2"] = (g2, g1)
                        break
            
            # 2. Sync to knockout for UI compatibility
            for stage in ["R16", "QF", "SF", "FINAL"]:
                bracket_matches = comp["bracket"].get(stage, [])
                comp["knockout"][stage] = []
                for bm in bracket_matches:
                    res = None
                    if stage == "FINAL":
                        if bm["res1"] is not None:
                            res = bm["res1"]
                    else:
                        if bm["res1"] is not None and bm["res2"] is not None:
                            # Aggregate score
                            res = (bm["res1"][0] + bm["res2"][0], bm["res1"][1] + bm["res2"][1])
                        elif bm["res1"] is not None:
                            res = bm["res1"]
                    comp["knockout"][stage].append({
                        "home": bm["h"],
                        "away": bm["a"],
                        "result": res
                    })

    def _process_cpu_transfers(self):
        # A simple rotation where random CPU teams with high budget buy random good players from other teams
        for t in self.teams:
            if self.player_team and t["short"] == self.player_team["short"]: continue
            if t["short"] == "LIB" or t["short"].endswith("_NT") or t.get("is_national") or t.get("league") == "NT": continue
            if t["short"] not in self.rosters: continue
            if t.get("budget", 0) > 20:
                if random.random() < 0.1:
                    # Filter teams that are not player team, not LIB, not NT and have rosters
                    choices = [
                        x["short"] for x in self.teams 
                        if x["short"] != t["short"] 
                        and (not self.player_team or x["short"] != self.player_team["short"]) 
                        and x["short"] != "LIB" 
                        and not x["short"].endswith("_NT") 
                        and not x.get("is_national") 
                        and x.get("league") != "NT"
                        and x["short"] in self.rosters
                    ]
                    if not choices: continue
                    target_short = random.choice(choices)
                    target_roster = self.rosters.get(target_short, [])
                    if target_roster and len(target_roster) > 14:
                        target_p = random.choice(target_roster)
                        
                        ovr = target_p.get("ovr", 70)
                        base_v = max(1, max(0, ovr - 60) ** 1.8 * 0.15)
                        val = int(base_v)
                        if val < t["budget"] and val > 0:
                            t["budget"] -= val
                            target_team = self.get_team_by_short(target_short)
                            if target_team and "budget" in target_team:
                                target_team["budget"] += val
                            idx = target_roster.index(target_p)
                            popped = target_roster.pop(idx)
                            self.rosters[t["short"]].append(popped)
                            
                            # Add News
                            if val > 30:
                                self.add_news("market", f"¡FICHAJE BOMBA: {popped['name']}!", f"El {t['name']} rompe el mercado pagando ${val}M por la estrella del {target_short}.", importance=2)
                            elif t.get("league") == self.league_id:
                                self.add_news("market", f"Traspaso: {popped['name']}", f"{popped['name']} se une al {t['name']} por un valor de ${val}M.")

    def _process_negotiations(self):
        to_remove = []
        for neg in self.negotiations:
            if neg["state"] == "rejected":
                neg["cooldown"] -= 1
                if neg["cooldown"] <= 0:
                    to_remove.append(neg)
                continue
                
            neg["wait"] -= 1
            if neg["wait"] <= 0 and neg["state"] == "pending":
                # CPU considers the offer
                val = neg["estimated_value"]
                bid = neg["bid"]
                ratio = bid / float(val)
                
                # Special logic for Free Agents (LIB)
                if neg["t_short"] == "LIB":
                    if ratio >= 0.9:
                        neg["state"] = "accepted"
                        neg["wait"] = 0
                        return
                    else:
                        neg["state"] = "rejected"
                        neg["cooldown"] = 2
                        return

                # Logic for normal clubs
                if ratio >= 1.2:
                    neg["state"] = "accepted"
                elif ratio >= 0.85:
                    if random.random() < 0.5:
                        neg["state"] = "counter" # CPU proposes counter
                        neg["counter_val"] = int(val * random.uniform(1.05, 1.3))
                    else:
                        neg["state"] = "rejected"
                        neg["cooldown"] = 3
                else:
                    neg["state"] = "rejected"
                    neg["cooldown"] = 4
                    
        for x in to_remove:
            self.negotiations.remove(x)

    def _process_manager_applications(self):
        """Process the manager's applications to other teams."""
        to_remove = []
        for app in self.manager_applications:
            if app["state"] == "pending":
                app["wait"] -= 1
                if app["wait"] <= 0:
                    # CPU decides based on manager's record
                    win_rate = self.career_stats["wins"] / max(1, self.career_stats["matches"])
                    prestige = win_rate * 100 + len(self.career_stats["titles"]) * 20
                    target = self.get_team_by_short(app["team_short"])
                    if not target:
                        app["state"] = "rejected"
                        continue
                    # Better teams need higher prestige
                    team_ovr = self.get_team_ovr(app["team_short"])
                    threshold = team_ovr - 10  # e.g. 80 OVR team needs ~70 prestige
                    if prestige >= threshold or random.random() < 0.25:
                        app["state"] = "accepted"
                    else:
                        app["state"] = "rejected"
            elif app["state"] == "rejected":
                app["cooldown"] = app.get("cooldown", 0) - 1
                if app["cooldown"] <= 0:
                    to_remove.append(app)
        for x in to_remove:
            self.manager_applications.remove(x)

    def upgrade_agent(self):
        """Mejora el nivel de tu representante para obtener mejores beneficios."""
        AGENTS_DATA = [
            {"level": 0, "name": "Ninguno", "commission": 0.0, "price": 0},
            {"level": 1, "name": "Básico (Familiar)", "commission": 0.03, "price": 0.1},
            {"level": 2, "name": "Intermedio (Profesional)", "commission": 0.05, "price": 0.5},
            {"level": 3, "name": "Top (Agente FIFA)", "commission": 0.07, "price": 2.0},
            {"level": 4, "name": "Leyenda (Jorge Mendes Style)", "commission": 0.10, "price": 5.0}
        ]
        
        curr_lvl = self.agent.get("level", 0)
        if curr_lvl >= 4:
            return False, "Ya tienes al mejor representante posible."
            
        next_agent = AGENTS_DATA[curr_lvl + 1]
        if self.career_stats["money"] < next_agent["price"]:
            return False, f"Necesitas ${next_agent['price']}M para contratar a un agente de nivel {next_agent['level']}."
            
        self.career_stats["money"] -= next_agent["price"]
        self.agent = next_agent
        
        # Recreate profile
        if "agent_profile" in self.career_stats:
            del self.career_stats["agent_profile"]
        self._ensure_agent_profile()
        agent_prof = self.career_stats.get("agent_profile", {})
        agent_name = agent_prof.get("name", next_agent["name"])
        
        # News
        self.add_news("local", "Nuevo Representante", f"{self.manager_name} ahora trabaja con {agent_name}.")
        self.add_email("info", "Contrato con Agente", f"¡Hola! Soy {agent_name}, tu nuevo representante. A partir de ahora, mi comisión será del {int(next_agent['commission']*100)}% pero te aseguro mejores contratos y ofertas.")
        
        return True, f"Has mejorado a {next_agent['name']}."

    def hire_agent(self, agent_id):
        # Deprecated in favor of upgrade_agent but kept for compat
        return self.upgrade_agent()

    def _generate_manager_offers(self):
        """CPU teams may offer the manager a job. Agent level increases chances and quality."""
        if not self.transfer_window_open: return
        if len(self.manager_offers) >= 3: return
        
        # Base chance 8%. Agent level adds 5% per level.
        chance = 0.08 + (self.agent.get("level", 0) * 0.05)
        
        # Boost chance if player has active agent suggestions
        suggestions = getattr(self, 'agent_suggestions', [])
        if suggestions:
            chance += 0.15  # Significant boost when agent is actively looking
        
        if random.random() > chance: return
            
        candidates = [t for t in self.teams 
                     if t["short"] != self.player_team["short"]
                     and t.get("budget", 0) > 10
                     and t.get("is_playable", True)]
        
        # Filter candidates based on manager prestige + agent bonus
        win_rate = self.career_stats["wins"] / max(1, self.career_stats["matches"])
        
        # Base prestige from wins/titles
        prestige = win_rate * 80 + len(self.career_stats["titles"]) * 15
        # Bonus prestige from individual awards (Legacy/Player career impact)
        awards = self.career_stats.get("individual_awards", [])
        prestige += len(awards) * 5
        
        # Agent level 3 allows looking at teams with up to 20 OVR higher than prestige
        agent_bonus = self.agent.get("level", 0) * 6 
        
        eligible = [t for t in candidates if self.get_team_ovr(t["short"]) <= (prestige + 15 + agent_bonus)]
        if not eligible: return
        
        # Prioritize suggested destinations
        suggested_teams = [s["team"] for s in suggestions if s.get("team")]
        suggested_leagues = [s["league"] for s in suggestions if not s.get("team")]
        
        prioritized = [t for t in eligible 
                       if t["short"] in suggested_teams 
                       or t.get("league") in suggested_leagues]
        
        # 70% chance to pick from suggestions if available
        if prioritized and random.random() < 0.70:
            team = random.choice(prioritized)
        else:
            team = random.choice(eligible)
        
        for o in self.manager_offers:
            if o["team_short"] == team["short"]: return
        
        # Salary offer: Agent negotiated bonus
        base_salary = random.randint(1, 5)
        agent_mult = 1.0 + (self.agent.get("level", 0) * 0.2)
        salary_offer = round(base_salary * agent_mult, 2)
        
        self.manager_offers.append({
            "team_short": team["short"],
            "team_name": team["name"],
            "salary": salary_offer,
            "state": "pending",
            "expires_in": 14
        })
        
        # Notify if it came from a suggestion
        if team["short"] in suggested_teams or team.get("league") in suggested_leagues:
            self.add_email("agent", f"¡Oferta de {team['name']}!",
                f"Jefe, tengo noticias. El {team['name']} ha mostrado interés gracias a mis contactos. "
                f"Revisa las ofertas en tu buzón.")

    def _generate_agent_recommendations(self):
        """Generates informal club recommendations via the agent in Player Mode."""
        if self.mode != "player": return
        if not self.transfer_window_open: return
        if len(self.agent_recommendations) >= 3: return
        
        # Base chance 12% per week (called daily, so lower)
        if random.random() > 0.03: return
        
        candidates = [t for t in self.teams if t["short"] != self.player_team["short"] and t.get("is_playable", True)]
        # Filter by player OVR and agent level
        p_ovr = self.career_player["ovr"]
        agent_lvl = self.agent.get("level", 0)
        max_ovr = p_ovr + 5 + (agent_lvl * 4)
        min_ovr = p_ovr - 15
        
        eligible = [t for t in candidates if min_ovr <= self.get_team_ovr(t["short"]) <= max_ovr]
        if not eligible: return
        
        team = random.choice(eligible)
        if any(r["team_short"] == team["short"] for r in self.agent_recommendations): return
        
        t_ovr = self.get_team_ovr(team["short"])
        
        # Define Sporting Project
        projects = [
            {"name": "Eje del Proyecto", "desc": "Serás la pieza central sobre la que construiremos el equipo."},
            {"name": "Caza-Talento", "desc": "Te ven como la joven promesa que revitalizará el vestuario."},
            {"name": "Refuerzo Estrella", "desc": "Quieren que seas el salto de calidad para pelear por títulos."},
            {"name": "Muro Defensivo", "desc": "Buscan solidez y tú eres su candidato número uno."},
            {"name": "Revulsivo de Lujo", "desc": "Entrarás en la rotación de un equipo top para marcar diferencias."}
        ]
        if t_ovr > p_ovr + 5: project = projects[4] # Revulsivo
        elif t_ovr < p_ovr - 5: project = projects[0] # Eje
        else: project = random.choice(projects[:3])
        
        # Define Economic Project
        base_sal = self._calculate_salary(self.career_player)
        agent_bonus = 1.0 + (agent_lvl * 0.15)
        proposed_sal = round(base_sal * agent_bonus * random.uniform(0.9, 1.2), 2)
        
        econ_types = [
            "Contrato con bonus por rendimiento y goles.",
            "Sueldo base alto con incremento anual garantizado.",
            "Prima de fichaje inmediata si firmamos esta semana.",
            "Contrato blindado con cláusula de rescisión baja."
        ]
        
        self.agent_recommendations.append({
            "team_short": team["short"],
            "team_name": team["name"],
            "project_name": project["name"],
            "project_desc": project["desc"],
            "salary": proposed_sal,
            "economic_desc": random.choice(econ_types),
            "expires_in": 10,
            "date": self.current_date.isoformat()
        })
        
        self.add_news("AGENTE", "RECOMENDACIÓN", f"Tu agente tiene una nueva propuesta del {team['name']}. Revisa los detalles en la oficina.", importance=2)
        
        # Add a chance of rumor in the press
        if random.random() < 0.6:
            self.add_rumor(team["name"], importance=1)

    def apply_to_team(self, team_short):
        """Manager sends application to manage another team."""
        # Check not already applied
        for app in self.manager_applications:
            if app["team_short"] == team_short:
                return "Ya has enviado una solicitud a este equipo."
        
        if team_short == self.player_team["short"]:
            return "Ya diriges este equipo."
        
        t = self.get_team_by_short(team_short)
        if not t:
            return "Equipo no encontrado."
            
        if not t.get("is_playable", True):
            return "Este club no acepta solicitudes (No jugable)."
        
        self.manager_applications.append({
            "team_short": team_short,
            "team_name": t["name"],
            "state": "pending",
            "wait": random.randint(7, 21),  # 1-3 weeks response time
            "cooldown": 0
        })
        return "Solicitud enviada. Espera la respuesta del club."

    def accept_offer(self, offer_idx):
        """Accept an incoming offer from another team."""
        if offer_idx < 0 or offer_idx >= len(self.manager_offers):
            return "Oferta no válida."
        offer = self.manager_offers[offer_idx]
        return self.change_team(offer["team_short"])

    def accept_application(self, app_idx):
        """Accept a confirmed application."""
        if app_idx < 0 or app_idx >= len(self.manager_applications):
            return "Solicitud no válida."
        app = self.manager_applications[app_idx]
        if app["state"] != "accepted":
            return "Esta solicitud no ha sido aceptada aún."
        return self.change_team(app["team_short"])

    def change_team(self, new_short):
        """Move the manager to a different team."""
        new_team = self.get_team_by_short(new_short)
        if not new_team:
            return "Equipo no encontrado."
        
        old_short = self.player_team["short"]
        
        # Store detailed history for narrative hooks
        exit_stats = {
            "short": old_short,
            "ovr": self.career_player["ovr"] if self.career_player else 70,
            "goals": self.current_team_stats["goals"],
            "matches": self.current_team_stats["matches"],
            "titles": len([t for t in self.career_stats["titles"] if old_short in t]) # Approximate
        }
        # Update or add
        self.team_history = [h for h in self.team_history if h["short"] != old_short]
        self.team_history.append(exit_stats)
        
        # Reset current stint stats
        self.current_team_stats = {"goals": 0, "matches": 0}
            
        self.player_team = new_team
        self.league_id = new_team.get("league", "EN")
        
        if new_short not in self.career_stats["teams_managed"]:
            self.career_stats["teams_managed"].append(new_short)
            
        # Roster movement for Player Career Mode transfer
        if self.mode == "player" and self.career_player:
            # 1. Remove player from the old team's roster
            if old_short in self.rosters:
                self.rosters[old_short] = [p for p in self.rosters[old_short] if not p.get("is_user_player")]
            
            # 2. Add player to the new team's roster
            if new_short in self.rosters:
                # Find a random available shirt number if the current number is taken
                taken_nums = {p["num"] for p in self.rosters[new_short] if "num" in p}
                p_num = self.career_player.get("num", 10)
                if p_num in taken_nums:
                    # Assign a random free number
                    for candidate in range(1, 100):
                        if candidate not in taken_nums:
                            self.career_player["num"] = candidate
                            break
                self.rosters[new_short].append(self.career_player)
                
            # Set joined date and joined transfer window to allow changing the shirt number!
            self.joined_date = self.current_date
            self.joined_transfer_window = self._get_transfer_window_name()
            
            # Trigger transfer reactions
            self._generate_transfer_reactions(old_short, new_short)
            
        self._log_milestone("TRANSFER", f"Fichó por {new_team['name']}")
        
        region_name = "el continente"
        if self.league_id in ["ES", "EN", "IT", "DE", "FR", "PT", "TR", "BE"]: region_name = "Europa"
        elif self.league_id in ["AR", "BR", "CO"]: region_name = "Sudamérica"
        
        subj = "NUEVA ETAPA" if self.mode == "player" else "NUEVO FICHAJE"
        name_ent = self.career_player["name"] if self.mode == "player" else self.manager_name
        
        # Dynamic expectations for transfers
        if self.mode == "player":
            p_ovr = self.career_player["ovr"]
            t_ovr = self.get_team_ovr(new_short)
            if p_ovr > t_ovr + 3:
                comment = f"Llega como la gran estrella mediática del {new_team['name']}, destinado a liderar el vestuario."
            elif p_ovr > t_ovr - 3:
                comment = f"Se espera que sea un refuerzo de lujo para elevar la competitividad interna del equipo."
            else:
                comment = f"Tendrá que luchar por un puesto, pero la directiva confía en su potencial a largo plazo."
            news_desc = f"{name_ent} se une a las filas del {new_team['name']}. {comment} El movimiento ha causado furor en {region_name}."
        else:
            news_desc = f"{name_ent} asume el banquillo del {new_team['name']}. Es uno de los movimientos más comentados en {region_name}."
            
        self.add_news("MERCADO", f"¡{subj}!", news_desc, importance=3, expiry_days=10)
        
        # Clear all offers/applications
        self.manager_offers = []
        self.manager_applications = []
        self.negotiations = []
        self.agent_suggestions = [] # Reset search when signing for a new club
        
        return f"¡Bienvenido a {new_team['name']}!"


    def _end_season(self):
        # Ballon d'Or and Yearly Awards
        self._generate_yearly_awards()
        
        # Gather Global Top Scorers and MVP candidates BEFORE resetting
        mvps = []
        for sn in self.scorers.keys():
            sorted_sc = sorted(self.scorers[sn].items(), key=lambda x: x[1], reverse=True)
            if sorted_sc:
                mvps.extend([(name, goals, sn) for name, goals in sorted_sc[:3]])
                
        mvps.sort(key=lambda x: x[1], reverse=True)
        top_players = mvps[:5]
        
        # Check if player won the league
        player_lg = self.player_team.get("league", "EN")
        lg_st = list(self.standings.get(player_lg, {}).items())
        lg_st.sort(key=lambda x: (x[1]["pts"], x[1]["gf"]-x[1]["ga"]), reverse=True)
        if lg_st and lg_st[0][0] == self.player_team["short"]:
            title_name = f"LIGA {player_lg}"
            self.career_stats["titles"].append(f"{title_name} (Temp. {self.year})")
            self._log_milestone("TITLE", f"Campeón de {title_name}")
            self.add_news("GLORIA", "¡CAMPEONES!", f"El {self.player_team['name']} se ha coronado campeón. Una temporada para el recuerdo.", importance=3)
        
        # SAVE final standings BEFORE resetting — used by _generate_continental for year 2+
        import copy
        self._final_standings = copy.deepcopy(self.standings)
        
        self.career_stats["seasons_completed"] += 1
        
        # Generate partnership and rivalry narratives
        self._generate_relationship_news()
        
        # Progress everyone, restart
        self._progress_season()
        self.year += 1
        # Increment age of children
        for child in self.career_stats.get("children", []):
            child["age"] += 1
        
        # Advance dates by 1 year (use replace to avoid leap-year drift)
        self.season_start = self.season_start.replace(year=self.season_start.year + 1)
        self.season_end = self.season_end.replace(year=self.season_end.year + 1)
        self.current_date = self.season_start
        self.calendar.clear()
        
        # Reset standings
        for lg in self.leagues:
            if lg not in self.standings:
                self.standings[lg] = {}
            lg_teams = [t for t in self.teams if t.get("league", "EN") == lg]
            for t in lg_teams:
                self.standings[lg][t["short"]] = {"pts":0, "ph":0, "w":0, "d":0, "l":0, "gf":0, "ga":0}
            
            self.scorers[f"LIGA_{lg}"] = {}
            self.assists[f"LIGA_{lg}"] = {}
            
        self._generate_schedules()
        self._generate_continental()
        self._generate_national_cups()
        
        # International Tournaments (June/July every 2/4 years)
        if self.year % 4 == 0:
            self._generate_intl_tournament("WORLD_CUP")
        elif self.year % 4 == 2:
            self._generate_intl_tournament("EURO_CUP")
            self._generate_intl_tournament("COPA_AMERICA")
            self._generate_intl_tournament("AFCON")
            self._generate_intl_tournament("ASIAN_CUP")
            self._generate_intl_tournament("GOLD_CUP")
            
        # 5. Check for GOAT status (National, Global and Club)
        self._check_national_goat_status()
        self._check_global_goat_status()
        self._check_club_goat_status()
        
        self._initialize_objectives()
        return top_players

    def _generate_intl_tournament(self, type_key):
        """Initializes a bracket-based international tournament for national teams."""
        from data.national_teams import NATIONAL_TEAMS, build_national_squad
        
        # 1. Filter candidates by continent or all for World Cup
        candidates = []
        if type_key == "WORLD_CUP":
            candidates = NATIONAL_TEAMS
        elif type_key == "EURO_CUP":
            candidates = [nt for nt in NATIONAL_TEAMS if nt.get("continent") == "EU"]
        elif type_key == "COPA_AMERICA":
            # Real-world behavior: 10 CONMEBOL teams + 6 CONCACAF guest teams
            sa_teams = [nt for nt in NATIONAL_TEAMS if nt.get("continent") == "SA"]
            na_teams = [nt for nt in NATIONAL_TEAMS if nt.get("continent") == "NA"]
            na_teams.sort(key=lambda x: x.get("target_ovr", 75), reverse=True)
            candidates = sa_teams + na_teams[:6]
        elif type_key == "AFCON":
            candidates = [nt for nt in NATIONAL_TEAMS if nt.get("continent") == "AF"]
        elif type_key == "ASIAN_CUP":
            candidates = [nt for nt in NATIONAL_TEAMS if nt.get("continent") == "AS"]
        elif type_key == "GOLD_CUP":
            candidates = [nt for nt in NATIONAL_TEAMS if nt.get("continent") == "NA"]
        
        if len(candidates) < 4: return  # Minimum 4 teams for a bracket
        
        candidates.sort(key=lambda x: x.get("target_ovr", 75), reverse=True)
        n = len(candidates)
        
        # World Cup: 48 teams (12 groups of 4), others: 16/24 (must be power of 2 for direct brackets)
        if type_key == "WORLD_CUP":
            size = min(n, 48)
        elif type_key == "EURO_CUP":
            size = min(n, 16) if n >= 16 else (8 if n >= 8 else 4)
        elif type_key == "COPA_AMERICA":
            size = min(n, 16) if n >= 16 else (8 if n >= 8 else 4)
        elif n >= 16: size = 16
        elif n >= 8: size = 8
        else: size = 4
        
        qualified = [nt["country_code"] for nt in candidates[:size]]
        random.shuffle(qualified)
        
        # World Cup uses group stage + R32
        if type_key == "WORLD_CUP" and size >= 48:
            # 12 groups of 4
            groups = {}
            for g_idx in range(12):
                g_name = chr(65 + g_idx) if g_idx < 26 else f"G{g_idx}"
                g_teams = qualified[g_idx*4 : g_idx*4+4]
                groups[g_name] = {
                    "teams": g_teams,
                    "standings": {s: {"pts":0,"ph":0,"w":0,"d":0,"l":0,"gf":0,"ga":0} for s in g_teams}
                }
            self.intl_tournaments[type_key] = {
                "name": "Copa del Mundo",
                "format": "WC_GROUPS",
                "groups": groups,
                "round": "GROUPS",
                "bracket": {"R32": [], "R16": [], "QF": [], "SF": [], "FINAL": []},
                "teams": qualified
            }
            # Schedule group matches
            self._schedule_wc_groups(type_key)
            return
        
        # Standard bracket for other tournaments
        if size >= 16:
            bracket_key = "R16"
            bracket = {
                "R16": [{"h": qualified[i], "a": qualified[i+1], "res1": None, "res2": None} for i in range(0, size, 2)],
                "QF": [],
                "SF": [],
                "FINAL": []
            }
        elif size >= 8:
            bracket_key = "QF"
            bracket = {
                "R16": [],
                "QF": [{"h": qualified[i], "a": qualified[i+1], "res1": None, "res2": None} for i in range(0, size, 2)],
                "SF": [],
                "FINAL": []
            }
        else:
            bracket_key = "SF"
            bracket = {
                "R16": [],
                "QF": [],
                "SF": [{"h": qualified[i], "a": qualified[i+1], "res1": None, "res2": None} for i in range(0, size, 2)],
                "FINAL": []
            }
        
        # 4. Prepare Team Data and Rosters for the tournament
        for code in qualified:
            nt_data, nt_roster, _ = build_national_squad(code, self.rosters, self.teams)
            if nt_data:
                self.rosters[nt_data["short"]] = nt_roster
        
        names = {"WORLD_CUP": "Copa del Mundo", "EURO_CUP": "Eurocopa", "COPA_AMERICA": "Copa América", "AFCON": "Copa Africana de Naciones", "ASIAN_CUP": "Copa Asiática", "GOLD_CUP": "Copa de Oro CONCACAF"}
        self.intl_tournaments[type_key] = {
            "name": names.get(type_key, type_key),
            "round": bracket_key,
            "bracket": bracket,
            "teams": qualified
        }
        
        # 5. Schedule first round
        self._schedule_intl_round(type_key, bracket_key)

    def _schedule_wc_groups(self, type_key):
        """Schedule World Cup group stage (3 matchdays per group)."""
        tournament = self.intl_tournaments[type_key]
        all_matchdays = []
        for g_name, g_data in tournament["groups"].items():
            teams = g_data["teams"]
            if len(teams) < 4: continue
            matchups = [
                [(teams[0], teams[1]), (teams[2], teams[3])],
                [(teams[0], teams[2]), (teams[1], teams[3])],
                [(teams[0], teams[3]), (teams[1], teams[2])],
            ]
            for md_idx, md_matches in enumerate(matchups):
                while len(all_matchdays) <= md_idx:
                    all_matchdays.append([])
                for m in md_matches:
                    from data.national_teams import get_national_team
                    h_nt = get_national_team(m[0])
                    a_nt = get_national_team(m[1])
                    if h_nt and a_nt:
                        all_matchdays[md_idx].append((h_nt["short"], a_nt["short"]))
        
        start_date = self.current_date + datetime.timedelta(days=10)
        while start_date.weekday() != 5:
            start_date += datetime.timedelta(days=1)
        for md_matches in all_matchdays:
            d_str = start_date.isoformat()
            self.calendar.setdefault(d_str, []).append({"type": f"INTL_{type_key}", "lg": type_key, "matches": md_matches, "leg": 1})
            start_date += datetime.timedelta(days=4)

    def _advance_wc_groups(self, type_key):
        """After WC group stage, top 2 from each group + 8 best 3rds advance to R32."""
        tournament = self.intl_tournaments[type_key]
        top2 = []
        thirds = []
        for g_name in sorted(tournament["groups"].keys()):
            g = tournament["groups"][g_name]
            st = sorted(g["standings"].items(), key=lambda x: (x[1]["pts"], x[1]["gf"]-x[1]["ga"]), reverse=True)
            top2.extend([s[0] for s in st[:2]])
            if len(st) >= 3:
                thirds.append(st[2])
        # Best 8 third-placed teams
        thirds.sort(key=lambda x: (x[1]["pts"], x[1]["gf"]-x[1]["ga"]), reverse=True)
        best_thirds = [s[0] for s in thirds[:8]]
        all_qualified = top2 + best_thirds  # 24 + 8 = 32
        random.shuffle(all_qualified)
        
        r32 = [{"h": all_qualified[i], "a": all_qualified[i+1], "res1": None, "res2": None} for i in range(0, min(32, len(all_qualified)), 2)]
        tournament["bracket"]["R32"] = r32
        tournament["round"] = "R32"
        self._schedule_intl_round(type_key, "R32")

    def _schedule_intl_round(self, type_key, round_key):
        """Schedules single-leg matches for international tournaments in June/July."""
        tournament = self.intl_tournaments[type_key]
        matches = tournament["bracket"][round_key]
        
        # June 15th approx
        start_date = self.current_date + datetime.timedelta(days=10)
        while start_date.weekday() != 5: # Saturday
            start_date += datetime.timedelta(days=1)
            
        d1 = start_date.isoformat()
        if d1 not in self.calendar: self.calendar[d1] = []
        
        m_list = []
        for m in matches:
            from data.national_teams import get_national_team
            h_nt = get_national_team(m["h"])
            a_nt = get_national_team(m["a"])
            if h_nt and a_nt:
                m_list.append((h_nt["short"], a_nt["short"]))
        
        self.calendar[d1].append({"type": f"INTL_{type_key}", "lg": type_key, "matches": m_list, "leg": 1})

    def _apply_intl_match(self, type_key, t1_short, t2_short, g1, g2):
        """Records a match result for an international tournament."""
        tournament = self.intl_tournaments.get(type_key)
        if not tournament: return
        
        # Handle WC group stage
        if tournament.get("format") == "WC_GROUPS" and tournament["round"] == "GROUPS":
            for g_name, g_data in tournament["groups"].items():
                st = g_data["standings"]
                # Find both teams in this group
                t1_code = None
                t2_code = None
                for code in st.keys():
                    from data.national_teams import get_national_team
                    nt = get_national_team(code)
                    if nt and nt["short"] == t1_short: t1_code = code
                    if nt and nt["short"] == t2_short: t2_code = code
                if t1_code and t2_code:
                    st[t1_code]["ph"] += 1; st[t1_code]["gf"] += g1; st[t1_code]["ga"] += g2
                    st[t2_code]["ph"] += 1; st[t2_code]["gf"] += g2; st[t2_code]["ga"] += g1
                    if g1 > g2:
                        st[t1_code]["pts"] += 3; st[t1_code]["w"] += 1; st[t2_code]["l"] += 1
                    elif g1 == g2:
                        st[t1_code]["pts"] += 1; st[t1_code]["d"] += 1; st[t2_code]["pts"] += 1; st[t2_code]["d"] += 1
                    else:
                        st[t2_code]["pts"] += 3; st[t2_code]["w"] += 1; st[t1_code]["l"] += 1
                    # Check if all groups finished
                    all_done = all(s["ph"] >= 3 for g in tournament["groups"].values() for s in g["standings"].values())
                    if all_done:
                        self._advance_wc_groups(type_key)
                    return
        
        r = tournament["round"]
        matches = tournament["bracket"].get(r, [])
        
        for m in matches:
            from data.national_teams import get_national_team
            h_nt = get_national_team(m["h"])
            a_nt = get_national_team(m["a"])
            if h_nt and a_nt:
                if h_nt["short"] == t1_short and a_nt["short"] == t2_short:
                    m["res1"] = (g1, g2)
                    break

    def _check_intl_progression(self, type_key):
        """Moves winners to the next round of an international tournament."""
        tournament = self.intl_tournaments.get(type_key)
        if not tournament: return
        r = tournament["round"]
        if r == "FINISHED": return
        matches = tournament["bracket"].get(r, [])
        if not matches: return
        
        # Check if all matches in round are finished
        all_finished = True
        for m in matches:
            if m["res1"] is None: 
                all_finished = False
                break
        
        if not all_finished: return
        
        # Determine winners
        winners = []
        for m in matches:
            g1, g2 = m["res1"]
            if g1 > g2:
                winners.append(m["h"])
            elif g2 > g1:
                winners.append(m["a"])
            else:
                # Penalties simulation
                winner = random.choice([m["h"], m["a"]])
                winners.append(winner)
        
        # News for the round finish
        if r == "FINAL":
            if not winners:
                return
            champion_code = winners[0]
            from data.national_teams import COUNTRY_MAP
            champion_name = COUNTRY_MAP.get(champion_code, champion_code)
            self.add_news("INTL", f"¡{champion_name.upper()} CAMPEÓN!", f"Han ganado la {tournament['name']} tras una final épica.", importance=3)
            
            # Awards
            self._generate_cup_awards(type_key) # Reusing the award generator
            
            if self.is_called_up:
                # Check if career player's country won
                if self.career_player.get("nat") == champion_code:
                     self.career_stats.setdefault("titles", []).append(tournament["name"])
                     self.add_email("info", f"¡Campeones de la {tournament['name']}!", "¡Increíble! Tu país ha ganado el torneo. Eres una leyenda nacional.")
                     self._update_prestige(50)
            
            tournament["round"] = "FINISHED"
        else:
            # Move to next round
            next_rounds = {"R32": "R16", "R16": "QF", "QF": "SF", "SF": "FINAL"}
            nr = next_rounds.get(r)
            if not nr: return
            
            tournament["round"] = nr
            
            # 3. Check for Historic Milestones for each winner
            round_vals = {"GROUPS": 0, "R16": 1, "QF": 2, "SF": 3, "FINAL": 4, "TITLE": 5}
            for w_short in winners:
                from data.national_teams import get_national_team
                nt = get_national_team(w_short.replace("_NT", ""))
                if nt and "history" in nt:
                    h_key = "BEST_WC" if type_key == "WORLDCUP" else "BEST_CONT"
                    h_best = nt["history"].get(h_key, "GROUPS")
                    
                    # If current round (nr) is better than historic best
                    if round_vals.get(nr, 0) > round_vals.get(h_best, 0):
                        team_name = nt["name"]
                        r_name = "CUARTOS" if nr == "QF" else ("SEMIFINALES" if nr == "SF" else "la GRAN FINAL")
                        self.add_news("INTL", f"¡{team_name.upper()} HACE HISTORIA!", f"Superan su récord histórico al alcanzar {r_name}. ¡Hazaña total!")
                        
                        # Boost market value for the entire roster due to historic hype
                        self._boost_roster_value(w_short, 0.15)
                        
                        # Extra prestige if player is in this team
                        if self.career_player.get("nat") == w_short.replace("_NT", ""):
                            self._update_prestige(15)

            # Generate next matches: winner Match 1 vs winner Match 2, etc.
            new_matches = []
            for i in range(0, len(winners), 2):
                new_matches.append({"h": winners[i], "a": winners[i+1], "res1": None, "res2": None})
            tournament["bracket"][nr] = new_matches
            
            # Schedule next round (in 4 days)
            self._schedule_intl_round(type_key, nr)

    def start_player_career(self, player_data, league_id, team_short=None):
        """Initializes a career focused on a single player."""
        self.active = True
        self.mode = "player"
        self.manager_name = player_data["name"] # Using name as identifier
        self.year = 1
        
        # Assign to the correct slot range for player mode
        self.current_slot = self._find_first_empty_slot("player")
        self.skill_points = 0
        
        # 1. Expand universe
        base_teams = copy.deepcopy(TEAMS)
        gen_teams, gen_rosters = generate_filler_teams(len(base_teams), base_teams)
        self.teams = base_teams + gen_teams
        
        # 2. Get rosters
        db_rosters = get_base_rosters()
        self.rosters = {}
        for t in self.teams:
            short = t["short"]
            if short in db_rosters:
                self.rosters[short] = copy.deepcopy(db_rosters[short])
            elif short in gen_rosters:
                self.rosters[short] = copy.deepcopy(gen_rosters[short])
            else:
                from data.procedural import generate_roster
                self.rosters[short] = generate_roster(t.get("league", "EN"), 74)
        
        self.ensure_roster_minimums()
        
        # Check for legacy generation skip!
        if getattr(self, "start_year_offset", 0) > 0:
            self._apply_legacy_roster_regeneration()
            
        self.league_id = league_id
        
        # 3. Assign to team
        if not team_short:
            team_short = self._assign_player_to_best_team(player_data, league_id)
        
        self.player_team = self.get_team_by_short(team_short)
        
        # Add player to roster
        player_data["is_user_player"] = True
        self.career_player = copy.deepcopy(player_data)
        self.rosters[team_short].append(self.career_player)
        
        # 4. Dates
        eu_leagues = ["EN", "ES", "IT", "DE", "FR", "PT", "TR", "BE", "RU", "RO", "SC", "AT", "AF"]
        is_eu = self.league_id in eu_leagues
        base_date = datetime.date(2024, 7, 1) if is_eu else datetime.date(2024, 1, 1)
        end_date = datetime.date(2025, 6, 30) if is_eu else datetime.date(2024, 12, 31)
        
        # Apply year skip offset
        offset = getattr(self, "start_year_offset", 0)
        if offset > 0:
            base_date = base_date.replace(year=base_date.year + offset)
            end_date = end_date.replace(year=end_date.year + offset)
            
        self.current_date = base_date
        self.season_start = base_date
        self.season_end = end_date
        self.calendar.clear()
        
        self._init_budgets()
        
        # Standings
        self.leagues = ["EN", "ES", "IT", "DE", "FR", "PT", "TR", "BE", "RU", "RO", "SC", "AT", "BR", "AR", "CO", "CL", "PE", "MX", "US", "JP", "AF"]
        for lg in self.leagues:
            self.standings[lg] = {}
            self.scorers[f"LIGA_{lg}"] = {}
            self.assists[f"LIGA_{lg}"] = {}
            lg_teams = [t for t in self.teams if t.get("league", "EN") == lg]
            for t in lg_teams:
                self.standings[lg][t["short"]] = {"pts":0, "ph":0, "w":0, "d":0, "l":0, "gf":0, "ga":0}
        
        # Full reset of career_stats for a fresh career
        self.career_stats = {
            "matches": 0, "wins": 0, "draws": 0, "losses": 0,
            "goals_scored": 0, "goals_conceded": 0,
            "player_goals": 0, "player_assists": 0,
            "matches_played": 0,
            "titles": [], "teams_managed": [self.player_team["short"]],
            "seasons_completed": 0,
            "coach_confidence": 20,   # Young player starts with low trust
            "teammate_rel": 40,       # New kid, hasn't earned respect yet
            "fan_rel": 30,            # Unknown to the fans
            "board_rel": 50,
            "transfers_in": 0, "transfers_out": 0,
            "total_spent": 0, "total_earned": 0,
            "rating_history": [], "avg_rating": 0.0,
            "prestige": 5,
            "money": 0.0,
            "individual_awards": [],
            "partnerships": {},
            "rivalries": {},
            "is_captain": False,
            "is_nt_captain": False,
            "children": []
        }
        
        # Guardar metadata de legado generacional si corresponde
        is_legacy = getattr(self, "start_year_offset", 0) > 0
        self.career_stats["is_legacy_career"] = is_legacy
        if is_legacy:
            legacy_info = self.check_legacy_match(player_data["name"])
            if legacy_info:
                self.career_stats["player_legacy"] = legacy_info
                
        self.retired = False
        
        # News: First Professional Contract
        p_name = self.career_player["name"]
        ovr = self.career_player["ovr"]
        team_name = self.player_team["name"]
        
        if ovr >= 60:
            expectations = "Las expectativas son máximas; se dice que es un talento generacional que podría debutar de inmediato."
        elif ovr >= 56:
            expectations = "El club confía en que se adapte rápido y sea una pieza importante en la rotación esta temporada."
        else:
            expectations = "Se espera que empiece su desarrollo en el equipo reserva o gane minutos en copas locales."
            
        self.add_news("MERCADO", "PRIMER CONTRATO PROFESIONAL", 
                      f"El joven {p_name} ha firmado hoy su primer vínculo profesional con el {team_name}. {expectations}", 
                      importance=3, expiry_days=15)
        
        # Inicializar Club Libre
        self._init_free_agents_club()
        
        self._generate_schedules()
        self._initialize_objectives()
        
        # 5. Initial Emails
        self.add_email("board", f"Bienvenido a {self.player_team['name']}", 
                       f"Hola {self.manager_name}, estamos encantados de tenerte en el equipo. "
                       "Nuestras expectativas para esta temporada son claras: revisa tus objetivos en la pestaña de Oficina.")
        
        self.add_email("info", "Tu nueva carrera", 
                       "¡Felicidades por tu debut profesional! Recuerda que tu rol en el equipo dependerá de tu rendimiento "
                       "y de la confianza del mánager. ¡Buena suerte!")

        # Contract welcome (player mode): read-only summary in the inbox
        try:
            p_name = self.career_player.get("name", self.manager_name)
            club_name = self.player_team["name"]
            contract_years = int(self.career_player.get("contract_years", 3) or 0)
            role = self.career_player.get("role") or self._get_player_role(self.career_player)

            ann_salary = self.career_player.get("salary", None)
            if ann_salary is None:
                ann_salary = self._calculate_salary(self.career_player)
            weekly_k = round((float(ann_salary) * 1000.0) / 52.0, 1)

            can_renew = contract_years <= 2
            renew_str = "Ya puedes negociar la renovación." if can_renew else f"La negociación se habilita cuando queden 2 años (aprox. en {max(0, contract_years-2)} año(s))."

            self.add_email(
                "contract",
                "Detalles de tu contrato",
                f"Hola {p_name}. Aquí tienes el resumen de tu contrato con el {club_name}: "
                f"- Duración: {contract_years} año(s) restante(s). "
                f"- Rol contractual: {role}. "
                f"- Salario anual: ${float(ann_salary):.2f}M. "
                f"- Salario semanal: ${weekly_k}k. "
                f"{renew_str} "
                f"(Consulta la pestaña 'CONTRATO' cuando quieras.)",
                data={"contract_years": contract_years, "salary_m_year": ann_salary, "role": role}
            )
        except Exception:
            # Never block career start due to optional contract info
            pass
        
        self._ensure_social_media_exists()
        if self.year > 1:
            self._generate_continental()

    def _assign_player_to_best_team(self, player_data, league_id):
        """Logic to automatically assign a new player to a team that needs them."""
        lg_teams = [t for t in self.teams if t.get("league") == league_id]
        if not lg_teams: lg_teams = self.teams[:20] # Fallback
        
        pos = player_data["pos"]
        
        # Scoring teams based on position scarcity and overall level (target mid-low table)
        scores = []
        for t in lg_teams:
            short = t["short"]
            rost = self.rosters.get(short, [])
            pos_count = sum(1 for p in rost if p.get("pos") == pos)
            team_ovr = self.get_team_ovr(short)
            
            # Ideal team: 65-75 OVR, and few players in that position
            score = 100
            score -= abs(team_ovr - 68) * 2 # Penalty for being too strong/weak
            score -= pos_count * 5 # Penalty for having too many players in that position
            
            scores.append((short, score))
            
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[0][0] if scores else lg_teams[0]["short"]

    def _progress_season(self):
        """Handle yearly player growth, declines, retirements, budget changes, and academy progression."""
        # Clear manager offers for the new season
        self.manager_offers = []
        self.manager_applications = []
        
        # Clean up national team rosters to avoid duplicate serialization and double aging
        nt_keys = [k for k in self.rosters.keys() if k.endswith("_NT")]
        for k in nt_keys:
            del self.rosters[k]
        
        # Yearly budget injection
        for t in self.teams:
            if "budget" in t:
                t["budget"] += random.randint(10, 50)
            
        # Player growth
        processed_player_ids = set()
        for short, rost in list(self.rosters.items()):
            if short.endswith("_NT"):
                continue
            for p in rost:
                if id(p) in processed_player_ids:
                    continue
                processed_player_ids.add(id(p))
                try:
                    age = int(p.get("age", 25))
                except (ValueError, TypeError):
                    age = 25
                try:
                    pot = int(p.get("pot", p.get("ovr", 75)))
                except (ValueError, TypeError):
                    pot = 75
                try:
                    ovr = int(p.get("ovr", 75))
                except (ValueError, TypeError):
                    ovr = 75
                
                # Ensure ovr and pot keys exist as ints
                p["age"] = age
                p["pot"] = pot
                p["ovr"] = ovr
                if "s" not in p:
                    p["s"] = {}
                
                age += 1
                p["age"] = age
                
                if age <= 28 and ovr < pot:
                    diff = pot - ovr
                    growth = max(1, diff // 3)
                    p["ovr"] = min(99, ovr + growth)
                    for stat in p.get("s", {}):
                        try:
                            stat_val = int(p["s"][stat])
                        except (ValueError, TypeError):
                            stat_val = 70
                        p["s"][stat] = min(99, stat_val + growth)
                elif age >= 33:
                    decline = random.randint(1, 3)
                    p["ovr"] = max(40, ovr - decline)
                    if "speed" in p.get("s", {}):
                        try:
                            speed_val = int(p["s"]["speed"])
                        except (ValueError, TypeError):
                            speed_val = 70
                        p["s"]["speed"] = max(1, speed_val - decline - 1)
                    
            # Retirements
            self.rosters[short] = [
                p for p in rost 
                if not (int(p.get("age", 25)) > 34 and random.random() < 0.3)
            ]
            
            # Spawn Academy
            t_obj = self.get_team_by_short(short)
            if t_obj:
                ya = t_obj.get("youth_academy", [])
                # Age up ya
                for y in ya: 
                    try:
                        y["age"] = int(y.get("age", 15)) + 1
                    except (ValueError, TypeError):
                        y["age"] = 15
                ya = [y for y in ya if int(y.get("age", 15)) <= 18] # Removed if too old
                
                # new spawn
                if len(ya) < 5:
                    gen_pot = random.randint(70, 94)
                    ya.append({
                        "name": f"J. Promesa {random.randint(100,999)}",
                        "pos": random.choice(["CB", "CM", "ST", "GK"]),
                        "age": random.randint(13, 15),
                        "pot": gen_pot,
                        "ovr": gen_pot - random.randint(15, 25),
                        "num": random.randint(50, 99),
                        "s": {"speed": 60, "shot": 60, "passing": 60, "defense": 60, "gk": 10}
                    })
                t_obj["youth_academy"] = ya
                
        # Process player contract decrement (aging is already done in the main roster loop)
        if self.mode == "player" and self.career_player:
            cy = self.career_player.get("contract_years", 3)
            self.career_player["contract_years"] = max(0, cy - 1)

    def get_save_path(self, slot_id):
        import os
        return os.path.join(self.save_dir, f"career_save_{slot_id}.json")

    def has_any_save(self):
        import os, json
        if not os.path.exists(self.manifest_file): return False
        try:
            with open(self.manifest_file, "r") as f:
                data = json.load(f)
                return any(data.values())
        except: return False

    def get_slots_metadata(self):
        import os, json
        slots = {i: None for i in range(1, 21)}
        if os.path.exists(self.manifest_file):
            try:
                with open(self.manifest_file, "r", encoding="utf-8") as f:
                    m = json.load(f)
                    for k, v in m.items():
                        if int(k) in slots:
                            # Robust verification: check if file actually exists
                            if v and os.path.exists(self.get_save_path(int(k))):
                                slots[int(k)] = v
                            else:
                                slots[int(k)] = None
            except: pass
        return slots

    def check_legacy_match(self, entered_name):
        """
        Checks if there is any existing save with a matching surname.
        Returns a dict with details about the matching save if found, else None.
        """
        if not entered_name: return None
        
        # Extract surname (last word)
        words = entered_name.strip().split()
        if not words: return None
        surname = words[-1].lower()
        
        # Ignore extremely short surnames (e.g. less than 3 letters) to avoid false positives
        if len(surname) < 3: return None
        
        slots = self.get_slots_metadata()
        for slot_id, meta in slots.items():
            if meta and meta.get("name"):
                import os
                if not os.path.exists(self.get_save_path(slot_id)):
                    continue
                m_words = meta["name"].strip().split()
                if m_words:
                    m_surname = m_words[-1].lower()
                    if m_surname == surname:
                        # Found a match! Let's return details
                        save_pos = None
                        save_league = None
                        
                        import json
                        save_path = self.get_save_path(slot_id)
                        try:
                            with open(save_path, "r", encoding="utf-8") as f:
                                data = json.load(f)
                                save_league = data.get("league_id")
                                if data.get("mode") == "player" and data.get("career_player"):
                                    save_pos = data["career_player"].get("pos")
                        except: pass
                        
                        return {
                            "slot_id": slot_id,
                            "name": meta["name"],
                            "team": meta["team"],
                            "year": meta.get("year", 1) + 2024 - 1, # Approximate calendar year
                            "mode": meta.get("mode", "manager"),
                            "pos": save_pos,
                            "league": save_league
                        }
        return None

    def _apply_legacy_roster_regeneration(self):
        """Regenerates all players in all rosters to represent the new generation in the legacy year-skip."""
        from data.procedural import generate_player
        import random
        
        for short, roster in list(self.rosters.items()):
            t_obj = self.get_team_by_short(short)
            lg = t_obj.get("league", "EN") if t_obj else "EN"
            
            new_roster = []
            num_pool = list(range(1, 99))
            random.shuffle(num_pool)
            
            for p in roster:
                if p.get("is_user_player"):
                    new_roster.append(p)
                    if p.get("num") in num_pool:
                        num_pool.remove(p["num"])
                    continue
                
                new_p = generate_player(lg, p["pos"], p["ovr"])
                new_p["num"] = num_pool.pop() if num_pool else random.randint(1, 99)
                new_roster.append(new_p)
                
            self.rosters[short] = new_roster

    def load_config(self):
        import os, json
        config_path = os.path.join(self.save_dir, "config.json")
        self.autosave_enabled = True
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    c = json.load(f)
                    self.autosave_enabled = c.get("autosave", True)
            except: pass

    def save_config(self):
        import os, json
        os.makedirs(self.save_dir, exist_ok=True)
        config_path = os.path.join(self.save_dir, "config.json")
        try:
            with open(config_path, "w") as f:
                json.dump({"autosave": getattr(self, 'autosave_enabled', True)}, f)
        except: pass

    def _update_manifest(self, slot_id, career_data):
        import os, json
        os.makedirs(self.save_dir, exist_ok=True)
        slots = self.get_slots_metadata()
        
        # Extract lightweight metadata
        d = career_data["current_date"]
        # Convert iso string back to a readable date or just keep string
        slots[slot_id] = {
            "name": career_data["manager_name"],
            "team": career_data["player_team"]["name"],
            "team_short": career_data["player_team"]["short"],
            "date": d,
            "year": career_data["year"],
            "mode": career_data["mode"]
        }
        
        with open(self.manifest_file, "w", encoding="utf-8") as f:
            json.dump(slots, f, ensure_ascii=False, indent=2)

    def has_save(self):
        # Compatibility override or global check
        return self.has_any_save()
        
    def get_save_data(self):
        """Devuelve un diccionario con todos los datos de la partida actual."""
        return {
            "manager_name": self.manager_name,
            "year": self.year,
            "current_date": self.current_date.isoformat() if self.current_date else None,
            "season_start": self.season_start.isoformat() if self.season_start else None,
            "season_end": self.season_end.isoformat() if self.season_end else None,
            "league_id": self.league_id,
            "player_team": self.player_team,
            "teams": self.teams,
            "rosters": self.rosters,
            "calendar": self.calendar,
            "standings": self.standings,
            "scorers": self.scorers,
            "assists": self.assists,
            "continental": self.continental,
            "scouted_players": self.scouted_players,
            "negotiations": self.negotiations,
            "career_stats": self.career_stats,
            "news": self.news,
            "inbox": self.inbox,
            "manager_offers": self.manager_offers,
            "manager_applications": self.manager_applications,
            "managing_nt": self.managing_nt,
            "is_called_up": self.is_called_up,
            "nt_stats": self.nt_stats,
            "_final_standings": self._final_standings,
            "mode": self.mode,
            "career_player": self.career_player,
            "skill_points": self.skill_points,
            "objectives": self.objectives,
            "agent": self.agent,
            "agent_suggestions": self.agent_suggestions,
            "agent_recommendations": self.agent_recommendations,
            "difficulty": getattr(self, "difficulty", 5)
        }

    def load_from_data(self, data):
        """Carga el estado de la partida desde un diccionario de datos."""
        import datetime
        self.active = True
        self.manager_name = data["manager_name"]
        self.year = data["year"]
        self.current_date = datetime.date.fromisoformat(data["current_date"]) if data["current_date"] else None
        self.season_start = datetime.date.fromisoformat(data["season_start"]) if data["season_start"] else None
        self.season_end = datetime.date.fromisoformat(data["season_end"]) if data["season_end"] else None
        self.league_id = data["league_id"]
        self.player_team = data["player_team"]
        self.teams = data["teams"]
        self.rosters = data["rosters"]
        self.calendar = data["calendar"]
        self.standings = data["standings"]
        self.scorers = data["scorers"]
        self.assists = data["assists"]
        self.continental = data["continental"]
        self.scouted_players = data["scouted_players"]
        self.negotiations = data["negotiations"]
        self.career_stats = data["career_stats"]
        self.news = data["news"]
        self.inbox = data["inbox"]
        self.manager_offers = data["manager_offers"]
        self.manager_applications = data["manager_applications"]
        self.managing_nt = data["managing_nt"]
        self.is_called_up = data["is_called_up"]
        self.nt_stats = data["nt_stats"]
        self._final_standings = data["_final_standings"]
        self.mode = data["mode"]
        self.career_player = data["career_player"]
        self.skill_points = data.get("skill_points", 0)
        self.objectives = data.get("objectives", [])
        self.agent = data.get("agent", {"name": "Ninguno", "level": 0, "commission": 0.0})
        self.agent_suggestions = data.get("agent_suggestions", [])
        self.agent_recommendations = data.get("agent_recommendations", [])
        self.difficulty = data.get("difficulty", 5)
        self._ensure_social_media_exists()
        self._align_career_player_reference()
        return True

    def _align_career_player_reference(self):
        """Aligns self.career_player to point to the exact same dictionary inside self.rosters."""
        if self.mode == "player" and self.player_team and self.career_player:
            team_short = self.player_team["short"]
            if team_short in self.rosters:
                real_p = next((p for p in self.rosters[team_short] if p.get("is_user_player") or p.get("name", "").lower().strip() == self.career_player.get("name", "").lower().strip()), None)
                if real_p:
                    # Update is_user_player flag just in case
                    real_p["is_user_player"] = True
                    self.career_player = real_p

    def delete_career(self, slot_id):
        import os, json
        path = self.get_save_path(slot_id)
        file_deleted = False
        if os.path.exists(path):
            try:
                os.remove(path)
                file_deleted = True
            except:
                pass
        
        # Ensure manifest file exists and clean up entry
        m = {str(i): None for i in range(1, 21)}
        if os.path.exists(self.manifest_file):
            try:
                with open(self.manifest_file, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    for k, v in loaded.items():
                        m[k] = v
            except:
                pass
        
        m[str(slot_id)] = None
        try:
            with open(self.manifest_file, "w", encoding="utf-8") as f:
                json.dump(m, f, ensure_ascii=False, indent=2)
        except:
            pass
                
        return file_deleted

    def save_career(self, slot_id=None):
        if slot_id is None: slot_id = self.current_slot
        self.current_slot = slot_id
        import os, json
        os.makedirs(self.save_dir, exist_ok=True)
        data = self.get_save_data()
        save_path = self.get_save_path(slot_id)
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            
        self._update_manifest(slot_id, data)

    def load_career(self, slot_id=1):
        self.current_slot = slot_id
        import os, json
        save_path = self.get_save_path(slot_id)
        if not os.path.exists(save_path): return False
        
        try:
            with open(save_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            self.manager_name = data["manager_name"]
            self.year = data["year"]
            
            # Dates
            if data.get("current_date"): self.current_date = datetime.date.fromisoformat(data["current_date"])
            if data.get("season_start"): self.season_start = datetime.date.fromisoformat(data["season_start"])
            if data.get("season_end"): self.season_end = datetime.date.fromisoformat(data["season_end"])
            
            self.league_id = data["league_id"]
            self.player_team = data["player_team"]
            self.teams = data["teams"]
            self.rosters = data["rosters"]
            
            if "calendar" in data:
                self.calendar = data["calendar"]
            elif "schedule" in data:
                # Migrate older save if somehow reached here, very complex, we just fail it gracefully. 
                pass # Already dropped compat
                
            self.standings = data["standings"]
            self.scorers = data["scorers"]
            self.assists = data["assists"]
            self.continental = data.get("continental", {})
            self.scouted_players = data.get("scouted_players", [])
            self.negotiations = data.get("negotiations", [])
            self.career_stats = data.get("career_stats", self.career_stats)
            # Migration: Ensure coach confidence exists
            if "coach_confidence" not in self.career_stats:
                self.career_stats["coach_confidence"] = 40
                
            # Migration: individual stats
            if "player_goals" not in self.career_stats: self.career_stats["player_goals"] = 0
            if "player_assists" not in self.career_stats: self.career_stats["player_assists"] = 0
            self.news = data.get("news", [])
            self.inbox = data.get("inbox", [])
            self.manager_offers = data.get("manager_offers", [])
            self.manager_applications = data.get("manager_applications", [])
            self.managing_nt = data.get("managing_nt")
            self.is_called_up = data.get("is_called_up", False)
            self.nt_stats = data.get("nt_stats", {"matches": 0, "goals": 0})
            self._final_standings = data.get("_final_standings", {})
            self.mode = data.get("mode", "manager")
            self.career_player = data.get("career_player")
            self.skill_points = data.get("skill_points", 0)
            self._ensure_social_media_exists()
            
            # Retroactively calculate missing 'ovr' for older saves
            from data.rosters import calculate_ovr
            # Add transfer/loan status
            for short, rost in self.rosters.items():
                for p in rost:
                    if "transfer_listed" not in p: p["transfer_listed"] = False
                    if "loan_listed" not in p: p["loan_listed"] = False
                    if "ovr" not in p:
                        p["ovr"] = calculate_ovr(p)
            self.leagues = ["EN", "ES", "IT", "DE", "FR", "PT", "TR", "BE", "RU", "RO", "SC", "AT", "BR", "AR", "CO", "CL", "PE", "MX", "US", "JP", "AF"]
            
            # Migration: Ensure standings exist for all leagues (older saves may be missing some)
            for lg in self.leagues:
                if lg not in self.standings:
                    self.standings[lg] = {}
                    lg_teams = [t for t in self.teams if t.get("league", "EN") == lg]
                    for t in lg_teams:
                        self.standings[lg][t["short"]] = {"pts":0, "ph":0, "w":0, "d":0, "l":0, "gf":0, "ga":0}
                if f"LIGA_{lg}" not in self.scorers:
                    self.scorers[f"LIGA_{lg}"] = {}
                if f"LIGA_{lg}" not in self.assists:
                    self.assists[f"LIGA_{lg}"] = {}
            
            # Migration: Fix slot assignment for legacy saves in the wrong range
            old_slot = self.current_slot
            if self.mode == "player" and self.current_slot < 11:
                self.current_slot = self._find_first_empty_slot("player")
            elif self.mode == "manager" and self.current_slot > 10:
                self.current_slot = self._find_first_empty_slot("manager")
            
            if self.current_slot != old_slot:
                self.save_career(self.current_slot)
                old_save_path = self.get_save_path(old_slot)
                if os.path.exists(old_save_path):
                    try:
                        os.remove(old_save_path)
                    except: pass
                if os.path.exists(self.manifest_file):
                    try:
                        with open(self.manifest_file, "r", encoding="utf-8") as f:
                            slots = json.load(f)
                        slots[str(old_slot)] = None
                        with open(self.manifest_file, "w", encoding="utf-8") as f:
                            json.dump(slots, f, ensure_ascii=False, indent=2)
                    except: pass
            
            self.active = True
            self.ensure_roster_minimums()
            self._align_career_player_reference()
            return True
        except:
            return False
    def _generate_national_cups(self):
        """Initializes National Cups for all leagues with 16 teams."""
        cup_titles = {
            "EN": "FA Cup", "ES": "Copa del Rey", "IT": "Coppa Italia",
            "DE": "DFB Pokal", "FR": "Coupe de France", "PT": "Taça de Portugal", "TR": "Türkiye Kupası", "TR": "Türkiye Kupası",
            "BE": "Croky Cup", "RU": "Copa de Rusia", "RO": "Copa de Rumanía", "SC": "Copa de Escocia", "AT": "Copa de Austria",
            "BR": "Copa do Brasil", "AR": "Copa Argentina", "CO": "Copa Colombia", "CL": "Copa de Chile", "PE": "Copa de Perú", "MX": "Copa MX",
            "US": "US Open Cup", "JP": "Emperor's Cup", "AF": "Copa de África"
        }
        
        for lg in self.leagues:
            lg_teams = [t["short"] for t in self.teams if t.get("league", "EN") == lg]
            
            # Qualify top 16
            if self.year == 1 or not self._final_standings.get(lg):
                lg_teams.sort(key=lambda s: self.get_team_ovr(s), reverse=True)
            else:
                st = list(self._final_standings.get(lg, {}).items())
                st.sort(key=lambda x: (x[1]["pts"], x[1]["gf"]-x[1]["ga"]), reverse=True)
                lg_teams = [s[0] for s in st[:16]]
            
            qualified = lg_teams[:16]
            if len(qualified) >= 8 and len(qualified) < 16:
                qualified = qualified[:8]
            size = len(qualified)
            if size < 8: continue
            
            # Bracket of 16 (Octavos) or 8 (Cuartos)
            random.shuffle(qualified)
            bracket_key = "R16" if size >= 16 else "QF"
            bracket = {
                "R16": [{"h": qualified[i], "a": qualified[i+1], "res1": None, "res2": None} for i in range(0, size, 2)] if size >= 16 else [],
                "QF": [{"h": qualified[i], "a": qualified[i+1], "res1": None, "res2": None} for i in range(0, size, 2)] if size == 8 else [],
                "SF": [],
                "FINAL": []
            }
            
            self.national_cups[lg] = {
                "name": cup_titles.get(lg, f"Copa {lg}"),
                "round": bracket_key,
                "bracket": bracket
            }
            
            self._schedule_cup_round(lg, bracket_key)

    def _schedule_cup_round(self, lg, round_key):
        """Schedules ida/vuelta or final for a cup round on Tuesdays."""
        cup = self.national_cups[lg]
        matches = cup["bracket"][round_key]
        
        # Find next available Tuesdays
        current_dt = self.current_date + datetime.timedelta(days=21)
        while current_dt.weekday() != 1: # Tuesday
            current_dt += datetime.timedelta(days=1)
        
        # 1st Leg
        d1 = current_dt.isoformat()
        if d1 not in self.calendar: self.calendar[d1] = []
        m_list1 = [(m["h"], m["a"]) for m in matches]
        self.calendar[d1].append({"type": f"COPA_{lg}", "lg": lg, "matches": m_list1, "leg": 1})
        
        if round_key != "FINAL":
            # 2nd Leg (14 days later)
            current_dt += datetime.timedelta(days=14)
            d2 = current_dt.isoformat()
            if d2 not in self.calendar: self.calendar[d2] = []
            m_list2 = [(m["a"], m["h"]) for m in matches]
            self.calendar[d2].append({"type": f"COPA_{lg}", "lg": lg, "matches": m_list2, "leg": 2})

    def _apply_cup_match(self, lg, t1, t2, g1, g2):
        """Records a cup match result."""
        cup = self.national_cups.get(lg)
        if not cup: return
        r = cup["round"]
        matches = cup["bracket"].get(r, [])
        
        for m in matches:
            if m["h"] == t1 and m["a"] == t2:
                m["res1"] = (g1, g2)
                break
            elif m["h"] == t2 and m["a"] == t1:
                m["res2"] = (g2, g1)
                break

    def _check_league_progression(self, lg):
        """Placeholder for league-specific logic (e.g. clinching titles early)."""
        pass

    def _check_continental_progression(self, comp_name):
        """Moves winners of continental matches to the next phase if groups/rounds are finished."""
        comp = self.continental.get(comp_name)
        if not comp: return
        
        phase = comp["phase"]
        if phase in ("FINISHED", "LEAGUE"): return
        
        # Legacy self-healing: if phase is "KNOCKOUT", dynamically find the actual active bracket round
        if phase == "KNOCKOUT":
            for r in ["R16", "QF", "SF", "FINAL"]:
                matches = comp["bracket"].get(r, [])
                if matches:
                    any_unfinished = False
                    for m in matches:
                        if r == "FINAL":
                            if m["res1"] is None: any_unfinished = True; break
                        else:
                            if m["res1"] is None or m["res2"] is None: any_unfinished = True; break
                    if any_unfinished:
                        phase = r
                        comp["phase"] = r
                        break
            if comp["phase"] == "KNOCKOUT":
                for r in ["R16", "QF", "SF", "FINAL"]:
                    if comp["bracket"].get(r):
                        phase = r
                        comp["phase"] = r
                if comp["phase"] == "KNOCKOUT":
                    phase = "R16"
                    comp["phase"] = "R16"

        if phase == "GROUPS":
            # Check if all 6 matches are played for all teams
            all_done = True
            for g in comp["groups"].values():
                for s in g["standings"].values():
                    if s["ph"] < 6: all_done = False; break
            if all_done:
                self._advance_continental_phase(comp_name)
        else:
            # Knockout logic (similar to cup)
            matches = comp["bracket"].get(phase, [])
            all_finished = True
            for m in matches:
                if phase == "FINAL":
                    if m["res1"] is None: all_finished = False; break
                else:
                    if m["res1"] is None or m["res2"] is None: all_finished = False; break
            if all_finished:
                self._advance_continental_phase(comp_name)

    def _advance_continental_phase(self, comp_name):
        """Advances continental competition to the next stage (Groups -> QF -> SF -> Final -> Finished)."""
        comp = self.continental.get(comp_name)
        if not comp: return
        
        phase = comp["phase"]
        if phase == "GROUPS":
            self._advance_continental_knockout(comp_name)
        else:
            matches = comp["bracket"].get(phase, [])
            winners = []
            for m in matches:
                # Home/Away aggregate score
                h_goals = m["res1"][0] + m["res2"][0] if phase != "FINAL" else m["res1"][0]
                a_goals = m["res1"][1] + m["res2"][1] if phase != "FINAL" else m["res1"][1]
                
                if h_goals > a_goals: winners.append(m["h"])
                elif a_goals > h_goals: winners.append(m["a"])
                else: winners.append(random.choice([m["h"], m["a"]])) # Simplified penalties
            
            # Guard against empty winners (e.g. empty or legacy corrupted bracket)
            if not winners:
                return

            next_phases = {"R16": "QF", "QF": "SF", "SF": "FINAL", "FINAL": "FINISHED"}
            np = next_phases.get(phase, "FINISHED")
            comp["phase"] = np
            
            # Check for historical milestone for all winners
            for winner in winners:
                self._check_club_historical_milestone(winner, comp_name, np)
            
            if np == "FINISHED":
                # Champion!
                champion = winners[0]
                team_name = self.get_team_by_short(champion)["name"]
                self.add_news("global", f"¡{team_name} CAMPEÓN CONTINENTAL!", f"Se ha coronado ganando la {comp_name}.")
                if champion == self.player_team["short"]:
                    self.career_stats["titles"].append(comp_name)
                    self.add_email("info", "Gloria Continental", f"¡Impresionante! Eres el nuevo rey del continente con el {team_name}. La prensa mundial habla de vosotros.")
                
                # Continental Awards
                self._generate_cup_awards(comp_name)
            else:
                # Pair winners for next stage
                new_matches = []
                for i in range(0, len(winners), 2):
                    if i + 1 < len(winners):
                        new_matches.append({"h": winners[i], "a": winners[i+1], "res1": None, "res2": None})
                comp["bracket"][np] = new_matches
                # Schedule (reuse schedule logic)
                self._schedule_continental_round(comp_name, np)

    def _schedule_continental_round(self, comp_name, phase):
        """Schedules continental knockout matches."""
        comp = self.continental.get(comp_name)
        matches = comp["bracket"].get(phase, [])
        # Find next 2 open Wednesdays
        d = self.current_date + datetime.timedelta(days=7)
        scheduled = 0
        while scheduled < 2:
            if d.weekday() == 2: # Wednesday
                d_str = d.isoformat()
                if scheduled == 0 or phase == "FINAL":
                    m_list = [(m["h"], m["a"]) for m in matches]
                else:
                    m_list = [(m["a"], m["h"]) for m in matches]
                
                self.calendar.setdefault(d_str, []).append({
                    "type": comp_name,
                    "lg": comp_name,
                    "matches": m_list,
                    "leg": 1 if (scheduled == 0 or phase == "FINAL") else 2
                })
                scheduled += 1
                if phase == "FINAL": break # Final is single match
            d += datetime.timedelta(days=1)


    def _check_cup_progression(self, lg):
        """Moves winners to the next round of the cup."""
        cup = self.national_cups.get(lg)
        if not cup: return
        r = cup["round"]
        if r == "FINISHED": return
        matches = cup["bracket"].get(r, [])
        if not matches: return
        
        # Check if all matches in round are finished
        all_finished = True
        for m in matches:
            if r == "FINAL":
                if m["res1"] is None: all_finished = False; break
            else:
                if m["res1"] is None or m["res2"] is None: all_finished = False; break
        
        if not all_finished: return
        
        # Determine winners
        winners = []
        for m in matches:
            if r == "FINAL":
                g1, g2 = m["res1"]
                if g1 > g2: winners.append(m["h"])
                else: winners.append(m["a"])
                
                # Global news for the champion
                team_name = self.get_team_by_short(winners[-1])["name"]
                self.add_news("global", f"¡{team_name} CAMPEÓN!", f"Se ha coronado ganando la {cup['name']}.")
                if winners[-1] == self.player_team["short"]:
                    self.career_stats["titles"].append(cup["name"])
                    self.add_email("info", "Felicidades: Campeón de Copa", f"¡Increíble logro! Has ganado la {cup['name']}. La directiva está eufórica.")
                
                # Individual Awards
                self._generate_cup_awards(lg)
            else:
                h_goals = m["res1"][0] + m["res2"][0]
                a_goals = m["res1"][1] + m["res2"][1]
                if h_goals > a_goals: winners.append(m["h"])
                elif a_goals > h_goals: winners.append(m["a"])
                else: # Tie-breaker (simple random/penalties simulation)
                    winners.append(random.choice([m["h"], m["a"]]))
        
        # Move to next round
        next_rounds = {"R16": "QF", "QF": "SF", "SF": "FINAL", "FINAL": "FINISHED"}
        nr = next_rounds[r]
        cup["round"] = nr
        
        # Check for historical milestones for all winners
        for winner in winners:
            self._check_club_historical_milestone(winner, cup["name"], nr)
        
        if nr != "FINISHED":
            # Generate next matches: winner Match 1 vs winner Match 2, etc.
            new_matches = []
            for i in range(0, len(winners), 2):
                new_matches.append({"h": winners[i], "a": winners[i+1], "res1": None, "res2": None})
            cup["bracket"][nr] = new_matches
            self._schedule_cup_round(lg, nr)
    
    def _generate_cup_awards(self, lg):
        """Calculates and announces individual awards for a finished cup/intl tournament."""
        cup = self.national_cups.get(lg) or self.intl_tournaments.get(lg)
        if not cup: return
        stat_key = f"COPA_{lg}" if lg in self.national_cups else f"INTL_{lg}"
        
        # 1. Top Scorer
        scorers = self.scorers.get(stat_key, {})
        top_sc = sorted(scorers.items(), key=lambda x: x[1], reverse=True)
        scorer_name = top_sc[0][0] if top_sc else "N/A"
        scorer_val = top_sc[0][1] if top_sc else 0
        
        # 2. Top Assister
        assists = self.assists.get(stat_key, {})
        top_as = sorted(assists.items(), key=lambda x: x[1], reverse=True)
        assister_name = top_as[0][0] if top_as else "N/A"
        assister_val = top_as[0][1] if top_as else 0
        
        # 3. MVP & XI Ideal & Best GK
        perfs = self.cup_performers.get(stat_key, [])
        avg_perfs = {} # {name: [ratings, team, pos]}
        for p in perfs:
            if p["name"] not in avg_perfs:
                avg_perfs[p["name"]] = [[], p["team"], p.get("pos", "CM")]
            avg_perfs[p["name"]][0].append(p["rating"])
            
        rankings = []
        for name, data in avg_perfs.items():
            avg = sum(data[0]) / len(data[0])
            rankings.append({"name": name, "team": data[1], "pos": data[2], "avg": avg, "matches": len(data[0])})
        
        # Filter minimum matches (e.g. at least 2 for a short tournament)
        rankings = [r for r in rankings if r["matches"] >= 2]
        rankings.sort(key=lambda x: x["avg"], reverse=True)
        
        mvp = rankings[0] if rankings else {"name": "N/A", "avg": 0, "team": ""}
        
        # Best GK
        gks = [r for r in rankings if r["pos"] == "GK"]
        best_gk = gks[0] if gks else {"name": "N/A", "avg": 0, "team": ""}
        
        # XI Ideal (Simplified: top 11)
        xi = rankings[:11]
        xi_names = ", ".join([p["name"] for p in xi[:3]]) + "..."
        
        # News and Awards
        title = f"PREMIOS: {cup['name']}"
        desc = (f"MVP: {mvp['name']} ({mvp['team']}) - {mvp['avg']:.2f}\n"
                f"Goleador: {scorer_name} ({scorer_val} goles)\n"
                f"Asistente: {assister_name} ({assister_val} asistencias)\n"
                f"Guante de Oro: {best_gk['name']}")
        
        self.add_news("LOCAL", title, desc, importance=2)
        
        # Email if player won something
        if self.mode == "player":
            p_name = self.career_player["name"]
            won = []
            if scorer_name == p_name: won.append("Máximo Goleador")
            if assister_name == p_name: won.append("Máximo Asistente")
            if mvp["name"] == p_name: won.append("MVP del Torneo")
            if best_gk["name"] == p_name: won.append("Mejor Portero")
            if p_name in [p["name"] for p in xi]: won.append("XI Ideal")
            
            if won:
                awards_str = ", ".join(won)
                self.career_stats.setdefault("individual_awards", []).append(f"{awards_str} - {cup['name']}")
                self.add_email("info", "¡Premios Individuales!", f"Has ganado los siguientes reconocimientos en la {cup['name']}: {awards_str}. ¡Tu valor en el mercado ha subido!")
                self._update_prestige(10)
        
        # Clean up for next season cup
        if stat_key in self.cup_performers: del self.cup_performers[stat_key]
        if stat_key in self.scorers: self.scorers[stat_key] = {}
        if stat_key in self.assists: self.assists[stat_key] = {}


    def _initialize_objectives(self):
        """Generates seasonal objectives based on team strength and mode."""
        self.season_start_stats = {
            "wins": self.career_stats.get("wins", 0),
            "matches": self.career_stats.get("matches", 0),
            "matches_played": self.career_stats.get("matches_played", 0),
            "player_goals": self.career_stats.get("player_goals", 0),
            "player_assists": self.career_stats.get("player_assists", 0)
        }
        self.objectives = []
        short = self.player_team["short"]
        ovr = self.get_team_ovr(short)
        
        if self.mode == "manager":
            # 1. League Position
            target_pos = 1 if ovr > 84 else (4 if ovr > 78 else 10)
            self.objectives.append({
                "desc": f"Terminar en el Top {target_pos} de la liga",
                "type": "team_pos", "target": target_pos, "current": 20, "status": "pending"
            })
            # 2. Results
            self.objectives.append({
                "desc": "Ganar al menos 15 partidos oficiales",
                "type": "wins", "target": 15, "current": 0, "status": "pending"
            })
            # 3. Confidence
            self.objectives.append({
                "desc": "Mantener confianza del DT sobre 60",
                "type": "coach_confidence", "target": 60, "current": 40, "status": "pending"
            })
        else:
            # Player Mode
            self.objectives.append({
                "desc": "Jugar al menos 12 partidos",
                "type": "matches", "target": 12, "current": 0, "status": "pending"
            })
            target_g = 8 if ovr > 75 else 4
            self.objectives.append({
                "desc": f"Marcar {target_g} goles en la temporada",
                "type": "player_goals", "target": target_g, "current": 0, "status": "pending"
            })
            self.objectives.append({
                "desc": "Valoración media de al menos 7.0",
                "type": "avg_rating", "target": 7.0, "current": 0.0, "status": "pending"
            })

    def _update_objectives_progress(self):
        """Synchronizes objective 'current' values with actual career stats."""
        base = getattr(self, 'season_start_stats', {})
        for obj in self.objectives:
            t = obj["type"]
            if t == "team_pos":
                # Find current standing
                st = list(self.standings.get(self.league_id, {}).items())
                st.sort(key=lambda x: (x[1]["pts"], x[1]["gf"]-x[1]["ga"]), reverse=True)
                for i, (short, _) in enumerate(st):
                    if short == self.player_team["short"]:
                        obj["current"] = i + 1
                        break
            elif t == "wins":
                obj["current"] = self.career_stats["wins"] - base.get("wins", 0)
            elif t == "matches":
                actual_val = self.career_stats.get("matches_played", 0) if self.mode == "player" else self.career_stats["matches"]
                base_val = base.get("matches_played", 0) if self.mode == "player" else base.get("matches", 0)
                obj["current"] = actual_val - base_val
            elif t == "player_goals":
                obj["current"] = self.career_stats["player_goals"] - base.get("player_goals", 0)
            elif t == "player_assists":
                obj["current"] = self.career_stats["player_assists"] - base.get("player_assists", 0)
            elif t == "coach_confidence":
                obj["current"] = self.career_stats["coach_confidence"]
            elif t == "avg_rating":
                obj["current"] = self.career_stats["avg_rating"]
            
            # Update status
            if t == "team_pos":
                if obj["current"] <= obj["target"]: obj["status"] = "on_track"
                else: obj["status"] = "behind"
            else:
                if obj["current"] >= obj["target"]: obj["status"] = "completed"

    def ensure_roster_minimums(self):
        """Ensures every team has at least 18 players to avoid MatchScene crashes."""
        from data.procedural import generate_player
        for t in self.teams:
            short = t["short"]
            if short == "LIB": continue
            rost = self.rosters.get(short, [])
            if len(rost) < 18:
                lg = t.get("league", "EN")
                ovr = int(t.get("stats", {}).get("speed", 72))
                used_nums = [p.get("num") for p in rost if "num" in p]
                num_pool = [n for n in range(1, 99) if n not in used_nums]
                import random
                random.shuffle(num_pool)
                
                needed = 18 - len(rost)
                # Ensure at least one GK if missing
                has_gk = any(p.get("pos") == "GK" for p in rost)
                
                for i in range(needed):
                    pos = "GK" if (not has_gk and i == 0) else random.choice(["CB", "LB", "RB", "CM", "ST", "LW", "RW"])
                    if pos == "GK": has_gk = True
                    p = generate_player(lg, pos, ovr)
                    p["num"] = num_pool.pop() if num_pool else random.randint(1, 99)
                    rost.append(p)
                self.rosters[short] = rost

    def _init_free_agents_club(self):
        """Crea el club virtual 'Libre' para jugadores paródicos."""
        lib_team = {
            "name": "Agentes Libres",
            "short": "LIB",
            "primary": (100, 100, 100),
            "secondary": (50, 50, 50),
            "accent": (200, 200, 200),
            "league": "LIB", # Liga especial
            "stats": {"speed": 75, "shot": 75, "defense": 75, "passing": 75},
            "badge_shape": "circle",
            "is_playable": False
        }
        if not any(t["short"] == "LIB" for t in self.teams):
            self.teams.append(lib_team)
        self.rosters["LIB"] = []
        
    def add_to_free_agents(self, player):
        """Añade un jugador al club de agentes libres si no está ya."""
        if "LIB" not in self.rosters:
            self._init_free_agents_club()
        
        if not any(p["name"] == player["name"] for p in self.rosters["LIB"]):
            self.rosters["LIB"].append(player)
            # Asegurarse de que el jugador sepa que es libre
            player["team_short"] = "LIB"
            player["is_free_agent"] = True
    def _get_top_teams_shorts(self, lg_id, count=3):
        """Obtiene los shorts de los mejores N equipos de una liga según la tabla."""
        table = self.standings.get(lg_id, {})
        if not table: return []
        sorted_teams = sorted(table.items(), key=lambda x: (x[1]["pts"], x[1].get("gf",0)-x[1].get("ga",0)), reverse=True)
        return [t[0] for t in sorted_teams[:count]]

    def _get_continent_by_nat(self, nat):
        eu = ["EN", "ES", "FR", "IT", "DE", "PT", "NL", "BE", "HR", "CH", "DK", "NO", "SE", "PL", "UA", "GR", "TR", "SC", "WA"]
        sa = ["AR", "BR", "CO", "UY", "CL", "EC", "PY", "PE", "VE", "BO"]
        af = ["MA", "SN", "EG", "NG", "CM", "AF", "DZ", "TN", "CI", "GH", "ZA"]
        as_oc = ["JP", "KR", "AU", "AS", "CN", "QA", "SA_AS", "IR"]
        na = ["US", "MX", "CA", "NA"]
        
        if nat in eu: return "EU"
        if nat in sa: return "SA"
        if nat in af: return "AF"
        if nat in as_oc: return "AS"
        if nat in na: return "NA"
        return "OT"

    def _generate_yearly_awards(self):
        """Calculates Ballon d'Or for Global and Continents."""
        all_players = []
        for t_short, roster in self.rosters.items():
            if t_short == "LIB": continue
            # Only process registered club teams
            team_obj = self.get_team_by_short(t_short)
            if not team_obj: continue
            
            for p in roster:
                # Score = OVR*0.6 + Goals*1.5 + Assists*1.0 + random factor
                score = p.get("ovr", 70) * 0.6
                score += p.get("club_goals", 0) * 1.5
                score += p.get("club_assists", 0) * 1.0
                score += random.uniform(0, 5)
                
                player_info = {
                    "name": p["name"],
                    "team": t_short,
                    "nat": p.get("nat", "??"),
                    "score": score,
                    "ovr": p.get("ovr", 70),
                    "goals": p.get("club_goals", 0),
                    "assists": p.get("club_assists", 0),
                    "pos": p.get("pos", "CM"),
                    "age": p.get("age", 25)
                }
                all_players.append(player_info)
        
        if not all_players: return
        
        all_players.sort(key=lambda x: x["score"], reverse=True)
        
        # 1. Global Ballon d'Or
        winner = all_players[0]
        self.add_news("GLORIA", "¡BALÓN DE ORO GLOBAL!", f"{winner['name']} ({winner['team']}) ha ganado el Balón de Oro tras una temporada espectacular.", importance=3)
        
        # 2. Premios por Liga (Bota de Oro y Máximo Asistente)
        for lg in self.leagues:
            # Goleadores
            lg_scorers = self.scorers.get(f"LIGA_{lg}", {})
            if lg_scorers:
                sorted_sc = sorted(lg_scorers.items(), key=lambda x: x[1], reverse=True)
                top_sc_name, top_sc_val = sorted_sc[0]
                self.add_news("INFO", f"BOTA DE ORO: {lg}", f"{top_sc_name} es el máximo goleador de la liga {lg} con {top_sc_val} goles.", importance=2)
                
                if self.mode == "player" and top_sc_name == self.career_player["name"]:
                    self.career_stats.setdefault("individual_awards", []).append(f"Bota de Oro {lg} (Temp. {self.year})")
                    self._update_prestige(15)

            # Asistentes
            lg_assists = self.assists.get(f"LIGA_{lg}", {})
            if lg_assists:
                sorted_as = sorted(lg_assists.items(), key=lambda x: x[1], reverse=True)
                top_as_name, top_as_val = sorted_as[0]
                self.add_news("INFO", f"MÁX. ASISTENTE: {lg}", f"{top_as_name} lidera la tabla de asistencias en {lg} con {top_as_val} pases de gol.", importance=1)

                if self.mode == "player" and top_as_name == self.career_player["name"]:
                    self.career_stats.setdefault("individual_awards", []).append(f"Máximo Asistente {lg} (Temp. {self.year})")
                    self._update_prestige(10)

        # 3. Continents
        continents = {
            "EU": "Jugador del Año en Europa", 
            "SA": "Rey de América", 
            "AF": "Balón de Oro Africano", 
            "AS": "Balón de Oro Asiático"
        }
        for cont_id, award_name in continents.items():
            cont_players = [p for p in all_players if self._get_continent_by_nat(p["nat"]) == cont_id]
            if cont_players:
                c_winner = cont_players[0]
                self.add_news("INTL", f"¡{award_name.upper()}!", f"{c_winner['name']} ({c_winner['team']}) es el mejor jugador del continente.", importance=2)
                
                # Notification if it's the player
                if self.mode == "player" and c_winner["name"] == self.career_player["name"]:
                    self.career_stats.setdefault("individual_awards", []).append(f"{award_name} (Temp. {self.year})")
                    self.add_email("info", f"¡Ganador del {award_name}!", f"Felicidades, has sido nombrado el mejor jugador del continente. ¡Tu nombre ya es historia!")
                    self._update_prestige(30)
                    
        # 5. Bota de Oro de Europa
        eu_leagues = ["EN", "ES", "FR", "IT", "DE", "PT", "NL", "BE", "RU", "RO", "AT", "HR", "CH", "DK", "NO", "SE", "PL", "UA", "GR", "TR", "SC", "WA"]
        top_5 = ["EN", "ES", "IT", "DE", "FR"]
        mid_leagues = ["PT", "NL", "BE", "TR", "UA", "GR", "PL", "RU", "SC"]
        
        eu_candidates = []
        for p in all_players:
            team_obj = self.get_team_by_short(p["team"])
            p_lg = team_obj.get("league", "??") if team_obj else "??"
            if p_lg in eu_leagues:
                factor = 1.0
                if p_lg in top_5: factor = 2.0
                elif p_lg in mid_leagues: factor = 1.5
                
                p_score = p["goals"] * factor
                eu_candidates.append({"name": p["name"], "team": p["team"], "goals": p["goals"], "pts": p_score})
        
        if eu_candidates:
            eu_candidates.sort(key=lambda x: x["pts"], reverse=True)
            gs_winner = eu_candidates[0]
            self.add_news("GLORIA", "BOTA DE ORO DE EUROPA", 
                          f"{gs_winner['name']} ({gs_winner['team']}) ha ganado la Bota de Oro con {gs_winner['goals']} goles ({gs_winner['pts']} puntos).", 
                          importance=3)
            
            if self.mode == "player" and gs_winner["name"] == self.career_player["name"]:
                self.career_stats.setdefault("individual_awards", []).append(f"Bota de Oro de Europa (Temp. {self.year})")
                self.add_email("info", "¡BOTA DE ORO DE EUROPA!", "¡Espectacular! Eres el máximo goleador del continente europeo. Te llevas la Bota de Oro.")
                self._update_prestige(40)

        # 6. Equipo Ideal de cada Liga
        for lg in self.leagues:
            self._generate_league_best_xi(lg, all_players)

        # 7. Equipo Ideal de Europa (UEFA Team of the Year)
        self._generate_european_best_xi(all_players)

        # 8. Global Winner Notification (Ballon d'Or)
        if self.mode == "player" and winner["name"] == self.career_player["name"]:
            self.career_stats.setdefault("individual_awards", []).append(f"Balón de Oro Global (Temp. {self.year})")
            if "pending_award_presentations" not in self.career_stats:
                self.career_stats["pending_award_presentations"] = []
            self.career_stats["pending_award_presentations"].append("Balón de Oro Global")
            self.add_email("info", "¡BALÓN DE ORO!", "¡Increíble! Eres el mejor jugador del mundo. Has ganado el Balón de Oro Global.")
            self._update_prestige(50)
            
        # 9. Mejor Portero & Mejor Joven
        gks = [p for p in all_players if p["pos"] == "GK"]
        if gks:
            winner_gk = gks[0]
            if self.mode == "player" and winner_gk["name"] == self.career_player["name"]:
                if "Mejor Portero del Mundo" not in self.career_stats.setdefault("individual_awards", []):
                    self.career_stats["individual_awards"].append("Mejor Portero del Mundo")
                    self.career_stats.setdefault("pending_award_presentations", []).append("Mejor Portero del Mundo")
                
        youngs = [p for p in all_players if p["age"] <= 21]
        if youngs:
            winner_young = youngs[0]
            if self.mode == "player" and winner_young["name"] == self.career_player["name"]:
                if "Mejor Jugador Joven (U21)" not in self.career_stats.setdefault("individual_awards", []):
                    self.career_stats["individual_awards"].append("Mejor Jugador Joven (U21)")
                    self.career_stats.setdefault("pending_award_presentations", []).append("Mejor Jugador Joven (U21)")

    def _generate_league_best_xi(self, lg, all_players):
        """Generates a balanced 4-3-3 Team of the Season for a league."""
        lg_players = [p for p in all_players if (self.get_team_by_short(p["team"]).get("league") if self.get_team_by_short(p["team"]) else None) == lg]
        if not lg_players: return
        
        # Categorize
        gks = [p for p in lg_players if self._get_pos_cat(p["name"]) == "GK"]
        dfs = [p for p in lg_players if self._get_pos_cat(p["name"]) == "DF"]
        mfs = [p for p in lg_players if self._get_pos_cat(p["name"]) == "MF"]
        fws = [p for p in lg_players if self._get_pos_cat(p["name"]) == "FW"]
        
        # Sort by score
        gks.sort(key=lambda x: x["score"], reverse=True)
        dfs.sort(key=lambda x: x["score"], reverse=True)
        mfs.sort(key=lambda x: x["score"], reverse=True)
        fws.sort(key=lambda x: x["score"], reverse=True)
        
        # Pick 1-4-3-3
        xi = []
        if gks: xi.append(gks[0])
        xi.extend(dfs[:4])
        xi.extend(mfs[:3])
        xi.extend(fws[:3])
        
        if len(xi) < 5: return # Not enough players?
        
        names = [p["name"] for p in xi]
        xi_str = ", ".join(names)
        self.add_news("GLORIA", f"EQUIPO IDEAL: {lg}", f"Se ha revelado el 11 de gala de la temporada en {lg}: {xi_str}.", importance=2)
        
        # Reward player if in XI
        if self.mode == "player":
            if any(p["name"] == self.career_player["name"] for p in xi):
                self.career_stats.setdefault("individual_awards", []).append(f"Equipo Ideal {lg} (Temp. {self.year})")
                self.add_email("info", "¡En el 11 Ideal!", f"Felicidades, has sido seleccionado en el equipo ideal de la temporada en {lg}. ¡Un reconocimiento a tu gran año!")
                self._update_prestige(20)

    def _generate_european_best_xi(self, all_players):
        """Generates a balanced 4-3-3 Team of the Year for Europe."""
        eu_leagues = ["EN", "ES", "FR", "IT", "DE", "PT", "NL", "BE", "RU", "RO", "AT", "HR", "CH", "DK", "NO", "SE", "PL", "UA", "GR", "TR", "SC", "WA"]
        eu_players = [p for p in all_players if (self.get_team_by_short(p["team"]).get("league") if self.get_team_by_short(p["team"]) else None) in eu_leagues]
        if not eu_players: return
        
        # Categorize
        gks = [p for p in eu_players if self._get_pos_cat(p["name"]) == "GK"]
        dfs = [p for p in eu_players if self._get_pos_cat(p["name"]) == "DF"]
        mfs = [p for p in eu_players if self._get_pos_cat(p["name"]) == "MF"]
        fws = [p for p in eu_players if self._get_pos_cat(p["name"]) == "FW"]
        
        # Sort by score
        gks.sort(key=lambda x: x["score"], reverse=True)
        dfs.sort(key=lambda x: x["score"], reverse=True)
        mfs.sort(key=lambda x: x["score"], reverse=True)
        fws.sort(key=lambda x: x["score"], reverse=True)
        
        # Pick 1-4-3-3
        xi = []
        if gks: xi.append(gks[0])
        xi.extend(dfs[:4])
        xi.extend(mfs[:3])
        xi.extend(fws[:3])
        
        if len(xi) < 5: return
        
        names = [p["name"] for p in xi]
        xi_str = ", ".join(names)
        self.add_news("GLORIA", "EQUIPO DEL AÑO (UEFA)", f"Se ha anunciado el 11 ideal de Europa de esta temporada: {xi_str}.", importance=3)
        
        # Reward player if in XI
        if self.mode == "player":
            if any(p["name"] == self.career_player["name"] for p in xi):
                self.career_stats.setdefault("individual_awards", []).append(f"Once Ideal de Europa (Temp. {self.year})")
                self.add_email("info", "¡Élite Europea!", "Has sido seleccionado en el 11 ideal de Europa. ¡Estás entre los mejores del continente!")
                self._update_prestige(35)

    def _get_pos_cat(self, p_name):
        """Finds player category (GK, DF, MF, FW) by searching in rosters."""
        for rost in self.rosters.values():
            for p in rost:
                if p["name"] == p_name:
                    pos = p.get("pos", "ST")
                    if pos == "GK": return "GK"
                    if pos in ["CB", "LB", "RB", "LWB", "RWB"]: return "DF"
                    if pos in ["CDM", "CM", "CAM", "LM", "RM"]: return "MF"
                    return "FW"
        return "FW"

# Global instance
career_manager = CareerManager()

