import random
import copy
import uuid
import pygame
from data.teams import TEAMS
from data.rosters import all_rosters, calculate_ovr
from data.legends import LEGENDS

class UltimateManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UltimateManager, cls).__new__(cls)
            cls._instance.init_vars()
        return cls._instance

    def _get_user(self):
        import os
        # getpass.getuser() falla en Android
        try:
            import getpass
            return getpass.getuser()
        except:
            return os.environ.get("USER", os.environ.get("USERNAME", "AndroidUser"))

    @property
    def username(self):
        try:
            from systems.network import NetworkManager
            net = NetworkManager()
            if net.username:
                return net.username
        except:
            pass
        return self._get_user()

    @property
    def server_url(self):
        try:
            from systems.network import NetworkManager
            net = NetworkManager()
            return f"{net.server_url}/api/ultimate"
        except:
            return f"http://{self.server_ip}:{self.server_port}/api/ultimate"

    def init_vars(self):
        import os, json
        # Cargar configuración de servidor
        self.server_ip = "localhost" # Por defecto
        self.server_port = 5001 # Por defecto
        config_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "server_config.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, "r") as f:
                    cfg = json.load(f)
                    if "server_ip" in cfg:
                        self.server_ip = cfg["server_ip"]
                    elif "ip" in cfg:
                        self.server_ip = cfg["ip"]
                    if "port" in cfg:
                        self.server_port = int(cfg["port"])
            except: pass
            
        print(f"DEBUG: Servidor IP detectada: {self.server_ip}")
        print(f"DEBUG: Servidor URL base: {self.server_url}")
        self.team_name = "Mi Club"
        self.abbreviation = "MCU"
        self.badge = None
        self.kit = None
        self.primary = (0, 100, 200) # Azul por defecto
        self.secondary = (255, 255, 255) # Blanco
        self.accent = (255, 215, 0) # Oro
        self.coins = 500
        self.fc_points = 0
        self.squad = [None] * 18
        self.club_items = {"players": [], "badges": [], "kits": [], "consumables": []}
        self.stats = {"matches": 0, "wins": 0, "draws": 0, "losses": 0, "gf": 0, "ga": 0}
        self.formation = "4-3-3"   # Formación táctica activa
        self.captain_name = None    # Nombre del capitán designado
        self.player_id = self.username
        self.market_auctions = []
        self.pending_items = [] # Artículos de sobre sin gestionar
        self.online_status = "CONNECTING" # CONNECTING, ONLINE, OFFLINE_ERROR
        self.connection_error_msg = ""
        self.pending_picks = [] # Picks comprados pero no seleccionados
        self.pending_packs = [] # Sobres adquiridos pero no abiertos
        self.discard_recovery = [] # Almacén para recuperación de descartes (Quick Sell Recovery)
        
        # --- CARGA DE DATOS DE USUARIO ---
        # --- TIENDA ORIGINAL REFINADA (6 Normales + Promo) ---
        self.store_packs = [
            {"id": "bronze", "name": "SOBRE BRONCE", "price": 400, "price_points": 50, "event": "NORMAL", "cat": "NORMAL", "type": "PACK", "total_items": 12, "legend_chance": 0.0, "event_chance": 0.0, "color_tier": "BRONCE", "details": {"players": "3-6", "min_players": 3, "max_players": 6, "guaranteed": "BRONCE", "prob": "ESPECIAL: 0%"}},
            {"id": "bronze_p", "name": "SOBRE BRONCE PREMIUM", "price": 750, "price_points": 75, "event": "NORMAL", "cat": "NORMAL", "type": "PACK", "total_items": 12, "legend_chance": 0.0, "event_chance": 0.0, "color_tier": "BRONCE", "details": {"players": "6-9", "min_players": 6, "max_players": 9, "guaranteed": "BRONCE PREM", "prob": "ESPECIAL: 0%"}},
            {"id": "silver", "name": "SOBRE PLATA", "price": 1500, "price_points": 100, "event": "NORMAL", "cat": "NORMAL", "type": "PACK", "total_items": 12, "legend_chance": 0.0, "event_chance": 0.0, "color_tier": "PLATA", "details": {"players": "3-6", "min_players": 3, "max_players": 6, "guaranteed": "PLATA (65+)", "min_ovr": 65, "prob": "ESPECIAL: 0%"}},
            {"id": "silver_p", "name": "SOBRE PLATA PREMIUM", "price": 2500, "price_points": 150, "event": "NORMAL", "cat": "NORMAL", "type": "PACK", "total_items": 12, "legend_chance": 0.0, "event_chance": 0.0, "color_tier": "PLATA", "details": {"players": "6-9", "min_players": 6, "max_players": 9, "guaranteed": "PLATA PREM", "min_ovr": 68, "prob": "ESPECIAL: 0%"}},
            {"id": "gold", "name": "SOBRE ORO", "price": 5000, "price_points": 250, "event": "NORMAL", "cat": "NORMAL", "type": "PACK", "total_items": 12, "legend_chance": 0.002, "event_chance": 0.002, "color_tier": "ORO", "details": {"players": "3-6", "min_players": 3, "max_players": 6, "guaranteed": "ORO (75+)", "min_ovr": 75, "prob": "ESPECIAL: 0.2%"}},
            {"id": "gold_p", "name": "SOBRE ORO PREMIUM", "price": 7500, "price_points": 350, "event": "NORMAL", "cat": "NORMAL", "type": "PACK", "total_items": 12, "legend_chance": 0.005, "event_chance": 0.005, "color_tier": "ORO", "details": {"players": "6-9", "min_players": 6, "max_players": 9, "guaranteed": "ORO PREM", "min_ovr": 78, "prob": "ESPECIAL: 0.5%"}},
            {"id": "promo_elite", "name": "SOBRE ÉLITE LEYENDA", "price": 25000, "price_points": 1000, "event": "NORMAL", "cat": "PROMO", "type": "PACK", "total_items": 12, "legend_chance": 0.015, "event_chance": 0.01, "color_tier": "ELITE", "details": {"players": "12", "min_players": 12, "max_players": 12, "guaranteed": "ÉLITE (80+)", "min_ovr": 80, "prob": "ESPECIAL: 1.5%"}}
        ]

        # EVENTO MUNDIAL
        from data.event_worldcup import is_event_active
        if is_event_active():
            self.store_packs.append({
                "id": "wc_mega_pack", "name": "MEGASOBRE MUNDIAL 2026", "price": 75000, "price_points": 2500, "event": "WC", "cat": "PROMO", "type": "PACK",
                "total_items": 57, "legend_chance": 0.05, "event_chance": 0.05, "color_tier": "ELITE", 
                "details": {
                    "players": "47+3 Picks", "min_players": 47, "max_players": 47, "guaranteed": "3 PICKS + 47 WC", 
                    "prob": "ESPECIAL: 5% | PICKS: 20% ESP", "pick_count": 3, "pick_chance": 1.0, "pick_special_chance": 0.2,
                    "embedded_picks": [
                        {"id": "wc_pick", "name": "PLAYER PICK MUNDIAL", "details": {"options": 3, "min_ovr": 80, "is_wc": True}}
                    ]
                }
            })
            self.store_packs.append({
                "id": "worldcup", "name": "SOBRE MUNDIAL 2026", "price": 35000, "price_points": 1500, "event": "WC", "cat": "PROMO", "type": "PACK",
                "total_items": 12, "legend_chance": 0.02, "event_chance": 0.015, "color_tier": "ORO", "details": {"players": "12", "min_players": 12, "max_players": 12, "guaranteed": "ORO WC (82+)", "min_ovr": 82, "prob": "ESPECIAL: 2%"}
            })
        
        # EVENTO FLASHBACK
        from data.event_flashback import is_flashback_active
        if is_flashback_active():
            self.store_packs.append({
                "id": "flashback_pack", "name": "SOBRE FLASHBACK", "price": 45000, "price_points": 1800, "event": "FLASHBACK", "cat": "PROMO", "type": "PACK",
                "total_items": 12, "legend_chance": 0.02, "event_chance": 0.03, "color_tier": "ELITE", "details": {"players": 12, "guaranteed": "FLASHBACK (82+)"}
            })
        
        self.has_claimed_founder_reward = False
        self.legend_pick_options = []
        self.pending_picks = [] # Picks comprados pero no abiertos
        self.all_legends = [] # Se poblará desde el servidor o local
        
        # --- MODO LIGA (DIVISION RIVALS) ---
        self.league_state = {
            "division": 10,
            "points": 0,
            "matches_played": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "history": [], # ["W", "L", "D"]
            "best_div": 10,
            "last_reward_claimed": True
        }
        
        self.online_league_state = {
            "division": 10,
            "points": 0,
            "matches_played": 0,
            "wins": 0,
            "draws": 0,
            "losses": 0,
            "history": [], # ["W", "L", "D"]
            "best_div": 10,
            "last_reward_claimed": True
        }
        
        # --- PASE DE BATALLA Y OBJETIVOS DIARIOS ---
        self.battle_pass = {
            "xp": 0,
            "level": 1,
            "claimed_levels": [],
            "last_reset": "2000-01-01" # Para comparar fechas y hacer reset diario
        }
        
        self.daily_objectives = [
            {"id": "play_1", "desc": "Juega 1 partido", "type": "play", "target": 1, "progress": 0, "completed": False, "xp": 100},
            {"id": "win_1", "desc": "Gana 1 partido", "type": "win", "target": 1, "progress": 0, "completed": False, "xp": 200},
            {"id": "goals_3", "desc": "Marca 3 goles", "type": "goals", "target": 3, "progress": 0, "completed": False, "xp": 150}
        ]
        
        self.sbc_state = {}
        
        # Cargar datos guardados (En un hilo para no bloquear Android)
        import threading
        threading.Thread(target=self._initial_sync, daemon=True).start()

    def _initial_sync(self):
        """Ejecuta la sincronización inicial en segundo plano."""
        self.load_ultimate()
        self.check_daily_reset()
        self.sync_legends()
        self._check_dev_gift()

    def check_daily_reset(self):
        """Verifica si ha pasado el tiempo de reseteo diario (18:00 UTC)."""
        import datetime
        now = datetime.datetime.utcnow()
        reset_time = now.replace(hour=18, minute=0, second=0, microsecond=0)
        
        if now < reset_time:
            effective_reset = reset_time - datetime.timedelta(days=1)
        else:
            effective_reset = reset_time
            
        reset_str = effective_reset.strftime("%Y-%m-%d")
        if self.battle_pass.get("last_reset") != reset_str:
            self.battle_pass["last_reset"] = reset_str
            # Resetear objetivos diarios
            for obj in self.daily_objectives:
                obj["progress"] = 0
                obj["completed"] = False
            
            # Resetear SBCs diarios y de mejoras
            keys_to_delete = [k for k in self.sbc_state.keys() if k.startswith("daily_") or k.startswith("upgrade_")]
            for k in keys_to_delete:
                del self.sbc_state[k]
                
            self.save_ultimate()

    def advance_objectives(self, gf, ga):
        """Actualiza el progreso de los objetivos diarios basado en el resultado del partido."""
        is_win = gf > ga
        
        xp_ganada = 0
        
        for obj in self.daily_objectives:
            if obj["completed"]: continue
            
            if obj["type"] == "play":
                obj["progress"] += 1
            elif obj["type"] == "win" and is_win:
                obj["progress"] += 1
            elif obj["type"] == "goals":
                obj["progress"] += gf
                
            if obj["progress"] >= obj["target"]:
                obj["progress"] = obj["target"]
                obj["completed"] = True
                xp_ganada += obj["xp"]
                
        if xp_ganada > 0:
            self.battle_pass["xp"] += xp_ganada
            # Check level up
            xp_needed = self.battle_pass["level"] * 1000
            while self.battle_pass["xp"] >= xp_needed:
                self.battle_pass["xp"] -= xp_needed
                self.battle_pass["level"] += 1
                xp_needed = self.battle_pass["level"] * 1000
                
        self.save_ultimate()

    def load_ultimate(self):
        """Carga el estado del club desde el archivo local y sincroniza con el servidor."""
        import requests
        import json
        import os
        
        # 1. Cargar desde archivo local (Salvavidas Offline)
        if os.path.exists("ultimate_save.json"):
            try:
                with open("ultimate_save.json", "r") as f:
                    data = json.load(f)
                    self._apply_loaded_data(data)
            except Exception as e:
                print(f"Error cargando archivo local: {e}")

        # 2. Sincronizar con Servidor (OBLIGATORIO)
        url = f"{self.server_url}/load/{self.username}"
        print(f"Intentando conectar al servidor: {url}")
        try:
            r = requests.get(url, timeout=5)
            print(f"Respuesta del servidor: {r.status_code}")
            if r.status_code == 200:
                try:
                    data = r.json()
                except (ValueError, Exception):
                    data = None
                if data and "new_user" not in data:
                    self._apply_loaded_data(data)
                self.online_status = "ONLINE"
                print(f"Sincronización Cloud completada: {self.username}")
            else:
                self.online_status = "OFFLINE_ERROR"
                self.connection_error_msg = f"Error del servidor ({r.status_code})"
                print(f"Error: Servidor devolvió {r.status_code}")
        except Exception as e:
            self.online_status = "OFFLINE_ERROR"
            self.connection_error_msg = "No se pudo contactar con el servidor central."
            print(f"Error Cloud al conectar a {url}: {e}")

        # 3. Cargar Mercado Global
        self.refresh_market()

    def _apply_loaded_data(self, data):
        self.team_name = data.get("team_name", self.team_name)
        self.abbreviation = data.get("abbreviation", self.abbreviation)
        self.badge = data.get("badge", self.badge)
        self.kit = data.get("kit", self.kit)
        self.primary = tuple(data.get("primary", self.primary))
        self.secondary = tuple(data.get("secondary", self.secondary))
        self.accent = tuple(data.get("accent", self.accent))
        self.coins = data.get("coins", self.coins)
        self.fc_points = data.get("fc_points", 0)
        self.squad = data.get("squad", self.squad)
        self.club_items = data.get("club_items", self.club_items)
        if "badges" not in self.club_items: self.club_items["badges"] = []
        if "kits" not in self.club_items: self.club_items["kits"] = []
        if "consumables" not in self.club_items: self.club_items["consumables"] = []
        self.pending_items = data.get("pending_items", [])
        self.pending_picks = data.get("pending_picks", [])
        self.pending_packs = data.get("pending_packs", [])
        self.discard_recovery = data.get("discard_recovery", [])
        self.stats = data.get("stats", self.stats)
        
        # MIGRACIÓN: Fixer para Megasobres antiguos (Asegurar diseño correcto)
        for p in self.pending_packs:
            # 1. Caso especial Megasobre Mundial
            if "MEGASOBRE MUNDIAL" in p.get("name", "").upper():
                p["event"] = "WC"
                p["color_tier"] = "ELITE"
                p["cat"] = "PROMO"
                p["total_items"] = 57
                if "details" not in p: p["details"] = {}
                p["details"]["players"] = "47+3 Picks"
                p["details"]["min_players"] = 47
                p["details"]["max_players"] = 47
                p["details"]["pick_count"] = 3
                p["details"]["prob"] = "WC: 5% | PICKS: 20%"
                p["details"]["guaranteed"] = "3 PICKS + 47 WC"
                continue

            # 2. Caso general: Sincronizar con catálogo de tienda si falta info
            store_match = next((sp for sp in self.store_packs if sp["id"] == p.get("id")), None)
            if store_match:
                for key in ["event", "color_tier", "cat", "details", "total_items"]:
                    if key not in p or (key == "details" and not p[key]):
                        p[key] = copy.deepcopy(store_match[key])
        
        # Migración de datos si hay archivos antiguos o corruptos
        if "goals_for" in self.stats:
            self.stats["gf"] = self.stats.pop("goals_for")
        if "goals_against" in self.stats:
            self.stats["ga"] = self.stats.pop("goals_against")
        if "gf" not in self.stats: self.stats["gf"] = 0
        if "ga" not in self.stats: self.stats["ga"] = 0
        # Migración de Nombres de Formación (Inglés -> Español)
        old_to_new = {
            "4-3-3 ATTACK": "4-3-3 OFENSIVA",
            "4-3-3 DEFEND": "4-3-3 DEFENSIVA",
            "4-3-3 FALSE 9": "4-3-3 FALSO 9",
            "4-4-2 HOLDING": "4-4-2 CONTENCIÓN",
            "4-2-3-1 NARROW": "4-2-3-1 CERRADA",
            "4-2-3-1 WIDE": "4-2-3-1 ANCHA",
            "4-1-2-1-2 NARROW": "4-1-2-1-2 CERRADA",
            "4-1-2-1-2 WIDE": "4-1-2-1-2 ANCHA",
            "4-3-2-1": "4-3-2-1 ÁRBOL"
        }
        raw_form = data.get("formation", "4-3-3")
        self.formation = old_to_new.get(raw_form, raw_form)
        
        self.captain_name = data.get("captain_name", None)
        self.has_claimed_founder_reward = data.get("has_claimed_founder_reward", False)
        self.legend_pick_options = data.get("legend_pick_options", [])
        self.league_state = data.get("league_state", self.league_state)
        self.online_league_state = data.get("online_league_state", self.online_league_state)
        self.battle_pass = data.get("battle_pass", self.battle_pass)
        self.daily_objectives = data.get("daily_objectives", self.daily_objectives)
        self.sbc_state = data.get("sbc_state", self.sbc_state)
        # Ensure new fields if loading old save
        if "last_reward_claimed" not in self.league_state:
            self.league_state["last_reward_claimed"] = True
        if "last_reward_claimed" not in self.online_league_state:
            self.online_league_state["last_reward_claimed"] = True
        
        # MIGRACIÓN: Corrección de regate para leyendas regateadoras (v2.1)
        _dribbling_fix = {
            "Maradonna": 97, "Ronaldinhu": 96, "Peléi": 96, "Ronnaldo": 93,
            "Zidanne": 93, "J. Cruyffe": 93, "Cruijff": 92, "Iniestta": 92,
            "Kakáh": 91, "Henrie": 89, "Erick Kantonah": 85, "Wayner Runi": 84,
        }
        for p in self.club_items["players"]:
            fix_val = _dribbling_fix.get(p.get("name"))
            if fix_val and p.get("s", {}).get("dribbling", 0) < fix_val:
                p["s"]["dribbling"] = fix_val
        for p in (self.squad or []):
            if p:
                fix_val = _dribbling_fix.get(p.get("name"))
                if fix_val and p.get("s", {}).get("dribbling", 0) < fix_val:
                    p["s"]["dribbling"] = fix_val

        for p in self.club_items["players"]:
            if p.get("name") == "Alisson Becker":
                p["name"] = "Alisson"
            self._ensure_player_stats(p)
            
        for p in (self.squad or []):
            if p and p.get("name") == "Alisson Becker":
                p["name"] = "Alisson"

        # Re-vincular squad con los objetos reales del club para evitar duplicidad de IDs
        new_squad = [None] * max(18, len(self.squad))
        used_uids = set() 
        used_names = set()
        for i, sp in enumerate(self.squad):
            if sp:
                match = None
                for cp in self.club_items["players"]:
                    # Regla estricta: Mismo nombre Y que no se haya usado ya esa instancia NI ese nombre
                    if cp["name"] == sp["name"] and cp["ovr"] == sp["ovr"] and id(cp) not in used_uids and cp["name"] not in used_names:
                        match = cp
                        break
                if match:
                    new_squad[i] = match
                    used_uids.add(id(match))
                    used_names.add(match["name"])
                else:
                    # Si no hay match en el club (o ya se usó el nombre), este slot queda vacío para evitar duplicados
                    self._ensure_player_stats(sp)
                    if sp["name"] not in used_names:
                        new_squad[i] = sp
                        used_names.add(sp["name"])
                    else:
                        new_squad[i] = None
        self.squad = new_squad

        while len(self.squad) < 18:
            self.squad.append(None)
            
        # MIGRACIÓN: Si la banca (11-17) está vacía tras cargar, poblarla con los mejores del club
        # MIGRACIÓN / RESTAURACIÓN DE BANCA
        filled_subs = [p for p in self.squad[11:18] if p]
        if len(filled_subs) < 3:
            all_p = self.club_items.get("players", [])
            starters = [p for p in self.squad[:11] if p]
            starter_uids = {p.get("uid") for p in starters}
            starter_names = {p.get("name") for p in starters}
            
            # Jugadores disponibles (no titulares, ni por UID ni por nombre, y solo uno por nombre)
            available = []
            seen_avail_names = set()
            for p in all_p:
                p_name = p.get("name")
                if p.get("uid") not in starter_uids and p_name not in starter_names and p_name not in seen_avail_names:
                    available.append(p)
                    seen_avail_names.add(p_name)
            
            available.sort(key=lambda x: x.get("ovr", 0), reverse=True)
            
            # Poblar huecos vacíos de la banca
            count = 0
            for i in range(11, 18):
                if count < len(available):
                    self.squad[i] = available[count]
                    count += 1
                else:
                    self.squad[i] = None
        
        # FINAL: Recalcular medias para asegurar consistencia tras cambios en fórmulas
        self.refresh_all_ovrs()

    def _ensure_player_stats(self, p):
        if "stats" not in p:
            p["stats"] = {"matches": 0, "goals": 0, "assists": 0, "rating_sum": 0.0}
        if "uid" not in p:
            p["uid"] = uuid.uuid4().hex
            
        if "rarity" not in p:
            if p.get("is_legend"):
                p["rarity"] = "LEYENDA"
            else:
                ovr = p.get("ovr", 75)
                if ovr >= 75: p["rarity"] = "ORO"
                elif ovr >= 65: p["rarity"] = "PLATA"
                else: p["rarity"] = "BRONCE"
            
        # MIGRACIÓN: Inyectar dribbling/physical si faltan (para jugadores antiguos)
        s = p.get("s", {})
        if "dribbling" not in s or "physical" not in s:
            pos = p.get("pos", "CM")
            pot = p.get("pot", p.get("ovr", 75))
            
            # Mismas reglas que el script de actualización
            if "dribbling" not in s:
                mult = 0.82
                if pos == "GK": mult = 0.45
                elif pos == "CB": mult = 0.60
                elif pos in ["LB", "RB", "LWB", "RWB"]: mult = 0.78
                elif pos in ["CAM", "LM", "RM"]: mult = 0.90
                elif pos in ["ST", "CF"]: mult = 0.86
                elif pos in ["LW", "RW"]: mult = 0.93
                s["dribbling"] = int(pot * mult)
                
            if "physical" not in s:
                mult = 0.78
                if pos == "GK": mult = 0.80
                elif pos == "CB": mult = 0.92
                elif pos in ["LB", "RB", "LWB", "RWB"]: mult = 0.82
                elif pos in ["ST", "CF"]: mult = 0.88
                elif pos in ["LW", "RW"]: mult = 0.70
                s["physical"] = int(pot * mult)
            
            p["s"] = s

    def rename_club(self, new_name):
        self.team_name = new_name
        self.save_ultimate()

    def refresh_all_ovrs(self):
        """Recalcula las medias de todos los jugadores del club y squad para asegurar consistencia,
        sincronizando los stats con la base de datos maestra."""
        from data.rosters import calculate_ovr, all_rosters
        
        # 1. Crear un diccionario de la mejor versión de cada jugador actual
        master_players = {}
        for team, players in all_rosters.items():
            for p in players:
                name = p.get("name")
                pot = p.get("pot", 0)
                if name not in master_players or pot > master_players[name].get("pot", 0):
                    master_players[name] = p

        # Cargar leyendas maestras
        master_legends = {}
        try:
            from data.legends import LEGENDS
            for l in LEGENDS:
                master_legends[l.get("name")] = l
        except:
            pass

        def sync_player(p):
            if not p: return
            name = p.get("name")
            
            # Sincronizar leyendas
            if name in master_legends:
                p["is_legend"] = True
                p["rarity"] = "LEYENDA"
                if p.get("card_type") == "FOUNDER" and name == "J. Cruyffe":
                    # El Cruyff fundador es media 88 fija
                    p["pot"] = 88
                else:
                    master = master_legends[name]
                    # Sincronizar stats base si es una carta normal o especial sin modificaciones de stats de evo
                    if "evolution" not in p:
                        p["s"] = copy.deepcopy(master.get("s", p.get("s", {})))
                        p["pot"] = master.get("pot", p.get("pot", 90))
                        p["pos"] = master.get("pos", p.get("pos", "CAM"))

            # Sincronizar stats base si no es una carta especial modificada o evolución avanzada
            elif name in master_players and not p.get("is_legend") and p.get("card_type", "NORMAL") == "NORMAL" and "evolution" not in p:
                master = master_players[name]
                p["s"] = copy.deepcopy(master.get("s", p.get("s", {})))
                p["pot"] = master.get("pot", p.get("pot", 75))
                # También sincronizamos pos base
                p["pos"] = master.get("pos", p.get("pos", "CM"))

            p["ovr"] = calculate_ovr(p)
            # Actualizar rareza basada en la nueva media si no es especial
            if not p.get("is_legend") and p.get("card_type", "NORMAL") == "NORMAL":
                if p["ovr"] >= 75: p["rarity"] = "ORO"
                elif p["ovr"] >= 65: p["rarity"] = "PLATA"
                else: p["rarity"] = "BRONCE"

        # Actualizar club
        for p in self.club_items.get("players", []):
            sync_player(p)
        
        # Actualizar squad (XI + Banca)
        for p in self.squad:
            sync_player(p)

    def request_admin_coins(self, amount=1000000):
        """Inyecta monedas y puntos FC de forma atómica e inmediata tanto local como en servidor."""
        # 1. Actualización Local Instantánea (Para que sea usable YA)
        self.coins += amount
        self.fc_points += 10000
        print(f"[ADMIN] +{amount} monedas y +10000 FC Points inyectados localmente. Saldo actual: {self.coins} Monedas, {self.fc_points} FC Points")
        
        # 2. Sincronización Silenciosa con el Servidor
        import threading
        def _sync():
            import requests
            try:
                # Usar el endpoint de admin que modifica el archivo en el servidor
                from systems.network import NetworkManager
                url = f"{NetworkManager().server_url}/api/admin/add_coins"
                requests.post(url, json={"username": self.username, "amount": amount}, timeout=3)
                # Forzar un guardado local para asegurar persistencia
                self.save_ultimate()
            except Exception as e:
                print(f"[ADMIN ERROR] No se pudo sincronizar con el servidor: {e}")
        
        threading.Thread(target=_sync, daemon=True).start()

    def _check_dev_gift(self):
        """Lógica de regalo desactivada para evitar duplicados infinitos."""
        # if self.username == "sadav":
        #     # Logic disabled by request
        #     pass
        return

    def list_player_on_market(self, player_idx, bid, buy):
        """Lista un jugador en el mercado global."""
        if 0 <= player_idx < len(self.club_items["players"]):
            player = self.club_items["players"][player_idx]
            
            if player.get("untradeable", False):
                print("Error: No puedes vender un jugador intransferible.")
                return False
            
            return self.list_on_market(player, bid, buy)
        return False

    def list_direct_item_on_market(self, player, bid, buy):
        """Lista un jugador directamente (por ejemplo, desde un sobre) sin estar en el club."""
        if player.get("untradeable", False):
            print("Error: No puedes vender un jugador intransferible.")
            return False
        return self.list_on_market(player, bid, buy)

    def discard_player(self, player_idx):
        """Descarta un jugador y lo añade a la lista de recuperación."""
        if 0 <= player_idx < len(self.club_items["players"]):
            player = self.club_items["players"].pop(player_idx)
            
            # Valor de descarte
            value = 0
            if not player.get("untradeable", False):
                ovr = player.get("ovr", 75)
                if ovr >= 90: value = 1000
                elif ovr >= 85: value = 500
                else: value = 150
            
            self.coins += value
            
            # Añadir a recuperación (máximo 10 items)
            player["discard_price"] = value
            self.discard_recovery.insert(0, player)
            if len(self.discard_recovery) > 10:
                self.discard_recovery.pop()
                
            self.save_ultimate()
            return value
        return -1

    def recover_player(self, recovery_idx):
        """Recupera un jugador descartado pagando su precio de descarte."""
        if 0 <= recovery_idx < len(self.discard_recovery):
            player = self.discard_recovery[recovery_idx]
            price = player.get("discard_price", 0)
            
            if self.coins >= price:
                self.coins -= price
                self.discard_recovery.pop(recovery_idx)
                self.club_items["players"].append(player)
                self.save_ultimate()
                return True
        return False

    def reset_club(self):
        """Borra todo el progreso y reinicia el club."""
        import os
        if os.path.exists("ultimate_save.json"):
            try:
                os.remove("ultimate_save.json")
            except: pass
            
        # Limpiar variables manualmente sin llamar a init_vars() (evita hilos zombis de carga)
        self.team_name = "Mi Club"
        self.abbreviation = "MIC"
        self.badge = None
        self.kit = None
        self.primary = (0, 100, 200)
        self.secondary = (255, 255, 255)
        self.accent = (255, 215, 0)
        self.coins = 500
        self.fc_points = 0
        self.squad = [None] * 18
        self.club_items = {"players": [], "badges": [], "kits": [], "consumables": []}
        self.stats = {"matches": 0, "wins": 0, "draws": 0, "losses": 0, "gf": 0, "ga": 0}
        self.formation = "4-3-3"
        self.captain_name = None
        self.pending_items = []
        self.pending_picks = []
        self.pending_packs = []
        self.discard_recovery = []
        self.has_claimed_founder_reward = False
        self.legend_pick_options = []
        self.sbc_state = {}
        self.league_state = {
            "division": 10, "points": 0, "matches_played": 0,
            "wins": 0, "draws": 0, "losses": 0, "history": [],
            "best_div": 10, "last_reward_claimed": True
        }
        self.online_league_state = {
            "division": 10, "points": 0, "matches_played": 0,
            "wins": 0, "draws": 0, "losses": 0, "history": [],
            "best_div": 10, "last_reward_claimed": True
        }
        self.battle_pass = {
            "xp": 0, "level": 1, "claimed_levels": [],
            "last_reset": "2000-01-01"
        }
        self.daily_objectives = [
            {"id": "play_1", "desc": "Juega 1 partido", "type": "play", "target": 1, "progress": 0, "completed": False, "xp": 100},
            {"id": "win_1", "desc": "Gana 1 partido", "type": "win", "target": 1, "progress": 0, "completed": False, "xp": 200},
            {"id": "goals_3", "desc": "Marca 3 goles", "type": "goals", "target": 3, "progress": 0, "completed": False, "xp": 150}
        ]
        
        self.save_ultimate()

    def sync_legends(self):
        """Intenta sincronizar la lista de leyendas con el servidor."""
        try:
            import requests
            from systems.network import NetworkManager
            r = requests.get(f"{NetworkManager().server_url}/api/ultimate/legends", timeout=2)
            if r.status_code == 200:
                try:
                    self.all_legends = r.json()
                except (ValueError, Exception):
                    self.all_legends = []
                    print("Error: Respuesta de leyendas no es JSON válido.")
                    return
                print(f"Sincronizadas {len(self.all_legends)} leyendas desde el servidor.")
                return
        except:
            pass
        
        # Ya no hay fallback local, si falla el servidor no hay leyendas disponibles
        self.all_legends = []
        if self.online_status == "ONLINE":
            print("Error: El servidor no devolvió la lista de leyendas.")

    def create_starter_pack(self):
        """Genera el sobre inicial de 19 jugadores para tener una plantilla completa."""
        items = []
        
        # 19 Jugadores iniciales (calidad media/baja)
        club_shorts = [t["short"] for t in TEAMS if not t.get("is_national", False)]
        all_players_list = []
        for t_short, team_players in all_rosters.items():
            if t_short in club_shorts:
                all_players_list.extend(team_players)
        
        # Filtrar jugadores "normalitos" (media entre 70 y 80)
        medium_players = [p for p in all_players_list if 70 <= calculate_ovr(p) <= 80]
        if not medium_players: medium_players = all_players_list

        for _ in range(19):
            p = copy.deepcopy(random.choice(medium_players))
            p["is_legend"] = False
            p["ovr"] = calculate_ovr(p)
            p["uid"] = uuid.uuid4().hex
            p["name"] = self._normalize_player_name(p["name"])
            items.append({"type": "player", "data": p})
            self.club_items["players"].append(p)
            
        # Auto-poblar el 11 inicial (uno por posición básica)
        self._auto_generate_lineup()
            
        # 2 Estilos de química (Items de mejora)
        chem_styles = [
            {"id": "hunter", "name": "CAZADOR", "stat": "speed", "val": 3},
            {"id": "shadow", "name": "SOMBRA", "stat": "defense", "val": 3},
            {"id": "sniper", "name": "FRANCOTIRADOR", "stat": "shot", "val": 3},
            {"id": "engine", "name": "MOTOR", "stat": "passing", "val": 3}
        ]
        for _ in range(3):
            style = random.choice(chem_styles)
            items.append({"type": "consumable", "data": style})
            self.club_items["consumables"].append(style)
            
        # Monedas extra
        self.coins += 1000
        
        self.save_ultimate()
        return items

    def _auto_generate_lineup(self):
        """Asigna jugadores a las posiciones tácticas de la formación actual de forma inteligente."""
        players = sorted(self.club_items["players"], key=lambda x: x["ovr"], reverse=True)
        self.squad = [None] * 11
        used_ids = set()

        # Obtener el mapa de posiciones esperado para la formación actual
        pos_map = self._get_position_map_for_formation()

        def find_best(pos_list):
            for p in players:
                p_id = p.get("uid", id(p))
                if p_id not in used_ids and p["pos"] in pos_list:
                    used_ids.add(p_id)
                    return p
            return None

        # 1. Asignación por posición ideal
        for i in range(11):
            expected_pos = pos_map.get(i, [])
            self.squad[i] = find_best(expected_pos)
        
        # 2. Rellenar huecos con los mejores disponibles (fuera de posición)
        for i in range(11):
            if self.squad[i] is None:
                for p in players:
                    p_id = p.get("uid", id(p))
                    if p_id not in used_ids:
                        self.squad[i] = p
                        used_ids.add(p_id)
                        break

    def _get_position_map_for_formation(self):
        """Devuelve qué posiciones son ideales para cada slot (0-10) según la formación."""
        form = self.formation
        # Mapeo universal (Slot 0 siempre es GK)
        m = {0: ["GK"]}
        
        if "4-3-3" in form:
            m.update({1: ["LB", "LWB"], 2: ["CB"], 3: ["CB"], 4: ["RB", "RWB"]})
            if "OFENSIVA" in form: m.update({5: ["CM"], 6: ["CM"], 7: ["CAM"], 8: ["LW"], 9: ["RW"], 10: ["ST"]})
            elif "DEFENSIVA" in form: m.update({5: ["CDM"], 6: ["CM"], 7: ["CM"], 8: ["LW"], 9: ["RW"], 10: ["ST"]})
            elif "FALSO 9" in form: m.update({5: ["CM"], 6: ["CM"], 7: ["CM"], 8: ["LW"], 9: ["RW"], 10: ["CF", "ST"]})
            else: m.update({5: ["CM", "CDM"], 6: ["CM"], 7: ["CM", "CAM"], 8: ["LW"], 9: ["RW"], 10: ["ST"]})
            
        elif "4-4-2" in form:
            m.update({1: ["LB"], 2: ["CB"], 3: ["CB"], 4: ["RB"], 7: ["LM"], 8: ["RM"], 9: ["ST"], 10: ["ST"]})
            if "CONTENCIÓN" in form: m.update({5: ["CDM"], 6: ["CDM"]})
            else: m.update({5: ["CM"], 6: ["CM"]})
            
        elif "4-2-3-1" in form:
            m.update({1: ["LB"], 2: ["CB"], 3: ["CB"], 4: ["RB"], 5: ["CDM"], 6: ["CDM"], 10: ["ST"]})
            if "ANCHA" in form: m.update({7: ["LM"], 8: ["RM"], 9: ["CAM"]})
            else: m.update({7: ["CAM"], 8: ["CAM"], 9: ["CAM"]})

        elif "4-1-2-1-2" in form:
            m.update({1: ["LB"], 2: ["CB"], 3: ["CB"], 4: ["RB"], 5: ["CDM"], 8: ["CAM"], 9: ["ST"], 10: ["ST"]})
            if "ANCHA" in form: m.update({6: ["LM"], 7: ["RM"]})
            else: m.update({6: ["CM"], 7: ["CM"]})

        elif "4-3-2-1" in form:
            m.update({1: ["LB"], 2: ["CB"], 3: ["CB"], 4: ["RB"], 5: ["CM"], 6: ["CM"], 7: ["CM"], 8: ["CF", "CAM"], 9: ["CF", "CAM"], 10: ["ST"]})

        elif form == "3-4-3":
            m.update({1: ["CB"], 2: ["CB"], 3: ["CB"], 4: ["LM"], 5: ["CM"], 6: ["CM"], 7: ["RM"], 8: ["LW"], 9: ["RW"], 10: ["ST"]})

        elif form == "3-5-2":
            m.update({1: ["CB"], 2: ["CB"], 3: ["CB"], 4: ["LM"], 5: ["CDM"], 6: ["CAM"], 7: ["CDM"], 8: ["RM"], 9: ["ST"], 10: ["ST"]})

        elif form == "5-2-1-2":
            m.update({1: ["LWB", "LB"], 2: ["CB"], 3: ["CB"], 4: ["CB"], 5: ["RWB", "RB"], 6: ["CM"], 7: ["CM"], 8: ["CAM"], 9: ["ST"], 10: ["ST"]})

        elif form == "5-4-1":
            m.update({1: ["LWB", "LB"], 2: ["CB"], 3: ["CB"], 4: ["CB"], 5: ["RWB", "RB"], 6: ["LM"], 7: ["CM"], 8: ["CM"], 9: ["RM"], 10: ["ST"]})

        return m

    def advance_match_stats(self, res):
        """Procesa resultados de un partido jugado."""
        gf, ga = res["gf"], res["ga"]
        self.stats["matches"] += 1
        self.stats["gf"] += gf
        self.stats["ga"] += ga
        
        if gf > ga: self.stats["wins"] += 1
        elif gf < ga: self.stats["losses"] += 1
        else: self.stats["draws"] += 1
        
        # Monedas
        self.coins += res.get("reward", 500)
        
        # Estadísticas de jugadores (Solo los que jugaron)
        p_stats = res.get("player_stats", [])
        for ps in p_stats:
            p_name = ps["name"]
            # Buscar en el club
            club_p = next((p for p in self.club_items["players"] if p["name"] == p_name), None)
            if club_p:
                self._ensure_player_stats(club_p)
                club_p["stats"]["matches"] += 1
                club_p["stats"]["rating_sum"] += ps.get("rating", 6.0)
                
                g_scored = 0
                a_scored = 0
                for ev in res.get("goal_events", []):
                    if ev["scorer"] == p_name: g_scored += 1
                    if ev["assistant"] == p_name: a_scored += 1
                
                club_p["stats"]["goals"] += g_scored
                club_p["stats"]["assists"] += a_scored
                
                if "evolution" in club_p:
                    self._process_evolution(club_p, g_scored, a_scored)
                    
    def advance_league_match(self, gf, ga):
        """Procesa el resultado de un partido de liga en Ultimate Team."""
        from scenes.ultimate_league import LEAGUE_DATA
        state = self.league_state
        
        # 1. Determinar resultado
        res = "L"
        pts = 0
        if gf > ga: res = "W"; pts = 3
        elif gf == ga: res = "D"; pts = 1
        
        # 2. Actualizar estado
        state["points"] += pts
        state["matches_played"] += 1
        state["history"].append(res)
        
        # 3. Verificar si terminó la temporada (10 partidos o ya alcanzó el título)
        # O si ya no puede ni salvarse (opcional, pero mejor al terminar los 10)
        data = LEAGUE_DATA[state["division"]]
        
        season_ended = False
        if state["matches_played"] >= 10:
            season_ended = True
        elif state["points"] >= 30: # Max puntos posibles
            season_ended = True
            
        if season_ended:
            self._handle_season_end()
            
    def _handle_season_end(self):
        """Gestiona el fin de una temporada de 10 partidos."""
        from scenes.ultimate_league import LEAGUE_DATA
        state = self.league_state
        div = state["division"]
        data = LEAGUE_DATA[div]
        pts = state["points"]
        
        # Determinar logro
        achieved = "NONE"
        if pts >= data["title"]: achieved = "TITLE"
        elif pts >= data["asc"]: achieved = "ASCENSO"
        elif pts >= data["perm"]: achieved = "PERMANENCIA"
        else: achieved = "DESCENSO"
        
        # Aplicar cambios de división
        old_div = div
        if achieved == "TITLE" or achieved == "ASCENSO":
            if div > 1: state["division"] -= 1
        elif achieved == "DESCENSO":
            if div < 10 and data["perm"] > 0: # Solo si hay descenso en esa div
                state["division"] += 1
        
        # Guardar mejor división
        state["best_div"] = min(state["best_div"], state["division"])
        
        # Preparar recompensas (se reclaman en el hub o automáticamente)
        self._grant_league_rewards(achieved, old_div)
        
        # Resetear temporada
        state["points"] = 0
        state["matches_played"] = 0
        state["history"] = []
        state["last_reward_claimed"] = False
        
    def _grant_league_rewards(self, achieved, div):
        from scenes.ultimate_league import LEAGUE_DATA
        data = LEAGUE_DATA[div]
        
        # Multiplicadores de recompensa según logro
        mult = 1.0
        if achieved == "TITLE": mult = 1.5
        elif achieved == "ASCENSO": mult = 1.2
        elif achieved == "PERMANENCIA": mult = 1.0
        else: mult = 0.5 # Descenso / Fracaso
        
        # Monedas
        reward_coins = int(data["reward_m"] * mult)
        self.coins += reward_coins
        
        # Sobres
        # Si es Título, damos el sobre de la división y uno extra aleatorio
        pack_name = data["reward_p"]
        store_match = next((p for p in self.store_packs if p["name"] == pack_name), self.store_packs[0])
        
        import copy
        self.pending_packs.append(copy.deepcopy(store_match))
        
        if achieved == "TITLE":
            # Sobre extra de oro premium para campeones
            bonus_pack = next((p for p in self.store_packs if p["id"] == "gold_p"), self.store_packs[0])
            self.pending_packs.append(copy.deepcopy(bonus_pack))

    def advance_online_league_match(self, gf, ga):
        """Procesa el resultado de un partido de liga online en Ultimate Team."""
        from scenes.ultimate_league import LEAGUE_DATA
        state = self.online_league_state
        
        # 1. Determinar resultado
        res = "L"
        pts = 0
        if gf > ga:
            res = "W"
            pts = 3
            state["wins"] += 1
        elif gf == ga:
            res = "D"
            pts = 1
            state["draws"] += 1
        else:
            state["losses"] += 1
        
        # 2. Actualizar estado
        state["points"] += pts
        state["matches_played"] += 1
        state["history"].append(res)
        
        # 3. Verificar si terminó la temporada (10 partidos o ya alcanzó el título)
        data = LEAGUE_DATA[state["division"]]
        
        season_ended = False
        if state["matches_played"] >= 10:
            season_ended = True
        elif state["points"] >= 30: # Max puntos posibles
            season_ended = True
            
        if season_ended:
            self._handle_online_season_end()
            
    def _handle_online_season_end(self):
        """Gestiona el fin de una temporada online de 10 partidos."""
        from scenes.ultimate_league import LEAGUE_DATA
        state = self.online_league_state
        div = state["division"]
        data = LEAGUE_DATA[div]
        pts = state["points"]
        
        # Determinar logro
        achieved = "NONE"
        if pts >= data["title"]: achieved = "TITLE"
        elif pts >= data["asc"]: achieved = "ASCENSO"
        elif pts >= data["perm"]: achieved = "PERMANENCIA"
        else: achieved = "DESCENSO"
        
        # Aplicar cambios de división
        old_div = div
        if achieved == "TITLE" or achieved == "ASCENSO":
            if div > 1: state["division"] -= 1
        elif achieved == "DESCENSO":
            if div < 10 and data["perm"] > 0: # Solo si hay descenso en esa div
                state["division"] += 1
        
        # Guardar mejor división
        state["best_div"] = min(state["best_div"], state["division"])
        
        # Preparar recompensas (online da recompensas un 50% superiores!)
        self._grant_online_league_rewards(achieved, old_div)
        
        # Resetear temporada
        state["points"] = 0
        state["matches_played"] = 0
        state["history"] = []
        state["last_reward_claimed"] = False

    def _grant_online_league_rewards(self, achieved, div):
        from scenes.ultimate_league import LEAGUE_DATA
        data = LEAGUE_DATA[div]
        
        # Multiplicadores de recompensa según logro
        mult = 1.0
        if achieved == "TITLE": mult = 1.5
        elif achieved == "ASCENSO": mult = 1.2
        elif achieved == "PERMANENCIA": mult = 1.0
        else: mult = 0.5 # Descenso / Fracaso
        
        # Monedas (un 50% más por jugar online!)
        reward_coins = int(data["reward_m"] * mult * 1.5)
        self.coins += reward_coins
        
        # Sobres
        # Si es Título, damos el sobre de la división y uno extra aleatorio
        pack_name = data["reward_p"]
        store_match = next((p for p in self.store_packs if p["name"] == pack_name), self.store_packs[0])
        
        import copy
        self.pending_packs.append(copy.deepcopy(store_match))
        
        if achieved == "TITLE":
            # Sobre extra de oro premium para campeones
            bonus_pack = next((p for p in self.store_packs if p["id"] == "gold_p"), self.store_packs[0])
            self.pending_packs.append(copy.deepcopy(bonus_pack))
            # E inyectamos otro sobre extra por ser Campeón Online!
            wc_bonus_pack = next((p for p in self.store_packs if p["id"] == "silver_p"), self.store_packs[0])
            self.pending_packs.append(copy.deepcopy(wc_bonus_pack))

    def _process_evolution(self, player, goals, assists):
        from data.evolutions import EVOLUTIONS_DB
        from data.rosters import calculate_ovr
        
        evo_state = player["evolution"]
        evo_db = next((e for e in EVOLUTIONS_DB if e["id"] == evo_state["id"]), None)
        if not evo_db: return
        
        lvl_idx = evo_state["level"]
        if lvl_idx >= len(evo_db["levels"]): return # Evolución ya terminada
        
        lvl = evo_db["levels"][lvl_idx]
        progress = 0
        if lvl["obj_type"] == "matches": progress = 1
        elif lvl["obj_type"] == "goals": progress = goals
        elif lvl["obj_type"] == "assists": progress = assists
        
        if progress > 0:
            evo_state["progress"] += progress
            if evo_state["progress"] >= lvl["target"]:
                # ¡Nivel completado!
                evo_state["progress"] = 0
                evo_state["level"] += 1
                
                # Aplicar recompensas
                if "reward_stats" in lvl:
                    for s_k, s_v in lvl["reward_stats"].items():
                        if s_k in player["s"]: player["s"][s_k] += s_v
                    player["ovr"] = calculate_ovr(player)
                
                if "reward_design" in lvl:
                    player["card_type"] = lvl["reward_design"]

    def calculate_chemistry(self):
        """Calcula la química total del equipo (Max 100)."""
        starters = [p for p in self.squad if p]
        if not starters: return 0
        
        total_chem = 0
        legend_bonus = 0
        
        # Obtener mapeo dinámico de posiciones
        pos_map = self._get_position_map_for_formation()
        
        nations = [p.get("nat", "???") for p in starters]
        
        for i, p in enumerate(starters):
            if not p: continue
            
            p_chem = 0
            if p.get("is_legend"):
                p_chem = 10
                legend_bonus += 1
            else:
                # 5 puntos base por estar en posición correcta
                expected = pos_map.get(i, [])
                if p["pos"] in expected:
                    p_chem = 5
                
                # +1 por cada jugador del mismo país (excluyéndose a sí mismo)
                my_nat = p.get("nat", "???")
                nat_matches = nations.count(my_nat) - 1
                p_chem += nat_matches
                
                # Cap de 10 por jugador
                p_chem = min(10, p_chem)
            
            total_chem += p_chem
            
        final_chem = min(100, total_chem + legend_bonus)
        return final_chem


    def save_ultimate(self):
        """Sincroniza el estado del club con el servidor central de forma asíncrona."""
        import threading
        data = {
            "team_name": self.team_name,
            "abbreviation": self.abbreviation,
            "badge": self.badge,
            "kit": self.kit,
            "primary": self.primary,
            "secondary": self.secondary,
            "accent": self.accent,
            "coins": self.coins,
            "fc_points": self.fc_points,
            "squad": self.squad,
            "club_items": self.club_items,
            "stats": self.stats,
            "formation": self.formation,
            "captain_name": self.captain_name,
            "has_claimed_founder_reward": self.has_claimed_founder_reward,
            "legend_pick_options": self.legend_pick_options,
            "pending_items": self.pending_items,
            "pending_picks": self.pending_picks,
            "pending_packs": self.pending_packs,
            "discard_recovery": self.discard_recovery,
            "league_state": self.league_state,
            "online_league_state": self.online_league_state,
            "battle_pass": self.battle_pass,
            "daily_objectives": self.daily_objectives,
            "sbc_state": self.sbc_state
        }
        
        def _save_task():
            import requests
            import json
            
            # Guardado Local Inmediato
            try:
                with open("ultimate_save.json", "w") as f:
                    json.dump(data, f)
            except Exception as e:
                print(f"Error local: {e}")
                
            # Sincronización Cloud
            try:
                requests.post(f"{self.server_url}/save", json={
                    "username": self.username,
                    "club_data": data
                }, timeout=1)
            except:
                pass 
                
        # Limpiar referencias de inventario si no están en master database
        self._sync_player_names()
        
        threading.Thread(target=_save_task, daemon=True).start()

    def _normalize_player_name(self, alias_name):
        """Intenta sincronizar un alias/nombre de evento con su contraparte oficial exacta."""
        if not hasattr(self, "_official_names_cache"):
            from data.rosters import all_rosters
            from data.legends import LEGENDS
            self._official_names_cache = []
            for roster in all_rosters.values():
                self._official_names_cache.extend([p["name"] for p in roster])
            self._official_names_cache.extend([l["name"] for l in LEGENDS])
            
        alias_lower = alias_name.lower().strip()
        
        # 1. Exact match (insensitive)
        for off in self._official_names_cache:
            if off.lower() == alias_lower:
                return off
                
        # 2. Partial match scoring
        import re
        parts = re.sub(r'[^a-zA-Z0-9\s]', '', alias_lower).split()
        if not parts: return alias_name
        
        best_match = alias_name
        best_score = 0
        
        for off in self._official_names_cache:
            off_lower = off.lower()
            score = 0
            for part in parts:
                if part in off_lower:
                    score += len(part)
            if score > best_score:
                best_score = score
                best_match = off
                
        # Validar un mínimo de coincidencia (ej: 4 letras)
        if best_score >= 4:
            return best_match
            
        return alias_name

    def _sync_player_names(self):
        """Asegura que todos los nombres en el club sean los oficiales."""
        for p in self.club_items.get("players", []):
            p["name"] = self._normalize_player_name(p.get("name", "Unknown"))
        for i in range(len(self.squad)):
            if self.squad[i]:
                self.squad[i]["name"] = self._normalize_player_name(self.squad[i].get("name", "Unknown"))

    def check_founder_reward(self):
        """Verifica si el jugador es elegible para el sobre de elección de leyenda."""
        import datetime
        # --- LÍMITE ESTRICTO: 26 de Sep de 2026 a las 0:00 ET ---
        limit_date = datetime.datetime(2026, 9, 26, 0, 0)
        now = datetime.datetime.now()
        
        if now < limit_date and not self.has_claimed_founder_reward:
            if not self.legend_pick_options:
                # Generar 3 opciones aleatorias de las leyendas disponibles
                if not self.all_legends:
                    from data.legends import LEGENDS
                    self.all_legends = LEGENDS
                self.legend_pick_options = random.sample(self.all_legends, 3)
                for p in self.legend_pick_options:
                    p["is_legend"] = True
                    p["name"] = self._normalize_player_name(p["name"])
                    p["ovr"] = calculate_ovr(p)
            return True
        return False

    def _generate_uid(self):
        import time
        return f"p_{int(time.time()*1000)}_{random.randint(1000, 9999)}"

    def can_add_to_squad(self, player, ignore_idx=-1):
        """Verifica si un jugador puede entrar al squad (regla de no repetidos por nombre/UID)."""
        if not player: return True
        p_name = player.get("name")
        p_uid = player.get("uid")
        
        for i, s_p in enumerate(self.squad):
            if i == ignore_idx: continue
            if s_p:
                if s_p.get("uid") == p_uid or s_p.get("name") == p_name:
                    return False, f"¡{p_name} ya está en la alineación!"
        return True, ""

    def claim_legend_pick(self, index):
        """Asigna la leyenda elegida al club."""
        if not self.legend_pick_options or index >= len(self.legend_pick_options):
            return False
            
        chosen = copy.deepcopy(self.legend_pick_options[index])
        chosen["uid"] = self._generate_uid()
        chosen["untradeable"] = True
        chosen["is_sbc"] = True # Marcado como SBC/Elección especial
        chosen["card_type"] = "FOUNDER" # Forzar estilo negro para el Cruyff negro
        self.club_items["players"].append(chosen)
        self.has_claimed_founder_reward = True
        self.legend_pick_options = []
        self.save_ultimate()
        return chosen

    def set_captain(self, player):
        """Designa un jugador como capitán del club."""
        # Limpiar capitán anterior en todos los jugadores
        for p in self.club_items["players"]:
            p["is_captain"] = False
        player["is_captain"] = True
        self.captain_name = player.get("name")
        self.save_ultimate()

    def swap_players(self, p1, p2):
        """Intercambia dos jugadores entre el XI inicial y la banca (o entre ellos)."""
        if p1 in self.squad and p2 in self.squad:
            # Intercambio entre titulares
            idx1, idx2 = self.squad.index(p1), self.squad.index(p2)
            self.squad[idx1], self.squad[idx2] = self.squad[idx2], self.squad[idx1]
        elif p1 in self.squad:
            # P1 es titular, P2 es suplente
            idx = self.squad.index(p1)
            self.squad[idx] = p2
        elif p2 in self.squad:
            # P2 es titular, P1 es suplente
            idx = self.squad.index(p2)
            self.squad[idx] = p1
        
        self.save_ultimate()

    def buy_item(self, item_id, currency="COINS"):
        """Gestiona la compra de cualquier artículo de la tienda (Sobres, Picks, Jugadores)."""
        import requests
        item = next((p for p in self.store_packs if p["id"] == item_id), None)
        if not item: return {"status": "error", "msg": "Artículo no encontrado"}
        
        # Validación de Seguridad con el Servidor
        try:
            payload = {
                "username": self.username,
                "pack_id": item_id,
                "currency": currency
            }
            if currency == "FC_POINTS":
                payload["current_points"] = self.fc_points
                payload["pack_price_points"] = item["price_points"]
            else:
                payload["current_coins"] = self.coins
                payload["pack_price"] = item["price"]

            r = requests.post(f"{self.server_url}/open_pack", json=payload, timeout=1.5)
            
            if r.status_code != 200:
                return {"status": "error", "msg": "Saldo insuficiente o error de servidor"}
            
            try:
                res_data = r.json()
            except (ValueError, Exception):
                return {"status": "error", "msg": "Respuesta inválida del servidor"}
            if currency == "FC_POINTS":
                self.fc_points = res_data.get("new_points_balance", self.fc_points)
            else:
                self.coins = res_data.get("new_balance", self.coins)
        except:
            # Fallback offline seguro
            if currency == "FC_POINTS":
                if self.fc_points >= item["price_points"]:
                    self.fc_points -= item["price_points"]
                else:
                    return {"status": "error", "msg": "Puntos FC insuficientes"}
            else:
                if self.coins >= item["price"]:
                    self.coins -= item["price"]
                else:
                    return {"status": "error", "msg": "Monedas insuficientes"}

        # Lógica por tipo de artículo
        if item["type"] == "PACK":
            return {"status": "pack", "items": self._generate_pack_items(item)}
        elif item["type"] == "PICK":
            opts = self._generate_pick_options(item)
            pick_obj = {"id": item["id"], "name": item["name"], "options": opts}
            self.pending_picks.append(pick_obj)
            self.save_ultimate()
            return {"status": "pick", "pick": pick_obj}
        elif item["type"] in ["BADGE", "KIT", "PLAYER"]:
            # Añadir directamente al club
            cat = "badges" if item["type"] == "BADGE" else ("kits" if item["type"] == "KIT" else "players")
            item["data"]["name"] = self._normalize_player_name(item["data"]["name"])
            self.club_items[cat].append(item["data"])
            self.save_ultimate()
            return {"status": "direct", "msg": f"{item['name']} añadido al club"}
            
        return {"status": "error", "msg": "Tipo de artículo no soportado"}

    def add_reward_pack(self, pack_config):
        """Añade un sobre de recompensa (no comprado) al inventario del club."""
        self.pending_packs.append(pack_config)
        self.save_ultimate()
        return True

    def _generate_random_player(self, rarity="ORO", min_ovr=0):
        """Genera un jugador aleatorio de una rareza específica para SBCs o recompensas directas."""
        from data.rosters import all_rosters, calculate_ovr
        all_p = []
        for roster in all_rosters.values(): all_p.extend(roster)
        
        # Filtrar por rareza
        if rarity == "ORO": filtered = [p for p in all_p if calculate_ovr(p) >= 75]
        elif rarity == "PLATA": filtered = [p for p in all_p if 65 <= calculate_ovr(p) < 75]
        elif rarity == "BRONCE": filtered = [p for p in all_p if calculate_ovr(p) < 65]
        else: filtered = all_p
        
        # Filtrar por OVR mínimo adicional
        if min_ovr > 0:
            filtered = [p for p in filtered if calculate_ovr(p) >= min_ovr]
            
        if not filtered: filtered = all_p
            
        p = copy.deepcopy(random.choice(filtered))
        p["uid"] = self._generate_uid()
        p["name"] = self._normalize_player_name(p["name"])
        p["ovr"] = calculate_ovr(p)
        p["rarity"] = rarity
        return p

    def _generate_pick_options(self, pick_config, force_special=False):
        """Genera los jugadores aleatorios para una elección (Player Pick)."""
        details = pick_config.get("details", {})
        num_options = details.get("options", 3)
        min_ovr = details.get("min_ovr", 0)
        rarity = details.get("rarity")
        is_legend = details.get("is_legend", False)
        nats = details.get("nats", [])
        
        is_wc_pick = "wc" in pick_config.get("id", "").lower()
        pool = []
        if is_legend:
            pool = self.all_legends if self.all_legends else LEGENDS
        else:
            from data.rosters import all_rosters
            for roster in all_rosters.values(): pool.extend(roster)
            
        final_options = []
        from data.event_worldcup import is_event_active, get_event_cards
        wc_active = is_event_active()
        event_cards = get_event_cards() if wc_active else []
        from data.rosters import calculate_ovr
        
        # Determinar qué slot tendrá la especial si está forzado
        special_slot = random.randint(0, num_options - 1) if force_special else -1

        for idx in range(num_options):
            # Forzar mínimo de Oro (75+) para todos los Picks de nivel superior
            effective_min = max(min_ovr, 75)
            
            if idx == special_slot:
                # Pool Especial: WC + Leyendas (Filtrar leyendas que ya están en el evento)
                event_names = {c["name"] for c in event_cards} if wc_active else set()
                active_legends = [l for l in (self.all_legends if self.all_legends else LEGENDS) if l["name"] not in event_names]
                
                special_pool_cards = event_cards + active_legends
                # Filtrar por el mínimo efectivo (Megasobre 80+, Normal 75+)
                special_pool = [p for p in special_pool_cards if calculate_ovr(p) >= effective_min]
                if special_pool:
                    p = copy.deepcopy(random.choice(special_pool))
                    p["uid"] = self._generate_uid()
                    p["name"] = self._normalize_player_name(p["name"])
                    p["ovr"] = calculate_ovr(p)
                    if p.get("is_legend"): p["rarity"] = "LEYENDA"
                    final_options.append(p)
                    continue

            # Pool Base: Jugadores normales filtrados por OVR (Mínimo Oro 75+)
            filtered_base = [p for p in pool if calculate_ovr(p) >= effective_min]
            if not filtered_base: filtered_base = pool # Fallback seguridad
            
            p = copy.deepcopy(random.choice(filtered_base))
            p["uid"] = self._generate_uid()
            p["name"] = self._normalize_player_name(p["name"])
            p["ovr"] = calculate_ovr(p)
            # Asegurar rareza ORO si es base >= 75
            if not p.get("is_legend"): p["rarity"] = "ORO"
            final_options.append(p)
        return final_options

    def select_pick_player(self, pick_idx, player_idx):
        """Cobra un jugador de un pick pendiente."""
        if 0 <= pick_idx < len(self.pending_picks):
            pick = self.pending_picks[pick_idx]
            player = pick["options"][player_idx]
            self.pending_items.append({"type": "player", "data": player})
            self.pending_picks.pop(pick_idx)
            self.save_ultimate()
            return player
        return None

    def open_pack(self, pack_id):
        """Antigua función (mantenida por compatibilidad pero delegada a buy_item)."""
        res = self.buy_item(pack_id)
        if res["status"] == "pack": return res["items"]
        return None

    def open_pending_pack(self, pack_idx):
        """Abre un sobre que el usuario ya tiene en su inventario."""
        if 0 <= pack_idx < len(self.pending_packs):
            pack = self.pending_packs.pop(pack_idx)
            items = self._generate_pack_items(pack)
            self.save_ultimate() # Guardado de seguridad inmediato
            return items
        return None

    def _generate_pack_items(self, pack):
        """Probabilidades drásticamente aumentadas para eventos especiales"""
        # Probabilidades leídas directamente del metadata del sobre (Sin adivinar rarezas)
        p_event = pack.get("event", "NORMAL")
        legend_chance = pack.get("legend_chance", 0.0005)
        event_drop_chance = pack.get("event_chance", 0.0)
        
        from data.event_worldcup import is_event_active, get_event_cards
        from data.event_flashback import is_flashback_active, get_flashback_cards
        
        wc_active = is_event_active()
        fb_active = is_flashback_active()
        event_cards = get_event_cards() if wc_active else []
        
        items = []
        total_items = pack.get("total_items", 12)
        
        # --- CONFIGURACIÓN DEL SOBRE ---
        details = pack.get("details", {})
        embedded = details.get("embedded_picks", [])
        pick_count = details.get("pick_count", 0)
        pick_chance = details.get("pick_chance", 1.0)
        # --- LÓGICA DE PICKS DINÁMICA (CONJUNTO ENTERO) ---
        pick_special_chance = details.get("pick_special_chance", 0.0)
        num_special_picks = 0
        current_pick_chance = pick_special_chance
        
        # Dar hasta 2 oportunidades (la base + 1 milagro) para activar la racha
        for _ in range(2):
            if random.random() < current_pick_chance:
                num_special_picks += 1
                current_pick_chance *= 0.1
                # Si sale premiado, seguimos la racha indefinidamente con prob. decreciente
                while random.random() < current_pick_chance:
                    num_special_picks += 1
                    current_pick_chance *= 0.1
                break # Salimos al haber procesado la racha
            else:
                # Si falla, la siguiente oportunidad de milagro es 10 veces más difícil
                current_pick_chance *= 0.1
        
        # Elegir qué slots de pick tendrán la especial
        special_pick_slots = random.sample(range(pick_count), min(num_special_picks, pick_count)) if pick_count > 0 else []

        if random.random() < pick_chance:
            for i in range(pick_count):
                for pick_cfg in embedded:
                    is_this_pick_special = (i in special_pick_slots)
                    opts = self._generate_pick_options(pick_cfg, force_special=is_this_pick_special)
                    self.pending_picks.append({"id": pick_cfg.get("id", "pick"), "name": pick_cfg.get("name", "PLAYER PICK"), "options": opts})
        
        # --- GENERAR JUGADORES Y CLUB ITEMS ---
        min_ovr = details.get("min_ovr", 0)
        min_p = details.get("min_players", total_items)
        max_p = details.get("max_players", total_items)
        final_player_count = random.randint(min_p, max_p)
        
        # Pool de todos los jugadores (Excluyendo leyendas para que solo salgan como especiales)
        all_pool = []
        from data.rosters import all_rosters
        for r_id, roster in all_rosters.items(): 
            if r_id == "LEG": continue # No mezclar leyendas en el pool común
            all_pool.extend(roster)
        
        # --- LÓGICA DE ESPECIALES POR SOBRE ---
        special_roll_chance = max(event_drop_chance, legend_chance)
        active_legends = (self.all_legends if self.all_legends else LEGENDS)
        
        num_specials_in_pack = 0
        current_pack_chance = special_roll_chance
        
        # Dar hasta 2 oportunidades (la base + 1 milagro) para activar la racha
        for _ in range(2):
            if random.random() < current_pack_chance:
                num_specials_in_pack += 1
                current_pack_chance *= 0.1
                # Si sale premiado, seguimos la racha indefinidamente con prob. decreciente
                while random.random() < current_pack_chance:
                    num_specials_in_pack += 1
                    current_pack_chance *= 0.1
                break
            else:
                # Si falla, la siguiente oportunidad de milagro es 10 veces más difícil
                current_pack_chance *= 0.1
        
        # Repartir los especiales en slots aleatorios
        special_slots = random.sample(range(final_player_count), min(num_specials_in_pack, final_player_count)) if final_player_count > 0 else []

        for i in range(total_items):
            if i < final_player_count:
                p = None
                
                # Preparar pools
                event_names = {c["name"] for c in event_cards} if wc_active else set()
                active_legends = [l for l in (self.all_legends if self.all_legends else LEGENDS) if l["name"] not in event_names]
                
                # Suelo de OVR
                pack_min_ovr = details.get("min_ovr", 0)
                if p_event == "WC": pack_min_ovr = max(pack_min_ovr, 75)
                if pack.get("color_tier") == "ELITE": pack_min_ovr = max(pack_min_ovr, 80)
                if pack.get("color_tier") == "ORO": pack_min_ovr = max(pack_min_ovr, 75)

                # 1. ¿Este slot es uno de los elegidos para ser especial?
                if i in special_slots:
                    special_pool = []
                    if wc_active: special_pool.extend(event_cards)
                    if fb_active and p_event == "FLASHBACK": 
                        special_pool.extend(get_flashback_cards())
                    special_pool.extend(active_legends)
                    
                    if special_pool:
                        valid_specials = [s for s in special_pool if calculate_ovr(s) >= pack_min_ovr]
                        if not valid_specials: valid_specials = special_pool 
                        
                        p = copy.deepcopy(random.choice(valid_specials))
                        if p.get("is_legend"):
                            p["rarity"] = "LEYENDA"
                            p["event"] = "LEYENDA"
                
                # 2. Slot Normal (Si no salió especial)
                if not p:
                    forced_rarity = details.get("rarity")
                    if forced_rarity:
                        if forced_rarity == "ORO": filtered = [fp for fp in all_pool if calculate_ovr(fp) >= 75 and fp["name"] not in event_names]
                        elif forced_rarity == "PLATA": filtered = [fp for fp in all_pool if 65 <= calculate_ovr(fp) < 75 and fp["name"] not in event_names]
                        else: filtered = [fp for fp in all_pool if calculate_ovr(fp) < 65 and fp["name"] not in event_names]
                    else:
                        filtered = [fp for fp in all_pool if calculate_ovr(fp) >= pack_min_ovr and fp["name"] not in event_names]
                    
                    if not filtered: filtered = all_pool
                    p = copy.deepcopy(random.choice(filtered))
                    
                    # Rarity por OVR
                    ovr = calculate_ovr(p)
                    if not p.get("is_legend") and p.get("rarity") != "LEYENDA":
                        if ovr >= 75: p["rarity"] = "ORO"
                        elif ovr >= 65: p["rarity"] = "PLATA"
                        else: p["rarity"] = "BRONCE"
                    p["event"] = "NORMAL"

                p["ovr"] = calculate_ovr(p) if not p.get("ovr") else p["ovr"]
                p["uid"] = self._generate_uid()
                items.append({"type": "player", "data": p})
            else:
                # Generar Club Item (Escudo o Equipación)
                item_type = random.choice(["BADGE", "KIT"])
                # Elegir un equipo aleatorio de TEAMS
                team = random.choice(TEAMS)
                items.append({
                    "type": item_type.lower(),
                    "data": {"name": team["name"], "short": team["short"]}
                })
        # Añadir todos los items a pending_items para la pantalla de revelación
        self.pending_items.extend(items)
        self.save_ultimate()
        return items

    def refresh_market(self):
        """Refresca las subastas del mercado global desde el servidor."""
        import requests
        try:
            r = requests.get(f"{self.server_url}/market", timeout=1.5)
            if r.status_code == 200:
                try:
                    self.market_auctions = r.json()
                except (ValueError, Exception):
                    pass
        except:
            pass

    def simulate_market_tick(self):
        """Tick periódico del mercado: refresca datos y limpia subastas expiradas."""
        import time
        self.refresh_market()
        # Limpiar subastas expiradas localmente
        now_ms = int(time.time() * 1000)
        self.market_auctions = [a for a in self.market_auctions if a.get("expires", now_ms + 1) > now_ms]

    def list_on_market(self, player, start_bid, buy_now):
        """Publica un jugador en el mercado global."""
        import requests, time
        auction = {
            "id": f"auc_{self.username}_{int(time.time()*1000)}",
            "seller_id": self.username,
            "player_data": player,
            "current_bid": start_bid,
            "buy_now": buy_now,
            "expires": int(time.time() * 1000) + (6 * 3600 * 1000),
            "is_bot": False
        }
        try:
            r = requests.post(f"{self.server_url}/market/list", json=auction, timeout=1.5)
            if r.status_code == 200:
                # Quitar del club
                self.club_items["players"] = [p for p in self.club_items["players"] if p.get("uid") != player.get("uid")]
                # Quitar del squad si estaba
                for i, sp in enumerate(self.squad):
                    if sp and sp.get("uid") == player.get("uid"):
                        self.squad[i] = None
                self.save_ultimate()
                return True
        except:
            pass
        return False

    def buy_from_market(self, auction):
        """Compra un jugador del mercado global."""
        import requests
        price = auction.get("buy_now", 0)
        if self.coins < price:
            return False, "Monedas insuficientes"
        try:
            r = requests.post(f"{self.server_url}/market/buy", json={"auction_id": auction["id"]}, timeout=1.5)
            if r.status_code == 200:
                self.coins -= price
                player = auction["player_data"]
                if "uid" not in player:
                    player["uid"] = self._generate_uid()
                self.club_items["players"].append(player)
                self.save_ultimate()
                return True, f"{player.get('name', 'Jugador')} fichado por {price} monedas"
            elif r.status_code == 404:
                return False, "La subasta ya no está disponible (ya vendida)"
            else:
                return False, f"Error del servidor (Código {r.status_code})"
        except requests.exceptions.Timeout:
            return False, "Error: Tiempo de espera agotado (Servidor lento)"
        except Exception as e:
            print(f"Error en compra: {e}")
            return False, "Error de conexión con el servidor"

    def bid_on_market(self, auction, bid_amount):
        """Oferta una puja por un jugador en el mercado global."""
        import requests
        if self.coins < bid_amount:
            return False, "Monedas insuficientes"
        if bid_amount <= auction.get("current_bid", 0):
            return False, f"La puja debe ser mayor que {auction.get('current_bid', 0)}"
        
        try:
            payload = {
                "auction_id": auction["id"],
                "bid_amount": bid_amount,
                "bidder": self.username
            }
            r = requests.post(f"{self.server_url}/market/bid", json=payload, timeout=1.5)
            if r.status_code == 200:
                self.coins -= bid_amount
                self.save_ultimate()
                # Actualizar localmente de inmediato para feedback instantáneo
                auction["current_bid"] = bid_amount
                auction["last_bidder"] = self.username
                player_name = auction.get("player_data", {}).get("name", "Jugador")
                return True, f"Puja de {bid_amount} realizada por {player_name}"
            else:
                try:
                    err_data = r.json()
                    err_msg = err_data.get("error", "Error desconocido del servidor")
                except (ValueError, Exception):
                    err_msg = f"Error del servidor (código {r.status_code})"
                return False, f"Error: {err_msg}"
        except Exception as e:
            print(f"Error en puja: {e}")
            return False, "Error de conexión con el servidor"

    def get_market_value(self, player):
        ovr = player.get('ovr', 75)
        base = 200
        if ovr >= 85: base = 15000
        elif ovr >= 80: base = 5000
        elif ovr >= 75: base = 2000
        elif ovr >= 65: base = 800
        if player.get('is_legend'): base *= 5
        if player.get('card_type') in ('WORLDCUP', 'WORLDCUP_LEGEND', 'FLASHBACK'): base *= 3
        if player.get('rarity') == 'EVENTO': base *= 2
        return base

    def get_price_ranges(self, player):
        val = self.get_market_value(player)
        min_bid = max(150, int(val * 0.5))
        max_buy = int(val * 3)
        return min_bid, max_buy

    def get_quick_sell_value(self, player):
        ovr = player.get('ovr', 75)
        if player.get('is_legend'): return 10000
        if ovr >= 83: return 800
        if ovr >= 80: return 400
        if ovr >= 75: return 200
        if ovr >= 65: return 80
        return 30

    def get_my_auctions(self):
        return [a for a in self.market_auctions if a.get('seller_id') == self.username]

ultimate_manager = UltimateManager()
